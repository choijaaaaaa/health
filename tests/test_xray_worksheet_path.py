"""작업 시트·스틸·완성클립 폴더 이름이 바뀌는 걸 막는다.

WHY(2026-09-24): 시트 이름을 한 번 바꿨더니 사용자가 편집기에 열어둔 파일이 사라져
"내가 뽑을 게 몇 번이었지"를 처음부터 다시 물어야 했다. 이 경로들은 사람이 매일 여는
자리라 정리 욕심으로 건드리면 안 된다.
"""
from scripts import prep_clip_worksheet as w
from scripts import collect_clips as c


def test_worksheet_paths_are_pinned():
    # 2026-09-25 사용자 지시로 deploy/작업/ 한 단계로 옮겼다 — 여기서 또 바꾸지 말 것
    assert w.SHEET.name == "건강만사전.md"
    assert w.WORK.name == "건강만사전_스틸"
    assert w.INBOX == w.WORK, "스틸과 Flow 결과를 한 폴더에서 받는다"
    assert c.INBOX == w.INBOX, "collect_clips와 prep_clip_worksheet이 같은 폴더를 봐야 한다"
    assert w.SHEET.parent == w.WORK.parent and w.SHEET.parent.name == "작업" and w.SHEET.parent.parent.name == "deploy"


def test_sheet_numbers_stay_fixed_within_a_round(tmp_path):
    # 2026-10-06 사용자 "기존 번호를 무시하고 정리하면 어케해 기존 번호 기준으로 이미지 넣어놨는데 플로우에다가"
    sheet = tmp_path / "건강만사전.md"
    first = w._stable_numbers(sheet, ["a", "b", "c"])
    assert first == {"a": 1, "b": 2, "c": 3}
    # b가 끝나 빠지고 새 요청 d가 들어와도 a·c는 그대로, d는 쓴 적 없는 번호
    again = w._stable_numbers(sheet, ["a", "c", "d"])
    assert again == {"a": 1, "c": 3, "d": 4}
