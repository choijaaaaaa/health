# 건강정보 카드뉴스 생성기. WHY: 카드뉴스는 텍스트+이미지 합성뿐이라 AI 불필요 —
# 순수 PIL 스크립트로 자동화해서 Claude 세션 없이 반복 생산 가능하게 분리함.
# 폰트 웨이트(Apple SD Gothic Neo ttc index)로 타이포 위계, 그림자/패널로 입체감을 준다.
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
# ttc 내부 인덱스: 0=Regular 2=Medium 4=SemiBold 6=Bold 8=Light
W, H = 1080, 1350
MARGIN = 72

BG_TOP = (253, 249, 245)
BG_BOTTOM = (246, 237, 230)
INK = (43, 35, 31)
INK_SOFT = (139, 124, 110)
ACCENT = (200, 74, 98)
ACCENT_DEEP = (163, 52, 74)
ACCENT_SOFT = (250, 222, 227)
GOLD = (178, 122, 38)
GOLD_SOFT = (241, 227, 198)
PANEL = (255, 253, 250)
SHADOW = (60, 45, 35)


def _font(size, weight="regular"):
    idx = {"light": 8, "regular": 0, "medium": 2, "semibold": 4, "bold": 6}[weight]
    return ImageFont.truetype(FONT_PATH, size, index=idx)


def _vertical_gradient(top, bottom):
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def _draw_centered(draw, lines, y, line_height, size, color, weight="regular"):
    f = _font(size, weight)
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        w = bbox[2] - bbox[0]
        draw.text(((W - w) / 2 - bbox[0], y), line, font=f, fill=color)
        y += line_height
    return y


