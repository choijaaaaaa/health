# scripts/link_health.py 순수 로직 검사 — 네트워크·DB·브라우저 없이 링크 추출·글↔topic 매칭·생존 판정·알림 중복 제거를 본다.
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("link_health", ROOT / "scripts" / "link_health.py")
lh = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lh)

# 실제 블로그 본문(스마트에디터) 꼴을 줄인 것 — 표식 줄의 링크는 <a href>와 보이는 글자 둘 다에 들어 있다
POST_HTML = """
<p class="se-text-paragraph"><span>🔗 나이아신아마이드 크림 구매: </span><span><a href="https://naver.me/xvC5xYzR"
 class="se-link" data-linkdata='{"link": "https://naver.me/xvC5xYzR"}'>https://naver.me/xvC5xYzR</a></span></p>
<p><span>함께 보면 좋은 글 https://naver.me/AbC123 &amp; 끝</span></p>
"""


def test_extract_links_reads_label_and_bare_links():
    got = lh.extract_links(POST_HTML)
    assert ("나이아신아마이드 크림", "https://naver.me/xvC5xYzR") in got
    assert (None, "https://naver.me/AbC123") in got
    # 같은 링크가 href·글자로 두 번 나와도 한 번만
    assert [l for _, l in got].count("https://naver.me/xvC5xYzR") == 1


def test_extract_links_empty_page():
    assert lh.extract_links("<html><body>링크 없음</body></html>") == []


def test_post_title_decodes_plus_and_entities():
    raw = "%EA%B0%95%EC%95%84%EC%A7%80+%26quot%3B%EC%82%AC%EB%A3%8C%26quot%3B"
    assert lh.post_title(raw) == '강아지 "사료"'


TOPICS = {
    "피부_29": "나이아신아마이드, 잡티가 그대로라면 농도보다 바른 기간부터, 나이아신아마이드 크림",
    "소화_14": "역류성 식도염, 누우면 심해지는 이유, 위산 억제 베개",
    "육아_1": "",
}


def test_map_post_exact_and_spacing():
    assert lh.map_post_to_topic("나이아신아마이드,  잡티가 그대로라면 농도보다 바른 기간부터, 나이아신아마이드 크림",
                                TOPICS) == "피부_29"


def test_map_post_without_product_tail():
    # 10-08 이전에 올린 글은 제목 끝 ", <제품>"이 없다
    assert lh.map_post_to_topic("역류성 식도염, 누우면 심해지는 이유", TOPICS) == "소화_14"


def test_map_post_fuzzy_after_small_edit():
    assert lh.map_post_to_topic("나이아신아마이드, 잡티가 그대로라면 농도보다 바른 기간부터예요, 나이아신아마이드 크림",
                                TOPICS) == "피부_29"


def test_map_post_unrelated_is_none():
    assert lh.map_post_to_topic("세탁조 클리너 추천 — 곰팡이 냄새 잡은 후기", TOPICS) is None


def test_map_post_same_keyword_but_rewritten_tail():
    topics = {"댕냥_발바닥": "강아지 발바닥, 패드가 갈라지고 각질이 솟았을 때 먼저 볼 것, 강아지 발바닥 보습",
              "댕냥_발톱": "강아지 발톱, 집에서 깎다 피가 날 때, 강아지 발톱깎이"}
    assert lh.map_post_to_topic("강아지 발바닥, 패드가 갈라지고 각질이 하얗게 솟았을 때 보습제 전에 볼 것",
                                topics) == "댕냥_발바닥"


def test_map_post_same_keyword_different_episode_is_none():
    # 검색어만 같은 다른 편에는 붙이지 않는다
    topics = {"비뇨기_19": "신장 기능 저하, 전해질 파우더 한 포에 든 칼륨이 부담이 되는 이유"}
    assert lh.map_post_to_topic("신장 기능 저하, 사실 거품뇨, 피로감, 붓기로 나타나요 - 만성신장질환 초기신호",
                                topics) is None


def test_map_post_title_is_head_of_old_paragraph_caption():
    topics = {"혈당_6": "당화혈색소, 공복혈당은 정상인데 당뇨병전단계라는 얘기를 들으신 분들 많으실 텐데요. 공복혈당 하나만"}
    assert lh.map_post_to_topic("당화혈색소, 공복혈당은 정상인데 당뇨병전단계", topics) == "혈당_6"


def _p(pid, status="SALE", enabled=True):
    return {"id": pid, "enabled": enabled, "productStatus": status, "storeStatus": "ACTIVE",
            "affiliateStorePenalty": False}


