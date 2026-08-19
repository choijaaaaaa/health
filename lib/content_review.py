# 콘텐츠 QA — 구조적/기계적 검사만 담당(제목 잘림·CTA 문구·글자수 등). WHY
# LLM 판단형 검사(논리 오류·과장·번역 여부 등)가 없는지(2026-08-15, "제미나이
# 호출은 일러스트 생성에만 써야하는거야. 다른 어떤것도 호출하면 안되었었는데"):
# 이 파일은 원래 Gemini API로 논리/과장/번역독립성까지 자동 판단했었는데,
# Gemini는 일러스트 생성(`lib/gemini_illust.py`)에만 쓰기로 확정되면서
# 전부 제거했다. **판단형 검사(문장이 맥락상 말이 되는지, 과장인지, 번역인지)는
# 이제 작성한 세션/에이전트가 직접 비판적으로 재검토해서 판단할 것** — 외부
# API를 대신 부르지 않는다. 이 파일에 남은 건 패턴 매칭만으로 가능한 기계적
# 검사(제목 글자수, 마지막 줄이 잘린 문장처럼 보이는지, CTA 문구 블랙리스트 등)뿐.
#
# 사용법:
#   python3 -m lib.content_review <topic> [lang]  — topic 하나만 기계적 검사
#     (lang 생략 시 한국어)
#   python3 -m lib.content_review --all            — data/ 밑 모든 topic 배치 검사(한국어 전용)
#   python3 -m lib.content_review --hook-pattern <topic>  — 제목 쓰기 전에 먼저,
#     12종 훅 패턴 중 이번 topic이 뭔지 확인(결정론적 시드, API 호출 없음)
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# WHY 지역 소싱 기준 별도 추가(2026-08-03): 한국 콘텐츠는 원래 한국에서 흔히 구할 수
# 있는 재료로 리서치하지만, 다른 언어권은 그 지역 문서로 독립 리서치해도 초안을
# 쓰는 과정에서 그 나라에 없거나 생소한 재료가 슬쩍 들어갈 위험이 있다 — 이건
# 사람이 한국어로만 검수해서는 절대 못 잡는 문제라 작성 세션이 직접 의식적으로
# 확인해야 한다(예전엔 LLM 리뷰가 자동으로 잡아줬지만 지금은 API 호출 자체를
# 안 쓰므로, 아래 체크리스트를 세션이 스스로 점검하는 용도로 남겨둔다).
MANUAL_REVIEW_CHECKLIST = """작성/수정한 세션이 TTS·발행 전 직접 눈으로 확인할 것
(예전엔 이 항목들을 Gemini API로 자동 판단했으나 지금은 세션이 직접 판단):
1. 논리적으로 말이 안 되거나 앞뒤가 안 맞는 문장은 없는가
2. 문법은 멀쩡하지만 맥락상 김빠지거나 성의없어 보이는 대체/팁 제안은 없는가
   (예: "맥주 대신 무알코올 맥주로 바꿔보세요"처럼 동어반복적인 경우)
3. 과장되거나 근거 없어 보이는 의학적 주장은 없는가
4. 앞 문장과 모순되는 내용은 없는가
5. 원인 설명이 구체적 수치·기전 근거 없이 두루뭉술하지 않은가
6. (비한국어 topic만) 해결책 재료·식품이 이 언어권/지역에서 실제로 흔히
   구할 수 있는 것인가(그 지역에 없거나 생소한 재료를 대안으로 제시하지
   않았는가)
7. (blog_seo만) 번역투/직역투 표현은 없는가, 그 언어권 광고/표시규제상
   위험한 확정적 효능 주장은 없는가(data/global_research_rules.md "표현
   주의" 절 참고), 제목이 핵심 검색 키워드로 시작하는가, 출처 없이 소수점
   단위까지 정밀한 수치를 인용하지 않았는가
8. (다국어 topic만) 언어 간 제목/훅이 사실상 번역인지, 그 언어권 독자에게
   맞춘 진짜 다른 각도로 다시 쓰여졌는지(번역 금지 원칙, CLAUDE.md "글로벌
   확장" 절)"""


