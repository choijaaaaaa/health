# 콘텐츠 QA — narration.txt/card_news_spec.json의 문장이 맥락상 말이 되는지 LLM으로
# 리뷰한다. WHY(2026-08-03, "이렇게 문맥에 맞지 않는 이상한 말들 얼마나 많겠어? ...
# 시험하는 방법론에 대해 고민해야해"): 해시태그 누락·헷지 문장 같은 규칙 기반 검사로는
# "문법은 멀쩡한데 내용이 김빠지는" 문제(예: "맥주 대신 무알코올 맥주로 바꿔보세요"처럼
# 동어반복적인 대체 제안)를 못 잡는다 — 이건 패턴 매칭이 아니라 "이 문장이 맥락상
# 말이 되는가"를 판단해야 하는 문제라 LLM 리뷰가 필요하다.
#
# WHY lang 파라미터(2026-08-03, 글로벌 확장 대비 — "내가 한국인이다보니 문맥이랑
# 그런것들 스스로 검증이 안되잖아? ... 자동화? ... 너 스스로 검증하는 시스템"):
# 사용자는 한국어 화자라 영어·스페인어 등 다른 언어 콘텐츠는 직접 검수할 수 없다 —
# 대신 이 리뷰는 LLM이 하는 거라 언어와 무관하게 똑같이 돌릴 수 있다. lang="kor"
# (기본값)이면 기존 동작 그대로, 다른 언어를 주면 그 언어 원어민 편집자 기준으로
# 검토하되 issue 설명은 항상 한국어로 반환해서(quote는 원문 그대로) 한국어 화자인
# 사용자가 결과를 읽을 수 있게 한다. 지역 콘텐츠 특유의 검사 항목(해결책 재료가 그
# 지역에서 실제로 흔한지)도 이때만 추가된다 — 한국 콘텐츠는 애초에 한국 소싱
# 기준이라 해당 없음.
#
# 사용법:
#   python3 -m lib.content_review <topic> [lang]  — topic 하나만 리뷰(lang 생략 시 한국어)
#   python3 -m lib.content_review --all            — data/ 밑 모든 topic 배치 리뷰(한국어 전용)
#   python3 -m lib.content_review --lang-check <base_topic>  — 언어별 훅/제목이 진짜
#     독립 리서치인지(번역 아닌지) 검사(아래 check_language_independence 참고)
#   python3 -m lib.content_review --lang-check --all         — data/ 밑 다국어 topic 전체 검사
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
# WHY gemini-3.6-flash(2026-08-05): "latest" 별칭(gemini-flash-latest)이 이 API 키에서
# 400 Bad Request(INVALID_ARGUMENT)로 막혀 모든 topic의 content_review가 실패하는 걸
# 실측 확인(장_1/ru 작업 중 발견). 대체 후보로 먼저 gemini-3.1-flash-lite를 썼지만,
# 같은 프롬프트·같은 텍스트를 gemini-3.5-flash/gemini-3.6-flash와 나란히 비교했더니
# lite 모델만 criteria에 없는 근거(예: "전통 음식이라 향신료 제안이 부자연스럽다")로
# 같은 문장을 반려→통과→반려를 반복하는 비결정적 판정을 보였다 — flash-lite가 QA
# 게이트로 쓰기엔 신뢰도가 부족하다고 판단해 더 안정적인 판정을 준 3.6으로 교체.
MODEL = "gemini-3.6-flash"