def test_liveness_alive_when_selling():
    state, hit = lh.liveness(805935200949985, [[_p(1), _p(805935200949985)]])
    assert state == "alive" and hit["id"] == 805935200949985


def test_liveness_alive_on_fallback_search():
    # 이름 검색엔 없고 품목 검색에서 판매 중으로 나오면 살아 있다(상품명이 바뀐 경우)
    assert lh.liveness("7", [[_p(1)], [_p(7)]])[0] == "alive"


def test_liveness_stopped_and_gone():
    assert lh.liveness(7, [[_p(7, status="SUSPENSION")]])[0] == "stopped"
    assert lh.liveness(7, [[_p(7, enabled=False)], []])[0] == "stopped"
    assert lh.liveness(7, [[_p(1)], [_p(2)]]) == ("gone", None)


def _alert(**kw):
    base = {"project": "health-shorts", "topic": "피부_29", "platform": "네이버 블로그", "old_link": "https://naver.me/a",
            "resolved_at": None}
    base.update(kw)
    return base


def test_dedupe_skips_open_duplicate():
    assert lh.dedupe_alerts([_alert()], [_alert(id=1)]) == []


def test_dedupe_keeps_other_platform_link_and_resolved_history():
    new = [_alert(platform="네이버 클립"), _alert(old_link="https://naver.me/b"), _alert()]
    out = lh.dedupe_alerts(new, [_alert(id=1, resolved_at="2026-10-01T00:00:00Z")])
    # 풀린 옛 알림은 막지 않고, 같은 배치 안 중복은 하나만
    assert len(out) == 3
    assert len(lh.dedupe_alerts([_alert(), _alert()], [])) == 1


def test_dedupe_keeps_youtube_audit_rows():
    yt = _alert(platform="유튜브 쇼츠", resolved_at="2026-10-15T00:00:00Z")
    assert lh.dedupe_alerts([yt], [_alert(platform="유튜브 쇼츠", id=3)]) == [yt]


def test_replace_in_description_respects_link_boundary():
    desc = "▶ 큐티클 오일: https://naver.me/AbC\n▶ 다른 것: https://naver.me/AbCd"
    out = lh.replace_in_description(desc, "https://naver.me/AbC", "https://naver.me/New1")
    assert "https://naver.me/New1\n" in out and "https://naver.me/AbCd" in out


def test_description_links_parses_product_block():
    desc = "📦 영상 속 제품 (네이버 쇼핑 제휴 링크)\n▶ 세라마이드 바디크림: https://naver.me/x1Y2\n\n본문"
    assert lh.description_links(desc) == {"세라마이드 바디크림": "https://naver.me/x1Y2"}


@pytest.mark.parametrize("url,no", [
    ("https://smartstore.naver.com/main/products/392100126", "392100126"),
    ("https://brandconnect.naver.com/affiliates/100?channelProductNo=10810949244", "10810949244"),
    (None, None), ("https://example.com", None),
])
def test_product_no(url, no):
    assert lh.product_no(url) == no


def test_naver_me_cache_resolves_once(tmp_path, monkeypatch):
    import requests
    calls = []

    class R:
        headers = {"Location": "https://brandconnect.naver.com/affiliates/1?channelProductNo=42"}

    monkeypatch.setattr(requests, "head", lambda *a, **k: calls.append(a) or R())
    c = lh.NaverMeCache(tmp_path / "c.json")
    assert c.get("https://naver.me/q") == "42"
    assert c.get("https://naver.me/q") == "42"
    assert len(calls) == 1
    c.save()
    assert lh.NaverMeCache(tmp_path / "c.json").get("https://naver.me/q") == "42"


def test_off_item_drops_diy_kits_and_cases():
    assert lh.off_item("솔라콤 아크릴 무드등 만들기 조명 DIY 키트", "무드등")
    assert lh.off_item("원터치 화장솜 면봉케이스 인공눈물 보관통", "인공눈물")
    assert not lh.off_item("필립스 LED 수면 무드등", "무드등")
    assert not lh.off_item("젖병 리필 니플", "젖병 리필")


def test_confirmed_dead_needs_two_sightings_apart():
    import datetime as dt
    now = dt.datetime(2026, 10, 15, 12, tzinfo=dt.timezone.utc)
    assert not lh.confirmed_dead({"id": 7, "since": "2026-10-15T11:00:00Z"}, 7, now)
    assert lh.confirmed_dead({"id": 7, "since": "2026-10-15T05:00:00Z"}, 7, now)
    # 그사이 카탈로그 상품이 바뀌었으면 처음부터 다시 센다
    assert not lh.confirmed_dead({"id": 8, "since": "2026-10-14T00:00:00Z"}, 7, now)
