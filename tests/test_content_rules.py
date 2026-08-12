# data/*/ 실제 콘텐츠가 CLAUDE.md의 콘텐츠 규칙을 지키는지 스캔하는 회귀 테스트.
# WHY: 지금까지는 세션마다 수동으로 grep/눈으로 확인해왔는데, 여러 세션이 동시에
# 서로 다른 topic을 만들다 보니(2026-08-01 기준) 규칙 하나 빠뜨리는 사고가 반복됐다
# (해시태그 누락, "~대요" 잔존, network/rich_paste 플래그 오적용, 댓글 키워드 충돌 등
# 전부 CLAUDE.md에 실제로 기록된 사고 사례). topic 이름은 하드코딩하지 않고 data/*/를
# 매 실행마다 다시 스캔해서, 지금 이 순간 존재하는 topic 전체를 자동으로 검사한다.
#
# 이 파일은 읽기 전용이다 — data/*/ 콘텐츠나 ~/.claude/comment-keywords.md를
# 절대 쓰지 않는다(다른 세션이 실시간으로 편집 중일 수 있음).
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
ILLUST_DIR = ROOT / "assets_library" / "illust"
COMMENT_KEYWORDS_PATH = Path.home() / ".claude" / "comment-keywords.md"

# CLAUDE.md "[광고]+고지문" 절 기준(2026-08-10) — "네이버 클립"과 "네이버 블로그"
# 둘 다 network: "naver"를 가져야 한다. 네이버 클립은 link_in_comment도 같이
# 켜서 캡션 맨 아래에 "[광고]+고지문"이 한 덩어리로만 붙게 한다(본문 중간
# 상품 링크 삽입은 안 함 — 상품은 클립 앱 네이티브 기능으로 붙임).
NAVER_NETWORK_PLATFORMS = {"네이버 블로그", "네이버 클립"}
# WHY 네이버 클립 제외(2026-08-05): 클립은 캡션에 링크를 텍스트로 넣지 않는다
# — 사용자가 클립 앱에서 직접 "쇼핑 커넥트" 버튼으로 상품을 붙인다("내가
# 직접 링크넣고있어 영상에서"). network:"naver"는 대시보드 JS가 naver.me
# 링크를 캡션에 자동 삽입하게 만드는 트리거라, 클립에 남겨두면 실제로
# 쓰지도 않는 링크가 캡션에 끼어드는 사고로 이어진다.

# CLAUDE.md 기준 — 클립보드 HTML 붙여넣기(이미지까지 같이 들어가는) 리치 에디터는
# 네이버 블로그·티스토리뿐. 그 외 전 플랫폼은 rich_paste를 갖지 않아야 한다.
RICH_PASTE_PLATFORMS = {"네이버 블로그", "티스토리"}

# CLAUDE.md 433번대 절 "장기/증상 이름 걱정형도 약하다"에서 실제로 문제였던 정확한
# 문구 원문: "콩팥 건강 걱정되는 분들 주목!", "혈관 건강 걱정되는 분들 주목!" —
# 공통 부분인 "걱정되는 분들 주목"이 남아있으면 장기/증상명+걱정형 훅으로 되돌아간
# 것이므로 실패시킨다.
WEAK_HOOK_PHRASE = "걱정되는 분들 주목"


def _discover_topics() -> list[str]:
    """data/*/ 밑 실제 topic 디렉터리를 매번 다시 스캔한다(하드코딩 금지).

    WHY 2단계 탐색(2026-08-03, 글로벌 확장 — data/<topic>/<lang>/ 중첩 구조 도입):
    기존 flat topic(data/<topic>/platform_captions.json)은 그대로 topic 이름만
    낸다. 언어별 하위 폴더로 나뉜 새 글로벌 topic(data/<topic>/<lang>/
    platform_captions.json)은 언어 폴더가 없으면 콘텐츠 파일 자체가 없어서 그냥
    topic 이름만 내면 이후 _load_json이 전부 스킵돼 실질적으로 검사가 빠진다 —
    "<topic>/<lang>" 형태로 언어별 경로를 각각 독립 topic처럼 낸다(Path가 슬래시를
    그대로 하위 경로로 처리하므로 DATA_DIR / topic 형태의 기존 호출부는 그대로 동작)."""
    if not DATA_DIR.exists():
        return []
    topics = []
    for p in sorted(DATA_DIR.iterdir()):
        if not p.is_dir():
            continue
        if (p / "platform_captions.json").exists():
            topics.append(p.name)
            continue
        for sub in sorted(p.iterdir()):
            if sub.is_dir() and (sub / "platform_captions.json").exists():
                topics.append(f"{p.name}/{sub.name}")
    return topics


