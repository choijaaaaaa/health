# 유튜브 쇼츠 자동 업로드. WHY: data/<topic>/platform_captions.json의 "유튜브 쇼츠"
# 항목은 "제목: ...\n\n설명란:\n..." 형식의 캡션 하나로 저장돼 있는데(대시보드에서
# 사람이 복사해서 붙여넣는 용도로 만든 형식) — 이 파서로 제목/설명을 분리해서 그대로
# YouTube Data API v3 videos.insert에 넘긴다. 카테고리는 건강 정보 콘텐츠에 맞는
# "26"(Howto & Style)을 기본값으로 쓴다.
from __future__ import annotations

import csv
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
# WHY youtube.upload 대신 전체 관리 스코프(2026-08-02): 재생목록 생성·채널 조회 등을
# 쓰려면 youtube.upload만으로는 부족해서 범위를 넓혔다 — OAuth 동의 화면에도 이
# 스코프를 미리 등록해둬야 한다(Google Cloud Console > 데이터 액세스).
SCOPES = ["https://www.googleapis.com/auth/youtube"]
HOWTO_AND_STYLE_CATEGORY = "26"
# WHY 하루 4개, 10/13/16/19시(2026-08-02, 처음엔 "10시, 11시, 14시, 17시"였다가
# "10 13 16 19로 해"로 최종 확정): 사용자가 확정한 하루 업로드 페이스 —
# --daily-batch가 이 시각들(KST)에 맞춰 예약 게시로 올린다.
KST = ZoneInfo("Asia/Seoul")
DAILY_UPLOAD_HOURS = (10, 13, 16, 19)
# WHY 언어별로 따로 두는지(2026-08-03, en/ja 실제 콘텐츠 생기면서): platform_captions.json의
# 플랫폼 이름과 "제목:"/"설명란:" 구분자가 언어마다 다르게 저장돼 있다(en은 "Title:"/
# "Description:", ja는 "タイトル:"/"説明:" — dashboard.py가 사람이 복사-붙여넣기 하도록
# 그 언어 그대로 만든 캡션이라 번역이 아니라 실제 포맷이 다름). 아직 콘텐츠가 없는
# 나머지 13개 언어는 필요해질 때 여기 추가할 것.
YOUTUBE_PLATFORM_NAMES = {"ko": "유튜브 쇼츠", "en": "YouTube Shorts", "ja": "YouTube Shorts"}
CAPTION_MARKERS = {
    "ko": ("제목:", "설명란:\n"),
    "en": ("Title:", "Description:\n"),
    "ja": ("タイトル:", "説明:\n"),
}
# WHY 재생목록 제목 접두사도 언어별로(2026-08-03): "건강정보 - "로 채널 안 재생목록을
# 한눈에 묶어보게 한 기존 설계(_playlist_title_for_category 참고)를 en/ja 채널에도
# 그대로 적용하되 그 언어로. ja의 "健康情報"는 실제 ja 카드뉴스 eyebrow 필드와 동일한
# 표현을 그대로 재사용(가슴쓰림_1/ja/card_news_spec.json 확인).
PLAYLIST_TITLE_PREFIX = {"ko": "건강정보", "en": "Health Info", "ja": "健康情報"}
PLAYLIST_DESCRIPTION = {
    "ko": lambda c: f"{c} 관련 건강 정보 모음",
    "en": lambda c: f"Health info about {c}",
    "ja": lambda c: f"{c}に関する健康情報まとめ",
}


def _env_prefix(channel: str | None) -> str:
    """WHY 이 함수를 여기서 관리하는지(2026-08-03, 다국어 업로드 오케스트레이션):
    원래 lib/youtube_auth_setup.py에만 있었는데, upload 쪽도 채널별 자격증명을
    읽어야 해서 그대로 복사하면 두 파일이 어긋나기 쉽다 — SCOPES를 이 파일에서
    관리하고 youtube_auth_setup.py가 import해 쓰는 기존 패턴과 동일하게, 이제
    _env_prefix도 여기서 관리하고 youtube_auth_setup.py가 import해 쓴다."""
    return f"YOUTUBE_{channel.upper().replace('-', '_')}_" if channel else "YOUTUBE_"


