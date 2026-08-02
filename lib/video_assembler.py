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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_PATH = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
FPS = 30

# WHY 기본 엔딩 CTA(2026-08-02, "카드뉴스랑 숏폼 영상 마지막에 구독, 좋아요, 팔로우
# 요청하는 글도 추가하자"): 매번 topic마다 문구를 새로 넘길 필요 없이 항상 같은
# 표준 문구로 나가게 모듈 상수로 고정 — end_card_text를 명시로 넘기면 그걸 쓰고,
# 안 넘기면(기본) 이 문구를 쓴다. 완전히 끄고 싶으면 end_card_duration=0.
DEFAULT_END_CARD_TEXT = "더 많은 건강정보가 궁금하다면 구독·좋아요·팔로우 해주세요"

# WHY 칠판 스타일 기본 배경 전환(2026-08-02): 실사진을 그대로 배경에 깔면 밋밋하고
# 눈에 확 안 들어온다는 피드백("real 이미지 그대로 배경으로 넣고 있는데... 확 보이지가
# 않는다") — 카드뉴스처럼 칠판 같은 배경에 감각적인 폰트로 나레이션을 써주는 쪽으로
# 새 topic 기본값을 바꾼다. 폰트는 무료 상업적 이용 가능한 구글 폰트 "Gaegu"(SIL OFL
# 1.1, assets_library/fonts/OFL-Gaegu.txt 참고) — 손글씨/마카체 느낌의 한글 지원 폰트.
CHALK_FONT_PATH = str(Path(__file__).resolve().parent.parent / "assets_library" / "fonts" / "Gaegu-Bold.ttf")
CHALKBOARD_TOP = (32, 66, 48)
CHALKBOARD_BOTTOM = (20, 42, 31)


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


def _make_title_card_png(text: str, out_path: Path, font_size=88, char_path: str | None = None):
    """영상 맨 앞에 붙는 단색 배경 + 큰 제목 카드. WHY: 플랫폼이 썸네일을 영상
    첫 프레임으로 자동 지정하는 경우가 많아서, 이 카드 자체를 그대로 썸네일로
    쓸 수 있게 글자를 크고 굵게, 배경은 단색으로 단순하게 만든다.

    WHY char_path(2026-07-31, "캐릭터를 큼직하고 흐리게 글자의 배경으로"): 순수
    단색 배경 대신, 캐릭터 이미지를 캔버스보다 훨씬 크게 확대·크롭해서 흐리게 깐
    뒤 ACCENT 톤 스크림을 얹는다 — 브랜드 컬러는 유지하면서 캐릭터가 은은하게
    느껴지는 배경 무드를 만든다."""
    img = Image.new("RGB", (W, H), (200, 74, 98))
    if char_path:
        target = int(H * 1.15)
        char = Image.open(char_path).convert("RGB").resize((target, target))
        char = char.filter(ImageFilter.GaussianBlur(25))
        left, top = (target - W) // 2, (target - H) // 2
        char = char.crop((left, top, left + W, top + H))
        scrim = Image.new("RGBA", (W, H), (200, 74, 98, 150))
        img = Image.alpha_composite(char.convert("RGBA"), scrim).convert("RGB")
    font = ImageFont.truetype(FONT_PATH, font_size, index=6)
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


