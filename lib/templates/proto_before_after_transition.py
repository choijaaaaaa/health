# 풀블리드(전체화면) "전-후" 전환 숏츠 템플릿. WHY: 좌우 분할 화면은 원인을
# 설명하는 동안 화면 절반(해결책 자리)이 계속 비어있어 낭비된다 — 대신 화면
# 전체가 원인(before: 어둡고 차가운 톤)과 해결(after: 밝고 따뜻한 톤)을 번갈아
# 전담하고, ffmpeg xfade가 장면 전환을 맡는다(PIL 크로스페이드보다 빠르고 이
# 스크립트가 단순해짐). "오늘 만든 다른 템플릿에서 실제로 겪은 3개 버그"
# (중앙정렬 비대칭-안전영역, 그림자 블러 오버플로, 하단 자막 잘림)를 피하려고
# 블러 그림자는 아예 안 쓰고, 모든 정렬은 캔버스 중앙(540)이 아니라 안전영역
# 박스 중앙으로 하고, 모든 텍스트 블록은 그리기 전에 폰트를 줄여서 안전영역
# 안에 맞춘 뒤 마지막에 한 번 더 실측 bbox로 검증한다.
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from lib.bgm import mix_bgm  # noqa: E402
from lib.video_assembler import (  # noqa: E402
    _title_font_for_lang, _wrap_text_for_lang, draw_ad_tag_overlay,
)

W, H = 1080, 1920
FPS = 30

_ILLUST_DIR = _REPO_ROOT / "assets_library" / "illust"

# WHY 중복 정의(직접 import 불가): video_assembler.py의 _YT_SAFE_RIGHT/_YT_SAFE_BOTTOM은
# _place_chalk_doodle() 함수 안의 지역 상수라 모듈 레벨에서 import할 수 없다 — 값이
# 바뀌면 그 파일과 이 파일 둘 다 손으로 맞춰야 한다. 유튜브 쇼츠 앱 실기기 UI(좋아요/
# 댓글/공유 아이콘 열, 채널명·설명 캡션 띠)가 오른쪽 150px·아래쪽 320px를 항상 가린다.
_YT_SAFE_RIGHT = 150
_YT_SAFE_BOTTOM = 320
_SAFE_MARGIN = 50  # 왼쪽·위쪽 등 나머지 가장자리 여백(요구사항: ~40-60px)

SAFE_LEFT = _SAFE_MARGIN
SAFE_TOP = _SAFE_MARGIN
SAFE_RIGHT = W - _YT_SAFE_RIGHT
SAFE_BOTTOM = H - _YT_SAFE_BOTTOM
# WHY 안전영역 "중앙"이 540이 아님: 유튜브 UI가 오른쪽만 150px 가리므로 안전
# 박스 자체가 좌우 비대칭이다(왼쪽 50 vs 오른쪽 150) — 모든 요소를 캔버스
# 중앙(540)이 아니라 이 SAFE_CX(≈490)에 맞춰야 실기기에서 진짜로 중앙처럼
# 보인다. 오늘 다른 템플릿에서 실제로 터진 "중앙정렬 비대칭-안전영역 버그"가
# 바로 이 축을 캔버스 중앙 기준으로 잘못 잡아서 생겼다.
SAFE_CX = (SAFE_LEFT + SAFE_RIGHT) / 2
# WHY 이거 하나 더 필요한지(2026-08-05, 사용자가 오프닝 화면 스크린샷 보고
# "중앙 정렬은 안했네 왜지?" 지적): SAFE_CX는 안전박스 폭(880px)을 꽉 채우는
# 요소엔 맞지만, 그보다 좁은 요소를 SAFE_CX에 맞추면 안전박스 자체가 좌우
# 비대칭이라(왼쪽 50 vs 오른쪽 150) 캔버스 눈으로 보면 왼쪽으로 쏠려 보인다.
# 오프닝 히어로 카드처럼 폭을 안전박스 최대치까지 안 채워도 되는 요소는
# 캔버스 진짜 중앙(540)에 맞추되, 폭을 VISUAL_CENTER_MAX_WIDTH 이하로만
# 잡으면 두 안전 경계 다 자동으로 지켜진다(540 기준 좌우 대칭 최대폭).
VISUAL_CX = W / 2
VISUAL_CENTER_MAX_WIDTH = 2 * min(VISUAL_CX - SAFE_LEFT, SAFE_RIGHT - VISUAL_CX)


def _verify_safe_area(bbox: tuple[float, float, float, float], label: str) -> None:
    """실제로 그려진 뒤의 bbox를 최종 방어선으로 확인한다. 프로액티브 축소
    (_fit_text_block)를 거쳐도 로직 실수가 있으면 여기서 바로 잡힌다 — 오늘 만든
    다른 템플릿들에서 이 확인이 실제 버그(중앙정렬 비대칭, 그림자 블러 오버플로,
    하단 잘림)를 잡아냈으므로 생략하지 않는다."""
    left, top, right, bottom = bbox
    if left < SAFE_LEFT or top < SAFE_TOP or right > SAFE_RIGHT or bottom > SAFE_BOTTOM:
        raise RuntimeError(
            f"[safe-area 위반] {label}: bbox=({left:.0f},{top:.0f},{right:.0f},{bottom:.0f}) "
            f"허용범위=({SAFE_LEFT},{SAFE_TOP})~({SAFE_RIGHT},{SAFE_BOTTOM}) "
            f"(W-{_YT_SAFE_RIGHT}={SAFE_RIGHT}, H-{_YT_SAFE_BOTTOM}={SAFE_BOTTOM})"
        )


