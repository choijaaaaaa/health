#!/usr/bin/env python3
"""쇼츠마다 '핵심 제품 하나 + 한 줄 이유 + 제휴 링크' 댓글을 단다(건강만사전 adult · 육아만사전 baby).

WHY(2026-10-06 사용자 "설명란의 링크를 아무도 안 봐서, 가장 핵심이 되는 링크 하나만 댓글에 설명과 함께"):
설명란은 안 펼쳐 본다. 쇼츠 댓글·설명란 링크는 2023년부터 클릭이 안 되는(글자로만 보이는) 제약이 있지만
사용자가 감수하기로 했다. 문구는 `data/_audit/yt_comment_lines.json`({topic: {product, reason}}).
댓글 고정은 API에 없다 — 스튜디오에서 손으로.

중복 방지는 상태 파일 없이 한다: 단 댓글 중 이 채널이 쓴 것에 같은 링크가 있으면 건너뛴다.
공개 전(예약) 영상엔 댓글이 안 달리므로 공개된 것만 단다 — 매일 launchd(health_yt.sh)가 돌린다.

    .venv/bin/python3 scripts/yt_comment.py adult            # 무엇을 달지만
    .venv/bin/python3 scripts/yt_comment.py adult --commit
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import yt_upload as y  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402

LINES = ROOT / "data" / "_audit" / "yt_comment_lines.json"
# 공정위 추천·보증 지침 — 제휴 링크가 들어간 글마다 표시
DISCLOSURE = "(네이버 쇼핑 제휴 링크 — 구매 시 수수료를 받을 수 있어요)"


def comment_text(product: str, reason: str, link: str) -> str:
    return f"[광고] 영상 속 {product}\n{reason}\n👉 {link}\n{DISCLOSURE}"


def _already(yt, video_id: str, channel_id: str, link: str) -> bool:
    res = yt.commentThreads().list(part="snippet", videoId=video_id, maxResults=100, textFormat="plainText").execute()
    for it in res.get("items", []):
        s = it["snippet"]["topLevelComment"]["snippet"]
        if s.get("authorChannelId", {}).get("value") == channel_id and link in s.get("textDisplay", ""):
            return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", choices=list(y.CHANNELS))
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()
    ch = y.Channel(a.channel)
    from lib.brandconnect import existing_naver_links
    lines = json.loads(LINES.read_text(encoding="utf-8")) if LINES.exists() else {}
    links = existing_naver_links()
    now = dt.datetime.now(dt.timezone.utc)
    yt = cid = None
    done = skipped = 0
    for row in sorted(ch.rows(), key=lambda r: r.get("publish_at") or ""):
        topic, vid = row["topic"][len(ch.key):], row.get("video_id")
        spec = lines.get(topic)
        if not vid or not spec or not links.get(spec["product"]):
            continue
        when = row.get("publish_at")
        if when and dt.datetime.fromisoformat(when.replace("Z", "+00:00")) > now:
            skipped += 1          # 예약(비공개) 영상엔 댓글을 못 단다 — 공개 뒤 다음 회차에서
            continue
        text = comment_text(spec["product"], spec["reason"], links[spec["product"]])
        if not a.commit:
            print(f"  [미리보기] {topic}: {spec['product']}")
            continue
        if yt is None:
            yt, _ = ch.service()
            cid = os.environ[ch.env + "CHANNEL_ID"]
        try:
            if _already(yt, vid, cid, links[spec["product"]]):
                continue
            yt.commentThreads().insert(part="snippet", body={"snippet": {
                "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": text}}}}).execute()
            done += 1
            print(f"  ✅ {topic}: {spec['product']}")
        except HttpError as e:
            print(f"  ❌ {topic}: {e.status_code if hasattr(e, 'status_code') else ''} {str(e)[:160]}")
    print(f"{ch.code}: 단 댓글 {done} · 공개 전이라 미룸 {skipped}{'' if a.commit else ' (미리보기 — --commit 없이는 안 단다)'}")


if __name__ == "__main__":
    main()
