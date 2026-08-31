# 렌더된 카드뉴스 이미지가 지금의 card_news_spec.json과 어긋나 있는지 훑는다.
#
# WHY(2026-08-31): 네이버에 실제로 올라가는 건 이미지다. 그런데 사실검증으로 spec을
# 고쳐도 재렌더를 빠뜨리면 **폐기된 주장이 이미지에는 그대로 남는다** — 실측에서
# 머리_2는 캡션·spec을 8/28에 새치 관련 근거 없는 주장(가공육·다크초콜릿)을 걷어내는
# 방향으로 다시 썼는데, 이미지는 8/27자 옛 내용 그대로였다. 텍스트만 고치고 끝내면
# 겉보기엔 해결된 것처럼 보이지만 독자가 보는 화면은 안 바뀐다.
#
# 또 topic을 리네임하면 옛 접두어 파일이 그대로 남는다(예: output/머리_2/card_news/
# 새치_1_00_표지.jpg). 게시할 때 잘못 집어가기 쉽고, 파일명으로 카드를 찾는 곳
# (lib/card_news_hub.py)에서도 어긋난다.
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# WHY 60초 여유: 같은 배치에서 spec 저장 → 렌더가 순서대로 일어나므로 초 단위 차이는
# 정상이다. 이걸 안 두면 방금 재렌더한 topic이 매번 걸린다.
MTIME_SLACK_SEC = 60


def _card_prefix(stem: str) -> str | None:
    """'<접두어>_NN_<섹션명>' 에서 접두어를 뽑는다. 접두어에도 '_'가 들어가므로
    끝에서부터 'NN_' 자리를 찾는다(그냥 앞에서 자르면 '고령_15'가 '고령'이 된다)."""
    m = re.search(r"^(.*)_(\d{2})_", stem)
    return m.group(1) if m else None


def scan(topics: list[str] | None = None) -> list[dict]:
    out = []
    for spec_path in sorted((ROOT / "data").glob("*/card_news_spec.json")):
        topic = spec_path.parts[-2]
        if topics and topic not in topics:
            continue
        card_dir = ROOT / "output" / topic / "card_news"
        jpgs = sorted(card_dir.glob("*.jpg")) if card_dir.is_dir() else []
        problems = []
        if not jpgs:
            out.append({"topic": topic, "problems": ["렌더된 카드 없음"]})
            continue
        newest = max(j.stat().st_mtime for j in jpgs)
        if spec_path.stat().st_mtime > newest + MTIME_SLACK_SEC:
            hours = int((spec_path.stat().st_mtime - newest) // 3600)
            problems.append(f"spec이 이미지보다 {hours}시간 최신 — 재렌더 안 됨")
        stale_prefix = sorted({p for j in jpgs
                               if (p := _card_prefix(j.stem)) and p != topic})
        if stale_prefix:
            problems.append(f"옛 접두어 파일 잔존 — {', '.join(stale_prefix)}")
        if problems:
            out.append({"topic": topic, "problems": problems})
    return out


def _cli() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="카드 이미지가 spec과 어긋났는지 검사")
    ap.add_argument("topics", nargs="*", help="생략 시 전체")
    ap.add_argument("--render-cmd", action="store_true", help="고칠 재렌더 명령을 출력")
    args = ap.parse_args()
    rows = scan(args.topics or None)
    for r in rows:
        print(f"⚠️  {r['topic']}")
        for p in r["problems"]:
            print(f"     {p}")
    print(f"\n확인 필요 {len(rows)}개")
    if args.render_cmd and rows:
        print("\n# 아래를 health-shorts 루트에서 실행하면 재렌더된다")
        for r in rows:
            t = r["topic"]
            print(f'rm -f "output/{t}/card_news"/*.jpg && '
                  f'.venv/bin/python3 lib/card_news.py "data/{t}/card_news_spec.json" '
                  f'assets_library/illust "output/{t}/card_news" "{t}" kor')


if __name__ == "__main__":
    _cli()
