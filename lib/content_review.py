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
#     10종 훅 패턴 중 이번 topic이 뭔지 확인(결정론적 시드, API 호출 없음)
#   python3 -m lib.content_review --title-archetype <topic> <lang>    — blog_seo
#     제목 쓰기 전에 먼저(topic+lang 시드, 아래 "blog_seo 전용 다양화 장치" 참고)
#   python3 -m lib.content_review --closing-archetype <topic> <lang>  — blog_seo
#   python3 -m lib.content_review --card-structure <topic>            — 카드 짜임
#   python3 -m lib.content_review --connectives <topic>               — 네이버 접속어
#     클로징 문단 쓰기 전에 먼저. select_section_header_archetype()은 CLI 없이
#     함수를 직접 import해서 쓸 것(section 인자를 받으므로 CLI 매핑 생략)
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from lib import tracks

ROOT = Path(__file__).resolve().parent.parent


# WHY 트랙 경로를 이 모듈에서 한 번 더 감싸는지: 폴더 규칙 자체는 lib/tracks.py 한 곳에서
# 정하지만, 이 모듈의 ROOT는 테스트가 tmp_path로 갈아끼운다(tests/test_content_review.py) —
# tracks.ROOT를 그대로 쓰면 갈아낀 루트를 무시하고 저장소 실데이터를 읽는다.
def _data_dir(topic: str) -> Path:
    return ROOT / tracks.data_dir(topic).relative_to(tracks.ROOT)


def _output_dir(topic: str) -> Path:
    return ROOT / tracks.output_dir(topic).relative_to(tracks.ROOT)


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
7-1. (blog_seo만) ⚠️ 인용한 수치에 **그 수치가 성립하는 조건**이 함께
   적혀 있는가 — 비교 대상·하위집단·기간. 2026-08-28 실측 사례: AREDS2
   시험 결과를 "루테인·제아잔틴이 AMD 진행 위험을 약 26% 낮췄다"로 썼는데,
   실제 18%는 *베타카로틴 포함 제형 대비*이고 25%는 *식이 섭취가 낮았던
   하위집단*에서만 나온 수치였다 — 조건을 떼어내면 일반적인 효과처럼
   읽히고, 독자는 그걸 보고 보충제를 산다. 조건을 못 쓰겠으면 그 수치를
   빼는 쪽이 맞다.
7-2. (blog_seo만) 관찰연구 결과를 인과로 단정하지 않았는가 — 코호트·
   단면연구는 "~와 연관됐다", 무작위 개입시험만 "~를 낮췄다"로 쓴다.