BASE_CRITERIA = """1. 논리적으로 말이 안 되거나 앞뒤가 안 맞는 문장
2. 문법은 멀쩡하지만 맥락상 김빠지거나 성의없어 보이는 대체/팁 제안
   (예: "맥주 대신 무알코올 맥주로 바꿔보세요"처럼 동어반복적이거나 너무
   뻔해서 실질적 정보가 없는 경우)
3. 과장되거나 근거 없어 보이는 의학적 주장
4. 앞 문장과 모순되는 내용
5. 원인 설명이 구체적 수치·기전 근거 없이 두루뭉술한 경우(예: "혈당을 올려서
   좋지 않은 환경을 만들어요"처럼 왜/어떻게인지 막연한 문장 — "인슐린 저항성을
   높여서", "염증 반응을 유발해서"처럼 최소한 어떤 생리적 경로인지는 짚어줘야 함.
   모든 문장에 통계 수치가 있어야 한다는 뜻은 아니고, "그냥 안 좋다"는 식으로
   기전 설명 자체가 빠진 경우만 지적할 것)"""

# WHY 지역 소싱 기준 별도 추가(2026-08-03): 한국 콘텐츠는 원래 한국에서 흔히 구할 수
# 있는 재료로 리서치하지만, 다른 언어권은 그 지역 문서로 독립 리서치해도 LLM이 초안을
# 쓰는 과정에서 그 나라에 없거나 생소한 재료가 슬쩍 들어갈 위험이 있다 — 이건 사람이
# 한국어로만 검수해서는 절대 못 잡는 문제라 LLM 리뷰에 필수로 넣는다.
REGIONAL_CRITERION = """6. 언급된 해결책 재료·식품이 이 언어권/지역에서 실제로 흔히 구할 수 있는지
   의심스러운 경우(그 지역에 없거나 매우 생소한 재료를 아무 설명 없이 대안으로
   제시하는 경우)"""

REVIEW_PROMPT = """당신은 {lang_desc} 건강 정보 숏폼 콘텐츠를 검수하는 깐깐한
{lang_desc} 원어민 편집자입니다. 아래는 한 topic의 나레이션 대본과 카드뉴스
텍스트입니다({lang_desc}로 작성됨). 다음 기준으로 문제 있는 문장만 찾아주세요:

{criteria}

문제가 없으면 빈 배열 []만 반환하세요. 문제가 있으면 아래 JSON 배열 형식
으로만 답하세요(설명 문장이나 코드블록 표시 없이 JSON만) — quote는 원문
({lang_desc}) 그대로, issue 설명은 한국어 화자인 검수자를 위해 반드시
한국어로 쓸 것:
[{{"quote": "문제 문장 원문 그대로", "issue": "무엇이 문제인지 한국어 한 줄 설명"}}]

--- 나레이션 ---
{narration}

--- 카드뉴스 텍스트 ---
{card_text}
"""


def _build_prompt(lang: str, narration: str, card_text: str) -> str:
    if lang == "kor":
        lang_desc = "한국어"
        criteria = BASE_CRITERIA
    else:
        lang_desc = lang
        criteria = BASE_CRITERIA + "\n" + REGIONAL_CRITERION
    return REVIEW_PROMPT.format(lang_desc=lang_desc, criteria=criteria, narration=narration, card_text=card_text)


def _headers() -> dict:
    return {"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"}


def _topic_dir(topic: str, lang: str = "kor") -> Path:
    """WHY(2026-08-04 버그 수정): review_topic/_card_news_text/review_all이 전부
    data/<topic>/narration.txt(예전 단일 언어 구조)만 보고 있었다 — 2026-08-03
    글로벌 확장으로 전 topic이 data/<topic>/<lang>/ 중첩 구조로 바뀐 뒤에도 이
    함수들은 안 고쳐진 채로 남아있었다. 그 결과 narration_path.exists()가 항상
    False가 되고 review_topic()이 "narration도 card_text도 없음"으로 판단해
    빈 리스트(= "문제 없음")를 그냥 반환하고 있었다 — 에러 없이 조용히 아무
    리뷰도 안 한 것(실제로 목_1/허리_1/갱년기_1 등에서 "문제 없음"으로 나왔던
    결과가 전부 이 버그로 인한 거짓 통과였음을 실측 확인). lang="kor"이면 ko/,
    다른 언어는 GLOBAL_LANG_LABELS_FALLBACK을 코드→이름의 역방향으로 찾아 그
    코드 폴더를 본다. 중첩 폴더가 없으면(가정: 예전 단일 언어 구조 topic 대비)
    topic 폴더 자체로 폴백한다."""
    base = ROOT / "data" / topic
    if lang == "kor":
        code = "ko"
    else:
        code = next((k for k, v in GLOBAL_LANG_LABELS_FALLBACK.items() if v == lang), lang)
    nested = base / code
    return nested if nested.exists() else base


