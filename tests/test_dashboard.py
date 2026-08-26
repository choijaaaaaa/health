# lib/dashboard.py의 generate() 대시보드 HTML 생성기 테스트.
# WHY: platform_captions.json(변수명은 spec)을 읽어 플랫폼별 카드 HTML을 만드는데,
# 최근 해시태그 누락 경고·네이버 network 플래그·"열기" 버튼 캡션 자동복사·영상
# placeholder 분기에서 실제 회귀가 있었던 함수라 이 부분을 특히 두텁게 검증한다.
from __future__ import annotations

import json
import re

from lib.dashboard import _dock_products, generate


def _write_spec(path, platforms, title="테스트 주제", topic="테스트주제_1", products=None):
    spec = {"topic": topic, "title": title, "platforms": platforms}
    if products is not None:
        spec["products"] = products
    path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    return path


def _platform(name, ptype, caption="기본 캡션 #건강 #정보", url="https://example.com", **flags):
    p = {"name": name, "url": url, "type": ptype, "caption": caption, "action": "테스트 액션"}
    p.update(flags)
    return p


def _make_dirs(tmp_path):
    """card_news_dir와 out_path를 tmp_path 하위 서브디렉터리로 분리.
    WHY out_path를 tmp_path 바로 밑에 두지 않는지: generate()가 내부에서
    _update_topics_index()를 호출해 out_path의 조부모 디렉터리에 topics.json을
    쓴다 — out_path를 tmp_path/output/<topic>/dashboard.html로 두 단계 중첩해야
    topics.json도 tmp_path 안에 갇혀서 테스트끼리 서로 오염시키지 않는다."""
    card_news_dir = tmp_path / "card_news"
    card_news_dir.mkdir()
    out_dir = tmp_path / "output" / "테스트주제_1"
    out_dir.mkdir(parents=True)
    out_path = out_dir / "dashboard.html"
    return card_news_dir, out_path


def test_generate_creates_html_with_all_platform_names(tmp_path):
    platforms = [
        _platform("네이버 블로그", "text", network="naver", rich_paste=True),
        _platform("인스타그램 릴스", "video", no_caption_link=True, comment_dm_automation=True),
    ]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))

    assert out_path.exists()
    html = out_path.read_text(encoding="utf-8")
    assert "네이버 블로그" in html
    assert "인스타그램 릴스" in html


def test_excluded_platforms_not_rendered(tmp_path):
    """회귀(2026-08-04): 유튜브 쇼츠/틱톡은 업로드 자동화 대상이라 대시보드 UI에
    카드 자체가 안 뜨고, 그 옆의 다른 플랫폼은 그대로 떠야 한다. 한국어 이름과
    글로벌(영어) 이름 둘 다 걸러지는지 확인한다."""
    platforms = [
        _platform("유튜브 쇼츠", "video"),
        _platform("틱톡", "video"),
        _platform("YouTube Shorts", "video"),
        _platform("TikTok", "video"),
        _platform("인스타그램 릴스", "video"),
    ]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    html = out_path.read_text(encoding="utf-8")

    # WHY 전체 html이 아니라 platform-card만 검사하는지: CARD_TEMPLATE 안에 이
    # 플랫폼 이름들을 언급하는 고정 JS 주석(구독자 500명 조건 설명 등)이 있어서
    # 전체 텍스트로 검사하면 그 주석 때문에 오탐(false positive)이 난다.
    cards = re.findall(r'<div class="platform-card".*?(?=<div class="platform-card"|</section>)', html, re.S)
    assert len(cards) == 1
    assert "인스타그램 릴스" in cards[0]


def test_video_filename_never_rendered_regardless_of_files_present(tmp_path):
    """회귀(2026-08-05, "회색박스 텍스트 필요없잖아? 이제 어차피 영상을
    깃허브에 올려놓지를 않는데?"): mp4가 git에 안 올라가서 어떤 영상 파일이
    있든(원본만, 안전 여백 버전까지 둘 다) 대시보드에는 그 파일명을 전혀
    보여주지 않는다 — video_assembler.py가 만드는 <...>_shorts_instagram.mp4
    선택 로직은 이제 dashboard.py 밖(로컬 폴더)에서만 의미가 있다."""
    platforms = [
        _platform("인스타그램 릴스", "video"),
        _platform("네이버 클립", "video"),
    ]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    video_dir = out_path.parent
    (video_dir / "테스트주제_1_shorts.mp4").write_bytes(b"fake original video")
    (video_dir / "테스트주제_1_shorts_instagram.mp4").write_bytes(b"fake safe-margin video")

    generate(str(spec_path), str(card_news_dir), str(video_dir / "테스트주제_1_shorts.mp4"), str(out_path))
    html = out_path.read_text(encoding="utf-8")

    assert "테스트주제_1_shorts.mp4" not in html
    assert "테스트주제_1_shorts_instagram.mp4" not in html