def _lang_from_topic(topic: str) -> str:
    """topic이 "갑상선_1/en"처럼 언어 하위 폴더를 포함하면 그 언어 코드를, 옛날
    단일 언어 topic("갑상선_1")이면 기본 "ko"를 반환한다."""
    return topic.rsplit("/", 1)[1] if "/" in topic else "ko"


def _get_credentials(lang: str = "ko") -> Credentials:
    """언어별로 별도 GCP 프로젝트/OAuth 클라이언트를 쓰므로(쿼터 격리,
    data/global_channels.json 참고) lang마다 다른 env var 접두사로 자격증명을
    읽는다 — ko는 기존 무접두사 변수(YOUTUBE_CLIENT_ID 등)를 그대로 쓴다(하위
    호환)."""
    prefix = _env_prefix(None if lang == "ko" else lang)
    creds = Credentials(
        token=None,
        refresh_token=os.environ[f"{prefix}REFRESH_TOKEN"],
        client_id=os.environ[f"{prefix}CLIENT_ID"],
        client_secret=os.environ[f"{prefix}CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def _parse_title_description(caption: str, lang: str = "ko") -> tuple[str, str]:
    """"제목: X\n\n설명란:\nY" 형식을 (title, description)으로 분리한다(위
    CAPTION_MARKERS 참고 — 언어마다 구분자가 다름). 이 형식은 lib/dashboard.py가
    사람이 복사-붙여넣기 하도록 만든 캡션 그대로라, 새 포맷으로 바뀌면 이 파서도
    같이 고쳐야 한다."""
    title_prefix, desc_marker = CAPTION_MARKERS.get(lang, CAPTION_MARKERS["ko"])
    if desc_marker not in caption:
        raise ValueError(f"예상한 '{desc_marker.strip()}' 구분자가 캡션에 없음: {caption[:80]!r}...")
    title_part, description = caption.split(desc_marker, 1)
    title = title_part.replace(title_prefix, "", 1).strip()
    return title, description.strip()


def _build_status_body(privacy_status: str, publish_at: str | None) -> dict:
    """publishAt이 있으면 YouTube API 제약대로 privacyStatus를 강제로 private으로
    바꾼다(public/unlisted 상태에서 publishAt을 주면 API가 거부함)."""
    body = {"selfDeclaredMadeForKids": False}
    if publish_at:
        body["privacyStatus"] = "private"
        body["publishAt"] = publish_at
    else:
        body["privacyStatus"] = privacy_status
    return body


def _extract_first_frame(video_path: str) -> Path:
    """영상 첫 프레임을 임시 jpg로 뽑는다. WHY: 유튜브가 자동으로 제안하는 썸네일
    후보는 영상 중간 지점 위주라, 이 파이프라인의 타이틀 카드(영상 맨 앞, 훅 문구가
    큼직하게 박힌 프레임)를 썸네일로 쓰려면 명시적으로 0초 프레임을 추출해서 올려야
    한다."""
    tmp_path = Path(tempfile.mkstemp(suffix=".jpg")[1])
    subprocess.run(
        ["ffmpeg", "-y", "-ss", "0", "-i", video_path, "-frames:v", "1", str(tmp_path)],
        check=True, capture_output=True,
    )
    return tmp_path


def _set_thumbnail(youtube, video_id: str, video_path: str) -> None:
    """실패해도 영상 업로드 자체는 이미 성공한 뒤라 예외를 삼키고 경고만 남긴다.

    ⚠️ WHY 실패 원인을 코드에 단정적으로 안 적어두는지(2026-08-02): 테스트 중
    404 "videoNotFound"를 봤는데, 원인은 채널 미인증도 쇼츠 제약도 아니고 단순히
    그 영상을 테스트 후 지워서였다(`videos.list`로 확인 — 실제로 존재하지 않는
    영상이었음). 즉 이 에러의 진짜 흔한 원인은 잘못된 videoId(삭제됐거나 오타)다 —
    채널 인증(`channels().list().status.longUploadsStatus == "allowed"`로 확인
    가능)이나 쇼츠 제약 쪽으로 성급하게 결론 내리지 말고, 먼저 videoId가 실제로
    존재하는 영상인지부터 의심할 것."""
    thumb_path = _extract_first_frame(video_path)
    try:
        youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(str(thumb_path), mimetype="image/jpeg"),
        ).execute()
        print("[youtube_upload] 썸네일을 영상 첫 프레임으로 설정 완료")
    except HttpError as e:
        print(
            f"[youtube_upload] ⚠️ 썸네일 설정 실패(영상 업로드 자체는 성공함): {e}\n"
            "  videoId가 실제로 존재하는지(삭제되지 않았는지) 먼저 확인하세요."
        )
    finally:
        thumb_path.unlink(missing_ok=True)


def _category_from_topic(topic: str) -> str:
    """topic 폴더명("카테고리_N", 2026-08-02 신규 명명 규칙)에서 카테고리만 뽑는다.
    예: "눈_1" -> "눈", "다리쥐_3" -> "다리쥐". 접미사 번호가 없는 옛날 topic명
    ("가슴쓰림유발음식_1"처럼 원래도 "_숫자"로 끝남)도 마지막 "_숫자"만 떼어내는
    방식이라 그대로 호환된다. WHY 맨 앞에서 "/"로 먼저 자르는지(2026-08-03): topic이
    "갑상선_1/en"처럼 언어 하위 폴더를 포함하면 "_\\d+$"가 매치하지 않아 카테고리가
    "갑상선_1/en"째로 남는 버그가 있었다 — 언어 접미사부터 떼어내고 번호를 뗀다."""
    return re.sub(r"_\d+$", "", topic.split("/", 1)[0])


def _category_label(topic: str, lang: str) -> str | None:
    """재생목록 제목에 쓸 카테고리 라벨(2026-08-03, 다국어 업로드). ko는 지금처럼
    topic 폴더명에서 뽑은 한국어 카테고리 단어를 그대로 쓴다. 그 외 언어는 이
    스크립트가 직접 번역하지 않고 data/<topic>/card_news_spec.json의 topic_word(영어
    카드뉴스 챌크두들 폰트 배치용으로 이미 있는 짧은 카테고리 라벨, 예:
    "갑상선_1/en" -> "Thyroid")를 재사용한다 — 같은 topic도 언어권마다 원인·해결책을
    독립적으로 리서치하므로(CLAUDE.md "원칙 — 언어마다 독립적으로 리서치" 참고) 이
    스크립트가 카테고리 단어를 임의로 번역하면 실제 그 언어 콘텐츠와 안 맞을 위험이
    있다. topic_word가 아직 없는 topic(예: 일부 ja topic)은 None을 반환 — 호출부가
    재생목록 추가를 건너뛰고 경고만 남긴다."""
    if lang == "ko":
        return _category_from_topic(topic)
    spec_path = ROOT / "data" / topic / "card_news_spec.json"
    if not spec_path.exists():
        return None
    return json.loads(spec_path.read_text(encoding="utf-8")).get("topic_word")


def _playlist_title_for_category(category: str, lang: str = "ko") -> str:
    """WHY 카테고리 단어 그대로 안 쓰는지(2026-08-02): "눈", "다리쥐"처럼 topic
    폴더명용 짧은 카테고리 단어는 사람이나 유튜브 검색·추천 시스템이 봤을 때
    무슨 주제인지 알아보기 어렵다("이거만 하면 사람들이랑 유튜브 검사 시스템에서
    이게 눈 건강과 관련된거라고 인지 못함" — 사용자 지적) — "건강정보 - 카테고리"
    형식으로 채널의 모든 재생목록이 "건강정보 - "로 시작해 한눈에 묶여 보이게
    한다(처음엔 "카테고리 관련 건강정보"였다가 이 형식으로 확정, 2026-08-02).
    en/ja 채널은 같은 형식을 그 언어 접두사로(PLAYLIST_TITLE_PREFIX, 2026-08-03)."""
    prefix = PLAYLIST_TITLE_PREFIX.get(lang, PLAYLIST_TITLE_PREFIX["ko"])
    return f"{prefix} - {category}"


def _get_or_create_playlist(youtube, category: str, lang: str = "ko") -> str:
    """카테고리에 대응하는 재생목록 제목(`_playlist_title_for_category`)과 정확히
    같은 재생목록이 이미 있으면 그 ID를 재사용하고, 없으면 새로 만든다 — topic마다
    재생목록이 늘어나지 않고 같은 카테고리는 계속 한 재생목록에 쌓이게 하기 위함."""
    title = _playlist_title_for_category(category, lang)
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
        request = youtube.playlists().list_next(request, response)

    description_fn = PLAYLIST_DESCRIPTION.get(lang, PLAYLIST_DESCRIPTION["ko"])
    response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": description_fn(category)},
            "status": {"privacyStatus": "public"},
        },
    ).execute()
    print(f"[youtube_upload] 재생목록 신규 생성: {title}")
    return response["id"]


