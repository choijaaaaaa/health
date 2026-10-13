# 숫자를 한글 읽기로 풀어 TTS에 넘긴다 — 화면 자막은 숫자 그대로 둔다.
#
# WHY(2026-09-24 사용자 "40 이런거 숫자로 넣는거 맨날 끊긴다. 2026 이런거만 그런줄알았는데 숫자
# 나올 때 이런 일이 상당히 많이 발생하네"): Fish Audio는 아라비아 숫자를 만나면 읽기가 뭉개지거나
# 끊긴다. 실측(소화_14 74초 "40세가 넘어")에서 음량은 끊기지 않았으니 무음이 아니라 **발음이
# 무너지는 것**이다. 숫자를 미리 한글로 바꿔 보내면 애초에 판단할 게 없어진다.
#
# 🚨 원고(narration.txt)와 자막은 숫자를 그대로 둔다 — 화면에 "사백 밀리그램"이 뜨면 읽기 힘들다.
# 바꾸는 건 **API로 보내는 텍스트 한 곳뿐**이다.
from __future__ import annotations

import re

_SINO = ["영", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]
_SINO_UNIT = ["", "십", "백", "천"]
_BIG = ["", "만", "억", "조"]
_NATIVE = ["", "한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉", "열",
           "열한", "열두", "열세", "열네", "열다섯", "열여섯", "열일곱", "열여덟", "열아홉", "스무"]

# 고유어로 세는 단위 — "네 잔", "세 번". 나머지는 한자어("사십 세", "사백 밀리그램").
# 2026-09-28 "명" 추가 — "7명 중 1명"을 "칠 명 중 일 명"으로 읽었다(소화_31, 사용자 "일곱 명 중 한 명 이렇게 가야").
_NATIVE_UNITS = ("개", "잔", "컵", "번", "마리", "살", "시", "군데", "가지", "방울", "알",
                 "명", "달", "캔", "장", "병", "접시", "숟가락", "그릇", "곳", "켤레", "겹")
# 고유어 단위로 시작하지만 한자어로 읽는 말 — "3개월"은 "세 개월"이 아니라 "삼 개월"
_SINO_WORDS = ("개월", "개국", "개년")
# 단위 그대로 읽으면 어색한 기호는 한글로 바꿔 준다.
# 🚨 영문 단위를 여기 빼먹으면 TTS가 알파벳으로 읽는다 — 2026-10-13 "15cm"를 "십오 씨엠"으로 읽었다(사용자 "센티미터도
# 아니고 … 단위 같은 거 개같이 읽는 거 많을 것 같은데"). 대본에 쓸 만한 길이·무게·부피·온도 단위는 전부 넣는다.
# IU·ppm은 한국어로도 알파벳으로 읽는 게 관례라("사백 아이유", "피피엠") 읽기를 못 박아 둔다.
_UNIT_WORD = {"%": "퍼센트", "mg": "밀리그램", "g": "그램", "kg": "킬로그램",
              "mcg": "마이크로그램", "μg": "마이크로그램", "µg": "마이크로그램",
              "mL": "밀리리터", "ml": "밀리리터", "L": "리터", "l": "리터",
              "cm": "센티미터", "mm": "밀리미터", "km": "킬로미터", "m": "미터",
              "℃": "도", "°C": "도", "kcal": "킬로칼로리", "IU": "아이유", "ppm": "피피엠",
              # 혈압·혈당 단위는 진료실에서 부르는 대로
              "mmHg": "밀리미터 수은주", "mg/dL": "밀리그램 퍼 데시리터", "mmol/L": "밀리몰 퍼 리터"}


def _sino(n: int) -> str:
    """한자어 읽기. 1은 자리값 앞에서 생략한다(십, 백 — "일십"이 아니다)."""
    if n == 0:
        return "영"
    chunks, out = [], []
    while n:
        chunks.append(n % 10000)
        n //= 10000
    for i in range(len(chunks) - 1, -1, -1):
        c = chunks[i]
        if not c:
            continue
        part = ""
        for j, d in enumerate(reversed(str(c))):
            d = int(d)
            if not d:
                continue
            head = "" if (d == 1 and j > 0) else _SINO[d]
            part = head + _SINO_UNIT[j] + part
        out.append(part + _BIG[i])
    return "".join(out)