8. (다국어 topic만) 언어 간 제목/훅이 사실상 번역인지, 그 언어권 독자에게
   맞춘 진짜 다른 각도로 다시 쓰여졌는지(번역 금지 원칙, CLAUDE.md "글로벌
   확장" 절)"""


def _topic_dir(topic: str, lang: str = "kor") -> Path:
    """WHY(2026-08-04 버그 수정): 예전엔 data/<topic>/narration.txt(단일 언어
    구조)만 봤다 — 글로벌 확장 이후 전 topic이 data/<topic>/<lang>/ 중첩
    구조로 바뀌었다. lang="kor"이면 ko/, 다른 언어는 GLOBAL_LANG_LABELS_FALLBACK을
    코드→이름의 역방향으로 찾아 그 코드 폴더를 본다. 중첩 폴더가 없으면(예전
    단일 언어 구조 topic 대비) topic 폴더 자체로 폴백한다."""
    base = _data_dir(topic)
    nested = base / _lang_code(lang)
    return nested if nested.exists() else base


def _caption_dirs(topic: str, lang: str = "kor") -> list[Path]:
    """platform_captions.json을 검사할 디렉터리 전부.

    WHY 하나가 아닌지(2026-08-30 실측): 한국어 topic은 캡션 파일이 두 곳에
    따로 있고 나가는 곳도 다르다 — flat(data/<topic>/)은 네이버 블로그,
    ko/ 폴더는 vernhaven blog_seo. _topic_dir()은 ko/가 있으면 무조건 그쪽만
    보므로, 두 파일이 모두 있는 topic에서 네이버 캡션은 어떤 검사도 받지
    않고 지나갔다. 실제로 네이버 캡션 16개를 새로 쓰는 동안 서브에이전트
    셋이 각각 "content_review가 내 파일을 안 본다"고 따로 보고했다.
    """
    base = _data_dir(topic)
    dirs = [_topic_dir(topic, lang)]
    if lang == "kor" and base not in dirs and (base / "platform_captions.json").exists():
        dirs.append(base)
    return dirs


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
        # ⚠️ startswith만 보면 "계속된다면 지금 확인하세요"처럼 **앞에 말이 붙은** 줄이 빠져나간다
        # (2026-09-23 실측, 코_10). 폐기 문구는 줄 어디에 있든 그 줄 전체를 다시 써야 하므로 포함으로 본다.
        stripped = text.strip()
        return any(p in stripped for p in GENERIC_CTA_CLOSING_PHRASES)

    spec_path = _topic_dir(topic, lang) / "card_news_spec.json"
    if spec_path.exists():
        title = json.loads(spec_path.read_text(encoding="utf-8")).get("title")
        if isinstance(title, list) and len(title) >= 2:
            if _is_generic_cta(title[-1]):
                issues.append({
                    "quote": title[-1],
                    "issue": f'card_news_spec.json title 마지막 줄("{title[-1]}")이 의미 없는 CTA 문구입니다 — 무엇에 대한 해결책인지 드러나는 명사구로 바꾸세요(예: "OO 줄이는 습관 3가지").',
                    "severity": "medium",
                })
            # ⚠️ 마지막 줄만 보면 안 된다(2026-09-23 실측): "…며칠째 계속된다면 / 저장부터 하세요 /
            # 후유증 막는 대처법 3가지"처럼 **중간 줄**에 박힌 폐기 CTA는 116개 topic에서 린터를
            # 통과한 채 살아남아 있었다. 그 줄은 자리만 차지하고 검색어가 들어갈 공간을 뺏는다.
            for line in title[:-1]:
                if _is_generic_cta(line):
                    issues.append({
                        "quote": line,
                        "issue": f'title 중간 줄("{line}")이 폐기된 CTA 문구입니다 — 그 줄을 지우고 '
                                 "앞 훅이 문장으로 끝나도록 다시 쓰세요.",
                        "severity": "medium",
                    })

    for caption_dir in _caption_dirs(topic, lang):
        caption_path = caption_dir / "platform_captions.json"
        if not caption_path.exists():
            continue
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
    issues: list[dict] = []
    for caption_dir in _caption_dirs(topic, lang):
        caption_path = caption_dir / "platform_captions.json"
        if not caption_path.exists():
            continue
        spec = json.loads(caption_path.read_text(encoding="utf-8"))
        has_blog = any(p.get("name") in ("네이버 블로그", "티스토리") for p in spec.get("platforms", []))
        if not has_blog:
            continue
        title = spec.get("title", "")
        length = len(title)
        if BLOG_TITLE_MIN_LENGTH <= length <= BLOG_TITLE_MAX_LENGTH:
            continue
        issues.append({
            "quote": title,
            "issue": f'블로그 제목이 {length}자입니다 — {BLOG_TITLE_MIN_LENGTH}~{BLOG_TITLE_MAX_LENGTH}자 사이로 맞추세요.',
            "severity": "medium",
        })
    return issues




def _blog_seo_entry(topic: str, lang: str = "kor") -> dict | None:
    """platform_captions.json의 blog_seo 항목. 없으면 None(= 블로그 트랙이
    아닌 topic이라 검사 대상이 아님)."""
    caption_path = _topic_dir(topic, lang) / "platform_captions.json"
    if not caption_path.exists():
        return None
    try:
        spec = json.loads(caption_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for entry in spec.get("platforms", []):
        if entry.get("platform") == "blog_seo":
            return entry
    return None

# WHY 수치에 출처가 붙었는지 기계로 보는지(2026-08-28): 건강 콘텐츠는 YMYL이라
# 구글 품질 평가에서 가장 엄격한 잣대가 적용되는데, 미발행분 246건을 훑어보니
# 본문에 퍼센트·용량 수치가 613곳 나오는 반면 기관·연구를 함께 밝힌 글은
# 일부였다. 사람이 매번 세는 대신 "수치는 있는데 근처에 출처가 없는" 자리를
# 뽑아준다 — 그 수치가 틀렸다는 뜻이 아니라 확인이 필요한 자리라는 뜻이다.
# 조건(비교군·하위집단) 누락은 기계로 못 잡으니 위 체크리스트 7-1로 넘긴다.
_CLAIM_NUM = re.compile(
    r"\d[\d.,]*\s?(?:%|percent|Prozent|por ciento|per cento|procent|パーセント|퍼센트"
    r"|mg\b|g\b|ng/mL|mmHg|kcal)"
)
# 출처로 인정하는 신호 — 기관명, 저널명, "~에 따르면" 계열, 연구 언급
_CLAIM_SRC = re.compile(
    # 기관·저널 고유명
    r"(Harvard|BMJ|Lancet|JAMA|NEJM|Cochrane|NIH|NIDDK|NIEHS|NHLBI|NCI|CDC|WHO|IARC|FDA|EFSA|NHS"
    r"|Mayo|AREDS|NHANES|AHA|American Heart|NTP|Linus Pauling|DGE|RKI|RIVM|Voedingscentrum"
    r"|Livsmedelsverket|Folkhälsomyndigheten|ANSES|Santé publique|HAS|ISS|CREA|AESAN|LARN"
    r"|Ministerio|Ministère|Ministero|厚生労働省|질병관리청|식약처"
    # 기관 일반명 — Institute/University/학회 등
    r"|Institut\w*|Istituto|Universit\w*|College|School of|Società|Society|Association"
    r"|Academy|Foundation|학회|연구소|学会|研究所"
    # 인용 도입 표현
    r"|according to|laut |selon |secondo |según |volgens |enligt |によると|に基づ|에 따르면"
    # 연구·근거 언급
    r"|stud(y|ies)|trial|research|analysis|meta-analys|review|figures"
    r"|Studie|Forschung|Analyse|étude|recherche|studio|ricerca|estudio|investigación"
    r"|onderzoek|studien|forskning|研究|データ|연구|데이터|분석"
    # 지침·권고
    r"|guideline|recommend|raccomanda|recomienda|aanbevel|rekommend|Leitlinie|Empfehlung"
    r"|recommandation|linea guida|directriz|richtlijn|riktlinje|지침|권고|ガイドライン)",
    re.I,
)


def check_unsourced_claims(topic: str, lang: str = "kor") -> list[dict]:
    """blog_seo 본문에서 출처 신호 없이 등장하는 수치를 뽑는다.
    같은 문장 또는 바로 앞 문장에 출처 신호가 있으면 통과로 본다."""
    entry = _blog_seo_entry(topic, lang)
    if not entry:
        return []
    body = re.sub(r"<[^>]+>", " ", entry.get("body_html") or "")
    body = re.sub(r"\s+", " ", body).strip()
    sentences = [s.strip() for s in re.split(r"(?<=[.!?\u3002])\s+", body) if s.strip()]
    issues: list[dict] = []
    for i, s in enumerate(sentences):
        if not _CLAIM_NUM.search(s):
            continue
        window = s if i == 0 else sentences[i - 1] + " " + s
        if _CLAIM_SRC.search(window):
            continue
        issues.append({
            "quote": s[:160],
            "issue": "수치가 있는데 이 문장·앞 문장에 출처 신호가 없음 — 근거를 밝히거나 수치를 빼세요",
        })
    return issues


def check_opening_hook(topic: str, lang: str = "kor") -> list[dict]:
    """나레이션 첫 문장이 조건절 자격심사("~라면 주목하세요"류)인지, 그리고
    0~5초 안에 정보가 도착할 길이인지 검사한다(2026-09-17 신설).

    WHY 이 검사가 필요한지: 훅 문형 규칙은 문서에만 있을 땐 지켜지지 않았다 —
    실측 115편 중 71편이 조건절 훅이었고 최장 11.9초짜리도 있었다. 기계가 잡지
    않으면 다음 topic에서 또 들어온다."""
    base = _data_dir(topic)
    path = next((p for p in (base / lang / "narration.txt", base / "ko" / "narration.txt",
                             base / "narration.txt") if p.exists()), None)
    if path is None:
        return []
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    first = re.split(r"(?<=[.!?])\s+", text.replace("\n", " ").strip())[0].strip()
    if not first:
        return []

    issues: list[dict] = []
    if BANNED_HOOK_TAIL.search(first):
        issues.append({
            "quote": first[:120],
            "issue": ("훅이 저장·주목 유도로 끝납니다(\"~라면 저장하세요/주목하세요\"류) — "
                      "시청자를 거르기만 하고 정보를 안 줘서 0~5초를 버립니다. "
                      "HOOK_PATTERNS의 정보 제시형으로 다시 쓰세요."),
            "severity": "high",
        })

    # 반투명 인체 포맷(data/<topic>/xray.json)은 도입부를 Flow 클립 두 개(행위 4초 + 부위 4초 = 8초)로 채운다.
    # 칠판으로 넘어가기 전까지의 나레이션 = 첫 두 문장이 8초를 넘으면 클립을 늘려야 하고, 늘린 도입부는
    # "너무 긴 편"이었다(2026-09-19 사용자, 소화_9 시험본 13.6초 → "대충 8초 정도로 끊어야").
    if (_data_dir(topic) / "xray.json").exists():
        sents = re.split(r"(?<=[.!?])\s+", text.replace("\n", " ").strip())
        opening = re.sub(r"\s+", "", sents[0])
        if len(opening) > XRAY_OPENING_MAX_CHARS:
            issues.append({
                "quote": sents[0][:140],
                "issue": (f"반투명 인체 포맷 도입부(훅 문장)가 공백 제외 {len(opening)}자 — 약 "
                          f"{len(opening) / SPEECH_CHARS_PER_SEC:.1f}초입니다(목표 {XRAY_OPENING_MAX_CHARS}자 ≈ 6초). "
                          f"도입부 Flow 구간이 늘어집니다."),
                "severity": "high",
            })

    dense = re.sub(r"\s+", "", first)
    if len(dense) > OPENING_MAX_CHARS:
        issues.append({
            "quote": first[:120],
            "issue": (f"첫 문장이 공백 제외 {len(dense)}자 — 약 {len(dense) / SPEECH_CHARS_PER_SEC:.1f}초입니다"
                      f"(권장 {OPENING_MAX_CHARS}자/약 6초 이내). 상황·증상만 남기고 곧바로 첫 항목으로 넘어가세요."),
            "severity": "medium",
        })
    return issues


# ══════════════════════ 네이버 블로그 원고 품질(2026-09-17 신설) ══════════════════════
# WHY: 사용자 지적 "네이버블로그도그렇고 클립도 그렇고 내용이 좀 애매해 그렇게까지
# 사람들한테 도움이 되지 않는 느낌이야". 전수 실측으로 원인 두 가지를 특정했다.
#  ① 385편 중 199편(52%)이 수치를 쓰면서 그 수치의 출처 기관을 본문에 안 밝힌다 —
#     "30% 낮아진다는 연구 결과가 있어요"는 독자 입장에서 검증 불가능한 카더라다.
#     CLAUDE.md "수치를 쓸 땐 어느 기관인지 문장 안에 적는다"는 규칙이 blog_seo에만
#     기계 검사(check_unsourced_claims)로 걸려 있었고 네이버 원고는 무방비였다.
#  ② 152편 중 62편이 나레이션 문장을 40% 이상 그대로 재사용한다(최고 87%). 네이버
#     원고는 1000자 이상인데 60~75초짜리 나레이션은 350~410자뿐이라, 재사용하면
#     나머지를 같은 말 반복으로 채우게 된다 — 그게 "애매하다"의 실체다.
# 네이버 원고는 나레이션의 확장판이 아니라 **별도 장르**여야 한다.
# WHY 시간 단위(분·시간·일·주)를 빼는지: "20분 이상 천천히 드세요"는 검증할 주장이
# 아니라 실행 지침이라, 넣으면 경고의 대부분이 이쪽으로 채워져 진짜 문제가 묻힌다.
# 독자가 출처 없이는 믿을 수 없는 것 — 효과크기·유병률·용량·측정값만 대상으로 둔다.
_NAVER_NUM = re.compile(
    r"\d[\d.,]*\s?(?:%|퍼센트|배\b|명 중|mg|ml|kcal|mmHg)"
)
# 무기명 귀속 — 출처를 밝히는 척하지만 누구인지 안 밝히는 표현
_NAVER_VAGUE_SRC = re.compile(
    r"(연구\s?결과가\s?있|연구가\s?있|한\s?연구에|여러\s?연구|알려져\s?있|보고가\s?있|조사\s?결과가\s?있)"
)
# ⚠️ 약칭만 넣으면 **정식 명칭을 쓴 문장이 오탐으로 잡힌다**(2026-09-23 머리_14 실측:
# "식품의약품안전처 통합식품안전정보망"이 출처 없음으로 걸렸다). 기관을 제대로 밝힌 쪽이
# 벌을 받는 셈이라, 자주 쓰는 정식 명칭을 같이 둔다.
_NAVER_REAL_SRC = re.compile(
    # ⚠️ 2026-09-23 머리_14(콜라겐) 실측: "한국소비자원 시험에서 …"가 출처 없음으로 걸렸다 —
    # 끝이 '원'이라 `[가-힣]{2,}연구원`에도 안 걸린다. 위 WHY의 "정식 명칭을 쓴 쪽이 벌을 받는" 사례가
    # 그대로 반복돼 공공기관 이름을 직접 추가한다(소비자원 보도자료는 이 채널이 자주 쓰는 1차 자료다).
    r"(대학교|대학병원|서울대|연세|삼성서울|아산|질병관리청|식약처|식품의약품안전처|"
    r"한국소비자원|소비자원|한국소비자연맹|"
    r"보건복지부|국민건강|건강보험심사평가원|국민건강보험공단|농촌진흥청|기상청|"
    # ⚠️ 2026-09-24 육아 트랙 실측: "대한의사협회지"(학술지)와 "중앙응급의료센터"(응급처치 소관
    # 기관)가 둘 다 출처 없음으로 걸렸다 — 학회·병원만 알고 협회·센터·의료원을 몰랐다.
    r"WHO|세계보건기구|학회|협회|센터|의료원|연구소|재단|NHS|CDC|FDA|메이요|하버드|논문|저널|"
    r"[가-힣]{2,}병원|[가-힣]{2,}연구원|[A-Z][A-Za-z]{2,})"
)
NARRATION_REUSE_MAX = 40.0      # 나레이션 문장 재사용 상한(%)


def _shingles(text: str, n: int = 8) -> set[str]:
    flat = re.sub(r"\d\d\s·[^\n]*", "", text)          # "01 · 소제목" 이미지 마커 제거
    flat = re.sub(r"[\s#·\-—]", "", flat)
    return {flat[i:i + n] for i in range(len(flat) - n + 1)}


def _naver_caption(topic: str) -> str | None:
    for d in _caption_dirs(topic, "kor"):
        path = d / "platform_captions.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for pl in data.get("platforms", []):
            if pl.get("name") == "네이버 블로그":
                return pl.get("caption") or ""
    return None


def check_naver_blog_quality(topic: str, lang: str = "kor") -> list[dict]:
    """네이버 블로그 원고가 (a) 수치의 출처를 밝히는지 (b) 나레이션 재탕이 아닌지
    검사한다. 한국어 전용 — 다른 언어엔 네이버 원고 자체가 없다."""
    if lang not in ("kor", "ko"):
        return []
    caption = _naver_caption(topic)
    if not caption:
        return []

    issues: list[dict] = []
    body = re.sub(r"\d\d\s·[^\n]*", " ", caption)
    for sent in (x.strip() for x in re.split(r"(?<=[.!?])\s+", body) if x.strip()):
        if _NAVER_NUM.search(sent) and not _NAVER_REAL_SRC.search(sent):
            issues.append({
                "quote": sent[:140],
                "issue": ("수치가 있는데 어느 기관·연구인지 이 문장에 없습니다 — "
                          "기관명을 문장 안에 쓰거나, 못 쓰겠으면 그 수치를 빼세요."),
                "severity": "high",
            })
        elif _NAVER_VAGUE_SRC.search(sent) and not _NAVER_REAL_SRC.search(sent):
            issues.append({
                "quote": sent[:140],
                "issue": ('"연구 결과가 있어요"식 무기명 귀속입니다 — 출처를 밝히는 것처럼 '
                          "보이지만 독자가 확인할 수 없습니다. 기관명을 밝히세요."),
                "severity": "high",
            })

    base = _data_dir(topic)
    nar_path = next((p for p in (base / "narration.txt", base / "ko" / "narration.txt")
                     if p.exists()), None)
    if nar_path:
        ns = _shingles(nar_path.read_text(encoding="utf-8"))
        if ns:
            reuse = len(ns & _shingles(caption)) / len(ns) * 100
            if reuse >= NARRATION_REUSE_MAX:
                issues.append({
                    "quote": f"나레이션 문장 재사용률 {reuse:.0f}%",
                    "issue": (f"네이버 원고가 나레이션의 확장판입니다(상한 {NARRATION_REUSE_MAX:.0f}%). "
                              "60~75초 나레이션엔 350~410자뿐이라 1000자를 채우려면 같은 말을 "
                              "반복하게 됩니다 — 분량·조건·예외처럼 영상에 못 담은 내용으로 "
                              "독립된 글을 쓰세요."),
                    "severity": "medium",
                })
    return issues


# 2026-09-20 사용자 "사람들에게 크게 도움이 되지 않는 느낌… 놀랄 만큼 도움될 내용이 많이 들어가면 좋겠다":
# 기존 원고는 "커피·진통제·짠 음식이 위에 나쁘다"처럼 다 아는 말만 하고, 실행할 수 있는 숫자도 병원에 가야
# 할 신호도 없었다. 아래 네 가지를 새 원고(card_news_spec에 "content_v2": true)에 강제한다.
# 6.13자/초 기준 약 380~521자.
#
# WHY 상한이 80이 아니라 85인지(2026-09-24): 원래 "62~80초"는 6.7자/초라는 틀린 상수로 환산한 값이라
# 실제로는 한 번도 지켜진 적이 없다 — 발행본 67편 중 48%가 80초를 넘고, 사용자가 유일하게 품질을 인정한
# 본보기 소화_14조차 82.3초다. 숫자를 지킬 수 없는 채로 두면 경고가 상시 켜져 있어 아무도 안 본다.
# 실제로 만들어져 통과한 길이에 맞춰 85초로 둔다.
V2_MIN_SECONDS, V2_MAX_SECONDS = 62, 85
V2_MIN_NUMBERS = 3
# "명·세·살"은 건강 콘텐츠에서 가장 흔한 단위인데 빠져 있었다(2026-09-23) — "인구 천 명당 17.2명",
# "만 50세부터"처럼 실행에 직결되는 수치가 통째로 안 잡혀 원고를 멀쩡히 쓰고도 미달로 걸렸다.
_NUM_WITH_UNIT = re.compile(
    r"\d[\d,.]*\s?[만억]?\s?(?:mg|g|kg|ml|L|밀리그램|그램|칼로리|kcal|도|℃|%|퍼센트|배|분|시간|일|주|개월|년|회|번|잔|컵|알|정|포|명|세|살|리터|밀리리터|티스푼|큰술|작은술|단계|층|줄)")
_MYTH_PATTERNS = [
    re.compile(r"(좋다고|낫는다고|도움이 된다고|괜찮다고|효과가 있다고)\s*(들으|알려|생각|믿)"),
    re.compile(r"(알려져 ?있지만|생각하기 쉽지만|흔히 ?아는 것과 달리|사실은 ?반대)"),
    # "떠올리지만 / 떠올리는데 / 여기기 쉽지만 / 아는 사람이 많은데" — 실제로 자주 쓰는 반박 형태인데
    # 위 셋에 안 걸려 멀쩡한 원고가 실패했다(2026-09-24 대사_22 실측).
    re.compile(r"(떠올리|여기|착각하|믿|넘기|생각하)(지만|는데|기 쉽지만)"),
    re.compile(r"(반대(쪽|로)|~?가 아니라)"),
    re.compile(r"(분|사람|경우)이 많은데"),
    re.compile(r"오히려"),
]
_DOCTOR_PATTERNS = [re.compile(r"(병원|진료|전문의|응급실).{0,20}(가|받|상담|방문)"),
                    re.compile(r"(이런 ?증상|이럴 ?때|다음 중 하나라도)")]


def _narration_seconds(topic: str, dense_chars: int) -> tuple[float, bool]:
    """(초, 실측인지). mp3가 있으면 직접 재고, 아직 TTS 전이면 글자수로 추정한다.

    WHY 실측을 우선하는지(2026-09-24): 발화 속도는 topic마다 5.83~6.40자/초로 흔들려서(문장 길이·숫자
    읽기·문장 사이 쉼의 양이 달라서다) 상수 하나로 환산하면 ±4초가 그냥 난다. 순환_12는 추정 86초로
    상한을 넘었는데 실제 음성은 82.9초였다 — 멀쩡한 원고를 줄이게 만드는 종류의 오탐이다."""
    audio = _output_dir(topic) / "narration.mp3"
    if audio.exists():
        try:
            out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                  "-of", "csv=p=0", str(audio)], capture_output=True, text=True, timeout=20)
            return float(out.stdout.strip()), True
        except (ValueError, OSError, subprocess.SubprocessError):
            pass
    return dense_chars / SPEECH_CHARS_PER_SEC, False


