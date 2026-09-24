#!/bin/bash
cd /Users/chlwjddms16/Desktop/project/health-shorts
.venv/bin/python3 - <<'PY' 2>&1 | grep -v "채널 기본"
import sys,pathlib
sys.path.insert(0,".")
from lib.fish_tts import synthesize
r=synthesize("비뇨기_16", pathlib.Path("data/비뇨기_16/narration.txt").read_text(encoding="utf-8").strip())
print(f"TTS {r['duration']:.1f}초")
PY
.venv/bin/python3 scripts/xray_build.py 비뇨기_16 --preview 2>&1 | grep -E "미리보기|shorts_xray|실패"
