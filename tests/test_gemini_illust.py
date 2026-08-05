# lib/gemini_illust.py의 "이미 있으면 스킵" 가드 테스트. WHY: 유료 API(Gemini)를
# 실수로 다시 부르면 바로 돈이 나간다 — requests.post를 mock으로 대체해서 실제
# 네트워크/과금 없이 스킵·강제재생성 분기만 검증한다.
from __future__ import annotations

from unittest.mock import patch

from lib.gemini_illust import generate_illustration


def test_skips_api_call_when_file_already_exists(tmp_path, make_solid_jpg):
    """회귀(2026-08-05, "이쪽도 돈 계속 나간다" 최적화 요청): out_path에 파일이
    이미 있으면 requests.post를 아예 호출하지 않아야 한다."""
    existing = make_solid_jpg("돼지감자_illust.jpg")

    with patch("lib.gemini_illust.requests.post") as mock_post:
        result = generate_illustration("돼지감자", out_path=str(existing))

    mock_post.assert_not_called()
    assert result == str(existing)


def test_force_true_calls_api_even_when_file_exists(tmp_path, make_solid_jpg):
    """force=True면 파일이 있어도 의도적으로 다시 생성해야 한다."""
    existing = make_solid_jpg("양파_illust.jpg")

    fake_response = _fake_gemini_response()
    with patch("lib.gemini_illust.requests.post", return_value=fake_response) as mock_post:
        generate_illustration("양파", out_path=str(existing), force=True)

    mock_post.assert_called_once()


def test_calls_api_when_file_does_not_exist(tmp_path):
    """파일이 아예 없으면 정상적으로 API를 호출해서 생성해야 한다."""
    out_path = tmp_path / "가지_illust.jpg"

    fake_response = _fake_gemini_response()
    with patch("lib.gemini_illust.requests.post", return_value=fake_response) as mock_post:
        result = generate_illustration("가지", out_path=str(out_path))

    mock_post.assert_called_once()
    assert out_path.exists()
    assert result == str(out_path)


def _fake_gemini_response():
    import base64
    from unittest.mock import MagicMock

    tiny_jpg = base64.b64encode(b"fake jpg bytes").decode("ascii")
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.json.return_value = {
        "candidates": [{"content": {"parts": [{"inlineData": {"data": tiny_jpg}}]}}]
    }
    return resp
