# ⛔ 사용 중단(2026-09-18) — 이미지는 미드저니만 쓴다. 기록용으로만 보관.
# 캐논 스틸을 Gemini로 "편집"해 부위를 추가한다 — 구도·크롭을 원본과 동일하게 유지하는 게 목적.
# WHY(2026-09-18): 미드저니는 자궁·난소를 8장 연속 못 그렸고, Gemini로 새로 그리면 장기는 정확해도
# 몸 실루엣·크롭이 달라져 세트에서 튀었다. 기존 캐논을 입력으로 주고 "그대로 두고 X만 추가"로
# 시키면 구도가 원본과 같게 나온다(cu_pelvis → cu_pelvis_female로 검증).
#
# 사용: ../../.venv/bin/python3 gemini_edit_still.py <원본.jpg> <후보폴더> "<추가할 것 영어 설명>" [장수]
import base64, os, sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
MODEL = "gemini-3.1-flash-lite-image"

src, out_dir, what = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 3
out_dir.mkdir(parents=True, exist_ok=True)
prompt = (
    "Edit this image. Keep everything exactly as it is — the same framing, crop, camera angle, body outline, "
    "existing organs, bones, background and lighting — do not move, resize or redraw anything. Only add: "
    f"{what}. Render the added structures in exactly the same translucent soft pale cyan glass style as the "
    "existing ones, no brighter and no different color. No text, labels, arrows or watermarks."
)
data = base64.b64encode(src.read_bytes()).decode()
for i in range(n):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
        headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"},
        json={"contents": [{"parts": [{"inline_data": {"mime_type": "image/jpeg", "data": data}},
                                      {"text": prompt}]}]},
        timeout=180)
    r.raise_for_status()
    parts = r.json()["candidates"][0]["content"]["parts"]
    img = next((p for p in parts if "inlineData" in p), None)
    if img is None:
        print(f"e{i}: 이미지 없음 — {str(parts)[:160]}", file=sys.stderr)
        continue
    (out_dir / f"e{i}.png").write_bytes(base64.b64decode(img["inlineData"]["data"]))
    print(f"e{i}: {out_dir / f'e{i}.png'}")
