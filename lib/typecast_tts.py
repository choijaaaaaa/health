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
            # WHY 마지막 구간만 -to를 안 주는지(2026-08-02, "마지막에 뚝뚝 끊기는" 버그
            # 수정): 타입캐스트 단어 타임스탬프의 end가 그 단어의 자연스러운 여운(끝소리
            # decay)까지 포함 안 할 수 있는데, 지금까지는 모든 구간을 "-to seg_end"로
            # 정확히 잘랐다 — 중간 문장은 바로 뒤에 무음이 붙어서 덜 티 나지만, 맨 마지막
            # 문장은 그 뒤에 아무것도 안 붙어서 잘린 꼬리가 그대로 들린다. 마지막 구간만
            # 원본 끝까지 살려서 여운이 잘리지 않게 한다.
            cmd = ["ffmpeg", "-y", "-i", str(src), "-ss", str(seg_start)]
            if i < len(entries) - 1:
                cmd += ["-to", str(seg_end)]
            cmd += ["-c:a", "pcm_s16le", str(seg_path)]
            subprocess.run(cmd, check=True, capture_output=True)
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


def _call_tts(text: str, voice_name: str, audio_format: str) -> tuple[bytes, list[dict], str]:
    api_key = os.environ["TYPECAST_API_KEY"]
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
    return audio_bytes, words, ext


def synthesize(topic: str, text: str, voice_name: str | None = None, audio_format: str = "mp3") -> dict:
    if voice_name is None:
        voice_name = _random_voice_name()
        print(f"[typecast] 보이스 랜덤 선택: {voice_name}")

    audio_bytes, words, ext = _call_tts(text, voice_name, audio_format)
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
        "duration": words[-1]["end"] if words else None,
        "word_count": len(words),
        "words": words,
    }


# WHY 세그먼트별 다른 보이스(2026-08-01): 캐릭터 여러 명이 번갈아 나오는 topic(예:
# 60대주의음식_1의 사골국/믹스커피/과일즙)이 지금까지는 나레이션 목소리가 하나로 고정돼서
# "캐릭터는 바뀌는데 말하는 사람은 안 바뀌는" 어색함이 있었다 — 캐릭터 화면 전환에 맞춰
# 문단(=narration.txt의 빈 줄 구분 단락, card_news_spec.json items 순서와 1:1 대응하는
# 기존 관례)마다 다른 보이스로 TTS를 따로 호출하고 이어붙인다.
SEGMENT_GAP_MS = 400  # 문장 사이 간격(SENTENCE_GAP_MS)보다 살짝 길게 — 화자 전환 체감용


def _pick_segment_voices(n: int) -> list[str]:
    """n개 세그먼트에 서로 겹치지 않는 보이스를 배정(보이스 개수보다 세그먼트가 많으면
    그 다음부터는 랜덤 재사용하되 바로 직전과는 겹치지 않게 한다)."""
    names = [v["name"] for v in json.loads((ROOT / "data" / "typecast_voices.json").read_text())]
    if n <= len(names):
        return random.sample(names, n)
    picked = random.sample(names, len(names))
    while len(picked) < n:
        choices = [v for v in names if v != picked[-1]]
        picked.append(random.choice(choices))
    return picked


