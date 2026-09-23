#!/usr/bin/env python3
# 부위 점등 클립이 **맞는 자리에, 맞는 크기로** 켜지는지 기계로 잰다.
#
# WHY(2026-09-24 사용자 "신장 위치가 저게맞냐? 심장아니냐 저기???"): part_kidney는 점등 중심은
# 해부학 위치와 맞았는데, 후광까지 번져 세로 14%(실제 신장 7%)를 덮었고 그 위쪽 끝이 심장 높이(29%)에
# 닿아 **심장으로 읽혔다.** 위치만 보면 통과하므로 크기도 같이 본다.
#
# 🚨 **전신 스틸(`canon_*`)로 만든 클립만 판정한다.** 처음엔 전신 해부학 비율을 전부에 들이댔다가
# 9종 중 8종이 걸렸는데 대부분이 `cu_*`(클로즈업) 스틸이라 기준 자체가 안 맞는 오탐이었다.
# 클로즈업에 "전체가 켜지면 잘못"을 걸어봐도 12종이 걸렸고, 그중 part_eye·part_hand처럼
# **피사체가 곧 그 부위**인 것은 전체 점등이 맞다. 둘을 가르려면 그 스틸이 부위보다 넓은 범위를
# 보여주는지 알아야 하는데 파일명으론 판단이 안 된다 — 그래서 클로즈업은 **수치만 적고 판정하지
# 않는다.** 오탐 섞인 경고는 사람이 곧 무시하게 된다.
#
#   .venv/bin/python3 scripts/part_glow_audit.py            # 전부
#   .venv/bin/python3 scripts/part_glow_audit.py part_kidney
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
LIB = XRAY / "output"

# 선 자세 전신 기준(머리끝 0, 발바닥 1)의 중심 높이와 세로 크기 — 전신 스틸로 만든 클립에만 쓴다.
ANATOMY = {
    "part_thyroid": ("갑상선", 0.13, 0.03),
    "part_lungs": ("폐", 0.27, 0.12),
    "part_heart": ("심장", 0.29, 0.07),
    "part_liver": ("간", 0.33, 0.08),
    "part_stomach": ("위", 0.35, 0.07),
    "part_kidney": ("신장", 0.37, 0.07),
    "part_intestines": ("장", 0.44, 0.13),
    "part_bladder": ("방광", 0.55, 0.06),
    "part_uterus_ovary": ("자궁·난소", 0.56, 0.07),
}
TOL_POS = 0.06       # 중심이 이보다 어긋나면 다른 장기로 읽힌다
TOL_SIZE = 1.8       # 실제 크기의 몇 배까지 봐주나 — 후광이 조금 번지는 건 연출이다
CLOSEUP_MAX = 0.55   # 클로즈업에서 점등이 피사체 세로의 이 비율을 넘으면 "부위"로 안 읽힌다


def source_stills() -> dict[str, str]:
    """part_prompts.md의 `[프레임: <스틸>.jpg 단독]` 표기에서 클립→스틸을 읽는다."""
    text = (XRAY / "part_prompts.md").read_text(encoding="utf-8")
    return dict(re.findall(r"###\s+(part_[a-z_]+).*?\[프레임:\s*([a-z_]+)\.jpg", text))


def measure(clip: Path, at: str = "3.2") -> tuple[float, float, float] | None:
    """(점등 중심, 점등 세로 크기, 점등 위쪽 끝) — 전부 피사체 세로 길이 대비 비율.

    프레임이 아니라 피사체(청록 유리) 기준으로 재는 이유: 클립마다 인체가 차지하는 비율이 달라
    프레임 기준으로는 서로 비교가 안 된다."""
    with tempfile.TemporaryDirectory() as td:
        f = Path(td) / "f.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", at, "-i", str(clip),
                        "-frames:v", "1", str(f)], check=True)
        im = Image.open(f).convert("RGB")
        w, h = im.size
        px = im.load()
        amber, body = [], []
        for y in range(0, h, 2):
            for x in range(0, w, 2):
                r, g, b = px[x, y]
                if r > 150 and g > 90 and b < 110 and r - b > 70:
                    amber.append(y); body.append(y)
                elif b > 70 and b - r > 25 and g > 50:
                    body.append(y)
    if not amber or len(body) < 50:
        return None
    body.sort(); amber.sort()
    top, bot = body[int(len(body) * 0.002)], body[int(len(body) * 0.998)]
    span = (bot - top) or 1
    return ((amber[len(amber) // 2] - top) / span,
            (amber[-1] - amber[0]) / span,
            (amber[0] - top) / span)


def main() -> None:
    stills = source_stills()
    names = sys.argv[1:] or sorted(p.stem for p in LIB.glob("part_*.mp4"))
    bad = 0
    for name in names:
        clip = LIB / f"{name}.mp4"
        if not clip.exists():
            print(f"{name}: 클립 없음"); continue
        still = stills.get(name, "")
        m = measure(clip)
        if m is None:
            print(f"   {name:22s} 점등을 못 찾음 — 점등 없는 클립이거나 강조색이 캐논과 다르다")
            continue
        c, hh, top = m
        full_body = still.startswith("canon_")
        notes = []
        if full_body and name in ANATOMY:
            ko, want_c, want_h = ANATOMY[name]
            if abs(c - want_c) > TOL_POS:
                notes.append(f"중심 {c:.0%}(기준 {want_c:.0%})")
            if hh > want_h * TOL_SIZE:
                notes.append(f"세로 {hh:.0%}(실제 {want_h:.0%}의 {hh / want_h:.1f}배)")
            for other, (oko, oc, _h) in ANATOMY.items():
                if other != name and abs(oc - want_c) > TOL_POS and top <= oc <= top + hh:
                    notes.append(f"{oko} 높이({oc:.0%})까지 덮음"); break

            kind = "전신"
            if notes:
                bad += 1
                print(f"⚠️ {name:22s} {ko:8s} [{kind}] " + " / ".join(notes))
            else:
                print(f"✅ {name:22s} {ko:8s} [{kind}] 중심 {c:.0%}, 세로 {hh:.0%}")
            continue

        # 🚨 클로즈업은 판정하지 않고 수치만 적는다.
        # WHY: "점등이 피사체 전체를 덮으면 잘못"으로 걸었더니 12종이 걸렸는데, part_eye·part_hand·
        # part_nail처럼 **피사체 자체가 그 부위인** 클립은 전체가 켜지는 게 맞다. 반대로 part_bladder가
        # 하반신 전체로 켜지던 건 진짜 사고였다. 둘을 가르려면 그 스틸이 부위보다 넓은 범위를
        # 보여주는지 알아야 하는데 그건 파일명으로 판단할 수 없다 — 오탐 섞인 경고를 내느니
        # 수치만 내놓고 사람이 보게 한다.
        print(f"   {name:22s} {'—':8s} [클로즈업] 중심 {c:.0%}, 세로 {hh:.0%}"
              + ("  ← 피사체 전체 점등" if hh > CLOSEUP_MAX else ""))
    print(f"\n해부학 기준으로 어긋난 클립 {bad}개 (클로즈업은 판정 대상 아님 — 수치만)")


if __name__ == "__main__":
    main()
