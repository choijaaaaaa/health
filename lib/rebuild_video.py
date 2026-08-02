# 기존 topic의 숏폼 영상을 최신 스타일(칠판 배경+배너 실사진+엔딩 CTA)로 다시
# 조립할 때 필요한 인자를 data/*의 spec·캡션·자막에서 그대로 유도한다.
# WHY(2026-08-02): 원래 조립 시 어떤 인자(모션 스케줄 타이밍 등)를 썼는지 기록해둔
# 매니페스트가 없어서, 기존 spec/narration.srt에서 매번 같은 방식으로 재유도해야
# 여러 topic에 걸쳐 일관되게 재현할 수 있다.
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path

from PIL import Image

from lib.video_assembler import _parse_srt, assemble, DEFAULT_END_CARD_TEXT

ROOT = Path(__file__).resolve().parent.parent
ILLUST_DIR = ROOT / "assets_library" / "illust"
MOTION_DIR = ROOT / "assets_library" / "motion"
REAL_DIR = ROOT / "assets_library" / "real"

BG_CANDIDATES = [
    ("0x00FF00", (0, 255, 0)),
    ("0x0000FF", (0, 0, 255)),
    ("0xFF00FF", (255, 0, 255)),
    ("0x00FFFF", (0, 255, 255)),
    ("0xAA00FF", (170, 0, 255)),
    ("0xFFFFFF", (255, 255, 255)),
]


def _char_name(char_file: str) -> str:
    return char_file.replace("_illust.jpg", "")


@lru_cache(maxsize=None)
def nearest_bg_color_for_motion(name: str) -> str:
    """모션 클립(mp4) 첫 프레임의 모서리 픽셀을 5색 크로마키 후보 중 가장 가까운
    색으로 매핑한다.
    ⚠️ WHY 일러스트가 아니라 모션 클립에서 직접 읽는지(2026-08-02, 눈_1 재조립
    실사 확인 중 발견): 기존 캐릭터 일러스트는 카드뉴스 표지 중복 방지를 위해
    나중에 배경색을 다양하게 리컬러했지만(recolor_background), 그 리컬러는 정지
    이미지 파일에만 적용됐고 이미 Kling으로 만들어둔 모션 mp4는 그대로 원래
    배경색(대부분 초록)으로 남아있다 — 일러스트 모서리 색으로 bg_color를
    유도하면 실제 모션 클립 배경과 안 맞아서 크로마키 제거가 안 되고 초록
    사각형이 그대로 화면에 노출되는 사고가 난다. 모션 클립 자체의 첫 프레임을
    읽어야 실제로 지워야 할 색을 정확히 알 수 있다."""
    motion_path = MOTION_DIR / f"{name}_motion.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        frame_path = Path(tmp) / "frame.png"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(motion_path), "-vframes", "1", str(frame_path)],
            check=True, capture_output=True,
        )
        img = Image.open(frame_path).convert("RGB")
        r, g, b = img.getpixel((2, 2))
    best = min(BG_CANDIDATES, key=lambda c: sum((a - b) ** 2 for a, b in zip(c[1], (r, g, b))))
    return best[0]


def find_real_photo(char_name: str) -> str | None:
    exact = REAL_DIR / f"{char_name}.jpg"
    if exact.exists():
        return str(exact)
    cands = sorted(REAL_DIR.glob(f"{char_name}_real_*.jpg"))
    return str(cands[0]) if cands else None


_WORD_RE = re.compile(r"[가-힣A-Za-z0-9]+")


def _keywords(item: dict) -> set[str]:
    """항목의 name+body 문장에서 뽑은 내용어 — narration.srt 문장과 겹치는 단어를
    찾아 그 항목이 실제로 언급되는 구간을 잡는 근거로 쓴다. char_file 베이스 이름
    (예: 탄산음료)은 일러스트용 대표 명칭일 뿐 나레이션엔 그 단어 그대로 안 나오는
    경우가 많아서(예: "단 음료"라고만 씀) name/body 쪽이 훨씬 신뢰도 높다.
    WHY '대신' 항목은 name을 아예 안 쓰는지: "튀김 대신"처럼 대안 항목 이름은
    원인 항목 이름("기름진 튀김·가공식품")의 단어를 그대로 재사용해서, name까지
    키워드로 넣으면 원인 문단에서 대안 항목이 잘못 잡힌다(둘 다 "튀김" 매치) —
    대안 항목은 body(실제로 그 대안 식품을 설명하는 문장)만 신뢰한다."""
    text = " ".join(item["body"]) if "대신" in item["name"] else item["name"] + " " + " ".join(item["body"])
    return {w for w in _WORD_RE.findall(text) if len(w) >= 2}