def _topic_dir(topic: str, lang: str = "kor") -> Path:
    """WHY(2026-08-04 버그 수정): 예전엔 data/<topic>/narration.txt(단일 언어
    구조)만 봤다 — 글로벌 확장 이후 전 topic이 data/<topic>/<lang>/ 중첩
    구조로 바뀌었다. lang="kor"이면 ko/, 다른 언어는 GLOBAL_LANG_LABELS_FALLBACK을
    코드→이름의 역방향으로 찾아 그 코드 폴더를 본다. 중첩 폴더가 없으면(예전
    단일 언어 구조 topic 대비) topic 폴더 자체로 폴백한다."""
    base = ROOT / "data" / topic
    nested = base / _lang_code(lang)
    return nested if nested.exists() else base


def _lang_code(lang: str) -> str:
    """lang(예: "kor", "영어", "es")를 폴더 코드(예: "ko", "en", "es")로 정규화한다."""
    if lang == "kor":
        return "ko"
    return next((k for k, v in GLOBAL_LANG_LABELS_FALLBACK.items() if v == lang), lang)


# WHY(2026-08-08, "야 전반적으로 썸네일 글 이상하게 나오는 현상... 짤려서
# 만들어지는애들이 많아"): lib/card_news.py/lib/rebuild_video.py가 spec["title"]의
# 마지막 줄을 "주제명 라벨"로 간주해 자동으로 떼고 나머지만 표지·영상 오프닝
# 훅으로 쓴다(예: ["혈당 관리에 어려움이 있는", "분들 주목!", "돼지감자차 이야기"]
# → 라벨만 "돼지감자차 이야기"). 이 관례를 모르고 title을 그냥 훅 문장 하나를
# 여러 줄로 나눠서만 쓴 topic이 많았다(전체 스캔 결과 52개 조합) — 마지막 줄
# "자체"가 이어지는 문장 조각처럼 보이는 어미/격조사로 끝나는지(블랙리스트)로
# 판정한다. WHY 화이트리스트(훅이 문장부호로 끝나야 함) 대신 블랙리스트인지:
# 처음엔 "훅이 ?!로 안 끝나면 의심"으로 짰다가 "예전보다 키가 줄고 허리가 자꾸
# 굽고 있다면, 이유가 있어요"처럼 문장부호 없이 정상 종결되는 흔한 한국어 평서형
# (~요)을 대량 오탐(118개, 실제로는 52개만 진짜)했다 — "마지막 줄이 조사/어미로
# 안 끝났으면 괜찮다"는 쪽이 훨씬 보수적이라 오탐이 적다.
_KO_CONTINUATION_ENDINGS = ("면", "고", "며", "서", "데", "지만")
_JA_CONTINUATION_ENDINGS = ("で", "に", "と", "も", "が", "を", "は", "の", "から", "ので")


def check_title_truncation(topic: str, lang: str = "kor") -> list[dict]:
    """spec["title"](list)의 마지막 줄이 독립 라벨이 아니라 훅 문장이 이어지다
    잘린 조각처럼 보이면 경고한다 — 최종 판단은 사람이 하되, 놓치기 쉬운 신호를
    자동으로 표시만 한다."""
    spec_path = _topic_dir(topic, lang) / "card_news_spec.json"
    if not spec_path.exists():
        return []
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    title = spec.get("title")
    if not isinstance(title, list) or len(title) < 2:
        return []
    last = title[-1].strip()
    if not last:
        return []
    lang_code = "ko" if lang == "kor" else lang
    if lang_code == "ko":
        suspect = last.endswith(_KO_CONTINUATION_ENDINGS)
    elif lang_code == "ja":
        suspect = last.endswith(_JA_CONTINUATION_ENDINGS)
    elif lang_code in ("en", "es", "pt", "ru"):
        # WHY 소문자 시작(2026-08-08): 진짜 독립 라벨은 명사구라 보통 대문자로
        # 시작한다(예: "3 Foods Hurting Your Circulation") — 소문자로 시작하면
        # 바로 앞 줄에서 이어지는 문장 조각일 확률이 높다.
        suspect = last[0].islower()
    else:
        suspect = False
    if not suspect:
        return []
    hook = " ".join(title[:-1]).strip()
    return [{
        "quote": " / ".join(title),
        "issue": (
            f'title 배열의 마지막 줄("{last}")을 라벨로 간주해 표지·영상 훅에서 뗐더니'
            f' "{hook}"만 남습니다 — 마지막 줄이 진짜 독립된 주제 라벨(예: "돼지감자차'
            f' 이야기", "3 Foods Hurting Your Circulation")인지, 아니면 훅 문장이 이어지다'
            f' 잘린 조각인지 확인하세요. 후자라면 훅을 완결된 문장/질문으로 마무리하고'
            f' 별도로 짧은 독립 라벨을 마지막 줄에 추가해야 합니다.'
        ),
        "severity": "high",
    }]