def check_content_depth(topic: str, lang: str = "kor") -> list[dict]:
    """새 기준(content_v2) 원고가 실제로 도움이 되는 내용을 담았는지 — 숫자·통념 반박·병원 신호·분량.

    WHY 마커(card_news_spec의 "content_v2")로 거는지: 기존 434개 topic은 TTS 재생성 비용 때문에 손대지
    않기로 했다(2026-09-19). 마커가 있는 새 원고만 검사해야 옛 topic이 전부 실패로 뜨지 않는다."""
    if lang not in ("kor", "ko"):
        return []
    # ⚠️ 스펙 위치가 topic마다 다르다(check_search_keyword와 같은 사정) — flat만 보면 ko/ 폴더를 쓰는
    # topic이 content_v2 마커를 달아도 깊이 검사가 조용히 꺼진 채 "문제 없음"으로 통과한다.
    spec_path = next((p for p in (_data_dir(topic) / "ko" / "card_news_spec.json",
                                  _data_dir(topic) / "card_news_spec.json") if p.exists()), None)
    nar_path = _data_dir(topic) / "narration.txt"
    if spec_path is None or not nar_path.exists():
        return []
    try:
        if not json.loads(spec_path.read_text(encoding="utf-8")).get("content_v2"):
            return []
    except json.JSONDecodeError:
        return []
    text = nar_path.read_text(encoding="utf-8")
    dense = re.sub(r"\s", "", text)
    secs, measured = _narration_seconds(topic, len(dense))
    issues = []
    if not V2_MIN_SECONDS <= secs <= V2_MAX_SECONDS:
        issues.append({"quote": f"{len(dense)}자", "severity": "high",
                       "issue": f"나레이션이 {'실측 ' if measured else '약 '}{secs:.0f}초입니다 — "
                                f"목표 {V2_MIN_SECONDS}~{V2_MAX_SECONDS}초"
                                f"({round(V2_MIN_SECONDS * SPEECH_CHARS_PER_SEC)}~"
                                f"{round(V2_MAX_SECONDS * SPEECH_CHARS_PER_SEC)}자, 공백 제외)."})
    nums = _NUM_WITH_UNIT.findall(text)
    if len(nums) < V2_MIN_NUMBERS:
        issues.append({"quote": ", ".join(nums) or "(없음)", "severity": "high",
                       "issue": f"단위가 붙은 수치가 {len(nums)}개뿐입니다(최소 {V2_MIN_NUMBERS}개) — "
                                "'줄이세요' 대신 '하루 400mg 이하', '식후 30분'처럼 실행할 수 있게 쓰세요."})
    if not any(p.search(text) for p in _MYTH_PATTERNS):
        issues.append({"quote": text[:40], "severity": "medium",
                       "issue": "통념을 뒤집는 대목이 없습니다 — 시청자가 이미 아는 말만 하면 놀랄 게 없습니다. "
                                "'~가 좋다고 알려졌지만 오히려…' 같은 반전을 한 개는 넣으세요."})
    if not any(p.search(text) for p in _DOCTOR_PATTERNS):
        issues.append({"quote": text[-40:], "severity": "high",
                       "issue": "병원에 가야 할 신호가 없습니다 — 구체적 증상으로 한 줄 넣으세요"
                                "(예: 체중이 줄거나 검은 변을 보면 바로 진료)."})
    return issues


