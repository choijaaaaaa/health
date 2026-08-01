# 품목명 → 캐릭터 일러스트 자동 생성 (Gemini API). WHY: 지금까지 수작업으로 만든
# 캐릭터들(양파/사과/가지 등)과 톤을 맞추기 위해 스타일 프롬프트를 고정해둔다.
# ⚠️ 모델명은 Gemini 쪽이 자주 바뀜 — 요청 실패 시 MODEL 상수만 교체하면 됨.
from __future__ import annotations

import base64
import os
import random
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

# 2026-07-30 검증 완료: 이 프롬프트(눈코입 큼직하게)로 만든 돼지감자 캐릭터가
# Kling 모션 생성에서 입 위치 오류·눈 왜곡 없이 안정적으로 나온 첫 케이스(v7) —
# 이후 새 캐릭터도 이 기본 프롬프트 그대로 쓸 것, 임의로 수정하지 말 것.
# WHY 배경색을 흰색 대신 크로마키로: 흰 배경 + colorkey 조합은 캐릭터 얼굴의 밝은
# 하이라이트(이마·볼)까지 "흰색에 가깝다"고 오인해서 구멍이 뚫리는 문제가 있었다
# (2026-07-30 돼지감자차_1에서 실사진 합성 시 확인).
# ⚠️ 크로마키 색은 초록 고정이 아니라 캐릭터 색상 보고 매번 판단할 것(2026-07-31,
# 사용자 지적: "항상 초록색이면 안된다, 오이같은거면 초록으로하면 씹창난다") —
# 오이·상추·브로콜리·시금치처럼 캐릭터 자체가 초록 계열이면 초록 배경과 겹쳐서
# colorkey가 캐릭터 몸통까지 지워버리니 그 색은 후보에서 뺀다.
# ⚠️ 안전한 색이 여럿이어도 항상 초록만 쓰지 말 것(2026-08-01, "죄다 초록색이니까
# 인스타에서 보기가 좀 그렇네" 피드백) — 아래 pick_bg_color()로 안 겹치는 후보
# 중에서 매번 무작위로 고른다. 캐릭터 색이 뭐랑 겹치는지 판단하는 것 자체는
# 여전히 세션이 직접 해서 avoid에 넘겨야 한다(자동 색상 인식 아님).
STYLE_PROMPT = (
    "귀여운 3D 카툰 스타일 캐릭터 일러스트. 대상: {item}. "
    "눈, 코, 입은 얼굴 크기 대비 큼직하고 뚜렷하게 그려서(특히 입은 벌렸을 때 표정이 확실히 "
    "구분되도록 큼직하게) 표정이 잘 읽히게 한다. 팔다리는 그리지 않는다(뿌리/줄기 형태의 몸통만). "
    "배경은 크로마키 합성용 순수 {bg_color_name}색({bg_color_hex}) 단색으로만 — 캐릭터 자체 "
    "색상과 절대 겹치지 않는 선명한 {bg_color_name}이어야 하고, 배경에 다른 사물이나 그라디언트, "
    "그림자 무늬를 넣지 않는다. "
    "정사각형 구도, 텍스트나 글자는 절대 넣지 않음, 로고나 워터마크 없음."
)

# WHY 랜덤 배경색(2026-08-01): 여태 안전한 캐릭터(갈색/베이지 등)엔 매번 기본값 초록을
# 그대로 썼더니, 캐릭터 배지가 인스타 피드에 연달아 올라올 때 죄다 초록빛 톤으로
# 비슷해 보인다는 피드백 — 안전한 색이 여러 개면 그중 하나로 고정하지 말고 매번
# 랜덤으로 고른다(타입캐스트 보이스 랜덤 선택과 같은 패턴). 지금까지 만든 캐릭터는
# 이미 과금 완료된 상태라 재작업 안 함, 새 캐릭터부터 적용.
# WHY 5색으로 확장(2026-08-01, "3색? 좀더 다양화좀 안되나"): colorkey 자체는 어떤
# 색이든 잘 빠지지만, `video_assembler.py`의 despill 필터(가장자리 잔여 색 억제)는
# ffmpeg 자체 제약으로 green/blue 타입만 있다 — 마젠타는 이미 despill 없이도
# 실사용 중이라(가장자리에 아주 약한 색 번짐 감수), 같은 조건인 시안·보라도
# 추가함. 노랑·주황·빨강처럼 흔한 식재료 색은 캐릭터와 겹칠 확률이 너무 높아서
# 후보에서 뺐다 — 이 5색은 전부 음식 캐릭터 색과 잘 안 겹치는 축에 속한다.
BG_COLOR_CANDIDATES = [
    ("초록", "#00FF00"),   # despill 지원
    ("파란", "#0000FF"),   # despill 지원
    ("마젠타", "#FF00FF"),  # despill 없음(기존부터 이 상태로 실사용 중)
    ("시안", "#00FFFF"),    # despill 없음
    ("보라", "#AA00FF"),    # despill 없음
]