def _group_by_paragraph(narration_txt: str, srt_entries: list[tuple[float, float, str]]):
    """narration.txt 문단(빈 줄 구분)과 narration.srt 문장을 다시 짝짓는다 — SRT는
    문장 단위, spec item은 문단(원인 1개~해결책 여러 개) 단위라 둘의 경계가 다르다.
    같은 원본 텍스트를 그대로 문장 단위로 쪼갠 것뿐이라 문단 텍스트에 그 문장이
    부분 문자열로 포함되는지로 안전하게 다시 묶을 수 있다."""
    paragraphs = [p.strip() for p in narration_txt.split("\n\n") if p.strip()]
    groups = [[] for _ in paragraphs]
    pi = 0
    for entry in srt_entries:
        text = entry[2].strip()
        while pi < len(paragraphs) - 1 and text not in paragraphs[pi]:
            pi += 1
        groups[pi].append(entry)
    return [g for g in groups if g]


def build_motion_schedule(items: list[dict], srt_entries: list[tuple[float, float, str]], narration_txt: str):
    """narration.txt 문단 단위로 각 항목의 name/body 키워드 겹침 점수를 매겨 어느
    항목이 그 문단에 해당하는지 정한다(문장 단위로 하면 도입부 훅 문장이 뒷부분
    품목명을 미리 한 번 언급하는 것만으로 엉뚱하게 일찍 전환되는 문제가 있었다 —
    문단 전체 겹침 점수를 보면 그런 스침 언급 한 단어에 흔들리지 않는다). 한
    문단에 여러 항목이 걸리면(마무리 문단에서 대안들을 한 번에 나열하는 경우 등)
    문단 내 키워드 등장 위치 비율로 시간을 비례 배분한다 — 정확한 원본 타이밍
    기록이 없어서 택한 근사치다."""
    keyword_sets = [_keywords(it) for it in items]
    names = [_char_name(it["char_file"]) for it in items]
    n = len(items)

    para_groups = _group_by_paragraph(narration_txt, srt_entries)

    points: list[tuple[float, int]] = [(0.0, 0)]
    assigned = {0}
    for gi, group in enumerate(para_groups):
        if gi == 0:
            continue  # 첫 문단은 항상 도입부(item[0])
        full_text = "".join(e[2] for e in group)

        # WHY 캐릭터 이름 직접 등장에 가중치 10을 주는지: "케일"/"고등어"처럼 대안
        # 캐릭터는 실제 음식명이라 나레이션에 그대로 등장해 강한 신호가 되지만,
        # "탄산음료"/"라면"처럼 원인 캐릭터가 추상적 대표 명칭인 경우엔 등장 안
        # 하고 body 키워드(성분·수치 등) 여러 개가 겹치는 걸로만 판단해야 한다 —
        # 이름 매치 1개 또는 body 키워드 3개 이상을 "확실한 매치" 기준(임계값 3)으로
        # 삼아서, 우연히 겹치는 단어 1~2개짜리 스침 매치를 걸러낸다.
        raw = []
        for idx in range(n):
            if idx in assigned:
                continue
            name_hit = names[idx] in full_text
            body_hits = sum(1 for kw in keyword_sets[idx] if kw in full_text)
            score = (10 if name_hit else 0) + body_hits
            if score > 0:
                raw.append((score, idx))
        if not raw:
            continue
        # WHY 절대 임계값 대신 최고점 대비 상대 임계값(2026-08-02, 관절_1/다리쥐_1에서
        # 실제 발견): 진짜 매치 점수 폭이 topic마다 크게 달라서(캐릭터 이름이 나레이션에
        # 그대로 나오면 10+, 안 나오면 body 단어 몇 개 겹치는 정도로 4~5) 고정 임계값
        # 하나로는 어떤 topic에선 스침 매치를 못 거르고 어떤 topic에선 진짜 매치까지
        # 걸러버렸다 — 이 문단의 최고 점수 대비 50% 이상인 후보만 남기면(최소 3점)
        # "우연히 단어 하나 겹친 것"과 "이 문단이 진짜 다루는 항목(들)"이 안정적으로
        # 갈린다. 문단 하나가 여러 항목을 같이 언급하는 경우(마무리 문단, 원인+대안을
        # 한 문단에 묶어 쓴 topic 등)엔 최고점과 비등한 후보가 여럿 남아 자연스럽게
        # 다중 선택된다.
        best = max(s for s, _ in raw)
        cutoff = max(3, best * 0.5)
        scored = []
        for score, idx in raw:
            if score < cutoff:
                continue
            name_hit = names[idx] in full_text
            pos = full_text.find(names[idx]) if name_hit else min(
                full_text.find(kw) for kw in keyword_sets[idx] if kw in full_text
            )
            scored.append((pos, score, idx))
        if not scored:
            continue
        scored.sort()

        # 문단 내 절대 위치 → 절대 시각으로 변환(문장마다 길이가 달라 문단을 한
        # 덩어리로 이어붙인 뒤 누적 길이로 각 문장의 오프셋을 구한다)
        offsets = []
        acc = 0
        for e in group:
            offsets.append((acc, acc + len(e[2]), e[0], e[1]))
            acc += len(e[2])

        def pos_to_time(pos):
            for lo, hi, s, e in offsets:
                if lo <= pos < hi or (hi == acc and pos >= hi):
                    frac = (pos - lo) / max(hi - lo, 1)
                    return s + (e - s) * frac
            return group[0][0]

        for pos, score, idx in scored:
            t = pos_to_time(pos)
            points.append((t, idx))
            assigned.add(idx)

    total_end = srt_entries[-1][1] if srt_entries else 0.0
    segments = []
    for i, (t, idx) in enumerate(points):
        seg_end = points[i + 1][0] if i + 1 < len(points) else total_end
        if seg_end <= t:
            continue
        name = names[idx]
        char_file = f"{name}_illust.jpg"
        motion_path = str(MOTION_DIR / f"{name}_motion.mp4")
        bg_color = nearest_bg_color_for_motion(name)
        segments.append((round(t, 3), round(seg_end, 3), motion_path, bg_color))
    return segments


