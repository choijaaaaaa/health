#!/usr/bin/env python3
"""아직 못 받은 클립을 **스틸까지 한 폴더에 번호순으로 모아** 작업 시트로 낸다.

WHY(2026-09-24): 시트에 번호를 붙여놓고 스틸은 `stills/act/`·`stills/mech/`에 원래 이름으로
흩어져 있어 매칭이 안 됐다 — "번호별로 뭔지 그게 중요한건데". 시트 번호와 스틸 파일 앞 번호를
같게 맞추고, act/mech를 가르지 않고 `작업/스틸/` 한 곳에 모은다.

결과 영상만 번호 없이 원래 이름으로 저장한다(`RENDER/<이름>.mp4`) — 조립기가 그 이름으로 찾는다.

    .venv/bin/python3 scripts/prep_clip_worksheet.py
"""
from __future__ import annotations

import datetime as dt
import json
import re
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
# 트랙별 자리는 lib/tracks.py의 work_paths()가 준다(deploy/작업/ 안에 건강만사전.md·육아만사전.md).
SHEET, WORK, INBOX = tracks.work_paths(None)
CANON = "assets_library/xray/stills/canon_organs.jpg"


DOWNLOADS = Path.home() / "Downloads"
CONSUMED = SHEET.parent / ".받은것_건강만사전.json"



def _mj_refs() -> dict[str, str]:
    from lib.mj_refs import all_refs
    return all_refs()


