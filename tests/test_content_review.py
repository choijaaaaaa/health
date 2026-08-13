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
from lib.content_review import (  # noqa: E402
    _build_blog_prompt,
    _build_prompt,
    _card_news_text,
    _topic_dir,
    check_blog_title_independence,
    review_blog_seo,
    review_topic,
)


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


# WHY 이 테스트들이 필요한지(2026-08-04 회귀 방지): review_topic/_card_news_text가
# 전부 data/<topic>/narration.txt(구식 단일 언어 구조)만 보고 있어서, 2026-08-03
# 글로벌 확장으로 모든 topic이 data/<topic>/<lang>/ 중첩 구조로 바뀐 뒤에는 실제로는
# 파일을 하나도 못 찾아 조용히 "문제 없음"(빈 리스트)을 반환하고 있었다 — 에러도 안
# 나고 API 호출도 안 되니 겉으로는 "정상적으로 통과"처럼 보였다. 위 _write_topic
# 기반 테스트들은 전부 평평한 구조라 이 버그를 못 잡았다(폴백 경로만 탔음) — 이
# 테스트들은 실제 운영 구조(중첩)를 흉내내서 진짜로 파일을 찾는지 확인한다.

def _write_nested_topic(tmp_path, monkeypatch, topic: str, lang_code: str = "ko",
                         narration: str = "", spec: dict | None = None):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    data_dir = tmp_path / "data" / topic / lang_code
    data_dir.mkdir(parents=True)
    if narration:
        (data_dir / "narration.txt").write_text(narration, encoding="utf-8")
    if spec is not None:
        (data_dir / "card_news_spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")


def test_topic_dir_resolves_nested_ko_folder_when_present(tmp_path, monkeypatch):
    _write_nested_topic(tmp_path, monkeypatch, "목_1", "ko", narration="아무 문장.")
    assert _topic_dir("목_1", "kor") == tmp_path / "data" / "목_1" / "ko"


def test_topic_dir_resolves_nested_lang_folder_via_name_reverse_lookup(tmp_path, monkeypatch):
    _write_nested_topic(tmp_path, monkeypatch, "목_1", "en", narration="Some sentence.")
    assert _topic_dir("목_1", "영어") == tmp_path / "data" / "목_1" / "en"


