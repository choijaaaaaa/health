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
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from lib.mission_control_log import report_issue

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
# WHY 업로드 추적을 Supabase로(2026-08-15, 중복 업로드 사고 재발 방지):
# 예전엔 output/youtube_uploaded.json(git 추적 플랫 리스트)이 "이미 올렸는지"
# 판단의 유일한 근거였는데, 두 가지로 실제 사고가 났다 — ①이 파일을 git이
# 추적하다 보니 무관한 커밋(대시보드 재생성 버그)이 실수로 67건을 날려버려서
# 그 사이 backlog가 같은 topic을 재업로드(중복 10개+ 발생, vernhaven 채널
# 실측). ②동시 세션 경쟁 — 두 세션이 거의 같은 시각에 --backlog를 돌리면
# 둘 다 "아직 안 올림" 스냅샷을 읽고 동시에 업로드해버릴 수 있음(로컬 파일
# 읽기-쓰기 사이에 락이 없음). Supabase `youtube_uploaded` 테이블은 `topic`이
# PRIMARY KEY라 DB 자체가 유일성을 보장하고, 업로드 "직전"에 이 키로 원자적
# INSERT를 먼저 시도해서(성공해야만 실제 업로드 진행) 경쟁 조건을 근본적으로
# 닫는다 — 상세는 아래 _sb_reserve_upload/_sb_finalize_upload/_sb_release_upload.
# 로컬 output/youtube_uploaded.json은 더 이상 쓰지 않는다(레거시, index.html도
# 이미 Supabase를 직접 읽음 — 2026-08-08 스키마 도입 시점부터).
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
_SB_HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
}


def _sb_fetch_uploaded() -> set[str]:
    """지금 시점 기준 "이미 올라간" topic 집합을 Supabase에서 매번 새로
    조회한다(로컬 캐시 없음 — 동시 세션이 방금 올린 것까지 반영돼야 후보
    선정이 정확함). status='pending'(예약만 되고 아직 확정 안 된 것)도 함께
    후보에서 빼야 다른 세션이 지금 업로드 중인 topic을 또 집지 않는다."""
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/youtube_uploaded",
        headers=_SB_HEADERS,
        params={"select": "topic"},
        timeout=30,
    )
    resp.raise_for_status()
    return {row["topic"] for row in resp.json()}


def _sb_reserve_upload(topic: str, lang: str) -> bool:
    """실제 업로드 API를 부르기 직전에 호출 — topic을 PK로 하는 행을
    status='pending'으로 원자적 INSERT 시도한다. 이미 그 topic이 있으면
    (다른 세션이 먼저 예약했거나 이미 확정됐거나) PostgREST가 충돌을
    조용히 무시하고 빈 배열을 반환하므로, 그걸로 "예약 실패 = 이미 누가
    처리 중/처리 완료"를 판별한다. 여기서 True가 나와야만 실제 YouTube
    업로드로 진행할 것 — 이 체크 없이 업로드하면 경쟁 조건이 다시 열린다."""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/youtube_uploaded?on_conflict=topic",
        headers={**_SB_HEADERS, "Prefer": "resolution=ignore-duplicates,return=representation"},
        json=[{"topic": topic, "lang": lang, "status": "pending"}],
        timeout=30,
    )
    resp.raise_for_status()
    return len(resp.json()) > 0


def _sb_finalize_upload(topic: str, video_id: str, privacy_status: str, publish_at: str | None) -> None:
    """업로드 성공 후 예약 행을 실제 결과로 확정한다."""
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/youtube_uploaded",
        headers=_SB_HEADERS,
        params={"topic": f"eq.{topic}"},
        json={
            "video_id": video_id, "privacy_status": privacy_status,
            "publish_at": publish_at, "status": "confirmed",
        },
        timeout=30,
    )
    resp.raise_for_status()


