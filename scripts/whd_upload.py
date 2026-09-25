#!/usr/bin/env python3
"""세상건강사전(@worldshealthdictionary) 유튜브 채널 업로드 — 아침엔 건강숏츠(육아 포함), 오후엔 댕냥사전.

WHY 따로 스크립트인지(2026-09-25): lib/youtube_upload.py는 언어별 채널 구조(ko = 무접두사 키)라, 그대로
돌리면 `.env`의 기본 토큰이 가리키는 **개인 채널(@choiguevara)**로 올라가고, 영상도 `output/<topic>/
*shorts.mp4` 글롭이 **네이버판(광고 표시 없음, 제품 화살표 있음)**을 집는다. 둘 다 올린 뒤엔 되돌리기
어려운 사고라, 이 채널 전용 키(`YOUTUBE_WHD_*`)·유튜브판 파일·채널 ID 확인을 한 곳에 묶었다.

    .venv/bin/python3 scripts/whd_upload.py whoami                   # 토큰이 어느 채널인지(읽기만)
    .venv/bin/python3 scripts/whd_upload.py plan                     # 올릴 수 있는 topic과 예약 시각(업로드 안 함)
    .venv/bin/python3 scripts/whd_upload.py upload 소화_18 --private  # 한 편을 비공개로(시험용)
    .venv/bin/python3 scripts/whd_upload.py schedule --days 7 --commit   # 다음 7일 아침 슬롯에 예약 게시
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
from googleapiclient.http import MediaFileUpload  # noqa: E402

from lib import youtube_upload as yu  # noqa: E402

KST = dt.timezone(dt.timedelta(hours=9))
# 예약 게시 시각(KST) — 아침 건강숏츠, 오후 댕냥사전. 환경변수로 바꾼다(하드코딩 금지 규칙).
MORNING_HOUR = int(os.environ.get("WHD_MORNING_HOUR", "7"))
AFTERNOON_HOUR = int(os.environ.get("WHD_AFTERNOON_HOUR", "17"))
# youtube_uploaded 표의 키 — 옛 채널 기록과 섞이지 않게 채널 접두어를 붙인다
KEY_PREFIX = "whd/"


def _creds() -> Credentials:
    c = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_WHD_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_WHD_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_WHD_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=yu.SCOPES,
    )
    c.refresh(Request())
    return c


def _service_checked():
    """🚨 올리기 전에 매번 토큰이 가리키는 채널을 확인한다 — 다른 채널이면 여기서 멈춘다."""
    yt = build("youtube", "v3", credentials=_creds())
    items = yt.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    want = os.environ["YOUTUBE_WHD_CHANNEL_ID"]
    if not items or items[0]["id"] != want:
        got = items[0]["id"] if items else "(없음)"
        raise SystemExit(f"❌ 토큰 채널이 {got} — 세상건강사전({want})이 아니라서 중단")
    return yt, items[0]["snippet"]["title"]


def _video(topic: str) -> Path:
    # 유튜브판 = 광고 표시 O, 제품 화살표 X (XRAY_FORMAT·CLAUDE.md 두 벌 규칙)
    return ROOT / "output" / topic / "nocta" / "shorts_xray_test.mp4"


def _caption(topic: str) -> tuple[str, str] | None:
    for p in (ROOT / "data" / topic / "platform_captions.json", ROOT / "data" / topic / "ko" / "platform_captions.json"):
        if not p.exists():
            continue
        plat = next((x for x in json.loads(p.read_text(encoding="utf-8")).get("platforms", [])
                     if x.get("name") == "유튜브 쇼츠"), None)
        if plat:
            try:
                return yu._parse_title_description(plat["caption"], "ko")
            except ValueError:
                return None   # "제목:/설명란:" 형식이 아닌 옛 캡션 — 새로 써야 한다
    return None


def _products_block(topic: str) -> str:
    """설명란 맨 앞에 붙는 제휴 링크 줄 — 유튜브판 영상의 '광고' 표시와 짝이다(CLAUDE.md 두 벌 규칙:
    "설명란 제휴 링크는 화면에 직접 밝혀야 한다"). 링크가 없는 품목은 뺀다."""
    from lib.brandconnect import existing_naver_links
    caps = next((p for p in (ROOT / "data" / topic / "platform_captions.json",
                             ROOT / "data" / topic / "ko" / "platform_captions.json") if p.exists()), None)
    products = json.loads(caps.read_text(encoding="utf-8")).get("products", []) if caps else []
    links = existing_naver_links()
    lines = [f"▶ {p}: {links[p]}" for p in products if links.get(p)]
    if not lines:
        return ""
    return "📦 영상 속 제품 (네이버 쇼핑 제휴 링크 — 구매 시 수수료를 받을 수 있어요)\n" + "\n".join(lines) + "\n\n"


def _uploaded() -> set[str]:
    return {t[len(KEY_PREFIX):] for t in yu._sb_fetch_uploaded() if t.startswith(KEY_PREFIX)}


def ready_topics() -> list[tuple[str, list[str]]]:
    """(topic, 막힌 이유들). 이유가 비어야 올릴 수 있다 — 완성본 검사·미션컨트롤 기준을 그대로 쓴다."""
    from lib.mission_control_sync import uploadable_topics
    done = _uploaded()
    out = []
    for t in sorted(uploadable_topics()):
        if t in done:
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


def slots(n: int, hour: int, start: dt.date | None = None) -> list[str]:
    """다음 n개 예약 시각(UTC ISO). 오늘 슬롯이 이미 지났으면 내일부터."""
    now = dt.datetime.now(KST)
    day = start or now.date()
    first = dt.datetime.combine(day, dt.time(hour), KST)
    if first <= now + dt.timedelta(minutes=30):
        first += dt.timedelta(days=1)
    return [(first + dt.timedelta(days=i)).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            for i in range(n)]


def upload(yt, topic: str, privacy: str, publish_at: str | None) -> str:
    title, desc = _caption(topic)
    desc = _products_block(topic) + desc
    title = title if len(title) <= 100 else title[:100].rsplit(" ", 1)[0]
    key = KEY_PREFIX + topic
    if not yu._sb_reserve_upload(key, "ko"):
        raise SystemExit(f"❌ {topic}: 이미 예약·업로드된 기록이 있어 건너뜀(중복 방지)")
    try:
        status = yu._build_status_body(privacy, publish_at)
        # AI로 만든 영상 표시 — 유튜브 정책상 사실적인 합성 콘텐츠는 공개해야 한다
        status["containsSyntheticMedia"] = True
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
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("whoami")
    sub.add_parser("plan")
    u = sub.add_parser("upload"); u.add_argument("topic"); u.add_argument("--private", action="store_true")
    u.add_argument("--publish-at")
    s = sub.add_parser("schedule"); s.add_argument("--days", type=int, default=7); s.add_argument("--commit", action="store_true")
    a = ap.parse_args()

    if a.cmd == "whoami":
        _, name = _service_checked(); print(f"✅ 토큰 채널: {name} ({os.environ['YOUTUBE_WHD_CHANNEL_ID']})"); return

    rows = ready_topics()
    ok = [t for t, why in rows if not why]
    if a.cmd == "plan" or (a.cmd == "schedule" and not a.commit):
        for t, why in rows:
            print(("✅ " if not why else "⛔ ") + t + ("" if not why else "  — " + " / ".join(why)))
        times = slots(min(a.days if a.cmd == "schedule" else len(ok), len(ok)), MORNING_HOUR)
        print(f"\n아침 {MORNING_HOUR}시 슬롯 예약안:")
        for t, when in zip(ok, times):
            print(f"  {dt.datetime.fromisoformat(when.replace('Z', '+00:00')).astimezone(KST):%m-%d %H:%M}  {t}")
        return

    yt, name = _service_checked()
    if a.cmd == "upload":
        if a.topic not in ok:
            raise SystemExit(f"❌ {a.topic}은 아직 올릴 수 없음: {dict(rows).get(a.topic, ['목록에 없음'])}")
        vid = upload(yt, a.topic, "private" if a.private else "public", a.publish_at)
        print(f"✅ {name}에 업로드: https://youtube.com/shorts/{vid}"); return
    for t, when in zip(ok, slots(a.days, MORNING_HOUR)):
        vid = upload(yt, t, "public", when)
        print(f"✅ {t} → {when} 예약: https://youtube.com/shorts/{vid}")


if __name__ == "__main__":
    main()
