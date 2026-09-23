# 네이버 자동완성·연관검색어 수집 — topic 선정과 제목에 "사람들이 실제로 치는 말"을 쓰기 위한 도구.
#
# WHY(2026-09-23 사용자): 네이버 클립은 검색어 기준으로 영상을 띄워주는 경향이 있다. 지금까지 제목을
# "담석증, 기름진 음식 탓만이 아니라…"처럼 읽기 좋은 문장으로 지어왔는데, 검색 노출이 목적이면 사람들이
# 실제로 치는 말("오른쪽 윗배 통증")이 앞에 와야 한다.
#
# WHY 검색광고 API가 아니라 자동완성인지: 월간 검색량을 주는 네이버 검색광고 API는 광고 계정과 키가 필요한데
# 아직 없다. 자동완성은 키 없이 되고 절대 검색량은 안 나오지만 **어떤 표현으로 검색하는지**는 그대로 준다.
# 키가 생기면 여기에 검색량 컬럼만 붙이면 된다.
#
#   python3 -m lib.naver_keywords 담석증 위경련            # 씨앗 키워드 직접 지정
#   python3 -m lib.naver_keywords --topic 소화_13          # topic의 병명·증상에서 씨앗을 뽑아 수집
#   python3 -m lib.naver_keywords --expand 2 담석증        # 자동완성 결과를 다시 씨앗으로(2단계)
from __future__ import annotations

import argparse
import json
import random
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "_audit" / "naver_keywords.json"
AC_URL = "https://ac.search.naver.com/nx/ac?q={q}&con=0&frm=nv&ans=2&r_format=json&r_enc=UTF-8&r_unicode=0&t_koreng=1&run=2&rev=4&q_enc=UTF-8&st=100"
# WHY User-Agent를 브라우저로 두는지: 기본 python-urllib UA는 차단당한다(다른 프로젝트에서 실측).
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/153.0.0.0 Safari/537.36")
PAUSE = (0.6, 1.4)          # 공개 엔드포인트라 천천히 — 한 번에 몰아치지 않는다


def autocomplete(query: str) -> list[str]:
    """검색창 자동완성 목록. 실패하면 빈 리스트(수집 도구라 예외로 파이프라인을 멈추지 않는다)."""
    req = urllib.request.Request(AC_URL.format(q=urllib.parse.quote(query)), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []
    out: list[str] = []
    for group in data.get("items", []):
        for item in group:
            if item and isinstance(item[0], str):
                out.append(item[0].strip())
    return [k for k in dict.fromkeys(out) if k and k != query]


def collect(seeds: list[str], expand: int = 1) -> dict[str, list[str]]:
    """씨앗마다 자동완성을 받고, expand>1이면 결과를 다시 씨앗으로 한 단계 더 판다."""
    result: dict[str, list[str]] = {}
    queue = [(s, 1) for s in seeds]
    seen = set()
    while queue:
        q, depth = queue.pop(0)
        if q in seen:
            continue
        seen.add(q)
        time.sleep(random.uniform(*PAUSE))
        kws = autocomplete(q)
        if kws:
            result[q] = kws
        if depth < expand:
            # 씨앗을 그대로 포함한 제안만 더 판다 — 엉뚱한 주제로 새는 걸 막는다
            for k in kws[:5]:
                if q.replace(" ", "") in k.replace(" ", ""):
                    queue.append((k, depth + 1))
    return result


def _topic_seeds(topic: str) -> list[str]:
    """topic의 제목에서 병명·증상 표현을 뽑아 씨앗으로 쓴다."""
    spec = json.loads((ROOT / "data" / topic / "card_news_spec.json").read_text(encoding="utf-8"))
    title = spec.get("video_title") or spec["title"]
    head = re.split(r"[,·—]", title[0])[0].strip()
    seeds = [head]
    for line in title[1:]:
        # "속이 쓰리고 아프다면" 같은 증상 구절에서 조사·어미를 떼고 명사구만
        m = re.findall(r"[가-힣]{2,}\s?[가-힣]{0,4}(?=이|가|을|를|은|는|면|고|서|\s|$)", line)
        seeds += [x.strip() for x in m if 2 <= len(x.strip()) <= 12]
    return list(dict.fromkeys(seeds))[:6]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", nargs="*")
    ap.add_argument("--topic", help="이 topic의 제목에서 씨앗을 뽑는다")
    ap.add_argument("--expand", type=int, default=1, help="자동완성 결과를 다시 씨앗으로 파고드는 단계 수")
    a = ap.parse_args()

    seeds = list(a.seeds)
    if a.topic:
        seeds += _topic_seeds(a.topic)
    if not seeds:
        raise SystemExit("씨앗 키워드나 --topic 중 하나는 필요하다")

    got = collect(seeds, a.expand)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    old.update({k: {"collected_at": time.strftime("%Y-%m-%d %H:%M"), "keywords": v} for k, v in got.items()})
    OUT.write_text(json.dumps(old, ensure_ascii=False, indent=1), encoding="utf-8")

    for seed, kws in got.items():
        print(f"\n[{seed}] {len(kws)}개")
        for k in kws[:12]:
            print("   ", k)
    print(f"\n저장: {OUT.relative_to(ROOT)}  (누적 {len(old)}개 씨앗)")


if __name__ == "__main__":
    main()