def _sb_record_existing_upload(topic: str, lang: str, video_id: str) -> None:
    """이미 유튜브에 올라가 있는(이 스크립트가 만든 게 아닌) 영상을 사후에
    기록할 때 쓴다(`lib/youtube_organize_playlists.py` — 수동 테스트 업로드 등
    upload_short()를 안 거친 영상을 채널 스캔으로 찾아 소급 정리하는 경우).
    이런 영상은 이미 존재가 확정된 상태라 예약 단계가 필요 없어 바로
    upsert(merge-duplicates)로 confirmed 처리한다."""
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/youtube_uploaded?on_conflict=topic",
        headers={**_SB_HEADERS, "Prefer": "resolution=merge-duplicates,return=minimal"},
        json=[{"topic": topic, "lang": lang, "video_id": video_id, "status": "confirmed"}],
        timeout=30,
    )
    resp.raise_for_status()


def _sb_release_upload(topic: str) -> None:
    """업로드가 실패하면 예약을 풀어(행 삭제) 나중에(같은 세션 재시도든 다른
    세션이든) 다시 후보로 잡힐 수 있게 한다 — status='pending'인 것만 지워서
    이미 확정된(status='confirmed') 행을 실수로 건드리지 않는다."""
    requests.delete(
        f"{SUPABASE_URL}/rest/v1/youtube_uploaded",
        headers=_SB_HEADERS,
        params={"topic": f"eq.{topic}", "status": "eq.pending"},
        timeout=30,
    ).raise_for_status()
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
YOUTUBE_PLATFORM_NAMES = {
    "ko": "유튜브 쇼츠", "en": "YouTube Shorts", "ja": "YouTube Shorts",
    # WHY es/pt/ru도 "YouTube Shorts"(영어 이름) 그대로인지(2026-08-05 추가):
    # 이 세 언어의 platform_captions.json도 en/ja처럼 캡션 언어와 무관하게
    # 플랫폼 이름 자체는 "YouTube Shorts"로 통일해서 쓰고 있음(실측 확인 —
    # 구내염_1/es, 당뇨_1/pt, 수면_1/ru 전부 동일).
    "es": "YouTube Shorts", "pt": "YouTube Shorts", "ru": "YouTube Shorts",
}
# WHY es/pt/ru는 값이 리스트인지(2026-08-05, 실제 업로드 배치에서 발견된 버그 —
# "예상한 'Description:' 구분자가 캡션에 없음" 에러): 세션마다 영어 마커("Title:"/
# "Description:")를 쓰기도 하고 그 언어 마커("Título:"/"Descripción:",
# "Название:"/"Заголовок:"+"Описание:" 등)를 쓰기도 해서 하나로 고정할 수 없다
# (실측: es 12/20, pt 15/16, ru 16/12/2로 세 갈래 다 섞여 있음 — 콘텐츠 작성 시
# 마커를 통일하라고 강제하는 규칙이 없었던 게 원인으로 보임). _parse_title_description이
# 이 리스트를 순서대로 시도해서 실제 캡션에 있는 마커를 찾는다.
CAPTION_MARKERS = {
    "ko": [("제목:", "설명란:\n")],
    "en": [("Title:", "Description:\n")],
    "ja": [
        ("タイトル:", "説明:\n"),
        ("タイトル:", "概要欄:\n"),
        ("Title:", "Description:\n"),
    ],
    "es": [("Title:", "Description:\n"), ("Título:", "Descripción:\n")],
    "pt": [("Title:", "Description:\n"), ("Título:", "Descrição:\n")],
    "ru": [
        ("Title:", "Description:\n"),
        ("Название:", "Описание:\n"),
        ("Заголовок:", "Описание:\n"),
    ],
}
# WHY 재생목록 제목 접두사도 언어별로(2026-08-03): "건강정보 - "로 채널 안 재생목록을
# 한눈에 묶어보게 한 기존 설계(_playlist_title_for_category 참고)를 en/ja 채널에도
# 그대로 적용하되 그 언어로. ja의 "健康情報"는 실제 ja 카드뉴스 eyebrow 필드와 동일한
# 표현을 그대로 재사용(가슴쓰림_1/ja/card_news_spec.json 확인).
PLAYLIST_TITLE_PREFIX = {
    "ko": "건강정보", "en": "Health Info", "ja": "健康情報",
    "es": "Información de Salud", "pt": "Informações de Saúde", "ru": "Информация о здоровье",
}
PLAYLIST_DESCRIPTION = {
    "ko": lambda c: f"{c} 관련 건강 정보 모음",
    "en": lambda c: f"Health info about {c}",
    "ja": lambda c: f"{c}に関する健康情報まとめ",
    "es": lambda c: f"Información de salud sobre {c}",
    "pt": lambda c: f"Informações de saúde sobre {c}",
    "ru": lambda c: f"Информация о здоровье: {c}",
}

