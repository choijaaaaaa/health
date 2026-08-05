# 체크리스트/자가진단형 Shorts 템플릿. WHY: 세로 체크리스트가 내레이션 진행에 맞춰
# 하나씩 체크되는 포맷 — 항목 개수는 card_news_spec.json의 items에서 그대로 읽어
# N개 어떤 topic이든 코드 변경 없이 동작해야 한다(하드코딩 3개 금지).
from __future__ import annotations

import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from lib.bgm import mix_bgm  # noqa: E402
from lib.video_assembler import _title_font_for_lang, _wrap_text_for_lang, _parse_srt  # noqa: E402

W, H = 1080, 1920
FPS = 30
ITEM_ICON_DIR = PROJECT_ROOT / "assets_library" / "illust"

# lib/video_assembler.py의 _YT_SAFE_RIGHT/_YT_SAFE_BOTTOM과 반드시 같은 값이어야
# 한다 — 유튜브 Shorts 앱 UI(공유/좋아요 버튼 등)가 화면 우측·하단을 가리는 픽셀 폭.
_YT_SAFE_RIGHT = 150
_YT_SAFE_BOTTOM = 320
_SAFE_TOP = 50
_SAFE_LEFT = 50
SAFE_X1 = W - _YT_SAFE_RIGHT
SAFE_Y1 = H - _YT_SAFE_BOTTOM
_CENTER_X = W // 2
# 화면 중앙(cx=540)은 세이프 영역 중앙(490)과 다르다 — 그대로 max_width를 주면
# 우측 세이프 경계를 넘어간다. 중앙정렬 텍스트는 항상 이 폭으로 캡핑한다.
SAFE_CENTERED_MAX_WIDTH = 2 * min(_CENTER_X - _SAFE_LEFT, SAFE_X1 - _CENTER_X)


def _assert_within_safe_area(label, bbox):
    """bbox=(x0,y0,x1,y1)는 실제로 렌더된 텍스트 블록의 경계 — 세이프 영역
    (`_SAFE_LEFT`/`_SAFE_TOP`/`SAFE_X1`/`SAFE_Y1`) 밖으로 나가면 즉시 에러로
    잡는다. 각 렌더 함수는 이 함수에 도달하기 전에 이미 폰트 축소·행 수 제한
    (`_layout_multiline`)·항목 개수에 맞춘 동적 행 높이(`_checklist_layout`)로
    안 걸리게 맞춰야 정상 — 이 assert가 실제로 걸리면 그 계산 로직에 구멍이
    있다는 뜻이라 조용히 넘어가지 않고 바로 멈춘다.
    """
    x0, y0, x1, y1 = bbox
    if x0 < _SAFE_LEFT - 1 or y0 < _SAFE_TOP - 1 or x1 > SAFE_X1 + 1 or y1 > SAFE_Y1 + 1:
        raise RuntimeError(
            f"[proto_checklist] 세이프 영역 침범 — {label}: "
            f"bbox=({x0:.0f},{y0:.0f},{x1:.0f},{y1:.0f}), "
            f"허용 범위=({_SAFE_LEFT},{_SAFE_TOP})~({SAFE_X1},{SAFE_Y1})"
        )


# ---------------------------------------------------------------------------
# 토픽 시드 변주 — 프로젝트 표준 컨벤션: sum(ord(c) * (i*k + c0)) % len(options),
# 축마다 (k, c0)를 다르게 줘서 accent/배경/체크박스 모양이 서로 다른 주기로 순환.
# ---------------------------------------------------------------------------
ACCENT_PALETTE: list[tuple[int, int, int]] = [
    (27, 148, 123),
    (200, 90, 60),
    (74, 110, 200),
    (150, 90, 190),
    (200, 140, 40),
    (170, 60, 110),
]
BG_TONES: list[tuple[int, int, int]] = [
    (250, 247, 242),
    (235, 242, 245),
    (238, 244, 236),
    (243, 238, 246),
    (247, 238, 232),
]
CHECKBOX_SHAPES = ["rounded_square", "circle"]


def _accent_for_seed(seed: str) -> tuple[int, int, int]:
    idx = sum(ord(c) for c in seed) % len(ACCENT_PALETTE)
    return ACCENT_PALETTE[idx]


def _bg_variant_for_seed(seed: str) -> tuple[str, tuple[int, int, int], tuple[int, int, int]]:
    tone_idx = sum(ord(c) * (i + 1) for i, c in enumerate(seed)) % len(BG_TONES)
    mode = "gradient" if sum(ord(c) * (i * 3 + 2) for i, c in enumerate(seed)) % 2 == 0 else "solid"
    top = BG_TONES[tone_idx]
    bottom = tuple(max(0, round(c * 0.94)) for c in top)
    return (mode, top, bottom)


def _checkbox_shape_for_seed(seed: str) -> str:
    idx = sum(ord(c) * (i * 2 + 1) for i, c in enumerate(seed)) % len(CHECKBOX_SHAPES)
    return CHECKBOX_SHAPES[idx]


TEXT_DARK = (34, 45, 56)
TEXT_GRAY = (120, 128, 138)
BOX_BORDER = (196, 203, 212)
CARD_WHITE = (255, 255, 255)
SHADOW = (20, 30, 40)


def _accent_soft(accent: tuple[int, int, int]) -> tuple[int, int, int]:
    """eyebrow 배지 배경용 — accent를 흰색 쪽으로 옅게 섞는다(혼합비 ~0.83)."""
    return tuple(round(c + (255 - c) * 0.83) for c in accent)


# WHY 언어별 딕셔너리(2026-08-05 버그 수정, "콩팥_1 일본어 영상 격자 네모" 실제
# 발견): 이 3개 라벨이 lang과 무관하게 한국어 리터럴로 고정돼 있어서, 한글
# 글리프가 없는 언어별 폰트로 그리면 빈 사각형(tofu box)으로 깨졌다 — 다른
# 화면 텍스트는 다 lang에 맞는 폰트/문구를 쓰는데 이 eyebrow 배지만 예외였음.
EYEBROW_SELFCHECK_BY_LANG = {
    "kor": "자가진단", "en": "Self-Check", "ja": "セルフチェック",
    "es": "Autochequeo", "pt": "Autoavaliação", "ru": "Самопроверка",
}
EYEBROW_CAUSE_BY_LANG = {
    "kor": "원인 분석", "en": "Root Cause", "ja": "原因分析",
    "es": "La Causa", "pt": "A Causa", "ru": "Причина",
}
EYEBROW_WRAPUP_BY_LANG = {
    "kor": "마무리", "en": "Wrap-Up", "ja": "まとめ",
    "es": "Resumen", "pt": "Resumo", "ru": "Итог",
}
CLOSING_TIP_HEADER_BY_LANG = {
    "kor": "마무리 팁", "en": "Wrap-Up Tip", "ja": "まとめのコツ",
    "es": "Consejo Final", "pt": "Dica Final", "ru": "Итоговый совет",
}
CHECKLIST_HEADER_BEFORE = "확인해야 할 3가지"
CHECKLIST_HEADER_AFTER = "오늘부터 이렇게"
MODE_FADE = 0.4
ITEM_FADE = 0.45
ITEM_FIX_FADE = 0.45


