# Threads 업로드 공통 헬퍼(2026-08-26 인스타그램·페이스북 채널 폐지로 축소). WHY: 세 플랫폼 다 "계정별 자격증명
# 읽기"와 "로컬 영상 파일을 공개 URL로 만들기"가 똑같이 필요해서 여기 한 곳에
# 모은다 — lib/youtube_upload.py의 _env_prefix/_get_credentials 패턴을 그대로 따름.
#
# WHY 영상을 Supabase Storage에 올려 공개 URL로 바꾸는지: Instagram/Threads의
# Content Publishing API(POST /media)는 로컬 파일 직접 업로드를 지원하지 않고
# video_url(공개 접근 가능한 URL)만 받는다 — 그래서 게시 직전에 소셜용 임시
# 버킷(social-media-temp, public=true, video/mp4 전용, 50MB 제한 — Supabase
# 프로젝트 플랜상 그 이상은 400 EntityTooLarge로 거부됨, 2026-08-22 실측)에
# 올려 공개 URL을 얻는다. Facebook 페이지 영상(POST /{page-id}/videos)은
# 반대로 멀티파트 직접 업로드를 지원해서 이 과정이 필요 없다.
from __future__ import annotations

import os
import time
import uuid
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GRAPH_BASE = "https://graph.facebook.com/v21.0"
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
TEMP_BUCKET = "social-media-temp"


def _env_prefix(account: str) -> str:
    return f"META_{account.upper().replace('-', '_')}_"


def get_token(account: str) -> str:
    """계정별 override(META_<ACCOUNT>_TOKEN)가 있으면 그걸, 없으면 공유
    시스템 사용자 토큰(META_SYSTEM_USER_TOKEN)을 쓴다. WHY override가
    필요한지(2026-08-22): 한입역사 페이지는 비즈니스 포트폴리오가 아니라
    개인 프로필 소유라서 시스템 사용자 토큰으로 접근이 안 되고, 그 페이지를
    만든 개인 로그인으로 따로 발급받은 토큰을 써야 한다."""
    override = os.environ.get(f"{_env_prefix(account)}TOKEN")
    if override:
        return override
    return os.environ["META_SYSTEM_USER_TOKEN"]


def upload_video_to_temp_url(video_path: str) -> str:
    """로컬 mp4를 social-media-temp 버킷에 올리고 공개 URL을 반환한다. 파일명은
    매번 uuid로 새로 만들어 겹치지 않게 한다(재시도 시 캐시된 옛 파일을 다시
    읽는 걸 방지). 호출부가 게시 완료 후 delete_temp_url()로 지워야 버킷이
    안 쌓인다."""
    path = Path(video_path)
    object_name = f"{uuid.uuid4().hex}{path.suffix}"
    with path.open("rb") as f:
        resp = requests.post(
            f"{SUPABASE_URL}/storage/v1/object/{TEMP_BUCKET}/{object_name}",
            headers={
                "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                "apikey": SUPABASE_SERVICE_ROLE_KEY,
                "Content-Type": "video/mp4",
            },
            data=f,
            timeout=120,
        )
    resp.raise_for_status()
    return f"{SUPABASE_URL}/storage/v1/object/public/{TEMP_BUCKET}/{object_name}"


def delete_temp_url(public_url: str) -> None:
    """upload_video_to_temp_url()이 올린 임시 파일을 게시 완료 후 정리한다.
    실패해도(이미 지워졌거나 네트워크 문제) 호출부 흐름을 막지 않게 예외를
    삼킨다 — 게시 자체는 이미 끝난 뒤라 이 정리 실패로 전체를 실패 처리할
    필요가 없다."""
    object_name = public_url.rsplit(f"{TEMP_BUCKET}/", 1)[-1]
    try:
        requests.delete(
            f"{SUPABASE_URL}/storage/v1/object/{TEMP_BUCKET}/{object_name}",
            headers={
                "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
                "apikey": SUPABASE_SERVICE_ROLE_KEY,
            },
            timeout=30,
        )
    except requests.RequestException as e:
        print(f"[meta_upload] ⚠️ 임시 파일 정리 실패(게시는 이미 완료됨): {e}")


def wait_for_container(creation_id: str, token: str, graph_base: str = GRAPH_BASE,
                        timeout_s: int = 300) -> None:
    """Instagram/Threads 둘 다 컨테이너 생성(POST /media 또는 /threads)이 비동기라
    바로 발행할 수 없다 — status_code가 FINISHED가 될 때까지 폴링한다. IN_PROGRESS면
    5초 간격 재시도, ERROR면 즉시 예외, timeout_s를 넘기면 TimeoutError."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        resp = requests.get(
            f"{graph_base}/{creation_id}",
            params={"fields": "status_code,status", "access_token": token},
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()
        status_code = body.get("status_code")
        if status_code == "FINISHED":
            return
        if status_code == "ERROR":
            raise RuntimeError(f"컨테이너 처리 실패: {body}")
        time.sleep(5)
    raise TimeoutError(f"컨테이너 처리 시간 초과({timeout_s}초): {creation_id}")
