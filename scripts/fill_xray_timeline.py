#!/usr/bin/env python3
"""xray.json의 timeline을 나레이션 구조에서 자동으로 채운다.

WHY(2026-09-23): 이 포맷은 "먼저 / 두 번째로는 / 마지막으로"로 항목이 갈리도록 원고를 쓴다
(SCRIPT_V2_GUIDE.md). 그 구절이 곧 항목 전환 지점이라 손으로 옮겨 적을 이유가 없다 —
틀리면 칠판 라벨과 위쪽 기전 영상이 딴 시각에 바뀐다.

`_mech`(항목별 기전 클립)와 `_items`(칠판 왼쪽 품목)는 원고를 쓴 에이전트가 미리 적어둔 값이다.
해결책 문단은 항목 순서를 한 번 더 훑도록 같은 세 쌍을 되풀이해 붙인다.

⚠️ 구절은 **자막에 있는 그대로**여야 한다(`lib/xray_timeline._time_of`가 문자열 검색을 한다).
그래서 나레이션 원문에서 문장 앞부분을 잘라 쓴다.

    python3 scripts/fill_xray_timeline.py <topic> [...]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEAD = ("먼저", "두 번째로는", "두번째로는", "마지막으로")


def _phrase(line: str, words: int = 3) -> str:
    """문장 앞 몇 어절 — 자막 한 줄 안에서 유일하게 찾히도록 짧게 쓴다."""
    return " ".join(line.split()[:words])


def _cue_lines(topic: str) -> list[str]:
    """자막 줄 원문. ⚠️ 나레이션 원문에서 구절을 뽑으면 자막 줄 경계를 넘어가 못 찾는다
    (2026-09-23 실측: "먼저 단백질이에요. 콜라겐이"가 자막에선 두 줄로 갈려 있었다).
    자막이 있으면 거기서 뽑아야 `_time_of`의 문자열 검색이 반드시 맞는다."""
    d = ROOT / "output" / topic
    srt = next(iter(sorted(d.glob("*narration.srt"))), None) if d.is_dir() else None
    if not srt:
        return []
    out = []
    for block in srt.read_text(encoding="utf-8").strip().split("\n\n"):
        ls = block.strip().split("\n")
        if len(ls) >= 3:
            out.append(" ".join(ls[2:]).strip())
    return out


def fill(topic: str) -> str:
    path = ROOT / "data" / topic / "xray.json"
    cfg = json.loads(path.read_text(encoding="utf-8"))
    lines = _cue_lines(topic)
    if not lines:
        nar = next(p for p in (ROOT / "data" / topic / "narration.txt",
                               ROOT / "data" / topic / "ko" / "narration.txt") if p.exists())
        lines = [l.strip() for l in nar.read_text(encoding="utf-8").splitlines() if l.strip()]

    mech, items = cfg.get("_mech") or [], cfg.get("_items") or []
    if len(mech) < 3 or len(items) < 3:
        return f"{topic}: _mech/_items가 3개 미만이라 건너뜀"

    starts = [l for l in lines if l.startswith(LEAD)]
    if len(starts) < 3:
        return f"{topic}: '먼저/두 번째로는/마지막으로' 문단을 {len(starts)}개만 찾음 — 원고 구조 확인 필요"

    tl = [{"from": _phrase(starts[i]), "item": items[i], "mech": mech[i]} for i in range(3)]

    # 해결책 문단(세 항목 뒤 본문)에서도 항목이 한 번씩 더 지나가게 한다 — 칠판 사진이 결론에서 멈춰 있지 않도록.
    tail = lines[lines.index(starts[2]) + 1:]
    extra = [l for l in tail if not l.startswith(LEAD)][-2:]
    for i, l in enumerate(extra):
        tl.append({"from": _phrase(l), "item": items[i % 3], "mech": mech[i % 3]})
    if extra:
        cfg["summary_from"] = _phrase(extra[0])

    cfg["timeline"] = tl
    cfg.setdefault("opening_until", None)
    path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"{topic}: timeline {len(tl)}구간 — " + " / ".join(t["from"] for t in tl[:3])


if __name__ == "__main__":
    for t in sys.argv[1:]:
        print(fill(t))
