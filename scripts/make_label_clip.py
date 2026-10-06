#!/usr/bin/env python3
"""해결책 칸용 '라벨 짚기' 클립 — 링크 거는 상품 사진에서 고르는 기준이 적힌 자리를 호박색 테두리로 짚고 그쪽으로 당긴다.

WHY(2026-10-07 사용자 "결론 해법 쪽에 칠판만 나오는데, 우리가 말하는 그 라벨에 어떤 게 들어가 있는지 이런 것들을
영상으로 제공하면 … 기전 때처럼 위쪽에 영상 띄워주고"): 해결책 문장은 "상자에서 이 표시를 보라"인데 칠판 글자만으론
어디를 보라는 건지 안 보인다. make_part_clip의 호박색 점등은 흰 상품 사진 위에선 안 보이고 글자를 덮어서, 글자는
그대로 두고 테두리로 짚는다. 사진은 반드시 링크를 건 바로 그 상품(assets_library/real/_products) — 라벨 글자를 AI로
그리면 뭉개진다(Flow·미드저니 금지).

    .venv/bin/python3 scripts/make_label_clip.py <상품 사진> <out.mp4> --box 0.55,0.38,0.30,0.10 [--box …]

--box는 상품 사진 안 비율(x,y,w,h). 여러 개면 순서대로 짚는다(앞 테두리는 남겨 둔다).
"""
from __future__ import annotations

import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

W, H, FPS = 720, 1280, 30
BG = (22, 32, 44)          # 엑스레이 화면의 어두운 슬레이트 바탕과 같은 톤 — 칸이 바뀌어도 튀지 않게
AMBER = (255, 176, 66)     # 이 포맷에서 "여기"를 뜻하는 색(부위 점등과 같은 값)
FIT_W, FIT_H = 620, 900    # 상품 사진을 캔버스에 올릴 최대 크기
ZOOM_END = 1.55            # 테두리 쪽으로 당기는 폭 — 라벨 글자가 칸 안에서 읽힐 만큼


def _canvas(photo: Path) -> tuple[Image.Image, tuple[int, int, int, int]]:
    im = Image.open(photo).convert("RGB")
    s = min(FIT_W / im.width, FIT_H / im.height)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    cv = Image.new("RGB", (W, H), BG)
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=28, fill=255)
    x, y = (W - im.width) // 2, (H - im.height) // 2
    cv.paste(im, (x, y), mask)
    return cv, (x, y, im.width, im.height)


def _ease(u: float) -> float:
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("out")
    ap.add_argument("--box", action="append", required=True, help="상품 사진 안 비율 x,y,w,h")
    ap.add_argument("--seconds", type=float, default=5.0)
    a = ap.parse_args()

    cv, (px, py, pw, ph) = _canvas(Path(a.photo))
    boxes = []
    for b in a.box:
        x, y, w, h = (float(v) for v in b.split(","))
        boxes.append((px + x * pw, py + y * ph, px + (x + w) * pw, py + (y + h) * ph))
    n = int(a.seconds * FPS)
    per = (a.seconds - 1.0) / len(boxes)            # 첫 1초는 상품 전체를 보여 주고, 나머지를 테두리마다 나눈다
    proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                             "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", a.out],
                            stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        frame = cv.copy()
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        line = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd, ld = ImageDraw.Draw(glow), ImageDraw.Draw(line)
        focus = None
        for i, (x0, y0, x1, y1) in enumerate(boxes):
            start = 1.0 + i * per
            alpha = _ease((t - start) / 0.5)
            if alpha <= 0:
                continue
            focus = (x0, y0, x1, y1, start)
            pulse = 0.75 + 0.25 * (0.5 + 0.5 * math.sin((t - start) * 4.5))
            pad = 10
            r = [x0 - pad, y0 - pad, x1 + pad, y1 + pad]
            gd.rounded_rectangle(r, radius=14, outline=AMBER + (int(160 * alpha * pulse),), width=18)
            ld.rounded_rectangle(r, radius=14, outline=AMBER + (int(255 * alpha),), width=6)
        glow = glow.filter(ImageFilter.GaussianBlur(10))
        # 번짐은 테두리 바깥으로만 — 안쪽까지 퍼지면 라벨 글자가 하얗게 덮여 오히려 안 읽힌다(2026-10-07 실측)
        keep = Image.new("L", (W, H), 255)
        kd = ImageDraw.Draw(keep)
        for (x0, y0, x1, y1) in boxes:
            kd.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], fill=0)
        glow.putalpha(Image.composite(glow.getchannel("A"), Image.new("L", (W, H), 0), keep))
        frame = Image.alpha_composite(Image.alpha_composite(frame.convert("RGBA"), glow), line).convert("RGB")
        # 지금 짚는 테두리 쪽으로 당긴다(첫 1초는 전체)
        if focus:
            x0, y0, x1, y1, start = focus
            z = 1 + (ZOOM_END - 1) * _ease((t - 0.6) / (a.seconds - 1.2))
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            k = _ease((t - 0.6) / 1.2)
            cx, cy = W / 2 + (cx - W / 2) * k, H / 2 + (cy - H / 2) * k
        else:
            z, cx, cy = 1 + (ZOOM_END - 1) * _ease((t - 0.6) / (a.seconds - 1.2)), W / 2, H / 2
        cw, ch = W / z, H / z
        lx = min(max(cx - cw / 2, 0), W - cw)
        ly = min(max(cy - ch / 2, 0), H - ch)
        frame = frame.crop((lx, ly, lx + cw, ly + ch)).resize((W, H), Image.LANCZOS)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait():
        raise SystemExit("ffmpeg 인코딩 실패")
    print(f"완료: {a.out}")


if __name__ == "__main__":
    main()
