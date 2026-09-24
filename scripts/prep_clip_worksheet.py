#!/usr/bin/env python3
"""아직 못 받은 클립을 **스틸까지 한 폴더에 번호순으로 모아** 작업 시트로 낸다.

WHY(2026-09-24): 시트에 번호를 붙여놓고 스틸은 `stills/act/`·`stills/mech/`에 원래 이름으로
흩어져 있어 매칭이 안 됐다 — "번호별로 뭔지 그게 중요한건데". 시트 번호와 스틸 파일 앞 번호를
같게 맞추고, act/mech를 가르지 않고 `작업/스틸/` 한 곳에 모은다.

결과 영상만 번호 없이 원래 이름으로 저장한다(`RENDER/<이름>.mp4`) — 조립기가 그 이름으로 찾는다.

    .venv/bin/python3 scripts/prep_clip_worksheet.py
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks  # noqa: E402
LIB = ROOT / "assets_library" / "xray" / "output"
STILLS = ROOT / "assets_library" / "xray" / "stills"
# 🚨 기본(건강) 트랙의 작업 자리. 이름을 바꾸지 말 것(2026-09-24 사용자 "이름도 매번바뀌고") —
# 시트를 `지금_뽑을것.md`에서 이 이름으로 한 번 바꿨더니 편집기에 열어둔 파일이 사라져서
# "내가 뭘 뽑아야 하는지"를 다시 물어야 했다. tests/test_xray_worksheet_path.py가 막는다.
# 트랙별 자리는 lib/tracks.py의 work_paths()가 준다(육아는 작업_육아/).
SHEET, WORK, INBOX = tracks.work_paths(None)
CANON = "assets_library/xray/stills/canon_organs.jpg"


DOWNLOADS = Path.home() / "Downloads"
CONSUMED = ROOT / "assets_library" / "xray" / "작업" / ".받은것.json"


def _unopened_deliveries() -> list[Path]:
    """다운로드 폴더에 아직 안 푼 미드저니 zip이 있는가.

    WHY(2026-09-24): 사용자가 미드저니 5장을 이미 뽑아 zip으로 줬는데 그걸 안 풀고
    시트를 다시 만들어 "03~07은 미드저니부터"로 내보냈다 — 같은 걸 또 뽑으라는 말이
    됐다("아까 미드저니꺼 5개도 뽑아줬는데 다시또뽑으라는거냐"). 시트가 사람에게
    일을 시키기 전에 **이미 받은 게 없는지 먼저 본다.**
    """
    try:
        done = set(json.loads(CONSUMED.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        done = set()
    return [z for z in sorted(DOWNLOADS.glob("midjourney_session*.zip"))
            if z.name not in done]


def mark_consumed(paths) -> None:
    """푼 zip을 기록한다 — 다음부터 경고에 안 뜬다."""
    try:
        done = set(json.loads(CONSUMED.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        done = set()
    done |= {Path(p).name for p in paths}
    CONSUMED.write_text(json.dumps(sorted(done), ensure_ascii=False, indent=2), encoding="utf-8")


def _pending(track: str | None) -> list[list]:
    """그 트랙의 아직 못 받은 요청만. 트랙은 topic 접두어가 아니라 파일이 있는 자리로 가른다 —
    `data/육아/_shared/`처럼 topic 이름이 접두어를 안 가진 공용 요청이 있다."""
    out, seen = [], set()
    for f in tracks.glob_topic_files(ROOT / "data", "*/clip_requests.json"):
        if tracks.track_of_path(f) != track:
            continue
        topic = f.parent.name
        # 트랙 공용 요청(`data/육아/_shared/`)은 **그 트랙 시트에만** 싣는다 — 2026-09-24
        # 사용자 확인. 기본 시트에 섞였더니 프롬프트가 길어 이 프로젝트 요청이 아래로
        # 밀려 "애기 이야기만 있다"가 됐다. 트랙별 시트가 생긴 지금은 자리를 가르면 된다
        # (통째로 빼면 아기 캐논 6장·기전 13종이 어느 시트에도 안 떠서 영영 안 뽑힌다).
        if track is None and topic.startswith("_"):
            continue
        try:
            reqs = json.loads(f.read_text(encoding="utf-8")).get("requests", [])
        except json.JSONDecodeError:
            continue
        for r in reqs:
            n = r.get("name")
            if not n or n in seen or _done(r, track):
                continue
            seen.add(n)
            out.append([topic, r, _sub_of(r)])
    return out


def _sub_of(r: dict) -> str:
    """스틸 저장 갈래. 기전은 mech/, 행위·부위는 act/, 스틸만 받는 요청은 stills/ 바로 밑."""
    if r.get("kind") == "still":
        return "still"
    return "mech" if r["name"].startswith("m_") else "act"


def _done(r: dict, track: str | None) -> bool:
    """받은 것으로 볼지 — 영상 요청은 클립이, 스틸 요청은 스틸 자체가 최종 산출물이다.

    WHY(2026-09-24 육아 트랙): 아기 몸이 나오는 장면은 Flow(Veo)에 보내지 않는다. 미성년자
    안전필터가 `infant`/`child` 단어만으로도 막은 전례가 있어서, 아기는 미드저니 정지 스틸로만
    뽑고 카메라 푸시인·점등은 scripts/make_part_clip.py가 코드로 입힌다. 그래서 "Flow 결과
    mp4가 없으면 미완"이라는 기존 판정이 이 요청들엔 영영 참이라 시트에서 안 내려간다."""
    if r.get("kind") == "still":
        return (tracks.stills_dir(track) / f"{r['name']}.jpg").exists()
    return (LIB / f"{r['name']}.mp4").exists()