def check_xray_clips(topic: str, lang: str = "kor") -> list[dict]:
    """xray.json이 가리키는 클립이 실제로 있는지. 없으면 실패 — 비슷한 클립으로 대충 때우지 않는다.

    WHY(2026-09-21 사용자 "클립이 더 필요하다고 판단되면 막 연관없는거 아무거나 넣지말고 나한테 더 요청을 해"):
    라이브러리에 맞는 기전이 없을 때 남는 클립을 끼워 넣으면 화면과 나레이션이 어긋난다(그 자체가 이 채널에서
    반복된 사고다). 없으면 `data/<topic>/clip_requests.json`에 적고 사용자에게 요청한 뒤 조립을 멈춘다."""
    if lang not in ("kor", "ko"):
        return []
    path = _data_dir(topic) / "xray.json"
    if not path.exists():
        return []
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return [{"quote": "xray.json", "severity": "high", "issue": "xray.json이 깨졌습니다."}]
    lib = ROOT / "assets_library" / "xray" / "output"
    issues = []
    refs = [cfg.get("inset", {}).get("clip")] + [o.get("clip") for o in cfg.get("opening", [])]
    # ⚠️ `act`도 같이 본다 — 항목 칸은 왼쪽 행위·오른쪽 기전으로 나뉘는데 예전엔 mech만 검사해서
    # 없는 행위 클립을 적어두면 content_review는 통과하고 조립할 때서야 터졌다.
    refs += [f"assets_library/xray/output/{r[k]}.mp4"
             for r in cfg.get("timeline", []) for k in ("mech", "act") if r.get(k)]
    refs += [f"assets_library/xray/output/{a}.mp4" for a in cfg.get("_acts") or []]
    for ref in [r for r in refs if r]:
        if not (ROOT / ref).exists() and not (lib / Path(ref).name).exists():
            issues.append({"quote": ref, "severity": "high",
                           "issue": "클립이 없습니다 — 비슷한 클립으로 바꾸지 말고 "
                                    f"`data/{topic}/clip_requests.json`에 적어 사용자에게 렌더를 요청하세요."})
    req = _data_dir(topic) / "clip_requests.json"
    if req.exists():
        try:
            pending = [r for r in json.loads(req.read_text(encoding="utf-8")).get("requests", [])
                       if not (lib / f"{r.get('name')}.mp4").exists()]
        except json.JSONDecodeError:
            pending = []
        if pending:
            issues.append({"quote": ", ".join(r.get("name", "?") for r in pending), "severity": "high",
                           "issue": "아직 안 받은 클립 요청이 있습니다 — 받기 전에는 이 topic을 완료로 치지 않습니다."})
    return issues


# 항목을 여는 말 — 나레이션이 "먼저 전염이에요"처럼 항목을 선언하는 자리.
_ITEM_OPENERS = re.compile(
    r"^(?:먼저|첫\s*(?:번)?째(?:는|로)?|두\s*번째(?:는|로)?|세\s*번째(?:는|로)?|마지막(?:은|으로)?)\s+(.{1,30}?)(?:예요|이에요|입니다|이요)\.",
    re.MULTILINE)
TITLE_OVERLAP_FLOOR = 0.50   # 제목 줄 중 **가장 잘 맞는 한 줄**이 이보다 낮으면 각도가 다른 것으로 본다


def _bigrams(text: str) -> set[str]:
    """한글만 남긴 글자 2-gram. 조사·어미로 표면형이 달라져도 겹침이 잡힌다."""
    s = re.sub(r"[^가-힣]", "", text)
    return {s[i:i + 2] for i in range(len(s) - 1)}


def check_card_narration_alignment(topic: str, lang: str = "kor") -> list[dict]:
    """카드뉴스 제목·항목이 지금 나레이션과 같은 이야기를 하는지.

    WHY(2026-09-24 실측): 나레이션을 전면 재작성한 뒤 카드가 옛 각도에 남는 사고가 두 건 한꺼번에 났다 —
    고령_15는 원고를 "전염·치료시기·백신"으로 갈았는데 카드는 "담으로 오인·병원 미루기"에 머물러 **전염이
    통째로 빠졌고**, 대사_14는 items만 고치고 title이 "근육 지키고 요요 줄이는"으로 남아 구토·탈모·췌장을
    말하는 영상과 제목이 따로 놀았다. 둘 다 사람이 눈으로 훑어야만 보이는 종류라 그때까지 아무 검사도
    안 걸렸다.

    항목 누락은 확정적이라 high, 제목은 어휘 일치 휴리스틱이라 medium으로 둔다."""
    if lang not in ("kor", "ko"):
        return []
    spec_path = next((p for p in (_data_dir(topic) / "ko" / "card_news_spec.json",
                                  _data_dir(topic) / "card_news_spec.json") if p.exists()), None)
    nar_path = _data_dir(topic) / "narration.txt"
    if spec_path is None or not nar_path.exists():
        return []
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if not spec.get("content_v2"):   # 옛 topic은 검사하지 않는다(check_content_depth와 같은 사정)
        return []

    narration = nar_path.read_text(encoding="utf-8")
    spec_text = re.sub(r"\s", "", json.dumps(spec, ensure_ascii=False))
    issues = []

    # 1. 나레이션이 선언한 항목이 카드 어딘가에 있는가 — "먼저 전염이에요"의 '전염'
    for label in _ITEM_OPENERS.findall(narration):
        core = re.sub(r"\s", "", label)
        if core and core not in spec_text:
            issues.append({"quote": label, "severity": "high",
                           "issue": f"나레이션은 '{label}'을(를) 항목으로 말하는데 카드에는 없습니다 — "
                                    "원고를 고치고 card_news_spec.json을 안 따라 고친 상태입니다."})

    # 2. 제목이 통째로 다른 이야기를 하는가 — items만 고치고 제목을 옛 각도로 남긴 경우
    #
    # WHY 낱말이 아니라 **줄 단위 글자 2-gram 겹침**으로 재는지(2026-09-24 실측): 낱말로 재면 "있다면"·
    # "쓰는"·"것과" 같은 어미·조사가 전부 "나레이션에 없는 말"로 잡혀 오탐이 9건 중 9건이었다. 한국어는
    # 어미가 붙어 표면형이 달라지므로 낱말 일치는 신호가 안 된다. 또 줄 하나씩 보면 "쓰러지기 전 대처법
    # 3가지" 같은 멀쩡한 마무리 줄이 11%로 뜬다 — 마무리 줄은 원래 원고에 없는 말이다. **제목 전체에서
    # 가장 잘 맞는 한 줄**을 보면 각도가 살아있는 제목은 최소 한 줄이 크게 겹치고(60~100%), 각도가
    # 어긋난 제목만 모든 줄이 낮게 나온다(대사_14 실측 최대 23%).
    ref = _bigrams(narration) | _bigrams(json.dumps(spec.get("items", []), ensure_ascii=False))
    scored = [(len(g & ref) / len(g), line) for line in (spec.get("title") or [])
              if (g := _bigrams(line))]
    if scored:
        best, line = max(scored)
        if best < TITLE_OVERLAP_FLOOR:
            issues.append({"quote": " / ".join(l for _, l in scored), "severity": "medium",
                           "issue": f"제목이 나레이션·항목과 거의 안 겹칩니다(가장 겹치는 줄도 {best:.0%}) — "
                                    "각도를 바꾸고 제목만 옛것으로 남겨두지 않았는지 확인하세요."})
    return issues


MAX_PANEL_GAP_SEC = 8.0      # 위쪽 칸이 이보다 오래 안 바뀌면 "같은 그림에 색만" 구간이 된다

# 기관명을 문장마다 붙이면 읽는 사람은 "또 저 소리"가 된다.
_ORG_NAMES = re.compile(r"질병관리청|건강보험심사평가원|서울아산병원|서울대학교병원|식품의약품안전처|"
                        r"대한[가-힣]{2,6}학회|국제[가-힣]{2,8}학회|국립[가-힣]{2,6}원|한국소비자원")
MAX_ORG_MENTIONS = 2

# 설명 없이 던지면 못 알아듣는 말. 값은 "이 말을 풀어줬는지" 확인할 쉬운 표현이다.
_JARGON = {
    "미주신경": "신경", "사구체여과율": "신장", "크레아티닌": "노폐물", "하시모토": "면역",
    "갑상선자극호르몬": "호르몬", "베타차단제": "약", "전정": "귀", "포드맵": "당",
    "인슐린 저항성": "혈당", "사이토카인": "염증", "프로스타글란딘": "통증",
}


def check_plain_language(topic: str, lang: str = "kor") -> list[dict]:
    """기관명을 반복해 붙이지 않았는지, 전문용어를 설명 없이 던지지 않았는지.

    WHY(2026-09-24 사용자 지적): 공공데이터를 쓰기 시작한 뒤 원고에 기관명과 전문용어만 덧붙었다.
    대사_22에 질병관리청이 다섯 번 나왔고("뭐만하면 질병관리청 이지랄하네"), 순환_12는
    미주신경·사구체여과율·베타차단제가 설명 없이 박혀 있었다("전문용어 덕지덕지 붙여가지고
    이해도 안되게"). 한 항목은 **행동 → 원인 → 아이템** 세 마디면 된다."""
    if lang not in ("kor", "ko"):
        return []
    path = _data_dir(topic) / "narration.txt"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    issues = []
    # 🚨 세는 건 **수치 없이 붙은** 기관명이다. 퍼센트·기간 같은 숫자를 받치는 인용은 제 역할을
    # 하는 것이고("저하증이 항진증보다 1.8배"), 문제는 사실만 말하면 되는 자리에 이름을 덧댄 쪽이다.
    bare = [sent for sent in re.split(r"(?<=[.?!])\s+", text.strip())
            if _ORG_NAMES.search(sent) and not _NUM_WITH_UNIT.search(sent)]
    if len(bare) > MAX_ORG_MENTIONS:
        issues.append({"quote": bare[0][:40], "severity": "medium",
                       "issue": f"수치 없이 기관명만 붙인 문장이 {len(bare)}개입니다"
                                f"(권장 {MAX_ORG_MENTIONS}개 이하) — 숫자를 받치는 자리가 아니면 "
                                "사실만 말하세요."})
    for term, plain in _JARGON.items():
        if term in text and plain not in text:
            issues.append({"quote": term, "severity": "medium",
                           "issue": f"'{term}'을(를) 설명 없이 씁니다 — 쉬운 말('{plain}')로 한 번 풀거나 빼세요."})
    return issues


def check_summary_single_block(topic: str, lang: str = "kor") -> list[dict]:
    """결론 구간이 여러 행으로 쪼개져 품목 배지만 줄줄이 바뀌지 않는지.

    WHY(2026-09-24 사용자 "써머리에는 이미지는 줄줄이 나열해놓고 설명은 뒤에 몇개밖에 안 나온다"):
    결론은 "그래서 뭘 하면 되는지" 한 덩어리다. timeline을 거기서 더 쪼개면 칠판 품목만 계속
    바뀌는데 정작 말은 몇 마디뿐이라 따로 논다."""
    if lang not in ("kor", "ko"):
        return []
    path = _data_dir(topic) / "xray.json"
    if not path.exists():
        return []
    try:
        from lib.xray_timeline import resolve, summary_start
        ts = summary_start(topic)
        rows = resolve(topic) or []
    except Exception:
        return []
    if ts is None or not rows:
        return []
    inside = [r for r in rows if r["start"] >= ts - 0.05]
    if len(inside) > 1:
        return [{"quote": ", ".join(str(r["item"]) for r in inside), "severity": "medium",
                 "issue": f"결론 구간이 {len(inside)}개 행으로 쪼개져 품목이 계속 바뀝니다 — "
                          "결론은 한 덩어리로 두거나 아예 빼세요(칠판 전체 버전이 덮습니다)."}]
    return []


