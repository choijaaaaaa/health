# 증상 부위·상황을 칠판 분필 톤으로 그리는 글리프. 실사 클립 위에 얹어서
# "어디가/무엇이 문제인지"를 표시한다.
#
# WHY(2026-09-18): 실사 스톡은 "불편해하는 사람"은 넘치는데 "새벽에 종아리에 쥐가
# 난 순간" 같은 특정 장면은 없다(실측 적중률 6개 중 1개). 그래서 특정성을 영상이
# 아니라 오버레이가 맡는다 — 범용 클립을 재사용하고, topic마다 달라지는 건 이 글리프다.
# 덕분에 클립 풀이 100~150개에서 30~40개로 줄고, 부위 표현은 소싱 없이 항상 정확하다.
#
# WHY 부위 도해만으로 안 되는지: 수면·냄새·피로처럼 짚을 몸 부위가 없는 topic이
# 385편 중 101편이다. 그런 건 인체에 억지로 점을 찍는 대신 상황 픽토그램
# (누운 사람, 냄새 물결 등)으로 대체한다.
#
# 선 규약은 video_assembler._stroke_shape과 같다 — 그림자를 (3,3) 검정 110으로
# 먼저 깔고 그 위에 흰 선을 얹어야 칠판 위에서 떠 보인다.
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W = H = 620
CHALK = (255, 255, 255, 255)
ACCENT = (255, 214, 92, 255)          # ad_cta.CHALK_YELLOW와 같은 톤
_FONT = Path(__file__).resolve().parent.parent / "assets_library" / "fonts" / "Gaegu-Bold.ttf"


def _canvas() -> Image.Image:
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def _stroke(draw_fn) -> Image.Image:
    shadow = _canvas()
    draw_fn(ImageDraw.Draw(shadow), (4, 4), (0, 0, 0, 110))
    img = _canvas()
    draw_fn(ImageDraw.Draw(img), (0, 0), CHALK)
    return Image.alpha_composite(shadow, img)


# ─────────────────────────── 얼굴 도해 ───────────────────────────
# WHY 얼굴을 전신에서 분리했는지(2026-09-18 실측): 전신 도해에서 머리는 620px
# 캔버스 중 100px뿐이라 눈·코·입·귀 강조 원이 전부 같은 자리로 뭉쳐 구분이 안 됐다.
# 얼굴 부위는 얼굴만 크게 그린 별도 도해를 쓴다.
def _face(d, off, color, width=7):
    ox, oy = off
    cx, cy = 310 + ox, 300 + oy
    d.ellipse([cx - 150, cy - 190, cx + 150, cy + 190], outline=color, width=width)  # 머리
    d.arc([cx - 196, cy - 56, cx - 128, cy + 56], 90, 270, fill=color, width=width)  # 좌귀
    d.arc([cx + 128, cy - 56, cx + 196, cy + 56], 270, 90, fill=color, width=width)  # 우귀
    for ex in (cx - 62, cx + 62):                                                    # 눈
        d.arc([ex - 34, cy - 92, ex + 34, cy - 28], 0, 360, fill=color, width=width - 2)
    d.line([(cx, cy - 30), (cx, cy + 34)], fill=color, width=width - 2)              # 코
    d.arc([cx - 18, cy + 18, cx + 20, cy + 46], 20, 160, fill=color, width=width - 2)
    d.arc([cx - 62, cy + 62, cx + 62, cy + 134], 20, 160, fill=color, width=width)   # 입

FACE_REGIONS: dict[str, tuple[int, int, int]] = {   # (x, y, 강조 반지름)
    "눈":   (248, 240, 52),
    "코":   (310, 302, 46),
    "입":   (310, 398, 62),
    "귀":   (148, 300, 52),
    "머리": (310, 152, 66),
}

# ─────────────────────────── 인체 도해 ───────────────────────────
def _body(d, off, color, width=7):
    """정면 전신. 직사각형 몸통은 막대인간처럼 보여서, 어깨~허리~골반을 좁혔다
    넓히는 사다리꼴로 잡아 사람 실루엣이 읽히게 했다(2026-09-18 1차 렌더 반성)."""
    ox, oy = off
    cx = 310 + ox
    d.ellipse([cx - 46, 56 + oy, cx + 46, 148 + oy], outline=color, width=width)     # 머리
    d.line([(cx, 148 + oy), (cx, 182 + oy)], fill=color, width=width)                # 목
    torso = [(cx - 96, 196 + oy), (cx - 70, 338 + oy), (cx - 84, 396 + oy),
             (cx + 84, 396 + oy), (cx + 70, 338 + oy), (cx + 96, 196 + oy)]
    d.line(torso + [torso[0]], fill=color, width=width, joint="curve")               # 몸통
    d.line([(cx - 96, 200 + oy), (cx - 142, 300 + oy), (cx - 128, 392 + oy)],
           fill=color, width=width, joint="curve")                                   # 좌팔
    d.line([(cx + 96, 200 + oy), (cx + 142, 300 + oy), (cx + 128, 392 + oy)],
           fill=color, width=width, joint="curve")                                   # 우팔
    d.line([(cx - 50, 396 + oy), (cx - 62, 480 + oy), (cx - 56, 562 + oy)],
           fill=color, width=width, joint="curve")                                   # 좌다리
    d.line([(cx + 50, 396 + oy), (cx + 62, 480 + oy), (cx + 56, 562 + oy)],
           fill=color, width=width, joint="curve")                                   # 우다리

