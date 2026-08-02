# 캐릭터(Kling 모션 루프) + 실사진 배경 + 자막을 합쳐 숏츠 영상으로 조립.
# WHY: 이 ffmpeg 빌드엔 drawtext/subtitles(libass) 필터가 없어서 PIL로 자막 PNG를 그려
# overlay로 합성한다.
# 2026-07-30: 캐릭터 움직임을 Rhubarb 립싱크(입모양 3장 스위칭)에서 Kling AI
# image2video로 전환 — 입모양만 바뀌는 정지 이미지 스위칭은 "위치만 옮겨졌지 그림
# 자체는 그대로"라 밋밋하다는 피드백. 이제 Kling으로 뽑은 5초 자연스러운 움직임
# 영상(고개 갸웃 등) 하나를 대사 길이에 맞춰 반복 재생 — 대사 내용과 입모양이
# 정확히 맞을 필요는 없는 캐릭터 디자인(비인간 사물)이라 이 방식으로 충분하다.
# 캐릭터를 별도 알파 트랙으로 먼저 만드는 이유는 여전히 유효: 배경 합성은
# "인트로/코너" 딱 2구간으로만 나눠서 처리해야 전체-길이 overlay 체인 성능 문제를
# 피할 수 있다(2026-07-29 cat-fight 작업에서 확인).
from __future__ import annotations

import math
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FPS = 30

# WHY 기본 엔딩 CTA(2026-08-02, "카드뉴스랑 숏폼 영상 마지막에 구독, 좋아요, 팔로우
# 요청하는 글도 추가하자"): 매번 topic마다 문구를 새로 넘길 필요 없이 항상 같은
# 표준 문구로 나가게 모듈 상수로 고정 — end_card_text를 명시로 넘기면 그걸 쓰고,
# 안 넘기면(기본) 이 문구를 쓴다. 완전히 끄고 싶으면 end_card_duration=0.
DEFAULT_END_CARD_TEXT = "더 많은 건강정보가 궁금하다면 구독·좋아요·팔로우 해주세요"

# WHY 칠판 스타일 기본 배경 전환(2026-08-02): 실사진을 그대로 배경에 깔면 밋밋하고
# 눈에 확 안 들어온다는 피드백("real 이미지 그대로 배경으로 넣고 있는데... 확 보이지가
# 않는다") — 카드뉴스처럼 칠판 같은 배경에 감각적인 폰트로 나레이션을 써주는 쪽으로
# 새 topic 기본값을 바꾼다. 폰트는 무료 상업적 이용 가능한 구글 폰트 "Gaegu"(SIL OFL
# 1.1, assets_library/fonts/OFL-Gaegu.txt 참고) — 손글씨/마카체 느낌의 한글 지원 폰트.
CHALK_FONT_PATH = str(Path(__file__).resolve().parent.parent / "assets_library" / "fonts" / "Gaegu-Bold.ttf")
CHALKBOARD_TOP = (32, 66, 48)
CHALKBOARD_BOTTOM = (20, 42, 31)


def _parse_srt(srt_path: str) -> list[tuple[float, float, str]]:
    text = Path(srt_path).read_text()
    time_re = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)")
    entries = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = time_re.match(lines[1])
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
        end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
        entries.append((start, end, " ".join(lines[2:])))
    return entries


