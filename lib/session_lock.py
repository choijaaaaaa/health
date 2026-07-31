# 동시 Claude Code 세션이 같은 로컬 저장소를 쓸 때 topic 단위로 충돌을 막는 락.
# WHY: 여러 세션이 같은 topic을 서로 모르고 동시에 작업해서 캐릭터 일러스트·카드뉴스가
# 서로 덮어써지는 사고가 실제로 있었다(2026-07-31, 수면음식_1 topic에서 발생).
# git 커밋 단위가 아니라 "지금 이 순간 디스크에 손대고 있는지"를 보는 락이라 커밋 대상이
# 아니고(.gitignore 처리), 같은 디스크를 보는 세션끼리는 파일 하나로 바로 조율된다.
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

LOCK_DIR = Path(__file__).resolve().parent.parent / ".claude-locks"
STALE_SECONDS = 3 * 60 * 60  # 3시간 지나면 죽었거나 잊힌 락으로 간주하고 무시


def _lock_path(topic: str) -> Path:
    return LOCK_DIR / f"{topic}.lock"


def check(topic: str) -> dict | None:
    """활성 락이 있으면 정보를, 없거나 오래됐으면 None을 반환."""
    p = _lock_path(topic)
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    age = time.time() - data["timestamp"]
    if age > STALE_SECONDS:
        return None
    data["age_seconds"] = int(age)
    return data


def acquire(topic: str, note: str) -> None:
    existing = check(topic)
    if existing:
        raise RuntimeError(f"이미 활성 락이 있습니다: {json.dumps(existing, ensure_ascii=False)}")
    LOCK_DIR.mkdir(exist_ok=True)
    _lock_path(topic).write_text(
        json.dumps({"topic": topic, "timestamp": time.time(), "note": note}, ensure_ascii=False)
    )


def release(topic: str) -> None:
    p = _lock_path(topic)
    if p.exists():
        p.unlink()


def list_locks() -> list[dict]:
    LOCK_DIR.mkdir(exist_ok=True)
    out = []
    for f in LOCK_DIR.glob("*.lock"):
        data = json.loads(f.read_text())
        age = time.time() - data["timestamp"]
        data["age_seconds"] = int(age)
        data["stale"] = age > STALE_SECONDS
        out.append(data)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: session_lock.py {check|acquire|release|list} <topic> [note]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "list":
        for entry in list_locks():
            status = "STALE(무시)" if entry["stale"] else "ACTIVE"
            print(f"{entry['topic']}: {status} ({entry['age_seconds']}초 전) - {entry.get('note', '')}")
        sys.exit(0)

    topic = sys.argv[2]
    if cmd == "check":
        result = check(topic)
        print(json.dumps(result, ensure_ascii=False) if result else "UNLOCKED")
    elif cmd == "acquire":
        note = sys.argv[3] if len(sys.argv) > 3 else ""
        acquire(topic, note)
        print(f"락 생성 완료: {topic}")
    elif cmd == "release":
        release(topic)
        print(f"락 해제 완료: {topic}")
    else:
        print("usage: session_lock.py {check|acquire|release|list} <topic> [note]")
        sys.exit(1)