def _card_news_text(topic: str, lang: str = "kor") -> str:
    """WHY items[].name/body + closing만 뽑는지: card_news_spec.json엔 char_file
    (일러스트 파일명)·cover_scrim_color 같은 텍스트가 아닌 값도 섞여 있어서, 스키마
    (위 "카드뉴스 스펙" 절 참고: items[{{name, char_file, body}}], closing{{headline,
    tip, cta}})를 알고 정확히 그 필드만 골라야 리뷰 프롬프트에 노이즈가 안 낀다."""
    spec_path = _topic_dir(topic, lang) / "card_news_spec.json"
    if not spec_path.exists():
        return ""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    lines: list[str] = []
    for item in spec.get("items", []):
        lines.append(item.get("name", ""))
        lines.extend(item.get("body", []))
    closing = spec.get("closing", {})
    for headline in closing.get("headline", []):
        lines.extend(headline if isinstance(headline, list) else [headline])
    lines.extend(closing.get("tip", []))
    if closing.get("cta"):
        lines.append(closing["cta"])
    return "\n".join(line for line in lines if line)


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


# WHY 소급 적용 안 함(2026-08-10): 위 check_title_truncation()과 마찬가지로 새
# topic 작성 시점에만 통과시키면 되는 규칙이라 tests/test_content_rules.py(매
# 실행마다 data/ 전체를 재스캔하는 회귀 테스트)에는 안 넣는다 — 거기 넣으면
# 이 규칙 도입 이전에 쓰인 기존 topic 수십 개가 전부 실패해서 "소급 수정 안
# 함" 원칙과 충돌한다. check_title_truncation()처럼 review_topic() 경유로만
# 새 topic에 적용되게 한다.
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
    너무 빡빡하다는 판단에 25~50자로 완화, "25~40이 너무 빡세긴 한듯. 25~50으로
    가자" — 사용자 확정). 네이버 블로그·티스토리가 없는 topic(글로벌 등)은 대상 아님."""
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
    title_issues = (
        check_title_truncation(topic, lang)
        + check_title_closing(topic, lang)
        + check_blog_title_length(topic, lang)
    )
    narration_path = _topic_dir(topic, lang) / "narration.txt"
    narration = narration_path.read_text(encoding="utf-8") if narration_path.exists() else ""
    card_text = _card_news_text(topic, lang)
    if not narration and not card_text:
        return title_issues

    prompt = _build_prompt(lang, narration, card_text)
    # WHY 재시도(2026-08-03 버그 수정): --all로 전체 topic을 순회하다가 Gemini
    # 503(일시적 서버 과부하) 한 번에 스크립트 전체가 죽어서 뒤 topic들이 하나도
    # 리뷰가 안 된 채 끝난 적이 있다 — 5xx는 일시적일 확률이 높으니 지수 백오프로
    # 최대 3번 재시도하고, 그래도 안 되면 그 topic만 건너뛴다(전체를 죽이지 않음).
    last_error: requests.exceptions.HTTPError | None = None
    resp = None
    for attempt in range(3):
        resp = requests.post(
            f"{BASE_URL}/models/{MODEL}:generateContent",
            headers=_headers(),
            json={"contents": [{"parts": [{"text": prompt}]}]},
        )
        if resp.status_code < 500:
            break
        last_error = requests.exceptions.HTTPError(f"{resp.status_code} 서버 오류", response=resp)
        time.sleep(2 ** attempt)
    else:
        print(f"[content_review] ⚠️ {topic}: 서버 오류로 3회 재시도 후 실패 — 건너뜀 ({last_error})")
        return title_issues
    resp.raise_for_status()
    data = resp.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    # WHY 코드블록 벗기기: 지시했는데도 가끔 ```json ... ``` 로 감싸서 올 때가 있어서
    # (Gemini 응답 관성) json.loads 전에 벗겨낸다.
    text = re.sub(r"^```(?:json)?\n?|\n?```$", "", text.strip())
    try:
        issues = json.loads(text)
    except json.JSONDecodeError:
        print(f"[content_review] ⚠️ {topic}: 응답 파싱 실패 — {text[:200]}")
        return title_issues
    return title_issues + (issues if isinstance(issues, list) else [])