# WHY 언어별 타겟 시장 현지 시간대(2026-08-03, "각 나라별 오후 6시 전후... 아침저녁"
# 확정 — data/global_research_rules.md의 "1차 타겟 국가" 기준): 시청자가 실제로
# 스크롤하는 로컬 시간에 맞춰야 의미가 있어서 UTC/KST 일괄이 아니라 언어마다
# 다르게 잡는다. 미국처럼 여러 시간대에 걸친 나라는 인구 밀집 동부 기준
# (America/New_York), 아랍어(MENA/걸프 공통)는 대표로 UAE 기준 — 특정 국가로
# 좁혀지면 그때 조정할 것.
LANGUAGE_TIMEZONES: dict[str, ZoneInfo] = {
    "ko": KST,
    "en": ZoneInfo("America/New_York"),
    "ja": ZoneInfo("Asia/Tokyo"),
    "zh-TW": ZoneInfo("Asia/Taipei"),
    "es": ZoneInfo("America/Mexico_City"),
    "pt": ZoneInfo("America/Sao_Paulo"),
    "fr": ZoneInfo("Europe/Paris"),
    "de": ZoneInfo("Europe/Berlin"),
    "ru": ZoneInfo("Europe/Moscow"),
    "vi": ZoneInfo("Asia/Ho_Chi_Minh"),
    "ar": ZoneInfo("Asia/Dubai"),
    "bn": ZoneInfo("Asia/Dhaka"),
    "tr": ZoneInfo("Europe/Istanbul"),
    "th": ZoneInfo("Asia/Bangkok"),
    "id": ZoneInfo("Asia/Jakarta"),
    "hi": ZoneInfo("Asia/Kolkata"),
}
# WHY 채널당 하루 2개, 현지 오전 10시·오후 6시(2026-08-03 최종 확정 — "일 1개가
# 나을거같아 2개가 나을거간아" 고민 끝에 "걍 2개 ㄱㄱ" → "각 국가별 그 나라 시간의
# 오전 10시, 오후 6시"로 시각까지 못박음): 계정 캐스케이드 리스크 발견 이후에도
# 사용자가 최종적으로 2개/일을 선택함 — 채널 하나 기준 속도로는 여러 소스가
# "3개/일 이상"을 위험 신호로 언급한 것보다 충분히 낮은 페이스.
CHANNEL_DAILY_HOURS = (10, 18)


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
    CAPTION_MARKERS 참고 — 언어마다 구분자 후보가 여러 개일 수 있음, 순서대로
    시도해서 실제 캡션에 있는 걸 찾는다). 이 형식은 lib/dashboard.py가 사람이
    복사-붙여넣기 하도록 만든 캡션 그대로라, 새 포맷으로 바뀌면 이 파서도
    같이 고쳐야 한다."""
    candidates = CAPTION_MARKERS.get(lang, CAPTION_MARKERS["ko"])
    for title_prefix, desc_marker in candidates:
        if desc_marker in caption:
            title_part, description = caption.split(desc_marker, 1)
            title = title_part.replace(title_prefix, "", 1).strip()
            return title, description.strip()
    tried = ", ".join(repr(m.strip()) for _, m in candidates)
    raise ValueError(f"예상한 구분자({tried}) 중 캡션에 있는 게 없음: {caption[:80]!r}...")


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


def _remove_from_playlist(youtube, playlist_id: str, video_id: str) -> bool:
    """topic 카테고리 재편(2026-08-11, 구강/피부 등 세분화된 topic들을 상위
    카테고리로 통합)으로 옛 카테고리 재생목록에 남은 영상을 정리할 때 쓴다.
    playlistItems는 video_id가 아니라 playlistItem 고유 id로 삭제해야 해서,
    먼저 list로 그 id를 찾아야 한다. 못 찾으면(이미 없음) False만 반환하고
    조용히 넘어간다 — _add_to_category_playlist와 마찬가지로 호출부가 이미
    완료된 작업(리네임) 자체를 막지 않게 예외를 삼킨다."""
    request = youtube.playlistItems().list(part="id,snippet", playlistId=playlist_id, maxResults=50)
    item_id = None
    while request is not None and item_id is None:
        response = request.execute()
        for item in response.get("items", []):
            if item["snippet"]["resourceId"]["videoId"] == video_id:
                item_id = item["id"]
                break
        request = youtube.playlistItems().list_next(request, response)
    if item_id is None:
        return False
    try:
        youtube.playlistItems().delete(id=item_id).execute()
        return True
    except HttpError as e:
        print(f"[youtube_upload] ⚠️ 재생목록에서 제거 실패: {e}")
        return False


def _add_to_category_playlist(youtube, topic: str, video_id: str, lang: str = "ko") -> None:
    """실패해도 업로드 자체는 이미 성공한 뒤라 예외를 삼키고 경고만 남긴다.

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


