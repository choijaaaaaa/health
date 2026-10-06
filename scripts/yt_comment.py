#!/usr/bin/env python3
"""쇼츠마다 "제품 정보는 설명란에" 안내 댓글을 단다(건강만사전 adult · 육아만사전 baby).

WHY(2026-10-06): 처음엔 사용자 "설명란의 링크를 아무도 안 봐서, 핵심 링크 하나만 설명과 함께 댓글로"에 따라
[광고]·제품·이유·링크를 댓글로 달았다. 같은 날 사용자 "댓글은 선택해서 링크를 복사하는 것조차도 안 돼. 광고 이런 것도
없애고 제품에 대한 내용 없애자. 그냥 상세한 내용은 설명창 참조하라는 식으로" → 링크·제품 없이 설명란 안내 한 줄만.
링크가 없으니 광고 표시는 설명란(제휴 링크 줄과 함께)에만 둔다. 설명란에 제품 줄이 있는 영상에만 단다.

중복 방지: 단 뒤 DB `youtube_uploaded.commented_at`에 시각을 적고, 적힌 행은 유튜브를 다시 조회하지 않는다.
공개 전(예약) 영상엔 댓글이 안 달리므로 공개된 것만 — launchd(10:30 health_yt.sh, 18:20 yt_comment_evening.sh).
`--rewrite`: 예전 형식([광고]·링크)으로 단 댓글을 지금 문구로 고친다(한 번만).

    .venv/bin/python3 scripts/yt_comment.py adult            # 무엇을 달지만
    .venv/bin/python3 scripts/yt_comment.py adult --commit
    .venv/bin/python3 scripts/yt_comment.py adult --rewrite --commit
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import yt_upload as y  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402

TEXT = "📌 영상에 나온 제품과 자세한 내용은 설명란(더보기)에 정리해 뒀어요."
# 예전 형식 댓글을 알아보는 표시 — --rewrite가 이걸 찾아 고친다
OLD_MARK = "[광고] 영상 속"


def _mine(yt, video_id: str, channel_id: str) -> list[dict]:
    res = yt.commentThreads().list(part="snippet", videoId=video_id, maxResults=100, textFormat="plainText").execute()
    return [it["snippet"]["topLevelComment"] for it in res.get("items", [])
            if it["snippet"]["topLevelComment"]["snippet"].get("authorChannelId", {}).get("value") == channel_id]


def _mark(key: str) -> None:
    """댓글 단 행에 시각을 적는다 — 다음 회차엔 유튜브 조회 없이 건너뛴다."""
    import requests
    yu = y.yu
    requests.patch(f"{yu.SUPABASE_URL}/rest/v1/youtube_uploaded", headers={**yu._SB_HEADERS, "Prefer": "return=minimal"},
                   params={"topic": f"eq.{key}"},
                   json={"commented_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, timeout=30).raise_for_status()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", choices=list(y.CHANNELS))
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--rewrite", action="store_true", help="예전 형식 댓글을 지금 문구로 고친다")
    a = ap.parse_args()
    ch = y.Channel(a.channel)
    now = dt.datetime.now(dt.timezone.utc)
    yt = cid = None
    done = fixed = skipped = 0
    for row in sorted(ch.rows(), key=lambda r: r.get("publish_at") or ""):
        topic, vid = row["topic"][len(ch.key):], row.get("video_id")
        if not vid or not y._products_block(topic):
            continue                     # 설명란에 제품 줄이 없으면 안내할 게 없다
        if row.get("commented_at") and not a.rewrite:
            continue
        when = row.get("publish_at")
        if when and dt.datetime.fromisoformat(when.replace("Z", "+00:00")) > now:
            skipped += 1                 # 예약(비공개) 영상엔 댓글을 못 단다 — 공개 뒤 다음 회차에서
            continue
        if not a.commit:
            print(f"  [미리보기] {topic}")
            continue
        if yt is None:
            yt, _ = ch.service()
            cid = os.environ[ch.env + "CHANNEL_ID"]
        try:
            mine = _mine(yt, vid, cid)
            old = [c for c in mine if OLD_MARK in c["snippet"].get("textDisplay", "")]
            if old:
                for c in old:
                    yt.comments().update(part="snippet", body={"id": c["id"], "snippet": {"textOriginal": TEXT}}).execute()
                fixed += 1
                print(f"  ✏️  {topic}: 예전 댓글 고침")
            elif not any(TEXT in c["snippet"].get("textDisplay", "") for c in mine):
                yt.commentThreads().insert(part="snippet", body={"snippet": {
                    "videoId": vid, "topLevelComment": {"snippet": {"textOriginal": TEXT}}}}).execute()
                done += 1
                print(f"  ✅ {topic}")
            _mark(row["topic"])
        except HttpError as e:
            print(f"  ❌ {topic}: {str(e)[:200]}")
    print(f"{ch.code}: 새 댓글 {done} · 고친 댓글 {fixed} · 공개 전이라 미룸 {skipped}"
          f"{'' if a.commit else ' (미리보기 — --commit 없이는 안 단다)'}")


if __name__ == "__main__":
    main()
