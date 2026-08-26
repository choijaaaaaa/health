# Threads 자동 업로드. WHY 별도 토큰 체계인지: Threads API(graph.threads.net)는
# Instagram/Facebook의 시스템 사용자 토큰 체계와 별개로, 계정마다 독립된 OAuth
# 앱 역할(Threads 테스터) 승인을 거쳐야 발급된다 — 그래서 lib/meta_upload.py의
# 공유 토큰을 쓰지 않고 계정별 THREADS_<ACCOUNT>_TOKEN/THREADS_<ACCOUNT>_USER_ID를
# 그대로 읽는다.
from __future__ import annotations

import os
import sys

import requests
from dotenv import load_dotenv

from lib.meta_upload import delete_temp_url, upload_video_to_temp_url, wait_for_container

load_dotenv()

THREADS_GRAPH_BASE = "https://graph.threads.net/v1.0"


def _env_prefix(account: str) -> str:
    return f"THREADS_{account.upper().replace('-', '_')}_"


def _get_token(account: str) -> str:
    return os.environ[f"{_env_prefix(account)}TOKEN"]


def _get_user_id(account: str) -> str:
    return os.environ[f"{_env_prefix(account)}USER_ID"]


def post_thread(account: str, text: str, video_path: str | None = None) -> dict:
    """video_path가 없으면 텍스트만, 있으면 영상과 함께 게시한다."""
    token = _get_token(account)
    user_id = _get_user_id(account)
    temp_url = None
    try:
        data = {"text": text, "access_token": token}
        if video_path:
            temp_url = upload_video_to_temp_url(video_path)
            data["media_type"] = "VIDEO"
            data["video_url"] = temp_url
        else:
            data["media_type"] = "TEXT"

        create_resp = requests.post(f"{THREADS_GRAPH_BASE}/{user_id}/threads", data=data, timeout=60)
        create_resp.raise_for_status()
        creation_id = create_resp.json()["id"]

        if video_path:
            wait_for_container(creation_id, token, graph_base=THREADS_GRAPH_BASE)

        publish_resp = requests.post(
            f"{THREADS_GRAPH_BASE}/{user_id}/threads_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=60,
        )
        publish_resp.raise_for_status()
        result = publish_resp.json()
        print(f"[threads_upload] [{account}] 게시 완료: thread id {result['id']}")
        return result
    finally:
        if temp_url:
            delete_temp_url(temp_url)


if __name__ == "__main__":
    account_arg, text_arg = sys.argv[1], sys.argv[2]
    video_arg = sys.argv[3] if len(sys.argv) > 3 else None
    post_thread(account_arg, text_arg, video_arg)
