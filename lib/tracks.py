# topic이 어느 트랙에 속하고 그 파일들이 어디 사는지를 한 자리에서 정한다.
#
# WHY(2026-09-24 사용자 "플랫폼은 같이 가져가도 폴더 하나 안에 있으면 다 어지러우니까 폴더 구조도
# 좀 잡아 따로 만들어"): 파이프라인은 하나로 공유하되 자리는 트랙별로 가른다. 기존 건강 topic
# 415개는 옮기지 않는다 — 다른 세션이 같은 폴더를 계속 쓰고 있어 대량 이동은 그 자체가 사고다.
# 새로 시작하는 트랙만 한 단계 접어 넣고, 경로 해석을 여기 한 곳에 모아 호출부가 접두어를
# 하드코딩하지 않게 한다.
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# dir: data/·output/ 밑에서 이 트랙이 쓰는 폴더 이름. None이면 기존처럼 평평하게 둔다.
# domain: 브랜드커넥트 상품 판정 기준(유아용품을 빼느냐 마느냐가 갈린다).
# section: 통합 작업대(deploy/작업/만사전.md)에 이 트랙 항목을 내보내는 섹션 이름(ai-video-network/tools/manjeon_sheet.py).
TRACKS: dict[str, dict] = {
    # 🚨 육아 트랙 브랜드는 「육아만사전」(2026-09-30 사용자 "건강만사전의 육아쪽은 육아만사전으로 명명하고 … 다 반영") —
    # 작업대 시트·엔딩 카드·해시태그·미션컨트롤 탭이 이 이름을 쓴다. 내부 식별자(폴더 `육아/`, topic `육아_N`)는 그대로.
    "육아": {"prefix": "육아_", "dir": "육아", "domain": "baby", "section": "baby", "stills": "baby",
           "brand": "육아만사전", "end_card": "육아만사전 · 더 많은 육아정보는 구독·좋아요·팔로우",
           # 업로드용 사본 자리 — 건강만사전(deploy/health-shorts/)과 섞이지 않게 따로 뗀다(2026-09-30 사용자
           # "deploy도 헬스숏츠가아니라 따로 뗴라고 분명히 말했찌?"). 댕냥사전이 deploy/dangnyang-shorts/인 것과 같은 식.
           "deploy": "parenting-shorts",
           # 네이버 블로그도 계정이 다르다(2026-10-01 사용자 "육아만사전은 chlwjddms16이 아니고 chlwjddms17이다 블로그")
           # — 브랜드커넥트 계정과 같은 chlwjddms17. 새 topic 캡션의 블로그 url은 여기서 가져온다.
           "naver_blog": "https://blog.naver.com/chlwjddms17",
           # 틱톡은 옛 세상만사전 일본어 계정을 육아만사전으로 바꿔 쓴다(2026-10-09 사용자 "일본어 올리던 계정이 육아만사전")
           "tiktok": "https://www.tiktok.com/@parentingdictionary"},
}
DEFAULT = {"prefix": "", "dir": None, "domain": "health", "section": "health", "stills": None,
           "brand": "건강만사전", "end_card": "건강만사전 · 더 많은 건강정보는 구독·좋아요·팔로우",
           "deploy": "health-shorts", "naver_blog": "https://blog.naver.com/chlwjddms16",
           # 틱톡 계정 주소(2026-10-14 사용자 "사이트 주소 바뀌었다" — 옛 세상만사전 한국어 계정 @nerdengineering을 이름 바꿈)
           "tiktok": "https://www.tiktok.com/@healthdictionary1"}


def _base(topic: str) -> str:
    """`육아_1/en`처럼 언어가 붙어 오는 자리가 있다 — 트랙 판정엔 topic 부분만 쓴다."""
    return topic.split("/", 1)[0]


def track_of(topic: str) -> str | None:
    base = _base(topic)
    return next((name for name, t in TRACKS.items() if base.startswith(t["prefix"])), None)


def spec_of(topic: str) -> dict:
    name = track_of(topic)
    return TRACKS[name] if name else DEFAULT


def domain_of(topic: str) -> str:
    return spec_of(topic)["domain"]


def data_dir(topic: str) -> Path:
    """data/ 밑 그 topic의 폴더. 언어 세그먼트는 그대로 이어붙인다(`data/육아/육아_1/en`)."""
    return _dir(ROOT / "data", topic)


def output_dir(topic: str) -> Path:
    return _dir(ROOT / "output", topic)


def _dir(base: Path, topic: str) -> Path:
    d = spec_of(topic)["dir"]
    return (base / d / topic) if d else (base / topic)


def track_dirs() -> list[str]:
    """data/·output/ 밑에서 topic이 아니라 트랙 폴더인 이름들 — topic 목록을 훑는 쪽이 건너뛰어야 한다."""
    return [t["dir"] for t in TRACKS.values() if t["dir"]]


def iter_topic_dirs(base: Path) -> list[Path]:
    """base(data/ 또는 output/) 밑의 topic 폴더 전부 — 트랙 폴더는 한 단계 더 들어가서 편다.

    `_audit`·`_retired`처럼 밑줄로 시작하는 살림 폴더는 topic이 아니라서 뺀다."""
    def usable(p: Path) -> bool:
        return p.is_dir() and not p.name.startswith(("_", "."))

    out: list[Path] = []
    for p in sorted(base.iterdir()):
        if not usable(p):
            continue
        if p.name in track_dirs():
            out += sorted(q for q in p.iterdir() if usable(q))
        else:
            out.append(p)
    return out


