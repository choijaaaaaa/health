# 인스타그램/페이스북에 이미 올라간 게시물과 로컬 topic을 대조해서 "아직 안 올린"
# topic 목록을 뽑는다. WHY 이 스크립트가 필요한지(2026-08-22): 유튜브 쪽은
# youtube_uploaded 테이블로 업로드 시점부터 추적해왔지만, 인스타/페이스북은 이번에
# 처음 API 연동을 했고 그 이전부터 사람이 수동으로 올려온 게시물이 이미 50개+
# 있다 — 새 자동화를 시작하기 전에 현재 상태부터 역산해서 파악해야 한다.
#
# WHY 병명 키워드로 매칭하는지: 실제 게시물 캡션은 platform_captions.json의
# title(예: "안검염, 눈꺼풀 가장자리가...")과 완전히 같은 문장이 아니라 사람이
# 플랫폼마다 손으로 살짝 다르게 쓴 것으로 보인다(예: 인스타 "눈 흰자에 갑자기
# 핏자국이 번진 적 있나요" vs title "결막하출혈, ..."). 대신 title의 쉼표 앞
# 병명 자체는 두 텍스트 모두에 그대로 등장하므로, 문자열 유사도가 아니라
# 병명이 캡션에 포함되는지로 매칭한다.
from __future__ import annotations

import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
GRAPH_BASE = "https://graph.facebook.com/v21.0"


def _fetch_all_captions(url: str, field: str, token: str) -> list[str]:
    captions: list[str] = []
    params = {"fields": field, "limit": 100, "access_token": token}
    while url:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        body = resp.json()
        captions += [item.get(field, "") or "" for item in body.get("data", [])]
        url = body.get("paging", {}).get("next")
        params = {}  # next 링크에 이미 쿼리스트링이 포함돼 있음
    return captions


def _disease_term(title: str) -> str:
    return title.split(",", 1)[0].strip()


def _load_local_topics() -> list[dict]:
    topics = json.loads((ROOT / "output" / "topics.json").read_text(encoding="utf-8"))
    result = []
    for t in topics:
        topic = t["topic"]
        if "/" in topic:  # ko 외 언어·blog_seo 등은 이 감사 대상에서 제외
            continue
        for candidate in (ROOT / "data" / topic / "platform_captions.json",
                           ROOT / "data" / topic / "ko" / "platform_captions.json"):
            if candidate.exists():
                spec = json.loads(candidate.read_text(encoding="utf-8"))
                title = spec.get("title", "")
                if title:
                    result.append({"topic": topic, "title": title, "term": _disease_term(title)})
                break
    return result


def audit() -> dict:
    token = os.environ["META_SYSTEM_USER_TOKEN"]
    ig_id = os.environ["META_WORTHITSHOPPING_IG_ID"]
    page_id = os.environ["META_WORTHITSHOPPING_PAGE_ID"]

    ig_captions = _fetch_all_captions(f"{GRAPH_BASE}/{ig_id}/media", "caption", token)
    fb_captions = _fetch_all_captions(f"{GRAPH_BASE}/{page_id}/videos", "description", token)
    print(f"[meta_posting_audit] Instagram 게시물 {len(ig_captions)}개, Facebook 게시물 {len(fb_captions)}개 조회됨")

    local_topics = _load_local_topics()
    print(f"[meta_posting_audit] 로컬 topic {len(local_topics)}개 확인")

    ig_posted, fb_posted, not_posted_either = [], [], []
    for t in local_topics:
        term = t["term"]
        on_ig = any(term in c for c in ig_captions)
        on_fb = any(term in c for c in fb_captions)
        if on_ig:
            ig_posted.append(t["topic"])
        if on_fb:
            fb_posted.append(t["topic"])
        if not on_ig and not on_fb:
            not_posted_either.append(t["topic"])

    return {
        "total_local_topics": len(local_topics),
        "ig_posted_count": len(ig_posted),
        "fb_posted_count": len(fb_posted),
        "not_posted_either": not_posted_either,
    }


if __name__ == "__main__":
    result = audit()
    print(f"\n=== 요약 ===")
    print(f"로컬 topic 총 {result['total_local_topics']}개")
    print(f"Instagram에 이미 올라간 것: {result['ig_posted_count']}개")
    print(f"Facebook에 이미 올라간 것: {result['fb_posted_count']}개")
    print(f"둘 다 아직 안 올라간 topic: {len(result['not_posted_either'])}개")
    for topic in result["not_posted_either"][:30]:
        print(f"  - {topic}")
