#!/usr/bin/env python3
"""유튜브 채널 하나를 연결해 `.env`에 `YOUTUBE_<CODE>_*` 키로 저장한다 — 토큰은 화면에 찍지 않는다.

WHY(2026-09-27): 건강숏츠를 성인 건강·아기 건강 두 채널로 나눴다. 채널마다 브라우저 로그인으로
refresh token을 받아야 하는데, lib/youtube_auth_setup.py는 토큰을 화면에 출력하고 사람이 .env에
옮겨 적게 돼 있어 비밀값이 대화·로그에 남는다. 여기선 받은 즉시 .env에 쓰고, 어떤 채널에
연결됐는지(이름·ID)만 보여준다 — 엉뚱한 채널을 고른 걸 바로 알 수 있게.

OAuth 클라이언트는 세상건강사전 때 쓴 것(YOUTUBE_WHD_CLIENT_*)을 쓴다 — 그 앱의 토큰은 12일 넘게
만료 없이 유지됐다(7일 만료되는 테스트 앱이 아님).

    .venv/bin/python3 scripts/yt_connect.py adult    # 성인 건강 채널
    .venv/bin/python3 scripts/yt_connect.py baby     # 아기 건강 채널
    .venv/bin/python3 scripts/yt_connect.py whd      # 댕냥사전 채널(값은 dangnyang-shorts/.env로 옮긴다)
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

from google_auth_oauthlib.flow import InstalledAppFlow  # noqa: E402
from googleapiclient.discovery import build  # noqa: E402

# 업로드·예약(youtube) + 댓글(youtube.force-ssl, 2026-10-06 쇼츠 제품 댓글) — force-ssl 없이는 commentThreads가 403
SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.force-ssl"]


def _set_env(values: dict[str, str]) -> None:
    p = ROOT / ".env"
    text = p.read_text(encoding="utf-8")
    for k, v in values.items():
        line = f"{k}={v}"
        text = re.sub(rf"^{k}=.*$", line, text, flags=re.M) if re.search(rf"^{k}=", text, re.M) else text.rstrip("\n") + "\n" + line + "\n"
    p.write_text(text, encoding="utf-8")


def main() -> None:
    code = sys.argv[1].upper()
    cid, csec = os.environ["YOUTUBE_WHD_CLIENT_ID"], os.environ["YOUTUBE_WHD_CLIENT_SECRET"]
    flow = InstalledAppFlow.from_client_config({"installed": {
        "client_id": cid, "client_secret": csec,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]}}, SCOPES)
    print(f"[yt_connect] {code} — 브라우저에서 로그인하고 **연결할 채널을 고르세요**.", flush=True)
    # prompt=consent: 이미 동의한 계정이어도 refresh token을 새로 받으려면 동의 화면을 다시 거쳐야 한다
    creds = flow.run_local_server(port=0, open_browser=True, prompt="consent")
    yt = build("youtube", "v3", credentials=creds)
    ch = yt.channels().list(part="id,snippet", mine=True).execute()["items"][0]
    _set_env({f"YOUTUBE_{code}_CLIENT_ID": cid, f"YOUTUBE_{code}_CLIENT_SECRET": csec,
              f"YOUTUBE_{code}_REFRESH_TOKEN": creds.refresh_token, f"YOUTUBE_{code}_CHANNEL_ID": ch["id"]})
    print(f"[yt_connect] ✅ {code} = {ch['snippet']['title']} ({ch['id']}) — .env에 저장")


if __name__ == "__main__":
    main()