TOPICS = _discover_topics()


def _load_json(path: Path, topic: str, filename: str) -> dict:
    if not path.exists():
        pytest.skip(f"{topic}: {filename} 없음 — 아직 작업 중인 topic으로 보고 스킵")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pytest.fail(f"{topic}/{filename}: 유효하지 않은 JSON — {e}")


def _iter_strings(obj):
    """JSON 구조를 재귀적으로 순회하며 모든 leaf 문자열을 낸다.
    card_news_spec.json은 title/items[].body/closing.tip 외에 items[].name,
    closing.headline/cta 등도 전부 나레이션과 동급의 사용자 노출 텍스트라
    CLAUDE.md 자체 점검 명령(`grep -rn "대요" data/<topic>/`)도 파일 전체를
    구분 없이 훑는다 — 그 방식을 그대로 따른다."""
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_strings(v)


def _bad_endings(text: str) -> list[str]:
    """"~대요"(전언체)로 끝나는 문장이 있으면 그 문장을 반환한다.
    문장은 마침표/느낌표/물음표/줄바꿈 기준으로 자르고, 끝에 붙은 문장부호를
    뗀 뒤 실제 어미가 "대요"인지 본다(문장 내부에 "대요"가 우연히 들어간
    다른 단어의 일부인 경우는 대상에서 제외)."""
    hits = []
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", text):
        sentence = sentence.strip()
        if not sentence:
            continue
        tail = sentence.rstrip("!?.。！？\"'”’)")
        if tail.endswith("대요"):
            hits.append(sentence)
    return hits


# ---------------------------------------------------------------------------
# 규칙 6: 모든 JSON 파일이 유효한 JSON인가
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_card_news_spec_is_valid_json(topic):
    path = DATA_DIR / topic / "card_news_spec.json"
    if not path.exists():
        pytest.skip(f"{topic}: card_news_spec.json 없음")
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pytest.fail(f"{topic}/card_news_spec.json: 유효하지 않은 JSON — {e}")


@pytest.mark.parametrize("topic", TOPICS)
def test_platform_captions_is_valid_json(topic):
    path = DATA_DIR / topic / "platform_captions.json"
    if not path.exists():
        pytest.skip(f"{topic}: platform_captions.json 없음")
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        pytest.fail(f"{topic}/platform_captions.json: 유효하지 않은 JSON — {e}")


# ---------------------------------------------------------------------------
# 규칙 1: 해시태그 필수 — platform_captions.json의 모든 caption에 '#' 최소 1개
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_all_captions_have_hashtags(topic):
    spec = _load_json(DATA_DIR / topic / "platform_captions.json", topic, "platform_captions.json")
    missing = [p["name"] for p in spec.get("platforms", []) if "#" not in p.get("caption", "")]
    assert not missing, (
        f"{topic}: 아래 플랫폼 caption에 해시태그(#)가 없음 — {missing}"
    )


# ---------------------------------------------------------------------------
# 규칙 1-1: 네이버 블로그 캡션 최소 1000자 (2026-08-02, 저품질 방지 — 사용자 확정)
# ---------------------------------------------------------------------------

NAVER_BLOG_MIN_LENGTH = 1000


@pytest.mark.parametrize("topic", TOPICS)
def test_naver_blog_min_length(topic):
    spec = _load_json(DATA_DIR / topic / "platform_captions.json", topic, "platform_captions.json")
    for p in spec.get("platforms", []):
        if p["name"] == "네이버 블로그":
            length = len(p.get("caption", ""))
            assert length >= NAVER_BLOG_MIN_LENGTH, (
                f"{topic}: 네이버 블로그 caption이 {length}자 — 최소 {NAVER_BLOG_MIN_LENGTH}자 필요"
            )


