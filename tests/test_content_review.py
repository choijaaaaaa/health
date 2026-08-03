# lib/content_review.py 테스트. WHY: 실제 Gemini API는 절대 호출하지 않는다(과금·
# 네트워크 의존) — requests.post를 monkeypatch로 가짜 응답으로 대체하고, 문자열
# 추출·JSON 파싱 로직만 검증한다(다른 외부 API 모듈 테스트와 같은 패턴, 예:
# test_youtube_upload.py).
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib.content_review as content_review  # noqa: E402
from lib.content_review import _build_prompt, _card_news_text, review_topic  # noqa: E402


class _FakeResponse:
    def __init__(self, text: str, status_code: int = 200):
        self._text = text
        self.status_code = status_code

    def raise_for_status(self):
        pass

    def json(self):
        return {"candidates": [{"content": {"parts": [{"text": self._text}]}}]}


def _write_topic(tmp_path, monkeypatch, topic: str, narration: str = "", spec: dict | None = None):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    data_dir = tmp_path / "data" / topic
    data_dir.mkdir(parents=True)
    if narration:
        (data_dir / "narration.txt").write_text(narration, encoding="utf-8")
    if spec is not None:
        (data_dir / "card_news_spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")


def test_card_news_text_extracts_items_and_closing_only(tmp_path, monkeypatch):
    spec = {
        "cover_char_file": "맥주_illust.jpg",
        "cover_scrim_color": "#000000",
        "items": [
            {"name": "맥주", "char_file": "맥주_illust.jpg", "body": ["첫 줄", "둘째 줄"]},
        ],
        "closing": {
            "headline": [["헤드라인1", "헤드라인2"]],
            "tip": ["팁 문장"],
            "cta": "구독해주세요",
        },
    }
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec)
    text = _card_news_text("테스트토픽_1")
    assert "맥주" in text
    assert "첫 줄" in text
    assert "둘째 줄" in text
    assert "헤드라인1" in text
    assert "팁 문장" in text
    assert "구독해주세요" in text
    # char_file/cover_scrim_color 같은 비텍스트 필드는 안 섞여 들어가야 함
    assert "illust.jpg" not in text
    assert "#000000" not in text


def test_card_news_text_missing_file_returns_empty(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1")
    assert _card_news_text("테스트토픽_1") == ""


def test_review_topic_parses_json_array_response(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="문제되는 문장이야.")
    fake_issues = [{"quote": "문제되는 문장이야.", "issue": "테스트용 이슈"}]
    fake_body = json.dumps(fake_issues, ensure_ascii=False)

    # WHY **kwargs인지: requests.post(..., headers=..., json=...)를 키워드 인자로
    # 호출하는데, 인자명을 json으로 받으면 함수 안에서 모듈 전역 json이 가려져
    # 위에서 미리 만들어둔 fake_body(json.dumps 결과)를 못 쓴다 — **kwargs로 받아
    # 그 충돌을 피한다.
    def fake_post(*args, **kwargs):
        return _FakeResponse(fake_body)

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    result = review_topic("테스트토픽_1")
    assert result == fake_issues


def test_review_topic_strips_code_fence_before_parsing(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="아무 문장.")
    fenced = "```json\n[{\"quote\": \"아무 문장.\", \"issue\": \"이슈\"}]\n```"

    def fake_post(*args, **kwargs):
        return _FakeResponse(fenced)

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    result = review_topic("테스트토픽_1")
    assert result == [{"quote": "아무 문장.", "issue": "이슈"}]


def test_review_topic_returns_empty_list_on_unparseable_response(tmp_path, monkeypatch, capsys):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="아무 문장.")

    def fake_post(*args, **kwargs):
        return _FakeResponse("이건 JSON이 아닙니다")

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    result = review_topic("테스트토픽_1")
    assert result == []
    assert "파싱 실패" in capsys.readouterr().out


def test_review_topic_no_content_skips_api_call(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1")

    def fake_post(*args, **kwargs):
        raise AssertionError("콘텐츠가 없으면 API를 호출하면 안 됨")

    monkeypatch.setattr(content_review.requests, "post", fake_post)
    assert review_topic("테스트토픽_1") == []


def test_review_topic_retries_then_succeeds_after_transient_503(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="아무 문장.")
    fake_issues = [{"quote": "아무 문장.", "issue": "이슈"}]
    fake_body = json.dumps(fake_issues, ensure_ascii=False)
    calls = {"n": 0}

    def fake_post(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] < 3:
            return _FakeResponse("일시적 서버 오류", status_code=503)
        return _FakeResponse(fake_body, status_code=200)

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)
    monkeypatch.setattr(content_review.time, "sleep", lambda _: None)

    result = review_topic("테스트토픽_1")
    assert result == fake_issues
    assert calls["n"] == 3


def test_review_topic_gives_up_after_repeated_503_and_returns_empty(tmp_path, monkeypatch, capsys):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="아무 문장.")

    def fake_post(*args, **kwargs):
        return _FakeResponse("일시적 서버 오류", status_code=503)

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)
    monkeypatch.setattr(content_review.time, "sleep", lambda _: None)

    result = review_topic("테스트토픽_1")
    assert result == []
    assert "건너뜀" in capsys.readouterr().out


def test_build_prompt_default_lang_is_korean_without_regional_criterion(tmp_path, monkeypatch):
    prompt = _build_prompt("kor", "나레이션", "카드텍스트")
    assert "한국어" in prompt
    assert "해결책 재료" not in prompt  # REGIONAL_CRITERION은 한국어 리뷰엔 없어야 함


def test_build_prompt_non_kor_adds_regional_criterion_and_language_name(tmp_path, monkeypatch):
    prompt = _build_prompt("영어", "narration", "card text")
    assert "영어" in prompt
    assert "해결책 재료" in prompt  # 지역 소싱 기준이 추가돼야 함


def test_review_topic_passes_lang_through_to_prompt(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="Some sentence.")
    captured = {}

    def fake_post(*args, **kwargs):
        captured["prompt"] = kwargs["json"]["contents"][0]["parts"][0]["text"]
        return _FakeResponse("[]")

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    review_topic("테스트토픽_1", lang="영어")
    assert "영어" in captured["prompt"]
    assert "해결책 재료" in captured["prompt"]


def test_review_all_continues_past_one_topic_erroring(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    for topic, narration in [("토픽A_1", "정상 문장."), ("토픽B_1", "에러날 문장.")]:
        data_dir = tmp_path / "data" / topic
        data_dir.mkdir(parents=True)
        (data_dir / "narration.txt").write_text(narration, encoding="utf-8")

    def fake_review_topic(topic):
        if topic == "토픽B_1":
            raise content_review.requests.exceptions.ConnectionError("네트워크 오류")
        return []

    monkeypatch.setattr(content_review, "review_topic", fake_review_topic)
    results = content_review.review_all()
    assert results == {}
    assert "건너뜀" in capsys.readouterr().out
