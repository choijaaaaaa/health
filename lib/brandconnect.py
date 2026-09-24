# 네이버 브랜드커넥트(쇼핑 커넥트) 상품 검색기 — topic 조사 단계에서 해결책 품목이 실제로 제휴 가능한지 확인한다.
#
# WHY(2026-09-19 사용자 지시): "좀 특이한 품목을 추천했는데 브랜드커넥트에 없어버리면 이걸 연동조차 할 수가
# 없는 상태" — 해결책 품목은 브랜드커넥트에 상품이 있을 때만 쓴다. 매 topic 조사 때 이 검사를 돌린다.
#
# WHY 이런 구조인지:
# - 브랜드커넥트는 공개 API가 없다. 상품 검색은 로그인한 브라우저에서만 되고, 페이지가 내부 요청
#   (gw-brandconnect.naver.com/affiliate/query/affiliate-products/search-by-query)으로 목록을 받는다.
#   그 요청을 직접 흉내 내면 403(x-space-id 등 페이지가 붙이는 헤더 필요)이라, 페이지를 열고 페이지가 받은
#   응답을 그대로 읽는다 — 우리가 헤더를 위조하지 않는다.
# - 로그인은 사용자의 실제 Google Chrome(전용 프로필)에서 한다. Playwright가 띄운 Chromium은 네이버 로그인이
#   끝까지 안 됐다(자동화 브라우저 감지로 보임, 2026-09-19 실측). 로그인된 Chrome에 로컬 디버그 포트로 붙기만 한다.
# - 링크 발급도 한다(2026-09-19 사용자 지시 "미션콘트롤에 내가직접하던 링크 발급까지 다 하는거야"). 페이지의
#   "링크 발급" 버튼을 실제로 눌러서 발급하고, 응답의 상품 ID가 고른 상품과 같을 때만 쓴다 — 버튼을 잘못 눌러
#   엉뚱한 상품 링크가 들어가면 수수료가 새는 데다 아무도 모른다. 이미 발급된 상품은 응답에 naver.me 링크가 온다.
# - 발급한 링크는 health-shorts Supabase global_product_links(market=naver)에 넣는다 — mission-control
#   "미등록 링크" 칸과 대시보드가 읽는 곳. 사용자가 직접 넣어둔 링크는 절대 덮어쓰지 않는다.
# - 네이버 로그인 세션은 이 맥의 ~/.config/health-shorts/brandconnect-chrome에만 있다. 서버·저장소에 두지 않는다.
#
# 사용:
#   .venv/bin/python3 -m lib.brandconnect login              # 전용 Chrome 창을 띄운다(최초 1회 로그인)
#   .venv/bin/python3 -m lib.brandconnect search "저염 소금"
#   .venv/bin/python3 -m lib.brandconnect check <topic>      # platform_captions.json의 products 전부 검사
from __future__ import annotations

import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

from lib import tracks

ROOT = Path(__file__).resolve().parent.parent
PROFILE = Path.home() / ".config" / "health-shorts" / "brandconnect-chrome"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PORT = 9333        # 127.0.0.1 전용. ~/.claude/system-map.md에 등록
SPACE_ID = json.loads((ROOT / "data" / "affiliate_accounts.json").read_text())["naver_brandconnect_id"]
SEARCH_URL = "https://brandconnect.naver.com/{sid}/affiliate/products/search?query={q}&tab=product"
API_MARK = "affiliate-products/search-by-query"
PAUSE = (2.5, 5.0)   # 검색 사이 대기(초) — 사람이 직접 찾는 속도를 넘지 않게


def _cdp_up() -> bool:
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=2)
        return True
    except Exception:
        return False


