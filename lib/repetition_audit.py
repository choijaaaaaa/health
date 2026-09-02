# 콘텐츠가 같은 틀로 수렴하고 있는지 축별로 재는 도구.
#
# WHY(2026-08-31): 사용자가 "제목이나 내용이 비슷비슷해서 저품질 되는 느낌"이라고
# 지적해 실측했더니 실제로 그랬다 — 카드 385개 중 320개(83%)가 아이템 7개 고정,
# 307개(80%)가 단 두 가지 원인/해결 배열, 네이버 본문의 78%가 "먼저 ~예요"로 시작,
# ko blog_seo의 91%가 H2 "정리하면"이었다. 제목 자체는 중복 0건이라 눈에 안 띄는데
# 구조가 판박이인 형태여서, 사람이 글을 몇 편 읽어봐도 잘 안 드러난다.
#
# 통과/실패 게이트가 아니라 "지금 어디가 쏠려 있는지" 보는 계기판이다. 쏠림이
# 얼마부터 위험한지에 대한 객관적 기준이 없어서 임계값을 두지 않았다 — 대신 작업
# 전후로 돌려 수치가 내려가는지 확인하는 용도로 쓴다.
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

BLOG_LANGS = ("de", "en", "es", "fr", "it", "ja", "ko", "nl", "sv")


def _naver_caption(topic: str) -> str | None:
    """한국어 캡션은 topic마다 flat 또는 ko/ 한 곳에만 있다(CLAUDE.md 참고)."""
    for path in (DATA / topic / "platform_captions.json", DATA / topic / "ko" / "platform_captions.json"):
        if not path.exists():
            continue
        try:
            spec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None
        for entry in spec.get("platforms", []):
            if entry.get("name") == "네이버 블로그":
                return entry.get("caption")
        return None
    return None


def _card_spec(topic: str) -> dict | None:
    for path in (DATA / topic / "ko" / "card_news_spec.json", DATA / topic / "card_news_spec.json"):
        if path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                return None
    return None


def topics() -> list[str]:
    return sorted(p.name for p in DATA.iterdir() if p.is_dir() and not p.name.startswith("_"))


def _share(counter: collections.Counter, total: int, top: int = 3) -> list[str]:
    return [f"{v * 100 // total:2}%  {k}" for k, v in counter.most_common(top)] if total else []


def card_structure_report() -> dict:
    """카드 아이템 개수와 원인(C)/해결(S) 배열이 얼마나 한 형태로 몰려 있는지."""
    counts, shapes, names = collections.Counter(), collections.Counter(), collections.Counter()
    for topic in topics():
        spec = _card_spec(topic)
        if not spec:
            continue
        items = [i.get("name", "") for i in spec.get("items", [])]
        if not items:
            continue
        counts[len(items)] += 1
        shapes["".join("S" if re.search(r"(대신|이렇게)$", n) else "C" for n in items)] += 1
        names.update(items)
    total = sum(counts.values())
    return {"total": total, "counts": counts, "shapes": shapes, "names": names}


# WHY 문단 첫머리만 세는지(2026-09-01 정정): 처음엔 캡션 전체에서 "먼저"/"마지막으로"를
# 그냥 찾았는데, 그 수치가 실제 쏠림보다 훨씬 부풀려져 있었다. 두 작업자가 각각
# 실측해서 알려준 내용 — 남은 "먼저"는 전부 정상 한국어였고("채소를 먼저 먹고",
# "담당 의사와 먼저 상의하세요"), 남은 "마지막으로"는 전부 `NN · 소제목` 마커 라인
# (= 카드 제목)이라 본문 접속어가 아니다. 원인을 나열하며 문단을 여는 자리만 세야
# 고칠 수 있는 수치가 된다.
_MARKER_LINE = re.compile(r"^\d{2} · ")


def _prose_paragraphs(caption: str) -> list[str]:
    """마커 라인·해시태그를 뺀 본문 문단들."""
    out = []
    for line in caption.split("\n"):
        line = line.strip()
        if not line or line.startswith("#") or _MARKER_LINE.match(line):
            continue
        out.append(line)
    return out


def caption_phrase_report() -> dict:
    """네이버 본문이 같은 접속어로 원인을 열고 닫는 비율(문단 첫머리 기준)."""
    patterns = {
        "'먼저'로 문단 열기": r"^먼저[\s,]",
        "'두 번째는'으로 열기": r"^두 ?번째",
        "'마지막으로'로 열기": r"^마지막으로",
        "'무조건 끊을 필요는'": r"무조건 (다 )?끊",
    }
    hit = collections.Counter()
    total = 0
    for topic in topics():
        caption = _naver_caption(topic)
        if not caption:
            continue
        total += 1
        paras = _prose_paragraphs(caption)
        for label, pat in patterns.items():
            if any(re.search(pat, para) for para in paras):
                hit[label] += 1
    return {"total": total, "hit": hit}


def blog_h2_report() -> dict:
    """언어별 blog_seo H2 헤더 쏠림."""
    per_lang: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    articles = collections.Counter()
    for topic in topics():
        for lang in BLOG_LANGS:
            path = DATA / topic / lang / "platform_captions.json"
            if not path.exists():
                continue
            try:
                spec = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            for entry in spec.get("platforms", []):
                if entry.get("platform") != "blog_seo":
                    continue
                articles[lang] += 1
                for raw in re.findall(r"<h2>(.*?)</h2>", entry.get("body_html", ""), re.S):
                    per_lang[lang][re.sub(r"<[^>]+>", "", raw).strip()] += 1
    return {"articles": articles, "per_lang": per_lang}


def main() -> None:
    card = card_structure_report()
    print(f"■ 카드 구조 — 스펙 {card['total']}개")
    top_count, n = card["counts"].most_common(1)[0]
    print(f"   아이템 {top_count}개인 topic  {n} ({n * 100 // card['total']}%)")
    for line in _share(card["shapes"], card["total"]):
        print(f"   같은 원인/해결 배열  {line}")
    print("   반복되는 카드 제목:", ", ".join(f"{k}({v})" for k, v in card["names"].most_common(4)))

    cap = caption_phrase_report()
    print(f"\n■ 네이버 본문 접속어 — 캡션 {cap['total']}개")
    for label, c in cap["hit"].most_common():
        print(f"   {c * 100 // cap['total']:3}%  {label}")

    blog = blog_h2_report()
    print("\n■ blog_seo H2 쏠림 (언어별 최다 헤더가 그 언어 글의 몇 %에 등장하는지)")
    for lang in BLOG_LANGS:
        total = blog["articles"][lang]
        if not total:
            continue
        top = blog["per_lang"][lang].most_common(2)
        detail = " / ".join(f"{k[:26]} {v * 100 // total}%" for k, v in top)
        print(f"   {lang:3} 글 {total:3}편  {detail}")

    print("\n임계값을 두지 않은 이유는 파일 상단 WHY 참고 — 작업 전후 비교용 계기판이다.")


if __name__ == "__main__":
    main()
