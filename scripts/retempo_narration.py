#!/usr/bin/env python3
"""이미 뽑은 나레이션의 배속만 바꾼다 — 음높이는 그대로 두고 늘이고(atempo), 자막·단어 시각도 같은 비율로 늘인다.

WHY(2026-10-07 사용자 "속도만 1.2배에서 1.1배로 줄이자" → "다시 뽑지 말고 뽑은 거 기준으로 1.1배로 바꾸는 건 안 됨?"):
TTS를 다시 뽑으면 크레딧이 든다. 이미 1.2배로 뽑은 음성을 1.1/1.2 배속으로 늘이면 같은 결과가 나온다. narration.mp3만 늘이고
srt·words를 그대로 두면 자막이 점점 앞당겨지므로 함께 바꾼다. narration_raw.mp3(웅얼거림 정리 전 원본)도 늘인다 —
gate_narration_pauses가 raw와 words를 짝지어 다시 정리하므로 하나만 늘이면 엉뚱한 자리가 무음이 된다.
원본은 output/<topic>/_tempo_<옛 배속>/에 남긴다.

    .venv/bin/python3 scripts/retempo_narration.py 피부_28 피부_29 --from 1.2 --to 1.1
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks  # noqa: E402

_T = re.compile(r"(\d{2}):(\d{2}):(\d{2}),(\d{3})")


def _scale_srt(text: str, k: float) -> str:
    def sub(m: re.Match) -> str:
        ms = (int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3])) * 1000 + int(m[4])
        ms = round(ms * k)
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    return _T.sub(sub, text)


def retempo(topic: str, src: float, dst: float) -> float:
    out = tracks.output_dir(topic)
    audio, srt, words = out / "narration.mp3", out / "narration.srt", out / "narration_words.json"
    raw = out / "narration_raw.mp3"
    if not audio.exists() or not srt.exists():
        raise SystemExit(f"❌ {topic}: narration.mp3·srt가 없다")
    keep = out / f"_tempo_{src:g}"
    if keep.exists():
        raise SystemExit(f"❌ {topic}: {keep.name}이 이미 있다 — 같은 배속 변환을 두 번 하면 두 번 느려진다")
    keep.mkdir()
    for f in (audio, raw, srt, words):
        if f.exists():
            shutil.copy2(f, keep / f.name)
    factor = dst / src                 # atempo 배속(<1이면 느려진다)
    k = src / dst                      # 시각은 그만큼 늘어난다
    for f in (audio, raw):
        if not (keep / f.name).exists():
            continue
        tmp = out / "narration.retempo.mp3"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(keep / f.name), "-af", f"atempo={factor:.6f}",
                        "-c:a", "libmp3lame", "-b:a", "192k", str(tmp)], check=True)
        tmp.replace(f)
    srt.write_text(_scale_srt((keep / srt.name).read_text(encoding="utf-8"), k), encoding="utf-8")
    if (keep / words.name).exists():
        ws = json.loads((keep / words.name).read_text(encoding="utf-8"))
        for w in ws:
            w["start"], w["end"] = round(w["start"] * k, 3), round(w["end"] * k, 3)
        words.write_text(json.dumps(ws, ensure_ascii=False), encoding="utf-8")
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(audio)],
                                capture_output=True, text=True, check=True).stdout.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="+")
    ap.add_argument("--from", dest="src", type=float, required=True)
    ap.add_argument("--to", dest="dst", type=float, required=True)
    a = ap.parse_args()
    for t in a.topics:
        print(f"✅ {t}: {a.src:g}배 → {a.dst:g}배, {retempo(t, a.src, a.dst):.1f}초")


if __name__ == "__main__":
    main()
