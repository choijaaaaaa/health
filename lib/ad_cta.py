# 광고 배너 클릭 유도 CTA 오버레이. WHY(2026-09-14 사용자 요청): 네이버 클립 등
# 플랫폼이 영상 하단에 붙이는 제휴 광고 배너("AD 리스테린 쿨민트 가글 …")를
# 시청자가 그냥 지나친다 — 배너 바로 위에 "제품 보러 가기"와 아래 화살표를 얹어
# 시선을 배너로 내린다. 정지해 있으면 배경 칠판에 묻히므로 재생 내내 위아래로
# 까딱이며 살짝 회전시킨다.
#
# 왜 조립 파이프라인 안이 아니라 별도 모듈인지: 이미 완성된 영상 108편에도
# 소급 적용해야 해서, 완성본 mp4에 덧입히는 경로와 새로 조립하는 경로가 같은
# 코드를 써야 한다.
from __future__ import annotations

import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
_FONTS = Path(__file__).resolve().parent.parent / "assets_library" / "fonts"

# WHY 이 자리인지(실측 2026-09-14): 칠판 나무 선반이 y≈1660~1760, 그 아래 검은
# 여백(1760~1920)에 플랫폼 광고 배너가 얹힌다. 그래서 CTA는 선반 위 빈 칠판에
# 두고 화살표로 아래를 가리킨다. 좌측 x<260은 "급식 당번" 명패, 우측 x>760은
# 원형 사진이 이미 쓰고 있어 그 사이만 비어 있다.
CTA_CX = 510          # 명패와 원형 사진 사이의 빈 구간 중앙
CTA_CY = 1545         # 나무 선반 위. 유튜브 하단 안전선(1600)보다도 위다

# WHY 칠판 상단 기준 오프셋이 따로 필요한지(2026-09-17): 위 CTA_CY는 상단 배너가
# 있던 시절(칠판이 y≈255부터 시작)에 실측한 절대 좌표다. 배너를 끄면 칠판이 그만큼
# 위로 올라가서 같은 좌표가 나무 선반 한가운데를 뚫고 앉고, 화살표가 광고 배너가
# 아니라 사진 배경을 가리킨다(실측 확인). 선반은 칠판 이미지의 고정 위치이므로
# 절대 y가 아니라 **칠판 상단으로부터의 거리**로 잡아야 레이아웃이 바뀌어도 맞는다.
CTA_CY_FROM_BOARD_TOP = 1290   # = 기존 1545 - 그때의 칠판 상단(255)
BOB_PX = 13           # 위아래 진폭(px)
BOB_PERIOD = 1.6      # 한 번 까딱이는 주기(초)
TILT_DEG = 5.0        # 좌우 기울기 진폭(도)
TILT_PERIOD = 2.3     # 기울기 주기(초) — 진폭 주기와 어긋나게 둬야 기계적으로 안 보인다

# WHY 도입부엔 CTA를 띄우지 않는지(2026-09-17 사용자 지적): t=0부터 깔면 맨 앞
# 제목 카드(=썸네일) 글자를 배지가 정통으로 덮는다. 네이버 클립은 업로더가
# 영상 프레임 중에서 썸네일을 고르는 방식이라, 전 구간에 CTA가 깔려 있으면
# 깨끗한 썸네일 후보 프레임 자체가 하나도 없다 — 광고 유도가 박힌 썸네일은
# 클릭률을 떨어뜨리므로 배너로 시선을 내리려다 유입을 깎아먹는 역효과다.
# 5초인 이유: 초반 0~5초가 이탈을 가르는 훅 구간이라 같은 이유로 비워둬야
# 한다. 5초 안에 이탈할 시청자는 어차피 배너를 안 누르므로 잃는 것도 없다.
# 공정위 "처음부터 끝까지 노출" 대상은 이 CTA가 아니라 광고 표시 배지
# (video_assembler._build_ad_tag_badge)다 — 그쪽은 계속 전 구간 유지.
CTA_START_SEC = 5.0

# 분필 톤 안에서 가장 눈에 띄는 색. 순백은 본문 판서와 같아 묻힌다.
CHALK_YELLOW = (255, 214, 92)
CHALK_WHITE = (245, 245, 240)

_LABEL_BY_LANG = {
    "kor": "제품 보러 가기",
    "en": "See the product",
    "ja": "商品を見る",
    "de": "Produkt ansehen",
    "fr": "Voir le produit",
    "it": "Vedi il prodotto",
    "es": "Ver el producto",
    "nl": "Bekijk product",
    "sv": "Se produkten",
}
_FONT_BY_LANG = {
    "kor": "Gaegu-Bold.ttf",
    "ja": "NotoSansJP-Bold.ttf",
}


def _font(lang: str, size: int) -> ImageFont.FreeTypeFont:
    name = _FONT_BY_LANG.get(lang, "NotoSans-Bold.ttf")
    return ImageFont.truetype(str(_FONTS / name), size)


