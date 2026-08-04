# 타임라인/여정형 숏츠 템플릿. WHY: 메커니즘→아이템1..N→"해결 정리" 순서로 세로
# 트랙을 따라 정거장(스탑)이 진행되는 포맷 — 카드뉴스식 슬라이드 전환 대신 "여정을
# 따라가는" 느낌을 준다. 배경은 칠판이 아니라 오프화이트/쿨그레이 그라디언트(차분한
# 인포그래픽 톤), 낙서 없음.
#
# 2026-08-04 재구축: 오늘 낮에 이미 한 번 완성·하드닝까지 끝난 파일이었으나 커밋 전
# 동시 세션의 git 작업으로 디스크에서 유실됨 — 동일 스펙으로 처음부터 다시 작성.
#
# 핵심 안전장치(오늘 스크린샷 리뷰로 실제 발견된 버그): 클로징 "정리" 스탑의 불릿
# 목록이 화면 맨 아래 유튜브 쇼츠 앱 UI(좋아요/댓글/자막 버튼 등, 우측 150px·하단
# 320px)에 거의 닿을 만큼 내려와 있었다 — fit_lines_in_box()로 안전영역 안에
# 들어갈 때까지 폰트/줄간격을 줄이고, 그래도 안 들어가면 조용히 잘라내지 않고
# RuntimeError로 즉시 알린다.
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from lib.video_assembler import _title_font_for_lang, _wrap_text_for_lang  # noqa: E402

W, H = 1080, 1920
FPS = 30

# WHY 중복 정의(video_assembler.py의 로컬 상수라 import 불가): 이 값들은 반드시
# video_assembler.py의 _YT_SAFE_RIGHT/_YT_SAFE_BOTTOM과 항상 동일해야 한다 —
# 유튜브 쇼츠 앱 UI(좋아요/댓글/공유 버튼 열, 채널명·설명 캡션 띠)가 실기기에서
# 가리는 픽셀 범위를 실측한 값이라 template마다 따로 잴 필요는 없지만, 그쪽 값이
# 바뀌면 여기도 같이 바꿔야 한다.
_YT_SAFE_RIGHT = 150
_YT_SAFE_BOTTOM = 320

# WHY 색 팔레트를 5~6개로: 항상 코랄 하나로 고정되면 topic이 여러 개 쌓였을 때
# 전부 같은 색으로 보인다는 문제(video_assembler.py의 _accent_color_for_seed와
# 같은 이유) — 오프화이트 배경 위에서도 선명하게 도드라지는 톤만 골랐다.
_ACCENT_PALETTE = [
    (224, 92, 90),    # 코랄
    (48, 158, 152),   # 틸
    (86, 106, 210),   # 인디고
    (214, 155, 52),   # 앰버
    (146, 98, 196),   # 바이올렛
    (58, 140, 100),   # 세이지 그린
]

# WHY 배경 톤도 seed로: 매번 똑같은 오프화이트/쿨그레이 그라디언트만 쓰면 색상
# 축(accent)이 달라도 뼈대가 같아 보인다 — 미세한 hue만 다른 5종.
_BG_TONE_PALETTE = [
    ((250, 249, 247), (231, 233, 238)),  # 뉴트럴 쿨그레이
    ((250, 247, 245), (234, 228, 225)),  # 웜 오프화이트
    ((247, 249, 250), (222, 230, 236)),  # 블루 틴트
    ((249, 248, 250), (230, 226, 238)),  # 라벤더 틴트
    ((248, 250, 248), (225, 233, 226)),  # 민트 틴트
]

# WHY 2종만: 필요 이상으로 늘리면 "채워진 원 vs 링" 구분 자체가 옅어져서 변주
# 효과가 없다 — 눈에 확실히 다르게 보이는 두 스타일만.
_NODE_ICON_STYLES = ["filled", "ringed"]

_CLOSING_LABEL_BY_LANG = {"kor": "오늘의 정리", "ja": "今日のまとめ"}
_CLOSING_LABEL_DEFAULT = "Today's Recap"

_TEXT_DARK = (45, 48, 54)
_TEXT_MUTED = (140, 143, 150)
_RAIL_COLOR = (214, 217, 222)
_FUTURE_FILL = (226, 228, 232)
_FUTURE_OUTLINE = (198, 201, 206)

_measure_img = Image.new("RGB", (10, 10))
_measure_draw = ImageDraw.Draw(_measure_img)