def _make_chalk_caption_png(text: str, out_path: Path, font_size=68, max_width=940):
    """칠판 배경용 자막(2026-08-02). _make_caption_png와 달리 반투명 박스가 없다 —
    배경 자체가 이미 짙은 칠판색이라 박스를 얹으면 이중으로 어두워지고 사진 위에
    붙인 스티커 같은 느낌만 준다. 대신 Gaegu(분필/마카 느낌 폰트)로 흰 글자를
    직접 쓰고, 옅은 그림자만 살짝 깔아서 배경 톤이 조금 밝은 부분에서도 읽히게 한다."""
    font = ImageFont.truetype(CHALK_FONT_PATH, font_size)
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

    pad, gap = 20, 14
    img_w, img_h = max_w + pad * 2, sum(line_heights) + gap * (len(lines) - 1) + pad * 2
    img = Image.new("RGBA", (img_w, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    y = pad
    for line, lh in zip(lines, line_heights):
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = (img_w - w) / 2 - bbox[0]
        draw.text((x + 3, y - bbox[1] + 3), line, font=font, fill=(0, 0, 0, 110))  # 옅은 그림자
        draw.text((x, y - bbox[1]), line, font=font, fill=(255, 255, 255, 255))
        y += lh + gap
    img.save(out_path)


def _build_character_segment(motion_path: str, duration: float, out_path: Path, bg_color: str = "0xFFFFFF"):
    """_build_character_loop의 단일 세그먼트 버전 — 캐릭터 여러 명이 구간별로
    번갈아 나오는 _build_character_schedule에서 재사용한다."""
    similarity = "0.03" if bg_color.upper() == "0XFFFFFF" else "0.15"
    despill = ""
    if bg_color.upper() == "0X00FF00":
        despill = "despill=type=green:mix=1.0:expand=0,"
    elif bg_color.upper() == "0X0000FF":
        despill = "despill=type=blue:mix=1.0:expand=0,"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        keyed = tmp_path / "keyed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", motion_path,
             "-vf", f"colorkey={bg_color}:{similarity}:{similarity},{despill}format=argb,"
                    "lut=a='if(gt(val\\,16)\\,255\\,0)'",
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
             "-t", f"{duration}", "-c:v", "qtrle", str(out_path)],
            check=True, capture_output=True,
        )


