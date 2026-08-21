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
# 사용법: python3 -m lib.mission_control_sync [--commit]
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent

# WHY dashboard.py의 _UI_EXCLUDED_PLATFORMS와 정확히 동일한 값을 써야 하는지:
# 저기서 카드로 안 보여주는 플랫폼(자동 업로드되거나 UI에서만 숨긴 것)은
# 여기서도 "수동으로 캡션 복사+링크 이동"이 필요 없다는 뜻이라 똑같이 뺀다.
# 두 파일이 어긋나면 mission-control과 로컬 대시보드가 서로 다른 플랫폼
# 목록을 보여주는 사고가 난다 — dashboard.py 쪽 상수가 바뀌면 이것도 같이
# 바꿀 것(같은 리스트를 import해서 공유하지 않는 이유는 dashboard.py가
# Jinja류 순수 문자열 템플릿 모듈이라 무거운 의존성 없이 상수만 복제하는
# 쪽이 이 작은 동기화 스크립트엔 더 가볍다는 판단).
_UI_EXCLUDED_PLATFORMS = {
    "유튜브 쇼츠", "틱톡", "YouTube Shorts", "TikTok",
    "인스타그램 카드뉴스", "Instagram Carousel",
}


def collect_rows() -> list[dict]:
    """data/<topic>/platform_captions.json(플랫 구조 — ko 영상/카드뉴스
    topic만 해당, blog_seo처럼 언어 서브폴더가 있는 topic은 대상 아님)을
    스캔해 수동 포스팅 대상 플랫폼만 골라 행 목록으로 만든다."""
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
            print(f"  ⚠️  {topic_dir.name}: platform_captions.json 파싱 실패, 건너뜀")
            continue

        for p in data.get("platforms", []):
            name = p.get("name")
            if not name or name in _UI_EXCLUDED_PLATFORMS:
                continue
            caption = p.get("caption")
            if not caption:
                continue
            rows.append({
                "topic": topic_dir.name,
                "platform_name": name,
                "network": p.get("network"),
                "type": p.get("type"),
                "url": p.get("url") or "",
                "caption": caption,
                "no_caption_link": bool(p.get("no_caption_link")),
            })
    return rows


def push_to_supabase(rows: list[dict]) -> int:
    import urllib.request
    import urllib.error

    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 .env에 설정되어 있지 않습니다.")

    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        f"{supabase_url}/rest/v1/hs_platform_captions?on_conflict=topic,platform_name",
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


if __name__ == "__main__":
    main()
