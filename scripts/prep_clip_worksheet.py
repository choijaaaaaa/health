#!/usr/bin/env python3
"""아직 못 받은 클립을 통합 작업대(`deploy/작업/만사전.md` + `만사전_스틸/`)의 건강·육아 섹션으로 낸다.

WHY(2026-09-24): 시트에 번호를 붙여놓고 스틸은 `stills/act/`·`stills/mech/`에 원래 이름으로
흩어져 있어 매칭이 안 됐다 — "번호별로 뭔지 그게 중요한건데". 시트 번호와 스틸 파일 앞 번호를
같게 맞추고, act/mech를 가르지 않고 스틸 폴더 한 곳에 모은다.

WHY 섹션인지(2026-10-25 사용자 "건강·육아·댕냥 … 굳이 떨어질 필요가 없을 듯"): 시트는 댕냥사전과 하나로 합쳤다. 이 생성기는
프롬프트·순서만 정해 트랙별 섹션(health·baby)으로 내보내고, 번호 매기기·시트·스틸 사본·manifest는
`ai-video-network/tools/manjeon_sheet.py`가 한다 — 두 저장소 생성기가 서로의 항목을 지우지 않게(`lib/workbench.py`).

결과 영상만 번호 없이 원래 이름으로 저장한다(`<이름>.mp4`) — 조립기가 그 이름으로 찾는다.

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

from lib import tracks, workbench  # noqa: E402
LIB = ROOT / "assets_library" / "xray" / "output"
STILLS = ROOT / "assets_library" / "xray" / "stills"
# 🚨 기본(건강) 트랙의 작업 자리. 이름을 바꾸지 말 것(2026-09-24 사용자 "이름도 매번바뀌고") —
# 시트를 `지금_뽑을것.md`에서 이 이름으로 한 번 바꿨더니 편집기에 열어둔 파일이 사라져서
# "내가 뭘 뽑아야 하는지"를 다시 물어야 했다. tests/test_xray_worksheet_path.py가 막는다.
# 자리는 lib/tracks.py의 work_paths()가 준다 — 건강·육아·댕냥 공용 `deploy/작업/만사전.md`·`만사전_스틸/`.
SHEET, WORK, INBOX = tracks.work_paths(None)
CANON = "assets_library/xray/stills/canon_organs.jpg"


DOWNLOADS = Path.home() / "Downloads"
# 푼 미드저니 zip 기록 — 통합 작업대의 숨은 상태 폴더에 둔다(작업대엔 시트·스틸 폴더만 보이게)
CONSUMED = SHEET.parent / ".만사전" / "받은것_health.json"



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
    CONSUMED.parent.mkdir(parents=True, exist_ok=True)
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
    # 작업대 스틸 폴더는 세 채널 공용이다 — `*<이름>.jpg`로 넓게 찾으면 다른 클립(…_<이름>)까지 걸린다. 정확한 꼴만 본다.
    work = tracks.work_paths(track)[1]
    for p in sorted(work.glob(f"*{name}.jpg")) if work.exists() else []:
        if p.stem == name or re.fullmatch(rf"\d{{2,3}}_{re.escape(name)}", p.stem):
            return p
    return None


def _harvest_loose_stills(pend: list[list], work: Path, track: str | None) -> None:
    """스틸 폴더에 사람이 넣은 스틸 중 stills/에 없는 것을 원본 자리로 건져낸다.

    WHY(2026-09-24): 사람이 넣은 스틸이 라이브러리에 사본이 없으면 시트를 다시 만들 때 "아직 미드저니부터"로
    또 내보낸다. 폴더는 세 채널 공용이라 병합기 manifest로 **이 저장소 몫만** 고른다(`workbench.claim`) —
    댕냥 스틸은 그쪽 받기 스크립트가 가져간다. 복사만 하고 원본은 병합기가 새 번호 사본으로 정리한다.
    """
    if not work.exists():
        return
    want = {r["name"]: sub for _t, r, sub in pend}
    got = workbench.claim()
    for f in got["mine"] + got["unclaimed"]:
        src = Path(f["path"])
        sub = want.get(f["clip"])
        if f["kind"] != "still" or src.suffix != ".jpg" or not sub:
            continue
        # 스틸 자체가 산출물인 요청(아기 캐논 등)은 act/mech로 가르지 않고 트랙 스틸 폴더에 둔다
        dst = (tracks.stills_dir(track) if sub == "still" else STILLS / sub) / f"{f['clip']}.jpg"
        if dst.exists():
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(src, dst)
        except FileNotFoundError:
            # 그 사이 다른 세션 병합기가 새 번호로 이름을 바꿨다 — 다음 판에 다시 건진다
            print(f"  ⚠ {src.name}: 옮겨지는 중이라 이번엔 못 건졌다 — 시트를 한 번 더 만들면 건진다")
            continue
        print(f"  건져냄: {src.name} → {dst.relative_to(ROOT)}")


def main() -> None:
    # 트랙마다 섹션을 따로 낸다 — 병합기가 세 채널 섹션을 한 시트로 합치며 01부터 이어 매긴다
    for track in [None, *tracks.TRACKS]:
        build(track)


def _why(r: dict) -> str:
    return f"<details><summary>왜 필요한가</summary>\n\n{r.get('why', '')}\n\n</details>"


def _mj_item(r: dict, sub: str, refs: dict[str, str], has: bool) -> dict:
    """1부 미드저니 한 칸 — 프롬프트·레퍼런스 설명·접어 둔 대안 문구."""
    mode = r.get("ref_mode") or "Style Reference"
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
    extra = []
    if r.get("midjourney_alt") and not baby:
        extra.append("<details><summary>막히거나 비례가 어른처럼 나오면 이 문구로</summary>\n\n"
                     f"```\n{r['midjourney_alt']}\n```\n\n</details>")
    extra.append(_why(r))
    return {"prompt": prompt, "note": how, "extra": "\n\n".join(extra), "col": "✅ 있음" if has else "뽑기"}


def build(track: str | None) -> None:
    section = tracks.section_of(track)
    pend = _pending(track)
    if not pend:
        # 비어도 섹션은 낸다 — 다 받은 트랙의 옛 항목이 통합 시트에 남지 않게
        workbench.publish(section, [])
        print(f"{section} 섹션 — 0종")
        return
    work = tracks.work_paths(track)[1]
    # 🚨 미드저니가 필요한 것을 앞으로 몬다(2026-09-26 사용자 "몇 번을 말해 미드저니를 위쪽으로 몰아서 쫙 뽑게 하라니까").
    # 사람은 미드저니를 한 번에 다 뽑고 → 세션이 확인·정리 → Flow를 한 번에 돈다. 병합기도 같은 원칙으로 세 채널을 세운다.
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
    srcs = {r["name"]: _existing_still(sub, r["name"], track) for _t, r, sub in pend}
    # 스틸만 받는 요청은 언제나 1부(미드저니), 영상 요청은 스틸이 없을 때만 1부를 거친다
    need_mj = [x for x in pend if x[2] == "still" or not srcs[x[1]["name"]]]
    refs = _mj_refs() if need_mj else {}
    items = []
    for topic, r, sub in pend:
        src = srcs[r["name"]]
        items.append({
            "clip": r["name"], "topic": topic, "start": str(src) if src else None,
            "mj": _mj_item(r, sub, refs, bool(src)) if (sub == "still" or not src) else None,
            # 스틸만 받는 요청을 Flow에 섞으면 "이것도 Flow를 돌려야 하나"가 된다 — flow를 비워 2부에서 뺀다
            "flow": None if sub == "still" else {"prompt": r.get("flow", ""), "sec": r.get("seconds", 6), "extra": _why(r)},
            "meta": {"kind": sub},
        })
    workbench.publish(section, items)
    n_still = sum(1 for x in pend if x[2] == "still")
    n_todo = sum(1 for x in pend if x[2] != "still" and not srcs[x[1]["name"]])
    print(f"{section} 섹션 — {len(pend)}종 (스틸 있음 {len(pend) - n_still - n_todo} / "
          f"미드저니부터 {n_todo} / 스틸만 {n_still})")
    if n_todo and (pending_zip := _unopened_deliveries()):
        print(f"\n🚨 아직 안 푼 미드저니 zip {len(pending_zip)}개가 다운로드 폴더에 있다 —"
              " 이것부터 확인해라. 같은 걸 또 뽑으라고 내보내게 된다:")
        for z in pending_zip:
            print(f"   - {z.name}  ({time.strftime('%m-%d %H:%M', time.localtime(z.stat().st_mtime))})")


if __name__ == "__main__":
    main()
