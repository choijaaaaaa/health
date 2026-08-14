# 네이버 블로그 운영용 카드뉴스 허브 집계 스크립트. WHY(2026-08-14, "기존 헬스
# 숏츠 업로드용 UI에다가 고도화좀 해봐" → 이어서 "건강 / 육아+반려동물 / 경제
# 이렇게 세 쌍으로 네이버 블로그 계정 세 개로 운영하기로 결정" — 최초엔
# 건강+뷰티 / 육아+홈리빙+반려동물 2개 계정 기준으로 짰다가 계정 구성이
# 3개로 바뀌면서 그룹을 다시 나눔): 각 버티컬은 독립 레포(`<이름>-content`)라
# 브라우저 fetch()로 형제 디렉터리를 직접 못 읽는다 — output/all_products.json을
# index.html이 읽는 기존 패턴처럼, 이 스크립트가 형제 레포들을 미리 스캔해
# health-shorts output/card_news_hub.json 하나로 합쳐두고 index.html의
# "카드뉴스 허브" 탭이 그것만 읽는다.
#
# 사용법: python3 -m lib.card_news_hub
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# WHY dir_name=None이 health 자신인지: health-shorts는 다른 버티컬과 달리
# 형제 디렉터리가 아니라 이 스크립트가 실행되는 레포 자체다 —
# _find_sibling_project() 호출 없이 ROOT를 바로 쓴다.
#
# ⚠️ 뷰티(cerulem)·홈리빙(nookery)은 지금 활성 네이버 계정 3개
# (건강/육아+반려동물/경제) 어디에도 배정되지 않아 이 dict에서 제외했다 —
# 재테크(fiscallo)가 2번째 라운드까지 계정 없이 빠져있던 것과 같은 원칙
# ("계정이 없으면 그룹에 안 넣는다"). 두 버티컬용 계정이 나중에 생기면
# VERTICAL_REPOS에 다시 추가할 것 — 레포 자체(cerulem-content/
# nookery-content)는 안 건드렸으니 데이터는 그대로 있다.
# (레포 디렉터리명, 한글 표시 라벨, 네이버 계정 그룹명)
#
# ⚠️ health/jp_review는 여기서 뺐다(2026-08-14, "카드뉴스허브자체가 내가
# 원하던 바랑 다르게 들어갔네... 부문별로 탭을 나눠서 하는게 나을듯") —
# 건강은 이미 자기 topic마다 완전한 대시보드(완료 체크·플랫폼 카드)가
# 있어서 "숏츠·전체 목록" 탭(건강으로 개명)이 그대로 그 역할을 하고,
# jp_review도 같은 이유로 자기 전용 대시보드+탭을 새로 만들어 완전히
# 분리했다(자세한 내용은 jp-review-shorts CLAUDE.md 참고) — 이 스크립트는
# 이제 "완전한 대시보드가 없는" 신규 버티컬(littlebrook/pawnest/fiscallo)만
# 담당한다. 영상 지원(video_path)도 그 두 버티컬과 함께 제거 — 실제로 쓰던
# 버티컬이 없어져서 죽은 코드로 남기지 않음.
VERTICAL_REPOS: dict[str, tuple[str | None, str, str]] = {
    "littlebrook": ("littlebrook-content", "육아",     "육아+반려동물"),
    "pawnest":     ("pawnest-content",     "반려동물", "육아+반려동물"),
    "fiscallo":    ("fiscallo-content",    "경제",     "경제"),
}

# 그룹 표시 순서 고정(dict 삽입 순서에 기대지 않고 명시).
GROUP_ORDER = ["육아+반려동물", "경제"]


def _find_sibling_project(name: str) -> Path:
    """seo-blog/scripts/ingest_health_shorts.py의 동명 함수와 동일한 로직
    (조상 디렉터리 순회) — 이 파일도 워크트리에서 실행될 수 있어 고정 깊이
    계산은 위험하다.

    WHY verticals/ 폴백이 필요한지(2026-08-14, "헬스숏츠 빼고는 전부 다
    한번 병합좀 해봐"): pawnest-content 등 형제 버티컬 레포들이
    `~/Desktop/project/`에서 `~/Desktop/project/verticals/`로 한 단계
    더 들어갔다 — health-shorts 자신은 옮기지 않았으므로(사용자 명시
    제외) 이 스크립트의 조상 경로엔 `verticals` 세그먼트가 전혀 없어
    위 조상 순회만으론 못 찾는다(반대 방향, 즉 옮겨진 레포가 옮기지 않은
    health-shorts를 찾는 경우는 옮겨진 쪽 조상 체인에 verticals가 이미
    포함돼 있어 그대로 잘 찾아진다 — 이 쪽만 별도 처리 필요)."""
    for ancestor in Path(__file__).resolve().parents:
        candidate = ancestor.parent / name
        if candidate.is_dir():
            return candidate
        verticals_candidate = ancestor.parent / "verticals" / name
        if verticals_candidate.is_dir():
            return verticals_candidate
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


