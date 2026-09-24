#!/usr/bin/env python3
"""**완성된 mp4 자체**를 재서 잘못된 것을 잡는다. preflight(조립 전 스펙 검사)와 짝이다.

WHY(2026-09-24): 오늘 사용자가 잡은 결함 여섯 중 다섯이 기계로 잴 수 있는 것이었는데
(배지가 화면 밖으로 넘침·옛 음성으로 조립됨·낡은 영상이 목록에 남음·클립 캡션 없음·
영상이 멈춰 있음) 나는 매번 사용자가 말해준 **뒤에** 검사를 만들었다. preflight는 스펙만
보기 때문에 "조립 결과가 실제로 어떻게 나왔는지"는 아무도 안 봤다 — 그 자리가 이 파일이다.

    .venv/bin/python3 scripts/verify_output.py            # 완성본이 있는 topic 전부
    .venv/bin/python3 scripts/verify_output.py 고령_15
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks                                       # noqa: E402
from lib.xray_timeline import resolve, summary_start         # noqa: E402

MIN_FREEZE_SEC = 4.0      # 이보다 오래 한 프레임이 이어지면 지적


def _probe(path: Path, *entries: str) -> str:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", *entries,
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return out.stdout.strip()


def _freezes(path: Path) -> list[tuple[float, float]]:
    """한 프레임이 그대로 멈춰 있는 구간. 자막만 바뀌는 칠판 구간도 여기 걸린다 — 그게 목적이다."""
    out = subprocess.run(
        ["ffmpeg", "-v", "info", "-i", str(path), "-vf", f"freezedetect=n=-45dB:d={MIN_FREEZE_SEC}",
         "-map", "0:v", "-f", "null", "-"], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", out)]
    durs = [float(x) for x in re.findall(r"freeze_duration: ([\d.]+)", out)]
    return list(zip(starts, durs))


def check(topic: str) -> list[str]:
    odir = tracks.output_dir(topic)
    vid = odir / "shorts_xray_test.mp4"
    if not vid.is_file():
        return []
    bad: list[str] = []

    # 1. 원본보다 새것인가 — 원고·시간표·스펙뿐 아니라 **음성·자막**까지 본다.
    #    음성을 다시 뽑으면 문장 시각이 전부 움직이므로 반드시 다시 조립해야 한다.
    ddir = tracks.data_dir(topic)
    srcs = [ddir / "xray.json", ddir / "narration.txt", ddir / "card_news_spec.json",
            ddir / "ko" / "card_news_spec.json", odir / "narration.mp3", odir / "narration.srt"]
    vt = vid.stat().st_mtime
    stale = [p.name for p in srcs if p.exists() and p.stat().st_mtime > vt]
    if stale:
        bad.append(f"원본이 영상보다 새것입니다 — 다시 조립해야 합니다: {', '.join(stale)}")

    # 2. 길이가 나레이션과 맞는가 — 자막이 잘리거나 뒤가 비면 여기서 드러난다
    dur = float(_probe(vid, "format=duration") or 0)
    adur = float(_probe(odir / "narration.mp3", "format=duration") or 0) if (odir / "narration.mp3").is_file() else 0
    if adur and not (adur - 1.0 <= dur <= adur + 6.0):
        bad.append(f"영상 {dur:.1f}초인데 나레이션은 {adur:.1f}초입니다 — 앞뒤가 비거나 잘렸습니다")

    # 3. 소리가 있는가(무음으로 나간 적이 실제로 있다)
    if not _probe(vid, "stream=codec_type").count("audio"):
        bad.append("오디오 트랙이 없습니다")

    # 4. 설명 구간이 멈춰 있는가 — 칠판(해결책) 구간의 정지는 **의도된 것**이라 세지 않는다.
    #    2026-09-24 사용자 확정: 해결책은 칠판만 나오는 씬에서 하나하나 짚는다("씬 전환이
    #    되어야 이해가 잘되지"). 거기서 화면이 안 바뀌는 건 설계지 결함이 아니다.
    ts = summary_start(topic)
    for st, d in _freezes(vid):
        if ts is not None and st >= ts - 1.0:
            continue
        bad.append(f"{st:.0f}초부터 {d:.0f}초간 설명 구간 화면이 멈춰 있습니다")

    # 6. 구간마다 너무 늘려 정지 화면이 됐는가
    for r in resolve(topic) or []:
        if ts is not None and r["start"] >= ts - 0.05:
            continue
        seg = r["end"] - r["start"]
        for kind, name in (("기전", r.get("mech")), ("행위", r.get("act"))):
            src = ROOT / "assets_library" / "xray" / "output" / f"{name}.mp4" if name else None
            if not src or not src.is_file():
                continue
            k = seg / float(_probe(src, "format=duration") or 1)
            if k >= 3.5:
                bad.append(f"{r['start']:.0f}초 구간을 {kind} 클립 {name}으로 {k:.1f}배 늘렸습니다 "
                           f"— 거의 정지 화면입니다")

    # 7. 업로드할 자리가 있는가
    caps = next((p for p in (ddir / "platform_captions.json", ddir / "ko" / "platform_captions.json")
                 if p.is_file()), None)
    if caps:
        names = [x.get("name") for x in json.loads(caps.read_text(encoding="utf-8")).get("platforms", [])]
        if "네이버 클립" not in names:
            bad.append("platform_captions.json에 네이버 클립 항목이 없습니다 — 올릴 자리가 안 생깁니다")

    # 8. 두 벌 다 있고 deploy 사본이 지금 영상과 같은가 — 유튜브판이 한 번도 안 나온 채
    #    몇 주를 갔다(2026-09-24 "영상 두개씩 만들어야한다고 했는데 반영안했노")
    yt = odir / "nocta" / "shorts_xray_test.mp4"
    if not yt.is_file():
        bad.append("유튜브판(nocta/)이 없습니다 — 화살표 없이 광고 표시만 있는 판을 같이 만들어야 합니다")
    elif yt.stat().st_mtime < vt - 600:
        bad.append("유튜브판이 네이버판보다 낡았습니다 — 같이 다시 조립해야 합니다")
    dep_dir = ROOT.parent / "ai-video-network" / "deploy" / "health-shorts" / topic
    for src, name in ((vid, "네이버클립.mp4"), (yt, "유튜브.mp4")):
        dep = dep_dir / name
        if not src.is_file():
            continue
        if not dep.is_file():
            bad.append(f"deploy에 {name}이 없습니다")
        elif dep.stat().st_size != src.stat().st_size:
            bad.append(f"deploy의 {name}이 지금 영상과 다릅니다 — stage_for_deploy를 다시 도세요")

    return bad


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*")
    a = ap.parse_args()
    topics = a.topics or sorted(
        p.parent.name for p in tracks.glob_topic_files(ROOT / "data", "*/xray.json")
        if (tracks.output_dir(p.parent.name) / "shorts_xray_test.mp4").is_file())
    total = 0
    for t in topics:
        bad = check(t)
        total += len(bad)
        print(f"{'✅' if not bad else '⚠️'} {t:12s} {len(bad)}건")
        for b in bad:
            print("      ·", b)
    print(f"\n완성본 지적 합계 {total}건")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
