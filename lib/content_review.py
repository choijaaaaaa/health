# 콘텐츠 QA — narration.txt/card_news_spec.json의 문장이 맥락상 말이 되는지 LLM으로
# 리뷰한다. WHY(2026-08-03, "이렇게 문맥에 맞지 않는 이상한 말들 얼마나 많겠어? ...
# 시험하는 방법론에 대해 고민해야해"): 해시태그 누락·헷지 문장 같은 규칙 기반 검사로는
# "문법은 멀쩡한데 내용이 김빠지는" 문제(예: "맥주 대신 무알코올 맥주로 바꿔보세요"처럼
# 동어반복적인 대체 제안)를 못 잡는다 — 이건 패턴 매칭이 아니라 "이 문장이 맥락상
# 말이 되는가"를 판단해야 하는 문제라 LLM 리뷰가 필요하다.
#
# 사용법:
#   python3 -m lib.content_review <topic>     — topic 하나만 리뷰
#   python3 -m lib.content_review --all        — data/ 밑 모든 topic 배치 리뷰
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
# WHY gemini-flash-latest(2026-08-03): lib/gemini_illust.py는 이미지 생성용이라 특정
# 버전(gemini-3.1-flash-lite-image)에 고정돼 있지만, 이건 텍스트 리뷰만 하면 되니
# 버전이 바뀌어도 자동으로 최신을 가리키는 latest 별칭을 쓴다 — 모델 리스트 조회로
# 실제 사용 가능함을 확인함(2026-08-03).
MODEL = "gemini-flash-latest"

REVIEW_PROMPT = """당신은 한국어 건강 정보 숏폼 콘텐츠를 검수하는 깐깐한 편집자입니다.
아래는 한 topic의 나레이션 대본과 카드뉴스 텍스트입니다. 다음 기준으로 문제
있는 문장만 찾아주세요:

1. 논리적으로 말이 안 되거나 앞뒤가 안 맞는 문장
2. 문법은 멀쩡하지만 맥락상 김빠지거나 성의없어 보이는 대체/팁 제안
   (예: "맥주 대신 무알코올 맥주로 바꿔보세요"처럼 동어반복적이거나 너무
   뻔해서 실질적 정보가 없는 경우)
3. 과장되거나 근거 없어 보이는 의학적 주장
4. 앞 문장과 모순되는 내용

문제가 없으면 빈 배열 []만 반환하세요. 문제가 있으면 아래 JSON 배열 형식
으로만 답하세요(설명 문장이나 코드블록 표시 없이 JSON만):
[{{"quote": "문제 문장 원문 그대로", "issue": "무엇이 문제인지 한국어 한 줄 설명"}}]

--- 나레이션 ---
{narration}

--- 카드뉴스 텍스트 ---
{card_text}
"""


def _headers() -> dict:
    return {"x-goog-api-key": os.environ["GEMINI_API_KEY"], "Content-Type": "application/json"}


def _card_news_text(topic: str) -> str:
    """WHY items[].name/body + closing만 뽑는지: card_news_spec.json엔 char_file
    (일러스트 파일명)·cover_scrim_color 같은 텍스트가 아닌 값도 섞여 있어서, 스키마
    (위 "카드뉴스 스펙" 절 참고: items[{{name, char_file, body}}], closing{{headline,
    tip, cta}})를 알고 정확히 그 필드만 골라야 리뷰 프롬프트에 노이즈가 안 낀다."""
    spec_path = ROOT / "data" / topic / "card_news_spec.json"
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


def review_topic(topic: str) -> list[dict]:
    narration_path = ROOT / "data" / topic / "narration.txt"
    narration = narration_path.read_text(encoding="utf-8") if narration_path.exists() else ""
    card_text = _card_news_text(topic)
    if not narration and not card_text:
        return []

    prompt = REVIEW_PROMPT.format(narration=narration, card_text=card_text)
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
        return []
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
        return []
    return issues if isinstance(issues, list) else []


def review_all() -> dict[str, list[dict]]:
    """data/ 밑 모든 topic을 순회하며 리뷰 — 기존 topic 전수 감사용(일회성 실행)."""
    results: dict[str, list[dict]] = {}
    topic_dirs = sorted(d for d in (ROOT / "data").iterdir() if d.is_dir() and (d / "narration.txt").exists())
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


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        review_all()
    elif len(sys.argv) > 1:
        found = review_topic(sys.argv[1])
        if found:
            for issue in found:
                print(f"- \"{issue.get('quote', '')}\" — {issue.get('issue', '')}")
        else:
            print("문제 없음")
    else:
        print("사용법: python3 -m lib.content_review <topic> 또는 --all")
