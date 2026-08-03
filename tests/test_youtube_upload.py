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

from datetime import datetime  # noqa: E402

import lib.youtube_upload as youtube_upload  # noqa: E402
from lib.youtube_upload import (  # noqa: E402
    KST,
    _build_status_body,
    _category_from_topic,
    _category_label,
    _env_prefix,
    _extract_first_frame,
    _lang_from_topic,
    _mark_youtube_uploaded,
    _next_daily_schedule,
    _parse_title_description,
    _playlist_title_for_category,
    _topics_posted_elsewhere,
    select_daily_topics,
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


def test_parse_title_description_english_caption():
    caption = (
        "Title: Why Your Thyroid Medication Might Not Be Working\n\n"
        "Description:\n"
        "Coffee, soy, and walnuts can interfere with absorption.\n\n"
        "#Shorts #thyroid #healthtips"
    )
    title, description = _parse_title_description(caption, "en")
    assert title == "Why Your Thyroid Medication Might Not Be Working"
    assert description.startswith("Coffee, soy, and walnuts")
    assert "#thyroid" in description


def test_parse_title_description_japanese_caption():
    caption = (
        "タイトル: 食後に胸が焼けるのはなぜ？\n\n"
        "説明:\n"
        "アルコール・揚げ物・ラーメンに注意しましょう。\n\n"
        "#Shorts #健康情報"
    )
    title, description = _parse_title_description(caption, "ja")
    assert title == "食後に胸が焼けるのはなぜ？"
    assert description.startswith("アルコール")


@pytest.mark.parametrize(
    "topic, lang, expected",
    [
        ("갑상선_1", "ko", "ko"),
        ("갑상선_1/en", "en", "en"),
        ("가슴쓰림_1/ja", "ja", "ja"),
    ],
)
def test_lang_from_topic(topic, lang, expected):
    assert _lang_from_topic(topic) == expected


@pytest.mark.parametrize(
    "channel, expected",
    [
        (None, "YOUTUBE_"),
        ("en", "YOUTUBE_EN_"),
        ("zh-TW", "YOUTUBE_ZH_TW_"),
    ],
)
def test_env_prefix(channel, expected):
    assert _env_prefix(channel) == expected


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
        ("갑상선_1/en", "갑상선"),
        ("가슴쓰림_1/ja", "가슴쓰림"),
    ],
)
def test_category_from_topic(topic, expected):
    assert _category_from_topic(topic) == expected


def test_playlist_title_for_category_is_descriptive():
    assert _playlist_title_for_category("눈") == "건강정보 - 눈"


def test_playlist_title_for_category_uses_language_prefix():
    assert _playlist_title_for_category("Thyroid", "en") == "Health Info - Thyroid"
    assert _playlist_title_for_category("胸焼け", "ja") == "健康情報 - 胸焼け"


def test_category_label_ko_uses_topic_folder_name():
    assert _category_label("갑상선_1", "ko") == "갑상선"


def test_category_label_reads_topic_word_from_spec(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    spec_dir = tmp_path / "data" / "갑상선_1" / "en"
    spec_dir.mkdir(parents=True)
    (spec_dir / "card_news_spec.json").write_text(json.dumps({"topic_word": "Thyroid"}), encoding="utf-8")
    assert _category_label("갑상선_1/en", "en") == "Thyroid"


def test_category_label_missing_topic_word_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    spec_dir = tmp_path / "data" / "가슴쓰림_1" / "ja"
    spec_dir.mkdir(parents=True)
    (spec_dir / "card_news_spec.json").write_text(json.dumps({"eyebrow": "健康情報"}), encoding="utf-8")
    assert _category_label("가슴쓰림_1/ja", "ja") is None


def test_category_label_missing_spec_file_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    assert _category_label("어떤주제_1/ja", "ja") is None


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


# WHY(2026-08-02, "10시, 11시, 14시, 17시 이렇게 네 개 토픽에 대해 영상 네 개
# 넣는거야... 이미 올려놓은 것들이 있다면 그걸 우선순위로 유튜브 올리고 아닌
# 경우에는 너가 randomly하게 선택해서"): 하루 배치 업로드의 topic 선택·스케줄
# 로직 테스트. 실제 posting_log.csv/topics.json은 안 건드리고 tmp_path로 격리.

def test_topics_posted_elsewhere_excludes_youtube_platform(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    (out_dir / "posting_log.csv").write_text(
        'topic,platform,postedAt\n'
        '"눈_1","인스타그램","2026-08-01T10:00:00Z"\n'
        '"눈_1","유튜브 쇼츠","2026-08-01T11:00:00Z"\n'
        '"다리쥐_1","유튜브 쇼츠","2026-08-01T12:00:00Z"\n',
        encoding="utf-8",
    )
    assert _topics_posted_elsewhere() == {"눈_1"}


def test_topics_posted_elsewhere_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    (tmp_path / "output").mkdir()
    assert _topics_posted_elsewhere() == set()


def _write_topics_json(out_dir, topic_names):
    out_dir.joinpath("topics.json").write_text(
        json.dumps([{"topic": t, "title": t, "url": "", "thumbnail": None} for t in topic_names],
                   ensure_ascii=False),
        encoding="utf-8",
    )


def test_select_daily_topics_prioritizes_posted_elsewhere(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    _write_topics_json(out_dir, ["눈_1", "다리쥐_1", "장_1", "장_2"])
    (out_dir / "youtube_uploaded.json").write_text("[]", encoding="utf-8")
    (out_dir / "posting_log.csv").write_text(
        'topic,platform,postedAt\n"장_2","인스타그램","2026-08-01T10:00:00Z"\n',
        encoding="utf-8",
    )
    selected = select_daily_topics(n=4)
    assert selected[0] == "장_2"
    assert set(selected) == {"눈_1", "다리쥐_1", "장_1", "장_2"}


def test_select_daily_topics_excludes_already_uploaded(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_upload, "ROOT", tmp_path)
    out_dir = tmp_path / "output"
    out_dir.mkdir()
    _write_topics_json(out_dir, ["눈_1", "다리쥐_1"])
    (out_dir / "youtube_uploaded.json").write_text(json.dumps(["눈_1"]), encoding="utf-8")
    selected = select_daily_topics(n=4)
    assert selected == ["다리쥐_1"]


def test_next_daily_schedule_uses_today_when_before_first_slot():
    now = datetime(2026, 8, 2, 9, 0, tzinfo=KST)
    schedule = _next_daily_schedule(4, now=now)
    assert schedule[0] == "2026-08-02T01:00:00Z"  # 10시 KST = 01시 UTC
    assert schedule[-1] == "2026-08-02T10:00:00Z"  # 19시 KST = 10시 UTC


def test_next_daily_schedule_rolls_to_tomorrow_when_past_first_slot():
    now = datetime(2026, 8, 2, 12, 0, tzinfo=KST)
    schedule = _next_daily_schedule(4, now=now)
    assert schedule[0] == "2026-08-03T01:00:00Z"