def _seed_pick(text: str, k: int, c0: int, options: list):
    """프로젝트 표준 결정적 시드 방식(video_assembler.py의 _accent_color_for_seed와
    동일 원리) — hash() 대신 문자 코드 합을 쓰는 이유는 파이썬 hash()가 프로세스마다
    랜덤이라 재생성 때마다 결과가 바뀌기 때문. k/c0을 축마다 다르게 줘서 같은
    title이라도 색·배경톤·아이콘 스타일이 서로 독립적으로 갈리게 한다."""
    seed_val = sum(ord(c) * (i * k + c0) for i, c in enumerate(text)) % len(options)
    return options[seed_val]


def fit_lines_in_box(
    lines: list[str],
    box_height: int,
    start_font_size: int,
    *,
    font_path: str,
    font_index: int,
    max_width: int,
    lang: str,
    floor: int = 14,
    step: int = 2,
    line_gap_ratio: float = 0.34,
):
    """N줄 텍스트가 box_height 안에 들어갈 때까지 폰트 크기/줄간격을 줄인다.
    WHY(오늘 발견된 실제 버그): 클로징 스탑의 불릿 목록을 고정 폰트 크기로 그리면
    아이템 개수(N)가 많은 topic에서 안전영역(H - _YT_SAFE_BOTTOM) 아래로 흘러넘친다
    — 여기서부터 floor(기본 14px)까지 줄여보고, 그래도 안 들어가면 조용히 잘라내지
    않고 RuntimeError로 바로 알린다(오늘 이 자리에서 발견된 버그를 재현 불가능하게
    막는 게 목적이라 "일단 그리고 본다"는 절대 금지).

    빈 문자열("")은 스펙상 문단 사이 여백 줄로 쓰이므로 줄바꿈 대상에서 제외하고
    그대로 빈 줄 하나로 유지한다."""
    size = start_font_size
    while size >= floor:
        font = ImageFont.truetype(font_path, size, index=font_index)
        wrapped: list[str] = []
        for line in lines:
            if line.strip() == "":
                wrapped.append("")
            else:
                wrapped.extend(_wrap_text_for_lang(_measure_draw, line, font, max_width, lang))
        line_h = size + int(size * line_gap_ratio)
        total_h = line_h * max(len(wrapped), 1)
        if total_h <= box_height:
            return font, wrapped, line_h
        size -= step
    raise RuntimeError(
        f"fit_lines_in_box: {len(lines)}줄 텍스트가 box_height={box_height}px 안에 "
        f"floor={floor}px까지 줄여도 들어가지 않습니다 (마지막 시도: {total_h}px). "
        "안전영역을 침범하므로 조용히 잘라내지 않고 중단합니다."
    )


def _make_gradient_bg(top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    return img


def _draw_checkmark(draw: ImageDraw.ImageDraw, cx: float, cy: float, size: float, color):
    w = max(2, int(size * 0.18))
    p1 = (cx - size * 0.5, cy)
    p2 = (cx - size * 0.12, cy + size * 0.42)
    p3 = (cx + size * 0.55, cy - size * 0.42)
    draw.line([p1, p2, p3], fill=color, width=w, joint="curve")


def _draw_title(canvas: Image.Image, eyebrow: str, title_lines: list[str], accent, font_path, font_index, lang):
    """상단 훅 배너(eyebrow 태그 + 타이틀). WHY 안전영역 체크(스펙 요구사항):
    타이틀도 stop label·클로징 헤더와 동일하게 fit_lines_in_box로 우측 세이프존
    (_YT_SAFE_RIGHT) 안에 들어가는지 확인한다."""
    draw = ImageDraw.Draw(canvas)
    max_w = W - 140 - _YT_SAFE_RIGHT
    left_x = 70

    if eyebrow:
        eb_font = ImageFont.truetype(font_path, 30, index=font_index)
        bbox = draw.textbbox((0, 0), eyebrow, font=eb_font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        pad_x, pad_y = 22, 12
        pill_w, pill_h = tw + pad_x * 2, th + pad_y * 2
        draw.rounded_rectangle([left_x, 40, left_x + pill_w, 40 + pill_h], radius=pill_h / 2, fill=accent)
        draw.text((left_x + pad_x - bbox[0], 40 + pad_y - bbox[1]), eyebrow, font=eb_font, fill=(255, 255, 255))
        title_top = 40 + pill_h + 22
    else:
        title_top = 60

    title_box_h = 260 - title_top
    if not title_lines:
        return
    font, wrapped, line_h = fit_lines_in_box(
        title_lines, title_box_h, 58,
        font_path=font_path, font_index=font_index, max_width=max_w, lang=lang, floor=14,
    )
    y = title_top
    for line in wrapped:
        if line:
            draw.text((left_x, y), line, font=font, fill=_TEXT_DARK)
        y += line_h


def _draw_stop_badge(canvas_rgba: Image.Image, cx: float, cy: float, state: str, accent, icon_style: str):
    draw = ImageDraw.Draw(canvas_rgba)
    if state == "future":
        r = 11
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_FUTURE_FILL, outline=_FUTURE_OUTLINE, width=2)
        return
    if state == "current":
        # 은은한 글로우 후광 — 별도 레이어에 블러 처리 후 합성.
        glow = Image.new("RGBA", canvas_rgba.size, (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gr = 56
        gdraw.ellipse([cx - gr, cy - gr, cx + gr, cy + gr], fill=accent + (150,))
        glow = glow.filter(ImageFilter.GaussianBlur(22))
        canvas_rgba.alpha_composite(glow)
        draw = ImageDraw.Draw(canvas_rgba)
        r = 27
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent + (255,), outline=(255, 255, 255, 255), width=5)
        return
    # passed
    r = 18
    if icon_style == "filled":
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent + (255,))
        _draw_checkmark(draw, cx, cy, r * 1.15, (255, 255, 255, 255))
    else:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 255), outline=accent + (255,), width=4)
        _draw_checkmark(draw, cx, cy, r * 1.15, accent + (255,))


