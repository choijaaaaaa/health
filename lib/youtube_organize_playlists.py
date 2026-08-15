# 이미 유튜브에 올라가 있는 영상들을 카테고리 재생목록에 소급 정리한다.
# WHY: youtube_upload.py의 upload_short()는 업로드 시점에 바로 재생목록에 추가하지만,
# 그 경로를 안 거치고(수동 테스트 업로드 등) 이미 올라간 영상은 재생목록에 없다 —
# Supabase youtube_uploaded 테이블도 upload_short() 경로로만 기록되므로 이미
# 올라간 영상의 video_id를 알 방법이 없어서, 채널 업로드 목록을 직접 조회해서
# topic과 매칭한다.
from __future__ import annotations

import json
from pathlib import Path

from googleapiclient.discovery import build

from lib.youtube_upload import (
    _get_credentials,
    _parse_title_description,
    _add_to_category_playlist,
    _lang_from_topic,
    _sb_record_existing_upload,
    ROOT,
)


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


def _topic_titles() -> dict[str, str]:
    """topic -> 유튜브 쇼츠 캡션에서 파싱한 제목."""
    titles = {}
    for d in sorted((ROOT / "data").iterdir()):
        captions_path = d / "platform_captions.json"
        if not captions_path.exists():
            continue
        spec = json.loads(captions_path.read_text(encoding="utf-8"))
        platform = next((p for p in spec.get("platforms", []) if p["name"] == "유튜브 쇼츠"), None)
        if platform is None:
            continue
        try:
            title, _ = _parse_title_description(platform["caption"])
        except ValueError:
            continue
        titles[d.name] = title
    return titles


def organize():
    youtube = build("youtube", "v3", credentials=_get_credentials())
    uploaded_videos = _channel_uploads(youtube)
    topic_titles = _topic_titles()

    matched, unmatched = [], []
    for video in uploaded_videos:
        topic = next((t for t, title in topic_titles.items() if title == video["title"]), None)
        if topic is None:
            unmatched.append(video)
            continue
        matched.append((topic, video))

    print(f"채널 업로드 영상 {len(uploaded_videos)}개, topic 매칭 {len(matched)}개, 미매칭 {len(unmatched)}개")
    for topic, video in matched:
        print(f"  {topic} -> {video['title']} ({video['video_id']})")
        _add_to_category_playlist(youtube, topic, video["video_id"])
        _sb_record_existing_upload(topic, _lang_from_topic(topic), video["video_id"])

    if unmatched:
        print("\n미매칭 영상(topic을 못 찾음 — 제목이 캡션과 다르게 수정됐을 수 있음):")
        for video in unmatched:
            print(f"  {video['title']} ({video['video_id']})")

    return matched, unmatched


if __name__ == "__main__":
    organize()
