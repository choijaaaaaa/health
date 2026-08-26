# lib/card_news.py 카드뉴스 생성 파이프라인 테스트.
# WHY: 실제 Gemini/Kling/Fish Audio 없이도 PIL 순수 로직만으로 파일 개수·이름 규칙·
# 이미지 유효성·예외 처리를 검증할 수 있는 모듈이라 실제 API 호출 없이 전부 커버 가능.
from __future__ import annotations

import inspect
import json

import pytest
from PIL import Image

from lib import card_news
from lib.card_news import H, W, generate, make_fact_card


def _write_spec(spec_path, spec: dict) -> None:
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")


def _setup_real_photos(char_dir, item_names: list[str], make_solid_jpg, colors=None) -> None:
    """char_dir과 형제 디렉터리인 real/에 item_names(접미사 "_illust.jpg" 뗀
    이름)와 매칭되는 실사진을 만든다. WHY(2026-08-25, 일러스트 생성 중단):
    generate()가 이제 char_dir(illust/)의 파일은 전혀 열지 않고 항상 이
    real/ 폴더에서 사진을 찾는다 — 테스트도 실제 파이프라인과 같은 디렉터리
    구조로 픽스처를 만들어야 한다."""
    real_dir = char_dir.parent / "real"
    real_dir.mkdir(exist_ok=True)
    colors = colors or [(120, 80, 40)] * len(item_names)
    for name, color in zip(item_names, colors):
        src = make_solid_jpg(f"{name}_real.jpg", color=color)
        (real_dir / f"{name}_real_01.jpg").write_bytes(src.read_bytes())


def _minimal_spec(item_names: list[str], char_files: list[str], eyebrow: str | None = None) -> dict:
    spec = {
        "title": ["훅 줄1", "훅 줄2", "테스트 주제"],
        "items": [
            {
                "name": name,
                "char_file": char_file,
                "body": ["본문 줄1", "본문 줄2", "", "빈 줄로 문단 구분"],
            }
            for name, char_file in zip(item_names, char_files)
        ],
        "closing": {
            "headline": [["마무리 줄1", "마무리 줄2"]],
            "tip": ["팁 줄1", "팁 줄2"],
            "cta": "지금 확인해보세요",
        },
    }
    if eyebrow is not None:
        spec["eyebrow"] = eyebrow
    return spec