def _draw_track(canvas_rgba: Image.Image, track_x: float, track_top: float, track_bottom: float,
                 dot_ys: list[float], current_idx: int, accent, icon_style: str):
    draw = ImageDraw.Draw(canvas_rgba)
    draw.line([(track_x, track_top), (track_x, track_bottom)], fill=_RAIL_COLOR + (255,), width=6)
    for i, y in enumerate(dot_ys):
        state = "current" if i == current_idx else ("passed" if i < current_idx else "future")
        _draw_stop_badge(canvas_rgba, track_x, y, state, accent, icon_style)


def _closing_bullets_and_header(items, closing, lang) -> tuple[str, list[str]]:
    headline = closing.get("headline") or []
    if headline:
        first_group = headline[0]
        if isinstance(first_group, list):
            header_text = " ".join(first_group)
        else:
            header_text = str(first_group)
    else:
        header_text = _CLOSING_LABEL_BY_LANG.get(lang, _CLOSING_LABEL_DEFAULT)
    bullets = [f"• {it.get('name', '')}" for it in items]
    return header_text, bullets


def _draw_detail_panel(canvas_rgba: Image.Image, stop: dict, panel_box: tuple[int, int, int, int],
                        accent, font_path, font_index, lang):
    """현재 스탑(current)의 라벨 + 본문(또는 클로징 헤더 + 불릿)을 고정 패널
    영역(panel_box) 안에 그린다. WHY 패널을 노드 y좌표가 아니라 항상 같은 고정
    박스로 두는지: 노드는 트랙을 따라 아래로 내려가므로, 본문을 노드 옆에
    붙이면 트랙 하단(=마지막 스탑, 하필 불릿이 제일 많은 클로징)에서 안전영역
    아래로 넘칠 위험이 구조적으로 가장 크다 — 패널을 고정 박스로 분리하면 어떤
    스탑이 현재든 동일한 안전 높이(panel_box) 안에서만 fit_lines_in_box가 동작해
    이 버그 자체가 재현 불가능해진다."""
    x0, y0, x1, y1 = panel_box
    max_w = x1 - x0
    draw = ImageDraw.Draw(canvas_rgba)

    header_box_h = 150
    header_font, header_wrapped, header_line_h = fit_lines_in_box(
        [stop["name"]], header_box_h, 50,
        font_path=font_path, font_index=font_index, max_width=max_w, lang=lang, floor=14,
    )
    y = y0
    for line in header_wrapped:
        if line:
            draw.text((x0, y), line, font=header_font, fill=accent)
        y += header_line_h
    header_bottom = y + 16

    body_lines = stop["body"] if stop["type"] == "item" else stop["bullets"]
    body_box_h = y1 - header_bottom
    body_font, body_wrapped, body_line_h = fit_lines_in_box(
        body_lines, body_box_h, 42,
        font_path=font_path, font_index=font_index, max_width=max_w, lang=lang, floor=14,
    )
    by = header_bottom
    for line in body_wrapped:
        if line:
            draw.text((x0, by), line, font=body_font, fill=_TEXT_DARK)
        by += body_line_h

    # ⚠️ 오늘 발견된 버그 지점 — 실제로 안전선 안에 들어갔는지 마지막 줄 픽셀
    # y좌표로 다시 확인한다(폰트 렌더링이 이론상 fit 계산과 미세하게 어긋나는
    # 경우 대비, 예: 하강부(descender)가 긴 문자).
    lowest_y = by
    safe_bottom = H - _YT_SAFE_BOTTOM
    if lowest_y > safe_bottom:
        raise RuntimeError(
            f"detail panel 콘텐츠가 안전영역을 벗어났습니다: lowest_y={lowest_y} > "
            f"safe_bottom={safe_bottom} (stop={stop['name']!r})"
        )


