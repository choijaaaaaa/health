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
        make_solid_jpg("아이템1.jpg", color=(255, 0, 0))
        (char_dir / "아이템1.jpg").write_bytes((tmp_path / "아이템1.jpg").read_bytes())
        make_solid_jpg("아이템2.jpg", color=(0, 0, 255))
        (char_dir / "아이템2.jpg").write_bytes((tmp_path / "아이템2.jpg").read_bytes())

        item_names = ["첫번째 카드", "두번째 카드"]
        spec = _minimal_spec(item_names, ["아이템1.jpg", "아이템2.jpg"])
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
        for fname, color in [("a.jpg", (10, 20, 30)), ("b.jpg", (200, 100, 50)), ("c.jpg", (0, 255, 0))]:
            src = make_solid_jpg(fname, color=color)
            (char_dir / fname).write_bytes(src.read_bytes())

        item_names = ["카드A", "카드B", "카드C"]
        spec = _minimal_spec(item_names, ["a.jpg", "b.jpg", "c.jpg"])
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
        src = make_solid_jpg("돼지감자.jpg", color=(150, 100, 50))
        (char_dir / "돼지감자.jpg").write_bytes(src.read_bytes())

        item_names = ["돼지감자란?", "주의할 점"]
        spec = _minimal_spec(item_names, ["돼지감자.jpg", "돼지감자.jpg"])
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

    def test_missing_char_file_raises_file_not_found(self, tmp_path, make_solid_jpg):
        topic = "누락파일검증_1"
        char_dir = tmp_path / "chars"
        char_dir.mkdir()
        # 의도적으로 char_file을 char_dir에 생성하지 않는다.

        spec = _minimal_spec(["카드1"], ["존재하지않음.jpg"])
        spec_path = tmp_path / "spec.json"
        _write_spec(spec_path, spec)

        out_dir = tmp_path / topic / "card_news"
        with pytest.raises(FileNotFoundError):
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