def _playlist_has_video(youtube, playlist_id: str, video_id: str) -> bool:
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    while request is not None:
        response = request.execute()
        if any(i["snippet"]["resourceId"]["videoId"] == video_id for i in response.get("items", [])):
            return True
        request = youtube.playlistItems().list_next(request, response)
    return False


def _add_to_category_playlist(youtube, topic: str, video_id: str, lang: str = "ko") -> None:
    """실패해도 업로드 자체는 이미 성공한 뒤라 예외를 삼키고 경고만 남긴다(썸네일
    설정과 동일한 정책).

    WHY _playlist_has_video로 먼저 확인하는지(2026-08-02, "버그있었나본데 그래서
    한도 이미 엄청빨리소진된듯? 네개씩 너어놨네"): 원래는 이미 그 영상이
    재생목록에 있는지 확인 없이 매번 무조건 insert했다 — organize()나
    daily-batch를 여러 번 돌리면 같은 영상이 같은 재생목록에 중복으로 쌓이는
    잠재적 버그였다(이번엔 실제 계정을 API로 직접 조회해서 확인한 결과 우연히
    중복은 없었지만, 재발 방지 차원에서 먼저 확인 후 없을 때만 추가하도록
    고침 — 불필요한 insert 호출을 줄여 quota 절약에도 도움됨).

    WHY category가 None이면 건너뛰는지(2026-08-03): en/ja는 _category_label이
    card_news_spec.json의 topic_word를 읽는데, 아직 그 필드가 없는 topic도 있다
    (예: 가슴쓰림_1/ja) — 라벨을 이 스크립트가 임의로 지어내지 않고, 없으면
    재생목록 추가만 건너뛴다(업로드 자체는 그대로 성공)."""
    category = _category_label(topic, lang)
    if category is None:
        print(f"[youtube_upload] ⚠️ {topic}: 재생목록 라벨(topic_word) 없음 — 재생목록 추가 건너뜀")
        return
    try:
        playlist_id = _get_or_create_playlist(youtube, category, lang)
        # WHY 재시도 루프(2026-08-03, 갑상선_1/en 실제 업로드 중 실측): 방금
        # playlists().insert()로 만든 재생목록을 곧바로 playlistItems().list()/
        # insert()로 조회·수정하면 "playlistNotFound"(404)가 난다 — YouTube가
        # 새로 만든 리소스를 다른 엔드포인트에서 바로 조회 가능하게 반영하는 데
        # 약간의 전파 지연이 있음(몇 초 뒤 수동 재시도하니 정상 동작 확인됨).
        # 기존 재생목록(이미 있던 카테고리)이면 이 지연이 없어 첫 시도에 바로 성공.
        for attempt in range(3):
            try:
                if _playlist_has_video(youtube, playlist_id, video_id):
                    print(f"[youtube_upload] 재생목록 '{category}'에 이미 있음 — 건너뜀")
                    return
                youtube.playlistItems().insert(
                    part="snippet",
                    body={
                        "snippet": {
                            "playlistId": playlist_id,
                            "resourceId": {"kind": "youtube#video", "videoId": video_id},
                        }
                    },
                ).execute()
                print(f"[youtube_upload] 재생목록 '{category}'에 추가 완료")
                return
            except HttpError as e:
                if e.resp.status == 404 and attempt < 2:
                    print(f"[youtube_upload] 재생목록 전파 지연으로 보임 — {2 - attempt}회 재시도 대기")
                    time.sleep(2)
                    continue
                raise
    except HttpError as e:
        print(f"[youtube_upload] ⚠️ 재생목록 추가 실패(영상 업로드 자체는 성공함): {e}")


