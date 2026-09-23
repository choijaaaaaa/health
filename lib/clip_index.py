# 클립 색인 — "이 장면을 어떤 주제에 쓸 수 있나"를 언어로 적어두고 검색한다.
#
# WHY(2026-09-24 사용자 "그 행동이나 기전들을 충분히 판단해서 어떤 주제에서도 매핑할 수 있어야 한다"):
# 지금까지는 topic을 쓸 때마다 에이전트가 ffmpeg로 프레임을 뽑아 보고 판단했다. 같은 클립을 매번 다시
# 보면서 매번 다르게 판단하고, 본 결과가 어디에도 안 남았다. 이름은 못 믿는다 —
# `m_follicle_weakening`은 난포가 아니라 모낭이고 `m_growth_arrest`는 무릎 성장판이다.
#
# 그래서 한 번만 제대로 보고 **`fits`(쓸 수 있는 맥락)** 을 적어둔다. 한 클립은 여러 주제에 매핑된다:
# `m_osmotic_water_pull`은 설사·복부팽만·탈수·다뇨·부종 어디에나 쓰인다.
#
#   python3 -m lib.clip_index --for 설사 탈모        # 이 증상에 쓸 수 있는 클립
#   python3 -m lib.clip_index --show m_inflammation  # 한 클립이 뭘 담았나
#   python3 -m lib.clip_index --missing              # 아직 기술 안 된 클립
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
INDEX = XRAY / "clip_index.json"
FRAMES = XRAY / "catalog"
OUT = XRAY / "output"


def load() -> dict:
    return json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}


def search(terms: list[str]) -> list[tuple[int, str, dict]]:
    """맥락·설명에 검색어가 많이 맞을수록 위로. 이름은 못 믿으므로 **낮게** 친다."""
    idx = load()
    hits = []
    for name, e in idx.items():
        hay_fits = " ".join(e.get("fits", []))
        hay_seen = e.get("seen", "")
        score = 0
        for t in terms:
            if t in hay_fits:
                score += 3            # 쓸 수 있는 맥락에 직접 적힌 것이 가장 강하다
            elif t in hay_seen:
                score += 2            # 화면에 실제로 보이는 것
            elif t in name:
                score += 1            # 이름만 맞는 건 오히려 함정인 적이 많았다
        if score:
            hits.append((score, name, e))
    return sorted(hits, key=lambda x: -x[0])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--for", dest="terms", nargs="*", help="이 증상·상황에 쓸 수 있는 클립")
    ap.add_argument("--show", help="클립 하나의 설명")
    ap.add_argument("--missing", action="store_true", help="아직 기술 안 된 클립")
    ap.add_argument("--limit", type=int, default=12)
    a = ap.parse_args()
    idx = load()

    if a.show:
        e = idx.get(a.show)
        if not e:
            raise SystemExit(f"{a.show}: 색인에 없음 — 프레임은 {FRAMES / (a.show + '.jpg')}")
        print(f"{a.show} [{e.get('kind','?')}]")
        print(f"  보이는 것: {e.get('seen','')}")
        print(f"  쓸 수 있는 곳: {', '.join(e.get('fits', []))}")
        if e.get("avoid"):
            print(f"  ⚠️ 주의: {e['avoid']}")
        return

    if a.missing:
        have = set(idx)
        allc = {p.stem for p in OUT.glob("*.mp4")}
        left = sorted(allc - have)
        print(f"미기술 {len(left)} / 전체 {len(allc)}")
        for x in left[:60]:
            print("  ", x)
        return

    if not a.terms:
        kinds: dict[str, int] = {}
        for e in idx.values():
            kinds[e.get("kind", "?")] = kinds.get(e.get("kind", "?"), 0) + 1
        print(f"색인 {len(idx)}종 — {kinds}")
        return

    for score, name, e in search(a.terms)[:a.limit]:
        print(f"[{score:2d}] {name:34s} {e.get('seen','')[:56]}")
        print(f"     └ {', '.join(e.get('fits', []))[:88]}")


if __name__ == "__main__":
    main()
