#!/usr/bin/env python3
# 설정·나레이션이 영상보다 새 것인 topic만 골라낸다.
#
# WHY(2026-09-24): 조립은 topic당 몇 분씩 걸려서 전부 다시 돌릴 수 없는데, 큐가 도는 동안
# xray.json을 고치면 **그 전에 읽힌 설정으로 만들어진 영상**이 남는다. 무엇이 낡았는지
# 파일 시각으로 가려서 그것만 다시 돌린다.
#
#   .venv/bin/python3 scripts/rebuild_stale.py            # 목록만
#   .venv/bin/python3 scripts/rebuild_stale.py --run      # 순차 재조립(병렬 금지 — 로드가 30을 넘는다)
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def stale(topics: list[str] | None = None) -> list[str]:
    out = []
    for cfg in sorted((ROOT / "data").glob("*/xray.json")):
        t = cfg.parent.name
        if topics and t not in topics:
            continue
        vid = ROOT / "output" / t / "shorts_xray_test.mp4"
        srcs = [cfg, cfg.parent / "narration.txt", ROOT / "output" / t / "narration.mp3"]
        newest = max((s.stat().st_mtime for s in srcs if s.exists()), default=0)
        if not vid.exists() or newest > vid.stat().st_mtime:
            out.append(t)
    return out


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    todo = stale(args or None)
    print(f"낡은 영상 {len(todo)}개: {todo}")
    if "--run" not in sys.argv:
        return
    for t in todo:
        print(f"=== {t}", flush=True)
        r = subprocess.run([str(ROOT / ".venv/bin/python3"), "scripts/xray_build.py", t, "--preview"],
                           cwd=ROOT, capture_output=True, text=True)
        tail = [ln for ln in (r.stdout + r.stderr).splitlines()
                if any(k in ln for k in ("미리보기", "shorts_xray", "실패", "부족"))]
        print("\n".join(tail[-3:]), flush=True)


if __name__ == "__main__":
    main()