def _naver_images(images_path: Path, repo_root: Path, topic: str) -> list[dict]:
    """번호 마커별 이미지 목록(2026-08-14, "이미지도 카드뉴스처럼 번호별로
    관리되게" 요청). 건강은 이 파일이 없다(card_news 폴더의 실제 렌더링된
    jpg를 쓰므로 collect_items()에서 별도 처리) — 3개 신규 버티컬(fiscallo/
    littlebrook/pawnest)은 카드뉴스 렌더링 파이프라인 자체가 없어(각 레포
    CLAUDE.md "이 프로젝트가 아닌 것" 절) 대신 Pexels 실사진 URL을 마커별로
    매핑해둔 이 JSON을 쓴다. 파일이 없으면(아직 이미지 소싱 전인 topic)
    빈 리스트 — index.html 쪽에서 "이미지 없음"으로 자연스럽게 처리된다.

    ⚠️ url이 http(s)로 시작 안 하면 로컬 파일명으로 보고 그 topic의
    output 디렉터리 기준 상대경로로 변환한다(2026-08-14, jp_review처럼
    Pexels 대신 실제 영상에서 뽑은 프레임 이미지를 쓰는 버티컬 대응) —
    naver_images.json엔 파일명만 적으면 되고, ROOT 기준 상대경로 계산은
    여기서 자동으로 처리된다."""
    if not images_path.exists():
        return []
    try:
        data = json.loads(images_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    images = []
    for d in data:
        url = d.get("url", "")
        if not url:
            continue
        if url.startswith("http://") or url.startswith("https://"):
            images.append({"marker": d.get("marker", ""), "url": url})
        else:
            local_path = _topic_output_dir(repo_root, topic) / url
            images.append({"marker": d.get("marker", ""), "url": os.path.relpath(local_path, ROOT)})
    return images


def _health_card_news_images(repo_root: Path, topic: str) -> list[dict]:
    """건강 topic의 실제 렌더링된 카드뉴스 jpg(00_표지, 01_..., ...)를
    번호 마커 목록으로 변환 — 신규 버티컬의 _naver_images()와 같은 모양
    ({marker, url})으로 맞춰서 index.html이 포맷 구분 없이 같은 렌더러로
    보여줄 수 있게 한다. url은 http(s)가 아니라 ROOT 기준 상대경로(로컬
    파일) — dashboard_path와 동일한 원리로 index.html이 file:// 또는 로컬
    서버에서 열리는 걸 전제한다."""
    card_news_dir = _topic_output_dir(repo_root, topic) / "card_news"
    if not card_news_dir.is_dir():
        return []
    images = []
    for jpg in sorted(card_news_dir.glob("*.jpg")):
        # "<topic>_00_표지.jpg" 또는 "00_표지.jpg" 둘 다 지원 — 파일명에서
        # 숫자_라벨 부분만 마커로 뽑는다(접두어 유무 무관하게 정규식 없이
        # "마지막에 나오는 NN_라벨" 패턴만 사용).
        stem = jpg.stem
        parts = stem.split("_")
        # 두 자리 숫자 조각(00, 01, ...)을 찾아 그 지점부터를 "NN · 라벨"
        # 마커로 삼는다 — naver_images.json의 마커 형식과 동일하게 맞춰서
        # index.html이 포맷 구분 없이 같은 방식으로 렌더링할 수 있게 한다.
        marker = stem
        for i, part in enumerate(parts):
            if len(part) == 2 and part.isdigit():
                marker = f"{part} · {'_'.join(parts[i + 1:])}"
                break
        images.append({"marker": marker, "url": os.path.relpath(jpg, ROOT)})
    return images


def collect_items() -> dict:
    # WHY os.path.relpath 한 줄로 충분한지: health 자신(repo_root == ROOT)은
    # "output/<topic>/ko/dashboard.html"이, 형제 레포는
    # "../cerulem-content/output/.../dashboard.html"이 나와야 하는데,
    # repo_root가 ROOT든 형제 디렉터리든 relpath(dashboard, ROOT) 한 줄로
    # 둘 다 자동으로 맞다 — repo마다 분기할 필요 없음.

    groups: dict[str, dict[str, dict]] = {g: {} for g in GROUP_ORDER}
    for key, repo_spec in VERTICAL_REPOS.items():
        dir_name, label, group_name = repo_spec[0], repo_spec[1], repo_spec[2]
        video_filename = repo_spec[3] if len(repo_spec) > 3 else None
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

            topic_output_dir = _topic_output_dir(repo_root, topic)
            dashboard = topic_output_dir / "dashboard.html"
            dashboard_path = os.path.relpath(dashboard, ROOT) if dashboard.exists() else None
            images = _naver_images(captions_path.parent / "naver_images.json", repo_root, topic)
            if not images and dir_name is None:
                images = _health_card_news_images(repo_root, topic)

            video_path = None
            if video_filename:
                video_file = topic_output_dir / video_filename
                if video_file.exists():
                    video_path = os.path.relpath(video_file, ROOT)

            title = caption.split("\n", 1)[0].strip()
            groups[group_name][key]["items"].append({
                "topic": topic,
                "title": title,
                "caption": caption,
                "dashboard_path": dashboard_path,
                "images": images,
                "video_path": video_path,
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