# ── topic-seeded 변형 축 ──────────────────────────────────────────────
# WHY 이 프로젝트 표준 시드 공식: 같은 topic은 항상 같은 결과가 나와야
# 재조립·재현이 가능하다(true randomness 금지, 프로젝트 공통 컨벤션). 축마다
# (k, c0)를 다르게 줘서 색 테마·전환 스타일·진행바 스타일이 서로 상관없이
# 독립적으로 흔들리게 한다.
THEME_PAIRS = [
    {
        "name": "cool_blue_warm_amber",
        "before": {"top": (26, 35, 56), "bottom": (13, 17, 29), "accent": (110, 160, 255)},
        # WHY after.accent를 흰색 대신 짙은 톤으로: 진행 표시(dots/bar)의 "완료"
        # 색이 밝은 after 배경 위에서 흰색이면 대비가 약해서(밝은 배경 + 밝은
        # 강조색) 잘 안 보인다 — 같은 색상군의 어두운 변형을 써서 대비를 확보.
        "after": {"top": (255, 179, 71), "bottom": (255, 106, 61), "accent": (120, 55, 18)},
    },
    {
        "name": "muted_gray_vivid_green",
        "before": {"top": (88, 90, 96), "bottom": (52, 53, 58), "accent": (214, 217, 224)},
        "after": {"top": (84, 214, 120), "bottom": (21, 150, 90), "accent": (10, 74, 40)},
    },
    {
        "name": "dusty_purple_bright_coral",
        "before": {"top": (70, 56, 92), "bottom": (38, 30, 52), "accent": (196, 168, 255)},
        "after": {"top": (255, 138, 128), "bottom": (255, 73, 108), "accent": (110, 18, 38)},
    },
    # WHY 5개 추가(2026-08-05, "저품질/반복" 정책 리스크 대응 — 원래 3개뿐이라
    # topic 3개마다 배색이 그대로 반복됐다): 기존 관습(before=차분/어두운 톤,
    # after=밝고 따뜻한 톤, after.accent는 진행 표시 대비를 위해 어두운
    # 변형)을 그대로 유지하면서 색상군만 서로 겹치지 않게 넓힘.
    {
        "name": "deep_teal_warm_gold",
        "before": {"top": (20, 60, 65), "bottom": (10, 30, 33), "accent": (120, 220, 210)},
        "after": {"top": (255, 200, 80), "bottom": (230, 150, 30), "accent": (90, 55, 10)},
    },
    {
        "name": "slate_navy_soft_peach",
        "before": {"top": (35, 45, 65), "bottom": (18, 24, 36), "accent": (150, 180, 220)},
        "after": {"top": (255, 190, 160), "bottom": (255, 150, 110), "accent": (110, 55, 30)},
    },
    {
        "name": "charcoal_maroon_bright_mint",
        "before": {"top": (50, 30, 35), "bottom": (28, 16, 20), "accent": (220, 140, 150)},
        "after": {"top": (110, 230, 190), "bottom": (40, 190, 140), "accent": (10, 70, 50)},
    },
    {
        "name": "plum_wine_sunny_yellow",
        "before": {"top": (60, 25, 55), "bottom": (32, 12, 30), "accent": (210, 140, 200)},
        "after": {"top": (255, 220, 90), "bottom": (255, 180, 40), "accent": (100, 70, 10)},
    },
    {
        "name": "steel_blue_warm_rose",
        "before": {"top": (45, 60, 80), "bottom": (22, 30, 42), "accent": (170, 200, 230)},
        "after": {"top": (255, 150, 170), "bottom": (230, 90, 120), "accent": (100, 25, 45)},
    },
]

WIPE_STYLES = ["wipeleft", "wiperight", "slideup", "smoothleft"]
PROGRESS_STYLES = ["dots", "bar"]
# WHY 훅 화면 텍스트 장식 스타일(2026-08-06, "판서형이 이미 하던 방식과 동일한
# 원칙을 신규 포맷에도 적용" — 판서형 title card의 plain/banner/boxed/underline
# 4종을 그대로 이식): 저품질/반복 콘텐츠 정책 리스크 대응으로 오프닝(=피드
# 썸네일 대체) 화면에도 topic-seeded 변형을 하나 더 둔다.
HOOK_STYLES = ["plain", "banner", "boxed", "underline"]
PIVOT_TRANSITION = "circleopen"  # before→after 전환점, 극적인 전환 하나만 고정
QUICK_XFADE_DUR = 0.3
PIVOT_XFADE_DUR = 0.85


def _seeded_choice(seed_str: str, options: list, k: int, c0: int):
    seed_val = sum(ord(c) * (i * k + c0) for i, c in enumerate(seed_str)) % len(options)
    return options[seed_val]


def _pick_variety(seed_str: str) -> dict:
    theme = _seeded_choice(seed_str, THEME_PAIRS, k=7, c0=3)
    wipe = _seeded_choice(seed_str, WIPE_STYLES, k=13, c0=11)
    progress = _seeded_choice(seed_str, PROGRESS_STYLES, k=5, c0=2)
    hook_style = _seeded_choice(seed_str, HOOK_STYLES, k=17, c0=5)
    # WHY 텍스트 위치 지터(2026-08-06, checklist의 title_eyebrow_y 지터와
    # 동일 원칙): ±20px 범위로 훅 화면 hero 카드 시작 y를 topic마다 살짝
    # 다르게 흔든다 — 안전영역 여유(hero_top이 SAFE_TOP+20에서 시작하고
    # leftover만큼 더 내려가는 구조라 ±20 정도는 항상 안전).
    y_jitter = sum(ord(c) * (i * 5 + 3) for i, c in enumerate(seed_str)) % 41 - 20
    return {"theme": theme, "wipe": wipe, "progress": progress, "hook_style": hook_style, "y_jitter": y_jitter}


# ── 유틸 ──────────────────────────────────────────────────────────────

def _font(lang: str, size: int) -> ImageFont.FreeTypeFont:
    path, index = _title_font_for_lang(lang)
    return ImageFont.truetype(path, size, index=index)


def _ffprobe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def _parse_srt(srt_path: str) -> list[tuple[float, float, str]]:
    import re
    text = Path(srt_path).read_text(encoding="utf-8")
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


def _proportional_durations(total: float, weights: list[float], min_dur: float) -> list[float]:
    """total 시간을 weights(대개 항목별 본문 글자 수) 비례로 나눈다 — 요구사항의
    "N개 해결책을 압축한 마지막 한 문장을 각 해결책 실제 글자 수 비례로 나눈다"를
    모든 구간(메커니즘·원인·해결책)에 동일하게 적용한 일반형. min_dur 미만으로
    떨어지는 항목은 바닥을 대주고 나머지 항목에서 비례로 빌려온다(너무 짧은
    본문 하나 때문에 화면이 순간적으로 스쳐 지나가는 것 방지)."""
    n = len(weights)
    if n == 0:
        return []
    total_w = sum(weights) or n
    raw = [total * w / total_w for w in weights] if sum(weights) > 0 else [total / n] * n
    deficit = sum(max(0.0, min_dur - r) for r in raw)
    if deficit <= 0:
        return raw
    boosted = [max(r, min_dur) for r in raw]
    surplus_idx = [i for i, r in enumerate(raw) if r > min_dur]
    surplus_total = sum(raw[i] - min_dur for i in surplus_idx)
    if surplus_total > 0:
        for i in surplus_idx:
            share = (raw[i] - min_dur) / surplus_total
            boosted[i] -= deficit * share
    boosted[-1] += total - sum(boosted)  # 부동소수 오차 보정 — 합계를 total과 정확히 맞춤
    return boosted


