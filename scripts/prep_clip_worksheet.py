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
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "assets_library" / "xray" / "output"
STILLS = ROOT / "assets_library" / "xray" / "stills"
WORK = ROOT / "assets_library" / "xray" / "작업" / "1_스틸"
# 🚨 이 세 경로는 고정이다 — 이름을 바꾸지 말 것(2026-09-24 사용자 "이름도 매번바뀌고").
# 시트를 `지금_뽑을것.md`에서 이 이름으로 한 번 바꿨더니, 편집기에 열어둔 파일이
# 사라져서 "내가 뭘 뽑아야 하는지" 자체를 다시 물어야 했다. 정리가 더 낫겠다 싶어도
# 바꾸지 말 것 — tests/test_xray_worksheet_path.py가 막는다.
SHEET = ROOT / "assets_library" / "xray" / "작업" / "0_작업지시.md"
CANON = "assets_library/xray/stills/canon_organs.jpg"
INBOX = ROOT / "assets_library" / "xray" / "작업" / "2_완성클립"


def _pending() -> list[list]:
    out, seen = [], set()
    for f in sorted((ROOT / "data").glob("*/clip_requests.json")):
        topic = f.parent.name
        try:
            reqs = json.loads(f.read_text(encoding="utf-8")).get("requests", [])
        except json.JSONDecodeError:
            continue
        for r in reqs:
            n = r.get("name")
            if not n or n in seen or _done(r):
                continue
            seen.add(n)
            out.append([topic, r, _sub_of(r)])
    return out


def _sub_of(r: dict) -> str:
    """스틸 저장 갈래. 기전은 mech/, 행위·부위는 act/, 스틸만 받는 요청은 stills/ 바로 밑."""
    if r.get("kind") == "still":
        return "still"
    return "mech" if r["name"].startswith("m_") else "act"


def _done(r: dict) -> bool:
    """받은 것으로 볼지 — 영상 요청은 클립이, 스틸 요청은 스틸 자체가 최종 산출물이다.

    WHY(2026-09-24 육아 트랙): 아기 몸이 나오는 장면은 Flow(Veo)에 보내지 않는다. 미성년자
    안전필터가 `infant`/`child` 단어만으로도 막은 전례가 있어서, 아기는 미드저니 정지 스틸로만
    뽑고 카메라 푸시인·점등은 scripts/make_part_clip.py가 코드로 입힌다. 그래서 "Flow 결과
    mp4가 없으면 미완"이라는 기존 판정이 이 요청들엔 영영 참이라 시트에서 안 내려간다."""
    if r.get("kind") == "still":
        return (STILLS / f"{r['name']}.jpg").exists()
    return (LIB / f"{r['name']}.mp4").exists()


def _existing_still(sub: str, name: str) -> Path | None:
    """번호가 붙었든 안 붙었든 그 이름으로 끝나는 스틸을 찾는다."""
    for p in (STILLS if sub == "still" else STILLS / sub).glob(f"*{name}.jpg"):
        return p
    for p in WORK.glob(f"*{name}.jpg"):
        return p
    return None


def main() -> None:
    pend = _pending()
    # 스틸이 있는 것을 앞 번호로 — 바로 Flow만 돌리면 되는 것부터 보이게
    pend.sort(key=lambda x: (_existing_still(x[2], x[1]["name"]) is None, x[0]))
    if WORK.exists():
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    for i, (topic, r, sub) in enumerate(pend, 1):
        src = _existing_still(sub, r["name"])
        r["_no"], r["_work"] = f"{i:02d}", f"{i:02d}_{r['name']}.jpg"
        if src:
            shutil.copy2(src, WORK / r["_work"])

    # 스틸만 받는 요청을 1·2부에 섞으면 "이것도 Flow를 돌려야 하나"가 된다 — 따로 세운다
    stills = [x for x in pend if x[2] == "still"]
    ready = [x for x in pend if x[2] != "still" and (WORK / x[1]["_work"]).exists()]
    todo = [x for x in pend if x[2] != "still" and x not in ready]
    # 맨 위 두 줄이 "내가 지금 뭘 하면 되는지"를 번호로 답해야 한다 — 표까지 읽게 하면
    # "몇번몇번 플로우랑 미드저니 뭐지?"를 또 묻게 된다(2026-09-24).
    span = lambda xs: ("없음" if not xs
                       else "·".join(r["_no"] for _t, r, _s in xs) if len(xs) <= 4
                       else f"{xs[0][1]['_no']}~{xs[-1][1]['_no']}")
    L = [f"# 지금 뽑을 클립 {len(pend)}종\n",
         f"\n## 내가 할 일\n",
         f"\n- **{span(ready)} → Flow만** 돌린다(스틸은 이미 `1_스틸/`에 있다).\n",
         f"- **{span(todo)} → 미드저니 먼저**, 나온 스틸을 `1_스틸/`에 `<번호>_<이름>.jpg`로 넣고 Flow.\n",
         f"- **{span(stills)} → 미드저니만**. **Flow 안 돌린다** — 스틸만 주면 코드가 클립을 만든다.\n",
         f"\n**받은 영상은 `{INBOX.relative_to(ROOT)}/`에 클립 이름 그대로 넣는다**"
         " — 그 뒤 `scripts/collect_clips.py --commit`이 라이브러리로 들인다.\n",
         "\n🚨 Flow는 **start 프레임만** 준다 — end를 주면 Veo가 사이를 맞추려고 피사체를 변형시킨다.\n",
         "\n| # | 이름 | topic | 할 일 |\n|---|---|---|---|\n"]
    for topic, r, sub_ in pend:
        할일 = ("미드저니만(스틸)" if sub_ == "still"
                else "Flow만" if (WORK / r["_work"]).exists() else "미드저니 → Flow")
        L.append(f"| {r['_no']} | `{r['name']}` | {topic} | {할일} |\n")

    if stills:
        L.append(f"\n---\n\n# 0부 · 미드저니만 — 스틸 {len(stills)}장 (Flow 안 돌린다)\n")
        L.append("\n🚨 **이 번호들은 영상을 뽑지 않는다.** 미드저니 스틸 한 장씩만 `1_스틸/`에 "
                 "`<번호>_<이름>.jpg`로 넣으면 된다 — 푸시인과 점등은 코드가 입힌다.\n")
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

    SHEET.write_text("".join(L), encoding="utf-8")
    print(f"{SHEET.relative_to(ROOT)} — {len(pend)}종 (스틸 있음 {len(ready)} / "
          f"미드저니부터 {len(todo)} / 스틸만 {len(stills)})")
    print(f"스틸 폴더: {WORK.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