GENERIC_CTA_CLOSING_PHRASES = (
    "저장부터 하세요", "저장하세요", "저장해두세요",
    "주목하세요", "주목!",
    "확인하세요", "확인해보세요", "지금 확인하세요",
    "놓치지 마세요",
)

BLOG_TITLE_MIN_LENGTH = 25
BLOG_TITLE_MAX_LENGTH = 50


def check_title_closing(topic: str, lang: str = "kor") -> list[dict]:
    """title 배열 마지막 줄·블로그 제목의 "-" 뒤쪽이 "저장부터 하세요"류 의미
    없는 CTA 문구인지 검사한다(2026-08-10, "저장부터 하세요 이딴건 너무
    구닥다리식 의미도 없는 문구" — 사용자 지적). CLAUDE.md "콘텐츠 톤" 절
    참고 — 마지막 라벨은 해결책을 미리보기하는 명사구여야 한다."""
    issues = []

    def _is_generic_cta(text: str) -> bool:
        stripped = text.strip()
        return any(stripped == p or stripped.startswith(p) for p in GENERIC_CTA_CLOSING_PHRASES)

    spec_path = _topic_dir(topic, lang) / "card_news_spec.json"
    if spec_path.exists():
        title = json.loads(spec_path.read_text(encoding="utf-8")).get("title")
        if isinstance(title, list) and len(title) >= 2 and _is_generic_cta(title[-1]):
            issues.append({
                "quote": title[-1],
                "issue": f'card_news_spec.json title 마지막 줄("{title[-1]}")이 의미 없는 CTA 문구입니다 — 무엇에 대한 해결책인지 드러나는 명사구로 바꾸세요(예: "OO 줄이는 습관 3가지").',
                "severity": "medium",
            })

    caption_path = _topic_dir(topic, lang) / "platform_captions.json"
    if caption_path.exists():
        blog_title = json.loads(caption_path.read_text(encoding="utf-8")).get("title", "")
        tail = blog_title.rsplit(" - ", 1)[-1] if " - " in blog_title else blog_title
        if _is_generic_cta(tail):
            issues.append({
                "quote": blog_title,
                "issue": f'블로그 제목("{blog_title}")의 마지막 라벨이 의미 없는 CTA 문구입니다 — 무엇에 대한 해결책인지 드러나는 명사구로 바꾸세요.',
                "severity": "medium",
            })

    return issues


def check_blog_title_length(topic: str, lang: str = "kor") -> list[dict]:
    """블로그 제목("platform_captions.json"의 "title" 필드)이 25~50자인지
    검사한다(2026-08-10 최초 25~40자 확정 → 2026-08-12 실측 위반율 67%로
    너무 빡빡하다는 판단에 25~50자로 완화). 네이버 블로그·티스토리가 없는
    topic(글로벌 등)은 대상 아님."""
    caption_path = _topic_dir(topic, lang) / "platform_captions.json"
    if not caption_path.exists():
        return []
    spec = json.loads(caption_path.read_text(encoding="utf-8"))
    has_blog = any(p.get("name") in ("네이버 블로그", "티스토리") for p in spec.get("platforms", []))
    if not has_blog:
        return []
    title = spec.get("title", "")
    length = len(title)
    if BLOG_TITLE_MIN_LENGTH <= length <= BLOG_TITLE_MAX_LENGTH:
        return []
    return [{
        "quote": title,
        "issue": f'블로그 제목이 {length}자입니다 — {BLOG_TITLE_MIN_LENGTH}~{BLOG_TITLE_MAX_LENGTH}자 사이로 맞추세요.',
        "severity": "medium",
    }]


def review_topic(topic: str, lang: str = "kor") -> list[dict]:
    """기계적(비-API) 검사만 수행한다 — 논리/과장/번역독립성 판단은 파일
    상단 MANUAL_REVIEW_CHECKLIST를 세션이 직접 확인할 것."""
    return (
        check_title_truncation(topic, lang)
        + check_title_closing(topic, lang)
        + check_blog_title_length(topic, lang)
    )


