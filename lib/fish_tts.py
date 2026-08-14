# Fish Audio TTS 연동(2026-08-14 도입, Typecast 대체). WHY: 프로젝트 결정상
# 타입캐스트를 걷어내고 Fish Audio로 전환하기로 했었는데 이 파일 자체가
# 없었던 상태였음 — jp-review-shorts/lib/fish_audio_tts.py(2026-08-13 그
# 프로젝트에서 먼저 시행착오 거쳐 안정화됨)를 그대로 이식, health-shorts
# 기존 typecast_tts.py의 호출 관례(topic 인자에 언어 접미사를 포함시켜
# output/<topic>/narration.* 경로를 그대로 결정, lang 파라미터는 코드값
# "kor"/"en"/"ja")만 맞춰서 다른 코드는 한 줄도 안 바꿔도 되게 했다.
#
# ⚠️ 보이스 선택(중요, jp-review-shorts에서 이미 확인됨): Fish Audio `/model`
# 목록은 자체 큐레이션이 아니라 사용자 업로드 보이스 클로닝 마켓플레이스라
# 카리나·아이유·정치인 등 실존 인물, 도라에몽 등 저작권 캐릭터 클론이 섞여
# 있다. `data/fish_audio_voices*.json`은 제목에 실존 인물·캐릭터 이름이
# 전혀 없는(순수 설명형 제목만) 항목만 사람이 확인 후 큐레이션한 목록 —
# 새 보이스 추가 시 항상 이 기준으로 확인할 것.
from __future__ import annotations

import base64
import json
import os
import random
import re
import subprocess
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_URL = "https://api.fish.audio/v1/tts/stream/with-timestamp"
VOICE_POOL_PATH_BY_LANG = {
    "kor": ROOT / "data" / "fish_audio_voices.json",
    "en": ROOT / "data" / "fish_audio_voices_en.json",
    "ja": ROOT / "data" / "fish_audio_voices_ja.json",
}
SENTENCE_END = re.compile(r"[.!?。！？।؟]$")
AUDIO_TEMPO = 1.0  # health-shorts 기존 원칙(2026-08-05, "배속 없이 원 속도") 그대로 유지
SENTENCE_GAP_MS = 320  # typecast_tts.py와 동일값 — 정보 전달용이라 숏폼 광고보다 여유있게


def _voice_pool(lang: str = "kor") -> list[dict]:
    path = VOICE_POOL_PATH_BY_LANG.get(lang, VOICE_POOL_PATH_BY_LANG["kor"])
    return json.loads(path.read_text(encoding="utf-8"))


def _voice_reference_id(name: str, lang: str = "kor") -> str:
    for v in _voice_pool(lang):
        if v["name"] == name:
            return v["reference_id"]
    raise ValueError(f"등록되지 않은 Fish Audio 보이스 이름({lang}): {name}")


def _random_voice_name(lang: str = "kor") -> str:
    """topic마다 등록된 보이스 중 하나를 난수로 골라 채널 전체 목소리가
    단조로워지지 않게 한다(typecast_tts.py와 동일 원칙)."""
    return random.choice(_voice_pool(lang))["name"]


def _format_srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|(?<=[。！？])|\n\s*\n")
# WHY 세 갈래 분기(jp-review-shorts에서 다국어 확장 전 실측 확인해 이식):
# ① ASCII 문장부호(.!?) + 공백 필수 — "0.09%"처럼 숫자 사이 마침표를 문장
#   경계로 오탐하는 걸 막는다.
# ② CJK 전각 문장부호(。！？)는 공백 없이 바로 분리 — 일본어는 마침표 뒤에
#   공백을 안 쓰는 게 관행이라 ①과 같은 공백 요구를 걸면 문장이 안 갈린다.
# ③ 빈 줄(문단 구분)도 항상 분리.
def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]


_NORMALIZE_RE = re.compile(r"[\s\W_]+", re.UNICODE)  # 공백/문장부호/기호 전부 제거(언어 무관 길이 비교용)


def _normalized_len(s: str) -> int:
    return len(_NORMALIZE_RE.sub("", s))


def _group_sentences(text: str, words: list[dict]) -> list[tuple[str | None, list[dict]]]:
    """Fish Audio의 word segment엔 문장부호가 안 붙어있다. 원문을 문장 단위로
    나눈 뒤 "정규화된 글자 길이"(공백·문장부호 제거 후 길이) 기준으로 반환
    세그먼트를 그리디하게 소비해서 그룹핑한다 — 공백으로 단어가 갈리는
    언어(한국어·영어)든 글자 단위로 세그먼트가 갈리는 언어(일본어)든 토큰화
    방식과 무관하게 동일하게 동작한다."""
    sentences = _split_sentences(text)
    entries: list[tuple[str | None, list[dict]]] = []
    idx = 0
    for sent in sentences:
        target_len = _normalized_len(sent)
        start_idx = idx
        consumed_len = 0
        while idx < len(words) and consumed_len < target_len:
            consumed_len += _normalized_len(words[idx]["text"])
            idx += 1
        chunk = words[start_idx:idx]
        if chunk:
            entries.append((sent, chunk))
    if idx < len(words):
        entries.append((None, words[idx:]))
    return entries


