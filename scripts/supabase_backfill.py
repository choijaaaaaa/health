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
            "season": t.get("season", []),
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

    youtube_done = json.loads((ROOT / "output" / "youtube_uploaded.json").read_text(encoding="utf-8"))
    upsert("youtube_uploaded", [{"topic": t} for t in youtube_done])


if __name__ == "__main__":
    main()