def _make_ad_tag_png(out_path: Path, font_size=28, padding=12):
    """공정위 표시광고 지침 대응 — 실제 쿠팡/네이버 제휴 링크를 쓰기로 확정한
    영상에만 assemble(..., ad_tag=True)로 켠다. "처음부터 끝까지 노출" 요건 때문에
    약하게(반투명)라도 전체 구간에 계속 떠 있어야 하고, 후반부에만 넣는 건 안 됨
    (shopping-shorts-video에서 확인된 규칙과 동일)."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = "광고"
    dummy = Image.new("RGBA", (1, 1))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    box_w, box_h = tw + padding * 2, th + padding * 2
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 100))
    draw = ImageDraw.Draw(img)
    draw.text((padding - bbox[0], padding - bbox[1]), text, font=font, fill=(255, 255, 255, 210))
    img.save(out_path)


def _cover_crop_subject(photo_path: str, out_w: int, out_h: int) -> Image.Image:
    """real 사진을 (out_w x out_h) 프레임에 꽉 차게 cover 크롭 — 정사각형 강제
    리사이즈로 피사체가 밀려나는 문제, 그리고 흰 스튜디오 배경 사진에서 피사체가
    일부만 차지해서 크롭 후에도 흰 여백만 남는 문제, 둘 다 대응한다(2026-08-02,
    "정사각형으로 리사이즈해서 크롭하면 안 됨" / "어떤 물건인지 알 수 있는게
    훨씬 나을거같네"). 원본 비율을 유지한 채 목표 프레임을 완전히 덮을 때까지
    확대하고 중앙을 잘라낸다.

    WHY 픽셀 단위 threshold 대신 행/열 밀도 프로파일(2026-08-02, "real 이미지의
    opacity를 없애라고 아직도 흐려" — 실제로는 블러가 아니라 크롭이 너무 헐거워서
    피사체가 작고 멀게 나온 문제): 흰 스튜디오컷은 배경에 미세한 그림자/비네팅이
    깔려서 "흰색이 아닌 픽셀 하나라도 있으면 subject"식 bounding box는 그림자
    번짐까지 다 잡아버려 사실상 전체 사진 크기로 뻥튀기된다(실측: 단순 bbox가
    전체 프레임의 90%+ 를 차지) — 그러면 확대 배율이 거의 없어서 피사체가 작고
    멀리 보인다. 대신 각 행/열에서 "피사체 픽셀 비율"이 일정 밀도 이상인 범위만
    골라내면, 그림자 번짐 같은 옅은 잡음은 걸러지고 실제로 피사체가 뭉쳐있는
    영역만 남는다 — 촘촘한(0.30) 기준부터 시작해서 전체 면적의 8% 이상을
    커버하는 첫 기준을 채택, 사진마다 피사체 밀도가 달라도 적당히 타이트한
    크롭을 자동으로 찾는다."""
    photo = Image.open(photo_path).convert("RGB")
    gray = photo.convert("L")
    subject_mask = gray.point(lambda x: 255 if x < 235 else 0)
    row_profile = subject_mask.resize((1, photo.height), Image.BOX)
    col_profile = subject_mask.resize((photo.width, 1), Image.BOX)
    rows = list(row_profile.getdata())
    cols = list(col_profile.getdata())
    total_area = photo.width * photo.height
    bbox = None
    for density in (0.30, 0.25, 0.20, 0.15, 0.10, 0.05, 0.02):
        row_thresh = 255 * density
        idx_rows = [i for i, v in enumerate(rows) if v > row_thresh]
        idx_cols = [i for i, v in enumerate(cols) if v > row_thresh]
        if not idx_rows or not idx_cols:
            continue
        candidate = (min(idx_cols), min(idx_rows), max(idx_cols), max(idx_rows))
        area = (candidate[2] - candidate[0]) * (candidate[3] - candidate[1])
        if area >= total_area * 0.08:
            bbox = candidate
            break

    if bbox:
        bw, bh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = round(bw * 0.15), round(bh * 0.15)
        crop_box = (
            max(bbox[0] - pad_x, 0), max(bbox[1] - pad_y, 0),
            min(bbox[2] + pad_x, photo.width), min(bbox[3] + pad_y, photo.height),
        )
        photo = photo.crop(crop_box)

    scale = max(out_w / photo.width, out_h / photo.height)
    resized = photo.resize((round(photo.width * scale), round(photo.height * scale)))
    left = (resized.width - out_w) // 2
    top = (resized.height - out_h) // 2
    return resized.crop((left, top, left + out_w, top + out_h))


def _make_title_png(text: str, out_path: Path, font_size=64, photo_path: str | None = None,
                     photo_img: Image.Image | None = None) -> int:
    """영상 상단을 가로로 꽉 채우는 후킹 배너. WHY: 작은 알약 모양 라벨은 존재감이
    약해서 스크롤 중 3초컷으로 넘어가는 문제를 못 막는다(2026-07-30 피드백) —
    화면 가로 전체를 덮는 굵은 배너로 바꾸고, 텍스트도 카테고리 라벨이 아니라
    후킹 문구(공감/호기심 유발)를 넣는다. 반환값(배너 높이)은 다른 오버레이가
    이 배너와 겹치지 않게 배치할 때 쓴다.

    WHY photo_path(2026-08-02, "분홍색 바탕 없애도 되고 바탕으로는 그 항목에 대한
    real 이미지를 흐린 색으로"): 단색 배경 대신 topic 대표 실사진을 배너 폭에 맞게
    확대·크롭해서 깐 뒤 반투명 스크림을 얹는다. photo_path가 없으면 기존 단색 배경으로
    폴백한다.

    WHY photo_img(2026-08-02, "배경으로 넣는 real 사진을 글자 뒤에있는거랑 칠판
    이미지 아래위랑 따로따로 넣어놨나보네?? 한 사진으로 해서... 지금은 뭔가 따로따로
    짤려보이잖아"): 배너와 칠판 배경(_build_chalkboard_bg)이 각자 photo_path로
    독립적으로 cover-crop을 하면 서로 다른 배율/영역으로 잘려서 이어지는 사진처럼
    안 보이는 문제가 있었다 — assemble()이 캔버스 전체(W x H) 크기로 미리 한 번만
    만든 배경 이미지를 photo_img로 넘기면, 배너는 그 이미지의 위쪽 box_h만큼만
    잘라 쓴다(같은 사진·같은 배율의 연속된 한 조각). photo_img가 있으면 photo_path는
    무시한다."""
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    max_text_w = W - 140
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_text_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_h = font_size + 16
    # WHY 위쪽 여백만 한 줄 높이(2026-08-02, "맨 위에있는 글자 한 줄만큼은 여백이
    # 생겨야 해"): 대칭 패딩(pad_y*2)이었을 땐 텍스트가 배너 상단에 너무 붙어 보였다
    # — 위쪽만 line_h만큼 비우고 아래쪽은 기존 여백을 유지한다. 배경 사진(box_h 전체)은
    # 그대로 화면 맨 위(y=0)부터 꽉 채우므로 이 여백은 사진 안쪽의 빈 공간일 뿐,
    # 사진 자체가 아래로 밀리는 게 아니다.
    pad_top = line_h
    pad_bottom = 30
    box_h = pad_top + line_h * len(lines) + pad_bottom

    has_photo = photo_img is not None or photo_path
    if has_photo:
        photo = photo_img.crop((0, 0, W, box_h)) if photo_img is not None else _cover_crop_subject(photo_path, W, box_h)
        # WHY 스크림 유지(2026-08-02): "opacity 없애라"는 지적은 칠판 뒤 전체화면
        # 배경(_build_chalkboard_bg)을 가리킨 것이었는데, 그때 배너의 텍스트
        # 가독성용 검은 저알파 스크림까지 같이 빼버렸다가 "위쪽 글자 배경 색상을
        # 왜 지웠냐, 그건 필요하다"는 지적을 받고 되돌렸다 — 배너는 스크림 유지,
        # 칠판 뒤 전체화면 배경만 스크림/블러 없이 원본 그대로 쓴다.
        scrim = Image.new("RGBA", (W, box_h), (0, 0, 0, 90))
        img = Image.alpha_composite(photo.convert("RGBA"), scrim)
    else:
        img = Image.new("RGBA", (W, box_h), (200, 74, 98, 240))
    draw = ImageDraw.Draw(img)
    y = pad_top
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) / 2 - bbox[0]
        if has_photo:
            draw.text((x, y - bbox[1]), line, font=font, fill=(255, 255, 255, 255),
                       stroke_width=3, stroke_fill=(0, 0, 0, 255))
        else:
            draw.text((x, y - bbox[1]), line, font=font, fill=(255, 255, 255, 255))
        y += line_h
    img.save(out_path)
    return box_h


def _make_title_card_png(text: str, out_path: Path, font_size=88, char_path: str | None = None):
    """영상 맨 앞에 붙는 단색 배경 + 큰 제목 카드. WHY: 플랫폼이 썸네일을 영상
    첫 프레임으로 자동 지정하는 경우가 많아서, 이 카드 자체를 그대로 썸네일로
    쓸 수 있게 글자를 크고 굵게, 배경은 단색으로 단순하게 만든다.

    WHY char_path(2026-07-31, "캐릭터를 큼직하고 흐리게 글자의 배경으로"): 순수
    단색 배경 대신, 캐릭터 이미지를 캔버스보다 훨씬 크게 확대·크롭해서 흐리게 깐
    뒤 ACCENT 톤 스크림을 얹는다 — 브랜드 컬러는 유지하면서 캐릭터가 은은하게
    느껴지는 배경 무드를 만든다."""
    img = Image.new("RGB", (W, H), (200, 74, 98))
    if char_path:
        target = int(H * 1.15)
        char = Image.open(char_path).convert("RGB").resize((target, target))
        char = char.filter(ImageFilter.GaussianBlur(25))
        left, top = (target - W) // 2, (target - H) // 2
        char = char.crop((left, top, left + W, top + H))
        scrim = Image.new("RGBA", (W, H), (200, 74, 98, 150))
        img = Image.alpha_composite(char.convert("RGBA"), scrim).convert("RGB")
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
    draw = ImageDraw.Draw(img)
    max_text_w = W - 160
    words, lines, cur = text.split(), [], ""
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

    line_h = font_size + 26
    total_h = line_h * len(lines)
    y = (H - total_h) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2 - bbox[0], y - bbox[1]), line, font=font, fill=(255, 255, 255))
        y += line_h
    img.save(out_path)


def _make_caption_png(text: str, out_path: Path, font_size=60, max_width=940):
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_heights, max_w = [], 0
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
        max_w = max(max_w, bbox[2] - bbox[0])

    pad_x, pad_y, gap = 30, 18, 8
    box_w, box_h = max_w + pad_x * 2, sum(line_heights) + gap * (len(lines) - 1) + pad_y * 2
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, box_w, box_h], radius=16, fill=(0, 0, 0, 165))
    y = pad_y
    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (box_w - w) / 2 - bbox[0]
        draw.text((x, y - bbox[1]), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        y += lh + gap
    img.save(out_path)


def _make_chalk_caption_png(text: str, out_path: Path, font_size=68, max_width=940):
    """칠판 배경용 자막(2026-08-02). _make_caption_png와 달리 반투명 박스가 없다 —
    배경 자체가 이미 짙은 칠판색이라 박스를 얹으면 이중으로 어두워지고 사진 위에
    붙인 스티커 같은 느낌만 준다. 대신 Gaegu(분필/마카 느낌 폰트)로 흰 글자를
    직접 쓰고, 옅은 그림자만 살짝 깔아서 배경 톤이 조금 밝은 부분에서도 읽히게 한다."""
    font = ImageFont.truetype(CHALK_FONT_PATH, font_size)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_heights, max_w = [], 0
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
        max_w = max(max_w, bbox[2] - bbox[0])

    pad, gap = 20, 14
    img_w, img_h = max_w + pad * 2, sum(line_heights) + gap * (len(lines) - 1) + pad * 2
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = pad
    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (img_w - w) / 2 - bbox[0]
        draw.text((x + 3, y - bbox[1] + 3), line, font=font, fill=(0, 0, 0, 110))  # 옅은 그림자
        draw.text((x, y - bbox[1]), line, font=font, fill=(255, 255, 255, 255))
        y += lh + gap
    img.save(out_path)


# WHY 칠판 우상단 아이템 라벨(2026-08-02, "칠판 우상단에 멈춰있는 일러스트와 그
# 아래에 그 아이템의 이름을 함께 넣어줘야해" — 코너의 움직이는 캐릭터만으로는
# "이게 뭔지 사람들이 인지 잘 못할듯"하다는 지적): 카드뉴스의 원형 배지(카드뉴스
# `_char_medallion`)와 톤을 맞춘 정지 아이콘(흰 링 + 그림자) + 그 아래 분필체
# 이름 라벨을 만든다 — 카드뉴스는 자체 함수가 따로 있어(캔버스 크기·색상 상수가
# 다름) 그대로 import하지 않고 이 모듈 안에서 동일한 스타일을 재구현했다.
def _make_item_label_png(illust_path: str | None, name: str, out_path: Path,
                          icon_size: int = 108, font_size: int = 40) -> None:
    ring_w = 6
    pad = ring_w + 10
    icon_canvas = icon_size + pad * 2

    if illust_path and Path(illust_path).exists():
        raw = Image.open(illust_path).convert("RGB").resize((icon_size, icon_size))
        raw = raw.convert("RGBA")
        # WHY 자동 키 색 감지(2026-08-01 card_news.py 동일 이유): 캐릭터 배경
        # 크로마키가 초록/파랑/마젠타 등 topic마다 다를 수 있어 모서리 픽셀을
        # 실제 배경색으로 채택한다.
        key = raw.getpixel((2, 2))[:3]
        kr, kg, kb = key
        px = raw.load()
        for yy in range(raw.height):
            for xx in range(raw.width):
                r, g, b, a = px[xx, yy]
                if abs(r - kr) + abs(g - kg) + abs(b - kb) < 160:
                    px[xx, yy] = (r, g, b, 0)
        mask = Image.new("L", (icon_size, icon_size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, icon_size, icon_size), fill=255)
        combined_mask = ImageChops.multiply(raw.split()[3], mask)
        icon = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))
        icon.paste(raw, (0, 0), combined_mask)
    else:
        icon = None

    icon_img = Image.new("RGBA", (icon_canvas, icon_canvas), (0, 0, 0, 0))
    shadow = Image.new("RGBA", icon_img.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        [pad - 3, pad + 6, pad + icon_size + 3, pad + icon_size + 12], fill=(0, 0, 0, 90))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    icon_img = Image.alpha_composite(icon_img, shadow)
    idraw = ImageDraw.Draw(icon_img)
    idraw.ellipse([pad - ring_w, pad - ring_w, pad + icon_size + ring_w, pad + icon_size + ring_w],
                  fill=(255, 255, 255, 255))
    if icon is not None:
        icon_img.paste(icon, (pad, pad), icon)

    font = ImageFont.truetype(CHALK_FONT_PATH, font_size)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    bbox = d.textbbox((0, 0), name, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    canvas_w = max(icon_canvas, text_w + 20)
    gap = 8
    canvas_h = icon_canvas + gap + text_h + 10
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    canvas.alpha_composite(icon_img, ((canvas_w - icon_canvas) // 2, 0))
    draw = ImageDraw.Draw(canvas)
    tx = (canvas_w - text_w) / 2 - bbox[0]
    ty = icon_canvas + gap - bbox[1]
    draw.text((tx + 2, ty + 2), name, font=font, fill=(0, 0, 0, 130))
    draw.text((tx, ty), name, font=font, fill=(255, 255, 255, 255))
    canvas.save(out_path)


# WHY 칠판 모서리 낙서(2026-08-02, "파츠같은거 귀여운거 랜덤으로 칠판 모서리쪽에
# 추가하는게 어떨까 싶어 너무 휑하고 별로야"): 칠판 배경이 실사진 그대로라 텍스트가
# 없는 구간이 휑하다는 지적 — 실제 이미지 생성 없이 PIL 도형만으로 그린 작은
# 분필 낙서(별·하트·반짝임·음표·스마일리)를 캡션과 같은 흰색+옅은 그림자 톤으로
# 그려서 칠판 모서리에 하나씩 얹는다. `_stroke_shape`가 캡션과 동일한 그림자 기법
# (오프셋 +3,+3, 검정 alpha 110)을 재사용해서 톤을 맞춘다.
_DOODLE_SIZE = 130


def _doodle_canvas() -> Image.Image:
    return Image.new("RGBA", (_DOODLE_SIZE, _DOODLE_SIZE), (0, 0, 0, 0))


def _stroke_shape(draw_fn) -> Image.Image:
    shadow = _doodle_canvas()
    draw_fn(ImageDraw.Draw(shadow), (3, 3), (0, 0, 0, 110))
    img = _doodle_canvas()
    draw_fn(ImageDraw.Draw(img), (0, 0), (255, 255, 255, 255))
    return Image.alpha_composite(shadow, img)


def _doodle_star() -> Image.Image:
    cx, cy, r_outer, r_inner = _DOODLE_SIZE / 2, _DOODLE_SIZE / 2, 46, 19
    pts = []
    for i in range(10):
        ang = math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        pts.append((cx + r * math.cos(ang), cy - r * math.sin(ang)))

    def draw(d, off, color):
        p = [(x + off[0], y + off[1]) for x, y in pts]
        d.line(p + [p[0]], fill=color, width=5, joint="curve")

    return _stroke_shape(draw)


def _doodle_heart() -> Image.Image:
    def draw(d, off, color):
        ox, oy = off
        d.arc([20 + ox, 15 + oy, 68 + ox, 63 + oy], 130, 360, fill=color, width=5)
        d.arc([62 + ox, 15 + oy, 110 + ox, 63 + oy], 180, 50, fill=color, width=5)
        d.line([(21 + ox, 40 + oy), (65 + ox, 105 + oy)], fill=color, width=5, joint="curve")
        d.line([(109 + ox, 40 + oy), (65 + ox, 105 + oy)], fill=color, width=5, joint="curve")

    return _stroke_shape(draw)


def _doodle_sparkle() -> Image.Image:
    def draw(d, off, color):
        cx, cy = _DOODLE_SIZE / 2 + off[0], _DOODLE_SIZE / 2 + off[1]
        for ang in (0, 90, 180, 270):
            rad = math.radians(ang)
            x2, y2 = cx + 42 * math.cos(rad), cy + 42 * math.sin(rad)
            d.line([(cx, cy), (x2, y2)], fill=color, width=5)
        for ang in (45, 135, 225, 315):
            rad = math.radians(ang)
            x2, y2 = cx + 20 * math.cos(rad), cy + 20 * math.sin(rad)
            d.line([(cx, cy), (x2, y2)], fill=color, width=4)

    return _stroke_shape(draw)


def _doodle_note() -> Image.Image:
    def draw(d, off, color):
        ox, oy = off
        d.ellipse([20 + ox, 78 + oy, 46 + ox, 100 + oy], outline=color, width=5)
        d.line([(44 + ox, 89 + oy), (44 + ox, 25 + oy)], fill=color, width=5)
        d.line([(44 + ox, 25 + oy), (78 + ox, 35 + oy)], fill=color, width=5, joint="curve")
        d.line([(78 + ox, 35 + oy), (78 + ox, 55 + oy)], fill=color, width=5)

    return _stroke_shape(draw)


def _doodle_smiley() -> Image.Image:
    def draw(d, off, color):
        ox, oy = off
        d.ellipse([15 + ox, 15 + oy, 115 + ox, 115 + oy], outline=color, width=5)
        d.ellipse([42 + ox, 48 + oy, 52 + ox, 58 + oy], fill=color)
        d.ellipse([78 + ox, 48 + oy, 88 + ox, 58 + oy], fill=color)
        d.arc([40 + ox, 55 + oy, 90 + ox, 90 + oy], 20, 160, fill=color, width=5)

    return _stroke_shape(draw)


_DOODLES = [_doodle_star, _doodle_heart, _doodle_sparkle, _doodle_note, _doodle_smiley]

# WHY 실측 상수(2026-08-02): 칠판.png(1024x1024)에서 초록 판서면이 실제로 시작/끝나는
# y좌표를 픽셀 스캔으로 구함(위/아래 흰 여백·나무 프레임을 제외한 순수 판서면 범위).
# 이 사진 자체를 바꾸지 않는 한 다시 잴 필요 없음 — CHALKBOARD_CROP_LEFT/RIGHT와
# 같은 성격의 상수.
_CHALKBOARD_GREEN_TOP_ORIG = 142
_CHALKBOARD_GREEN_BOTTOM_ORIG = 866

# WHY 옛날 교실 감성 문구(2026-08-02, "옛날 감성나는 칠판 주번... 그런것들 들어가면
# 딱 좋을거같아서"): 실존 인물을 가리키지 않는 흔한 조합 이름(가상의 "홍길동"류)만
# 골라서, 실제 학급 게시물처럼 보이는 작은 명패를 왼쪽 아래 모서리에 하나 얹는다.
_JUBAN_NAMES = ["김민지", "이준서", "박서연", "최도윤", "정하은", "강지호", "윤서아", "임하준"]


def _doodle_juban_box(name: str) -> Image.Image:
    """분필체로 "주번 OOO" 글자를 얇은 사각 테두리로 감싼 작은 명패 — 실제 교실
    칠판 모서리에 붙던 주번 표시판을 흉내낸다."""
    text = f"주번 {name}"
    font = ImageFont.truetype(CHALK_FONT_PATH, 30)
    pad_x, pad_y = 16, 10
    dummy = Image.new("RGBA", (1, 1))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    box_w, box_h = tw + pad_x * 2, th + pad_y * 2

    def draw(d, off, color):
        ox, oy = off
        d.rectangle([2 + ox, 2 + oy, box_w - 2 + ox, box_h - 2 + oy], outline=color, width=3)
        d.text((pad_x - bbox[0] + ox, pad_y - bbox[1] + oy), text, font=font, fill=color)

    shadow = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw(ImageDraw.Draw(shadow), (2, 2), (0, 0, 0, 100))
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw(ImageDraw.Draw(img), (0, 0), (255, 255, 255, 255))
    return Image.alpha_composite(shadow, img)


def _place_chalk_doodle(canvas: Image.Image, seed: str, top_pad: int, per_corner: int = 2) -> Image.Image:
    """칠판 판서면 위쪽 양쪽 모서리에 낙서를 여러 개(기본 한쪽당 2개) 흩뿌리고,
    왼쪽 아래 모서리엔 "주번 OOO" 명패를 하나 얹는다.

    WHY 위쪽 모서리로만 도형을 흩뿌리는지: 자막은 판서면 세로 중앙에, 캐릭터는
    항상 오른쪽 아래 모서리에 나온다 — 왼쪽/오른쪽 위 모서리는 이 topic이 몇
    초짜리든, 자막이 몇 줄이든 겹칠 일이 없는 유일한 안전 지대다.
    WHY 처음엔 한쪽에 하나였다가 늘렸는지(2026-08-02, "좀 많았으면 하는데...
    너무 적은데 오히려 좀 더 화려하게 갔으면 싶어"): 실제 영상으로 보니 낙서
    하나로는 휑함이 거의 안 가려졌다 — 양쪽 모서리에 서로 다른 도형을 2개씩
    묶어서(겹침 방지 로직 포함) 훨씬 장식적으로 만들었다.
    WHY 왼쪽 아래에 "주번" 명패를 추가로 얹는지(2026-08-02, "옛날 감성나는 칠판
    주번... 그런것들 들어가면 딱 좋을거같아서"): 실제 교실 칠판 느낌을 살리는
    포인트 — 캐릭터가 항상 오른쪽 아래에 있어서 왼쪽 아래는 비어있는 유일한
    하단 모서리다. 판서면 세로 중앙의 자막과 겹치지 않게 판서면 맨 아래쪽 끝에
    바짝 붙여서 배치한다.
    WHY seed로 topic을 쓰는지: 같은 topic을 재조립해도 매번 낙서·명패 이름이
    안 바뀌게(재현 가능) — card_news.py의 _photo_backdrop과 같은 패턴."""
    rng = random.Random(seed)
    cropped_w = CHALKBOARD_CROP_RIGHT - CHALKBOARD_CROP_LEFT
    scale = (W / cropped_w) * CHALKBOARD_ZOOM
    green_top_canvas = round(top_pad + _CHALKBOARD_GREEN_TOP_ORIG * scale)
    green_bottom_canvas = round(top_pad + _CHALKBOARD_GREEN_BOTTOM_ORIG * scale)

    zone_w, zone_h, top_gap = 260, 220, 20
    for side in ("left", "right"):
        shapes = rng.sample(_DOODLES, min(per_corner, len(_DOODLES)))
        placed: list[tuple[float, float]] = []
        for fn in shapes:
            lx = ly = 0
            doodle = None
            for _attempt in range(12):
                size = rng.randint(55, 85)
                doodle = fn().resize((size, size))
                angle = rng.uniform(-18, 18)
                doodle = doodle.rotate(angle, expand=True, resample=Image.BICUBIC)
                lx = rng.randint(0, max(zone_w - doodle.width, 0))
                ly = rng.randint(0, max(zone_h - doodle.height, 0))
                cx, cy = lx + doodle.width / 2, ly + doodle.height / 2
                if all(((cx - px) ** 2 + (cy - py) ** 2) ** 0.5 > 55 for px, py in placed):
                    placed.append((cx, cy))
                    break
            x = 25 + lx if side == "left" else W - zone_w - 25 + lx
            y = green_top_canvas + top_gap + ly
            canvas.alpha_composite(doodle, (x, y))

    juban = _doodle_juban_box(rng.choice(_JUBAN_NAMES))
    juban_x, juban_y = 30, green_bottom_canvas - juban.height - 30
    canvas.alpha_composite(juban, (juban_x, juban_y))
    return canvas


def _build_character_segment(motion_path: str, duration: float, out_path: Path, bg_color: str = "0xFFFFFF"):
    """_build_character_loop의 단일 세그먼트 버전 — 캐릭터 여러 명이 구간별로
    번갈아 나오는 _build_character_schedule에서 재사용한다."""
    similarity = "0.03" if bg_color.upper() == "0XFFFFFF" else "0.15"
    despill = ""
    if bg_color.upper() == "0X00FF00":
        despill = "despill=type=green:mix=1.0:expand=0,"
    elif bg_color.upper() == "0X0000FF":
        despill = "despill=type=blue:mix=1.0:expand=0,"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        keyed = tmp_path / "keyed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", motion_path,
             "-vf", f"colorkey={bg_color}:{similarity}:{similarity},{despill}format=argb,"
                    "lut=a='if(gt(val\\,16)\\,255\\,0)'",
             "-c:v", "qtrle", str(keyed)],
            check=True, capture_output=True,
        )
        reversed_ = tmp_path / "reversed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(keyed), "-vf", "reverse", "-c:v", "qtrle", str(reversed_)],
            check=True, capture_output=True,
        )
        pingpong = tmp_path / "pingpong.mov"
        list_path = tmp_path / "pp_list.txt"
        list_path.write_text(f"file '{keyed.resolve()}'\nfile '{reversed_.resolve()}'")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(pingpong)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(pingpong),
             "-t", f"{duration}", "-c:v", "qtrle", str(out_path)],
            check=True, capture_output=True,
        )


def _build_character_schedule(
    schedule: list[tuple[float, float, str]] | list[tuple[float, float, str, str]],
    total_duration: float, out_path: Path, bg_color: str = "0xFFFFFF",
):
    """캐릭터 여러 명이 구간별로 번갈아 나오는 캐릭터 트랙. WHY(2026-07-31, 수면음식_1
    — 대추/체리/호두 세 캐릭터가 각자 자기 대사 구간에만 나와야 하는데
    _build_character_loop은 캐릭터 1개를 전체 길이에 반복하는 구조라 못 씀):
    schedule의 각 구간마다 _build_character_segment로 개별 캐릭터 트랙을 만들고
    concat으로 이어붙인다. 각 세그먼트는 독립적으로 ping-pong 처리되므로 세그먼트
    경계에서도 포즈가 끊기지 않는다.

    WHY 세그먼트별 bg_color(2026-08-01, 갑상선방해음식_1/위장더부룩음식_1에서 실제
    발생 — 초록 계열 캐릭터라 파란 배경으로 생성한 일러스트(케일·페퍼민트차 등)가
    섞인 topic에서 전체에 초록 colorkey를 쓰면 파란 배경이 그대로 남는 사고): 튜플이
    (start, end, path) 3개면 전역 bg_color를, (start, end, path, bg_color) 4개면
    그 세그먼트 전용 색을 쓴다 — 캐릭터마다 크로마키 색이 다른 topic(초록/파랑 섞임)을
    지원하기 위함."""
    schedule = sorted(schedule, key=lambda x: x[0])
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seg_paths = []
        for i, entry in enumerate(schedule):
            start, end, motion_path = entry[0], entry[1], entry[2]
            seg_bg_color = entry[3] if len(entry) > 3 else bg_color
            dur = min(end, total_duration) - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"char_seg_{i:03d}.mov"
            _build_character_segment(motion_path, dur, seg, bg_color=seg_bg_color)
            seg_paths.append(seg)
        list_path = tmp_path / "char_list.txt"
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(out_path)],
            check=True, capture_output=True,
        )


def _build_character_loop(motion_path: str, total_duration: float, out_path: Path, bg_color: str = "0xFFFFFF"):
    """Kling 모션 클립(단색 배경)에서 배경을 알파로 빼고, 대사 길이만큼 반복시킨
    알파 채널 영상(qtrle mov)을 만든다. 대사 타이밍과 동기화하지 않고 그냥 반복.

    WHY 정방향+역방향(ping-pong) 이어붙이기: Kling이 생성한 클립은 시작 포즈와
    끝 포즈가 같다는 보장이 없어서, 그냥 -stream_loop로 반복하면 루프 지점마다
    포즈가 툭 끊기는 느낌이 난다(2026-07-30 확인). 정방향 재생 뒤 바로 역방향
    재생을 이어붙이면 마지막 프레임이 항상 첫 프레임으로 대칭 복귀하므로,
    프롬프트가 끝-시작을 맞춰주길 기대하지 않아도 구조적으로 끊김이 없다.

    WHY bg_color 파라미터화 + 초록 배경 권장(2026-07-30): 흰 배경은 캐릭터 얼굴의
    밝은 하이라이트(이마·볼)까지 "흰색에 가깝다"고 오인해서 threshold를 아주 좁게
    잡아야만 했다(0.03) — 그래도 여전히 위험한 여지가 있다. gemini_illust.py의
    STYLE_PROMPT를 초록 배경(#00FF00)으로 바꿔뒀으니, 그 프롬프트로 새로 만든
    캐릭터는 bg_color="0x00FF00"로 넉넉한 threshold(0.15 정도)를 써도 안전하다.
    기존 흰 배경 캐릭터(예: 돼지감자)는 기본값 그대로 좁은 threshold 유지.

    WHY alpha 이분법 처리(2026-07-30): colorkey가 threshold 안쪽 픽셀도 완전
    불투명이 아니라 부분투명(반쯤 섞인 alpha)으로 만드는 경우가 있는데, 이게
    280px로 축소되는 코너 장면에서 배경(초록 잎)이 캐릭터 얼굴에 얼룩덜룩
    비쳐 보이는 원인이었다(세션 내내 "눈 왜곡"으로 오인했던 문제의 진짜 정체 —
    Kling 생성 결과가 아니라 이 로컬 합성 단계의 버그였음). lut=a로 alpha를
    16 기준 완전 불투명(255) 아니면 완전 투명(0)으로 강제해서 부분투명을 없앤다.

    WHY despill(2026-07-31): alpha 이분법 처리는 "안/밖"만 정하지, 안쪽으로 판정된
    가장자리 픽셀 자체의 색(그린 스크린 촬영/렌더링에서 늘 발생하는 초록 스필)은
    그대로 남는다 — 그 결과 캐릭터 테두리에 초록 형광 라인이 둘러진 것처럼 보였다
    (0x00FF00 배경으로 처음 실사용한 v8 클립에서 확인). despill로 가장자리의 잔여
    초록기를 억제한다. despill 필터는 초록/파랑만 지원해서 그 두 색일 때만 적용.

    WHY format=argb (yuva420p 아님, 2026-07-31): qtrle 인코더는 rgb24/rgb555be/argb/
    gray만 지원한다(yuva420p 미지원) — yuva420p로 지정해도 qtrle 인코딩 시 결국 argb로
    재변환되므로, 처음부터 qtrle가 실제로 쓰는 argb를 직접 지정해 불필요한 왕복 변환을
    없앤다.

    ⚠️ WHY .upper() 비교를 대문자 리터럴과 하는지: `bg_color.upper()`는 "0x00FF00"의
    "x"까지 "X"로 바꿔버려서 "0x00FF00"(소문자 x) 리터럴과 절대 같아질 수 없다 —
    이 버그 때문에 despill 분기가 조용히 한 번도 실행된 적이 없었다(2026-07-31,
    초록 배경 v8 클립에서 형광 초록 테두리가 안 없어지던 진짜 원인 — despill을
    mix=1.0까지 올려도 전혀 효과가 없었던 이유). 비교 대상 리터럴도 항상 .upper()로
    맞춰서 이 클래스의 버그가 재발하지 않게 한다."""
    similarity = "0.03" if bg_color.upper() == "0XFFFFFF" else "0.15"
    despill = ""
    if bg_color.upper() == "0X00FF00":
        despill = "despill=type=green:mix=1.0:expand=0,"
    elif bg_color.upper() == "0X0000FF":
        despill = "despill=type=blue:mix=1.0:expand=0,"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        keyed = tmp_path / "keyed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", motion_path,
             "-vf", f"colorkey={bg_color}:{similarity}:{similarity},{despill}format=argb,"
                    "lut=a='if(gt(val\\,16)\\,255\\,0)'",
             "-c:v", "qtrle", str(keyed)],
            check=True, capture_output=True,
        )
        reversed_ = tmp_path / "reversed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(keyed), "-vf", "reverse", "-c:v", "qtrle", str(reversed_)],
            check=True, capture_output=True,
        )
        pingpong = tmp_path / "pingpong.mov"
        list_path = tmp_path / "pp_list.txt"
        list_path.write_text(f"file '{keyed.resolve()}'\nfile '{reversed_.resolve()}'")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(pingpong)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(pingpong),
             "-t", f"{total_duration}", "-c:v", "qtrle", str(out_path)],
            check=True, capture_output=True,
        )


def make_gradient_bg(out_path: Path, top=(253, 249, 245), bottom=(246, 237, 230)):
    """실사진이 없는 topic용 배경. WHY(2026-07-31, 수면음식_1): 캐릭터 일러스트(크로마키
    배경 포함)를 실수로 --images 자리에 넣으면 초록 배경이 그대로 노출되는 사고가 났다
    — 실사진이 없을 땐 카드뉴스와 같은 톤의 단색 그라디언트를 배경으로 쓴다."""
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    img.save(out_path, quality=95)


CHALKBOARD_PHOTO_PATH = str(Path(__file__).resolve().parent.parent / "assets_library" / "backgrounds" / "칠판.png")
# WHY 실측 좌표를 상수로 고정(2026-08-02): 실물 칠판 사진(assets_library/backgrounds/
# 칠판.png, 1024x1024)의 좌우 흰 여백을 나무 프레임 가장자리까지 잘라내기 위해
# 픽셀을 직접 스캔해서 찾은 값 — "나무 프레임이 가로 폭에 딱맞게" 요청 반영.
# 이 배경 이미지 자체를 바꾸지 않는 한 다시 측정할 필요 없음.
CHALKBOARD_CROP_LEFT = 65
CHALKBOARD_CROP_RIGHT = 962
# WHY CHALKBOARD_ZOOM(2026-08-02, "가로는 완전 꽉차게 더 크게... 위아래로 더 키워서
# 아래 일러스트랑 위 글자 직전까지"): 위 CROP_LEFT/RIGHT만으로 너비를 캔버스에 맞추면
# 좌우에 흰 여백이 살짝 남고 세로도 다 못 채운다 — 크롭 폭보다 더 확대한 뒤 가로만
# 캔버스 폭(W)으로 중앙 크롭하면, 같은 배율로 세로도 함께 커져서 두 요청을 동시에
# 만족한다(가로는 여백 없이 꽉 참, 세로는 비례해서 더 커짐).
CHALKBOARD_ZOOM = 1.35
# WHY 위/아래 여백은 안 자르는지: 사진 원본의 흰 위쪽 여백엔 제목 배너가,
# 아래쪽 여백엔 캐릭터가 들어갈 자리라 그대로 살려둔다(사용자 요청) — 다만 세로로
# 늘려서 캔버스(1920)를 다 채우면 위아래 여백이 부족해서, 늘리는 대신 같은 톤의
# 흰색으로 캔버스 크기까지 패딩한다.
CHALKBOARD_BG_FILL = (248, 248, 248)
# WHY CHALKBOARD_CONTENT_BOTTOM(2026-08-02, "칠판을 아예 맨 아래까지 내리고... 그
# 어떤 필요로 하는 아이템을... 넣는게"): 칠판 사진 원본(1024 세로)은 나무 받침대
# 아래로 흰 촬영 배경이 ~924px까지 이어지는데, photo_bg_img 합성 시 이 흰 여백이
# 투명 처리되면서 실사진이 그대로 비쳐 보였다 — "도움이 되는 항목이 화면에 안
# 뜬다"는 지적대로, 이 틈이 정보 없이 방해만 됐다. 실측(픽셀 스캔)으로 프레임+
# 받침대가 끝나는 지점을 찾은 값 — 이 지점 아래는 칠판 톤 단색으로 채워서 판서면이
# 화면 맨 아래까지 이어지는 것처럼 보이게 한다(이 배경 이미지를 바꾸지 않는 한
# 다시 측정할 필요 없음).
CHALKBOARD_CONTENT_BOTTOM = 924
# WHY 폴백값으로만 남김(2026-08-02): 원래는 고정 상수로 썼지만, 상단 배너 높이가
# 제목 줄 수에 따라 달라져서(1줄 vs 2줄) 고정값이면 배너 아래로 흰 틈이 남거나
# 배너와 겹치는 경우가 생겼다 — assemble()이 실제 배너 높이(title_h)를
# _build_chalkboard_bg(top_pad=title_h)로 넘겨서 항상 배너 바로 아래부터 칠판이
# 시작하게 한다. top_pad를 명시하지 않고 이 함수를 단독 호출할 때만 이 기본값을 쓴다.
CHALKBOARD_TOP_PAD = 220


def _chalkboard_display_height() -> int:
    """실제 렌더링되는 칠판 사진의 세로 픽셀 높이(캔버스 폭 W, CHALKBOARD_ZOOM
    배율 적용 후) — _build_chalkboard_bg와 동일한 크롭/스케일 계산을 반복해서
    구한다. WHY 필요한지(2026-08-02, "글이 너무 아래로 쏠려있잖아 칠판 기준으로
    중앙으로"): 자막을 칠판 영역 안에서 세로 중앙 정렬하려면 칠판이 화면에서 실제로
    차지하는 세로 범위를 알아야 한다."""
    photo = Image.open(CHALKBOARD_PHOTO_PATH).convert("RGB")
    cropped_width = CHALKBOARD_CROP_RIGHT - CHALKBOARD_CROP_LEFT
    scale = (W / cropped_width) * CHALKBOARD_ZOOM
    return round(photo.height * scale)


def _build_chalkboard_bg(total_duration: float, out_path: Path, top_pad: int | None = None,
                          photo_bg_path: str | None = None, photo_bg_img: Image.Image | None = None,
                          doodle_seed: str | None = None):
    """칠판 스타일 기본 배경(2026-08-02, 실물 칠판 사진으로 교체). 좌우 흰 여백을
    나무 프레임 가장자리까지 잘라서 프레임이 가로 폭에 꽉 차게 만들고, 위아래는
    원본 비율 그대로 살린 뒤 부족한 높이만큼 같은 톤의 흰색으로 패딩해서 캔버스를
    채운다 — 위쪽 흰 여백엔 제목 배너, 아래쪽 흰 여백엔 캐릭터가 들어간다.

    WHY 완전 정적(2026-08-02, "왜 칠판이 움직여 ;; 이제 칠판은 가만있고 자막만
    들어가면 되는거지"): 처음엔 실사진 배경과 통일감을 주려고 미세 zoompan을
    넣었는데, 칠판은 자막을 얹는 고정 판서면이라 배경 자체가 계속 확대되면
    산만하다는 피드백 — zoompan을 빼고 완전히 고정된 한 프레임을 총 길이만큼
    그대로 유지한다.

    WHY photo_bg_path + 흰색 키잉(2026-08-02, "칠판 뒤에 배경에 전체 화면을
    가득채우게 real에서 해당 아이템을 넣어... 흰색 공간이랑 글자같은거 뒤에서
    보일수 있게"): topic 대표 실사진을 캔버스 전체에 깔고, 칠판 사진 자체의 촬영
    배경(흰 벽/바닥 — 초록 판서면·나무 프레임 밖 여백)만 투명 처리해서 그 위에
    얹는다. 초록 판서면·나무 프레임은 흰색과 색이 뚜렷이 달라서 그대로 남고, 흰
    여백 자리에만 실사진이 비친다.

    ⚠️ **흰색 블렌드도, 블러도 뺌**(2026-08-02, "흰색 저게 그림을 가리고있는거같잖아
    ... opacity 안줘도 되겠다" → 블러 32도 여전히 "opacity 계속 넣네"로 재지적 →
    "opacity 아예 없애"): 처음엔 흰 배경과 80:20 블렌드를 넣었다가 뺐는데, 그 다음
    단계였던 강한 블러(card_news.py `_photo_backdrop`과 동일한 32)조차 사진을 흐릿하게
    만들어서 마치 opacity가 낮은 것처럼 보인다는 지적을 받았다 — 블러를 완전히 빼고
    실사진을 그대로(선명하게) 쓴다. 흐림 효과 자체를 이 배경에는 아예 쓰지 않는다.

    WHY photo_bg_img(2026-08-02, "배너랑 칠판 아래위 사진이 따로따로 짤려보이잖아"):
    배너(_make_title_png)와 여기가 각자 photo_bg_path로 독립적인 cover-crop을 하면
    서로 다른 배율/영역이 잘려서 이어지는 사진처럼 안 보인다 — assemble()이 캔버스
    전체(W x H) 크기로 미리 한 번만 만든 이미지를 photo_bg_img로 넘기면, 배너와
    여기 둘 다 같은 이미지의 위/아래 조각을 잘라 쓰게 되어 하나로 이어져 보인다.
    photo_bg_img가 있으면 photo_bg_path는 무시한다.

    WHY doodle_seed(2026-08-02, "파츠같은거 귀여운거 랜덤으로 칠판 모서리쪽에
    추가하는게 어떨까 싶어 너무 휑하고 별로야"): 판서면 위쪽 모서리에 작은 분필
    낙서를 하나 얹어서 빈 배경이 휑해 보이는 걸 덜어낸다 — `_place_chalk_doodle`
    참고. 안 주면(기존 호출부·테스트 호환) 낙서 없이 그대로."""
    with tempfile.TemporaryDirectory() as tmp:
        photo = Image.open(CHALKBOARD_PHOTO_PATH).convert("RGB")
        cropped = photo.crop((CHALKBOARD_CROP_LEFT, 0, CHALKBOARD_CROP_RIGHT, photo.height))
        scale = (W / cropped.width) * CHALKBOARD_ZOOM
        resized = cropped.resize((round(cropped.width * scale), round(cropped.height * scale)))
        left = (resized.width - W) // 2
        resized = resized.crop((left, 0, left + W, resized.height))

        effective_top_pad = CHALKBOARD_TOP_PAD if top_pad is None else top_pad
        effective_top_pad = min(effective_top_pad, max(H - resized.height, 0))

        if photo_bg_img is not None or photo_bg_path:
            photo_full = photo_bg_img if photo_bg_img is not None else _cover_crop_subject(photo_bg_path, W, H)
            canvas = photo_full.convert("RGBA")

            r, g, b = resized.split()
            thresh = 225

            def _white_band(band):
                return band.point(lambda x: 255 if x >= thresh else 0)

            white_mask = ImageChops.multiply(ImageChops.multiply(_white_band(r), _white_band(g)), _white_band(b))
            board_alpha = ImageChops.invert(white_mask)
            resized_rgba = resized.convert("RGBA")
            resized_rgba.putalpha(board_alpha)
            canvas.alpha_composite(resized_rgba, (0, effective_top_pad))
            canvas = canvas.convert("RGB")

            # WHY 받침대 아래를 칠판 톤으로 채우는지: 위 board_alpha가 원본 사진의
            # 흰 촬영 배경(나무 받침대 아래 CHALKBOARD_CONTENT_BOTTOM~1024px 구간)을
            # 투명 처리해서 실사진이 그대로 비쳤다 — 그 자리를 칠판 하단색으로 덮어서
            # 판서면이 화면 끝까지 이어지는 것처럼 보이게 한다.
            board_bottom_y = effective_top_pad + round(CHALKBOARD_CONTENT_BOTTOM * scale)
            if board_bottom_y < H:
                fill = Image.new("RGB", (W, H - board_bottom_y), CHALKBOARD_BOTTOM)
                canvas.paste(fill, (0, board_bottom_y))
        else:
            canvas = Image.new("RGB", (W, H), CHALKBOARD_BG_FILL)
            canvas.paste(resized, (0, effective_top_pad))

        if doodle_seed:
            canvas = _place_chalk_doodle(canvas.convert("RGBA"), doodle_seed, effective_top_pad).convert("RGB")

        still = Path(tmp) / "chalkboard.jpg"
        canvas.save(still, quality=95)

        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(still), "-t", f"{total_duration}",
             "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
            check=True, capture_output=True,
        )


def _build_background(images: list[str], total_duration: float, out_path: Path, xfade_dur: float = 0.7):
    """실사진 슬라이드쇼 배경. WHY 크로스페이드: 이전엔 concat demuxer로 하드컷만
    이어붙여서 사진이 바뀔 때마다 뚝뚝 끊기는 느낌이었다(2026-07-30 피드백: "좀더
    끊김없이 계속 움직일 수 있도록") — xfade로 디졸브 전환을 넣어 계속 움직이는
    느낌을 유지한다. 이미지가 4장 정도로 적어서 xfade 체인이 성능 문제는 없음
    (수백 개 세그먼트를 잇는 것과는 다른 케이스 — cat-fight 교훈은 여기 해당 안 됨)."""
    n = len(images)
    seg_dur = (total_duration + (n - 1) * xfade_dur) / n if n > 1 else total_duration
    frames = max(int(seg_dur * FPS), 1)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seg_paths = []
        for i, img in enumerate(images):
            seg = tmp_path / f"bg_{i:03d}.mp4"
            vf = (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"zoompan=z='min(zoom+0.0010,1.10)':d={frames}:s={W}x{H}:fps={FPS}"
            )
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{seg_dur}",
                 "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)],
                check=True, capture_output=True,
            )
            seg_paths.append(seg)

        if n == 1:
            subprocess.run(["ffmpeg", "-y", "-i", str(seg_paths[0]), "-c", "copy", str(out_path)],
                            check=True, capture_output=True)
            return

        inputs = []
        for p in seg_paths:
            inputs += ["-i", str(p)]
        filters, prev = [], "0:v"
        for i in range(1, n):
            offset = i * (seg_dur - xfade_dur)
            out_label = f"vx{i}" if i < n - 1 else "vout"
            filters.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={xfade_dur}:offset={offset}[{out_label}]")
            prev = out_label
        subprocess.run(
            ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
             "-map", "[vout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
            check=True, capture_output=True,
        )


def _build_background_schedule(
    schedule: list[tuple[float, float, list[str]]], total_duration: float, out_path: Path,
):
    """배경 사진도 캐릭터처럼 구간별로 맞춰야 하는 경우(품목별 실사진이 있는 topic).
    WHY(2026-07-31, 당뇨유발음식_1 — 단팥빵 나레이션 구간에 찹쌀떡 사진이 나오는 문제
    발견): 기존 _build_background는 이미지 개수만큼 전체 길이를 균등 분할해서
    나레이션 타이밍과 무관하게 순서대로 보여줬다 — _build_character_schedule과
    동일한 패턴으로, 구간마다 그 구간에 맞는 사진(들)만 골라 별도로 배경을 만들고
    이어붙인다. 각 구간 안에 사진이 여러 장이면 그 구간 안에서만 크로스페이드된다."""
    schedule = sorted(schedule, key=lambda x: x[0])
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seg_paths = []
        for i, (start, end, imgs) in enumerate(schedule):
            dur = min(end, total_duration) - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"bg_seg_{i:03d}.mp4"
            _build_background(imgs, dur, seg)
            seg_paths.append(seg)
        list_path = tmp_path / "bg_list.txt"
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(out_path)],
            check=True, capture_output=True,
        )


def assemble(
    images: list[str] | None,
    motion_path: str | None,
    audio_path: str,
    srt_path: str,
    out_path: str,
    title: str,
    # WHY 기본값 0(2026-07-31): "5초 뒤에 옮기지 말고 처음부터 우하단에" 피드백 이후
    # 이게 표준이 됐다 — 풀스크린 인트로가 필요한 특수한 경우에만 명시적으로 넘길 것.
    intro_duration: float = 0,
    ad_tag: bool = False,
    bg_color: str = "0xFFFFFF",
    title_card_duration: float = 1.3,
    title_card_text: str | None = None,
    title_card_char_path: str | None = None,
    # WHY motion_schedule(2026-07-31, 수면음식_1 — 대추/체리/호두 세 캐릭터가 각자
    # 대사 구간에만 나와야 함): [(start, end, motion_path), ...] 형태로 주면
    # motion_path 대신 이 스케줄로 캐릭터 트랙을 만든다. 시간은 나레이션(오디오) 기준
    # 0초부터 — assemble 내부에서 제목 카드만큼 알아서 밀어준다. motion_path와
    # motion_schedule 둘 다 없으면 에러, 둘 다 있으면 motion_schedule 우선.
    motion_schedule: list[tuple[float, float, str]] | None = None,
    # WHY image_schedule(2026-07-31, 당뇨유발음식_1 — 단팥빵 나레이션 구간에 찹쌀떡
    # 사진이 나오는 문제 발견): motion_schedule과 동일한 패턴. [(start, end,
    # [이미지경로,...]), ...]로 주면 images 대신 이 스케줄로 배경을 만든다 — 품목별
    # 실사진이 있는 topic(여러 캐릭터가 번갈아 나오는 topic)은 배경도 같이 맞출 것.
    image_schedule: list[tuple[float, float, list[str]]] | None = None,
    # WHY bg_style 기본값 "chalkboard"(2026-08-02): 실사진 배경이 밋밋하고 눈에 안
    # 띈다는 피드백으로 새 topic 기본값을 카드뉴스 톤 칠판 배경+분필체 자막으로
    # 바꿨다. "photo"를 명시하면 기존 실사진 슬라이드쇼 방식(images/image_schedule
    # 필요)을 그대로 쓸 수 있다 — 과거 topic 재조립이나 특별히 실사진이 필요한
    # 경우를 위해 남겨둠.
    bg_style: str = "chalkboard",
    # WHY 기본 켜짐(2026-08-02, "숏폼 영상 마지막에 구독, 좋아요, 팔로우 요청하는
    # 글도 추가하자"): 제목 카드와 대칭으로 영상 맨 끝에 CTA 카드를 붙인다 —
    # end_card_duration=0으로 주면 완전히 끌 수 있다(기존 영상 재조립 시 굳이
    # 필요 없는 경우 등).
    end_card_duration: float = 2.0,
    end_card_text: str | None = None,
    end_card_char_path: str | None = None,
    # WHY title_banner_photo_path(2026-08-02, "분홍색 바탕 없애도 되고 바탕으로는
    # 그 항목에 대한 real 이미지를 흐린 색으로"): 상단 배너의 단색 배경을 topic
    # 대표 실사진 블러로 바꾼다. 안 주면 기존 단색 배경 그대로 폴백.
    title_banner_photo_path: str | None = None,
):
    if not motion_path and not motion_schedule:
        raise ValueError("motion_path 또는 motion_schedule 중 하나는 필요합니다")
    if bg_style not in ("chalkboard", "photo"):
        raise ValueError(f"알 수 없는 bg_style: {bg_style!r} (chalkboard 또는 photo만 가능)")
    if bg_style == "photo" and not images and not image_schedule:
        raise ValueError("bg_style='photo'면 images 또는 image_schedule 중 하나는 필요합니다")
    duration_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    total_duration = float(duration_probe.stdout.strip())

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        char_track = tmp_path / "char.mov"
        if motion_schedule:
            _build_character_schedule(motion_schedule, total_duration, char_track, bg_color=bg_color)
        else:
            _build_character_loop(motion_path, total_duration, char_track, bg_color=bg_color)

        # WHY item_schedule(2026-08-02, "그 아이템에 따라 뒤에 배경이 바꼈으면
        # 좋겠고" + "칠판 우상단에 멈춰있는 일러스트와... 이름을 함께 넣어줘야해"):
        # motion_schedule의 각 구간(캐릭터 파일 경로)에서 품목명을 추출해서, 그
        # 품목의 일러스트(assets_library/illust/<품목>_illust.jpg)와 실사진
        # (assets_library/real/<품목>_real_*.jpg)을 자동으로 찾는다. 이 스케줄을
        # 그대로 재사용해서 상단 배너 사진과 칠판 우상단 라벨 둘 다 구간마다 바꾼다
        # — 캐릭터가 이미 이 파일명 규칙(<품목>_motion.mp4)을 따르고 있어서 별도
        # 인자 없이 기존 motion_schedule만으로 유도 가능하다. 못 찾으면(예: 파일명이
        # 규칙과 다른 경우) None으로 두고 title_banner_photo_path/아이콘 없음으로
        # 자연 폴백한다.
        item_schedule: list[dict] = []
        if motion_schedule:
            for entry in motion_schedule:
                seg_start, seg_end, motion_p = entry[0], entry[1], entry[2]
                motion_p = Path(motion_p)
                base = motion_p.stem
                if base.endswith("_motion"):
                    base = base[: -len("_motion")]
                assets_root = motion_p.parent.parent
                illust_p = assets_root / "illust" / f"{base}_illust.jpg"
                real_dir = assets_root / "real"
                real_candidates = sorted(real_dir.glob(f"{base}_real_*.jpg"))
                if real_candidates:
                    real_p = real_candidates[0]
                elif (real_dir / f"{base}.jpg").exists():
                    real_p = real_dir / f"{base}.jpg"
                else:
                    real_p = None
                item_schedule.append({
                    "start": seg_start,
                    "end": seg_end,
                    "name": base,
                    "illust": str(illust_p) if illust_p.exists() else None,
                    "real_photo": str(real_p) if real_p else title_banner_photo_path,
                })

        # WHY shared_bg_photo를 여기서 한 번만 만드는지(2026-08-02, "배경으로 넣는
        # real 사진을... 한 사진으로 해서... 따로따로 짤려보이잖아"): 배너와 칠판
        # 배경이 각자 photo_path로 독립적인 cover-crop을 하면 서로 다른 배율/영역이
        # 잘려서 이어지는 사진처럼 안 보인다 — 캔버스 전체(W x H) 크기로 딱 한 번만
        # cover-crop한 뒤, 배너는 이 이미지의 위쪽 조각을, 칠판 배경은 흰 부분만
        # 투명 처리해서 전체를 재사용한다(같은 사진, 같은 배율).
        shared_bg_photo = _cover_crop_subject(title_banner_photo_path, W, H) if title_banner_photo_path else None

        # WHY 배너를 배경보다 먼저 만드는지(2026-08-02, "위아래로 더 키워서... 위
        # 글자 직전까지"): 칠판 배경의 상단 흰 패딩이 배너 높이와 정확히 맞아떨어져야
        # 배너 바로 아래부터 칠판이 시작한다(틈도 안 남고 겹치지도 않고). 배너 높이는
        # 제목 줄 수에 따라 달라지므로(1줄/2줄) 고정값 대신 실제 배너를 먼저 만들어서
        # 그 높이(title_h)를 칠판 배경 생성에 넘긴다.
        title_png = tmp_path / "title.png"
        title_h = _make_title_png(title, title_png, photo_path=title_banner_photo_path, photo_img=shared_bg_photo)

        # WHY caption_center_y(2026-08-02, "글이 너무 아래로 쏠려있잖아 칠판 기준으로
        # 중앙으로 들어가게"): 기존엔 화면 하단 기준 고정 오프셋(-620)으로 자막을
        # 앉혔는데, 칠판이 훨씬 커진 뒤로는 그 위치가 칠판 영역의 중앙이 아니라
        # 아래쪽에 치우쳐 보였다 — 칠판이 실제로 화면에서 차지하는 세로 범위
        # (title_h ~ title_h+칠판높이)의 중앙에 자막을 놓는다.
        caption_center_y = None
        if bg_style == "chalkboard":
            board_bottom = min(title_h + _chalkboard_display_height(), H)
            caption_center_y = (title_h + board_bottom) / 2

        bg = tmp_path / "bg.mp4"
        if bg_style == "chalkboard":
            _build_chalkboard_bg(total_duration, bg, top_pad=title_h, photo_bg_img=shared_bg_photo,
                                  doodle_seed=Path(out_path).stem)
        elif image_schedule:
            _build_background_schedule(image_schedule, total_duration, bg)
        else:
            _build_background(images, total_duration, bg)

        # 1) 인트로 구간: 캐릭터 크게, 중앙. WHY intro_duration<=0이면 통째로 스킵
        # (2026-07-31, "5초 뒤에 우하단으로 옮기지 말고 처음부터 우하단에 있게"):
        # 인트로 자체를 안 만들고 처음부터 코너(작게) 구간으로 시작한다.
        intro_out = None
        if intro_duration > 0:
            intro_out = tmp_path / "intro.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-t", f"{intro_duration}", "-i", str(bg),
                 "-t", f"{intro_duration}", "-i", str(char_track),
                 "-filter_complex",
                 f"[1:v]scale=760:-1[char];[0:v][char]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2-80[v]",
                 "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(intro_out)],
                check=True, capture_output=True,
            )

        # 2) 이후 구간: 캐릭터 작게, 우측 하단. WHY -140(2026-08-02, "그 일러스트는
        # 아래로 더 빼서 나무 틀에 걸치고"): 기존 -320은 캐릭터가 칠판 초록 판서면
        # 안쪽에 붕 떠 보였다 — 칠판 나무 프레임/받침대 쪽으로 더 내려서 걸쳐
        # 앉은 것처럼 보이게 오프셋을 줄였다.
        main_dur = total_duration - intro_duration
        main_out = tmp_path / "main.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{intro_duration}", "-t", f"{main_dur}", "-i", str(bg),
             "-ss", f"{intro_duration}", "-t", f"{main_dur}", "-i", str(char_track),
             "-filter_complex",
             f"[1:v]scale=280:-1[char];[0:v][char]overlay=x=main_w-overlay_w-30:y=main_h-overlay_h-140[v]",
             "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(main_out)],
            check=True, capture_output=True,
        )

        # 0) 맨 앞 제목 카드 — 단색 배경 + 큼직한 글자, 플랫폼이 영상 첫 프레임을
        # 썸네일로 자동 지정하는 경우가 많아서 이 카드 자체가 썸네일 역할도 한다.
        # WHY -r FPS(2026-07-31 버그 수정): 이 명령에 프레임레이트를 안 주면 ffmpeg가
        # image2 loop 입력에 기본 25fps를 붙이는데, main_out(bg/char 체인)은 30fps라
        # 뒤에서 -c copy로 concat할 때 두 세그먼트의 프레임레이트가 달라 타임스탬프가
        # 어긋난다. 겉보기엔 영상 길이가 실제보다 늘어나 보이고(30/25=1.2배), 캐릭터가
        # 여러 명 번갈아 나오는 영상에서는 캐릭터 전환 타이밍이 한 구간씩 밀려 보이는
        # 형태로 드러났다(수면음식_1에서 실제로 발견) — 캐릭터 1명짜리 영상에서도
        # 전체적인 자막/오디오 싱크가 미세하게 어긋나는 형태로 존재했을 가능성이 있다.
        title_card_png = tmp_path / "title_card.png"
        _make_title_card_png(title_card_text or title, title_card_png, char_path=title_card_char_path)
        title_card_out = tmp_path / "title_card.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-t", f"{title_card_duration}", "-r", str(FPS), "-i", str(title_card_png),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(title_card_out)],
            check=True, capture_output=True,
        )

        # 0-2) 맨 끝 엔딩 카드 — 제목 카드와 같은 스타일(단색+큰 글자)로 구독/좋아요/
        # 팔로우 CTA. end_card_duration=0이면 통째로 스킵(기존 인트로 스킵 패턴과 동일).
        end_card_out = None
        if end_card_duration > 0:
            end_card_png = tmp_path / "end_card.png"
            _make_title_card_png(end_card_text or DEFAULT_END_CARD_TEXT, end_card_png,
                                  char_path=end_card_char_path or title_card_char_path)
            end_card_out = tmp_path / "end_card.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-t", f"{end_card_duration}", "-r", str(FPS), "-i", str(end_card_png),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", str(end_card_out)],
                check=True, capture_output=True,
            )

        combined = tmp_path / "combined.mp4"
        list_path = tmp_path / "scenes.txt"
        scene_files = ([title_card_out] + ([intro_out] if intro_out else []) + [main_out]
                       + ([end_card_out] if end_card_out else []))
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in scene_files))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(combined)],
            check=True, capture_output=True,
        )

        # WHY video_total: 맨 앞 제목 카드 + 맨 끝 엔딩 카드가 붙어서 영상 전체
        # 길이가 나레이션 길이(total_duration)보다 길어졌다 — 이후 배너/자막 단계는
        # 전부 이 늘어난 길이 기준으로 처리해야 한다.
        video_total = title_card_duration + total_duration + end_card_duration

        # 3) 상단 후킹 배너(+ 우상단 아이템 라벨, + 필요시 광고 태그) — 전체 길이에
        # 한 번만 overlay하는 대신, item_schedule이 있으면(motion_schedule로 캐릭터
        # 여러 명이 번갈아 나오는 topic) 구간마다 다른 배너 사진 + 아이템 라벨을
        # enable=between()으로 스위칭한다. WHY -t를 이미지 입력과 출력 양쪽에 명시:
        # -loop 1 이미지 + -shortest 조합만으로는 종료를 못 잡고 무한정 도는
        # 경우가 있었다(2026-07-30) — 길이를 직접 못박아서 확실히 끝나게 한다.
        titled = tmp_path / "titled.mp4"

        # WHY enable='between(...)': 제목 카드 구간엔 이미 큼직한 훅 카피가 화면
        # 중앙에 떠 있어서 상단 배너까지 같이 뜨면 겹쳐 보인다(2026-07-31 지적) —
        # 배너는 제목 카드가 끝난 뒤부터 나온다. WHY 상한도 뒀는지(2026-08-02, 엔딩
        # 카드 추가): 엔딩 카드도 마찬가지로 CTA 문구가 중앙에 크게 뜨는데, 예전처럼
        # gte로 열어두면 배너가 엔딩 카드 구간까지 계속 떠서 겹친다 — 나레이션
        # 구간(title_card_duration ~ title_card_duration+total_duration)에서만 뜨게
        # 상한을 추가했다.
        cmd_inputs = ["-i", str(combined)]
        filter_parts = []
        current = "0:v"
        next_input_idx = 1

        def _add_input(path: Path) -> int:
            nonlocal next_input_idx
            cmd_inputs.extend(["-loop", "1", "-r", str(FPS), "-t", f"{video_total}", "-i", str(path)])
            idx = next_input_idx
            next_input_idx += 1
            return idx

        if item_schedule:
            # WHY 세그먼트별 배너+라벨(2026-08-02, "그 아이템에 따라 뒤에 배경이
            # 바꼈으면 좋겠고" + "칠판 우상단에... 이름을 함께 넣어줘야해"): 문단이
            # 아니라 캐릭터 전환 구간(item_schedule) 단위로 배너 사진과 우상단
            # 아이콘+이름을 같이 바꾼다 — 자막 세그먼트 오버레이(아래 4번)와 같은
            # enable=between() 패턴이라 별도 concat 없이 한 번의 필터그래프로 끝난다.
            for i, item in enumerate(item_schedule):
                seg_start_abs = item["start"] + title_card_duration
                seg_end_abs = item["end"] + title_card_duration
                win = f"between(t\\,{seg_start_abs}\\,{seg_end_abs})"

                banner_png = tmp_path / f"title_seg_{i:03d}.png"
                _make_title_png(title, banner_png, photo_path=item["real_photo"])
                banner_idx = _add_input(banner_png)
                nxt = f"vb{i}"
                filter_parts.append(f"[{current}][{banner_idx}:v]overlay=x=0:y=0:enable='{win}'[{nxt}]")
                current = nxt

                label_png = tmp_path / f"label_seg_{i:03d}.png"
                _make_item_label_png(item["illust"], item["name"], label_png)
                label_idx = _add_input(label_png)
                nxt = f"vl{i}"
                filter_parts.append(
                    f"[{current}][{label_idx}:v]overlay=x=main_w-overlay_w-24:y={title_h + 20}:enable='{win}'[{nxt}]")
                current = nxt
        else:
            banner_idx = _add_input(title_png)
            enable_expr = f"between(t\\,{title_card_duration}\\,{title_card_duration + total_duration})"
            nxt = "vb"
            filter_parts.append(f"[{current}][{banner_idx}:v]overlay=x=0:y=0:enable='{enable_expr}'[{nxt}]")
            current = nxt
            if ad_tag:
                ad_png = tmp_path / "ad_tag.png"
                _make_ad_tag_png(ad_png)
                ad_idx = _add_input(ad_png)
                nxt = "vad"
                filter_parts.append(
                    f"[{current}][{ad_idx}:v]overlay=x=main_w-overlay_w-20:y={title_h + 16}:enable='{enable_expr}'[{nxt}]")
                current = nxt

        filter_complex = ";".join(filter_parts)
        subprocess.run(
            ["ffmpeg", "-y", *cmd_inputs,
             "-filter_complex", filter_complex,
             "-map", f"[{current}]", "-r", str(FPS), "-t", f"{video_total}",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(titled)],
            check=True, capture_output=True,
        )
        combined = titled

        # WHY 자막 합성 전 CFR 재인코딩(2026-08-02 버그 수정): combined는 title_card_out+
        # main_out+end_card_out을 "-f concat -c copy"(스트림 복사)로 이어붙인 뒤 배너를
        # 얹은 결과라, 이어붙인 지점의 PTS/GOP 구조가 살짝 불규칙해질 수 있다 — 특히 정적인
        # 칠판 배경처럼 장면 변화가 거의 없는 구간에서 x264가 비정상적으로 긴 B-프레임
        # 체인을 잡으면, 바로 다음 자막 오버레이 단계에서 overlay 필터가 PTS를 맞추는 동안
        # 자막이 최대 1~2초 안 보이는 사고로 이어졌다(사용자가 "목소리가 자막보다 먼저
        # 나간다"로 실제 발견 — 골다공증_1의 8초 넘는 긴 자막 구간에서 재현). 자막을 얹기
        # 직전에 한 번 깨끗하게 고정 프레임레이트로 재인코딩해서 이후 모든 세그먼트 오버레이가
        # 규칙적인 프레임 구조 위에서 이뤄지게 한다.
        normalized = tmp_path / "normalized.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(combined), "-r", str(FPS), "-vsync", "cfr",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(normalized)],
            check=True, capture_output=True,
        )
        combined = normalized

        # 4) 자막 굽기 (문장 구간별로 짧게 잘라 처리 — 안전한 세그먼트 방식)
        # WHY offset: 자막 타이밍은 오디오(나레이션) 기준 0초부터라, 제목 카드만큼
        # (title_card_duration) 밀어서 실제 영상 타임라인에 맞춰야 한다.
        offset = title_card_duration
        srt_entries = _parse_srt(srt_path)
        # WHY 클램프(2026-08-02 버그 수정): 멀티보이스 TTS(synthesize_segments)로 만든
        # SRT는 문단 사이 무음 간격(SEGMENT_GAP_MS)을 누적한 타임스탬프를 쓰는데, 실제
        # 합쳐진 오디오 길이와 최대 2초 가까이 어긋나는 경우가 실제로 있었다(구내염_1
        # 등에서 확인 — SRT 마지막 자막이 63.1초인데 실제 오디오는 61.1초, 문단 6개
        # =간격 5개×0.4초=2.0초와 거의 정확히 일치). 이 어긋남 때문에 마지막 자막
        # 구간이 total_duration을 넘어 엔딩 카드 영역까지 침범해서, 마지막 자막과
        # 엔딩 카드 CTA 문구가 겹쳐 보이는 사고가 났다. SRT를 신뢰하지 않고 오디오
        # 실측 길이(total_duration, ffprobe로 직접 잰 값)를 항상 상한으로 강제한다 —
        # 어긋남이 어디서 오든(멀티보이스 gap 누적, 반올림 등) 여기서 한 번에 방어한다.
        srt_entries = [
            (start, min(end, total_duration), text)
            for start, end, text in srt_entries
            if start < total_duration
        ]
        cap_dir = tmp_path / "caps"
        cap_dir.mkdir()
        timeline, cursor = [(0.0, offset, None)], 0.0
        for start, end, text in srt_entries:
            if start > cursor + 0.05:
                timeline.append((cursor + offset, start + offset, None))
            timeline.append((start + offset, end + offset, text))
            cursor = end
        if cursor < total_duration - 0.05:
            timeline.append((cursor + offset, total_duration + offset, None))
        # WHY 엔딩 카드 구간도 세그먼트로 명시(2026-08-02): 위 세그먼트들은 전부
        # total_duration+offset(=title_card_duration+total_duration)까지만 커버한다 —
        # 엔딩 카드를 붙이면서 video_total이 그보다 길어졌는데(end_card_duration만큼)
        # 여기서 세그먼트를 안 만들면 밑에서 concat한 captioned 영상이 combined보다
        # 짧아져서 엔딩 카드 부분이 통째로 잘려나간다. 자막 없는 구간으로 명시해서
        # video_total까지 확실히 채운다.
        if end_card_duration > 0:
            timeline.append((total_duration + offset, video_total, None))

        seg_paths = []
        for i, (start, end, text) in enumerate(timeline):
            dur = end - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"cap_{i:04d}.mp4"
            if text:
                cap_png = cap_dir / f"cap_{i:04d}.png"
                if bg_style == "chalkboard":
                    _make_chalk_caption_png(text, cap_png)
                else:
                    _make_caption_png(text, cap_png)
                cap_y_expr = (
                    f"{caption_center_y}-overlay_h/2" if caption_center_y is not None
                    else "main_h-overlay_h-620"
                )
                # WHY -r 명시 + trim 필터로 전환(2026-08-02 버그 수정): 원래
                # "-ss {start} -t {dur} -i combined"(입력 단 seek)로 잘랐는데, 이 방식은
                # combined처럼 키프레임이 드문(정적인 칠판 배경이라 대부분 장면이 안 바뀜)
                # 영상에서 seek 지점 근처 프레임을 정확히 못 낼 때가 있었다 — 캐릭터/배경은
                # 이미 맞는 시점으로 나오는데 overlay되는 자막 PNG만 최대 1~2초 가까이
                # 안 보이는 사고로 이어졌다(사용자가 "목소리가 자막보다 먼저 나간다"로 실제
                # 발견, 재현 테스트로 combined 입력을 거칠 때만 재현되고 단독 오버레이는
                # 문제없음을 확인). "-i combined" 통째로 열고 trim 필터로 정확히 잘라내는
                # 방식(디코드 기반이라 느리지만 항상 정확함)으로 바꿔서 해결. 자막 PNG 루프
                # 입력에도 -r을 명시해 두 입력의 프레임레이트를 맞춘다(overlay 프레임 동기화
                # 안전장치, 위 trim 수정과는 별개 원인이었지만 같이 방어).
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(combined),
                     "-loop", "1", "-r", str(FPS), "-t", f"{dur}", "-i", str(cap_png),
                     "-filter_complex",
                     f"[0:v]trim=start={start}:duration={dur},setpts=PTS-STARTPTS[bg];"
                     f"[bg][1:v]overlay=x=(main_w-overlay_w)/2:y={cap_y_expr}[v]",
                     "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)],
                    check=True, capture_output=True,
                )
            else:
                subprocess.run(
                    ["ffmpeg", "-y", "-i", str(combined),
                     "-filter_complex", f"[0:v]trim=start={start}:duration={dur},setpts=PTS-STARTPTS[v]",
                     "-map", "[v]", "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)],
                    check=True, capture_output=True,
                )
            seg_paths.append(seg)

        cap_list = tmp_path / "cap_list.txt"
        cap_list.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths))
        captioned = tmp_path / "captioned.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cap_list),
             "-c", "copy", str(captioned)],
            check=True, capture_output=True,
        )

        # WHY adelay 대신 -shortest 안 씀: 제목 카드 구간은 무음이어야 하므로 오디오를
        # title_card_duration만큼 뒤로 민다 — 그러면 오디오 길이가 정확히 영상 길이와
        # 같아져서 -shortest로 잘라낼 필요가 없다(제목 카드가 잘려나가는 사고 방지).
        offset_ms = int(title_card_duration * 1000)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(captioned), "-i", audio_path,
             "-filter_complex", f"[1:a]adelay={offset_ms}|{offset_ms}[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             out_path],
            check=True, capture_output=True,
        )
    print(f"영상 조립 완료: {out_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--images", default=None,
                    help="쉼표로 구분된 배경용 실사진 경로들 — --bg-style photo일 때만 필요")
    p.add_argument("--bg-style", default="chalkboard", choices=["chalkboard", "photo"],
                    help="배경 스타일(2026-08-02 기본값 chalkboard로 전환) — "
                         "chalkboard: 짙은 초록 그라디언트+분필체 자막(images 불필요), "
                         "photo: 기존 실사진 슬라이드쇼(images 또는 image_schedule 필요)")
    p.add_argument("--motion", default=None, help="Kling으로 생성한 캐릭터 모션 루프 클립(흰 배경) — 캐릭터 1명짜리 topic용")
    p.add_argument("--motion-schedule", default=None,
                    help="캐릭터 여러 명이 구간별로 번갈아 나올 때 사용. "
                         "형식: 'start-end:경로,start-end:경로,...' (초 단위, 나레이션 기준 0초부터). "
                         "--motion 대신 이걸 쓰면 이 스케줄이 우선한다.")
    p.add_argument("--audio", required=True)
    p.add_argument("--srt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", required=True, help="영상 상단에 계속 표시할 주제 라벨")
    p.add_argument("--intro-duration", type=float, default=0)
    p.add_argument("--ad-tag", action="store_true", help="실제 제휴 링크를 쓰기로 확정한 경우에만 켠다")
    p.add_argument("--bg-color", default="0xFFFFFF",
                    help="캐릭터 모션 클립의 배경색(colorkey 대상) — 새 캐릭터는 0x00FF00 권장")
    p.add_argument("--title-card-duration", type=float, default=1.3,
                    help="영상 맨 앞 단색 제목 카드(썸네일용) 길이(초)")
    p.add_argument("--title-card-text", default=None,
                    help="제목 카드에만 쓸 별도 문구(안 주면 --title 그대로 사용) — "
                         "썸네일은 문제 제기 훅만, 상단 배너는 훅+주제 전체를 보여주고 싶을 때 분리")
    p.add_argument("--title-card-char", default=None,
                    help="제목 카드 배경에 크게 흐리게 깔 캐릭터 이미지 경로(안 주면 단색 배경만)")
    p.add_argument("--end-card-duration", type=float, default=2.0,
                    help="영상 맨 끝 구독/좋아요/팔로우 CTA 카드 길이(초) — 0이면 엔딩 카드 생략")
    p.add_argument("--end-card-text", default=None,
                    help="엔딩 카드에 쓸 문구(안 주면 기본 CTA 문구 사용)")
    p.add_argument("--end-card-char", default=None,
                    help="엔딩 카드 배경에 흐리게 깔 캐릭터 이미지 경로(안 주면 --title-card-char 재사용)")
    p.add_argument("--title-banner-photo", default=None,
                    help="상단 후킹 배너 배경에 흐리게 깔 topic 대표 real 이미지 경로(안 주면 단색 배경)")
    args = p.parse_args()

    motion_schedule = None
    if args.motion_schedule:
        motion_schedule = []
        for chunk in args.motion_schedule.split(","):
            # "start-end:path" 또는 "start-end:path:bg_color"(세그먼트별 크로마키 색 override)
            parts = chunk.split(":")
            span, path = parts[0], parts[1]
            start_s, end_s = span.split("-")
            if len(parts) > 2:
                motion_schedule.append((float(start_s), float(end_s), path, parts[2]))
            else:
                motion_schedule.append((float(start_s), float(end_s), path))

    assemble(
        images=args.images.split(",") if args.images else None,
        motion_path=args.motion,
        audio_path=args.audio,
        srt_path=args.srt,
        out_path=args.out,
        title=args.title,
        intro_duration=args.intro_duration,
        ad_tag=args.ad_tag,
        bg_color=args.bg_color,
        title_card_duration=args.title_card_duration,
        title_card_text=args.title_card_text,
        title_card_char_path=args.title_card_char,
        motion_schedule=motion_schedule,
        bg_style=args.bg_style,
        end_card_duration=args.end_card_duration,
        end_card_text=args.end_card_text,
        end_card_char_path=args.end_card_char,
        title_banner_photo_path=args.title_banner_photo,
    )