def _mark_youtube_uploaded(topic: str) -> None:
    """WHY(2026-08-02, "완성된 콘텐츠 목록에서 유튜브 숏츠"만" 완료되었는지를 해당
    라인에서 확인할 수 있게"): output/completed_topics.json(콘텐츠 제작 전체 완료)과
    별개로, 유튜브 업로드가 끝난 topic만 index.html에서 따로 표시할 수 있게
    output/youtube_uploaded.json에 기록한다. WHY 예약 게시(publish_at)여도 여기서
    바로 기록하는지: "완전히 업로드가 완료되는게 기준이 아니라 예약 설정해서
    업로드를 완료한 경우에 확인할 수 있게 해주면 된다" — 실제 공개 전환 시각까지
    기다리지 않고, 업로드+썸네일+재생목록 등록까지 끝나면(이 함수가 호출되는
    시점) 완료로 본다."""
    path = ROOT / "output" / "youtube_uploaded.json"
    uploaded = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    if topic not in uploaded:
        uploaded.append(topic)
        uploaded.sort()
        path.write_text(json.dumps(uploaded, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _topics_posted_elsewhere() -> set[str]:
    """output/posting_log.csv(위 "포스팅 기록" 절 — 사용자가 다른 플랫폼에 올린
    기록을 CSV로 내보내서 git에 커밋해두는 파일)에서 유튜브 쇼츠가 아닌 다른
    플랫폼에 이미 포스팅된 topic 집합을 구한다. WHY(2026-08-02, "아직 올리지
    않은 토픽 중에 내가 이미 올려놓은 것들이 있다면 그걸 우선순위로 유튜브
    올리고"): 사용자가 다른 플랫폼에 먼저 올려둔 topic은 유튜브만 마치면 그
    topic 전체가 끝나니 우선 처리한다. 파일이 없으면(아직 CSV를 커밋 안 함)
    빈 집합 — 이 경우 select_daily_topics는 전부 무작위 선택으로 폴백한다."""
    log_path = ROOT / "output" / "posting_log.csv"
    if not log_path.exists():
        return set()
    posted = set()
    with log_path.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("topic") and row.get("platform") != "유튜브 쇼츠":
                posted.add(row["topic"])
    return posted


def select_daily_topics(n: int = len(DAILY_UPLOAD_HOURS)) -> list[str]:
    """유튜브에 아직 안 올라간 topic 중 n개를 고른다. WHY 선택 순서(2026-08-02,
    "아닌 경우에는 너가 randomly하게 선택해서 올리는"): 다른 플랫폼에 이미
    포스팅된 topic을 우선하고, 부족하면 나머지 중에서 무작위로 채운다 —
    "이미 진행 중인 topic부터 끝내고, 아니면 아무거나 순서 상관없이" 라는
    사용자 의도를 그대로 반영."""
    topics_path = ROOT / "output" / "topics.json"
    all_topics = [t["topic"] for t in json.loads(topics_path.read_text(encoding="utf-8"))]
    uploaded_path = ROOT / "output" / "youtube_uploaded.json"
    uploaded = set(json.loads(uploaded_path.read_text(encoding="utf-8"))) if uploaded_path.exists() else set()
    candidates = [t for t in all_topics if t not in uploaded]

    posted_elsewhere = _topics_posted_elsewhere()
    priority = [t for t in candidates if t in posted_elsewhere]
    rest = [t for t in candidates if t not in posted_elsewhere]
    random.shuffle(rest)

    selected = priority[:n]
    if len(selected) < n:
        selected += rest[: n - len(selected)]
    return selected


def _next_daily_schedule(n: int, hours: tuple[int, ...] = DAILY_UPLOAD_HOURS,
                          now: datetime | None = None) -> list[str]:
    """오늘 첫 슬롯(hours[0], 기본 10시 KST)이 아직 안 지났으면 오늘, 이미 지났으면
    내일 기준으로 예약 게시 시각(UTC ISO 8601, publishAt용) 리스트를 만든다. WHY
    통째로 다음날로 미루는지(부분적으로 오늘/내일 안 섞는 이유): 하루 배치(10/11/
    14/17시)가 절반은 오늘 절반은 내일로 흩어지면 "하루 4개" 페이스 개념이
    깨진다 — 첫 슬롯이 지났으면 그날 배치는 통째로 다음날로 넘긴다. now는
    테스트에서 현재 시각을 주입하기 위한 파라미터(안 주면 실제 현재 시각)."""
    now = now or datetime.now(KST)
    base_date = now.date()
    if now.hour >= hours[0]:
        base_date += timedelta(days=1)
    utc = ZoneInfo("UTC")
    return [
        datetime(base_date.year, base_date.month, base_date.day, h, 0, tzinfo=KST)
        .astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for h in hours[:n]
    ]


def upload_daily_batch(privacy_status: str = "private") -> list[dict]:
    """`python3 lib/youtube_upload.py --daily-batch` 진입점(2026-08-02, "유튜브
    업로드는 내가 업로드 하라고 하면 API 찔러서 10시, 11시, 14시, 17시 이렇게
    네 개 토픽에 대해 영상 네 개 넣는거야"). select_daily_topics로 고른 topic들을
    _next_daily_schedule 시각에 맞춰 순서대로 예약 게시 업로드한다."""
    topics = select_daily_topics(len(DAILY_UPLOAD_HOURS))
    if not topics:
        print("[youtube_upload] 업로드할 topic이 없음 — 전부 이미 유튜브에 올라감")
        return []
    schedule = _next_daily_schedule(len(topics))
    results = []
    for topic, publish_at in zip(topics, schedule):
        print(f"[youtube_upload] {topic} → {publish_at} 예약 게시로 업로드")
        results.append(upload_short(topic, privacy_status=privacy_status, publish_at=publish_at))
    return results


def upload_short(
    topic: str,
    video_path: str | None = None,
    privacy_status: str = "private",
    category_id: str = HOWTO_AND_STYLE_CATEGORY,
    publish_at: str | None = None,
) -> dict:
    """privacy_status는 기본 "private" — 처음 몇 번은 비공개로 올려서 결과 확인 후
    "public"으로 바꿔 부를 것을 권장(공개 업로드는 되돌리기 어려운 작업이라 기본값을
    안전한 쪽으로 잡는다).

    publish_at: 예약 게시 시각(ISO 8601 UTC, 예: "2026-08-03T09:00:00Z")을 주면 그
    시각에 유튜브가 자동으로 공개 전환한다. WHY privacy_status를 강제로 "private"로
    덮어쓰는지: YouTube API 자체 제약으로, publishAt이 설정된 영상은 업로드 시점의
    privacyStatus가 반드시 "private"여야 한다(그래야 예약 개념이 성립) — public이나
    unlisted로 두면 API가 아예 거부한다."""
    lang = _lang_from_topic(topic)
    captions_path = ROOT / "data" / topic / "platform_captions.json"
    spec = json.loads(captions_path.read_text(encoding="utf-8"))
    platform_name = YOUTUBE_PLATFORM_NAMES.get(lang, YOUTUBE_PLATFORM_NAMES["ko"])
    platform = next((p for p in spec["platforms"] if p["name"] == platform_name), None)
    if platform is None:
        raise ValueError(f"{topic}: platform_captions.json에 '{platform_name}' 항목이 없음")

    title, description = _parse_title_description(platform["caption"], lang)

    if video_path is None:
        # WHY 정확한 파일명을 조립하지 않고 글롭으로 찾는지(2026-08-03, 언어별
        # 폴더 구조화 이후 발견): topic이 "골다공증_1/ko"처럼 "/"를 포함하면
        # f"{topic}_shorts.mp4"가 "골다공증_1/ko_shorts.mp4"라는 잘못된 경로
        # 문자열이 되어(Path가 "/"를 다시 구분자로 해석) 실제 파일을 못 찾았다
        # (실측 확인: output/골다공증_1/ko/골다공증_1_shorts.mp4가 실제 파일인데
        # output/골다공증_1/ko/골다공증_1/ko_shorts.mp4를 찾으려 함). 게다가
        # 언어별로 실제 파일명 규칙도 다르다(ko는 "<topic>_shorts.mp4", en은
        # 완전히 다른 내부 슬러그를 쓰기도 하고(en_heartburn_1_shorts.mp4) 접두사
        # 없이 그냥 "shorts.mp4"인 topic도 있다(2026-08-03 실측: 골다공증_1/en,
        # 공복_1/en, 고령_1/en, 갑상선_1/en 전부 "shorts.mp4") — 그래서 정확한
        # 이름을 조립하는 대신 그 디렉터리의 유일한 "*shorts.mp4"(밑줄 없이,
        # 접두사가 없는 파일도 매치하도록)를 찾는다.
        video_dir = ROOT / "output" / topic
        candidates = list(video_dir.glob("*shorts.mp4"))
        if not candidates:
            raise FileNotFoundError(f"영상 파일 없음: {video_dir}/*shorts.mp4")
        video_path = str(candidates[0])
    if not Path(video_path).exists():
        raise FileNotFoundError(f"영상 파일 없음: {video_path}")

    tags = [w[1:] for w in description.split() if w.startswith("#")]

    status_body = _build_status_body(privacy_status, publish_at)

    youtube = build("youtube", "v3", credentials=_get_credentials(lang))
    # WHY defaultLanguage/defaultAudioLanguage를 명시로 넘기는지(2026-08-03, "영어로
    # 된거 업로드했는데 미국 알고리즘에 뜨긴 뜨겠지?"): 이 필드가 없으면 유튜브가
    # 제목·설명·오디오를 분석해서 언어를 추정해야 하는데, 새 채널의 첫 영상들처럼
    # 아직 참고할 시청 데이터가 없는 시점엔 이 명시적 신호가 자동 추정보다 훨씬
    # 빠르고 확실하게 언어권 시청자에게 노출시켜준다. `lang` 코드(en/ja/ko 등)는
    # data/global_channels.json의 code와 동일한 ISO 639-1 계열이라 그대로 재사용.
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
                "defaultLanguage": lang,
                "defaultAudioLanguage": lang,
            },
            "status": status_body,
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4"),
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube_upload] 업로드 중... {int(status.progress() * 100)}%")

    video_id = response["id"]
    _set_thumbnail(youtube, video_id, video_path)
    _add_to_category_playlist(youtube, topic, video_id, lang)
    _mark_youtube_uploaded(topic)
    if publish_at:
        print(f"[youtube_upload] 업로드 완료(예약 게시 {publish_at}): https://youtube.com/shorts/{video_id}")
    else:
        print(f"[youtube_upload] 업로드 완료: https://youtube.com/shorts/{video_id} (privacy={privacy_status})")
    return response


if __name__ == "__main__":
    if sys.argv[1:2] == ["--daily-batch"]:
        privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
        upload_daily_batch(privacy_status=privacy_arg)
    else:
        topic_arg = sys.argv[1]
        privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
        publish_at_arg = sys.argv[3] if len(sys.argv) > 3 else None
        upload_short(topic_arg, privacy_status=privacy_arg, publish_at=publish_at_arg)
