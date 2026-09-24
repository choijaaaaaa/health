#!/usr/bin/env python3
"""`대본검토/사진변경/<topic>.json`에 적힌 슬롯별 품목대로 공용 사진 배정표(ko)를 다시 잡는다.

WHY(2026-09-24): 대본을 새로 쓰면 카드 항목이 바뀌고, 카드 배지·사진은 **슬롯 번호**로 배정표에서
나온다 — 글만 바꾸고 배정표를 그대로 두면 "더운 잠자리" 카드에 고추 사진이 붙는다(여성_4 실측).
여러 에이전트가 배정표(sqlite)를 동시에 쓰면 꼬이므로, 에이전트는 이 JSON만 남기고 적용은 여기서
한 번에 한다. 이미 많이 쓰인 사진을 피해(재사용 상한 원칙) 품목마다 가장 덜 쓰인 사진을 고른다.

    .venv/bin/python3 scripts/apply_photo_changes.py            # 뭐가 바뀔지만
    .venv/bin/python3 scripts/apply_photo_changes.py --commit [topic ...]
"""
from __future__ import annotations

import argparse
import collections
import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT.parent / "assets-shared" / "catalog.db"
CHANGES = ROOT / "대본검토" / "사진변경"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*")
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()
    files = [CHANGES / f"{t}.json" for t in a.topics] if a.topics else sorted(CHANGES.glob("*.json"))
    c = sqlite3.connect(DB)
    used = collections.Counter(r[0] for r in c.execute("select photo_id from assignments"))
    missing: list[str] = []
    for f in files:
        spec = json.loads(f.read_text(encoding="utf-8"))
        topic = spec["topic"]
        want = dict(spec.get("slots", {}))
        if spec.get("cover"):
            want["cover"] = spec["cover"]
        taken: set[str] = set()
        for slot, item in want.items():
            for s in (slot, f"bg:{slot}"):
                pool = [r[0] for r in c.execute(
                    "select id from photos where item=? and (rejected is null or rejected=0)", (item,))]
                # 1) 이 topic에서 아직 안 쓴 사진 → 2) 쓴 사진이라도(배지·배경이 같은 사진) →
                # 3) 장기 품목은 사진 풀이 아니라 X-ray 프레임으로 이미 배정돼 있다(xray_organ_photos.py) —
                #    다른 topic 배정에서 그 품목에 쓴 사진을 가져온다
                ids = [x for x in pool if x not in taken] or pool or [r[0] for r in c.execute(
                    "select distinct photo_id from assignments where item=?", (item,))]
                if not ids:
                    missing.append(f"{topic} {s} '{item}'")
                    continue
                pid = min(ids, key=lambda p: used[p])
                taken.add(pid)
                used[pid] += 1
                if a.commit:
                    cur = c.execute("update assignments set item=?, photo_id=? where project='health-shorts' "
                                    "and topic=? and lang='ko' and slot=?", (item, pid, topic, s))
                    if cur.rowcount == 0:
                        c.execute("insert into assignments(project,topic,lang,slot,item,photo_id) "
                                  "values('health-shorts',?,'ko',?,?,?)", (topic, s, item, pid))
        print(f"{'✅' if a.commit else '[dry]'} {topic}: {len(want)}슬롯")
    if a.commit:
        c.commit()
    if missing:
        print(f"\n⚠️ 사진이 없는 품목 {len(missing)}건 — 카드 char_file을 사진 있는 품목으로 바꿔야 한다:")
        for m in missing:
            print("   -", m)


if __name__ == "__main__":
    main()
