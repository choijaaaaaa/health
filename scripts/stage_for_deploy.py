#!/usr/bin/env python3
"""완성된 숏츠 영상을 topic마다 `output/<topic>/shorts.mp4` 깊은 곳까지
찾아 들어가지 않아도 되게, `deploy/` 한 곳에 topic명 그대로 모아준다
(2026-09-18, "deploy에 health-shorts도 넣어줘 — 업로드 편해지게" 요청 —
ai-video-network/tools/stage_for_deploy.py와 동일한 패턴을 이식).

health-shorts topic 폴더명(예: "소화_5")이 이미 그 자체로 사람이 알아볼 수
있는 한글이라 1biteinfo처럼 별도 한글 라벨 변환이 필요 없다 — 그래서 이
스크립트는 그쪽보다 훨씬 단순하다. 영상 트랙은 ko 단일 언어만 존재하므로
(card_news처럼 언어별 서브폴더가 없음, 2026-09-18 실측 확인) 언어 폴더
구분도 없이 `deploy/<topic>/shorts.mp4` 평평한 구조로 복사한다.

사용법(health-shorts/ 루트에서):
    python3 scripts/stage_for_deploy.py            # 전체 스캔 후 복사/갱신
    python3 scripts/stage_for_deploy.py --dry-run   # 뭐가 복사될지만 미리 보기
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "output"
DEPLOY_DIR = ROOT / "deploy"


def _iter_shorts() -> list[tuple[str, Path]]:
    if not OUTPUT_DIR.is_dir():
        return []
    found = []
    for topic_dir in sorted(OUTPUT_DIR.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
            continue
        mp4 = topic_dir / "shorts.mp4"
        if mp4.is_file():
            found.append((topic_dir.name, mp4))
    return found


def stage(dry_run: bool) -> None:
    DEPLOY_DIR.mkdir(exist_ok=True)
    copied = skipped = 0
    seen: set[Path] = set()

    for topic, mp4 in _iter_shorts():
        dest_dir = DEPLOY_DIR / topic
        dest_path = dest_dir / "shorts.mp4"
        seen.add(dest_path)
        if dest_path.exists() and dest_path.stat().st_mtime >= mp4.stat().st_mtime:
            skipped += 1
            continue
        rel_label = f"{topic}/shorts.mp4"
        if dry_run:
            print(f"[dry-run] {mp4} -> {rel_label}")
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(mp4, dest_path)
            print(f"복사됨: {rel_label}")
        copied += 1

    stale = [] if dry_run or not DEPLOY_DIR.is_dir() else [
        p for p in DEPLOY_DIR.rglob("*") if p.is_file() and p not in seen
    ]
    if stale:
        print(f"\n⚠️  deploy/에 원본을 못 찾은 파일 {len(stale)}개(삭제 안 함, 직접 확인할 것):")
        for p in stale:
            print("   -", p.relative_to(DEPLOY_DIR))

    print(f"\n완료 — 새로 복사/갱신 {copied}건, 이미 최신 {skipped}건")
    print(f"deploy 위치: {DEPLOY_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="복사 없이 뭐가 될지만 표시")
    args = parser.parse_args()
    stage(args.dry_run)
