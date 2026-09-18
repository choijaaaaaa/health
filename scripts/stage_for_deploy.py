#!/usr/bin/env python3
"""완성된 숏츠 영상 + 네이버 카드뉴스를 topic마다 `output/<topic>/` 깊은
곳까지 찾아 들어가지 않아도 되게, **ai-video-network가 쓰는 공용
`deploy/`** 한 곳에 모아준다(2026-09-18, "deploy에 health-shorts도 넣어줘 —
업로드 편해지게" 요청). 🚨 처음엔 `health-shorts/deploy/`라는 이 프로젝트
전용 폴더로 만들었다가 "여기다 넣으라는 게 아니라 원래 쓰던 그 deploy
폴더에 같이 넣으라는 거였다"는 정정을 받고 위치를 옮김 — 사용자는 이미
`ai-video-network/deploy/`를 업로드 작업 거점으로 매일 열어보고 있어서,
프로젝트가 다르다고 폴더를 또 하나 만들면 오히려 "어디 봐야 하지"가
늘어난다. health-shorts와 ai-video-network는 서로 다른 저장소·코드베이스지만
(이 워크스페이스 관례상 코드를 실시간 참조하지 않음), **`deploy/`라는
파일시스템 경로 하나는 공유**한다 — ai-video-network 쪽 `tools/
stage_for_deploy.py`가 쓰는 `<lang>/<topic>/` 구조를 그대로 따라서 ko
밑에 들어간다(health-shorts는 영상·카드뉴스 모두 ko 단일 언어라 그 외
언어 폴더는 안 씀).

- 영상: `deploy/ko/<topic>/shorts.mp4` ← `output/<topic>/shorts.mp4`
- 카드뉴스: `deploy/ko/<topic>/card_news/<파일명>` ← `output/<topic>/card_news/*.jpg`
  (2026-09-18 실측: shorts.mp4가 있는 topic은 전부 네이버용 카드뉴스가
  `output/<topic>/card_news/`에 flat으로 있다 — `ko/card_news`가 아님,
  그 하위 언어 폴더(en/ja/...)는 blog_seo용이라 대상 아님)

⚠️ **1biteinfo/worlds-figure와 폴더를 같이 쓰지만 서로의 topic을 모른다** —
충돌 방지는 이름 형태 차이에 의존한다: health-shorts topic은 항상
`<한글단어>_<숫자>`(예: `소화_5`), 1biteinfo 쪽 라벨은 `<두 자리 번호>
<한글라벨>`(예: `22 백두산 화산`, 숫자 뒤에 공백) — 밑줄 vs 공백이라 실제로
안 겹친다. 그래도 아래 "원본을 못 찾은 파일" 경고는 이 형태(`_TOPIC_NAME_RE`)에
맞는 폴더만 검사해서 1biteinfo 파일을 오탐하지 않는다.

사용법(health-shorts/ 루트에서):
    python3 scripts/stage_for_deploy.py            # 전체 스캔 후 복사/갱신
    python3 scripts/stage_for_deploy.py --dry-run   # 뭐가 복사될지만 미리 보기
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
DEPLOY_DIR = ROOT.parent / "ai-video-network" / "deploy" / "ko"

_TOPIC_NAME_RE = re.compile(r"^[가-힣]+_\d+$")


def _iter_topics() -> list[tuple[str, Path]]:
    """shorts.mp4가 있는 topic 폴더만 대상(카드뉴스만 있는 topic은 네이버
    블로그 쪽만 트랙이라 업로드 파일 자체가 없음 — 위 WHY 절 참고)."""
    if not OUTPUT_DIR.is_dir():
        return []
    found = []
    for topic_dir in sorted(OUTPUT_DIR.iterdir()):
        if not topic_dir.is_dir() or not (topic_dir / "shorts.mp4").is_file():
            continue
        found.append((topic_dir.name, topic_dir))
    return found


def _copy_if_newer(src: Path, dest: Path, dry_run: bool, seen: set[Path]) -> bool:
    seen.add(dest)
    if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return False
    rel_label = dest.relative_to(DEPLOY_DIR)
    if dry_run:
        print(f"[dry-run] {src} -> ko/{rel_label}")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"복사됨: ko/{rel_label}")
    return True


def stage(dry_run: bool) -> None:
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    seen: set[Path] = set()

    for topic, topic_dir in _iter_topics():
        dest_dir = DEPLOY_DIR / topic
        if _copy_if_newer(topic_dir / "shorts.mp4", dest_dir / "shorts.mp4", dry_run, seen):
            copied += 1
        else:
            skipped += 1

        card_dir = topic_dir / "card_news"
        if card_dir.is_dir():
            for jpg in sorted(card_dir.glob("*.jpg")):
                if _copy_if_newer(jpg, dest_dir / "card_news" / jpg.name, dry_run, seen):
                    copied += 1
                else:
                    skipped += 1

    stale = [] if dry_run else [
        p for p in DEPLOY_DIR.rglob("*")
        if p.is_file() and p not in seen and _TOPIC_NAME_RE.match(p.relative_to(DEPLOY_DIR).parts[0])
    ]
    if stale:
        print(f"\n⚠️  deploy/ko/에 원본을 못 찾은 health-shorts 파일 {len(stale)}개(삭제 안 함, 직접 확인할 것):")
        for p in stale:
            print("   -", p.relative_to(DEPLOY_DIR))

    print(f"\n완료 — 새로 복사/갱신 {copied}건, 이미 최신 {skipped}건")
    print(f"deploy 위치: {DEPLOY_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="복사 없이 뭐가 될지만 표시")
    args = parser.parse_args()
    stage(args.dry_run)
