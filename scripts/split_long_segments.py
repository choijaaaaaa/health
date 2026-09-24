#!/usr/bin/env python3
# 클립 하나로 못 채우는 긴 구간을 **자막 문장 경계에서** 쪼갠다.
#
# WHY(2026-09-24): 구간이 클립 길이의 4배를 넘으면 늘려도 정지 화면이 되고, 남는 만큼은 반복으로
# 때워져 "같은 그림에 색만 바뀌는" 화면이 된다. 쪼갠 두 조각은 **같은 클립을 그대로 쓰므로**
# 엉뚱한 장면이 끼어들 위험이 없다 — 화면이 한 번 더 넘어가는 것뿐이다.
#
# 🚨 쪼개는 자리는 반드시 **자막에 실재하는 문장 시작**이어야 한다(시간표는 구절 문자열로 시각을
# 찾는다). 문장 한가운데를 고르면 조립이 첫 줄에서 죽는다.
#
#   .venv/bin/python3 scripts/split_long_segments.py            # 어디를 쪼갤지만
#   .venv/bin/python3 scripts/split_long_segments.py --apply
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib import tracks                                        # noqa: E402
from lib.xray_timeline import _cues, resolve, summary_start   # noqa: E402

LIB = ROOT / "assets_library" / "xray" / "output"
MAX_STRETCH = 4.0
_dur_cache: dict[str, float] = {}


def dur(name: str) -> float:
    if name not in _dur_cache:
        f = LIB / f"{name}.mp4"
        _dur_cache[name] = float(subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
            capture_output=True, text=True).stdout or 0) if f.exists() else 0.0
    return _dur_cache[name]


def worst_ratio(row: dict) -> float:
    d = row["end"] - row["start"]
    return max((d / dur(n) for n in (row.get("mech"), row.get("act")) if n and dur(n)), default=0.0)


def main() -> None:
    apply = "--apply" in sys.argv
    total = 0
    for cfg in tracks.glob_topic_files(ROOT / "data", "*/xray.json"):
        topic = cfg.parent.name
        try:
            rows, cues, ts = resolve(topic), _cues(topic), summary_start(topic)
        except Exception:
            continue
        if not rows:
            continue
        d = json.loads(cfg.read_text(encoding="utf-8"))
        tl = d.get("timeline") or []
        if len(tl) != len(rows):
            continue
        inserts = []
        for i, r in enumerate(rows):
            if ts is not None and r["start"] >= ts - 0.05:      # 결론은 칠판이 덮는다
                continue
            if worst_ratio(r) <= MAX_STRETCH:
                continue
            # 구간 한가운데에 가장 가까운 자막 시작을 고른다 — 양쪽이 고르게 나뉜다
            mid = (r["start"] + r["end"]) / 2
            inner = [c for c in cues if r["start"] + 1.0 < c[0] < r["end"] - 1.0]
            if not inner:
                print(f"  ⚠️ {topic} {r['start']:.1f}초 — 쪼갤 문장 경계가 없다(클립 요청 필요)")
                continue
            cut = min(inner, key=lambda c: abs(c[0] - mid))
            phrase = " ".join(cut[2].split()[:3])
            if phrase in " ".join(c[2] for c in cues if c is not cut):
                phrase = " ".join(cut[2].split()[:5])
            inserts.append((i, dict(tl[i], **{"from": phrase})))
            print(f"  {topic:10s} {r['start']:5.1f}초 {worst_ratio(r):.1f}배 → \"{phrase}\"에서 쪼갬")
        if inserts and apply:
            for off, (i, row) in enumerate(inserts):
                tl.insert(i + 1 + off, row)
            d["timeline"] = tl
            cfg.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        total += len(inserts)
    print(f"\n{'쪼갬' if apply else '쪼갤 곳'} {total}개")


if __name__ == "__main__":
    main()
