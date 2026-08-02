# 유튜브 쇼츠 자동 업로드. WHY: data/<topic>/platform_captions.json의 "유튜브 쇼츠"
# 항목은 "제목: ...\n\n설명란:\n..." 형식의 캡션 하나로 저장돼 있는데(대시보드에서
# 사람이 복사해서 붙여넣는 용도로 만든 형식) — 이 파서로 제목/설명을 분리해서 그대로
# YouTube Data API v3 videos.insert에 넘긴다. 카테고리는 건강 정보 콘텐츠에 맞는
# "26"(Howto & Style)을 기본값으로 쓴다.
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
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


def upload_short(
    topic: str,
    video_path: str | None = None,
    privacy_status: str = "private",
    category_id: str = HOWTO_AND_STYLE_CATEGORY,
) -> dict:
    """privacy_status는 기본 "private" — 처음 몇 번은 비공개로 올려서 결과 확인 후
    "public"으로 바꿔 부를 것을 권장(공개 업로드는 되돌리기 어려운 작업이라 기본값을
    안전한 쪽으로 잡는다)."""
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
            "status": {"privacyStatus": privacy_status, "selfDeclaredMadeForKids": False},
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4"),
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"[youtube_upload] 업로드 중... {int(status.progress() * 100)}%")

    video_id = response["id"]
    print(f"[youtube_upload] 업로드 완료: https://youtube.com/shorts/{video_id} (privacy={privacy_status})")
    return response


if __name__ == "__main__":
    topic_arg = sys.argv[1]
    privacy_arg = sys.argv[2] if len(sys.argv) > 2 else "private"
    upload_short(topic_arg, privacy_status=privacy_arg)
