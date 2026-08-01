# 실물 사진 자동 소싱 (Pexels + Unsplash API). WHY: assets_library/real/은 지금까지 사용자가
# 직접 제공하거나 수동으로 소싱해왔는데, 검색 자동화 후 후보 몇 장을 받아서 Claude가 직접
# 눈으로 보고 고르는 반자동 흐름으로 바꾼다 — 완전 무인 자동화는 엉뚱한 사진이나 화질/구도
# 문제가 섞일 수 있어 위험하다는 판단(2026-08-01). 두 소스를 같이 쓰는 이유: 한식/특정 국물
# 요리 등은 재고가 한 소스에만 있거나 아예 없는 경우가 꽤 있어서, 한쪽에서 안 나오면 다른
# 쪽에서 보완한다. Pexels License·Unsplash License 둘 다 상업적 이용(이 프로젝트처럼 제휴
# 마케팅으로 수익화하는 콘텐츠 포함)을 명시적으로 허용해 라이선스 걱정 없이 쓸 수 있다.
#
# ⚠️ 검색어는 호출하는 쪽(Claude)이 영어로 번역해서 넘길 것 — 두 API 다 한글 검색은 결과가
# 거의 안 나온다. 정확한 한식 메뉴명으로 검색해서 후보가 부실하거나 없으면, 더 넓은 상위
# 개념(예: "설렁탕" → "korean beef bone soup"로도 안 나오면 "bone broth soup"까지 넓힘)으로
# 재검색해서 "비슷하게라도 맞는" 사진을 쓸지는 Claude가 후보를 직접 보고 판단한다 — 이 판단을
# 코드에 규칙으로 박아두지 않고 매번 호출하는 쪽에서 유연하게 정한다.
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_URL = "https://api.pexels.com/v1/search"
UNSPLASH_URL = "https://api.unsplash.com/search/photos"
CANDIDATE_DIR = Path(__file__).resolve().parent.parent / "assets_library" / "real" / "_candidates"


def _search_pexels(query: str, count: int) -> list[tuple[str, str]]:
    """(파일명 접두어, 이미지 URL) 튜플 리스트 반환. 키 없으면 조용히 빈 리스트."""
    if not os.environ.get("PEXELS_API_KEY"):
        return []
    resp = requests.get(
        PEXELS_URL,
        headers={"Authorization": os.environ["PEXELS_API_KEY"]},
        params={"query": query, "per_page": count, "orientation": "portrait"},
    )
    resp.raise_for_status()
    photos = resp.json().get("photos", [])
    return [(f"pexels_{i:02d}", p["src"]["large2x"]) for i, p in enumerate(photos, start=1)]


def _search_unsplash(query: str, count: int) -> list[tuple[str, str]]:
    if not os.environ.get("UNSPLASH_ACCESS_KEY"):
        return []
    resp = requests.get(
        UNSPLASH_URL,
        headers={"Authorization": f"Client-ID {os.environ['UNSPLASH_ACCESS_KEY']}"},
        params={"query": query, "per_page": count, "orientation": "portrait"},
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return [(f"unsplash_{i:02d}", r["urls"]["regular"]) for i, r in enumerate(results, start=1)]


def search_candidates(query: str, count: int = 5, source: str = "both") -> list[str]:
    """query(영어)로 Pexels·Unsplash에서 사진을 검색해 각 소스별 상위 count장을
    assets_library/real/_candidates/<query>/에 다운로드하고 로컬 경로 리스트를 반환한다.
    source: "pexels" | "unsplash" | "both"(기본값). 숏폼 세로 영상 배경용이라 portrait로 검색.

    다운로드 후에는 Read 도구로 직접 후보들을 눈으로 확인하고, 고른 사진만
    assets_library/real/<품목>_real_NN.jpg로 옮긴 뒤 나머지 후보와 _candidates 폴더는 지운다.
    두 소스 다 결과가 부실하면 더 넓은 검색어로 재호출해서 다시 판단할 것."""
    candidates: list[tuple[str, str]] = []
    if source in ("pexels", "both"):
        candidates += _search_pexels(query, count)
    if source in ("unsplash", "both"):
        candidates += _search_unsplash(query, count)

    if not candidates:
        print(f"[real_photo_sourcing] '{query}' 검색 결과 없음 (API 키 미설정이거나 결과 0건)")
        return []

    out_dir = CANDIDATE_DIR / query
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, url in candidates:
        img_resp = requests.get(url)
        img_resp.raise_for_status()
        out_path = out_dir / f"{name}.jpg"
        out_path.write_bytes(img_resp.content)
        paths.append(str(out_path))
        print(f"[real_photo_sourcing] 후보 저장: {out_path}")
    return paths


if __name__ == "__main__":
    query = sys.argv[1]
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    source = sys.argv[3] if len(sys.argv) > 3 else "both"
    search_candidates(query, count, source)
