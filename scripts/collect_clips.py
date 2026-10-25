#!/usr/bin/env python3
"""작업 폴더에 받은 클립을 라이브러리로 들이고, 작업 시트를 다시 만든다.

WHY(2026-09-24 사용자 "폴더도 좀 어디다넣을지도 구조화하고 딱 거기서만 작업하면 되게"): 요청 시트와
스틸과 결과물이 매번 다른 자리에 생겨서, 어디서 작업해야 하는지 물어봐야 알 수 있었다. 작업 자리를
한 곳으로 고정한다.

    ai-video-network/deploy/작업/          (2026-09-25 저장소 밖 한 단계로 옮김)
      만사전.md             ← 건강·육아·댕냥 공용 시트(2026-10-25 통합). 이 파일만 읽으면 된다(번호·프롬프트)
      만사전_스틸/          ← 스틸이 번호순으로 있다. 미드저니로 새로 뽑은 것도, Flow 결과 mp4도 여기

`만사전_스틸/`에 mp4를 넣고 이걸 돌리면 **이 저장소 몫만**(병합기 manifest로 가른다 — 댕냥 클립은 그쪽 세션이
가져간다) 라이브러리(`output/`)로 옮기고 시트를 다시 만든다. 번호가 다시 매겨지므로 **남은 것만 1번부터** 보인다.

    .venv/bin/python3 scripts/collect_clips.py            # 뭐가 들어올지만
    .venv/bin/python3 scripts/collect_clips.py --commit
"""
from __future__ import annotations

import argparse
import contextlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks, workbench  # noqa: E402

XRAY = ROOT / "assets_library" / "xray"
# 받는 곳은 건강·육아·댕냥 공용 deploy/작업/만사전_스틸/ — 스틸 옆에 mp4를 그대로 넣으면 된다
INBOX = tracks.work_paths(None)[2]
LIB = XRAY / "output"


def _known() -> dict[str, dict]:
    """요청해둔 클립 이름 → 요청 본문. 오타로 엉뚱한 파일이 들어오는 걸 막는다."""
    out: dict[str, dict] = {}
    # 트랙 폴더(data/육아/…)는 한 단계 깊어서 평평한 글롭에 안 걸린다
    for f in tracks.glob_topic_files(ROOT / "data", "*/clip_requests.json"):
        try:
            for r in json.loads(f.read_text(encoding="utf-8")).get("requests", []):
                if r.get("name"):
                    out.setdefault(r["name"], r)
        except json.JSONDecodeError:
            continue
    return out


def _refresh() -> None:
    """들인 뒤 시트를 다시 만들고(사람이 넣은 스틸도 그때 건져낸다) 다시 조립할 topic을 보인다."""
    subprocess.run([sys.executable, "scripts/prep_clip_worksheet.py"], cwd=ROOT, check=False)
    print("\n이제 그 topic들을 다시 조립하면 된다:")
    subprocess.run([sys.executable, "scripts/rebuild_stale.py"], cwd=ROOT, check=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()

    INBOX.mkdir(parents=True, exist_ok=True)
    known = _known()
    moved, unknown = [], []
    # 옮기는 동안은 작업대 lock을 잡는다 — 그 사이 다른 세션 병합기가 폴더를 다시 채우면 옮길 파일이 사라진다
    with (workbench.lock() if a.commit else contextlib.nullcontext()):
        got = workbench.claim(no_lock=a.commit)
        found = [f for f in got["mine"] + got["unclaimed"] if f["kind"] == "video" and f["file"].endswith(".mp4")]
        if not found:
            print(f"{INBOX.name}/ 에 이 저장소 mp4가 없다 — Flow 결과를 **클립 이름 그대로** 넣어라.")
        for f in found:
            # 번호를 앞에 붙여 저장했어도 받아준다("04_act_inject_belly.mp4") — 번호 떼기는 claim이 한다
            name = f["clip"]
            if name not in known:
                unknown.append(f["file"])
                continue
            dest = LIB / f"{name}.mp4"
            moved.append((f["file"], dest.name))
            if a.commit:
                shutil.move(f["path"], str(dest))

    for src, dst in moved:
        print(f"  {'✅' if a.commit else '[dry]'} {src} → output/{dst}")
    if got["others"]:
        print(f"  (다른 채널 몫 {got['others']}개는 그대로 — 그쪽 세션이 가져간다)")
    if got["ambiguous"]:
        print(f"\n⚠️ 두 저장소가 같은 클립 이름을 써서 못 가른 파일 {len(got['ambiguous'])}개 — 시트 번호를 앞에 붙여 저장해야 한다:")
        for f in got["ambiguous"]:
            print("   -", f["file"])
    if unknown:
        print(f"\n⚠️ 요청 목록에 없는 이름 {len(unknown)}개 — 파일명을 확인해라(그대로 두었다):")
        for n in unknown:
            print("   -", n)
    if not a.commit:
        print(f"\ndry-run — 옮기지 않았다. 실제로 들이려면 --commit")
        return

    print(f"\n클립 {len(moved)}개 반영. 작업 시트를 다시 만든다(사람이 넣은 스틸도 그때 건져낸다).")
    _refresh()


if __name__ == "__main__":
    main()