def _native(n: int) -> str:
    """고유어 읽기. 스물 넘어가면 어차피 잘 안 쓰므로 한자어로 넘긴다."""
    return _NATIVE[n] if 1 <= n <= 20 else _sino(n)


def _read(num: str, unit: str) -> str:
    if "." in num:
        whole, frac = num.split(".", 1)
        body = _sino(int(whole or 0)) + " 점 " + " ".join(_SINO[int(d)] for d in frac)
    else:
        n = int(num)
        body = _native(n) if unit in _NATIVE_UNITS else _sino(n)
    return body + (" " + _UNIT_WORD.get(unit, unit) if unit else "")


# 숫자 + (만/억) + 단위. 단위는 한글이거나 mg/%/℃ 같은 기호.
# 영문 단위는 긴 것부터(mL이 m보다, mm가 m보다 먼저), 뒤에 영문이 더 붙으면 단위가 아니다(3mmHg·5min 등)
_LATIN_UNITS = sorted((u for u in _UNIT_WORD if u.isascii() and u != "%"), key=len, reverse=True)
_PAT = re.compile(r"(?<![0-9.])(\d[\d,]*(?:\.\d+)?)\s*([만억조])?\s*"
                  r"(%|℃|°C|μg|µg|(?:" + "|".join(map(re.escape, _LATIN_UNITS)) + r")(?![A-Za-z])|[가-힣]{1,4})?")


# WHY 영어로 읽는지(2026-10-06 피부_29): "비타민B3"가 "비타민B삼", "오메가3"가 "오메가삼"으로 나왔다. 성분 이름에 붙은
# 숫자는 한국어로도 영어로 읽는 게 관례다("비타민 비쓰리·디쓰리", "오메가쓰리", "코엔자임 큐텐").
_EN_NUM = {1: "원", 2: "투", 3: "쓰리", 4: "포", 5: "파이브", 6: "식스", 7: "세븐", 8: "에잇", 9: "나인",
           10: "텐", 11: "일레븐", 12: "트웰브"}
_LETTER_KO = {"A": "에이", "B": "비", "C": "씨", "D": "디", "E": "이", "K": "케이", "Q": "큐"}
_CODE_PAT = re.compile(r"(?<![A-Za-z])([ABCDEKQ])(\d{1,2})(?![\d.,%])")
_OMEGA_PAT = re.compile(r"오메가\s?([369])(?!\d)")


def _english_codes(text: str) -> str:
    def code(m: re.Match) -> str:
        n = int(m.group(2))
        return _LETTER_KO[m.group(1)] + _EN_NUM[n] if n in _EN_NUM else m.group(0)
    text = _CODE_PAT.sub(code, text)
    return _OMEGA_PAT.sub(lambda m: "오메가" + _EN_NUM[int(m.group(1))], text)


# 전화·긴급 번호는 한 자리씩 읽는다 — 2026-10-14 "119"를 "백십구"로 읽었다(사용자 "일일구가 아니고 백십구라고 읽더만 말이 되냐").
# 뒤에 세는 단위가 붙으면(119명·112개) 그건 수량이라 원래대로 읽는다. 0은 "공"(전화번호 관례).
_DIGIT_READ = {"0": "공", **{str(i): _SINO[i] for i in range(1, 10)}}
# 수량·연도·혈압으로도 흔한 숫자(120·1600·1800 등)는 넣지 않는다 — "혈압 120"을 "일이공"으로 읽게 된다
_HOTLINE = re.compile(r"(?<![\d.,])(112|119|114|911|1339|1388|1393|1577|1588|1544|1566|1644|1661|1670|1899)"
                      r"(?![\d.,%])(?!\s*(?:개|명|번|살|세|분|초|년|월|일|주|배|회|층|가지|마리|권|장|대|곳|원|칼로리|걸음|"
                      r"g|kg|mg|ml|mL|cm|m|km|kcal|IU|mmHg))")
_PHONE = re.compile(r"(?<![\d])(\d{2,4})-(\d{3,4})(?:-(\d{4}))?(?![\d])")


def _digits(s: str) -> str:
    return "".join(_DIGIT_READ[c] for c in s)   # 띄우면 TTS가 한 자씩 끊어 읽는다 — "일일구"로 붙인다