def _vertical_gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def _remove_chroma(img: Image.Image, thresh: int = 160) -> Image.Image:
    """캐릭터 일러스트의 크로마키 배경(코너 픽셀 색을 자동으로 키 색상 채택 —
    캐릭터 자체가 초록 계열이면 파란/마젠타로 배경이 바뀌므로 하드코딩 금지,
    card_news.py의 _remove_chroma_bg와 같은 원리)을 투명 처리한다."""
    img = img.convert("RGBA")
    key = img.getpixel((2, 2))[:3]
    kr, kg, kb = key
    pixels = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = pixels[x, y]
            if abs(r - kr) + abs(g - kg) + abs(b - kb) < thresh:
                pixels[x, y] = (r, g, b, 0)
    return img


def _fit_text_block(dummy_draw, lines: list[str], lang: str, max_width: int, max_height: int,
                     max_size: int, min_size: int = 26, line_gap: float = 1.32
                     ) -> tuple[list[str], ImageFont.FreeTypeFont, int]:
    """safe-area 박스(max_width x max_height) 안에 들어갈 때까지 폰트를 줄이며
    다시 줄바꿈한다 — 위반을 감지한 "뒤"가 아니라 그리기 "전"에 미리 맞춘다."""
    wrapped: list[str] = []
    size = max_size
    while size >= min_size:
        font = _font(lang, size)
        wrapped = []
        for raw in lines:
            if raw == "":
                wrapped.append("")
                continue
            wrapped.extend(_wrap_text_for_lang(dummy_draw, raw, font, max_width, lang))
        line_h = int(size * line_gap)
        total_h = line_h * len(wrapped)
        widest = max(
            (dummy_draw.textbbox((0, 0), ln, font=font)[2] - dummy_draw.textbbox((0, 0), ln, font=font)[0]
             for ln in wrapped if ln), default=0,
        )
        if total_h <= max_height and widest <= max_width:
            return wrapped, font, line_h
        size -= 2
    # 최소 크기로도 못 맞추는 극단적으로 긴 문단 — 줄 수를 강제로 잘라서라도
    # safe-area는 지킨다. 이후 _verify_safe_area가 최종 확인.
    font = _font(lang, min_size)
    line_h = int(min_size * line_gap)
    max_lines = max(1, max_height // line_h)
    return wrapped[:max_lines], font, line_h


def _draw_text_block(draw, lines: list[str], font, line_h: int, cx: float, top_y: float,
                      color=(255, 255, 255), stroke=(0, 0, 0)) -> tuple[float, float, float, float]:
    y = top_y
    left = right = cx
    for line in lines:
        if line == "":
            y += line_h * 0.55
            continue
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = cx - w / 2 - bbox[0]
        draw.text((x, y - bbox[1]), line, font=font, fill=color, stroke_width=3, stroke_fill=stroke)
        left = min(left, cx - w / 2)
        right = max(right, cx + w / 2)
        y += line_h
    return (left, top_y, right, y)


def _draw_chip(draw, text: str, font, cx: float, y: float, fill, text_color) -> tuple:
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pad_x, pad_y = 26, 14
    box_w, box_h = w + pad_x * 2, h + pad_y * 2
    x0, y0 = cx - box_w / 2, y
    draw.rounded_rectangle([x0, y0, x0 + box_w, y0 + box_h], radius=box_h / 2, fill=fill)
    draw.text((cx - w / 2 - bbox[0], y0 + pad_y - bbox[1]), text, font=font, fill=text_color)
    return (x0, y0, x0 + box_w, y0 + box_h)


def _draw_progress(draw, style: str, index: int, total: int, cx: float, y: float, accent) -> tuple:
    box_w = SAFE_RIGHT - SAFE_LEFT - 60
    if style == "bar":
        h = 8
        x0 = cx - box_w / 2
        draw.rounded_rectangle([x0, y, x0 + box_w, y + h], radius=h / 2, fill=(120, 120, 120))
        frac = (index + 1) / total
        fill_w = max(box_w * frac, h)
        draw.rounded_rectangle([x0, y, x0 + fill_w, y + h], radius=h / 2, fill=accent)
        return (x0, y, x0 + box_w, y + h)
    r = 7
    gap = min(30, box_w / max(total - 1, 1))
    total_w = gap * (total - 1) + r * 2
    x0 = cx - total_w / 2
    for i in range(total):
        dot_cx = x0 + i * gap + r
        fill = accent if i <= index else (150, 150, 150)
        draw.ellipse([dot_cx - r, y, dot_cx + r, y + 2 * r], fill=fill)
    return (x0 - r, y, x0 + total_w - r + 2 * r, y + 2 * r)


def _char_medallion(chroma_img: Image.Image, size: int) -> Image.Image:
    """흰 테두리 원형 배지 — before/after 어느 톤 배경 위에서도 캐릭터 경계가
    또렷하게 읽히도록 항상 흰색 링을 쓴다(그림자 블러는 안전영역 오버플로
    위험이 있어 의도적으로 안 씀)."""
    photo = chroma_img.resize((size, size))
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, size, size), fill=255)
    from PIL import ImageChops
    combined_mask = ImageChops.multiply(photo.split()[3], mask)
    ring_w = 8
    canvas = Image.new("RGBA", (size + ring_w * 2, size + ring_w * 2), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(canvas)
    cdraw.ellipse([0, 0, canvas.width, canvas.height], fill=(255, 255, 255, 255))
    canvas.paste(photo, (ring_w, ring_w), combined_mask)
    return canvas


def _lighten(color: tuple[int, int, int], amt: float) -> tuple[int, int, int]:
    return tuple(int(c + (255 - c) * amt) for c in color)


def _hero_card(chroma_img: Image.Image, card_w: int, card_h: int, palette: dict) -> Image.Image:
    """오프닝 화면 전용 큰 시각적 앵커. 기존 600px 원형 메달리온은 본문
    beat에는 유지하되(그대로 재사용), 오프닝만 이 함수로 교체 — 캐릭터 주변에
    큰 반투명 "유리 패널" 카드를 깔아서 확대된 캐릭터 둘레가 빈 캔버스가
    아니라 채워진 블록으로 읽히게 한다(before 톤 자체가 원래 어둡기 때문에
    카드가 없으면 확대된 캐릭터만 둥둥 떠 있고 나머지는 여전히 빈 배경처럼
    보임 — 요구사항의 "40%+ 빈 배경" 문제의 진짜 원인). 그림자 블러는 기존
    파일 전체 컨벤션대로 안전영역 오버플로 위험 때문에 안 씀 — 대신 accent
    색 테두리 링으로 경계를 준다."""
    radius = 56
    canvas = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(canvas)
    accent = palette["accent"]
    # WHY 패널 색을 순백 대신 팔레트 top을 밝힌 톤으로: "cool/dim" 정체성을
    # 오프닝에서도 유지하면서(순백 카드는 밝고 따뜻해 보여 전환 후 화면인
    # after와 구분이 안 됨) 어두운 배경 위에서도 카드 경계가 또렷하게 보일
    # 만큼은 밝게(35%) 만든다.
    panel_rgb = _lighten(palette["top"], 0.35)
    cdraw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=radius, fill=(*panel_rgb, 235))
    cdraw.rounded_rectangle([0, 0, card_w - 1, card_h - 1], radius=radius, outline=(*accent, 220), width=5)

    # WHY 콘텐츠 bbox로 먼저 트림: 크로마 제거된 일러스트는 640x640 정사각
    # 안에 실제 캐릭터가 여백을 두고 들어있어서(원본 소스 자체의 여백),
    # 정사각 그대로 카드를 키워도 캐릭터 주위 빈 여백만 함께 커진다(실제
    # 렌더 확인 결과 — 카드는 커졌는데 캐릭터 체감 크기는 그대로였음). 알파
    # 채널 bbox로 실제 그려진 픽셀 범위만 잘라낸 뒤 카드에 맞게 "contain"
    # 방식으로 최대한 키운다 — 이래야 "작은 원형 로고 아님, 큰 시각적 앵커"
    # 요구사항이 실제로 체감된다.
    alpha = chroma_img.split()[3]
    bbox = alpha.getbbox()
    cropped = chroma_img.crop(bbox) if bbox else chroma_img
    cw, ch = cropped.size
    target_w, target_h = card_w * 0.88, card_h * 0.88
    scale = min(target_w / cw, target_h / ch)
    new_w, new_h = max(1, round(cw * scale)), max(1, round(ch * scale))
    char_img = cropped.resize((new_w, new_h))
    cx0 = (card_w - new_w) // 2
    cy0 = (card_h - new_h) // 2
    canvas.paste(char_img, (cx0, cy0), char_img)
    return canvas


