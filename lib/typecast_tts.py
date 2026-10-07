# 한국어 나레이션 TTS — 타입캐스트 API. fish_tts.synthesize()와 같은 반환 모양이라 조립 쪽은 그대로다.
# WHY(2026-09-29 사용자 "피쉬오디오 너무 짜친다… api로 뽑는게 크레딧이 더 싸다"): 한국어는 여기로 옮겼다.
# 자막 정렬(_build_srt)은 fish_tts 것을 그대로 쓴다 — 읽기용 텍스트로 정렬하고 화면엔 숫자가 살아 있는 원문을 띄운다.
# 문장 사이 무음을 잘라 끼우지 않는다: 타입캐스트는 문장 사이를 스스로 띄우고, 단어 시작점에서 자르면
# 첫 음절이 날아간다(fish_tts에서 겪은 문제).
from __future__ import annotations

import base64
import logging
import os
import subprocess
from pathlib import Path

import requests
from dotenv import load_dotenv

from lib import tracks
from lib.fish_tts import _build_srt, _split_sentences
from lib.korean_numbers import to_speech

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

API_URL = "https://api.typecast.ai/v1/text-to-speech/with-timestamps"
MODEL = "ssfm-v30"
# 🚨 한국어 보이스는 하나만 쓴다(2026-09-19 "tts 목소리도 딱 그거로만 쫙 가자" 원칙 유지).
# 필재(Piljae) — 2026-09-29 "필재 1.2배로 가야겠다"(1.1에서 올림) → 2026-10-07 다시 1.1(아래)
VOICE_ID = "tc_68257f68bc6e3c161ab5078d"
# 2026-10-07 1.2 → 1.1(사용자 "속도만 1.2배에서 1.1배로 줄이자. 지금 좀 빠른 느낌이 있어서").
AUDIO_TEMPO = 1.1
# 한 번에 보내는 글자 상한 — 넘으면 문단 경계에서 나눠 부르고 이어 붙인다
MAX_CHARS_PER_CALL = int(os.environ.get("TYPECAST_MAX_CHARS", "1500"))
TIMEOUT_SEC = int(os.environ.get("TYPECAST_TIMEOUT_SEC", "180"))


def _call(text: str) -> tuple[bytes, list[dict], float]:
    resp = requests.post(
        API_URL,
        headers={"X-API-KEY": os.environ["TYPECAST_API_KEY"], "Content-Type": "application/json"},
        json={"voice_id": VOICE_ID, "text": text, "model": MODEL, "language": "kor", "granularity": "word",
              "output": {"audio_format": "mp3", "audio_tempo": AUDIO_TEMPO}},
        timeout=TIMEOUT_SEC,
    )
    if not resp.ok:
        raise RuntimeError(f"[typecast] {resp.status_code}: {resp.text[:300]}")
    d = resp.json()
    words = d.get("words") or []
    if not words:
        raise RuntimeError("[typecast] 응답에 words가 없다 — API 응답 형식이 바뀌었을 수 있다")
    return base64.b64decode(d["audio"]), words, float(d.get("audio_duration") or words[-1]["end"])


def _chunks(spoken: str) -> list[str]:
    paras = [p.strip() for p in spoken.split("\n\n") if p.strip()]
    out: list[str] = []
    for p in paras:
        if out and len(out[-1]) + len(p) + 2 <= MAX_CHARS_PER_CALL:
            out[-1] += "\n\n" + p
        else:
            out.append(p)
    return out


def _concat_mp3(parts: list[bytes], dst: Path) -> None:
    import subprocess
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        lst = Path(tmp) / "list.txt"
        names = []
        for i, b in enumerate(parts):
            (Path(tmp) / f"{i}.mp3").write_bytes(b)
            names.append(f"file '{Path(tmp) / f'{i}.mp3'}'")
        lst.write_text("\n".join(names))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                        "-c", "copy", str(dst)], check=True)


def synthesize(topic: str, text: str, *, approved: bool = False) -> dict:
    """1. 숫자를 한글로 푼 읽기용 텍스트 → 2. 문단 묶음별 호출 → 3. 이어 붙이고 시각 보정 → 4. mp3·srt 쓰기 → 5. 쉼 정리.

    🚨 approved는 **사용자가 이번에 뽑으라고 말했을 때만** True로 넘긴다. WHY(2026-09-29 "이제부터 절대 tts 너가
    바로 그냥 갖다박아서 뽑지 못하게 해… 크레딧이 생각보다 많이들어서"): 세션이 원고를 고친 김에 25편을 한 번에
    뽑았다가 보이스가 바로 바뀌어 전부 버렸다. 원고가 준비되면 사용자에게 요청하고 기다린다."""
    if not approved:
        raise PermissionError("[typecast] 사용자 승인 없이 TTS를 뽑지 않는다 — 원고를 보여주고 '뽑아줘'를 받은 뒤 --approved로 실행")
    spoken = to_speech(text)
    if len(_split_sentences(spoken)) != len(_split_sentences(text)):
        raise ValueError("[typecast] 읽기용 텍스트와 원문의 문장 수가 다르다 — 자막이 어긋난다")
    audios: list[bytes] = []
    words: list[dict] = []
    offset = 0.0
    for chunk in _chunks(spoken):
        audio, ws, dur = _call(chunk)
        audios.append(audio)
        words += [{"text": w["text"], "start": w["start"] + offset, "end": w["end"] + offset} for w in ws]
        offset += dur

    out = tracks.output_dir(topic)
    out.mkdir(parents=True, exist_ok=True)
    audio_path, srt_path = out / "narration.mp3", out / "narration.srt"
    if len(audios) == 1:
        audio_path.write_bytes(audios[0])
    else:
        _concat_mp3(audios, audio_path)
    srt_path.write_text(_build_srt(spoken, words, display=text), encoding="utf-8")
    # 5. 말 사이 웅얼거림 정리(lib/tts_gate.py WHY) — 원본은 narration_raw.mp3로 남긴다
    import json
    import shutil
    from lib.tts_gate import gaps_from_words, gate
    shutil.copy2(audio_path, out / "narration_raw.mp3")
    (out / "narration_words.json").write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    try:
        gate(audio_path, gaps_from_words(words))
    except subprocess.CalledProcessError as e:
        # 디코딩이 안 되는 응답(테스트 목 등)이면 원본을 그대로 둔다 — 조용히 넘기지 않고 남긴다
        logging.getLogger(__name__).warning("[typecast] 쉼 정리 실패 — 원본 음성 그대로: %s", e)
    return {"audio_path": str(audio_path), "srt_path": str(srt_path), "duration": offset,
            "word_count": len(words), "words": words}


if __name__ == "__main__":
    import sys

    args = [a for a in sys.argv[1:] if a != "--approved"]
    if len(args) != 1:
        sys.exit("사용법: .venv/bin/python3 -m lib.typecast_tts <topic> --approved  (사용자가 뽑으라고 한 topic만)")
    t = args[0]
    r = synthesize(t, (tracks.data_dir(t) / "narration.txt").read_text(encoding="utf-8").strip(),
                   approved="--approved" in sys.argv)
    print(f"[typecast] {t}: {r['duration']:.1f}초, 단어 {r['word_count']}개 → {r['audio_path']}")