def ease_out_cubic(x: float) -> float:
    x = max(0, min(1, x))
    return 1 - (1 - x) ** 3


def progress(t: float, start: float, dur: float) -> float:
    return ease_out_cubic((t - start) / dur)


# ---------------------------------------------------------------------------
# 폰트/텍스트 레이아웃
# ---------------------------------------------------------------------------
_FONT_CACHE: dict[tuple[str, int, int], "ImageFont.FreeTypeFont"] = {}


def _load_font(path: str, index: int, size: int) -> "ImageFont.FreeTypeFont":
    key = (path, index, size)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, size, index=index)
    return _FONT_CACHE[key]


def _layout_multiline(
    draw, raw_lines, font_path, font_index, base_size,
    max_width, max_height, lang, min_size=18, line_h_ratio=1.28,
):
    """`raw_lines`(작성자가 미리 나눠둔 줄 또는 단일 문단)를 `max_width` 폭에
    맞게 줄바꿈하고, 전체 높이가 `max_height`를 넘으면 폰트 크기를 줄여가며
    다시 줄바꿈한다 — `min_size`까지 줄여도 안 맞으면 마지막 줄에 말줄임표를
    붙여 강제로 잘라낸다(자리표시자 텍스트가 몇 배로 길어져도 절대 세이프
    영역을 침범하지 않게 하는 마지막 안전장치).
    """
    size = base_size
    while True:
        f = _load_font(font_path, font_index, size)
        wrapped = []
        for line in raw_lines:
            wrapped.extend(_wrap_text_for_lang(draw, line, f, max_width, lang) or [""])
        line_h = round(size * line_h_ratio)
        total_h = line_h * max(len(wrapped), 1)
        if total_h <= max_height or size <= min_size:
            if total_h > max_height and line_h > 0:
                max_lines = max(1, int(max_height // line_h))
                if len(wrapped) > max_lines:
                    wrapped = wrapped[:max_lines]
                    wrapped[-1] = wrapped[-1].rstrip() + "…"
            return (wrapped, f, line_h)
        size -= 2


def draw_centered_lines(draw, lines, f, center_x, top_y, line_h, fill, alpha=255, label="centered-text"):
    """가운데 정렬로 여러 줄을 그리고, 실제로 렌더된 bbox가 세이프 영역
    안인지 검사한다. 반환값은 마지막 줄 아래 y좌표(다음 요소 배치용)."""
    if not lines:
        return top_y
    color = fill + (alpha,) if len(fill) == 3 else fill
    bx0 = math.inf
    by0 = math.inf
    bx1 = -math.inf
    by1 = -math.inf
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=f)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = center_x - tw / 2 - bbox[0]
        y = top_y + i * line_h - bbox[1]
        draw.text((round(x), round(y)), line, font=f, fill=color)
        ly0 = top_y + i * line_h
        lx0 = center_x - tw / 2
        bx0 = min(bx0, lx0)
        by0 = min(by0, ly0)
        bx1 = max(bx1, lx0 + tw)
        by1 = max(by1, ly0 + th)
    _assert_within_safe_area(label, (bx0, by0, bx1, by1))
    return top_y + len(lines) * line_h


def draw_lines_left(draw, lines, f, x, top_y, line_h, fill, alpha=255, label="left-text"):
    if not lines:
        return top_y
    color = fill + (alpha,) if len(fill) == 3 else fill
    bx0 = math.inf
    by0 = math.inf
    bx1 = -math.inf
    by1 = -math.inf
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=f)
        draw.text((round(x), round(top_y + i * line_h - bbox[1])), line, font=f, fill=color)
        ly0 = top_y + i * line_h
        lx0 = x + bbox[0]
        ly1 = ly0 + (bbox[3] - bbox[1])
        lx1 = x + bbox[2]
        bx0 = min(bx0, lx0)
        by0 = min(by0, ly0)
        bx1 = max(bx1, lx1)
        by1 = max(by1, ly1)
    _assert_within_safe_area(label, (bx0, by0, bx1, by1))
    return top_y + len(lines) * line_h


def draw_eyebrow(canvas, draw, text, f, center_x, y, accent, accent_soft, alpha=255, label="eyebrow"):
    bbox = draw.textbbox((0, 0), text, font=f)
    th = bbox[3] - bbox[1]
    tw = bbox[2] - bbox[0]
    pad_x, pad_y = 34, 16
    pill_h = th + pad_y * 2
    pill_w = tw + pad_x * 2
    x0 = center_x - pill_w / 2
    pill = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pill)
    pd.rounded_rectangle(
        [round(x0), round(y), round(x0 + pill_w), round(y + pill_h)],
        radius=round(pill_h // 2), fill=accent_soft + (alpha,),
    )
    pd.text((round(x0 + pad_x - bbox[0]), round(y + pad_y - bbox[1])), text, font=f, fill=accent + (alpha,))
    canvas.alpha_composite(pill)
    _assert_within_safe_area(label, (x0, y, x0 + pill_w, y + pill_h))
    return y + pill_h


def _build_background(mode: str, top, bottom) -> "Image.Image":
    if mode == "solid":
        return Image.new("RGB", (W, H), top)
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


_ICON_CACHE: dict[tuple[Path, int], "Image.Image"] = {}


def get_icon(path: Path, size: int) -> "Image.Image":
    key = (path, size)
    if key not in _ICON_CACHE:
        img = Image.open(path).convert("RGB")
        w, h = img.size
        side = min(w, h)
        top = (h - side) // 2
        left = (w - side) // 2
        img = img.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS)
        mask = Image.new("L", (size, size), 0)
        md = ImageDraw.Draw(mask)
        md.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=255)
        rgba = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        rgba.paste(img, (0, 0))
        rgba.putalpha(mask)
        _ICON_CACHE[key] = rgba
    return _ICON_CACHE[key]


