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


def test_ingredient_codes_are_read_in_english():
    # 2026-10-06 피부_29 "비타민B3"가 "비타민B삼"으로 녹음됐다 — 성분 이름의 숫자는 영어로 읽는 게 관례
    assert to_speech("비타민B3의 한 종류") == "비타민비쓰리의 한 종류"
    assert to_speech("오메가3") == "오메가쓰리"
    assert to_speech("코엔자임Q10") == "코엔자임큐텐"
    assert to_speech("SPF 50") == "SPF 오십"
    assert to_speech("2~5%") == "이 퍼센트에서 오 퍼센트"


# 2026-10-13 "15cm"를 "십오 씨엠"으로 읽었다 — 영문 단위는 한글 읽기로 바뀌어야 한다
def test_latin_units_read_in_korean():
    from lib.korean_numbers import to_speech
    assert to_speech("15cm쯤") == "십오 센티미터쯤"
    assert to_speech("2~3cm") == "이 센티미터에서 삼 센티미터"
    assert to_speech("120mmHg") == "백이십 밀리미터 수은주"
    assert to_speech("126mg/dL") == "백이십육 밀리그램 퍼 데시리터"
    assert to_speech("400IU") == "사백 아이유"
    assert to_speech("3m 거리") == "삼 미터 거리"


def test_no_raw_units_left_in_any_narration():
    """모든 원고를 TTS용으로 바꿨을 때 숫자나 소문자 영문 단위가 남으면 TTS가 알파벳·숫자로 읽는다."""
    import re
    from pathlib import Path
    from lib import tracks
    from lib.korean_numbers import to_speech
    root = Path(__file__).resolve().parent.parent / "data"
    bad = []
    for d in tracks.iter_topic_dirs(root):
        p = d / "narration.txt"
        if not p.exists():
            continue
        sp = to_speech(p.read_text(encoding="utf-8"))
        left = re.findall(r"\d|(?<![A-Za-z])[a-zμµ°][A-Za-z/]{0,5}(?![A-Za-z])", sp)
        if left:
            bad.append(f"{d.name}: {sorted(set(left))[:5]}")
    assert not bad, "TTS 텍스트에 날것으로 남은 숫자·단위:\n" + "\n".join(bad)
