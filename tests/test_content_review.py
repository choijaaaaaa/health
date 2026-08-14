# lib/content_review.py 테스트. WHY 이 파일이 API mock을 안 쓰는지(2026-08-15):
# content_review.py는 더 이상 Gemini(또는 어떤 외부 LLM)도 호출하지 않는다 —
# 논리/과장/번역독립성 판단은 세션이 직접 하는 것으로 바뀌었고, 이 파일엔
# 패턴 매칭만으로 되는 기계적 검사만 남았다. 그래서 이 테스트들도 전부
# 순수 함수 호출 + 파일시스템 fixture만으로 검증한다(mock 불필요).
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import lib.content_review as content_review  # noqa: E402
from lib.content_review import (  # noqa: E402
    _lang_code,
    _topic_dir,
    check_blog_title_length,
    check_title_closing,
    check_title_truncation,
    review_all,
    review_topic,
    select_hook_pattern,
)


def _write_topic(tmp_path, monkeypatch, topic: str, spec: dict | None = None, captions: dict | None = None):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    data_dir = tmp_path / "data" / topic
    data_dir.mkdir(parents=True)
    if spec is not None:
        (data_dir / "card_news_spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    if captions is not None:
        (data_dir / "platform_captions.json").write_text(json.dumps(captions, ensure_ascii=False), encoding="utf-8")
    return data_dir


def _write_nested_topic(tmp_path, monkeypatch, topic: str, lang_code: str = "ko",
                         spec: dict | None = None, captions: dict | None = None):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    data_dir = tmp_path / "data" / topic / lang_code
    data_dir.mkdir(parents=True)
    if spec is not None:
        (data_dir / "card_news_spec.json").write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    if captions is not None:
        (data_dir / "platform_captions.json").write_text(json.dumps(captions, ensure_ascii=False), encoding="utf-8")
    return data_dir


# ---------------------------------------------------------------------------
# _topic_dir / _lang_code
# ---------------------------------------------------------------------------

def test_topic_dir_resolves_nested_ko_folder_when_present(tmp_path, monkeypatch):
    _write_nested_topic(tmp_path, monkeypatch, "목_1", "ko", spec={"title": ["훅"]})
    assert _topic_dir("목_1", "kor") == tmp_path / "data" / "목_1" / "ko"


def test_topic_dir_resolves_nested_lang_folder_via_name_reverse_lookup(tmp_path, monkeypatch):
    _write_nested_topic(tmp_path, monkeypatch, "목_1", "en", spec={"title": ["hook"]})
    assert _topic_dir("목_1", "영어") == tmp_path / "data" / "목_1" / "en"


def test_topic_dir_falls_back_to_flat_when_no_nested_folder(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec={"title": ["훅"]})
    assert _topic_dir("테스트토픽_1", "kor") == tmp_path / "data" / "테스트토픽_1"


def test_lang_code_kor_maps_to_ko():
    assert _lang_code("kor") == "ko"


def test_lang_code_reverse_lookup_from_korean_name():
    assert _lang_code("영어") == "en"


def test_lang_code_unknown_passes_through():
    assert _lang_code("xx") == "xx"


# ---------------------------------------------------------------------------
# check_title_truncation
# ---------------------------------------------------------------------------

def test_check_title_truncation_flags_korean_continuation_ending(tmp_path, monkeypatch):
    spec = {"title": ["혈당 관리에 어려움이 있는", "분들이라면"]}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec)
    issues = check_title_truncation("테스트토픽_1")
    assert len(issues) == 1
    assert issues[0]["severity"] == "high"


def test_check_title_truncation_passes_independent_label(tmp_path, monkeypatch):
    spec = {"title": ["혈당 관리에 어려움이 있는 분들 주목!", "돼지감자차 이야기"]}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec)
    assert check_title_truncation("테스트토픽_1") == []


def test_check_title_truncation_flags_lowercase_start_for_english(tmp_path, monkeypatch):
    spec = {"title": ["Struggling with blood sugar", "and how to fix it"]}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec)
    issues = check_title_truncation("테스트토픽_1", lang="en")
    assert len(issues) == 1


def test_check_title_truncation_skips_single_line_title(tmp_path, monkeypatch):
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec={"title": ["한 줄짜리 훅"]})
    assert check_title_truncation("테스트토픽_1") == []


def test_check_title_truncation_missing_spec_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    (tmp_path / "data" / "테스트토픽_1").mkdir(parents=True)
    assert check_title_truncation("테스트토픽_1") == []


# ---------------------------------------------------------------------------
# check_title_closing
# ---------------------------------------------------------------------------

