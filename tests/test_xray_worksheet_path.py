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

