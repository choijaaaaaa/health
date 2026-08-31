# blog_seo 글이 "검색에 실제로 통하는 형태"인지 검사하는 회귀 테스트.
# WHY 별도 파일인지(2026-08-31): test_content_rules.py는 캡션 규칙(해시태그·
# 플래그·훅 문구)을 다루고 이 파일은 발행 품질(분량·제목 길이)만 다룬다 —
# 두 관심사가 섞이면 한쪽 실패가 다른 쪽을 가린다.
#
# WHY 이 검사가 필요해졌는지: 이 기준은 원래 인입 스크립트
# (../verticals/vernhaven-blog/scripts/ingest_health_shorts.py)에만 있었고
# 그것도 "경고"로만 찍혔다 — 실행해도 아무것도 안 막으니 아무도 안 고쳤고,
# 2026-08-31 실측에서 84편이 최소 분량 미달(최저 257단어), 49편이 제목 길이
# 초과인 채로 이미 인입돼 있었다. 콘텐츠를 만드는 쪽(이 저장소)에서 막지
# 않으면 발행 직전에야 경고로 알게 되고, 그때는 이미 늦다.
#
# 이 파일은 읽기 전용이다 — data/*/ 를 절대 쓰지 않는다(다른 세션이 실시간
# 편집 중일 수 있음).
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DEBT_PATH = DATA_DIR / "_audit" / "blog_seo_quality_debt.json"

# ⚠️ 값 동기화 필수 — ingest_health_shorts.py의 동명 상수와 같은 값이어야 한다.
# 저장소가 달라 상수를 공유할 방법이 없다(이 프로젝트의 다른 이중 구현들과 같은 사정).
MIN_BODY_WORDS_LATIN = 500
MIN_BODY_CHARS_CJK = 1000
TITLE_MAX_CHARS = {"ko": 35, "ja": 35}
TITLE_MAX_CHARS_DEFAULT = 65

CJK_LANGS = ("ja", "ko")
_TAG_RE = re.compile(r"<[^>]+>")


def _strip_tags(html: str) -> str:
    # 인입 스크립트의 strip_tags와 동일 — 태그를 공백으로 바꿔 단어 경계를 만든다.
    return _TAG_RE.sub(" ", html)


def _discover_blog_seo() -> list[str]:
    """blog_seo 항목을 실제로 가진 "<topic>/<lang>" 전부. topic 이름 하드코딩 금지."""
    if not DATA_DIR.exists():
        return []
    found = []
    for topic_dir in sorted(DATA_DIR.iterdir()):
        if not topic_dir.is_dir():
            continue
        for lang_dir in sorted(topic_dir.iterdir()):
            if not lang_dir.is_dir():
                continue
            path = lang_dir / "platform_captions.json"
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            if any(p.get("platform") == "blog_seo" for p in data.get("platforms", [])):
                found.append(f"{topic_dir.name}/{lang_dir.name}")
    return found


COMBOS = _discover_blog_seo()


def _load_debt() -> dict[str, dict]:
    """이미 발행됐지만 아직 못 고친 건들의 명시적 목록.

    WHY 예외 목록을 두는지: 지금 있는 미달분(2026-08-31 기준 분량 84편·제목 49편)을
    전부 고치기 전에는 이 테스트가 통째로 빨간불이 되고, 그러면 새로 들어오는
    위반을 아무도 못 본다 — 기존 채무는 명시적으로 적어두고 "새 위반 0"을 먼저
    강제한다.
    WHY 고쳐진 항목이 목록에 남아 있으면 실패시키는지: 안 그러면 예외 목록이
    영원히 안 줄어든다. 고치는 쪽이 목록에서 지우는 게 강제돼야 채무가 단조 감소한다.
    """
    if not DEBT_PATH.exists():
        return {}
    entries = json.loads(DEBT_PATH.read_text(encoding="utf-8")).get("entries", {})
    return entries


DEBT = _load_debt()


def _blog_seo_entry(combo: str) -> dict:
    path = DATA_DIR / combo / "platform_captions.json"
    if not path.exists():
        pytest.skip(f"{combo}: platform_captions.json 없음")
    data = json.loads(path.read_text(encoding="utf-8"))
    for platform in data.get("platforms", []):
        if platform.get("platform") == "blog_seo":
            return platform
    pytest.skip(f"{combo}: blog_seo 항목 없음")


def _body_shortfall(combo: str, entry: dict) -> str | None:
    """분량 미달이면 사람이 읽을 설명, 충족이면 None."""
    lang = combo.split("/")[1]
    text = _strip_tags(entry.get("body_html", ""))
    if lang in CJK_LANGS:
        if len(text) < MIN_BODY_CHARS_CJK:
            return f"본문 {len(text)}자 (최소 {MIN_BODY_CHARS_CJK}자)"
        return None
    words = len(text.split())
    if words < MIN_BODY_WORDS_LATIN:
        return f"본문 {words}단어 (최소 {MIN_BODY_WORDS_LATIN}단어)"
    return None


def _title_overflow(combo: str, entry: dict) -> str | None:
    lang = combo.split("/")[1]
    limit = TITLE_MAX_CHARS.get(lang, TITLE_MAX_CHARS_DEFAULT)
    title = entry.get("title", "")
    if len(title) > limit:
        return f"제목 {len(title)}자 (최대 {limit}자)"
    return None


@pytest.mark.parametrize("combo", COMBOS)
def test_blog_seo_body_meets_minimum_length(combo):
    """검색 노출에 불리한 얇은 글을 새로 만들지 못하게 막는다."""
    shortfall = _body_shortfall(combo, _blog_seo_entry(combo))
    allowed = DEBT.get(combo, {}).get("body")
    if allowed:
        assert shortfall, (
            f"{combo}: 분량 미달이 해소됐는데 {DEBT_PATH.name}에 아직 남아 있다 "
            f"— 해당 항목의 \"body\" 키를 지울 것(채무 목록은 줄어들기만 해야 한다)"
        )
        return
    assert not shortfall, (
        f"{combo}: {shortfall} — 물타기 말고 그 언어권 공식기관 자료로 섹션을 더할 것. "
        f"이미 발행된 글이라 당장 못 고치면 {DEBT_PATH} 에 사유와 함께 등록할 것"
    )


@pytest.mark.parametrize("combo", COMBOS)
def test_blog_seo_title_fits_search_result(combo):
    """구글 검색결과에서 잘리는 제목을 새로 만들지 못하게 막는다."""
    overflow = _title_overflow(combo, _blog_seo_entry(combo))
    allowed = DEBT.get(combo, {}).get("title")
    if allowed:
        assert overflow, (
            f"{combo}: 제목 길이가 해소됐는데 {DEBT_PATH.name}에 아직 남아 있다 "
            f"— 해당 항목의 \"title\" 키를 지울 것"
        )
        return
    assert not overflow, (
        f"{combo}: {overflow} — 핵심 검색어를 앞에 두고 훅은 살린 채 줄일 것. "
        f"slug는 절대 바꾸지 말 것(이미 인입된 글의 URL이 끊긴다)"
    )


def test_debt_list_has_no_stale_entries():
    """채무 목록에 이제 존재하지도 않는 조합이 남아 있으면 실패시킨다.

    WHY: topic이 지워지거나 이름이 바뀌면 예외만 남아 목록이 실제보다 커 보인다 —
    "얼마나 남았나"를 이 파일 하나로 신뢰할 수 있어야 한다.
    """
    stale = sorted(set(DEBT) - set(COMBOS))
    assert not stale, f"{DEBT_PATH.name}에 존재하지 않는 조합이 남아 있음 — {stale}"
