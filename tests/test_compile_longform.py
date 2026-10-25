# 몰아보기 롱폼(scripts/compile_longform.py)과 롱폼 업로드 기록(yt_upload LONGFORM 키) 테스트. DB·유튜브는 부르지 않는다.
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import pytest
import requests

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import compile_longform as cl  # noqa: E402

yup = cl.yup


class _Resp:
    def __init__(self, rows):
        self._rows = rows

    def raise_for_status(self):
        return None

    def json(self):
        return self._rows


def _slot(days: int, hour: int) -> str:
    d = dt.datetime.now(yup.KST).date() + dt.timedelta(days=days)
    return dt.datetime.combine(d, dt.time(hour), yup.KST).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_longform_row_does_not_take_a_shorts_slot(monkeypatch):
    """롱폼을 내일 17시에 예약해 둬도 쇼츠 17시 슬롯 계산은 그 자리를 빈 칸으로 본다."""
    # 오늘(0)·모레(2)는 쇼츠가 차 있고 내일(1)엔 롱폼만 있다 — 지금 시각과 무관하게 답이 정해지게
    rows = [{"topic": "adult/소화_1", "publish_at": _slot(0, 17), "status": "confirmed"},
            {"topic": "adult/longform/adult_stomach_20261025", "publish_at": _slot(1, 17), "status": "confirmed"},
            {"topic": "adult/소화_9", "publish_at": _slot(2, 17), "status": "confirmed"}]
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(rows))
    monkeypatch.setattr(yup, "PUBLISH_HOURS", [17])
    assert yup.next_free_slots(yup.Channel("adult"), 2) == [_slot(1, 17), _slot(3, 17)]


def test_rows_hide_longform_unless_asked(monkeypatch):
    rows = [{"topic": "adult/longform/x", "publish_at": None}, {"topic": "adult/위_1", "publish_at": None}]
    monkeypatch.setattr(requests, "get", lambda *a, **k: _Resp(rows))
    ch = yup.Channel("adult")
    assert [r["topic"] for r in ch.rows()] == ["adult/위_1"]
    assert len(ch.rows(include_longform=True)) == 2


@pytest.mark.parametrize("title,kw,products,want", [
    ("위경련증상, 명치가 쥐어짜듯 아프고 식은땀까지 난다면 - 유독 아픈 날의 방아쇠 3가지", "위경련증상", [],
     "명치가 쥐어짜듯 아프고 식은땀까지 난다면"),
    ("역류성식도염, 밤에 눕기만 하면 신물이 목까지 올라온다면 베개 쌓기 말고 이렇게 누우세요", "역류성식도염", [],
     "밤에 눕기만 하면 신물이 목까지 올라온다면"),
    ("피부가려움증, 찬바람 불자 정강이가 하얗게 일어난다면 - 씻는 습관부터 바꿔요, 세라마이드 바디크림", "피부가려움증",
     ["세라마이드 바디크림"], "찬바람 불자 정강이가 하얗게 일어난다면"),
    # 머리가 문장이면(검색어 뒤 말이 길면) 증상이 거기 있어서 떼지 않는다
    ("위고비 마운자로 맞은 다음 날 메스꺼움 심할 때, 펜 반씩 나눠 맞기 전에 꼭 알아둘 것", "위고비", [],
     "위고비 마운자로 맞은 다음 날 메스꺼움 심할 때, 펜 반씩 나눠 맞기 전에 꼭 알아둘 것"),
])
def test_split_title(title, kw, products, want):
    assert cl.split_title(title, kw, products) == want


def _ep(keyword: str, chapter: float) -> cl.Episode:
    return cl.Episode(topic="t", video_id="v", publish_at="", title="", keyword=keyword, short=keyword, hook="h",
                      search_volume=0, products=[], product_lines=[], sources=[], subscribe_line="", src="",
                      chapter_sec=chapter)


def test_chapters_start_at_zero_and_keep_ten_second_gaps():
    ch = cl.chapters([_ep("a", 0), _ep("b", 80.2), _ep("c", 167.6)])
    assert [cl._ts(t) for t, _ in ch] == ["0:00", "1:20", "2:47"]
    with pytest.raises(SystemExit):
        cl.chapters([_ep("a", 0), _ep("b", 5), _ep("c", 90)])     # 10초 미만 간격
    with pytest.raises(SystemExit):
        cl.chapters([_ep("a", 0), _ep("b", 80)])                    # 3개 미만


def test_upload_md_round_trip(tmp_path):
    """compile_longform이 쓴 upload.md를 yt_upload가 그대로 읽는다(설명란 안의 빈 줄·목차 포함)."""
    desc = "위염 증상, 소개\n\n⏱ 목차\n0:00 1. 역류성식도염 — 신물\n\n#건강만사전 #위염증상"
    cl.write_upload_md(tmp_path / "upload.md", "위염 증상 | 몰아보기 4편", desc, ["위염 증상", "명치 통증"])
    assert yup.read_longform_upload(tmp_path) == ("위염 증상 | 몰아보기 4편", desc, ["위염 증상", "명치 통증"])


def test_upload_md_rejects_angle_brackets(tmp_path):
    cl.write_upload_md(tmp_path / "upload.md", "제목", "설명 <b>", ["a"])
    with pytest.raises(SystemExit):
        yup.read_longform_upload(tmp_path)
