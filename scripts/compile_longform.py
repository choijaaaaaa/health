#!/usr/bin/env python3
"""이미 유튜브에 공개된 쇼츠를 검색어 테마로 묶어 16:9 몰아보기 롱폼 한 편으로 만든다(올리기는 yt_upload.py longform).

WHY(2026-10-25 사용자): 공개된 쇼츠를 주기적으로 롱폼으로 모아 올린다. 묶는 기준은 topic 접두어(소화_)가 아니라
시청자가 검색창에 칠 증상·질병 이름이다 — "위암인 사람 폐암인 사람 자궁관련 어떤 질병이 있는사람 이런사람들이 다
검색어를 그걸치고 들어올거아니야". 테마(검색어·들어갈 topic·제목 머리)는 data/_longform/compilation_themes.json.

화면: 세로 쇼츠를 1920×1080 가운데(608×1080)에 놓고 양옆은 같은 영상을 흐리게 깐 남색 판 — 왼쪽은 편 목록,
오른쪽은 지금 편 번호·제목·제품. 편마다 맨 앞 썸네일 카드(0.2초)와 맨 끝 엔딩 카드는 잘라내고, 엔딩 카드는 맨 끝에
한 번만 붙인다(사용자 "도움이되셨다면~하는 마무리 씬은 마지막에만 나오도록"). 편 사이는 1.2초 제목 카드로 컷 전환
(줌·글리치·플래시 금지 — 루트 규칙 "조립 화면 효과 다 구리다").

    .venv/bin/python3 scripts/compile_longform.py adult --list               # 테마 후보 표(공개 편 수·검색량)
    .venv/bin/python3 scripts/compile_longform.py adult stomach --dry-run    # 들어갈 편·자를 지점·제목·설명란만
    .venv/bin/python3 scripts/compile_longform.py adult stomach              # → output/_longform/adult_stomach_<날짜>/

결과 폴더: longform.mp4 · thumbnail.jpg(1280×720) · upload.md(제목·설명란·태그 — yt_upload.py longform이 그대로 올린다)
· manifest.json(들어간 topic·video_id·시작 시각·자른 프레임).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from lib import tracks  # noqa: E402
from lib.rebuild_video import OUTRO_KOR, _resolve_output_file  # noqa: E402
from lib.video_assembler import FONT_PATH, FPS, OUTRO_GAP, OUTRO_TAIL, _build_ad_tag_badge  # noqa: E402

import yt_upload as yup  # noqa: E402

THEMES = ROOT / "data" / "_longform" / "compilation_themes.json"
OUT_BASE = ROOT / "output" / "_longform"
KST = dt.timezone(dt.timedelta(hours=9))

# assemble()의 title_card_duration 기본값 — 편마다 맨 앞 이만큼이 썸네일 카드고, 나레이션은 이 시각에 시작한다.
# 엔딩 카드는 그 나레이션이 끝나는 자리(0.2 + 나레이션 길이, 프레임 격자로 반올림)에서 시작한다(video_assembler.assemble
# 타임라인 `(total_duration + offset, video_total)` 구간).
TITLE_CARD_SEC = 0.2
OUT_W, OUT_H = 1920, 1080
FG_W, FG_H = 608, 1080             # 1080×1920을 높이 1080에 맞춘 폭 607.5 → 짝수
FG_X = (OUT_W - FG_W) // 2
COVER_SEC = 2.5                    # 표지 — 3초 안(사양)
CARD_SEC = 1.2                     # 편 사이 제목 카드
TARGET_LUFS = -14.0                # 유튜브 재생 정규화 기준 근처로 편마다 맞춘다
PEAK_DB = -2.0                     # 샘플 피크 상한 — AAC 인코딩이 1dB 안팎 올려 트루피크가 -1 근처에 온다
SR = 48000
SPF = SR // FPS                    # 프레임당 오디오 샘플(1600) — 소리 길이를 화면 길이에 샘플 단위로 맞춘다
# 엔딩 카드(정지 그림) 판정 — 작은 회색 프레임 평균 차이(0~255). 엔딩 카드 첫 프레임은 칠판 윗띠가 한 프레임 겹쳐
# 마지막 프레임과 2.3쯤 차이 나고(소화_1 실측), 칠판→엔딩 카드 전환은 40 넘게 차이 난다.
STATIC_DIFF = 8.0
MIN_END_CARD_SEC = 1.5             # 엔딩 카드는 최소 2초짜리다 — 이보다 짧은 정지 꼬리는 엔딩 카드가 아니다

NAVY = (12, 22, 42)
NAVY_LIGHT = (24, 42, 76)
ACCENT = (255, 184, 77)
TEXT = (246, 248, 251)
SUB = (214, 221, 232)
DIM = (128, 141, 164)
_WEIGHT_INDEX = {"bold": 6, "semibold": 4, "medium": 2}   # AppleSDGothicNeo.ttc 안의 굵기 번호


@dataclass
class Episode:
    topic: str
    video_id: str
    publish_at: str
    title: str                      # 유튜브 제목 그대로
    keyword: str                    # 화면·목차용 검색어("위경련 증상")
    short: str                      # 롱폼 제목에 늘어놓을 짧은 이름("위경련")
    hook: str                       # 제목에서 검색어 머리·부제·제품 꼬리를 뗀 한 줄
    search_volume: int
    products: list[str]
    product_lines: list[str]
    sources: list[str]
    subscribe_line: str
    src: str                        # 원본 유튜브판(nocta) 경로
    cut_from: int = 0               # 남길 첫 프레임(썸네일 카드 다음)
    cut_to: int = 0                 # 엔딩 카드 첫 프레임(이 프레임부터 버린다)
    cut_note: str = ""
    loudness_in: float = 0.0
    gain_db: float = 0.0
    start_sec: float = 0.0          # 롱폼 안에서 이 편 화면이 시작하는 시각
    chapter_sec: float = 0.0        # 목차 시각(편 사이 카드 시작)
    extra: dict = field(default_factory=dict)


# ── 데이터 ────────────────────────────────────────────────────────────

def _nospace(s: str) -> str:
    return re.sub(r"\s+", "", s or "")


def _utc(iso: str) -> dt.datetime:
    return dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))


def load_themes(channel: str) -> dict[str, dict]:
    data = json.loads(THEMES.read_text(encoding="utf-8"))
    if channel not in data:
        raise SystemExit(f"❌ {THEMES.relative_to(ROOT)}에 {channel} 채널 테마가 없음")
    return data[channel]


def published(channel: str) -> dict[str, dict]:
    """{topic: youtube_uploaded 행} — 공개 시각이 지났고 확정된 쇼츠만(예약만 된 편은 뺀다)."""
    ch = yup.Channel(channel)
    now = dt.datetime.now(dt.timezone.utc)
    out = {}
    for r in ch.rows():
        when = r.get("publish_at")
        if r.get("status") == "confirmed" and r.get("video_id") and when and _utc(when) <= now:
            out[r["topic"][len(ch.key):]] = r
    return out


def media_root() -> Path:
    """mp4·mp3는 git에 없어 worktree엔 없다 — 본 저장소(main 체크아웃)에서 읽는다. main에서 돌리면 ROOT 그대로."""
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--path-format=absolute", "--git-common-dir"],
                       capture_output=True, text=True)
    return Path(r.stdout.strip()).parent if r.returncode == 0 and r.stdout.strip() else ROOT


def _topic_out(topic: str, media: Path) -> Path:
    """그 topic의 output 폴더 — 이 저장소에 영상이 있으면 여기, 없으면 media 쪽."""
    rel = tracks.output_dir(topic).relative_to(tracks.ROOT)
    here = ROOT / rel
    return here if (here / "nocta" / "shorts_xray_test.mp4").exists() else media / rel


def _spec(topic: str) -> dict:
    d = tracks.data_dir(topic)
    p = next((x for x in (d / "card_news_spec.json", d / "ko" / "card_news_spec.json") if x.exists()), None)
    return json.loads(p.read_text(encoding="utf-8")) if p else {}


def split_title(title: str, search_keyword: str, products: list[str]) -> str:
    """유튜브 제목 → 화면용 훅 한 줄. 검색어 머리("위경련증상, ")·제품 꼬리(", 레티놀 크림")·부제(" - …")를 뗀다.

    머리는 검색어 뒤에 붙은 말이 짧을 때만 뗀다 — "위고비 마운자로 맞은 다음 날 메스꺼움 심할 때, …"처럼 머리가 문장이면
    증상이 거기 있어서 남긴다. 조건절이 끝난 뒤에도 말이 이어지면("…올라온다면 베개 쌓기 말고 이렇게 누우세요") 조건절까지만."""
    t = title.strip()
    head, sep, rest = t.partition(", ")
    kw = _nospace(search_keyword)
    if sep and kw and _nospace(head).startswith(kw) and len(_nospace(head)) - len(kw) <= 8:
        t = rest
    for p in products:
        if p and t.endswith(", " + p):
            t = t[: -len(", " + p)]
    t = t.split(" - ", 1)[0].strip()
    m = re.search(r"(다면|라면)\s", t)
    if m and len(t) > 28:
        t = t[: m.end(1)]
    return t


def _keyword(spec: dict, title: str) -> str:
    """화면용 검색어 — 카드 첫 줄 머리("위염 증상")가 검색어와 같으면 띄어쓰기가 고와서 그걸 쓴다."""
    kw = spec.get("search_keyword") or title.split(",", 1)[0]
    first = (spec.get("title") or [""])[0].split(",", 1)[0].strip()
    return first if first and _nospace(first).startswith(_nospace(kw)) and len(first) <= len(kw) + 10 else kw


def _short(keyword: str) -> str:
    return re.sub(r"\s*증상$", "", keyword).strip() or keyword


def _sources(desc: str) -> list[str]:
    """유튜브 설명란 끝 `출처:` 목록(목숨·안전 주장 편만 있다)."""
    lines = desc.splitlines()
    if "출처:" not in [x.strip() for x in lines]:
        return []
    i = [x.strip() for x in lines].index("출처:")
    out = []
    for x in lines[i + 1:]:
        if not x.strip():
            break
        out.append(x.strip().lstrip("·").strip())
    return out


def load_episodes(channel: str, theme: dict, media: Path, links: dict[str, str]) -> list[Episode]:
    """테마 topic 중 공개된 것만, 공개일 순."""
    pub = published(channel)
    eps = []
    for topic in theme["topics"]:
        row = pub.get(topic)
        if not row:
            continue
        cap = yup._caption(topic)
        if cap is None:
            raise SystemExit(f"❌ {topic}: '유튜브 쇼츠' 캡션이 없음")
        title, desc = cap
        spec = _spec(topic)
        products = yup._products(topic)
        kw = _keyword(spec, title)
        out = _topic_out(topic, media)
        src = out / "nocta" / "shorts_xray_test.mp4"
        if not src.exists():
            raise SystemExit(f"❌ {topic}: 유튜브판 영상 없음 {src}")
        eps.append(Episode(
            topic=topic, video_id=row["video_id"], publish_at=row["publish_at"], title=title, keyword=kw,
            short=_short(kw), hook=split_title(title, spec.get("search_keyword") or kw, products),
            search_volume=int(spec.get("search_volume") or 0), products=products,
            product_lines=yup.product_lines(topic, links), sources=_sources(desc),
            subscribe_line=next((x.strip() for x in desc.splitlines() if "구독" in x), ""), src=str(src)))
    eps.sort(key=lambda e: e.publish_at)
    return eps


# ── 자를 지점 ─────────────────────────────────────────────────────────

def _probe(path: Path, entry: str, stream: str | None = None) -> str:
    cmd = ["ffprobe", "-v", "error"] + (["-select_streams", stream] if stream else []) + \
          ["-show_entries", entry, "-of", "csv=p=0", str(path)]
    return subprocess.run(cmd, capture_output=True, text=True, check=True).stdout.strip()


def _dur(path: Path) -> float:
    return float(_probe(path, "format=duration"))


def _gray(src: Path, first: int, count: int, w: int = 36, h: int = 64) -> list[bytes]:
    """first번째 프레임부터 count장을 작은 회색 프레임으로."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf",
                        f"select=gte(n\\,{first}),scale={w}:{h},format=gray", "-fps_mode", "passthrough",
                        "-frames:v", str(count), "-f", "rawvideo", "-"], capture_output=True, check=True)
    n = w * h
    return [r.stdout[i:i + n] for i in range(0, len(r.stdout) - n + 1, n)]