def _build_srt(text: str, words: list[dict]) -> str:
    entries = _group_sentences(text, words)
    lines = []
    for i, (sent, chunk) in enumerate(entries, start=1):
        start = _format_srt_time(chunk[0]["start"])
        end = _format_srt_time(chunk[-1]["end"])
        display_text = sent if sent is not None else " ".join(w["text"] for w in chunk)
        lines.append(f"{i}\n{start} --> {end}\n{display_text}\n")
    return "\n".join(lines)


def _insert_sentence_pauses(text: str, audio_bytes: bytes, words: list[dict]) -> tuple[bytes, list[dict]]:
    """문장 사이에 명시적 무음을 끼워넣는다 — 자연 발화만으로는 문장 경계가
    뭉개져서 이후 씬 타이밍 계산(narration.srt 문장 경계 기준)이 부정확해지는
    걸 막기 위함(typecast_tts.py와 동일 접근)."""
    entries = _group_sentences(text, words)
    if len(entries) <= 1:
        return audio_bytes, words

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "src.mp3"
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
        for i, (_sent, entry) in enumerate(entries):
            seg_start, seg_end = entry[0]["start"], entry[-1]["end"]
            seg_path = tmp_path / f"seg_{i:03d}.wav"
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
        out_path = tmp_path / "out.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), str(out_path)],
            check=True, capture_output=True,
        )
        return out_path.read_bytes(), new_words


def _apply_tempo(audio_bytes: bytes, words: list[dict], tempo: float) -> tuple[bytes, list[dict]]:
    if tempo == 1.0:
        return audio_bytes, words
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "src.mp3"
        src.write_bytes(audio_bytes)
        out = tmp_path / "out.mp3"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(src), "-filter:a", f"atempo={tempo}", str(out)],
            check=True, capture_output=True,
        )
        scaled_words = [{"text": w["text"], "start": w["start"] / tempo, "end": w["end"] / tempo} for w in words]
        return out.read_bytes(), scaled_words


def _call_tts(text: str, voice_name: str, lang: str = "kor", max_retries: int = 3) -> tuple[bytes, list[dict]]:
    """⚠️ Fish Audio 스트리밍 API는 문장이 여러 개(청크 4개+)로 나뉘는 긴
    텍스트에서 신뢰성 문제가 있다(jp-review-shorts 실측, 재현 확인) — 마지막
    청크의 alignment는 전체 텍스트를 다 담고 있는데 실제 audio_base64는
    0.1초짜리만 오는 식으로 조용히 잘리거나, 반대로 텍스트가 반복
    재생성되기도 한다. 매번 실제 오디오 길이를 alignment 마지막 단어 end
    시각과 대조해서, 허용 오차(15~30%) 밖이면 전체를 다시 호출한다."""
    for attempt in range(1, max_retries + 1):
        audio_bytes, words = _call_tts_once(text, voice_name, lang)
        if not words:
            print(f"[fish_tts] 시도 {attempt}: 응답에 word timestamp 없음, 재시도")
            continue
        claimed_end = words[-1]["end"]
        actual_dur = _probe_duration_from_bytes(audio_bytes)
        if 0.85 * claimed_end <= actual_dur <= 1.3 * claimed_end:
            return audio_bytes, words
        print(f"[fish_tts] 시도 {attempt}: 길이 불일치(claimed={claimed_end:.1f}s, "
              f"actual={actual_dur:.1f}s) — 재시도")
    raise RuntimeError(
        f"[fish_tts] {max_retries}번 재시도해도 오디오 길이가 alignment과 안 맞음 — "
        f"API 응답이 계속 불안정함"
    )


def _probe_duration_from_bytes(audio_bytes: bytes) -> float:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        f.write(audio_bytes)
        p = f.name
    try:
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nokey=1:noprint_wrappers=1", p],
            capture_output=True, text=True, check=True,
        )
        return float(out.stdout.strip())
    finally:
        Path(p).unlink(missing_ok=True)