# WHY 별도 함수(2026-08-03, "그게 어쨌든 한국이랑 글로벌의 유튜브 숏츠 영상 제목이
# 다르게들어가고있다는거지? ... 독립적으로 되어있지 않을 떄 각각의 세션이 판단해서
# 제목을 바꾸도록 유도해야할거같아. 저품질이 큰 이슈라서"): 위 review_topic()은 한
# 언어 콘텐츠 "안"의 논리·과장 문제만 본다 — 언어 "간" 비교(같은 topic의 ko 제목과
# 다른 언어 제목이 사실상 번역인지)는 완전히 다른 질문이라 별도 함수로 둔다. 실제로
# 감사해보니 topic마다 결과가 갈렸다: 가슴쓰림_1은 en(식후 타이밍)·ja(술자리 후)로
# 진짜 다른 각도였지만, 관절_1·눈_1은 거의 1:1 직역이었다 — "번역 금지, 언어권마다
# 독립적으로 리서치"(CLAUDE.md "글로벌 확장 준비" 절) 원칙이 실제로는 안 지켜지는
# topic이 있다는 뜻이고, 유튜브의 "반복적 콘텐츠"(repetitious content) 정책상 이건
# 수익화 심사에 실제로 불리한 저품질 신호다.
LANG_INDEPENDENCE_PROMPT = """당신은 다국어 콘텐츠의 현지화 품질을 감사하는
편집자입니다. 아래는 같은 주제를 다루는 건강 정보 숏폼의 한국어 원문 제목/훅과,
{lang_label} 버전의 제목/훅입니다.

한국어 원문:
{ko_text}

{lang_label} 버전:
{other_text}

{lang_label} 버전이 한국어 원문을 거의 그대로 번역한 것인지, 아니면 그 언어권
독자에게 맞춰 진짜 다른 각도(다른 상황·다른 예시·다른 프레이밍)로 다시 쓰여진
것인지 판단하세요. 문장 구조·예시·강조점이 한국어 원문과 거의 1:1로 대응되면
"번역"으로 판단합니다(단어 선택이 달라도 구조와 예시가 같으면 번역으로 봄).

아래 JSON 형식으로만 답하세요(설명 문장이나 코드블록 표시 없이):
{{"is_translation": true 또는 false, "reason": "판단 근거 한국어로 한 줄"}}
"""