def _rounded_panel(canvas, box, radius, fill, shadow_offset=14, shadow_blur=28, shadow_opacity=55):
    x0, y0, x1, y1 = box
    # 그림자 레이어
    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow_layer)
    sdraw.rounded_rectangle(
        [x0, y0 + shadow_offset, x1, y1 + shadow_offset], radius=radius,
        fill=(*SHADOW, shadow_opacity),
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
    canvas.paste(Image.alpha_composite(canvas.convert("RGBA"), shadow_layer).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle(box, radius=radius, fill=fill)
    return canvas


def _char_medallion(path, size, ring_color=ACCENT_SOFT, ring_w=10):
    raw = Image.open(path).convert("RGB").resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    photo = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    photo.paste(raw, (0, 0), mask)

    pad = ring_w + 18
    canvas = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    # 부드러운 그림자
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.ellipse([pad - 4, pad + 10, pad + size + 4, pad + size + 18], fill=(*SHADOW, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.alpha_composite(canvas, shadow)
    cdraw = ImageDraw.Draw(canvas)
    cdraw.ellipse([pad - ring_w, pad - ring_w, pad + size + ring_w, pad + size + ring_w], fill=ring_color)
    canvas.paste(photo, (pad, pad), photo)
    return canvas


def _diamond_divider(draw, y, color=GOLD):
    cx = W // 2
    pts = [(cx, y - 9), (cx + 9, y), (cx, y + 9), (cx - 9, y)]
    draw.polygon(pts, fill=color)
    draw.line([(MARGIN + 40, y), (cx - 24, y)], fill=color, width=3)
    draw.line([(cx + 24, y), (W - MARGIN - 40, y)], fill=color, width=3)


def _top_chip(canvas, draw, text, fill):
    f = _font(30, "semibold")
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 34, 16
    chip_w, chip_h = tw + pad_x * 2, th + pad_y * 2
    x0 = (W - chip_w) // 2
    y0 = 64
    draw.rounded_rectangle([x0, y0, x0 + chip_w, y0 + chip_h], radius=chip_h // 2, fill=fill)
    draw.text((x0 + pad_x - bbox[0], y0 + pad_y - bbox[1]), text, font=f, fill=(255, 255, 255))
    return y0 + chip_h


def make_cover(title_lines, char_paths, out_path, bg_photo_path=None):
    """bg_photo_path 주면 실사진을 풀블리드 배경으로 쓰는 임팩트있는 썸네일형 표지로,
    안 주면 기존 플랫 그라디언트 배경 표지로 만든다."""
    if bg_photo_path:
        _make_cover_photo(title_lines, char_paths, out_path, bg_photo_path)
    else:
        _make_cover_flat(title_lines, char_paths, out_path)


def make_cover_titlecard(hook_text: str, out_path, font_size: int = 92, char_path: str | None = None):
    """WHY 숏폼 영상 제목 카드와 완전히 동일한 스타일(2026-07-31, "카드뉴스 첫장도
    숏폼 영상 썸네일이랑 똑같이 그냥 가져가자"): 사진·캐릭터 배지·주제 태그 다 빼고,
    단색 배경 + 문제 제기 훅 한 줄/두 줄만 크게 — 영상 쪽 `_make_title_card_png`와
    같은 로직(ACCENT 단색 배경, 굵은 흰 글자, 단어 단위 줄바꿈)을 카드뉴스 캔버스
    (1080x1350)에 맞게 그대로 재사용한다.

    WHY char_path(2026-07-31, "캐릭터를 큼직하고 흐리게 글자의 배경으로"): 캐릭터
    이미지를 캔버스보다 크게 확대·크롭해서 흐리게 깐 뒤 ACCENT 스크림을 얹는다 —
    영상 제목 카드와 동일한 처리."""
    img = Image.new("RGB", (W, H), ACCENT)
    if char_path:
        target = int(H * 1.15)
        char = Image.open(char_path).convert("RGB").resize((target, target))
        char = char.filter(ImageFilter.GaussianBlur(25))
        left, top = (target - W) // 2, (target - H) // 2
        char = char.crop((left, top, left + W, top + H))
        scrim = Image.new("RGBA", (W, H), (*ACCENT, 150))
        img = Image.alpha_composite(char.convert("RGBA"), scrim).convert("RGB")
    font = _font(font_size, "bold")
    draw = ImageDraw.Draw(img)
    max_text_w = W - 160
    words, lines, cur = hook_text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_text_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_h = font_size + 28
    total_h = line_h * len(lines)
    y = (H - total_h) / 2 - 30
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2 - bbox[0], y - bbox[1]), line, font=font, fill=(255, 255, 255))
        y += line_h

    _draw_centered(draw, ["넘겨서 확인하기  →"], H - 110, 0, 34, (255, 214, 224), "semibold")
    img.save(out_path, quality=95)


def _make_cover_flat(title_lines, char_paths, out_path):
    img = _vertical_gradient(BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    _top_chip(img, draw, "건강 카드뉴스", ACCENT)

    unique_paths = list(dict.fromkeys(str(p) for p in char_paths))
    size, gap = 200, 24
    n = len(unique_paths)
    cols = min(n, 3)
    med_size = size + (10 + 18) * 2
    total_w = med_size * cols + gap * (cols - 1)
    start_x = (W - total_w) // 2
    y0 = 250
    row_h = med_size + gap
    for idx, path in enumerate(unique_paths):
        row, col = divmod(idx, cols)
        remainder = n - cols * (n // cols)
        row_items = cols if row < n // cols else remainder
        row_w = med_size * row_items + gap * (row_items - 1)
        row_x0 = (W - row_w) // 2
        x = row_x0 + col * (med_size + gap)
        y = y0 + row * row_h
        m = _char_medallion(path, size)
        img.paste(m, (x, y), m)

    rows = (n + cols - 1) // cols
    y = y0 + rows * row_h + 30
    draw = ImageDraw.Draw(img)
    y = _draw_centered(draw, title_lines[:-1], y, 66, 46, INK_SOFT, "medium")
    y = _draw_centered(draw, [title_lines[-1]], y + 4, 70, 60, INK, "bold")
    _diamond_divider(draw, y + 50)
    _draw_centered(draw, ["넘겨서 확인하기  →"], y + 90, 40, 32, ACCENT, "semibold")
    img.save(out_path, quality=95)


def _make_cover_photo(title_lines, char_paths, out_path, bg_photo_path):
    # WHY 사진을 크게 블러 + 전체 스크림으로 배경화(2026-07-30, 재지적): 이전엔 선명한
    # 사진 위에 캐릭터를 큼직하게 얹고 그 아래 작은 글자를 깔아서 "감자 위에 글자
    # 쳐박아놓은" 느낌이었다 — 후킹은 글자가 해야 하므로, 사진은 흐린 배경 무드로만
    # 쓰고 캔버스 중앙 전체를 훅 카피가 차지하도록 레이아웃을 뒤집는다.
    photo = Image.open(bg_photo_path).convert("RGB")
    ratio = W / H
    pw, ph = photo.size
    if pw / ph > ratio:
        new_w = int(ph * ratio)
        photo = photo.crop(((pw - new_w) // 2, 0, (pw - new_w) // 2 + new_w, ph))
    else:
        new_h = int(pw / ratio)
        photo = photo.crop((0, (ph - new_h) // 2, pw, (ph - new_h) // 2 + new_h))
    photo = photo.resize((W, H)).filter(ImageFilter.GaussianBlur(38))
    img = photo.convert("RGBA")

    # 전체 캔버스에 고른 어두운 스크림 — 사진의 어느 부분에 글자가 와도 대비 확보
    scrim = Image.new("RGBA", (W, H), (18, 13, 10, 158))
    img = Image.alpha_composite(img, scrim)

    draw = ImageDraw.Draw(img)
    _top_chip(img, draw, "건강 카드뉴스", ACCENT)

    # 훅 카피(마지막 줄 제외) — 캔버스 중앙을 지배하는 메인 카피, 흰색 굵게
    hook_lines = title_lines[:-1]
    topic_line = title_lines[-1]
    hook_line_h = 110
    hook_h = hook_line_h * len(hook_lines)
    pill_h = 78
    med_size = 92
    med_canvas = med_size + (6 + 14) * 2
    gap_hook_pill, gap_pill_med, gap_med_hint = 44, 40, 26
    hint_h = 50
    block_h = hook_h + gap_hook_pill + pill_h + gap_pill_med + med_canvas + gap_med_hint + hint_h
    region_top, region_bottom = 150, H - 40
    y = region_top + (region_bottom - region_top - block_h) // 2

    y = _draw_centered(draw, hook_lines, y, hook_line_h, 84, (255, 255, 255), "bold")
    y += gap_hook_pill

    # 주제 태그 — 알약형 캡슐, 액센트 컬러(작은 상단 칩과 짝을 이루는 톤)
    pf = _font(40, "bold")
    pbbox = draw.textbbox((0, 0), topic_line, font=pf)
    ptw, pth = pbbox[2] - pbbox[0], pbbox[3] - pbbox[1]
    ppad_x, ppad_y = 32, 15
    pchip_w, pchip_h = ptw + ppad_x * 2, pth + ppad_y * 2
    px0 = (W - pchip_w) // 2
    draw.rounded_rectangle([px0, y, px0 + pchip_w, y + pchip_h], radius=pchip_h // 2, fill=ACCENT)
    draw.text((px0 + ppad_x - pbbox[0], y + ppad_y - pbbox[1]), topic_line, font=pf, fill=(255, 255, 255))
    y += pchip_h + gap_pill_med

    # 캐릭터 — 중앙 공간을 글자에 내주기 위해 작은 배지로만
    unique_paths = list(dict.fromkeys(str(p) for p in char_paths))
    if unique_paths:
        m = _char_medallion(unique_paths[0], med_size, ring_color=(255, 255, 255), ring_w=6)
        img.paste(m, ((W - m.width) // 2, y), m)
        y += m.height + gap_med_hint
    else:
        y += gap_med_hint

    draw = ImageDraw.Draw(img)
    _draw_centered(draw, ["넘겨서 확인하기  →"], y, 0, 34, (255, 214, 224), "semibold")

    img.convert("RGB").save(out_path, quality=95)


def make_fact_card(num, name, char_path, body_lines, total, out_path, eyebrow="HEALTH TIP"):
    img = _vertical_gradient(BG_TOP, BG_BOTTOM)
    img = img.convert("RGB")

    # 패널을 화면 상단 가까이까지 크게 — 이전엔 위쪽에 빈 배경이 너무 많이 남아서
    # "짜친다"는 피드백(2026-07-30, 반복 지적)
    panel_box = [MARGIN - 24, 130, W - MARGIN + 24, H - 140]
    img = _rounded_panel(img, panel_box, radius=40, fill=PANEL)
    draw = ImageDraw.Draw(img)

    # 상단 라벨 — 페이지 번호는 큼직한 숫자 대신 하단 바에서 "N / total"로
    # 작게만 보여준다(2026-07-30, 큰 숫자가 정보량 대비 공간을 너무 차지한다는 피드백)
    label_f = _font(32, "semibold")
    draw.text((MARGIN, 56), eyebrow, font=label_f, fill=GOLD)

    # 캐릭터는 첫 화면(표지) 이후로는 크게 안 들어가도 된다는 판단 —
    # 팩트카드는 정보가 주인공이라 캐릭터를 패널 우상단의 작은 배지로 축소.
    char_size = 130
    m = _char_medallion(char_path, char_size, ring_w=8)
    badge_x = panel_box[2] - m.width - 20
    badge_y = panel_box[1] + 20
    img.paste(m, (badge_x, badge_y), m)

    # 캐릭터 이름 라벨 — 배지만 보고는 어떤 품목인지 못 알아볼 수 있어서
    # (표지에만 이름이 있고 이후 페이지는 넘겨서 못 봄, 2026-07-30 피드백) 매 카드에 표시.
    # WHY 알약형 배지로 강화(2026-07-31 재지적: "명칭 언급이 필요할듯" — 기존 22px
    # 연회색 텍스트는 너무 눈에 안 띄어서 사실상 없는 것과 마찬가지였다): 액센트
    # 색 배경 + 굵은 글자로 배지 형태를 줘서 확실히 읽히게 한다.
    char_label = Path(char_path).stem.replace("_illust", "")
    label_f2 = _font(28, "bold")
    lb = draw.textbbox((0, 0), char_label, font=label_f2)
    lw, lh = lb[2] - lb[0], lb[3] - lb[1]
    lpad_x, lpad_y = 18, 8
    lchip_w, lchip_h = lw + lpad_x * 2, lh + lpad_y * 2
    badge_cx = badge_x + m.width / 2
    lchip_y = badge_y + m.height + 8
    lchip_x0 = badge_cx - lchip_w / 2
    draw.rounded_rectangle(
        [lchip_x0, lchip_y, lchip_x0 + lchip_w, lchip_y + lchip_h],
        radius=lchip_h // 2, fill=ACCENT_SOFT,
    )
    draw.text((lchip_x0 + lpad_x - lb[0], lchip_y + lpad_y - lb[1]), char_label, font=label_f2, fill=ACCENT_DEEP)

    # 글자 크게 — 계속 반복 지적된 부분(2026-07-30 여러 차례) — 이번엔 이전보다
    # 한 단계가 아니라 확실히 크게: 제목 76→92, 본문 46→58. 간격도 커진 폰트
    # 크기에 맞게 같이 늘려서 겹치지 않게 조정.
    # WHY +50이 아니라 +80: 이름 배지가 알약형(2026-07-31)으로 커지면서 제목 첫 줄
    # 우측 상단과 살짝 겹치던 문제 — 여유를 더 준다.
    draw = ImageDraw.Draw(img)
    y = panel_box[1] + m.height + 80
    y = _draw_centered(draw, [name], y, 0, 92, INK, "bold")
    _diamond_divider(draw, y + 132)
    _draw_centered(draw, body_lines, y + 182, 86, 58, INK, "medium")

    draw.rectangle([0, H - 70, W, H], fill=ACCENT)
    _draw_centered(draw, [f"{num} / {total}"], H - 58, 0, 30, (255, 255, 255), "medium")
    img.save(out_path, quality=95)


def make_closing(headline_blocks, tip_lines, char_paths, cta_text, out_path):
    img = _vertical_gradient(BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    _top_chip(img, draw, "마무리", GOLD)

    # 단일 캐릭터 주제면 char_paths에 같은 이미지가 여러 번 들어있을 수 있어
    # (아이템마다 char_file 지정 구조라) — 중복 제거하고, 첫 화면(표지)만큼
    # 크게 안 보여줘도 되니 작게 표시.
    unique_paths = list(dict.fromkeys(str(p) for p in char_paths))
    size, gap = 130, 16
    med_size = size + (8 + 18) * 2
    total_w = med_size * len(unique_paths) + gap * (len(unique_paths) - 1)
    start_x = (W - total_w) // 2
    label_f2 = _font(20, "semibold")
    for j, path in enumerate(unique_paths):
        m = _char_medallion(path, size, ring_color=GOLD_SOFT, ring_w=8)
        bx = start_x + j * (med_size + gap)
        img.paste(m, (bx, 190), m)
        char_label = Path(path).stem.replace("_illust", "")
        lb = draw.textbbox((0, 0), char_label, font=label_f2)
        lw = lb[2] - lb[0]
        draw.text((bx + m.width / 2 - lw / 2 - lb[0], 190 + m.height + 2), char_label, font=label_f2, fill=INK_SOFT)

    # 글자 크게 — 팩트카드와 동일하게 마무리 카드도 확실히 키움(2026-07-30)
    draw = ImageDraw.Draw(img)
    y = 190 + med_size + 76
    for i, block in enumerate(headline_blocks):
        weight = "bold" if i == 0 else "semibold"
        color = INK if i == 0 else ACCENT_DEEP
        y = _draw_centered(draw, block, y, 76, 56, color, weight) + 34
    _diamond_divider(draw, y + 6)
    _draw_centered(draw, tip_lines, y + 58, 64, 42, INK_SOFT, "regular")

    draw.rectangle([0, H - 96, W, H], fill=ACCENT)
    _draw_centered(draw, [cta_text], H - 68, 0, 34, (255, 255, 255), "semibold")
    img.save(out_path, quality=95)


def generate(spec_path: str, char_dir: str, out_dir: str):
    """spec_path: JSON 파일 — {title, items:[{name, char_file, body}], closing:{headline, tip, cta}}"""
    spec = json.loads(Path(spec_path).read_text())
    char_dir = Path(char_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    char_paths = [str(char_dir / item["char_file"]) for item in spec["items"]]
    eyebrow = spec.get("eyebrow", "HEALTH TIP")

    # WHY make_cover_titlecard가 기본(2026-07-31): "카드뉴스 첫장도 숏폼 영상
    # 썸네일이랑 똑같이 그냥 가져가자" 피드백 이후 이 스타일이 표준이 됐다 —
    # spec["title"]는 마지막 줄이 주제명(예: "돼지감자차 이야기")이고 나머지가
    # 문제 제기 훅이라는 기존 관례를 그대로 따라 훅만 뽑아 쓴다(주제명은 표지에서
    # 뺌, 영상 제목 카드와 동일한 처리). CLI로 바로 generate() 호출해도 예전
    # 그라디언트 표지(make_cover)로 되돌아가지 않도록 여기서 기본값을 바꿔둔다.
    hook_text = " ".join(spec["title"][:-1]) if len(spec["title"]) > 1 else spec["title"][0]
    make_cover_titlecard(hook_text, out_dir / "00_표지.jpg", char_path=char_paths[0] if char_paths else None)

    n = len(spec["items"])
    for i, item in enumerate(spec["items"], start=1):
        make_fact_card(i, item["name"], char_dir / item["char_file"], item["body"], n, out_dir / f"{i:02d}_{item['name']}.jpg", eyebrow=eyebrow)

    closing = spec["closing"]
    make_closing(closing["headline"], closing["tip"], char_paths, closing["cta"], out_dir / f"{n+1:02d}_마무리.jpg")
    print(f"카드뉴스 {n+2}장 생성 완료: {out_dir}")


if __name__ == "__main__":
    spec_path, char_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    generate(spec_path, char_dir, out_dir)
