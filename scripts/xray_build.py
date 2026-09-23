#!/usr/bin/env python3
"""반투명 인체 포맷 영상을 topic 하나에 대해 끝까지 만든다 — 칠판 조립 → 도입부 Flow → 기전 전환.

WHY(2026-09-23 파일럿에서 확정): 이 포맷은 손으로 돌리면 단계가 셋이고 그중 둘이 실수하기 쉽다.
  1. `rebuild_video` — 칠판 본체
  2. `xray_splice`로 도입부 Flow 2컷 — ⚠️ 시각을 **0으로 줘야** 한 묶음(chain)으로 이어져 전체 화면이 된다.
     0.2/1.6처럼 실제 시각을 주면 두 번째 컷이 위쪽 칸 크기로 잘려 들어간다(실측).
  3. 항목마다 기전 클립 교체 — ⚠️ 기전 클립은 4초인데 항목 구간은 13~30초다. 느리게 늘리면 정지 화면이
     되므로(구도 전환이 느린 게 지루함의 원인) **루프로 채운다.**

xray.json에 `opening[].range`와 `opening_until`을 적어두면 이 스크립트가 그대로 재현한다.

    python3 scripts/xray_build.py <topic>            # 조립까지
    python3 scripts/xray_build.py <topic> --dry-run  # 실행할 명령만
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.xray_timeline import resolve  # noqa: E402

PY = str(ROOT / ".venv" / "bin" / "python3")
LIB = "assets_library/xray/output"
MIN_PANEL_SEC = 3.0          # 이보다 짧은 구간에 기전을 갈아 끼우면 깜빡임으로만 보인다


PANEL_W, PANEL_H = 960, 680          # lib/video_assembler.XRAY_PANEL 과 같은 값
HALF_W = PANEL_W // 2


def _loop_to(clip: Path, seconds: float, out: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(clip),
                    "-t", f"{seconds:.2f}", "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-an", str(out)], check=True)


def _split_loop(act: Path, mech: Path, seconds: float, out: Path,
                act_focus: float = 0.34, mech_focus: float = 0.5) -> None:
    """왼쪽 행위 · 오른쪽 기전으로 한 칸에 나란히 넣고 구간 길이만큼 루프시킨다.

    WHY(2026-09-24 사용자 "왼쪽에 행동 오른쪽에 기전 이렇게 들어가야 할거같다"): 기전만 크게 띄우면
    "몸 안에서 무슨 일이 벌어지는지"는 보이는데 **그게 어떤 행동 때문인지**가 안 보인다. 둘을 나란히
    놓아야 "이 행동을 하면 → 몸이 이렇게 된다"가 한 화면에서 읽힌다.

    `act_focus`가 0.34인 이유: 행위 클립은 720x1280 전신이라 그대로 반으로 자르면 머리나 발만 남는다.
    위에서 34% 지점을 중심으로 잡아야 손과 상체(동작이 실제로 보이는 곳)가 들어온다.
    """
    vf = (f"[0:v]scale={HALF_W}:-2,crop={HALF_W}:{PANEL_H}:0:'min(ih-{PANEL_H},ih*{act_focus})'[a];"
          f"[1:v]scale={HALF_W}:-2,crop={HALF_W}:{PANEL_H}:0:'min(ih-{PANEL_H},ih*{mech_focus})'[m];"
          f"[a][m]hstack=2")
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-stream_loop", "-1", "-i", str(act), "-stream_loop", "-1", "-i", str(mech),
                    "-filter_complex", vf, "-t", f"{seconds:.2f}",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-an", str(out)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ad-tag", action="store_true", help="유튜브판(광고 표시 얹음)")
    ap.add_argument("--base", help="덧씌울 원본 디렉토리(예: nocta)")
    a = ap.parse_args()

    cfg = json.loads((ROOT / "data" / a.topic / "xray.json").read_text(encoding="utf-8"))
    if not a.dry_run:
        subprocess.run([PY, "-m", "lib.rebuild_video", a.topic], cwd=ROOT, check=True)

    args = []
    # 도입부: 전부 시각 0 — fill_until까지 한 묶음으로 이어 붙여 전체 화면으로 덮는다
    for o in cfg.get("opening", []):
        rng = o.get("range")
        args.append(f"0:{o['clip']}" + (f"@{rng[0]}-{rng[1]}" if rng else ""))

    # 항목 구간마다 위쪽 칸을 갈아 끼운다. `act`가 있으면 **왼쪽 행위 · 오른쪽 기전**으로 나눠 넣는다.
    tl = resolve(a.topic) or []
    acts = cfg.get("_acts") or []
    tmp = Path(tempfile.mkdtemp(prefix="xray_loop_"))
    for i, row in enumerate(tl):
        mech, dur = row.get("mech"), row["end"] - row["start"]
        if not mech or dur < MIN_PANEL_SEC:
            continue
        src = ROOT / LIB / f"{mech}.mp4"
        if not src.exists():
            raise SystemExit(f"기전 클립 없음: {mech} — 비슷한 걸로 바꾸지 말고 clip_requests.json에 적을 것")
        act = row.get("act") or (acts[i % len(acts)] if acts else None)
        dst = tmp / f"p{i}_{mech}.mp4"
        if not a.dry_run:
            if act:
                asrc = ROOT / LIB / f"{act}.mp4"
                if not asrc.exists():
                    raise SystemExit(f"행위 클립 없음: {act} — clip_requests.json에 적을 것")
                _split_loop(asrc, src, dur, dst)
            else:
                _loop_to(src, dur, dst)
        args.append(f"{row['start']:.2f}:{dst}")

    cmd = [PY, "scripts/xray_splice.py", a.topic, *args, "--panel"]
    if cfg.get("opening_until"):
        cmd += ["--fill-until", str(cfg["opening_until"])]
    if a.ad_tag:
        cmd.append("--ad-tag")
    if a.base:
        cmd += ["--base", a.base]

    print(" ".join(cmd))
    if not a.dry_run:
        subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