def pick_bg_color(avoid: list[str] | None = None) -> tuple[str, str]:
    """캐릭터 색상과 겹치는 후보를 avoid(색 이름, 예: ["초록"])로 빼고 나머지 중
    무작위로 (bg_color_name, bg_color_hex)를 고른다. 캐릭터 색을 판단하는 건 이
    함수가 아니라 호출하는 쪽(세션)의 몫 — 예: 오이·상추·브로콜리처럼 초록 계열
    캐릭터면 avoid=["초록"]으로 호출. 후보가 다 제외되면(캐릭터 색이 5색 다
    겹치는 특이 케이스) ValueError를 내니, 그런 경우엔 이 후보 밖의 색을 직접
    정해서 generate_illustration()에 명시로 넘길 것."""
    candidates = [c for c in BG_COLOR_CANDIDATES if c[0] not in (avoid or [])]
    if not candidates:
        raise ValueError(f"모든 기본 배경색 후보가 avoid에 걸림: {avoid} — 직접 색을 정해서 호출할 것")
    return random.choice(candidates)


def _headers():
    return {
        "x-goog-api-key": os.environ["GEMINI_API_KEY"],
        "Content-Type": "application/json",
    }


def generate_illustration(
    item_name: str,
    out_path: str | None = None,
    bg_color_name: str = "초록",
    bg_color_hex: str = "#00FF00",
) -> str:
    """bg_color_name/bg_color_hex: 캐릭터 자체 색상과 겹치지 않는 크로마키 배경색을
    호출자가 판단해서 넘긴다 — 캐릭터가 초록 계열(오이·상추 등)이면 파란색이나
    마젠타로 바꿔서 호출할 것(기본값 초록은 갈색/베이지 계열 채소·과일 기준)."""
    prompt = STYLE_PROMPT.format(item=item_name, bg_color_name=bg_color_name, bg_color_hex=bg_color_hex)
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


def edit_illustration(base_image_path: str, instruction: str, out_path: str) -> str:
    """기존 이미지를 조건으로 넣어 특정 부분만 바꾼다. WHY: 텍스트만으로 새로 생성하면
    캐릭터 정체성(몸 형태·색감)이 매번 달라질 수 있다(2026-07-30 확인 — 눈코입만 키우려
    했는데 몸 전체 디자인이 바뀐 사례) — 원본 이미지를 같이 보내서 "이 부분만" 바꾸도록
    조건을 걸면 나머지가 훨씬 안정적으로 유지된다(입모양 변형 세트 만들 때 썼던 것과 동일한 기법)."""
    with open(base_image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    resp = requests.post(
        f"{BASE_URL}/models/{MODEL}:generateContent",
        headers=_headers(),
        json={"contents": [{"parts": [
            {"inline_data": {"mime_type": "image/jpeg", "data": image_b64}},
            {"text": instruction},
        ]}]},
    )
    resp.raise_for_status()
    data = resp.json()

    parts = data["candidates"][0]["content"]["parts"]
    image_part = next((p for p in parts if "inlineData" in p), None)
    if image_part is None:
        raise RuntimeError(f"[gemini] 이미지가 응답에 없음: {data}")

    image_bytes = base64.b64decode(image_part["inlineData"]["data"])
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    print(f"[gemini] 이미지 편집 완료: {out_path}")
    return out_path


if __name__ == "__main__":
    item_name = sys.argv[1]
    generate_illustration(item_name)