def _diff(a: bytes, b: bytes) -> float:
    return sum(abs(x - y) for x, y in zip(a, b)) / len(a)


def find_cut(src: Path, narration: Path) -> tuple[int, int, str, dict]:
    """(남길 첫 프레임, 엔딩 카드 첫 프레임, 설명, 근거).

    계산: assemble()은 [제목 카드 0.2초][나레이션 길이][엔딩 카드]를 잇고 경계를 프레임 격자로 반올림한다 →
    엔딩 카드 시작 = round((0.2 + 나레이션 길이) × 30). 검출: 끝에서부터 마지막 프레임과 같은(정지) 프레임이 이어지는
    구간의 첫 프레임. 둘이 1프레임 안에서 맞으면 계산값, 어긋나면(조립 뒤 음성만 바뀐 편 등) 검출값을 쓰고 알린다."""
    total = int(_probe(src, "stream=nb_frames", "v:0"))
    start = round(TITLE_CARD_SEC * FPS)
    calc = round((TITLE_CARD_SEC + _dur(narration)) * FPS)
    first = max(start + 1, min(calc, total) - 60)
    frames = _gray(src, first, total - first)
    i = len(frames) - 1
    while i > 0 and _diff(frames[i - 1], frames[-1]) < STATIC_DIFF:
        i -= 1
    detected = first + i
    if (total - detected) < MIN_END_CARD_SEC * FPS:
        raise SystemExit(f"❌ {src}: 끝 정지 구간이 {(total - detected) / FPS:.2f}초뿐 — 엔딩 카드를 못 찾음")
    # 앞: start 프레임엔 썸네일 카드가 없어야 하고(첫 프레임과 다름) 바로 다음 프레임과 이어져야 한다. 원본엔 썸네일 카드
    # 끝(5번)에 도입 클립이 얹히기 전 칠판 한 프레임이 끼어 있다 — start(6번)부터 남기면 그 프레임도 같이 빠진다.
    head = _gray(src, 0, start + 2)
    head_ok = _diff(head[0], head[start]) >= STATIC_DIFF and _diff(head[start], head[start + 1]) < STATIC_DIFF
    if not head_ok:
        print(f"⚠️ {src}: {start}번 프레임이 썸네일 카드 다음 첫 장면으로 안 보임 — 앞부분을 눈으로 확인할 것", file=sys.stderr)
    proof = {"source_frames": total, "end_card_calc": calc, "end_card_detected": detected,
             "title_card_frames": start, "content_starts_clean": head_ok,
             "narration_sec": round(_dur(narration), 3)}
    if abs(detected - calc) <= 1:
        return start, calc, "계산=검출", proof
    return start, detected, f"계산 {calc} ≠ 검출 {detected} — 검출값 사용", proof


