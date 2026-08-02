# 유튜브 쇼츠 자동 업로드. WHY: data/<topic>/platform_captions.json의 "유튜브 쇼츠"
# 항목은 "제목: ...\n\n설명란:\n..." 형식의 캡션 하나로 저장돼 있는데(대시보드에서
# 사람이 복사해서 붙여넣는 용도로 만든 형식) — 이 파서로 제목/설명을 분리해서 그대로
# YouTube Data API v3 videos.insert에 넘긴다. 카테고리는 건강 정보 콘텐츠에 맞는
# "26"(Howto & Style)을 기본값으로 쓴다.
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

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


def _get_credentials() -> Credentials:
    creds = Credentials(
        token=None,
        refresh_token=os.environ["YOUTUBE_REFRESH_TOKEN"],
        client_id=os.environ["YOUTUBE_CLIENT_ID"],
        client_secret=os.environ["YOUTUBE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def _parse_title_description(caption: str) -> tuple[str, str]:
    """"제목: X\n\n설명란:\nY" 형식을 (title, description)으로 분리한다.
    이 형식은 lib/dashboard.py가 사람이 복사-붙여넣기 하도록 만든 캡션 그대로라,
    새 포맷으로 바뀌면 이 파서도 같이 고쳐야 한다."""
    if "설명란:\n" not in caption:
        raise ValueError(f"예상한 '설명란:' 구분자가 캡션에 없음: {caption[:80]!r}...")
    title_part, description = caption.split("설명란:\n", 1)
    title = title_part.replace("제목:", "", 1).strip()
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
    방식이라 그대로 호환된다."""
    return re.sub(r"_\d+$", "", topic)


def _playlist_title_for_category(category: str) -> str:
    """WHY 카테고리 단어 그대로 안 쓰는지(2026-08-02): "눈", "다리쥐"처럼 topic
    폴더명용 짧은 카테고리 단어는 사람이나 유튜브 검색·추천 시스템이 봤을 때
    무슨 주제인지 알아보기 어렵다("이거만 하면 사람들이랑 유튜브 검사 시스템에서
    이게 눈 건강과 관련된거라고 인지 못함" — 사용자 지적) — "건강정보 - 카테고리"
    형식으로 채널의 모든 재생목록이 "건강정보 - "로 시작해 한눈에 묶여 보이게
    한다(처음엔 "카테고리 관련 건강정보"였다가 이 형식으로 확정, 2026-08-02)."""
    return f"건강정보 - {category}"


def _get_or_create_playlist(youtube, category: str) -> str:
    """카테고리에 대응하는 재생목록 제목(`_playlist_title_for_category`)과 정확히
    같은 재생목록이 이미 있으면 그 ID를 재사용하고, 없으면 새로 만든다 — topic마다
    재생목록이 늘어나지 않고 같은 카테고리는 계속 한 재생목록에 쌓이게 하기 위함."""
    title = _playlist_title_for_category(category)
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
        request = youtube.playlists().list_next(request, response)

    response = youtube.playlists().insert(
        part="snippet,status",
        body={
            "snippet": {"title": title, "description": f"{category} 관련 건강 정보 모음"},
            "status": {"privacyStatus": "public"},
        },
    ).execute()
    print(f"[youtube_upload] 재생목록 신규 생성: {title}")
    return response["id"]


def _add_to_category_playlist(youtube, topic: str, video_id: str) -> None:
    """실패해도 업로드 자체는 이미 성공한 뒤라 예외를 삼키고 경고만 남긴다(썸네일
    설정과 동일한 정책)."""
    category = _category_from_topic(topic)
    try:
        playlist_id = _get_or_create_playlist(youtube, category)
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
    captions_path = ROOT / "data" / topic / "platform_captions.json"
    spec = json.loads(captions_path.read_text(encoding="utf-8"))
    platform = next((p for p in spec["platforms"] if p["name"] == "유튜브 쇼츠"), None)
    if platform is None:
        raise ValueError(f"{topic}: platform_captions.json에 '유튜브 쇼츠' 항목이 없음")

    title, description = _parse_title_description(platform["caption"])

    if video_path is None:
        video_path = str(ROOT / "output" / topic / f"{topic}_shorts.mp4")
    if not Path(video_path).exists():
        raise FileNotFoundError(f"영상 파일 없음: {video_path}")

    tags = [w[1:] for w in description.split() if w.startswith("#")]

    status_body = _build_status_body(privacy_status, publish_at)

    youtube = build("youtube", "v3", credentials=_get_credentials())
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
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
    _add_to_category_playlist(youtube, topic, video_id)
    _mark_youtube_uploaded(topic)
    if publish_at:
        print(f"[youtube_upload] 업로드 완료(예약 게시 {publish_at}): https://youtube.com/shorts/{video_id}")
    else:
        print(f"[youtube_upload] 업로드 완료: https://youtube.com/shorts/{video_id} (privacy={privacy_status})")
    return response


if __name__ == "__main__":
    topic_arg = sys.argv[1]
    privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
    publish_at_arg = sys.argv[3] if len(sys.argv) > 3 else None
    upload_short(topic_arg, privacy_status=privacy_arg, publish_at=publish_at_arg)