def check_language_independence(base_topic: str) -> dict[str, dict]:
    """base_topic(예: "가슴쓰림_1")의 ko 대비 각 비-ko 언어 title이 진짜 독립
    리서치인지(번역이 아닌지) LLM으로 판단한다. 반환값은
    {lang: {"is_translation": bool, "reason": str}} — is_translation=True인
    항목이 있으면 그 언어의 title/narration을 다시 써야 한다(자동 수정 안 함,
    content_review.py의 다른 검사들과 같은 원칙 — 판단은 사람/세션 몫)."""
    topic_dir = ROOT / "data" / base_topic
    ko_captions = topic_dir / "ko" / "platform_captions.json"
    if not ko_captions.exists():
        return {}
    ko_title = json.loads(ko_captions.read_text(encoding="utf-8")).get("title", "")

    results: dict[str, dict] = {}
    lang_dirs = sorted(p.name for p in topic_dir.iterdir() if p.is_dir() and p.name != "ko")
    for lang in lang_dirs:
        captions_path = topic_dir / lang / "platform_captions.json"
        if not captions_path.exists():
            continue
        other_title = json.loads(captions_path.read_text(encoding="utf-8")).get("title", "")
        if not other_title:
            continue
        prompt = LANG_INDEPENDENCE_PROMPT.format(
            lang_label=GLOBAL_LANG_LABELS_FALLBACK.get(lang, lang),
            ko_text=ko_title,
            other_text=other_title,
        )
        resp = None
        last_error: requests.exceptions.HTTPError | None = None
        for attempt in range(3):
            resp = requests.post(
                f"{BASE_URL}/models/{MODEL}:generateContent",
                headers=_headers(),
                json={"contents": [{"parts": [{"text": prompt}]}]},
            )
            if resp.status_code < 500:
                break
            last_error = requests.exceptions.HTTPError(f"{resp.status_code} 서버 오류", response=resp)
            time.sleep(2 ** attempt)
        else:
            print(f"[content_review] ⚠️ {base_topic}/{lang}: 서버 오류로 3회 재시도 후 실패 — 건너뜀 ({last_error})")
            continue
        resp.raise_for_status()
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        text = re.sub(r"^```(?:json)?\n?|\n?```$", "", text.strip())
        try:
            verdict = json.loads(text)
        except json.JSONDecodeError:
            print(f"[content_review] ⚠️ {base_topic}/{lang}: 응답 파싱 실패 — {text[:200]}")
            continue
        results[lang] = verdict
    return results


# WHY 여기 별도로 두는지: lib/dashboard.py의 GLOBAL_LANG_LABELS와 같은 매핑이지만,
# content_review.py가 dashboard.py를 import하면 없는 의존성(순환 import 위험은
# 없지만 이 파일은 원래 dashboard.py를 몰라도 되는 독립 모듈이었음)이 생기므로
# 표시용 한글 라벨만 이 파일 안에 최소한으로 복제해둔다 — 안 알려진 코드는
# 코드 그대로 표시(예: "es")해도 판단 자체엔 지장 없음.
GLOBAL_LANG_LABELS_FALLBACK = {
    "en": "영어", "ja": "일본어", "zh-TW": "대만어", "es": "스페인어",
    "pt": "포르투갈어", "fr": "프랑스어", "de": "독일어", "ru": "러시아어",
    "vi": "베트남어", "ar": "아랍어", "bn": "벵골어", "tr": "터키어",
    "th": "태국어", "id": "인도네시아어", "hi": "힌디어",
}


def check_language_independence_all() -> dict[str, dict[str, dict]]:
    """data/ 밑 모든 다국어 topic(ko/ 하위 폴더가 있는 topic)을 순회하며
    check_language_independence()를 돌린다 — 일회성 전수 감사용."""
    results: dict[str, dict[str, dict]] = {}
    topic_dirs = sorted(
        d.name for d in (ROOT / "data").iterdir()
        if d.is_dir() and (d / "ko" / "platform_captions.json").exists()
    )
    for base_topic in topic_dirs:
        verdicts = check_language_independence(base_topic)
        if not verdicts:
            continue
        results[base_topic] = verdicts
        for lang, v in verdicts.items():
            mark = "⚠️ 번역 의심" if v.get("is_translation") else "✅ 독립적"
            print(f"[{base_topic}/{lang}] {mark} — {v.get('reason', '')}")
    return results


