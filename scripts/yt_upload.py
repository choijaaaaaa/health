#!/usr/bin/env python3
"""건강숏츠 유튜브 업로드 — 성인 건강 채널(adult)과 아기 건강 채널(baby), 매일 오후 6시 예약 게시.

WHY(2026-09-27 사용자 "성인 건강이랑 애기 건강도 나눌 거임. 유튜브 두 개 더 팠어 … 매일 오후 6시에"):
주제가 섞이면 추천·구독 유입이 흐려져 채널을 나눴다(세상건강사전은 댕냥사전 전용이 됐다). 채널마다
`.env`의 `YOUTUBE_<CODE>_*` 키(scripts/yt_connect.py가 넣는다)로만 올리고, 올리기 직전 채널 ID를 확인한다.
lib/youtube_upload.py를 그대로 돌리면 개인 채널로 네이버판 영상이 올라가서 따로 뒀다.

    .venv/bin/python3 scripts/yt_upload.py adult whoami
    .venv/bin/python3 scripts/yt_upload.py adult plan                  # 올릴 수 있는 것과 예약안(업로드 안 함)
    .venv/bin/python3 scripts/yt_upload.py adult status
    .venv/bin/python3 scripts/yt_upload.py adult schedule --count 5 --commit   # 다음 빈 슬롯(8시·18시)에 예약
    .venv/bin/python3 scripts/yt_upload.py adult reschedule 대사_14 2026-09-28
    .venv/bin/python3 scripts/yt_upload.py baby replace 육아_7          # 공개 전 예약 영상을 새 파일로 교체
    .venv/bin/python3 scripts/yt_upload.py adult longform output/_longform/adult_stomach_20261025 --at "2026-10-26 20:00"
                                                                       # 몰아보기 롱폼(compile_longform.py 결과) — --commit 없으면 미리보기만
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
CHANNELS = {"adult": {"track": None, "base_tags": ["건강만사전", "건강정보", "건강쇼츠"]},
            "baby": {"track": "육아", "base_tags": ["육아만사전", "육아정보", "아기건강", "육아"]}}
# 예약 게시 시각(KST), 하루 여러 편이면 쉼표로. 환경변수로 바꾼다(하드코딩 금지 규칙).
# WHY(2026-10-14 사용자 "건강, 육아, 댕냥 전부 오전 10시 / 오후 5시 업로드로 바꾸자. 하루에 두 번"): 10시·17시 두 편.
# (10-09엔 18시 한 편, 10-06엔 8시·18시였다.)
PUBLISH_HOURS = sorted(int(h) for h in os.environ.get("HEALTH_YT_PUBLISH_HOURS", "17").split(","))
PUBLISH_HOUR = PUBLISH_HOURS[-1]   # reschedule에 날짜만 줄 때 쓰는 기본 시각(저녁)
# 캡션은 한때 세상건강사전 채널용으로 썼다 — 올릴 때 이 채널 이름으로 바꿔 넣는다
OLD_BRAND_TAG = "#세상건강사전"
# 설명란 제휴 링크 고지 — 쇼츠·몰아보기 롱폼이 같은 문구를 쓴다
PRODUCT_LINK_NOTICE = "네이버 쇼핑 제휴 링크 — 구매 시 수수료를 받을 수 있어요"
# 몰아보기 롱폼은 youtube_uploaded에 `<채널>/longform/<폴더명>`으로 남긴다. WHY 쇼츠 행에서 빼는지: 17시 슬롯 계산
# (next_free_slots)이 이 행의 공개 시각을 "그날 17시 쇼츠가 찼다"로 읽으면 그날 쇼츠 한 편이 밀린다.
LONGFORM = "longform/"


class Channel:
    def __init__(self, code: str):
        if code not in CHANNELS:
            raise SystemExit(f"채널은 {list(CHANNELS)} 중 하나")
        self.code, self.track = code, CHANNELS[code]["track"]
        self.base_tags = CHANNELS[code]["base_tags"]
        self.env = f"YOUTUBE_{code.upper()}_"
        self.key = f"{code}/"          # youtube_uploaded 표 키 접두어 — 채널끼리 안 섞이게

    def service(self):
        """🚨 올리기 전에 매번 토큰이 가리키는 채널을 확인한다 — 다른 채널이면 여기서 멈춘다."""
        c = Credentials(token=None, refresh_token=os.environ[self.env + "REFRESH_TOKEN"],
                        client_id=os.environ[self.env + "CLIENT_ID"], client_secret=os.environ[self.env + "CLIENT_SECRET"],
                        token_uri="https://oauth2.googleapis.com/token", scopes=None)  # 동의받은 범위 그대로(업로드+댓글) — 범위를 지정하면 덜 받은 토큰이 갱신에 실패한다
        c.refresh(Request())
        yt = build("youtube", "v3", credentials=c)
        items = yt.channels().list(part="id,snippet", mine=True).execute().get("items", [])
        want = os.environ[self.env + "CHANNEL_ID"]
        if not items or items[0]["id"] != want:
            raise SystemExit(f"❌ 토큰 채널이 {items[0]['id'] if items else '(없음)'} — {self.code}({want})가 아니라서 중단")
        return yt, items[0]["snippet"]["title"]

    def rows(self, include_longform: bool = False) -> list[dict]:
        """이 채널 업로드 기록. 기본은 쇼츠 행만 — 슬롯 계산·올릴 후보·안내 댓글이 롱폼 행을 topic으로 읽지 않게."""
        import requests
        r = requests.get(f"{yu.SUPABASE_URL}/rest/v1/youtube_uploaded", headers=yu._SB_HEADERS,
                         params={"select": "topic,video_id,publish_at,status,commented_at", "topic": f"like.{self.key}*"}, timeout=30)
        r.raise_for_status()
        return [x for x in r.json() if include_longform or not x["topic"].startswith(self.key + LONGFORM)]


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


def _products(topic: str) -> list[str]:
    p = _captions_file(topic)
    return [x for x in (json.loads(p.read_text(encoding="utf-8")).get("products") or []) if x and x != "-"] if p else []


def product_lines(topic: str, links: dict[str, str] | None = None) -> list[str]:
    """`▶ 품목: 링크` 줄들 — 링크가 발급된 품목만. link_health가 설명란에서 이 꼴을 찾아 죽은 링크를 고친다."""
    if links is None:
        from lib.brandconnect import existing_naver_links
        links = existing_naver_links()
    return [f"▶ {x}: {links[x]}" for x in _products(topic) if links.get(x)]


def _products_block(topic: str) -> str:
    """설명란 맨 앞 제휴 링크 줄 — 유튜브판 영상의 '광고' 표시와 짝(설명란 제휴 링크는 직접 밝힌다)."""
    lines = product_lines(topic)
    return (f"📦 영상 속 제품 ({PRODUCT_LINK_NOTICE})\n" + "\n".join(lines) + "\n\n") if lines else ""


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
    """이미 예약된 시각을 건너뛰고 다음 빈 슬롯 n개(UTC ISO) — 하루 PUBLISH_HOURS 시각마다 한 편."""
    taken = {dt.datetime.fromisoformat(r["publish_at"].replace("Z", "+00:00")).astimezone(KST).replace(minute=0, second=0)
             for r in ch.rows() if r.get("publish_at")}
    # 유튜브 예약은 지금보다 충분히 뒤여야 받는다 — 30분 안쪽 슬롯은 건너뛴다
    earliest = dt.datetime.now(KST) + dt.timedelta(minutes=30)
    day, out = earliest.date(), []
    while len(out) < n:
        for h in PUBLISH_HOURS:
            slot = dt.datetime.combine(day, dt.time(h), KST)
            if slot > earliest and slot not in taken and len(out) < n:
                out.append(slot.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
        day += dt.timedelta(days=1)
    return out


def _kst(iso: str) -> str:
    return f"{dt.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(KST):%m-%d %H:%M}"


def _tags(desc: str, base: list[str], items: list[str] = ()) -> list[str]:
    """영상 태그 = 제품 이름 + 설명란 해시태그 + 채널 기본 태그(중복 없이, 유튜브 태그 한도 500자 안).

    제품 이름은 띄어 쓴 그대로 맨 앞에 — 해시태그는 붙여 써야 해서 사람들이 실제로 치는 "세라마이드 바디크림"이
    태그에 없었다(2026-10-08 사용자 "태그도 그 제품 명칭이 들어가면 … 제품으로 다이렉트로 유입될 수도")."""
    out: list[str] = []
    for t in list(items) + [w[1:] for w in desc.split() if w.startswith("#")] + base:
        if t and t not in out and len(",".join(out + [t])) <= 480:
            out.append(t)
    return out


def _insert(ch: Channel, yt, channel_title: str, topic: str, privacy: str, publish_at: str | None) -> str:
    """유튜브에 올리기만 한다(DB 기록은 부르는 쪽이 맡는다)."""
    title, desc = _caption(topic)
    desc = _products_block(topic) + desc.replace(OLD_BRAND_TAG, "#" + channel_title.replace(" ", ""))
    title = title if len(title) <= 100 else title[:100].rsplit(" ", 1)[0]
    status = yu._build_status_body(privacy, publish_at)
    status["containsSyntheticMedia"] = True     # AI로 만든 영상 표시
    resp = yt.videos().insert(
        part="snippet,status",
        body={"snippet": {"title": title, "description": desc,
                          "tags": _tags(desc, ch.base_tags, _products(topic)),
                          "categoryId": yu.HOWTO_AND_STYLE_CATEGORY,
                          "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
              "status": status},
        media_body=MediaFileUpload(str(_video(topic)), chunksize=-1, resumable=True, mimetype="video/mp4"),
    ).execute()
    return resp["id"]


def upload(ch: Channel, yt, channel_title: str, topic: str, privacy: str, publish_at: str | None) -> str:
    key = ch.key + topic
    if not yu._sb_reserve_upload(key, "ko"):
        raise SystemExit(f"❌ {topic}: 이미 예약·업로드된 기록이 있어 건너뜀(중복 방지)")
    try:
        vid = _insert(ch, yt, channel_title, topic, privacy, publish_at)
    except BaseException:
        yu._sb_release_upload(key)
        raise
    yu._sb_finalize_upload(key, vid, privacy, publish_at)
    return vid


def read_longform_upload(folder: Path) -> tuple[str, str, list[str]]:
    """compile_longform.py가 쓴 upload.md → (제목, 설명란, 태그). 사람이 upload.md를 고쳤으면 고친 대로 올라간다.

    형식: `제목: …` / 빈 줄 / `설명란:` 다음 줄부터 본문 / 빈 줄 / 마지막 `태그: a, b, c`."""
    text = (folder / "upload.md").read_text(encoding="utf-8").strip()
    head, sep, tag_line = text.rpartition("\n\n태그: ")
    title_part, sep2, desc = head.partition("\n\n설명란:\n")
    if not sep or not sep2 or not title_part.startswith("제목: "):
        raise SystemExit(f"❌ {folder / 'upload.md'}: '제목:' / '설명란:' / '태그:' 형식이 아님")
    title, desc = title_part[len("제목: "):].strip(), desc.strip()
    # 유튜브가 거부하는 것 — 제목 100자·설명 5000바이트 초과, 꺾쇠(<>)
    if len(title) > 100 or len(desc.encode("utf-8")) > 5000 or any(c in title + desc for c in "<>"):
        raise SystemExit(f"❌ 제목 {len(title)}자 / 설명 {len(desc.encode('utf-8'))}바이트 — 유튜브 한도(100자·5000바이트·꺾쇠 금지) 초과")
    return title, desc, [t.strip() for t in tag_line.split(",") if t.strip()]


def upload_longform(ch: Channel, folder: Path, publish_at: str) -> str:
    """몰아보기 롱폼을 비공개로 올리고 publish_at(UTC ISO)에 공개되게 예약한 뒤 썸네일을 붙인다.

    기록 키는 `<채널>/longform/<폴더명>` — 쇼츠 슬롯·후보 계산은 rows()가 이 키를 빼고 본다."""
    man = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    if man.get("channel") != ch.code:
        raise SystemExit(f"❌ {folder.name}는 {man.get('channel')} 채널용 — {ch.code}로 올리지 않음")
    video, thumb = folder / "longform.mp4", folder / "thumbnail.jpg"
    if not video.exists():
        raise SystemExit(f"❌ 영상 없음: {video}")
    title, desc, tags = read_longform_upload(folder)
    key = ch.key + LONGFORM + folder.name
    yt, _ = ch.service()
    if not yu._sb_reserve_upload(key, "ko"):
        raise SystemExit(f"❌ {key}: 이미 예약·업로드된 기록이 있어 건너뜀(중복 방지)")
    try:
        status = yu._build_status_body("private", publish_at)
        status["containsSyntheticMedia"] = True     # 쇼츠와 같은 AI 생성 표시
        vid = yt.videos().insert(
            part="snippet,status",
            body={"snippet": {"title": title, "description": desc, "tags": tags,
                              "categoryId": yu.HOWTO_AND_STYLE_CATEGORY,
                              "defaultLanguage": "ko", "defaultAudioLanguage": "ko"},
                  "status": status},
            media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True, mimetype="video/mp4"),
        ).execute()["id"]
    except BaseException:
        yu._sb_release_upload(key)
        raise
    yu._sb_finalize_upload(key, vid, "public", publish_at)
    if thumb.exists():
        # 커스텀 썸네일은 채널 전화번호 인증이 없으면 403 — 영상 업로드·예약은 이미 끝났으니 알리고 넘어간다
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
        except HttpError as e:
            print(f"⚠️ 썸네일 설정 실패(영상·예약은 완료) — 스튜디오에서 {thumb}를 직접 올릴 것: {str(e)[:160]}")
    return vid


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", choices=list(CHANNELS))
    sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("whoami", "plan", "status"):
        sub.add_parser(c)
    r = sub.add_parser("reschedule"); r.add_argument("topic"); r.add_argument("date", help="YYYY-MM-DD(KST)")
    r.add_argument("--hour", type=int, default=None, help="공개 시각(KST 시). 없으면 하루 마지막 슬롯")
    s = sub.add_parser("schedule"); s.add_argument("--count", type=int, default=5); s.add_argument("--commit", action="store_true")
    rp = sub.add_parser("replace", help="공개 전 예약 영상을 지금 영상 파일로 갈아 끼운다(같은 공개 시각)")
    rp.add_argument("topic")
    lf = sub.add_parser("longform", help="몰아보기 롱폼(compile_longform.py 결과 폴더)을 비공개로 올려 예약 — --commit 없으면 미리보기")
    lf.add_argument("dir", help="output/_longform/<채널>_<테마>_<날짜>")
    lf.add_argument("--at", required=True, help="공개 시각 KST 'YYYY-MM-DD HH:MM'")
    lf.add_argument("--commit", action="store_true")
    a = ap.parse_args()
    ch = Channel(a.channel)

    if a.cmd == "whoami":
        _, name = ch.service(); print(f"✅ {ch.code} 토큰 채널: {name} ({os.environ[ch.env + 'CHANNEL_ID']})"); return
    if a.cmd == "status":
        for row in sorted(ch.rows(include_longform=True), key=lambda x: x.get("publish_at") or ""):
            kind = "watch?v=" if row["topic"].startswith(ch.key + LONGFORM) else "shorts/"
            print(f"  {_kst(row['publish_at']) if row.get('publish_at') else '예약 없음':12s} {row['topic'][len(ch.key):]:10s} "
                  f"{row['status']:9s} https://youtube.com/{kind}{row.get('video_id')}")
        return
    if a.cmd == "longform":
        folder = Path(a.dir) if Path(a.dir).is_dir() else ROOT / a.dir
        when_kst = dt.datetime.strptime(a.at, "%Y-%m-%d %H:%M").replace(tzinfo=KST)
        if when_kst < dt.datetime.now(KST) + dt.timedelta(minutes=30):
            raise SystemExit(f"❌ 공개 시각 {a.at}는 지금부터 30분 안쪽이거나 지났다 — 유튜브 예약이 거부한다")
        when = when_kst.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        title, desc, tags = read_longform_upload(folder)
        print(f"제목({len(title)}자): {title}\n설명 {len(desc.encode('utf-8'))}바이트 · 태그 {len(tags)}개 · 공개 {a.at} KST\n"
              f"기록 키: {ch.key + LONGFORM + folder.name}")
        if not a.commit:
            print("미리보기만 — 올리려면 --commit"); return
        vid = upload_longform(ch, folder, when)
        print(f"✅ 롱폼 → {a.at} KST 공개 예약: https://youtube.com/watch?v={vid}"); return
    if a.cmd == "reschedule":
        # 롱폼도 `reschedule longform/<폴더명> <날짜> --hour <시>`로 옮길 수 있게 롱폼 행까지 본다
        row = next((x for x in ch.rows(include_longform=True) if x["topic"] == ch.key + a.topic), None)
        if not row or not row.get("video_id"):
            raise SystemExit(f"❌ {a.topic}: 올라간 기록이 없음")
        when = dt.datetime.combine(dt.date.fromisoformat(a.date), dt.time(a.hour if a.hour is not None else PUBLISH_HOUR), KST) \
            .astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        yt, _ = ch.service()
        yt.videos().update(part="status", body={"id": row["video_id"], "status": {
            "privacyStatus": "private", "publishAt": when, "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}).execute()
        yu._sb_finalize_upload(ch.key + a.topic, row["video_id"], "public", when)
        print(f"✅ {a.topic} → {_kst(when)} 공개 예약"); return

    if a.cmd == "replace":
        # WHY(2026-10-01 사용자 "썸네일 RSV하면 그게 뭔지모르잖아"): 예약해 둔 뒤 썸네일·영상을 고치면 유튜브엔
        # 옛 파일이 그대로 나간다. 영상 파일은 API로 바꿀 수 없어서 지우고 같은 시각으로 다시 올린다.
        # 🚨 이미 공개된 영상은 조회수·댓글이 사라지므로 손대지 않는다 — 공개 시각이 아직 미래인 것만.
        import requests
        row = next((x for x in ch.rows() if x["topic"] == ch.key + a.topic), None)
        if not row or not row.get("video_id") or not row.get("publish_at"):
            raise SystemExit(f"❌ {a.topic}: 예약된 기록이 없음")
        when = row["publish_at"]
        if dt.datetime.fromisoformat(when.replace("Z", "+00:00")) <= dt.datetime.now(dt.timezone.utc):
            raise SystemExit(f"❌ {a.topic}: 이미 공개된 영상이라 갈아 끼우지 않음({_kst(when)})")
        yt, name = ch.service()
        # 🚨 새 영상을 먼저 올리고, 성공한 뒤에만 옛 영상·기록을 지운다. WHY(2026-10-07 피부_28·29): 지우고 올리다가
        # 업로드 한도(uploadLimitExceeded)에 걸려 예약 영상이 통째로 사라졌다 — 유튜브 영상 삭제는 되돌릴 수 없다.
        vid = _insert(ch, yt, name, a.topic, "public", when)
        yt.videos().delete(id=row["video_id"]).execute()
        requests.delete(f"{yu.SUPABASE_URL}/rest/v1/youtube_uploaded", headers=yu._SB_HEADERS,
                        params={"topic": f"eq.{ch.key + a.topic}"}, timeout=30).raise_for_status()
        if not yu._sb_reserve_upload(ch.key + a.topic, "ko"):
            raise SystemExit(f"⚠️ {a.topic}: 새 영상 {vid}는 올라갔는데 기록을 못 남겼다 — youtube_uploaded를 직접 확인할 것")
        yu._sb_finalize_upload(ch.key + a.topic, vid, "public", when)
        print(f"✅ {a.topic} 교체 → {_kst(when)} 예약: https://youtube.com/shorts/{vid} (옛 {row['video_id']} 삭제)"); return

    rows = ready_topics(ch)
    ok = sorted([t for t, why in rows if not why], key=_priority)
    if a.cmd == "plan" or not a.commit:
        for t, why in rows:
            print(("✅ " if not why else "⛔ ") + t + ("" if not why else "  — " + " / ".join(why)))
        n = len(ok) if a.cmd == "plan" else min(a.count, len(ok))
        print(f"\n{ch.code} 채널 {'·'.join(map(str, PUBLISH_HOURS))}시 빈 슬롯 예약안:")
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