# ---------------------------------------------------------------------------
# 규칙 1-2: 네이버 블로그·티스토리는 같은 원고 금지(2026-08-12, 재발 방지 —
# CLAUDE.md에 규칙은 있었는데 자동 검사가 없어서 실측 85개 topic 전부
# 제목이 동일했고 그중 29개는 본문까지 완전히 동일했던 사고 이후 추가).
# 제목(캡션 첫 줄)과 본문 전체 중 하나라도 두 플랫폼이 완전히 같으면 실패 —
# "도입부·설명 문장을 다르게 재작성"하라는 규칙의 최소 방어선.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_naver_blog_and_tistory_not_duplicated(topic):
    spec = _load_json(DATA_DIR / topic / "platform_captions.json", topic, "platform_captions.json")
    platforms = {p["name"]: p for p in spec.get("platforms", [])}
    naver = platforms.get("네이버 블로그")
    tistory = platforms.get("티스토리")
    if not naver or not tistory:
        pytest.skip(f"{topic}: 네이버 블로그·티스토리 둘 다 있는 topic 아님")
    naver_caption = naver.get("caption", "").strip()
    tistory_caption = tistory.get("caption", "").strip()
    naver_title = next((l.strip() for l in naver_caption.split("\n") if l.strip()), "")
    tistory_title = next((l.strip() for l in tistory_caption.split("\n") if l.strip()), "")
    assert naver_title != tistory_title, (
        f"{topic}: 네이버 블로그·티스토리 제목이 동일함 — {naver_title!r}"
    )
    assert naver_caption != tistory_caption, (
        f"{topic}: 네이버 블로그·티스토리 본문이 완전히 동일함 — 도입부/설명 문장을 다르게 재작성할 것"
    )


# ---------------------------------------------------------------------------
# 규칙 2: "~대요"(전언체) 금지
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_narration_no_jeonwoncheol_ending(topic):
    path = DATA_DIR / topic / "narration.txt"
    if not path.exists():
        pytest.skip(f"{topic}: narration.txt 없음")
    text = path.read_text(encoding="utf-8")
    hits = _bad_endings(text)
    assert not hits, (
        f"{topic}/narration.txt: '~대요'(전언체)로 끝나는 문장 발견 — {hits}"
    )


@pytest.mark.parametrize("topic", TOPICS)
def test_card_news_spec_no_jeonwoncheol_ending(topic):
    spec = _load_json(DATA_DIR / topic / "card_news_spec.json", topic, "card_news_spec.json")
    all_hits = []
    for s in _iter_strings(spec):
        all_hits.extend(_bad_endings(s))
    assert not all_hits, (
        f"{topic}/card_news_spec.json: '~대요'(전언체)로 끝나는 문장 발견 — {all_hits}"
    )


@pytest.mark.parametrize("topic", TOPICS)
def test_platform_captions_no_jeonwoncheol_ending(topic):
    spec = _load_json(DATA_DIR / topic / "platform_captions.json", topic, "platform_captions.json")
    all_hits = []
    for p in spec.get("platforms", []):
        hits = _bad_endings(p.get("caption", ""))
        if hits:
            all_hits.append((p["name"], hits))
    assert not all_hits, (
        f"{topic}/platform_captions.json: '~대요'(전언체)로 끝나는 문장 발견 — {all_hits}"
    )


# ---------------------------------------------------------------------------
# 규칙 3: network: "naver" 플래그 — 이름에 "네이버"가 들어간 플랫폼만
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_naver_network_flag(topic):
    spec = _load_json(DATA_DIR / topic / "platform_captions.json", topic, "platform_captions.json")
    problems = []
    for p in spec.get("platforms", []):
        name = p["name"]
        should_have_flag = name in NAVER_NETWORK_PLATFORMS
        has_flag = p.get("network") == "naver"
        if should_have_flag and not has_flag:
            problems.append(f"{name}: network=naver가 있어야 하는 플랫폼인데 없음")
        if not should_have_flag and "network" in p:
            problems.append(f"{name}: network 플래그가 없어야 하는데 존재({p.get('network')!r})")
    assert not problems, f"{topic}: {problems}"


