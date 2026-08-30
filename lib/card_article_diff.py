# 카드뉴스 spec과 같은 topic의 ko 기사(blog_seo)가 서로 다른 말을 하는지 훑는다.
#
# WHY 이게 필요한지(2026-08-30 실측): 네이버 블로그 게시물은 카드 이미지와 그 아래
# 글이 한 화면에 같이 나간다. 그런데 카드 spec은 영상/카드뉴스 트랙에서 먼저 쓰였고
# blog_seo 기사는 나중에 사실검증을 거쳐 쓰여서, 같은 주제인데 숫자와 기전이 어긋난
# 채로 남은 곳이 있다. 실제 사례:
#   계절질환_1 — 카드 "온도차 5도·필터 2주" vs 기사 "8도 안팎·한 달에서 세 달"
#                (원문 대조 결과 카드가 맞았고 기사가 프랑스 기준을 들여온 것이었다)
#   손발_1    — 카드 "카페인이 철분 흡수 방해" vs 기사 "카페인이 아니라 폴리페놀"
#   수면_1    — 카드 "대추의 사포닌·마그네슘" vs 기사 "칼륨·폴리페놀"
# 숫자는 기계로 잡히지만 기전 충돌은 안 잡힌다 — 이 도구는 "확인할 자리"를 좁혀줄
# 뿐이고 판정은 사람/세션이 한다. 통과/실패 게이트로 쓰지 말 것.
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

_NUM = re.compile(
    r"\d+(?:[.,]\d+)?\s*"
    r"(?:%|퍼센트|배|도|℃|분|시간|주|개월|년|일|g|kg|mg|ng|mcg|ml|L|칼로리|kcal|명|건|회)"
)


def _spec_path(topic: str) -> Path | None:
    for cand in (ROOT / "data" / topic / "ko" / "card_news_spec.json",
                 ROOT / "data" / topic / "card_news_spec.json"):
        if cand.exists():
            return cand
    return None


def _article_text(topic: str) -> str | None:
    path = ROOT / "data" / topic / "ko" / "platform_captions.json"
    if not path.exists():
        return None
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for entry in spec.get("platforms", []):
        if entry.get("platform") == "blog_seo":
            return re.sub(r"<[^>]+>", " ", entry.get("body_html", ""))
    return None


def _spec_text(path: Path) -> str:
    spec = json.loads(path.read_text(encoding="utf-8"))
    parts = [" ".join(i.get("body", [])) + " " + i.get("name", "") for i in spec.get("items", [])]
    parts += [" ".join(h) for h in spec.get("closing", {}).get("headline", [])]
    parts += spec.get("closing", {}).get("tip", [])
    return " ".join(parts)


def numbers_only_in_cards(topic: str) -> list[str]:
    """카드에는 있는데 기사 본문엔 없는 수치. 틀렸다는 뜻이 아니라 확인할 자리라는 뜻."""
    path = _spec_path(topic)
    article = _article_text(topic)
    if not path or article is None:
        return []
    in_cards = {m.group(0).replace(" ", "") for m in _NUM.finditer(_spec_text(path))}
    in_article = {m.group(0).replace(" ", "") for m in _NUM.finditer(article)}
    return sorted(in_cards - in_article)


def main() -> None:
    topics = sys.argv[1:] or sorted(
        d.name for d in (ROOT / "data").iterdir()
        if d.is_dir() and not d.name.startswith("_")
    )
    flagged = 0
    for topic in topics:
        only = numbers_only_in_cards(topic)
        if not only:
            continue
        flagged += 1
        print(f"[{topic}] 카드에만 있는 수치 — {', '.join(only)}")
    print(f"\n{len(topics)}개 topic 검사 · 확인 필요 {flagged}개")
    print("숫자만 본다 — 기전이 서로 뒤집힌 경우(카드 '카페인 탓' vs 기사 '카페인 아님')는")
    print("여기 안 잡히니 카드 문구와 기사를 직접 대조할 것.")


if __name__ == "__main__":
    main()
