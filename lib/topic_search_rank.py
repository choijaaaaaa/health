# topic별 검색 수요 측정 — 어떤 topic을 먼저 만들지, 제목 맨 앞에 뭘 둘지 정하는 근거.
#
# WHY(2026-09-23 사용자 "네이버 클립은 검색했던 검색어 기준으로 영상을 띄워준다… 제목도 검색어 트렌드에
# 맞춰 짓는 게 핵심"): 지금까지 topic 선정은 계절 캘린더·트렌드 감으로 했고 제목은 읽기 좋은 문장으로
# 지었다. 둘 다 "이 주제를 몇 명이 실제로 검색하는지"를 한 번도 안 봤다.
#
# 하는 일: topic마다 대표 검색어(병명·증상)를 뽑아 검색광고 keywordstool에 던지고,
#   ① 대표어 자체의 월간 검색량  ② 그 hint로 딸려온 연관 키워드 중 상위
# 를 topic에 귀속시켜 저장한다. ②가 제목 앞에 둘 실제 후보다 — 우리가 "담석증"으로 부르는 주제를
# 사람들은 "오른쪽 윗배 통증"으로 검색하기 때문.
#
#   .venv/bin/python3 -m lib.topic_search_rank                 # 미게시 topic 전부
#   .venv/bin/python3 -m lib.topic_search_rank --all           # 게시분 포함 전부
#   .venv/bin/python3 -m lib.topic_search_rank --topics 소화_13 눈_25
#   .venv/bin/python3 -m lib.topic_search_rank --report        # API 호출 없이 저장된 결과만 다시 본다
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

import requests
from dotenv import load_dotenv

from lib import tracks
from lib.naver_keywords import autocomplete
from lib.naver_searchad import volumes

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "_audit" / "topic_search_rank.json"

# WHY: 대표어가 이런 꼴이면 검색어가 아니라 훅 문장의 앞부분이 잘려나온 것이다("손발이 자주 저리거나").
# hint로 던져봐야 0건이라 조용히 순위 밖으로 밀리므로, 조회 전에 골라내 사람이 보게 남긴다.
_SENTENCE_TAIL = re.compile(r"(이|가|은|는|을|를|에|로|와|과|도|만)$|(거나|다면|면|고|서|때|중)$")

# WHY 진료과·병원을 거르는지: keywordstool은 광고주 기준 연관어라 어떤 질환을 던져도 "이비인후과
# (52만)"·"내과(41만)"가 최상위로 올라온다. 검색량은 크지만 **병원을 찾는 검색**이라 건강정보
# 영상으로는 절대 안 잡힌다 — 그대로 두면 순위표가 진료과 목록이 된다.
_CLINIC = re.compile(r"(내과|외과|안과|치과|피부과|정형외과|이비인후과|산부인과|비뇨기과|신경과"
                     r"|정신과|가정의학과|한의원|병원|의원|클리닉|약국)$")


def useful_related(related: list[dict], seed: str) -> list[dict]:
    """제목 후보로 쓸 수 있는 연관어만. 진료과·병원과 대표어 자기 자신은 뺀다."""
    flat = seed.replace(" ", "")
    return [r for r in related if not _CLINIC.search(r["keyword"]) and r["keyword"] != flat]


# WHY 접미어를 화이트리스트로 두는지(2026-09-23 실측): "대표어를 포함하는 연관어"까지 넓혔더니
# "동상"→"동상이몽"(예능 프로그램), "혈당"→"혈당측정기"(기기 구매)가 최고 볼륨으로 뽑혔다.
# 부분문자열은 의미를 보장하지 않는다. **정보를 찾는 검색**이 확실한 접미형만 자동 승격 대상으로 둔다.
_INFO_SUFFIX = ("증상", "초기증상", "원인", "치료", "치료법", "치료방법", "예방", "검사",
                "수치", "정상수치", "좋은음식", "에좋은음식", "낫는법", "빨리낫는법",
                "자가진단", "관리법", "전염", "전염성", "재발", "합병증", "진단")


def upgrade_keyword(seed: str, related: list[dict], volume: int) -> tuple[str, int]:
    """대표어와 그 정보형 접미 변형 중 검색량이 가장 큰 것. 제품·기기·무관어로는 절대 갈아타지 않는다."""
    flat = seed.replace(" ", "")
    best = (flat, volume)
    for r in useful_related(related, seed):
        k = r["keyword"]
        if k.startswith(flat) and k[len(flat):] in _INFO_SUFFIX and r["total"] > best[1]:
            best = (k, r["total"])
    return best


def _spec(topic: str) -> dict | None:
    base = tracks.data_dir(topic)
    for p in (base / "ko" / "card_news_spec.json", base / "card_news_spec.json"):
        if p.exists():
            return json.loads(p.read_text(encoding="utf-8"))
    return None


def seed_for(topic: str) -> tuple[str, bool]:
    """(대표 검색어, 문장조각여부). thumb_word가 있으면 그게 정답 — 썸네일에 박는 병명과 같다."""
    spec = _spec(topic)
    if not spec:
        return "", True
    if spec.get("thumb_word"):
        return spec["thumb_word"].strip(), False
    title = spec.get("video_title") or spec.get("title") or []
    if not title:
        return "", True
    head = re.split(r"[,·—]", title[0])[0].strip()
    words = head.split()
    # 두 어절 넘거나 조사·어미로 끝나면 문장 조각이다
    fragment = len(words) > 2 or bool(_SENTENCE_TAIL.search(head))
    return head, fragment


