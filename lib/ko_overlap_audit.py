# 한국어 blog_seo 본문이 같은 topic의 네이버 블로그 캡션과 얼마나 겹치는지 잰다.
#
# WHY(2026-09-03): 지시는 처음부터 "한국도 같이 넣되 네이버 블로그와 내용이 겹치지
# 않게 구성"이었는데, CLAUDE.md에 "8개 언어(한국 제외)"라고 적힌 줄이 오래 남아
# 여러 세션이 반복해서 ko를 대상에서 뺐다. 그 결과 ko만 글 수도 분량도 절반이 됐고,
# 겹침을 재는 장치도 없어서 실제로 겹치는지 아무도 몰랐다.
#
# 8자 단위 shingle로 잰다 — 한국어는 조사가 붙어 어절 단위 비교가 둔하고, 8자면
# 우연히 일치하기엔 충분히 길다. 두 지표를 같이 본다:
#   자카드     — 두 글이 전체적으로 얼마나 같은가
#   SEO 커버리지 — SEO 본문 중 네이버에도 있는 부분의 비율(이쪽이 중복 판정에 직접적)
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SHINGLE = 8
OVERLAP_LIMIT = 20  # SEO 커버리지가 이 %를 넘으면 다시 쓸 것


def _naver_caption(topic: str) -> str | None:
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


def _ko_body(topic: str) -> str | None:
    path = DATA / topic / "ko" / "platform_captions.json"
    if not path.exists():
        return None
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    for entry in spec.get("platforms", []):
        if entry.get("platform") == "blog_seo":
            return re.sub(r"<[^>]+>", " ", entry.get("body_html", ""))
    return None


def _shingles(text: str) -> set[str]:
    packed = re.sub(r"\s+", "", text)
    return {packed[i:i + SHINGLE] for i in range(max(0, len(packed) - SHINGLE))}


def overlap(topic: str) -> tuple[int, int, int] | None:
    """(자카드%, SEO 커버리지%, SEO 글자수). 둘 중 하나라도 없으면 None."""
    naver, body = _naver_caption(topic), _ko_body(topic)
    if not naver or not body:
        return None
    a, b = _shingles(naver), _shingles(body)
    if not a or not b:
        return None
    return (
        round(len(a & b) / len(a | b) * 100),
        round(len(a & b) / len(b) * 100),
        len(re.sub(r"\s+", "", body)),
    )


def main() -> None:
    topics = sys.argv[1:] or sorted(
        d.name for d in DATA.iterdir() if d.is_dir() and not d.name.startswith("_")
    )
    rows = [(t, *r) for t in topics if (r := overlap(t))]
    rows.sort(key=lambda x: -x[2])
    print(f"{'topic':14}{'자카드%':>8}{'네이버와 겹침%':>14}{'글자수':>8}")
    for t, j, c, n in rows:
        flag = "  ⚠️ 다시 쓸 것" if c > OVERLAP_LIMIT else ""
        print(f"{t:14}{j:8}{c:14}{n:8}{flag}")
    over = [r for r in rows if r[2] > OVERLAP_LIMIT]
    print(f"\n{len(rows)}개 비교 · 겹침 {OVERLAP_LIMIT}% 초과 {len(over)}개")
    print("ko 본문은 같은 topic이라도 네이버와 다른 각도로 써야 한다 — 같은 사람이 두 곳을")
    print("다 봤을 때 중복으로 느끼지 않아야 하고, 검색엔진에도 서로 다른 페이지여야 한다.")


if __name__ == "__main__":
    main()
