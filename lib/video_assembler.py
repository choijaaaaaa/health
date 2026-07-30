# 캐릭터(Kling 모션 루프) + 실사진 배경 + 자막을 합쳐 숏츠 영상으로 조립.
# WHY: 이 ffmpeg 빌드엔 drawtext/subtitles(libass) 필터가 없어서 PIL로 자막 PNG를 그려
# overlay로 합성한다.
# 2026-07-30: 캐릭터 움직임을 Rhubarb 립싱크(입모양 3장 스위칭)에서 Kling AI
# image2video로 전환 — 입모양만 바뀌는 정지 이미지 스위칭은 "위치만 옮겨졌지 그림
# 자체는 그대로"라 밋밋하다는 피드백. 이제 Kling으로 뽑은 5초 자연스러운 움직임
# 영상(고개 갸웃 등) 하나를 대사 길이에 맞춰 반복 재생 — 대사 내용과 입모양이
# 정확히 맞을 필요는 없는 캐릭터 디자인(비인간 사물)이라 이 방식으로 충분하다.
# 캐릭터를 별도 알파 트랙으로 먼저 만드는 이유는 여전히 유효: 배경 합성은
# "인트로/코너" 딱 2구간으로만 나눠서 처리해야 전체-길이 overlay 체인 성능 문제를
# 피할 수 있다(2026-07-29 cat-fight 작업에서 확인).
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FPS = 30


def _parse_srt(srt_path: str) -> list[tuple[float, float, str]]:
    text = Path(srt_path).read_text()
    time_re = re.compile(r"(\d\d):(\d\d):(\d\d),(\d\d\d) --> (\d\d):(\d\d):(\d\d),(\d\d\d)")
    entries = []
    for block in text.strip().split("\n\n"):
        lines = block.strip().split("\n")
        if len(lines) < 3:
            continue
        m = time_re.match(lines[1])
        if not m:
            continue
        h1, m1, s1, ms1, h2, m2, s2, ms2 = map(int, m.groups())
        start = h1 * 3600 + m1 * 60 + s1 + ms1 / 1000
        end = h2 * 3600 + m2 * 60 + s2 + ms2 / 1000
        entries.append((start, end, " ".join(lines[2:])))
    return entries


def _make_ad_tag_png(out_path: Path, font_size=28, padding=12):
    """공정위 표시광고 지침 대응 — 실제 쿠팡/네이버 제휴 링크를 쓰기로 확정한
    영상에만 assemble(..., ad_tag=True)로 켠다. "처음부터 끝까지 노출" 요건 때문에
    약하게(반투명)라도 전체 구간에 계속 떠 있어야 하고, 후반부에만 넣는 건 안 됨
    (shopping-shorts-video에서 확인된 규칙과 동일)."""
    font = ImageFont.truetype(FONT_PATH, font_size)
    text = "광고"
    dummy = Image.new("RGBA", (1, 1))
    bbox = ImageDraw.Draw(dummy).textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    box_w, box_h = tw + padding * 2, th + padding * 2
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 100))
    draw = ImageDraw.Draw(img)
    draw.text((padding - bbox[0], padding - bbox[1]), text, font=font, fill=(255, 255, 255, 210))
    img.save(out_path)


def _make_title_png(text: str, out_path: Path, font_size=64) -> int:
    """영상 상단을 가로로 꽉 채우는 후킹 배너. WHY: 작은 알약 모양 라벨은 존재감이
    약해서 스크롤 중 3초컷으로 넘어가는 문제를 못 막는다(2026-07-30 피드백) —
    화면 가로 전체를 덮는 굵은 배너로 바꾸고, 텍스트도 카테고리 라벨이 아니라
    후킹 문구(공감/호기심 유발)를 넣는다. 반환값(배너 높이)은 다른 오버레이가
    이 배너와 겹치지 않게 배치할 때 쓴다."""
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    max_text_w = W - 140
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_text_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_h = font_size + 16
    pad_y = 30
    box_h = pad_y * 2 + line_h * len(lines)
    img = Image.new("RGBA", (W, box_h), (200, 74, 98, 240))
    draw = ImageDraw.Draw(img)
    y = pad_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2 - bbox[0], y - bbox[1]), line, font=font, fill=(255, 255, 255, 255))
        y += line_h
    img.save(out_path)
    return box_h


def _make_title_card_png(text: str, out_path: Path, font_size=88):
    """영상 맨 앞에 붙는 단색 배경 + 큰 제목 카드. WHY: 플랫폼이 썸네일을 영상
    첫 프레임으로 자동 지정하는 경우가 많아서, 이 카드 자체를 그대로 썸네일로
    쓸 수 있게 글자를 크고 굵게, 배경은 단색으로 단순하게 만든다."""
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
    img = Image.new("RGB", (W, H), (200, 74, 98))
    draw = ImageDraw.Draw(img)
    max_text_w = W - 160
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_text_w and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_h = font_size + 26
    total_h = line_h * len(lines)
    y = (H - total_h) / 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) / 2 - bbox[0], y - bbox[1]), line, font=font, fill=(255, 255, 255))
        y += line_h
    img.save(out_path)


