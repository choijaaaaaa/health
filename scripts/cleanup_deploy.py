#!/usr/bin/env python3
"""mission-control Upload 탭에서 목표 플랫폼이 전부 체크된(완료) topic의
공용 `ai-video-network/deploy/health-shorts/` **복사본**(shorts.mp4 +
card_news/)만 지운다 — 원본(`output/<topic>/`)은 절대 건드리지 않는다
(2026-09-18, ai-video-network/tools/cleanup_deploy.py와 동일 패턴 이식,
위치는 stage_for_deploy.py와 동일 경위로 두 번 정정됨 — 그쪽 파일 상단
WHY 참고, 최종은 1biteinfo/worlds-figure와 섞이지 않는 이 프로젝트 전용
서브폴더).

완료 판정은 mission-control 웹앱(app/(dashboard)/upload/page.tsx의
UploadTable/PostingBadge)과 동일 기준: hs_platform_captions(project=
'health-shorts'인 목표 플랫폼 — 네이버 블로그(type='text')·네이버
클립(type='video') 둘 다, health-shorts엔 type='cards' 자체가 없음
2026-09-18 실측 확인)와 posting_log(실제 체크된 플랫폼)를 대조해
postedCount === platformCount(그리고 >0)인 topic만 완료로 본다 — 즉
카드뉴스(네이버 블로그)·영상(네이버 클립) **둘 다 체크돼야** deploy/
복사본을 지운다. 두 테이블 다 이 프로젝트 자신의 Supabase 프로젝트
안에 있다(하나는 public 스키마, 하나는 mission_control 스키마 — 다른
프로젝트처럼 자격증명을 따로 복사해올 필요 없음, health-shorts/.env
SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY 하나로 둘 다 조회 가능).

사용법(health-shorts/ 루트에서):
    python3 scripts/cleanup_deploy.py            # 뭐가 지워질지만 미리 보기
    python3 scripts/cleanup_deploy.py --commit    # 실제로 deploy/ 하위 폴더 삭제
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DEPLOY_DIR = ROOT.parent / "ai-video-network" / "deploy" / "health-shorts"
load_dotenv(ROOT / ".env")

# WHY 기본 User-Agent를 갈아끼우는지: lib/mission_control_sync.py와 동일 사유
# (Cloudflare 엣지가 파이썬 기본 UA를 403으로 막음, 2026-09-13).
_UA = "Mozilla/5.0 (compatible; project-tools/1.0)"


def _fetch_all(url: str, key: str, table: str, select: str, profile: str | None, extra: str = "") -> list[dict]:
    page_size = 1000
    rows: list[dict] = []
    offset = 0
    while True:
        headers = {"apikey": key, "Authorization": f"Bearer {key}", "User-Agent": _UA}
        if profile:
            headers["Accept-Profile"] = profile
        params = f"select={select}&limit={page_size}&offset={offset}{extra}"
        req = urllib.request.Request(f"{url}/rest/v1/{table}?{params}", headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                chunk = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{table} 조회 실패: {e.code} {e.read().decode(errors='replace')}") from e
        rows.extend(chunk)
        if len(chunk) < page_size:
            break
        offset += page_size
    return rows


def _completed_topics() -> set[str]:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

    captions = _fetch_all(
        url, key, "hs_platform_captions", "topic,platform_name,type", "mission_control",
        extra="&project=eq.health-shorts",
    )
    posting_log = _fetch_all(url, key, "posting_log", "topic,platform", None)

    posted_by_topic: dict[str, set[str]] = {}
    for row in posting_log:
        posted_by_topic.setdefault(row["topic"], set()).add(row["platform"])

    targets: dict[str, set[str]] = {}
    for row in captions:
        targets.setdefault(row["topic"], set()).add(row["platform_name"])

    completed = set()
    for topic, target in targets.items():
        if not target:
            continue
        posted = posted_by_topic.get(topic, set())
        if target.issubset(posted):
            completed.add(topic)
    return completed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", action="store_true", help="실제로 삭제(기본은 미리보기만)")
    args = parser.parse_args()

    completed = _completed_topics()
    if not completed or not DEPLOY_DIR.is_dir():
        print("mission-control 기준 완료된 topic이 없습니다.")
        return

    removed = 0
    for topic in sorted(completed):
        target = DEPLOY_DIR / topic
        if not target.is_dir():
            continue
        if args.commit:
            shutil.rmtree(target)
            print(f"삭제됨: deploy/health-shorts/{topic}")
        else:
            print(f"[dry-run] 삭제 예정: deploy/health-shorts/{topic}")
        removed += 1

    verb = "삭제" if args.commit else "삭제 예정(--commit으로 실행)"
    print(f"\n{verb}: {removed}개 폴더 — 원본(output/<topic>/)은 그대로 유지됨")


if __name__ == "__main__":
    main()