def _build_character_schedule(
    schedule: list[tuple[float, float, str]] | list[tuple[float, float, str, str]],
    total_duration: float, out_path: Path, bg_color: str = "0xFFFFFF",
):
    """캐릭터 여러 명이 구간별로 번갈아 나오는 캐릭터 트랙. WHY(2026-07-31, 수면음식_1
    — 대추/체리/호두 세 캐릭터가 각자 자기 대사 구간에만 나와야 하는데
    _build_character_loop은 캐릭터 1개를 전체 길이에 반복하는 구조라 못 씀):
    schedule의 각 구간마다 _build_character_segment로 개별 캐릭터 트랙을 만들고
    concat으로 이어붙인다. 각 세그먼트는 독립적으로 ping-pong 처리되므로 세그먼트
    경계에서도 포즈가 끊기지 않는다.

    WHY 세그먼트별 bg_color(2026-08-01, 갑상선방해음식_1/위장더부룩음식_1에서 실제
    발생 — 초록 계열 캐릭터라 파란 배경으로 생성한 일러스트(케일·페퍼민트차 등)가
    섞인 topic에서 전체에 초록 colorkey를 쓰면 파란 배경이 그대로 남는 사고): 튜플이
    (start, end, path) 3개면 전역 bg_color를, (start, end, path, bg_color) 4개면
    그 세그먼트 전용 색을 쓴다 — 캐릭터마다 크로마키 색이 다른 topic(초록/파랑 섞임)을
    지원하기 위함."""
    schedule = sorted(schedule, key=lambda x: x[0])
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seg_paths = []
        for i, entry in enumerate(schedule):
            start, end, motion_path = entry[0], entry[1], entry[2]
            seg_bg_color = entry[3] if len(entry) > 3 else bg_color
            dur = min(end, total_duration) - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"char_seg_{i:03d}.mov"
            _build_character_segment(motion_path, dur, seg, bg_color=seg_bg_color)
            seg_paths.append(seg)
        list_path = tmp_path / "char_list.txt"
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(out_path)],
            check=True, capture_output=True,
        )


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
    기존 흰 배경 캐릭터(예: 돼지감자)는 기본값 그대로 좁은 threshold 유지.

    WHY alpha 이분법 처리(2026-07-30): colorkey가 threshold 안쪽 픽셀도 완전
    불투명이 아니라 부분투명(반쯤 섞인 alpha)으로 만드는 경우가 있는데, 이게
    280px로 축소되는 코너 장면에서 배경(초록 잎)이 캐릭터 얼굴에 얼룩덜룩
    비쳐 보이는 원인이었다(세션 내내 "눈 왜곡"으로 오인했던 문제의 진짜 정체 —
    Kling 생성 결과가 아니라 이 로컬 합성 단계의 버그였음). lut=a로 alpha를
    16 기준 완전 불투명(255) 아니면 완전 투명(0)으로 강제해서 부분투명을 없앤다.

    WHY despill(2026-07-31): alpha 이분법 처리는 "안/밖"만 정하지, 안쪽으로 판정된
    가장자리 픽셀 자체의 색(그린 스크린 촬영/렌더링에서 늘 발생하는 초록 스필)은
    그대로 남는다 — 그 결과 캐릭터 테두리에 초록 형광 라인이 둘러진 것처럼 보였다
    (0x00FF00 배경으로 처음 실사용한 v8 클립에서 확인). despill로 가장자리의 잔여
    초록기를 억제한다. despill 필터는 초록/파랑만 지원해서 그 두 색일 때만 적용.

    WHY format=argb (yuva420p 아님, 2026-07-31): qtrle 인코더는 rgb24/rgb555be/argb/
    gray만 지원한다(yuva420p 미지원) — yuva420p로 지정해도 qtrle 인코딩 시 결국 argb로
    재변환되므로, 처음부터 qtrle가 실제로 쓰는 argb를 직접 지정해 불필요한 왕복 변환을
    없앤다.

    ⚠️ WHY .upper() 비교를 대문자 리터럴과 하는지: `bg_color.upper()`는 "0x00FF00"의
    "x"까지 "X"로 바꿔버려서 "0x00FF00"(소문자 x) 리터럴과 절대 같아질 수 없다 —
    이 버그 때문에 despill 분기가 조용히 한 번도 실행된 적이 없었다(2026-07-31,
    초록 배경 v8 클립에서 형광 초록 테두리가 안 없어지던 진짜 원인 — despill을
    mix=1.0까지 올려도 전혀 효과가 없었던 이유). 비교 대상 리터럴도 항상 .upper()로
    맞춰서 이 클래스의 버그가 재발하지 않게 한다."""
    similarity = "0.03" if bg_color.upper() == "0XFFFFFF" else "0.15"
    despill = ""
    if bg_color.upper() == "0X00FF00":
        despill = "despill=type=green:mix=1.0:expand=0,"
    elif bg_color.upper() == "0X0000FF":
        despill = "despill=type=blue:mix=1.0:expand=0,"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        keyed = tmp_path / "keyed.mov"
        subprocess.run(
            ["ffmpeg", "-y", "-i", motion_path,
             "-vf", f"colorkey={bg_color}:{similarity}:{similarity},{despill}format=argb,"
                    "lut=a='if(gt(val\\,16)\\,255\\,0)'",
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


def make_gradient_bg(out_path: Path, top=(253, 249, 245), bottom=(246, 237, 230)):
    """실사진이 없는 topic용 배경. WHY(2026-07-31, 수면음식_1): 캐릭터 일러스트(크로마키
    배경 포함)를 실수로 --images 자리에 넣으면 초록 배경이 그대로 노출되는 사고가 났다
    — 실사진이 없을 땐 카드뉴스와 같은 톤의 단색 그라디언트를 배경으로 쓴다."""
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        color = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        draw.line([(0, y), (W, y)], fill=color)
    img.save(out_path, quality=95)


CHALKBOARD_PHOTO_PATH = str(Path(__file__).resolve().parent.parent / "assets_library" / "backgrounds" / "칠판.png")
# WHY 실측 좌표를 상수로 고정(2026-08-02): 실물 칠판 사진(assets_library/backgrounds/
# 칠판.png, 1024x1024)의 좌우 흰 여백을 나무 프레임 가장자리까지 잘라내기 위해
# 픽셀을 직접 스캔해서 찾은 값 — "나무 프레임이 가로 폭에 딱맞게" 요청 반영.
# 이 배경 이미지 자체를 바꾸지 않는 한 다시 측정할 필요 없음.
CHALKBOARD_CROP_LEFT = 65
CHALKBOARD_CROP_RIGHT = 962
# WHY 위/아래 여백은 안 자르는지: 사진 원본의 흰 위쪽 여백엔 제목 배너가,
# 아래쪽 여백엔 캐릭터가 들어갈 자리라 그대로 살려둔다(사용자 요청) — 다만 세로로
# 늘려서 캔버스(1920)를 다 채우면 위아래 여백이 부족해서, 늘리는 대신 같은 톤의
# 흰색으로 캔버스 크기까지 패딩한다.
CHALKBOARD_BG_FILL = (248, 248, 248)
CHALKBOARD_TOP_PAD = 220


def _build_chalkboard_bg(total_duration: float, out_path: Path):
    """칠판 스타일 기본 배경(2026-08-02, 실물 칠판 사진으로 교체). 좌우 흰 여백을
    나무 프레임 가장자리까지 잘라서 프레임이 가로 폭에 꽉 차게 만들고, 위아래는
    원본 비율 그대로 살린 뒤 부족한 높이만큼 같은 톤의 흰색으로 패딩해서 캔버스를
    채운다 — 위쪽 흰 여백엔 제목 배너, 아래쪽 흰 여백엔 캐릭터가 들어간다. 완전히
    정적이면 밋밋해서 실사진 배경과 같은 미세 zoompan(서서히 확대)만 적용한다."""
    with tempfile.TemporaryDirectory() as tmp:
        photo = Image.open(CHALKBOARD_PHOTO_PATH).convert("RGB")
        cropped = photo.crop((CHALKBOARD_CROP_LEFT, 0, CHALKBOARD_CROP_RIGHT, photo.height))
        scale = W / cropped.width
        resized = cropped.resize((W, round(cropped.height * scale)))

        canvas = Image.new("RGB", (W, H), CHALKBOARD_BG_FILL)
        top_pad = min(CHALKBOARD_TOP_PAD, max(H - resized.height, 0))
        canvas.paste(resized, (0, top_pad))

        still = Path(tmp) / "chalkboard.jpg"
        canvas.save(still, quality=95)

        frames = max(int(total_duration * FPS), 1)
        vf = f"zoompan=z='min(zoom+0.0006,1.06)':d={frames}:s={W}x{H}:fps={FPS}"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", str(still), "-t", f"{total_duration}",
             "-vf", vf, "-c:v", "libx264", "-pix_fmt", "yuv420p", str(out_path)],
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


def _build_background_schedule(
    schedule: list[tuple[float, float, list[str]]], total_duration: float, out_path: Path,
):
    """배경 사진도 캐릭터처럼 구간별로 맞춰야 하는 경우(품목별 실사진이 있는 topic).
    WHY(2026-07-31, 당뇨유발음식_1 — 단팥빵 나레이션 구간에 찹쌀떡 사진이 나오는 문제
    발견): 기존 _build_background는 이미지 개수만큼 전체 길이를 균등 분할해서
    나레이션 타이밍과 무관하게 순서대로 보여줬다 — _build_character_schedule과
    동일한 패턴으로, 구간마다 그 구간에 맞는 사진(들)만 골라 별도로 배경을 만들고
    이어붙인다. 각 구간 안에 사진이 여러 장이면 그 구간 안에서만 크로스페이드된다."""
    schedule = sorted(schedule, key=lambda x: x[0])
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        seg_paths = []
        for i, (start, end, imgs) in enumerate(schedule):
            dur = min(end, total_duration) - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"bg_seg_{i:03d}.mp4"
            _build_background(imgs, dur, seg)
            seg_paths.append(seg)
        list_path = tmp_path / "bg_list.txt"
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in seg_paths))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(out_path)],
            check=True, capture_output=True,
        )


def assemble(
    images: list[str] | None,
    motion_path: str | None,
    audio_path: str,
    srt_path: str,
    out_path: str,
    title: str,
    # WHY 기본값 0(2026-07-31): "5초 뒤에 옮기지 말고 처음부터 우하단에" 피드백 이후
    # 이게 표준이 됐다 — 풀스크린 인트로가 필요한 특수한 경우에만 명시적으로 넘길 것.
    intro_duration: float = 0,
    ad_tag: bool = False,
    bg_color: str = "0xFFFFFF",
    title_card_duration: float = 1.3,
    title_card_text: str | None = None,
    title_card_char_path: str | None = None,
    # WHY motion_schedule(2026-07-31, 수면음식_1 — 대추/체리/호두 세 캐릭터가 각자
    # 대사 구간에만 나와야 함): [(start, end, motion_path), ...] 형태로 주면
    # motion_path 대신 이 스케줄로 캐릭터 트랙을 만든다. 시간은 나레이션(오디오) 기준
    # 0초부터 — assemble 내부에서 제목 카드만큼 알아서 밀어준다. motion_path와
    # motion_schedule 둘 다 없으면 에러, 둘 다 있으면 motion_schedule 우선.
    motion_schedule: list[tuple[float, float, str]] | None = None,
    # WHY image_schedule(2026-07-31, 당뇨유발음식_1 — 단팥빵 나레이션 구간에 찹쌀떡
    # 사진이 나오는 문제 발견): motion_schedule과 동일한 패턴. [(start, end,
    # [이미지경로,...]), ...]로 주면 images 대신 이 스케줄로 배경을 만든다 — 품목별
    # 실사진이 있는 topic(여러 캐릭터가 번갈아 나오는 topic)은 배경도 같이 맞출 것.
    image_schedule: list[tuple[float, float, list[str]]] | None = None,
    # WHY bg_style 기본값 "chalkboard"(2026-08-02): 실사진 배경이 밋밋하고 눈에 안
    # 띈다는 피드백으로 새 topic 기본값을 카드뉴스 톤 칠판 배경+분필체 자막으로
    # 바꿨다. "photo"를 명시하면 기존 실사진 슬라이드쇼 방식(images/image_schedule
    # 필요)을 그대로 쓸 수 있다 — 과거 topic 재조립이나 특별히 실사진이 필요한
    # 경우를 위해 남겨둠.
    bg_style: str = "chalkboard",
    # WHY 기본 켜짐(2026-08-02, "숏폼 영상 마지막에 구독, 좋아요, 팔로우 요청하는
    # 글도 추가하자"): 제목 카드와 대칭으로 영상 맨 끝에 CTA 카드를 붙인다 —
    # end_card_duration=0으로 주면 완전히 끌 수 있다(기존 영상 재조립 시 굳이
    # 필요 없는 경우 등).
    end_card_duration: float = 2.0,
    end_card_text: str | None = None,
    end_card_char_path: str | None = None,
):
    if not motion_path and not motion_schedule:
        raise ValueError("motion_path 또는 motion_schedule 중 하나는 필요합니다")
    if bg_style not in ("chalkboard", "photo"):
        raise ValueError(f"알 수 없는 bg_style: {bg_style!r} (chalkboard 또는 photo만 가능)")
    if bg_style == "photo" and not images and not image_schedule:
        raise ValueError("bg_style='photo'면 images 또는 image_schedule 중 하나는 필요합니다")
    duration_probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True, check=True,
    )
    total_duration = float(duration_probe.stdout.strip())

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        char_track = tmp_path / "char.mov"
        if motion_schedule:
            _build_character_schedule(motion_schedule, total_duration, char_track, bg_color=bg_color)
        else:
            _build_character_loop(motion_path, total_duration, char_track, bg_color=bg_color)

        bg = tmp_path / "bg.mp4"
        if bg_style == "chalkboard":
            _build_chalkboard_bg(total_duration, bg)
        elif image_schedule:
            _build_background_schedule(image_schedule, total_duration, bg)
        else:
            _build_background(images, total_duration, bg)

        # 1) 인트로 구간: 캐릭터 크게, 중앙. WHY intro_duration<=0이면 통째로 스킵
        # (2026-07-31, "5초 뒤에 우하단으로 옮기지 말고 처음부터 우하단에 있게"):
        # 인트로 자체를 안 만들고 처음부터 코너(작게) 구간으로 시작한다.
        intro_out = None
        if intro_duration > 0:
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
        # WHY -r FPS(2026-07-31 버그 수정): 이 명령에 프레임레이트를 안 주면 ffmpeg가
        # image2 loop 입력에 기본 25fps를 붙이는데, main_out(bg/char 체인)은 30fps라
        # 뒤에서 -c copy로 concat할 때 두 세그먼트의 프레임레이트가 달라 타임스탬프가
        # 어긋난다. 겉보기엔 영상 길이가 실제보다 늘어나 보이고(30/25=1.2배), 캐릭터가
        # 여러 명 번갈아 나오는 영상에서는 캐릭터 전환 타이밍이 한 구간씩 밀려 보이는
        # 형태로 드러났다(수면음식_1에서 실제로 발견) — 캐릭터 1명짜리 영상에서도
        # 전체적인 자막/오디오 싱크가 미세하게 어긋나는 형태로 존재했을 가능성이 있다.
        title_card_png = tmp_path / "title_card.png"
        _make_title_card_png(title_card_text or title, title_card_png, char_path=title_card_char_path)
        title_card_out = tmp_path / "title_card.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-t", f"{title_card_duration}", "-r", str(FPS), "-i", str(title_card_png),
             "-c:v", "libx264", "-pix_fmt", "yuv420p", str(title_card_out)],
            check=True, capture_output=True,
        )

        # 0-2) 맨 끝 엔딩 카드 — 제목 카드와 같은 스타일(단색+큰 글자)로 구독/좋아요/
        # 팔로우 CTA. end_card_duration=0이면 통째로 스킵(기존 인트로 스킵 패턴과 동일).
        end_card_out = None
        if end_card_duration > 0:
            end_card_png = tmp_path / "end_card.png"
            _make_title_card_png(end_card_text or DEFAULT_END_CARD_TEXT, end_card_png,
                                  char_path=end_card_char_path or title_card_char_path)
            end_card_out = tmp_path / "end_card.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-loop", "1", "-t", f"{end_card_duration}", "-r", str(FPS), "-i", str(end_card_png),
                 "-c:v", "libx264", "-pix_fmt", "yuv420p", str(end_card_out)],
                check=True, capture_output=True,
            )

        combined = tmp_path / "combined.mp4"
        list_path = tmp_path / "scenes.txt"
        scene_files = ([title_card_out] + ([intro_out] if intro_out else []) + [main_out]
                       + ([end_card_out] if end_card_out else []))
        list_path.write_text("\n".join(f"file '{p.resolve()}'" for p in scene_files))
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_path),
             "-c", "copy", str(combined)],
            check=True, capture_output=True,
        )

        # WHY video_total: 맨 앞 제목 카드 + 맨 끝 엔딩 카드가 붙어서 영상 전체
        # 길이가 나레이션 길이(total_duration)보다 길어졌다 — 이후 배너/자막 단계는
        # 전부 이 늘어난 길이 기준으로 처리해야 한다.
        video_total = title_card_duration + total_duration + end_card_duration

        # 3) 상단 후킹 배너(+ 필요시 광고 태그) — 전체 길이에 한 번만 overlay
        # (세그먼트 아님, 성능 안전). WHY -t를 이미지 입력과 출력 양쪽에 명시:
        # -loop 1 이미지 + -shortest 조합만으로는 종료를 못 잡고 무한정 도는
        # 경우가 있었다(2026-07-30, 15분 넘게 안 끝나고 파일이 계속 커지는 걸
        # 확인 후 kill) — 길이를 직접 못박아서 확실히 끝나게 한다.
        title_png = tmp_path / "title.png"
        title_h = _make_title_png(title, title_png)
        titled = tmp_path / "titled.mp4"

        # WHY enable='between(...)': 제목 카드 구간엔 이미 큼직한 훅 카피가 화면
        # 중앙에 떠 있어서 상단 배너까지 같이 뜨면 겹쳐 보인다(2026-07-31 지적) —
        # 배너는 제목 카드가 끝난 뒤부터 나온다. WHY 상한도 뒀는지(2026-08-02, 엔딩
        # 카드 추가): 엔딩 카드도 마찬가지로 CTA 문구가 중앙에 크게 뜨는데, 예전처럼
        # gte로 열어두면 배너가 엔딩 카드 구간까지 계속 떠서 겹친다 — 나레이션
        # 구간(title_card_duration ~ title_card_duration+total_duration)에서만 뜨게
        # 상한을 추가했다.
        enable_expr = f"between(t\\,{title_card_duration}\\,{title_card_duration + total_duration})"
        if ad_tag:
            ad_png = tmp_path / "ad_tag.png"
            _make_ad_tag_png(ad_png)
            subprocess.run(
                ["ffmpeg", "-y",
                 "-i", str(combined),
                 "-loop", "1", "-t", f"{video_total}", "-i", str(title_png),
                 "-loop", "1", "-t", f"{video_total}", "-i", str(ad_png),
                 "-filter_complex",
                 f"[0:v][1:v]overlay=x=0:y=0:enable='{enable_expr}'[t];"
                 f"[t][2:v]overlay=x=main_w-overlay_w-20:y={title_h + 16}:enable='{enable_expr}'[v]",
                 "-map", "[v]", "-t", f"{video_total}", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(titled)],
                check=True, capture_output=True,
            )
        else:
            subprocess.run(
                ["ffmpeg", "-y", "-i", str(combined), "-loop", "1", "-t", f"{video_total}", "-i", str(title_png),
                 "-filter_complex", f"[0:v][1:v]overlay=x=0:y=0:enable='{enable_expr}'[v]",
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
        # WHY 엔딩 카드 구간도 세그먼트로 명시(2026-08-02): 위 세그먼트들은 전부
        # total_duration+offset(=title_card_duration+total_duration)까지만 커버한다 —
        # 엔딩 카드를 붙이면서 video_total이 그보다 길어졌는데(end_card_duration만큼)
        # 여기서 세그먼트를 안 만들면 밑에서 concat한 captioned 영상이 combined보다
        # 짧아져서 엔딩 카드 부분이 통째로 잘려나간다. 자막 없는 구간으로 명시해서
        # video_total까지 확실히 채운다.
        if end_card_duration > 0:
            timeline.append((total_duration + offset, video_total, None))

        seg_paths = []
        for i, (start, end, text) in enumerate(timeline):
            dur = end - start
            if dur <= 0.02:
                continue
            seg = tmp_path / f"cap_{i:04d}.mp4"
            if text:
                cap_png = cap_dir / f"cap_{i:04d}.png"
                if bg_style == "chalkboard":
                    _make_chalk_caption_png(text, cap_png)
                else:
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
    p.add_argument("--images", default=None,
                    help="쉼표로 구분된 배경용 실사진 경로들 — --bg-style photo일 때만 필요")
    p.add_argument("--bg-style", default="chalkboard", choices=["chalkboard", "photo"],
                    help="배경 스타일(2026-08-02 기본값 chalkboard로 전환) — "
                         "chalkboard: 짙은 초록 그라디언트+분필체 자막(images 불필요), "
                         "photo: 기존 실사진 슬라이드쇼(images 또는 image_schedule 필요)")
    p.add_argument("--motion", default=None, help="Kling으로 생성한 캐릭터 모션 루프 클립(흰 배경) — 캐릭터 1명짜리 topic용")
    p.add_argument("--motion-schedule", default=None,
                    help="캐릭터 여러 명이 구간별로 번갈아 나올 때 사용. "
                         "형식: 'start-end:경로,start-end:경로,...' (초 단위, 나레이션 기준 0초부터). "
                         "--motion 대신 이걸 쓰면 이 스케줄이 우선한다.")
    p.add_argument("--audio", required=True)
    p.add_argument("--srt", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--title", required=True, help="영상 상단에 계속 표시할 주제 라벨")
    p.add_argument("--intro-duration", type=float, default=0)
    p.add_argument("--ad-tag", action="store_true", help="실제 제휴 링크를 쓰기로 확정한 경우에만 켠다")
    p.add_argument("--bg-color", default="0xFFFFFF",
                    help="캐릭터 모션 클립의 배경색(colorkey 대상) — 새 캐릭터는 0x00FF00 권장")
    p.add_argument("--title-card-duration", type=float, default=1.3,
                    help="영상 맨 앞 단색 제목 카드(썸네일용) 길이(초)")
    p.add_argument("--title-card-text", default=None,
                    help="제목 카드에만 쓸 별도 문구(안 주면 --title 그대로 사용) — "
                         "썸네일은 문제 제기 훅만, 상단 배너는 훅+주제 전체를 보여주고 싶을 때 분리")
    p.add_argument("--title-card-char", default=None,
                    help="제목 카드 배경에 크게 흐리게 깔 캐릭터 이미지 경로(안 주면 단색 배경만)")
    p.add_argument("--end-card-duration", type=float, default=2.0,
                    help="영상 맨 끝 구독/좋아요/팔로우 CTA 카드 길이(초) — 0이면 엔딩 카드 생략")
    p.add_argument("--end-card-text", default=None,
                    help="엔딩 카드에 쓸 문구(안 주면 기본 CTA 문구 사용)")
    p.add_argument("--end-card-char", default=None,
                    help="엔딩 카드 배경에 흐리게 깔 캐릭터 이미지 경로(안 주면 --title-card-char 재사용)")
    args = p.parse_args()

    motion_schedule = None
    if args.motion_schedule:
        motion_schedule = []
        for chunk in args.motion_schedule.split(","):
            # "start-end:path" 또는 "start-end:path:bg_color"(세그먼트별 크로마키 색 override)
            parts = chunk.split(":")
            span, path = parts[0], parts[1]
            start_s, end_s = span.split("-")
            if len(parts) > 2:
                motion_schedule.append((float(start_s), float(end_s), path, parts[2]))
            else:
                motion_schedule.append((float(start_s), float(end_s), path))

    assemble(
        images=args.images.split(",") if args.images else None,
        motion_path=args.motion,
        audio_path=args.audio,
        srt_path=args.srt,
        out_path=args.out,
        title=args.title,
        intro_duration=args.intro_duration,
        ad_tag=args.ad_tag,
        bg_color=args.bg_color,
        title_card_duration=args.title_card_duration,
        title_card_text=args.title_card_text,
        title_card_char_path=args.title_card_char,
        motion_schedule=motion_schedule,
        bg_style=args.bg_style,
        end_card_duration=args.end_card_duration,
        end_card_text=args.end_card_text,
        end_card_char_path=args.end_card_char,
    )
