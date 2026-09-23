#!/usr/bin/env python3
# 아직 안 받은 클립 요청만 모아 렌더 시트 하나로 만든다.
#
# WHY: 요청은 topic별 clip_requests.json에 흩어져 쌓이는데, 사용자는 미드저니·Flow를
# 한 자리에서 돌린다. 손으로 옮겨 적던 때는 (1) 새 요청이 시트에 안 올라가 그대로 묻히고
# (2) 이미 렌더한 항목이 시트에 남아 두 번 뽑는 일이 반복됐다. output/에 파일이 있으면
# 받은 것으로 보고 빼므로, 시트는 항상 "지금 뽑아야 할 것"만 남는다.
#
#   .venv/bin/python3 scripts/build_clip_request_sheet.py
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XRAY = ROOT / "assets_library" / "xray"
RENDERED = XRAY / "output"
SHEET = XRAY / "작업" / "REQUEST.md"

HEADER = """# 클립 요청 시트

**미드저니로 스틸을 뽑고 → Flow에 start 프레임 단독으로 넣고 → 모션 프롬프트**를 붙인다.
결과는 `assets_library/xray/RENDER/<이름>.mp4`로 저장하면 세션이 `scripts/publish_xray_clips.py`로 정리한다.

## 🚨 레퍼런스 이미지를 반드시 같이 넣는다

라이브러리 195종이 **같은 인체 모델**로 통일돼 있다. 텍스트 프롬프트만으로 뽑으면 톤·체형이 달라져
**다른 사람이 나온다.** 요청마다 아래에 어느 이미지를 어떤 방식으로 넣을지 적어뒀다. 갈래는 둘이다.

| 클립 | 붙이는 법 | 왜 |
|---|---|---|
| `act_`(행위) · `part_`(부위) | **Omni Reference** | 전신 인체가 그대로 나와야 한다 — 톤·체형 고정 |
| `m_`(기전) | **Style Reference**(색·질감만) | 🚨 Omni는 "이 대상을 넣어라"라서 **클로즈업에 전신 인체가 끼어든다** |

## 그 밖의 고정 규칙

- Flow는 **start 프레임만** 준다 — end를 주면 Veo가 사이를 맞추려고 피사체를 변형시킨다.
- 길이는 **4·6·8·10초** 네 가지뿐이다. 기전은 **4초 안에 컷 3개**(한 장면을 4초 끄는 것보다 리듬이 산다).
- 얼굴은 이목구비 없이 매끈하게. 점등은 **호박색 하나뿐**이고 나머지는 끝까지 청록 유리다.
- 미드저니 4장 중 1장 채택, 나머지는 `stills/_candidates/<파일명>/`에 보관.

이 파일은 `scripts/build_clip_request_sheet.py`가 각 topic의 `clip_requests.json`에서 다시 만든다.
**직접 고치지 마라** — 고칠 내용은 해당 topic의 `clip_requests.json`에 넣는다.
"""

DEFAULT_REF = "assets_library/xray/stills/canon_organs.jpg"


def _reference(r: dict) -> tuple[str, str, str]:
    """(레퍼런스 이미지, 붙이는 방식, 스틸 저장 위치). 요청이 직접 적어두면 그게 이긴다.

    WHY 이름 앞글자로 가르는지: 기전 클립에 Omni Reference를 넣으면 위벽 클로즈업 안에 전신 인체가
    끼어든다(`mechanism_prompts.md`에 실측 기록). 행위·부위는 반대로 Omni가 없으면 매번 다른
    체형·톤의 사람이 나온다."""
    name = r.get("name", "")
    ref = r.get("ref") or DEFAULT_REF
    if name.startswith("m_"):
        return ref, "Style Reference (⚠️ Omni Reference 금지)", f"assets_library/xray/stills/mech/{name}.jpg"
    return ref, "Omni Reference", f"assets_library/xray/stills/act/{name}.jpg"


def collect() -> list[tuple[str, dict]]:
    """topic별 요청 중 아직 렌더 안 된 것만. 같은 클립을 여러 topic이 요청하면 첫 건만 남긴다."""
    out: list[tuple[str, dict]] = []
    seen: set[str] = set()
    for p in sorted((ROOT / "data").glob("*/clip_requests.json")):
        topic = p.parent.name
        try:
            reqs = json.loads(p.read_text(encoding="utf-8")).get("requests", [])
        except json.JSONDecodeError:
            continue
        for r in reqs:
            name = r.get("name")
            if not name or name in seen or (RENDERED / f"{name}.mp4").exists():
                continue
            seen.add(name)
            out.append((topic, r))
    return out


def main() -> None:
    reqs = collect()
    lines = [HEADER, f"\n**{date.today().isoformat()} 기준 {len(reqs)}종**\n", "---\n"]
    for i, (topic, r) in enumerate(reqs, 1):
        lines.append(f"\n## {i}. `{r['name']}` — {topic}\n")
        ref, mode, still = _reference(r)
        lines.append(f"\n**왜 필요한가**: {r.get('why', '')}\n")
        ready = (ROOT / still).exists()
        if ready:
            # 스틸이 이미 있으면 미드저니 단계는 끝난 것 — Flow만 돌리면 된다
            lines.append(f"\n✅ **start 스틸 준비됨**: `{still}` — 미드저니 단계 생략, 아래 Flow만 돌린다.\n")
        else:
            lines.append(f"\n**레퍼런스**: `{ref}` — **{mode}**로 넣는다\n")
            lines.append(f"\n### 미드저니 (start 스틸 → `{still}`)\n```\n{r.get('midjourney', '')}\n```\n")
        lines.append(f"\n### Flow ({r.get('seconds', 6)}초)\n```\n{r.get('flow', '')}\n```\n")
        if r.get("_render_note"):
            lines.append(f"\n> {r['_render_note']}\n")
        lines.append("\n---\n")

    SHEET.parent.mkdir(parents=True, exist_ok=True)
    SHEET.write_text("".join(lines), encoding="utf-8")
    print(f"{SHEET.relative_to(ROOT)} — {len(reqs)}종")
    for topic, r in reqs:
        print(f"  {topic:12s} {r['name']}")


if __name__ == "__main__":
    main()