def _is_already_uploaded(topic: str, uploaded: set[str]) -> bool:
    """topic이 uploaded 집합에 있는지 확인 — 정확히 같은 문자열뿐 아니라, 그
    topic의 "구 플랫 이름"(언어 접미사 없는 버전)도 같이 확인한다.

    WHY(2026-08-03 버그 수정, 실제 사고로 발견): <주제>/<lang> 중첩 구조 도입
    전에 올라간 topic들은 youtube_uploaded.json에 "갑상선_1"(접미사 없음)로
    기록돼 있는데, topics.json은 이제 "갑상선_1/ko"로만 topic을 나열한다 —
    문자열 그대로만 비교하면 이미 올라간 topic이 "아직 안 올라감"으로 보여서
    똑같은 영상이 새 이름으로 재업로드되는 사고가 실제로 났다(15개 topic이
    한국어 채널에 중복 업로드됨, 2026-08-03). "갑상선_1/ko"의 "/ko" 접미사를
    떼서 "갑상선_1"도 uploaded에 있는지 같이 확인하면 이 클래스의 버그가
    재발하지 않는다 — 언어가 "ko"(가장 오래된 관례)일 때만 해당, en/ja 등은
    애초에 접미사 없는 옛 이름으로 기록된 적이 없어서 확인할 필요 없음."""
    if topic in uploaded:
        return True
    if "/" in topic:
        base, lang = topic.rsplit("/", 1)
        if lang == "ko" and base in uploaded:
            return True
    return False


def _has_video(topic: str) -> bool:
    """WHY(2026-08-07, 실제 사고로 발견): topics.json은 콘텐츠만 완성돼도(영상
    조립 전, light-card 폴백 대시보드만 있어도) topic을 등록한다 — daily 선택
    함수가 이걸 그대로 후보로 쓰면 영상 없는 topic이 뽑혀서 upload_short()가
    FileNotFoundError를 던지고, upload_daily_per_channel()의 언어별 통짜
    try/except 때문에 그 뒤로 예정돼있던 같은 언어의 나머지 topic까지 전부
    스킵돼버린다(실측: ko 배치에서 비염_1/질염_1이 영상 없이 뽑혀서 발견)."""
    video_dir = ROOT / "output" / topic
    if not video_dir.exists():
        return False
    return any(m for m in video_dir.glob("*shorts.mp4") if "instagram" not in m.name)


