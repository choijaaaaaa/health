#!/usr/bin/env python3
# 미드저니에서 내려받은 묶음을 요청 이름별 폴더로 정리한다.
#
# WHY(2026-09-24): 미드저니 파일명은 프롬프트 앞 60자로 만들어지는데, 이 라이브러리의 프롬프트는
# 앞부분이 전부 같은 정형문("Medical holographic visualization of a single translucent gla…")이라
# **파일명만으로는 어느 요청인지 못 가른다.** 대신 한 번에 돌린 묶음은 **요청 시트 순서대로** 나오므로
# 생성 시각순 = 시트 순서로 맞춘다.
#
# 🚨 순서 가정이 맞는지 **종류(단일 인체 / 미세 클로즈업 / 두 사람 / 그 외)로 검증**한 뒤에만 옮긴다.
# 시트의 act_/m_ 구분과 실제 이미지 종류가 한 칸이라도 어긋나면 중단한다 — 어긋난 채 옮기면
# 엉뚱한 이름이 붙어 나중에 "이름과 내용이 다른 클립"이 또 생긴다(이 라이브러리의 단골 사고).
#
#   .venv/bin/python3 scripts/sort_midjourney_batch.py ~/Downloads/mj_session
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks  # noqa: E402

STILLS = ROOT / "assets_library" / "xray" / "stills"
JOB_RE = re.compile(r"^(?P<prefix>.+)_(?P<uid>[0-9a-f-]{36})_(?P<idx>[0-3])\.png$")


def kind_of(prefix: str) -> str:
    p = prefix.lower()
    if "of_two" in p:
        return "two"
    if "microscopic" in p:
        return "mech"
    if "of_a_single" in p:
        return "act"
    return "other"          # 손으로 쓴 프롬프트 — act로 친다


def pending_requests() -> list[tuple[str, str]]:
    """(topic, 이름) — 시트와 같은 순서(토픽 폴더명 정렬, 파일 안 순서)."""
    lib = ROOT / "assets_library" / "xray" / "output"
    out, seen = [], set()
    # 트랙 폴더(data/육아/…)는 한 단계 깊어서 평평한 글롭에 안 걸린다
    for f in tracks.glob_topic_files(ROOT / "data", "*/clip_requests.json"):
        for r in json.loads(f.read_text(encoding="utf-8")).get("requests", []):
            n = r.get("name")
            if n and n not in seen and not (lib / f"{n}.mp4").exists():
                seen.add(n); out.append((f.parent.name, n))
    return out


def main() -> None:
    src = Path(sys.argv[1]).expanduser()
    jobs: dict[str, dict] = {}
    for p in src.glob("*.png"):
        m = JOB_RE.match(p.name)
        if not m:
            continue
        j = jobs.setdefault(m["uid"], {"kind": kind_of(m["prefix"]), "files": [], "t": p.stat().st_mtime})
        j["files"].append(p)
        j["t"] = min(j["t"], p.stat().st_mtime)
    ordered = sorted(jobs.values(), key=lambda j: j["t"])
    reqs = pending_requests()
    print(f"작업 {len(ordered)}개 / 미수령 요청 {len(reqs)}종\n")

    # 종류 검증 — 시트가 기대하는 종류와 실제가 맞는지 한 칸씩
    plan, mismatch = [], []
    for job, (topic, name) in zip(ordered, reqs):
        want = "mech" if name.startswith("m_") else "act"
        got = job["kind"]
        ok = (got == want) or (want == "act" and got in ("two", "other"))
        plan.append((name, topic, job, ok))
        if not ok:
            mismatch.append((name, want, got))
    for name, topic, job, ok in plan:
        print(f"{'✅' if ok else '❌'} {name:30s} {topic:10s} {job['kind']:6s} {len(job['files'])}장")
    if len(ordered) < len(reqs):
        print(f"\n⚠️ 요청보다 {len(reqs) - len(ordered)}개 모자람 — 뒤쪽 {[n for n, _ in reqs[len(ordered):]]}는 아직 없음")
    if mismatch:
        raise SystemExit(f"\n❌ 종류가 어긋난 칸 {len(mismatch)}개 {mismatch} — 순서 가정이 틀렸다. 옮기지 않는다.")

    for name, _topic, job, _ok in plan:
        sub = "mech" if name.startswith("m_") else "act"
        dest = STILLS / "_candidates" / name
        dest.mkdir(parents=True, exist_ok=True)
        for f in sorted(job["files"]):
            shutil.copy2(f, dest / f"{name}_{f.name[-5]}.png")
    print(f"\n{STILLS / '_candidates'} 아래 요청 이름별로 4장씩 복사했다(원본은 그대로).")
    print("고른 1장을 stills/act/ 또는 stills/mech/ 로 옮기면 Flow 단계로 간다.")


if __name__ == "__main__":
    main()
