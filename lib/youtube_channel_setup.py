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
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
# WHY assets_library/channel_banners/(2026-08-03): 배너 이미지는 디자인 작업이라
# API가 만들 수 없다(위 파일 헤더 WHY 참고) — 사람이 이미지를 여기 넣어두면 그
# 파일을 그대로 업로드해서 채널에 붙인다. "<채널코드>.jpg"가 있으면 그 채널
# 전용 배너를 쓰고, 없으면 "default.jpg"로 폴백한다 — 지금 있는 health.jpeg처럼
# 텍스트 없는 범용 이미지는 언어 구분 없이 모든 채널에 그대로 재사용 가능하므로
# (CLAUDE.md "언어마다 독립적으로 리서치" 원칙은 글로 쓰는 콘텐츠 얘기고, 텍스트
# 없는 배경 사진엔 적용되지 않음) 채널마다 매번 새로 만들 필요 없다. 나중에 특정
# 채널만 다른 배너를 쓰고 싶으면 그 채널 코드로 파일만 추가하면 된다.
BANNER_DIR = ROOT / "assets_library" / "channel_banners"
BANNER_EXTENSIONS = ("jpg", "jpeg", "png")

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


def _resolve_banner_path(channel: str) -> Path | None:
    """<채널코드>.{jpg,jpeg,png}가 있으면 그걸, 없으면 default.{jpg,jpeg,png}를
    찾는다. 둘 다 없으면 None(배너 설정을 건너뜀)."""
    for name in (channel, "default"):
        for ext in BANNER_EXTENSIONS:
            path = BANNER_DIR / f"{name}.{ext}"
            if path.exists():
                return path
    return None


def setup_channel(channel: str) -> None:
    meta = CHANNEL_META[channel]
    youtube = build("youtube", "v3", credentials=_get_credentials(channel))

    current = youtube.channels().list(part="brandingSettings", mine=True).execute()
    branding = current["items"][0]["brandingSettings"]
    branding["channel"]["description"] = meta["description"]
    branding["channel"]["keywords"] = meta["keywords"]
    branding["channel"]["country"] = meta["country"]
    branding["channel"]["defaultLanguage"] = meta["default_language"]

    banner_path = _resolve_banner_path(channel)
    if banner_path is not None:
        banner_response = youtube.channelBanners().insert(
            media_body=MediaFileUpload(str(banner_path), mimetype="image/jpeg" if banner_path.suffix != ".png" else "image/png"),
        ).execute()
        branding.setdefault("image", {})["bannerExternalUrl"] = banner_response["url"]
        print(f"[youtube_channel_setup] 배너 이미지 적용: {banner_path.name}")
    else:
        print(f"[youtube_channel_setup] ⚠️ {channel}: 배너 이미지 없음(assets_library/channel_banners/) — 건너뜀")

    youtube.channels().update(
        part="brandingSettings",
        body={"id": current["items"][0]["id"], "brandingSettings": branding},
    ).execute()
    print(f"[youtube_channel_setup] {channel} 채널 세팅 완료")


if __name__ == "__main__":
    channel_arg = sys.argv[1]
    setup_channel(channel_arg)