def _remove_chroma(img: Image.Image, thresh: int = 160) -> Image.Image:
    """캐릭터 일러스트는 Kling/Gemini 생성 단계에서 크로마키 배경(코너 픽셀 색을
    자동으로 키 색상 채택 — 캐릭터 자체가 초록 계열이면 배경이 파란/마젠타로
    바뀌므로 하드코딩 금지)으로 만들어진다 — `card_news.py`의
    `_remove_chroma_bg`, `proto_before_after_transition.py`의 `_remove_chroma`와
    동일한 원리. 이 파일의 체크리스트 행 아이콘(`get_icon`)은 작게(64~130px)
    표시돼 배경색이 스티커 프레임처럼 보여 그대로 둬도 무리 없지만, 오프닝
    화면은 이미지를 거의 카드 전체 크기로 키우므로 크로마 배경을 그대로 두면
    자간진단 카드가 아니라 "깨진 초록/마젠타 스크린"처럼 보인다 — 반드시
    투명 처리 후 흰 카드 위에 올린다."""
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


_COVER_CACHE: dict[tuple[Path, int, int], "Image.Image"] = {}


def get_cover_card_image(path: Path, box_w: int, box_h: int) -> "Image.Image":
    """오프닝 화면의 커버 이미지 카드용 — 크로마 배경을 제거한 캐릭터를 정사각형
    그대로(왜곡 없이) box 안에 맞춰 중앙 배치한 투명 배경 RGBA를 반환한다.
    호출부가 이미 흰 패널(`draw_shadowed_panel`)을 먼저 그려두므로, 투명한
    영역은 자연스럽게 그 흰 카드가 비쳐 보인다. 프레임마다(제목 화면 지속
    시간 + 다음 모드로의 크로스페이드 구간) 반복 호출되므로 `get_icon`과 같은
    캐싱 패턴을 그대로 따른다 — 크로마 제거는 픽셀 단위 순회라 느려서
    프레임마다 다시 계산하면 안 된다."""
    key = (path, box_w, box_h)
    if key not in _COVER_CACHE:
        square = min(box_w, box_h)
        raw = Image.open(path).convert("RGB").resize((square, square), Image.LANCZOS)
        raw = _remove_chroma(raw)
        canvas = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
        cx = (box_w - square) // 2
        cy = (box_h - square) // 2
        canvas.alpha_composite(raw, (cx, cy))
        _COVER_CACHE[key] = canvas
    return _COVER_CACHE[key]


