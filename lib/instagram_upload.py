# Instagram Reels 자동 업로드. WHY: lib/youtube_upload.py와 같은 구조(계정별
# 자격증명, CLI 진입점)로 맞춰서, 나중에 다른 계정에서도 이 파일을 복사해
# 그대로 확장할 수 있게 한다. account는 .env의 META_<ACCOUNT>_* 접두사와
# 매칭되는 값(예: "worthitshopping", "hanip_science", "bite_en", "bite_ja",
# "hanip_history") — 실제 값은 health-shorts/.env 주석 참고.
from __future__ import annotations

import sys

import requests

from lib.meta_upload import GRAPH_BASE, delete_temp_url, get_ig_id, get_token, upload_video_to_temp_url, wait_for_container


def upload_reel(account: str, video_path: str, caption: str) -> dict:
    """video_path(로컬 mp4)를 공개 URL로 올린 뒤 Reels 컨테이너를 만들고
    발행한다. 실패하든 성공하든 임시 URL은 마지막에 정리한다."""
    token = get_token(account)
    ig_id = get_ig_id(account)
    temp_url = upload_video_to_temp_url(video_path)
    try:
        create_resp = requests.post(
            f"{GRAPH_BASE}/{ig_id}/media",
            data={
                "media_type": "REELS",
                "video_url": temp_url,
                "caption": caption,
                "access_token": token,
            },
            timeout=60,
        )
        create_resp.raise_for_status()
        creation_id = create_resp.json()["id"]

        wait_for_container(creation_id, token)

        publish_resp = requests.post(
            f"{GRAPH_BASE}/{ig_id}/media_publish",
            data={"creation_id": creation_id, "access_token": token},
            timeout=60,
        )
        publish_resp.raise_for_status()
        result = publish_resp.json()
        print(f"[instagram_upload] [{account}] 업로드 완료: media id {result['id']}")
        return result
    finally:
        delete_temp_url(temp_url)


if __name__ == "__main__":
    account_arg, video_arg, caption_arg = sys.argv[1], sys.argv[2], sys.argv[3]
    upload_reel(account_arg, video_arg, caption_arg)
