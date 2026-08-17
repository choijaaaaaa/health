# Voicebox(로컬 Qwen3-TTS MLX 앱) 연동 — 한국어 나레이션 전용(2026-08-17
# 도입). WHY: Fish Audio 한국어 보이스 품질에 불만족 — 로컬 Voicebox.app으로
# 클론한 "한국어1" 보이스를 실측 비교(같은 대본으로 생성해서 직접 들어봄)
# 후 이걸로 교체하기로 확정. en/ja는 대상 밖 — `lib/fish_tts.py` 그대로
# 유지(비교 대상이 된 적 없음, 이 파일은 lang="kor" 전용).
#
# ⚠️ 로컬 앱 의존(Fish Audio와의 근본적 차이): Voicebox.app이 이 컴퓨터에서
# 항상 켜져 있어야 한다(백그라운드 서버 프로세스, 기본 포트 17493) — 클라우드
# API가 아니라 로컬 추론이라 생성마다 오래 걸린다(문장당 수 초~수십 초,
# 실측 700자 나레이션 전체를 한 번에 넣으면 약 100초).
#
# ⚠️ 문장 단위로 쪼개서 호출하는 이유(fish_tts.py의 _MAX_SENTENCES_PER_CALL
# 원칙과 동일 발상, 원인은 다름): Voicebox의 POST /generate는 Fish Audio와
# 달리 단어/문장 정렬(alignment) 타임스탬프를 아예 반환하지 않는다 — 전체
# 텍스트를 한 번에 넣으면 narration.srt를 만들 문장 경계 정보 자체가 없어진다.
# 문장 하나당 API 호출 하나로 쪼개면, 각 결과물 오디오 길이(ffprobe 실측)를
# 그대로 그 문장의 구간 길이로 쓸 수 있어 별도 정렬 없이 정확한 문장 단위
# SRT가 나온다 — fish_tts.py의 _build_srt가 만드는 것도 결국 문장 단위
# 엔트리라 이 파이프라인 하류(video_assembler.py 등)엔 차이가 없다.
from __future__ import annotations

import json
import re
import subprocess
import tempfile
import time
from pathlib import Path

import requests

from lib.mission_control_log import report_issue

ROOT = Path(__file__).resolve().parent.parent

API_BASE = "http://localhost:17493"
# WHY 프로필 하드코딩(2026-08-17): 사용자가 "한국어1"/"한국어2" 두 샘플을
# 직접 듣고 "한국어1"로 확정 — 여러 보이스 랜덤 선택하던 fish_tts.py와
# 달리 지금은 단일 확정 보이스만 쓴다. 나중에 보이스를 더 늘리기로 하면
# 이 상수를 fish_tts.py의 _random_voice_name()처럼 풀 방식으로 바꿀 것.
PROFILE_ID_KOR = "191e6fbc-0658-4d24-b5c2-4b1aacc1814a"  # Voicebox 프로필 "한국어1"

AUDIO_TEMPO = 1.0  # fish_tts.py와 동일 원칙 — 배속 없이 원 속도
SENTENCE_GAP_MS = 320  # fish_tts.py/typecast_tts.py와 동일값

_POLL_INTERVAL_SEC = 3
_POLL_TIMEOUT_SEC = 180  # 문장 하나 기준 — 실측 700자 전체가 100초 안팎이라 문장 단위는 충분히 여유

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|(?<=[。！？])|\n\s*\n")


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]


def _format_srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nokey=1:noprint_wrappers=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def _generate_sentence_wav(text: str, out_path: Path) -> None:
    """Voicebox에 문장 하나를 보내고 완료될 때까지 폴링한 뒤 wav로 받는다.

    ⚠️ GET /generate/{id}/status는 SSE 스트림이라 일반 JSON 파서로 읽으면
    응답이 끝날 때까지(=생성 완료까지) 연결이 안 닫혀서 그냥 블로킹된다(실측
    확인) — 상태 폴링은 반드시 GET /history/{id}(일반 JSON)를 써야 한다."""
    resp = requests.post(
        f"{API_BASE}/generate",
        json={"profile_id": PROFILE_ID_KOR, "text": text, "language": "ko"},
        timeout=30,
    )
    resp.raise_for_status()
    generation_id = resp.json()["id"]

    deadline = time.monotonic() + _POLL_TIMEOUT_SEC
    while time.monotonic() < deadline:
        h = requests.get(f"{API_BASE}/history/{generation_id}", timeout=15)
        h.raise_for_status()
        info = h.json()
        status = info.get("status")
        if status == "completed":
            audio = requests.get(f"{API_BASE}/audio/{generation_id}", timeout=30)
            audio.raise_for_status()
            out_path.write_bytes(audio.content)
            return
        if status == "failed":
            raise RuntimeError(f"[voicebox_tts] 생성 실패: {info.get('error')}")
        time.sleep(_POLL_INTERVAL_SEC)
    raise RuntimeError(f"[voicebox_tts] {_POLL_TIMEOUT_SEC}초 안에 생성이 끝나지 않음(생성 ID: {generation_id})")


