#!/usr/bin/env python3
"""부위 점등 클립(4초)을 미드저니 스틸 한 장에서 코드로 만든다 — Flow 렌더를 대체한다.

WHY(2026-09-20 사용자 "최대한 효율적으로 덜 뽑아도 되게"): 부위 점등 클립은 "카메라가 천천히 밀고
들어가고 한 부위만 호박색으로 켜져 맥동한다"가 전부다. 행위 클립(몸이 움직임)·기전 클립(3컷 미시 장면)과
달리 Veo가 만들어야 할 변화가 없어서, 스틸 한 장에 줌과 점등을 입히면 같은 그림이 나온다. 부위 31종을
Flow로 뽑으면 31회 렌더가 필요하지만 이 스크립트를 쓰면 미드저니 스틸만 있으면 된다.

점등 영역: `--region`(스틸 안 비율 x,y,w,h 타원)을 주면 그 안만, 안 주면 배경을 뺀 피사체 전체.
전신/몸통 스틸은 region 필수(위·장처럼 한 부위만 켜져야 함), 장기 클로즈업 스틸은 생략 가능.

    python3 scripts/make_part_clip.py stills/cu_eye.jpg output/part_eye.mp4
    python3 scripts/make_part_clip.py stills/cu_torso_organs.jpg output/part_stomach.mp4 \
        --region 0.42,0.46,0.26,0.16 --label-debug
"""
from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 720, 1280, 30
DUR = 4.0
ZOOM_END = 1.16          # 파일럿 A의 push-in 폭에 맞춘 값(WS→MS 2단계)
GLOW_IN = (1.3, 2.7)     # 캐논 타임스탬프: 1.3s에 켜지기 시작, 2.7s에 만개
PULSE_PERIOD = 1.4
AMBER = (255, 176, 66)


def _subject_mask(img: Image.Image) -> Image.Image:
    """어두운 배경(slate blue-grey void)을 뺀 피사체 영역."""
    g = img.convert("L")
    return g.point(lambda v: 255 if v > 45 else 0).filter(ImageFilter.GaussianBlur(8))


def _region_mask(img: Image.Image, region: tuple[float, float, float, float]) -> Image.Image:
    x, y, w, h = region
    m = Image.new("L", img.size, 0)
    box = [x * img.width, y * img.height, (x + w) * img.width, (y + h) * img.height]
    ImageDraw.Draw(m).ellipse(box, fill=255)
    m = m.filter(ImageFilter.GaussianBlur(min(img.size) * 0.03))
    # 배경까지 물들면 빛이 공중에 뜬다 — 피사체 안쪽으로만 제한
    sub = _subject_mask(img)
    return Image.composite(m, Image.new("L", img.size, 0), sub)


def _lit(base: Image.Image, mask: Image.Image, amount: float) -> Image.Image:
    """mask 안을 호박색으로 물들이고 밝힌다. amount 0=그대로, 1=완전 점등."""
    if amount <= 0:
        return base
    lum = base.convert("L")
    amber = Image.merge("RGB", [lum.point(lambda v, c=c: min(255, int(v * (c / 190) + c * 0.22))) for c in AMBER])
    glow = amber.filter(ImageFilter.GaussianBlur(14))
    amber = Image.blend(amber, glow, 0.35)
    m = mask.point(lambda v: int(v * amount))
    return Image.composite(amber, base, m)


def build(still: Path, out: Path, region: tuple[float, float, float, float] | None,
          zoom: float = ZOOM_END, glow_in: tuple[float, float] = GLOW_IN) -> None:
    src = Image.open(still).convert("RGB")
    if src.size != (W, H):
        src = src.resize((W, H), Image.LANCZOS)
    mask = _region_mask(src, region) if region else _subject_mask(src)
    rcx, rcy = (region[0] + region[2] / 2, region[1] + region[3] / 2) if region else (0.5, 0.5)
    frames = round(DUR * FPS)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for i in range(frames):
            t = i / FPS
            # 카메라: 후반으로 갈수록 느려지는 push-in(파일럿 A "the camera eases to a stop")
            z = 1 + (zoom - 1) * (1 - (1 - min(t / DUR, 1)) ** 2)
            cw, ch = W / z, H / z
            # 전신 스틸에서 배를 켜면 카메라도 배로 가야 한다 — region이 있으면 그 중심으로 밀고 들어간다
            cx = min(max(rcx * W, cw / 2), W - cw / 2)
            cy = min(max(rcy * H, ch / 2), H - ch / 2)
            box = (round(cx - cw / 2), round(cy - ch / 2), round(cx + cw / 2), round(cy + ch / 2))
            frame = src.crop(box).resize((W, H), Image.LANCZOS)
            fm = mask.crop(box).resize((W, H), Image.LANCZOS)
            ramp = 0.0 if t < glow_in[0] else min(1.0, (t - glow_in[0]) / (glow_in[1] - glow_in[0]))
            # 만개 후엔 꺼지지 않고 0.78~1.0 사이에서 숨만 쉰다(캐논: 마지막 프레임까지 켜진 채)
            pulse = 1.0 if ramp < 1 else 0.89 + 0.11 * math.cos(2 * math.pi * (t - glow_in[1]) / PULSE_PERIOD)
            _lit(frame, fm, ramp * pulse).save(td / f"{i:04d}.png")
        subprocess.run(["ffmpeg", "-y", "-framerate", str(FPS), "-i", str(td / "%04d.png"),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", str(out)],
                       check=True, capture_output=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("still")
    ap.add_argument("out")
    ap.add_argument("--region", help="점등 타원 x,y,w,h (0~1 비율). 생략하면 피사체 전체")
    # WHY(2026-09-24 사용자 "이미지는 확대하지않고 그대로 있어도된다. 줌 땡기니까 벗어나는거 아니냐?"):
    # push-in을 걸면 점등 부위가 화면 밖으로 밀려날 수 있고, 도입부처럼 클립의 앞부분만 잘라 쓰면
    # 아직 확대 중이라 부위가 제자리에 없다. 고정 화면이 필요한 자리엔 줌을 끈다.
    ap.add_argument("--no-zoom", action="store_true", help="push-in 없이 고정 화면으로")
    # 도입부는 클립 앞쪽 2.6초만 잘라 쓰는데 기본 점등은 1.3초에 켜지기 시작해 2.7초에 만개한다 —
    # 그대로 쓰면 앞 절반이 깜깜하다(실측: part_kidney 2.6초까지 점등 0%).
    ap.add_argument("--glow-in", help="점등 시작,만개 시각 (기본 1.3,2.7)")
    a = ap.parse_args()
    region = tuple(float(v) for v in a.region.split(",")) if a.region else None
    if region and len(region) != 4:
        raise SystemExit("--region은 x,y,w,h 네 값")
    glow = tuple(float(v) for v in a.glow_in.split(",")) if a.glow_in else GLOW_IN
    build(Path(a.still), Path(a.out), region, zoom=1.0 if a.no_zoom else ZOOM_END, glow_in=glow)
    print(f"완료: {a.out}")


if __name__ == "__main__":
    main()