def _call_tts_once(text: str, voice_name: str, lang: str = "kor") -> tuple[bytes, list[dict]]:
    """SSE 스트림을 소비해서 오디오(mp3 바이트)와 단어 타임스탬프를 반환한다."""
    api_key = os.environ["FISH_AUDIO_API_KEY"]
    body = {
        "text": text,
        "reference_id": _voice_reference_id(voice_name, lang),
        "format": "mp3",
        "latency": "normal",
    }
    resp = requests.post(
        API_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=body,
        stream=True,
        timeout=180,
    )
    resp.raise_for_status()

    # ⚠️ chunk_seq당 이벤트가 여러 번 올 수 있다(jp-review-shorts 실측). Fish
    # Audio 문서는 "최신 alignment이 이전 값을 대체"라고 하는데, audio에
    # 그대로 적용하면 안 된다 — 같은 chunk_seq의 1번째 이벤트가 이미 완결된
    # 오디오이고 2번째 이벤트는 거의 빈 "꼬리" 델타인 경우가 있어서, 최신
    # 값으로 덮어쓰면 완결된 오디오가 통째로 지워진다("tts가 짜집기된 것처럼
    # 목소리가 바뀐다"는 증상의 실제 원인). audio는 각 chunk_seq당 "처음 온
    # 것만" 쓰고, alignment는 정렬 정보만 갱신되는 성격이라 최신 값을 쓴다.
    audio_chunks: dict[int, bytes] = {}
    alignment_by_chunk: dict[int, tuple[float, dict]] = {}
    for raw_line in resp.iter_lines():
        if not raw_line:
            continue
        line = raw_line.decode("utf-8")
        if not line.startswith("data:"):
            continue
        payload = line[len("data:"):].strip()
        if not payload or payload == "[DONE]":
            continue
        event = json.loads(payload)
        seq = event.get("chunk_seq", 0)
        if event.get("audio_base64") and seq not in audio_chunks:
            audio_chunks[seq] = base64.b64decode(event["audio_base64"])
        alignment = event.get("alignment")
        if alignment and alignment.get("segments"):
            alignment_by_chunk[seq] = (event.get("chunk_audio_offset_sec", 0.0), alignment)

    # ⚠️ 청크를 바이트째로 그냥 이어붙이면 안 된다(jp-review-shorts 실측 —
    # "SRT는 41초까지 있다는데 실제 오디오 파일은 29초에서 끊김" 사고 원인).
    # 각 chunk_seq의 audio_base64는 그 자체로 완결된 mp3 스트림이라, 여러
    # 완결된 mp3를 바이트로 그냥 이어붙이면 디코더가 첫 스트림만 읽고
    # 멈추거나 길이를 잘못 계산한다. 각 청크를 WAV로 디코드해 이어붙이고
    # 마지막에 한 번만 mp3로 재인코딩한다.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        wav_files = []
        for seq in sorted(audio_chunks):
            src = tmp_path / f"chunk_{seq}.mp3"
            src.write_bytes(audio_chunks[seq])
            wav = tmp_path / f"chunk_{seq}.wav"
            subprocess.run(["ffmpeg", "-y", "-i", str(src), "-c:a", "pcm_s16le", str(wav)],
                            check=True, capture_output=True)
            wav_files.append(wav)
        concat_list = tmp_path / "concat.txt"
        concat_list.write_text("\n".join(f"file '{p}'" for p in wav_files))
        combined_wav = tmp_path / "combined.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(combined_wav)],
            check=True, capture_output=True,
        )
        combined_mp3 = tmp_path / "combined.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", str(combined_wav), str(combined_mp3)],
                        check=True, capture_output=True)
        audio_bytes = combined_mp3.read_bytes()
    words = []
    for seq in sorted(alignment_by_chunk):
        offset, alignment = alignment_by_chunk[seq]
        for seg in alignment["segments"]:
            words.append({"text": seg["text"], "start": seg["start"] + offset, "end": seg["end"] + offset})
    return audio_bytes, words


_MAX_SENTENCES_PER_CALL = 1  # WHY(jp-review-shorts 실측, 재현됨): Fish Audio
# 스트리밍 응답에서 "마지막 청크"의 alignment는 정상인데 실제 audio_base64는
# 근거리 0.1초짜리로 사실상 비어있게 오는 사고가 문장 4개(청크 2~3개)만
# 돼도 재현됐다 — 청크가 여러 개면 마지막 청크가 불안정한 게 실제 패턴으로
# 보인다(재시도해도 동일 재현되는 결정론적 문제). 한 번 호출에 문장 1개만
# 넣어 항상 단일 청크로 끝나도록 강제한다 — API 호출 수는 늘지만 비용은
# 무시할 수준.


