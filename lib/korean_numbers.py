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
                 "명", "달", "캔", "장", "병", "접시", "숟가락", "그릇", "곳", "켤레")
# 고유어 단위로 시작하지만 한자어로 읽는 말 — "3개월"은 "세 개월"이 아니라 "삼 개월"
_SINO_WORDS = ("개월", "개국", "개년")
# 단위 그대로 읽으면 어색한 기호는 한글로 바꿔 준다.
_UNIT_WORD = {"%": "퍼센트", "mg": "밀리그램", "g": "그램", "kg": "킬로그램",
              "mL": "밀리리터", "ml": "밀리리터", "L": "리터", "l": "리터",
              "℃": "도", "kcal": "킬로칼로리"}


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
_PAT = re.compile(r"(?<![0-9.])(\d[\d,]*(?:\.\d+)?)\s*([만억조])?\s*"
                  r"(%|℃|kcal|mg|kg|g|mL|ml|L|l|[가-힣]{1,4})?")


def to_speech(text: str) -> str:
    """TTS에 보낼 텍스트 — 아라비아 숫자를 한글 읽기로 바꾼다."""
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
                                                   "시간", "분", "초", "센티미터", "리터", "밀리리터"}, key=len, reverse=True))
    text = re.sub(rf"(\d+)\s*(?:에서|~|∼)\s*(\d+)\s*({_units}|%)", r"\1\3에서 \2\3", text)
    return _PAT.sub(sub, text)