def _existing_still(sub: str, name: str, track: str | None) -> Path | None:
    """번호가 붙었든 안 붙었든 그 이름으로 끝나는 스틸을 찾는다."""
    base = tracks.stills_dir(track) if sub == "still" else STILLS / sub
    for p in sorted(base.glob(f"*{name}.jpg")) if base.exists() else []:
        return p
    work = tracks.work_paths(track)[1]
    for p in sorted(work.glob(f"*{name}.jpg")) if work.exists() else []:
        return p
    return None


def _harvest_loose_stills(pend: list[list], work: Path, track: str | None) -> None:
    """`1_스틸/`에만 있고 stills/에는 없는 스틸을 먼저 원본 자리로 옮긴다.

    🚨 아래에서 이 폴더를 통째로 지우고 다시 채운다 — 사람이 방금 넣은 스틸이
    stills/act|mech/에 사본이 없으면 그대로 사라진다. 이 저장소는 세션 여럿이
    같이 쓰고(육아 트랙 등) 시트 갱신은 아무 세션이나 돌리므로, 내가 안 지워도
    남이 지운다. 지우기 전에 원본 자리로 건져낸다(2026-09-24).
    """
    if not work.exists():
        return
    want = {r["name"]: sub for _t, r, sub in pend}
    for f in sorted(work.glob("*.jpg")):
        name = f.stem.split("_", 1)[1] if f.stem[:2].isdigit() and "_" in f.stem else f.stem
        sub = want.get(name)
        if not sub:
            continue
        # 스틸 자체가 산출물인 요청(아기 캐논 등)은 act/mech로 가르지 않고 트랙 스틸 폴더에 둔다
        dst = (tracks.stills_dir(track) if sub == "still" else STILLS / sub) / f"{name}.jpg"
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dst)
        print(f"  건져냄: {f.name} → {dst.relative_to(ROOT)}")


def main() -> None:
    # 트랙마다 시트를 따로 낸다 — 한 폴더에 섞이면 번호가 엉켜 "몇 번을 뽑으라는 거냐"가 된다
    for track in [None, *tracks.TRACKS]:
        build(track)


