# lib/youtube_channel_setup.py의 배너 이미지 경로 해석 테스트. WHY: 실제 유튜브
# API는 절대 호출하지 않는다(비용은 없지만 실제 채널 브랜딩이 바뀌는 부작용이
# 있음) — 채널코드/default 폴백 로직만 순수하게 검증한다.
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import lib.youtube_channel_setup as youtube_channel_setup  # noqa: E402
from lib.youtube_channel_setup import _resolve_banner_path  # noqa: E402


def test_resolve_banner_path_uses_channel_specific_file_when_present(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_channel_setup, "BANNER_DIR", tmp_path)
    (tmp_path / "en.jpg").write_bytes(b"fake")
    (tmp_path / "default.jpg").write_bytes(b"fake")
    assert _resolve_banner_path("en") == tmp_path / "en.jpg"


def test_resolve_banner_path_falls_back_to_default(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_channel_setup, "BANNER_DIR", tmp_path)
    (tmp_path / "default.png").write_bytes(b"fake")
    assert _resolve_banner_path("ja") == tmp_path / "default.png"


def test_resolve_banner_path_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(youtube_channel_setup, "BANNER_DIR", tmp_path)
    assert _resolve_banner_path("es") is None