def synthesize_segments(
    topic: str, segments: list[str], voice_names: list[str] | None = None, audio_format: str = "mp3"
) -> dict:
    """narration.txt를 문단(항목)별로 나눠 각각 다른 보이스로 TTS를 생성한 뒤 이어붙인다.
    voice_names를 안 주면 문단 개수만큼 서로 겹치지 않는 보이스를 랜덤 배정한다.
    출력 경로는 synthesize()와 동일(output/<topic>/narration.mp3, narration.srt)이라
    video_assembler.py 등 이후 단계는 단일/멀티 보이스 여부와 무관하게 그대로 쓰면 된다."""
    if voice_names is None:
        voice_names = _pick_segment_voices(len(segments))
    elif len(voice_names) != len(segments):
        raise ValueError("voice_names 개수가 segments 개수와 다름")

    ext = audio_format
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        concat_list = tmp_path / "concat.txt"
        lines: list[str] = []
        merged_words: list[dict] = []
        segment_starts: list[float] = []
        cursor = 0.0

        for i, (text, voice_name) in enumerate(zip(segments, voice_names)):
            segment_starts.append(cursor)
            print(f"[typecast] 세그먼트 {i + 1}/{len(segments)} 보이스: {voice_name}")
            audio_bytes, words, ext = _call_tts(text, voice_name, audio_format)
            audio_bytes, words = _insert_sentence_pauses(audio_bytes, ext, words)

            # WHY WAV로 저장(2026-08-02 버그 수정, "목소리가 바뀔 때 싱크가 점점
            # 더 어긋난다" 사용자 실측 발견): 여기서 seg_path를 mp3(ext)로 저장하면
            # 무음 gap 파일(WAV)과 형식이 섞인 채로 아래 concat 디먼서에 들어가는데,
            # 독립적으로 인코딩된 mp3 세그먼트마다 인코더 프라이밍/패딩이 붙어있어서
            # concat 디먼서가 디코드+재인코딩하는 과정에서 이어붙이는 지점마다 미세한
            # 시간 오차가 생긴다 — 세그먼트가 하나씩 늘어날 때마다 이 오차가 누적돼서
            # 뒤로 갈수록(=목소리가 바뀔 때마다) 자막·캐릭터 전환이 실제 음성보다
            # 점점 더 어긋나 보였다(이명_1에서 파형 실측으로 확인 — 첫 세그먼트는
            # 오차 0, 이후 세그먼트마다 커짐). 무음 gap 파일과 동일하게 무손실 WAV로
            # 저장해서 concat 입력을 전부 PCM으로 통일하면, 실제 인코딩은 맨 마지막
            # 병합 단계에서 한 번만 일어나 이 누적 오차가 생기지 않는다.
            seg_path = tmp_path / f"seg_{i:03d}.wav"
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp_seg:
                tmp_seg.write(audio_bytes)
                tmp_seg_path = tmp_seg.name
            subprocess.run(
                ["ffmpeg", "-y", "-i", tmp_seg_path, "-c:a", "pcm_s16le", str(seg_path)],
                check=True, capture_output=True,
            )
            os.remove(tmp_seg_path)
            lines.append(f"file '{seg_path}'")

            for w in words:
                merged_words.append({"text": w["text"], "start": cursor + w["start"], "end": cursor + w["end"]})
            # WHY 단어 타임스탬프 대신 실제 파일 길이로 커서를 미는지(2026-08-02 버그
            # 수정): words[-1]["end"]를 그대로 썼더니 실제 합쳐진 오디오 길이보다 SRT가
            # 최대 2초 가까이 더 길게 찍히는 사고가 났다(구내염_1 등에서 확인) —
            # `_insert_sentence_pauses`가 마지막 문장 구간은 자연스러운 여운을 위해
            # `-to`로 안 자르고 원본 끝까지 살리기 때문에(위 WHY 주석 참고), 실제 세그먼트
            # 오디오 길이가 마지막 단어의 API 타임스탬프와 정확히 일치한다는 보장이 없다.
            # ffprobe로 이 세그먼트 파일의 실제 길이를 재서 커서를 미는 게 훨씬 신뢰할
            # 수 있다 — 단어별 개별 타임스탬프(merged_words)는 그대로 두고, 다음 세그먼트가
            # 시작하는 절대 위치(cursor)만 실측값 기준으로 고정한다.
            seg_probe = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(seg_path)],
                capture_output=True, text=True, check=True,
            )
            seg_duration = float(seg_probe.stdout.strip())
            cursor += seg_duration

            if i < len(segments) - 1:
                silence = tmp_path / f"gap_{i:03d}.wav"
                probe = subprocess.run(
                    ["ffprobe", "-v", "error", "-select_streams", "a:0",
                     "-show_entries", "stream=sample_rate,channels", "-of", "csv=p=0", str(seg_path)],
                    capture_output=True, text=True, check=True,
                )
                sample_rate, channels = probe.stdout.strip().split(",")
                subprocess.run(
                    ["ffmpeg", "-y", "-f", "lavfi",
                     "-i", f"anullsrc=r={sample_rate}:cl={'mono' if channels == '1' else 'stereo'}",
                     "-t", str(SEGMENT_GAP_MS / 1000), str(silence)],
                    check=True, capture_output=True,
                )
                lines.append(f"file '{silence}'")
                cursor += SEGMENT_GAP_MS / 1000

        concat_list.write_text("\n".join(lines))
        out_dir = ROOT / "output" / topic
        out_dir.mkdir(parents=True, exist_ok=True)
        audio_path = out_dir / f"narration.{ext}"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), str(audio_path)],
            check=True, capture_output=True,
        )

    srt_path = out_dir / "narration.srt"
    srt_path.write_text(_build_srt(merged_words))

    return {
        "audio_path": str(audio_path),
        "srt_path": str(srt_path),
        "duration": merged_words[-1]["end"] if merged_words else None,
        "word_count": len(merged_words),
        "voice_names": voice_names,
        "segment_starts": segment_starts,
        "words": merged_words,
    }


if __name__ == "__main__":
    if "--multi-voice" in sys.argv:
        # 사용법: python3 lib/typecast_tts.py <topic> --multi-voice <narration.txt 경로>
        topic = sys.argv[1]
        narration_path = sys.argv[sys.argv.index("--multi-voice") + 1]
        segments = [p.strip() for p in Path(narration_path).read_text().split("\n\n") if p.strip()]
        result = synthesize_segments(topic, segments)
        print(json.dumps({k: v for k, v in result.items() if k != "words"}, ensure_ascii=False, indent=2))
    else:
        topic = sys.argv[1]
        text = sys.argv[2]
        voice_name = sys.argv[3] if len(sys.argv) > 3 else None
        result = synthesize(topic, text, voice_name)
        print(json.dumps({k: v for k, v in result.items() if k != "words"}, ensure_ascii=False, indent=2))