BODY_REGIONS: dict[str, tuple[int, int, int]] = {   # (x, y, 강조 반지름)
    "폐":     (310, 248, 62),
    "위/장":  (310, 316, 66),
    "방광":   (310, 372, 48),
    "여성":   (310, 372, 52),
    "허리":   (310, 350, 60),
    "관절":   (372, 480, 48),
    "손":     (438, 386, 46),
    "다리":   (248, 490, 52),
    "발":     (248, 556, 44),
    "피부":   (168, 300, 50),
}


def _halo(d, off, x, y, r, width=7):
    """분필로 동그라미 두 번 친 느낌 — 안쪽은 굵게, 바깥은 얇게."""
    ox, oy = off
    c = ACCENT if off == (0, 0) else (0, 0, 0, 110)
    for rr, w in ((r, width), (r + 18, max(width - 4, 2))):
        d.ellipse([x - rr + ox, y - rr + oy, x + rr + ox, y + rr + oy], outline=c, width=w)


def body_glyph(region: str, label: str | None = None) -> Image.Image:
    """얼굴 부위면 얼굴 도해, 그 외는 전신 도해에 강조를 얹는다."""
    if region in FACE_REGIONS:
        base, (x, y, r) = _face, FACE_REGIONS[region]
    elif region in BODY_REGIONS:
        base, (x, y, r) = _body, BODY_REGIONS[region]
    else:
        raise KeyError(f"모르는 부위: {region} (FACE_REGIONS/BODY_REGIONS에 추가할 것)")

    def draw(d, off, color):
        base(d, off, color)
        _halo(d, off, x, y, r)

    return _label(_stroke(draw), label or region)


REGIONS = {**FACE_REGIONS, **BODY_REGIONS}

# ─────────────────────────── 상황 픽토그램 ───────────────────────────
# 짚을 몸 부위가 없는 topic용(수면·냄새·피로 등). 인체에 억지로 점을 찍지 않는다.
def _scene_sleep(d, off, color):
    ox, oy = off
    d.arc([120 + ox, 300 + oy, 500 + ox, 420 + oy], 180, 360, fill=color, width=6)   # 이불 덮인 몸
    d.ellipse([150 + ox, 268 + oy, 226 + ox, 344 + oy], outline=color, width=6)      # 머리
    d.line([(96 + ox, 420 + oy), (524 + ox, 420 + oy)], fill=color, width=6)         # 침대
    d.line([(120 + ox, 420 + oy), (120 + ox, 466 + oy)], fill=color, width=5)
    d.line([(500 + ox, 420 + oy), (500 + ox, 466 + oy)], fill=color, width=5)
    for i, (zx, zy, s) in enumerate(((330, 232, 30), (386, 180, 40), (452, 120, 52))):
        c = ACCENT if off == (0, 0) else (0, 0, 0, 110)
        d.line([(zx + ox, zy + oy), (zx + s + ox, zy + oy),
                (zx + ox, zy + s + oy), (zx + s + ox, zy + s + oy)], fill=c, width=5)


def _scene_smell(d, off, color):
    ox, oy = off
    d.arc([200 + ox, 372 + oy, 420 + ox, 492 + oy], 180, 360, fill=color, width=6)   # 용기
    d.line([(200 + ox, 432 + oy), (420 + ox, 432 + oy)], fill=color, width=6)
    c = ACCENT if off == (0, 0) else (0, 0, 0, 110)
    for k, sx in enumerate((246, 310, 374)):                                          # 냄새 물결
        pts = []
        for t in range(0, 41):
            yy = 352 - t * 6
            pts.append((sx + 22 * math.sin(t / 3.2 + k) + ox, yy + oy))
        d.line(pts, fill=c, width=5, joint="curve")


def _scene_fatigue(d, off, color):
    ox, oy = off
    d.rounded_rectangle([160 + ox, 250 + oy, 450 + ox, 386 + oy], radius=18,
                        outline=color, width=6)                                       # 배터리
    d.rounded_rectangle([450 + ox, 292 + oy, 478 + ox, 344 + oy], radius=8,
                        outline=color, width=6)
    c = ACCENT if off == (0, 0) else (0, 0, 0, 110)
    d.rectangle([182 + ox, 272 + oy, 232 + ox, 364 + oy], outline=c, width=6)         # 잔량 한 칸
    d.line([(300 + ox, 430 + oy), (340 + ox, 430 + oy)], fill=color, width=5)


SCENES = {"수면": _scene_sleep, "냄새": _scene_smell, "피로": _scene_fatigue}


def scene_glyph(key: str, label: str | None = None) -> Image.Image:
    if key not in SCENES:
        raise KeyError(f"모르는 상황: {key} (SCENES에 추가할 것)")
    img = _stroke(SCENES[key])
    return _label(img, label or key)


def _label(img: Image.Image, text: str) -> Image.Image:
    """WHY 라벨을 위에 두는지: 아래에 두면 다리·발 강조 원과 글자가 겹쳤다.
    WHY 가운뎃점을 막는지: Gaegu-Bold에 U+00B7 글리프가 없어 두부로 깨진다
    (실측 확인 — '—'·'～'·'∙'도 마찬가지). 구분자는 '/'만 쓴다."""
    for bad in ("·", "∙", "—", "～"):
        text = text.replace(bad, "/")
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(str(_FONT), 60)
    tb = d.textbbox((0, 0), text, font=f)
    x = (W - (tb[2] - tb[0])) / 2 - tb[0]
    d.text((x + 3, 3), text, font=f, fill=(0, 0, 0, 120))
    d.text((x, 0), text, font=f, fill=ACCENT)
    return img


def render(key: str, label: str | None = None) -> Image.Image:
    return body_glyph(key, label) if key in REGIONS else scene_glyph(key, label)
