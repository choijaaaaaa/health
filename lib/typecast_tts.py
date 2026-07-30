# 타입캐스트 TTS 연동 (shopping-shorts-video/lib/typecast_tts.py에서 이식, job_id 기반
# paths.py 의존 제거하고 topic 폴더 직접 사용하도록 단순화). 문장 사이 무음 삽입 로직은
# 동일 — audio_tempo가 쉬는 구간까지 같이 빨리 감아버려서 문장 단위로 잘라 무음을 끼워넣는다.
from __future__ import annotations

import base64
import json
import os
import random
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_URL = "https://api.typecast.ai/v1/text-to-speech/with-timestamps"
SENTENCE_END = re.compile(r"[.!?]$")
AUDIO_TEMPO = 1.15  # 건강정보 콘텐츠는 차분한 톤이 맞아서 쇼핑숏츠(1.2)보다 살짝 느리게
SENTENCE_GAP_MS = 320  # 정보 전달용이라 숏폼 광고보다 살짝 여유있게


def _voice_id(name: str) -> str:
    voices = json.loads((ROOT / "data" / "typecast_voices.json").read_text())
    for v in voices:
        if v["name"] == name:
            return v["actor_id"]
    raise ValueError(f"등록되지 않은 보이스 이름: {name}")


def _random_voice_name() -> str:
    """WHY 랜덤 보이스(2026-07-31): 매번 "상현"으로 고정하면 채널 전체가 목소리
    단조로워진다는 피드백 — topic마다 등록된 보이스 중 하나를 난수로 골라
    다양성을 준다."""
    voices = json.loads((ROOT / "data" / "typecast_voices.json").read_text())
    return random.choice(voices)["name"]


def _format_srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _group_sentences(words: list[dict]) -> list[list[dict]]:
    entries = []
    buf = []
    for w in words:
        buf.append(w)
        if SENTENCE_END.search(w["text"].strip()):
            entries.append(buf)
            buf = []
    if buf:
        entries.append(buf)
    return entries


def _build_srt(words: list[dict]) -> str:
    entries = _group_sentences(words)
    lines = []
    for i, entry in enumerate(entries, start=1):
        start = _format_srt_time(entry[0]["start"])
        end = _format_srt_time(entry[-1]["end"])
        text = " ".join(w["text"] for w in entry)
        lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(lines)


def _insert_sentence_pauses(audio_bytes: bytes, audio_format: str, words: list[dict]) -> tuple[bytes, list[dict]]:
    entries = _group_sentences(words)
    if len(entries) <= 1:
        return audio_bytes, words

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / f"src.{audio_format}"
        src.write_bytes(audio_bytes)

        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=sample_rate,channels", "-of", "csv=p=0", str(src)],
            capture_output=True, text=True, check=True,
        )
        sample_rate, channels = probe.stdout.strip().split(",")

        silence = tmp_path / "silence.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi",
             "-i", f"anullsrc=r={sample_rate}:cl={'mono' if channels == '1' else 'stereo'}",
             "-t", str(SENTENCE_GAP_MS / 1000), str(silence)],
            check=True, capture_output=True,
        )

        concat_list = tmp_path / "concat.txt"
        new_words = []
        cursor = 0.0
        lines = []
        for i, entry in enumerate(entries):
            seg_start, seg_end = entry[0]["start"], entry[-1]["end"]
            seg_path = tmp_path / f"seg_{i:03d}.wav"
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(src), "-ss", str(seg_start), "-to", str(seg_end),
                 "-c:a", "pcm_s16le", str(seg_path)],
                check=True, capture_output=True,
            )
            lines.append(f"file '{seg_path}'")

            for w in entry:
                new_words.append({
                    "text": w["text"],
                    "start": cursor + (w["start"] - seg_start),
                    "end": cursor + (w["end"] - seg_start),
                })
            cursor += (seg_end - seg_start)

            if i < len(entries) - 1:
                lines.append(f"file '{silence}'")
                cursor += SENTENCE_GAP_MS / 1000

        concat_list.write_text("\n".join(lines))
        out_path = tmp_path / f"out.{audio_format}"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), str(out_path)],
            check=True, capture_output=True,
        )
        return out_path.read_bytes(), new_words


def synthesize(topic: str, text: str, voice_name: str | None = None, audio_format: str = "mp3") -> dict:
    api_key = os.environ["TYPECAST_API_KEY"]
    if voice_name is None:
        voice_name = _random_voice_name()
        print(f"[typecast] 보이스 랜덤 선택: {voice_name}")

    body = {
        "voice_id": _voice_id(voice_name),
        "text": text,
        "model": "ssfm-v30",
        "language": "kor",
        "granularity": "word",
        "output": {"audio_format": audio_format, "audio_tempo": AUDIO_TEMPO},
    }
    resp = requests.post(
        API_URL,
        headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
        json=body,
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()

    ext = data.get("audio_format", audio_format)
    audio_bytes = base64.b64decode(data["audio"])
    words = data.get("words") or []

    audio_bytes, words = _insert_sentence_pauses(audio_bytes, ext, words)

    out_dir = ROOT / "output" / topic
    out_dir.mkdir(parents=True, exist_ok=True)

    audio_path = out_dir / f"narration.{ext}"
    srt_path = out_dir / "narration.srt"
    audio_path.write_bytes(audio_bytes)
    srt_path.write_text(_build_srt(words))

    return {
        "audio_path": str(audio_path),
        "srt_path": str(srt_path),
        "duration": words[-1]["end"] if words else data.get("audio_duration"),
        "word_count": len(words),
        "words": words,
    }


if __name__ == "__main__":
    topic = sys.argv[1]
    text = sys.argv[2]
    voice_name = sys.argv[3] if len(sys.argv) > 3 else None
    result = synthesize(topic, text, voice_name)
    print(json.dumps({k: v for k, v in result.items() if k != "words"}, ensure_ascii=False, indent=2))
