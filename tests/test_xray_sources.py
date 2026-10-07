# 화면 출처 줄 — 위험이 걸린 주장 문장 동안 출처를 띄우는지, 출처 없는 위험 원고를 잡는지.
import json
import sys
from pathlib import Path

from lib import content_review as cr
from lib import xray_timeline as xt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import xray_splice  # noqa: E402

CUES = [(0.0, 3.0, "쪽쪽이, 안아서만 재우시나요?"),
        (3.5, 9.0, "자던 아기가 갑자기 숨지는 영아돌연사를 다룬 연구 7개를 모아 보니 61% 낮았어요."),
        (9.5, 12.0, "그래서 질병관리청도 권해요.")]


def _topic(tmp_path, monkeypatch, cfg):
    (tmp_path / "xray.json").write_text(json.dumps(cfg, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(xt.tracks, "data_dir", lambda t: tmp_path)
    return "t"


def test_sources_cover_the_sentence(tmp_path, monkeypatch):
    t = _topic(tmp_path, monkeypatch, {"sources": [{"from": "자던 아기가", "text": "출처: Hauck 외, Pediatrics 2005"}]})
    (s,) = xt.sources(t, CUES)
    assert 3.4 < s["start"] < 3.6 and abs(s["end"] - (9.0 + xt.SOURCE_HOLD)) < 1e-6


def test_sources_until_extends(tmp_path, monkeypatch):
    t = _topic(tmp_path, monkeypatch, {"sources": [{"from": "자던 아기가", "until": "질병관리청도", "text": "x"}]})
    (s,) = xt.sources(t, CUES)
    assert abs(s["end"] - (12.0 + xt.SOURCE_HOLD)) < 1e-6


def test_source_png_fits_width(tmp_path):
    img = xray_splice._source_png("출처: 질병관리청 국가건강정보포털 「영아돌연사증후군」 · Hauck 외, Pediatrics(2005) 연구 7개 분석", tmp_path / "s.png")
    assert img.width <= xray_splice.SOURCE_MAX_W


def test_safety_topic_without_sources_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr(cr, "_data_dir", lambda t: tmp_path)
    monkeypatch.setattr(cr.tracks, "output_dir", lambda t: tmp_path / "out")
    (tmp_path / "narration.txt").write_text("자던 아기가 갑자기 숨지는 영아돌연사 위험이 낮았어요.", encoding="utf-8")
    (tmp_path / "xray.json").write_text(json.dumps({"timeline": []}), encoding="utf-8")
    assert any("출처" in x["issue"] for x in cr.check_safety_sources("t"))
    (tmp_path / "xray.json").write_text(json.dumps({"timeline": [], "sources": [{"from": "자던", "text": "출처: x"}]}), encoding="utf-8")
    assert cr.check_safety_sources("t") == []


def test_built_topic_is_skipped(tmp_path, monkeypatch):
    # 이 규칙 전에 조립된 편은 미션컨트롤 목록에서 떨어뜨리지 않는다
    monkeypatch.setattr(cr, "_data_dir", lambda t: tmp_path)
    out = tmp_path / "out"; out.mkdir()
    (out / "shorts_xray_test.mp4").write_bytes(b"x")
    monkeypatch.setattr(cr.tracks, "output_dir", lambda t: out)
    (tmp_path / "narration.txt").write_text("영아돌연사", encoding="utf-8")
    (tmp_path / "xray.json").write_text(json.dumps({"timeline": []}), encoding="utf-8")
    assert cr.check_safety_sources("t") == []
