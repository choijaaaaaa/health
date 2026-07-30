# 품목명 → 캐릭터 일러스트 자동 생성 (Gemini API). WHY: 지금까지 수작업으로 만든
# 캐릭터들(양파/사과/가지 등)과 톤을 맞추기 위해 스타일 프롬프트를 고정해둔다.
# ⚠️ 모델명은 Gemini 쪽이 자주 바뀜 — 요청 실패 시 MODEL 상수만 교체하면 됨.
from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
# ⚠️ Imagen 4 Fast/Standard($0.02~0.04/장)이 제일 싸지만 "신규 사용자에게 더 이상
# 제공 안 함" 404가 떠서 못 씀(2026-07-30 확인) — 그다음으로 저렴한 이 모델로 확정.
MODEL = "gemini-3.1-flash-lite-image"  # ~$0.0336/장
LIBRARY_DIR = Path(__file__).resolve().parent.parent / "assets_library" / "illust"

STYLE_PROMPT = (
    "귀여운 3D 카툰 스타일 캐릭터 일러스트. 대상: {item}. "
    "동글동글하고 표정이 풍부한 눈코입(웃는 얼굴), 자연스러운 팔다리(뿌리나 줄기 형태로 "
    "그 식재료 특성에 맞게), 배경은 부드럽게 블러 처리된 정원/밭 풍경. "
    "정사각형 구도, 텍스트나 글자는 절대 넣지 않음, 로고나 워터마크 없음."
)


def _headers():
    return {
        "x-goog-api-key": os.environ["GEMINI_API_KEY"],
        "Content-Type": "application/json",
    }


def generate_illustration(item_name: str, out_path: str | None = None) -> str:
    prompt = STYLE_PROMPT.format(item=item_name)
    resp = requests.post(
        f"{BASE_URL}/models/{MODEL}:generateContent",
        headers=_headers(),
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )
    resp.raise_for_status()
    data = resp.json()

    parts = data["candidates"][0]["content"]["parts"]
    image_part = next((p for p in parts if "inlineData" in p), None)
    if image_part is None:
        raise RuntimeError(f"[gemini] 이미지가 응답에 없음: {data}")

    image_bytes = base64.b64decode(image_part["inlineData"]["data"])

    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)
    out_path = out_path or str(LIBRARY_DIR / f"{item_name}_illust.jpg")
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    print(f"[gemini] {item_name} 일러스트 생성 완료: {out_path}")
    return out_path


if __name__ == "__main__":
    item_name = sys.argv[1]
    generate_illustration(item_name)