def test_check_title_closing_flags_generic_cta_in_card_news_title(tmp_path, monkeypatch):
    spec = {"title": ["다래끼, 자꾸 나거나 낫는 데 오래 걸린다면", "저장부터 하세요"]}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec)
    issues = check_title_closing("테스트토픽_1")
    assert len(issues) == 1
    assert issues[0]["severity"] == "medium"


def test_check_title_closing_flags_generic_cta_in_blog_title(tmp_path, monkeypatch):
    captions = {"title": "다래끼, 자꾸 나거나 낫는 데 오래 걸린다면 - 확인하세요"}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", captions=captions)
    issues = check_title_closing("테스트토픽_1")
    assert len(issues) == 1


def test_check_title_closing_passes_descriptive_label(tmp_path, monkeypatch):
    spec = {"title": ["다래끼, 자꾸 나거나 낫는 데 오래 걸린다면", "재발 줄이는 습관 3가지"]}
    captions = {"title": "다래끼, 자꾸 나거나 낫는 데 오래 걸린다면 - 재발 줄이는 습관 3가지"}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec, captions=captions)
    assert check_title_closing("테스트토픽_1") == []


# ---------------------------------------------------------------------------
# check_blog_title_length
# ---------------------------------------------------------------------------

def test_check_blog_title_length_passes_within_range(tmp_path, monkeypatch):
    captions = {
        "title": "적당한 길이의 블로그 제목입니다 - 습관 세 가지",
        "platforms": [{"name": "네이버 블로그"}],
    }
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", captions=captions)
    assert check_blog_title_length("테스트토픽_1") == []


def test_check_blog_title_length_flags_too_short(tmp_path, monkeypatch):
    captions = {"title": "짧은 제목", "platforms": [{"name": "네이버 블로그"}]}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", captions=captions)
    issues = check_blog_title_length("테스트토픽_1")
    assert len(issues) == 1


def test_check_blog_title_length_skips_topic_without_blog_platform(tmp_path, monkeypatch):
    captions = {"title": "짧은 제목", "platforms": [{"name": "YouTube Shorts"}]}
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", captions=captions)
    assert check_blog_title_length("테스트토픽_1") == []


def test_check_blog_title_length_missing_file_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    (tmp_path / "data" / "테스트토픽_1").mkdir(parents=True)
    assert check_blog_title_length("테스트토픽_1") == []


# ---------------------------------------------------------------------------
# review_topic — 세 기계적 검사의 합
# ---------------------------------------------------------------------------

def test_review_topic_combines_all_mechanical_checks(tmp_path, monkeypatch):
    spec = {"title": ["혈당 관리에 관심이 있는", "분들이라면"]}  # truncation 위반("면"으로 끝남)
    captions = {"title": "짧음", "platforms": [{"name": "네이버 블로그"}]}  # length 위반
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec, captions=captions)
    issues = review_topic("테스트토픽_1")
    assert len(issues) == 2


def test_review_topic_clean_topic_returns_empty(tmp_path, monkeypatch):
    spec = {"title": ["깔끔한 훅 문장이에요", "독립 라벨"]}
    captions = {
        "title": "충분히 긴 정상적인 블로그 제목입니다 - 습관 세 가지",
        "platforms": [{"name": "네이버 블로그"}],
    }
    _write_topic(tmp_path, monkeypatch, "테스트토픽_1", spec=spec, captions=captions)
    assert review_topic("테스트토픽_1") == []


# ---------------------------------------------------------------------------
# review_all
# ---------------------------------------------------------------------------

def test_review_all_reports_topics_with_issues(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(content_review, "ROOT", tmp_path)
    clean_dir = tmp_path / "data" / "토픽A_1"
    clean_dir.mkdir(parents=True)
    (clean_dir / "narration.txt").write_text("정상 문장.", encoding="utf-8")

    dirty_dir = tmp_path / "data" / "토픽B_1"
    dirty_dir.mkdir(parents=True)
    (dirty_dir / "narration.txt").write_text("문장.", encoding="utf-8")
    (dirty_dir / "card_news_spec.json").write_text(
        json.dumps({"title": ["혈당 관리에 관심이 있는", "분들이라면"]}, ensure_ascii=False), encoding="utf-8",
    )

    results = review_all()
    assert "토픽B_1" in results
    assert "토픽A_1" not in results
    out = capsys.readouterr().out
    assert "1개에서 문제 발견" in out


# ---------------------------------------------------------------------------
# select_hook_pattern — 결정론적 시드
# ---------------------------------------------------------------------------

def test_select_hook_pattern_is_deterministic_for_same_topic():
    assert select_hook_pattern("눈_1") == select_hook_pattern("눈_1")


def test_select_hook_pattern_returns_name_and_description_tuple():
    name, desc = select_hook_pattern("눈_1")
    assert isinstance(name, str) and name
    assert isinstance(desc, str) and desc
