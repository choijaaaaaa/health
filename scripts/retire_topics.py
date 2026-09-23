#!/usr/bin/env python3
"""심사에서 폐기(drop)로 판정된 topic을 격리한다 — 지우지 않고 `data/_retired/`로 옮긴다.

WHY(2026-09-23 사용자 "있던거에서 내용 고도화할게있으면 고도화해서 수정하고 안되겠다싶음 폐기하고"):
네이버 클립은 검색어로 노출되므로 **검색되지 않는 소재는 만들어도 묻힌다.** 제작비(원고·TTS·Flow 클립)를
쓸 가치가 없는 topic은 로스터에서 빼야 남은 것에 집중할 수 있다.

WHY 삭제가 아니라 이동인지: 판정은 검색량이라는 한 축으로 내린 것이라 뒤집힐 수 있다(계절이 돌아오거나
그 병이 뉴스를 타면 수요가 생긴다). `data/_retired/<topic>/`에 그대로 두면 언제든 되돌릴 수 있고,
`data/` 순회 코드는 `_`로 시작하는 폴더를 이미 건너뛰므로 파이프라인에서는 사라진 것과 같다.

⚠️ `output/<topic>/`(렌더 결과)과 mission-control 행은 건드리지 않는다 — 이미 게시된 것이 있으면
그 기록이 남아야 하고, 로컬 렌더물은 `prune_published.py`가 따로 정리한다.

    python3 scripts/retire_topics.py --from <판정 JSON>      # 미리보기
    python3 scripts/retire_topics.py --from <판정 JSON> --commit
    python3 scripts/retire_topics.py --restore <topic> ...   # 되돌리기
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RETIRED = DATA / "_retired"
LEDGER = RETIRED / "_ledger.json"


def _ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {}


def _has_global(topic: str) -> list[str]:
    """이 topic에 비-ko 언어 콘텐츠가 있는지. 있으면 폴더째 옮기면 안 된다.

    WHY(2026-09-23 실측): 심사는 **한국어 검색량** 한 축으로 내린 판정인데, 같은 폴더에 SEO 블로그
    (vernhaven)용 9개 언어 `blog_seo` 원고가 들어 있는 topic이 있다(미세먼지_12·피부_26). 폴더를
    옮기면 그쪽 재인입이 조용히 누락된다 — 영상 트랙에서만 빼고 폴더는 제자리에 둔다.
    """
    d = DATA / topic
    return sorted(x.name for x in d.iterdir()
                  if x.is_dir() and x.name != "ko" and (x / "platform_captions.json").exists())


def _mark_video_retired(topic: str, v: dict, commit: bool) -> None:
    for p in (DATA / topic / "ko" / "card_news_spec.json", DATA / topic / "card_news_spec.json"):
        if not p.exists():
            continue
        if commit:
            s = json.loads(p.read_text(encoding="utf-8"))
            s["video_retired"] = {k: v.get(k) for k in ("verdict", "into", "reason") if v.get(k)}
            p.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")
        return


def retire(verdicts: dict, commit: bool) -> None:
    drops = {t: v for t, v in verdicts.items() if v.get("verdict") in ("drop", "merge")}
    if not drops:
        print("폐기·통합 대상이 없습니다.")
        return
    ledger = _ledger()
    moved = marked = 0
    for topic, v in sorted(drops.items()):
        src = DATA / topic
        if not src.is_dir():
            print(f"  건너뜀(없음) {topic}")
            continue
        tag = "통합" if v["verdict"] == "merge" else "폐기"
        into = f" → {v.get('into')}" if v.get("into") else ""
        langs = _has_global(topic)
        if langs:
            print(f"  {tag}(영상만) {topic}{into}  ⚠️ 글로벌 {','.join(langs)} 있어 폴더 유지")
            _mark_video_retired(topic, v, commit)
            marked += 1
        else:
            print(f"  {tag} {topic}{into}  {v.get('reason', '')[:52]}")
            if commit:
                RETIRED.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src), str(RETIRED / topic))
            moved += 1
        if commit:
            ledger[topic] = {k: v.get(k) for k in ("verdict", "into", "reason") if v.get(k)}
            ledger[topic]["global_kept"] = bool(langs)
    if commit:
        RETIRED.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{'완료' if commit else '예정'} — 폴더 격리 {moved}개 · 영상만 제외 {marked}개"
          + ("" if commit else "  (실제 반영은 --commit)"))


def restore(topics: list[str]) -> None:
    ledger = _ledger()
    for topic in topics:
        src = RETIRED / topic
        if not src.is_dir():
            print(f"  없음 {topic}")
            continue
        shutil.move(str(src), str(DATA / topic))
        ledger.pop(topic, None)
        print(f"  복구 {topic}")
    LEDGER.write_text(json.dumps(ledger, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", help="판정 JSON({topic: {verdict, reason, into}})")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--restore", nargs="*", help="격리한 topic을 data/로 되돌린다")
    a = ap.parse_args()

    if a.restore:
        restore(a.restore)
        return
    if not a.src:
        raise SystemExit("--from 판정JSON 또는 --restore topic 중 하나가 필요합니다")
    retire(json.loads(Path(a.src).read_text(encoding="utf-8")), a.commit)


if __name__ == "__main__":
    main()
