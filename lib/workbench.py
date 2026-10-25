# 통합 작업대(deploy/작업/만사전.md) 병합기와 주고받는 자리. WHY: 시트·스틸 폴더는 병합기만 쓰고 이 저장소는 섹션만 낸다.
"""건강·육아 생성기·받기 스크립트가 `ai-video-network/tools/manjeon_sheet.py`를 부르는 얇은 층.

병합기는 다른 저장소 파일이라 import하지 않고 subprocess로 부른다(표준 라이브러리만 쓰는 스크립트라 이 venv python으로 돈다).
  - publish(section, items): 그 트랙 섹션을 바꾸고 시트·스틸 폴더·manifest를 다시 만든다
  - claim(no_lock): 스틸 폴더의 받은 파일 중 이 저장소 몫(mine)·시트에 없는 이름(unclaimed)
  - lock(): 받은 파일을 옮기는 동안 병합기가 같은 폴더를 다시 채우지 않게(병합기와 같은 `.만사전/lock`)

경로는 호출 때마다 `tracks.DEPLOY_WORK`에서 읽는다 — 테스트가 그 값만 바꿔 임시 작업대로 돌릴 수 있게.
"""
from __future__ import annotations

import contextlib
import fcntl
import json
import subprocess
import sys

from lib import tracks


def _cmd(*args: str) -> list[str]:
    return [sys.executable, str(tracks.MANJEON), "--work", str(tracks.DEPLOY_WORK), *args]


def publish(section: str, items: list[dict]) -> None:
    payload = json.dumps({"channel": section, "items": items}, ensure_ascii=False)
    subprocess.run(_cmd("publish", section), input=payload, text=True, check=True)


def claim(no_lock: bool = False) -> dict:
    out = subprocess.run(_cmd("claim", tracks.MANJEON_REPO, *(["--no-lock"] if no_lock else [])),
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


@contextlib.contextmanager
def lock():
    p = tracks.DEPLOY_WORK / ".만사전" / "lock"
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)
