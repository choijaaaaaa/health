"""트랙 폴더 규약을 못 박는다.

WHY(2026-09-24): 육아 트랙만 `data/육아/<topic>/`으로 한 단계 접었다. 이때 가장 쉬운 사고는
topic 이름을 `"육아/육아_1"`로 부르는 것이다 — 이 저장소에서 topic 안의 `/`는 **이미 언어**를
뜻해서(`가슴쓰림_1/en`), fish_tts·youtube_upload·index.html이 `육아_1`을 언어 코드로 읽는다.
트랙은 경로에만 있고 이름에는 없다는 규약을 여기서 지킨다.
"""
import json

from lib import tracks


def test_topic_name_never_carries_the_track():
    """트랙 폴더가 topic 이름에 새어 들어가면 안 된다 — `/`는 언어 자리다."""
    for topic in ("육아_1", "소화_14"):
        assert "/" not in topic
        assert tracks.topic_of_path(tracks.data_dir(topic), tracks.ROOT / "data") == topic


def test_track_topic_lives_one_level_deeper():
    assert tracks.data_dir("육아_1") == tracks.ROOT / "data" / "육아" / "육아_1"
    assert tracks.output_dir("육아_1") == tracks.ROOT / "output" / "육아" / "육아_1"


def test_default_track_layout_is_unchanged():
    """기존 415개 topic은 안 옮긴다 — 평평한 자리를 그대로 가리켜야 한다."""
    assert tracks.data_dir("소화_14") == tracks.ROOT / "data" / "소화_14"
    assert tracks.output_dir("소화_14") == tracks.ROOT / "output" / "소화_14"


def test_language_segment_is_appended_not_parsed():
    assert tracks.data_dir("육아_1/en") == tracks.ROOT / "data" / "육아" / "육아_1" / "en"
    assert tracks.data_dir("소화_14/ja") == tracks.ROOT / "data" / "소화_14" / "ja"


def test_domain_follows_the_track():
    """브랜드커넥트 상품 판정이 갈린다 — 육아는 유아용품이 정답이라 _KID_WORDS를 안 뺀다."""
    assert tracks.domain_of("육아_3") == "baby"
    assert tracks.domain_of("눈_5") == "health"


def _fixture(base):
    (base / "소화_14").mkdir(parents=True)
    (base / "육아" / "육아_1").mkdir(parents=True)
    (base / "육아" / "_shared").mkdir(parents=True)
    (base / "_audit").mkdir()


def test_iter_topic_dirs_flattens_tracks_and_skips_housekeeping(tmp_path):
    _fixture(tmp_path)
    names = [p.name for p in tracks.iter_topic_dirs(tmp_path)]
    assert "소화_14" in names and "육아_1" in names
    assert "육아" not in names, "트랙 폴더 자체가 topic으로 잡히면 그 안의 topic이 통째로 사라진다"
    assert "_audit" not in names and "_shared" not in names


def test_glob_topic_files_reaches_into_tracks(tmp_path):
    _fixture(tmp_path)
    for p in (tmp_path / "소화_14", tmp_path / "육아" / "육아_1", tmp_path / "육아" / "_shared"):
        (p / "clip_requests.json").write_text(json.dumps({"requests": []}), encoding="utf-8")
    hits = tracks.glob_topic_files(tmp_path, "*/clip_requests.json")
    assert {p.parent.name for p in hits} == {"소화_14", "육아_1", "_shared"}


def test_track_of_path_reads_the_folder_not_the_name():
    """`data/육아/_shared/`처럼 topic 이름이 접두어를 안 가진 공용 요청이 있다."""
    assert tracks.track_of_path(tracks.ROOT / "data" / "육아" / "_shared" / "clip_requests.json") == "육아"
    assert tracks.track_of_path(tracks.ROOT / "data" / "소화_14" / "clip_requests.json") is None


def test_work_and_stills_dirs_are_split_per_track():
    sheet, stills, inbox = tracks.work_paths("육아")
    assert sheet.parent.name == "작업_육아" and stills.name == "1_스틸" and inbox.name == "2_완성클립"
    assert tracks.work_paths(None)[0].parent.name == "작업"
    assert tracks.stills_dir("육아").name == "baby"
    assert tracks.stills_dir(None).name == "stills"
