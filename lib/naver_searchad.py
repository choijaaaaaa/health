# 네이버 검색광고 API — 키워드별 월간 검색량을 받아 topic 선정·제목에 쓴다.
#
# WHY(2026-09-23 사용자 "네이버 클립은 사람들이 검색했던 검색어 기준으로 영상을 띄워주는 경향이 있다"):
# 자동완성(lib/naver_keywords.py)은 "어떤 말로 검색하는지"까지만 알려준다. 어느 쪽이 더 많이 검색되는지는
# 숫자가 있어야 정할 수 있어서 검색광고 API의 키워드도구(keywordstool)를 쓴다.
#
# 키 3개가 필요하다(.env):
#   NAVER_AD_API_KEY       액세스라이선스
#   NAVER_AD_SECRET        비밀키
#   NAVER_AD_CUSTOMER_ID   고객 ID(숫자)
# searchad.naver.com → 도구 → API 사용 관리에서 발급.
#
#   python3 -m lib.naver_searchad 담석증 위경련 "마운자로 부작용"
#   python3 -m lib.naver_searchad --from-keywords      # naver_keywords.json에 모아둔 것 전부
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
KEYWORDS = ROOT / "data" / "_audit" / "naver_keywords.json"
OUT = ROOT / "data" / "_audit" / "naver_search_volume.json"
BASE = "https://api.searchad.naver.com"
# WHY 한 번에 5개인지: keywordstool은 hintKeywords를 최대 5개까지 받는다(초과 시 400).
BATCH = 5


def _headers(method: str, path: str) -> dict:
    load_dotenv(ROOT / ".env")
    key, secret, cid = (os.environ["NAVER_AD_API_KEY"], os.environ["NAVER_AD_SECRET"],
                        os.environ["NAVER_AD_CUSTOMER_ID"])
    ts = str(round(time.time() * 1000))
    sign = base64.b64encode(hmac.new(secret.encode(), f"{ts}.{method}.{path}".encode(),
                                     hashlib.sha256).digest()).decode()
    return {"X-Timestamp": ts, "X-API-KEY": key, "X-Customer": cid, "X-Signature": sign}


def volumes(keywords: list[str]) -> list[dict]:
    """[{keyword, pc, mobile, total, competition}] — 검색량은 월간, '< 10'은 0으로 본다.

    🚨 **`~부작용` 복합어는 실제 수요와 무관하게 항상 0으로 돌아온다**(2026-09-23 실측:
    위고비 86,800인데 위고비부작용 0, 타이레놀 59,300인데 타이레놀부작용 0, 마운자로부작용·
    스테로이드부작용·임플란트부작용도 전부 0). 광고를 집행할 수 없는 키워드라 API가 데이터를
    주지 않는 것이지 아무도 안 찾는다는 뜻이 아니다 — 자동완성(`lib/naver_keywords.py`)에는
    "마운자로 부작용"이 상위로 뜬다. **부작용 계열은 이 숫자로 폐기 판정을 하지 말 것.**
    """
    out: list[dict] = []
    for i in range(0, len(keywords), BATCH):
        chunk = [k.replace(" ", "") for k in keywords[i:i + BATCH]]   # API는 공백을 싫어한다
        r = requests.get(f"{BASE}/keywordstool", params={"hintKeywords": ",".join(chunk), "showDetail": 1},
                         headers=_headers("GET", "/keywordstool"), timeout=30)
        r.raise_for_status()
        for row in r.json().get("keywordList", []):
            def num(v):
                return 0 if isinstance(v, str) and "<" in v else int(v or 0)
            pc, mo = num(row.get("monthlyPcQcCnt")), num(row.get("monthlyMobileQcCnt"))
            out.append({"keyword": row.get("relKeyword"), "pc": pc, "mobile": mo, "total": pc + mo,
                        "competition": row.get("compIdx")})
        time.sleep(0.4)      # 공식 rate limit은 넉넉하지만 연타하지 않는다
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("keywords", nargs="*")
    ap.add_argument("--from-keywords", action="store_true", help="naver_keywords.json에 모인 키워드 전부 조회")
    ap.add_argument("--top", type=int, default=40, help="출력할 상위 개수")
    a = ap.parse_args()

    kws = list(a.keywords)
    if a.from_keywords and KEYWORDS.exists():
        data = json.loads(KEYWORDS.read_text(encoding="utf-8"))
        for seed, v in data.items():
            kws.append(seed)
            kws += v.get("keywords", [])
    kws = list(dict.fromkeys(k for k in kws if k))
    if not kws:
        raise SystemExit("키워드를 넘기거나 --from-keywords 를 쓸 것")

    rows = volumes(kws)
    rows.sort(key=lambda r: -r["total"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"updated_at": time.strftime("%Y-%m-%d %H:%M"), "rows": rows},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{'키워드':28s} {'월 검색량':>9s}  {'모바일 비중':>8s}  경쟁")
    for r in rows[:a.top]:
        share = f"{r['mobile'] / r['total'] * 100:.0f}%" if r["total"] else "-"
        print(f"{r['keyword'][:28]:28s} {r['total']:9,d}  {share:>8s}  {r['competition'] or '-'}")
    print(f"\n저장: {OUT.relative_to(ROOT)}  ({len(rows)}개)")


if __name__ == "__main__":
    main()