def select_daily_topics(n: int = len(DAILY_UPLOAD_HOURS)) -> list[str]:
    """유튜브에 아직 안 올라간 topic 중 n개를 고른다. WHY 선택 순서(2026-08-02,
    "아닌 경우에는 너가 randomly하게 선택해서 올리는"): 다른 플랫폼에 이미
    포스팅된 topic을 우선하고, 부족하면 나머지 중에서 무작위로 채운다 —
    "이미 진행 중인 topic부터 끝내고, 아니면 아무거나 순서 상관없이" 라는
    사용자 의도를 그대로 반영."""
    topics_path = ROOT / "output" / "topics.json"
    all_topics = [t["topic"] for t in json.loads(topics_path.read_text(encoding="utf-8"))]
    uploaded = _sb_fetch_uploaded()
    candidates = [t for t in all_topics if not _is_already_uploaded(t, uploaded) and _has_video(t)]

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


def select_daily_topics_for_lang(lang: str, n: int) -> list[str]:
    """select_daily_topics와 같은 로직(다른 플랫폼 이미 게시된 topic 우선, 나머지는
    무작위)이지만 특정 언어(채널) 하나로 한정한다 — 채널마다 각자의 topic 풀에서
    골라야 "언어당 하루 2개"가 성립한다(전체 topic 풀에서 통으로 뽑으면 그날 특정
    채널엔 하나도 안 걸리는 일이 생김)."""
    topics_path = ROOT / "output" / "topics.json"
    all_topics = [t["topic"] for t in json.loads(topics_path.read_text(encoding="utf-8"))]
    lang_topics = [t for t in all_topics if _lang_from_topic(t) == lang]
    uploaded = _sb_fetch_uploaded()
    candidates = [t for t in lang_topics if not _is_already_uploaded(t, uploaded) and _has_video(t)]

    posted_elsewhere = _topics_posted_elsewhere()
    priority = [t for t in candidates if t in posted_elsewhere]
    rest = [t for t in candidates if t not in posted_elsewhere]
    random.shuffle(rest)

    selected = priority[:n]
    if len(selected) < n:
        selected += rest[: n - len(selected)]
    return selected


def _next_channel_schedule(lang: str, hours: tuple[int, ...] = CHANNEL_DAILY_HOURS,
                            now: datetime | None = None) -> list[str]:
    """_next_daily_schedule과 같은 패턴(첫 슬롯 지났으면 그날 배치 통째로 다음날로)
    이지만, 시간대가 KST 고정이 아니라 LANGUAGE_TIMEZONES에서 그 언어의 타겟 시장
    현지 시간대를 가져와 쓴다."""
    tz = LANGUAGE_TIMEZONES.get(lang, KST)
    now = now or datetime.now(tz)
    base_date = now.date()
    if now.hour >= hours[0]:
        base_date += timedelta(days=1)
    utc = ZoneInfo("UTC")
    return [
        datetime(base_date.year, base_date.month, base_date.day, h, 0, tzinfo=tz)
        .astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for h in hours
    ]


