#!/usr/bin/env python3
"""클립에서 부위가 가장 밝게 켜져 있는 구간을 찾아준다 — 도입부에 쓸 2.4초를 고르는 용도.

WHY(2026-09-20 실측): Flow가 낸 행위 클립은 "마지막 프레임까지 켜져 있으라"고 써도 점등이 깜빡인다
(01은 후반 2.13%였다가 끝에서 0%, 05·06은 끝에서만 켜짐). 사람이 눈으로 구간을 고르면 매번 달라지고
빠뜨리니, 프레임별 따뜻한 색 비율을 재서 가장 밝은 연속 구간을 뽑는다.

    python3 scripts/pick_glow_window.py assets_library/xray/RENDER/01.mp4 --len 2.4
    python3 scripts/pick_glow_window.py assets_library/xray/RENDER/*.mp4 --len 2.4 --json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops

FPS = 30
STRIDE = 3  # 0.1초 간격이면 충분하다 — 프레임마다 재면 클립당 수십 초가 걸린다


def _warm_series(path: Path) -> list[float]:
    """0.1초 간격으로 '따뜻한 색(호박색) 픽셀 비율'을 잰다."""
    with tempfile.TemporaryDirectory() as td:
        subprocess.run(["ffmpeg", "-y", "-i", str(path), "-vf", f"select='not(mod(n\\,{STRIDE}))',scale=180:-1",
                        "-vsync", "0", f"{td}/%04d.png"], check=True, capture_output=True)
        out = []
        for f in sorted(Path(td).glob("*.png")):
            im = Image.open(f).convert("RGB")
            r, _, b = im.split()
            mask = ImageChops.subtract(r, b).point(lambda v: 255 if v > 40 else 0)
            out.append(sum(mask.getdata()) / 255 / (im.width * im.height))
        return out


def best_window(path: Path, length: float) -> dict:
    s = _warm_series(path)
    step = STRIDE / FPS
    n = max(1, round(length / step))
    if len(s) <= n:
        return {"start": 0.0, "end": len(s) * step, "score": sum(s) / max(1, len(s))}
    sums = [sum(s[i:i + n]) for i in range(len(s) - n + 1)]
    i = max(range(len(sums)), key=lambda k: sums[k])
    return {"start": round(i * step, 2), "end": round((i + n) * step, 2),
            "score": round(sums[i] / n * 100, 2), "max": round(max(s) * 100, 2)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--len", type=float, default=2.4, help="뽑을 구간 길이(초)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    res = {Path(c).stem: best_window(Path(c), a.len) for c in a.clips}
    if a.json:
        print(json.dumps(res, ensure_ascii=False, indent=1))
    else:
        for k, v in res.items():
            print(f"{k}: {v['start']:.2f}~{v['end']:.2f}초  평균 점등 {v['score']:.2f}% (최대 {v['max']:.2f}%)")


if __name__ == "__main__":
    main()
