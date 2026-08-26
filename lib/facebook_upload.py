# Facebook 페이지 영상 자동 업로드. WHY 직접 멀티파트 업로드인지: Instagram/Threads와
# 달리 POST /{page-id}/videos는 로컬 파일을 그대로 받아서, Supabase 임시 호스팅
# (lib/meta_upload.py의 upload_video_to_temp_url)이 필요 없다.
from __future__ import annotations

import sys

import requests

from lib.meta_upload import GRAPH_BASE, get_page_access_token, get_page_id


def upload_video(account: str, video_path: str, caption: str) -> dict:
    page_token = get_page_access_token(account)
    page_id = get_page_id(account)
    with open(video_path, "rb") as f:
        resp = requests.post(
            f"{GRAPH_BASE}/{page_id}/videos",
            data={"description": caption, "access_token": page_token},
            files={"source": f},
            timeout=300,
        )
    resp.raise_for_status()
    result = resp.json()
    print(f"[facebook_upload] [{account}] 업로드 완료: video id {result['id']}")
    return result


if __name__ == "__main__":
    account_arg, video_arg, caption_arg = sys.argv[1], sys.argv[2], sys.argv[3]
    upload_video(account_arg, video_arg, caption_arg)
