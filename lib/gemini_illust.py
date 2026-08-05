# 품목명 → 캐릭터 일러스트 자동 생성 (Gemini API). WHY: 지금까지 수작업으로 만든
# 캐릭터들(양파/사과/가지 등)과 톤을 맞추기 위해 스타일 프롬프트를 고정해둔다.
# ⚠️ 모델명은 Gemini 쪽이 자주 바뀜 — 요청 실패 시 MODEL 상수만 교체하면 됨.
from __future__ import annotations

import base64
import os
import random
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image

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


def recolor_background(image_path, avoid: list[str] | None = None, out_path=None) -> tuple[str, str]:
    """이미 생성된 캐릭터 일러스트의 배경색만 다른 색으로 바꾼다 — 캐릭터 자체
    (Gemini로 그린 픽셀)는 건드리지 않으니 재생성 비용이 안 든다.
    WHY(2026-08-01, "만들어진 아이템 기준으로 배경 색상 씌우는거면 지금 만들어진
    것들도 수정 가능한거 아닌가" 요청): 배경은 크로마키용 단색 한 장이라, 영상
    합성 때 colorkey로 제거되는 것과 동일한 방식으로 배경만 골라내서 다른 단색
    으로 다시 칠하면 된다. 배경 판정은 `card_news.py`의 `_remove_chroma_bg`
    자동감지와 같은 방식(좌상단 모서리 픽셀을 키 색으로 채택 + 거리 임계값)."""
    img = Image.open(image_path).convert("RGB")
    px = img.load()
    w, h = img.size
    bg_key = px[2, 2]
    name, hex_ = pick_bg_color(avoid)
    new_rgb = tuple(int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    thresh = 160
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y]
            if abs(r - bg_key[0]) + abs(g - bg_key[1]) + abs(b - bg_key[2]) < thresh:
                px[x, y] = new_rgb
    img.save(out_path or image_path, quality=95)
    return name, hex_


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
    force: bool = False,
) -> str:
    """bg_color_name/bg_color_hex: 캐릭터 자체 색상과 겹치지 않는 크로마키 배경색을
    호출자가 판단해서 넘긴다 — 캐릭터가 초록 계열(오이·상추 등)이면 파란색이나
    마젠타로 바꿔서 호출할 것(기본값 초록은 갈색/베이지 계열 채소·과일 기준).

    WHY out_path에 파일이 이미 있으면 API를 아예 안 부르는지(2026-08-05, "이쪽도
    돈 계속 나간다" — 최적화 요청): "새 캐릭터 만들기 전 ls assets_library/illust/로
    확인" 규칙이 세션이 매번 기억해서 손으로 확인해야 하는 절차였다 — 실제로 이전에
    같은 캐릭터가 언어 세션마다 중복 생성돼서(이어폰·면봉·바나나 등) 비용이 샌
    이력이 있다(CLAUDE.md 참고). 존재 여부 확인을 코드 레벨 가드로 옮기면 깜빡하고
    또 호출해도 돈이 안 나간다 — 의도적으로 다시 그리고 싶으면 force=True로 명시."""
    out_path = out_path or str(LIBRARY_DIR / f"{item_name}_illust.jpg")
    if not force and Path(out_path).exists():
        print(f"[gemini] {item_name} 일러스트 이미 있음, 생성 스킵: {out_path} (재생성하려면 force=True)")
        return out_path

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


# WHY 정지 이미지 루프 폴백(2026-08-03, "이런 쓰레기같은 품질의 이미지를 스스로
# 판단하고 답없으면 그냥 제미나이가 생성한 움직이지 않는 이미지를 쓰게 만들어줄수있어?"):
# Kling image2video는 둥글고 팔다리 없는 디자인일수록 5초 안에 형태가 무너지는 경우가
# 실제로 있었다(우메보시_motion.mp4/버터_motion.mp4/된장국_motion.mp4에서 실측 확인 —
# 캐릭터가 옆모습으로 돌아가며 없어야 할 팔다리가 생기거나, 아예 다른 실사 사진으로
# 바뀌어버리는 정체성 붕괴). Kling 모션을 만든 뒤엔 반드시 프레임 몇 장을 뽑아서
# (ffmpeg -vf fps=... 로) 육안 검수하고, 캐릭터 정체성이 무너지는 프레임이 하나라도
# 있으면 그 Kling 결과물은 버리고 이 함수로 정지 루프를 만들어 대신 쓴다 — 자동 판단은
# 코드가 아니라(육안 없이는 "형태가 무너졌다"를 픽셀 규칙만으로 신뢰성 있게 감지하기
# 어려움) 매번 프레임을 실제로 보는 세션/서브에이전트가 판단할 것. Kling 모션 클립과
# 똑같은 해상도(960x960)·프레임레이트(30fps)·길이(~5.1초)로 만들어서 이후
# video_assembler.py의 ping-pong·chroma-key 처리 파이프라인이 출처(Kling vs 정지
# 루프)와 무관하게 동일하게 동작한다.
def build_static_motion_loop(illust_path: str, out_path: str, duration: float = 5.1) -> str:
    """Kling을 아예 안 쓰거나(비용 절감) Kling 결과가 불량 판정났을 때 쓰는 대체
    모션 클립 — 캐릭터가 전혀 움직이지 않는 정지 루프. 크로마키 배경은 원본
    일러스트 그대로 유지되므로 video_assembler.py의 colorkey 로직이 그대로 먹힌다."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-loop", "1", "-i", str(illust_path),
            "-t", str(duration), "-r", "30",
            "-vf", "scale=960:960",
            "-pix_fmt", "yuv420p", str(out_path),
        ],
        check=True, capture_output=True,
    )
    print(f"[gemini_illust] 정지 이미지 루프 생성 완료(Kling 대체): {out_path}")
    return out_path


if __name__ == "__main__":
    item_name = sys.argv[1]
    force = "--force" in sys.argv[2:]
    generate_illustration(item_name, force=force)