# ---------------------------------------------------------------------------
# 규칙 4: rich_paste — 네이버 블로그·티스토리에만 true
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_rich_paste_flag(topic):
    spec = _load_json(DATA_DIR / topic / "platform_captions.json", topic, "platform_captions.json")
    problems = []
    for p in spec.get("platforms", []):
        name = p["name"]
        should_have = name in RICH_PASTE_PLATFORMS
        has_it = p.get("rich_paste") is True
        if should_have and not has_it:
            problems.append(f"{name}: rich_paste=true 여야 하는데 없음/false")
        if not should_have and "rich_paste" in p:
            problems.append(f"{name}: 단순 텍스트 입력창 플랫폼인데 rich_paste 존재({p.get('rich_paste')!r})")
    assert not problems, f"{topic}: {problems}"


# ---------------------------------------------------------------------------
# 규칙 7: card_news_spec.json의 items[].char_file이 assets_library/illust/에 실존하는가
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_char_files_exist(topic):
    spec = _load_json(DATA_DIR / topic / "card_news_spec.json", topic, "card_news_spec.json")
    missing = []
    for item in spec.get("items", []):
        char_file = item.get("char_file")
        if not char_file:
            continue
        if not (ILLUST_DIR / char_file).exists():
            missing.append(char_file)
    assert not missing, (
        f"{topic}: card_news_spec.json items[].char_file이 assets_library/illust/에 없음 — {missing}"
    )


# ---------------------------------------------------------------------------
# 규칙 8 (부분 자동화): "장기/증상 이름 + 걱정형" 훅 — 예전 문제 문구가
# 그대로 남아있으면 실패. CLAUDE.md 원문 예시: "콩팥 건강 걱정되는 분들 주목!",
# "혈관 건강 걱정되는 분들 주목!"
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("topic", TOPICS)
def test_no_weak_organ_worry_hook(topic):
    problems = []

    card_news_path = DATA_DIR / topic / "card_news_spec.json"
    if card_news_path.exists():
        spec = _load_json(card_news_path, topic, "card_news_spec.json")
        title_lines = spec.get("title", [])
        joined = "".join(title_lines)
        if any(WEAK_HOOK_PHRASE in line for line in title_lines) or WEAK_HOOK_PHRASE in joined:
            problems.append(f"card_news_spec.json title에 약한 훅 문구 잔존: {title_lines}")

    captions_path = DATA_DIR / topic / "platform_captions.json"
    if captions_path.exists():
        cap_spec = _load_json(captions_path, topic, "platform_captions.json")
        if WEAK_HOOK_PHRASE in cap_spec.get("title", ""):
            problems.append(f"platform_captions.json title에 약한 훅 문구 잔존: {cap_spec.get('title')!r}")
        for p in cap_spec.get("platforms", []):
            caption_start = p.get("caption", "")[:120]
            if WEAK_HOOK_PHRASE in caption_start:
                problems.append(f"{p['name']} caption 시작부에 약한 훅 문구 잔존: {caption_start!r}")

    assert not problems, f"{topic}: {problems}"


# ---------------------------------------------------------------------------
# 규칙 5: comment_keyword 중복 금지
#   - 지금 data/*/platform_captions.json에서 실제 쓰이는 comment_keyword가
#     서로 다른 topic 2곳 이상에서 겹치면 명백한 충돌 → fail
#   - ~/.claude/comment-keywords.md "키워드 레지스트리" 테이블에 이미 다른
#     프로젝트/topic 이름으로 등록된 키워드를 지금 data가 재사용하고 있으면
#     역시 fail(등록 안 된 새 키워드는 경고 대상이지 fail 아님)
#
# WHY UNIVERSAL_COMMENT_KEYWORD 예외(2026-08-01): topic마다 고유 키워드를 쓰던
# 방식에서 전체 topic 공용 "쿠팡"으로 정책이 바뀌었다 — 인포크 댓글→DM 자동화가
# 게시물(릴스/카드뉴스) 단위로 룰이 걸리는 구조라, 트리거 단어가 모든 topic에서
# 똑같아도 게시물마다 다른 링크를 매핑하면 되기 때문(topic마다 다른 단어를 짜내고
# 레지스트리에서 중복을 확인하던 절차가 더 이상 필요 없어짐). 그래서 이 키워드만은
# 여러 topic에서 겹치는 게 사고가 아니라 의도된 정상 상태다.
# ---------------------------------------------------------------------------

