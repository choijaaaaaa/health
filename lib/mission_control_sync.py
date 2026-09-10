# mission-control "게시물 발행" 탭용 캡션 동기화 스크립트. WHY(2026-08-21,
# "health-shorts 쪽 vercel 사이트에 구축되어있는거 mission쪽으로 통합해야겠는데...
# 캡션도 바로바로복사되고 그러니까 기존 health shorts 요구사항을 모두 반영해서
# mission쪽에 녹여내자"): mission-control은 Vercel에 배포돼 어디서든 접근 가능한
# 반면 health-shorts 자신의 대시보드(index.html/output/<topic>/dashboard.html)는
# Basic Auth 뒤에 있고 로컬 파일시스템 기반이라 mission-control이 직접 못 읽는다
# — lib/card_news_hub.py가 형제 버티컬(육아·반려동물·경제)의 네이버 캡션을
# naver_card_news 테이블로 미리 합쳐두는 것과 똑같은 원리로, 이 스크립트는
# health-shorts 자신의 수동 포스팅 대상 캡션을 mission-control 쪽 Supabase
# 스키마로 미리 합쳐둔다. card_news_hub.py가 health/jp_review를 일부러 뺐던 이유
# ("이미 자기 대시보드가 있어서")가 이제 사용자 요청으로 뒤집힌 셈 — 그렇다고
# card_news_hub.py에 얹지 않고 별도 스크립트로 둔 이유는 대상 스키마
# (naver_card_news는 형제 블로그 Supabase, 이건 health-shorts 자신의 Supabase
# mission_control 스키마)와 데이터 모양(캡션 1개 vs topic당 플랫폼 여러 개)이
# 달라서 억지로 합치면 두 함수 다 분기투성이가 된다.
#
# ⚠️ 2026-08-21, "AI영상(1bite-history)·jp-review-shorts도 mission-control로
# 통합" 요청으로 hs_platform_captions에 project 컬럼 추가(UNIQUE도
# (project, topic, platform_name)로 갱신) — 이 스크립트는 계속
# project="health-shorts" 고정, 다른 두 프로젝트는 각자 저장소에 이식된
# 자기 버전의 이 스크립트가 project="jp-review-shorts"/"1bite-history"로
# 같은 테이블에 upsert한다(같은 Supabase 프로젝트, 다른 저장소가 서로의
# 코드를 실시간 참조하지 않는 이 워크스페이스 관례상 파일을 복사해 이식).
#
# 사용법: python3 -m lib.mission_control_sync [--commit]
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

# WHY dashboard.py의 _ALLOWED_PLATFORMS와 정확히 동일한 값을 써야 하는지: 두
# 파일이 어긋나면 mission-control과 로컬 대시보드가 서로 다른 플랫폼 목록을
# 보여주는 사고가 난다 — dashboard.py 쪽 상수가 바뀌면 이것도 같이 바꿀 것
# (같은 리스트를 import해서 공유하지 않는 이유는 dashboard.py가 Jinja류 순수
# 문자열 템플릿 모듈이라 무거운 의존성 없이 상수만 복제하는 쪽이 이 작은
# 동기화 스크립트엔 더 가볍다는 판단).
# ⚠️ 네이버 블로그 단일 채널로 전환(2026-09-09) — dashboard.py 동명 절 WHY 참고.
# ⚠️ 네이버 클립 재추가(2026-09-10): "영상 폐기한다"를 다시 뒤집어 108편을 네이버에
# 올리기로 함 — 다만 유튜브 업로드는 하지 않는다("유튜브 업로드는 안할거고 네이버에만").
# 그래서 영상 트랙 전체를 되살리는 게 아니라 **네이버 두 곳만** 허용한다. 인스타그램
# 릴스·페이스북·쓰레드·유튜브 쇼츠·틱톡 캡션은 데이터로만 남고 화면엔 안 뜬다.
_ALLOWED_PLATFORMS = {"네이버 블로그", "네이버 클립"}


