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

🚨 Flow는 **start 프레임만** 준다 — end를 주면 Veo가 사이를 맞추려고 피사체를 변형시킨다.
🚨 길이는 4·6·8·10초 네 가지뿐이다.

이 파일은 `scripts/build_clip_request_sheet.py`가 각 topic의 `clip_requests.json`에서 다시 만든다.
**직접 고치지 마라** — 고칠 내용은 해당 topic의 `clip_requests.json`에 넣는다.
"""


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
        lines.append(f"\n**왜 필요한가**: {r.get('why', '')}\n")
        lines.append(f"\n### 미드저니 (start 스틸)\n```\n{r.get('midjourney', '')}\n```\n")
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