UNIVERSAL_COMMENT_KEYWORD = "쿠팡"

def _parse_registry_table(md_text: str) -> dict[str, str]:
    """"## 키워드 레지스트리" 헤딩 아래 표만 파싱한다(그 아래 "### 참고" 절은
    "미확인" 항목이라 정식 레지스트리로 취급하지 않음 — 작업지시 원문 기준).
    반환값: {키워드: 프로젝트/채널 컬럼 원문}"""
    lines = md_text.splitlines()
    registry: dict[str, str] = {}
    in_section = False
    in_table = False
    for line in lines:
        if line.strip().startswith("## "):
            in_section = line.strip() == "## 키워드 레지스트리"
            in_table = False
            continue
        if not in_section:
            continue
        if line.strip().startswith("### "):
            # 레지스트리 섹션 안의 하위 소제목(예: "### 참고 — 아직 미확인 항목")부터는
            # 정식 등록이 아니므로 파싱 중단.
            break
        if not line.strip().startswith("|"):
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) < 2:
            continue
        keyword, project = cols[0], cols[1]
        if keyword == "키워드" or set(keyword) <= {"-", ":"}:
            in_table = True
            continue
        if not in_table:
            continue
        if keyword:
            registry[keyword] = project
    return registry


def _collect_current_keyword_usage() -> dict[str, list[str]]:
    usage: dict[str, list[str]] = {}
    for topic in TOPICS:
        path = DATA_DIR / topic / "platform_captions.json"
        if not path.exists():
            continue
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue  # 별도 JSON 유효성 테스트에서 이미 잡힘
        keyword = spec.get("comment_keyword")
        if keyword:
            usage.setdefault(keyword, []).append(topic)
    return usage


def test_comment_keyword_no_cross_topic_duplicates():
    usage = _collect_current_keyword_usage()
    conflicts = {
        kw: topics
        for kw, topics in usage.items()
        if kw != UNIVERSAL_COMMENT_KEYWORD and len(set(topics)) > 1
    }
    assert not conflicts, (
        f"comment_keyword가 서로 다른 topic 2곳 이상에서 중복 사용됨(인포크 댓글→DM "
        f"자동화가 엉뚱한 topic으로 갈 수 있음): {conflicts}"
    )


def test_comment_keyword_not_registered_to_other_project():
    if not COMMENT_KEYWORDS_PATH.exists():
        pytest.skip(f"{COMMENT_KEYWORDS_PATH} 없음 — 레지스트리 파일을 찾을 수 없어 스킵")

    registry = _parse_registry_table(COMMENT_KEYWORDS_PATH.read_text(encoding="utf-8"))
    usage = _collect_current_keyword_usage()

    conflicts = []
    for keyword, topics in usage.items():
        if keyword not in registry:
            continue  # 미등록 키워드는 경고 대상이지 fail 대상이 아님
        registered_project = registry[keyword]
        owning_topics = set(topics)
        if keyword == UNIVERSAL_COMMENT_KEYWORD:
            # 전체 topic 공용 키워드는 "health-shorts / <특정 topic>"이 아니라
            # 프로젝트 전체 소속으로 등록돼 있어야 한다 — 어떤 topic이 쓰든 정상.
            matches_current_topic = "health-shorts" in registered_project
        else:
            # "health-shorts / <topic>" 형태로 지금 쓰는 topic과 정확히 일치하면 문제 없음.
            matches_current_topic = any(
                f"health-shorts / {t}" in registered_project for t in owning_topics
            )
        if not matches_current_topic:
            conflicts.append(
                f"'{keyword}'는 레지스트리에 '{registered_project}' 소속으로 이미 등록돼 "
                f"있는데, 지금 data에서는 {sorted(owning_topics)}가 같은 키워드를 씀"
            )

    assert not conflicts, "; ".join(conflicts)