def test_topic_dir_falls_back_to_flat_when_no_nested_folder(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", narration="아무 문장.")
    assert _topic_dir("테스트토픽_1", "kor") == tmp_path / "data" / "테스트토픽_1"


def test_review_topic_finds_content_in_nested_ko_structure(tmp_path, monkeypatch):
    """회귀: 중첩 구조 topic의 narration.txt를 못 찾아 API 호출 자체를 건너뛰고
    조용히 빈 리스트를 반환하던 버그(2026-08-04)."""
    _write_nested_topic(tmp_path, monkeypatch, "목_1", "ko", narration="문제되는 문장이야.")
    fake_issues = [{"quote": "문제되는 문장이야.", "issue": "테스트용 이슈"}]

    def fake_post(*args, **kwargs):
        return _FakeResponse(json.dumps(fake_issues, ensure_ascii=False))

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    result = review_topic("목_1")
    assert result == fake_issues


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


# ---------------------------------------------------------------------------
# review_blog_seo / _build_blog_prompt — 2026-08-13 blog_seo QA 커버리지 추가
# ---------------------------------------------------------------------------

def _write_blog_topic(tmp_path, monkeypatch, topic: str, lang_code: str,
                       blog: dict | None, extra_platforms: list[dict] | None = None):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    data_dir = tmp_path / "data" / topic / lang_code
    data_dir.mkdir(parents=True)
    platforms = list(extra_platforms or [])
    if blog is not None:
        platforms.append({"platform": "blog_seo", **blog})
    spec = {"topic": f"{topic}_{lang_code}", "title": "영상 훅 제목", "platforms": platforms}
    (data_dir / "platform_captions.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")


def test_review_blog_seo_missing_file_returns_empty_without_api_call(tmp_path, monkeypatch):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    (tmp_path / "data" / "테스트토픽_1" / "es").mkdir(parents=True)

    def fake_post(*args, **kwargs):
        raise AssertionError("platform_captions.json이 없으면 API를 호출하면 안 됨")

    monkeypatch.setattr(content_review.requests, "post", fake_post)
    assert review_blog_seo("테스트토픽_1", "es") == []


def test_review_blog_seo_no_blog_entry_returns_empty_without_api_call(tmp_path, monkeypatch):
    _write_blog_topic(tmp_path, monkeypatch, "테스트토픽_1", "es", blog=None,
                       extra_platforms=[{"name": "YouTube Shorts", "caption": "영상 캡션"}])

    def fake_post(*args, **kwargs):
        raise AssertionError("blog_seo 항목이 없으면 API를 호출하면 안 됨")

    monkeypatch.setattr(content_review.requests, "post", fake_post)
    assert review_blog_seo("테스트토픽_1", "es") == []


def test_review_blog_seo_sends_title_meta_body_and_parses_result(tmp_path, monkeypatch):
    blog = {
        "title": "문제되는 제목",
        "meta_description": "문제되는 메타 설명",
        "body_html": "<p>문제되는 본문 문장.</p>",
    }
    _write_blog_topic(tmp_path, monkeypatch, "테스트토픽_1", "es", blog=blog)
    fake_issues = [{"quote": "문제되는 본문 문장.", "issue": "테스트용 이슈"}]
    captured = {}

    def fake_post(*args, **kwargs):
        captured["prompt"] = kwargs["json"]["contents"][0]["parts"][0]["text"]
        return _FakeResponse(json.dumps(fake_issues, ensure_ascii=False))

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    result = review_blog_seo("테스트토픽_1", "es")
    assert result == fake_issues
    assert "문제되는 제목" in captured["prompt"]
    assert "문제되는 메타 설명" in captured["prompt"]
    assert "문제되는 본문 문장." in captured["prompt"]
    assert "<p>" not in captured["prompt"]  # HTML 태그는 제거돼야 함


def test_review_topic_includes_blog_seo_issues(tmp_path, monkeypatch):
    """review_topic()이 narration/card_news 리뷰뿐 아니라 blog_seo도 자동으로
    합쳐서 반환하는지(단일 CLI 명령으로 전부 커버되는 게 이번 변경의 핵심)."""
    _write_nested_topic(tmp_path, monkeypatch, "테스트토픽_1", "es", narration="정상 문장.")
    blog = {"title": "t", "meta_description": "m", "body_html": "<p>블로그 문제 문장.</p>"}
    caption_path = tmp_path / "data" / "테스트토픽_1" / "es" / "platform_captions.json"
    caption_path.write_text(
        json.dumps({"topic": "t_es", "title": "훅", "platforms": [{"platform": "blog_seo", **blog}]}, ensure_ascii=False),
        encoding="utf-8",
    )
    narration_issues = []
    blog_issues = [{"quote": "블로그 문제 문장.", "issue": "블로그 이슈"}]

    def fake_post(*args, **kwargs):
        prompt = kwargs["json"]["contents"][0]["parts"][0]["text"]
        body = blog_issues if "블로그" in prompt else narration_issues
        return _FakeResponse(json.dumps(body, ensure_ascii=False))

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    result = review_topic("테스트토픽_1", "es")
    assert blog_issues[0] in result


def test_build_blog_prompt_includes_regulatory_note_for_known_lang():
    prompt = _build_blog_prompt("es", "제목", "메타", "<p>본문</p>")
    assert "AESAN" in prompt
    assert "번역투" in prompt  # BLOG_NATIVE_FLUENCY_CRITERION
    assert "검색될 법한 핵심 증상" in prompt  # BLOG_TITLE_SEARCHABILITY_CRITERION


def test_build_blog_prompt_omits_regulatory_note_for_unknown_lang_code():
    # "xx"는 REGULATORY_NOTES_BY_LANG에 없는 코드 — 프롬프트 생성 자체는
    # 에러 없이 되고, 규제 기준 문구만 빠져야 한다(GLOBAL_LANG_LABELS_FALLBACK도
    # 모르는 코드라 _lang_code가 그대로 "xx"를 반환하는 경로).
    prompt = _build_blog_prompt("xx", "제목", "메타", "<p>본문</p>")
    assert "광고/표시규제" not in prompt


def test_build_blog_prompt_strips_html_tags_from_body():
    prompt = _build_blog_prompt("es", "제목", "메타", "<h2>소제목</h2><p>본문 문장.</p>")
    assert "<h2>" not in prompt
    assert "<p>" not in prompt
    assert "본문 문장." in prompt


def test_build_blog_prompt_includes_fabricated_precision_criterion_for_all_langs():
    # 이 기준(출처 없는 과도하게 정밀한 수치)은 kor/비kor 둘 다에 적용돼야 함
    # — BLOG_NATIVE_FLUENCY_CRITERION/BLOG_REGULATORY_CRITERION과 달리 언어
    # 무관한 팩트체크 문제라서.
    non_kor_prompt = _build_blog_prompt("es", "제목", "메타", "<p>본문</p>")
    kor_prompt = _build_blog_prompt("kor", "제목", "메타", "<p>본문</p>")
    assert "검증이 불가능한 과도하게 정밀한" in non_kor_prompt
    assert "검증이 불가능한 과도하게 정밀한" in kor_prompt


# ---------------------------------------------------------------------------
# check_blog_title_independence — ko가 없는 blog_seo 전용 언어독립성 검사
# ---------------------------------------------------------------------------

def test_check_blog_title_independence_returns_empty_for_fewer_than_two_langs(tmp_path, monkeypatch):
    _write_blog_topic(tmp_path, monkeypatch, "테스트토픽_1", "es", blog={"title": "t"})
    assert check_blog_title_independence("테스트토픽_1") == {}


def test_check_blog_title_independence_uses_alphabetically_first_as_anchor(tmp_path, monkeypatch):
    """blog_seo는 ko가 없으니 기준점은 코드명 사전순 첫 언어(예: de/es/ja 중 de)여야
    하고, 기준점 언어 자신은 결과 키에 없어야 한다(자기 자신과 비교 안 함)."""
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    for lang_code, title in [("ja", "日本語のタイトル"), ("de", "Deutscher Titel"), ("es", "Título en español")]:
        data_dir = tmp_path / "data" / "테스트토픽_1" / lang_code
        data_dir.mkdir(parents=True)
        spec = {"topic": f"t_{lang_code}", "title": "훅", "platforms": [{"platform": "blog_seo", "title": title}]}
        (data_dir / "platform_captions.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")

    captured_prompts = []

    def fake_post(*args, **kwargs):
        prompt = kwargs["json"]["contents"][0]["parts"][0]["text"]
        captured_prompts.append(prompt)
        return _FakeResponse(json.dumps({"is_translation": False, "reason": "독립적"}, ensure_ascii=False))

    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setattr(content_review.requests, "post", fake_post)

    results = check_blog_title_independence("테스트토픽_1")
    assert set(results.keys()) == {"es", "ja"}  # "de"가 기준점이라 결과 키에 없음
    assert all("Deutscher Titel" in p for p in captured_prompts)  # 모든 비교가 기준점(de) 대비