def build_cta_png(out_path: Path, lang: str = "kor") -> tuple[int, int]:
    """CTA 배지 하나를 투명 PNG로 그린다. 반환값은 (너비, 높이).

    회전시킬 것이므로 캔버스에 여백을 넉넉히 둔다 — 여백이 없으면 기울일 때
    모서리가 잘린다.
    """
    label = _LABEL_BY_LANG.get(lang, _LABEL_BY_LANG["en"])
    size = 54 if lang in ("kor", "ja") else 44
    font = _font(lang, size)

    pad_x, pad_y = 34, 20
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    tb = probe.textbbox((0, 0), label, font=font)
    tw, th = tb[2] - tb[0], tb[3] - tb[1]

    box_w = tw + pad_x * 2
    box_h = th + pad_y * 2
    arrow_h = 78
    gap = 10
    margin = 30                     # 회전 여유
    cw = box_w + margin * 2
    ch = box_h + gap + arrow_h + margin * 2

    img = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bx0, by0 = margin, margin
    bx1, by1 = bx0 + box_w, by0 + box_h

    # 분필로 대충 그린 듯한 테두리 박스 — 칠판 톤을 유지하면서 배경과 분리한다.
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, fill=(28, 32, 30, 205))
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=16, outline=CHALK_YELLOW, width=4)
    d.text((bx0 + pad_x - tb[0], by0 + pad_y - tb[1]), label, font=font, fill=CHALK_YELLOW)

    # 아래 화살표: 배너를 가리키는 방향 지시. 선 + 삼각 머리.
    ax = (bx0 + bx1) / 2
    ay0 = by1 + gap
    ay1 = ay0 + arrow_h
    d.line([(ax, ay0), (ax, ay1 - 26)], fill=CHALK_WHITE, width=8)
    d.polygon([(ax - 24, ay1 - 30), (ax + 24, ay1 - 30), (ax, ay1)], fill=CHALK_WHITE)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return cw, ch


def cta_filter(overlay_label: str, base_label: str, cw: int, ch: int,
               out_label: str = "v", start_at: float = CTA_START_SEC,
               center_y: float | None = None, center_x: float | None = None) -> str:
    """CTA를 까딱이며 얹는 filter_complex 조각.

    rotate는 오버레이 입력에만 걸어야 한다 — 베이스 영상에 걸면 화면 전체가 돈다.
    `c=none`으로 회전 여백을 투명하게 두고, ow/oh를 키워 모서리 잘림을 막는다.

    WHY 등장 지연을 fade가 아니라 overlay의 `enable`로 거는지: 오버레이 입력은
    PNG 한 장짜리라 자체 타임스탬프가 0에 멈춰 있다 — 그 스트림에 fade를 걸면
    st에 영영 도달하지 못해 CTA가 끝까지 안 나온다. 반면 overlay의 `enable`/`t`는
    베이스 영상 타임라인으로 평가되므로 의도대로 동작한다(y의 까딱임도 같은
    이유로 이미 overlay 쪽 `t`를 쓰고 있다).
    """
    rot = (f"[{overlay_label}]format=rgba,"
           f"rotate=a='{math.radians(TILT_DEG):.5f}*sin(2*PI*t/{TILT_PERIOD})':"
           f"c=none:ow=rotw(iw):oh=roth(ih)[cta]")
    cx = CTA_CX if center_x is None else center_x
    x = f"{cx}-overlay_w/2"
    cy = CTA_CY if center_y is None else center_y
    y = f"{cy}-overlay_h/2+{BOB_PX}*sin(2*PI*t/{BOB_PERIOD})"
    ov = (f"[{base_label}][cta]overlay=x='{x}':y='{y}':format=auto"
          f":enable='gte(t,{start_at})'[{out_label}]")
    return f"{rot};{ov}"


def apply_to_video(src: str | Path, dst: str | Path, lang: str = "kor",
                   start_at: float = CTA_START_SEC) -> None:
    """완성된 mp4에 CTA를 덧입힌다(오디오는 그대로 복사).

    기존 영상 소급 적용과 신규 조립 양쪽에서 같은 결과가 나오도록 이 함수 하나만 쓴다.
    """
    src, dst = Path(src), Path(dst)
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "cta.png"
        cw, ch = build_cta_png(png, lang)
        fc = cta_filter("1:v", "0:v", cw, ch, "v", start_at=start_at)
        dst.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-i", str(png),
             "-filter_complex", fc,
             "-map", "[v]", "-map", "0:a?",
             "-c:v", "libx264", "-preset", "medium", "-crf", "20",
             "-pix_fmt", "yuv420p", "-c:a", "copy",
             str(dst)],
            check=True, capture_output=True,
        )


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("usage: python3 lib/ad_cta.py <입력.mp4> <출력.mp4> [lang]")
        sys.exit(1)
    apply_to_video(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "kor")
    print(f"CTA 적용 완료: {sys.argv[2]}")