def _stop_index_at(ranges: list[tuple[float, float]], t: float) -> int:
    for i, (start, end) in enumerate(ranges):
        if start <= t < end:
            return i
    return len(ranges) - 1


def _probe_duration(audio_path: str) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    return float(result.stdout.strip())


def render(topic_dir: str, lang: str, audio_path: str, srt_path: str, spec_path: str, out_path: str) -> None:
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    items = spec.get("items", [])
    if not items:
        raise RuntimeError(f"{spec_path}: 'items'가 비어 있어 타임라인 스탑을 만들 수 없습니다")
    closing = spec.get("closing", {})
    title_lines = spec.get("title", [])
    eyebrow = spec.get("eyebrow", "")
    title_str = " ".join(title_lines) if title_lines else Path(topic_dir).name

    duration = _probe_duration(audio_path)
    font_path, font_index = _title_font_for_lang(lang)

    accent = _seed_pick(title_str, 1, 2, _ACCENT_PALETTE)
    bg_top, bg_bottom = _seed_pick(title_str, 3, 5, _BG_TONE_PALETTE)
    icon_style = _seed_pick(title_str, 5, 9, _NODE_ICON_STYLES)

    stops = [{"type": "item", "name": it.get("name", ""), "body": it.get("body", [])} for it in items]
    closing_header, closing_bullets = _closing_bullets_and_header(items, closing, lang)
    stops.append({"type": "closing", "name": closing_header, "bullets": closing_bullets})
    total_stops = len(stops)

    weights = []
    for s in stops:
        text_len = len(s["name"]) + sum(len(x) for x in (s["body"] if s["type"] == "item" else s["bullets"]))
        weights.append(max(text_len, 1))
    total_w = sum(weights)
    ranges: list[tuple[float, float]] = []
    t_cursor = 0.0
    for i, w in enumerate(weights):
        end = duration if i == total_stops - 1 else t_cursor + duration * w / total_w
        ranges.append((t_cursor, end))
        t_cursor = end

    track_x = 120
    track_top = 300
    track_bottom = H - _YT_SAFE_BOTTOM - 40
    if total_stops > 1:
        dot_ys = [track_top + i * (track_bottom - track_top) / (total_stops - 1) for i in range(total_stops)]
    else:
        dot_ys = [track_top]

    panel_box = (230, track_top + 10, W - _YT_SAFE_RIGHT - 50, track_bottom - 10)

    bg_base = _make_gradient_bg(bg_top, bg_bottom)
    _draw_title(bg_base, eyebrow, title_lines, accent, font_path, font_index, lang)
    header_rgba = bg_base.convert("RGBA")

    state_bases: list[Image.Image] = []
    for idx, stop in enumerate(stops):
        frame_rgba = header_rgba.copy()
        _draw_track(frame_rgba, track_x, track_top, track_bottom, dot_ys, idx, accent, icon_style)
        _draw_detail_panel(frame_rgba, stop, panel_box, accent, font_path, font_index, lang)
        state_bases.append(frame_rgba.convert("RGB"))

    total_frames = max(1, round(duration * FPS))
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", audio_path,
        "-map", "0:v", "-map", "1:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        str(out_path),
    ]
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for f in range(total_frames):
            t = f / FPS
            idx = _stop_index_at(ranges, t)
            frame = state_bases[idx].copy()
            draw = ImageDraw.Draw(frame)
            frac = min(max(t / duration, 0.0), 1.0) if duration > 0 else 1.0
            progress_y = track_top + frac * (track_bottom - track_top)
            draw.line([(track_x, track_top), (track_x, progress_y)], fill=accent, width=8)
            marker_r = 9
            draw.ellipse(
                [track_x - marker_r, progress_y - marker_r, track_x + marker_r, progress_y + marker_r],
                fill=accent, outline=(255, 255, 255), width=3,
            )
            proc.stdin.write(frame.tobytes())
    finally:
        proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        stderr = proc.stderr.read().decode(errors="replace") if proc.stderr else ""
        raise RuntimeError(f"ffmpeg 인코딩 실패(exit={ret}):\n{stderr[-2000:]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="타임라인/여정형 숏츠 템플릿 단독 테스트용 CLI")
    parser.add_argument("--topic-dir", required=True)
    parser.add_argument("--lang", required=True)
    parser.add_argument("--audio", required=True)
    parser.add_argument("--srt", required=True)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    render(args.topic_dir, args.lang, args.audio, args.srt, args.spec, args.out)
    print(f"done: {args.out}")
