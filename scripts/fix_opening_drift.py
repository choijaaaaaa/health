#!/usr/bin/env python3
"""나레이션을 다시 뽑아 시각이 밀린 뒤, 도입부 경계를 지금 자막에 맞춰 다시 맞춘다.

WHY(2026-09-24): 숫자 읽기가 깨진 음성 18편을 다시 뽑았더니 문장 시각이 전부 몇백 ms씩
움직였다. `opening_until`은 그대로라서 ①문장 한가운데서 칠판으로 넘어가거나 ②도입부가
끝나기 전에 시간표 첫 구간이 시작해 **전체 화면 도입 영상 위에 칸이 겹쳐 그려졌다.**
topic 스무 개를 손으로 맞추면 또 어긋난다 — 규칙이 하나뿐이니 기계가 한다.

규칙(둘 다 `XRAY_FORMAT.md`에 있는 것):
  1. 도입부는 **문장 경계**에서 끝난다 — 지금 값에서 가장 가까운 자막 끝으로 스냅한다.
  2. 그 시각보다 먼저 시작하는 시간표 행은 **도입부에 흡수된다**(삭제) — 남겨두면 칸이 겹친다.

    .venv/bin/python3 scripts/fix_opening_drift.py            # 뭐가 바뀔지만
    .venv/bin/python3 scripts/fix_opening_drift.py --commit
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks                                  # noqa: E402
from lib.xray_timeline import _cues, _time_of           # noqa: E402


def fix(topic: str, commit: bool) -> list[str]:
    path = tracks.data_dir(topic) / "xray.json"
    if not path.exists():
        return []
    cfg = json.loads(path.read_text(encoding="utf-8"))
    until = cfg.get("opening_until")
    if not until:
        return []
    cues = _cues(topic)
    if not cues:
        return []

    notes: list[str] = []
    # 1. 자막 끝으로 스냅 — 문장을 자르지 않게. 다만 **시간표 첫 구간을 넘어서지 않는다**:
    #    가장 가까운 끝으로만 붙이면 "먼저 제로 탄산음료예요" 같은 첫 항목 선언까지 도입부가
    #    먹어버린다(실측). 겹침을 없애는 쪽으로만 움직이고, 모자라면 줄인다.
    starts = []
    for row in cfg.get("timeline", []):
        try:
            starts.append(_time_of(row["from"], cues))
        except ValueError:
            pass
    ceiling = min(starts) + 0.05 if starts else float("inf")
    ends = [en for _st, en, _t in cues if en <= ceiling] or [en for _st, en, _t in cues]
    snapped = min(ends, key=lambda e: abs(e - until))
    if abs(snapped - until) > 0.05:
        notes.append(f"도입부 {until} → {snapped}초(자막 끝에 맞춤)")
        cfg["opening_until"] = snapped
        until = snapped

    # 2. 도입부 안에서 시작하는 행은 흡수 — 남으면 전체 화면 위에 칸이 겹친다
    kept, dropped = [], []
    for row in cfg.get("timeline", []):
        try:
            st = _time_of(row["from"], cues)
        except ValueError:
            kept.append(row)            # 자막에 없는 구절은 여기서 손대지 않는다(preflight가 따로 잡는다)
            continue
        (dropped if st < until - 0.05 else kept).append(row)
    if dropped:
        notes.append(f"도입부에 흡수된 행 {len(dropped)}개: " +
                     ", ".join(repr(r["from"]) for r in dropped))
        cfg["timeline"] = kept

    if notes and commit:
        path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return notes


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*")
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()
    topics = a.topics or sorted(
        p.parent.name for p in tracks.glob_topic_files(ROOT / "data", "*/xray.json"))
    n = 0
    for t in topics:
        notes = fix(t, a.commit)
        if notes:
            n += 1
            print(f"{'✅' if a.commit else '[dry]'} {t}")
            for x in notes:
                print("     ·", x)
    print(f"\n{n}개 topic 조정" + ("" if a.commit else " — 실제로 고치려면 --commit"))


if __name__ == "__main__":
    main()