# ── 소리 ──────────────────────────────────────────────────────────────

def loudness(path: Path, t0: float | None = None, t1: float | None = None) -> tuple[float, float]:
    """(통합 LUFS, 트루피크 dBTP)."""
    seek = ["-ss", f"{t0:.3f}", "-to", f"{t1:.3f}"] if t0 is not None else []
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", *seek, "-i", str(path), "-vn",
                        "-af", "loudnorm=print_format=json", "-f", "null", "-"], capture_output=True, text=True)
    js = json.loads(r.stderr[r.stderr.rindex("{"): r.stderr.rindex("}") + 1])
    return float(js["input_i"]), float(js["input_tp"])


def _gain_chain(lufs: float) -> tuple[float, str]:
    """편 음량을 TARGET_LUFS로 올리고 피크만 리미터로 누른다(level=false — 리미터가 음량을 다시 키우지 않게)."""
    gain = TARGET_LUFS - lufs
    return gain, f"volume={gain:.2f}dB,alimiter=limit={10 ** (PEAK_DB / 20):.4f}:level=false:latency=true"


# ── 그림 ──────────────────────────────────────────────────────────────

def _font(size: int, weight: str = "bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_PATH, size, index=_WEIGHT_INDEX[weight])


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int) -> list[str]:
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
            continue
        if cur:
            lines.append(cur)
        while draw.textlength(w, font=font) > width:     # 띄어쓰기 없는 긴 말만 글자 단위로
            k = len(w)
            while k > 1 and draw.textlength(w[:k], font=font) > width:
                k -= 1
            lines.append(w[:k])
            w = w[k:]
        cur = w
    return lines + ([cur] if cur else [])


