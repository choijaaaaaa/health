# 유튜브 쇼츠 자동 업로드. WHY: data/<topic>/platform_captions.json의 "유튜브 쇼츠"
# 항목은 "제목: ...\n\n설명란:\n..." 형식의 캡션 하나로 저장돼 있는데(대시보드에서
# 사람이 복사해서 붙여넣는 용도로 만든 형식) — 이 파서로 제목/설명을 분리해서 그대로
# YouTube Data API v3 videos.insert에 넘긴다. 카테고리는 건강 정보 콘텐츠에 맞는
# "26"(Howto & Style)을 기본값으로 쓴다.
from __future__ import annotations

import json
import os
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
