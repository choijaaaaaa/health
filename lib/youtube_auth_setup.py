# 유튜브 업로드용 OAuth refresh token 1회 발급 스크립트. WHY: lib/youtube_upload.py의
# SCOPES(youtube 전체 관리)는 Google이 "민감 스코프"로 취급해서 access token이
# 1시간마다 만료되는데, refresh_token을 한 번 받아두면 매번 재로그인 없이 자동
# 갱신해서 쓸 수 있다.
# ⚠️ 앱이 OAuth 동의 화면에서 "테스트" 상태로 남아있으면(구글 앱 인증을 안 받으면)
# Google 정책상 refresh_token이 발급 후 7일 뒤 만료될 수 있다 — 그러면 이 스크립트를
# 다시 실행해서 새 토큰을 받아야 한다. 완전 무인 자동화를 원하면 나중에 OAuth 앱
# 인증(verification)까지 받는 걸 고려할 것.
from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.youtube_upload import SCOPES  # noqa: E402 — WHY: 스코프를 한 곳(youtube_upload.py)에서만 관리해 둘이 어긋나는 걸 방지

load_dotenv()


def main() -> None:
    client_id = os.environ["YOUTUBE_CLIENT_ID"]
    client_secret = os.environ["YOUTUBE_CLIENT_SECRET"]

    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

    print("[youtube_auth] 브라우저가 자동으로 안 열리면 아래 URL을 직접 열어서 로그인하세요.")
    creds = flow.run_local_server(port=0, open_browser=True)

    print("\n[youtube_auth] 발급 완료 — 아래 값을 .env의 YOUTUBE_REFRESH_TOKEN에 넣으세요:\n")
    print(creds.refresh_token)


if __name__ == "__main__":
    main()
