#!/usr/bin/env python3
"""건강숏츠 유튜브 업로드 — 성인 건강 채널(adult)과 아기 건강 채널(baby), 매일 오후 6시 예약 게시.

WHY(2026-09-27 사용자 "성인 건강이랑 애기 건강도 나눌 거임. 유튜브 두 개 더 팠어 … 매일 오후 6시에"):
주제가 섞이면 추천·구독 유입이 흐려져 채널을 나눴다(세상건강사전은 댕냥사전 전용이 됐다). 채널마다
`.env`의 `YOUTUBE_<CODE>_*` 키(scripts/yt_connect.py가 넣는다)로만 올리고, 올리기 직전 채널 ID를 확인한다.
lib/youtube_upload.py를 그대로 돌리면 개인 채널로 네이버판 영상이 올라가서 따로 뒀다.

    .venv/bin/python3 scripts/yt_upload.py adult whoami
    .venv/bin/python3 scripts/yt_upload.py adult plan                  # 올릴 수 있는 것과 예약안(업로드 안 함)
    .venv/bin/python3 scripts/yt_upload.py adult status
    .venv/bin/python3 scripts/yt_upload.py adult schedule --count 5 --commit   # 다음 빈 18시 슬롯에 예약
    .venv/bin/python3 scripts/yt_upload.py adult reschedule 대사_14 2026-09-28
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from google.auth.transport.requests import Request  # noqa: E402
from google.oauth2.credentials import Credentials  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402
from googleapiclient.errors import HttpError  # noqa: E402
from googleapiclient.http import MediaFileUpload  # noqa: E402

from lib import tracks  # noqa: E402
from lib import youtube_upload as yu  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
# 채널 → 어느 트랙 topic을 올리나. 육아 트랙이 아기 건강, 나머지(트랙 없음)가 성인 건강.
CHANNELS = {"adult": {"track": None}, "baby": {"track": "육아"}}
# 예약 게시 시각(KST). 환경변수로 바꾼다(하드코딩 금지 규칙).
PUBLISH_HOUR = int(os.environ.get("HEALTH_YT_PUBLISH_HOUR", "18"))
# 캡션은 한때 세상건강사전 채널용으로 썼다 — 올릴 때 이 채널 이름으로 바꿔 넣는다
OLD_BRAND_TAG = "#세상건강사전"


class Channel:
    def __init__(self, code: str):
        if code not in CHANNELS:
            raise SystemExit(f"채널은 {list(CHANNELS)} 중 하나")
        self.code, self.track = code, CHANNELS[code]["track"]
        self.env = f"YOUTUBE_{code.upper()}_"
        self.key = f"{code}/"          # youtube_uploaded 표 키 접두어 — 채널끼리 안 섞이게

    def service(self):
        """🚨 올리기 전에 매번 토큰이 가리키는 채널을 확인한다 — 다른 채널이면 여기서 멈춘다."""
        c = Credentials(token=None, refresh_token=os.environ[self.env + "REFRESH_TOKEN"],
                        client_id=os.environ[self.env + "CLIENT_ID"], client_secret=os.environ[self.env + "CLIENT_SECRET"],
                        token_uri="https://oauth2.googleapis.com/token", scopes=yu.SCOPES)
        c.refresh(Request())
        yt = build("youtube", "v3", credentials=c)
        items = yt.channels().list(part="id,snippet", mine=True).execute().get("items", [])
        want = os.environ[self.env + "CHANNEL_ID"]
        if not items or items[0]["id"] != want:
            raise SystemExit(f"❌ 토큰 채널이 {items[0]['id'] if items else '(없음)'} — {self.code}({want})가 아니라서 중단")
        return yt, items[0]["snippet"]["title"]

    def rows(self) -> list[dict]:
        import requests
        r = requests.get(f"{yu.SUPABASE_URL}/rest/v1/youtube_uploaded", headers=yu._SB_HEADERS,
                         params={"select": "topic,video_id,publish_at,status", "topic": f"like.{self.key}*"}, timeout=30)
        r.raise_for_status()
        return r.json()


def _video(topic: str) -> Path:
    # 유튜브판 = 광고 표시 O, 제품 화살표 X (CLAUDE.md 두 벌 규칙)
    return tracks.output_dir(topic) / "nocta" / "shorts_xray_test.mp4"


def _captions_file(topic: str) -> Path | None:
    d = tracks.data_dir(topic)
    return next((p for p in (d / "platform_captions.json", d / "ko" / "platform_captions.json") if p.exists()), None)


def _caption(topic: str) -> tuple[str, str] | None:
    p = _captions_file(topic)
    if not p:
        return None
    plat = next((x for x in json.loads(p.read_text(encoding="utf-8")).get("platforms", []) if x.get("name") == "유튜브 쇼츠"), None)
    if not plat:
        return None
    try:
        return yu._parse_title_description(plat["caption"], "ko")
    except ValueError:
        return None


def _products_block(topic: str) -> str:
    """설명란 맨 앞 제휴 링크 줄 — 유튜브판 영상의 '광고' 표시와 짝(설명란 제휴 링크는 직접 밝힌다)."""
    from lib.brandconnect import existing_naver_links
    p = _captions_file(topic)
    products = json.loads(p.read_text(encoding="utf-8")).get("products", []) if p else []
    links = existing_naver_links()
    lines = [f"▶ {x}: {links[x]}" for x in products if links.get(x)]
    return ("📦 영상 속 제품 (네이버 쇼핑 제휴 링크 — 구매 시 수수료를 받을 수 있어요)\n" + "\n".join(lines) + "\n\n") if lines else ""


def ready_topics(ch: Channel) -> list[tuple[str, list[str]]]:
    """(topic, 막힌 이유들) — 이 채널 트랙의 topic 중 완성본 검사·미션컨트롤 기준을 통과한 것."""
    from lib.mission_control_sync import uploadable_topics
    done = {r["topic"][len(ch.key):] for r in ch.rows()}
    out = []
    for t in sorted(uploadable_topics()):
        if tracks.track_of(t) != ch.track or t in done:
            continue
        why = []
        if not _video(t).exists():
            why.append("유튜브판 영상 없음")
        if _caption(t) is None:
            why.append("'유튜브 쇼츠' 캡션 없음")
        v = subprocess.run([sys.executable, "scripts/verify_output.py", t], cwd=ROOT, capture_output=True, text=True)
        why += [l.strip() for l in v.stdout.splitlines() if l.strip().startswith("·")]
        out.append((t, why))
    return out


def _priority(topic: str) -> tuple:
    # 조회수가 잘 나오는 위고비·마운자로 영상을 앞으로
    title = (_caption(topic) or ("", ""))[0]
    return (0 if ("위고비" in title or "마운자로" in title) else 1, topic)


def next_free_slots(ch: Channel, n: int) -> list[str]:
    """이미 예약된 날짜를 건너뛰고 다음 빈 PUBLISH_HOUR 슬롯 n개(UTC ISO) — 하루 한 편."""
    taken = {dt.datetime.fromisoformat(r["publish_at"].replace("Z", "+00:00")).astimezone(KST).date()
             for r in ch.rows() if r.get("publish_at")}
    now = dt.datetime.now(KST)
    day = now.date() if now < dt.datetime.combine(now.date(), dt.time(PUBLISH_HOUR), KST) - dt.timedelta(minutes=30) \
        else now.date() + dt.timedelta(days=1)
    out = []
    while len(out) < n:
        if day not in taken:
            out.append(dt.datetime.combine(day, dt.time(PUBLISH_HOUR), KST).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        day += dt.timedelta(days=1)
    return out


def _kst(iso: str) -> str:
    return f"{dt.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(KST):%m-%d %H:%M}"


def upload(ch: Channel, yt, channel_title: str, topic: str, privacy: str, publish_at: str | None) -> str:
    title, desc = _caption(topic)
    desc = _products_block(topic) + desc.replace(OLD_BRAND_TAG, "#" + channel_title.replace(" ", ""))
    title = title if len(title) <= 100 else title[:100].rsplit(" ", 1)[0]
    key = ch.key + topic
    if not yu._sb_reserve_upload(key, "ko"):
        raise SystemExit(f"❌ {topic}: 이미 예약·업로드된 기록이 있어 건너뜀(중복 방지)")
    try:
        status = yu._build_status_body(privacy, publish_at)
        status["containsSyntheticMedia"] = True     # AI로 만든 영상 표시
        resp = yt.videos().insert(
            part="snippet,status",
            body={"snippet": {"title": title, "description": desc,
                              "tags": [w[1:] for w in desc.split() if w.startswith("#")],
                              "categoryId": yu.HOWTO_AND_STYLE_CATEGORY,
                              "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
                  "status": status},
            media_body=MediaFileUpload(str(_video(topic)), chunksize=-1, resumable=True, mimetype="video/mp4"),
        ).execute()
    except BaseException:
        yu._sb_release_upload(key)
        raise
    yu._sb_finalize_upload(key, resp["id"], privacy, publish_at)
    return resp["id"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", choices=list(CHANNELS))
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("whoami", "plan", "status"):
        sub.add_parser(c)
    r = sub.add_parser("reschedule"); r.add_argument("topic"); r.add_argument("date", help="YYYY-MM-DD(KST)")
    s = sub.add_parser("schedule"); s.add_argument("--count", type=int, default=5); s.add_argument("--commit", action="store_true")
    a = ap.parse_args()
    ch = Channel(a.channel)

    if a.cmd == "whoami":
        _, name = ch.service(); print(f"✅ {ch.code} 토큰 채널: {name} ({os.environ[ch.env + 'CHANNEL_ID']})"); return
    if a.cmd == "status":
        for row in sorted(ch.rows(), key=lambda x: x.get("publish_at") or ""):
            print(f"  {_kst(row['publish_at']) if row.get('publish_at') else '예약 없음':12s} {row['topic'][len(ch.key):]:10s} "
                  f"{row['status']:9s} https://youtube.com/shorts/{row.get('video_id')}")
        return
    if a.cmd == "reschedule":
        row = next((x for x in ch.rows() if x["topic"] == ch.key + a.topic), None)
        if not row or not row.get("video_id"):
            raise SystemExit(f"❌ {a.topic}: 올라간 기록이 없음")
        when = dt.datetime.combine(dt.date.fromisoformat(a.date), dt.time(PUBLISH_HOUR), KST) \
            .astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        yt, _ = ch.service()
        yt.videos().update(part="status", body={"id": row["video_id"], "status": {
            "privacyStatus": "private", "publishAt": when, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}).execute()
        yu._sb_finalize_upload(ch.key + a.topic, row["video_id"], "public", when)
        print(f"✅ {a.topic} → {_kst(when)} 공개 예약"); return

    rows = ready_topics(ch)
    ok = sorted([t for t, why in rows if not why], key=_priority)
    if a.cmd == "plan" or not a.commit:
        for t, why in rows:
            print(("✅ " if not why else "⛔ ") + t + ("" if not why else "  — " + " / ".join(why)))
        n = len(ok) if a.cmd == "plan" else min(a.count, len(ok))
        print(f"\n{ch.code} 채널 {PUBLISH_HOUR}시 빈 슬롯 예약안:")
        for t, when in zip(ok[:n], next_free_slots(ch, n)):
            print(f"  {_kst(when)}  {t}")
        return

    yt, name = ch.service()
    todo = ok[:a.count]
    for t, when in zip(todo, next_free_slots(ch, len(todo))):
        try:
            vid = upload(ch, yt, name, t, "public", when)
        except HttpError as e:
            # 하루 업로드 한도에 걸리면 멈춘다 — 남은 건 다음 실행이 빈 슬롯부터 이어서 채운다
            if any(k in str(e) for k in ("uploadLimitExceeded", "quotaExceeded")):
                print(f"⏸ 오늘 업로드 한도 도달 — {t}부터는 다음 실행에서"); break
            raise
        print(f"✅ {t} → {_kst(when)} 예약: https://youtube.com/shorts/{vid}")


if __name__ == "__main__":
    main()
