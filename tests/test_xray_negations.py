# xray.json negations → 빨간 X 시각 계산. WHY: 같은 부정어("아니에요")가 원고에 여러 번 나와도 부정 문장 뒤에서만 찾아야 한다.
import json

from lib import xray_timeline


CUES = [
    (0.0, 3.0, "훅 문장이에요?"),
    (3.5, 6.0, "이건 답이 아니에요."),
    (6.5, 9.0, "그런데 교차복용은 기본 방법이 아니에요."),
]


def _write(tmp_path, monkeypatch, negs):
    (tmp_path / "xray.json").write_text(json.dumps({"negations": negs}, ensure_ascii=False), encoding="utf-8")
    monkeypatch.setattr(xray_timeline.tracks, "data_dir", lambda topic: tmp_path)


def test_x_at_found_after_from_not_earlier_match(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [{"from": "교차복용은", "x_at": "아니에요", "clip": "c.mp4"}])
    (m,) = xray_timeline.negations("t", CUES)
    assert 6.5 < m["start"] < m["x_start"] < 9.0
    assert m["end"] == 9.0 + xray_timeline.NEGATION_HOLD
    assert m["clip"] == "c.mp4"


def test_without_x_at_mark_starts_at_from(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [{"from": "답이"}])
    (m,) = xray_timeline.negations("t", CUES)
    assert m["x_start"] == m["start"] and m["clip"] is None


def test_missing_phrase_raises(tmp_path, monkeypatch):
    _write(tmp_path, monkeypatch, [{"from": "없는 말"}])
    try:
        xray_timeline.negations("t", CUES)
    except ValueError:
        return
    raise AssertionError("구절을 못 찾으면 조용히 넘어가면 안 된다")


def test_no_negations_key_is_empty(tmp_path, monkeypatch):
    (tmp_path / "xray.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(xray_timeline.tracks, "data_dir", lambda topic: tmp_path)
    assert xray_timeline.negations("t", CUES) == []