class TestGenerate:
    def test_creates_expected_number_and_names_of_files(self, tmp_path, make_solid_jpg):
        # WHY out_dir.parent.name이 topic_prefix로 쓰이므로(generate() 구현 참고)
        # out_dir을 <topic>/card_news 구조로 만들어야 실제 사용 패턴과 동일하게 검증된다.
        topic = "테스트토픽_1"
        char_dir = tmp_path / "chars"
        char_dir.mkdir()
        _setup_real_photos(char_dir, ["아이템1", "아이템2"], make_solid_jpg, colors=[(255, 0, 0), (0, 0, 255)])

        item_names = ["첫번째 카드", "두번째 카드"]
        spec = _minimal_spec(item_names, ["아이템1_illust.jpg", "아이템2_illust.jpg"])
        spec_path = tmp_path / "spec.json"
        _write_spec(spec_path, spec)

        out_dir = tmp_path / topic / "card_news"
        generate(str(spec_path), str(char_dir), str(out_dir))

        files = sorted(p.name for p in out_dir.iterdir())
        n = len(item_names)
        assert len(files) == n + 2

        expected = {f"{topic}_00_표지.jpg"}
        for i, name in enumerate(item_names, start=1):
            expected.add(f"{topic}_{i:02d}_{name}.jpg")
        expected.add(f"{topic}_{n + 1:02d}_마무리.jpg")
        assert set(files) == expected

    def test_generated_files_are_valid_jpgs_with_correct_size(self, tmp_path, make_solid_jpg):
        topic = "사이즈검증_1"
        char_dir = tmp_path / "chars"
        char_dir.mkdir()
        _setup_real_photos(char_dir, ["a", "b", "c"], make_solid_jpg,
                            colors=[(10, 20, 30), (200, 100, 50), (0, 255, 0)])

        item_names = ["카드A", "카드B", "카드C"]
        spec = _minimal_spec(item_names, ["a_illust.jpg", "b_illust.jpg", "c_illust.jpg"])
        spec_path = tmp_path / "spec.json"
        _write_spec(spec_path, spec)

        out_dir = tmp_path / topic / "card_news"
        generate(str(spec_path), str(char_dir), str(out_dir))

        files = list(out_dir.iterdir())
        assert len(files) == len(item_names) + 2
        for f in files:
            with Image.open(f) as img:
                img.load()  # 실제로 디코딩까지 되는지(손상 파일이면 여기서 예외)
                assert img.format == "JPEG"
                assert img.size == (W, H)

    def test_item_name_with_special_characters_does_not_break(self, tmp_path, make_solid_jpg):
        # WHY: 실제 데이터(data/돼지감자차_1/card_news_spec.json)에 "돼지감자란?"처럼
        # 파일명에 안 쓰이는 특수문자가 item name에 들어간 전례가 있다 — macOS는 "/"만
        # 금지라 "?" 자체는 파일명에 들어갈 수 있지만, generate()가 이런 이름을 그대로
        # 예외 없이 파일로 저장하는지 실사용 패턴대로 확인한다.
        topic = "특수문자검증_1"
        char_dir = tmp_path / "chars"
        char_dir.mkdir()
        _setup_real_photos(char_dir, ["돼지감자"], make_solid_jpg, colors=[(150, 100, 50)])

        item_names = ["돼지감자란?", "주의할 점"]
        spec = _minimal_spec(item_names, ["돼지감자_illust.jpg", "돼지감자_illust.jpg"])
        spec_path = tmp_path / "spec.json"
        _write_spec(spec_path, spec)

        out_dir = tmp_path / topic / "card_news"
        generate(str(spec_path), str(char_dir), str(out_dir))

        files = sorted(p.name for p in out_dir.iterdir())
        assert len(files) == len(item_names) + 2
        assert f"{topic}_01_돼지감자란?.jpg" in files
        with Image.open(out_dir / f"{topic}_01_돼지감자란?.jpg") as img:
            img.load()
            assert img.size == (W, H)

    def test_missing_real_photo_raises_value_error(self, tmp_path, make_solid_jpg):
        # WHY ValueError(2026-08-25, 일러스트 생성 중단): 예전엔 char_dir에
        # 일러스트가 없으면 그 파일을 여는 시점에 FileNotFoundError가 났지만,
        # 이제 char_dir(illust/)은 아예 안 열고 real/에서만 사진을 찾는다 —
        # 없으면 렌더링 시작 전 사전 검사에서 ValueError로 막는다(폴백 없음).
        topic = "누락파일검증_1"
        char_dir = tmp_path / "chars"
        char_dir.mkdir()
        # 의도적으로 real/에 매칭 사진을 만들지 않는다.

        spec = _minimal_spec(["카드1"], ["존재하지않음_illust.jpg"])
        spec_path = tmp_path / "spec.json"
        _write_spec(spec_path, spec)

        out_dir = tmp_path / topic / "card_news"
        with pytest.raises(ValueError, match="실사진 없는 품목"):
            generate(str(spec_path), str(char_dir), str(out_dir))


class TestMakeFactCard:
    def test_eyebrow_default_is_health_tip(self):
        sig = inspect.signature(make_fact_card)
        assert sig.parameters["eyebrow"].default == "HEALTH TIP"

    def test_make_fact_card_without_eyebrow_arg_succeeds(self, tmp_path, make_solid_jpg):
        char_path = make_solid_jpg("캐릭터.jpg")
        out_path = tmp_path / "fact_card.jpg"
        # eyebrow를 안 넘겨도(기본값 사용) 예외 없이 생성되는지 확인.
        make_fact_card(1, "테스트 카드", char_path, ["본문 줄1", "본문 줄2"], 3, out_path)

        assert out_path.exists()
        with Image.open(out_path) as img:
            img.load()
            assert img.format == "JPEG"
            assert img.size == (W, H)


class TestMakeCoverTitlecard:
    def test_creates_valid_jpg_with_char_background(self, tmp_path, make_solid_jpg):
        char_path = make_solid_jpg("캐릭터.jpg", color=(80, 160, 220))
        out_path = tmp_path / "cover.jpg"
        card_news.make_cover_titlecard("테스트 훅 카피", out_path, char_path=str(char_path))

        assert out_path.exists()
        with Image.open(out_path) as img:
            img.load()
            assert img.format == "JPEG"
            assert img.size == (W, H)

    def test_creates_valid_jpg_without_char_background(self, tmp_path):
        out_path = tmp_path / "cover_no_char.jpg"
        card_news.make_cover_titlecard("캐릭터 없는 훅 카피", out_path)

        assert out_path.exists()
        with Image.open(out_path) as img:
            img.load()
            assert img.size == (W, H)
