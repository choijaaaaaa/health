#!/usr/bin/env python3
"""RENDER/<번호>.mp4 를 이름 붙여 output/<이름>.mp4 로 반영한다 — 파이프라인이 읽는 곳은 output뿐이다.

WHY(2026-09-23 실측): Flow로 141개(행위 41 + 기전 100)를 다 뽑아 `RENDER/`에 모아뒀는데
`output/`에는 옛 48개만 있었다. `xray.json`도 `content_review.check_xray_clips()`도 `output/`만
보므로, 이 반영을 안 하면 **클립이 있는데도 "없는 클립"으로 잡혀 제작이 멈춘다.**

번호↔이름은 `RENDER/_이름표.json`이 정본이다(`cu_*` 6개는 부위 클립을 코드로 만들 때 쓰는
스틸이라 mp4가 없는 게 정상).

끝부분에만 결함이 있는 클립은 `RENDER/_트림.json`에 `{"번호": 잘라낼_끝초}` 로 적어두면
그만큼 잘라서 반영한다 — 다시 렌더하지 않고 길이는 조립 단계에서 속도로 맞춘다.

    python3 scripts/publish_xray_clips.py            # 뭐가 반영될지만
    python3 scripts/publish_xray_clips.py --commit
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
RENDER = XRAY / "RENDER"
OUT = XRAY / "output"
NAMES = RENDER / "_이름표.json"
TRIM = RENDER / "_트림.json"


def _probe(path: Path) -> tuple[int, int, float]:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                        "-show_entries", "stream=width,height:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    s = (d.get("streams") or [{}])[0]
    return s.get("width", 0), s.get("height", 0), float((d.get("format") or {}).get("duration", 0))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true")
    a = ap.parse_args()

    names = json.loads(NAMES.read_text(encoding="utf-8"))
    trims = json.loads(TRIM.read_text(encoding="utf-8")) if TRIM.exists() else {}
    OUT.mkdir(parents=True, exist_ok=True)

    new = updated = skipped = 0
    low_res: list[str] = []
    for num, name in sorted(names.items(), key=lambda kv: int(kv[0]) if kv[0].isdigit() else 0):
        src = RENDER / f"{num}.mp4"
        if not src.exists():
            continue                      # cu_* 스틸은 mp4가 없다
        dst = OUT / f"{name}.mp4"
        w, h, dur = _probe(src)
        if h and h < 720:
            low_res.append(f"{num}({name}) {w}x{h}")
        cut = float(trims.get(num, 0) or 0)
        tag = "신규" if not dst.exists() else "갱신"
        (new := new + 1) if not dst.exists() else (updated := updated + 1)
        print(f"  {tag} {name:34s} {w}x{h} {dur:.1f}s" + (f" → 끝 {cut}s 잘라냄" if cut else ""))
        if not a.commit:
            continue
        if cut > 0 and dur > cut:
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src),
                            "-t", f"{dur - cut:.2f}", "-c:v", "libx264", "-crf", "18",
                            "-preset", "medium", "-an", str(dst)], check=True)
        else:
            shutil.copy2(src, dst)

    print(f"\n{'반영 완료' if a.commit else '반영 예정'} — 신규 {new} · 갱신 {updated}"
          + ("" if a.commit else "  (실제 반영은 --commit)"))
    if low_res:
        print(f"⚠️ 720p 미만 {len(low_res)}개: {', '.join(low_res[:8])}")


if __name__ == "__main__":
    main()