def _join_wrap(draw, items: list[str], font, width: int, sep: str = " · ") -> list[str]:
    """품목 이름 단위로 줄을 나눈다 — 단어 단위로 자르면 "체중계 ·" / "양배추"처럼 줄 끝에 가운뎃점이 남는다."""
    lines: list[str] = []
    for it in items:
        if lines and draw.textlength(lines[-1] + sep + it, font=font) <= width:
            lines[-1] += sep + it
        else:
            lines.append(it)
    return lines


def _fit(draw, text: str, width: int, max_lines: int, sizes: list[int], weight: str):
    """sizes(큰 것부터) 중 max_lines 안에 드는 가장 큰 글자. 끝까지 안 들면 마지막 줄을 말줄임."""
    for s in sizes:
        f = _font(s, weight)
        ls = _wrap(draw, text, f, width)
        if len(ls) <= max_lines:
            return f, ls
    f = _font(sizes[-1], weight)
    ls = _wrap(draw, text, f, width)[:max_lines]
    while ls[-1] and draw.textlength(ls[-1] + "…", font=f) > width:
        ls[-1] = ls[-1][:-1]
    ls[-1] += "…"
    return f, ls


def _fit_lines(draw, paras: list[str], width: int, max_lines: int, sizes: list[int]):
    """줄을 정해 둔 굵은 제목 — 각 줄이 폭 안에 드는 가장 큰 글자(정한 줄 안에서만 다시 나눈다)."""
    for s in sizes:
        f = _font(s, "bold")
        ls = [x for p in paras for x in _wrap(draw, p, f, width)]
        if len(ls) <= max_lines:
            return f, ls
    f = _font(sizes[-1], "bold")
    return f, [x for p in paras for x in _wrap(draw, p, f, width)][:max_lines]


def _cover_fill(img: Image.Image, w: int, h: int) -> Image.Image:
    s = max(w / img.width, h / img.height)
    r = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
    x, y = (r.width - w) // 2, (r.height - h) // 2
    return r.crop((x, y, x + w, y + h))


def _badge(img: Image.Image) -> Image.Image:
    """우상단 [광고] — 설명란 제휴 링크가 있는 영상은 처음부터 끝까지 화면에 밝힌다(공정위). 쇼츠판 배지와 같은 함수."""
    b = _build_ad_tag_badge("kor", font_size=30, padding=12)
    out = img.convert("RGBA")
    out.alpha_composite(b, (OUT_W - b.width - 28, 28))
    return out


def _gradient(w: int, h: int) -> Image.Image:
    g = Image.new("RGB", (w, h), NAVY)
    d = ImageDraw.Draw(g)
    for y in range(h):
        k = y / h
        d.line([(0, y), (w, y)], fill=tuple(round(a + (b - a) * k) for a, b in zip(NAVY, NAVY_LIGHT)))
    return g