def draw_checkbox(canvas, x, y, size, p, accent, shape):
    """p=0이면 빈 체크박스(테두리만), p>0이면 채워진 박스 위에 체크마크를
    두 획으로 나눠 그린다 — p<=0.5는 첫 획, p>0.5는 첫 획 완성+두 번째 획이
    진행되어 "체크마크가 그려지는" 애니메이션처럼 보인다."""
    box = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    radius = int(size * 0.22)

    def _outline():
        if shape == "circle":
            bd.ellipse([0, 0, size - 1, size - 1], fill=(255, 255, 255, 255),
                       outline=BOX_BORDER + (255,), width=5)
        else:
            bd.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius,
                                  fill=(255, 255, 255, 255), outline=BOX_BORDER + (255,), width=5)

    def _filled():
        if shape == "circle":
            bd.ellipse([0, 0, size - 1, size - 1], fill=accent + (255,))
        else:
            bd.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=accent + (255,))

    if p <= 0.001:
        _outline()
    else:
        _filled()
        pts = [
            (0.2 * size, 0.55 * size),
            (0.42 * size, 0.75 * size),
            (0.83 * size, 0.27 * size),
        ]
        width = max(6, size // 11)
        if p <= 0.5:
            t2 = p / 0.5
            x1 = pts[0][0] + (pts[1][0] - pts[0][0]) * t2
            y1 = pts[0][1] + (pts[1][1] - pts[0][1]) * t2
            bd.line([pts[0], (x1, y1)], fill=(255, 255, 255, 255), width=width, joint="curve")
        else:
            bd.line([pts[0], pts[1]], fill=(255, 255, 255, 255), width=width, joint="curve")
            t2 = (p - 0.5) / 0.5
            x2 = pts[1][0] + (pts[2][0] - pts[1][0]) * t2
            y2 = pts[1][1] + (pts[2][1] - pts[1][1]) * t2
            bd.line([pts[1], (x2, y2)], fill=(255, 255, 255, 255), width=width, joint="curve")
    canvas.alpha_composite(box, (round(x), round(y)))


def draw_shadowed_panel(canvas, box, radius, fill=(255, 255, 255, 235)):
    x0, y0, x1, y1 = box
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([round(x0), round(y0 + 18), round(x1), round(y1 + 18)],
                          radius=radius, fill=SHADOW + (60,))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    canvas.alpha_composite(shadow)
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([round(x0), round(y0), round(x1), round(y1)], radius=radius, fill=fill)
    canvas.alpha_composite(panel)


# ---------------------------------------------------------------------------
# spec 파싱 / 타이밍 / 레이아웃
# ---------------------------------------------------------------------------
def _join_body(body: list[str]) -> str:
    """spec의 body는 빈 문자열로 문단을 구분한 줄 리스트 — 화면엔 한 문단처럼
    흘려 보여주므로 빈 줄은 건너뛰고 공백으로 이어붙인다."""
    return " ".join(line for line in body if line)


def _load_items(spec: dict) -> tuple[str, str, list[dict]]:
    """spec["items"][0]은 "왜 이런 문제가 생길까요" 원인 카드, items[1:]는
    (원인, 대안) 쌍이 순서대로 배열돼 있다 — 쌍의 개수(=체크리스트 항목 개수)를
    여기서 직접 세므로, 항목이 3개든 5개든 코드 변경 없이 그대로 동작한다."""
    why_spec = spec["items"][0]
    why_header = why_spec["name"]
    why_body = _join_body(why_spec["body"])
    pair_items = spec["items"][1:]
    if len(pair_items) % 2 != 0 or not pair_items:
        raise RuntimeError(
            f"[proto_checklist] items[1:]는 (원인, 대안) 쌍이어야 하는데 "
            f"{len(pair_items)}개입니다 — card_news_spec.json 구조를 확인할 것"
        )
    items = [
        {
            "label": cause["name"],
            "fact": _join_body(cause["body"]),
            "fix": _join_body(fix["body"]),
            "icon": ITEM_ICON_DIR / cause["char_file"],
        }
        for cause, fix in zip(pair_items[0::2], pair_items[1::2])
    ]
    return (why_header, why_body, items)


def _proportional_durations(total: float, weights: list[float], min_dur: float) -> list[float]:
    """total 시간을 weights 비례로 나눈다(`proto_before_after_transition.py`와
    동일한 검증된 로직) — min_dur 미만으로 떨어지는 항목은 바닥을 대주고
    나머지 항목에서 비례로 빌려온다."""
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
    boosted[-1] += total - sum(boosted)
    return boosted


def _build_timing(cues: list[tuple[float, float, str]], total_duration: float, n_items: int,
                   items: list[dict]) -> dict:
    """srt 큐(2번째=원인 설명 시작, 3번째=체크리스트 시작으로 가정)를 기준으로
    화면 구간을 나눈다.
    WHY 텍스트 길이 비례 배분(2026-08-05, 전립선_1 실측 검증 중 발견 — 이전엔
    "원인 55%/대안 45%"를 항목 개수로 균등 스태거링만 했는데, 원인·대안이
    각각 개별 문장으로 시차 있게 내레이션되는 topic(예: 전립선_1)에서는 대안1
    체크가 실제 내레이션보다 8.7초나 늦게 뜨는 심각한 어긋남이 실측으로
    확인됐다. `proto_before_after_transition.py`가 이미 검증한 해법과 동일
    원칙 — SRT 구간 수를 믿는 대신(내레이션이 "모든 N가지 대안"을 마지막
    한 문장에 압축하기도 해서 구간 수가 topic마다 들쭉날쭉함), 원인·대안
    각각의 실제 본문 글자 수를 "비트" 가중치로 써서 checklist_dur를 비례
    배분한다 — 원인/대안이 각각 따로 내레이션되는 topic·마지막에 압축되는
    topic 둘 다에서 자연스럽게 맞아떨어진다."""
    if len(cues) > 1:
        why_start = cues[1][0]
    else:
        why_start = min(total_duration * 0.12, max(total_duration - 2, 0))
    if len(cues) > 2:
        list_start = cues[2][0]
    else:
        list_start = why_start + max(total_duration * 0.15, 2)
    list_start = max(list_start, why_start + 1)
    closing_reserve = min(4, max(total_duration * 0.12, 2))
    closing_start = total_duration - closing_reserve
    min_checklist_dur = 1.2 * n_items
    if closing_start - list_start < min_checklist_dur:
        closing_start = min(list_start + min_checklist_dur, total_duration)
    checklist_dur = max(closing_start - list_start, 0.01)

    weights = []
    for it in items:
        weights.append(max(len(it["fact"]), 1))
        weights.append(max(len(it["fix"]), 1))
    durs = _proportional_durations(checklist_dur, weights, min_dur=max(checklist_dur * 0.04, 0.6))

    check_times, fix_times = [], []
    t = list_start
    for i in range(n_items):
        check_times.append(t)
        t += durs[2 * i]
        fix_times.append(t)
        t += durs[2 * i + 1]
    return {
        "why_start": why_start,
        "list_start": list_start,
        "closing_start": closing_start,
        "check_times": check_times,
        "fix_times": fix_times,
    }


def _checklist_layout(measure_draw, items, n_items, font_path, font_index, lang, panel_top) -> dict:
    card_x0 = 90
    card_x1 = min(990, SAFE_X1 - 20)
    usable_height = SAFE_Y1 - panel_top - 40
    row_h = None
    row_gap = 36
    for gap_try in (36, 24, 16, 12):
        candidate = (usable_height - (n_items - 1) * gap_try) / n_items
        if candidate >= 130:
            row_h = min(candidate, 380)
            row_gap = gap_try
            break
    if row_h is None:
        # 항목이 너무 많아 표준 gap으로는 안 맞을 때 — 최소 행 높이(90)까지
        # 압축해서라도 세이프 영역 안에 배치를 시도한다.
        row_gap = 10
        row_h = max((usable_height - (n_items - 1) * row_gap) / n_items, 90)
    panel_bottom = panel_top + n_items * row_h + (n_items - 1) * row_gap + 40
    if panel_bottom > SAFE_Y1 + 1:
        raise RuntimeError(
            f"[proto_checklist] 체크리스트 항목이 너무 많아({n_items}개) "
            f"세이프 영역 안에 배치할 수 없습니다 — panel_bottom={panel_bottom:.0f} > {SAFE_Y1}"
        )
    box_size = round(min(max(row_h * 0.259, 56), 100))
    icon_size = round(min(max(row_h * 0.318, 64), 130))
    box_pad_left = 60
    text_left = card_x0 + box_pad_left + box_size + 40
    icon_x = card_x1 - 40 - icon_size
    max_w = max(icon_x - 30 - text_left, 200)
    label_size = round(min(max(row_h * 0.147, 28), 54))
    label_font = _load_font(font_path, font_index, label_size)
    label_line_h = round(label_size * 1.2)
    body_base_size = round(min(max(row_h * 0.082, 18), 30))

    rows = []
    for i, item in enumerate(items):
        row_top = panel_top + 40 + i * (row_h + row_gap)
        box_y = round(row_top + (row_h - box_size) / 2 - row_h * 0.088)
        icon_y = round(row_top + (row_h - icon_size) / 2)
        label_lines = _wrap_text_for_lang(measure_draw, item["label"], label_font, max_w, lang) or [""]
        max_label_lines = 2
        if len(label_lines) > max_label_lines:
            label_lines = label_lines[:max_label_lines]
            label_lines[-1] = label_lines[-1].rstrip() + "…"
        label_h = len(label_lines) * label_line_h
        body_top = box_y + 6 + label_h + 12
        body_max_h = max(row_top + row_h - body_top - 16, body_base_size * 1.28)
        fact_lines, fact_font, fact_line_h = _layout_multiline(
            measure_draw, [item["fact"]], font_path, font_index, body_base_size,
            max_w, body_max_h, lang, min_size=16,
        )
        fix_lines, fix_font, fix_line_h = _layout_multiline(
            measure_draw, [item["fix"]], font_path, font_index, body_base_size,
            max_w, body_max_h, lang, min_size=16,
        )
        rows.append({
            "label_lines": label_lines, "label_font": label_font, "label_line_h": label_line_h,
            "box_x": card_x0 + box_pad_left, "box_y": box_y,
            "icon_x": icon_x, "icon_y": icon_y,
            "row_top": row_top, "text_left": text_left, "body_top": body_top,
            "fact_lines": fact_lines, "fact_font": fact_font, "fact_line_h": fact_line_h,
            "fix_lines": fix_lines, "fix_font": fix_font, "fix_line_h": fix_line_h,
            "icon": item["icon"],
        })
    return {
        "card_x0": card_x0, "card_x1": card_x1,
        "panel_top": panel_top, "panel_bottom": panel_bottom,
        "row_h": row_h, "row_gap": row_gap,
        "box_size": box_size, "icon_size": icon_size,
        "rows": rows,
    }


# ---------------------------------------------------------------------------
# Ctx — topic 하나의 렌더링에 필요한 모든 상태(콘텐츠/변주/타이밍/레이아웃)를
# 갖고 있다. 여러 topic을 반복 렌더링해도 서로 상태를 공유하지 않는다.
# ---------------------------------------------------------------------------
class Ctx:
    def __init__(self, topic_dir, lang, audio_path, srt_path, spec_path, out_path, total_duration):
        self.topic_dir = topic_dir
        self.lang = lang
        self.audio_path = audio_path
        self.srt_path = srt_path
        self.spec_path = spec_path
        self.out_path = out_path
        self.total_duration = total_duration

        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)
        self.spec = spec

        title_full = list(spec["title"])
        self.title_main_lines = title_full[:-1] if len(title_full) > 1 else title_full
        self.title_sub = title_full[-1] if len(title_full) > 1 else ""
        title_seed = " ".join(title_full)

        self.why_header, self.why_body, self.items = _load_items(spec)
        self.n_items = len(self.items)
        self.closing_tip = list(spec["closing"]["tip"])
        self.closing_cta = spec["closing"]["cta"]

        # 오프닝 화면의 시각적 앵커 — card_news_spec.json의 cover_char_file을
        # 우선 쓰고, 없는 과거 spec은 첫 체크리스트 항목 아이콘으로 대체한다
        # (그래도 없으면 None -> render_title이 빈 체크박스 폴백으로 처리).
        cover_file = spec.get("cover_char_file")
        if cover_file:
            self.cover_image_path = ITEM_ICON_DIR / cover_file
        elif self.items:
            self.cover_image_path = self.items[0]["icon"]
        else:
            self.cover_image_path = None

        self.font_path, self.font_index = _title_font_for_lang(lang)

        # 토픽 시드 변주 — accent 색상 / 배경 톤·모드 / 체크박스 모양
        self.accent = _accent_for_seed(title_seed)
        self.accent_soft = _accent_soft(self.accent)
        bg_mode, bg_top, bg_bottom = _bg_variant_for_seed(title_seed)
        self.bg_base = _build_background(bg_mode, bg_top, bg_bottom)
        self.checkbox_shape = _checkbox_shape_for_seed(title_seed)
        # WHY y_jitter(2026-08-05, "저품질/반복" 정책 리스크 대응): topic마다
        # 오프닝(프레임 0=사실상 썸네일) eyebrow 시작 위치를 ±20px 정도 미세
        # 이동 — title_eyebrow_y가 아래 avail/text_avail 계산의 기준점이라
        # 여기서만 흔들어도 텍스트·카드 배분 전체가 자동으로 안전하게 맞춰짐.
        self.y_jitter = sum(ord(c) * (i * 5 + 3) for i, c in enumerate(title_seed)) % 41 - 20

        cues = _parse_srt(str(srt_path))
        self.timing = _build_timing(cues, total_duration, self.n_items, self.items)
        self.modes = [
            ("title", 0, self.timing["why_start"]),
            ("why", self.timing["why_start"], self.timing["list_start"]),
            ("checklist", self.timing["list_start"], self.timing["closing_start"]),
            ("closing", self.timing["closing_start"], None),
        ]

        measure_draw = ImageDraw.Draw(Image.new("RGBA", (2, 2)))

        # 체크리스트 화면 헤더("확인해야 할 3가지" -> "오늘부터 이렇게") 높이를
        # 먼저 추정해 panel_top(카드 시작 y)을 계산한다.
        header_font = _load_font(self.font_path, self.font_index, 60)
        header_lines_a = _wrap_text_for_lang(
            measure_draw, CHECKLIST_HEADER_BEFORE, header_font, SAFE_CENTERED_MAX_WIDTH, lang
        ) or [""]
        header_lines_b = _wrap_text_for_lang(
            measure_draw, CHECKLIST_HEADER_AFTER, header_font, SAFE_CENTERED_MAX_WIDTH, lang
        ) or [""]
        header_line_h = round(75)
        header_lines_count = max(len(header_lines_a), len(header_lines_b))
        eyebrow_h_est = round(48) + 32
        header_top = 110 + eyebrow_h_est + 55
        header_bottom = header_top + header_lines_count * header_line_h
        panel_top = header_bottom + 40
        self.checklist_header_font = header_font
        self.checklist_header_top = header_top
        self.checklist_layout = _checklist_layout(
            measure_draw, self.items, self.n_items, self.font_path, self.font_index, lang, panel_top
        )

        # title 화면(=업로드 썸네일 대체 프레임): 헤드라인 + (선택) 서브헤드 +
        # 커버 이미지 카드. 헤드라인·서브헤드는 상단에 짧게 캡핑하고, 나머지
        # 세로 공간은 전부 커버 이미지 카드에 넘겨 하단이 비지 않게 한다 —
        # 예전엔 eyebrow를 y=300에서 시작해 상단도 비고, 아이콘 하나(300px
        # 예약)만 놓고 그 아래 전부 배경만 남아 캔버스 하단 절반이 빈 채로
        # 남았었다(진단된 문제). eyebrow를 checklist 화면과 비슷하게 위로
        # 당겨서 그만큼을 이미지 카드 몫으로 돌린다.
        self.title_eyebrow_y = 90 + self.y_jitter
        text_top_est = self.title_eyebrow_y + eyebrow_h_est + 46
        text_block_budget = 480
        avail = max(SAFE_Y1 - text_top_est - 40, 200)
        text_avail = min(text_block_budget, avail)
        self.title_lines, self.title_font, self.title_line_h = _layout_multiline(
            measure_draw, self.title_main_lines, self.font_path, self.font_index, 76,
            min(940, SAFE_CENTERED_MAX_WIDTH), text_avail * 0.66, lang, min_size=40,
        )
        self.title_sub_lines, self.title_sub_font, self.title_sub_line_h = _layout_multiline(
            measure_draw, [self.title_sub] if self.title_sub else [], self.font_path, self.font_index, 40,
            min(860, SAFE_CENTERED_MAX_WIDTH), text_avail * 0.34, lang, min_size=22,
        )

        # why 화면: 원인 헤드라인 + 본문
        why_body_top_est = 420 + eyebrow_h_est + 70 + 100
        why_avail = max(SAFE_Y1 - why_body_top_est - 40, 160)
        self.why_header_lines, self.why_header_font, self.why_header_line_h = _layout_multiline(
            measure_draw, [self.why_header], self.font_path, self.font_index, 66,
            min(900, SAFE_CENTERED_MAX_WIDTH), 220, lang, min_size=36,
        )
        self.why_body_lines, self.why_body_font, self.why_body_line_h = _layout_multiline(
            measure_draw, [self.why_body], self.font_path, self.font_index, 42,
            min(900, SAFE_CENTERED_MAX_WIDTH), why_avail, lang, min_size=22,
        )

        # closing 화면: 헤드라인 + 팁 + CTA
        closing_start_y_est = 420 + eyebrow_h_est + 70
        closing_avail = max(SAFE_Y1 - closing_start_y_est - 40, 240)
        self.closing_header_lines, self.closing_header_font, self.closing_header_line_h = _layout_multiline(
            measure_draw, [CLOSING_TIP_HEADER_BY_LANG.get(lang, CLOSING_TIP_HEADER_BY_LANG["en"])], self.font_path, self.font_index, 66,
            min(900, SAFE_CENTERED_MAX_WIDTH), closing_avail * 0.2, lang, min_size=36,
        )
        self.closing_tip_lines, self.closing_tip_font, self.closing_tip_line_h = _layout_multiline(
            measure_draw, self.closing_tip, self.font_path, self.font_index, 46,
            min(900, SAFE_CENTERED_MAX_WIDTH), closing_avail * 0.48, lang, min_size=26,
        )
        self.closing_cta_lines, self.closing_cta_font, self.closing_cta_line_h = _layout_multiline(
            measure_draw, [self.closing_cta], self.font_path, self.font_index, 32,
            min(780, SAFE_CENTERED_MAX_WIDTH), closing_avail * 0.32, lang, min_size=20,
        )

    def font(self, size):
        return _load_font(self.font_path, self.font_index, size)

    def get_bg(self):
        return self.bg_base.copy()


