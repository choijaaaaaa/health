# 해결책 칠판 흐름 검사 — 체크리스트형 칠판과 문장 중간에서 시작하는 칠판을 잡는지.
import json
import shutil

import pytest

from lib import content_review as cr


@pytest.fixture
def topic(tmp_path, monkeypatch):
    monkeypatch.setattr(cr, "_data_dir", lambda t: tmp_path)

    def make(narration: str, summary_from: str) -> str:
        (tmp_path / "narration.txt").write_text(narration, encoding="utf-8")
        (tmp_path / "xray.json").write_text(json.dumps({"summary_from": summary_from, "timeline": []}), encoding="utf-8")
        return "t"
    yield make
    shutil.rmtree(tmp_path, ignore_errors=True)


def test_reasoned_board_passes(topic):
    t = topic("기전 설명이에요.\n\n그러니 결과지를 들고 물어보세요. 이 균은 침을 타고 들어와요. "
              "국과 찌개는 앞접시에 덜어 드세요. 체중이 줄면 진료받으세요.", "그러니 결과지를")
    assert cr.check_board_flow(t) == []


def test_checklist_board_flagged(topic):
    t = topic("기전 설명이에요.\n\n압박스타킹은 아침에 신으세요. 등급은 병원에서 고르세요. "
              "국물은 남기세요. 판막이 늘어나요.", "압박스타킹은")
    assert any("이유 없는" in x["issue"] for x in cr.check_board_flow(t))


def test_board_starting_mid_sentence_flagged(topic):
    t = topic("기전 설명이에요.\n\n그러니 속이 메스꺼우면 누우세요. 피가 뇌로 돌아와요.", "속이 메스꺼우면")
    assert any("한가운데" in x["issue"] for x in cr.check_board_flow(t))
