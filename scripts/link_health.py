#!/usr/bin/env python3
# 죽은 제휴 링크 탐지·교체·알림 — 건강·육아·댕냥 블로그를 로그인 없이 훑고, 로그인된 브랜드커넥트로 상품 생존을 본다.
#
# WHY(2026-10-15 사용자 "내 블로그는 로그인없이도 전부 확인가능하지않냐? 각 블로그를 확인해서 링크들 확인하고
# 문제생긴것들있으면 갱신하고, 그 갱신한 토픽은 유튜브는 너가 알아서 갱신해주고 네이버블로그랑 클립은 내가
# 수정할수있도록 미션콘틀롤에서 체크풀고 끌올좀해주면안되나?"): 브랜드커넥트 상품은 판매 중지·제휴 종료로 수시로
# 사라지고, 이미 올린 글의 naver.me 링크는 에러 없이 죽은 채 남는다.
#
# WHY 이런 구조인지:
# - 생존 판정은 로그인된 브랜드커넥트 검색으로만 한다. naver.me → brandconnect 리다이렉트는 가짜 제휴 ID에도
#   302를 내고, 스마트스토어 상품 페이지는 봇에 로그인을 요구해서 밖에서는 죽었는지 알 수 없다(2026-10-15 실측).
#   카탈로그 chosen 상품 이름으로 검색해 그 상품 ID가 판매 중(SALE·enabled·ACTIVE)으로 돌아오면 살아 있다.
#   이름이 바뀌었을 수 있어 품목 검색어로 한 번 더 찾아본 뒤에만 "죽음"으로 본다(거짓 교체가 더 해롭다).
# - 계정은 채널마다 다르다 — 건강(9333)·육아(9335)는 lib/brandconnect.use_account, 댕냥은 dangnyang-shorts의
#   lib/brandconnect.py를 그대로 불러 쓴다(그쪽 _assert_own_space가 계정 확인을 한다). 다른 계정으로 발급하면
#   수수료가 엉뚱한 계정으로 간다.
# - 대본이 고르는 기준을 박아 둔 품목(카탈로그 `pinned_criteria`)은 아무 상품으로 바꾸면 대본과 상품이 어긋난다
#   — 자동 교체하지 않고 "수동 교체 필요" 알림만 남긴다.
# - 네이버 블로그·클립은 사람이 고친다: product_link_alerts(D1)에 미해결 행을 넣으면 mission-control 업로드 탭이
#   그 topic을 맨 위로 올리고 체크를 풀어 보여 준다. 유튜브는 사용자가 자동 수정을 허락해 설명란을 직접 고치고,
#   감사 기록용으로 해결된 행(resolved_at=지금)을 남긴다.
# - posting_log는 읽기만 한다(지우면 올린 topic이 "안 올림"으로 되살아난다).
#
#   .venv/bin/python3 scripts/link_health.py                       # 세 채널 점검 계획만(기본 --dry-run)
#   .venv/bin/python3 scripts/link_health.py --profile pet --commit
#   .venv/bin/python3 scripts/link_health.py --posted-only --limit 20
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import html
import importlib.util
import json
import os
import random
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks  # noqa: E402

# 형제 저장소 위치 — 기본은 이 저장소 옆(~/Desktop/project/dangnyang-shorts), 옮기면 환경변수로
DANG_ROOT = Path(os.environ.get("DANGNYANG_ROOT") or ROOT.parent / "dangnyang-shorts")
REPORT_DIR = ROOT / "output" / "_link_health"
# 브라우저 UA — 네이버·Cloudflare 앞단이 파이썬 기본 UA를 막는다(infra/d1-postgrest/DEPLOY.md)
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/141.0 Safari/537.36"}
BLOG_PAUSE = (0.4, 1.0)    # 블로그 글 사이 대기(초) — 공개 페이지라도 몰아 받지 않는다
CLIP, BLOG, YT = "네이버 클립", "네이버 블로그", "유튜브 쇼츠"
NAVER_ME = re.compile(r"https?://naver\.me/[A-Za-z0-9]+")

PROFILES = {
    "health": {"project": "health-shorts", "domain": "health", "yt": "adult",
               "blog": tracks.DEFAULT["naver_blog"]},
    "baby": {"project": "health-shorts", "domain": "baby", "yt": "baby",
             "blog": tracks.TRACKS["육아"]["naver_blog"]},
    "pet": {"project": "dangnyang", "domain": "pet", "yt": "whd", "blog": None},  # 블로그 주소는 그쪽 저장소에서
}


def log(msg: str) -> None:
    print(msg, flush=True)


# ── 순수 함수(테스트 대상) ────────────────────────────────────────────────

