# 반투명 인체(xray) 클립 인벤토리 — 원고를 쓰기 전에 "쓸 수 있는 장면"이 뭔지 보는 창구.
#
# WHY(2026-09-23): 원고를 먼저 자유롭게 쓰고 나중에 클립을 찾으면, 라이브러리에 없는 기전이 쏟아져
# 그때마다 렌더를 기다리거나 비슷한 클립으로 때우게 된다(후자는 금지 — CLAUDE.md "없는 클립은
# 요청한다"). 그래서 **원고 단계에서 이 목록을 먼저 보고 기전을 고른다.**
#
# 목록을 문서에 박지 않는 이유: 클립이 늘 때마다 문서가 낡는다. 항상 실물 파일에서 읽는다.
#
#   python3 -m lib.xray_inventory              # 종류별 요약
#   python3 -m lib.xray_inventory --mech       # 기전 전체(원고 쓸 때 이것부터)
#   python3 -m lib.xray_inventory --find 염증 inflammation
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
OUT = XRAY / "output"
NAMES = XRAY / "RENDER" / "_이름표.json"

KINDS = {"m_": "기전", "act_": "행위", "part_": "부위", "pilot": "파일럿", "cu_": "부위스틸"}


def available() -> dict[str, list[str]]:
    """종류 → 이름 목록. output/에 실제로 있는 mp4만 — 파이프라인이 읽는 곳이 거기다."""
    got: dict[str, list[str]] = {v: [] for v in KINDS.values()}
    for p in sorted(OUT.glob("*.mp4")):
        for pre, kind in KINDS.items():
            if p.stem.startswith(pre):
                got[kind].append(p.stem)
                break
    return {k: v for k, v in got.items() if v}


def pending() -> list[str]:
    """이름표에는 있는데 output에 아직 반영 안 된 것 — `scripts/publish_xray_clips.py`로 반영한다."""
    if not NAMES.exists():
        return []
    names = set(json.loads(NAMES.read_text(encoding="utf-8")).values())
    have = {p.stem for p in OUT.glob("*.mp4")}
    return sorted(n for n in names - have if not n.startswith("cu_"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mech", action="store_true", help="기전 전체 목록")
    ap.add_argument("--act", action="store_true", help="행위 전체 목록")
    ap.add_argument("--part", action="store_true", help="부위 전체 목록")
    ap.add_argument("--find", nargs="*", help="이름에 이 말이 들어간 클립 찾기")
    a = ap.parse_args()

    got = available()
    if a.find:
        for kind, items in got.items():
            hit = [x for x in items if any(q.lower() in x.lower() for q in a.find)]
            if hit:
                print(f"[{kind}] " + ", ".join(hit))
        return
    for flag, kind in ((a.mech, "기전"), (a.act, "행위"), (a.part, "부위")):
        if flag:
            items = got.get(kind, [])
            print(f"{kind} {len(items)}종")
            for x in items:
                print("  ", x)
            return

    for kind, items in got.items():
        print(f"{kind:6s} {len(items):3d}종")
    left = pending()
    if left:
        print(f"\n⚠️ output에 아직 반영 안 된 클립 {len(left)}개 — "
              "`python3 scripts/publish_xray_clips.py --commit`으로 반영할 것")


if __name__ == "__main__":
    main()
