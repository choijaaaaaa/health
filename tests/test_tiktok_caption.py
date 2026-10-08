# lib/tiktok_caption — 클립·유튜브 캡션에서 틱톡 캡션을 만든다.
from lib import tiktok_caption


def _data(clip: str | None = "제목줄, 크림\n\n본문이에요.\n\n#건강만사전 #크림") -> dict:
    plats = [{"name": "유튜브 쇼츠", "caption": "제목: 유튜브 제목, 크림\n\n설명란:\n긴 설명"}]
    if clip is not None:
        plats.append({"name": "네이버 클립", "caption": clip})
    return {"products": ["크림"], "platforms": plats}


def test_builds_from_youtube_title_and_clip_body():
    out = tiktok_caption.build(_data())
    lines = out.splitlines()
    assert lines[0] == "유튜브 제목, 크림"
    assert "본문이에요." in out and "긴 설명" not in out
    assert "영상 속 제품: 크림 (네이버 쇼핑 제휴 상품)" in out
    assert lines[-1] == "#건강만사전 #크림"
    assert "http" not in out


def test_none_without_clip_caption():
    assert tiktok_caption.build(_data(clip=None)) is None