def derive(topic: str) -> dict:
    spec = json.loads((ROOT / "data" / topic / "card_news_spec.json").read_text())
    items = spec["items"]
    hook = " ".join(spec["title"][:-1])
    subject = spec["title"][-1]

    lead_name = _char_name(items[0]["char_file"])
    banner_photo = find_real_photo(lead_name)
    if banner_photo is None:
        counts = Counter(_char_name(it["char_file"]) for it in items)
        for name, _ in counts.most_common():
            banner_photo = find_real_photo(name)
            if banner_photo:
                break

    cover_char_file = spec.get("cover_char_file") or items[0]["char_file"]

    audio = ROOT / "output" / topic / f"{topic}_narration.mp3"
    srt = ROOT / "output" / topic / f"{topic}_narration.srt"
    out = ROOT / "output" / topic / f"{topic}_shorts.mp4"

    distinct_chars = {it["char_file"] for it in items}
    kwargs = dict(
        images=None,
        audio_path=str(audio),
        srt_path=str(srt),
        out_path=str(out),
        title=f"{hook} {subject}",
        title_card_text=hook,
        title_card_char_path=str(ILLUST_DIR / cover_char_file),
        title_banner_photo_path=banner_photo,
        end_card_text=DEFAULT_END_CARD_TEXT,
        end_card_char_path=str(ILLUST_DIR / cover_char_file),
    )

    if len(distinct_chars) == 1:
        name = _char_name(items[0]["char_file"])
        kwargs["motion_path"] = str(MOTION_DIR / f"{name}_motion.mp4")
        kwargs["motion_schedule"] = None
        kwargs["bg_color"] = nearest_bg_color_for_motion(_char_name(items[0]["char_file"]))
    else:
        srt_entries = _parse_srt(str(srt))
        narration_txt = (ROOT / "data" / topic / "narration.txt").read_text()
        kwargs["motion_path"] = None
        kwargs["motion_schedule"] = build_motion_schedule(items, srt_entries, narration_txt)
        kwargs["bg_color"] = nearest_bg_color_for_motion(_char_name(items[0]["char_file"]))

    return kwargs


def rebuild(topic: str):
    kwargs = derive(topic)
    print(f"=== {topic} ===")
    print("title:", kwargs["title"])
    print("banner photo:", kwargs["title_banner_photo_path"])
    if kwargs["motion_schedule"]:
        for seg in kwargs["motion_schedule"]:
            print("  segment:", seg)
    else:
        print("motion:", kwargs["motion_path"], "bg_color:", kwargs["bg_color"])
    assemble(**kwargs)
    print(f"완료: {kwargs['out_path']}")


if __name__ == "__main__":
    rebuild(sys.argv[1])
