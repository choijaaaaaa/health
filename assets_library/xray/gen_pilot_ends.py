# ⛔ 사용 중단(2026-09-18) — 이미지는 미드저니만 쓴다. 기록용으로만 보관.
# 파일럿 end 프레임 생성 — start(캐논)의 "재진술"이어야 하므로 새로 그리지 않고 Gemini로 편집한다.
# WHY: 카메라 무빙은 start/end 두 프레임의 차이가 만든다(SHOT_DESIGN_SYSTEM §1). end를 독립적으로
# 새로 그리면 모델이 서로 다른 두 장면으로 보고 사이를 못 잇는다(§2 "끝 프레임은 재진술").
import base64, os, sys, time
from pathlib import Path
import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE.parents[1] / ".env")
MODEL = "gemini-3.1-flash-lite-image"
KEEP = ("Keep the exact same translucent glass-like pale cyan style, the same organs and bones inside, the same "
        "smooth featureless face, the same dark slate blue-grey background and the same soft rim lighting. "
        "No text, labels, arrows or watermarks.")
# v2(2026-09-18): v1 end 자세가 약해서 Flow가 그 이상을 못 냈다 — 이미지가 이기므로 end 자세 자체를 극단으로.
JOBS = {
    "B2_end": ("stills/canon_organs.jpg",
              "Edit this image. The same figure from the same eye-level camera, now doubled over hard in pain: the torso "
              "folded forward almost horizontal, both arms wrapped tightly around the upper abdomen, one knee dropped low "
              "almost touching the floor, the other leg bent, the head hanging down toward the knees. The stomach glows "
              "intensely bright warm amber from within; every other organ stays soft pale cyan. " + KEEP),
    "C2_end": ("stills/canon_organs.jpg",
              "Edit this image. The same figure from the same eye-level camera, now losing balance from severe dizziness: "
              "the knees buckling, the whole body tipped about twenty-five degrees to the figure's left mid-stagger, one "
              "hand clutching the side of the head, the other arm flung out wide, one foot lifted off the floor. The brain "
              "inside the skull glows intensely bright warm amber; every other organ stays soft pale cyan. " + KEEP),
}
key = os.environ["GEMINI_API_KEY"]
out = HERE / "stills" / "_candidates" / "pilot"; out.mkdir(parents=True, exist_ok=True)
for name, (src, prompt) in JOBS.items():
    data = base64.b64encode((HERE / src).read_bytes()).decode()
    for i in range(2):
        # 429(분당 한도)는 잠깐 기다리면 풀린다 — 연속 편집 몇 장만 돌려도 걸린다(2026-09-18 실측)
        for attempt in range(6):
            r = requests.post(f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent",
                              headers={"x-goog-api-key": key, "Content-Type": "application/json"},
                              json={"contents": [{"parts": [{"inline_data": {"mime_type": "image/jpeg", "data": data}},
                                                            {"text": prompt}]}]}, timeout=180)
            if r.status_code != 429:
                break
            print(f"{name} {i}: 429, {20 * (attempt + 1)}초 대기", file=sys.stderr)
            time.sleep(20 * (attempt + 1))
        r.raise_for_status()
        img = next((p for p in r.json()["candidates"][0]["content"]["parts"] if "inlineData" in p), None)
        if img is None:
            print(name, i, "이미지 없음", file=sys.stderr); continue
        (out / f"{name}_{i}.png").write_bytes(base64.b64decode(img["inlineData"]["data"]))
        print(name, i, "ok")