def upload_daily_per_channel(langs: list[str] | None = None, privacy_status: str = "private") -> dict[str, list[dict]]:
    """`python3 lib/youtube_upload.py --daily-per-channel` 진입점(2026-08-03, "각
    국가별 그 나라 시간의 오전 10시, 오후 6시"로 채널당 하루 2개 확정). 채널
    (언어)마다 독립적으로 topic을 골라 그 나라 현지 시간 10시/18시에 예약 게시한다.

    WHY langs 언어별로 통째로 try/except(2026-08-03): 아직 자격증명이 발급 안 된
    언어(신규 계정 발급 전)나 topic이 아직 없는 언어가 섞여 있어도, 그 언어 하나
    실패했다고 나머지 이미 준비된 채널(ko/en 등)까지 전체가 멈추면 안 된다 —
    언어별로 독립적으로 시도하고 실패는 개별적으로 보고한다."""
    langs = langs or list(YOUTUBE_PLATFORM_NAMES.keys())
    results: dict[str, list[dict]] = {}
    for lang in langs:
        try:
            topics = select_daily_topics_for_lang(lang, len(CHANNEL_DAILY_HOURS))
            if not topics:
                print(f"[youtube_upload] [{lang}] 업로드할 topic 없음 — 건너뜀")
                results[lang] = []
                continue
            schedule = _next_channel_schedule(lang, hours=CHANNEL_DAILY_HOURS[: len(topics)])
            lang_results = []
            for topic, publish_at in zip(topics, schedule):
                print(f"[youtube_upload] [{lang}] {topic} → {publish_at} 예약 게시로 업로드")
                lang_results.append(upload_short(topic, privacy_status=privacy_status, publish_at=publish_at))
            results[lang] = lang_results
        except Exception as e:
            print(f"[youtube_upload] ⚠️ [{lang}] 실패, 다른 채널은 계속 진행: {e}")
            results[lang] = []
    return results


def _is_upload_limit_error(e: Exception) -> bool:
    """YouTube 계정당 하루 실제 업로드 개수 제한(API 쿼터와 다른 별개 제약,
    2026-08-07 실측 발견) 여부 확인. HttpError의 reason이 'uploadLimitExceeded'인
    경우만 True — 이 에러는 그날 그 채널에서 더 이상 업로드가 안 된다는 뜻이라
    호출부가 해당 채널을 즉시 포기하고 다음 채널로 넘어가야 한다(재시도해도
    똑같이 실패함, 다른 SKIP 사유와 달리 topic을 바꿔도 소용없음)."""
    if not isinstance(e, HttpError):
        return False
    content = e.content.decode("utf-8", errors="ignore") if isinstance(e.content, bytes) else str(e.content or "")
    return "uploadLimitExceeded" in content


def _last_scheduled_publish_at(lang: str) -> datetime | None:
    """그 채널(언어)에 이미 예약 게시로 올라가 있는 영상 중 가장 늦은 publishAt을
    찾는다. WHY(2026-08-07): backlog를 이어서 올릴 때 _next_channel_schedule처럼
    "지금부터"로 스케줄을 잡으면 이미 예약된 미래 영상과 같은 시각에 겹친다 —
    채널의 실제 업로드 대기열 맨 뒤에 이어붙이려면 지금 예약된 것 중 가장 늦은
    시각을 먼저 알아야 한다. 예약된 게 하나도 없으면 None(호출부가 "지금"으로
    폴백)."""
    youtube = build("youtube", "v3", credentials=_get_credentials(lang))
    channel = youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads_playlist = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    video_ids: list[str] = []
    page_token = None
    while True:
        resp = youtube.playlistItems().list(
            part="contentDetails", playlistId=uploads_playlist, maxResults=50, pageToken=page_token
        ).execute()
        video_ids += [i["contentDetails"]["videoId"] for i in resp["items"]]
        page_token = resp.get("nextPageToken")
        if not page_token or len(video_ids) > 500:
            break
    utc = ZoneInfo("UTC")
    latest: datetime | None = None
    for i in range(0, len(video_ids), 50):
        batch = video_ids[i:i + 50]
        vresp = youtube.videos().list(part="status", id=",".join(batch)).execute()
        for v in vresp["items"]:
            publish_at = v["status"].get("publishAt")
            if not publish_at:
                continue
            dt = datetime.strptime(publish_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=utc)
            if latest is None or dt > latest:
                latest = dt
    return latest


