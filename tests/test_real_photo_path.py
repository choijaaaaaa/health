# 실사진 판별 — 공용 사진 풀(assets-shared/files)까지 실사진으로 봐야 원형 배지로 잘리고 키잉을 건너뛴다.
from lib.video_assembler import _is_real_photo_path


def test_assets_shared_photo_is_real():
    assert _is_real_photo_path("/Users/x/Desktop/project/assets-shared/files/pexels_1_ab.jpg")


def test_legacy_real_folder_is_real():
    assert _is_real_photo_path("assets_library/real/시계_real_01.jpg")


def test_illustration_and_none_are_not_real():
    assert not _is_real_photo_path("assets_library/illust/시계_illust.jpg")
    assert not _is_real_photo_path("some/other/files/x.jpg")
    assert not _is_real_photo_path(None)