def _render_hook_screen(theme: dict, lang: str, hook_lines: list[str], char_chroma: Image.Image | None,
                         progress_style: str, progress_index: int, progress_total: int,
                         headline_size: int = 60, style: str = "plain", y_jitter: int = 0) -> Image.Image:
    """오프닝/타이틀 화면 전용 렌더러. WHY 별도 함수로 분리(공용 _render_screen
    재사용 안 함): 이 파이프라인은 별도 커스텀 썸네일을 업로드하지 않아
    (lib/youtube_upload.py 확인) 이 영상의 0프레임이 피드에서 실질적인
    썸네일 역할을 한다 — 작은 원형 캐릭터 + 그 아래 40%+ 빈 배경이던 기존
    구성은 썸네일 크기에서 훅이 약하게 읽혀서, 캐릭터를 큰 "유리 패널"
    카드로 확대하고 남은 세로 공간을 텍스트가 실측 높이만큼만 가져가게 해
    빈 공간을 없앤다. 나머지 beat(mechanism/cause/fix) 화면은 손대지 않고
    _render_screen을 그대로 쓴다.
    WHY 진행 표시(dots/bar)를 이 화면만 안 그리는지(2026-08-05, 사용자
    지적 "이미지의 상단 점이 필요하나?"): 진행 표시는 재생 중 "지금 몇
    번째 화면인지" 알려주는 용도라 그 자체로는 유효하지만, 정지 썸네일
    한 장으로 볼 땐 맥락 없는 점 몇 개일 뿐이라 후킹에 도움이 안 되고
    상단 공간만 차지한다 — 오프닝만 빼고 나머지 화면엔 그대로 남긴다."""
    palette = theme["before"]
    img = _vertical_gradient(palette["top"], palette["bottom"]).convert("RGB")
    draw = ImageDraw.Draw(img)
    accent = palette["accent"]

    dummy = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy)
    # WHY max_width가 아니라 VISUAL_CENTER_MAX_WIDTH인지: 이 오프닝 화면의
    # 카드·텍스트는 캔버스 진짜 중앙(VISUAL_CX=540)에 맞춰야 눈으로 봤을 때
    # 중앙정렬로 보인다(위 VISUAL_CENTER_MAX_WIDTH 정의 참고) — 안전박스
    # 최대폭(880)을 그대로 쓰면 SAFE_CX(490) 기준이 되어 화면 오른쪽에
    # 여백이 몰리고 왼쪽으로 쏠려 보인다.
    max_width = VISUAL_CENTER_MAX_WIDTH
    safe_h = SAFE_BOTTOM - SAFE_TOP

    # WHY y_jitter(2026-08-06, checklist의 title_eyebrow_y 지터와 동일 원칙 —
    # "저품질/반복" 정책 리스크 대응): topic마다 훅 화면 시작 위치를 ±20px
    # 흔든다. hero_avail_h가 hero_top을 그대로 반영해 계산되므로(아래) 안전
    # 여백은 자동으로 유지된다.
    hero_top = SAFE_TOP + 20 + y_jitter  # WHY 20인지: 진행 표시(dots)를 이 화면에서 뺐으므로
    # 예전 90px(dots+여백)이 필요 없다 — 위쪽 여백만 살짝 남기고 바로 시작.
    text_gap = 44
    # WHY 텍스트를 먼저 "측정"만 해서 실제 줄 수를 안다(자리 배치는 나중):
    # hero 카드 높이를 정하려면 텍스트가 실제로 몇 줄이 될지 먼저 알아야
    # 하고, 그래야 짧은 훅 문장에서도 hero 아래에 남는 빈 공간이 생기지 않는다.
    text_cap_h = int(safe_h * 0.46)
    wrapped, font, line_h = _fit_text_block(
        dummy_draw, hook_lines, lang, max_width, text_cap_h, max_size=headline_size, min_size=34,
    )
    text_block_h = line_h * len(wrapped)

    hero_w = max_width
    hero_avail_h = SAFE_BOTTOM - hero_top - text_gap - text_block_h
    # WHY 상한을 hero_w*1.4까지 넉넉하게: 카드가 남는 세로 공간을 최대한
    # 다 차지하게 해서 카드↔텍스트 사이에 빈 여백 띠가 생기지 않게 한다(처음
    # 시도에서 상한을 1.05로 좁게 잡았더니 남는 공간이 "카드 위 여백"과
    # "카드-텍스트 사이 여백" 두 군데로 쪼개져 화면 중간에 빈 회색 띠가
    # 보였음 — 실제 렌더 확인 후 수정). 남는 만큼은 전부 hero_top(카드 위쪽
    # 여백)으로 보내 카드가 텍스트 바로 위까지 바짝 채우게 한다.
    hero_h = max(min(hero_avail_h, hero_w * 1.4), 260)
    leftover = hero_avail_h - hero_h
    if leftover > 0:
        hero_top += leftover

    if char_chroma is not None:
        hero = _hero_card(char_chroma, round(hero_w), round(hero_h), palette)
        px = round(VISUAL_CX - hero.width / 2)
        py = round(hero_top)
        img.paste(hero, (px, py), hero)
        char_bbox = (px, py, px + hero.width, py + hero.height)
        _verify_safe_area(char_bbox, "hero-character")
        text_top = py + hero.height + text_gap
    else:
        # 캐릭터 일러스트가 없는 topic(방어적 fallback) — 텍스트를 세이프
        # 영역 안에서 세로 중앙에 맞춰 빈 위/아래 공백을 균등하게 나눈다.
        text_top = hero_top + max(hero_avail_h - text_block_h, 0) / 2 + text_gap

    # WHY plain/banner/boxed/underline 4종(2026-08-06, 판서형 title card
    # 스타일을 그대로 이식): banner는 텍스트 뒤에 깔려야 해서 그리기 전에
    # 미리 폭을 재고, boxed/underline은 실제로 그려진 뒤 bbox를 그대로 써서
    # 정확히 감싼다.
    if style == "banner":
        pad_x, pad_y = 40, 24
        max_tw = 0.0
        for line in wrapped:
            if not line:
                continue
            bb = dummy_draw.textbbox((0, 0), line, font=font)
            max_tw = max(max_tw, bb[2] - bb[0])
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(overlay).rounded_rectangle(
            [max(VISUAL_CX - max_tw / 2 - pad_x, SAFE_LEFT), max(text_top - pad_y, SAFE_TOP),
             min(VISUAL_CX + max_tw / 2 + pad_x, SAFE_RIGHT), min(text_top + text_block_h + pad_y, SAFE_BOTTOM)],
            radius=18, fill=(0, 0, 0, 120),
        )
        img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
        draw = ImageDraw.Draw(img)

    text_color = (255, 255, 255)
    stroke_color = (0, 0, 0)
    text_bbox = _draw_text_block(draw, wrapped, font, line_h, VISUAL_CX, text_top, text_color, stroke_color)
    _verify_safe_area(text_bbox, "hook")

    if style == "boxed":
        pad_x, pad_y = 30, 18
        box = [max(text_bbox[0] - pad_x, SAFE_LEFT), max(text_bbox[1] - pad_y, SAFE_TOP),
               min(text_bbox[2] + pad_x, SAFE_RIGHT), min(text_bbox[3] + pad_y, SAFE_BOTTOM)]
        draw.rounded_rectangle(box, radius=20, outline=(255, 255, 255), width=6)
    elif style == "underline":
        bar_w = min((text_bbox[2] - text_bbox[0]) + 50, SAFE_RIGHT - SAFE_LEFT)
        bar_h = 14
        bar_y = min(text_bbox[3] + 18, SAFE_BOTTOM - bar_h)
        draw.rounded_rectangle(
            [VISUAL_CX - bar_w / 2, bar_y, VISUAL_CX + bar_w / 2, bar_y + bar_h],
            radius=bar_h / 2, fill=(255, 255, 255),
        )

    return img


