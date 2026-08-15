"""로컬 git 추적 json/csv 관리 데이터를 Supabase로 1회 백필.
WHY: supabase/schema.sql 적용 직후, index.html이 Supabase 직접 읽기로 전환되기
전에 기존 completed_topics.json 등의 기록이 비어 보이지 않도록 먼저 옮겨둔다.
service_role 키로 RLS를 우회해 쓴다 — 반드시 서버 환경에서만 실행."""
import csv
import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
SUPABASE_URL = os.environ["SUPABASE_URL"]
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates,return=minimal",
}


def upsert(table: str, rows: list[dict]) -> None:
    if not rows:
        print(f"{table}: 건너뜀(데이터 없음)")
        return
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=rows, timeout=30)
    if resp.status_code >= 300:
        print(f"{table}: 실패 {resp.status_code} {resp.text[:300]}")
    else:
        print(f"{table}: {len(rows)}건 upsert 완료")


def main():
    topics = json.loads((ROOT / "output" / "topics.json").read_text(encoding="utf-8"))
    upsert("topics", [
        {
            "topic": t["topic"],
            "title": t.get("title"),
            "url": t.get("url"),
            "thumbnail": t.get("thumbnail"),
            "ad_tag": bool(t.get("ad_tag", False)),
            "tracks": t.get("tracks", []),
        }
        for t in topics
    ])

    completed = json.loads((ROOT / "output" / "completed_topics.json").read_text(encoding="utf-8"))
    upsert("completed_topics", [{"base_topic": t} for t in completed])

    posting_rows = []
    with (ROOT / "output" / "posting_log.csv").open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if row.get("topic") and row.get("platform") and row.get("postedAt"):
                posting_rows.append({"topic": row["topic"], "platform": row["platform"], "posted_at": row["postedAt"]})
    upsert("posting_log", posting_rows)

    coupang = json.loads((ROOT / "output" / "product_links.json").read_text(encoding="utf-8"))
    naver = json.loads((ROOT / "output" / "naver_product_links.json").read_text(encoding="utf-8"))
    global_rows = [{"market": "coupang", "product": k, "url": v} for k, v in coupang.items()]
    global_rows += [{"market": "naver", "product": k, "url": v} for k, v in naver.items()]
    upsert("global_product_links", global_rows)

    # WHY youtube_uploaded는 여기서 더 이상 백필 안 함(2026-08-15): 이 테이블은
    # 이제 lib/youtube_upload.py가 업로드 시점에 직접 쓰는 게 유일한 근거라(위
    # 파일 상단 WHY, health-shorts CLAUDE.md "유튜브 쇼츠 자동 업로드" 절
    # 참고), 로컬 output/youtube_uploaded.json(더 이상 갱신 안 되는 정지된
    # 파일)에서 이 테이블로 백필하면 최신 Supabase 상태를 오히려 오래된
    # 스냅샷으로 되돌릴 위험이 있다.


if __name__ == "__main__":
    main()