def collect_rows() -> list[dict]:
    """한국어 캡션 파일을 스캔해 수동 포스팅 대상 플랫폼만 골라 행 목록으로 만든다.

    WHY 두 위치를 다 보는지(2026-08-31 실측): 한국어 캡션은 topic당 한 곳에만
    있는데 그 위치가 topic마다 다르다 — 언어 폴더가 없는 옛 topic은
    data/<topic>/platform_captions.json, 언어 폴더가 생긴 topic은
    data/<topic>/ko/platform_captions.json이다(실측 342 대 17, 양쪽 다 있는
    topic은 0개). 예전엔 flat만 스캔해서 ko/ 쪽 17개 topic의 네이버 캡션이
    mission-control 목록에 아예 안 나왔다 — 그 topic들은 개별 대시보드를 직접
    열어야만 캡션을 복사할 수 있었다.
    """
    data_dir = ROOT / "data"
    rows: list[dict] = []
    if not data_dir.is_dir():
        return rows

    for topic_dir in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        captions_path = topic_dir / "platform_captions.json"
        if not captions_path.exists():
            captions_path = topic_dir / "ko" / "platform_captions.json"
        if not captions_path.exists():
            continue
        try:
            data = json.loads(captions_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ⚠️  {topic_dir.name}: platform_captions.json 파싱 실패, 건너뜀")
            continue

        for p in data.get("platforms", []):
            name = p.get("name")
            if name not in _ALLOWED_PLATFORMS:
                continue
            caption = p.get("caption")
            if not caption:
                continue
            rows.append({
                "project": "health-shorts",
                "topic": topic_dir.name,
                "platform_name": name,
                "network": p.get("network"),
                "type": p.get("type"),
                "url": p.get("url") or "",
                "caption": caption,
                "no_caption_link": bool(p.get("no_caption_link")),
                "link_in_comment": bool(p.get("link_in_comment")),
                "comment_dm_automation": bool(p.get("comment_dm_automation")),
                "suppress_product_block": bool(p.get("suppress_product_block")),
                "add_profile_note": bool(p.get("add_profile_note")),
            })
    return rows


# ⚠️ 2026-08-21, "링크 위젯도 있고 요구사항들 엄청 많았을텐데 제대로
# 반영이 안 되어있는거같다" 지적으로 추가 — platform_captions.json
# 최상위(topic 전체 공통, 플랫폼별이 아님)의 products/ad_tag/
# comment_keyword를 topic당 한 행으로 mission_control.topic_meta에
# 동기화한다. mission-control의 상품 링크 덕(dock) 위젯이 이 products
# 목록을 기준으로 쿠팡/네이버 검색 링크를 만들고, ad_tag는 "🏷️ 광고표시
# 적용" 배지, comment_keyword는 댓글→DM 자동화 CTA 문구에 쓰인다
# (lib/dashboard.py의 동일 필드 사용처 그대로 — dashboard.py WHY 참고).
def collect_topic_meta() -> list[dict]:
    data_dir = ROOT / "data"
    rows: list[dict] = []
    if not data_dir.is_dir():
        return rows
    for topic_dir in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        captions_path = topic_dir / "platform_captions.json"
        if not captions_path.exists():
            continue
        try:
            data = json.loads(captions_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        products = data.get("products") or []
        ad_tag = bool(data.get("ad_tag"))
        comment_keyword = data.get("comment_keyword") or (products[0] if products else None)
        if not products and not ad_tag and not comment_keyword:
            continue
        rows.append({
            "project": "health-shorts",
            "topic": topic_dir.name,
            "products": products,
            "ad_tag": ad_tag,
            "comment_keyword": comment_keyword,
        })
    return rows


def collect_topics_index() -> list[dict]:
    """output/topics.json을 그대로 읽어 topics 테이블 행으로 만든다.

    WHY 이 함수가 필요한지(2026-09-10): mission-control 목록의 "트랙" 배지
    (🎬 숏츠 / 🗞 카드뉴스)는 health-shorts 자신의 Supabase `topics` 테이블을
    읽는데, **그 테이블에 밀어넣는 코드가 이 저장소에 없었다** — 2026-09-09
    커밋도 "별도 파이썬 스크립트로 반영"이라고만 적혀 있고 스크립트가 남지
    않았다. 그래서 dashboard.py가 topics.json을 새로 계산해도 화면은 낡은 채로
    남아 "영상 있는 topic이 뭔지 모르겠다"가 됐다. 정식 명령에 넣어 매번 같이
    올라가게 한다."""
    path = ROOT / "output" / "topics.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def push_topics_index(rows: list[dict]) -> int:
    import urllib.request
    import urllib.error

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 .env에 설정되어 있지 않습니다.")

    # ⚠️ topics는 mission_control 스키마가 아니라 health-shorts 자신의 public
    # 스키마에 있다(mission-control의 hsSupabase가 그쪽을 본다) — 아래 두 함수와
    # 달리 Accept/Content-Profile을 붙이지 않는다.
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/topics?on_conflict=topic",
        data=json.dumps(rows).encode("utf-8"),
        method="POST",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"topics upsert 실패: {e.code} {e.read().decode(errors='replace')}") from e
    return len(rows)


def push_topic_meta(rows: list[dict]) -> int:
    import urllib.request
    import urllib.error

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 .env에 설정되어 있지 않습니다.")

    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/topic_meta?on_conflict=project,topic",
        data=body,
        method="POST",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Accept-Profile": "mission_control",
            "Content-Profile": "mission_control",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"upsert 실패: {e.code} {e.read().decode(errors='replace')}") from e
    return len(rows)