def check_xray_timeline_resolves(topic: str, lang: str = "kor") -> list[dict]:
    """xray.json timeline의 구절이 지금 자막에서 실제로 찾히는지.

    WHY(2026-09-24 실측): 원고를 다시 쓰면 문장이 바뀌는데 timeline의 `from` 구절은 옛 문장 그대로
    남는다. 그러면 조립이 첫 줄에서 죽는다 — 고령_15·눈_8·머리_14가 그 상태였다. 그런데
    check_xray_pacing은 resolve() 예외를 삼키고 빈 목록을 돌려줘서 **검수는 "문제 없음"으로 통과**했다.
    깨진 걸 조용히 넘기는 검사는 없는 것만 못하다."""
    if lang not in ("kor", "ko"):
        return []
    path = _data_dir(topic) / "xray.json"
    if not path.exists():
        return []
    try:
        tl = json.loads(path.read_text(encoding="utf-8")).get("timeline") or []
    except json.JSONDecodeError:
        return [{"quote": "xray.json", "severity": "high", "issue": "xray.json이 깨졌습니다."}]
    if not tl:
        return []
    try:
        from lib.xray_timeline import _cues
        text = " ".join(c[2] for c in _cues(topic))
    except (StopIteration, OSError):
        return [{"quote": topic, "severity": "high",
                 "issue": "나레이션 자막(narration.srt)이 없어 timeline을 풀 수 없습니다 — TTS를 먼저 돌리세요."}]
    missing = [r.get("from", "") for r in tl if r.get("from", "") not in text]
    if missing:
        return [{"quote": ", ".join(missing[:4]), "severity": "high",
                 "issue": f"timeline 구절 {len(missing)}개가 지금 자막에 없습니다 — 원고를 고치고 timeline을 "
                          "안 따라 고친 상태라 조립이 실패합니다."}]
    return []


MAX_SAME_MECH = 2      # 같은 기전 클립이 설명 구간에서 이보다 자주 나오면 같은 그림이 반복된다


def check_mech_variety(topic: str, lang: str = "kor") -> list[dict]:
    """한 기전 클립을 여러 구간에 돌려쓰지 않았는지.

    WHY(2026-09-24 눈_8 실측 지적 "위에 이미지 하나 박아놓고 대사만 치네"): 7구간 중 4구간이
    같은 `m_vitreous_floaters`였고, 그 클립은 색인에 **"호박색 점등이 없어 약하다"**고 적혀
    있는 것이었다. 흐릿한 같은 그림이 반복되면 영상이 아니라 정지 이미지로 읽힌다."""
    if lang not in ("kor", "ko"):
        return []
    path = _data_dir(topic) / "xray.json"
    if not path.exists():
        return []
    try:
        from lib.xray_timeline import resolve, summary_start
        rows, ts = resolve(topic) or [], summary_start(topic)
    except Exception:
        return []
    body = [r for r in rows if ts is None or r["start"] < ts - 0.05]
    if len(body) < 3:
        return []
    counts: dict[str, int] = {}
    for r in body:
        if r.get("mech"):
            counts[r["mech"]] = counts.get(r["mech"], 0) + 1
    over = {k: v for k, v in counts.items() if v > MAX_SAME_MECH}
    if not over:
        return []
    worst = max(over, key=over.get)
    return [{"quote": worst, "severity": "medium",
             "issue": f"기전 클립 '{worst}'이(가) 설명 구간 {len(body)}개 중 {over[worst]}번 나옵니다 "
                      f"(권장 {MAX_SAME_MECH}번 이하) — 같은 그림이 반복되면 정지 이미지로 보입니다. "
                      "구간마다 다른 기전을 고르거나 없으면 요청하세요."}]


def check_act_coverage(topic: str, lang: str = "kor") -> list[dict]:
    """설명 구간마다 행위 클립이 붙어 있는지.

    WHY(2026-09-24): 이 포맷의 핵심이 "왼쪽 행동 · 오른쪽 기전"인데, act를 안 적으면 기전만 크게
    나가고 검사는 조용히 통과했다. 견본으로 고른 소화_14조차 설명 구간 7개 중 act가 0개였다.
    맞는 클립이 없으면 요청하고 그 구간은 비워두되, **비어 있다는 사실은 보여야 한다.**"""
    if lang not in ("kor", "ko"):
        return []
    if not (_data_dir(topic) / "xray.json").exists():
        return []
    try:
        from lib.xray_timeline import resolve, summary_start
        rows, ts = resolve(topic) or [], summary_start(topic)
    except Exception:
        return []
    body = [r for r in rows if ts is None or r["start"] < ts - 0.05]
    if not body:
        return []
    missing = [r for r in body if not r.get("act")]
    if not missing:
        return []
    return [{"quote": ", ".join(f"{r['start']:.0f}초" for r in missing[:5]), "severity": "medium",
             "issue": f"설명 구간 {len(body)}개 중 {len(missing)}개에 행위 클립이 없습니다 — "
                      "기전만 크게 나갑니다. 맞는 클립이 없으면 clip_requests.json에 적으세요."}]


def check_xray_pacing(topic: str, lang: str = "kor") -> list[dict]:
    """도입부 컷이 문장을 자르지 않는지, 위쪽 칸이 오래 비어 있지 않은지.

    WHY(2026-09-24 비뇨기_16 실측 지적): 두 가지가 한꺼번에 드러났다.
    ① `opening_until`이 5.2초인데 통념 반박 문장은 4.64~14.40초라, 그 문장이 **0.5초만 전체 화면에
       나오고 칠판으로 넘어갔다.** 사용자 "왜 앞선 전체 영상에 잠깐 나오고 넘어가게 만드는것이며".
    ② 그 뒤 첫 항목이 20.56초에 시작해 **16초 동안 위쪽 칸에 영상이 없었다.** 부위 인셋만 맥동해서
       "6초부터 18초까지 똑같은 이미지에 색상만 들어가는 느낌"이 된다.
    둘 다 파일만 봐선 안 보이고 영상을 틀어봐야 보이는 종류라 검사로 못 박는다."""
    if lang not in ("kor", "ko"):
        return []
    path = _data_dir(topic) / "xray.json"
    if not path.exists():
        return []
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
        from lib.xray_timeline import _cues, resolve
        cues = _cues(topic)
        rows = resolve(topic) or []
    except Exception:
        return []
    if not cues:
        return []

    issues = []
    until = cfg.get("opening_until")
    if until is not None:
        # 문장 경계(자막 큐의 시작·끝)와 0.35초 안에서 맞아야 한다 — 그보다 멀면 문장을 자르는 것이다
        edges = [c[0] for c in cues] + [c[1] for c in cues]
        if min(abs(until - e) for e in edges) > 0.35:
            cut = next((c for c in cues if c[0] < until < c[1]), None)
            issues.append({"quote": f"opening_until={until}", "severity": "high",
                           "issue": f"도입부 컷이 문장 한가운데를 자릅니다"
                                    + (f" — \"{cut[2][:28]}…\"가 {cut[0]:.1f}~{cut[1]:.1f}초인데 "
                                       f"{until}초에 칠판으로 넘어갑니다. " if cut else " — ")
                                    + "문장이 끝나는 시각에 맞추세요."})

    # 🚨 도입부(전체 화면) 안에서 시작하는 구간이 있으면 칸이 도입 영상 위에 겹쳐 그려진다.
    if until is not None:
        inside = [r for r in rows if r["start"] < until - 0.05]
        if inside:
            issues.append({"quote": f"{inside[0]['start']:.1f}초", "severity": "high",
                           "issue": f"도입부가 {until}초까지인데 {len(inside)}개 구간이 그 안에서 시작합니다 — "
                                    "전체 화면 도입 영상 위에 칸이 겹쳐 그려집니다."})
    if rows:
        gap_start = until if until is not None else 0.0
        gaps = [(gap_start, rows[0]["start"])]
        gaps += [(rows[i]["end"], rows[i + 1]["start"]) for i in range(len(rows) - 1)]
        for s, e in gaps:
            if e - s > MAX_PANEL_GAP_SEC:
                issues.append({"quote": f"{s:.1f}~{e:.1f}초", "severity": "high",
                               "issue": f"위쪽 칸에 영상이 없는 구간이 {e - s:.0f}초입니다"
                                        f"(상한 {MAX_PANEL_GAP_SEC:.0f}초) — 그동안 화면이 칠판과 "
                                        "부위 인셋뿐이라 같은 그림에 색만 바뀌는 것처럼 보입니다. "
                                        "timeline에 구간을 더 나누거나 클립을 요청하세요."})
    return issues


