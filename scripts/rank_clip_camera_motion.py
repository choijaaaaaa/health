#!/usr/bin/env python3
"""클립 끝 1초의 프레임 변화량이 앞부분 대비 몇 배인지 잰다.

🚨 **이 숫자로 "끝부분 결함"을 판정하지 말 것 — 2026-09-23에 그렇게 썼다가 틀렸다.**
141개를 스캔해 상위 3개(act_snore 3.62배, m_eye_elongation 2.30, act_take_supplement 2.26)의
프레임을 실제로 뽑아보니 전부 **정상적인 카메라 줌인**이었다. 전신에서 해당 부위로 밀고 들어가며
호박색 점등이 완성되는, 오히려 그 클립에서 가장 쓸 만한 구간이다. 배수가 높다고 잘라냈으면
하이라이트를 버릴 뻔했다.

지금 이 도구의 쓸모는 하나뿐이다: **카메라 움직임이 큰 클립을 찾는 것**(도입부에 쓸 역동적인
컷을 고를 때). 결함 여부는 프레임을 직접 봐야 한다 — 이 채널에서 "라벨 말고 직접 확인"이
반복 확인된 원칙이다.

    python3 scripts/rank_clip_camera_motion.py                    # 전체 스캔
    python3 scripts/rank_clip_camera_motion.py --top 20         # 움직임 큰 순
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RENDER = ROOT / "assets_library" / "xray" / "RENDER"
FPS = 6                      # 초당 6장이면 0.17초 단위 — 끝 0.5초 이상의 결함을 잡기에 충분하다
TAIL_SEC = 1.0               # 마지막 1초를 "끝"으로 본다


def _frames(path: Path, out: Path) -> list[Path]:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(path),
                    "-vf", f"fps={FPS},scale=48:85,format=gray", str(out / "f%03d.png")], check=True)
    return sorted(out.glob("f*.png"))


def _diff(a: Path, b: Path) -> float:
    """두 그레이 프레임의 평균 절대차(0~255)."""
    ia, ib = Image.open(a).getdata(), Image.open(b).getdata()
    return sum(abs(x - y) for x, y in zip(ia, ib)) / len(ia)


def scan(path: Path) -> float:
    """끝 구간 변화량 ÷ 앞 구간 변화량. 1에 가까우면 고르고, 크면 끝에서 튄다."""
    with tempfile.TemporaryDirectory() as td:
        fr = _frames(path, Path(td))
        if len(fr) < 8:
            return 0.0
        diffs = [_diff(fr[i], fr[i + 1]) for i in range(len(fr) - 1)]
        tail_n = max(2, int(TAIL_SEC * FPS))
        head, tail = diffs[:-tail_n], diffs[-tail_n:]
        if not head or not tail:
            return 0.0
        h = sum(head) / len(head)
        return (max(tail) / h) if h > 0.01 else 0.0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=25)
    a = ap.parse_args()

    names = json.loads((RENDER / "_이름표.json").read_text(encoding="utf-8"))
    rows = []
    for num, name in sorted(names.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
        p = RENDER / f"{num}.mp4"
        if not p.exists():
            continue
        rows.append((scan(p), num, name))
    rows.sort(reverse=True)

    print(f"{'배수':>6s}  {'번호':>4s}  이름   (끝 1초 최대 변화량 ÷ 앞부분 평균)")
    for ratio, num, name in rows[:a.top]:
        print(f"{ratio:6.2f}  {num:>4s}  {name}")


if __name__ == "__main__":
    main()