# WHY 여기 별도로 두는지: lib/dashboard.py의 GLOBAL_LANG_LABELS와 같은 매핑이지만,
# content_review.py가 dashboard.py를 import하면 없는 의존성이 생기므로 표시용
# 한글 라벨만 이 파일 안에 최소한으로 복제해둔다 — 안 알려진 코드는 코드
# 그대로 표시(예: "es")해도 판단 자체엔 지장 없음.
GLOBAL_LANG_LABELS_FALLBACK = {
    "en": "영어", "ja": "일본어", "zh-TW": "대만어", "es": "스페인어",
    "pt": "포르투갈어", "fr": "프랑스어", "de": "독일어", "ru": "러시아어",
    "vi": "베트남어", "ar": "아랍어", "bn": "벵골어", "tr": "터키어",
    "th": "태국어", "id": "인도네시아어", "hi": "힌디어",
    "it": "이탈리아어", "nl": "네덜란드어", "sv": "스웨덴어",
}


def review_all() -> dict[str, list[dict]]:
    """data/ 밑 모든 topic을 순회하며 기계적 검사만 수행(한국어만, --all은
    문서상 한국어 전용) — 기존 topic 전수 감사용(일회성 실행)."""
    results: dict[str, list[dict]] = {}
    topic_dirs = sorted(
        d for d in (ROOT / "data").iterdir()
        if d.is_dir() and ((d / "ko" / "narration.txt").exists() or (d / "narration.txt").exists())
    )
    for d in topic_dirs:
        topic = d.name
        issues = review_topic(topic)
        if issues:
            results[topic] = issues
            print(f"\n[{topic}]")
            for issue in issues:
                print(f"  - \"{issue.get('quote', '')}\" — {issue.get('issue', '')}")
        else:
            print(f"[{topic}] 문제 없음")
    print(f"\n총 {len(topic_dirs)}개 topic 중 {len(results)}개에서 문제 발견")
    print(f"\n⚠️ 위 결과는 기계적 검사만입니다. 논리/과장/번역독립성은 아래 체크리스트를 직접 확인하세요:\n{MANUAL_REVIEW_CHECKLIST}")
    return results


# WHY 훅 패턴을 topic 시드로 강제 선택하는지(2026-08-10, "매번 난수 돌리면
# 되는거아닐까" — 실측 확인 결과 57개 topic 중 34개(60%)가 "~라면 이 N가지부터
# 확인해봐"류 한 가지 틀로 수렴, CLAUDE_ARCHIVE.md의 12종 로테이션 규칙이 문서에만
# 있고 실제로 거의 안 지켜지고 있었음): 매번 세션이 "직전 몇 개와 다른 걸 의식적으로
# 고르라"는 지침에만 의존하면 편한 패턴으로 계속 회귀한다 — `select_format`과 동일한
# 원칙(topic 문자열만으로 결정론적 시드, 전역 상태 없음, 재현 가능)으로 12개 중
# 하나를 강제로 골라주면 사람이 의식적으로 신경 쓸 필요가 없어진다.
HOOK_PATTERNS = [
    ("호출형", '"~있다면 주목!" — 예: "손발이 자주 저리거나 차갑고 잘 붓는다면 주목!"'),
    ("질문형", '"~이신가요?" — 예: "자꾸 속이 더부룩하고 신물이 올라오시나요?"'),
    ("원인 예고형", '"~고 있다면, 이유가 있어요" — 예: "자도 자도 피곤하고 있다면, 이유가 있어요"'),
    ("경고/중단 유도형", '"~라면 이제 그만" / "~하고 계셨다면 잠깐" — 예: "자기 전 이 습관, 하고 계셨다면 잠깐"'),
    ("저장 유도형", '"~라면 저장부터 하세요" — 예: "이 증상 있다면 저장부터 하세요"'),
    ("반전형", '"~그거, 사실 [의외의 원인] 때문이에요" — 예: "자꾸 붓는 얼굴, 사실 이 음식 때문일 수 있어요"'),
    ("체크리스트형", '"아래 중 하나라도 해당되면" — 예: "손발 저림·부종·피로감, 하나라도 해당되면"'),
    ("긴급/시급성형", '"~라면 지금 확인하세요" — 예: "요즘 부쩍 붓는다면 지금 확인하세요"'),
    ("혼잣말/공감형", '"나만 그런가 싶었다면" — 예: "요즘 유독 피곤한 게 나만 그런가 싶었다면"'),
    ("비교/대조형", '"다른 게 아니라 ~ 때문일 수 있어요" — 예: "나이 탓이 아니라 이 음식 때문일 수 있어요"'),
    ("직접 화법(대화체) 질문형", '"혹시 ~하지 않나요?" — 예: "혹시 자고 일어나도 개운하지 않나요?"'),
    ("숫자/통계 제시형", '"[N명 중 1명]이 겪는다는 ~, 혹시 나도?" — 예: "성인 3명 중 1명이 겪는다는 이 증상, 혹시 나도?"(수치는 실제 리서치로 뒷받침된 것만)'),
]


