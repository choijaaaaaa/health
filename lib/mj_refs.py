# 미드저니 레퍼런스 이미지 레지스트리(건강만사전) — 로컬 스틸을 R2 공개 도메인에 올리고 이름 → URL을 D1에 적어 둔다.
# dangnyang-shorts/lib/mj_refs.py와 같은 표·같은 방식(project만 다르다). 2026-09-29 사용자 "canon organs나 댕냥사전 이미지같은것들도
# 내가 일일히 넣지않고 너가 db에 넣은 상태로 프롬프트에 링크 넣으라고 했자나" — 건강 시트만 로컬 경로로 남아 있었다.
#
# WHY(2026-09-27 사용자 "건강만사전이랑 댕냥사전도 미드저니 레퍼런스 이미지 db에다 넣어놓고 프롬프트 칠 때
# 그 url로 넣는 거 해야겠다"): 작업지시서가 "Style Reference: stills/canon_organs.jpg"처럼 로컬 경로만 적어서
# 사용자가 매번 파일을 찾아 첨부했다. URL이 DB에 있으면 시트 생성기가 프롬프트에 `--sref <url>`을 바로 박는다.
#
# 표: mission_control.mj_references (D1 `health_shorts__mission_control_mj_references`, infra/d1-postgrest/migrate/02).
# key = "<project>/<name>" — health-shorts도 같은 표에 project="health-shorts"로 쓰면 된다.
# R2 키: mj-refs/<project>/<name>.jpg → https://img.vernhaven.com/mj-refs/...
#
#   .venv/bin/python3 -m lib.mj_refs add stills/canon_organs.jpg          # assets_library/xray/ 기준 경로
#   .venv/bin/python3 -m lib.mj_refs list
#   .venv/bin/python3 -m lib.mj_refs url canon_organs
from __future__ import annotations

import datetime as _dt
import json
import os
import sys
import urllib.parse
import urllib.request as _urlreq
from pathlib import Path

from dotenv import load_dotenv

# Cloudflare 엣지가 파이썬 기본 UA를 403으로 막는다(infra/d1-postgrest/DEPLOY.md)
_opener = _urlreq.build_opener()
_opener.addheaders = [("User-Agent", "Mozilla/5.0 (compatible; project-tools/1.0)")]
_urlreq.install_opener(_opener)

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
PROJECT = "health-shorts"
TABLE = "mj_references"
R2_ENV = ROOT.parent / "verticals" / ".env.r2"
load_dotenv(ROOT / ".env")


def _r2_conf() -> dict:
    return dict(l.strip().split("=", 1) for l in R2_ENV.read_text().splitlines()
                if "=" in l and not l.strip().startswith("#"))


def _db(method: str, query: str = "", body: dict | None = None, prefer: str = "") -> list | None:
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY가 .env에 없다")
    h = {"apikey": key, "Authorization": f"Bearer {key}", "Accept-Profile": "mission_control",
         "Content-Profile": "mission_control", "Content-Type": "application/json"}
    if prefer:
        h["Prefer"] = prefer
    req = _urlreq.Request(f"{url}/rest/v1/{TABLE}{query}", method=method, headers=h,
                          data=json.dumps(body).encode() if body is not None else None)
    with _urlreq.urlopen(req, timeout=30) as r:
        raw = r.read()
    return json.loads(raw) if raw else None


def add(rel: str, kind: str = "sref", note: str = "") -> str:
    """assets_library/xray/ 기준 경로(또는 절대경로)의 이미지를 올리고 URL을 돌려준다. 같은 이름이면 덮어쓴다."""
    import boto3
    from botocore.config import Config
    src = Path(rel) if Path(rel).is_absolute() else XRAY / rel
    if not src.is_file():
        raise FileNotFoundError(src)
    name = src.stem
    conf = _r2_conf()
    obj = f"mj-refs/{PROJECT}/{name}{src.suffix.lower()}"
    s3 = boto3.client("s3", endpoint_url=conf["R2_ENDPOINT"], aws_access_key_id=conf["R2_ACCESS_KEY_ID"],
                      aws_secret_access_key=conf["R2_SECRET_ACCESS_KEY"],
                      config=Config(signature_version="s3v4"), region_name="auto")
    ctype = "image/png" if src.suffix.lower() == ".png" else "image/jpeg"
    # 캐시 짧게: 같은 이름으로 스틸을 고쳐 올리면 미드저니가 새 이미지를 받아야 한다
    s3.put_object(Bucket=conf["R2_BUCKET"], Key=obj, Body=src.read_bytes(), ContentType=ctype,
                  CacheControl="public, max-age=300")
    url = f"{conf['R2_PUBLIC_BASE'].rstrip('/')}/{urllib.parse.quote(obj)}"
    local = str(src.resolve().relative_to(ROOT)) if src.resolve().is_relative_to(ROOT) else str(src)
    _db("POST", "?on_conflict=key", {"key": f"{PROJECT}/{name}", "project": PROJECT, "name": name, "kind": kind,
                                      "url": url, "local_path": local, "note": note or None,
                                      "updated_at": _dt.datetime.now(_dt.timezone.utc).isoformat()},
        prefer="resolution=merge-duplicates,return=minimal")
    return url


def all_refs() -> dict[str, str]:
    """{이름: URL} — 이 프로젝트 것 전부(시트 한 번 만들 때 한 번만 부른다)."""
    rows = _db("GET", f"?select=name,url&project=eq.{PROJECT}") or []
    return {r["name"]: r["url"] for r in rows}


def ensure(rel: str, cache: dict[str, str] | None = None) -> str:
    """등록돼 있으면 그 URL, 없으면 올리고 등록한 URL."""
    name = Path(rel).stem
    refs = cache if cache is not None else all_refs()
    if name not in refs:
        refs[name] = add(rel)
    return refs[name]


if __name__ == "__main__":
    cmd, *args = sys.argv[1:] or ["list"]
    if cmd == "add":
        for a in args:
            print(a, "→", add(a))
    elif cmd == "url":
        print(all_refs().get(args[0], "(없음)"))
    else:
        for n, u in sorted(all_refs().items()):
            print(f"{n:32s} {u}")
