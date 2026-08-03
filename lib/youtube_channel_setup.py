# 글로벌 채널(언어별) 초기 세팅 — 채널 설명·키워드·국가/기본 언어를 API로 일괄 반영.
# WHY: 브랜드 계정으로 채널만 만들어두면 설명·키워드가 전부 빈 값이라(실제 확인함 —
# worthitshopping-en/ja 둘 다 description="", keywords 없음) 검색 노출·첫 방문자
#전환에 불리하다. `channels().update()`(part=brandingSettings)로 채널당 반복
# 수동 작업 없이 한 번에 반영한다.
#
# ⚠️ 배너 이미지·외부 링크는 여기서 안 다룬다 — 배너는 이미지 파일 업로드가
# 필요한 별도 디자인 작업이고, 외부 링크(Studio의 "링크" 섹션)는 YouTube가
# 몇 년 전부터 이 기능을 brandingSettings API에서 빼서 공개 API로 설정하는
# 방법이 없다(Studio에서 직접 추가해야 함).
from __future__ import annotations

import os
import sys

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

load_dotenv()

# WHY 언어별로 완전히 새로 쓰는지(번역 아님): CLAUDE.md "글로벌 확장 준비" 절의
# "번역 금지, 언어권마다 독립적으로" 원칙과 같은 이유 — 어투·이모지 사용 습관이
# 언어권마다 다르다(한국어 원문을 그대로 옮기면 어색함).
CHANNEL_META = {
    "en": {
        "description": (
            "🛍️ Health info worth knowing\n"
            "✨ Real research on foods to avoid — and foods that actually help\n"
            "🔥 Only the tips that matter, no fluff\n"
        ),
        "keywords": "health tips nutrition facts food and health wellness healthy eating diet tips health information",
        "country": "US",
        "default_language": "en",
    },
    "ja": {
        "description": (
            "🛍️ 知っておくと得する健康情報\n"
            "✨ 体に良い食べ物・避けたい食べ物を実際の研究をもとに紹介\n"
            "🔥 本当に役立つ情報だけをお届けします\n"
        ),
        "keywords": "健康情報 栄養 食事 健康知識 ダイエット 食品 健康",
        "country": "JP",
        "default_language": "ja",
    },
}


def _get_credentials(channel: str) -> Credentials:
    prefix = f"YOUTUBE_{channel.upper()}_"
    creds = Credentials(
        token=None,
        refresh_token=os.environ[f"{prefix}REFRESH_TOKEN"],
        client_id=os.environ[f"{prefix}CLIENT_ID"],
        client_secret=os.environ[f"{prefix}CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube"],
    )
    creds.refresh(Request())
    return creds


def setup_channel(channel: str) -> None:
    meta = CHANNEL_META[channel]
    youtube = build("youtube", "v3", credentials=_get_credentials(channel))

    current = youtube.channels().list(part="brandingSettings", mine=True).execute()
    branding = current["items"][0]["brandingSettings"]
    branding["channel"]["description"] = meta["description"]
    branding["channel"]["keywords"] = meta["keywords"]
    branding["channel"]["country"] = meta["country"]
    branding["channel"]["defaultLanguage"] = meta["default_language"]

    youtube.channels().update(
        part="brandingSettings",
        body={"id": current["items"][0]["id"], "brandingSettings": branding},
    ).execute()
    print(f"[youtube_channel_setup] {channel} 채널 세팅 완료")


if __name__ == "__main__":
    channel_arg = sys.argv[1]
    setup_channel(channel_arg)