def push_to_supabase(rows: list[dict]) -> int:
    import urllib.request
    import urllib.error

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 .env에 설정되어 있지 않습니다.")

    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/hs_platform_captions?on_conflict=project,topic,platform_name",
        data=body,
        method="POST",
        headers={
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
            "Accept-Profile": "mission_control",
            "Content-Profile": "mission_control",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"upsert 실패: {e.code} {e.read().decode(errors='replace')}") from e
    return len(rows)


def main() -> None:
    commit = "--commit" in sys.argv
    rows = collect_rows()
    by_topic: dict[str, int] = {}
    for r in rows:
        by_topic[r["topic"]] = by_topic.get(r["topic"], 0) + 1
    print(f"topic {len(by_topic)}개, 플랫폼 행 {len(rows)}개 발견")
    for topic, count in list(by_topic.items())[:10]:
        print(f"  {topic}: {count}개 플랫폼")
    if len(by_topic) > 10:
        print(f"  ... 외 {len(by_topic) - 10}개 topic")

    meta_rows = collect_topic_meta()
    print(f"topic_meta {len(meta_rows)}개 topic(products/ad_tag/comment_keyword 있는 것만) 발견")

    ti = collect_topics_index()
    shorts = sum(1 for t in ti if "shorts" in (t.get("tracks") or []))
    print(f"topics(트랙 배지) {len(ti)}개 — 이 중 숏츠 {shorts}개")

    if not commit:
        print("\ndry-run — DB에 쓰지 않았습니다. 실제로 넣으려면 --commit을 추가하세요.")
        return

    # WHY 500개씩 나눠 보내는지: Supabase REST 요청 payload 크기 제한 대비
    # (health-shorts topic 규모 실측 500개 넘음, 미리 안전하게 분할).
    total = 0
    for i in range(0, len(rows), 500):
        chunk = rows[i:i + 500]
        total += push_to_supabase(chunk)
    print(f"\n{total}개 행을 mission_control.hs_platform_captions에 upsert했습니다.")

    meta_total = 0
    for i in range(0, len(meta_rows), 500):
        chunk = meta_rows[i:i + 500]
        meta_total += push_topic_meta(chunk)
    print(f"{meta_total}개 행을 mission_control.topic_meta에 upsert했습니다.")

    topic_rows = collect_topics_index()
    topic_total = 0
    for i in range(0, len(topic_rows), 500):
        topic_total += push_topics_index(topic_rows[i:i + 500])
    print(f"{topic_total}개 행을 topics(트랙 배지용)에 upsert했습니다.")


if __name__ == "__main__":
    main()