# ---------------------------------------------------------------------------
# 화면별 렌더 함수
# ---------------------------------------------------------------------------
def render_title(ctx: Ctx):
    """오프닝/타이틀 화면 — 이 파이프라인은 커스텀 썸네일을 따로 업로드하지
    않으므로(`lib/youtube_upload.py` 확인됨) 이 프레임이 피드에서 사실상
    썸네일 역할을 한다. 헤드라인 아래 커버 이미지 카드를 크게 채워 하단이
    비지 않게 하고, 카드 위에는 아직 "체크되지 않은" 빈 체크박스만 겹쳐
    자가진단 정체성을 유지한다 — 실제 체크(완료 상태)는 체크리스트 화면에서만
    등장해야 내레이션 흐름과 맞다(오프닝에서 이미 채워진 체크마크를 보여주면
    "이미 끝난 일"처럼 읽혀 혼란을 준다)."""
    canvas = ctx.get_bg().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    cx = W // 2
    y = draw_eyebrow(canvas, draw, EYEBROW_SELFCHECK_BY_LANG.get(ctx.lang, EYEBROW_SELFCHECK_BY_LANG["en"]), ctx.font(30), cx, ctx.title_eyebrow_y,
                      ctx.accent, ctx.accent_soft, label="title-eyebrow")
    y = draw_centered_lines(draw, ctx.title_lines, ctx.title_font, cx, y + 46, ctx.title_line_h,
                             TEXT_DARK, label="title-main")
    sub_y = y + 26
    if ctx.title_sub_lines:
        sub_y = draw_centered_lines(draw, ctx.title_sub_lines, ctx.title_sub_font, cx, sub_y,
                                     ctx.title_sub_line_h, ctx.accent, label="title-sub")

    # WHY SAFE_CENTERED_MAX_WIDTH로 폭을 캡핑하는지(2026-08-05 수정, 사용자
    # 지적 "쏠림 있는데 수정 안 한거같은데" — 이전 주석의 "세이프 영역
    # 자체를 기준으로 하므로 비대칭 버그가 재발할 여지 없다"는 판단이
    # 틀렸었다): 세이프 영역 자체(50~930)가 캔버스 진짜 중앙(540) 기준으로
    # 이미 비대칭이라, 그 전체 폭을 그대로 카드에 쓰면 카드 중심이 490에
    # 맞춰져 화면 전체로 보면 왼쪽으로 쏠려 보인다. SAFE_CENTERED_MAX_WIDTH
    # (540 기준 좌우 대칭 최대폭)로 카드 폭을 캡핑하고 540에 중앙정렬해야
    # 두 조건(안전영역 준수 + 눈으로 봤을 때 중앙)이 동시에 만족된다.
    card_top = sub_y + 44
    card_w_capped = SAFE_CENTERED_MAX_WIDTH
    card_x0 = _CENTER_X - card_w_capped // 2
    card_x1 = _CENTER_X + card_w_capped // 2
    card_bottom = SAFE_Y1
    card_w = card_x1 - card_x0
    card_h = card_bottom - card_top
    if card_h > 120:
        radius = 40
        draw_shadowed_panel(canvas, (card_x0, card_top, card_x1, card_bottom), radius=radius)
        if ctx.cover_image_path and ctx.cover_image_path.exists():
            inner_pad = 14
            img_box_w = round(card_w - inner_pad * 2)
            img_box_h = round(card_h - inner_pad * 2)
            cover = get_cover_card_image(ctx.cover_image_path, img_box_w, img_box_h)
            canvas.alpha_composite(cover, (round(card_x0 + inner_pad), round(card_top + inner_pad)))

            # "아직 체크 전"을 보여주는 빈 체크박스 배지 — 사진 위에서도 잘
            # 보이도록 부드러운 그림자를 깔고 그 위에 p=0(빈 박스)로 그린다.
            badge_size = min(96, round(card_h * 0.16))
            badge_x = card_x0 + 30
            badge_y = card_bottom - badge_size - 30
            shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            shadow_box = [badge_x - 8, badge_y + 8, badge_x + badge_size + 8, badge_y + badge_size + 20]
            if ctx.checkbox_shape == "circle":
                sd.ellipse(shadow_box, fill=SHADOW + (110,))
            else:
                sd.rounded_rectangle(shadow_box, radius=22, fill=SHADOW + (110,))
            shadow = shadow.filter(ImageFilter.GaussianBlur(12))
            canvas.alpha_composite(shadow)
            draw_checkbox(canvas, badge_x, badge_y, badge_size, 0, ctx.accent, ctx.checkbox_shape)
            # 기본 draw_checkbox 테두리(BOX_BORDER, 옅은 회색)는 흰 카드 위에서
            # 눈에 잘 안 띈다 — 배지 위에 accent색 링을 한 번 더 덧그려 토픽
            # 테마색과 연결되고 사진 배경 위에서도 또렷하게 보이게 한다.
            ring_box = [badge_x, badge_y, badge_x + badge_size - 1, badge_y + badge_size - 1]
            if ctx.checkbox_shape == "circle":
                draw.ellipse(ring_box, outline=ctx.accent + (255,), width=6)
            else:
                draw.rounded_rectangle(ring_box, radius=int(badge_size * 0.22),
                                        outline=ctx.accent + (255,), width=6)
        else:
            # 커버 이미지가 없는(과거 spec 등) topic 대비 폴백 — 카드 중앙에
            # 큼직한 빈 체크박스만 놓아도 이미지 없이 카드 공백은 채워진다.
            big_size = min(round(card_w * 0.42), round(card_h * 0.5), 260)
            bx = card_x0 + (card_w - big_size) // 2
            by = card_top + (card_h - big_size) // 2
            draw_checkbox(canvas, bx, by, big_size, 0, ctx.accent, ctx.checkbox_shape)
    return canvas


