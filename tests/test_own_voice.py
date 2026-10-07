# lib/own_voice.py 정렬 테스트 — 인식 결과가 대본과 조금 달라도(오인식·띄어쓰기) 대본 단어마다 시각이 붙는지
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib.own_voice import align  # noqa: E402


def test_align_keeps_script_words_and_times_despite_misrecognition():
    # "자꾸"를 "학구"로 잘못 들은 실측(2026-10-07 피부_31 시험) — 자막은 대본 낱말, 시각은 녹음에서
    words = [{"text": "정강이가", "start": 0.0, "end": 0.8}, {"text": "학구", "start": 0.9, "end": 1.3},
             {"text": "긁게", "start": 1.4, "end": 1.9}, {"text": "돼요.", "start": 2.0, "end": 2.5}]
    out = align("정강이가 자꾸 긁게 돼요.", words)
    assert [w["text"] for w in out] == ["정강이가", "자꾸", "긁게", "돼요."]
    assert out[0]["start"] == 0.0 and out[-1]["end"] == 2.5
    assert out[0]["end"] <= out[1]["start"] <= out[2]["start"] <= out[3]["start"]

