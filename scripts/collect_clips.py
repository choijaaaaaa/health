#!/usr/bin/env python3
"""작업 폴더에 받은 클립을 라이브러리로 들이고, 작업 시트를 다시 만든다.

WHY(2026-09-24 사용자 "폴더도 좀 어디다넣을지도 구조화하고 딱 거기서만 작업하면 되게"): 요청 시트와
스틸과 결과물이 매번 다른 자리에 생겨서, 어디서 작업해야 하는지 물어봐야 알 수 있었다. 작업 자리를
한 곳으로 고정한다.

    assets_library/xray/작업/
      0_작업지시.md     ← 이 파일만 읽으면 된다(번호·프롬프트)
      1_스틸/           ← 여기 스틸이 번호순으로 있다. 미드저니로 새로 뽑은 것도 여기 넣는다
      2_완성클립/       ← Flow 결과를 **클립 이름 그대로** 여기 넣는다
      _지난것/          ← 끝난 시트 보관

`2_완성클립/`에 넣고 이걸 돌리면 라이브러리(`output/`)로 옮기고 시트를 다시 만든다.
번호가 다시 매겨지므로 **남은 것만 1번부터** 보인다.

    .venv/bin/python3 scripts/collect_clips.py            # 뭐가 들어올지만
    .venv/bin/python3 scripts/collect_clips.py --commit
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
INBOX = XRAY / "작업" / "2_완성클립"
WORK = XRAY / "작업" / "1_스틸"
STILLS = XRAY / "stills"
LIB = XRAY / "output"


def _known() -> dict[str, dict]:
    """요청해둔 클립 이름 → 요청 본문. 오타로 엉뚱한 파일이 들어오는 걸 막는다."""
    out: dict[str, dict] = {}
    for f in (ROOT / "data").glob("*/clip_requests.json"):
        try:
            for r in json.loads(f.read_text(encoding="utf-8")).get("requests", []):
                if r.get("name"):
                    out.setdefault(r["name"], r)
        except json.JSONDecodeError:
            continue
    return out


def _still_dest(name: str, req: dict) -> Path:
    """스틸이 라이브러리에서 살 자리. 스틸만 받는 요청(아기 캐논 등)은 stills/ 바로 밑에 둔다 —
    make_part_clip.py가 그 경로로 클립을 만든다."""
    if req.get("kind") == "still":
        return STILLS / f"{name}.jpg"
    return STILLS / ("mech" if name.startswith("m_") else "act") / f"{name}.jpg"


def _harvest_stills(known: dict[str, dict], commit: bool) -> list[tuple[str, str]]:
    """1_스틸/에 새로 들어온 미드저니 스틸을 라이브러리로 들인다.

    WHY(2026-09-24): prep_clip_worksheet가 시트를 다시 만들 때 1_스틸/을 통째로 지우고 다시
    채운다. 사용자가 새로 뽑아 넣은 스틸을 그 전에 거둬가지 않으면 **그대로 사라진다** — 영상
    요청은 mp4가 남아 티가 안 났지만, 아기 캐논처럼 스틸 자체가 산출물인 요청은 결과물을 잃는다."""
    moved = []
    for f in sorted(WORK.glob("*.jpg")):
        name = f.stem.split("_", 1)[1] if f.stem[:2].isdigit() and "_" in f.stem else f.stem
        req = known.get(name)
        if req is None:
            continue
        dest = _still_dest(name, req)
        if dest.exists():          # 이미 들인 것을 시트가 복사해둔 사본이다
            continue
        moved.append((f.name, str(dest.relative_to(XRAY))))
        if commit:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, dest)
    return moved


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()

    INBOX.mkdir(parents=True, exist_ok=True)
    known = _known()
    stills = _harvest_stills(known, a.commit) if WORK.exists() else []
    for src, dst in stills:
        print(f"  {'✅' if a.commit else '[dry]'} {src} → {dst}")
    found = sorted(INBOX.glob("*.mp4"))
    if not found and not stills:
        print(f"{INBOX.relative_to(ROOT)}/ 가 비어 있다 — Flow 결과를 **클립 이름 그대로** 넣어라.")
    moved, unknown = [], []
    for f in found:
        # 번호를 앞에 붙여 저장했어도 받아준다("04_act_inject_belly.mp4")
        name = f.stem.split("_", 1)[1] if f.stem[:2].isdigit() and "_" in f.stem else f.stem
        if name not in known:
            unknown.append(f.name)
            continue
        dest = LIB / f"{name}.mp4"
        moved.append((f.name, dest.name))
        if a.commit:
            shutil.move(str(f), str(dest))

    for src, dst in moved:
        print(f"  {'✅' if a.commit else '[dry]'} {src} → output/{dst}")
    if unknown:
        print(f"\n⚠️ 요청 목록에 없는 이름 {len(unknown)}개 — 파일명을 확인해라(그대로 두었다):")
        for n in unknown:
            print("   -", n)
    if not a.commit:
        print(f"\ndry-run — 옮기지 않았다. 실제로 들이려면 --commit")
        return

    print(f"\n클립 {len(moved)}개 · 스틸 {len(stills)}장 반영. 작업 시트를 다시 만든다.")
    subprocess.run([sys.executable, "scripts/prep_clip_worksheet.py"], cwd=ROOT, check=False)
    print("\n이제 그 topic들을 다시 조립하면 된다:")
    subprocess.run([sys.executable, "scripts/rebuild_stale.py"], cwd=ROOT, check=False)


if __name__ == "__main__":
    main()