def render_why(ctx: Ctx):
    canvas = ctx.get_bg().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    cx = W // 2
    y = draw_eyebrow(canvas, draw, EYEBROW_CAUSE_BY_LANG.get(ctx.lang, EYEBROW_CAUSE_BY_LANG["en"]), ctx.font(30), cx, 420,
                      ctx.accent, ctx.accent_soft, label="why-eyebrow")
    y = draw_centered_lines(draw, ctx.why_header_lines, ctx.why_header_font, cx, y + 70,
                             ctx.why_header_line_h, TEXT_DARK, label="why-header")
    draw_centered_lines(draw, ctx.why_body_lines, ctx.why_body_font, cx, y + 30,
                         ctx.why_body_line_h, TEXT_GRAY, label="why-body")
    return canvas


def render_closing(ctx: Ctx):
    canvas = ctx.get_bg().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    cx = W // 2
    y = draw_eyebrow(canvas, draw, EYEBROW_WRAPUP_BY_LANG.get(ctx.lang, EYEBROW_WRAPUP_BY_LANG["en"]), ctx.font(30), cx, 420,
                      ctx.accent, ctx.accent_soft, label="closing-eyebrow")
    y = draw_centered_lines(draw, ctx.closing_header_lines, ctx.closing_header_font, cx, y + 70,
                             ctx.closing_header_line_h, TEXT_DARK, label="closing-header")
    y = draw_centered_lines(draw, ctx.closing_tip_lines, ctx.closing_tip_font, cx, y + 40,
                             ctx.closing_tip_line_h, TEXT_GRAY, label="closing-tip")
    draw_centered_lines(draw, ctx.closing_cta_lines, ctx.closing_cta_font, cx, y + 50,
                         ctx.closing_cta_line_h, ctx.accent, label="closing-cta")
    return canvas


