# 타입캐스트 TTS — API는 부르지 않고(_call 목), 자막이 원문 숫자로 뜨는지·여러 번 부를 때 시각이 이어지는지 본다.
from pathlib import Path

import pytest

from lib import fish_tts, tracks, typecast_tts


def _fake_call(text: str):
    words, t = [], 0.0
    for w in text.split():
        words.append({"text": w, "start": t, "end": t + 0.5})
        t += 0.6
    return b"ID3", words, t


def test_srt_shows_original_numbers(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(typecast_tts, "_call", _fake_call)
    monkeypatch.setattr(tracks, "output_dir", lambda _t: tmp_path)
    r = typecast_tts.synthesize("소화_99", "7명 중 1명꼴로 겪어요. 물은 500ml 드세요.", approved=True)
    srt = (tmp_path / "narration.srt").read_text(encoding="utf-8")
    assert "7명 중 1명꼴로 겪어요." in srt and "500ml" in srt
    assert srt.count("-->") == 2
    assert r["word_count"] > 0


def test_chunks_keep_time_continuous(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(typecast_tts, "_call", _fake_call)
    monkeypatch.setattr(typecast_tts, "MAX_CHARS_PER_CALL", 10)
    monkeypatch.setattr(typecast_tts, "_concat_mp3", lambda parts, dst: dst.write_bytes(b"".join(parts)))
    monkeypatch.setattr(tracks, "output_dir", lambda _t: tmp_path)
    r = typecast_tts.synthesize("소화_99", "첫 문단이에요.\n\n둘째 문단이에요.", approved=True)
    starts = [w["start"] for w in r["words"]]
    assert starts == sorted(starts) and starts[-1] > 1.0


def test_fish_refuses_korean():
    with pytest.raises(ValueError, match="typecast"):
        fish_tts.synthesize("소화_99", "안녕하세요.")


def test_refuses_without_user_approval(monkeypatch):
    monkeypatch.setattr(typecast_tts, "_call", lambda _t: pytest.fail("승인 없이 API를 불렀다"))
    with pytest.raises(PermissionError):
        typecast_tts.synthesize("소화_99", "안녕하세요.")