def glob_topic_files(base: Path, pattern: str) -> list[Path]:
    """`data/*/clip_requests.json`처럼 topic 폴더 밑 파일을 찾던 글롭의 트랙 대응판.

    트랙 폴더가 한 단계 깊으므로 `data/육아/*/clip_requests.json`도 같이 훑는다."""
    hits = list(base.glob(pattern))
    for d in track_dirs():
        hits += list((base / d).glob(pattern))
    return sorted(hits)


def stills_dir(track: str | None) -> Path:
    """그 트랙 캐논 스틸이 사는 곳. 기본 트랙은 지금까지처럼 stills/ 바로 밑이다."""
    base = ROOT / "assets_library" / "xray" / "stills"
    sub = (TRACKS[track] if track else DEFAULT)["stills"]
    return base / sub if sub else base


def track_of_path(path: Path) -> str | None:
    """파일 경로에서 트랙을 읽는다 — `data/육아/_shared/`처럼 topic 이름이 접두어를 안 가진 자리가 있다."""
    names = {t["dir"]: name for name, t in TRACKS.items() if t["dir"]}
    return next((names[q.name] for q in path.parents if q.name in names), None)


def topic_of_path(path: Path, base: Path) -> str | None:
    """`output/육아/육아_1/card_news` 같은 경로에서 **평평한 topic 이름**을 읽는다.

    🚨 topic 식별자에는 트랙 폴더를 넣지 않는다 — 이 저장소에서 `topic` 안의 `/`는 이미
    **언어**를 뜻한다(`가슴쓰림_1/en`). `육아/육아_1`로 부르면 dashboard·youtube_upload·
    fish_tts가 `육아_1`을 언어 코드로 읽는다. 트랙은 경로에만 있고 이름에는 없다."""
    try:
        parts = path.resolve().relative_to(base.resolve()).parts
    except ValueError:
        return None
    if not parts:
        return None
    return parts[1] if parts[0] in track_dirs() and len(parts) > 1 else parts[0]


# 🚨 사람이 작업하는 자리는 저장소 안이 아니라 `ai-video-network/deploy/작업/` 한 단계에 모은다
# (2026-09-25 사용자 "매번 폴더 막 들어가서 작업하기 존나 힘드니까 deploy 폴더 안에 … 프롬프트 넣을 md랑
# 스틸 넣을 공간만"). 브랜드마다 `<브랜드>.md` + `<브랜드>_스틸/`로 나란히 서고, 건강·육아·댕냥은 `만사전.md` 하나로 합쳤다(아래).
# worktree(~/Desktop/project/.worktrees/health-shorts/<설명>)에서 ROOT.parent를 쓰면 .worktrees 안에 가짜 deploy가 생겨
# 시트·업로드 파일이 엉뚱한 데로 갔다(2026-10-23 두 번) — .worktrees 밖에서 ai-video-network가 있는 조상을 찾는다
_PROJECT = next((p for p in ROOT.parents if ".worktrees" not in p.parts and (p / "ai-video-network").is_dir()), ROOT.parent)
DEPLOY_WORK = _PROJECT / "ai-video-network" / "deploy" / "작업"
DEPLOY_ROOT = _PROJECT / "ai-video-network" / "deploy"


def deploy_dir(topic: str) -> Path:
    """업로드용 사본 폴더 — 트랙마다 따로(`deploy/health-shorts/<topic>`, `deploy/parenting-shorts/<topic>`)."""
    return DEPLOY_ROOT / spec_of(topic)["deploy"] / _base(topic)


def deploy_roots() -> list[Path]:
    """트랙별 업로드 사본 폴더 전부 — 원본이 사라진 옛 사본을 훑을 때 쓴다."""
    return [DEPLOY_ROOT / t["deploy"] for t in [DEFAULT, *TRACKS.values()]]


# 🚨 건강·육아·댕냥은 작업대 하나(`만사전.md` + `만사전_스틸/`)를 같이 쓴다(2026-10-25 사용자 "어차피 동일한 컨셉으로
# 동일하게 가니까 … 굳이 떨어질 필요가 없을 듯"). 시트·스틸 폴더는 병합기 `ai-video-network/tools/manjeon_sheet.py`만 쓰고,
# 이 저장소 생성기는 트랙별 섹션(health·baby)만 내보낸다 — 댕냥 생성기(dangnyang-shorts)와 서로 덮어쓰지 않게.
MANJEON = _PROJECT / "ai-video-network" / "tools" / "manjeon_sheet.py"
MANJEON_REPO = "health-shorts"


def work_paths(track: str | None) -> tuple[Path, Path, Path]:
    """(작업지시 시트, 스틸 폴더, 완성클립 받는 곳) — 트랙과 상관없이 같은 통합 작업대. 스틸과 Flow 결과 mp4는
    같은 폴더에서 받는다(사람이 열 폴더를 하나로). 이름은 tests/test_xray_worksheet_path.py가 막는다."""
    stills = DEPLOY_WORK / "만사전_스틸"
    return DEPLOY_WORK / "만사전.md", stills, stills


def section_of(track: str | None) -> str:
    """통합 작업대에서 이 트랙 항목이 들어가는 섹션 이름(health / baby)."""
    return (TRACKS[track] if track else DEFAULT)["section"]


def brand(topic: str) -> str:
    """이 topic이 나가는 채널 브랜드 이름(건강만사전 / 육아만사전)."""
    t = track_of(topic)
    return (TRACKS[t] if t else DEFAULT)["brand"]


def tiktok_url(topic: str) -> str:
    """이 topic이 올라갈 틱톡 계정 주소(정하지 않았으면 빈 문자열)."""
    t = track_of(topic)
    return (TRACKS[t] if t else DEFAULT).get("tiktok", "")


def end_card_text(topic: str) -> str:
    """영상 엔딩 카드 문구 — 브랜드마다 다르다."""
    t = track_of(topic)
    return (TRACKS[t] if t else DEFAULT)["end_card"]
