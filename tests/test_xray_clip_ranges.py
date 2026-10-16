# X 위치(x_pos)·칸 클립 범위(act_range/mech_range) — 새 필드가 없으면 예전과 똑같이 동작해야 한다.
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

from lib import xray_timeline

ROOT = Path(__file__).resolve().parent.parent


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(mod)
    return mod


splice = _load("xray_splice")
build = _load("xray_build")


def test_x_center_default_unchanged():
    W, H = splice.W, splice.H
    assert splice._x_center((0, 0, W, H), None, 560, True) == (W // 2, int(H * 0.55))
    px, py, pw, ph = splice.XRAY_PANEL
    assert splice._x_center(splice.XRAY_PANEL, None, 400, False) == (px + pw // 2, py + ph // 2)


def test_x_center_uses_fraction_and_clamps_inside_area():
    W, H = splice.W, splice.H
    assert splice._x_center((0, 0, W, H), [0.5, 0.4], 300, True) == (W // 2, int(H * 0.4))
    # 가장자리로 주면 X가 화면 밖으로 안 나가게 반 크기만큼 안쪽에서 멈춘다
    cx, cy = splice._x_center((0, 0, W, H), [0.0, 1.0], 300, True)
    assert (cx, cy) == (150, H - 150)
    px, py, pw, ph = splice.XRAY_PANEL
    cx, cy = splice._x_center(splice.XRAY_PANEL, [1.0, 0.0], 200, False)
    assert (cx, cy) == (px + pw - 100, py + 100)


def test_cut_without_range_returns_original(tmp_path):
    clip = tmp_path / "c.mp4"
    assert build._cut(clip, None, tmp_path) is clip


def test_cut_trims_to_range(tmp_path):
    clip = tmp_path / "c.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=64x64:rate=30:duration=4",
                    "-pix_fmt", "yuv420p", str(clip)], check=True)
    out = build._cut(clip, [1.0, 2.5], tmp_path)
    assert out != clip and abs(build._duration(out) - 1.5) < 0.1


def test_cut_rejects_bad_range(tmp_path):
    with pytest.raises(SystemExit):
        build._cut(tmp_path / "c.mp4", [3, 1], tmp_path)


def test_resolve_passes_ranges(tmp_path, monkeypatch):
    tl = [{"from": "훅", "item": "a", "mech": "m1", "mech_range": [0, 2]},
          {"from": "답이", "item": "a", "mech": "m2", "act": "a2", "act_range": [1, 3]}]
    (tmp_path / "xray.json").write_text(json.dumps({"timeline": tl}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(xray_timeline.tracks, "data_dir", lambda topic: tmp_path)
    monkeypatch.setattr(xray_timeline, "_cues", lambda topic: [(0.0, 3.0, "훅 문장"), (3.5, 6.0, "이건 답이 아니에요.")])
    r0, r1 = xray_timeline.resolve("t")
    assert r0["mech_range"] == [0, 2] and r0["act_range"] is None
    assert r1["act_range"] == [1, 3] and r1["mech_range"] is None
