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

# CLAUDE.md "플랫폼별 필수 플래그" 절 기준 — 이름에 "네이버"가 들어간 플랫폼만
# network: "naver"를 가져야 한다(네이버 에디터에만 있는 "상품" 버튼 처리용).
NAVER_NAME_MARKER = "네이버"

# CLAUDE.md 기준 — 클립보드 HTML 붙여넣기(이미지까지 같이 들어가는) 리치 에디터는
# 네이버 블로그·티스토리뿐. 그 외 전 플랫폼은 rich_paste를 갖지 않아야 한다.
RICH_PASTE_PLATFORMS = {"네이버 블로그", "티스토리"}

# CLAUDE.md 433번대 절 "장기/증상 이름 걱정형도 약하다"에서 실제로 문제였던 정확한
# 문구 원문: "콩팥 건강 걱정되는 분들 주목!", "혈관 건강 걱정되는 분들 주목!" —
# 공통 부분인 "걱정되는 분들 주목"이 남아있으면 장기/증상명+걱정형 훅으로 되돌아간
# 것이므로 실패시킨다.
WEAK_HOOK_PHRASE = "걱정되는 분들 주목"


def _discover_topics() -> list[str]:
    """data/*/ 밑 실제 topic 디렉터리를 매번 다시 스캔한다(하드코딩 금지)."""
    if not DATA_DIR.exists():
        return []
    return sorted(p.name for p in DATA_DIR.iterdir() if p.is_dir())


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
        is_naver = NAVER_NAME_MARKER in name
        has_flag = p.get("network") == "naver"
        if is_naver and not has_flag:
            problems.append(f"{name}: 네이버 플랫폼인데 network=naver 없음")
        if not is_naver and "network" in p:
            problems.append(f"{name}: 네이버가 아닌데 network 플래그 존재({p.get('network')!r})")
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
# ---------------------------------------------------------------------------

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
    conflicts = {kw: topics for kw, topics in usage.items() if len(set(topics)) > 1}
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
        # "health-shorts / <topic>" 형태로 지금 쓰는 topic과 정확히 일치하면 문제 없음.
        owning_topics = set(topics)
        matches_current_topic = any(
            f"health-shorts / {t}" in registered_project for t in owning_topics
        )
        if not matches_current_topic:
            conflicts.append(
                f"'{keyword}'는 레지스트리에 '{registered_project}' 소속으로 이미 등록돼 "
                f"있는데, 지금 data에서는 {sorted(owning_topics)}가 같은 키워드를 씀"
            )

    assert not conflicts, "; ".join(conflicts)