def _make_caption_png(text: str, out_path: Path, font_size=60, max_width=940):
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
    dummy = Image.new("RGBA", (1, 1))
    d = ImageDraw.Draw(dummy)
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = d.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)

    line_heights, max_w = [], 0
    for line in lines:
        bbox = d.textbbox((0, 0), line, font=font)
        line_heights.append(bbox[3] - bbox[1])
        max_w = max(max_w, bbox[2] - bbox[0])

    pad_x, pad_y, gap = 30, 18, 8
    box_w, box_h = max_w + pad_x * 2, sum(line_heights) + gap * (len(lines) - 1) + pad_y * 2
    img = Image.new("RGBA", (box_w, box_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([0, 0, box_w, box_h], radius=16, fill=(0, 0, 0, 165))
    y = pad_y
    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (box_w - w) / 2 - bbox[0]
        draw.text((x, y - bbox[1]), line, font=font, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
        y += lh + gap
    img.save(out_path)


def _build_character_loop(motion_path: str, total_duration: float, out_path: Path, bg_color: str = "0xFFFFFF"):
    """Kling 모션 클립(단색 배경)에서 배경을 알파로 빼고, 대사 길이만큼 반복시킨
    알파 채널 영상(qtrle mov)을 만든다. 대사 타이밍과 동기화하지 않고 그냥 반복.

    WHY 정방향+역방향(ping-pong) 이어붙이기: Kling이 생성한 클립은 시작 포즈와
    끝 포즈가 같다는 보장이 없어서, 그냥 -stream_loop로 반복하면 루프 지점마다
    포즈가 툭 끊기는 느낌이 난다(2026-07-30 확인). 정방향 재생 뒤 바로 역방향
    재생을 이어붙이면 마지막 프레임이 항상 첫 프레임으로 대칭 복귀하므로,
    프롬프트가 끝-시작을 맞춰주길 기대하지 않아도 구조적으로 끊김이 없다.

    WHY bg_color 파라미터화 + 초록 배경 권장(2026-07-30): 흰 배경은 캐릭터 얼굴의
    밝은 하이라이트(이마·볼)까지 "흰색에 가깝다"고 오인해서 threshold를 아주 좁게
    잡아야만 했다(0.03) — 그래도 여전히 위험한 여지가 있다. gemini_illust.py의
    STYLE_PROMPT를 초록 배경(#00FF00)으로 바꿔뒀으니, 그 프롬프트로 새로 만든
    캐릭터는 bg_color="0x00FF00"로 넉넉한 threshold(0.15 정도)를 써도 안전하다.
    기존 흰 배경 캐릭터(예: 돼지감자)는 기본값 그대로 좁은 threshold 유지."""
    similarity = "0.03" if bg_color.upper() == "0xFFFFFF" else "0.15"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        keyed = tmp_path / "keyed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", motion_path,
             "-vf", f"colorkey={bg_color}:{similarity}:{similarity},format=yuva420p",
             "-c:v", "qtrle", str(keyed)],
            check=True, capture_output=True,
        )
        reversed_ = tmp_path / "reversed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(keyed), "-vf", "reverse", "-c:v", "qtrle", str(reversed_)],
            check=True, capture_output=True,
        )
        pingpong = tmp_path / "pingpong.mov"
        list_path = tmp_path / "pp_list.txt"
        list_path.write_text(f"file '{keyed.resolve()}'\nfile '{reversed_.resolve()}'")
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(pingpong)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(pingpong),
             "-t", f"{total_duration}", "-c:v", "qtrle", str(out_path)],
            check=True, capture_output=True,
        )


