import pathlib, sys, traceback, re
sys.path.insert(0, ".")
from lib.fish_tts import synthesize
for t in ["눈_8","머리_14","소화_13","소화_20","소화_21"]:
    txt = pathlib.Path(f"data/{t}/narration.txt").read_text(encoding="utf-8").strip()
    n = len(re.sub(r"\s","",txt))
    try:
        r = synthesize(t, txt)
        print(f"✅ {t:8s} {n}자 → {r['duration']:.1f}초", flush=True)
    except Exception:
        print(f"❌ {t}", flush=True); traceback.print_exc()
print("끝")