def _call_tts(text: str) -> tuple[bytes, list[dict]]:
    """문장 단위로 Voicebox를 호출해 이어붙이고, fish_tts.py의 _build_srt가
    기대하는 것과 동일한 모양(문장별 (start,end)를 담은 word-like dict 리스트,
    각 문장이 통째로 하나의 "단어"인 것처럼)을 만들어 반환한다."""
    sentences = _split_sentences(text)
    if not sentences:
        raise ValueError("[voicebox_tts] 빈 텍스트")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        wav_files = []
        for i, sent in enumerate(sentences):
            wav = tmp_path / f"sent_{i:03d}.wav"
            _generate_sentence_wav(sent, wav)
            wav_files.append(wav)

        silence = tmp_path / "silence.wav"
        probe = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "a:0",
             "-show_entries", "stream=sample_rate,channels", "-of", "csv=p=0", str(wav_files[0])],
            capture_output=True, text=True, check=True,
        )
        sample_rate, channels = probe.stdout.strip().split(",")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi",
             "-i", f"anullsrc=r={sample_rate}:cl={'mono' if channels == '1' else 'stereo'}",
             "-t", str(SENTENCE_GAP_MS / 1000), str(silence)],
            check=True, capture_output=True,
        )

        concat_list = tmp_path / "concat.txt"
        lines = []
        words: list[dict] = []
        cursor = 0.0
        for i, (sent, wav) in enumerate(zip(sentences, wav_files)):
            dur = _probe_duration(wav)
            lines.append(f"file '{wav}'")
            words.append({"text": sent, "start": cursor, "end": cursor + dur})
            cursor += dur
            if i < len(wav_files) - 1:
                lines.append(f"file '{silence}'")
                cursor += SENTENCE_GAP_MS / 1000

        concat_list.write_text("\n".join(lines))
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
    return audio_bytes, words


def _build_srt(words: list[dict]) -> str:
    """words의 각 항목이 이미 문장 하나씩이라(fish_tts.py처럼 word->문장
    그룹핑을 다시 할 필요 없음) 그대로 SRT 엔트리로 찍는다."""
    lines = []
    for i, w in enumerate(words, start=1):
        start = _format_srt_time(w["start"])
        end = _format_srt_time(w["end"])
        lines.append(f"{i}\n{start} --> {end}\n{w['text']}\n")
    return "\n".join(lines)


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
        scaled = [{"text": w["text"], "start": w["start"] / tempo, "end": w["end"] / tempo} for w in words]
        return out.read_bytes(), scaled


def synthesize(topic: str, text: str, voice_name: str | None = None, lang: str = "kor") -> dict:
    """fish_tts.synthesize()/typecast_tts.synthesize()와 동일한 반환 모양·
    호출 관례 — render 파이프라인은 어느 TTS를 쓰는지 신경 쓸 필요 없음.

    ⚠️ lang="kor" 전용이다(2026-08-17 확정 범위) — en/ja는 검증한 적 없어서
    호출하면 바로 크래시시킨다(조용히 Fish로 폴백하지 않음 — 잘못 넘긴 걸
    바로 알아채게 하려는 의도, 이 프로젝트의 "fail loud" 원칙).
    voice_name은 fish_tts.py와의 시그니처 호환을 위해서만 받고 무시한다
    (지금은 단일 확정 보이스 "한국어1"뿐)."""
    if lang != "kor":
        raise ValueError(
            f"[voicebox_tts] lang='{lang}'는 지원 안 함 — 지금은 한국어(kor)만 검증됨. "
            f"en/ja는 lib/fish_tts.py를 계속 쓸 것."
        )
    try:
        requests.get(f"{API_BASE}/health", timeout=5)
    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            "[voicebox_tts] localhost:17493에 연결 안 됨 — Voicebox.app이 켜져있는지 확인할 것"
        )

    try:
        audio_bytes, words = _call_tts(text)
    except Exception as e:
        report_issue(severity="error", category="tts_failure", entity=topic, message=str(e))
        raise
    audio_bytes, words = _apply_tempo(audio_bytes, words, AUDIO_TEMPO)

    out_dir = ROOT / "output" / topic
    out_dir.mkdir(parents=True, exist_ok=True)
    audio_path = out_dir / "narration.mp3"
    srt_path = out_dir / "narration.srt"
    audio_path.write_bytes(audio_bytes)
    srt_path.write_text(_build_srt(words))

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
        print("사용법: python3 lib/voicebox_tts.py <topic(예: 눈_8)> <text>")
        sys.exit(1)
    topic_arg = sys.argv[1]
    text_arg = sys.argv[2]
    result = synthesize(topic_arg, text_arg)
    print(json.dumps({k: v for k, v in result.items() if k != "words"}, ensure_ascii=False, indent=2))