# ── 화면(beat) 렌더링 ─────────────────────────────────────────────────

def _render_screen(tone: str, theme: dict, lang: str, label: str | None, body_lines: list[str],
                    char_chroma: Image.Image | None, progress_style: str, progress_index: int,
                    progress_total: int, headline_size: int = 52) -> Image.Image:
    palette = theme[tone]
    img = _vertical_gradient(palette["top"], palette["bottom"]).convert("RGB")
    draw = ImageDraw.Draw(img)

    accent = palette["accent"]
    _draw_progress(draw, progress_style, progress_index, progress_total, SAFE_CX, SAFE_TOP + 10, accent)

    y_cursor = SAFE_TOP + 55
    if label:
        chip_font = _font(lang, 34)
        chip_fill = (255, 255, 255) if tone == "before" else (24, 18, 16)
        chip_text_color = (20, 20, 20) if tone == "before" else (255, 255, 255)
        chip_bbox = _draw_chip(draw, label, chip_font, SAFE_CX, y_cursor, chip_fill, chip_text_color)
        _verify_safe_area(chip_bbox, f"chip[{label}]")
        y_cursor = chip_bbox[3] + 24

    char_bottom = y_cursor
    if char_chroma is not None:
        size = 600
        med = _char_medallion(char_chroma, size)
        # 캐릭터 자체는 원형 마스크라 사각 이미지 전체가 아니라 원 안쪽만 실제로
        # 보이므로, 안전영역 확인은 사각 붙임 좌표(placement box) 기준으로 충분히
        # 보수적으로 잡는다.
        px = round(SAFE_CX - med.width / 2)
        py = round(y_cursor)
        img.paste(med, (px, py), med)
        char_bbox = (px, py, px + med.width, py + med.height)
        _verify_safe_area(char_bbox, "character")
        char_bottom = py + med.height + 36

    dummy = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy)
    max_width = SAFE_RIGHT - SAFE_LEFT
    max_height = SAFE_BOTTOM - char_bottom
    wrapped, font, line_h = _fit_text_block(
        dummy_draw, body_lines, lang, max_width, max_height, max_size=headline_size,
    )
    text_color = (255, 255, 255)
    stroke_color = (0, 0, 0)
    text_bbox = _draw_text_block(draw, wrapped, font, line_h, SAFE_CX, char_bottom, text_color, stroke_color)
    _verify_safe_area(text_bbox, f"body[{label or 'hook'}]")

    return img