def render_checklist(ctx: Ctx, t: float):
    canvas = ctx.get_bg().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    cx = W // 2
    layout = ctx.checklist_layout

    # 헤더 문구가 "확인해야 할 N가지" -> "오늘부터 이렇게"로 전환
    # (첫 fix_time을 기준으로 삼아, 대안이 하나라도 드러나기 시작하면 전환).
    # WHY 순차 페이드인지(2026-08-05, 실제 화면 확인 중 발견 — "체크리스트형
    # 위에도 겹치는 현상이 좀 있다"): 항목별 fact/fix 크로스페이드와 똑같은
    # 문제 — 서로 다른 문단 텍스트를 동시에 반투명 겹쳐 그리면 글자 단위로
    # 뒤섞여 읽을 수 없다. 전환 구간 앞 절반엔 이전 헤더만 페이드아웃, 뒤
    # 절반엔 새 헤더만 페이드인해서 겹치는 순간 자체를 없앤다.
    fixes_p = progress(t, ctx.timing["fix_times"][0], MODE_FADE)
    eyebrow_y = draw_eyebrow(canvas, draw, EYEBROW_SELFCHECK_BY_LANG.get(ctx.lang, EYEBROW_SELFCHECK_BY_LANG["en"]), ctx.font(30), cx, 110,
                              ctx.accent, ctx.accent_soft, label="checklist-eyebrow")
    header_top = eyebrow_y + 55
    if fixes_p <= 0.5:
        before_alpha = max(0, 1 - fixes_p * 2)
        after_alpha = 0
    else:
        before_alpha = 0
        after_alpha = min(1, (fixes_p - 0.5) * 2)
    if before_alpha > 0.01:
        draw_centered_lines(draw, [CHECKLIST_HEADER_BEFORE], ctx.checklist_header_font, cx, header_top, 0,
                             TEXT_DARK, alpha=int(255 * before_alpha), label="checklist-header-before")
    if after_alpha > 0.01:
        draw_centered_lines(draw, [CHECKLIST_HEADER_AFTER], ctx.checklist_header_font, cx, header_top, 0,
                             TEXT_DARK, alpha=int(255 * after_alpha), label="checklist-header-after")

    draw_shadowed_panel(
        canvas,
        (layout["card_x0"] - 20, layout["panel_top"], layout["card_x1"] + 20, layout["panel_bottom"]),
        radius=44,
    )

    check_times = ctx.timing["check_times"]
    fix_times = ctx.timing["fix_times"]
    for i, row in enumerate(layout["rows"]):
        p = progress(t, check_times[i], ITEM_FADE)
        draw_checkbox(canvas, row["box_x"], row["box_y"], layout["box_size"], p, ctx.accent, ctx.checkbox_shape)
        draw_lines_left(draw, row["label_lines"], row["label_font"], row["text_left"], row["box_y"] + 6,
                         row["label_line_h"], TEXT_DARK, 255, label=f"checklist-label-{i}")

        if p > 0.001:
            icon_img = get_icon(row["icon"], layout["icon_size"])
            if p < 1:
                icon_img = icon_img.copy()
                a = icon_img.split()[3].point(lambda v, p=p: int(v * p))
                icon_img.putalpha(a)
            canvas.alpha_composite(icon_img, (round(row["icon_x"]), round(row["icon_y"])))

        # cause(fact)에서 fix로 전환 — 순차 페이드(먼저 fact가 완전히
        # 사라진 뒤에 fix가 나타남), 진짜 크로스페이드 아님. WHY(2026-08-05,
        # 실제 화면 확인 중 발견 — "문제점->해결책으로 넘어갈 때 글자가
        # 겹쳐져 보인다"): fact/fix는 서로 다른 문단 텍스트라 체크박스·아이콘처럼
        # 동시에 반투명 겹쳐도 자연스러운 크로스페이드가 아니라, 두 문단이
        # 글자 단위로 뒤섞여 읽을 수 없는 상태로 보인다 — 전환 구간(0.45초)의
        # 앞 절반엔 fact만 페이드아웃, 뒤 절반엔 fix만 페이드인해서 겹치는
        # 순간 자체를 없앤다.
        item_fix_p = progress(t, fix_times[i], ITEM_FIX_FADE)
        if item_fix_p <= 0.5:
            fact_alpha = max(0, 1 - item_fix_p * 2) if p > 0 else 0
            fix_alpha = 0
        else:
            fact_alpha = 0
            fix_alpha = min(1, (item_fix_p - 0.5) * 2)
        if fact_alpha > 0.01:
            draw_lines_left(draw, row["fact_lines"], row["fact_font"], row["text_left"], row["body_top"],
                             row["fact_line_h"], TEXT_GRAY, int(255 * fact_alpha), label=f"checklist-fact-{i}")
        if fix_alpha > 0.01:
            draw_lines_left(draw, row["fix_lines"], row["fix_font"], row["text_left"], row["body_top"],
                             row["fix_line_h"], ctx.accent, int(255 * fix_alpha), label=f"checklist-fix-{i}")
    return canvas