def review_all() -> dict[str, list[dict]]:
    """data/ 밑 모든 topic을 순회하며 리뷰(한국어만, --all은 문서상 한국어 전용) —
    기존 topic 전수 감사용(일회성 실행). WHY (d / "ko" / "narration.txt")도
    같이 보는지(2026-08-04 버그 수정): 글로벌 확장 이후 전 topic이 <topic>/ko/
    중첩 구조라 (d / "narration.txt")만 보면 전부 걸러져서 리뷰 대상이 0개가
    되는 버그가 있었다 — 중첩/구식 단일 언어 구조 둘 다 topic으로 인정한다."""
    results: dict[str, list[dict]] = {}
    topic_dirs = sorted(
        d for d in (ROOT / "data").iterdir()
        if d.is_dir() and ((d / "ko" / "narration.txt").exists() or (d / "narration.txt").exists())
    )
    for d in topic_dirs:
        topic = d.name
        try:
            issues = review_topic(topic)
        except requests.exceptions.RequestException as e:
            print(f"[content_review] ⚠️ {topic}: 요청 실패로 건너뜀 — {e}")
            continue
        if issues:
            results[topic] = issues
            print(f"\n[{topic}]")
            for issue in issues:
                print(f"  - \"{issue.get('quote', '')}\" — {issue.get('issue', '')}")
        else:
            print(f"[{topic}] 문제 없음")
    print(f"\n총 {len(topic_dirs)}개 topic 중 {len(results)}개에서 문제 발견")
    return results


# WHY 훅 패턴을 topic 시드로 강제 선택하는지(2026-08-10, "매번 난수 돌리면
# 되는거아닐까" — 실측 확인 결과 57개 topic 중 34개(60%)가 "~라면 이 N가지부터
# 확인해봐"류 한 가지 틀로 수렴, CLAUDE_ARCHIVE.md의 12종 로테이션 규칙이 문서에만
# 있고 실제로 거의 안 지켜지고 있었음): 매번 세션이 "직전 몇 개와 다른 걸 의식적으로
# 고르라"는 지침에만 의존하면 편한 패턴으로 계속 회귀한다 — `select_format`과 동일한
# 원칙(topic 문자열만으로 결정론적 시드, 전역 상태 없음, 재현 가능)으로 12개 중
# 하나를 강제로 골라주면 사람이 의식적으로 신경 쓸 필요가 없어진다. 진짜 난수가
# 아니라 시드 기반인 이유도 select_format과 동일 — 같은 topic을 나중에 다시 봐도
# "이건 왜 이 패턴이었지" 재현 가능해야 하고, 별도 상태 파일(직전 N개 기록 등) 없이
# 그 자체로 이미 넓게 퍼진다(진짜 난수도 이 문제는 못 막음 — 오히려 시드가 없으면
# 우연히 같은 패턴이 연달아 나올 수 있는데 시드는 topic 이름이 다르면 사실상 다른
# 결과가 나온다).
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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--hook-pattern":
        if len(sys.argv) > 2:
            name, desc = select_hook_pattern(sys.argv[2])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --hook-pattern <topic>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--lang-check":
        if len(sys.argv) > 2 and sys.argv[2] == "--all":
            check_language_independence_all()
        elif len(sys.argv) > 2:
            for lang, v in check_language_independence(sys.argv[2]).items():
                mark = "⚠️ 번역 의심" if v.get("is_translation") else "✅ 독립적"
                print(f"[{lang}] {mark} — {v.get('reason', '')}")
        else:
            print("사용법: python3 -m lib.content_review --lang-check <base_topic> 또는 --all")
    elif len(sys.argv) > 1 and sys.argv[1] == "--all":
        review_all()
    elif len(sys.argv) > 1:
        lang_arg = sys.argv[2] if len(sys.argv) > 2 else "kor"
        found = review_topic(sys.argv[1], lang_arg)
        if found:
            for issue in found:
                print(f"- \"{issue.get('quote', '')}\" — {issue.get('issue', '')}")
        else:
            print("문제 없음")
    else:
        print("사용법: python3 -m lib.content_review <topic> [lang] 또는 --all 또는 --lang-check ...")