def login() -> None:
    """전용 프로필로 실제 Chrome을 띄운다. 이미 떠 있으면 그대로 둔다."""
    if _cdp_up():
        print("[brandconnect] 전용 Chrome이 이미 떠 있음")
        return
    PROFILE.mkdir(parents=True, exist_ok=True)
    PROFILE.chmod(0o700)
    subprocess.Popen([CHROME, f"--user-data-dir={PROFILE}", f"--remote-debugging-port={PORT}",
                      "--remote-debugging-address=127.0.0.1", "--no-first-run", "--no-default-browser-check",
                      f"https://brandconnect.naver.com/{SPACE_ID}/affiliate/products"],
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(20):
        if _cdp_up():
            break
        time.sleep(0.5)
    print("[brandconnect] 전용 Chrome을 띄웠다 — 로그인이 풀려 있으면 그 창에서 로그인할 것(로그인 상태 유지 체크)")


def _norm(t: str) -> str:
    return re.sub(r"[\s·,/()\[\]-]", "", t).lower()


# 검색어에 그 말이 없으면 빼는 표현 — 가정용 건강 콘텐츠에 산업용 제습기(79만 원)·자동차 에어컨 필터가
# 뽑힌 실측 사례(2026-09-19). 강아지 밥그릇이 "위장약"에 걸린 것도 같은 부류다.
_OFF_CONTEXT = ("산업용", "업소용", "공업용", "영업용", "공장", "차량용", "자동차")
_PET_WORDS = ("반려견", "반려동물", "강아지", "고양이", "애견", "애묘", "반려묘", "펫")
# 검색어에 없는데 붙어 있으면 본품이 아니라 부속품이다(2026-09-19 전수 검토: 인공눈물→보관통, 필박스→쉐이커 깔대기,
# 식염수 스프레이→300원 빈 분무 용기)
_ACCESSORY = ("케이스", "보관통", "보관함", "공병", "소분", "분무 용기", "용기", "파우치", "홀더", "깔대기", "쉐이커",
              "리필통", "수납", "정리함", "거치대")
# 건강 채널 시청층은 중장년 — 유아·어린이용이 리뷰 수로 뽑혀 올라왔다(아연→유아 시럽)
_KID_WORDS = ("유아", "아기", "베이비", "키즈", "어린이", "아동", "신생아", "영유아")
# 검색어 낱말 → 상품명에서 같은 뜻으로 인정할 말. "강아지 사료"가 "반려견 사료"를 놓치던 문제.
_SYN = {
    "강아지": ("강아지", "반려견", "애견", "도그", "dog", "댕댕", "퍼피", "puppy"),
    "고양이": ("고양이", "반려묘", "애묘", "캣", "cat", "냥", "키튼", "kitten"),
    "반려동물": ("반려동물", "펫", "pet", "강아지", "고양이", "반려견", "반려묘"),
    "영양제": ("영양제", "보충제", "정", "캡슐", "환", "분말", "플러스"),
    "측정기": ("측정기", "측정계", "기"),
    "무알코올": ("무알코올", "무알콜", "논알콜", "논알코올", "제로"),
}


def _tok_in(tok: str, name: str) -> bool:
    return any(_norm(w) in name for w in _SYN.get(tok, (tok,)))


# 품목명 그대로 검색하면 뜻이 다른 상품이 리뷰 수로 올라오는 품목(2026-09-19 전수 검토) — 검색·선택은 이 검색어로,
# 카탈로그·링크 테이블 키는 원래 품목명 그대로
_QUERY_OVERRIDE = {
    "스테비아": "스테비아 감미료", "서리태": "국산 서리태 콩",
    # 표기 차이(상품명 쪽 표기로)
    "조리가위": "주방가위", "보디워시": "바디워시", "낫토": "낫또", "식품저울": "주방저울",
    "체성분측정기": "체지방 체중계", "체지방 측정계": "체지방 체중계", "비강세척기": "코세척기",
    "워터픽": "구강세정기", "소독약": "과산화수소수", "고SPF 선크림": "선크림", "저염간장": "저염 간장",
    "락토프리우유": "락토프리 우유", "식이섬유보충제": "차전자피 식이섬유", "아몬드 브리즈": "아몬드브리즈",
    "비타민A": "비타민A 영양제", "크롬": "크롬 영양제", "무설탕 껌": "자일리톨 껌", "포도당 정제": "식염포도당",
    "순면장갑": "순면 장갑", "흡습속건 양말": "쿨맥스 양말", "창문형 환풍기": "창문환풍기", "마우스가드": "마우스피스",
    "코골이 방지 마우스피스": "마우스피스", "노이즈캔슬링 이어플러그": "실리콘 이어플러그",
    "무자극 구강청결제": "무알콜 가글", "유두크림": "유두보호크림", "미세먼지 차단 안경": "보호 안경",
    "수면유도등": "수면등 무드등", "무카페인 허브차": "허브차", "고단백 두부": "두부", "등푸른생선": "고등어",
    "철분 보충 식품": "철분 영양제", "유당분해효소": "락타아제", "크랜베리 보충제": "크랜베리 영양제",
    "필박스": "알약 케이스", "옆베개": "옆잠 베개", "티눈밴드": "티눈 밴드", "비강스프레이": "비강 스프레이",
    "소독약": "상처 소독약", "밀크씨슬": "밀크씨슬 실리마린", "히알루론산": "먹는 히알루론산",
    "전해질 음료": "전해질 음료 분말", "압박붕대": "탄력 압박붕대", "수면등": "수면등 무드등",
}


def _q(name: str) -> str:
    return _QUERY_OVERRIDE.get(name, name)


# 검색어는 그대로 두되 상품명에 이 말이 있으면 다른 물건이다
_EXCLUDE_BY_ITEM = {
    "퀴노아": ("헤어", "앰플", "샴푸", "트리트먼트", "두유", "음료"), "에리스리톨": ("캔디", "사탕", "롤리팝", "자일리톨"),
    "락토프리 우유": ("쌀음료", "쌀우유", "라이스", "오트"), "곤약밥": ("주먹밥", "도시락"),
    "순면장갑": ("목장갑", "작업", "코팅"),
}


def choose(query: str, raw: list[dict], domain: str = "health") -> dict | None:
    """리뷰 많고 가격이 합리적인 관련 상품 하나. 관련 상품이 없으면 None(= 브랜드커넥트에 없음으로 본다).

    1. 관련성: 마지막 낱말(품목의 핵심 명사)은 반드시, 나머지 낱말은 절반 이상 상품명에 있을 것(동의어 인정).
       ⚠️ 처음엔 모든 낱말을 요구했더니 "무알코올 맥주"·"생리식염수 스프레이" 같은 실재 품목이 "없음"으로 찍혔다
       — "없음"은 앞으로 추천 금지 목록이 되므로 거짓 "없음"이 거짓 "있음"보다 더 해롭다.
       건강 품목에선 검색어에 없는 업소용·차량용·반려동물용 표현이 붙은 상품은 뺀다.
    2. 리뷰 하한 MIN_REVIEWS.
    3. 리뷰 상위 5개 안에서, 그 5개 가격 중간값의 2배를 넘는 것(대용량 묶음·고가 업소 모델)은 빼고
       리뷰가 가장 많은 것. ⚠️ 관련 후보 전체의 중간값을 쓰면 업소용이 많은 품목(제습기)에서 중간값이 치솟아
       79만 원짜리가 "합리적"으로 통과했다.
    """
    toks = [_norm(t) for t in query.split() if t.strip()]
    head, rest = toks[-1], toks[:-1]
    # 육아(baby) topic에선 유아용품이 정답이라 _KID_WORDS를 빼지 않는다(2026-09-20 육아 트랙 신설)
    off = (_OFF_CONTEXT + _ACCESSORY + (() if domain in ("pet", "baby") else _PET_WORDS)
           + (() if domain != "health" else _KID_WORDS)
           + next((v for k, v in _EXCLUDE_BY_ITEM.items() if _QUERY_OVERRIDE.get(k, k) == query), ()))

    def related(p):
        n = _norm(p["name"])
        if not _tok_in(head, n):
            return False
        if rest and sum(_tok_in(t, n) for t in rest) * 2 < len(rest):
            return False
        return not any(w in p["name"] and w not in query for w in off)

    rel = [p for p in raw if related(p) and (p["reviews"] or 0) >= MIN_REVIEWS and p.get("price")]
    if not rel:
        return None
    top = sorted(rel, key=lambda p: -(p["reviews"] or 0))[:5]
    prices = sorted(p["price"] for p in top)
    med = prices[len(prices) // 2]
    ok = [p for p in top if p["price"] <= 2 * med] or top
    return max(ok, key=lambda p: ((p["reviews"] or 0), p.get("commission") or 0))


MIN_REVIEWS = 20


def _product(p: dict) -> dict:
    return {
        "id": p["id"], "name": p["productName"], "store": p.get("storeName"),
        "price": p.get("discountedSalePrice") or p.get("salePrice"),
        "commission": p.get("commissionRate"), "reviews": (p.get("reviewInfo") or {}).get("totalReviewCount", 0),
        "rating": (p.get("reviewInfo") or {}).get("averageReviewScore"),
        "url": p.get("productUrl"), "link": p.get("shortenUrl"),
    }


def search(query: str, limit: int = 10, page=None) -> list[dict]:
    """판매 중·제휴 가능한 상품만, 리뷰 많은 순. 로그인이 풀렸으면 RuntimeError."""
    if page is not None:
        return _search_on(page, query, limit)
    with _session() as pg:
        return _search_on(pg, query, limit)


class _session:
    """로그인된 전용 Chrome에 붙은 탭 하나. 여러 건을 돌릴 땐 탭을 재사용한다."""
    def __enter__(self):
        from playwright.sync_api import sync_playwright
        if not _cdp_up():
            raise RuntimeError("전용 Chrome이 안 떠 있음 — `python3 -m lib.brandconnect login` 먼저")
        self._pw = sync_playwright().start()
        ctx = self._pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}").contexts[0]
        names = {c["name"] for c in ctx.cookies("https://naver.com")}
        if not {"NID_AUT", "NID_SES"} <= names:
            self._pw.stop()
            raise RuntimeError("브랜드커넥트 로그인이 풀렸음 — 전용 Chrome 창에서 다시 로그인할 것")
        self.page = ctx.new_page()
        return self.page

    def __exit__(self, *a):
        try:
            self.page.close()
        finally:
            self._pw.stop()


def _search_on(page, query: str, limit: int) -> list[dict]:
    with page.expect_response(lambda r: API_MARK in r.url, timeout=30000) as ri:
        page.goto(SEARCH_URL.format(sid=SPACE_ID, q=urllib.parse.quote_plus(query)), wait_until="domcontentloaded")
    data = ri.value.json().get("data") or []
    ok = [p for p in data if p.get("enabled") and p.get("productStatus") == "SALE"
          and p.get("storeStatus") == "ACTIVE" and not p.get("affiliateStorePenalty")]
    ok.sort(key=lambda p: -((p.get("reviewInfo") or {}).get("totalReviewCount") or 0))
    return [_product(p) for p in ok[:limit]]


_ISSUE_JS = """async ([id, sid]) => {
  const r = await fetch(`https://gw-brandconnect.naver.com/affiliate/command/affiliate-urls?affiliateProductId=${id}`,
    {method: "POST", credentials: "include", headers: {"x-space-id": sid, "accept": "application/json, text/plain, */*"}});
  return [r.status, await r.text()];
}"""


def issue(page, prod: dict) -> str:
    """prod의 제휴 링크(naver.me)를 상품 ID로 발급한다.

    WHY: 화면에서 이름으로 카드를 찾아 "링크 발급"을 누르면 같은 판매자의 이름 비슷한 상품(ID가 1~2 차이)이
    눌려 23건이 엉뚱한 상품으로 발급됐다. 로그인된 브랜드커넥트 탭 안에서 버튼이 부르는 API를 ID로 직접 부른다
    (쿠키는 탭 것, 헤더는 버튼 요청과 같은 x-space-id 하나)."""
    if prod.get("link"):
        return prod["link"]
    status, body = page.evaluate(_ISSUE_JS, [str(prod["id"]), str(SPACE_ID)])
    if status != 200:
        raise RuntimeError(f"발급 실패 HTTP {status}: {body[:200]}")
    url = json.loads(body).get("url")
    if not url or not url.startswith("https://naver.me/"):
        raise RuntimeError(f"발급 응답 이상: {body[:200]}")
    page.wait_for_timeout(800)
    return url


def _supabase():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    u, k = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    return u, {"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json"}


def existing_naver_links() -> dict[str, str]:
    import requests
    u, h = _supabase()
    rows = requests.get(f"{u}/rest/v1/global_product_links?select=product,url&market=eq.naver&limit=5000",
                        headers=h, timeout=30).json()
    return {r["product"]: r["url"] for r in rows if (r.get("url") or "").strip() not in ("", "-")}


def replace_link(product: str, old_url: str, new_url: str) -> None:
    """우리가 발급해 넣었던 링크(old_url)가 그대로 있을 때만 바꾼다 — 그 사이 사용자가 바꿨으면 손대지 않는다."""
    import requests
    u, h = _supabase()
    r = requests.patch(f"{u}/rest/v1/global_product_links?market=eq.naver&product=eq.{urllib.parse.quote(product)}"
                       f"&url=eq.{urllib.parse.quote(old_url, safe='')}", headers=dict(h, Prefer="return=minimal"),
                       json={"url": new_url}, timeout=30)
    r.raise_for_status()


def rechoose(only: list[str] | None = None) -> None:
    """선택 기준을 고친 뒤 이미 발급한 health 품목을 다시 골라, 바뀐 것만 새로 발급·교체한다."""
    if sys.platform == "darwin":
        subprocess.Popen(["caffeinate", "-ims", "-w", str(os.getpid())])
    cat = json.loads(CATALOG.read_text(encoding="utf-8"))
    # 초기 스윕 항목엔 status가 없다 — link_saved(우리가 넣은 링크)면 전부 대상
    todo = [n for n, v in cat.items() if v.get("chosen") and v.get("link_saved") and v.get("link")]
    todo += [n for n in (only or []) if n not in todo and n in cat]
    if only:
        todo = [n for n in todo if n in only]
    print(f"[brandconnect] 재선택 {len(todo)}개", flush=True)
    changed = 0
    with _session() as pg:
        for i, name in enumerate(todo, 1):
            time.sleep(random.uniform(*PAUSE))
            ent = cat[name]
            try:
                raw = _search_on(pg, _q(name), 40)
                pick = choose(_q(name), raw)
                if pick and pick["id"] == ent["chosen"]["id"] and ent.get("link"):
                    continue
                if not pick:
                    ent.update(status="확인필요" if raw else "없음", found=False,
                               sample=[r["name"][:60] for r in raw[:5]], rejected=ent["chosen"])
                    # 엉뚱한 상품 링크가 대시보드에 남는 것보다 "링크 없음"(-)이 낫다 — 우리가 넣은 링크일 때만
                    if ent.get("link"):
                        replace_link(name, ent["link"], "-")
                    ent.update(link=None, link_saved=False)
                    print(f"  {i}/{len(todo)} 탈락 {name} (이전 {ent['rejected']['name'][:36]}) — 링크 회수", flush=True)
                else:
                    link = issue(pg, pick)
                    if ent.get("link"):
                        replace_link(name, ent["link"], link)
                    else:
                        save_link(name, link)
                    print(f"  {i}/{len(todo)} 교체 {name}: {ent['chosen']['name'][:30]} → {pick['name'][:36]}", flush=True)
                    ent.update(chosen=pick, link=link, link_saved=True, status="있음", found=True,
                               rejected=ent["chosen"])
                changed += 1
            except Exception as e:
                print(f"  {i}/{len(todo)} 오류 {name}: {str(e)[:120]}", flush=True)
                if "has been closed" in str(e):
                    break
            ent["checked_at"] = time.strftime("%Y-%m-%d %H:%M")
            CATALOG.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[brandconnect] 재선택 완료 — 바뀜 {changed}개", flush=True)


def save_link(product: str, url: str) -> None:
    """빈 품목에만 넣는다(on_conflict=ignore) — 사용자가 직접 넣은 링크를 덮지 않는다."""
    import requests
    u, h = _supabase()
    h = dict(h, Prefer="resolution=ignore-duplicates,return=minimal")
    r = requests.post(f"{u}/rest/v1/global_product_links?on_conflict=market,product", headers=h,
                      json=[{"market": "naver", "product": product, "url": url}], timeout=30)
    if r.status_code == 400 and "UNIQUE constraint" in r.text:
        # D1 프록시는 ignore-duplicates를 무시하고 400을 낸다. 비어 있거나 "-"(링크 없음 표시)인 행만 채운다.
        r = requests.patch(f"{u}/rest/v1/global_product_links?market=eq.naver&product=eq.{urllib.parse.quote(product)}"
                           f"&url=in.(%22-%22,%22%22)", headers=h, json={"url": url}, timeout=30)
    r.raise_for_status()


CATALOG = ROOT / "data" / "_audit" / "brandconnect_catalog.json"
# 댕냥사전(신규)용 — 건강 쪽 링크 테이블(global_product_links)과 섞지 않도록 카탈로그 파일에만 둔다
CATALOG_PET = ROOT / "data" / "_audit" / "brandconnect_catalog_pet.json"
# 육아 트랙(2026-09-20 신설) — 브랜드커넥트 계정은 health와 같은 걸 쓰므로 링크 발급도 그대로 한다
CATALOG_BABY = ROOT / "data" / "_audit" / "brandconnect_catalog_baby.json"
SEED = ROOT / "data" / "brandconnect_seed.json"


def seed_items(domain: str) -> list[str]:
    if not SEED.exists():
        return []
    groups = json.loads(SEED.read_text(encoding="utf-8")).get(domain) or {}
    return [x for g in groups.values() for x in g]


def all_products(domain: str = "health") -> list[str]:
    """그 도메인 트랙의 topic들이 실제로 쓰는 품목 이름.

    WHY 도메인으로 가르는지(2026-09-24): 전 topic을 한 번에 훑으면 health 스윕이 육아 topic의
    "아기 로션"·"유아 해열제"까지 삼킨다 — choose()가 health 도메인에선 _KID_WORDS를 빼므로 전부
    거짓 "없음"이 되고, 그대로 추천 금지 목록(brandconnect_unavailable.json)에 올라 쓸 수 있는
    품목을 영영 못 쓰게 된다."""
    seen, out = set(), []
    files = []
    for d in tracks.iter_topic_dirs(ROOT / "data"):
        if tracks.domain_of(d.name) != domain:
            continue
        files += [d / "platform_captions.json", d / "ko" / "platform_captions.json"]
    for f in sorted(files):
        try:
            for p in json.loads(f.read_text(encoding="utf-8")).get("products") or []:
                if p.strip() and p.strip() not in seen:
                    seen.add(p.strip()); out.append(p.strip())
        except (json.JSONDecodeError, OSError):
            continue
    return out


def sweep(issue_missing: bool = True, only: list[str] | None = None, domain: str = "health",
          recheck_missing: bool = True) -> None:
    """전 품목을 검색해 카탈로그를 만들고, 링크가 없는 품목은 발급한다. 중단 후 재실행하면 이어서.
    health: 기본 트랙 topic 품목 + seed(health), 링크를 global_product_links에도 저장.
    baby: seed(baby) + 육아 트랙 topic 품목, health와 같은 계정이라 링크도 똑같이 저장한다.
    pet: seed(pet)만, 링크는 카탈로그 파일에만."""
    catalog_path = {"pet": CATALOG_PET, "baby": CATALOG_BABY}.get(domain, CATALOG)
    # 댕냥사전은 브랜드커넥트 계정(스페이스 ID)이 다르다(2026-09-19 사용자) — 이 계정으로 발급한 링크는 수수료가
    # 엉뚱한 계정으로 간다. 상품이 있는지는 어느 계정으로 봐도 같으므로 확인만 하고 발급은 절대 안 한다.
    if domain == "pet":
        issue_missing = False
    # WHY caffeinate(2026-09-19): 한 시간 넘게 도는 작업인데 맥이 잠들자 Chrome 연결이 끊겨 231건이 오류로
    # 쌓였다. 이 프로세스가 살아 있는 동안만 잠자기를 막는다(-w: 이 PID가 끝나면 자동 해제, 설정은 안 바꿈).
    if sys.platform == "darwin":
        subprocess.Popen(["caffeinate", "-ims", "-w", str(os.getpid())])
    cat = json.loads(catalog_path.read_text(encoding="utf-8")) if catalog_path.exists() else {}
    have = existing_naver_links() if domain in ("health", "baby") else {}
    if only:
        names = only
    elif domain == "pet":
        names = seed_items(domain)
    elif domain == "baby":
        names = list(dict.fromkeys(seed_items("baby") + all_products("baby")))
    else:
        names = list(dict.fromkeys(all_products() + seed_items("health")))
    # 오류로 끝난 품목은 다시 시도한다 — 창이 닫혀 200건 넘게 오류로만 기록된 뒤 재실행해도 건너뛰던 문제
    todo = [n for n in names if n not in cat or "error" in cat[n] or (recheck_missing and not cat[n].get("found"))
            or (issue_missing and n not in have and cat[n].get("chosen") and not cat[n].get("link_saved"))]
    print(f"[brandconnect] 품목 {len(names)} / 이번에 처리 {len(todo)} (기존 네이버 링크 {len(have)}개는 유지)", flush=True)
    with _session() as pg:
        for i, name in enumerate(todo, 1):
            time.sleep(random.uniform(*PAUSE))
            try:
                raw = _search_on(pg, _q(name), 40)
                pick = choose(_q(name), raw, domain)
                # 없음(추천 금지)과 확인 필요를 가른다 — 검색 결과가 0건이거나 핵심 명사가 들어간 상품이 하나도
                # 없을 때만 "없음". 상품은 있는데 기준에 안 걸린 건 "확인 필요"로 두고 금지하지 않는다
                # ("무알코올 맥주"가 상품명 "무알콜"이라 거짓 "없음"으로 찍힌 사례).
                # ⚠️ 처음엔 "핵심 명사가 든 상품이 없으면 없음"이었는데 표기 차이(낫토↔낫또, 보디워시↔바디워시,
                # 조리가위↔주방가위)로 거짓 "없음"이 쏟아졌다 — 검색 결과 0건일 때만 "없음"
                status = "있음" if pick else ("확인필요" if raw else "없음")
                ent = {"checked_at": time.strftime("%Y-%m-%d %H:%M"), "found": bool(pick), "status": status,
                       "chosen": pick, "hits": len(raw), "domain": domain,
                       "sample": [r["name"][:60] for r in raw[:5]] if not pick else None}
                if pick and issue_missing and name not in have:
                    link = issue(pg, pick)
                    # WHY baby도 저장하는지(2026-09-24): 육아 트랙은 브랜드커넥트 계정이 health와 같아
                    # 발급까지 하면서 저장만 안 했다 — 대시보드·mission-control "미등록 링크"엔 안 뜨고
                    # 재실행마다 같은 상품을 다시 발급했다. pet은 계정이 달라 발급 자체를 안 한다.
                    if domain in ("health", "baby"):
                        save_link(name, link)
                    ent.update(link=link, link_saved=True)
                elif name in have:
                    ent["link"] = have[name]
                cat[name] = ent
                mark = "발급" if ent.get("link_saved") else status
                print(f"  {i}/{len(todo)} {mark:3s} {name}" + (f" → {pick['name'][:36]} (리뷰 {pick['reviews']}, "
                      f"{pick['price']}원)" if pick else ""), flush=True)
            except Exception as e:
                cat[name] = {"checked_at": time.strftime("%Y-%m-%d %H:%M"), "error": str(e)[:200]}
                print(f"  {i}/{len(todo)} 오류 {name}: {str(e)[:120]}", flush=True)
                if "has been closed" in str(e):
                    catalog_path.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
                    raise SystemExit("[brandconnect] 전용 Chrome 창이 닫혀 중단 — `login`으로 다시 띄운 뒤 sweep 재실행")
            catalog_path.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    miss = [n for n in names if not (cat.get(n) or {}).get("found")]
    print(f"[brandconnect] 완료 — 브랜드커넥트에 없음 {len(miss)}개(카탈로그 found=false)", flush=True)


def _captions_path(topic: str) -> Path:
    base = tracks.data_dir(topic)
    return next(p for p in (base / "platform_captions.json", base / "ko" / "platform_captions.json") if p.exists())


def check_topic(topic: str) -> dict:
    """products 전부를 검색해 data/<topic>/brandconnect.json에 기록한다. 결과가 0건인 품목은 found=False."""
    products = json.loads(_captions_path(topic).read_text(encoding="utf-8")).get("products") or []
    out = {"checked_at": time.strftime("%Y-%m-%d %H:%M"), "products": {}}
    for i, name in enumerate(products):
        if i:
            time.sleep(random.uniform(*PAUSE))
        # WHY domain을 넘기는지(2026-09-24): 안 넘기면 health 기준이라 육아 topic의 "아기 로션"류가
        # _KID_WORDS에 걸려 전부 거짓 "없음"으로 찍히고, content_review가 그 파일을 그대로 믿는다.
        pick = choose(_q(name), search(_q(name), limit=40), tracks.domain_of(topic))
        out["products"][name] = {"found": bool(pick), "chosen": pick}
        print(f"  {'O' if pick else 'X'} {name}"
              + (f" — {pick['name'][:40]} (수수료 {pick['commission']}%, 리뷰 {pick['reviews']})" if pick else " — 없음"))
    path = tracks.data_dir(topic) / "brandconnect.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    missing = [n for n, v in out["products"].items() if not v["found"]]
    print(f"[brandconnect] {topic}: {len(products) - len(missing)}/{len(products)} 제휴 가능"
          + (f" — 없음: {missing} (해결책에서 빼거나 다른 품목으로 바꿀 것)" if missing else ""))
    return out


UNAVAILABLE = ROOT / "data" / "brandconnect_unavailable.json"

# 품목이 아니라 막연한 범주 — 추천 금지가 아니라 "구체 품목(예: 두부·귀리)으로 바꿀 것"
VAGUE = ("저지방 식품", "무가당 식품", "저나트륨 식품", "저염 식품", "통곡물 식품", "통밀 식품", "저포드맵 식품",
         "저지방 식단 관리 식품", "제로슈거 식품", "무가당차", "무가당음료", "무가당 견과류", "다이어트도시락",
         "고섬유질 식품", "저요오드 식품", "저나트륨 소금", "고령친화식품", "무가당 식품", "저당 베리류",
         "저염식 조미료", "철분 보충 식품")
# 검색 결과는 있지만 본품이 아닌 것만 잡히는 품목(2026-09-19 표본 검토) — 일반의약품·온라인 판매 불가 품목
MANUAL_NONE = {
    "위장약": "일반의약품 — 반려견 식기만 잡힘", "진통제": "먹는 진통제는 없음(파스·소염 스프레이만)",
    "알레르기약": "일반의약품 — 반려견 용품만 잡힘", "무좀 연고": "일반의약품 — 풋샴푸만 잡힘",
    "데일리렌즈": "콘택트렌즈 본품 없음(케이스만)", "금연패치": "니코틴 패치 없음(무니코틴 전자담배만 — 대체품이라 추천 금지)",
    "무알코올 음료": "대체품 — 추천 금지", "카페인정": "각성제 — 건강 해결책으로 추천하지 않음",
}


def write_unavailable() -> dict:
    """두 카탈로그에서 "없음"(추천 금지)과 "확인필요"(사람이 볼 것)를 모아 한 파일로 쓴다 — content_review·리서치가 읽는다."""
    out = {"updated_at": time.strftime("%Y-%m-%d %H:%M"),
           "_why": "브랜드커넥트에 없는 품목은 링크를 못 붙인다 — 해결책 상품으로 추천하지 않는다. "
                   "pet은 댕냥사전용(계정이 달라 health 계정으로 발급 금지). baby는 육아 트랙용"
                   "(계정은 health와 같다).", "health": {}, "pet": {}, "baby": {}}
    for domain, path in (("health", CATALOG), ("pet", CATALOG_PET), ("baby", CATALOG_BABY)):
        cat = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        none = {k for k, v in cat.items() if v.get("status") == "없음" and k not in VAGUE}
        if domain == "health":
            none |= {k for k in MANUAL_NONE if k in cat and not (cat[k].get("found"))}
        out[domain] = {
            "없음": sorted(none),
            "없음_사유": {k: MANUAL_NONE[k] for k in sorted(none) if k in MANUAL_NONE},
            "모호_구체품목으로": sorted(k for k in cat if k in VAGUE and not cat[k].get("found")) if domain == "health" else [],
            "확인필요": sorted(k for k, v in cat.items() if v.get("status") == "확인필요"
                           and k not in VAGUE and k not in MANUAL_NONE),
        }
    UNAVAILABLE.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "login":
        login()
    elif cmd == "search" and len(sys.argv) > 2:
        for h in search(sys.argv[2]):
            print(f"{h['commission']:>4}%  리뷰{h['reviews']:>6}  {h['price']:>7}원  {h['name'][:50]}  {h['link'] or '(링크 미발급)'}")
    elif cmd == "check" and len(sys.argv) > 2:
        check_topic(sys.argv[2])
    elif cmd == "sweep":
        sweep(issue_missing="--no-issue" not in sys.argv,
              domain="pet" if "--pet" in sys.argv else "baby" if "--baby" in sys.argv else "health",
              only=[a for a in sys.argv[2:] if not a.startswith("--")] or None)
    elif cmd == "rechoose":
        rechoose([a for a in sys.argv[2:] if not a.startswith("--")] or None)
    elif cmd == "unavailable":
        u = write_unavailable()
        for d in ("health", "pet", "baby"):
            print(f"{d}: 없음 {len(u[d]['없음'])} / 확인필요 {len(u[d]['확인필요'])}")
    else:
        print(__doc__ or "사용: login | search <검색어> | check <topic>")
