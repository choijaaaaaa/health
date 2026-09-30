#!/usr/bin/env python3
"""제휴 링크를 거는 **바로 그 상품**의 대표 이미지를 받아 해결책 칠판 사진으로 쓴다.

WHY(2026-09-27 사용자 "해결책을 주는 칠판에서는 위 이미지를 해결책에 대한 소싱된 이미지로"): 칠판 위 아이콘 줄을
사진 풀의 일반 사진(시계·처방전·이불)으로 채웠더니 "무엇을 사면 되는지"가 안 보였다. 브랜드커넥트에서 고른 상품
(`data/_audit/brandconnect_catalog.json`의 chosen) 사진이면 링크와 사진이 같은 물건이 된다. 댕냥사전
scripts/fetch_product_photos.py와 같은 방식.

사람 얼굴·광고 문구가 섞일 수 있어 바로 쓰지 않는다 — `assets_library/real/_product_candidates/`에 받고,
눈으로 본 것만 `--approve`로 `assets_library/real/_products/<품목>.jpg`에 올린다(칠판은 여기 것만 쓴다).

    .venv/bin/python3 scripts/fetch_product_photos.py              # xray topic 제품 전부(없는 것만)
    .venv/bin/python3 scripts/fetch_product_photos.py 유산균 차전자피
    .venv/bin/python3 scripts/fetch_product_photos.py --approve 유산균 차전자피
(브랜드커넥트 전용 Chrome이 떠 있어야 한다 — lib/brandconnect.login())
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib import tracks  # noqa: E402

CATALOG = ROOT / "data" / "_audit" / "brandconnect_catalog.json"
# 육아 트랙은 품목을 따로 스윕한 카탈로그에 둔다(같은 계정) — 이걸 안 읽으면 육아 해결책 칠판 사진이 한 장도 안 받아졌다
CATALOGS = [CATALOG, ROOT / "data" / "_audit" / "brandconnect_catalog_baby.json"]
CAND = ROOT / "assets_library" / "real" / "_product_candidates"
PRODUCTS = ROOT / "assets_library" / "real" / "_products"


def topic_products() -> list[str]:
    out: list[str] = []
    for x in tracks.glob_topic_files(ROOT / "data", "*/xray.json"):
        d = x.parent
        cap = next((p for p in (d / "platform_captions.json", d / "ko" / "platform_captions.json") if p.exists()), None)
        for n in (json.loads(cap.read_text(encoding="utf-8")).get("products", []) if cap else []):
            if n not in out:
                out.append(n)
    return out


def fetch(names: list[str]) -> None:
    import lib.brandconnect as b
    cat: dict = {}
    for c in CATALOGS:
        if c.exists():
            for k, v in json.loads(c.read_text(encoding="utf-8")).items():
                cat.setdefault(k, v)
    todo = [n for n in (names or topic_products())
            if cat.get(n, {}).get("found") and cat[n].get("chosen") and not (PRODUCTS / f"{n}.jpg").exists()
            and (names or not (CAND / f"{n}.jpg").exists())]
    print(f"받을 품목 {len(todo)}개")
    CAND.mkdir(parents=True, exist_ok=True)
    meta_p = CAND / "_meta.json"
    meta = json.loads(meta_p.read_text(encoding="utf-8")) if meta_p.exists() else {}
    with b._session() as page:
        for n in todo:
            want = cat[n]["chosen"]["id"]
            try:
                with page.expect_response(lambda r: b.API_MARK in r.url, timeout=30000) as ri:
                    page.goto(b.SEARCH_URL.format(sid=b.SPACE_ID, q=urllib.parse.quote_plus(n)), wait_until="domcontentloaded")
                data = ri.value.json().get("data") or []
            except Exception as e:  # 한 품목 실패로 전체를 멈추지 않는다
                print(f"  ✗ {n}: 검색 실패 {type(e).__name__}")
                continue
            hit = next((p for p in data if p.get("id") == want), None)
            if not hit or not hit.get("representativeProductImageUrl"):
                # 고른 상품이 이번 검색에 없으면 다른 상품 사진을 쓰지 않는다(링크와 사진이 어긋난다)
                print(f"  ✗ {n}: 고른 상품({want})이 검색 결과에 없음")
                continue
            url = hit["representativeProductImageUrl"]
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            (CAND / f"{n}.jpg").write_bytes(urllib.request.urlopen(req, timeout=30).read())
            meta[n] = {"product_id": want, "product_name": hit["productName"], "image": url}
            print(f"  ✓ {n} ← {hit['productName'][:40]}")
            time.sleep(1.5)
    meta_p.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def approve(names: list[str]) -> None:
    PRODUCTS.mkdir(parents=True, exist_ok=True)
    for n in names:
        src = CAND / f"{n}.jpg"
        if not src.exists():
            print(f"  건너뜀 {n}: 후보 없음")
            continue
        shutil.copy2(src, PRODUCTS / f"{n}.jpg")
        print(f"  ✓ _products/{n}.jpg")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--approve", action="store_true")
    a = ap.parse_args()
    approve(a.names) if a.approve else fetch(a.names)
