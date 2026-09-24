#!/usr/bin/env python3
"""완성된 숏츠 영상 + 네이버 카드뉴스를 topic마다 `output/<topic>/` 깊은
곳까지 찾아 들어가지 않아도 되게, **ai-video-network가 쓰는 공용
`deploy/`** 안의 이 프로젝트 전용 서브폴더에 모아준다(2026-09-18, "deploy에
health-shorts도 넣어줘 — 업로드 편해지게" 요청).

위치가 두 번 바뀌었다 — 경위를 남겨서 세 번째로 또 틀리지 않게 한다:
1. 처음엔 `health-shorts/deploy/`(이 프로젝트 전용 새 폴더)로 만들었다가
   "원래 쓰던 그 deploy 폴더에 같이 넣으라는 거였다"는 정정을 받음(사용자는
   `ai-video-network/deploy/`를 이미 매일 열어보는 업로드 작업 거점으로 씀).
2. 그래서 `ai-video-network/deploy/ko/<topic>/`에 1biteinfo/worlds-figure
   topic들과 **같은 계층**으로 섞어 넣었다가, "영상 플랫폼 애들이랑 섞이면
   보기 어렵다 — 헬스숏츠 폴더링 따로 해야지"로 다시 정정받음.
3. **최종**: `ai-video-network/deploy/health-shorts/<topic>/` — 같은
   `deploy/` 트리 안에 있어서 한 곳만 보면 되는 건 유지하면서, 이 프로젝트
   topic들은 전용 서브폴더로 시각적으로 분리됨. 1biteinfo/worlds-figure
   topic과 이름이 겹칠 걱정도 이제 없음(서로 다른 폴더).

- 영상: `deploy/health-shorts/<topic>/shorts.mp4` ← `output/<topic>/shorts.mp4`
- 카드뉴스: `deploy/health-shorts/<topic>/card_news/<파일명>` ←
  `output/<topic>/card_news/*.jpg` (2026-09-18 실측: shorts.mp4가 있는 topic은
  전부 네이버용 카드뉴스가 `output/<topic>/card_news/`에 flat으로 있다 —
  `ko/card_news`가 아님, 그 하위 언어 폴더(en/ja/...)는 blog_seo용이라 대상 아님)

사용법(health-shorts/ 루트에서):
    python3 scripts/stage_for_deploy.py            # 전체 스캔 후 복사/갱신
    python3 scripts/stage_for_deploy.py --dry-run   # 뭐가 복사될지만 미리 보기
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks  # noqa: E402

OUTPUT_DIR = ROOT / "output"
DEPLOY_DIR = ROOT.parent / "ai-video-network" / "deploy" / "health-shorts"


def _iter_topics() -> list[tuple[str, Path]]:
    """shorts.mp4가 있는 topic 폴더만 대상(카드뉴스만 있는 topic은 네이버
    블로그 쪽만 트랙이라 업로드 파일 자체가 없음 — 위 WHY 절 참고).

    🚨 `iter_topic_dirs`로 도는 이유: `output/`를 1단 iterdir하면 트랙 폴더
    (`output/육아/`)가 topic으로 잡히고 그 밑에 shorts.mp4가 없어서 육아 트랙이
    **통째로, 에러도 경고도 없이** 빠진다. 돌려주는 이름은 여전히 평평한
    topic(`육아_1`)이라 배포 폴더는 지금처럼 평평하게 유지된다 —
    `scripts/cleanup_deploy.py`가 Supabase에서 온 평평한 이름으로 같은 자리를 지운다."""
    if not OUTPUT_DIR.is_dir():
        return []
    found = []
    for topic_dir in tracks.iter_topic_dirs(OUTPUT_DIR):
        if not (topic_dir / "shorts.mp4").is_file():
            continue
        found.append((topic_dir.name, topic_dir))
    return found


def _copy_if_newer(src: Path, dest: Path, dry_run: bool, seen: set[Path]) -> bool:
    seen.add(dest)
    if dest.exists() and dest.stat().st_mtime >= src.stat().st_mtime:
        return False
    rel_label = dest.relative_to(DEPLOY_DIR)
    if dry_run:
        print(f"[dry-run] {src} -> health-shorts/{rel_label}")
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"복사됨: health-shorts/{rel_label}")
    return True


def _final_video(topic_dir: Path) -> Path:
    """올릴 영상 파일. 🚨 반투명 인체 포맷은 `shorts.mp4`가 **칠판만 있는 중간본**이고,
    도입부 Flow와 기전 클립까지 얹은 최종본은 `shorts_xray_test.mp4`다(scripts/xray_splice.py 출력).
    이걸 구분하지 않으면 업로드 폴더에 반쪽짜리가 올라간다(2026-09-23 실측).
    파일명의 `_test`는 시험 단계 이름이 그대로 굳은 것이라 올릴 때 `shorts.mp4`로 바꿔 담는다."""
    xray = topic_dir / "shorts_xray_test.mp4"
    plain = topic_dir / "shorts.mp4"
    if xray.is_file() and xray.stat().st_mtime >= plain.stat().st_mtime:
        return xray
    return plain


def stage(dry_run: bool) -> None:
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    copied = skipped = 0
    seen: set[Path] = set()

    for topic, topic_dir in _iter_topics():
        dest_dir = DEPLOY_DIR / topic
        if _copy_if_newer(_final_video(topic_dir), dest_dir / "shorts.mp4", dry_run, seen):
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

    # WHY 이름 형태 체크 없이 바로 rglob 전체를 stale로 보는지: 이 폴더
    # (deploy/health-shorts/) 자체가 이 프로젝트 전용이라 다른
    # 프로젝트(1biteinfo 등) 파일이 여기 섞여 들어올 일이 없다 — 예전엔
    # deploy/ko/ 최상위를 같이 써서 이름 형태(밑줄 vs 공백)로 구분해야
    # 했지만, 전용 서브폴더로 분리된 뒤로는 불필요해짐.
    stale = [] if dry_run else [
        p for p in DEPLOY_DIR.rglob("*") if p.is_file() and p not in seen
    ]
    # 🚨 카드뉴스는 원본이 사라진 파일을 **지운다.** 파일명이 항목 이름이라 원고를 고치면
    # ("매운 음식" → "빈속 커피") 옛 카드가 새 카드와 나란히 남고, 업로드할 때 둘 다 집어
    # 올리게 된다(2026-09-24 실측: 소화_14 deploy에 "매운 음식" 카드 2장이 남아 있었다).
    # 영상·그 밖의 파일은 예전처럼 알리기만 한다 — 이름이 안 바뀌므로 남아 있으면 다른 사정이다.
    removed = [p for p in stale if p.parent.name == "card_news"]
    for p in removed:
        p.unlink()
    if removed:
        print(f"\n옛 카드뉴스 {len(removed)}장 삭제(원고가 바뀌어 항목명이 달라진 것):")
        for p in removed:
            print("   -", p.name)
    rest = [p for p in stale if p not in removed]
    if rest:
        print(f"\n⚠️  deploy/health-shorts/에 원본을 못 찾은 파일 {len(rest)}개(삭제 안 함, 직접 확인할 것):")
        for p in rest:
            print("   -", p.relative_to(DEPLOY_DIR))

    print(f"\n완료 — 새로 복사/갱신 {copied}건, 이미 최신 {skipped}건")
    print(f"deploy 위치: {DEPLOY_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="복사 없이 뭐가 될지만 표시")
    args = parser.parse_args()
    stage(args.dry_run)
