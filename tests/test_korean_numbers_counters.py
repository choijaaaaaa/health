# 숫자 읽기 — 사람 수·개월·범위(2026-09-28 "7명 중 1명"을 "칠 명 중 일 명"으로 읽은 사고)
from lib.korean_numbers import to_speech


def test_people_count_is_native():
    assert to_speech("7명 중 1명꼴로") == "일곱 명 중 한 명꼴로"
    assert to_speech("10명 중 8명") == "열 명 중 여덟 명"


def test_range_repeats_unit():
    assert to_speech("10명 중 3에서 4명") == "열 명 중 세 명에서 네 명"
    assert to_speech("한 캔에 5에서 8그램") == "한 캔에 오 그램에서 팔 그램"


def test_months_stay_sino():
    assert to_speech("3개월") == "삼 개월"
    assert to_speech("2잔") == "두 잔"


def test_percent_and_month_ranges():
    assert to_speech("60~70%") == "육십 퍼센트에서 칠십 퍼센트"
    assert to_speech("6개월에서 9개월") == "육 개월에서 구 개월"
