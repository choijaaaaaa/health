# lib/typecast_tts.py의 오디오 처리 로직 테스트. WHY: 실제 유료 API(Typecast)는 절대
# 호출하지 않고, _call_tts()가 반환할 법한 오디오 바이트+단어 타임스탬프를 직접
# 합성해서 그 이후 순수 ffmpeg 가공 로직(_insert_sentence_pauses 등)만 검증한다.
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.typecast_tts import (  # noqa: E402
    SENTENCE_GAP_MS,
    _insert_sentence_pauses,
    _pick_segment_voices,
    _voice_lang_from_topic,
    _voice_pool,
)


def _make_tone(path: Path, duration: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration}",
         "-ar", "24000", "-ac", "1", str(path)],
        check=True, capture_output=True,
    )


def _probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def test_last_sentence_tail_is_not_clipped(tmp_path):
    """회귀: 마지막 문장의 실제 오디오가 단어 타임스탬프 end보다 더 길게(여운) 남아있어도
    잘리지 않고 그대로 살아있어야 한다(2026-08-02, "TTS 마지막에 뚝뚝 끊긴다" 버그)."""
    src_path = tmp_path / "src.wav"
    source_duration = 3.0
    _make_tone(src_path, source_duration)
    audio_bytes = src_path.read_bytes()

    # 마지막 단어의 timestamp end(2.5s)가 실제 오디오 길이(3.0s)보다 짧다 —
    # 타입캐스트가 여운을 타임스탬프에 반영 안 하는 상황을 흉내낸다.
    words = [
        {"text": "안녕.", "start": 0.0, "end": 1.0},
        {"text": "반가워.", "start": 1.0, "end": 2.5},
    ]

    out_bytes, new_words = _insert_sentence_pauses(audio_bytes, "wav", words)

    out_path = tmp_path / "out.wav"
    out_path.write_bytes(out_bytes)
    out_duration = _probe_duration(out_path)

    # 고쳐지기 전엔 seg0(1.0s) + gap + seg1(1.5s, 1.0~2.5로 잘림) ≈ 2.82s로 끝났다.
    # 고친 뒤엔 마지막 구간이 원본 끝(3.0s)까지 살아있어야 하므로
    # seg0(1.0s) + gap(0.32s) + seg1(2.0s, 1.0~3.0) ≈ 3.32s가 나와야 한다.
    expected_min = 1.0 + (SENTENCE_GAP_MS / 1000) + (source_duration - 1.0) - 0.1
    assert out_duration >= expected_min, (
        f"마지막 문장 꼬리가 잘린 것으로 보임: out_duration={out_duration:.2f}s, "
        f"기대 최소값={expected_min:.2f}s"
    )

    # 단어 타임스탬프(SRT용)는 문장 사이 무음 간격(cursor)만 반영해서 밀리는 게
    # 기존 정상 동작이다 — 오디오 꼬리를 살리는 이번 수정이 이 계산 자체를 바꾸면 안 됨.
    expected_last_word_end = 1.0 + (SENTENCE_GAP_MS / 1000) + (2.5 - 1.0)
    assert abs(new_words[-1]["end"] - expected_last_word_end) < 1e-6


def test_pick_segment_voices_uses_korean_pool_by_default():
    """회귀 방지: lang을 안 주면 기존처럼 한국어 보이스 풀에서 골라야 한다."""
    kor_names = {v["name"] for v in _voice_pool("kor")[0]}
    picked = _pick_segment_voices(3)
    assert set(picked) <= kor_names


def test_pick_segment_voices_uses_language_specific_pool():
    """회귀: --multi-voice로 영어 topic을 돌리면 한국어 보이스가 아니라 영어 보이스
    풀에서 골라야 한다(2026-08-04 버그 수정 — 예전엔 lang을 무시하고 항상
    data/typecast_voices.json만 읽어서 영어/일본어 텍스트에 한국어 보이스+
    language="kor"가 붙는 조용한 오류가 있었다)."""
    kor_names = {v["name"] for v in _voice_pool("kor")[0]}
    eng_names = {v["name"] for v in _voice_pool("영어")[0]}
    assert kor_names.isdisjoint(eng_names)  # 두 풀이 실제로 겹치지 않는지 전제 확인

    picked = _pick_segment_voices(2, lang="영어")
    assert set(picked) <= eng_names
    assert set(picked).isdisjoint(kor_names)


def test_voice_lang_from_topic():
    assert _voice_lang_from_topic("목_1") == "kor"
    assert _voice_lang_from_topic("목_1/ko") == "kor"
    assert _voice_lang_from_topic("목_1/en") == "영어"
    assert _voice_lang_from_topic("목_1/ja") == "일본어"


def test_middle_sentence_still_trimmed_to_next_boundary(tmp_path):
    """마지막이 아닌 문장은 기존처럼 -to로 정확히 잘려야 한다(회귀 방지 — 전체를
    안 자르게 되돌리는 실수 방지)."""
    src_path = tmp_path / "src.wav"
    _make_tone(src_path, 3.0)
    audio_bytes = src_path.read_bytes()

    words = [
        {"text": "하나.", "start": 0.0, "end": 1.0},
        {"text": "둘.", "start": 1.0, "end": 2.0},
        {"text": "셋.", "start": 2.0, "end": 2.9},
    ]

    out_bytes, _ = _insert_sentence_pauses(audio_bytes, "wav", words)
    out_path = tmp_path / "out.wav"
    out_path.write_bytes(out_bytes)
    out_duration = _probe_duration(out_path)

    gap = SENTENCE_GAP_MS / 1000
    # seg0(1.0) + gap + seg1(1.0) + gap + seg2(마지막이라 2.0~3.0=1.0, 원본 끝까지)
    expected = 1.0 + gap + 1.0 + gap + 1.0
    assert abs(out_duration - expected) < 0.15, (
        f"out_duration={out_duration:.2f}s, expected≈{expected:.2f}s"
    )
