# 랭킹 카운트다운 포맷 Shorts 템플릿(프로토타입 → 프로덕션 하드닝, 2026-08-04).
# WHY: topic의 items를 #N(첫 내레이션)부터 #1(마지막 내레이션=최악, "최악은 마지막에
# 공개" 구조)까지 카운트다운으로 보여준다. card_news_spec.json의 items 개수를 그대로
# N으로 써서(하드코딩 3 금지) 임의 topic에 일반화한다. 이전 세션에서 이미 이 스펙대로
# 완성했었지만 커밋 전에 동시 세션의 git 작업으로 디스크에서 유실되어 그대로 재구현.
from __future__ import annotations

import colorsys
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

# WHY sys.path 조작: lib/templates/는 lib/의 하위 패키지라 상대 import가 아니라
# 프로젝트 루트를 경로에 넣고 절대 import(`from lib.video_assembler import ...`)한다 —
# 이 파일이 `python proto_ranking_countdown.py`로 단독 실행될 때도(CLI 진입점) 항상
# 동작해야 하므로 패키지 상대 import에 의존할 수 없다.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from lib.bgm import mix_bgm  # noqa: E402
from lib.video_assembler import _title_font_for_lang, _wrap_text_for_lang  # noqa: E402

W, H = 1080, 1920
FPS = 30

# WHY 로컬 복제(video_assembler.py의 값과 반드시 일치시킬 것): 원본은
# _place_chalk_doodle() 안의 함수-로컬 상수라 import가 불가능하다 — 유튜브 쇼츠
# 플레이어 자체 UI(오른쪽 좋아요/댓글/공유 아이콘 열, 하단 채널명·설명 캡션 띠)와
# 실기기에서 겹치지 않기 위한 안전 영역(대략치, 기기·버전마다 조금씩 다름).
_YT_SAFE_RIGHT = 150
_YT_SAFE_BOTTOM = 320
_SAFE_MARGIN = 24  # 요구사항의 "plus margin" — 안전영역 경계에 바짝 붙지 않게 하는 추가 여유

SAFE_RIGHT_X = W - _YT_SAFE_RIGHT - _SAFE_MARGIN
SAFE_BOTTOM_Y = H - _YT_SAFE_BOTTOM - _SAFE_MARGIN
CONTENT_LEFT = 48
# WHY 안전영역 중심(490 근처)이 아니라 캔버스 진짜 중앙(540)인지(2026-08-05
# 수정, 사용자가 스크린샷 보고 "한쪽으로 쏠림 있는데" 지적 — 바로 위 예전
# 주석의 "안전영역 중심을 기준으로 삼는다"는 판단이 원인이었다): 안전영역
# 자체(48~906)가 540 기준으로 이미 비대칭이라, 그 중심(≈477)에 배지·미니
# 순위띠를 맞추면 폭이 좁은 요소라도 화면 전체로 보면 왼쪽으로 쏠려 보인다.
# 이 템플릿의 배지(320px)·미니 순위띠는 어차피 안전영역 폭을 다 채우지
# 않으므로, 540에 중앙정렬해도 VISUAL_CENTER_MAX_WIDTH 안에만 들면 안전영역
# 위반이 안 난다 — 아래 텍스트 wrap 폭도 이 상수로 캡핑한다.
CONTENT_CENTER_X = W // 2
VISUAL_CENTER_MAX_WIDTH = 2 * min(CONTENT_CENTER_X - CONTENT_LEFT, SAFE_RIGHT_X - CONTENT_CENTER_X)


def _seed_axis(title: str, k: int, c0: int, n_options: int) -> int:
    """프로젝트 표준 결정론적 seed 공식. WHY: 내장 hash()는 프로세스마다 랜덤이라
    같은 topic을 다시 렌더링해도 매번 결과가 달라진다 — 문자 코드 합산 방식은
    항상 같은 입력에 같은 출력을 보장한다(재현 가능). 축마다 (k, c0)를 다르게 줘서
    색·배경 색상·뱃지 모양이 서로 독립적으로 갈리게 한다."""
    return sum(ord(c) * (i * k + c0) for i, c in enumerate(title)) % n_options