def test_missing_hashtag_prints_warning(capsys, tmp_path):
    """회귀 1: 캡션에 '#'이 없으면 print()로 경고가 찍혀야 한다."""
    platforms = [_platform("해시태그없는플랫폼", "text", caption="해시태그가 아예 없는 캡션입니다")]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))

    captured = capsys.readouterr()
    assert "해시태그없는플랫폼" in captured.out
    assert "해시태그가 없습니다" in captured.out


def test_hashtag_present_no_warning_for_that_platform(capsys, tmp_path):
    """해시태그가 있는 캡션에는 그 플랫폼 이름으로 경고가 찍히면 안 된다."""
    platforms = [_platform("해시태그있는플랫폼", "text", caption="캡션 내용 #건강 #정보")]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))

    captured = capsys.readouterr()
    assert "해시태그있는플랫폼" not in captured.out


def test_naver_network_flag_sets_naver_button_attr_only_on_that_platform(tmp_path):
    """회귀 2: network:'naver'가 있는 플랫폼에만 data-naver-button='1'이 붙어야 하고,
    다른 플랫폼에는 붙으면 안 된다(잘못 붙으면 네이버 URL이 안 들어가는 버그 재발)."""
    # WHY "유튜브 쇼츠"가 아니라 "네이버 클립"/"일반영상플랫폼"을 쓰는지
    # (2026-08-04): "유튜브 쇼츠"는 이제 대시보드 UI에서 아예 빠지는 플랫폼이라
    # (lib/dashboard.py의 _UI_EXCLUDED_PLATFORMS 참고) 여기서 쓰면 필터링돼서
    # 카드 자체가 안 나온다 — 이 테스트의 목적(naver 아닌 video 플랫폼에는
    # data-naver-button이 안 붙는지 검증)과는 무관한 이름으로 교체.
    platforms = [
        _platform("네이버 클립", "video", network="naver"),
        _platform("일반영상플랫폼", "video"),
    ]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms, products=["돼지감자"])
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    html = out_path.read_text(encoding="utf-8")

    cards = re.findall(r'<div class="platform-card".*?(?=<div class="platform-card"|</section>)', html, re.S)
    assert len(cards) == 2

    naver_card = next(c for c in cards if "네이버 클립" in c)
    other_card = next(c for c in cards if "일반영상플랫폼" in c)

    assert 'data-naver-button="1"' in naver_card
    assert 'data-naver-button=""' in other_card


def test_btn_go_has_copy_target_with_sequential_idx_grouped_by_type(tmp_path):
    """회귀 3: '열기' 버튼에 data-copy-target='cap-{idx}'가 붙고 텍스트가
    '열기(캡션 자동복사) →'여야 한다. idx는 원본 JSON 순서가 아니라 TYPE_ORDER
    (video → cards → text)로 그룹핑된 뒤 0부터 매겨진다 — generate() 내부에서
    platforms_by_type 딕셔너리로 먼저 타입별로 묶은 뒤 순회하기 때문이다."""
    platforms = [
        _platform("텍스트A", "text"),
        _platform("영상B", "video"),
        _platform("카드C", "cards"),
        _platform("텍스트D", "text"),
    ]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    html = out_path.read_text(encoding="utf-8")

    assert '열기(캡션 자동복사) →' in html

    pairs = re.findall(r'<h3>(.*?)</h3>.*?data-copy-target="cap-(\d+)"', html, re.S)
    order = {name: idx for name, idx in pairs}
    assert order == {"영상B": "0", "카드C": "1", "텍스트A": "2", "텍스트D": "3"}


def _assert_no_video_status_ui(html):
    assert "<video" not in html
    assert "영상 준비 중" not in html
    assert "영상 조립 완료" not in html


def test_no_video_status_ui_when_video_path_is_none(tmp_path):
    """회귀(2026-08-05, "회색박스 텍스트 필요없잖아? 이제 어차피 영상을
    깃허브에 올려놓지를 않는데?"): video_path가 None이어도 영상 상태를
    알려주는 <video> 태그나 "영상 준비 중" 문구가 나오면 안 된다."""
    platforms = [_platform("영상플랫폼", "video")]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    _assert_no_video_status_ui(out_path.read_text(encoding="utf-8"))


def test_no_video_status_ui_when_video_file_does_not_exist(tmp_path):
    """video_path 문자열은 있지만 가리키는 파일이 실제로 없어도 마찬가지."""
    platforms = [_platform("영상플랫폼", "video")]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)
    missing_video = tmp_path / "없는파일_shorts.mp4"

    generate(str(spec_path), str(card_news_dir), str(missing_video), str(out_path))
    _assert_no_video_status_ui(out_path.read_text(encoding="utf-8"))


def test_no_video_status_ui_when_video_file_exists(tmp_path):
    """실제 mp4가 존재해도 마찬가지 — mp4는 git에 안 올라가서(.gitignore)
    GitHub Pages에서 재생도 안 되므로 파일 존재 여부와 무관하게 UI에 안 보여준다."""
    platforms = [_platform("영상플랫폼", "video")]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)
    video_path = tmp_path / "테스트주제_1_shorts.mp4"
    video_path.write_bytes(b"fake mp4 bytes")

    generate(str(spec_path), str(card_news_dir), str(video_path), str(out_path))
    _assert_no_video_status_ui(out_path.read_text(encoding="utf-8"))