def render_panel(eps: list[Episode], cur: int | None, series: str, brand: str) -> Image.Image:
    """편 화면 위에 얹는 1920×1080 판(가운데는 투명). cur=None이면 엔딩용 — 목록만, 오른쪽은 비운다."""
    img = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, FG_X - 1, OUT_H - 1], fill=(*NAVY, 205))
    d.rectangle([FG_X + FG_W, 0, OUT_W - 1, OUT_H - 1], fill=(*NAVY, 205))

    # 왼쪽 — 채널·몰아보기 이름·편 목록(지금 편만 밝게)
    lx, lw = 72, FG_X - 72 - 48
    d.text((lx, 76), brand, font=_font(34, "semibold"), fill=ACCENT)
    f, ls = _fit(d, series, lw, 2, [58, 52, 46], "bold")
    y = 132
    for line in ls:
        d.text((lx, y), line, font=f, fill=TEXT)
        y += round(f.size * 1.25)
    y += 40
    row = min(88, (OUT_H - 64 - y) // max(len(eps), 1))
    size = min(42, round(row * 0.52))
    for i, e in enumerate(eps):
        on = cur is None or i == cur
        num_f, name_f = _font(size, "bold"), _font(size, "bold" if i == cur else "medium")
        d.text((lx, y), f"{i + 1:02d}", font=num_f, fill=ACCENT if i == cur else DIM)
        nx = lx + round(size * 1.7)
        name = _fit(d, e.keyword, lw - (nx - lx), 1, [size], "bold" if i == cur else "medium")[1][0]
        d.text((nx, y), name, font=name_f, fill=TEXT if i == cur else (SUB if on else DIM))
        if i == cur:
            d.rectangle([lx - 30, y + 4, lx - 22, y + size + 8], fill=ACCENT)
        y += row

    # 오른쪽 — 번호 / 검색어 / 훅 / 제품
    if cur is not None:
        e = eps[cur]
        rx = FG_X + FG_W + 72
        rw = OUT_W - rx - 72
        nf, tf = _font(112, "bold"), _font(50, "semibold")
        num = f"{cur + 1:02d}"
        d.text((rx, 250), num, font=nf, fill=ACCENT, anchor="ls")
        d.text((rx + d.textlength(num, font=nf) + 16, 250), f"/ {len(eps):02d}", font=tf, fill=DIM, anchor="ls")
        y = 300
        f, ls = _fit(d, e.keyword, rw, 2, [96, 88, 80, 72, 64], "bold")
        for line in ls:
            d.text((rx, y), line, font=f, fill=TEXT)
            y += round(f.size * 1.22)
        y += 26
        # 제품 칸을 먼저 재서 훅이 그 위까지만 내려오게 한다
        pf = _font(40, "semibold")
        plines = _join_wrap(d, e.products, pf, rw)[:2]
        p_top = OUT_H - 84 - len(plines) * 54 - (46 if plines else 0)
        hf = _font(46, "medium")
        max_hook = max(1, (p_top - 30 - y) // round(46 * 1.4))
        hf, hl = _fit(d, e.hook, rw, min(4, max_hook), [46, 42, 38], "medium")
        for line in hl:
            d.text((rx, y), line, font=hf, fill=SUB)
            y += round(hf.size * 1.4)
        if plines:
            d.text((rx, p_top), "영상 속 제품", font=_font(30, "semibold"), fill=DIM)
            py = p_top + 46
            for line in plines:
                d.text((rx, py), line, font=pf, fill=TEXT)
                py += 54
    return _badge(img)


def render_card(e: Episode, idx: int, total: int, bg: Image.Image) -> Image.Image:
    """편 사이 제목 카드 — 다음 편 썸네일 카드를 흐리게 깔고 번호·검색어·훅."""
    # 썸네일 카드 글자가 비쳐 보이지 않게(위경련 카드 실측) 작게 줄여 세게 흐린 뒤 키운다 — 색감만 남긴다
    small = _cover_fill(bg.convert("RGB"), OUT_W // 8, OUT_H // 8).filter(ImageFilter.GaussianBlur(12))
    img = Image.blend(small.resize((OUT_W, OUT_H), Image.BILINEAR), Image.new("RGB", (OUT_W, OUT_H), NAVY), 0.72)
    d = ImageDraw.Draw(img)
    lab_f = _font(46, "semibold")
    kf, kl = _fit(d, e.keyword, 1500, 2, [140, 124, 108, 96], "bold")
    hf, hl = _fit(d, e.hook, 1400, 2, [54, 48, 44], "medium")
    h = 46 + 40 + len(kl) * round(kf.size * 1.18) + 30 + len(hl) * round(hf.size * 1.4)
    y = (OUT_H - h) // 2
    d.text((OUT_W // 2, y), f"다음 편 · {idx + 1:02d} / {total:02d}", font=lab_f, fill=ACCENT, anchor="ma")
    y += 46 + 40
    for line in kl:
        d.text((OUT_W // 2, y), line, font=kf, fill=TEXT, anchor="ma")
        y += round(kf.size * 1.18)
    y += 30
    for line in hl:
        d.text((OUT_W // 2, y), line, font=hf, fill=SUB, anchor="ma")
        y += round(hf.size * 1.4)
    return _badge(img).convert("RGB")


def render_cover(theme: dict, eps: list[Episode], tiles: list[Image.Image], brand: str, badge: bool) -> Image.Image:
    """표지(=썸네일 원판) — 왼쪽 큰 증상 말 + "몰아보기 N편", 오른쪽 각 편 썸네일 카드 타일."""
    img = _gradient(OUT_W, OUT_H)
    d = ImageDraw.Draw(img)
    # 오른쪽 타일 — 가장 크게 들어가는 격자
    ax0, ay0, aw, ah, gap = 1010, 80, 850, 920, 22
    best = None
    for cols in range(1, len(tiles) + 1):
        rows = -(-len(tiles) // cols)
        th = min((ah - (rows - 1) * gap) / rows, ((aw - (cols - 1) * gap) / cols) * 16 / 9)
        if best is None or th > best[0]:
            best = (th, cols, rows)
    th, cols, rows = best
    th = int(th)
    tw = int(th * 9 / 16)
    gx = ax0 + (aw - (cols * tw + (cols - 1) * gap)) // 2
    gy = ay0 + (ah - (rows * th + (rows - 1) * gap)) // 2
    mask = Image.new("L", (tw, th), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tw - 1, th - 1], radius=18, fill=255)
    for k, t in enumerate(tiles):
        x = gx + (k % cols) * (tw + gap)
        y = gy + (k // cols) * (th + gap)
        img.paste(_cover_fill(t.convert("RGB"), tw, th), (x, y), mask)
        d.rounded_rectangle([x, y, x + tw - 1, y + th - 1], radius=18, outline=(255, 255, 255), width=3)
    # 왼쪽 글자
    lx, lw = 110, 840
    bf = _font(40, "semibold")
    kf, kl = _fit_lines(d, theme["thumb_text"].split("\n"), lw, 3, [200, 184, 168, 152, 136, 120])
    sf = _font(104, "bold")
    h = 40 + 50 + len(kl) * round(kf.size * 1.12) + 40 + 104
    y = (OUT_H - h) // 2
    d.text((lx, y), brand, font=bf, fill=ACCENT)
    y += 40 + 50
    for line in kl:
        d.text((lx, y), line, font=kf, fill=TEXT)
        y += round(kf.size * 1.12)
    y += 40
    d.text((lx, y), f"몰아보기 {len(eps)}편", font=sf, fill=ACCENT)
    return (_badge(img) if badge else img.convert("RGBA")).convert("RGB")


def render_end(end_frame: Image.Image, eps: list[Episode], series: str, brand: str) -> Image.Image:
    """맨 끝 엔딩 — 마지막 편의 엔딩 카드 그림을 같은 가운데 자리에, 옆 판엔 이번 몰아보기 목록 전체."""
    base = _cover_fill(end_frame.convert("RGB"), OUT_W, OUT_H).filter(ImageFilter.GaussianBlur(30))
    base.paste(end_frame.convert("RGB").resize((FG_W, FG_H), Image.LANCZOS), (FG_X, 0))
    out = base.convert("RGBA")
    out.alpha_composite(render_panel(eps, None, series, brand))
    return out.convert("RGB")


def frame_at(src: Path, frame: int) -> Image.Image:
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(src), "-vf", f"select=eq(n\\,{frame})",
                        "-fps_mode", "passthrough", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                       capture_output=True, check=True)
    from io import BytesIO
    return Image.open(BytesIO(r.stdout)).convert("RGB")


# ── 설명란·제목 ───────────────────────────────────────────────────────

def _ts(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def build_title(theme: dict, eps: list[Episode]) -> str:
    """검색어 머리 | 편 이름(검색량 큰 순) <테마> 몰아보기 N편 — 100자 안, 넘치면 편 이름을 뒤에서 뺀다."""
    head, label = theme["title_head"], f"{theme['name']} 몰아보기 {len(eps)}편"
    names = [e.short for e in sorted(eps, key=lambda e: -e.search_volume) if _nospace(e.short) not in _nospace(head)]
    while names and len(f"{head} | {'·'.join(names)} {label}") > 100:
        names.pop()
    return f"{head} | {'·'.join(names)} {label}" if names else f"{head} | {label}"


def chapters(eps: list[Episode]) -> list[tuple[float, str]]:
    """유튜브 목차 — 0:00부터, 3개 이상, 10초 이상 간격. 표지는 2.5초라 따로 두면 10초 규칙에 걸려 1편 목차에 합친다."""
    out = [(0.0 if i == 0 else e.chapter_sec, f"{i + 1}. {e.keyword} — {e.hook}") for i, e in enumerate(eps)]
    gaps = [b[0] - a[0] for a, b in zip(out, out[1:])]
    if len(out) < 3 or any(g < 10 for g in gaps):
        raise SystemExit(f"❌ 목차 규칙 위반(3개 이상·10초 간격): {[(_ts(t), x) for t, x in out]}")
    return out


def build_description(theme: dict, eps: list[Episode], brand: str) -> str:
    names = "·".join(e.short for e in eps)
    parts = [f"{theme['intro']} {brand} 쇼츠 {len(eps)}편({names})을 한 번에 이어 붙였어요."]
    parts.append("⏱ 목차\n" + "\n".join(f"{_ts(t)} {x}" for t, x in chapters(eps)))
    prod = [f"{i + 1}. {e.keyword}\n" + "\n".join(e.product_lines) for i, e in enumerate(eps) if e.product_lines]
    if prod:
        parts.append("📦 편별 영상 속 제품\n" + "\n\n".join(prod))
        parts.append(f"[광고] {yup.PRODUCT_LINK_NOTICE}")
    srcs = [s for e in eps for s in e.sources]
    if srcs:
        parts.append("출처:\n" + "\n".join(f"· {s}" for s in dict.fromkeys(srcs)))
    sub = next((e.subscribe_line for e in reversed(eps) if e.subscribe_line), "")
    if sub:
        parts.append(sub)
    tags = [brand] + [_nospace(k) for k in theme["search_keywords"]] + [_nospace(e.keyword) for e in eps] + ["몰아보기"]
    parts.append(" ".join(f"#{t}" for t in dict.fromkeys(tags)))
    return "\n\n".join(parts)


def build_tags(theme: dict, eps: list[Episode], desc: str, channel: str) -> list[str]:
    items = list(theme["search_keywords"]) + [e.keyword for e in eps] + [p for e in eps for p in e.products]
    return yup._tags(desc, yup.CHANNELS[channel]["base_tags"], items)


def write_upload_md(path: Path, title: str, desc: str, tags: list[str]) -> None:
    """yt_upload.read_longform_upload()가 읽는 꼴 — 사람이 고쳐도 이 세 칸만 지키면 그대로 올라간다."""
    path.write_text(f"제목: {title}\n\n설명란:\n{desc}\n\n태그: {', '.join(tags)}\n", encoding="utf-8")


# ── 조립 ──────────────────────────────────────────────────────────────

X264 = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-g", str(FPS * 2), "-video_track_timescale", "15360"]


def _run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"❌ ffmpeg 실패: {' '.join(cmd[:6])} …")


def _still(png: Path, frames: int, out: Path) -> None:
    _run(["ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", str(png), "-frames:v", str(frames), *X264, str(out)])


def _silence(frames: int, out: Path) -> None:
    _run(["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=stereo", "-af", f"atrim=end_sample={frames * SPF}",
          "-c:a", "pcm_s16le", str(out)])


def _episode_av(e: Episode, panel: Path, out_v: Path, out_a: Path, gain_chain: str) -> None:
    n = e.cut_to - e.cut_from
    fc = (f"[0:v]trim=start_frame={e.cut_from}:end_frame={e.cut_to},setpts=PTS-STARTPTS,split[a][b];"
          f"[a]scale=480:-2,crop=480:270,boxblur=8:2,scale={OUT_W}:{OUT_H},eq=brightness=-0.06:saturation=0.8[bg];"
          f"[b]scale={FG_W}:{FG_H}:flags=lanczos[fg];[bg][fg]overlay={FG_X}:0[m];[m][1:v]overlay=0:0,format=yuv420p[v]")
    _run(["ffmpeg", "-y", "-i", e.src, "-i", str(panel), "-filter_complex", fc, "-map", "[v]", "-an",
          "-frames:v", str(n), *X264, str(out_v)])
    # 소리를 화면 프레임 수 × 1600샘플에 정확히 맞춘다 — 편마다 몇 ms씩 어긋나면 이어 붙일수록 자막과 말이 벌어진다
    af = (f"atrim=start={e.cut_from / FPS:.6f}:end={e.cut_to / FPS:.6f},asetpts=PTS-STARTPTS,aresample={SR},"
          f"aformat=channel_layouts=stereo,{gain_chain},afade=t=in:d=0.02,afade=t=out:st={n / FPS - 0.04:.3f}:d=0.04,"
          f"apad=whole_len={n * SPF},atrim=end_sample={n * SPF}")
    _run(["ffmpeg", "-y", "-i", e.src, "-vn", "-af", af, "-c:a", "pcm_s16le", str(out_a)])


def build(theme: dict, eps: list[Episode], out_dir: Path) -> dict:
    brand = tracks.brand(eps[0].topic)
    series = f"{theme['name']} 몰아보기"
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        segs: list[tuple[Path, Path]] = []
        t = 0.0

        # 1) 표지 + 썸네일 — 각 편 썸네일 카드(0.2초 구간 가운데 프레임)를 타일로
        tiles = [frame_at(Path(e.src), round(TITLE_CARD_SEC * FPS) // 2) for e in eps]
        render_cover(theme, eps, tiles, brand, badge=False).resize((1280, 720), Image.LANCZOS) \
            .save(out_dir / "thumbnail.jpg", quality=92)
        cover_png = tmp / "cover.png"
        render_cover(theme, eps, tiles, brand, badge=True).save(cover_png)
        nf = round(COVER_SEC * FPS)
        segs.append((tmp / "s00.mp4", tmp / "s00.wav"))
        _still(cover_png, nf, segs[-1][0]); _silence(nf, segs[-1][1])
        t += nf / FPS

        # 2) 편마다 [제목 카드(2편부터)] + 본편
        for i, e in enumerate(eps):
            if i:
                card_png = tmp / f"card{i:02d}.png"
                render_card(e, i, len(eps), tiles[i]).save(card_png)
                nf = round(CARD_SEC * FPS)
                e.chapter_sec = t
                segs.append((tmp / f"c{i:02d}.mp4", tmp / f"c{i:02d}.wav"))
                _still(card_png, nf, segs[-1][0]); _silence(nf, segs[-1][1])
                t += nf / FPS
            e.start_sec = t
            lufs, _ = loudness(Path(e.src), e.cut_from / FPS, e.cut_to / FPS)
            e.loudness_in, (e.gain_db, chain) = lufs, _gain_chain(lufs)
            panel = tmp / f"panel{i:02d}.png"
            render_panel(eps, i, series, brand).save(panel)
            segs.append((tmp / f"e{i:02d}.mp4", tmp / f"e{i:02d}.wav"))
            _episode_av(e, panel, segs[-1][0], segs[-1][1], chain)
            t += (e.cut_to - e.cut_from) / FPS
            print(f"  {i + 1:2d}. {e.topic:8s} {e.keyword:14s} {(e.cut_to - e.cut_from) / FPS:6.2f}초  "
                  f"{lufs:+.1f}→{TARGET_LUFS:.0f} LUFS  ({e.cut_note})")

        # 3) 맨 끝 엔딩 한 번 — 마지막 편의 엔딩 카드 그림 + 채널 엔딩 멘트(조립기와 같은 쉼·여운)
        last = eps[-1]
        end_png = tmp / "end.png"
        render_end(frame_at(Path(last.src), last.cut_to + 3), eps, series, brand).save(end_png)
        outro_sec = _dur(OUTRO_KOR)
        nf = -(-round((OUTRO_GAP + outro_sec + OUTRO_TAIL) * 1000) * FPS // 1000)
        _, o_chain = _gain_chain(loudness(OUTRO_KOR)[0])
        segs.append((tmp / "z.mp4", tmp / "z.wav"))
        _still(end_png, nf, segs[-1][0])
        gap_ms = round(OUTRO_GAP * 1000)
        _run(["ffmpeg", "-y", "-i", str(OUTRO_KOR), "-af",
              f"aresample={SR},aformat=channel_layouts=stereo,{o_chain},adelay={gap_ms}|{gap_ms},"
              f"apad=whole_len={nf * SPF},atrim=end_sample={nf * SPF}", "-c:a", "pcm_s16le", str(segs[-1][1])])
        end_start = t
        t += nf / FPS

        # 4) 잇기 — 화면은 같은 설정으로 인코딩한 조각을 복사로, 소리는 PCM으로 샘플 단위로 이은 뒤 한 번만 AAC
        (tmp / "v.txt").write_text("".join(f"file '{v}'\n" for v, _ in segs))
        (tmp / "a.txt").write_text("".join(f"file '{a}'\n" for _, a in segs))
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "v.txt"), "-c", "copy", str(tmp / "v.mp4")])
        _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(tmp / "a.txt"), "-c", "copy", str(tmp / "a.wav")])
        final = out_dir / "longform.mp4"
        _run(["ffmpeg", "-y", "-i", str(tmp / "v.mp4"), "-i", str(tmp / "a.wav"), "-map", "0:v", "-map", "1:a",
              "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(final)])

    frames = int(_probe(final, "stream=nb_frames", "v:0"))
    expect = round(t * FPS)
    a_dur = float(_probe(final, "stream=duration", "a:0"))
    if frames != expect or abs(a_dur - frames / FPS) > 0.05:
        raise SystemExit(f"❌ 길이 불일치: 화면 {frames}프레임(예상 {expect}), 소리 {a_dur:.3f}초")
    lufs, tp = loudness(final)
    return {"frames": frames, "duration_sec": round(frames / FPS, 3), "audio_sec": round(a_dur, 3),
            "loudness_lufs": lufs, "true_peak_db": tp, "end_card_start_sec": round(end_start, 3),
            "end_card_sec": round(nf / FPS, 3)}


# ── 테마 후보 표 ──────────────────────────────────────────────────────

def list_themes(channel: str) -> None:
    pub = published(channel)
    print(f"| 테마 | 대표 검색어(월 검색량) | 공개 편 | 편 수 | 메모 |\n|---|---|---|---|---|")
    for slug, th in load_themes(channel).items():
        vols = sorted(th.get("volumes", {}).items(), key=lambda x: -x[1])[:3]
        on = [t for t in th["topics"] if t in pub]
        print(f"| {slug} {th['name']} | {' · '.join(f'{k} {v:,}' for k, v in vols)} | {', '.join(on)} | "
              f"{len(on)} | {th.get('note', '')} |")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("channel", choices=list(yup.CHANNELS))
    ap.add_argument("theme", nargs="?", help="compilation_themes.json의 테마 키(예: stomach)")
    ap.add_argument("--list", action="store_true", help="테마 후보 표")
    ap.add_argument("--dry-run", action="store_true", help="편·자를 지점·제목·설명란만 보고 조립하지 않음")
    ap.add_argument("--date", default=dt.datetime.now(KST).strftime("%Y%m%d"), help="결과 폴더 날짜(기본 오늘 KST)")
    ap.add_argument("--min-episodes", type=int, default=3)
    a = ap.parse_args()
    if a.list or not a.theme:
        list_themes(a.channel)
        return
    themes = load_themes(a.channel)
    if a.theme not in themes:
        raise SystemExit(f"❌ 테마 {a.theme} 없음 — {list(themes)}")
    theme = themes[a.theme]

    from lib.brandconnect import existing_naver_links
    media = media_root()
    eps = load_episodes(a.channel, theme, media, existing_naver_links())
    if len(eps) < a.min_episodes:
        raise SystemExit(f"❌ 공개된 편이 {len(eps)}편뿐({[e.topic for e in eps]}) — 최소 {a.min_episodes}편")
    t = COVER_SEC
    for i, e in enumerate(eps):
        narration = _resolve_output_file(Path(e.src).parent.parent, "_narration.mp3")
        if narration is None:
            raise SystemExit(f"❌ {e.topic}: 나레이션 음성이 없어 엔딩 카드 시작을 계산할 수 없음")
        e.cut_from, e.cut_to, e.cut_note, e.extra = find_cut(Path(e.src), narration)
        if i:
            e.chapter_sec = t
            t += CARD_SEC
        e.start_sec = t
        t += (e.cut_to - e.cut_from) / FPS

    title = build_title(theme, eps)
    if a.dry_run:
        for i, e in enumerate(eps):
            print(f"{i + 1:2d}. {e.topic:8s} {e.publish_at[:10]} 프레임 {e.cut_from}~{e.cut_to} "
                  f"({(e.cut_to - e.cut_from) / FPS:.2f}초, {e.cut_note})  {e.keyword} — {e.hook}")
        brand = tracks.brand(eps[0].topic)
        print(f"\n제목({len(title)}자): {title}\n\n{build_description(theme, eps, brand)}")
        return

    out_dir = OUT_BASE / f"{a.channel}_{a.theme}_{a.date}"
    print(f"조립 → {out_dir.relative_to(ROOT)} ({len(eps)}편)")
    stats = build(theme, eps, out_dir)
    brand = tracks.brand(eps[0].topic)
    desc = build_description(theme, eps, brand)
    write_upload_md(out_dir / "upload.md", title, desc, build_tags(theme, eps, desc, a.channel))
    manifest = {
        "channel": a.channel, "theme": a.theme, "theme_name": theme["name"], "folder": out_dir.name,
        "created_at": dt.datetime.now(KST).isoformat(timespec="seconds"), "title": title,
        "upload_key": f"{a.channel}/{yup.LONGFORM}{out_dir.name}",
        "layout": {"size": [OUT_W, OUT_H], "short": [FG_W, FG_H, FG_X], "cover_sec": COVER_SEC, "card_sec": CARD_SEC,
                   "target_lufs": TARGET_LUFS},
        **stats,
        "episodes": [{
            "n": i + 1, "topic": e.topic, "video_id": e.video_id, "url": f"https://youtube.com/shorts/{e.video_id}",
            "publish_at": e.publish_at, "keyword": e.keyword, "hook": e.hook, "products": e.products,
            "start_sec": round(e.start_sec, 3), "start": _ts(e.start_sec), "chapter": _ts(0 if i == 0 else e.chapter_sec),
            "source": str(Path(e.src).relative_to(media)) if Path(e.src).is_relative_to(media) else e.src,
            "cut": {"from_frame": e.cut_from, "to_frame": e.cut_to, "kept_sec": round((e.cut_to - e.cut_from) / FPS, 3),
                    "method": e.cut_note, **e.extra},
            "loudness_in": e.loudness_in, "gain_db": round(e.gain_db, 2)} for i, e in enumerate(eps)],
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ {out_dir.relative_to(ROOT)}/longform.mp4 {stats['duration_sec'] / 60:.1f}분 · "
          f"{stats['loudness_lufs']:.1f} LUFS · 제목 {len(title)}자")


if __name__ == "__main__":
    main()
