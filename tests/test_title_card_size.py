# 썸네일(영상 맨 앞 제목 카드) 글자 크기. WHY(2026-09-30 "썸네일 글자 작게 박는 경우도 있네 크게크게 박어"):
# 띄어 쓴 병명·긴 한 단어 병명이 88px로 남는 회귀를 막는다.
from PIL import Image

from lib.video_assembler import _make_title_card_png


def _text_height(path) -> int:
    im = Image.open(path).convert("L")
    rows = [y for y in range(im.height) if max(im.crop((0, y, im.width, y + 1)).getdata()) > 240]
    return rows[-1] - rows[0] if rows else 0


def test_spaced_disease_name_is_big(tmp_path):
    # 두 줄로 나뉘어 줄마다 수백 px — 예전(88px 한 줄)이면 글자 높이가 100px 남짓이었다
    _make_title_card_png("아기 고열", tmp_path / "a.png")
    assert _text_height(tmp_path / "a.png") > 450


def test_long_single_word_split_at_suffix(tmp_path):
    _make_title_card_png("과민성대장증후군", tmp_path / "b.png")
    assert _text_height(tmp_path / "b.png") > 250


def test_long_sentence_still_fits_width(tmp_path):
    _make_title_card_png("자다가 소변 때문에 자주 깨는 사람", tmp_path / "c.png")
    im = Image.open(tmp_path / "c.png").convert("L")
    cols = [x for x in range(im.width) if max(im.crop((x, 0, x + 1, im.height)).getdata()) > 240]
    assert cols[0] >= int(im.width * 0.05) and cols[-1] <= int(im.width * 0.95)
