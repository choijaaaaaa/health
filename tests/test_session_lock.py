# lib/session_lock.py 테스트. WHY: 동시 세션 락은 실서비스 사고(수면음식_1 덮어쓰기)를
# 막는 안전장치라 회귀가 나면 안 된다. 저장소에는 다른 세션들이 실제로 쓰는 진짜
# .claude-locks/가 있으므로, 모든 테스트는 monkeypatch로 LOCK_DIR을 tmp_path 하위로
# 리다이렉트한 뒤에만 acquire/release/list_locks를 호출한다 — 절대 진짜 락 디렉터리를
# 건드리지 않는다.
from __future__ import annotations

import json
import time

import pytest

from lib import session_lock


@pytest.fixture(autouse=True)
def isolated_lock_dir(tmp_path, monkeypatch):
    """모든 테스트에서 LOCK_DIR을 tmp_path 하위로 강제 리다이렉트."""
    monkeypatch.setattr(session_lock, "LOCK_DIR", tmp_path / ".claude-locks")
    return tmp_path


def test_check_returns_none_when_no_lock():
    assert session_lock.check("없는토픽") is None


def test_acquire_then_check_returns_lock_info():
    session_lock.acquire("토픽1", "작업 중")
    result = session_lock.check("토픽1")
    assert result is not None
    assert result["topic"] == "토픽1"
    assert result["note"] == "작업 중"
    assert "timestamp" in result


def test_acquire_twice_same_topic_raises_runtime_error():
    session_lock.acquire("토픽1", "첫 작업")
    with pytest.raises(RuntimeError):
        session_lock.acquire("토픽1", "두번째 작업")


def test_release_then_check_returns_none():
    session_lock.acquire("토픽1", "작업 중")
    session_lock.release("토픽1")
    assert session_lock.check("토픽1") is None


def test_release_nonexistent_lock_does_not_raise():
    # 파일이 없으면 그냥 통과하는 구조 (release()가 존재 여부를 확인 후 unlink)
    session_lock.release("존재안하는토픽")


def test_check_returns_none_for_stale_lock():
    session_lock.LOCK_DIR.mkdir(exist_ok=True)
    stale_timestamp = time.time() - session_lock.STALE_SECONDS - 10
    lock_path = session_lock._lock_path("오래된토픽")
    lock_path.write_text(
        json.dumps({"topic": "오래된토픽", "timestamp": stale_timestamp, "note": "옛날 작업"}, ensure_ascii=False)
    )
    assert session_lock.check("오래된토픽") is None


def test_list_locks_returns_all_topics_with_stale_flag():
    session_lock.acquire("최근토픽", "지금 작업 중")

    session_lock.LOCK_DIR.mkdir(exist_ok=True)
    stale_timestamp = time.time() - session_lock.STALE_SECONDS - 10
    session_lock._lock_path("오래된토픽").write_text(
        json.dumps({"topic": "오래된토픽", "timestamp": stale_timestamp, "note": "옛날 작업"}, ensure_ascii=False)
    )

    locks = session_lock.list_locks()
    by_topic = {entry["topic"]: entry for entry in locks}

    assert set(by_topic.keys()) == {"최근토픽", "오래된토픽"}
    assert by_topic["최근토픽"]["stale"] is False
    assert by_topic["오래된토픽"]["stale"] is True


def test_different_topics_do_not_interfere():
    session_lock.acquire("토픽A", "A 작업")
    assert session_lock.check("토픽B") is None
    session_lock.acquire("토픽B", "B 작업")
    assert session_lock.check("토픽A") is not None
    assert session_lock.check("토픽B") is not None
