# 엔딩 멘트 음성("도움이 되셨다면 … 화면 더블클릭 부탁드립니다") 필터 조각. WHY: 멘트가 나레이션에 겹치거나 잘리면 안 된다.
from lib.video_assembler import OUTRO_GAP, _narration_with_outro
from lib import rebuild_video


def test_no_outro_keeps_old_filter():
    assert _narration_with_outro(200, 0.7, 0.0, 3, 80.0, 82.2, "narr") == "[1:a]adelay=200|200,apad=pad_dur=0.7[narr]"


def test_outro_starts_after_narration_and_pads_to_full_length():
    f = _narration_with_outro(200, 0.7, 4.6, 3, 80.2, 85.9, "narr")
    assert f"adelay={int((80.2 + OUTRO_GAP) * 1000)}" in f and "[3:a]" in f
    assert f.count("apad=whole_dur=85.900") == 2 and f.endswith("[narr]")


def test_outro_file_is_shipped():
    # 한 번 뽑아 저장소에 둔 파일 — 없으면 조용히 멘트 없는 영상이 나간다
    assert rebuild_video.OUTRO_KOR.exists()
