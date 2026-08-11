# topic 카테고리 재편(2026-08-11, 구강/피부 등 세분화된 topic 43개를 상위
# 카테고리로 통합)으로 이미 업로드된 영상들을 옛 카테고리 재생목록에서 새
# 카테고리 재생목록으로 소급 이동시킨다. 폴더 리네임만으로는 이미 올라간
# 영상의 재생목록이 자동으로 안 바뀌기 때문에 별도로 정리해야 한다.
from __future__ import annotations

import json
from pathlib import Path

from googleapiclient.discovery import build

from lib.youtube_upload import (
    ROOT,
    YOUTUBE_PLATFORM_NAMES,
    _get_credentials,
    _parse_title_description,
    _category_from_topic,
    _playlist_title_for_category,
    _get_or_create_playlist,
    _playlist_has_video,
    _add_to_category_playlist,
    _remove_from_playlist,
)

LANGS = ["ko", "en", "ja", "es", "pt", "ru"]

MAPPING = {
    "구내염_1": "입_2", "잇몸_1": "입_3", "치아_1": "입_4", "이갈이_1": "입_5",
    "다래끼_1": "눈_4",
    "손톱_1": "손_1",
    "이명_1": "귀_1",
    "체취_1": "냄새_1",
    "두피_1": "머리_1", "새치_1": "머리_2", "탈모_1": "머리_3",
    "가슴쓰림_1": "소화_1", "공복_1": "소화_2", "변비_1": "소화_3",
    "식곤증_1": "소화_4", "위_1": "소화_5", "장_1": "소화_6",
    "냉증_1": "순환_1", "부종_1": "순환_2", "정맥류_1": "순환_3",
    "손발저림_1": "순환_4", "혈압_1": "순환_5",
    "다한증_1": "피부_3", "두드러기_1": "피부_4", "무좀_1": "피부_5",
    "관절_1": "근골격_1", "골다공증_1": "근골격_2", "다리쥐_1": "근골격_3",
    "목_1": "근골격_4", "허리_1": "근골격_5",
    "코골이_1": "코_3", "하지불안증후군_1": "수면_2",
    "기억력_1": "뇌_1", "편두통_1": "뇌_2",
    "비염_1": "코_1", "코피_1": "코_2",
    "방광염_1": "비뇨기_1", "콩팥_1": "비뇨기_2", "남성_1": "비뇨기_3", "남성_2": "비뇨기_4",
    "멀미_1": "어지럼증_2", "이석증_1": "어지럼증_3",
    "당뇨_1": "혈당_4",
}


def _channel_uploads(youtube) -> list[dict]:
    channel = youtube.channels().list(part="contentDetails", mine=True).execute()
    uploads_id = channel["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    videos = []
    request = youtube.playlistItems().list(part="snippet", playlistId=uploads_id, maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response["items"]:
            videos.append({
                "video_id": item["snippet"]["resourceId"]["videoId"],
                "title": item["snippet"]["title"],
            })
        request = youtube.playlistItems().list_next(request, response)
    return videos


def _find_playlist_id(youtube, title: str) -> str | None:
    """_get_or_create_playlist와 달리 없으면 만들지 않는다 — 옛 카테고리
    재생목록은 정리 대상이지 새로 만들 이유가 없다(빈 옛 재생목록이 남으면
    그 자체가 이번에 없애려는 clutter)."""
    request = youtube.playlists().list(part="snippet", mine=True, maxResults=50)
    while request is not None:
        response = request.execute()
        for item in response.get("items", []):
            if item["snippet"]["title"] == title:
                return item["id"]
        request = youtube.playlists().list_next(request, response)
    return None


def _new_topic_title(new_topic: str, lang: str) -> str | None:
    captions_path = ROOT / "data" / new_topic / lang / "platform_captions.json"
    if not captions_path.exists():
        return None
    spec = json.loads(captions_path.read_text(encoding="utf-8"))
    platform_name = YOUTUBE_PLATFORM_NAMES.get(lang)
    platform = next((p for p in spec.get("platforms", []) if p["name"] == platform_name), None)
    if platform is None:
        return None
    try:
        title, _ = _parse_title_description(platform["caption"], lang)
    except ValueError:
        return None
    return title


def migrate():
    matched_total, unmatched_total, removed_total = 0, 0, 0
    for lang in LANGS:
        try:
            youtube = build("youtube", "v3", credentials=_get_credentials(lang))
        except Exception as e:
            print(f"[{lang}] 인증 실패, 건너뜀: {e}")
            continue

        uploads = _channel_uploads(youtube)
        title_to_video = {v["title"]: v["video_id"] for v in uploads}
        print(f"\n=== {lang}: 채널 업로드 {len(uploads)}개 ===")

        for old, new in MAPPING.items():
            title = _new_topic_title(new, lang)
            if title is None:
                continue
            video_id = title_to_video.get(title)
            if video_id is None:
                unmatched_total += 1
                continue

            old_category = _category_from_topic(old)
            old_playlist_title = _playlist_title_for_category(old_category, lang)
            old_playlist_id = _find_playlist_id(youtube, old_playlist_title)
            if old_playlist_id and _playlist_has_video(youtube, old_playlist_id, video_id):
                if _remove_from_playlist(youtube, old_playlist_id, video_id):
                    removed_total += 1
                    print(f"  {old} -> {new}: '{old_playlist_title}'에서 제거")

            _add_to_category_playlist(youtube, new, video_id, lang)
            matched_total += 1

    print(f"\n완료: 매칭 {matched_total}건 (옛 재생목록 제거 {removed_total}건), 미매칭 {unmatched_total}건")


if __name__ == "__main__":
    migrate()