def select_hook_pattern(topic: str) -> tuple[str, str]:
    """select_format()과 동일한 시드 공식으로 topic당 훅 패턴 하나를 결정론적으로
    고른다. (이름, 설명) 튜플 반환 — 내용 기준(핵심 키워드로 시작 → 구체적 걱정
    포인트로 연결)은 패턴과 무관하게 그대로 유지, 바뀌는 건 문장 어미/형태뿐."""
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(topic))
    return HOOK_PATTERNS[seed_val % len(HOOK_PATTERNS)]


# WHY 블로그 제목 아키타입도 topic-seeded인지(2026-08-13, CLAUDE.md "블로그 SEO
# 서브트랙" 절): 영상 훅과 같은 topic·언어라도 블로그 제목은 다른 문패턴을 써야
# 하는데(제목/카드뉴스 표지 문구와 겹치지 않게), select_hook_pattern과 똑같은
# 문제(세션이 매번 편한 패턴으로 회귀)가 생길 수 있어 동일한 결정론적 시드
# 원칙을 재사용한다 — 시드 문자열에 "blog"를 더해 같은 topic이라도 hook과
# 다른 시드값이 나오게 한다.
BLOG_TITLE_ARCHETYPES = [
    ("질문형", '"~이신가요?"/"~때문일까요?" 형태로 독자에게 직접 묻는 제목'),
    ("숫자리스트형", '"OO를 부르는 N가지 습관" 처럼 개수를 명시하는 제목'),
    ("원인지목형", '"~의 진짜 원인은 OO" 처럼 원인을 직접 지목하는 제목'),
    ("통념반박형", '"~은 OO 때문이 아니다" 처럼 흔한 오해를 반박하는 제목'),
    ("비교형", '"OO가 아니라 XX 때문" 처럼 두 대상을 대조하는 제목'),
]


def select_blog_title_archetype(topic: str, lang: str) -> tuple[str, str]:
    """blog_seo title 아키타입을 (topic, lang, "blog") 시드로 결정론적으로
    고른다 — select_hook_pattern과 동일 공식, 시드 문자열만 다르다."""
    seed_str = f"{topic}|{lang}|blog"
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(seed_str))
    return BLOG_TITLE_ARCHETYPES[seed_val % len(BLOG_TITLE_ARCHETYPES)]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--hook-pattern":
        if len(sys.argv) > 2:
            name, desc = select_hook_pattern(sys.argv[2])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --hook-pattern <topic>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--blog-title-archetype":
        if len(sys.argv) > 3:
            name, desc = select_blog_title_archetype(sys.argv[2], sys.argv[3])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --blog-title-archetype <topic> <lang>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--all":
        review_all()
    elif len(sys.argv) > 1:
        lang_arg = sys.argv[2] if len(sys.argv) > 2 else "kor"
        found = review_topic(sys.argv[1], lang_arg)
        if found:
            for issue in found:
                print(f"- \"{issue.get('quote', '')}\" — {issue.get('issue', '')}")
        else:
            print("문제 없음(기계적 검사만) — 아래 체크리스트는 직접 확인하세요:")
        print(f"\n{MANUAL_REVIEW_CHECKLIST}")
    else:
        print("사용법: python3 -m lib.content_review <topic> [lang] 또는 --all 또는 --hook-pattern <topic>")
