# 사용자 본인 녹음 → narration.mp3·narration.srt·narration_words.json. WHY: 2026-10-07부터 건강·육아(댕냥 포함) 나레이션은 TTS가 아니라 사용자 목소리.
#
# WHY(2026-10-07 사용자 "건강·육아·댕냥 이쪽은 tts 안 쓰고 내 목소리 쓰는 게 좋을 것 같다. 돈 아깝기도 하고. 좀 느리게
# 빼는 거도 좋을 거 같아서 시간 상한도 없애자"): 타입캐스트가 만들던 세 파일을 녹음에서 똑같이 만들어, 조립(xray_build)부터는
# 아무것도 바꾸지 않게 한다. 단어 시각은 faster-whisper로 뽑고, 화면 자막은 대본 원문(숫자 그대로)을 쓴다 — 인식 결과를
# 자막으로 쓰면 오인식이 화면에 그대로 박힌다.
#
#   .venv/bin/python3 -m lib.own_voice <topic> <녹음 파일(m4a·mp3·wav)>
#
# 1. 앞뒤 무음 자르기·음량 맞추기 → 2. 단어 시각 인식 → 3. 대본(읽기용) 글자와 인식 글자를 맞춰 대본 단어마다 시각 →
# 4. mp3·srt·words 쓰기(원본은 narration_raw로 보관)
from __future__ import annotations

import difflib
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from lib import tracks
from lib.fish_tts import _build_srt, _split_sentences
from lib.korean_numbers import to_speech

log = logging.getLogger(__name__)
# 한국어 인식 정확도와 속도(맥 CPU, 1분 녹음 1~2분)의 절충. 정확도가 모자라면 환경변수로 large-v3.
WHISPER_MODEL = os.environ.get("OWN_VOICE_WHISPER_MODEL", "medium")
# 앞뒤 무음 판정 — 숨소리·방 잡음은 남기지 않을 만큼, 말끝 여운은 자르지 않을 만큼
SILENCE_DB = os.environ.get("OWN_VOICE_SILENCE_DB", "-40dB")
_KEEP = re.compile(r"[가-힣A-Za-z0-9]")


def _prepare(src: Path, dst: Path) -> None:
    """앞뒤 무음을 자르고 방송 음량(-16 LUFS)으로 맞춘 mono mp3."""
    trim = (f"silenceremove=start_periods=1:start_threshold={SILENCE_DB}:start_silence=0.15,"
            f"areverse,silenceremove=start_periods=1:start_threshold={SILENCE_DB}:start_silence=0.3,areverse,"
            "loudnorm=I=-16:TP=-1.5:LRA=11")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", trim, "-ac", "1", "-ar", "44100",
                    "-c:a", "libmp3lame", "-b:a", "192k", str(dst)], check=True)


def _recognize(audio: Path) -> list[dict]:
    from faster_whisper import WhisperModel
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    segs, _info = model.transcribe(str(audio), language="ko", word_timestamps=True, vad_filter=False)
    return [{"text": w.word.strip(), "start": w.start, "end": w.end} for s in segs for w in (s.words or []) if w.word.strip()]


def _char_times(words: list[dict]) -> tuple[str, list[tuple[float, float]]]:
    """인식 단어를 글자 흐름으로 펴고 글자마다 (시작, 끝) 시각을 고르게 나눠 단다."""
    chars, times = [], []
    for w in words:
        cs = _KEEP.findall(w["text"])
        if not cs:
            continue
        step = (w["end"] - w["start"]) / len(cs)
        for i, c in enumerate(cs):
            chars.append(c)
            times.append((w["start"] + i * step, w["start"] + (i + 1) * step))
    return "".join(chars), times


def align(spoken: str, words: list[dict]) -> list[dict]:
    """대본(읽기용) 띄어쓰기 단위마다 녹음 시각을 붙인다. 못 맞춘 글자는 앞뒤 맞춘 글자 사이로 보간한다."""
    rec, rtimes = _char_times(words)
    tokens = spoken.split()
    script = "".join("".join(_KEEP.findall(t)) for t in tokens)
    sm = difflib.SequenceMatcher(None, script, rec, autojunk=False)
    at: list[float | None] = [None] * len(script)
    end_at: list[float | None] = [None] * len(script)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            at[a + k], end_at[a + k] = rtimes[b + k]
    # 보간 — 못 맞춘 구간은 앞뒤 맞춘 시각 사이를 글자 수로 나눈다
    known = [i for i, v in enumerate(at) if v is not None]
    if not known:
        raise ValueError("[own_voice] 녹음과 대본이 전혀 안 맞는다 — 다른 topic 녹음이거나 대본이 바뀌었다")
    total_end = rtimes[-1][1]
    for i in range(len(script)):
        if at[i] is not None:
            continue
        prev = max((k for k in known if k < i), default=None)
        nxt = min((k for k in known if k > i), default=None)
        t0 = end_at[prev] if prev is not None else 0.0
        t1 = at[nxt] if nxt is not None else total_end
        lo = prev if prev is not None else -1
        hi = nxt if nxt is not None else len(script)
        frac0, frac1 = (i - lo - 1) / (hi - lo - 1), (i - lo) / (hi - lo - 1)
        at[i], end_at[i] = t0 + (t1 - t0) * frac0, t0 + (t1 - t0) * frac1
    out, pos = [], 0
    for t in tokens:
        n = len(_KEEP.findall(t))
        if n == 0:
            continue
        out.append({"text": t, "start": round(at[pos], 3), "end": round(end_at[pos + n - 1], 3)})
        pos += n
    matched = sum(n for _a, _b, n in sm.get_matching_blocks()) / max(1, len(script))
    if matched < 0.6:
        log.warning("[own_voice] 대본과 녹음이 %.0f%%만 맞는다 — 대본과 다르게 읽었는지 확인할 것", matched * 100)
    return out


def ingest(topic: str, recording: Path) -> dict:
    text = (tracks.data_dir(topic) / "narration.txt").read_text(encoding="utf-8").strip()
    spoken = to_speech(text)
    if len(_split_sentences(spoken)) != len(_split_sentences(text)):
        raise ValueError("[own_voice] 읽기용 텍스트와 원문의 문장 수가 다르다 — 자막이 어긋난다")
    out = tracks.output_dir(topic)
    out.mkdir(parents=True, exist_ok=True)
    shutil.copy2(recording, out / f"narration_raw{recording.suffix.lower()}")
    audio = out / "narration.mp3"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "n.mp3"
        _prepare(recording, tmp)
        words = _recognize(tmp)
        shutil.copy2(tmp, audio)
    aligned = align(spoken, words)
    (out / "narration_words.json").write_text(json.dumps(aligned, ensure_ascii=False), encoding="utf-8")
    (out / "narration.srt").write_text(_build_srt(spoken, aligned, display=text), encoding="utf-8")
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
                               capture_output=True, text=True, check=True).stdout.strip())
    return {"audio_path": str(audio), "duration": dur, "word_count": len(aligned)}


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) != 3:
        sys.exit("사용법: .venv/bin/python3 -m lib.own_voice <topic> <녹음 파일>")
    r = ingest(sys.argv[1], Path(sys.argv[2]))
    print(f"[own_voice] {sys.argv[1]}: {r['duration']:.1f}초, 단어 {r['word_count']}개 → {r['audio_path']}")
