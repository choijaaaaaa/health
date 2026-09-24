#!/bin/bash
# TTS → 시간표 구절 확인 → 조립. 순차로만 — 병렬은 로드 30 넘겨서 다 멈춘다.
cd /Users/chlwjddms16/Desktop/project/health-shorts
.venv/bin/python3 - <<'PY' 2>&1 | grep -vE "채널 기본"
import sys, pathlib
sys.path.insert(0, ".")
from lib.fish_tts import synthesize
for t in pathlib.Path("scratchpad/stale.txt").read_text(encoding="utf-8").split():
    try:
        r = synthesize(t, pathlib.Path(f"data/{t}/narration.txt").read_text(encoding="utf-8").strip())
        print(f"✅ TTS {t} {r['duration']:.1f}초", flush=True)
    except Exception as e:
        print(f"❌ TTS {t}: {e}", flush=True)
PY
# 훅 끝 시각으로 opening_until 재정렬 + 깨진 구절 확인
.venv/bin/python3 - <<'PY'
import json, pathlib, sys
sys.path.insert(0, ".")
from lib.xray_timeline import _cues
for p in sorted(pathlib.Path("data").glob("*/xray.json")):
    t = p.parent.name
    try: cues = _cues(t)
    except Exception: continue
    if not cues: continue
    d = json.loads(p.read_text(encoding="utf-8"))
    if "opening_until" not in d: continue
    want = round(cues[0][1], 2)
    if abs(d["opening_until"] - want) > 0.05:
        d["opening_until"] = want
        p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"  opening_until 보정 {t} → {want}")
    txt = " ".join(c[2] for c in cues)
    miss = [r["from"] for r in d.get("timeline", []) if r["from"] not in txt]
    if miss: print(f"  ⚠️ {t} 구절 누락 {miss}")
PY
for t in 비뇨기_16 대사_22 순환_12 눈_8 머리_14 고령_15; do
  echo "=== $t ==="
  .venv/bin/python3 scripts/xray_build.py "$t" --preview 2>&1 | grep -E "미리보기|shorts_xray|⚠️|실패|부족"
done
.venv/bin/python3 scripts/stage_for_deploy.py 2>&1 | tail -2
echo "큐 끝"
