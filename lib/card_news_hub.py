# 네이버 블로그 운영용 카드뉴스 허브 집계 스크립트. WHY(2026-08-14, "기존 헬스
# 숏츠 업로드용 UI에다가 고도화좀 해봐" — 건강/뷰티/육아/홈리빙/반려동물 5개
# 버티컬을 네이버 계정 2개(건강+뷰티, 육아+홈리빙+반려동물)로 묶어 운영할
# 계획): 각 버티컬은 독립 레포(`<이름>-content`)라 브라우저 fetch()로 형제
# 디렉터리를 직접 못 읽는다 — output/all_products.json을 index.html이 읽는
# 기존 패턴처럼, 이 스크립트가 5개 레포를 미리 스캔해 health-shorts
# output/card_news_hub.json 하나로 합쳐두고 card_news_hub.html이 그것만 읽는다.
#
# 사용법: python3 -m lib.card_news_hub
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# WHY dir_name=None이 health 자신인지: health-shorts는 다른 4개와 달리 형제
# 디렉터리가 아니라 이 스크립트가 실행되는 레포 자체다 — _find_sibling_project()
# 호출 없이 ROOT를 바로 쓴다.
# (레포 디렉터리명, 한글 표시 라벨, 네이버 계정 그룹명)
VERTICAL_REPOS: dict[str, tuple[str | None, str, str]] = {
    "health":      (None,                 "건강",     "건강+뷰티"),
    "cerulem":     ("cerulem-content",     "뷰티",     "건강+뷰티"),
    "littlebrook": ("littlebrook-content", "육아",     "육아+홈리빙+반려동물"),
    "nookery":     ("nookery-content",     "홈리빙",   "육아+홈리빙+반려동물"),
    "pawnest":     ("pawnest-content",     "반려동물", "육아+홈리빙+반려동물"),
}

# 그룹 표시 순서 고정(dict 삽입 순서에 기대지 않고 명시) — 화면에서 항상
# 건강+뷰티가 먼저 나오게.
GROUP_ORDER = ["건강+뷰티", "육아+홈리빙+반려동물"]


def _find_sibling_project(name: str) -> Path:
    """seo-blog/scripts/ingest_health_shorts.py의 동명 함수와 동일한 로직
    (조상 디렉터리 순회) — 이 파일도 워크트리에서 실행될 수 있어 고정 깊이
    계산은 위험하다."""
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor.parent / name
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent.parent / name


def _repo_root(dir_name: str | None) -> Path:
    return ROOT if dir_name is None else _find_sibling_project(dir_name)


def _topic_data_dir(repo_root: Path, topic: str) -> Path:
    """data/<topic>/ko/를 먼저 보고 없으면 data/<topic>/로 폴백 —
    lib/content_review.py의 _topic_dir()와 동일한 원칙(실측: health-shorts
    한국어 topic 대부분이 이제 nested ko/ 구조)."""
    base = repo_root / "data" / topic
    nested = base / "ko"
    return nested if nested.exists() else base


def _topic_output_dir(repo_root: Path, topic: str) -> Path:
    base = repo_root / "output" / topic
    nested = base / "ko"
    return nested if nested.exists() else base


def _naver_blog_caption(captions_path: Path) -> str | None:
    if not captions_path.exists():
        return None
    try:
        data = json.loads(captions_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    for p in data.get("platforms", []):
        if p.get("name") == "네이버 블로그":
            return p.get("caption") or None
    return None


def collect_items() -> dict:
    # WHY os.path.relpath 한 줄로 충분한지: health 자신(repo_root == ROOT)은
    # "output/<topic>/ko/dashboard.html"이, 형제 레포는
    # "../cerulem-content/output/.../dashboard.html"이 나와야 하는데,
    # repo_root가 ROOT든 형제 디렉터리든 relpath(dashboard, ROOT) 한 줄로
    # 둘 다 자동으로 맞다 — repo마다 분기할 필요 없음.

    groups: dict[str, dict[str, dict]] = {g: {} for g in GROUP_ORDER}
    for key, (dir_name, label, group_name) in VERTICAL_REPOS.items():
        groups.setdefault(group_name, {})
        groups[group_name][key] = {"key": key, "label": label, "items": []}

        repo_root = _repo_root(dir_name)
        data_dir = repo_root / "data"
        if not data_dir.is_dir():
            continue

        for topic_dir in sorted(p for p in data_dir.iterdir() if p.is_dir()):
            topic = topic_dir.name
            captions_path = _topic_data_dir(repo_root, topic) / "platform_captions.json"
            caption = _naver_blog_caption(captions_path)
            if not caption:
                continue

            dashboard = _topic_output_dir(repo_root, topic) / "dashboard.html"
            dashboard_path = os.path.relpath(dashboard, ROOT) if dashboard.exists() else None

            title = caption.split("\n", 1)[0].strip()
            groups[group_name][key]["items"].append({
                "topic": topic,
                "title": title,
                "caption": caption,
                "dashboard_path": dashboard_path,
            })

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "groups": [
            {"group_name": g, "verticals": list(groups[g].values())}
            for g in GROUP_ORDER
        ],
    }


def write_hub_json(out_path: Path | None = None) -> Path:
    out_path = out_path or (ROOT / "output" / "card_news_hub.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    hub = collect_items()
    out_path.write_text(json.dumps(hub, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_path


if __name__ == "__main__":
    path = write_hub_json()
    hub = json.loads(path.read_text(encoding="utf-8"))
    print(f"{path}에 저장했습니다.\n")
    for group in hub["groups"]:
        print(f"[{group['group_name']}]")
        for v in group["verticals"]:
            print(f"  {v['label']}({v['key']}): {len(v['items'])}건")
