# lib/youtube_upload.py의 캡션 파서 테스트. WHY: 실제 유튜브 API는 절대 호출하지
# 않는다(비용은 없지만 실제 채널에 업로드되는 부작용이 있음) — "제목: ...\n\n설명란:\n..."
# 형식을 (title, description)으로 정확히 분리하는지만 검증한다. 이 형식은
# lib/dashboard.py가 만드는 "유튜브 쇼츠" 캡션과 동일해야 한다.
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lib.youtube_upload as youtube_upload  # noqa: E402
from lib.youtube_upload import (  # noqa: E402
    _build_status_body,
    _category_from_topic,
    _extract_first_frame,
    _mark_youtube_uploaded,
    _parse_title_description,
    _playlist_title_for_category,
)


def test_parse_title_description_happy_path():
    caption = (
        "제목: 자다가 다리에 자주 쥐가 난다면 주목! 다리쥐 부르는 음식 피하는 법\n\n"
        "설명란:\n"
        "전해질이 부족하면 근육이 수축해서 쥐가 나요.\n\n"
        "#Shorts #다리쥐 #건강정보"
    )
    title, description = _parse_title_description(caption)
    assert title == "자다가 다리에 자주 쥐가 난다면 주목! 다리쥐 부르는 음식 피하는 법"
    assert description.startswith("전해질이 부족하면")
    assert "#다리쥐" in description


def test_parse_title_description_missing_marker_raises():
    with pytest.raises(ValueError):
        _parse_title_description("제목만 있고 구분자가 없는 캡션")


def test_build_status_body_without_publish_at_uses_given_privacy():
    body = _build_status_body("public", None)
    assert body["privacyStatus"] == "public"
    assert "publishAt" not in body


def test_build_status_body_with_publish_at_forces_private():
    body = _build_status_body("public", "2026-08-03T09:00:00Z")
    assert body["privacyStatus"] == "private"
    assert body["publishAt"] == "2026-08-03T09:00:00Z"


def test_extract_first_frame_produces_readable_image(make_tiny_clip):
    clip = make_tiny_clip("clip.mp4", duration=1.0, color="0xFF0000")
    frame_path = _extract_first_frame(str(clip))
    try:
        assert frame_path.exists()
        assert frame_path.stat().st_size > 0
    finally:
        frame_path.unlink(missing_ok=True)


@pytest.mark.parametrize(
    "topic, expected",
    [
        ("눈_1", "눈"),
        ("다리쥐_3", "다리쥐"),
        ("60대_1", "60대"),
        ("가슴쓰림유발음식_1", "가슴쓰림유발음식"),
    ],
)
def test_category_from_topic(topic, expected):
    assert _category_from_topic(topic) == expected


def test_playlist_title_for_category_is_descriptive():
    assert _playlist_title_for_category("눈") == "건강정보 - 눈"


# WHY(2026-08-02): "완성된 콘텐츠 목록에서 유튜브 숏츠"만" 완료되었는지를 해당
# 라인에서 확인할 수 있게" — 실제 output/youtube_uploaded.json을 건드리면 안 되니
# youtube_upload.ROOT를 tmp_path로 monkeypatch해서 격리한다.
def test_mark_youtube_uploaded_creates_file_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    (tmp_path / "output").mkdir()
    _mark_youtube_uploaded("눈_1")
    data = json.loads((tmp_path / "output" / "youtube_uploaded.json").read_text(encoding="utf-8"))
    assert data == ["눈_1"]


def test_mark_youtube_uploaded_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    (out_dir / "youtube_uploaded.json").write_text(json.dumps(["다리쥐_1"]), encoding="utf-8")
    _mark_youtube_uploaded("다리쥐_1")
    data = json.loads((out_dir / "youtube_uploaded.json").read_text(encoding="utf-8"))
    assert data == ["다리쥐_1"]
