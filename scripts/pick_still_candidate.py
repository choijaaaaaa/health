#!/usr/bin/env python3
# 미드저니 4장 중 캐논 규칙에 맞는 것을 점수로 골라낸다.
#
# WHY(2026-09-24): 미드저니는 한 번 돌리면 4장이 한 세트로 나오고, 이 라이브러리는 "4장 중 1장 채택,
# 나머지는 _candidates에 보관"이 규칙이다(part_prompts.md). 그 고르는 일을 사람에게 넘기면 17세트
# 68장을 눈으로 훑어야 하는데, **캐논 규칙 대부분은 픽셀로 잴 수 있다.**
#
#   · 스틸은 중립(점등 없음) — 호박색은 Flow에서 켠다. 스틸에 미리 칠하면 부위마다 스틸이 필요해진다.
#   · 행위 스틸은 머리끝부터 발끝까지 전신이 보여야 한다(잘리면 동작의 무게중심이 안 보인다).
#   · 배경은 비어 있는 어두운 슬레이트.
#   · 청록 유리 한 가지 톤.
#
# 점수로 순위만 매긴다 — **채택은 사람이 한다.** 구도·동작이 프롬프트대로인지는 픽셀로 못 잰다.
#
#   .venv/bin/python3 scripts/pick_still_candidate.py                 # 전체
#   .venv/bin/python3 scripts/pick_still_candidate.py act_shingles_band
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CAND = ROOT / "assets_library" / "xray" / "stills" / "_candidates"
STEP = 4        # 픽셀을 4칸씩 건너뛰며 본다 — 816x1456을 전부 훑으면 세트당 몇 초씩 걸린다


def measure(path: Path) -> dict:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    px = im.load()
    amber = body = bright_bg = 0
    ys: list[int] = []
    total = 0
    for y in range(0, h, STEP):
        for x in range(0, w, STEP):
            r, g, b = px[x, y]
            total += 1
            if r > 150 and g > 90 and b < 110 and r - b > 70:
                amber += 1
            elif b > 70 and b - r > 25 and g > 50:
                body += 1
                ys.append(y)
            elif r > 120 and g > 120 and b > 120:
                bright_bg += 1          # 배경이 비어 있어야 하는데 밝은 덩어리가 있다
    top = min(ys) / h if ys else 1.0
    bot = max(ys) / h if ys else 0.0
    return {"amber": amber / total, "body": body / total,
            "bright": bright_bg / total, "top": top, "bot": bot}


def score(m: dict, full_body: bool) -> tuple[float, list[str]]:
    s, notes = 100.0, []
    # 호박색 감점은 **전신 행위·부위 스틸에만.** 기전 클로즈업은 프롬프트가 호박색 알갱이를 직접
    # 요구하므로(mechanism_prompts.md) 있는 게 정상이다 — 전부에 걸었다가 m_ 세트가 통째로 깎였다.
    if full_body and m["amber"] > 0.002:
        s -= min(40, m["amber"] * 2000); notes.append(f"점등색 섞임 {m['amber']:.1%}")
    if m["bright"] > 0.01:
        s -= min(20, m["bright"] * 400); notes.append(f"배경에 밝은 덩어리 {m['bright']:.1%}")
    if full_body:
        # 머리끝이 위에서 12% 안, 발끝이 아래에서 8% 안에 들어와야 전신이 다 나온 것
        if m["top"] > 0.12:
            s -= 25; notes.append(f"머리 위 여백 {m['top']:.0%}")
        if m["bot"] < 0.92:
            s -= 30; notes.append(f"발끝 잘림(몸 끝 {m['bot']:.0%})")
    if m["body"] < 0.04:
        s -= 20; notes.append(f"피사체가 작다 {m['body']:.1%}")
    return s, notes


def main() -> None:
    names = sys.argv[1:] or sorted(d.name for d in CAND.iterdir() if d.is_dir())
    for name in names:
        d = CAND / name
        if not d.is_dir():
            print(f"{name}: 폴더 없음"); continue
        full_body = name.startswith("act_")
        rows = []
        for f in sorted(d.glob("*.png")):
            m = measure(f)
            sc, notes = score(m, full_body)
            rows.append((sc, f.name, notes))
        rows.sort(reverse=True)
        print(f"\n{name}  ({'전신 행위' if full_body else '미세 클로즈업'})")
        for i, (sc, fn, notes) in enumerate(rows):
            mark = "→ 추천" if i == 0 else "      "
            print(f"  {mark} {fn[-6:-4]}번 {sc:5.0f}점  {' / '.join(notes) or '지적 없음'}")


if __name__ == "__main__":
    main()