def build(track: str | None) -> None:
    sheet, work, inbox = tracks.work_paths(track)
    pend = _pending(track)
    if not pend and not sheet.exists():
        return
    # 번호는 시트에 실리는 차례(0부 스틸 → 1부 Flow만 → 2부 미드저니부터)와 같아야 한다.
    # 안 그러면 "01~09 미드저니 먼저 / 03~11 스틸만"처럼 구간이 겹쳐 무엇부터 할지 알 수 없다.
    def order(x):
        _topic, r, sub = x
        if sub == "still":
            return (0, _topic)
        return (1 if _existing_still(sub, r["name"], track) else 2, _topic)

    pend.sort(key=order)
    _harvest_loose_stills(pend, work, track)
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    for i, (topic, r, sub) in enumerate(pend, 1):
        src = _existing_still(sub, r["name"], track)
        r["_no"], r["_work"] = f"{i:02d}", f"{i:02d}_{r['name']}.jpg"
        if src:
            shutil.copy2(src, work / r["_work"])

    # 스틸만 받는 요청을 1·2부에 섞으면 "이것도 Flow를 돌려야 하나"가 된다 — 따로 세운다
    stills = [x for x in pend if x[2] == "still"]
    ready = [x for x in pend if x[2] != "still" and (work / x[1]["_work"]).exists()]
    todo = [x for x in pend if x[2] != "still" and x not in ready]
    # 맨 위 두 줄이 "내가 지금 뭘 하면 되는지"를 번호로 답해야 한다 — 표까지 읽게 하면
    # "몇번몇번 플로우랑 미드저니 뭐지?"를 또 묻게 된다(2026-09-24).
    span = lambda xs: ("없음" if not xs
                       else "·".join(r["_no"] for _t, r, _s in xs) if len(xs) <= 4
                       else f"{xs[0][1]['_no']}~{xs[-1][1]['_no']}")
    L = [f"# 지금 뽑을 클립 {len(pend)}종" + (f" — {track} 트랙" if track else "") + "\n",
         f"\n## 내가 할 일\n",
         f"\n- **{span(ready)} → Flow만** 돌린다(스틸은 이미 `{work.relative_to(ROOT)}/`에 있다).\n",
         f"- **{span(todo)} → 미드저니 먼저**, 나온 스틸을 그 폴더에 `<번호>_<이름>.jpg`로 넣고 Flow.\n",
         f"- **{span(stills)} → 미드저니만**. **Flow 안 돌린다** — 스틸만 주면 코드가 클립을 만든다.\n",
         f"\n**받은 영상은 `{inbox.relative_to(ROOT)}/`에 클립 이름 그대로 넣는다**"
         " — 그 뒤 `scripts/collect_clips.py --commit`이 라이브러리로 들인다.\n",
         "\n🚨 Flow는 **start 프레임만** 준다 — end를 주면 Veo가 사이를 맞추려고 피사체를 변형시킨다.\n",
         "\n| # | 이름 | topic | 할 일 |\n|---|---|---|---|\n"]
    for topic, r, sub_ in pend:
        할일 = ("미드저니만(스틸)" if sub_ == "still"
                else "Flow만" if (work / r["_work"]).exists() else "미드저니 → Flow")
        L.append(f"| {r['_no']} | `{r['name']}` | {topic} | {할일} |\n")

    if stills:
        L.append(f"\n---\n\n# 0부 · 미드저니만 — 스틸 {len(stills)}장 (Flow 안 돌린다)\n")
        L.append(f"\n🚨 **이 번호들은 영상을 뽑지 않는다.** 미드저니 스틸 한 장씩만 "
                 f"`{work.relative_to(ROOT)}/`에 `<번호>_<이름>.jpg`로 넣으면 된다 — "
                 "푸시인과 점등은 코드가 입힌다.\n")
        for topic, r, _sub in stills:
            L.append(f"\n## {r['_no']}. `{r['name']}` — {topic}\n")
            L.append(f"\n**레퍼런스**: `{r.get('ref') or CANON}` — "
                     f"{r.get('ref_mode') or 'Omni Reference'} / 저장: `{r['_work']}`\n")
            L.append(f"\n<details><summary>왜 필요한가</summary>\n\n{r.get('why', '')}\n\n</details>\n")
            L.append(f"\n### 미드저니\n```\n{r.get('midjourney', '')}\n```\n")
            if r.get("midjourney_alt"):
                L.append("\n<details><summary>막히거나 비례가 어른처럼 나오면 이 문구로</summary>\n\n"
                         f"```\n{r['midjourney_alt']}\n```\n\n</details>\n")

    L.append(f"\n---\n\n# 1부 · 스틸 있음 — Flow만 ({len(ready)}종)\n")
    for topic, r, _sub in ready:
        L.append(f"\n## {r['_no']}. `{r['name']}` — {topic} ({r.get('seconds', 6)}초)\n")
        L.append(f"\n<details><summary>왜 필요한가</summary>\n\n{r.get('why', '')}\n\n</details>\n")
        L.append(f"\n```\n{r.get('flow', '')}\n```\n")

    L.append(f"\n---\n\n# 2부 · 미드저니부터 ({len(todo)}종)\n")
    L.append("\n`act_`는 **Omni Reference**, `m_`는 **Style Reference**"
             "(Omni 금지 — 클로즈업에 전신 인체가 끼어든다).\n")
    L.append("\n뽑은 스틸은 같은 폴더에 `<번호>_<이름>.jpg`로 넣으면 된다.\n")
    for topic, r, sub in todo:
        mode = r.get("ref_mode") or ("Style Reference (⚠️ Omni 금지)" if sub == "mech" else "Omni Reference")
        L.append(f"\n## {r['_no']}. `{r['name']}` — {topic} ({r.get('seconds', 6)}초)\n")
        L.append(f"\n**레퍼런스**: `{r.get('ref') or CANON}` — {mode} / 저장: `{r['_work']}`\n")
        L.append(f"\n<details><summary>왜 필요한가</summary>\n\n{r.get('why', '')}\n\n</details>\n")
        L.append(f"\n### 미드저니\n```\n{r.get('midjourney', '')}\n```\n")
        L.append(f"\n### Flow\n```\n{r.get('flow', '')}\n```\n")

    sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.write_text("".join(L), encoding="utf-8")
    print(f"{sheet.relative_to(ROOT)} — {len(pend)}종 (스틸 있음 {len(ready)} / "
          f"미드저니부터 {len(todo)} / 스틸만 {len(stills)})")
    print(f"  스틸 폴더: {work.relative_to(ROOT)}")
    if todo and (pending_zip := _unopened_deliveries()):
        print(f"\n🚨 아직 안 푼 미드저니 zip {len(pending_zip)}개가 다운로드 폴더에 있다 —"
              " 이것부터 확인해라. 같은 걸 또 뽑으라고 내보내게 된다:")
        for z in pending_zip:
            print(f"   - {z.name}  ({time.strftime('%m-%d %H:%M', time.localtime(z.stat().st_mtime))})")


if __name__ == "__main__":
    main()