def _render_mode(ctx: Ctx, idx: int, t: float):
    name = ctx.modes[idx][0]
    if name == "title":
        return render_title(ctx)
    if name == "why":
        return render_why(ctx)
    if name == "checklist":
        return render_checklist(ctx, t)
    return render_closing(ctx)


def render_frame(ctx: Ctx, t: float):
    idx = len(ctx.modes) - 1
    for i, (name, start, end) in enumerate(ctx.modes):
        if end is None or t < end:
            idx = i
            break
    name, start, end = ctx.modes[idx]
    frame = _render_mode(ctx, idx, t)
    if end is not None and end - t < MODE_FADE and idx + 1 < len(ctx.modes):
        blend = 1 - ease_out_cubic((end - t) / MODE_FADE)
        next_frame = _render_mode(ctx, idx + 1, t)
        frame = Image.blend(frame.convert("RGB"), next_frame.convert("RGB"), blend).convert("RGBA")
    return frame.convert("RGB")


# ---------------------------------------------------------------------------
# 엔트리포인트
# ---------------------------------------------------------------------------
def ffprobe_duration(path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def render(topic_dir: str, lang: str, audio_path: str, srt_path: str, spec_path: str, out_path: str) -> None:
    """임의의 topic 하나를 이 체크리스트 템플릿으로 렌더링한다 — 항목 개수는
    `spec_path`의 `items` 리스트에서 그대로 읽고, 폰트는 `lang`에 맞춰 자동으로
    고른다(다른 코드에서 여러 topic에 대해 반복 호출해도 서로 상태를 공유하지
    않는다 — 모든 콘텐츠/타이밍/레이아웃이 `Ctx` 인스턴스 안에만 산다).
    """
    audio_path = Path(audio_path)
    srt_path = Path(srt_path)
    spec_path = Path(spec_path)
    out_path = Path(out_path)
    topic_dir = Path(topic_dir)

    if not audio_path.exists():
        raise FileNotFoundError(f"narration audio not found: {audio_path}")
    if not srt_path.exists():
        raise FileNotFoundError(f"narration srt not found: {srt_path}")
    if not spec_path.exists():
        raise FileNotFoundError(f"card_news_spec.json not found: {spec_path}")

    duration = ffprobe_duration(audio_path)
    print(f"[proto_checklist] narration duration = {duration:.3f}s")

    ctx = Ctx(topic_dir, lang, audio_path, srt_path, spec_path, out_path, duration)
    print(f"[proto_checklist] items={ctx.n_items}, accent={ctx.accent}, checkbox_shape={ctx.checkbox_shape}")

    out_dir = out_path.parent
    frames_dir = out_dir / "_frames"
    out_dir.mkdir(parents=True, exist_ok=True)
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    frame_count = math.ceil(duration * FPS)
    print(f"[proto_checklist] rendering {frame_count} frames at {FPS}fps ...")
    for i in range(frame_count):
        t = min(i / FPS, duration)
        img = render_frame(ctx, t)
        img.save(frames_dir / f"frame_{i:06d}.png")
        if i % 150 == 0:
            print(f"  frame {i}/{frame_count} (t={t:.2f}s)")

    mixed_audio = mix_bgm(str(audio_path), str(frames_dir / "mixed_audio.m4a"), duration, topic_dir.name)

    print("[proto_checklist] muxing with ffmpeg ...")
    subprocess.run(
        [
            "ffmpeg", "-y",
            "-framerate", str(FPS),
            "-i", str(frames_dir / "frame_%06d.png"),
            "-i", mixed_audio,
            "-map", "0:v:0", "-map", "1:a:0",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "160k",
            "-t", f"{duration:.3f}",
            str(out_path),
        ],
        check=True,
    )
    shutil.rmtree(frames_dir)

    out_duration = ffprobe_duration(out_path)
    print(f"[proto_checklist] done -> {out_path}")
    print(f"[proto_checklist] output duration = {out_duration:.3f}s (audio = {duration:.3f}s)")


def main():
    """CLI 진입점 — 기존 하위호환 테스트용 경로(부종_1/ko)를 기본값으로 render()를
    호출한다."""
    topic_dir = PROJECT_ROOT / "output" / "부종_1" / "ko"
    render(
        topic_dir=str(topic_dir),
        lang="kor",
        audio_path=str(topic_dir / "부종_1_narration.mp3"),
        srt_path=str(topic_dir / "부종_1_narration.srt"),
        spec_path=str(PROJECT_ROOT / "data" / "부종_1" / "ko" / "card_news_spec.json"),
        out_path=str(PROJECT_ROOT / "output" / "_template_lab_ko" / "checklist" / "shorts.mp4"),
    )


if __name__ == "__main__":
    main()