def _backlog_schedule_for_lang(lang: str, n: int) -> list[str]:
    """현지 오전 10시/오후 6시(CHANNEL_DAILY_HOURS) 슬롯을 여러 날에 걸쳐 n개
    만든다. 채널에 이미 예약된 것 중 가장 늦은 시각이 있으면 그 다음 날부터
    이어서(대기열 뒤에 이어붙임), 없으면 _next_daily_schedule과 같은 규칙
    (오늘 첫 슬롯이 지났으면 내일부터)으로 지금 기준 시작."""
    tz = LANGUAGE_TIMEZONES.get(lang, KST)
    utc = ZoneInfo("UTC")
    last = _last_scheduled_publish_at(lang)
    if last is not None:
        day = last.astimezone(tz).date() + timedelta(days=1)
    else:
        now = datetime.now(tz)
        day = now.date()
        if now.hour >= CHANNEL_DAILY_HOURS[0]:
            day += timedelta(days=1)
    slots: list[str] = []
    while len(slots) < n:
        for h in CHANNEL_DAILY_HOURS:
            dt = datetime(day.year, day.month, day.day, h, 0, tzinfo=tz)
            slots.append(dt.astimezone(utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
            if len(slots) >= n:
                break
        day += timedelta(days=1)
    return slots


def upload_backlog(langs: list[str] | None = None, privacy_status: str = "private") -> dict[str, dict]:
    """`python3 lib/youtube_upload.py --backlog` 진입점(2026-08-07, "그냥 유튜브에
    올려줘 하면 이 방식대로 돌아가게 해" 확정 — CLAUDE.md "유튜브 쇼츠 자동
    업로드" 절 참고). 채널(언어)마다 아직 안 올라간 topic 전체를 한 번에
    큐잉해서, 그날 그 채널의 실제 uploadLimitExceeded 한도에 부딪힐 때까지
    밀어붙인다 — 채널마다 숫자를 미리 정해두지 않고 "덜 올라간 채널일수록
    더 많이 올라가는" 효과를 자연히 얻는다. 한도에 걸리면 그 채널만 즉시
    포기하고 다음 채널로 넘어가고(재시도해도 실패하므로), 그 외 개별 오류
    (네트워크 일시 오류 등)는 해당 topic만 건너뛰고 계속 진행한다."""
    langs = langs or list(YOUTUBE_PLATFORM_NAMES.keys())
    results: dict[str, dict] = {}
    for lang in langs:
        topics = select_daily_topics_for_lang(lang, 9999)
        if not topics:
            print(f"[youtube_upload] [{lang}] 업로드할 topic 없음 — 건너뜀")
            results[lang] = {"uploaded": [], "limit_hit": False}
            continue
        schedule = _backlog_schedule_for_lang(lang, len(topics))
        uploaded: list[dict] = []
        limit_hit = False
        for topic, publish_at in zip(topics, schedule):
            try:
                r = upload_short(topic, privacy_status=privacy_status, publish_at=publish_at)
                uploaded.append(r)
                print(f"[youtube_upload] [{lang}] {topic} → {publish_at} 업로드 완료")
            except Exception as e:
                # mission-control에도 보고 — 미설정 세션이 대부분이라 실패해도
                # 조용히 넘어간다(lib/mission_control_log.py 상단 WHY 참고).
                report_issue(
                    severity="error", category="upload_failure",
                    entity=topic, message=str(e),
                )
                if _is_upload_limit_error(e):
                    print(f"[youtube_upload] [{lang}] 하루 업로드 한도 도달 — {topic}부터 다음날로 미룸")
                    limit_hit = True
                    break
                print(f"[youtube_upload] ⚠️ [{lang}] {topic} 건너뜀: {e}")
        results[lang] = {"uploaded": uploaded, "limit_hit": limit_hit}
        print(f"[youtube_upload] --- {lang} 완료: {len(uploaded)}건 업로드"
              f"{'(한도 도달로 중단)' if limit_hit else ''} ---")
    return results


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
    unlisted로 두면 API가 아예 거부한다.

    ⚠️ Supabase 원자적 예약(2026-08-15) — 실제 YouTube 업로드를 시작하기 전에
    `_sb_reserve_upload()`로 이 topic을 먼저 "선점"한다. 이미 다른 세션이
    먼저 예약(또는 확정)해뒀으면 여기서 바로 RuntimeError로 끝나고 API 호출
    자체를 안 한다 — 중복 업로드가 물리적으로 불가능해지는 지점. 이후 어떤
    단계에서든 실패하면(캡션 없음, 영상 파일 없음, YouTube API 에러 등)
    반드시 예약을 풀어야(`_sb_release_upload`) 나중에 재시도할 수 있다."""
    lang = _lang_from_topic(topic)
    if not _sb_reserve_upload(topic, lang):
        raise RuntimeError(f"{topic}: 이미 예약/업로드된 topic — 중복 방지로 건너뜀")
    try:
        return _upload_short_inner(topic, lang, video_path, privacy_status, category_id, publish_at)
    except Exception:
        _sb_release_upload(topic)
        raise


def _upload_short_inner(
    topic: str, lang: str, video_path: str | None, privacy_status: str,
    category_id: str, publish_at: str | None,
) -> dict:
    """upload_short()의 실제 업로드 로직 — 예약 성공 후에만 호출된다(위 WHY
    참고). 실패 시 upload_short()가 예약을 풀어주므로 이 함수 안에서는
    별도 예외 처리 없이 그냥 실패해도 된다."""
    captions_path = ROOT / "data" / topic / "platform_captions.json"
    spec = json.loads(captions_path.read_text(encoding="utf-8"))
    platform_name = YOUTUBE_PLATFORM_NAMES.get(lang, YOUTUBE_PLATFORM_NAMES["ko"])
    platform = next((p for p in spec["platforms"] if p["name"] == platform_name), None)
    if platform is None:
        raise ValueError(f"{topic}: platform_captions.json에 '{platform_name}' 항목이 없음")

    title, description = _parse_title_description(platform["caption"], lang)
    # WHY(2026-08-07): YouTube 제목 100자 제한 초과 시 API가 "invalidTitle"로
    # 거부하는데 에러 메시지가 "제목이 비어있음"처럼 오해하기 쉽게 나옴(목_1/es,
    # 허리_1/es, 혈압_1/pt 실제 발생) — 단어 경계에서 잘라 재발을 막는다.
    if len(title) > 100:
        truncated = title[:100].rsplit(" ", 1)[0].rstrip(" ,.!?¿¡-")
        title = truncated or title[:100]

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
    _add_to_category_playlist(youtube, topic, video_id, lang)
    _sb_finalize_upload(topic, video_id, privacy_status, publish_at)
    if publish_at:
        print(f"[youtube_upload] 업로드 완료(예약 게시 {publish_at}): https://youtube.com/shorts/{video_id}")
    else:
        print(f"[youtube_upload] 업로드 완료: https://youtube.com/shorts/{video_id} (privacy={privacy_status})")
    return response


if __name__ == "__main__":
    if sys.argv[1:2] == ["--daily-batch"]:
        privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
        upload_daily_batch(privacy_status=privacy_arg)
    elif sys.argv[1:2] == ["--daily-per-channel"]:
        privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
        upload_daily_per_channel(privacy_status=privacy_arg)
    elif sys.argv[1:2] == ["--backlog"]:
        privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
        upload_backlog(privacy_status=privacy_arg)
    else:
        topic_arg = sys.argv[1]
        privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
        publish_at_arg = sys.argv[3] if len(sys.argv) > 3 else None
        upload_short(topic_arg, privacy_status=privacy_arg, publish_at=publish_at_arg)