def _call_tts_batched(text: str, voice_name: str, lang: str = "kor") -> tuple[bytes, list[dict]]:
    """긴 텍스트를 문장 단위로 나눠 API를 여러 번 호출한 뒤 WAV로 이어붙여서
    한 번 호출한 것과 동일한 (오디오, 전체 단어 타임스탬프) 결과를 만든다."""
    sentences = _split_sentences(text)
    if len(sentences) <= _MAX_SENTENCES_PER_CALL:
        return _call_tts(text, voice_name, lang)

    batches = [sentences[i:i + _MAX_SENTENCES_PER_CALL]
               for i in range(0, len(sentences), _MAX_SENTENCES_PER_CALL)]
    all_words: list[dict] = []
    cursor = 0.0
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        wav_files = []
        for i, batch in enumerate(batches):
            batch_text = " ".join(batch)
            audio_bytes, words = _call_tts(batch_text, voice_name, lang)
            src = tmp_path / f"batch_{i}.mp3"
            src.write_bytes(audio_bytes)
            wav = tmp_path / f"batch_{i}.wav"
            subprocess.run(["ffmpeg", "-y", "-i", str(src), "-c:a", "pcm_s16le", str(wav)],
                            check=True, capture_output=True)
            wav_files.append(wav)
            for w in words:
                all_words.append({"text": w["text"], "start": w["start"] + cursor, "end": w["end"] + cursor})
            cursor += _probe_duration_from_bytes(audio_bytes)

        concat_list = tmp_path / "concat.txt"
        concat_list.write_text("\n".join(f"file '{p}'" for p in wav_files))
        combined_wav = tmp_path / "combined.wav"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
             "-c", "copy", str(combined_wav)],
            check=True, capture_output=True,
        )
        combined_mp3 = tmp_path / "combined.mp3"
        subprocess.run(["ffmpeg", "-y", "-i", str(combined_wav), str(combined_mp3)],
                        check=True, capture_output=True)
        audio_bytes = combined_mp3.read_bytes()
    return audio_bytes, all_words


# WHY topic 인자가 곧 output 경로인지(health-shorts 기존 typecast_tts.py
# 관례 그대로 유지) — "눈_8"(한국어)은 output/눈_8/, "눈_8/en"(영어)은
# output/눈_8/en/으로 그대로 떨어지고, lang 코드는 topic 뒤 세그먼트에서
# 파생한다. 이 관례를 그대로 따라야 video_assembler.py/dashboard.py 등
# 기존 파이프라인이 아무것도 안 바뀐다.
_LANG_CODE_FROM_TOPIC = {"ko": "kor", "en": "en", "ja": "ja"}


def _voice_lang_from_topic(topic: str) -> str:
    """"눈_8/en" -> "en", "눈_8/ko" 또는 "눈_8"(언어 세그먼트 없음) -> "kor"."""
    code = topic.rsplit("/", 1)[1] if "/" in topic else "ko"
    if code not in _LANG_CODE_FROM_TOPIC:
        raise ValueError(f"fish_tts.py: 알 수 없는 언어 코드 '{code}'(topic={topic!r})")
    return _LANG_CODE_FROM_TOPIC[code]


def synthesize(topic: str, text: str, voice_name: str | None = None, lang: str = "kor") -> dict:
    """typecast_tts.synthesize()와 동일한 반환 모양(audio_path/srt_path/
    duration/word_count/words) — render 파이프라인은 어느 TTS를 호출하는지
    신경 쓸 필요 없음. out_dir은 typecast_tts.py와 동일하게 topic 인자를
    그대로 output/ 아래 상대경로로 쓴다(언어 세그먼트는 호출부가 topic에
    이미 포함시켜서 넘긴다, 예: "눈_8/en")."""
    if voice_name is None:
        voice_name = _random_voice_name(lang)
        print(f"[fish_tts] 보이스 랜덤 선택({lang}): {voice_name}")

    audio_bytes, words = _call_tts_batched(text, voice_name, lang)
    if not words:
        raise RuntimeError("[fish_tts] 응답에 word timestamp가 없음 — API 응답 형식이 바뀌었을 수 있음")
    audio_bytes, words = _insert_sentence_pauses(text, audio_bytes, words)
    audio_bytes, words = _apply_tempo(audio_bytes, words, AUDIO_TEMPO)

    out_dir = ROOT / "output" / topic
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "narration.mp3"
    srt_path = out_dir / "narration.srt"
    audio_path.write_bytes(audio_bytes)
    srt_path.write_text(_build_srt(text, words))

    duration = words[-1]["end"] if words else None
    return {
        "audio_path": str(audio_path),
        "srt_path": str(srt_path),
        "duration": duration,
        "word_count": len(words),
        "words": words,
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("사용법: python3 lib/fish_tts.py <topic(예: 눈_8 또는 눈_8/en)> <text> [voice_name]")
        sys.exit(1)
    topic_arg = sys.argv[1]
    text_arg = sys.argv[2]
    voice_arg = sys.argv[3] if len(sys.argv) > 3 else None
    result = synthesize(topic_arg, text_arg, voice_arg, lang=_voice_lang_from_topic(topic_arg))
    print(json.dumps({k: v for k, v in result.items() if k != "words"}, ensure_ascii=False, indent=2))