def _render_closing_screen(theme: dict, lang: str, closing: dict, char_chromas: list[Image.Image],
                            progress_style: str, progress_index: int, progress_total: int) -> Image.Image:
    palette = theme["after"]
    img = _vertical_gradient(palette["top"], palette["bottom"]).convert("RGB")
    draw = ImageDraw.Draw(img)
    accent = palette["accent"]
    _draw_progress(draw, progress_style, progress_index, progress_total, SAFE_CX, SAFE_TOP + 10, accent)

    y_cursor = SAFE_TOP + 60
    if char_chromas:
        size, gap = 150, 20
        meds = [_char_medallion(c, size) for c in char_chromas[:3]]
        total_w = sum(m.width for m in meds) + gap * (len(meds) - 1)
        x = SAFE_CX - total_w / 2
        top = y_cursor
        for m in meds:
            img.paste(m, (round(x), round(top)), m)
            x += m.width + gap
        char_bbox = (SAFE_CX - total_w / 2, top, SAFE_CX + total_w / 2, top + meds[0].height)
        _verify_safe_area(char_bbox, "closing-medallions")
        y_cursor = top + meds[0].height + 40

    dummy = Image.new("RGBA", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy)
    max_width = SAFE_RIGHT - SAFE_LEFT
    headline_lines = [ln for block in closing["headline"] for ln in block]
    max_height = int((SAFE_BOTTOM - y_cursor) * 0.62)
    wrapped, font, line_h = _fit_text_block(
        dummy_draw, headline_lines, lang, max_width, max_height, max_size=58,
    )
    bbox = _draw_text_block(draw, wrapped, font, line_h, SAFE_CX, y_cursor, (255, 255, 255), (0, 0, 0))
    _verify_safe_area(bbox, "closing-headline")

    tip_top = bbox[3] + 30
    tip_max_h = SAFE_BOTTOM - tip_top
    if tip_max_h > 40 and closing.get("tip"):
        tip_wrapped, tip_font, tip_line_h = _fit_text_block(
            dummy_draw, closing["tip"], lang, max_width, tip_max_h, max_size=38, min_size=22,
        )
        tip_bbox = _draw_text_block(draw, tip_wrapped, tip_font, tip_line_h, SAFE_CX, tip_top,
                                     (255, 245, 235), (0, 0, 0))
        _verify_safe_area(tip_bbox, "closing-tip")

    return img


# ── 영상 조립 ─────────────────────────────────────────────────────────

def _build_segment(png_path: Path, duration: float, out_path: Path) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loop", "1", "-i", str(png_path), "-t", f"{duration:.4f}",
         "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
        check=True, capture_output=True,
    )


def _xfade_chain(seg_paths: list[Path], raw_durs: list[float], transitions: list[tuple[str, float]],
                  out_path: Path) -> None:
    """가변 길이 세그먼트 + 가변 전환 길이를 xfade로 체인 연결한다
    (_build_background의 균등-세그먼트 패턴을 가변 길이로 일반화). raw_durs는
    이미 좌우 전환 절반씩을 얹어서 부풀려둔 실제 렌더 길이 — 이렇게 하면
    xfade가 겹치는 만큼 줄어도 최종 출력 길이가 정확히 목표 화면-시간 합계와
    같아진다(_allocate_screen_durations의 v_i 합 = 오디오 길이)."""
    n = len(seg_paths)
    inputs = []
    for p in seg_paths:
        inputs += ["-i", str(p)]
    filters, prev = [], "0:v"
    cum = raw_durs[0]
    for i in range(1, n):
        style, dur = transitions[i - 1]
        offset = max(cum - dur, 0.0)
        out_label = f"vx{i}" if i < n - 1 else "vout"
        filters.append(f"[{prev}][{i}:v]xfade=transition={style}:duration={dur:.3f}:offset={offset:.3f}[{out_label}]")
        prev = out_label
        cum = cum + raw_durs[i] - dur
    subprocess.run(
        ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
         "-map", "[vout]", "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
        check=True, capture_output=True,
    )