def test_card_news_thumbnails_rendered(tmp_path, make_solid_jpg):
    """회귀(2026-08-05, 방향 전환): 표지(00_표지.jpg) 외 카드뉴스 상세 이미지는
    이제 git에 안 올라가서(.gitignore) GitHub Pages에서 깨진 이미지로 보인다 —
    갤러리에는 표지 한 장만 나와야 한다."""
    platforms = [_platform("카드뉴스플랫폼", "cards")]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    # make_solid_jpg는 자기 자신의 tmp_path(테스트와 동일한 tmp_path) 바로 밑에
    # 파일을 만들므로, card_news_dir(하위 폴더) 경로를 이름에 포함시켜 그 안에 놓는다.
    make_solid_jpg("card_news/00_표지.jpg")
    make_solid_jpg("card_news/01_왜 이런 문제가 생길까요.jpg")
    make_solid_jpg("card_news/02_본문.jpg")

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    html = out_path.read_text(encoding="utf-8")

    assert html.count('<img src="card_news/') == 1
    assert "00_표지.jpg" in html
    assert "01_%EC%99%9C" not in html and "01_왜" not in html


def test_caption_html_special_characters_are_escaped(tmp_path):
    """캡션에 <, >, &가 있으면 _esc()로 이스케이프돼서 HTML이 안 깨져야 한다."""
    dangerous_caption = "위험 문자 테스트 <script>alert('x')</script> & 팀 <b>강조</b> #태그"
    platforms = [_platform("이스케이프플랫폼", "text", caption=dangerous_caption)]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    html = out_path.read_text(encoding="utf-8")

    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
    assert "&amp;" in html
    assert "&lt;b&gt;" in html


def test_no_caption_link_and_comment_dm_attrs_reflected(tmp_path):
    """no_caption_link/comment_dm_automation 플래그가 카드의 data 속성에 정확히 반영되는지."""
    platforms = [
        _platform("인스타그램 릴스", "video", no_caption_link=True, comment_dm_automation=True),
        _platform("네이버 블로그", "text"),
    ]
    spec_path = _write_spec(tmp_path / "platform_captions.json", platforms)
    card_news_dir, out_path = _make_dirs(tmp_path)

    generate(str(spec_path), str(card_news_dir), None, str(out_path))
    html = out_path.read_text(encoding="utf-8")

    cards = re.findall(r'<div class="platform-card".*?(?=<div class="platform-card"|</section>)', html, re.S)
    insta_card = next(c for c in cards if "인스타그램 릴스" in c)
    naver_card = next(c for c in cards if "네이버 블로그" in c)

    assert 'data-no-caption-link="1"' in insta_card
    assert 'data-comment-dm="1"' in insta_card
    assert 'data-no-caption-link=""' in naver_card
    assert 'data-comment-dm=""' in naver_card


# WHY(2026-08-02, "상품도 너한테 던져야겠다 이거 로컬스토리지 불안해서"): 상품 링크를
# output/product_links.json(상품명 → 쿠팡 링크)에서 미리 채워 넣는 기능 테스트.
# _dock_products는 순수 함수라 generate() 전체를 안 돌리고 직접 호출해서 검증한다.

def test_dock_products_prefills_known_link():
    html = _dock_products(["현미"], {"현미": "https://link.coupang.com/a/fSP6lbm8Ki"})
    assert 'value="https://link.coupang.com/a/fSP6lbm8Ki"' in html
    assert 'class="dock-product-row linked"' in html


def test_dock_products_leaves_unknown_product_blank():
    html = _dock_products(["처음 보는 상품"], {"현미": "https://link.coupang.com/a/fSP6lbm8Ki"})
    assert 'value=""' in html
    assert 'class="dock-product-row linked"' not in html


# WHY(2026-08-04, "네이버 커넥트도 주소를 그냥 너가 알고있게 해야겠다 쿠팡처럼... 위젯에도
# 띄워주게 해야되겠어"): 쿠팡과 같은 패턴으로 output/naver_product_links.json에서
# 네이버 커넥트 링크를 미리 채워 넣는 기능 테스트.

def test_dock_products_prefills_naver_link():
    html = _dock_products(["연어"], naver_links={"연어": "https://naver.me/5vJFBL58"})
    assert 'data-market="naver"' in html
    assert 'value="https://naver.me/5vJFBL58"' in html
    assert "네이버 커넥트로 이동" in html
    assert 'class="dock-product-row linked"' in html  # 쿠팡 링크가 없어도 네이버만 있으면 linked


def test_dock_products_naver_goto_link_absent_when_no_link():
    html = _dock_products(["처음 보는 상품"])
    assert 'data-market="naver"' in html  # 입력란 자체는 항상 있음
    assert "네이버 커넥트로 이동" not in html  # 링크가 없으면 이동 버튼은 안 뜸
