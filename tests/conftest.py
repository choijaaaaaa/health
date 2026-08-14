# pytest 공통 픽스처. WHY: 매 테스트 모듈이 각자 임시 이미지/영상을 만들면 중복이 심하고
# 느려진다 — 여기서 가볍고 빠른 합성 소스만 한 번 정의해서 공유한다. 실제 유료 API
# (Gemini/Kling/Fish Audio)는 어떤 테스트에서도 호출하지 않는다(비용+네트워크 의존 회피).
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def repo_root() -> Path:
    return ROOT


@pytest.fixture
def make_solid_jpg(tmp_path):
    """단색 정사각형 JPG를 만들어주는 팩토리. 캐릭터 일러스트 대역으로 쓴다."""
    def _make(name: str, color=(0, 255, 0), size=(256, 256)) -> Path:
        path = tmp_path / name
        Image.new("RGB", size, color).save(path, quality=90)
        return path
    return _make


@pytest.fixture
def make_tiny_clip(tmp_path):
    """ffmpeg color source로 짧은 합성 mp4를 만드는 팩토리. 실제 Kling 모션 클립 대역
    (단색 배경 유지) — video_assembler의 colorkey/스케줄 로직을 빠르게 검증하는 용도."""
    def _make(name: str, duration: float = 1.0, color: str = "0x00FF00", fps: int = 30, size="256x256") -> Path:
        path = tmp_path / name
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"color=c={color}:s={size}:d={duration}:r={fps}",
             "-pix_fmt", "yuv420p", str(path)],
            check=True, capture_output=True,
        )
        return path
    return _make


@pytest.fixture
def make_silent_audio(tmp_path):
    """짧은 무음 mp3를 만드는 팩토리. TTS 없이 영상 조립 로직만 테스트할 때 오디오 입력으로 쓴다."""
    def _make(name: str, duration: float = 3.0) -> Path:
        path = tmp_path / name
        subprocess.run(
            ["ffmpeg", "-y", "-f", "lavfi", "-i", f"anullsrc=r=24000:cl=mono", "-t", str(duration),
             "-q:a", "9", str(path)],
            check=True, capture_output=True,
        )
        return path
    return _make