def check_search_keyword(topic: str, lang: str = "kor") -> list[dict]:
    """검색어를 제목 맨 앞에 뒀는지 — `card_news_spec.json`의 `search_keyword` 기준.

    WHY(2026-09-23 사용자 "네이버 클립은 사람들이 검색했던 검색어 기준으로 영상을 띄워준다… 제목도
    검색어 트렌드에 맞춰 짓는 게 핵심"): "훅은 핵심 키워드로 시작" 규칙은 예전부터 있었지만 그 키워드가
    실제로 검색되는 말인지는 한 번도 안 봤다. 이제 `lib/topic_search_rank.py`가 월간 검색량으로 고른
    표현을 spec에 박아두고, 제목이 그 말로 시작하는지 여기서 검사한다.

    마커가 없는 옛 topic은 통과시킨다(content_v2와 같은 방식) — 게시 완료분을 전부 실패로 띄우지 않는다."""
    if lang not in ("kor", "ko"):
        return []
    # ⚠️ 스펙 위치가 topic마다 다르다(캡션과 같은 사정 — "한국어 캡션 파일은 topic마다 위치가 다르다" 절).
    # flat만 보면 ko/ 폴더를 쓰는 54개 topic이 검사 없이 통과한다.
    spec_path = next((p for p in (_data_dir(topic) / "ko" / "card_news_spec.json",
                                  _data_dir(topic) / "card_news_spec.json") if p.exists()), None)
    if spec_path is None:
        return []
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    kw = (spec.get("search_keyword") or "").strip()
    if not kw:
        return []
    flat_kw = re.sub(r"\s", "", kw)
    issues = []
    title = spec.get("video_title") or spec.get("title") or []
    if title and not re.sub(r"\s", "", title[0]).startswith(flat_kw):
        issues.append({"quote": title[0], "severity": "high",
                       "issue": f"제목이 검색어 '{kw}'로 시작하지 않습니다 — 클립은 검색어로 노출되므로 "
                                "이 말이 맨 앞에 와야 합니다."})
    caption = _naver_caption(topic)
    if caption:
        first = caption.strip().splitlines()[0]
        if not re.sub(r"\s", "", first).startswith(flat_kw):
            issues.append({"quote": first, "severity": "high",
                           "issue": f"네이버 캡션 첫 줄이 검색어 '{kw}'로 시작하지 않습니다."})
    return issues


def check_products_in_brandconnect(topic: str, lang: str = "kor") -> list[dict]:
    """해결책 품목(products)이 브랜드커넥트에 실제로 있는지 — 없는 품목은 링크를 달 수가 없다.

    WHY(2026-09-19 사용자 지시 "특이한 품목을 추천했는데 브랜드커넥트에 없어버리면 연동조차 할 수가 없는
    상태… 매번 그렇게 하도록"): 조사 단계에서 `python3 -m lib.brandconnect check <topic>`으로 확인한
    결과(data/<topic>/brandconnect.json) 또는 전체 카탈로그(data/_audit/brandconnect_catalog.json)를 본다.
    확인 기록이 없는 품목도 실패로 친다 — "안 돌려봤다"와 "있다"를 구분해야 검사가 빠지지 않는다."""
    if lang not in ("kor", "ko"):
        return []
    try:
        cap = next(p for p in (_data_dir(topic) / "platform_captions.json",
                               _data_dir(topic) / "ko" / "platform_captions.json") if p.exists())
        products = json.loads(cap.read_text(encoding="utf-8")).get("products") or []
    except (StopIteration, json.JSONDecodeError):
        return []
    known: dict = {}
    status: dict = {}
    cat = ROOT / "data" / "_audit" / "brandconnect_catalog.json"
    if cat.exists():
        for k, v in json.loads(cat.read_text(encoding="utf-8")).items():
            known[k] = v.get("found"); status[k] = v.get("status")
    # 표본을 사람이 보고 "본품 없음"으로 판정한 품목(일반의약품 등)은 카탈로그 status와 무관하게 없음으로 친다
    unav = ROOT / "data" / "brandconnect_unavailable.json"
    if unav.exists():
        for k in json.loads(unav.read_text(encoding="utf-8")).get("health", {}).get("없음", []):
            known[k] = False; status[k] = "없음"
    per = _data_dir(topic) / "brandconnect.json"
    if per.exists():
        known.update({k: v.get("found") for k, v in json.loads(per.read_text(encoding="utf-8"))["products"].items()})
    issues = []
    for name in products:
        if name not in known:
            issues.append({"quote": name, "severity": "high",
                           "issue": "브랜드커넥트 확인 기록 없음 — `python3 -m lib.brandconnect check "
                                    f"{topic}`을 돌려 제휴 가능 여부부터 확인하세요."})
        elif not known[name]:
            if status.get(name) == "확인필요":
                msg = ("브랜드커넥트에 비슷한 상품은 있으나 자동 선택 기준에 안 걸림 — 검색어를 실제 상품명에 가깝게 "
                       "바꾸거나(예: 무알코올→무알콜) 직접 확인하세요.")
            else:
                msg = ("브랜드커넥트에 없는 품목(추천 금지) — 해결책에서 빼거나 브랜드커넥트에 있는 품목으로 바꾸세요. "
                       "목록: data/brandconnect_unavailable.json")
            issues.append({"quote": name, "severity": "high", "issue": msg})
    for name in products:
        if any(w in name for w in WEAK_SUBSTITUTES):
            issues.append({"quote": name, "severity": "medium",
                           "issue": "원인 습관의 대체품(무알코올 맥주·전자담배·디카페인류)은 해결책으로 약하다 — "
                                    "몸에 실제로 도움이 되는 영양제·도구를 추천하세요."})
    return issues


# 2026-09-19 사용자: "술을 마시는게 좋지 않다 -> 무알코올 맥주, 담배를 피는게 좋지 않다 -> 전자담배 뭐이런식으로
# 걍 애매하게 대체제 던져주는것보단 영양제같은거 추천하는게 훨씬 효과적이다"
WEAK_SUBSTITUTES = ("무알코올", "무알콜", "논알콜", "전자담배", "금연초", "디카페인", "제로 콜라", "제로콜라", "제로음료")

def review_topic(topic: str, lang: str = "kor") -> list[dict]:
    """기계적(비-API) 검사만 수행한다 — 논리/과장/번역독립성 판단은 파일
    상단 MANUAL_REVIEW_CHECKLIST를 세션이 직접 확인할 것.

    🚨 폴더가 없으면 "문제 없음"이 아니라 실패로 답한다(2026-09-24). 검사 함수들은 파일이
    없으면 각자 빈 목록을 돌려주도록 만들어져 있어서(옛 topic 호환), 경로를 잘못 짚으면
    **한 건도 안 걸린 채 통과처럼 보인다** — 육아 트랙 원고 두 편이 실제로 그렇게 통과했다."""
    if not _data_dir(topic).is_dir():
        return [{"quote": topic, "severity": "high",
                 "issue": f"`{_data_dir(topic).relative_to(ROOT)}` 폴더가 없다 — 검사가 한 건도 안 돌았다. "
                          "topic 이름과 트랙 폴더(lib/tracks.py)를 확인하세요."}]
    return (
        check_opening_hook(topic, lang)
        + check_products_in_brandconnect(topic, lang)
        + check_naver_blog_quality(topic, lang)
        + check_title_truncation(topic, lang)
        + check_title_closing(topic, lang)
        + check_blog_title_length(topic, lang)
        + check_unsourced_claims(topic, lang)
        # ⚠️ 아래 셋은 각자 마커(content_v2 / xray.json / search_keyword)가 있는 topic만 검사한다.
        # 2026-09-23까지 앞의 둘은 정의만 돼 있고 여기 연결이 빠져 있어서, CLAUDE.md에 "자동으로 잡는다"고
        # 적혀 있는데도 review_topic을 돌리면 한 건도 안 걸렸다.
        + check_content_depth(topic, lang)
        + check_xray_clips(topic, lang)
        + check_search_keyword(topic, lang)
        + check_card_narration_alignment(topic, lang)
        + check_xray_timeline_resolves(topic, lang)
        + check_xray_pacing(topic, lang)
        + check_plain_language(topic, lang)
        + check_summary_single_block(topic, lang)
        + check_mech_variety(topic, lang)
        + check_act_coverage(topic, lang)
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
    topic_dirs = [
        d for d in tracks.iter_topic_dirs(ROOT / "data")
        if (d / "ko" / "narration.txt").exists() or (d / "narration.txt").exists()
    ]
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
# 원칙(topic 문자열만으로 결정론적 시드, 전역 상태 없음, 재현 가능)으로 10개 중
# 하나를 강제로 골라주면 사람이 의식적으로 신경 쓸 필요가 없어진다.
# 🚨 2026-09-17 전면 교체 — 조건절 훅("~라면 주목하세요"류) 금지.
# 기존 12종 중 5종(호출형·저장유도형·체크리스트형·긴급시급성형·경고중단유도형)이
# "[증상 나열]~라면 + 주목/확인/저장하세요" 문형을 **지시하고** 있었다. 그래서
# 세션이 규칙을 어긴 게 아니라 규칙대로 쓴 결과가 사용자가 금지한 문형이었다 —
# 같은 파일의 GENERIC_CTA_CLOSING_PHRASES가 "주목하세요"·"저장부터 하세요"를 이미
# 금지어로 갖고 있는데도 훅 쪽은 그대로 권하고 있어서 코드가 자기모순이었고,
# 그게 "하지 말라고 했는데 또 들어간" 실제 원인이다.
#
# 문제의 본질: 조건절 훅은 **정보를 하나도 주지 않고 자격 심사만 한다.** 실측상
# 115편 중 71편(62%)이 이 문형이고 27편은 첫 문장이 7초를 넘겼다(최장 11.9초) —
# 이탈을 가르는 0~5초를 통째로 "당신이 볼 영상인지" 확인하는 데 쓴 셈이다.
#
# 교체 기준: 첫 문장이 **그 자체로 정보를 담을 것**(원인·수치·반전·장면).
# 시청자 자격을 묻는 문형은 전부 뺐고, 남긴 질문형·공감형도 곧바로 정보가
# 이어지도록 설명에 못박았다.
HOOK_PATTERNS = [
    ("반전형", '"~그거, 사실 [의외의 원인] 때문이에요" — 예: "자꾸 붓는 얼굴, 사실 베개 높이 때문이에요"'),
    ("결론 선치형", '결론을 첫 문장에 바로 놓는다 — 예: "혈당 스파이크, 뭘 먹느냐보다 먹는 순서가 더 큽니다"'),
    ("통념 반박형", '"~라고 알고 계셨다면 그게 아니에요" — 예: "새치는 뽑으면 는다고 알고 계셨다면, 그게 아니에요"'),
    ("숫자/통계 제시형", '"[N명 중 1명]이 겪는 ~" — 예: "성인 3명 중 1명이 겪는 역류성 식도염"(수치는 실제 리서치로 뒷받침된 것만)'),
    ("효과 수치형", '같은 행동의 전후 차이를 수치로 — 예: "같은 밥이라도 순서만 바꾸면 식후 혈당 최고치가 30% 낮아집니다"'),
    ("장면 제시형", '증상이 드러나는 구체적 순간 하나를 묘사 — 예: "아침 첫 소변에 거품이 가라앉지 않고 남아 있습니다"'),
    ("비교/대조형", '"[흔한 원인]이 아니라 [진짜 원인] 때문이에요" — 예: "나이 탓이 아니라 저녁에 마신 커피 때문이에요"'),
    ("질문형", '"~이신가요?" — 짧게 묻고 **곧바로** 답을 준다. 예: "중이염, 귀가 먹먹하고 아프신가요?" → 다음 문장에서 바로 원인'),
    ("직접 화법(대화체) 질문형", '"혹시 ~하지 않나요?" — 질문형과 같이 다음 문장이 즉시 정보여야 한다'),
    ("혼잣말/공감형", '"나만 그런가 싶었다면" — 공감 한 마디로 짧게 열고 바로 원인으로. 증상을 길게 나열하지 말 것'),
]

# 훅 첫 문장 금지 문형 — 조건절 + 자격심사/CTA 꼬리. check_opening_hook()이 쓴다.
# WHY 문서가 아니라 정규식인지: 이 규칙은 2026-08-10에 이미 문서로 있었는데
# (GENERIC_CTA_CLOSING_PHRASES) 제목에만 적용돼서 나레이션 훅으로 계속 새어나왔다.
# ⚠️ 2026-09-19 정정: "~라면 확인하세요"는 금지 대상이 아니다. 사용자가 원하는 도입부가 바로
# "[상황]에서 [증상]이 나타나면 이걸 확인하세요 → 곧바로 첫 항목"이다("어떤 상황에서 어떤 현상이 나타나면
# 이런걸 확인하세요 바로 넘어가는거야"). 금지는 저장·주목 유도 꼬리만 — 처음 이 규칙을 만들 때 확인형까지
# 묶은 건 과잉이었다.
BANNED_HOOK_TAIL = re.compile(
    r"(?:다|라)면[^.!?]{0,20}?"
    r"(?:주목|저장부터|저장해|저장하세요|놓치지\s*마세요)"
)

# 첫 문장 권장 상한(공백 제외). 이 프로젝트 TTS 실측 발화속도 약 5.5자/초 기준
# 약 4초 — 0~5초 훅 구간 안에서 첫 정보가 도착하게 하려는 값이다.
# 발화 속도 실측(2026-09-24, 채널 통일 보이스 "30대 남자 인터뷰어", 재작성 7편의 mp3를 ffprobe로 직접 잰 값):
# 공백 제외 약 6.13자/초(5.83~6.40).
#
# ⚠️ 이 값을 6.7로 두면 안 된다. 6.7은 `fish_tts.AUDIO_TEMPO`가 1.1(1.1배속)이던 시절의 측정치인데
# 그 뒤 "배속 없이 원 속도" 원칙으로 1.0으로 돌아갔고 이 상수만 안 따라왔다(6.7÷1.1=6.09, 실측과 일치).
# 그 9% 과대평가 때문에 사전 핏 계산이 7편 전부 "80초 안"으로 통과시켰는데 실제 TTS는 83~92초로 나왔다.
# 발화 속도는 보이스·배속을 바꿀 때마다 다시 재야 한다.
SPEECH_CHARS_PER_SEC = 6.13
OPENING_MAX_CHARS = 40       # 도입 한 문장 ≈ 6초 — 사용자 "40자정도해도 5초정도밖에"
XRAY_OPENING_MAX_CHARS = 40  # 반투명 인체 포맷도 도입부 = 훅 한 문장


def select_hook_pattern(topic: str) -> tuple[str, str]:
    """select_format()과 동일한 시드 공식으로 topic당 훅 패턴 하나를 결정론적으로
    고른다. (이름, 설명) 튜플 반환 — 내용 기준(핵심 키워드로 시작 → 구체적 걱정
    포인트로 연결)은 패턴과 무관하게 그대로 유지, 바뀌는 건 문장 어미/형태뿐."""
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(topic))
    return HOOK_PATTERNS[seed_val % len(HOOK_PATTERNS)]


