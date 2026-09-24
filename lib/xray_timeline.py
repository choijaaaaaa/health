# 반투명 인체 포맷의 항목·기전 시간표 — xray.json의 "timeline"(구절 → 항목·기전 클립)을 실제 나레이션 시각으로 푼다.
# WHY 추정 대신 명시인지(2026-09-19): 기존 rebuild_video.build_motion_schedule은 문단 안 키워드 위치로 항목
# 전환 시각을 추정하는데, 한 문장에 두 항목이 같이 나오는 해결책 문장("카페인은 …, 진통제는 …")에서 순서가
# 뒤집혔다(커피→소금→이부프로펜). 새 포맷은 칠판 항목 라벨과 위쪽 영상 칸(기전 클립)이 같은 시각에 바뀌어야
# 하므로, topic 작성 때 구절 단위로 적어두고 두 곳이 이 표 하나를 따르게 한다.
from __future__ import annotations

import json
import re
from pathlib import Path

from lib import tracks

ROOT = Path(__file__).resolve().parent.parent
_TS = re.compile(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)")


def _cues(topic: str) -> list[tuple[float, float, str]]:
    srt = next(tracks.output_dir(topic).glob("*narration.srt"))
    out = []
    for block in srt.read_text(encoding="utf-8").strip().split("\n\n"):
        ls = block.strip().split("\n")
        m = _TS.match(ls[1]) if len(ls) >= 3 else None
        if m:
            g = [int(x) for x in m.groups()]
            out.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
                        g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, " ".join(ls[2:])))
    return out


def _time_of(phrase: str, cues) -> float:
    """구절이 들어 있는 자막 구간을 찾고, 구간 안 글자 위치 비율로 시각을 잡는다(공백 제외 글자 수 ∝ 발화 시간)."""
    for s, e, text in cues:
        k = text.find(phrase)
        if k >= 0:
            before = len(re.sub(r"\s", "", text[:k]))
            total = len(re.sub(r"\s", "", text)) or 1
            return s + (e - s) * before / total
    raise ValueError(f"xray.json timeline 구절을 자막에서 못 찾음: {phrase!r}")


def resolve(topic: str) -> list[dict] | None:
    """[{start, end, item, mech, act}] (나레이션 기준 초). timeline이 없으면 None.

    WHY `act`도 같이 내보내는지(2026-09-24 실측): 위쪽 칸은 **왼쪽 행위 · 오른쪽 기전**으로 나뉘는데,
    이 함수가 act를 떼고 돌려주는 바람에 topic이 timeline에 act를 적어도 xray_build가 못 받아
    기전만 크게 나갔다 — 항목마다 행위를 넣을 자리가 아예 없는 것처럼 보였다."""
    path = tracks.data_dir(topic) / "xray.json"
    if not path.exists():
        return None
    tl = json.loads(path.read_text(encoding="utf-8")).get("timeline")
    if not tl:
        return None
    cues = _cues(topic)
    starts = [_time_of(t["from"], cues) for t in tl]
    end_all = cues[-1][1]
    return [{"start": st, "end": starts[i + 1] if i + 1 < len(starts) else end_all,
             "item": t["item"], "mech": t.get("mech"), "act": t.get("act"),
             # `label`도 같이 — act 때와 똑같은 구멍이었다. 여기서 떼면 topic이 구간마다 부위
             # 이름을 적어둬도 조립기엔 안 가고 전부 inset 라벨 하나로 떨어진다(2026-09-24 실측).
             "label": t.get("label")}
            for i, (st, t) in enumerate(zip(starts, tl))]


def summary_start(topic: str) -> float | None:
    """해결책·요약 구간이 시작하는 시각(초). xray.json의 summary_from 구절 기준, 없으면 None.

    WHY(2026-09-20 사용자 "제품 보러 가기는 마지막 써머리 때만"): CTA 화살표를 이 시각부터만 띄운다."""
    path = tracks.data_dir(topic) / "xray.json"
    if not path.exists():
        return None
    phrase = json.loads(path.read_text(encoding="utf-8")).get("summary_from")
    if not phrase:
        return None
    try:
        return _time_of(phrase, _cues(topic))
    except (ValueError, StopIteration):
        return None
