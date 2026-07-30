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


def make_cover(title_lines, char_paths, out_path):
    img = _vertical_gradient(BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    _top_chip(img, draw, "건강 카드뉴스", ACCENT)

    size, gap = 200, 24
    n = len(char_paths)
    cols = min(n, 3)
    med_size = size + (10 + 18) * 2
    total_w = med_size * cols + gap * (cols - 1)
    start_x = (W - total_w) // 2
    y0 = 250
    row_h = med_size + gap
    for idx, path in enumerate(char_paths):
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


def make_fact_card(num, name, char_path, body_lines, total, out_path):
    img = _vertical_gradient(BG_TOP, BG_BOTTOM)
    img = img.convert("RGB")

    panel_box = [MARGIN - 24, 300, W - MARGIN + 24, H - 140]
    img = _rounded_panel(img, panel_box, radius=40, fill=PANEL)
    draw = ImageDraw.Draw(img)

    # 상단 "TIP 0N" 라벨
    label_f = _font(26, "semibold")
    draw.text((MARGIN, 74), "CHOLESTEROL TIP", font=label_f, fill=GOLD)
    num_f = _font(96, "bold")
    ntxt = f"{num:02d}"
    draw.text((MARGIN - 4, 100), ntxt, font=num_f, fill=ACCENT_SOFT)
    draw.text((MARGIN - 4, 100), ntxt, font=num_f, fill=None, stroke_width=3, stroke_fill=ACCENT)

    char_size = 340
    m = _char_medallion(char_path, char_size)
    img.paste(m, ((W - m.width) // 2, panel_box[1] - m.height // 2 + 10), m)

    draw = ImageDraw.Draw(img)
    y = panel_box[1] + m.height // 2 + 30
    y = _draw_centered(draw, [name], y, 0, 52, INK, "bold")
    _diamond_divider(draw, y + 58)
    _draw_centered(draw, body_lines, y + 100, 54, 33, INK, "regular")

    draw.rectangle([0, H - 70, W, H], fill=ACCENT)
    _draw_centered(draw, [f"{num} / {total}"], H - 58, 0, 28, (255, 255, 255), "medium")
    img.save(out_path, quality=95)


def make_closing(headline_blocks, tip_lines, char_paths, cta_text, out_path):
    img = _vertical_gradient(BG_TOP, BG_BOTTOM)
    draw = ImageDraw.Draw(img)
    _top_chip(img, draw, "마무리", GOLD)

    size, gap = 156, 20
    med_size = size + (8 + 14) * 2
    total_w = med_size * len(char_paths) + gap * (len(char_paths) - 1)
    start_x = (W - total_w) // 2
    for j, path in enumerate(char_paths):
        m = _char_medallion(path, size, ring_color=GOLD_SOFT, ring_w=8)
        img.paste(m, (start_x + j * (med_size + gap), 210), m)

    draw = ImageDraw.Draw(img)
    y = 210 + med_size + 60
    for i, block in enumerate(headline_blocks):
        weight = "bold" if i == 0 else "semibold"
        color = INK if i == 0 else ACCENT_DEEP
        y = _draw_centered(draw, block, y, 60, 44, color, weight) + 34
    _diamond_divider(draw, y + 6)
    _draw_centered(draw, tip_lines, y + 46, 50, 32, INK_SOFT, "regular")

    draw.rectangle([0, H - 96, W, H], fill=ACCENT)
    _draw_centered(draw, [cta_text], H - 68, 0, 32, (255, 255, 255), "semibold")
    img.save(out_path, quality=95)


def generate(spec_path: str, char_dir: str, out_dir: str):
    """spec_path: JSON 파일 — {title, items:[{name, char_file, body}], closing:{headline, tip, cta}}"""
    spec = json.loads(Path(spec_path).read_text())
    char_dir = Path(char_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    char_paths = [str(char_dir / item["char_file"]) for item in spec["items"]]

    make_cover(spec["title"], char_paths, out_dir / "00_표지.jpg")

    n = len(spec["items"])
    for i, item in enumerate(spec["items"], start=1):
        make_fact_card(i, item["name"], char_dir / item["char_file"], item["body"], n, out_dir / f"{i:02d}_{item['name']}.jpg")

    closing = spec["closing"]
    make_closing(closing["headline"], closing["tip"], char_paths, closing["cta"], out_dir / f"{n+1:02d}_마무리.jpg")
    print(f"카드뉴스 {n+2}장 생성 완료: {out_dir}")


if __name__ == "__main__":
    spec_path, char_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
    generate(spec_path, char_dir, out_dir)