# ══════════════════════ blog_seo 전용 다양화 장치(2026-08-19) ══════════════════════
# WHY 이 3개가 별도로 필요한지: 2026-08-19 blog_seo(en/ja/de/fr/it/es/nl/sv)
# 품질 감사 결과, 16개 topic 중 94%가 H2 "실제 해결책" 섹션 헤더로 동일 문구
# ("What Actually Helps"류)를, 75%가 클로징 문단 오프너로 동일 문구("None of
# this means...")를 재사용하고 있었다. CLAUDE.md "블로그 SEO 서브트랙" 절엔
# "select_hook_pattern과 동일한 원리로 title 아키타입을 (topic, lang, 'blog')
# 시드로 고정 선택한다"고 적혀 있었지만, 실제로는 이 함수 자체가 구현된 적이
# 없었다(문서만 있고 코드가 없던 상태 — 문서-실태 괴리의 원인).
#
# WHY 이 절이 `select_blog_title_archetype`(topic·lang을 "|"로 구분한 시드,
# --blog-title-archetype CLI)를 대체하는지: 같은 날 다른 세션이 거의 동일한
# 기능(제목 아키타입만, closing/section-header는 없음)을 독립적으로 먼저
# 커밋해 병합됐다(동시 세션이 lib/*.py를 동시 편집할 수 있다는 기존 위험이
# 실제로 발생) — 사실상 같은 문제의 같은 해법이 이름만 다르게 중복 생성된
# 상태라, "이미 있는 것을 중복 생성하지 않는다" 원칙에 따라 하나로 합친다.
# 사용처가 이 파일 안에서 방금 추가된 CLI 분기뿐이고(다른 코드·문서·데이터에
# 참조 없음, grep으로 확인) 실제 topic 콘텐츠는 이미 텍스트로 확정 발행된
# 상태라 함수 이름을 바꿔도 과거 산출물엔 영향 없다.
#
# WHY seed에 lang까지 합치는지(자매 프로젝트 furrowly-content/sparelow-content의
# select_title_archetype(topic)과 다른 점): 그쪽 함수는 topic 문자열만으로
# 시드를 걸어서 같은 topic의 8개 언어 전부가 항상 같은 아키타입을 뽑는
# 버그가 있다 — 이번 감사에서 "제목이 topic별로 8개 언어 전체가 같은 수사
# 패턴으로 수렴"한 원인으로 추정된다. topic+lang을 합친 문자열로 시드를
# 걸면 같은 topic이라도 언어마다 다른 아키타입이 나온다(select_hook_pattern과
# 동일한 시드 공식, 축만 하나 늘림).


# WHY 한국어 예시를 따로 붙이는지(2026-08-30): 예시가 영어뿐이라 ko 작성 때 참고가
# 안 됐고, 실측 결과 ko 네이버 블로그 제목 342건이 한 틀로 수렴했다 —
# "A - B" 대시 구조 93%, 조건절(~라면/~다면) 74%, "숫자+가지" 50%.
# 아키타입이 5종으로 갈라져 있어도 문장 뼈대가 같으면 다양성이 없다.
TITLE_ARCHETYPES = [
    ("질문형", '"Why Does ~ Happen?" 류 질문형 — 예: "Why Does Your Blood Sugar Spike Right After Lunch?" '
               '/ ko 예: "식혜는 왜 콜라보다 혈당을 빨리 올릴까요"'),
    ("숫자·리스트형", '"N Things/Signs/Habits ~" 류 숫자 명시형 — 예: "3 Habits That Are Quietly Wrecking Your Sleep" '
                 '/ ko 예: "잠들기 전 30분, 수면을 망치는 세 가지"'),
    ("원인지목형", '"~ Is Secretly Behind ~" / "~ Might Be Causing ~" 류 원인 직접 지목형 — 예: "Your Afternoon Coffee Might Be Behind That 3 P.M. Crash" '
               '/ ko 예: "오후 3시의 졸음, 점심 커피가 범인일 수 있어요"'),
    ("통념반박형", '"~ Isn\'t What You Think" / "The Truth About ~" 류 통념 반박형 — 예: "Dry Eyes Aren\'t Just About Screen Time" '
               '/ ko 예: "안구건조증은 화면 탓만이 아닙니다"'),
    ("비교형", '"~ vs ~" 또는 "It\'s Not ~ — It\'s ~" 류 대조형 — 예: "It\'s Not Your Age — It\'s This One Habit" '
             '/ ko 예: "나이 탓이 아니라 이 습관 하나입니다"'),
]

# ko 제목이 수렴하는 형태들. 새 제목이 이 중 둘 이상에 걸리면 다시 쓸 것.
KO_TITLE_OVERUSED = [
    (r" - ", '"A - B" 대시 구조(전체의 93%)'),
    (r"(라면|다면|신가요)\s*[-?]?\s*$|(라면|다면|신가요)\s+-", "조건절 마무리(~라면/~다면/~신가요, 74%)"),
    (r"\d+\s*가지", '"숫자+가지"(50%)'),
    (r"(습관|법|방법)\s*\d*\s*가지?\s*$", '"~하는 습관/법"으로 끝맺기'),
]


def select_title_archetype(topic: str, lang: str) -> tuple[str, str]:
    """select_hook_pattern과 동일한 시드 공식이되, topic+lang을 합친 문자열로
    시드를 걸어 같은 topic이라도 언어마다 다른 아키타입이 나오게 한다(위 WHY
    참고). (이름, 설명) 튜플 반환 — 완성 문구가 아니라 "이번 topic·언어는 이
    수사 패턴으로 쓰라"는 지시이므로, 실제 제목 문장은 이 패턴에 맞춰 그
    언어로 직접 새로 쓸 것(번역·직역 금지 원칙과 별개로, 예시 문구를 그대로
    베끼지 말 것)."""
    seed_str = f"{topic}_{lang}"
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(seed_str))
    return TITLE_ARCHETYPES[seed_val % len(TITLE_ARCHETYPES)]