def to_speech(text: str) -> str:
    """TTS에 보낼 텍스트 — 아라비아 숫자를 한글 읽기로 바꾼다."""
    text = _english_codes(text)
    # 전화번호(02-1234-5678, 1577-1234)·긴급 번호(119)는 한 자리씩 — 수량 읽기보다 먼저
    text = _PHONE.sub(lambda m: ", ".join(_digits(g) for g in m.groups() if g), text)
    text = _HOTLINE.sub(lambda m: _digits(m.group(1)), text)
    def sub(m: re.Match) -> str:
        num, big, unit = m.group(1).replace(",", ""), m.group(2), m.group(3) or ""
        # 단위 자리에 조사·어미가 걸린 경우(40세가 → unit="세가")는 단위만 떼어 읽고 나머지는 붙인다
        tail = ""
        sino_word = next((w for w in _SINO_WORDS if unit.startswith(w)), None)
        if sino_word:
            unit, tail = sino_word, unit[len(sino_word):]
        elif unit and unit not in _UNIT_WORD:
            for k in range(len(unit), 0, -1):
                if unit[:k].endswith(_NATIVE_UNITS) or k == 1:
                    tail = unit[k:]
                    unit = unit[:k]
                    break
        if big:
            return _sino(int(float(num))) + big + (" " + _UNIT_WORD.get(unit, unit) if unit else "") + tail
        return _read(num, unit) + tail
    # "3에서 4명", "3~4명" — 앞 숫자에도 단위를 붙여 "세 명에서 네 명"으로 읽는다("삼 에서 사 명" 방지)
    _units = "|".join(sorted(set(_NATIVE_UNITS) | {"그램", "킬로그램", "밀리그램", "퍼센트", "배", "주", "년", "일", "개월",
                                                   "시간", "분", "초", "센티미터", "리터", "밀리리터",
                                                   "월", "세", "회", "층", "단계", "도", "학년", "번째", "킬로"}
                                                  | set(map(re.escape, _LATIN_UNITS)), key=len, reverse=True))
    text = re.sub(rf"(\d+)\s*(?:에서|~|∼)\s*(\d+)\s*({_units}|%)(?![A-Za-z])", r"\1\3에서 \2\3", text)
    # 단위 없는 범위("1~2")와 남은 물결표 — TTS가 "~"를 못 읽거나 건너뛴다(2026-10-13 전수 검사: "사~오 월")
    text = re.sub(r"(\d)\s*[~∼]\s*(\d)", r"\1에서 \2", text)
    # 숫자 없이 단위만 쓴 자리("kg당")도 알파벳으로 읽으면 안 된다 — 한 글자 단위(m·g·L)는 약어와 헷갈려 뺀다
    text = re.sub(r"(?<![A-Za-z0-9])(" + "|".join(map(re.escape, (u for u in _LATIN_UNITS if len(u) > 1))) + r")(?![A-Za-z])",
                  lambda m: _UNIT_WORD[m.group(1)], text)
    # 줄표(—)는 소리로 읽히거나 이상하게 끊긴다 — 쉼표 쉼으로
    text = re.sub(r"\s*[—–]\s*", ", ", text)
    # 기호가 낀 숫자 — "7:30"은 시각, "1:1"은 비율, "1/2"은 분수(그대로 보내면 "칠:삼십", "일/이"로 넘어간다)
    def clock(m: re.Match) -> str:
        h, mi = int(m.group(1)), int(m.group(2))
        return _native(h) + " 시" + (" " + _sino(mi) + " 분" if mi else "")
    text = re.sub(r"(?<![\d:])(\d{1,2}):([0-5]\d)(?![\d:])", clock, text)
    text = re.sub(r"(?<![\d:])(\d+)\s*:\s*(\d+)(?![\d:])", lambda m: _sino(int(m.group(1))) + " 대 " + _sino(int(m.group(2))), text)
    text = re.sub(r"(?<![\d/])(\d+)\s*/\s*(\d+)(?![\d/])", lambda m: _sino(int(m.group(2))) + "분의 " + _sino(int(m.group(1))), text)
    # 달 이름은 관례 읽기 — 6월 "유월", 10월 "시월"("육 월", "십 월"로 읽으면 어색하다)
    text = re.sub(r"(?<!\d)(6|10)\s*월", lambda m: {"6": "유월", "10": "시월"}[m.group(1)], text)
    return _PAT.sub(sub, text)