# ---- Axis 1: 뱃지 색상 램프(경고 색상 escalation) ----
# WHY 4가지 램프: "항상 파랑→호박색→빨강"이면 매번 같은 무드로 보인다는 요구사항
# 그대로 — "위험도 escalation" 논리는 유지하되(항상 차분한 색→경고색으로 진행)
# topic마다 실제 색 팔레트 자체는 바뀐다.
_BADGE_RAMPS: list[list[tuple[int, int, int]]] = [
    [(59, 130, 246), (250, 204, 21), (239, 68, 68)],   # 파랑 → 호박색 → 빨강
    [(45, 212, 191), (251, 146, 60), (220, 38, 38)],   # 청록 → 주황 → 진빨강
    [(168, 85, 247), (244, 63, 94), (127, 29, 29)],    # 보라 → 장미색 → 짙은 적갈색
    [(34, 197, 94), (234, 179, 8), (190, 18, 60)],     # 초록 → 금색 → 진홍
]


def _ramp_color(ramp: list[tuple[int, int, int]], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    n = len(ramp)
    pos = t * (n - 1)
    i = min(int(pos), n - 2)
    frac = pos - i
    a, b = ramp[i], ramp[i + 1]
    return tuple(round(a[ch] + (b[ch] - a[ch]) * frac) for ch in range(3))


# ---- Axis 2: 배경 그라디언트 색조(navy/purple 계열 안에서 seed) ----
def _hsv(h: float, s: float, v: float) -> tuple[int, int, int]:
    r, g, b = colorsys.hsv_to_rgb((h % 360) / 360.0, s, v)
    return round(r * 255), round(g * 255), round(b * 255)


def _make_background(base_hue: float) -> Image.Image:
    """세로 그라디언트(위: 짙은 navy, 아래: 조금 더 채도 높은 purple 톤) + 상하단
    비네트. WHY 1px 열로 만들고 resize: 1080x1920 전체를 픽셀 단위 for문으로 채우면
    느리다 — 세로 1픽셀짜리 그라디언트를 만들고 가로로 늘리는 쪽이 훨씬 빠르다."""
    top = _hsv(base_hue, 0.55, 0.11)
    bottom = _hsv((base_hue + 18) % 360, 0.62, 0.24)
    col = Image.new("RGB", (1, H))
    for y in range(H):
        t = y / (H - 1)
        col.putpixel((0, y), tuple(round(top[c] + (bottom[c] - top[c]) * t) for c in range(3)))
    bg = col.resize((W, H), Image.BILINEAR)

    # 상하단 비네트로 입체감 — 중앙이 살짝 밝고 위아래 가장자리가 더 어두워지게.
    vign = Image.new("L", (1, H), 0)
    for y in range(H):
        d = abs(y - H / 2) / (H / 2)
        vign.putpixel((0, y), round(70 * (d ** 1.6)))
    vign = vign.resize((W, H), Image.BILINEAR)
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(dark, bg, vign)


# ---- Axis 3: 뱃지 모양(원 vs 방패형) ----
def _supersample(size: tuple[int, int], draw_fn, scale: int = 4) -> Image.Image:
    """폴리곤 테두리 앤티앨리어싱용 — scale배 크게 그린 뒤 LANCZOS로 축소한다."""
    big = Image.new("RGBA", (size[0] * scale, size[1] * scale), (0, 0, 0, 0))
    d = ImageDraw.Draw(big)
    draw_fn(d, scale)
    return big.resize(size, Image.LANCZOS)


def _badge_circle(diameter: int, fill: tuple[int, int, int, int],
                   ring: tuple[int, int, int, int]) -> Image.Image:
    def draw_fn(d, scale):
        pad = 6 * scale
        box = [pad, pad, diameter * scale - pad, diameter * scale - pad]
        d.ellipse(box, fill=fill)
        d.ellipse(box, outline=ring, width=7 * scale)
    return _supersample((diameter, diameter), draw_fn)


def _badge_shield(diameter: int, fill: tuple[int, int, int, int],
                   ring: tuple[int, int, int, int]) -> Image.Image:
    def draw_fn(d, scale):
        pad = 10 * scale
        s = diameter * scale
        w = s - 2 * pad
        left, top, right = pad, pad, pad + w
        mid_y = pad + w * 0.55
        bottom = pad + w
        pts = [
            (left, top + w * 0.14),
            (left + w * 0.18, top),
            (right - w * 0.18, top),
            (right, top + w * 0.14),
            (right, mid_y),
            ((left + right) / 2, bottom),
            (left, mid_y),
        ]
        d.polygon(pts, fill=fill)
        d.line(pts + [pts[0]], fill=ring, width=7 * scale, joint="curve")
    return _supersample((diameter, diameter), draw_fn)


_BADGE_SHAPE_FNS = {"circle": _badge_circle, "shield": _badge_shield}


def _rounded_panel(w: int, h: int, radius: int, fill_rgba: tuple[int, int, int, int],
                    shadow_blur: int = 14, shadow_offset: tuple[int, int] = (0, 8),
                    shadow_alpha: int = 110) -> tuple[Image.Image, int]:
    """팩트 텍스트 뒤 반투명 패널 + 드롭섀도. WHY 이전에 실제로 터진 버그: 블러
    반경만큼 캔버스에 여유 패딩(pad)을 안 주고 그리면 블러가 이미지 경계에서
    잘리면서 오히려 더 날카로운 가짜 경계가 생기고, 패널을 안전영역 경계 가까이
    붙이면 이 블러 번짐이 안전영역 밖으로 새 나간다 — 여기서 pad를 리턴해서
    합성할 때 그만큼 왼쪽/위로 당겨 배치하게 하고, 최종 안전영역 검사가 실제로
    새는지 픽셀 단위로 다시 확인한다."""
    pad = shadow_blur * 2 + max(abs(shadow_offset[0]), abs(shadow_offset[1]))
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sx, sy = pad + shadow_offset[0], pad + shadow_offset[1]
    sd.rounded_rectangle([sx, sy, sx + w, sy + h], radius=radius, fill=(0, 0, 0, shadow_alpha))
    shadow = shadow.filter(ImageFilter.GaussianBlur(shadow_blur))
    canvas.alpha_composite(shadow)

    panel = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(panel)
    pd.rounded_rectangle([pad, pad, pad + w, pad + h], radius=radius, fill=fill_rgba)
    canvas.alpha_composite(panel)
    return canvas, pad


def _unsafe_zone_mask() -> Image.Image:
    mask = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(mask)
    d.rectangle([W - _YT_SAFE_RIGHT, 0, W, H], fill=255)
    d.rectangle([0, H - _YT_SAFE_BOTTOM, W, H], fill=255)
    return mask


_UNSAFE_MASK = _unsafe_zone_mask()


def _safe_area_violation(frame: Image.Image, bg: Image.Image,
                          threshold: int = 16) -> tuple[bool, tuple[int, int, int, int] | None]:
    """렌더된 프레임과 배경만 있는 클린 프레임을 픽셀 단위로 비교해서, 의미 있게
    달라진(=실제로 뭔가 그려진) 픽셀이 안전영역 밖(오른쪽 150px대, 하단 320px대)에
    있는지 확인한다. WHY bbox 계산 대신 픽셀 diff: 텍스트 bbox만 검사하면 패널의
    드롭섀도 블러 번짐처럼 "그려진 요소의 실제 텍스트 상자 밖으로 새는 시각적
    잔여물"을 못 잡는다 — 실제로 이 템플릿을 처음 만들 때 패널 그림자 블러가
    안전영역 경계를 넘어간 버그가 이 방식으로만 잡혔다."""
    diff = ImageChops.difference(frame.convert("RGB"), bg.convert("RGB")).convert("L")
    mask = diff.point(lambda p: 255 if p > threshold else 0)
    combined = ImageChops.multiply(mask, _UNSAFE_MASK)
    bbox = combined.getbbox()
    return bbox is not None, bbox


def _load_items(spec_path: str) -> list[dict]:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    items = spec.get("items", [])
    if not items:
        raise ValueError(f"card_news_spec.json에 items가 없습니다: {spec_path}")
    out = []
    for it in items:
        body_lines = [ln for ln in it.get("body", []) if ln.strip()]
        out.append({"name": it["name"], "fact_text": " ".join(body_lines)})
    return out


def _ffprobe_duration(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def _parse_srt(srt_path: str) -> list[tuple[float, float, str]]:
    """SRT 구간 목록. WHY 필요: 첫 구간(entries[0])의 길이가 실제 나레이션에서
    훅 문장("아침엔 얼굴이 퉁퉁 붓고...")을 읽는 데 걸리는 시간과 정확히
    일치한다 — 이 값을 훅 화면 노출 시간으로 그대로 쓰면 오디오와 화면이
    어긋나지 않는다(proto_before_after_transition.py와 동일한 패턴)."""
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


def _render_item_frame(bg: Image.Image, item: dict, rank: int, n_items: int, lang: str,
                        badge_color: tuple[int, int, int], shape_name: str,
                        shrink_step: int = 0, y_jitter: int = 0) -> Image.Image:
    """카운트다운 한 아이템(랭크 뱃지 + 아이템 이름 + 팩트 텍스트 패널 + 하단 진행
    도트)을 그린 프레임 하나. shrink_step은 안전영역 위반 시 재시도마다 콘텐츠를
    한 단계씩 줄이기 위한 값(0=원래 크기)."""
    frame = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(frame)
    fpath, findex = _title_font_for_lang(lang)
    shrink = max(0.62, 1.0 - shrink_step * 0.09)
    y_jitter = round(y_jitter * shrink)
    # WHY max_text_w도 shrink 적용: 패널 드롭섀도 블러 번짐 등으로 실제 픽셀이
    # 경계를 넘는 게 감지되면(아래 _render_item_safe) 이 폭 자체를 줄여
    # 재시도해야 패널 오른쪽 가장자리가 실질적으로 경계에서 멀어진다 — 폰트
    # 크기만 줄이고 폭은 그대로면 재시도가 무의미해진다. 기준 폭은
    # VISUAL_CENTER_MAX_WIDTH(540 중앙정렬 기준 좌우 대칭 최대폭) — 안전영역
    # 전체 폭(858px)을 그대로 쓰면 CONTENT_CENTER_X=540 기준으로 텍스트가
    # 오른쪽 경계에 치우쳐 배치돼 화면상 왼쪽 쏠림으로 보인다(2026-08-05 수정).
    max_text_w = round(VISUAL_CENTER_MAX_WIDTH * shrink)

    # 1) 랭크 뱃지
    badge_d = round(320 * shrink)
    ring = (255, 255, 255, 220)
    badge_img = _BADGE_SHAPE_FNS[shape_name](badge_d, (*badge_color, 255), ring)
    badge_x = CONTENT_CENTER_X - badge_d // 2
    badge_y = round(140 * shrink) + y_jitter
    frame.alpha_composite(badge_img, (badge_x, badge_y))

    num_text = str(rank)
    num_font_size = round((150 if len(num_text) == 1 else 112) * shrink)
    num_font = ImageFont.truetype(fpath, num_font_size, index=findex)
    nb = draw.textbbox((0, 0), num_text, font=num_font)
    nw, nh = nb[2] - nb[0], nb[3] - nb[1]
    nx = badge_x + badge_d // 2 - nw // 2 - nb[0]
    ny = badge_y + badge_d // 2 - nh // 2 - nb[1]
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        draw.text((nx + dx, ny + dy), num_text, font=num_font, fill=(0, 0, 0, 150))
    draw.text((nx, ny), num_text, font=num_font, fill=(255, 255, 255, 255))

    # 2) 아이템 이름
    name_font = ImageFont.truetype(fpath, round(70 * shrink), index=findex)
    name_lines = _wrap_text_for_lang(draw, item["name"], name_font, max_text_w, lang)
    y = badge_y + badge_d + round(36 * shrink)
    for line in name_lines:
        lb = draw.textbbox((0, 0), line, font=name_font)
        lx = CONTENT_CENTER_X - (lb[2] - lb[0]) // 2 - lb[0]
        draw.text((lx, y), line, font=name_font, fill=(255, 255, 255, 255))
        y += round((lb[3] - lb[1]) * 1.4)

    # 3) 팩트 텍스트 패널
    fact_font = ImageFont.truetype(fpath, round(44 * shrink), index=findex)
    panel_text_w = max_text_w - 90
    fact_lines = _wrap_text_for_lang(draw, item["fact_text"], fact_font, panel_text_w, lang)[:5]
    line_h = round(round(44 * shrink) * 1.55)
    panel_w = max_text_w
    panel_h = 56 + line_h * len(fact_lines)
    panel_img, ppad = _rounded_panel(panel_w, panel_h, 30, (18, 18, 32, 195))
    panel_y = y + round(26 * shrink)
    frame.alpha_composite(panel_img, (CONTENT_LEFT - ppad, panel_y - ppad))
    ty = panel_y + 28
    for line in fact_lines:
        lb = draw.textbbox((0, 0), line, font=fact_font)
        lx = CONTENT_CENTER_X - (lb[2] - lb[0]) // 2 - lb[0]
        draw.text((lx, ty), line, font=fact_font, fill=(235, 235, 245, 255))
        ty += line_h

    # 4) 하단 진행 도트 — 왼쪽이 #N(첫 공개), 오른쪽이 #1(마지막 공개) 순서.
    dot_r, gap = 9, 26
    start_x = CONTENT_CENTER_X - (n_items - 1) * gap // 2
    dot_y = SAFE_BOTTOM_Y - 18
    for i in range(n_items):
        dot_rank = n_items - i
        revealed = dot_rank >= rank
        active = dot_rank == rank
        cx = start_x + i * gap
        if active:
            color, r = (*badge_color, 255), dot_r + 4
        elif revealed:
            color, r = (255, 255, 255, 190), dot_r
        else:
            color, r = (255, 255, 255, 70), dot_r
        draw.ellipse([cx - r, dot_y - r, cx + r, dot_y + r], fill=color)

    return frame


def _render_item_safe(bg: Image.Image, item: dict, rank: int, n_items: int, lang: str,
                       badge_color: tuple[int, int, int], shape_name: str,
                       max_attempts: int = 6, y_jitter: int = 0) -> Image.Image:
    """안전영역 픽셀 diff 검사를 통과할 때까지 콘텐츠를 줄여가며 재시도. WHY
    silently 넘기지 않는지: 요구사항 그대로 — 위반이 감지되면 여백을 넓히거나
    콘텐츠를 줄여 다시 그리고, 그래도 끝내 못 맞추면 예외를 던져서 문제를
    숨기지 않는다."""
    for attempt in range(max_attempts):
        frame = _render_item_frame(bg, item, rank, n_items, lang, badge_color, shape_name,
                                    shrink_step=attempt, y_jitter=y_jitter)
        violated, bbox = _safe_area_violation(frame, bg)
        if not violated:
            return frame
        print(f"[safe-area] rank #{rank} '{item['name']}' attempt {attempt}: "
              f"violation bbox={bbox} — shrinking content and re-rendering", file=sys.stderr)
    raise RuntimeError(
        f"rank #{rank} '{item['name']}'가 {max_attempts}번 재시도 후에도 "
        f"안전영역(우측 {_YT_SAFE_RIGHT}px, 하단 {_YT_SAFE_BOTTOM}px)을 벗어납니다."
    )


def _render_hook_frame(bg: Image.Image, spec: dict, n_items: int, lang: str,
                        ramp: list[tuple[int, int, int]], shape_name: str,
                        shrink_step: int = 0, y_jitter: int = 0) -> Image.Image:
    """카운트다운 시작 전 오프닝(훅) 화면. WHY 별도 화면인지: 이 화면이 유튜브
    쇼츠 피드의 사실상 썸네일(프레임 0)인데, 아이템 #N 화면을 그대로 프레임 0에
    쓰면 "왜 부종이 생길까요" 같은 개별 아이템 문구만 보여 후킹이 약했다(2026-08-05,
    사용자 지적: "썸네일이 제대로 안잡혀있다"). 또한 SRT 첫 구간이 실제로 이 훅
    문장을 읽는 나레이션이라(render()의 hook_duration 참고) 아이템 화면을 t=0에
    바로 놓으면 나레이션과도 어긋난다.
    구성: eyebrow 배지 → headline(spec title) → 미니 순위 미리보기(N→1, 왼쪽이
    먼저 공개되는 #N, 오른쪽이 마지막에 공개되는 #1 — 하단 진행 도트와 같은 방향) →
    red-escalation 그라디언트 바 → 가장 나쁜 항목(#1) 예고 배지(어떤 항목인지는
    밝히지 않고 숫자만 - 스포일러 방지)."""
    frame = bg.copy().convert("RGBA")
    draw = ImageDraw.Draw(frame)
    fpath, findex = _title_font_for_lang(lang)
    shrink = max(0.62, 1.0 - shrink_step * 0.09)
    max_w = round(VISUAL_CENTER_MAX_WIDTH * shrink)

    eyebrow_text = spec.get("eyebrow") or ""
    title_lines_raw = spec.get("title") or []

    y = round(70 * shrink) + round(y_jitter * shrink)

    # 1) eyebrow 배지
    if eyebrow_text:
        eb_font = ImageFont.truetype(fpath, round(34 * shrink), index=findex)
        ebbox = draw.textbbox((0, 0), eyebrow_text, font=eb_font)
        etw, eth = ebbox[2] - ebbox[0], ebbox[3] - ebbox[1]
        pad_x, pad_y = round(30 * shrink), round(14 * shrink)
        pill_w, pill_h = etw + pad_x * 2, eth + pad_y * 2
        px0 = CONTENT_CENTER_X - pill_w // 2
        draw.rounded_rectangle(
            [px0, y, px0 + pill_w, y + pill_h], radius=pill_h // 2,
            fill=(255, 255, 255, 235),
        )
        draw.text((px0 + pad_x - ebbox[0], y + pad_y - ebbox[1]), eyebrow_text,
                   font=eb_font, fill=(*ramp[-1], 255))
        y += pill_h + round(34 * shrink)

    # 2) headline(spec title)
    title_font = ImageFont.truetype(fpath, round(64 * shrink), index=findex)
    title_lines: list[str] = []
    for raw_line in title_lines_raw:
        title_lines += _wrap_text_for_lang(draw, raw_line, title_font, max_w, lang)
    line_h = round(round(64 * shrink) * 1.32)
    for line in title_lines:
        lb = draw.textbbox((0, 0), line, font=title_font)
        lx = CONTENT_CENTER_X - (lb[2] - lb[0]) // 2 - lb[0]
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            draw.text((lx + dx, y + dy), line, font=title_font, fill=(0, 0, 0, 130))
        draw.text((lx, y), line, font=title_font, fill=(255, 255, 255, 255))
        y += line_h
    y += round(30 * shrink)

    # 3) 미니 순위 미리보기 — N개 항목을 카운트다운으로 보여줄 거라는 예고.
    # 하단 진행 도트(_render_item_frame)와 같은 방향(왼쪽=#N 먼저 공개,
    # 오른쪽=#1 마지막 공개)으로 맞춰 두 화면이 같은 시각 문법을 쓰게 한다.
    dot_d = max(28, min(56, round((max_w - (n_items - 1) * 14) / max(n_items, 1))))
    dot_d = round(dot_d * shrink)
    gap = round(dot_d * 0.32)
    strip_w = n_items * dot_d + (n_items - 1) * gap
    start_x = CONTENT_CENTER_X - strip_w // 2
    num_font = ImageFont.truetype(fpath, round(dot_d * 0.42), index=findex)
    for i in range(n_items):
        rank = n_items - i
        t = (n_items - rank) / max(n_items - 1, 1)
        color = _ramp_color(ramp, t)
        cx = start_x + i * (dot_d + gap) + dot_d // 2
        cy = y + dot_d // 2
        draw.ellipse([cx - dot_d // 2, cy - dot_d // 2, cx + dot_d // 2, cy + dot_d // 2],
                     fill=(*color, 235), outline=(255, 255, 255, 200), width=2)
        num_text = str(rank)
        nb = draw.textbbox((0, 0), num_text, font=num_font)
        draw.text((cx - (nb[2] - nb[0]) // 2 - nb[0], cy - (nb[3] - nb[1]) // 2 - nb[1]),
                   num_text, font=num_font, fill=(255, 255, 255, 255))
    y += dot_d + round(40 * shrink)

    # 4) red-escalation 그라디언트 바 — 왼쪽(첫 공개, 순함)에서 오른쪽(#1, 최악)
    # 으로 갈수록 위험색이 짙어지는 배지 램프를 그대로 가로 바에 매핑.
    bar_h = round(16 * shrink)
    bar_w = max_w
    grad_row = Image.new("RGB", (bar_w, 1))
    for x in range(bar_w):
        grad_row.putpixel((x, 0), _ramp_color(ramp, x / max(bar_w - 1, 1)))
    grad = grad_row.resize((bar_w, bar_h), Image.BILINEAR).convert("RGBA")
    bar_mask = Image.new("L", (bar_w, bar_h), 0)
    ImageDraw.Draw(bar_mask).rounded_rectangle(
        [0, 0, bar_w - 1, bar_h - 1], radius=bar_h // 2, fill=255)
    bar_x0 = CONTENT_CENTER_X - bar_w // 2
    frame.paste(grad, (bar_x0, y), bar_mask)
    y += bar_h + round(52 * shrink)

    # 5) 가장 나쁜(#1) 항목 예고 배지 — 어떤 항목인지는 밝히지 않고 "1"이라는
    # 숫자로만 긴장감을 준다(스포일러 없이 후킹).
    badge_d = round(420 * shrink)
    badge_img = _BADGE_SHAPE_FNS[shape_name](badge_d, (*ramp[-1], 255), (255, 255, 255, 225))
    badge_x = CONTENT_CENTER_X - badge_d // 2
    frame.alpha_composite(badge_img, (badge_x, y))
    num_text = "1"
    num_font2 = ImageFont.truetype(fpath, round(190 * shrink), index=findex)
    nb = draw.textbbox((0, 0), num_text, font=num_font2)
    nx = badge_x + badge_d // 2 - (nb[2] - nb[0]) // 2 - nb[0]
    ny = y + badge_d // 2 - (nb[3] - nb[1]) // 2 - nb[1]
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
        draw.text((nx + dx, ny + dy), num_text, font=num_font2, fill=(0, 0, 0, 160))
    draw.text((nx, ny), num_text, font=num_font2, fill=(255, 255, 255, 255))

    return frame


def _render_hook_safe(bg: Image.Image, spec: dict, n_items: int, lang: str,
                       ramp: list[tuple[int, int, int]], shape_name: str,
                       max_attempts: int = 6, y_jitter: int = 0) -> Image.Image:
    """훅 화면 버전의 _render_item_safe — 안전영역 위반 시 shrink_step을 올려가며
    재시도, 끝내 못 맞추면 예외로 알린다(요구사항 그대로, 조용히 넘기지 않음)."""
    for attempt in range(max_attempts):
        frame = _render_hook_frame(bg, spec, n_items, lang, ramp, shape_name,
                                    shrink_step=attempt, y_jitter=y_jitter)
        violated, bbox = _safe_area_violation(frame, bg)
        if not violated:
            return frame
        print(f"[safe-area] hook screen attempt {attempt}: violation bbox={bbox} — "
              f"shrinking content and re-rendering", file=sys.stderr)
    raise RuntimeError(f"훅 화면이 {max_attempts}번 재시도 후에도 안전영역을 벗어납니다.")


def render(topic_dir: str, lang: str, audio_path: str, srt_path: str, spec_path: str,
           out_path: str) -> None:
    """랭킹 카운트다운 Shorts 렌더링 진입점. topic_dir(예: "output/부종_1")의
    폴더명을 topic-seeded variety(뱃지 색 램프/배경 색조/뱃지 모양)의 seed
    문자열로 쓴다 — 이 프로젝트의 다른 topic-seed 로직(doodle_seed 등)과 같은
    convention: 언어 접미사 없는 topic 폴더명 하나로 언어 버전 간에도 같은
    variety가 재현되게 한다."""
    items = _load_items(spec_path)
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    n = len(items)
    seed_title = Path(topic_dir).name

    ramp = _BADGE_RAMPS[_seed_axis(seed_title, k=5, c0=2, n_options=len(_BADGE_RAMPS))]
    base_hue = 215 + _seed_axis(seed_title, k=3, c0=11, n_options=86)  # navy(215)~purple(300)
    shape_name = ("circle", "shield")[_seed_axis(seed_title, k=7, c0=13, n_options=2)]
    y_jitter = _seed_axis(seed_title, k=19, c0=6, n_options=41) - 20

    total_duration = _ffprobe_duration(audio_path)
    # srt_path는 총 길이 상호검증용이 아니라 훅 화면 노출 시간을 정하는 데 직접
    # 쓴다 — 실제 나레이션 첫 구간(entries[0])이 정확히 훅 문장이라(2026-08-05
    # 확인), 그 구간 길이를 훅 화면에 그대로 배정해야 나레이션과 화면이 맞는다.
    # 그 뒤 아이템별 배분은 여전히 오디오 실측 총 길이 기준으로 계산해 SRT
    # 타임스탬프 누적 오차(멀티보이스 TTS 무음 간격 등)가 전체 길이에 번지지
    # 않게 한다(video_assembler.py의 기존 관행과 동일).
    entries = _parse_srt(srt_path) if Path(srt_path).exists() else []
    if not entries:
        print(f"[warn] srt_path가 비어 있습니다: {srt_path}", file=sys.stderr)
    hook_duration = entries[0][1] if entries else max(total_duration * 0.1, 2.5)
    remaining = max(total_duration - hook_duration, 1.0)

    bg = _make_background(base_hue)

    # 아이템별 화면 노출 시간 — 각 아이템 팩트 텍스트 길이에 비례 배분(내레이션이
    # 대략 텍스트량에 비례해 길어지는 경향을 근사). 최소 노출시간을 둬서 아주
    # 짧은 아이템도 순간적으로 스쳐 지나가지 않게 한다. 훅 화면 시간(hook_duration)은
    # 이 배분에서 빼고 남은 remaining만 아이템들이 나눠 쓴다.
    min_dur = 3.0
    weights = [max(len(it["fact_text"]), 12) for it in items]
    total_weight = sum(weights)
    raw_durs = [max(min_dur, remaining * w / total_weight) for w in weights]
    scale = remaining / sum(raw_durs)
    durs = [d * scale for d in raw_durs]

    total_frames = round(total_duration * FPS)
    hook_frames = round(hook_duration * FPS)
    frames_per_item = [max(round(min_dur * FPS), round(d * FPS)) for d in durs]
    frames_per_item[-1] += (total_frames - hook_frames) - sum(frames_per_item)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        seg_paths = []

        hook_frame = _render_hook_safe(bg, spec, n, lang, ramp, shape_name, y_jitter=y_jitter)
        hook_png = tmp_path / "hook.png"
        hook_frame.convert("RGB").save(hook_png, quality=95)
        hook_seg = tmp_path / "seg_hook.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(hook_png),
             "-frames:v", str(hook_frames), "-r", str(FPS),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(hook_seg)],
            check=True, capture_output=True,
        )
        seg_paths.append(hook_seg)

        for idx, item in enumerate(items):
            rank = n - idx  # 내레이션 순서 그대로: 첫 아이템=#N(가장 순함) ... 마지막=#1(최악)
            severity_t = (n - rank) / max(n - 1, 1)  # 0.0(#N, 순함) ~ 1.0(#1, 최악)
            badge_color = _ramp_color(ramp, severity_t)
            frame = _render_item_safe(bg, item, rank, n, lang, badge_color, shape_name, y_jitter=y_jitter)
            item_png = tmp_path / f"item_{idx:02d}.png"
            frame.convert("RGB").save(item_png, quality=95)

            seg_path = tmp_path / f"seg_{idx:02d}.mp4"
            n_frames = frames_per_item[idx]
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", str(item_png),
                 "-frames:v", str(n_frames), "-r", str(FPS),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg_path)],
                check=True, capture_output=True,
            )
            seg_paths.append(seg_path)

        list_path = tmp_path / "concat_list.txt"
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths), encoding="utf-8")
        video_only = tmp_path / "video_only.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(video_only)],
            check=True, capture_output=True,
        )

        mixed_audio = mix_bgm(audio_path, str(tmp_path / "mixed_audio.m4a"), total_duration, seed_title)

        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_only), "-i", mixed_audio,
             "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             "-shortest", str(out_path)],
            check=True, capture_output=True,
        )
    print(f"랭킹 카운트다운 영상 조립 완료: {out_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="랭킹 카운트다운 Shorts 템플릿 단독 테스트용 CLI")
    parser.add_argument("--topic-dir", default="output/부종_1")
    parser.add_argument("--lang", default="kor")
    parser.add_argument("--audio", default="output/부종_1/ko/부종_1_narration.mp3")
    parser.add_argument("--srt", default="output/부종_1/ko/부종_1_narration.srt")
    parser.add_argument("--spec", default="data/부종_1/ko/card_news_spec.json")
    parser.add_argument("--out", default="output/_template_lab_ko/ranking_countdown/shorts.mp4")
    args = parser.parse_args()

    render(
        topic_dir=args.topic_dir,
        lang=args.lang,
        audio_path=args.audio,
        srt_path=args.srt,
        spec_path=args.spec,
        out_path=args.out,
    )
