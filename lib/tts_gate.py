# 나레이션의 '말 사이' 구간을 조용히 만든다. WHY(2026-10-04 사용자 "요로 끝나는 문장이 병신같은 소리… 35초랑 8~9초"):
# 타입캐스트(필재)가 문장 끝 "~요" 뒤 쉬는 자리에 목소리 높이(≈100Hz)의 웅얼거림을 남긴다 — 육아_17 실측
# -32~-45dB(정상 무음은 -60dB 아래), 1.0배속으로 뽑아도 같아서 배속 탓이 아니다. 단어 시각을 알고 있으니
# 쉼 가운데만 잘라 낸다. 단어 시작점 바로 앞을 자르면 첫 음절이 날아가므로(fish_tts 계보) 양쪽에 여유를 둔다.
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

import numpy as np

SR = 48000
MIN_GAP = 0.18      # 이보다 짧은 쉼은 건드리지 않는다(단어 사이 숨은 자연스러운 이음)
HEAD = 0.08         # 앞 단어 끝 뒤로 남기는 여유 — "요"의 자연스러운 꼬리
TAIL = 0.05         # 다음 단어 시작 앞 여유 — 첫 음절 보호
FADE = 0.03


def gaps_from_words(words: list[dict]) -> list[tuple[float, float]]:
    return [(a["end"], b["start"]) for a, b in zip(words, words[1:]) if b["start"] - a["end"] >= MIN_GAP]


def gaps_from_srt(srt_path: Path) -> list[tuple[float, float]]:
    """srt 항목(=문장) 사이 쉼. 항목 시각은 타입캐스트 단어 시각에서 나온 것이라 문장 끝·시작과 맞다."""
    def sec(t: str) -> float:
        h, m, rest = t.split(":"); s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    cues = []
    for block in srt_path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.splitlines()
        if len(lines) >= 2 and "-->" in lines[1]:
            a, b = lines[1].split(" --> ")
            cues.append((sec(a.strip()), sec(b.strip())))
    return [(e, s) for (_, e), (s, _) in zip(cues, cues[1:]) if s - e >= MIN_GAP]


def gate(audio: Path, gaps: list[tuple[float, float]], out: Path | None = None) -> int:
    """gaps 안쪽(앞 HEAD, 뒤 TAIL 여유를 뺀 구간)을 FADE로 페이드해 무음으로 만든다. 바꾼 구간 수를 돌려준다."""
    out = out or audio
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(audio), "-ac", "1", "-ar", str(SR),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    env = np.ones_like(x)
    nf = int(FADE * SR)
    done = 0
    for e, s in gaps:
        a, b = int((e + HEAD) * SR), int((s - TAIL) * SR)
        if b - a <= 2 * nf:
            continue
        env[a:a + nf] = np.minimum(env[a:a + nf], np.linspace(1, 0, nf))
        env[a + nf:b - nf] = 0
        env[b - nf:b] = np.minimum(env[b - nf:b], np.linspace(0, 1, nf))
        done += 1
    y = (x * env).astype(np.float32)
    with tempfile.TemporaryDirectory() as td:
        pcm = Path(td) / "g.f32"
        pcm.write_bytes(y.tobytes())
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", str(pcm),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(out)], check=True)
    return done