def _build_background(images: list[str], total_duration: float, out_path: Path, xfade_dur: float = 0.7):
    """실사진 슬라이드쇼 배경. WHY 크로스페이드: 이전엔 concat demuxer로 하드컷만
    이어붙여서 사진이 바뀔 때마다 뚝뚝 끊기는 느낌이었다(2026-07-30 피드백: "좀더
    끊김없이 계속 움직일 수 있도록") — xfade로 디졸브 전환을 넣어 계속 움직이는
    느낌을 유지한다. 이미지가 4장 정도로 적어서 xfade 체인이 성능 문제는 없음
    (수백 개 세그먼트를 잇는 것과는 다른 케이스 — cat-fight 교훈은 여기 해당 안 됨)."""
    n = len(images)
    seg_dur = (total_duration + (n - 1) * xfade_dur) / n if n > 1 else total_duration
    frames = max(int(seg_dur * FPS), 1)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seg_paths = []
        for i, img in enumerate(images):
            seg = tmp_path / f"bg_{i:03d}.mp4"
            vf = (
                f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
                f"zoompan=z='min(zoom+0.0010,1.10)':d={frames}:s={W}x{H}:fps={FPS}"
            )
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-i", img, "-t", f"{seg_dur}",
                 "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)],
                check=True, capture_output=True,
            )
            seg_paths.append(seg)

        if n == 1:
            subprocess.run(["ffmpeg", "-y", "-i", str(seg_paths[0]), "-c", "copy", str(out_path)],
                            check=True, capture_output=True)
            return

        inputs = []
        for p in seg_paths:
            inputs += ["-i", str(p)]
        filters, prev = [], "0:v"
        for i in range(1, n):
            offset = i * (seg_dur - xfade_dur)
            out_label = f"vx{i}" if i < n - 1 else "vout"
            filters.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={xfade_dur}:offset={offset}[{out_label}]")
            prev = out_label
        subprocess.run(
            ["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(filters),
             "-map", "[vout]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
            check=True, capture_output=True,
        )


def assemble(
    images: list[str],
    motion_path: str,
    audio_path: str,
    srt_path: str,
    out_path: str,
    title: str,
    intro_duration: float = 5.3,
    ad_tag: bool = False,
    bg_color: str = "0xFFFFFF",
    title_card_duration: float = 1.3,
):
    duration_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    total_duration = float(duration_probe.stdout.strip())

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        char_track = tmp_path / "char.mov"
        _build_character_loop(motion_path, total_duration, char_track, bg_color=bg_color)

        bg = tmp_path / "bg.mp4"
        _build_background(images, total_duration, bg)

        # 1) 인트로 구간: 캐릭터 크게, 중앙
        intro_out = tmp_path / "intro.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-t", f"{intro_duration}", "-i", str(bg),
             "-t", f"{intro_duration}", "-i", str(char_track),
             "-filter_complex",
             f"[1:v]scale=760:-1[char];[0:v][char]overlay=x=(main_w-overlay_w)/2:y=(main_h-overlay_h)/2-80[v]",
             "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(intro_out)],
            check=True, capture_output=True,
        )

        # 2) 이후 구간: 캐릭터 작게, 우측 하단
        main_dur = total_duration - intro_duration
        main_out = tmp_path / "main.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", f"{intro_duration}", "-t", f"{main_dur}", "-i", str(bg),
             "-ss", f"{intro_duration}", "-t", f"{main_dur}", "-i", str(char_track),
             "-filter_complex",
             f"[1:v]scale=280:-1[char];[0:v][char]overlay=x=main_w-overlay_w-30:y=main_h-overlay_h-320[v]",
             "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(main_out)],
            check=True, capture_output=True,
        )

        # 0) 맨 앞 제목 카드 — 단색 배경 + 큼직한 글자, 플랫폼이 영상 첫 프레임을
        # 썸네일로 자동 지정하는 경우가 많아서 이 카드 자체가 썸네일 역할도 한다.
        title_card_png = tmp_path / "title_card.png"
        _make_title_card_png(title, title_card_png)
        title_card_out = tmp_path / "title_card.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-t", f"{title_card_duration}", "-i", str(title_card_png),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(title_card_out)],
            check=True, capture_output=True,
        )

        combined = tmp_path / "combined.mp4"
        list_path = tmp_path / "scenes.txt"
        list_path.write_text(
            f"file '{title_card_out.resolve()}'\nfile '{intro_out.resolve()}'\nfile '{main_out.resolve()}'"
        )
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(combined)],
            check=True, capture_output=True,
        )

        # WHY video_total: 맨 앞에 제목 카드(title_card_duration)가 붙어서 영상 전체
        # 길이가 나레이션 길이(total_duration)보다 길어졌다 — 이후 배너/자막 단계는
        # 전부 이 늘어난 길이 기준으로 처리해야 한다.
        video_total = title_card_duration + total_duration

        # 3) 상단 후킹 배너(+ 필요시 광고 태그) — 전체 길이에 한 번만 overlay
        # (세그먼트 아님, 성능 안전). WHY -t를 이미지 입력과 출력 양쪽에 명시:
        # -loop 1 이미지 + -shortest 조합만으로는 종료를 못 잡고 무한정 도는
        # 경우가 있었다(2026-07-30, 15분 넘게 안 끝나고 파일이 계속 커지는 걸
        # 확인 후 kill) — 길이를 직접 못박아서 확실히 끝나게 한다.
        title_png = tmp_path / "title.png"
        title_h = _make_title_png(title, title_png)
        titled = tmp_path / "titled.mp4"

        if ad_tag:
            ad_png = tmp_path / "ad_tag.png"
            _make_ad_tag_png(ad_png)
            subprocess.run(
                ["ffmpeg", "-y",
                 "-i", str(combined),
                 "-loop", "1", "-t", f"{video_total}", "-i", str(title_png),
                 "-loop", "1", "-t", f"{video_total}", "-i", str(ad_png),
                 "-filter_complex",
                 f"[0:v][1:v]overlay=x=0:y=0[t];[t][2:v]overlay=x=main_w-overlay_w-20:y={title_h + 16}[v]",
                 "-map", "[v]", "-t", f"{video_total}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(titled)],
                check=True, capture_output=True,
            )
        else:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(combined), "-loop", "1", "-t", f"{video_total}", "-i", str(title_png),
                 "-filter_complex", "[0:v][1:v]overlay=x=0:y=0[v]",
                 "-map", "[v]", "-t", f"{video_total}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(titled)],
                check=True, capture_output=True,
            )
        combined = titled

        # 4) 자막 굽기 (문장 구간별로 짧게 잘라 처리 — 안전한 세그먼트 방식)
        # WHY offset: 자막 타이밍은 오디오(나레이션) 기준 0초부터라, 제목 카드만큼
        # (title_card_duration) 밀어서 실제 영상 타임라인에 맞춰야 한다.
        offset = title_card_duration
        srt_entries = _parse_srt(srt_path)
        cap_dir = tmp_path / "caps"
        cap_dir.mkdir()
        timeline, cursor = [(0.0, offset, None)], 0.0
        for start, end, text in srt_entries:
            if start > cursor + 0.05:
                timeline.append((cursor + offset, start + offset, None))
            timeline.append((start + offset, end + offset, text))
            cursor = end
        if cursor < total_duration - 0.05:
            timeline.append((cursor + offset, total_duration + offset, None))

        seg_paths = []
        for i, (start, end, text) in enumerate(timeline):
            dur = end - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"cap_{i:04d}.mp4"
            if text:
                cap_png = cap_dir / f"cap_{i:04d}.png"
                _make_caption_png(text, cap_png)
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", f"{start}", "-t", f"{dur}", "-i", str(combined),
                     "-loop", "1", "-t", f"{dur}", "-i", str(cap_png),
                     "-filter_complex", "[0:v][1:v]overlay=x=(main_w-overlay_w)/2:y=main_h-overlay_h-620[v]",
                     "-map", "[v]", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)],
                    check=True, capture_output=True,
                )
            else:
                subprocess.run(
                    ["ffmpeg", "-y", "-ss", f"{start}", "-t", f"{dur}", "-i", str(combined),
                     "-c:v", "libx264", "-pix_fmt", "yuv420p", str(seg)],
                    check=True, capture_output=True,
                )
            seg_paths.append(seg)

        cap_list = tmp_path / "cap_list.txt"
        cap_list.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths))
        captioned = tmp_path / "captioned.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(cap_list),
             "-c", "copy", str(captioned)],
            check=True, capture_output=True,
        )

        # WHY adelay 대신 -shortest 안 씀: 제목 카드 구간은 무음이어야 하므로 오디오를
        # title_card_duration만큼 뒤로 민다 — 그러면 오디오 길이가 정확히 영상 길이와
        # 같아져서 -shortest로 잘라낼 필요가 없다(제목 카드가 잘려나가는 사고 방지).
        offset_ms = int(title_card_duration * 1000)
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(captioned), "-i", audio_path,
             "-filter_complex", f"[1:a]adelay={offset_ms}|{offset_ms}[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
             out_path],
            check=True, capture_output=True,
        )
    print(f"영상 조립 완료: {out_path}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--images", required=True, help="쉼표로 구분된 배경용 실사진 경로들")
    p.add_argument("--motion", required=True, help="Kling으로 생성한 캐릭터 모션 루프 클립(흰 배경)")
    p.add_argument("--audio", required=True)
    p.add_argument("--srt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", required=True, help="영상 상단에 계속 표시할 주제 라벨")
    p.add_argument("--intro-duration", type=float, default=5.3)
    p.add_argument("--ad-tag", action="store_true", help="실제 제휴 링크를 쓰기로 확정한 경우에만 켠다")
    p.add_argument("--bg-color", default="0xFFFFFF",
                    help="캐릭터 모션 클립의 배경색(colorkey 대상) — 새 캐릭터는 0x00FF00 권장")
    p.add_argument("--title-card-duration", type=float, default=1.3,
                    help="영상 맨 앞 단색 제목 카드(썸네일용) 길이(초)")
    args = p.parse_args()

    assemble(
        images=args.images.split(","),
        motion_path=args.motion,
        audio_path=args.audio,
        srt_path=args.srt,
        out_path=args.out,
        title=args.title,
        intro_duration=args.intro_duration,
        ad_tag=args.ad_tag,
        bg_color=args.bg_color,
        title_card_duration=args.title_card_duration,
    )