def _with_ref(prompt: str, ref: str, mode: str, refs: dict[str, str]) -> str:
    """레퍼런스 이미지를 DB의 공개 URL로 프롬프트 안에 박는다(`--sref <url>`).

    WHY(2026-09-29 사용자 "canon organs나 댕냥사전 이미지같은것들도 내가 일일히 넣지않고 너가 db에 넣은 상태로 프롬프트에
    링크 넣으라고 했자나"): 시트가 "레퍼런스: assets_library/…/canon_organs.jpg"처럼 로컬 경로만 적어 사용자가 매번 파일을
    찾아 첨부했다. 댕냥사전 build_work_sheet._with_sref와 같은 방식 — `--no` 목록은 다음 `--`까지 이어지므로 그 앞에 넣는다."""
    from lib.mj_refs import ensure
    rel = ref.split("assets_library/xray/", 1)[-1]
    try:
        url = ensure(rel, refs)
    except FileNotFoundError:
        # 레퍼런스 자체가 같은 시트에서 먼저 뽑을 스틸(육아 baby_canon_organs 등)이면 아직 파일이 없다 —
        # 시트를 못 만들고 멈추지 말고, 그 스틸이 들어온 뒤 시트를 다시 만들면 링크가 박힌다(비율은 지금도 박는다)
        return prompt if "--ar " in prompt else f"{prompt.split(' --', 1)[0].rstrip()} --ar 9:16" + (" --" + prompt.split(" --", 1)[1] if " --" in prompt else "")
    # 댕냥사전 시트와 같은 꼴 "본문 --ar 9:16 --sref <url> --no …"(2026-09-29 사용자 "ref 구문이 앞으로 가야 하는 것 같다,
    # 9:16이 설정된 16:9로 나온다") — 본문 속 "vertical 9:16"은 비율 파라미터가 아니라 계정 기본값(16:9)으로 나왔다.
    # 전부 --sref(Style Reference). WHY(2026-09-29 사용자 "--sref가 맞네… oref 할 때 옴니로 들어가서 개판으로 출력"):
    # Omni는 캐논의 모양·자세까지 따라 하려다 장면이 뒤틀린다. 반투명 캐논은 질감·색만 따르면 된다(댕냥사전과 같은 결론).
    tag = f"--sref {url}"
    # 🚨 아기가 나오는 스틸은 아기 캐논을 --oref로(2026-09-30 사용자 "애기 이미지 기준으로… db에 올리고 그걸 참조해야
    # 하지 않겠냐? 프롬프트 쳐서 넣고 있는데 잘 안 나온다"): --sref는 질감·색만 따라가 몸 비례가 어른으로 나왔다.
    # 아기 몸 비례는 모양 참조(Omni)라야 고정된다 — Omni는 V7 전용이라 --v 7도 같이.
    baby = Path(ref).stem.startswith("baby_")
    if baby:
        # 🚨 아기 장면은 성인 캐논 --sref(화풍)만 + 직접 표현 문구(2026-09-30 세 번 시험한 결론):
        #  ① --sref만+돌려 말한 문구 → 어른 비례  ② --oref(아기 캐논)만 → 비례는 잡혔는데 회색 스튜디오·유리 상자·어른 얼굴
        #  ③ --oref+--sref → 화풍은 돌아왔지만 캐논의 "정면 전신" 구도로 끌려가 트림 장면이 선 아기+전신 어른이 됐다.
        # 모양 참조(Omni)는 캐논 구도까지 끌고 오니 장면용으론 못 쓴다. 비례는 직접 표현 문구가, 화풍은 --sref가 맡는다.
        style = ensure("stills/canon_organs.jpg", refs)
        tag = f"--sref {style}"
        # "3D anatomical model(s)"이 박물관 진열 모형으로 읽혀 유리 상자가 계속 생겼다
        prompt = re.sub(r"3D anatomical models?", "hologram figures" if "two" in prompt[:120] else "hologram figure", prompt)
    body = prompt.split(" --", 1)[0].rstrip().rstrip(",")
    no = " --no " + prompt.split(" --no ", 1)[1] if " --no " in prompt else " --no text, letters, numbers, labels, arrows, watermark, logo"
    if baby:
        body = body.rstrip(".") + (". The frame is cropped so the adult's head and face are entirely outside it —"
                 " only the adult's hands, arms and at most a shoulder are visible." if "two " in body[:120] else ".")
        no += (", glass box, display case, museum model, container, pedestal, grey backdrop, studio floor, floor reflection,"
               " adult head, adult face, adult full body, skin-colored body, opaque skin, doll")
    return f"{body} --ar 9:16 {tag}{no}"

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
    clip = LIB / f"{r['name']}.mp4"
    # "redo": "<ISO 시각>" — 받은 클립이 요청과 달라 다시 뽑는 중. 그 시각 뒤에 새 클립이 들어오기 전까진
    # 시트에 남긴다(2026-09-25 act_full_belly_refuse_water: 물을 밀어내야 하는데 꿀꺽 마셔서 재요청했는데,
    # 라이브러리에 옛 클립이 있다는 이유로 시트에서 빠져 프롬프트를 찾을 데가 없었다).
    if r.get("redo"):
        return clip.exists() and dt.datetime.fromtimestamp(clip.stat().st_mtime) > dt.datetime.fromisoformat(r["redo"])
    return clip.exists()


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
    """스틸 폴더에만 있고 stills/에는 없는 스틸을 먼저 원본 자리로 옮긴다.

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
    if not pend:
        # 비어도 파일은 둔다 — 사람이 deploy/작업/을 열었을 때 "이 브랜드는 할 게 없다"가 바로 보이게
        sheet.parent.mkdir(parents=True, exist_ok=True); work.mkdir(parents=True, exist_ok=True)
        sheet.write_text("# 지금 뽑을 클립 없음\n\n요청이 생기면 이 파일이 번호순 작업지시로 바뀐다.\n", encoding="utf-8")
        print(f"{sheet.relative_to(ROOT.parent)} — 0종")
        return
    # 번호는 시트에 실리는 차례(0부 스틸 → 1부 Flow만 → 2부 미드저니부터)와 같아야 한다.
    # 안 그러면 "01~09 미드저니 먼저 / 03~11 스틸만"처럼 구간이 겹쳐 무엇부터 할지 알 수 없다.
    # 🚨 미드저니가 필요한 번호를 앞(01~)으로 몬다(2026-09-26 사용자 "몇 번을 말해 미드저니를 위쪽으로 몰아서
    # 쫙 뽑게 하라니까"). 사람은 미드저니를 한 번에 다 뽑고 → 세션이 확인·정리 → Flow를 한 번에 돈다.
    # 🚨 다른 요청의 레퍼런스가 되는 스틸(육아 baby_canon_organs 등)을 맨 앞에, 아직 없는 레퍼런스를 쓰는 스틸을
    # 그 뒤로(2026-09-30): 순서가 섞이자 1번부터 링크 없는 프롬프트가 나와 32칸이 레퍼런스 없이 뽑힐 뻔했다.
    ref_names = {Path(r.get("ref") or "").stem for _t, r, _s in pend}
    def order(x):
        _topic, r, sub = x
        if sub == "still":
            ref_missing = bool(r.get("ref")) and not (ROOT / r["ref"]).exists()
            return (0, 0 if r["name"] in ref_names else (2 if ref_missing else 1), _topic)
        return (2 if _existing_still(sub, r["name"], track) else 1, 0, _topic)

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
        else:
            # 🚨 스틸이 없는 항목은 폴더를 **빈자리로 두지 않는다**(2026-09-24): "스틸 다
            # 모아놨다"는 말만 믿고 열었다가 파일이 없어 헛걸음했다. 왜 없는지, 뭘 하면
            # 되는지를 그 자리에 적어둔다.
            (work / f"{i:02d}_{r['name']}_스틸없음.txt").write_text(
                f"{r['name']} — 스틸이 아직 없습니다.\n\n"
                f"{sheet.name}의 {i:02d}번에 미드저니 프롬프트가 있습니다.\n"
                f"그걸로 이미지를 뽑아 이 폴더에 `{i:02d}_{r['name']}.jpg` 로 넣어주세요.\n"
                f"(이 쪽지는 지워도 됩니다)\n", encoding="utf-8")

    # 스틸만 받는 요청을 1·2부에 섞으면 "이것도 Flow를 돌려야 하나"가 된다 — 따로 세운다
    stills = [x for x in pend if x[2] == "still"]
    ready = [x for x in pend if x[2] != "still" and (work / x[1]["_work"]).exists()]
    todo = [x for x in pend if x[2] != "still" and x not in ready]
    # 맨 위가 "지금 뭘 하면 되는지"를 번호로 답해야 한다. 미드저니는 전부 1부에 몰고, Flow는 전부 2부에 몬다 —
    # 한 항목 안에 미드저니·Flow를 같이 두면 미드저니를 뽑으려고 Flow 프롬프트 사이를 헤집어야 했다.
    mj = stills + todo                     # 미드저니가 필요한 것(번호 01부터 연속)
    flow = todo + ready                    # Flow를 돌릴 것(미드저니 확인이 끝난 뒤)
    flow.sort(key=lambda x: x[1]["_no"])
    span = lambda xs: ("없음" if not xs
                       else "·".join(r["_no"] for _t, r, _s in xs) if len(xs) <= 4
                       else f"{xs[0][1]['_no']}~{xs[-1][1]['_no']}")
    folder = work.relative_to(ROOT.parent)
    # 끝난 단계는 안 남긴다(2026-09-27 "미드저니도 다뽑았으면 없어져도되잖아") — 미드저니가 0장이면 Flow만 적는다
    steps = ([f"\n1. **미드저니 {span(mj)} — 1부를 위에서부터 쫙 뽑는다.** 결과는 `{folder}/`에 넣거나 zip째 다운로드 폴더에 둔다.\n",
              "2. **세션에 말한다** — 세션이 확인·분류해서 번호 이름으로 정리하고 이 시트를 다시 만든다.\n",
              f"3. **Flow {span(flow)} — 2부를 쫙 돌린다.** 같은 번호 스틸을 start 프레임으로만 넣는다(end 비움).\n"]
             if mj else
             [f"\n1. **Flow {span(flow)} — 아래를 쫙 돌린다.** 같은 번호 스틸을 start 프레임으로만 넣는다(end 비움).\n"])
    L = [f"# 지금 뽑을 것 {len(pend)}종" + (f" — {track} 트랙" if track else "") + "\n",
         "\n## 내가 할 일 (이 순서대로)\n", *steps,
         f"   결과 mp4는 `{folder}/`에 클립 이름 그대로 넣거나 다운로드 폴더에 둔다.\n",
         "\n| # | 이름 | topic | 미드저니 | Flow |\n|---|---|---|---|---|\n"]
    for topic, r, sub_ in pend:
        has = (work / r["_work"]).exists()
        L.append(f"| {r['_no']} | `{r['name']}` | {topic} | {'✅ 있음' if has else '뽑기'} | "
                 f"{'— (스틸만)' if sub_ == 'still' else '돌리기'} |\n")

    if mj:
        L.append(f"\n---\n\n# 1부 · 미드저니 — {len(mj)}장 쫙 먼저\n")
        L.append("\n레퍼런스는 전부 **Style Reference**(`--sref`, 프롬프트 안 링크) — Omni는 모양까지 따라 해 장면이 뒤틀린다. "
                 "저장 이름은 번호마다 적혀 있다.\n")
    refs = _mj_refs() if mj else {}
    for topic, r, sub in mj:
        mode = r.get("ref_mode") or "Style Reference"
        tag = " · 🖼 스틸만(Flow 없음)" if sub == "still" else ""
        L.append(f"\n## {r['_no']}. `{r['name']}` — {topic}{tag}\n")
        # 아기 스틸은 직접 표현 문구(midjourney_alt)가 먼저 — 돌려 말한 기본 문구로는 어른 비례가 나왔다(2026-09-30 실측)
        baby = (Path(r.get('ref') or '').stem.startswith("baby_") or r["name"].startswith("baby_")) and r.get("midjourney_alt")
        if r.get("style") == "real":
            # 일반 사진풍 요청(속이 보일 필요 없는 아이 행위 장면)엔 반투명 캐논 --sref를 붙이면 다시 엑스레이로 끌려간다
            # (2026-10-04 사용자 "그냥 엑스레이사진을 안 하면 되지") — 비율만 박는다
            raw = r.get('midjourney', '')
            body, no = raw.split(" --no ", 1) if " --no " in raw else (raw, "text, letters, numbers, labels, watermark, logo")
            prompt = f"{body.split(' --', 1)[0].rstrip()} --ar 9:16 --no {no}"
        else:
            prompt = _with_ref(r["midjourney_alt"] if baby else r.get('midjourney', ''), r.get('ref') or CANON, mode, refs)
        how = "레퍼런스 없음 — 일반 사진풍(엑스레이 아님)" if r.get("style") == "real" else (f"레퍼런스는 프롬프트 안에 링크로 들어 있다({'Omni — 아기 몸 비례 고정' if '--oref' in prompt else 'Style'})" if "ref https://" in prompt
               else f"레퍼런스 `{Path(r.get('ref') or CANON).name}`는 아직 없다 — 먼저 뽑는 번호 결과가 들어오면 시트를 다시 만들어 링크를 박는다")
        L.append(f"\n저장: `{r['_work']}` · {how}\n")
        L.append(f"\n```\n{prompt}\n```\n")
        if r.get("midjourney_alt") and not baby:
            L.append("\n<details><summary>막히거나 비례가 어른처럼 나오면 이 문구로</summary>\n\n"
                     f"```\n{r['midjourney_alt']}\n```\n\n</details>\n")
        L.append(f"\n<details><summary>왜 필요한가</summary>\n\n{r.get('why', '')}\n\n</details>\n")

    L.append(f"\n---\n\n# 2부 · Flow — {len(flow)}개 (미드저니 확인 끝난 뒤)\n")
    L.append("\n🚨 **start 프레임만** 준다 — end를 주면 Veo가 사이를 맞추려고 피사체를 변형시킨다.\n")
    for topic, r, _sub in flow:
        wait = "" if (work / r["_work"]).exists() else " · ⏳ 1부 스틸 먼저"
        L.append(f"\n## {r['_no']}. `{r['name']}` — {topic} ({r.get('seconds', 6)}초){wait}\n")
        L.append(f"\n스틸: `{r['_work']}`\n\n```\n{r.get('flow', '')}\n```\n")
        L.append(f"\n<details><summary>왜 필요한가</summary>\n\n{r.get('why', '')}\n\n</details>\n")

    sheet.parent.mkdir(parents=True, exist_ok=True)
    sheet.write_text("".join(L), encoding="utf-8")
    print(f"{sheet.relative_to(ROOT.parent)} — {len(pend)}종 (스틸 있음 {len(ready)} / "
          f"미드저니부터 {len(todo)} / 스틸만 {len(stills)})")
    print(f"  스틸 폴더: {work.relative_to(ROOT.parent)}")
    if todo and (pending_zip := _unopened_deliveries()):
        print(f"\n🚨 아직 안 푼 미드저니 zip {len(pending_zip)}개가 다운로드 폴더에 있다 —"
              " 이것부터 확인해라. 같은 걸 또 뽑으라고 내보내게 된다:")
        for z in pending_zip:
            print(f"   - {z.name}  ({time.strftime('%m-%d %H:%M', time.localtime(z.stat().st_mtime))})")


if __name__ == "__main__":
    main()