def unposted() -> set[str]:
    """네이버 블로그에 카드뉴스가 아직 안 나간 topic — 영상 제작 대상(CLAUDE.md 규칙)."""
    load_dotenv(ROOT / ".env")
    url, key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    rows: list[dict] = []
    for off in range(0, 20000, 1000):
        page = requests.get(f"{url}/rest/v1/posting_log?select=topic,platform&limit=1000&offset={off}",
                            headers=h, timeout=60).json()
        if not page:
            break
        rows += page
    blogged = {x["topic"] for x in rows if "블로그" in (x.get("platform") or "")}
    return all_topics() - blogged


def all_topics() -> set[str]:
    return {d.name for d in tracks.iter_topic_dirs(ROOT / "data")}


def measure(topics: list[str], seed_override: dict[str, list[str]] | None = None,
            per_topic: int = 10) -> dict:
    """topic → {seed, volume, related[]}.

    ⚠️ 연관어를 keywordstool에서 받지 않는다 — 그건 **광고주 그룹 기준**이라 "족저근막염"을 던지면
    "대상포진"·"독감예방접종"이 딸려온다(건강 광고주가 같이 사는 키워드일 뿐 의미 연관이 아니다).
    의미는 자동완성이, 숫자는 검색광고 API가 준다. 그래서 자동완성으로 후보를 만들고 그 후보들의
    볼륨만 조회한다.
    """
    seed_override = seed_override or {}
    seeds: dict[str, list[str]] = {}
    fragments: list[str] = []
    for t in topics:
        if t in seed_override and seed_override[t]:
            seeds[t] = seed_override[t]
            continue
        s, frag = seed_for(t)
        if not s or frag:
            fragments.append(t)
            continue
        seeds[t] = [s]

    # 1. 자동완성으로 topic마다 "사람들이 실제로 치는 말" 후보를 모은다
    candidates: dict[str, list[str]] = {}
    for topic, base in seeds.items():
        pool = list(base)
        # 자동완성은 대표어 하나만 판다 — 후보가 이미 여럿이면 그 볼륨은 어차피 조회되고,
        # 자동완성의 역할은 "우리가 생각 못 한 표현"을 한 겹 더 얹는 것뿐이다(호출 수가 topic 수만큼 든다).
        pool += autocomplete(base[0])[:per_topic]
        candidates[topic] = list(dict.fromkeys(pool))

    # 2. 전체 후보를 한 번에 조회한다 — 같은 키워드가 여러 topic에 걸쳐도 호출은 한 번이면 된다
    every = list(dict.fromkeys(k for v in candidates.values() for k in v))
    vol = {r["keyword"]: r for r in volumes(every)}

    result: dict[str, dict] = {}
    for topic, pool in candidates.items():
        base = seeds[topic][0]
        rows = [vol[k.replace(" ", "")] for k in pool if k.replace(" ", "") in vol]
        rows.sort(key=lambda r: -r["total"])
        exact = vol.get(base.replace(" ", ""))
        result[topic] = {
            "seed": base,
            "volume": exact["total"] if exact else 0,
            "competition": exact["competition"] if exact else None,
            "related": [{"keyword": r["keyword"], "total": r["total"]} for r in rows],
        }
    return {"topics": result, "fragment_seeds": sorted(fragments)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topics", nargs="*", help="지정한 topic만")
    ap.add_argument("--all", action="store_true", help="게시분 포함 전체")
    ap.add_argument("--report", action="store_true", help="API 호출 없이 저장된 결과 출력")
    ap.add_argument("--seeds", help="topic → 후보 키워드 목록 JSON(스펙에서 대표어가 안 뽑히는 topic용)")
    ap.add_argument("--top", type=int, default=40)
    a = ap.parse_args()

    if a.report:
        data = json.loads(OUT.read_text(encoding="utf-8"))
    else:
        targets = sorted(a.topics) if a.topics else sorted(all_topics() if a.all else unposted())
        override = {}
        if a.seeds:
            raw = json.loads(Path(a.seeds).read_text(encoding="utf-8"))
            override = {t: v.get("candidates", []) for t, v in raw.items() if v.get("candidates")}
        print(f"{len(targets)}개 topic 조회 중… (외부 후보 {len(override)}개)")
        data = measure(targets, seed_override=override)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    rows = sorted(data["topics"].items(), key=lambda kv: -kv[1]["volume"])
    print(f"\n{'topic':14s} {'대표 검색어':16s} {'월 검색량':>9s}  쓸 만한 연관 검색어")
    for topic, v in rows[:a.top]:
        rel = useful_related(v["related"], v["seed"])[:3]
        shown = ", ".join(f"{r['keyword']}({r['total']:,})" for r in rel) or "-"
        print(f"{topic:14s} {v['seed'][:16]:16s} {v['volume']:9,d}  {shown[:60]}")
    zero = [t for t, v in rows if v["volume"] == 0]
    print(f"\n측정 {len(rows)}개 · 검색량 0 {len(zero)}개 · 대표어 추출 실패 {len(data['fragment_seeds'])}개")
    print(f"저장: {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