CLOSING_ARCHETYPES = [
    ("핵심 팁 재요약형", "앞서 나온 팁 중 가장 중요한 것 하나를 한 문장으로 다시 짚고 끝낸다 — \"~것 다 끊을 필요 없다\"류 안심 문구 반복 금지."),
    ("다음 행동 제안형", "지금 당장 할 수 있는 작은 행동 하나를 구체적으로 제안하며 끝낸다(예: \"오늘 저녁부터 이것 하나만 바꿔보세요\")."),
    ("체크리스트 회고형", "글 앞부분에서 짚은 원인/증상 항목들을 짧게 체크리스트처럼 훑어보며 끝낸다."),
    ("질문 던지기형", "독자가 스스로 점검해볼 질문 하나를 던지며 끝낸다(예: \"오늘 하루, 몇 개나 해당됐나요?\")."),
    ("전문가 상담 안내 강조형", "증상이 지속·악화되면 병원 방문을 권하는 문구를 자연스럽게 마무리에 녹인다(YMYL 규칙과 겹쳐도 무방, 오히려 강화)."),
]


def select_closing_archetype(topic: str, lang: str) -> tuple[str, str]:
    """클로징 문단의 문구 자체가 아니라 "어떤 방식으로 마무리할지" 구조적
    전략을 topic+lang 시드로 결정론적으로 고른다 — 작성자가 그 전략을 그
    언어로 자기 문장으로 풀어 쓰라는 것이지, 위 설명 문구를 그대로 옮기라는
    뜻이 아니다. 지금 75%가 수렴한 "None of this means you need to cut out
    X, Y, Z entirely"류 안심형 오프너는 옵션 중 하나로만 남기고 강제하지
    않기 위함."""
    seed_str = f"{topic}_{lang}"
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(seed_str))
    return CLOSING_ARCHETYPES[seed_val % len(CLOSING_ARCHETYPES)]


# WHY 카드 구조까지 시드로 흔드는지(2026-08-31 실측): 카드 스펙 385개 중 320개(83%)가
# 아이템 7개 고정이고, 307개(80%)가 단 두 가지 원인/해결 배열이었다("원인·대안 3쌍"
# 아니면 "원인만 7개"). 제목은 중복 0건이라 눈에 안 띄는데 글을 여러 편 이어 보면
# 같은 틀이 반복되는 게 드러난다 — 사용자가 "저품질 되는 느낌"이라고 먼저 알아챘다.
# 훅·제목 아키타입과 같은 원리로 topic 시드를 걸어 구조 자체를 흔든다.
CARD_STRUCTURES = [
    ("원인·대안 3쌍", "원인 3개를 각각 바로 뒤에 대안과 붙여 3쌍으로(원인1→대안1→원인2→대안2→원인3→대안3). 아이템 7개."),
    ("원인 몰기 후 대안 몰기", "원인 3개를 먼저 연달아 보여주고 대안 3개를 뒤에 몰아서. 순서가 바뀌면 읽는 리듬이 달라진다. 아이템 7개."),
    ("원인 2개 깊게", "원인을 3개로 늘리지 말고 2개만 골라 각각 두 장씩 깊게 파고든다(기전 한 장 + 대안 한 장). 아이템 5~6개."),
    ("오해 깨기", "흔한 오해 한 장으로 열고, 실제 원인 → 실제 대안 순으로. 첫 장을 '왜 이런 문제가 생길까요'로 시작하지 않는다. 아이템 6~7개."),
    ("체크리스트형", "원인/대안을 나누지 않고 '오늘 바꿀 것' 항목을 죽 나열한다. 아이템 5~8개."),
    ("한 가지 집중", "원인 하나만 끝까지 파고든다(기전→근거→대안→주의점). 여러 개 나열하지 않는다. 아이템 5~6개."),
]

# WHY 접속어까지 흔드는지: 네이버 본문의 77%가 "먼저 ~"로 원인을 열고 64%가
# "마지막으로"로 닫고 있었다. 내용이 달라도 읽는 느낌이 같아진다.
CAPTION_CONNECTIVES = [
    ("먼저/두 번째로/마지막으로", "가장 흔한 기본형 — 이미 과반이 쓰고 있으니 이 시드가 나왔을 때만 쓸 것"),
    ("첫 번째는/그다음은/여기에 하나 더", "번호를 세되 마지막을 '하나 더'로 열어두는 형태"),
    ("~부터 보면/이것도 겹치면/여기에", "원인을 쌓아 올리는 형태 — 순번을 세지 않는다"),
    ("의외로 ~/생각보다 ~/무엇보다", "각 항목을 의외성으로 여는 형태"),
    ("접속어 없이", "'먼저·두 번째' 같은 순번 표지를 아예 쓰지 않고 소제목만으로 넘어간다"),
]


def _even_seed(text: str) -> int:
    """WHY 기존 select_hook_pattern의 덧셈 시드를 안 쓰는지(2026-08-31): 한글은
    ord 값이 44,032~55,203 좁은 구간에 몰려 있어서 그 공식으로 6으로 나누면
    배분이 34~108개까지 벌어졌다(실측). 선택지가 적을수록 이 쏠림이 그대로
    콘텐츠 쏠림이 되므로 여기서는 균등한 해시를 쓴다."""
    return int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16)


def select_card_structure(topic: str) -> tuple[str, str]:
    """카드 구성 방식을 topic 시드로 결정론적으로 고른다. 완성된 카드가 아니라
    '이번 topic은 이 짜임으로 가라'는 지시다 — 소재상 도저히 안 맞으면 다른 걸
    골라도 되지만, 그때도 직전 몇 개 topic과 같은 짜임은 피할 것."""
    return CARD_STRUCTURES[_even_seed("card:" + topic) % len(CARD_STRUCTURES)]


def select_caption_connectives(topic: str) -> tuple[str, str]:
    """네이버 본문에서 항목을 잇는 접속어 세트를 topic 시드로 고른다."""
    return CAPTION_CONNECTIVES[_even_seed("conn:" + topic) % len(CAPTION_CONNECTIVES)]


SECTION_HEADER_ARCHETYPES = {
    # "actual_fix" = H2 "실제 해결책" 섹션(94%가 "What Actually Helps"로 고정돼 있던 그 섹션)
    "actual_fix": [
        ("행동 동사형", "동사로 바로 시작하는 소제목 — 예: \"Cut Back on Late-Night Screens\", \"Swap Soda for Sparkling Water\""),
        ("질문형", "\"그럼 뭘 하면 될까?\"류 질문형 소제목 — 예: \"So What Actually Works?\""),
        ("결과 제시형", "이렇게 하면 어떻게 좋아지는지 결과를 먼저 제시하는 소제목 — 예: \"What Happens When You Fix This\""),
        # ⚠️ 숫자형은 아래 목록 개수와 반드시 일치해야 한다(2026-08-31 실측): 아키타입만
        # 보고 "3 Wege…"를 붙였는데 그 아래 항목이 5개여서 헤더가 본문과 어긋난 사례가 있다.
        ("숫자형", "\"N가지 방법\" 같은 숫자 명시형 소제목 — 예: \"3 Changes That Actually Move the Needle\". ⚠️ N은 그 섹션 아래 실제 항목 수와 일치시킬 것"),
        ("대조형", "\"문제 vs 실제 해결책\" 대조 구조 소제목 — 예: \"Skip the Myths — Here's What Helps\""),
    ],
    # "summary" = 글 맨 끝 요약 H2. 2026-08-31 실측에서 ko는 23편 중 21편이 "정리하면"
    # 하나로 고정돼 있었고(다른 언어도 37~52%), 중간 H2는 topic마다 잘 갈리는데 마지막
    # 두 개만 판박이라 글을 이어 읽으면 같은 틀이 그대로 드러났다.
    "summary": [
        ("한 줄 결론형", "결론 자체를 소제목으로 — 예: \"결국 문제는 온도차였어요\""),
        ("행동 지시형", "오늘 무엇부터 할지를 소제목에 — 예: \"오늘 하나만 바꾼다면\""),
        ("안심형", "다 끊지 않아도 된다는 톤 — 예: \"전부 끊을 필요는 없어요\""),
        ("되짚기형", "앞에서 짚은 것을 다시 세는 형태 — 예: \"세 가지를 다시 짚으면\""),
        ("질문 회수형", "도입부 질문에 답하는 형태 — 예: \"그래서 왜 아침마다 그럴까요\""),
    ],
}


def select_section_header_archetype(topic: str, lang: str, section: str) -> tuple[str, str]:
    """H2 섹션 헤더의 완성 문구가 아니라 문패턴 스타일을 topic+lang+section
    시드로 결정론적으로 고른다. section 인자는 최소 "actual_fix"(H2 "실제
    해결책" 섹션) 지원 — 필요하면 SECTION_HEADER_ARCHETYPES에 다른 섹션
    키를 추가할 것. CLI 없이 blog_seo 작성 세션이 직접 import해서 쓰는
    용도라 사용 시 SECTION_HEADER_ARCHETYPES에 없는 section을 넘기면
    KeyError로 바로 드러난다(조용히 기본값 폴백하지 않음)."""
    seed_str = f"{topic}_{lang}_{section}"
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(seed_str))
    options = SECTION_HEADER_ARCHETYPES[section]
    return options[seed_val % len(options)]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--hook-pattern":
        if len(sys.argv) > 2:
            name, desc = select_hook_pattern(sys.argv[2])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --hook-pattern <topic>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--title-archetype":
        if len(sys.argv) > 3:
            name, desc = select_title_archetype(sys.argv[2], sys.argv[3])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --title-archetype <topic> <lang>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--closing-archetype":
        if len(sys.argv) > 3:
            name, desc = select_closing_archetype(sys.argv[2], sys.argv[3])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --closing-archetype <topic> <lang>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--card-structure":
        if len(sys.argv) > 2:
            name, desc = select_card_structure(sys.argv[2])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --card-structure <topic>")
    elif len(sys.argv) > 1 and sys.argv[1] == "--connectives":
        if len(sys.argv) > 2:
            name, desc = select_caption_connectives(sys.argv[2])
            print(f"{name} — {desc}")
        else:
            print("사용법: python3 -m lib.content_review --connectives <topic>")
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
        print("사용법: python3 -m lib.content_review <topic> [lang] 또는 --all 또는 --hook-pattern <topic> 또는 --title-archetype <topic> <lang> 또는 --closing-archetype <topic> <lang>")
