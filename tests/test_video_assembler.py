# lib/video_assembler.py 회귀/단위 테스트.
# WHY 이 파일이 존재: 2026-07-31 타이틀 카드 fps 버그(제목 카드를 -r 명시 없이
# 만들면 ffmpeg 기본 25fps가 붙어서 본편(30fps)과 concat -c copy할 때 타임스탬프가
# 어긋나 영상 길이가 1.2배로 늘어남) 재발을 자동으로 잡기 위해 작성됨. 그 외
# _parse_srt/_build_character_schedule/_build_background_schedule/make_gradient_bg도
# 함께 커버한다. 전부 conftest의 합성 픽스처(단색 jpg/짧은 color-source mp4/무음
# mp3)만 쓰고 실제 유료 API는 호출하지 않는다.
from __future__ import annotations

import subprocess

import pytest
from PIL import Image

from lib.video_assembler import (
    FPS,
    _build_background_schedule,
    _build_chalkboard_bg,
    _build_character_schedule,
    _make_chalk_caption_png,
    _parse_srt,
    assemble,
    make_gradient_bg,
)


def _ffprobe_duration(path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def _ffprobe_frame_rate(path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    num, den = out.stdout.strip().split("/")
    return float(num) / float(den)


def _write_srt(tmp_path, entries: list[tuple[str, str, str]]):
    """entries: [(start_ts, end_ts, text), ...] — 타임스탬프는 SRT 형식 문자열 그대로."""
    blocks = []
    for i, (start, end, text) in enumerate(entries, start=1):
        blocks.append(f"{i}\n{start} --> {end}\n{text}")
    path = tmp_path / "narration.srt"
    path.write_text("\n\n".join(blocks) + "\n")
    return path


class TestAssembleValidation:
    def test_raises_without_motion_path_or_schedule(self, make_solid_jpg, make_silent_audio, tmp_path):
        img = make_solid_jpg("bg.jpg")
        audio = make_silent_audio("narration.mp3", duration=2.0)
        srt = _write_srt(tmp_path, [("00:00:00,000", "00:00:01,000", "테스트")])
        with pytest.raises(ValueError):
            assemble(
                images=[str(img)],
                motion_path=None,
                audio_path=str(audio),
                srt_path=str(srt),
                out_path=str(tmp_path / "out.mp4"),
                title="제목",
                motion_schedule=None,
            )


class TestParseSrt:
    def test_parses_timestamps_and_text(self, tmp_path):
        srt = _write_srt(tmp_path, [
            ("00:00:00,000", "00:00:01,500", "첫 번째 자막"),
            ("00:00:01,500", "00:00:03,250", "두 번째 자막"),
            ("00:01:02,100", "00:01:04,000", "세 번째 자막"),
        ])
        entries = _parse_srt(str(srt))
        assert len(entries) == 3

        start0, end0, text0 = entries[0]
        assert start0 == pytest.approx(0.0)
        assert end0 == pytest.approx(1.5)
        assert text0 == "첫 번째 자막"

        start1, end1, text1 = entries[1]
        assert start1 == pytest.approx(1.5)
        assert end1 == pytest.approx(3.25)
        assert text1 == "두 번째 자막"

        start2, end2, text2 = entries[2]
        # 1분 2.1초 = 62.1초
        assert start2 == pytest.approx(62.1)
        assert end2 == pytest.approx(64.0)
        assert text2 == "세 번째 자막"

    def test_multiline_caption_joined_with_space(self, tmp_path):
        blocks = "1\n00:00:00,000 --> 00:00:02,000\n첫 줄\n둘째 줄\n"
        srt = tmp_path / "multi.srt"
        srt.write_text(blocks)
        entries = _parse_srt(str(srt))
        assert len(entries) == 1
        assert entries[0][2] == "첫 줄 둘째 줄"


class TestBuildCharacterSchedule:
    def test_total_duration_matches_sum_of_segments(self, make_tiny_clip, tmp_path):
        clip_a = make_tiny_clip("char_a.mp4", duration=1.0, color="0x00FF00")
        clip_b = make_tiny_clip("char_b.mp4", duration=1.0, color="0x0000FF")
        schedule = [
            (0.0, 1.2, str(clip_a)),
            (1.2, 2.5, str(clip_b)),
        ]
        total_duration = 2.5
        out_path = tmp_path / "char_schedule.mov"
        _build_character_schedule(schedule, total_duration, out_path, bg_color="0x00FF00")

        assert out_path.exists()
        dur = _ffprobe_duration(out_path)
        assert dur == pytest.approx(total_duration, abs=0.3)


class TestBuildBackgroundSchedule:
    def test_total_duration_matches_sum_of_segments(self, make_solid_jpg, tmp_path):
        img_a = make_solid_jpg("bg_a.jpg", color=(255, 0, 0))
        img_b = make_solid_jpg("bg_b.jpg", color=(0, 0, 255))
        schedule = [
            (0.0, 1.0, [str(img_a)]),
            (1.0, 2.2, [str(img_b)]),
        ]
        total_duration = 2.2
        out_path = tmp_path / "bg_schedule.mp4"
        _build_background_schedule(schedule, total_duration, out_path)

        assert out_path.exists()
        dur = _ffprobe_duration(out_path)
        assert dur == pytest.approx(total_duration, abs=0.3)


class TestMakeGradientBg:
    def test_top_and_bottom_rows_match_target_colors(self, tmp_path):
        top = (250, 100, 50)
        bottom = (10, 20, 200)
        out_path = tmp_path / "gradient.jpg"
        make_gradient_bg(out_path, top=top, bottom=bottom)

        assert out_path.exists()
        img = Image.open(out_path).convert("RGB")
        w, h = img.size
        top_pixel = img.getpixel((w // 2, 0))
        bottom_pixel = img.getpixel((w // 2, h - 1))

        # JPEG 압축 손실을 감안해 넉넉한 허용치로 top/bottom 색과의 근접성만 확인.
        for c_actual, c_expected in zip(top_pixel, top):
            assert abs(c_actual - c_expected) < 20
        for c_actual, c_expected in zip(bottom_pixel, bottom):
            assert abs(c_actual - c_expected) < 20


class TestChalkboardBackground:
    """2026-08-02 — 실사진 대신 칠판 스타일이 기본이 된 배경/자막 렌더링 검증."""

    def test_build_chalkboard_bg_duration_matches(self, tmp_path):
        out_path = tmp_path / "chalk_bg.mp4"
        duration = 2.0
        _build_chalkboard_bg(duration, out_path)

        assert out_path.exists()
        dur = _ffprobe_duration(out_path)
        assert dur == pytest.approx(duration, abs=0.2)

    def test_make_chalk_caption_png_renders_nonempty_text(self, tmp_path):
        out_path = tmp_path / "chalk_cap.png"
        _make_chalk_caption_png("칠판 자막 테스트", out_path)

        assert out_path.exists()
        img = Image.open(out_path)
        assert img.mode == "RGBA"
        # WHY 완전 투명(전부 alpha=0)이 아닌지 확인: 글자가 실제로 그려졌는지의
        # 최소 확인 — 폰트 로드 실패 등으로 빈 캔버스만 저장되는 회귀를 잡는다.
        alpha = img.getchannel("A")
        assert alpha.getextrema()[1] > 0, "캡션 PNG에 불투명 픽셀이 없음 — 텍스트가 안 그려진 것으로 보임"


class TestAssembleFpsRegression:
    """2026-07-31 실제 발생했던 버그: 타이틀 카드 PNG->mp4 변환 시 -r FPS를 명시 안
    하면 ffmpeg 기본 25fps가 붙고, 본편(30fps)과 -f concat -c copy로 이어붙이는
    순간 두 세그먼트의 타임스탬프가 어긋나 최종 영상 길이가 실제보다 늘어난다
    (30/25=1.2배). title_card_duration + audio_duration이 기대 길이이므로, 실제
    측정된 duration이 그 값에서 크게 벗어나면(오차 0.5초 초과) 이 버그가 재발한 것."""

    def test_output_duration_matches_title_card_plus_audio(
        self, make_solid_jpg, make_tiny_clip, make_silent_audio, tmp_path,
    ):
        img = make_solid_jpg("bg.jpg", color=(120, 90, 60))
        motion = make_tiny_clip("char.mp4", duration=1.0, color="0x00FF00")
        audio_duration = 3.5
        audio = make_silent_audio("narration.mp3", duration=audio_duration)
        srt = _write_srt(tmp_path, [
            ("00:00:00,200", "00:00:01,500", "첫 번째 문장입니다"),
            ("00:00:01,800", "00:00:03,000", "두 번째 문장입니다"),
        ])
        out_path = tmp_path / "out.mp4"
        title_card_duration = 1.3

        assemble(
            images=[str(img)],
            motion_path=str(motion),
            audio_path=str(audio),
            srt_path=str(srt),
            out_path=str(out_path),
            title="테스트 제목",
            bg_color="0x00FF00",
            title_card_duration=title_card_duration,
            # WHY end_card_duration=0(2026-08-02): 이 테스트는 title 카드/본편 fps
            # 불일치 버그 재발만 좁게 검증하는 테스트라, 엔딩 카드(기본 켜짐, 2026-08-02
            # 추가)까지 길이에 섞이면 이 테스트의 관심사가 아닌 변수가 늘어난다 —
            # 엔딩 카드 자체는 별도 테스트(TestAssembleEndCard)에서 검증한다.
            end_card_duration=0,
        )

        assert out_path.exists()
        expected_duration = title_card_duration + audio_duration
        actual_duration = _ffprobe_duration(out_path)
        assert actual_duration == pytest.approx(expected_duration, abs=0.5), (
            f"expected ~{expected_duration}s, got {actual_duration}s — "
            "title 카드/본편 프레임레이트 불일치(fps 버그) 재발 의심"
        )

        frame_rate = _ffprobe_frame_rate(out_path)
        assert frame_rate == pytest.approx(FPS, abs=0.1)


class TestAssembleEndCard:
    """2026-08-02 추가: 영상 맨 끝 구독/좋아요/팔로우 CTA 카드(end_card_duration,
    기본 2.0초 켜짐). 길이가 정확히 그만큼 늘어나는지, 0으로 주면 완전히
    꺼지는지(기존 동작과 동일해지는지) 검증."""

    def _assemble(self, tmp_path, make_solid_jpg, make_tiny_clip, make_silent_audio, **kwargs):
        img = make_solid_jpg("bg.jpg", color=(120, 90, 60))
        motion = make_tiny_clip("char.mp4", duration=1.0, color="0x00FF00")
        audio = make_silent_audio("narration.mp3", duration=2.0)
        srt = _write_srt(tmp_path, [("00:00:00,200", "00:00:01,500", "테스트 문장")])
        out_path = tmp_path / "out.mp4"
        assemble(
            images=[str(img)], motion_path=str(motion), audio_path=str(audio),
            srt_path=str(srt), out_path=str(out_path), title="테스트 제목",
            bg_color="0x00FF00", title_card_duration=1.0, **kwargs,
        )
        return out_path

    def test_end_card_extends_duration_by_exact_amount(
        self, make_solid_jpg, make_tiny_clip, make_silent_audio, tmp_path,
    ):
        out_path = self._assemble(
            tmp_path, make_solid_jpg, make_tiny_clip, make_silent_audio,
            end_card_duration=1.5,
        )
        expected = 1.0 + 2.0 + 1.5  # title_card_duration + audio_duration + end_card_duration
        actual = _ffprobe_duration(out_path)
        assert actual == pytest.approx(expected, abs=0.5)

    def test_end_card_duration_zero_disables_it(
        self, make_solid_jpg, make_tiny_clip, make_silent_audio, tmp_path,
    ):
        out_path = self._assemble(
            tmp_path, make_solid_jpg, make_tiny_clip, make_silent_audio,
            end_card_duration=0,
        )
        expected = 1.0 + 2.0  # title_card_duration + audio_duration만, 엔딩 카드 없음
        actual = _ffprobe_duration(out_path)
        assert actual == pytest.approx(expected, abs=0.5)

    def test_srt_overrunning_audio_does_not_leak_into_end_card(
        self, make_solid_jpg, make_tiny_clip, make_silent_audio, tmp_path,
    ):
        """2026-08-02 실제 버그 재현: 멀티보이스 TTS가 만든 SRT의 마지막 자막
        end 타임스탬프가 실제 오디오 길이보다 길면(구내염_1 등에서 실측 — 문단 사이
        무음 간격이 누적돼 최대 2초 가까이 어긋남), 마지막 자막 구간이 엔딩 카드
        영역까지 침범해서 자막 텍스트와 엔딩 카드 CTA 문구가 한 프레임에 겹쳐
        보였다. SRT가 오디오보다 길어도 최종 영상 길이가 (title+audio+end_card)를
        넘지 않아야 한다(넘으면 자막이 뒤로 밀리며 엔딩 카드를 침범했다는 뜻)."""
        img = make_solid_jpg("bg.jpg", color=(120, 90, 60))
        motion = make_tiny_clip("char.mp4", duration=1.0, color="0x00FF00")
        audio_duration = 2.0
        audio = make_silent_audio("narration.mp3", duration=audio_duration)
        # SRT 마지막 자막이 실제 오디오(2.0초)보다 1초 더 긴 3.0초까지 찍혀있음 —
        # 멀티보이스 gap 누적 오차를 흉내낸 것.
        srt = _write_srt(tmp_path, [
            ("00:00:00,200", "00:00:03,000", "실제 오디오보다 긴 자막")
        ])
        out_path = tmp_path / "out.mp4"
        title_card_duration = 1.0
        end_card_duration = 1.5
        assemble(
            images=[str(img)], motion_path=str(motion), audio_path=str(audio),
            srt_path=str(srt), out_path=str(out_path), title="테스트 제목",
            bg_color="0x00FF00", title_card_duration=title_card_duration,
            end_card_duration=end_card_duration,
        )
        expected = title_card_duration + audio_duration + end_card_duration
        actual = _ffprobe_duration(out_path)
        assert actual == pytest.approx(expected, abs=0.5), (
            f"expected ~{expected}s, got {actual}s — SRT가 오디오보다 길 때 "
            "엔딩 카드 영역까지 침범해서 영상이 늘어난 것으로 보임(클램프 회귀)"
        )
