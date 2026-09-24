#!/usr/bin/env python3
"""반투명 인체 포맷 영상을 topic 하나에 대해 끝까지 만든다 — 칠판 조립 → 도입부 Flow → 기전 전환.

WHY(2026-09-23 파일럿에서 확정): 이 포맷은 손으로 돌리면 단계가 셋이고 그중 둘이 실수하기 쉽다.
  1. `rebuild_video` — 칠판 본체
  2. `xray_splice`로 도입부 Flow 2컷 — ⚠️ 시각을 **0으로 줘야** 한 묶음(chain)으로 이어져 전체 화면이 된다.
     0.2/1.6처럼 실제 시각을 주면 두 번째 컷이 위쪽 칸 크기로 잘려 들어간다(실측).
  3. 항목마다 기전 클립 교체 — ⚠️ 기전 클립은 4초인데 항목 구간은 13~30초다. **재생 속도로 맞춘다**
     (반복하면 같은 동작이 끊겨 돌아가는 게 보인다). 정지 화면이 되지 않게 MAX_STRETCH까지만 늘리고
     남는 만큼만 반복으로 채운다.

xray.json에 `opening[].range`와 `opening_until`을 적어두면 이 스크립트가 그대로 재현한다.

    python3 scripts/xray_build.py <topic>            # 조립까지
    python3 scripts/xray_build.py <topic> --dry-run  # 실행할 명령만
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from lib.xray_timeline import resolve  # noqa: E402

PY = str(ROOT / ".venv" / "bin" / "python3")
LIB = "assets_library/xray/output"
MIN_PANEL_SEC = 3.0          # 이보다 짧은 구간에 기전을 갈아 끼우면 깜빡임으로만 보인다


PANEL_W, PANEL_H = 960, 680          # lib/video_assembler.XRAY_PANEL 과 같은 값



# 반복은 쓰지 않는다 — 2026-09-24 사용자 "반복재생 말고 속도 느리게해서 하라했자나".
# 상한을 2.5로 뒀더니 18.6초 구간(6초 클립, 3.1배 필요)이 상한에 걸려 결국 반복으로 넘어갔다.
# 시청층이 중장년이라 느린 건 오히려 낫다는 판단이 이미 있어(PANEL_SPEED 0.5) 4배까지 연다.
MAX_STRETCH = 4.0
# 그래도 넘치면 **반복하지 않고 멈춘다.** 4배로도 못 채운다는 건 그 구간에 보여줄 장면이 모자라다는
# 뜻이고, 같은 4초를 다섯 번 돌리면 "같은 그림에 색만 바뀌는" 화면이 된다(실측 지적).
# 사용자 "이것도 영상이 더 필요한거면 더 만들어서 해야지" — 클립을 하나 더 요청한다.
SMOOTH_FROM = 1.15           # 이 이상 늘릴 때만 프레임 보간 — 그냥 늘리면 같은 프레임이 반복돼 끊긴다


def _duration(clip: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(clip)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def _overstretched(clip: Path, seconds: float) -> float:
    """구간을 채우려면 MAX_STRETCH보다 더 늘려야 하는가 — 그 배율을 돌려준다(아니면 0)."""
    need = seconds / _duration(clip)
    return need if need > MAX_STRETCH else 0.0


def _fit(clip: Path, seconds: float) -> str:
    """구간을 채우도록 재생 속도를 조절하는 필터 조각.

    WHY 반복이 아니라 속도인지(2026-09-24 사용자 "영상 Loop 말고 왠만하면 시간을 늘리거나 줄이는거로해
    영상을 느리게 빠르게 해서"): 4초 클립을 20초 구간에 다섯 번 되풀이하면 같은 동작이 다섯 번 끊겨
    돌아가는 게 그대로 보인다. 한 번을 구간 길이에 맞춰 늘리면 동작이 끊기지 않는다.

    다만 무한정 늘리진 않는다 — 30초 구간에 4초 클립이면 7.5배라 정지 화면이 된다. `MAX_STRETCH`까지만
    늘리고 남는 만큼은 반복으로 채운다(호출부가 `-stream_loop -1`을 준다).
    """
    k = min(seconds / _duration(clip), MAX_STRETCH)
    f = f"setpts={k:.4f}*(PTS-STARTPTS)"
    if k >= SMOOTH_FROM:
        f += ",minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc"
    return f


# 클립을 **자르지 않는다** — 2026-09-24 사용자 "자르는거 없이 영상 풀로 다 나올수있게".
# 세로 클립(720x1280)을 칸 높이 680에 맞추면 폭이 382라 반칸(477)에 넉넉히 들어간다. 남는 좌우는
# 클립 배경과 같은 색으로 메운다(클립 네 귀퉁이를 찍어 잰 값). 예전엔 폭을 먼저 맞추고 넘치는 높이를
# 잘라냈는데, 그러면 전신 클립에서 발이 잘려 동작의 무게중심이 안 보였다.
VOID = "0x142E35"            # 클립 배경(어두운 슬레이트) — 메운 자리가 티 나지 않게
DIVIDER = "0x3A5A66"         # 두 영상 사이 구분선 — 왼쪽 행동 / 오른쪽 기전의 경계
# 8인 이유: 반칸 폭이 짝수로 떨어져야 한다((960-8)/2 = 476). 6으로 두면 477이 홀수라
# libx264가 폭을 짝수로 맞추면서 결과가 958px로 2px 모자랐다(실측).
DIVIDER_W = 8
HALF_W = (PANEL_W - DIVIDER_W) // 2


LABEL_PAD = 18               # 칸 모서리가 radius 28로 둥글게 깎이므로 그 안쪽에 둔다


def _side_labels(td: Path) -> tuple[Path, Path]:
    """좌우가 각각 무엇인지 알려주는 라벨 두 장.

    WHY(2026-09-24 사용자 "왼쪽이 행동, 오른쪽이 기전이라는걸 보여주고"): 두 장면을 나란히 놓는 것만으론
    어느 쪽이 원인이고 어느 쪽이 몸 안인지 안 읽힌다. 구분선만으로는 "다른 장면"까지만 전달된다."""
    from lib.video_assembler import _make_pill_label_png
    paths = []
    for text in ("이 행동이", "몸 안에선"):
        p = td / f"label_{text}.png"
        if not p.exists():
            _make_pill_label_png(text, p, font_size=38)
        paths.append(p)
    return paths[0], paths[1]


def _fit_whole(idx: int, clip: Path, seconds: float, width: int) -> str:
    """클립 하나를 잘라내지 않고 `width`×PANEL_H 안에 통째로 앉힌다."""
    return (f"[{idx}:v]scale=-2:{PANEL_H},{_fit(clip, seconds)},"
            f"pad={width}:{PANEL_H}:(ow-iw)/2:0:color={VOID}")


def _fill_to(clip: Path, seconds: float, out: Path) -> None:
    """칸 하나를 기전 클립으로만 채운다(행위 클립이 없는 항목)."""
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-stream_loop", "-1", "-i", str(clip),
                    "-filter_complex", _fit_whole(0, clip, seconds, PANEL_W),
                    "-t", f"{seconds:.2f}",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-an", str(out)], check=True)


def _split_fill(act: Path, mech: Path, seconds: float, out: Path) -> None:
    """왼쪽 행위 · 오른쪽 기전으로 한 칸에 나란히 넣고 구간 길이에 맞춘다.

    WHY(2026-09-24 사용자 "왼쪽에 행동 오른쪽에 기전 이렇게 들어가야 할거같다"): 기전만 크게 띄우면
    "몸 안에서 무슨 일이 벌어지는지"는 보이는데 **그게 어떤 행동 때문인지**가 안 보인다. 둘을 나란히
    놓아야 "이 행동을 하면 → 몸이 이렇게 된다"가 한 화면에서 읽힌다.

    가운데 구분선을 두는 이유: 배경색이 같은 두 장면이 맞닿으면 한 화면으로 읽혀 좌우가 다른
    이야기라는 게 안 보인다. 왼쪽 블록 오른쪽 끝을 구분선 색으로 메워 경계를 만든다.

    두 클립은 길이가 달라 각자의 배속으로 같은 구간을 채운다.
    """
    labels = _side_labels(out.parent)
    vf = (f"{_fit_whole(0, act, seconds, HALF_W)},"
          f"pad={HALF_W + DIVIDER_W}:{PANEL_H}:0:0:color={DIVIDER}[a];"
          f"{_fit_whole(1, mech, seconds, HALF_W)}[m];"
          f"[a][m]hstack=2[panel];"
          f"[panel][2:v]overlay={LABEL_PAD}:{LABEL_PAD}[l];"
          f"[l][3:v]overlay={HALF_W + DIVIDER_W + LABEL_PAD}:{LABEL_PAD}")
    subprocess.run(["ffmpeg", "-y", "-v", "error",
                    "-stream_loop", "-1", "-i", str(act), "-stream_loop", "-1", "-i", str(mech),
                    "-i", str(labels[0]), "-i", str(labels[1]),
                    "-filter_complex", vf, "-t", f"{seconds:.2f}",
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-an", str(out)], check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--ad-tag", action="store_true", help="유튜브판(광고 표시 얹음)")
    ap.add_argument("--base", help="덧씌울 원본 디렉토리(예: nocta)")
    # WHY 미리보기 모드가 따로 있는지: 없는 행위 클립을 만나면 평소엔 멈춰야 한다(비슷한 걸로 때우면
    # 화면과 나레이션이 어긋나는 사고가 반복됐다). 다만 클립을 아직 다 못 받은 상태에서 **구성이
    # 어떻게 보이는지** 확인해야 할 때가 있다. 그때도 대체 클립은 절대 쓰지 않고, 그 구간만 기전
    # 단독으로 두고 어디가 비었는지 출력한다.
    ap.add_argument("--preview", action="store_true",
                    help="못 받은 행위 클립이 있어도 그 구간만 기전 단독으로 두고 끝까지 조립(발행 금지)")
    a = ap.parse_args()

    cfg = json.loads((ROOT / "data" / a.topic / "xray.json").read_text(encoding="utf-8"))
    if not a.dry_run:
        subprocess.run([PY, "-m", "lib.rebuild_video", a.topic], cwd=ROOT, check=True)
        # 결론 구간은 영상 칸 없이 칠판을 크게 쓴다("그래서 뭘 하면 되는지"를 읽히는 자리다).
        # 그 칠판 전체 버전을 여기서 같이 만든다 — 따로 돌려야 하는 단계로 두면 빠지고, 빠져도
        # xray_splice가 조용히 건너뛰어 영상 칸이 끝까지 남는다(2026-09-24 실측).
        if cfg.get("summary_from"):
            subprocess.run([PY, "-m", "lib.rebuild_video", a.topic, "--board"], cwd=ROOT, check=True)

    args = []
    # 도입부: 전부 시각 0 — fill_until까지 한 묶음으로 이어 붙여 전체 화면으로 덮는다
    for o in cfg.get("opening", []):
        # 도입부 클립도 아직 못 받았을 수 있다 — timeline 쪽만 걸러내다 여기서 ffmpeg가 죽었다
        # (2026-09-24 순환_12 실측: opening이 미수령 act_toilet_strain_faint를 가리켜 exit 254).
        if not (ROOT / o["clip"]).exists():
            if not a.preview:
                raise SystemExit(f"도입부 클립 없음: {o['clip']} — clip_requests.json에 적을 것")
            print(f"  ⚠️ 미리보기: 도입부 클립 {Path(o['clip']).stem}가 없어 건너뜁니다")
            continue
        rng = o.get("range")
        args.append(f"0:{o['clip']}" + (f"@{rng[0]}-{rng[1]}" if rng else ""))

    # 항목 구간마다 위쪽 칸을 갈아 끼운다. `act`가 있으면 **왼쪽 행위 · 오른쪽 기전**으로 나눠 넣는다.
    tl = resolve(a.topic) or []
    acts = cfg.get("_acts") or []
    tmp = Path(tempfile.mkdtemp(prefix="xray_loop_"))
    for i, row in enumerate(tl):
        mech, dur = row.get("mech"), row["end"] - row["start"]
        if not mech or dur < MIN_PANEL_SEC:
            continue
        src = ROOT / LIB / f"{mech}.mp4"
        if not src.exists():
            raise SystemExit(f"기전 클립 없음: {mech} — 비슷한 걸로 바꾸지 말고 clip_requests.json에 적을 것")
        act = row.get("act") or (acts[i % len(acts)] if acts else None)
        dst = tmp / f"p{i}_{mech}.mp4"
        if not a.dry_run:
            # 4배로도 못 채우면 나머지는 반복으로 때워진다 — 같은 4초가 계속 돌아가는 화면이 된다.
            # 그 구간엔 보여줄 장면이 모자란 것이므로 클립을 하나 더 받아야 한다.
            for kind, name in (("기전", mech), ("행위", act)):
                p = ROOT / LIB / f"{name}.mp4" if name else None
                over = _overstretched(p, dur) if p and p.exists() else 0.0
                if over:
                    msg = (f"{row['start']:.1f}초 구간({dur:.0f}초)을 {kind} 클립 {name}"
                           f"({_duration(p):.0f}초) 하나로 못 채웁니다 — {over:.1f}배가 필요한데 상한은 "
                           f"{MAX_STRETCH}배입니다. 구간을 쪼개거나 클립을 하나 더 요청하세요.")
                    if not a.preview:
                        raise SystemExit(f"장면 부족: {msg}")
                    print(f"  ⚠️ 미리보기: {msg}")
            asrc = ROOT / LIB / f"{act}.mp4" if act else None
            if asrc and not asrc.exists():
                if not a.preview:
                    raise SystemExit(f"행위 클립 없음: {act} — clip_requests.json에 적을 것")
                print(f"  ⚠️ 미리보기: {row['start']:.1f}초 구간은 행위 클립 {act}가 없어 기전 단독")
                asrc = None
            if asrc:
                _split_fill(asrc, src, dur, dst)
            else:
                _fill_to(src, dur, dst)
        args.append(f"{row['start']:.2f}:{dst}")

    cmd = [PY, "scripts/xray_splice.py", a.topic, *args, "--panel"]
    if cfg.get("opening_until"):
        cmd += ["--fill-until", str(cfg["opening_until"])]
    if a.ad_tag:
        cmd.append("--ad-tag")
    if a.base:
        cmd += ["--base", a.base]

    print(" ".join(cmd))
    if not a.dry_run:
        subprocess.run(cmd, cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