def blog_id(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def post_title(raw: str) -> str:
    """PostTitleListAsync의 title은 URL 인코딩(+ = 공백)에 HTML 엔티티까지 섞여 온다."""
    return html.unescape(urllib.parse.unquote_plus(raw)).strip()


def norm_title(s: str) -> str:
    return re.sub(r"[\s\W_]+", "", html.unescape(s)).lower()


def _first_seg(s: str) -> str:
    return norm_title(re.split(r"[,—]| - ", s, maxsplit=1)[0])


def map_post_to_topic(title: str, topic_titles: dict[str, str], cutoff: float = 0.7) -> str | None:
    """블로그 글 제목 → topic. 글 제목은 네이버 블로그 캡션 첫 줄을 붙여 넣은 것이다.

    1. 정규화 후 완전 일치 2. 제목 끝 ", <제품>"을 뗀 꼴로 일치(10-08 이전 글은 제품 꼬리가 없다)
    3. 첫 마디(검색어, 첫 쉼표 앞)가 같은 topic이 하나뿐이면 그것 — 올린 뒤 캡션 문구를 다듬어 뒷부분이
       달라진 글이 많다(댕냥 7편 실측) 4. 글 첫 마디가 한 topic 제목의 앞부분 5. 유사도 cutoff 이상이면서
       2등과 0.05 넘게 차이 날 때만 — "~ 습관 3가지"처럼 틀이 같은 옛 글이 엉뚱한 topic에 붙지 않게."""
    t = norm_title(title)
    normed = {k: norm_title(v) for k, v in topic_titles.items() if v}
    for k, v in normed.items():
        if v == t:
            return k
    for k, v in topic_titles.items():
        if v and "," in v and norm_title(v.rsplit(",", 1)[0]) == t:
            return k
    # 옛 캡션은 첫 줄이 문단 통째라 글 제목이 그 앞부분만 잘라 쓴 꼴이다(혈당_6)
    head = [k for k, v in normed.items() if len(t) >= 12 and v.startswith(t)]
    if len(head) == 1:
        return head[0]
    ratio = {k: difflib.SequenceMatcher(None, t, v).ratio() for k, v in normed.items()}
    seg = _first_seg(title)
    # 검색어만 같은 다른 편(신장 기능 저하 → 전해질 파우더 편)에 붙지 않게 유사도 하한을 둔다
    same = [k for k, v in topic_titles.items() if v and len(seg) >= 3 and _first_seg(v) == seg and ratio[k] >= 0.45]
    if same:
        return max(same, key=lambda k: ratio[k])
    pre = [k for k, v in normed.items() if len(seg) >= 8 and v.startswith(seg)]
    if len(pre) == 1:
        return pre[0]
    ranked = sorted(ratio.items(), key=lambda kv: -kv[1])
    if ranked and ranked[0][1] >= cutoff and (len(ranked) == 1 or ranked[0][1] - ranked[1][1] > 0.05):
        return ranked[0][0]
    return None


def extract_links(page_html: str) -> list[tuple[str | None, str]]:
    """글 본문의 naver.me 링크와, 바로 앞 "🔗 <품목> 구매:" 표식의 품목 이름(없으면 None)."""
    text = html.unescape(re.sub(r"<[^>]+>", " ", page_html))
    text = re.sub(r"[ \t​]+", " ", text)
    out: list[tuple[str | None, str]] = []
    labelled = set()
    for m in re.finditer(r"🔗\s*([^\n:：]{1,40}?)\s*구매\s*[:：]\s*(https?://naver\.me/[A-Za-z0-9]+)", text):
        out.append((m.group(1).strip(), m.group(2)))
        labelled.add(m.group(2))
    for link in dict.fromkeys(NAVER_ME.findall(text)):
        if link not in labelled:
            out.append((None, link))
    return out


def product_no(url: str | None) -> str | None:
    """스마트스토어 상품 주소(/products/<n>)나 브랜드커넥트 리다이렉트(channelProductNo=<n>)의 상품 번호."""
    if not url:
        return None
    m = re.search(r"channelProductNo=(\d+)", url) or re.search(r"/products/(\d+)", url)
    return m.group(1) if m else None


def is_selling(p: dict) -> bool:
    # lib/brandconnect._search_on과 같은 기준 — 판매 중·제휴 가능·패널티 없음
    return bool(p.get("enabled") and p.get("productStatus") == "SALE"
                and p.get("storeStatus") == "ACTIVE" and not p.get("affiliateStorePenalty"))


def liveness(chosen_id, raws: list[list[dict]]) -> tuple[str, dict | None]:
    """'alive'(판매 중으로 검색됨) | 'stopped'(검색되지만 판매·제휴 중지) | 'gone'(어느 검색에도 없음)."""
    seen = [p for raw in raws for p in raw if str(p.get("id")) == str(chosen_id)]
    live = next((p for p in seen if is_selling(p)), None)
    if live:
        return "alive", live
    return ("stopped", seen[0]) if seen else ("gone", None)


# 교체 후보에서 뺄 말 — 검색어에 없는데 붙어 있으면 본품이 아니다("무드등" → "아크릴 무드등 만들기 DIY 키트", 10-15 실측).
# 사람이 고르던 sweep과 달리 여기선 아무도 안 보고 바로 링크가 바뀌므로 lib/brandconnect.choose보다 한 겹 더 거른다.
_NOT_ITEM = ("만들기", "DIY", "diy", "키트", "부품", "교체용", "리필", "공병", "보관통", "케이스")


_SPEC = re.compile(r"\d[\d,.]*\s*(?:ppm|iu|mcg|μg|mg|%)|spf\s*\d+|pa\+{1,4}", re.I)


def spec_tokens(name: str) -> set[str]:
    """함량·규격 표기(불소 1000ppm, 비타민D 400IU, SPF50 …) — 용량·개수(g·ml·개)는 뺀다."""
    return {re.sub(r"[\s,]", "", m.group(0)).lower() for m in _SPEC.finditer(name)}


def keeps_spec(old_name: str, new_name: str) -> bool:
    """자동 교체는 원래 상품의 함량 표기를 그대로 가진 상품으로만 — 10-15 아기 불소 치약이 1000ppm에서
    1450ppm(6세 이상용)으로 바뀌어 대본과 정반대가 된 사고. 규격이 다르면 사람이 고른다."""
    need = spec_tokens(old_name)
    return not need or need <= {re.sub(r"[\s,]", "", t) for t in spec_tokens(new_name)}


def off_item(name: str, query: str) -> bool:
    return any(w in name and w not in query for w in _NOT_ITEM)


CONFIRM_AFTER = dt.timedelta(hours=float(os.environ.get("LINK_HEALTH_CONFIRM_HOURS") or 6))


def confirmed_dead(first_seen: dict, chosen_id, now: dt.datetime | None = None) -> bool:
    """같은 상품이 CONFIRM_AFTER 넘게 계속 안 보였을 때만 죽음으로 확정한다."""
    if str(first_seen.get("id")) != str(chosen_id):
        return False
    since = dt.datetime.strptime(first_seen["since"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    return (now or dt.datetime.now(dt.timezone.utc)) - since >= CONFIRM_AFTER


def dead_reason(state: str, name: str) -> str:
    return {"stopped": f"판매·제휴 중지된 상품({name[:40]})",
            "gone": f"브랜드커넥트 검색에서 사라진 상품({name[:40]})"}[state]


def dedupe_alerts(new_rows: list[dict], open_rows: list[dict]) -> list[dict]:
    """같은 (project, topic, platform, old_link)로 아직 안 풀린 알림이 있으면 또 넣지 않는다."""
    key = lambda r: (r["project"], r["topic"], r["platform"], r.get("old_link") or "")  # noqa: E731
    seen = {key(r) for r in open_rows if not r.get("resolved_at")}
    out = []
    for r in new_rows:
        if r.get("resolved_at") is None and key(r) in seen:
            continue
        seen.add(key(r))
        out.append(r)
    return out


def replace_in_description(desc: str, old: str, new: str) -> str:
    """설명란의 옛 링크만 새 링크로 — naver.me/xxx가 다른 링크의 앞부분이 되지 않게 경계까지 본다."""
    return re.sub(re.escape(old) + r"(?![A-Za-z0-9])", new, desc)


def description_links(desc: str) -> dict[str, str]:
    """yt_upload._products_block이 쓴 "▶ <품목>: <링크>" 줄 → {품목: 링크}."""
    return {m.group(1).strip(): m.group(2) for m in re.finditer(r"▶\s*(.+?):\s*(https?://naver\.me/[A-Za-z0-9]+)", desc)}


# ── 브랜드커넥트 계정 ───────────────────────────────────────────────────

def _load_dang_bc():
    spec = importlib.util.spec_from_file_location("dangnyang_brandconnect", DANG_ROOT / "lib" / "brandconnect.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class Account:
    """채널 하나의 브랜드커넥트 계정·카탈로그·링크 표."""

    def __init__(self, name: str):
        self.name, self.cfg = name, PROFILES[name]
        if name == "pet":
            self.bc = _load_dang_bc()
            self.catalog_path = self.bc.CATALOG
        else:
            from lib import brandconnect as bc
            self.bc = bc
            self.catalog_path = bc.CATALOG_BABY if name == "baby" else bc.CATALOG
        self.use()

    def use(self) -> None:
        # health 모듈은 계정이 모듈 전역이라, 건강↔육아를 오갈 때마다 다시 끼운다
        if hasattr(self.bc, "use_account"):
            self.bc.use_account(self.cfg["domain"])

    def ensure_window(self) -> None:
        """창이 하나도 없으면 playwright connect_over_cdp가 "Browser context management is not supported"로
        죽는다(2026-10-15 실측, 9335) — 빈 탭 하나를 띄워 둔다."""
        import requests
        base = f"http://127.0.0.1:{self.bc.PORT}"
        try:
            pages = [t for t in requests.get(f"{base}/json/list", timeout=3).json() if t.get("type") == "page"]
        except Exception as e:
            raise SystemExit(f"[{self.name}] 브랜드커넥트 전용 Chrome(포트 {self.bc.PORT})이 안 떠 있음 — "
                             f"`python3 -m lib.brandconnect login{' --baby' if self.name == 'baby' else ''}`"
                             f"{'(dangnyang-shorts에서)' if self.name == 'pet' else ''} 후 다시 실행: {e}")
        if not pages:
            requests.put(f"{base}/json/new?about:blank", timeout=5)

    def search(self, page, query: str) -> list[dict]:
        """걸러내기 전 검색 응답 전체 — 판매 중지 상품까지 봐야 '중지'와 '사라짐'을 가른다."""
        bc = self.bc
        with page.expect_response(lambda r: bc.API_MARK in r.url, timeout=30000) as ri:
            page.goto(bc.SEARCH_URL.format(sid=bc.SPACE_ID, q=urllib.parse.quote_plus(query)),
                      wait_until="domcontentloaded")
        if hasattr(bc, "_assert_own_space"):
            bc._assert_own_space(page)
        if ri.value.status != 200:
            raise RuntimeError(f"검색 API {ri.value.status} — 로그인 계정을 확인할 것")
        return ri.value.json().get("data") or []

    def catalog(self) -> dict:
        return json.loads(self.catalog_path.read_text(encoding="utf-8"))

    def save_item(self, item: str, ent: dict) -> None:
        """그 품목 하나만 바꿔 쓴다 — 다른 세션이 한 시간 도는 사이 같은 파일을 고쳤을 수 있어 통째로 덮지 않고,
        들여쓰기도 파일에 있던 그대로 둬 git diff가 그 품목 줄만 남게 한다."""
        raw = self.catalog_path.read_text(encoding="utf-8")
        cat = json.loads(raw)
        cat[item] = ent
        m = re.match(r"\{\n( +)", raw)
        self.catalog_path.write_text(json.dumps(cat, ensure_ascii=False, indent=len(m.group(1)) if m else 1)
                                     + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")


# ── 데이터 모으기 ────────────────────────────────────────────────────

def _caption_file(d: Path) -> Path | None:
    return next((p for p in (d / "platform_captions.json", d / "ko" / "platform_captions.json") if p.exists()), None)


def topics_of(profile: str) -> dict[str, dict]:
    """{topic: {products, title(블로그 캡션 첫 줄)}} — 그 채널 topic만."""
    if profile == "pet":
        dirs = sorted(p for p in (DANG_ROOT / "data").iterdir() if p.is_dir() and p.name.startswith("댕냥_"))
    else:
        dirs = [d for d in tracks.iter_topic_dirs(ROOT / "data") if tracks.domain_of(d.name) == PROFILES[profile]["domain"]]
    out = {}
    for d in dirs:
        f = _caption_file(d)
        if not f:
            continue
        try:
            c = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        blog = next((p for p in c.get("platforms", []) if p.get("name") == BLOG), None)
        out[d.name] = {"products": [x.strip() for x in c.get("products") or [] if x and x.strip() not in ("", "-")],
                       "title": (blog or {}).get("caption", "").split("\n", 1)[0].strip()}
    return out


def _db():
    from lib.brandconnect import _supabase
    return _supabase()


def db_get(table: str, params: dict) -> list[dict]:
    import requests
    u, h = _db()
    r = requests.get(f"{u}/rest/v1/{table}", headers=h, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def caption_topics(project: str) -> set[str]:
    """미션컨트롤에 캡션 카드가 있는 topic(mission_control.hs_platform_captions).
    WHY(2026-10-17 사용자 "신규 포맷 기준으로 캡션 없던 애들 … 어차피 관리 안 할 거라서 검사에서도 막고 미션컨트롤에서도 빼"):
    개편 전 옛 포맷으로 올린 글은 카드가 없어 고칠 화면도 없다 — 블로그·클립 알림을 아예 만들지 않는다."""
    import requests
    u, h = _db()
    h = dict(h, **{"Accept-Profile": "mission_control"})
    out, off = set(), 0
    while True:
        r = requests.get(f"{u}/rest/v1/hs_platform_captions", headers=h, timeout=30,
                         params={"select": "topic", "project": f"eq.{project}", "limit": "1000", "offset": str(off)})
        r.raise_for_status()
        rows = r.json()
        out.update(x["topic"].split("/")[0] for x in rows)
        if len(rows) < 1000:
            return out
        off += 1000


def crawl_blog(url: str) -> list[dict]:
    """공개 글 목록 전부(로그인 불필요) — RSS는 50개뿐이라 PostTitleListAsync를 끝까지 넘긴다."""
    import requests
    bid, posts, seen = blog_id(url), [], set()
    for page in range(1, 200):
        r = requests.get("https://blog.naver.com/PostTitleListAsync.naver", headers=UA, timeout=20,
                         params={"blogId": bid, "currentPage": page, "countPerPage": 30})
        r.raise_for_status()
        # 이 응답은 JSON 안에 \' 이스케이프를 섞어 보낸다(표준 JSON 아님)
        rows = json.loads(r.text.replace("\\'", "'")).get("postList") or []
        new = [x for x in rows if x["logNo"] not in seen]
        if not new:
            break
        for x in new:
            seen.add(x["logNo"])
            posts.append({"logNo": x["logNo"], "title": post_title(x["title"]),
                          "url": f"https://blog.naver.com/{bid}/{x['logNo']}"})
    return posts


def fetch_post_links(url: str, log_no: str) -> list[tuple[str | None, str]]:
    import requests
    r = requests.get("https://m.blog.naver.com/PostView.naver", headers=UA, timeout=20,
                     params={"blogId": blog_id(url), "logNo": log_no})
    if r.status_code != 200:
        return []
    return extract_links(r.text)


class NaverMeCache:
    """naver.me → 상품 번호. 짧은 링크가 가리키는 상품은 바뀌지 않으므로 한 번 푼 건 저장해 둔다."""

    def __init__(self, path: Path):
        self.path = path
        self.data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}

    def get(self, link: str) -> str | None:
        if link in self.data:
            return self.data[link]
        import requests
        try:
            r = requests.head(link, headers=UA, allow_redirects=False, timeout=15)
            no = product_no(r.headers.get("Location"))
        except requests.RequestException:
            return None
        self.data[link] = no
        return no

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, ensure_ascii=False, indent=0), encoding="utf-8")


# ── 유튜브 ──────────────────────────────────────────────────────────

def yt_service(profile: str):
    """(youtube 클라이언트, youtube_uploaded 키 접두어). 채널 ID가 다르면 멈춘다."""
    code = PROFILES[profile]["yt"]
    if code in ("adult", "baby"):
        spec = importlib.util.spec_from_file_location("hs_yt_upload", ROOT / "scripts" / "yt_upload.py")
        yt_upload = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(yt_upload)
        ch = yt_upload.Channel(code)
        return ch.service()[0], ch.key
    # 댕냥 채널 키는 그쪽 .env에만 있다 — 이 프로세스 환경을 덮지 않게 값만 읽는다
    from dotenv import dotenv_values
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    env = dotenv_values(DANG_ROOT / ".env")
    c = Credentials(token=None, refresh_token=env["YOUTUBE_WHD_REFRESH_TOKEN"], client_id=env["YOUTUBE_WHD_CLIENT_ID"],
                    client_secret=env["YOUTUBE_WHD_CLIENT_SECRET"], token_uri="https://oauth2.googleapis.com/token",
                    scopes=None)
    c.refresh(Request())
    yt = build("youtube", "v3", credentials=c, cache_discovery=False)
    items = yt.channels().list(part="id", mine=True).execute().get("items", [])
    if not items or items[0]["id"] != env["YOUTUBE_WHD_CHANNEL_ID"]:
        raise SystemExit("❌ 댕냥 유튜브 토큰 채널이 다르다 — 중단")
    return yt, "whd-dang/"


def yt_videos(yt, key_prefix: str) -> dict[str, list[dict]]:
    """{topic: [{id, snippet}]} — 업로드 기록(youtube_uploaded)에 있는 영상만."""
    rows = db_get("youtube_uploaded", {"select": "topic,video_id", "topic": f"like.{key_prefix}*", "limit": "5000"})
    by_id = {r["video_id"]: r["topic"][len(key_prefix):] for r in rows if r.get("video_id")}
    out: dict[str, list[dict]] = {}
    ids = list(by_id)
    for i in range(0, len(ids), 50):
        for v in yt.videos().list(part="snippet", id=",".join(ids[i:i + 50])).execute().get("items", []):
            out.setdefault(by_id[v["id"]], []).append(v)
    return out


def yt_update_description(yt, video: dict, desc: str) -> None:
    s = video["snippet"]
    # 쓸 수 있는 필드만 다시 보낸다 — categoryId는 필수, 빼면 태그·언어가 지워진다
    body = {"id": video["id"], "snippet": {k: s[k] for k in ("title", "categoryId", "tags", "defaultLanguage",
                                                                 "defaultAudioLanguage") if k in s}}
    body["snippet"]["description"] = desc
    yt.videos().update(part="snippet", body=body).execute()


# ── 점검 본체 ────────────────────────────────────────────────────────

def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(profile: str, commit: bool, posted_only: bool, limit: int | None) -> dict:
    cfg = PROFILES[profile]
    project = cfg["project"]
    acct = Account(profile)
    blog_url = cfg["blog"] or json.loads((DANG_ROOT / "data" / "social_accounts.json").read_text())[BLOG]
    cache = NaverMeCache(REPORT_DIR / "naver_me_products.json")
    rep: dict = {"profile": profile, "started_at": _now(), "commit": commit}
    log(f"\n=== [{profile}] {blog_url} — {'실행(--commit)' if commit else '계획만(--dry-run)'} ===")

    # 1. topic·게시 현황·링크 표
    topics = topics_of(profile)
    posting = db_get("posting_log", {"select": "topic,platform", "limit": "5000"})
    posted: dict[str, set[str]] = {}
    for r in posting:
        if r["topic"] in topics:
            posted.setdefault(r["topic"], set()).add(r["platform"])
    have = acct.bc.existing_naver_links()

    # 2. 블로그 글 → topic, 글에 실제로 박힌 링크
    posts = crawl_blog(blog_url)
    titles = {t: v["title"] for t, v in topics.items()}
    mapped, post_links_n = [], 0
    for p in posts:
        topic = map_post_to_topic(p["title"], titles)
        if not topic:
            continue
        time.sleep(random.uniform(*BLOG_PAUSE))
        links = fetch_post_links(blog_url, p["logNo"])
        post_links_n += len(links)
        mapped.append(dict(p, topic=topic, links=links))
    rep.update(posts=len(posts), posts_mapped=len(mapped), post_links=post_links_n)
    log(f"블로그 글 {len(posts)}개 중 topic 매칭 {len(mapped)}개, 글 속 제휴 링크 {post_links_n}개")

    # 3. 점검할 품목: topic이 쓰는 품목 + 글에 표식으로 박힌 품목 — 카탈로그에 고른 상품이 있는 것만
    used: dict[str, set[str]] = {}
    for t, v in topics.items():
        if posted_only and not posted.get(t):
            continue
        for it in v["products"]:
            used.setdefault(it, set()).add(t)
    for p in mapped:
        for label, _ in p["links"]:
            if label:
                used.setdefault(label, set()).add(p["topic"])
    cat = acct.catalog()
    items = [it for it in used if (cat.get(it) or {}).get("chosen")]
    if limit:
        items = items[:limit]
    log(f"점검 품목 {len(items)}개(카탈로그에 상품이 없는 {len(used) - len([i for i in used if (cat.get(i) or {}).get('chosen')])}개 제외)")

    # 4. 생존 확인 → 죽은 것은 교체(또는 수동 알림)
    swapped: dict[str, dict] = {}     # item → {old, new, reason, kind}
    suspects_path = REPORT_DIR / "suspects.json"
    suspects = json.loads(suspects_path.read_text(encoding="utf-8")) if suspects_path.exists() else {}
    pending: list[str] = []
    mismatch, errors = [], []
    acct.ensure_window()
    if commit and sys.platform == "darwin":
        subprocess.Popen(["caffeinate", "-ims", "-w", str(os.getpid())])
    with acct.bc._session() as pg:
        if commit:
            # 발급 API는 브랜드커넥트 페이지 안에서 불러야 쿠키가 붙는다(lib/brandconnect.reissue_baby 참고)
            pg.goto(f"https://brandconnect.naver.com/{acct.bc.SPACE_ID}/affiliate/products", wait_until="domcontentloaded")
        for i, it in enumerate(items, 1):
            ent = cat[it]
            ch = ent["chosen"]
            db_link = have.get(it)
            # DB 링크가 카탈로그가 발급한 링크가 아니면(사용자가 직접 넣은 링크) 그 링크의 상품은 이 카탈로그로 판정 못 한다.
            # ⚠️ 상품 번호로 비교하지 말 것 — 카탈로그 productUrl의 번호와 naver.me의 channelProductNo는 같은 상품이라도
            # 다른 번호 체계인 경우가 있다(에어컨 필터·무릎담요 실측)
            if db_link and db_link not in (ent.get("link"), ch.get("link")):
                mismatch.append(it)
                continue
            try:
                time.sleep(random.uniform(*acct.bc.PAUSE))
                raws = [acct.search(pg, ch["name"])]
                state, hit = liveness(ch["id"], raws)
                if state != "alive":
                    time.sleep(random.uniform(*acct.bc.PAUSE))
                    raws.append(acct.search(pg, acct.bc._q(it)))
                    state, hit = liveness(ch["id"], raws)
                if state == "alive":
                    suspects.pop(f"{profile}/{it}", None)
                    continue
                reason = dead_reason(state, ch["name"])
                # 한 번 안 보인 것만으로는 바꾸지 않는다 — 상품이 몇 시간 검색에서 빠졌다 돌아오는 일이 있다
                # (10-15 반려동물 펫캠: 08시 0건 → 09시 다시 판매 중). 앞선 점검에서도 죽어 있었을 때만 확정.
                first = suspects.setdefault(f"{profile}/{it}", {"id": ch["id"], "since": _now()})
                if not confirmed_dead(first, ch["id"]):
                    pending.append(it)
                    log(f"  {i}/{len(items)} ⏳ {it}: {reason} — 다음 점검에서 다시 보고 확정")
                    continue
                pinned = ent.get("pinned_criteria")
                pool = [acct.bc._product(p) for p in raws[-1] if is_selling(p) and str(p["id"]) != str(ch["id"])
                        and not off_item(p.get("productName") or "", acct.bc._q(it))
                        and keeps_spec(ch["name"], p.get("productName") or "")]
                pick = None if pinned else acct.bc.choose(acct.bc._q(it), pool, cfg["domain"])
                if not pick:
                    why = f"고르는 기준 '{pinned}'" if pinned else "같은 기준의 대체 상품 없음"
                    swapped[it] = {"old": db_link or ent.get("link"), "new": None, "kind": "manual",
                                   "reason": f"{reason} — 수동 교체 필요({why})"}
                    log(f"  {i}/{len(items)} ✋ {it}: {reason} — 수동 교체 필요({why})")
                    continue
                new = acct.bc.issue(pg, pick) if commit else (pick.get("link") or "(발급 예정)")
                swapped[it] = {"old": db_link or ent.get("link"), "new": new, "kind": "dead",
                               "reason": f"{reason} → {pick['name'][:40]}로 교체"}
                log(f"  {i}/{len(items)} 🔁 {it}: {ch['name'][:30]} → {pick['name'][:36]} ({new})")
                if commit:
                    if db_link:
                        acct.bc.replace_link(it, db_link, new)
                    else:
                        acct.bc.save_link(it, new)
                    ent.update(chosen=pick, link=new, link_saved=True, status="있음", found=True, rejected=ch,
                               replaced_at=time.strftime("%Y-%m-%d %H:%M"),
                               replaced_note=f"link_health 자동 교체 — {reason}")
                    if profile == "baby":
                        ent["account"] = "baby"
                    elif profile == "pet":
                        ent["issued_by"] = str(acct.bc.SPACE_ID)
                    acct.save_item(it, ent)
                    suspects.pop(f"{profile}/{it}", None)
                    have[it] = new
            except Exception as e:  # 품목 하나 실패로 전체를 멈추지 않는다 — 창이 닫힌 경우만 중단
                errors.append(f"{it}: {str(e)[:120]}")
                log(f"  {i}/{len(items)} 오류 {it}: {str(e)[:120]}")
                if "has been closed" in str(e) or "로그인" in str(e) or "계정" in str(e):
                    raise SystemExit(f"[{profile}] 브랜드커넥트 세션 문제로 중단: {e}")
            if i % 50 == 0:
                log(f"  … {i}/{len(items)}")
    cache.save()
    suspects_path.write_text(json.dumps(suspects, ensure_ascii=False, indent=1), encoding="utf-8")
    rep.update(pending=pending, items_checked=len(items), dead=sorted(it for it, v in swapped.items() if v["kind"] == "dead"),
               manual=sorted(it for it, v in swapped.items() if v["kind"] == "manual"), mismatch=mismatch, errors=errors)

    # 5. 알림 — 죽은 품목: 그 품목을 쓰는 topic의 올린 블로그·클립 / 살아 있지만 글 링크가 옛 링크: 블로그만
    alerts: list[dict] = []
    post_by_topic = {}
    for p in mapped:
        post_by_topic.setdefault(p["topic"], p)
    for it, v in swapped.items():
        for t in sorted(used.get(it, ())):
            post = post_by_topic.get(t)
            for plat in (BLOG, CLIP):
                # 블로그는 체크를 안 했어도 글이 실제로 보이면 고쳐야 한다
                if plat not in posted.get(t, set()) and not (plat == BLOG and post):
                    continue
                # 클립은 본문을 못 읽는다 — 캡션 products에 그 품목이 있는 topic만(글 표식으로만 걸린 옛 품목은 블로그만)
                if plat == CLIP and it not in topics[t]["products"]:
                    continue
                old = v["old"]
                if plat == BLOG and post:
                    # 글에 실제로 박힌 링크를 옛 링크로 — 사용자가 글에서 찾아 바꿀 문자열이다
                    old = next((l for lab, l in post["links"] if lab == it), None) or \
                        (post["links"][0][1] if len(topics[t]["products"]) == 1 and post["links"] else old)
                # 글·클립에 이미 새 링크가 들어 있으면 고칠 게 없다 — 카탈로그 chosen이 DB 링크보다 옛 상품을 가리키던
                # 품목(10-15 두부·휴대용 선풍기 등 20건)은 다시 골라도 같은 상품·같은 naver.me가 나와 헛알림이 됐다
                if old and v["new"] and old == v["new"]:
                    continue
                alerts.append({"project": project, "topic": t, "platform": plat, "item": it, "kind": v["kind"],
                               "old_link": old, "new_link": v["new"], "reason": v["reason"],
                               "post_url": post["url"] if plat == BLOG and post else None})
    stale_posts = []
    for p in mapped:
        products = topics[p["topic"]]["products"]
        for label, link in p["links"]:
            it = label if label in have or label in cat else (products[0] if len(products) == 1 else None)
            if not it or it in swapped or not have.get(it) or link == have[it]:
                continue
            stale_posts.append(p["url"])
            # 두 naver.me가 같은 상품을 가리키면 링크만 다시 발급된 것(계정 교체 등), 다르면 교체 전 상품이다
            a, b = cache.get(link), cache.get(have[it])
            detail = "같은 상품, 다른 링크" if a and a == b else "교체 전 상품" if a and b else ""
            alerts.append({"project": project, "topic": p["topic"], "platform": BLOG, "item": it, "kind": "stale",
                           "old_link": link, "new_link": have[it],
                           "reason": "블로그 링크가 최신 링크와 다름" + (f"({detail})" if detail else ""),
                           "post_url": p["url"]})
    rep["stale_posts"] = sorted(set(stale_posts))

    # 6. 유튜브 설명란 — 죽어서 바뀐 링크, 또는 DB 링크와 다른 옛 링크를 새 링크로
    yt_changes = []
    try:
        yt, prefix = yt_service(profile)
        vids = yt_videos(yt, prefix)
    except SystemExit:
        raise
    except Exception as e:
        vids, yt = {}, None
        rep["youtube_error"] = str(e)[:200]
        log(f"유튜브 확인 실패(건너뜀): {str(e)[:160]}")
    for t, vs in vids.items():
        for v in vs:
            desc = v["snippet"].get("description", "")
            new_desc, why = desc, []
            for it, link in description_links(desc).items():
                sw = swapped.get(it)
                # 수동 교체 품목은 바꿀 링크가 없다 — 사람이 고른 뒤 다음 실행이 "옛 링크"로 잡아 고친다
                target = sw["new"] if sw and sw["kind"] == "dead" else (None if sw else have.get(it))
                if not target or target == link:
                    continue
                if commit and not target.startswith("https://naver.me/"):
                    continue
                new_desc = replace_in_description(new_desc, link, target)
                why.append((it, link, target, sw["reason"] if sw else "설명란 링크가 최신 링크와 다름",
                            sw["kind"] if sw else "stale"))
            if not why:
                continue
            yt_changes.append({"topic": t, "video_id": v["id"], "changes": [w[:3] for w in why]})
            log(f"  유튜브 {t} {v['id']}: " + ", ".join(f"{w[0]} {w[1]}→{w[2]}" for w in why))
            if commit:
                yt_update_description(yt, v, new_desc)
                for it, old, new, reason, kind in why:
                    alerts.append({"project": project, "topic": t, "platform": YT, "item": it, "kind": kind,
                                   "old_link": old, "new_link": new, "reason": reason + " — 설명란 자동 수정",
                                   "post_url": f"https://youtu.be/{v['id']}", "resolved_at": _now()})
    rep["youtube"] = yt_changes

    # 7. 알림 쓰기(중복 제외) + 블로그 글이 이미 새 링크로 고쳐진 알림은 자동으로 푼다
    open_rows = db_get("product_link_alerts", {"select": "id,project,topic,platform,old_link,new_link,resolved_at",
                                               "project": f"eq.{project}", "resolved_at": "is.null", "limit": "5000"})
    # 캡션 카드 없는 옛 포맷 topic은 사람이 관리하지 않는다 — 블로그·클립 알림을 만들지 않고, 남아 있던 것도 푼다
    with_cards = caption_topics(project)
    legacy = {a["topic"] for a in alerts if a["platform"] != YT and a["topic"] not in with_cards}
    alerts = [a for a in alerts if a["platform"] == YT or a["topic"] in with_cards]
    legacy_open = [r["id"] for r in open_rows if r["platform"] != YT and r["topic"] not in with_cards]
    open_rows = [r for r in open_rows if r["id"] not in set(legacy_open)]
    if legacy or legacy_open:
        log(f"옛 포맷(캡션 카드 없음) 제외: 새 알림 topic {len(legacy)}개, 열려 있던 알림 {len(legacy_open)}건 닫음")
    fresh = dedupe_alerts(alerts, open_rows)
    for r in fresh:
        r.setdefault("resolved_at", None)
        r["detected_at"] = _now()
    fixed = []
    links_by_topic = {}
    for p in mapped:
        links_by_topic.setdefault(p["topic"], set()).update(l for _, l in p["links"])
    for r in open_rows:
        got = links_by_topic.get(r["topic"])
        if r["platform"] == BLOG and got is not None and r.get("old_link") not in got \
                and (not r.get("new_link") or r["new_link"] in got):
            fixed.append(r["id"])
    rep.update(alerts_new=len(fresh), alerts_autoresolved=len(fixed), alerts_legacy_closed=len(legacy_open),
               alerts_open_before=len(open_rows))
    log(f"알림: 새로 {len(fresh)}건(블로그·클립 {sum(1 for r in fresh if r['platform'] != YT)}, 유튜브 기록 "
        f"{sum(1 for r in fresh if r['platform'] == YT)}), 이미 고쳐져 푸는 것 {len(fixed)}건")
    for r in fresh:
        if r["platform"] != YT:
            log(f"  · {r['topic']} {r['platform']} [{r['kind']}] {r['item']}: {r['reason']}")
    if commit:
        import requests
        u, h = _db()
        if fresh:
            rr = requests.post(f"{u}/rest/v1/product_link_alerts", headers=dict(h, Prefer="return=minimal"),
                               json=fresh, timeout=30)
            rr.raise_for_status()
        for i in fixed + legacy_open:
            requests.patch(f"{u}/rest/v1/product_link_alerts?id=eq.{i}", headers=dict(h, Prefer="return=minimal"),
                           json={"resolved_at": _now()}, timeout=30).raise_for_status()
    rep["alerts"] = fresh
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"{profile}.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"[{profile}] 요약 — 글 {rep['posts']}(매칭 {rep['posts_mapped']}) · 링크 {rep['post_links']} · 품목 "
        f"{rep['items_checked']} · 죽음 {len(rep['dead'])} · 수동 {len(rep['manual'])} · 옛 링크 글 "
        f"{len(rep['stale_posts'])} · 확정 대기 {len(pending)} · 유튜브 {len(yt_changes)}편 · 판정 보류 {len(mismatch)} · 오류 {len(errors)}")
    return rep


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default="health,baby,pet", help="health,baby,pet 중 쉼표로")
    ap.add_argument("--commit", action="store_true", help="교체·발급·유튜브 수정·알림 기록까지(기본은 계획만)")
    ap.add_argument("--dry-run", action="store_true", help="기본값 — 계획만 출력")
    ap.add_argument("--posted-only", action="store_true", help="어디든 올라간 topic의 품목만 점검")
    ap.add_argument("--limit", type=int, help="품목 수 상한(시험용)")
    a = ap.parse_args()
    commit = a.commit and not a.dry_run
    failed = []
    for prof in [p.strip() for p in a.profile.split(",") if p.strip()]:
        if prof not in PROFILES:
            raise SystemExit(f"프로필은 {list(PROFILES)} 중 하나")
        try:
            run(prof, commit, a.posted_only, a.limit)
        except SystemExit as e:
            # 한 채널의 Chrome·로그인 문제로 나머지 채널 점검까지 막지 않는다
            log(f"❌ [{prof}] {e}")
            failed.append(prof)
        except RuntimeError as e:
            log(f"❌ [{prof}] {e}")
            failed.append(prof)
    if failed:
        raise SystemExit(f"실패한 채널: {', '.join(failed)}")


if __name__ == "__main__":
    main()
