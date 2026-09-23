#!/usr/bin/env python3
"""이미 나간 topic의 로컬 사본을 지운다 — health-shorts 폴더가 끝없이 커지는 걸 막는다.

WHY(2026-09-21 사용자 "카드뉴스를 블로그에 이미 올린 토픽들은 전부 폴더랑 미션콘트롤에서까지 제거… 용량도 좀
줄이고"): 카드 이미지는 인입 시점에 Cloudflare R2로 올라가고 블로그·대시보드는 그 URL로 서비스한다. 로컬
파일은 그때부터 사본일 뿐인데 topic이 쌓이면서 output/이 2.4GB까지 늘었다.

지우는 것(전부 복구 가능한 사본):
1. `output/<topic>/<lang>/` — vernhaven `blog_posts`에 그 (topic, lang) 행이 있는 것만(= R2 업로드 완료)
2. 네이버 블로그에 카드뉴스가 나간 topic의 `output/<topic>/card_news`·`*.mp4`·`*.mp3`·`dashboard.html`
3. 같은 topic의 `ai-video-network/deploy/health-shorts/<topic>/` 사본
4. 미션컨트롤 `topics` 행(대시보드에서 감춤) — ⚠️ `posting_log`는 절대 건드리지 않는다.
   지우면 "안 올린 topic"으로 되살아나 다시 만들게 된다.

남기는 것: `data/<topic>/` 스펙 JSON(전부 합쳐 18MB, 재업로드·번역에 필요).

    python3 scripts/prune_published.py            # 뭐가 지워질지만 출력
    python3 scripts/prune_published.py --commit
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import urllib.parse
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
DEPLOY = ROOT.parent / "ai-video-network" / "deploy" / "health-shorts"
VERNHAVEN_ENV = ROOT.parent / "verticals" / "vernhaven-blog" / ".env.local"


def _kb(p: Path) -> int:
    if not p.exists():
        return 0
    return int(subprocess.run(["du", "-sk", str(p)], capture_output=True, text=True).stdout.split()[0])


def _rows(url: str, key: str, path: str) -> list[dict]:
    h = {"apikey": key, "Authorization": f"Bearer {key}"}
    out: list[dict] = []
    for off in range(0, 20000, 1000):
        r = requests.get(f"{url}/rest/v1/{path}&limit=1000&offset={off}", headers=h, timeout=60)
        r.raise_for_status()
        page = r.json()
        if not page:
            break
        out += page
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()

    load_dotenv(ROOT / ".env")
    hs_url, hs_key = os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    load_dotenv(VERNHAVEN_ENV, override=True)
    seo_url = os.environ["SUPABASE_URL"]
    seo_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_ANON_KEY"]

    ingested = {(x["source_topic"], x["lang"]) for x in
                _rows(seo_url, seo_key, "blog_posts?select=source_project,source_topic,lang")
                if (x.get("source_project") or "").startswith("health")}
    blogged = {x["topic"] for x in _rows(hs_url, hs_key, "posting_log?select=topic,platform")
               if "블로그" in (x.get("platform") or "")}

    freed = 0
    lang_dirs = [ROOT / "output" / t / lang for t, lang in sorted(ingested)
                 if (ROOT / "output" / t / lang).is_dir()]
    media: list[Path] = []
    for t in sorted(blogged):
        base = ROOT / "output" / t
        if not base.is_dir():
            continue
        if (base / "card_news").is_dir():
            media.append(base / "card_news")
        media += sorted(base.glob("*.mp4")) + sorted(base.glob("*.mp3")) + sorted(base.glob("dashboard.html"))
    deploy_dirs = [DEPLOY / t for t in sorted(blogged) if (DEPLOY / t).is_dir()]

    for group, label in ((lang_dirs, "언어 카드 폴더"), (media, "한국어 카드·영상·오디오"), (deploy_dirs, "배포 폴더 사본")):
        size = sum(_kb(p) for p in group)
        freed += size
        print(f"{label}: {len(group)}개, {size / 1024:.0f} MB")
        if a.commit:
            for p in group:
                shutil.rmtree(p) if p.is_dir() else p.unlink()

    rows = {x["topic"] for x in _rows(hs_url, hs_key, "topics?select=topic")} & blogged
    print(f"미션컨트롤 topics 행: {len(rows)}개")
    if a.commit:
        h = {"apikey": hs_key, "Authorization": f"Bearer {hs_key}", "Prefer": "return=minimal"}
        for t in sorted(rows):
            requests.delete(f"{hs_url}/rest/v1/topics?topic=eq.{urllib.parse.quote(t)}",
                            headers=h, timeout=30).raise_for_status()

    print(f"\n{'회수' if a.commit else '회수 예정'} {freed / 1024 / 1024:.2f} GB"
          + ("" if a.commit else "  — 실제로 지우려면 --commit"))


if __name__ == "__main__":
    main()
