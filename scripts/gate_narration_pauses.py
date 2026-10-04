#!/usr/bin/env python3
"""이미 뽑은 나레이션의 '말 사이' 웅얼거림을 정리한다(lib/tts_gate.py WHY). 원본은 narration_raw.mp3로 한 번만 보관.

    .venv/bin/python3 scripts/gate_narration_pauses.py 육아_17 근골격_16 …

단어 시각(narration_words.json)이 있으면 문장 안 쉼까지, 없으면 srt 문장 사이 쉼만 정리한다.
⚠️ 음성이 바뀌면 영상보다 새것이 돼 미션컨트롤 목록에서 빠진다 — 정리한 topic은 다시 조립할 것.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib import tracks  # noqa: E402
from lib.tts_gate import gaps_from_srt, gaps_from_words, gate  # noqa: E402


def main(topics: list[str]) -> None:
    for t in topics:
        out = tracks.output_dir(t)
        mp3, raw = out / "narration.mp3", out / "narration_raw.mp3"
        if not mp3.exists():
            print(f"✗ {t}: narration.mp3 없음"); continue
        if not raw.exists():
            shutil.copy2(mp3, raw)
        wj = out / "narration_words.json"
        gaps = gaps_from_words(json.loads(wj.read_text(encoding="utf-8"))) if wj.exists() else gaps_from_srt(out / "narration.srt")
        n = gate(raw, gaps, out=mp3)
        print(f"✓ {t}: 쉼 {n}곳 정리 ({'단어' if wj.exists() else '문장'} 기준)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1:])
