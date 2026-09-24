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
# work: 미드저니·Flow 작업 자리. 트랙마다 따로 둬야 시트 번호가 섞이지 않는다.
TRACKS: dict[str, dict] = {
    "육아": {"prefix": "육아_", "dir": "육아", "domain": "baby", "work": "작업_육아", "stills": "baby"},
}
DEFAULT = {"prefix": "", "dir": None, "domain": "health", "work": "작업", "stills": None}


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
    out: list[Path] = []
    for p in sorted(base.iterdir()):
        if not p.is_dir() or p.name.startswith("_") or p.name.startswith("."):
            continue
        if p.name in track_dirs():
            out += sorted(q for q in p.iterdir() if q.is_dir())
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


def work_paths(track: str | None) -> tuple[Path, Path, Path]:
    """(작업지시 시트, 스틸 폴더, 완성클립 받는 곳). 이름은 tests/test_xray_worksheet_path.py가 막는다."""
    work = ROOT / "assets_library" / "xray" / (TRACKS[track]["work"] if track else DEFAULT["work"])
    return work / "0_작업지시.md", work / "1_스틸", work / "2_완성클립"
