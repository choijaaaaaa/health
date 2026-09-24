#!/usr/bin/env python3
# 조립된 영상에서 **분할 패널이 실제로 들어간 구간**을 센다.
#
# WHY(2026-09-24): "왼쪽 행동·오른쪽 기전"이 일부 구간에만 들어가 있는데도 로그는 멀쩡했던 적이
# 있다(_panel_track이 뒤에서 덮어써서). 프레임을 눈으로 훑는 것 말고는 확인할 방법이 없었는데,
# 분할본에는 가운데 8px 구분선(0x3A5A66)이 있으므로 그 세로줄을 찾으면 기계로 셀 수 있다.
#
#   .venv/bin/python3 scripts/verify_split_panels.py <topic>
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.xray_timeline import resolve, summary_start   # noqa: E402

PANEL_X, PANEL_Y, PANEL_W, PANEL_H = 60, 190, 960, 680
DIV_RGB = (0x3A, 0x5A, 0x66)
TOL = 26


def has_divider(video: Path, t: float) -> bool:
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "f.png"
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video),
                            "-frames:v", "1", str(f)], capture_output=True)
        if r.returncode or not f.exists():
            return False
        im = Image.open(f).convert("RGB")
    px = im.load()
    # 칸 가운데 세로줄이 구분선 색으로 죽 이어지는지 — 위아래 60%만 봐도 충분하다
    cx = PANEL_X + PANEL_W // 2
    hit = 0
    ys = range(PANEL_Y + PANEL_H // 5, PANEL_Y + PANEL_H * 4 // 5, 4)
    total = 0
    for y in ys:
        total += 1
        for x in (cx - 2, cx - 1, cx, cx + 1):
            r_, g_, b_ = px[x, y]
            if abs(r_ - DIV_RGB[0]) < TOL and abs(g_ - DIV_RGB[1]) < TOL and abs(b_ - DIV_RGB[2]) < TOL:
                hit += 1
                break
    return total and hit / total > 0.8


def main() -> None:
    topic = sys.argv[1]
    video = ROOT / "output" / topic / "shorts_xray_test.mp4"
    if not video.exists():
        raise SystemExit(f"영상 없음: {video.relative_to(ROOT)}")
    rows = resolve(topic) or []
    # 결론 구절부터는 칠판 전체로 덮이므로 칸이 없는 게 맞다 — 여기서 분할을 기대하면 오탐이다
    ts = summary_start(topic)
    split = plain = 0
    for i, r in enumerate(rows, 1):
        mid = (r["start"] + r["end"]) / 2 + 0.2      # 영상은 제목카드만큼 밀려 있다
        ok = has_divider(video, mid)
        in_summary = ts is not None and r["start"] >= ts - 0.05
        # 아직 못 받은 행위 클립은 미리보기에서 기전 단독으로 떨어진다 — 어긋남이 아니다
        act = r.get("act")
        missing = bool(act) and not (ROOT / "assets_library/xray/output" / f"{act}.mp4").exists()
        want = bool(act) and not in_summary and not missing
        mark = "✅" if ok == want else ("❌" if want else "  ")
        if in_summary:
            mark = "결론"
        elif missing:
            mark = "대기"
        print(f"{mark} {i:2d} {r['start']:5.1f}-{r['end']:5.1f} {str(r.get('label') or ''):12s}"
              f" act={'있음' if want else '—':4s} 화면={'분할' if ok else '기전 단독'}")
        split += ok
        plain += not ok
    body = [r for r in rows if not (ts is not None and r["start"] >= ts - 0.05)]
    no_act = sum(1 for r in body if not r.get("act"))
    print(f"\n분할 {split}구간 / 기전 단독 {plain}구간"
          f"  — 설명 구간 {len(body)}개 중 행위 미지정 {no_act}개")


if __name__ == "__main__":
    main()
