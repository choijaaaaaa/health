#!/usr/bin/env python3
"""xray topic 전체를 한 번에 검사한다 — 조립·발행 전에 이것부터 돌린다.

WHY(2026-09-24): 사용자가 영상을 보고 하나씩 짚어주는 방식으로 하루를 보냈다. 지적받은 것들을
그때그때 고치기만 하면 **다음 topic에서 같은 게 또 나온다.** 그래서 지적 하나하나를 검사로
바꿔 전체에 돌린다. 여기서 0건이 나와야 조립할 자격이 있다.

    .venv/bin/python3 scripts/preflight_xray.py            # 전체
    .venv/bin/python3 scripts/preflight_xray.py 비뇨기_16   # 하나만
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import content_review as cr          # noqa: E402
from lib import tracks                       # noqa: E402
from lib.xray_timeline import resolve         # noqa: E402

# 축마다 "무엇을 막는 검사인지"를 적어둔다 — 경고만 보고는 왜 걸렸는지 모른다.
CHECKS = [
    (cr.check_xray_timeline_resolves, "시간표 구절이 지금 자막에 있는가(원고를 고치고 시간표를 안 고침)"),
    (cr.check_xray_pacing,            "도입부가 문장을 자르지 않는가 / 칸이 8초 넘게 비지 않는가 / 도입부 안에 칸이 겹치지 않는가"),
    (cr.check_summary_single_block,   "결론 구간이 여러 행으로 쪼개져 품목만 바뀌지 않는가"),
    (cr.check_mech_variety,           "같은 기전 클립을 3번 이상 돌려쓰지 않는가(정지 이미지로 보인다)"),
    (cr.check_act_coverage,           "설명 구간마다 행위 클립이 붙어 있는가(왼쪽 행동·오른쪽 기전)"),
    (cr.check_plain_language,         "수치 없이 기관명만 붙이거나 전문용어를 설명 없이 던지지 않는가"),
    (cr.check_card_narration_alignment, "카드가 지금 나레이션과 같은 이야기를 하는가"),
    (cr.check_xray_clips,             "참조한 클립이 실제로 있는가 / 미수령 요청이 남았는가"),
    (cr.check_content_depth,          "수치·통념 반박·병원 신호가 있는가, 길이가 맞는가"),
    (cr.check_search_keyword,         "제목이 검색어로 시작하는가"),
]


def labels_missing(topic: str) -> int:
    try:
        return sum(1 for r in resolve(topic) or [] if not r.get("label"))
    except Exception:
        return 0


def main() -> None:
    # topic 이름은 평평하게 — 트랙은 경로에만 있고 이름에는 없다
    topics = sys.argv[1:] or sorted(
        p.parent.name for p in tracks.glob_topic_files(ROOT / "data", "*/xray.json"))
    total = 0
    for t in topics:
        found = []
        for fn, _why in CHECKS:
            try:
                found += fn(t)
            except Exception as e:
                found.append({"severity": "high", "issue": f"{fn.__name__} 실행 실패: {e}"})
        n = labels_missing(t)
        if n:
            found.append({"severity": "medium", "issue": f"부위 라벨이 빈 구간 {n}개 — 전 구간이 한 이름으로 고정된다"})
        # 미수령 클립은 사람이 렌더해야 하는 것이라 따로 센다(고칠 수 있는 문제가 아니다)
        pend = [i for i in found if "안 받은 클립" in i["issue"]]
        # 🚨 이미 음성을 뽑아둔 topic은 **길이 초과로 막지 않는다.** 고치려면 원고를 줄이고
        # TTS를 다시 불러야 하는데, 이 프로젝트는 "길이가 마음에 안 들어서 다시 뽑는 것"을
        # 금지한다(글자수 과금, CLAUDE.md "TTS 재생성 기준"). 87초짜리 2초 때문에 돈을 쓰게
        # 하는 검사가 된다 — 다음 원고를 쓸 때 미리 맞추라는 뜻이지 이미 뽑은 걸 다시 뽑으라는
        # 뜻이 아니다. 음성이 아직 없는 topic에서는 그대로 막힌다(그때가 고칠 수 있는 때다).
        spoken = (ROOT / "output" / t / "narration.mp3").is_file()
        pend += [i for i in found
                 if spoken and "나레이션이 실측" in i["issue"] and i not in pend]
        real = [i for i in found if i not in pend]
        total += len(real)
        mark = "✅" if not real else "⚠️"
        tail = f"  (클립 대기 {len(pend)})" if pend else ""
        print(f"{mark} {t:12s} {len(real)}건{tail}")
        for i in real:
            print(f"      · {i['issue'][:96]}")
    print(f"\n고칠 지적 합계 {total}건" + (" — 조립해도 된다" if total == 0 else " — 고치고 조립할 것"))
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