def render(topic_dir: str, lang: str, audio_path: str, srt_path: str, spec_path: str, out_path: str,
           ad_tag: bool = False) -> None:
    """card_news_spec.json(mechanism → N쌍의 원인/해결 → closing)을 읽어 풀블리드
    전-후 전환 숏츠를 렌더링한다. N은 하드코딩하지 않고 items 길이에서 유도한다.

    타이밍 설계: 훅(SRT 첫 구간) 이후 나머지 오디오 구간을 메커니즘·원인 N개·
    해결책 N개(2N+1개 "beat")에 각 항목 본문 글자 수 비례로 나눈다. 이 프로젝트의
    실제 나레이션 패턴(예: 부종_1) 확인 결과 "해결책 N개를 마지막 한 문장에
    압축"하는 경우 원인 파트도 항목당 SRT 구간 수가 들쭉날쭉해서(사례 하나에
    구간이 2개 붙는 등) 구간을 항목에 1:1로 매칭하는 방식은 애초에 일반화가
    안 된다 — 대신 이 비례-분배를 모든 beat에 균일하게 적용해 특별 케이스
    분기 없이 "압축 문장" 요구사항을 자연스럽게 만족시킨다."""
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    entries = _parse_srt(srt_path)
    audio_duration = _ffprobe_duration(audio_path)

    items = spec["items"]
    if len(items) < 3 or (len(items) - 1) % 2 != 0:
        raise RuntimeError(
            f"card_news_spec items 구조가 'mechanism + N쌍(원인/해결)'이 아님: {len(items)}개"
        )
    n_pairs = (len(items) - 1) // 2
    mechanism_item = items[0]
    pairs = [(items[1 + 2 * i], items[2 + 2 * i]) for i in range(n_pairs)]
    causes = [c for c, _ in pairs]
    fixes = [f for _, f in pairs]

    seed_str = Path(topic_dir).name or spec.get("title", ["topic"])[0]
    variety = _pick_variety(seed_str)
    theme, wipe_style, progress_style = variety["theme"], variety["wipe"], variety["progress"]
    hook_style, hook_y_jitter = variety["hook_style"], variety["y_jitter"]

    hook_lines = spec["title"][:-1] if len(spec["title"]) > 1 else spec["title"]
    hook_duration = entries[0][1] if entries else max(audio_duration * 0.1, 2.5)
    remaining = max(audio_duration - hook_duration, 1.0)

    # WHY 클로징(마무리 팁) 화면도 최소 읽기 시간을 미리 확보해두는지
    # (2026-08-06, 코골이_1 실측 확인 — "마지막 빨간 부분 글은 긴데 볼 시간이
    # 없다"): 클로징은 헤드라인 2문단+팁까지 최대 6줄로 해결책 화면보다도
    # 텍스트가 많은데, 나레이션이 따로 없어 항상 "남는 시간"만 받다 보니
    # 1초 바닥까지 떨어져 있었다. 본문 글자 수 비례로 최소 시간을 먼저
    # 계산해서 예산 배분 단계에서부터 반영한다.
    _closing_spec = spec.get("closing", {})
    _closing_weight = (
        sum(len(ln) for block in _closing_spec.get("headline", []) for ln in block)
        + sum(len(ln) for ln in _closing_spec.get("tip", []) if ln)
    )
    CLOSING_READ_MIN = min(5.0, max(2.4, _closing_weight * 0.045))

    # WHY 해결책(fix)을 항목별 개별 화면으로 안 보여주는지(2026-08-06,
    # 코골이_1 실측 확인 — "~ 대신 해서 나오는 항목별 개선책 삭제해야겠다
    # 이거 하나하나 열거하니까 대본에 비해 시간이 너무 짧아서 안 된다"):
    # 해결책 N개를 각자 화면으로 쪼개면 나레이션이 원인 설명에 비해
    # 해결책은 짧게(또는 마지막 한 문장에 압축해서) 언급하는 topic이 많아,
    # 화면 하나당 실제로 줄 수 있는 시간이 구조적으로 부족했다(가독 최소
    # 시간을 강제로 보장해도 mechanism 구간을 계속 깎아먹는 식). 원인
    # 화면들 뒤에는 기존 클로징(요약+팁) 화면 하나만 두고, 해결책에 쓰였던
    # 예산을 전부 이 화면에 몰아준다.
    beats = [("mechanism", mechanism_item)] + [(f"cause{i}", c) for i, c in enumerate(causes, 1)]
    weights = [max(sum(len(l) for l in it["body"] if l), 1) for _, it in beats]
    min_dur = max(1.3, remaining * 0.03)
    mech_cause_budget = max(remaining - CLOSING_READ_MIN, min_dur * len(weights))
    durs = _proportional_durations(mech_cause_budget, weights, min_dur)

    mechanism_dur = durs[0]
    cause_durs = durs[1:1 + n_pairs]

    # WHY 원인(cause) 구간을 실제 SRT 타임스탬프로 덮어쓰는지(2026-08-05,
    # 코골이_1 실측 확인 — 세 번째 원인 화면이 실제 내레이션보다 12초 넘게
    # 일찍 뜨는 심각한 어긋남을 발견). 위 비례-배분은 "메커니즘 설명 뒤에
    # 곧장 원인1이 나온다"고 가정하는데, 실제로는 "이 세 가지가 각각 다른
    # 방식으로 만든다" 같은 다리 문장이 하나 더 있는 topic이 있어서 그
    # 구간이 어느 beat 가중치에도 안 잡히고, 뒤 beat들이 전부 앞당겨지며
    # 오차가 누적된다. 원인은 이 프로젝트 콘텐츠 관행상("항목 여러 개
    # 설명 전엔 이름부터 나열") 거의 항상 "첫 번째는 OO야" 식으로 항목명을
    # 직접 언급하므로, SRT 큐 텍스트에서 항목명을 순서대로 찾아 실제
    # 타임스탬프를 그대로 쓰는 게 비례-배분 추정보다 훨씬 정확하다 — 못
    # 찾은 원인이 하나라도 있으면 안전하게 비례-배분 결과를 그대로
    # 유지한다(원래 동작 그대로, 회귀 없음).
    cause_starts_real: list[float | None] = []
    search_from = 0
    for c in causes:
        name = c.get("name", "")
        found_start = None
        if name:
            for idx in range(search_from, len(entries)):
                if name in entries[idx][2]:
                    found_start = entries[idx][0]
                    search_from = idx + 1
                    break
        cause_starts_real.append(found_start)

    if all(s is not None for s in cause_starts_real):
        mechanism_dur = cause_starts_real[0] - hook_duration
        for i in range(n_pairs - 1):
            cause_durs[i] = cause_starts_real[i + 1] - cause_starts_real[i]
        # 마지막 원인 구간의 끝(=클로징 시작)도 첫 해결책 이름이 SRT에 개별
        # 언급되면 그 시점으로. 안 되면(해결책 N개가 마지막 한 문장에 압축된
        # topic — 게다가 그 문장이 원인과 다른 동의어를 쓰는 경우도 흔해서
        # "맥주"의 해결책 문장이 "술은..."으로 시작하는 식— 이름 문자열
        # 매칭 자체가 실패한다) SRT 마지막 큐의 시작 시각을 대신 쓴다 — 이
        # 프로젝트 나레이션 관행상 마지막 큐는 항상 마무리/해결책 요약
        # 문장이라 안전한 근사치다.
        fix0_name = fixes[0].get("name", "") if fixes else ""
        fix0_start_real = None
        if fix0_name:
            for idx in range(search_from, len(entries)):
                if fix0_name in entries[idx][2]:
                    fix0_start_real = entries[idx][0]
                    break
        if fix0_start_real is None and entries and entries[-1][0] > cause_starts_real[-1]:
            fix0_start_real = entries[-1][0]
        last_cause_end = (
            fix0_start_real if fix0_start_real is not None
            else cause_starts_real[-1] + cause_durs[-1]
        )
        cause_durs[-1] = max(last_cause_end - cause_starts_real[-1], min_dur)

    # 클로징(요약+팁) 화면 — 해결책 항목별 화면이 없어졌으므로 mechanism+원인
    # 이후 남는 시간 전부가 이 화면 하나로 간다. 최소 읽기 시간
    # (CLOSING_READ_MIN)에 못 미치면 mechanism 구간(문장 경계 정확도 요구가
    # 낮은 구간)에서 빌려온다.
    closing_dur = remaining - mechanism_dur - sum(cause_durs)
    if closing_dur < CLOSING_READ_MIN:
        shortfall = CLOSING_READ_MIN - closing_dur
        borrow = min(shortfall, max(mechanism_dur - min_dur, 0))
        mechanism_dur -= borrow
        closing_dur += borrow
    closing_dur = max(closing_dur, 1.0)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        char_cache: dict[str, Image.Image] = {}

        def chroma_for(char_file: str | None) -> Image.Image | None:
            if not char_file:
                return None
            if char_file not in char_cache:
                raw = Image.open(_ILLUST_DIR / char_file).convert("RGB").resize((640, 640))
                char_cache[char_file] = _remove_chroma(raw)
            return char_cache[char_file]

        total_beats = 2 + n_pairs + 1  # hook + mechanism + N cause + closing(해결책 개별 화면 없음)
        screens: list[dict] = []
        # WHY mechanism_item 폴백(2026-08-05, 코골이_1 실측 확인 — 오프닝
        # 화면이 캐릭터 하나 없이 텍스트만 덩그러니 뜨는 문제 발견): spec에
        # cover_char_file이 없는 topic이 실제로 많은데, 이 경우 이전엔
        # "캐릭터 없음" 방어 폴백(빈 배경)으로 빠져서 프레임 0(=사실상
        # 썸네일)가 휑하게 나왔다. mechanism_item(items[0])은 항상
        # char_file을 갖고 있으므로(아래 mechanism 화면에서 바로 다음 줄에
        # 쓰임) 이걸 1차 폴백으로 쓴다 — checklist가 이미 쓰는 것과 동일한
        # cover_char_file 폴백 원칙.
        screens.append({
            "tone": "before", "label": None, "body": hook_lines,
            "char": chroma_for(spec.get("cover_char_file") or mechanism_item.get("char_file")),
            "dur": hook_duration, "headline_size": 60,
        })
        screens.append({
            "tone": "before", "label": mechanism_item["name"], "body": mechanism_item["body"],
            "char": chroma_for(mechanism_item.get("char_file")), "dur": mechanism_dur, "headline_size": 50,
        })
        for c, dur in zip(causes, cause_durs):
            screens.append({
                "tone": "before", "label": c["name"], "body": c["body"],
                "char": chroma_for(c.get("char_file")), "dur": dur, "headline_size": 50,
            })
        pivot_boundary_index = 1 + n_pairs  # cause 마지막(index n_pairs) → 클로징(요약) 사이 — 문제→해결 피벗

        png_paths, target_durs = [], []
        for idx, s in enumerate(screens):
            if idx == 0:
                # 오프닝(훅) 화면만 큰 hero 카드 전용 렌더러 사용 — 나머지
                # mechanism/cause beat는 기존 _render_screen 그대로.
                img = _render_hook_screen(
                    theme, lang, s["body"], s["char"],
                    progress_style, idx, total_beats, headline_size=s["headline_size"],
                    style=hook_style, y_jitter=hook_y_jitter,
                )
            else:
                img = _render_screen(
                    s["tone"], theme, lang, s["label"], s["body"], s["char"],
                    progress_style, idx, total_beats, headline_size=s["headline_size"],
                )
            if ad_tag:
                img = draw_ad_tag_overlay(img, lang)
            p = tmp_path / f"scr_{idx:02d}.png"
            img.save(p)
            png_paths.append(p)
            target_durs.append(s["dur"])

        closing_char_files = list(dict.fromkeys(c.get("char_file") for c in causes if c.get("char_file")))
        closing_chromas = [chroma_for(f) for f in closing_char_files]
        closing_img = _render_closing_screen(
            theme, lang, spec["closing"], closing_chromas, progress_style, total_beats - 1, total_beats,
        )
        if ad_tag:
            closing_img = draw_ad_tag_overlay(closing_img, lang)
        closing_png = tmp_path / f"scr_{len(screens):02d}.png"
        closing_img.save(closing_png)
        png_paths.append(closing_png)
        target_durs.append(closing_dur)

        n = len(png_paths)
        transitions: list[tuple[str, float]] = []
        for i in range(1, n):
            if i == pivot_boundary_index + 1:
                # cause 마지막 화면과 fix 첫 화면 "사이"의 경계 — 문제→해결 피벗
                transitions.append((PIVOT_TRANSITION, PIVOT_XFADE_DUR))
            else:
                transitions.append((wipe_style, QUICK_XFADE_DUR))

        raw_durs = []
        for i in range(n):
            left = transitions[i - 1][1] / 2 if i - 1 >= 0 else 0.0
            right = transitions[i][1] / 2 if i < n - 1 else 0.0
            raw_durs.append(target_durs[i] + left + right)

        seg_paths = []
        for i, (p, dur) in enumerate(zip(png_paths, raw_durs)):
            seg = tmp_path / f"seg_{i:02d}.mp4"
            _build_segment(p, dur, seg)
            seg_paths.append(seg)

        chained = tmp_path / "chained.mp4"
        _xfade_chain(seg_paths, raw_durs, transitions, chained)

        # WHY 프레임 양자화 보정: 각 세그먼트를 -t(초)로 렌더링하면 ffmpeg가 30fps
        # 프레임 경계로 반올림하면서 세그먼트마다 최대 1프레임(1/30초)씩 오차가
        # 누적될 수 있다 — 세그먼트 수가 늘어나면(N이 큰 topic) 합계가 오디오
        # 길이보다 짧아져 "-shortest"가 영상 쪽에서 잘라버려 최종 길이가 오디오보다
        # 짧아지는 사고로 이어진다. 마지막 프레임을 살짝 더 늘려(tpad) 항상
        # 오디오 길이 이상을 보장한 뒤 -t로 정확히 맞춘다.
        chained_dur = _ffprobe_duration(str(chained))
        if chained_dur < audio_duration:
            pad_needed = audio_duration - chained_dur + 0.1
            padded = tmp_path / "chained_padded.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(chained),
                 "-vf", f"tpad=stop_mode=clone:stop_duration={pad_needed:.3f}",
                 "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p", str(padded)],
                check=True, capture_output=True,
            )
            chained = padded

        mixed_audio = mix_bgm(audio_path, str(tmp_path / "mixed_audio.m4a"), audio_duration, seed_str)

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(chained), "-i", mixed_audio,
             "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-t", f"{audio_duration:.4f}", "-shortest", str(out_path)],
            check=True, capture_output=True,
        )

    print(
        f"before/after 전환 영상 완료: {out_path} "
        f"(theme={theme['name']}, wipe={wipe_style}, progress={progress_style}, N={n_pairs})"
    )


if __name__ == "__main__":
    if len(sys.argv) < 7:
        print(
            "usage: python3 lib/templates/proto_before_after_transition.py "
            "<topic_dir> <lang> <audio_path> <srt_path> <spec_path> <out_path>"
        )
        sys.exit(1)
    render(
        topic_dir=sys.argv[1], lang=sys.argv[2], audio_path=sys.argv[3],
        srt_path=sys.argv[4], spec_path=sys.argv[5], out_path=sys.argv[6],
    )
