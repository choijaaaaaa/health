# lib/youtube_upload.py의 캡션 파서 테스트. WHY: 실제 유튜브 API는 절대 호출하지
# 않는다(비용은 없지만 실제 채널에 업로드되는 부작용이 있음) — "제목: ...\n\n설명란:\n..."
# 형식을 (title, description)으로 정확히 분리하는지만 검증한다. 이 형식은
# lib/dashboard.py가 만드는 "유튜브 쇼츠" 캡션과 동일해야 한다.
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.youtube_upload import _parse_title_description  # noqa: E402


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
