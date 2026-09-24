# 도입부 "써머리" 대사를 오디오·자막에서 통째로 잘라낸다.
#
# WHY(2026-09-17 사용자 지시 "대사랑 그부분 아예 다 빼면 문제없겠던데"): 첫 문장이
# "[증상 나열]~라면 주목하세요"식 조건절 자격심사라 정보를 하나도 안 주면서
# 이탈을 가르는 0~5초를 통째로 먹는다(실측 최장 11.9초). 원고를 다시 쓰면 TTS를
# 다시 뽑아야 하지만, **그 문장만 잘라내면 TTS 재호출이 필요 없다** — narration.srt에
# 문장 끝 시각이 이미 있고 뒤 문장들은 시각만 당기면 된다.
#
# WHY 컷 지점을 srt 시각이 아니라 실제 무음에서 찾는지: srt 타임스탬프는 TTS가
# 추정한 값이라 문장 끝과 몇십 ms 어긋난다 — 그대로 자르면 앞 문장 꼬리가 남거나
# 다음 문장 첫 음절이 날아간다(이 저장소에서 반복된 실패 유형).
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib import tracks  # noqa: E402

# 잘라낼 대상 — 조건절 + 자격심사/CTA 꼬리. lib.content_review.BANNED_HOOK_TAIL과 같은 기준.
SUMMARY_RE = re.compile(
    r"(?:다|라)면[^.!?]{0,20}?"
    r"(?:주목|확인하세요|확인해\s*보세요|저장부터|저장해|이제\s*그만|놓치지\s*마세요|의심해\s*보세요)"
)
TS = re.compile(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)")


def _sec(h, m, s, ms):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def _fmt(t: float) -> str:
    if t < 0:
        t = 0.0
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def parse_srt(path: Path) -> list[tuple[float, float, str]]:
    cues = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = TS.match(lines[1])
        if not m:
            continue
        g = m.groups()
        cues.append((_sec(*g[:4]), _sec(*g[4:]), "\n".join(lines[2:])))
    return cues


def write_srt(path: Path, cues: list[tuple[float, float, str]]) -> None:
    out = []
    for i, (st, en, text) in enumerate(cues, 1):
        out.append(f"{i}\n{_fmt(st)} --> {_fmt(en)}\n{text}\n")
    path.write_text("\n".join(out), encoding="utf-8")


def silences(audio: Path, noise="-35dB", dur=0.12) -> list[tuple[float, float]]:
    r = subprocess.run(
        ["ffmpeg", "-i", str(audio), "-af", f"silencedetect=noise={noise}:d={dur}",
         "-f", "null", "-"],
        capture_output=True, text=True,
    )
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stderr)]
    return list(zip(starts, ends))


def cut_point(audio: Path, first_end: float, second_start: float) -> float:
    """첫 문장 끝~둘째 문장 시작 사이의 실제 무음 한가운데를 컷 지점으로 고른다."""
    best = None
    for s, e in silences(audio):
        if e < first_end - 0.8 or s > second_start + 0.8:
            continue
        mid = (s + e) / 2
        d = abs(mid - (first_end + second_start) / 2)
        if best is None or d < best[0]:
            best = (d, mid)
    if best is None:                       # 무음을 못 찾으면 srt 간격의 중앙
        return (first_end + second_start) / 2
    # 둘째 문장 첫 음절을 절대 먹지 않도록 상한을 건다
    return min(best[1], second_start - 0.05)


def resolve(topic: str) -> tuple[Path, Path, Path] | None:
    out = tracks.output_dir(topic)
    data = tracks.data_dir(topic)
    mp3 = next((p for p in [out / "narration.mp3", *sorted(out.glob("*_narration.mp3"))]
                if p.exists()), None)
    srt = next((p for p in [out / "narration.srt", *sorted(out.glob("*_narration.srt"))]
                if p.exists()), None)
    txt = next((p for p in (data / "narration.txt", data / "ko" / "narration.txt")
                if p.exists()), None)
    if not (mp3 and srt and txt):
        return None
    return mp3, srt, txt


def trim(topic: str, commit: bool) -> str | None:
    paths = resolve(topic)
    if paths is None:
        return None
    mp3, srt, txt = paths
    cues = parse_srt(srt)
    if len(cues) < 2 or not SUMMARY_RE.search(cues[0][2]):
        return None

    cut = cut_point(mp3, cues[0][1], cues[1][0])
    msg = f"{topic}: {cut:.2f}초 잘라냄 — \"{cues[0][2][:46]}…\""
    if not commit:
        return msg

    tmp = mp3.with_suffix(".trimmed.mp3")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(mp3), "-ss", f"{cut}", "-c:a", "libmp3lame",
         "-q:a", "2", str(tmp)],
        check=True, capture_output=True,
    )
    tmp.replace(mp3)
    write_srt(srt, [(s - cut, e - cut, t) for s, e, t in cues[1:]])

    # narration.txt에서도 그 문장을 지운다 — 오디오와 원고가 어긋난 채 두지 않는다
    body = txt.read_text(encoding="utf-8")
    first = re.split(r"(?<=[.!?])\s+", body.replace("\n", " ").strip())[0]
    if first in body:
        body = re.sub(r" ?" + re.escape(first) + r" ?", " ", body, count=1)
        body = re.sub(r"[ \t]+\n", "\n", body)
        body = re.sub(r"\n +", "\n", body).lstrip()
        txt.write_text(body, encoding="utf-8")
    return msg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*")
    ap.add_argument("--commit", action="store_true")
    args = ap.parse_args()

    topics = args.topics or sorted(
        p.parent.name for p in tracks.glob_topic_files(ROOT / "output", "*/narration.srt"))
    hits = [m for t in topics if (m := trim(t, args.commit))]
    head = "" if args.commit else "[DRY RUN] "
    print(f"{head}도입부 써머리 대사 제거 대상 {len(hits)}편 / 검사 {len(topics)}편\n")
    for m in hits:
        print("  " + m)


if __name__ == "__main__":
    main()
