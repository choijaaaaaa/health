# 플랫폼별 업로드 결과물 대시보드 생성기. WHY: 포스팅 API가 없는 플랫폼이 대부분이라
# 자동 업로드는 불가능 — 대신 영상/카드뉴스 미리보기 + 캡션(수정 가능)을 한 페이지에
# 모아두고, 사람이 확인·수정한 뒤 버튼 눌러 플랫폼으로 이동해서 수동 업로드하는
# 흐름을 지원한다.
# 2026-07-30 개편: 플랫폼마다 "뭘 첨부하고 뭘 눌러야 하는지"가 한눈에 안 보인다는
# 피드백으로, type(video/cards/text)별 배지·행동 지침·바로가기 다운로드 링크를 추가하고
# 콘텐츠 유형별로 섹션을 나눠 스캔하기 쉽게 재구성.
from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.parse import quote, quote_plus


def _esc(text: str) -> str:
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace('"', "&quot;")
    )


TYPE_LABEL = {"video": "영상", "cards": "카드뉴스", "text": "텍스트"}
TYPE_SECTION_TITLE = {
    "video": "영상 업로드 플랫폼",
    "cards": "카드뉴스(캐러셀) 플랫폼",
    "text": "텍스트 게시 플랫폼",
}
TYPE_ORDER = ["video", "cards", "text"]

# WHY 이 플랫폼들은 대시보드 UI에서 아예 뺀다(2026-08-04, "틱톡 플랫폼 배제하고
# 유튜브 숏츠도 이제 어차피 다 업로드해주니까 이것도 배제하자"): 유튜브 쇼츠는
# 업로드 자동화가 이미 처리하고, 틱톡은 업로드 대상에서 제외하기로 해서, 파일
# 상단 WHY의 "사람이 수동 업로드" 전제가 이 둘에는 더 이상 맞지 않는다. 언어별로
# 표시 이름이 다르므로(한국어는 "유튜브 쇼츠"/"틱톡", 그 외 전 언어는 글로벌
# 표시용 영어 이름 "YouTube Shorts"/"TikTok"을 그대로 씀) 두 형태 모두 넣는다.
#
# ⚠️ 쓰레드·인스타그램 카드뉴스 추가(2026-08-04, "쓰레드랑 인스타 카드뉴스
# 없애자. 카드뉴스는 일단 나중에는 쓸수도 있겠는데 릴스보다 효과가없어서
# 갯수 한도가 있으니 릴스만 올려야할듯. 쓰레드는 효과가 없어서 그냥
# 배제하려고"): 캡션 자체는 그대로 두고(카드뉴스는 나중에 다시 쓸 가능성이
# 있다고 했으므로 platform_captions.json에서 삭제하지 않음 — 글로벌
# topic처럼 아예 캡션 작성 자체를 생략하는 것과는 다른 케이스, 여기는
# "UI에서만 숨기기") UI 카드만 숨긴다. 나중에 다시 켜고 싶으면 이 두 이름만
# 빼면 된다.
_UI_EXCLUDED_PLATFORMS = {
    "유튜브 쇼츠", "틱톡", "YouTube Shorts", "TikTok",
    "쓰레드", "인스타그램 카드뉴스", "Threads", "Instagram Carousel",
}

DOCK_PRODUCT_ROW_TEMPLATE = """
<div class="dock-product-row{row_class}" id="dock-row-{idx}">
  <div class="dock-product-head">
    <button class="row-toggle" data-row="dock-row-{idx}" title="링크 넣기">🔗</button>
    <span class="dock-product-name">{name}</span>
  </div>
  <div class="dock-product-market">
    <a href="{coupang_url}" target="_blank" rel="noopener">🛒 쿠팡 검색</a>
    <button type="button" class="copy-market-link" data-url="{coupang_url}" title="검색 링크 복사 — 파트너스 링크 생성기에 붙여넣기용">🔎 복사</button>
    <div class="product-link-row">
      <input type="text" class="product-link-input" data-market="coupang" data-product="{name_attr}" value="{link_value}" placeholder="쿠팡 링크 붙여넣고 Enter">
      <button type="button" class="copy-product-link" title="입력한 파트너스 링크 복사">📋 복사</button>
    </div>
    <div class="link-error" data-for="coupang"></div>
    <a href="{naver_search_url}" target="_blank" rel="noopener">🟢 네이버 검색</a>
    <button type="button" class="copy-market-link" data-url="{naver_search_url}" title="검색 링크 복사 — 브랜드커넥트 링크 생성기에 붙여넣기용">🔎 복사</button>
    {naver_goto}
    <div class="product-link-row">
      <input type="text" class="product-link-input" data-market="naver" data-product="{name_attr}" value="{naver_link_value}" placeholder="네이버 커넥트 링크 붙여넣고 Enter">
      <button type="button" class="copy-product-link" title="입력한 네이버 커넥트 링크 복사">📋 복사</button>
    </div>
  </div>
</div>
"""

CARD_TEMPLATE = """
<div class="platform-card" data-done-key="{done_key}" data-no-caption-link="{no_caption_link_attr}" data-naver-button="{naver_button_attr}" data-profile-note="{profile_note_attr}" data-comment-dm="{comment_dm_attr}" data-suppress-product-block="{suppress_product_block_attr}" data-link-in-comment="{link_in_comment_attr}">
  <div class="platform-head">
    <div class="platform-name-wrap">
      <span class="type-badge badge-{type}">{type_label}</span>
      <h3>{name}</h3>
    </div>
    <div class="head-actions">
      <label class="done-check">
        <input type="checkbox" class="done-toggle" data-key="{done_key}" data-name="{name}">
        <span>완료</span>
      </label>
      <a class="btn-go" href="{url}" target="_blank" rel="noopener" data-copy-target="cap-{idx}">열기(캡션 자동복사) →</a>
    </div>
  </div>
  <div class="action-line">{action}</div>
  {asset_link}
  <textarea class="caption-box" id="cap-{idx}" spellcheck="false">{caption}</textarea>
  <div class="card-actions">
    <button class="btn-copy" data-target="cap-{idx}">캡션 복사</button>
    <a class="btn-go" href="{url}" target="_blank" rel="noopener" data-copy-target="cap-{idx}">열기(캡션 자동복사) →</a>
    <span class="edit-hint">직접 수정 가능</span>
    {naver_connect_comment_btn}
  </div>
</div>
"""

# WHY 영상 미리보기 박스가 없는지(2026-08-05, "회색박스 텍스트 필요없잖아? 이제
# 어차피 영상을 깃허브에 올려놓지를 않는데?"): mp4가 git에 안 올라가서 실제로
# 재생도 안 되는 "영상 조립 완료 / 로컬에서 확인" 텍스트만 있는 박스였다 — 로컬
# output/ 폴더에서 직접 작업하는 사람에게는 굳이 화면에 또 안내할 필요가 없다는
# 지적으로 뺐다. 표지 이미지 갤러리만 남는다.
# WHY quick-dock에 실사진 소싱(Unsplash/Pexels)·제작 도구(인포크/쿠팡파트너스/
# 타입캐스트) 섹션이 없는지(2026-08-05, "UI에 찌꺼기가 좀 많이남아있다...
# 쓸모없는것들 정리"): 이 페이지는 콘텐츠가 이미 완성된 뒤 업로드만 하는
# 단계인데, 저 링크들은 전부 제작(리서치·TTS·소싱) 단계 도구라 이 시점엔 쓸
# 일이 없다.
PAGE_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 업로드 대시보드</title>
<style>
  :root {{
    --bg-top: #fdf9f5; --bg-bottom: #f6ede6;
    --ink: #2b231f; --ink-soft: #8b7c6e;
    --accent: #c84a62; --accent-deep: #a3344a; --accent-soft: #fadee3;
    --gold: #b27a26; --gold-soft: #f1e3c6; --panel: #fffdfa; --rule: #e9ddd0;
    --video: #3a6ea5; --video-soft: #dbe9f7;
    --cards: #7a5ca8; --cards-soft: #e9e0f5;
    --text: #4a8f6b; --text-soft: #dcefe4;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", -apple-system, sans-serif;
    background: linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
    color: var(--ink);
  }}
  header {{ padding: 36px 24px 24px; text-align: center; }}
  header .eyebrow {{
    display: inline-block; background: var(--accent); color: #fff; font-size: 12px; font-weight: 700;
    padding: 5px 16px; border-radius: 999px; margin-bottom: 12px;
  }}
  header h1 {{ margin: 0; font-size: 24px; line-height: 1.4; }}
  .ad-tag-badge {{
    display: inline-block; margin-top: 10px; background: #2f2a24; color: #fff; font-size: 12px;
    font-weight: 700; padding: 4px 12px; border-radius: 999px;
  }}

  section {{ max-width: 1040px; margin: 0 auto; padding: 0 24px 28px; }}
  section > h2 {{
    font-size: 14px; letter-spacing: 0.04em; color: var(--ink-soft); text-transform: uppercase;
    margin: 0 0 14px; display: flex; align-items: center; gap: 8px;
  }}
  section > h2::before {{ content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }}

  .card-gallery {{
    background: var(--panel); border: 1px solid var(--rule); border-radius: 18px; padding: 16px;
    scroll-margin-top: 20px;
  }}
  .card-scroll {{ display: flex; gap: 10px; overflow-x: auto; padding-bottom: 6px; }}
  .card-scroll img {{
    height: 220px; border-radius: 10px; box-shadow: 0 6px 14px rgba(60,45,35,0.15);
    cursor: pointer; flex: 0 0 auto;
  }}
  .card-scroll img:hover {{ outline: 3px solid var(--accent-soft); }}

  .quick-dock {{
    position: fixed; top: 50%; right: 14px; transform: translateY(-50%); z-index: 9999;
    width: 208px; max-height: 82vh; overflow-y: auto;
    background: var(--panel); border: 1px solid var(--rule); border-radius: 18px;
    box-shadow: 0 10px 30px rgba(60,45,35,0.25); padding: 14px;
    display: flex; flex-direction: column; gap: 14px;
  }}
  .dock-head {{ display: flex; align-items: center; justify-content: space-between; }}
  .dock-head span {{ font-size: 13px; font-weight: 700; color: var(--ink); }}
  .dock-section h4 {{
    margin: 0 0 8px; font-size: 11px; letter-spacing: 0.03em; text-transform: uppercase;
    color: var(--ink-soft);
  }}
  .dock-links {{ display: flex; flex-direction: column; gap: 6px; }}
  .dock-links a, .dock-links-btn {{
    display: flex; align-items: center; gap: 6px; width: 100%; box-sizing: border-box;
    background: var(--accent-soft); color: var(--accent-deep); text-decoration: none;
    font-size: 12px; font-weight: 700; padding: 8px 10px; border-radius: 8px;
    border: none; cursor: pointer; font-family: inherit; text-align: left;
  }}
  .dock-links a:hover, .dock-links-btn:hover {{ background: var(--gold-soft); color: var(--gold); }}
  .dock-product-row {{
    border: 1px solid var(--rule); border-radius: 10px; padding: 8px; margin-bottom: 6px;
    transition: background 0.2s, border-color 0.2s;
  }}
  .dock-product-row.linked {{ background: var(--gold-soft); border-color: var(--gold); }}
  .dock-product-head {{ display: flex; align-items: center; gap: 6px; }}
  .dock-product-name {{ flex: 1; font-size: 12px; font-weight: 700; }}
  .row-toggle {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 6px; border: none; font-size: 11px; cursor: pointer;
    background: var(--rule); color: var(--ink-soft); flex: 0 0 auto;
  }}
  .dock-product-row.linked .row-toggle {{ background: var(--gold); color: #fff; }}
  .dock-product-market {{ display: none; margin-top: 8px; }}
  .dock-product-row.row-expanded .dock-product-market {{ display: block; }}
  .dock-product-market a {{
    display: inline-block; font-size: 11px; font-weight: 700;
    background: var(--accent-soft); color: var(--accent-deep); text-decoration: none;
    padding: 5px 10px; border-radius: 999px; margin-bottom: 4px;
  }}
  .dock-product-market a:hover {{ background: var(--gold-soft); color: var(--gold); }}
  .copy-market-link {{
    display: inline-block; font-size: 11px; font-weight: 700;
    background: var(--accent-soft); color: var(--accent-deep); border: none;
    padding: 5px 10px; border-radius: 999px; margin-bottom: 4px; margin-left: 4px; cursor: pointer;
    font-family: inherit;
  }}
  .copy-market-link:hover {{ background: var(--gold-soft); color: var(--gold); }}
  .copy-market-link.copied {{ background: var(--gold); color: #fff; }}
  .product-link-row {{ display: flex; gap: 6px; align-items: center; }}
  .product-link-input {{
    display: block; flex: 1; min-width: 0; border: 1px solid var(--rule); border-radius: 6px;
    padding: 7px 9px; font-size: 12px; font-family: inherit; color: var(--ink); box-sizing: border-box;
  }}
  .product-link-input:focus {{ outline: 2px solid var(--accent-soft); }}
  .link-error {{
    display: none; color: #d33; font-size: 11px; margin: 2px 0 6px; line-height: 1.4;
  }}
  .link-error.show {{ display: block; }}
  .copy-product-link {{
    flex: 0 0 auto; font-size: 11px; font-weight: 700;
    background: var(--cards-soft); color: var(--cards); border: none;
    padding: 7px 10px; border-radius: 999px; cursor: pointer; font-family: inherit;
  }}
  .copy-product-link:hover {{ background: var(--gold-soft); color: var(--gold); }}
  .copy-product-link.copied {{ background: var(--gold); color: #fff; }}
  .copy-comment-links {{
    display: block; width: 100%; font-size: 12px; font-weight: 700; font-family: inherit;
    background: var(--accent); color: #fff; border: none; cursor: pointer;
    padding: 9px 14px; border-radius: 999px; margin-bottom: 10px; box-sizing: border-box;
  }}
  .copy-comment-links:hover {{ opacity: 0.9; }}
  .copy-comment-links.copied {{ background: var(--gold); color: #fff; }}

  .bottom-product-links {{
    margin: 40px 24px; padding: 20px; border-radius: 16px; background: var(--panel);
    border: 1px solid var(--rule);
  }}
  .bottom-product-links h2 {{ margin: 0 0 12px; font-size: 18px; }}
  .bottom-product-row {{
    display: flex; align-items: center; gap: 10px; flex-wrap: wrap;
    padding: 10px 0; border-top: 1px solid var(--rule); font-size: 13px;
  }}
  .bottom-product-name {{ font-weight: 700; min-width: 120px; }}
  .bottom-product-nolink {{ color: var(--ink-soft); }}
  @media (max-width: 860px) {{
    .quick-dock {{ position: static; transform: none; width: auto; max-height: none; margin: 0 24px 24px; }}
  }}

  .platform-section + .platform-section {{ margin-top: 6px; }}

  .platform-tabs {{ display: flex; gap: 8px; margin-bottom: 18px; }}
  .platform-tab-btn {{
    font-family: inherit; font-size: 14px; font-weight: 700; padding: 10px 20px;
    border-radius: 999px; border: 1px solid var(--rule); background: var(--panel);
    color: var(--ink-soft); cursor: pointer;
  }}
  .platform-tab-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  .platform-tab-pane {{ display: none; }}
  .platform-tab-pane.active {{ display: block; }}

  .grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 18px;
  }}
  .platform-card {{
    background: var(--panel); border: 1px solid var(--rule); border-radius: 16px; padding: 16px;
    display: flex; flex-direction: column;
  }}
  .platform-head {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 10px; }}
  .platform-name-wrap {{ display: flex; flex-direction: column; gap: 4px; }}
  .platform-head h3 {{ margin: 0; font-size: 16px; }}
  .type-badge {{
    display: inline-block; width: fit-content; font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 999px;
  }}
  .badge-video {{ background: var(--video-soft); color: var(--video); }}
  .badge-cards {{ background: var(--cards-soft); color: var(--cards); }}
  .badge-text {{ background: var(--text-soft); color: var(--text); }}
  .head-actions {{ display: flex; flex-direction: column; align-items: flex-end; gap: 8px; }}
  .done-check {{
    display: flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 700;
    color: var(--ink-soft); cursor: pointer; user-select: none;
  }}
  .done-check input {{ width: 15px; height: 15px; accent-color: var(--accent); cursor: pointer; }}
  .btn-go {{
    background: var(--accent); color: #fff; text-decoration: none; font-size: 13px; font-weight: 700;
    padding: 9px 16px; border-radius: 999px; white-space: nowrap;
  }}
  .platform-card.is-done {{ opacity: 0.55; border-color: var(--gold); background: var(--gold-soft); }}
  .platform-card.is-done .done-check {{ color: var(--gold); }}
  .action-line {{
    font-size: 13px; color: var(--ink); background: var(--gold-soft); border-radius: 8px;
    padding: 8px 12px; margin-bottom: 8px; line-height: 1.5;
  }}
  .asset-link {{
    display: inline-block; font-size: 12px; font-weight: 700; color: var(--accent-deep);
    text-decoration: none; margin-bottom: 10px;
  }}
  .asset-link.disabled {{ color: var(--ink-soft); cursor: default; }}
  .caption-box {{
    background: #fbf6f1; border: 1px solid var(--rule); border-radius: 10px; padding: 12px;
    font-family: inherit; font-size: 13px; line-height: 1.6;
    height: 180px; resize: vertical; margin: 0 0 10px; color: var(--ink);
  }}
  .caption-box:focus {{ outline: 2px solid var(--accent-soft); }}
  .card-actions {{ display: flex; align-items: center; gap: 10px; }}
  .btn-copy {{
    background: var(--accent-soft); color: var(--accent-deep); border: none;
    font-size: 12px; font-weight: 700; padding: 8px 16px; border-radius: 999px; cursor: pointer;
  }}
  .btn-copy.copied {{ background: var(--gold); color: #fff; }}
  .edit-hint {{ font-size: 11px; color: var(--ink-soft); }}
  .copy-naver-connect-comment {{
    background: var(--gold-soft, #fdeecb); color: var(--gold, #b5820a); border: none;
    font-size: 12px; font-weight: 700; padding: 8px 16px; border-radius: 999px; cursor: pointer;
  }}
  .copy-naver-connect-comment.copied {{ background: var(--gold); color: #fff; }}

  .lightbox {{
    display: none; position: fixed; inset: 0; background: rgba(20,14,10,0.85);
    align-items: center; justify-content: center; z-index: 100; padding: 24px;
  }}
  .lightbox.open {{ display: flex; }}
  .lightbox img {{ max-width: 100%; max-height: 90vh; border-radius: 12px; }}
</style>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"></script>
<script src="{asset_prefix}supabase_client.js"></script>
</head>
<body>
<header>
  <div class="eyebrow">업로드 대시보드</div>
  <h1>{title}</h1>
  {ad_tag_badge}
</header>

<div class="quick-dock" id="quickDock">
  <div class="dock-head">
    <span>빠른 도구</span>
  </div>
  <div class="dock-section">
    <h4>다운로드</h4>
    <div class="dock-links">
      <button class="dock-links-btn" id="downloadAllCards">🖼 카드 이미지 전체 다운로드</button>
    </div>
  </div>
  {dock_products}
</div>

<section>
  <h2>미리보기</h2>
  <div class="card-gallery" id="card-gallery">
    <div class="card-scroll">{card_thumbs}</div>
  </div>
</section>

{platform_sections}

{dock_products_bottom}

<div class="lightbox" id="lightbox"><img id="lightbox-img" src=""></div>

<script>
const CARD_IMAGE_NAMES = {card_image_names_js};
// WHY 파일명에 topic 접두어(2026-07-31): 여러 세션이 동시에 여러 topic을 작업하다보니
// 다운로드 폴더에 "shorts.mp4", "00_표지.jpg"가 topic마다 겹쳐서 뭐가 뭔지 구분이
// 안 됐다 — 다운로드되는 모든 파일명 앞에 topic 이름을 붙인다.
const TOPIC_NAME = {topic_name_js};
// WHY posting_log/product_links를 Supabase에도 미러링하는지(2026-08-08, "db에는
// 내가 제어하는것들 전반적으로 넣도록하자"): localStorage는 여전히 기기 재방문 시
// 즉시 복원되는 1차 소스로 유지하고(기존 캡션 자동삽입 로직이 이 값을 그대로
// 읽으므로 건드리지 않음), Supabase는 기기가 바뀌어도 안 사라지는 진짜 기록으로
// 병행 저장한다 — 초기 로드 시 localStorage에 없으면 Supabase 값으로 채운다.
const sb = window.supabase.createClient(window.HS_SUPABASE_URL, window.HS_SUPABASE_ANON_KEY);
// WHY 중복 접두어 방지: card_news.py가 이제 파일명에 topic을 직접 붙이므로(예전
// topic은 안 붙어있음), 이미 붙어있으면 또 붙이지 않는다.
function _withTopicPrefix(name) {{
  return name.startsWith(TOPIC_NAME + "_") ? name : TOPIC_NAME + "_" + name;
}}

document.querySelectorAll(".platform-tab-btn").forEach(btn => {{
  btn.addEventListener("click", () => {{
    const target = btn.dataset.tabTarget;
    document.querySelectorAll(".platform-tab-btn").forEach(b => b.classList.toggle("active", b === btn));
    document.querySelectorAll(".platform-tab-pane").forEach(
      p => p.classList.toggle("active", p.dataset.tabPane === target)
    );
  }});
}});

// WHY 링크의 ?tab=으로 들어온 경우 탭 전환 UI 자체를 없애는지(2026-08-07,
// "카드뉴스 탭으로 들어가서 대시보드 들어가는 경우엔 숏츠는 안 보이고,
// 숏츠 탭으로 들어가서 대시보드 들어가는 경우엔 카드뉴스형태 콘텐츠는 안
// 보여야지"): index.html 목록에서 어느 탭을 눌러 들어왔는지에 따라 그
// 트랙만 보이게 강제 — 전환 가능한 탭 버튼이 남아있으면 결국 다른 트랙도
// 볼 수 있어버리므로 버튼째로 숨긴다.
(function () {{
  const tabParam = new URLSearchParams(location.search).get("tab");
  const target = tabParam === "card_news" ? "cardnews" : tabParam;
  if (!target) return;
  const panes = document.querySelectorAll(".platform-tab-pane");
  const hasTarget = Array.from(panes).some(p => p.dataset.tabPane === target);
  if (!hasTarget) return;
  document.getElementById("topicTrackTabButtons")?.remove();
  panes.forEach(p => p.classList.toggle("active", p.dataset.tabPane === target));
}})();

const downloadAllBtn = document.getElementById("downloadAllCards");
if (downloadAllBtn) {{
  downloadAllBtn.addEventListener("click", () => {{
    const originalLabel = downloadAllBtn.textContent;
    downloadAllBtn.textContent = "다운로드 중…";
    CARD_IMAGE_NAMES.forEach((name, i) => {{
      setTimeout(() => {{
        const a = document.createElement("a");
        a.href = "card_news/" + name;
        a.download = _withTopicPrefix(decodeURIComponent(name));
        document.body.appendChild(a);
        a.click();
        a.remove();
        if (i === CARD_IMAGE_NAMES.length - 1) {{
          setTimeout(() => {{ downloadAllBtn.textContent = originalLabel; }}, 500);
        }}
      }}, i * 350);
    }});
  }});
}}

document.querySelectorAll(".row-toggle").forEach(btn => {{
  btn.addEventListener("click", () => {{
    const row = document.getElementById(btn.dataset.row);
    const open = row.classList.toggle("row-expanded");
    if (open) row.querySelector(".product-link-input").focus();
  }});
}});

// WHY: 쿠팡파트너스 링크 생성기는 URL을 붙여넣어야 하는데, 검색 버튼은 새 탭으로
// 페이지를 열 뿐 URL을 손에 쥐여주지 않는다 — 주소창에서 매번 직접 복사하지
// 않아도 되게 검색 링크 자체를 바로 클립보드에 담아준다.
document.querySelectorAll(".copy-market-link").forEach(btn => {{
  const originalLabel = btn.textContent;
  btn.addEventListener("click", () => {{
    navigator.clipboard.writeText(btn.dataset.url).then(() => {{
      btn.textContent = "복사됨 ✓";
      btn.classList.add("copied");
      setTimeout(() => {{ btn.textContent = originalLabel; btn.classList.remove("copied"); }}, 1500);
    }});
  }});
}});

// WHY: 파트너스에서 발급받은 실제 링크를 이 칸에 붙여넣어두는 건 캡션 자동
// 반영용인데, 그 링크를 다른 곳(예: 다른 플랫폼 캡션에 수동으로)에도 써야 할 때
// 입력창에서 직접 드래그 선택해 복사하지 않아도 되게 옆에 복사 버튼을 둔다.
document.querySelectorAll(".copy-product-link").forEach(btn => {{
  const originalLabel = btn.textContent;
  btn.addEventListener("click", () => {{
    const input = btn.previousElementSibling;
    navigator.clipboard.writeText(input.value.trim()).then(() => {{
      btn.textContent = "복사됨 ✓";
      btn.classList.add("copied");
      setTimeout(() => {{ btn.textContent = originalLabel; btn.classList.remove("copied"); }}, 1500);
    }});
  }});
}});

// WHY(2026-08-02, "쓰레드랑 페이스북같은거 인스타도 그렇게 댓글 달 때 복사해서 바로
// 붙여넣을 수 있는 그런 버튼도"): link_in_comment 플랫폼(쓰레드·페이스북)은 캡션
// 본문에 링크를 안 넣고 "댓글에 남겨둘게요"로만 안내해서, 실제로 댓글에 붙여넣을
// 링크 텍스트를 어디서도 바로 못 가져왔다 — 게시 직후 댓글로 남길 링크 목록(상품명+
// 링크+고지문구)을 한 번에 복사할 수 있는 버튼을 상품 링크 위젯에 추가한다. 상품
// 링크가 topic 전체에 하나뿐이라 플랫폼 카드마다 반복 안 넣고 여기 한 곳에만 둔다
// — 쓰레드·페이스북뿐 아니라 인스타그램 등 어느 플랫폼 댓글에 붙여넣어도 된다.
// WHY 안내 문장을 앞에 붙이는지(2026-08-02, "띡 링크만 전달하면 안될거같지않아?
// 어느정도 설명이 필요할것으로 보이는데"): _buildLinkBlock(false)만 그대로 복사하면
// 링크 목록만 툭 던지는 스팸성 댓글처럼 보인다 — 캡션에서 이미 "댓글에 남겨둘게요!"라고
// 예고했으니, 그 예고를 그대로 받는 안내 문장을 링크 앞에 붙여서 자연스러운 댓글
// 형태로 만든다. WHY "오늘 소개한 상품"이 아니라 "빠르게 이동할 수 있는 링크"인지
// (2026-08-02 재수정, "오늘 소개한..? 아니 그냥 목록 전달정도니까 빠르게 이동할수있는
// 링크 전달하는 정도의 문구로 해야함"): 상품을 소개하는 느낌보다 그냥 바로가기
// 링크 모음이라는 담백한 톤으로 정정.
const COMMENT_LINK_INTRO = "🔗 빠르게 이동할 수 있는 링크 목록이에요!";
// WHY 이 버튼이 따로 필요한지(2026-08-06, "네이버클립 근데 댓글까지 필요한거면
// 댓글도 어떻게 올릴지 UI에 반영되어야할거같은데"): 네이버 쇼핑 커넥트 표시
// 규정은 쿠팡 파트너스와 위치가 다르다 — 대가성 문구를 캡션 본문이 아니라
// 업로드 직후 남기는 "첫 번째 고정 댓글"로 따로 달아야 한다(공식 문서는 못
// 찾음, 실제 활동자 가이드 기준 — CLAUDE.md "네이버 클립" 절 참고). 문구
// 자체가 고정 문장이라 링크 조합이 필요없어서 COMMENT_LINK_INTRO/
// _buildLinkBlock 재사용 없이 상수 하나만 그대로 복사한다.
const NAVER_CONNECT_COMMENT = "이 포스팅은 네이버 쇼핑 커넥트 활동의 일환으로, 판매 발생 시 수수료를 제공받습니다.";
document.querySelectorAll(".copy-naver-connect-comment").forEach(btn => {{
  const originalLabel = btn.textContent;
  btn.addEventListener("click", () => {{
    navigator.clipboard.writeText(NAVER_CONNECT_COMMENT).then(() => {{
      btn.textContent = "복사됨 ✓";
      btn.classList.add("copied");
      setTimeout(() => {{ btn.textContent = originalLabel; btn.classList.remove("copied"); }}, 1500);
    }});
  }});
}});
// WHY querySelectorAll(2026-08-02, "쿠팡 링크 맨 아래에도 추가해달라고 했는데"):
// 이 버튼이 상단 덕 패널에만 있었는데, 페이지 맨 아래에도 같은 버튼을 복제해서
// 넣었다 — id 하나만 바라보는 getElementById로는 두 번째 복제본이 안 잡혀서
// class 기준 querySelectorAll로 바꿨다(위 row-toggle 등 다른 버튼들과 동일 패턴).
document.querySelectorAll(".copy-comment-links").forEach(copyCommentLinksBtn => {{
  const originalLabel = copyCommentLinksBtn.textContent;
  copyCommentLinksBtn.addEventListener("click", () => {{
    // WHY .text/.disclosure로 분해해서 쓰는지(2026-08-03 버그 수정, "댓글용 링크
    // 텍스트 복사 하면 [Object Object]만 뜨네" — 실제 발견): _buildLinkBlock이
    // 위 고지문구 위/아래 배치 재작업 때 문자열 대신 {{text, disclosure}} 객체를
    // 반환하도록 바뀌었는데, 여기서는 그 변경 전 코드 그대로 문자열 이어붙이듯
    // 썼다 — 객체를 문자열에 그냥 이어붙이면 JS가 암묵적으로 toString()을 불러서
    // "[object Object]"가 나온다. applyProductLinks()가 이미 쓰는 것과 같은
    // 패턴(.text/.disclosure 각각 접근)으로 맞춘다.
    const linkBlock = _buildLinkBlock(false);
    const text = linkBlock ? COMMENT_LINK_INTRO + "\\n\\n" + linkBlock.text + "\\n\\n" + linkBlock.disclosure : "";
    if (!text) {{
      copyCommentLinksBtn.textContent = "먼저 상품 링크를 입력해주세요";
      setTimeout(() => {{ copyCommentLinksBtn.textContent = originalLabel; }}, 1500);
      return;
    }}
    navigator.clipboard.writeText(text).then(() => {{
      copyCommentLinksBtn.textContent = "복사됨 ✓";
      copyCommentLinksBtn.classList.add("copied");
      setTimeout(() => {{
        copyCommentLinksBtn.textContent = originalLabel;
        copyCommentLinksBtn.classList.remove("copied");
      }}, 1500);
    }});
  }});
}});

document.querySelectorAll(".btn-copy").forEach(btn => {{
  const originalLabel = btn.textContent;
  const onCopied = () => {{
    btn.textContent = "복사됨 ✓";
    btn.classList.add("copied");
    setTimeout(() => {{ btn.textContent = originalLabel; btn.classList.remove("copied"); }}, 1500);
  }};
  btn.addEventListener("click", () => {{
    // WHY replace: 자동추가 구간 경계 표시는 보이지 않는 문자라 원래도 화면엔 안 보이지만,
    // 혹시 몰라 복사 시점에 한 번 더 확실히 제거한다.
    const text = document.getElementById(btn.dataset.target).value.split(AUTO_LINKS_START).join("").split(AUTO_LINKS_END).join("").split(AUTO_BOTTOM_START).join("").split(AUTO_BOTTOM_END).join("");
    navigator.clipboard.writeText(text).then(onCopied);
  }});
}});
// WHY 열기 버튼도 자동 복사(2026-08-01, "버튼 누르면 그 플랫폼으로 넘어가서 글까지
// 전부 들어가있는 상태로" 요청): 대부분 플랫폼은 URL 쿼리로 캡션을 미리 채우는 게
// 막혀 있어서(스팸 방지 목적, 페이스북도 예전엔 됐지만 지금은 링크 공유만 가능) 직접
// prefill은 불가능 — 대신 "열기" 클릭 시점에 캡션을 클립보드에 같이 복사해서, 플랫폼
// 페이지로 넘어간 뒤 붙여넣기 한 번만 하면 되게 한다. target="_blank"라 새 탭에서
// 열리므로 현재 페이지는 그대로 남아 있어 클립보드 복사 후 라벨 피드백도 보여줄 수 있다.
document.querySelectorAll(".btn-go[data-copy-target]").forEach(btn => {{
  const originalLabel = btn.textContent;
  btn.addEventListener("click", () => {{
    const target = document.getElementById(btn.dataset.copyTarget);
    if (!target) return;
    const text = target.value.split(AUTO_LINKS_START).join("").split(AUTO_LINKS_END).join("").split(AUTO_BOTTOM_START).join("").split(AUTO_BOTTOM_END).join("");
    navigator.clipboard.writeText(text).then(() => {{
      btn.textContent = "캡션 복사됨 ✓ 붙여넣기만 하면 돼요";
      setTimeout(() => {{ btn.textContent = originalLabel; }}, 2000);
    }});
  }});
}});
const lightbox = document.getElementById("lightbox");
const lightboxImg = document.getElementById("lightbox-img");
document.querySelectorAll(".card-scroll img").forEach(img => {{
  img.addEventListener("click", () => {{
    lightboxImg.src = img.src;
    lightbox.classList.add("open");
  }});
}});
lightbox.addEventListener("click", () => lightbox.classList.remove("open"));

const COUPANG_DISCLOSURE = {coupang_disclosure_js};
const NAVER_DISCLOSURE = {naver_disclosure_js};
const COMMENT_KEYWORD = {comment_keyword_js};
const LINK_STORAGE_PREFIX = "hs_link_{topic}_";
// WHY 눈에 안 보이는 문자(zero-width space/non-joiner) 두 개로 구간의 시작·끝을
// 표시: 이전엔 마커 하나로 "여기부터 끝까지"만 표시해서 자동추가 블록이 캡션 맨
// 끝에 붙는 경우에만 안전했다 — 그런데 공정위 표시광고 지침상 고지문이 "게시물
// 첫 부분/제목 근처"에 있어야 한다는 게 확인돼서(2026-08-02) 블록을 제목 바로
// 다음(중간)에 삽입해야 했고, 그러면 시작 마커만으로는 "블록이 어디서 끝나고
// 원래 본문이 어디서 다시 시작하는지" 알 수 없다. 시작/끝 마커로 구간을 정확히
// 감싸서 토글할 때마다 그 구간만 안전하게 제거하고 새로 넣을 수 있게 한다.
const AUTO_LINKS_START = "\\u200b";
const AUTO_LINKS_END = "\\u200c";
// WHY 마커 쌍이 하나 더 필요한지(2026-08-03): 위 마커 쌍은 "제목 바로 다음"(캡션
// 중간)에 삽입되는 블록 하나만 감쌀 수 있다 — 게시물 맨 끝에 고지문을 별도로
// 붙이려면 서로 겹치지 않는 별개의 마커 쌍으로 그 구간도 감싸야 토글·재계산 시
// 정확히 그 구간만 지우고 새로 넣을 수 있다(안 그러면 상품 링크 입력할 때마다
// applyProductLinks가 다시 돌면서 하단 고지문이 계속 누적됨).
const AUTO_BOTTOM_START = "\\u200d";
const AUTO_BOTTOM_END = "\\u2060";

function _stripMarkedRegion(text, startMark, endMark) {{
  const startIdx = text.indexOf(startMark);
  if (startIdx === -1) return text;
  const endIdx = text.indexOf(endMark, startIdx);
  const before = text.slice(0, startIdx).replace(/\\n+$/, "");
  const after = endIdx === -1 ? "" : text.slice(endIdx + endMark.length).replace(/^\\n+/, "");
  if (!before) return after;
  if (!after) return before;
  return before + "\\n\\n" + after;
}}

function _stripAutoLinks(text) {{
  text = _stripMarkedRegion(text, AUTO_LINKS_START, AUTO_LINKS_END);
  text = _stripMarkedRegion(text, AUTO_BOTTOM_START, AUTO_BOTTOM_END);
  return text;
}}

// WHY 마커/줄바꿈을 여기서 안 붙이는지(2026-08-02 리팩터): 예전엔 이 함수들이 직접
// "\\n\\n"+마커까지 붙여서 반환했는데, 그러면 "캡션 맨 끝에 이어붙이기"만 가능했다
// — 이제 삽입 위치(제목 바로 다음)를 applyProductLinks 쪽에서 결정해야 해서, 이
// 함수들은 순수 내용만 반환하고 마커·위치는 호출부에서 감싼다.
// WHY 고지문구 붙인 문자열을 바로 반환하지 않고 {{text, disclosure}}로 나눠
// 반환하는지(2026-08-03 재작업 — "링크랑 수수료 받는다는 문구... 상단뿐만아니라
// 하단에도 같이넣어줘 여러번 말했었는데 아직 대응이안된듯" 재지적): 처음 이
// 요청에 대응했을 때는 `_withDisclosure`가 고지문을 상품 블록 바로 위·아래에만
// 붙였다 — 그 블록 자체가 캡션 "제목 바로 다음"(중간)에 삽입되니, 실제로는 고지가
// 캡션 중간에 두 번 붙어있을 뿐 정작 게시물 맨 끝에는 하나도 없었다(사용자가
// 스크린샷으로 실제 확인). 진짜 요구사항은 "게시물 전체의 맨 위·맨 아래"라, 이제
// 이 함수들은 고지문 없이 순수 블록 내용만 반환하고, 맨 위(제목 다음)·맨 아래
// (캡션 최종 끝) 배치는 호출부(`applyProductLinks`)가 각각 한 번씩 담당한다.
function _buildLinkBlock(hasNaverButton) {{
  if (hasNaverButton) {{
    // WHY 실제 링크를 넣는지(2026-08-04, "등록만하면 되겠냐? 그럼 이제 자동으로
    // 링크 거는게 가능해진건데 네이버 커넥트도 링크 넣어놔야지 본문에"): 2026-08-01엔
    // 상품명만 나열했었다 — 그 시점엔 네이버 커넥트 계정 ID만 있고 상품별 최종
    // 링크 자체가 없어서("그 입력창이 성가시기만 하고 실제로 쓰는 링크도 아니었다")
    // URL을 넣을 수가 없었다. 이제 output/naver_product_links.json에 상품별 실제
    // naver.me 링크가 등록돼 있어서, 쿠팡 분기와 동일하게 실제 링크를 본문에 넣는다
    // (네이버 커넥트는 쿠팡과 달리 저품질 판정 이슈가 없는 네이버 자체 프로그램이라
    // 링크를 본문에 넣어도 안전 — 위 "네이버 블로그, 다시 브랜드커넥트로" 절 참고).
    // 아직 링크가 없는 상품은 이름만 나열(하위 호환 폴백).
    const lines = [];
    document.querySelectorAll('.product-link-input[data-market="naver"]').forEach(inp => {{
      const url = inp.value.trim();
      lines.push(url ? "🔗 " + inp.dataset.product + " 구매: " + url : "🔵 상품: " + inp.dataset.product);
    }});
    if (lines.length === 0) return null;
    return {{text: lines.join("\\n"), disclosure: NAVER_DISCLOSURE}};
  }}
  const lines = [];
  document.querySelectorAll('.product-link-input[data-market="coupang"]').forEach(inp => {{
    const url = inp.value.trim();
    if (url) lines.push("🔗 " + inp.dataset.product + " 구매: " + url);
  }});
  if (lines.length === 0) return null;
  return {{text: lines.join("\\n"), disclosure: COUPANG_DISCLOSURE}};
}}

// WHY 원본 URL 대신 CTA 문장(2026-07-30/31): 인스타·틱톡은 캡션 속 URL이 클릭이
// 안 된다(2026-07-30 확인) — 링크 텍스트 대신 안내 문장을 넣는다.
// ⚠️ WHY comment_keyword가 항상 "쿠팡" 고정인지(2026-08-01): topic마다 다르게 등록하던
// 방식에서 전체 topic 공용 "쿠팡"으로 통일했다 — 인포크 자동화가 게시물 단위로 걸리는
// 구조라 트리거 단어가 겹쳐도 게시물마다 다른 링크를 매핑하면 되기 때문(topic별 고유
// 키워드로 인포크/레지스트리 중복을 막던 절차가 필요 없어짐).
// ⚠️ WHY disclosure가 항상 쿠팡 고정인지(2026-08-01): 마켓 토글 자체가 없어져서 이
// CTA를 쓰는 플랫폼(인스타·틱톡)은 애초에 네이버 쪽 CTA가 나올 일이 없다 — no_caption_link
// 플랫폼과 network:"naver" 플랫폼(네이버 클립)은 서로 겹치지 않는 집합이라 안전하다.
// ⚠️ WHY hasCommentDm 분기가 필요한지(2026-07-31 버그 수정): "댓글에 남기면 보내드려요"는
// 인포크 댓글→DM 자동화가 실제로 연동된 인스타그램에만 맞는 말이다 — 이 자동화가 없는
// 틱톡까지 no_caption_link라는 이유만으로 똑같은 CTA를 붙였더니, 틱톡 캡션에 이미 있는
// "🔗 상품 링크는 프로필에!"와 정반대로 모순되는 두 안내가 나란히 붙는 버그가 났다
// ("틱톡에는 인포크 구조가 안 되는데 왜 댓글 달면 보내준다는 문구가 있냐" 지적). 자동화가
// 없는 플랫폼은 CTA 문장 없이 고지문구만 붙인다.
// ⚠️ WHY 프로필 안내를 여기서 직접 넣는지(2026-07-31 재수정): 처음엔 "정적 캡션에 이미
// 프로필 안내가 있다"고 가정하고 여기선 고지문구만 붙였는데, 다른 topic이 그 정적 문구를
// 안 써놓으면 고지문구만 덩그러니 붙고 링크를 어디서 찾으라는 안내가 아예 없어지는
// 사고가 났다("쿠팡 파트너스 관련된 무엇도 있는게 없는데 프로필로라도 가서 확인하라고
// 해야되는거 아니냐" 지적) — 정적 캡션에 의존하지 않도록 이 블록 자체가 항상 안내를
// 포함하게 만든다(중복되더라도 안내가 아예 없는 것보다 낫다).
// ⚠️ WHY _hasMarketLink 체크를 제거했는지(2026-07-31 버그 수정): no_caption_link
// 플랫폼(인스타·틱톡)은 URL을 애초에 캡션에 안 넣으므로 "상품 링크 입력창에 URL을
// 타이핑해놨는지"는 이 CTA 문구랑 아무 상관이 없다 — 근데 이 체크가 걸려있어서
// 대시보드 열 때마다(링크를 안 넣어놓은 상태) 인스타 캡션에 댓글 CTA가 통째로
// 사라져 보였다("인스타쪽 왜 댓글달면 링크 준다는거 없어졌어?" 반복 지적). CTA는
// hasCommentDm이 켜진 플랫폼이면 링크 입력 여부와 무관하게 항상 붙는다.
function _buildCtaBlock(hasCommentDm) {{
  if (!hasCommentDm) {{
    return {{text: "🔗 상품 링크는 프로필에서 확인해주세요!", disclosure: COUPANG_DISCLOSURE}};
  }}
  // WHY "이라고"(받침 있는 조사) 고정(2026-08-01 오타 수정): COMMENT_KEYWORD가
  // 항상 "쿠팡"(받침 ㅇ으로 끝남)으로 고정된 이후로 "라고"를 쓰면 "쿠팡라고"처럼
  // 문법이 틀린다 — 키워드가 이 정책 밖에서 바뀔 일이 없으므로 조사를 하드코딩한다.
  const cta = `💬 댓글에 "${{COMMENT_KEYWORD}}"이라고 치시면 제품 목록으로 이동할 수 있는 링크 바로 전송해드릴게요!`;
  return {{text: cta, disclosure: COUPANG_DISCLOSURE}};
}}

function applyProductLinks() {{
  document.querySelectorAll(".caption-box").forEach(box => {{
    const card = box.closest(".platform-card");
    const noCaptionLink = card.dataset.noCaptionLink === "1";
    const hasNaverButton = card.dataset.naverButton === "1";
    const hasCommentDm = card.dataset.commentDm === "1";
    const linkInComment = card.dataset.linkInComment === "1";
    // WHY suppressProductBlock(2026-07-31): 유튜브 쇼츠는 구독자 500명 조건을 채우기
    // 전까지 설명란 링크가 아예 클릭이 안 돼서 판매 관련 문구를 넣어봤자 반감만 산다는
    // 판단 — 이 조건을 넘기기 전까지는 링크/고지문구 자체를 아예 안 붙인다(팔로우 요청만
    // 정적 캡션에 남긴다). 500명 넘으면 이 플래그를 caption JSON에서 지울 것.
    // WHY linkInComment는 "약속 문구"만 빼고 고지문구는 남기는지(2026-08-04
    // 재수정, "맞는말이야? 본문에는 쿠팡 파트너스 관련 코멘트 없애도돼?" 지적으로
    // 바로잡음): 처음엔 "댓글에 남겨둘게요"라는 확정된 약속 문구와 쿠팡 파트너스
    // 고지문구를 한 묶음으로 보고 linkInComment면 둘 다(suppressBlock과 동일하게)
    // 없앴는데, 공정위 "추천·보증 등에 관한 표시·광고 심사지침" 기준으로 제휴
    // 고지는 게시물 본문(그것도 추가 행동 없이 보이는 위치)에 있어야지 댓글에만
    // 있으면 인정 안 된다 — 지워도 되는 건 "댓글에 넣으려면 넣고 안넣으려면
    // 안넣고" 약속 문구뿐, 고지문구는 본문에 남겨야 한다. linkInComment는
    // blockText(상품명/링크 나열, 애초에 본문에 넣을 링크가 없음)만 비우고
    // disclosure는 그대로 살린다.
    // WHY linkInComment는 고지문구를 아래(AUTO_BOTTOM)에는 안 넣고 위에만
    // 넣는지(2026-08-04, "페이스북은 고지문구 맨위에 하나만 있으면돼 어차피
    // 링크가 본문에 있지도 않은데"): 다른 플랫폼이 아래에도 고지문+상품 링크를
    // 반복하는 건 "끝까지 읽은 사람도 다시 링크를 볼 수 있어야 한다"는 요구
    // 때문인데, linkInComment 플랫폼은 애초에 본문에 링크 자체가 없어서(실제
    // 링크는 댓글에만 있음) 아래에 다시 반복할 대상이 없다 — 고지문 하나만
    // 아래에도 중복해서 넣을 이유가 없다.
    const suppressBlock = card.dataset.suppressProductBlock === "1";
    // WHY hasNaverButton으로 고지문을 다시 나누는지(2026-08-09, "네이버 클립에다가
    // 쿠팡 파트너스 올려놨네... 링크는 영상에서 넣는다고" — 네이버 클립은 상품을
    // 캡션이 아니라 클립 앱 자체의 상품 태그 기능으로 붙이므로 본문엔 광고 고지
    // 코멘트만 있으면 되는 linkInComment 케이스인데, 위 라인은 linkInComment면
    // 무조건 COUPANG_DISCLOSURE를 썼다 — 네이버 클립(hasNaverButton)엔 네이버
    // 고지문구가 붙어야 한다.
    const result = suppressBlock ? null : (linkInComment ? {{text: "", disclosure: hasNaverButton ? NAVER_DISCLOSURE : COUPANG_DISCLOSURE}} : (noCaptionLink ? _buildCtaBlock(hasCommentDm) : _buildLinkBlock(hasNaverButton)));
    const stripped = _stripAutoLinks(box.value);
    if (!result) {{
      box.value = stripped;
      return;
    }}
    let blockText = result.text;
    // WHY profile-note(2026-07-31): 유튜브 쇼츠 설명란 링크는 클릭이 안 된다는
    // 피드백 — 그렇다고 링크 텍스트 자체를 빼는 게 아니라(요청: "링크도 있지만
    // 프로필도 안내해주는 걸로"), 링크는 그대로 두고 프로필 확인 안내를 덧붙인다.
    if (card.dataset.profileNote === "1") {{
      blockText += "\\n\\n🔗 링크가 눌리지 않으면 채널 프로필에서 확인해주세요";
    }}
    // WHY linkInComment만 위쪽 고지문을 생략하는지(2026-08-04, "아니 맨위도
    // 아니다 걍 맨 아래 하나만 남겨줘" — 페이스북·쓰레드는 본문이 짧아서 맨
    // 아래 한 곳이면 충분하다는 취지였을 뿐, 다른 플랫폼(특히 블로그처럼 긴
    // 캡션)까지 위쪽 고지를 빼라는 뜻이 아니었다 — "이건 굳이 링크 안 걸리는
    // 페이스북·쓰레드 얘기지 블로그는 상단에 있어야 한다며?" 재지적으로
    // linkInComment 하나에만 걸리게 명시적으로 분기): 다른 플랫폼(네이버
    // 블로그·티스토리 등)은 공정위 지침상 "게시물 첫 부분"에 있어야 해서
    // 여전히 위/아래 둘 다 넣는다 — linkInComment만 예외로 위쪽을 생략한다.
    // ⚠️ WHY 네이버 클립(hasNaverButton)은 "[광고]+고지문"을 맨 아래 한
    // 덩어리로 합치는지(2026-08-10 재수정 — 한 번 맨 위로 합쳤다가 "클립이나
    // 숏츠나 맨 아래에 들어오게 하자... 상단에 들어올 필요가 없어보여 어차피
    // 바로 눈에 들어올만큼 짧은 글인데" 지적으로 다시 뒤집음): 네이버 클립
    // 캡션은 200~300자 수준으로 짧아서 스크롤 없이 전체가 한눈에 보이므로,
    // 공정위 "추가 행동 없이 보이는 위치" 요건은 위/아래 어느 쪽이든
    // 동일하게 충족된다 — 그럴 거면 본문 맨 위(사용자 정적 캡션 바로 앞)에
    // 끼어드는 것보다 맨 아래가 자연스럽다. "[광고]" 표시와 고지 문장은
    // 여전히 한 덩어리로 유지(따로 떨어지면 안 됨).
    let withTop;
    if (linkInComment && hasNaverButton) {{
      withTop = stripped;
    }} else if (linkInComment) {{
      withTop = stripped;
    }} else {{
      const topWrapped = AUTO_LINKS_START + result.disclosure + (blockText ? "\\n\\n" + blockText : "") + AUTO_LINKS_END;
      const firstBreak = stripped.indexOf("\\n");
      withTop = firstBreak === -1
        ? stripped + "\\n\\n" + topWrapped
        : stripped.slice(0, firstBreak) + "\\n\\n" + topWrapped + stripped.slice(firstBreak);
    }}
    // WHY 아래쪽도 고지문뿐 아니라 blockText(상품 링크/목록)까지 통째로
    // 반복하는지(2026-08-03, "맨밑에 링크없잖아? 링크 넣어라고... 쿠팡 뿐만
    // 아니라 네이버일때도 맨아래에도 상품 목록이랑 문구 띄워야한다고"): 처음엔
    // 고지문만 아래에 붙였는데, 실제 요구사항은 "끝까지 읽고 안 올려도 구매
    // 링크를 다시 볼 수 있어야 한다"였다 — 고지문+상품 링크(쿠팡) 또는
    // 고지문+상품 목록(네이버, hasNaverButton 분기도 같은 blockText 경로를
    // 타므로 이 한 줄로 둘 다 커버됨) 전체를 아래에도 그대로 반복한다.
    // WHY blockText가 빈 문자열일 때 줄바꿈을 안 붙이는지(linkInComment): 위
    // result 분기에서 linkInComment는 blockText가 항상 "" — 무조건 줄바꿈을
    // 이어붙이면 고지문 뒤에 내용 없는 빈 줄만 남는다.
    // WHY 네이버 클립만 "[광고] " 접두어를 붙이는지: 이 플랫폼은 광고 표시와
    // 고지 문장이 한 덩어리로(따로 떨어지지 않게) 나와야 한다는 요건이 있어서
    // (위 withTop 분기 WHY 참고) — 다른 플랫폼은 고지문만 그대로 둔다.
    const bottomDisclosure = (linkInComment && hasNaverButton) ? ("[광고] " + result.disclosure) : result.disclosure;
    const bottomWrapped = AUTO_BOTTOM_START + bottomDisclosure + (blockText ? "\\n\\n" + blockText : "") + AUTO_BOTTOM_END;
    box.value = withTop + "\\n\\n" + bottomWrapped;
  }});
}}

(async () => {{
  // WHY global_product_links도 같이 조회하는지(2026-08-09, "메인에서 넣었는데
  // 대시보드들어오니 또 반영이안되어있네" — 메인 페이지 미등록 링크 위젯은
  // global_product_links(상품명 기준, topic 무관)에 저장하는데 이 대시보드는
  // product_links(topic별로 따로)만 읽어서 서로 완전히 분리된 두 시스템이었다):
  // 이 topic에서 아직 한 번도 등록 안 한 상품이라도, 다른 topic에서(또는 메인
  // 페이지에서) 이미 등록된 같은 상품명의 전역 링크가 있으면 그걸 폴백으로
  // 채운다 — 우선순위는 topic 전용(product_links) > 전역(global_product_links).
  const [{{ data: dbLinks }}, {{ data: globalLinks }}] = await Promise.all([
    sb.from("product_links").select("market,product,url").eq("topic", TOPIC_NAME),
    sb.from("global_product_links").select("market,product,url"),
  ]);
  const globalLinkMap = new Map((globalLinks || []).map(r => [r.market + "_" + r.product, r.url]));
  const dbLinkMap = new Map((dbLinks || []).map(r => [r.market + "_" + r.product, r.url]));

  document.querySelectorAll(".product-link-input").forEach(inp => {{
    const row = inp.closest(".dock-product-row");
    const linkKey = inp.dataset.market + "_" + inp.dataset.product;
    const storageKey = LINK_STORAGE_PREFIX + linkKey;
    const saved = localStorage.getItem(storageKey) || dbLinkMap.get(linkKey) || globalLinkMap.get(linkKey) || "";
    if (saved) {{
      inp.value = saved;
      row.classList.add("linked");
      // WHY 기존 저장값도 로드 시 검증하는지(2026-08-08): 검증 로직 도입 전에
      // 이미 검색/목록 링크로 잘못 저장된 항목들이 있어서, 새로 입력할 때만
      // 막으면 그 기존 값들은 계속 숨어있는다 — 열자마자 바로 눈에 띄게 한다.
      if (inp.dataset.market === "coupang" && !/^https:\/\/link\.coupang\.com\/a\//.test(saved)) {{
        const err = row.querySelector('.link-error[data-for="coupang"]');
        if (err) {{
          err.textContent = "⚠️ 저장된 링크가 쿠팡 검색/목록 링크예요 — 파트너스 변환 링크로 다시 넣어주세요";
          err.classList.add("show");
        }}
      }}
    }}
    inp.addEventListener("input", () => {{
      const val = inp.value.trim();
      // WHY 쿠팡만 형식 검증하는지(2026-08-08, "쿠팡 목록 검색 링크가 파트너스
      // 변환 없이 그대로 들어가있는게 있다"): coupang.com/np/search 같은 일반
      // 검색·목록 링크는 파트너스 수수료가 안 붙는 무효 링크인데, 실수로
      // "🔎 복사"한 검색 링크를 그대로 여기 붙여넣는 경우가 있었다 — 실제
      // 파트너스 변환 링크(link.coupang.com/a/...)만 통과시킨다. 네이버는
      // 브랜드커넥트 링크 형식이 다양해서(리다이렉트·단축 등) 아직 강제하지 않음.
      if (inp.dataset.market === "coupang" && val && !/^https:\/\/link\.coupang\.com\/a\//.test(val)) {{
        inp.value = "";
        const err = row.querySelector('.link-error[data-for="coupang"]');
        if (err) {{
          err.textContent = "⚠️ 쿠팡 검색/목록 링크는 안 돼요 — 파트너스 변환 링크(link.coupang.com/a/...)를 넣어주세요";
          err.classList.add("show");
        }}
        localStorage.removeItem(storageKey);
        row.classList.remove("linked");
        sb.from("product_links").delete().eq("topic", TOPIC_NAME).eq("market", inp.dataset.market).eq("product", inp.dataset.product);
        applyProductLinks();
        return;
      }}
      const err = row.querySelector('.link-error[data-for="' + inp.dataset.market + '"]');
      if (err) err.classList.remove("show");
      if (val) {{
        localStorage.setItem(storageKey, val);
        row.classList.add("linked");
        sb.from("product_links").upsert({{ topic: TOPIC_NAME, market: inp.dataset.market, product: inp.dataset.product, url: val }});
      }} else {{
        localStorage.removeItem(storageKey);
        row.classList.remove("linked");
        sb.from("product_links").delete().eq("topic", TOPIC_NAME).eq("market", inp.dataset.market).eq("product", inp.dataset.product);
      }}
      applyProductLinks();
    }});
    inp.addEventListener("keydown", e => {{
      if (e.key === "Enter") {{ row.classList.remove("row-expanded"); inp.blur(); }}
    }});
  }});

  applyProductLinks();
}})();

// WHY JSON으로 저장(2026-08-02): 예전엔 이 키에 그냥 "1"만 넣었는데, 이러면
// 나중에 CSV로 내보낼 때 topic/플랫폼명을 키 문자열에서 역으로 파싱해야 하고
// topic 이름 자체에 "_"가 들어있어서(예: 눈_1) 안전하게 쪼갤 방법이 없다 — 값
// 안에 topic/platform/게시시각을 자체적으로 담아서 내보내기가 파싱 없이 바로
// 되게 한다(포스팅 스케줄 로그 — index.html의 CSV 내보내기/가져오기 참고).
const STORAGE_PREFIX = "hs_done_{topic}_";
(async () => {{
  const {{ data: dbPosted }} = await sb.from("posting_log").select("platform").eq("topic", TOPIC_NAME);
  const dbPostedSet = new Set((dbPosted || []).map(r => r.platform));

  document.querySelectorAll(".done-toggle").forEach(cb => {{
    const storageKey = STORAGE_PREFIX + cb.dataset.key;
    const card = cb.closest(".platform-card");
    if (localStorage.getItem(storageKey) || dbPostedSet.has(cb.dataset.name)) {{
      cb.checked = true;
      card.classList.add("is-done");
    }}
    cb.addEventListener("change", () => {{
      if (cb.checked) {{
        const postedAt = new Date().toISOString();
        const record = {{ topic: TOPIC_NAME, platform: cb.dataset.name, postedAt }};
        localStorage.setItem(storageKey, JSON.stringify(record));
        card.classList.add("is-done");
        sb.from("posting_log").upsert({{ topic: TOPIC_NAME, platform: cb.dataset.name, posted_at: postedAt }});
      }} else {{
        localStorage.removeItem(storageKey);
        card.classList.remove("is-done");
        sb.from("posting_log").delete().eq("topic", TOPIC_NAME).eq("platform", cb.dataset.name);
      }}
    }});
  }});
}})();
</script>
</body>
</html>
"""

SECTION_TEMPLATE = """
<section class="platform-section">
  <h2>{section_title}</h2>
  <div class="grid">{cards}</div>
</section>
"""


def _prefixed(name: str, topic: str) -> str:
    """WHY(2026-07-31): card_news.py가 이제 파일명에 topic 접두어를 직접 붙이므로,
    다운로드 파일명을 만들 때 이미 붙어있는 접두어를 또 붙이면 중복된다
    (예: "60대주의음식_1_60대주의음식_1_00_표지.jpg") — 이미 있으면 그대로 두고,
    없는(접두어 없는 예전 topic) 경우에만 붙인다."""
    return name if name.startswith(topic + "_") else f"{topic}_{name}"


def _asset_link(platform_type: str, topic: str, cover_name: str | None) -> str:
    # WHY video 타입엔 안내문 자체가 없는지(2026-08-05, "회색박스 텍스트
    # 필요없잖아? 이제 어차피 영상을 깃허브에 올려놓지를 않는데?"): mp4가 git에
    # 없어서 이 텍스트가 가리키던 다운로드/재생은 애초에 불가능했고, 로컬에서
    # 직접 작업하는 사람에게는 그 안내 자체가 불필요한 잡음이었다.
    topic_attr = _esc(topic)
    if platform_type == "cards":
        return '<a class="asset-link" href="#card-gallery">🖼 위 카드뉴스 미리보기로 이동 ↑</a>'
    if not cover_name:
        return ""
    return (f'<a class="asset-link" href="card_news/{quote(cover_name)}" '
            f'download="{_prefixed(cover_name, topic_attr)}">🖼 표지 이미지 다운로드 (선택)</a>')


def _load_product_links() -> dict[str, str]:
    """WHY(2026-08-02, "상품도 너한테 던져야겠다 이거 로컬스토리지 불안해서"):
    상품별 쿠팡 파트너스 링크를 브라우저 localStorage 대신 git 추적되는
    output/product_links.json(상품명 → 링크)에서 관리한다 — completed_topics.json/
    youtube_uploaded.json과 같은 패턴. 사용자가 채팅으로 상품+링크를 알려주면
    Claude Code가 이 파일에 직접 추가한다. 같은 상품이 여러 topic에서 반복
    등장해도 한 번만 등록해두면 이후 생성되는 모든 대시보드에 자동으로 채워진다."""
    path = Path(__file__).resolve().parent.parent / "output" / "product_links.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _load_naver_product_links() -> dict[str, str]:
    """_load_product_links()와 같은 패턴, 네이버 커넥트용(2026-08-04, "네이버 커넥트도
    주소를 그냥 너가 알고있게 해야겠다 쿠팡처럼"). 이미 링크를 확보한 상품은 이 파일에서
    찾아 고정 링크로 바로 보여준다 — 쿠팡과 동일하게 동일 상품명이면 링크도 재사용.

    ⚠️ 검색 링크는 별도로 여전히 필요하다(2026-08-04, "네이버 커넥트 검색도 전에
    있었는데 한번 뺐었거든... 검색해서 대응을 해야하는부분이라"): 2026-08-01엔
    "브랜드커넥트 검색 입력창"을 매번 검색해서 링크를 만들어야 해서 번거롭다고 없앴는데,
    이 파일에 아직 없는 신규 상품은 결국 사용자가 직접 검색해서 브랜드커넥트 링크를
    새로 만들어야 한다 — 이 파일은 "이미 만들어둔 링크 재사용" 캐시일 뿐, 검색 자체를
    대체하지 않는다. `_dock_products()`가 쿠팡 검색 버튼과 동일한 패턴(🟢 네이버 검색 +
    복사)을 항상 같이 렌더링하고, 이 파일에 링크가 있으면 그 아래 "네이버 커넥트로
    이동" 링크를 추가로 보여준다."""
    path = Path(__file__).resolve().parent.parent / "output" / "naver_product_links.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _dock_products(
    products: list[str],
    product_links: dict[str, str] | None = None,
    naver_links: dict[str, str] | None = None,
    naver_brandconnect_id: str | None = None,
) -> str:
    if not products:
        return ""
    product_links = product_links or {}
    naver_links = naver_links or {}
    rows = ""
    for idx, name in enumerate(products):
        coupang_url = f"https://www.coupang.com/np/search?component=&q={quote(name)}&channel=user"
        # WHY search.shopping.naver.com이 아니라 brandconnect.naver.com인지
        # (2026-08-07, "네이버 브랜드커넥트 연동 링크는 이런 형태로 들어가야하는데
        # 지금 네이버 쇼핑쪽 링크를 던지고 있네" — 실제 사용 링크 예시로 발견):
        # 일반 쇼핑 검색 결과가 아니라 브랜드커넥트 자체 상품 검색 페이지로 바로
        # 가야 그 자리에서 커넥트 링크를 만들 수 있다. ID는 data/affiliate_accounts.json의
        # naver_brandconnect_id 재사용(쿠팡처럼 topic마다 다른 게 아니라 계정
        # 고정값). quote_plus인 이유: 네이버가 실제 쓰는 URL이 공백을 %20이 아니라
        # +로 인코딩해서(실측 예시 URL 그대로) 맞춰준다.
        naver_search_url = (
            f"https://brandconnect.naver.com/{naver_brandconnect_id}/affiliate/products/search"
            f"?query={quote_plus(name)}&tab=product"
            if naver_brandconnect_id
            else f"https://search.shopping.naver.com/search/all?query={quote(name)}"
        )
        link = product_links.get(name, "")
        naver_link = naver_links.get(name, "")
        naver_goto = (
            f'<a href="{_esc(naver_link)}" target="_blank" rel="noopener">🟢 네이버 커넥트로 이동</a>'
            if naver_link else ""
        )
        rows += DOCK_PRODUCT_ROW_TEMPLATE.format(
            name=_esc(name), coupang_url=coupang_url, name_attr=_esc(name), idx=idx,
            link_value=_esc(link), row_class=" linked" if (link or naver_link) else "",
            naver_link_value=_esc(naver_link), naver_goto=naver_goto,
            naver_search_url=naver_search_url,
        )
    # WHY 네이버 입력란이 캡션 자동삽입(_buildLinkBlock)엔 안 쓰이는지(2026-08-04):
    # network:"naver" 플랫폼(네이버 블로그·클립) 캡션은 여전히 상품명만 나열하는
    # 브랜드커넥트 방식 그대로다(쿠팡 링크를 캡션에 넣으면 저품질 판정 이슈가 있어서,
    # 위 "네이버 블로그, 다시 브랜드커넥트로" 절 참고) — 이 네이버 입력란은 캡션에
    # 자동으로 들어가지 않고, 사용자가 그 링크를 직접 확인·복사해서 다른 곳(실제 블로그
    # 포스팅 등)에 쓰기 위한 위젯 전용 표시다.
    # WHY id 없이 class만 쓰는지(2026-08-02): 이 버튼을 페이지 맨 아래에도 복제해서
    # 넣으면서(`_product_links_bottom_section`) id가 중복되면 안 돼 — class 기준
    # querySelectorAll로 바인딩하도록 JS를 바꿔서 이제 id가 필요 없다.
    return (
        '<div class="dock-section"><h4>상품 링크</h4>'
        '<button type="button" class="copy-comment-links">'
        '💬 댓글용 링크 텍스트 복사</button>'
        f'{rows}'
        '<p class="dock-hint">쿠팡 링크를 붙여넣으면 아래 각 플랫폼 카드 캡션에 자동 반영돼요.</p>'
        '</div>'
    )


def _product_links_bottom_section(
    products: list[str],
    product_links: dict[str, str] | None = None,
    naver_links: dict[str, str] | None = None,
) -> str:
    """WHY(2026-08-02, "쿠팡 링크 맨 아래에도 추가해달라고 했는데 언제까지
    안해줄거냐?"): 상품 링크는 원래 화면 오른쪽에 `position: fixed`로 항상 떠
    있는 덕 패널(`_dock_products`)에만 있었다 — 위 "열기" 버튼처럼 페이지
    맨 아래에도 눈에 보이는 사본을 하나 더 둔다.

    ⚠️ 입력창(`<input class="product-link-input">`)까지 통째로 복제하지는
    않는다 — 링크 편집 상태의 유일한 원본(source of truth)은 상단 덕 패널
    뿐이어야 한다. 입력창을 두 벌 만들면 위에서 수정한 값이 아래엔 안
    반영되는 등 두 입력이 서로 안 맞는 상태가 생길 수 있어서, 여기는 읽기
    전용(검색 링크 + 이미 등록된 링크가 있으면 그 링크)만 보여주고 편집은
    항상 위쪽 패널에서 하게 한다. "댓글용 링크 텍스트 복사" 버튼은 상태가
    없는(클릭하면 그 순간 상단 입력값을 읽어서 복사하는) 동작이라 그대로
    복제해도 안전하다."""
    if not products:
        return ""
    product_links = product_links or {}
    naver_links = naver_links or {}
    rows = ""
    for name in products:
        coupang_url = f"https://www.coupang.com/np/search?component=&q={quote(name)}&channel=user"
        link = product_links.get(name, "")
        naver_link = naver_links.get(name, "")
        link_html = (
            f'<a href="{_esc(link)}" target="_blank" rel="noopener">🔗 등록된 링크로 이동</a>'
            if link else '<span class="bottom-product-nolink">등록된 링크 없음</span>'
        )
        naver_html = (
            f'<a href="{_esc(naver_link)}" target="_blank" rel="noopener">🟢 네이버 커넥트로 이동</a>'
            if naver_link else '<span class="bottom-product-nolink">네이버 링크 없음</span>'
        )
        rows += (
            '<div class="bottom-product-row">'
            f'<span class="bottom-product-name">{_esc(name)}</span>'
            f'<a href="{coupang_url}" target="_blank" rel="noopener">🛒 쿠팡 검색</a>'
            f'{link_html}'
            f'{naver_html}'
            '</div>'
        )
    return (
        '<section class="bottom-product-links">'
        '<h2>상품 링크</h2>'
        '<button type="button" class="copy-comment-links">💬 댓글용 링크 텍스트 복사</button>'
        f'{rows}'
        '<p class="dock-hint">링크 수정은 위쪽 "빠른 도구" 패널의 상품 링크에서 해주세요.</p>'
        '</section>'
    )


def _write_all_products(output_root: Path, data_root: Path) -> None:
    """WHY(2026-08-08, "제품 링크 안 되어있는 목록을 메인에다가 따로 빼놓고
    거기다 넣고 저장하면 글로벌로 반영되게"): index.html이 "아직 쿠팡/네이버
    링크가 없는 상품"을 계산하려면 "지금 topic들이 실제로 쓰는 상품명 전체
    목록"이 먼저 필요하다 — Supabase `topics` 테이블엔 상품명이 없고(topic/
    title/url/thumbnail/ad_tag/tracks뿐), 로컬 platform_captions.json에만
    있다. `global_product_links`(Supabase, market·product·url)처럼 자주
    바뀌는 "상태"가 아니라 "지금 뭐가 있는지" 정적 목록이라 topics.json과
    같은 패턴(git 추적 정적 파일, 매 generate() 호출마다 자동 갱신)으로
    둔다 — 굳이 Supabase 테이블·스키마 변경 없이 기존 하이브리드 구조 그대로
    확장."""
    products: set[str] = set()
    for fp in sorted(data_root.glob("*/ko/platform_captions.json")):
        try:
            spec = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        products.update(spec.get("products", []))
    # WHY 언어 하위 폴더 없는(2단계 아닌 flat) topic도 포함하는지: 위 glob은
    # "<topic>/ko/platform_captions.json"만 잡아서, 다국어 확장 이전에 만든
    # flat topic("<topic>/platform_captions.json")의 상품명이 누락된다.
    for fp in sorted(data_root.glob("*/platform_captions.json")):
        try:
            spec = json.loads(fp.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        products.update(spec.get("products", []))
    (output_root / "all_products.json").write_text(
        json.dumps(sorted(products), ensure_ascii=False, indent=2)
    )


def _update_topics_index(out_path: str):
    """WHY(2026-07-31): 매번 output/<topic>/dashboard.html 전체 경로를 외워서 들어가야
    했다("루트로 들어가면 안되나?") — output/ 밑의 모든 대시보드를 스캔해서
    output/topics.json을 갱신하면, 루트 index.html이 이걸 읽어 목록을 보여줄 수 있다.

    WHY 1단계+2단계 glob 둘 다(2026-08-03, 글로벌 확장 — data/output <topic>/<lang>/
    중첩 구조 도입): 기존 topic은 output/<topic>/dashboard.html(1단계), 언어별로
    나뉜 새 글로벌 topic은 output/<topic>/<lang>/dashboard.html(2단계)이다 — 2단계
    항목의 topic 식별자는 "<topic>/<lang>"로 조합해서 데이터 폴더 매칭·표시에 쓴다."""
    # WHY 프로젝트 루트 기준 고정 경로(2026-08-03): out_dir.parent로 output_root를
    # 추론하던 방식은 out_path가 정확히 output/<topic>/dashboard.html(1단계) 깊이일
    # 때만 맞았다 — 중첩 topic(output/<topic>/<lang>/dashboard.html, 2단계)에서는
    # out_dir.parent가 output/<topic>/이 되어버려 잘못된 루트를 잡는다. 프로젝트
    # 루트 기준 고정 경로로 output_root를 직접 계산하면 깊이와 무관하게 항상 맞는다.
    output_root = Path(__file__).resolve().parent.parent / "output"
    data_root = output_root.parent / "data"
    topics = []
    # WHY 중첩 topic의 통합 허브 페이지(output/<topic>/dashboard.html, 아래
    # _generate_unified_dashboard 참고)를 별도 flat topic으로 잘못 집계하지
    # 않는지(2026-08-04): 통합 페이지가 언어별 dashboard.html과 "같은 파일명
    # (dashboard.html)"을 쓰기로 하면서, 얕은 glob(`*/dashboard.html`)이 통합
    # 허브 페이지 자체도 걸어버려서 "가슴쓰림_1"이 "가슴쓰림_1/en"·"가슴쓰림_1/ja"와
    # 별개로 또 하나의 topic 행으로 중복 등록되는 문제가 생긴다 — 언어별 하위
    # dashboard.html이 이미 존재하는 base topic은 얕은 glob 결과에서 제외한다.
    nested_dash_paths = sorted(output_root.glob("*/*/dashboard.html"))
    nested_bases = {p.parent.parent.name for p in nested_dash_paths}
    flat_dash_paths = [p for p in sorted(output_root.glob("*/dashboard.html")) if p.parent.name not in nested_bases]
    dash_paths = flat_dash_paths + nested_dash_paths
    for dash in dash_paths:
        rel = dash.parent.relative_to(output_root)
        topic = "/".join(rel.parts)  # flat: "가슴쓰림_1", 중첩: "가슴쓰림_1/en"
        title = topic
        # WHY ad_tag도 여기서 같이 읽는지(2026-08-06, "플래그 세워서 육안으로
        # 신규 포맷이라는거 구분 가능하게"): 영상 우상단 광고 태그 오버레이가
        # 적용된 topic인지를 목록에서 바로 구분할 수 있어야 한다.
        ad_tag_applied = False
        # WHY season도 여기서 같이 읽는지(2026-08-12, "냉방병 온열질환 이런것도
        # 계절/시즌으로 넣으면되겠다" — 계절/환경 자체가 원인인 topic만 대상,
        # 땀띠·자외선·식중독처럼 여름에 흔하지만 원인이 계절 자체는 아닌
        # topic은 제외하기로 확정): platform_captions.json의 "season"
        # 필드(문자열 배열, 예: ["여름"]) 그대로 실어나른다 — 없으면 빈 배열.
        season: list[str] = []
        # WHY tracks를 저장 필드 대신 여기서 파생하는지(2026-08-07, "쇼츠 부문 /
        # 카드뉴스 부문" 목록 분리): 수동 플래그는 언젠가 빠뜨리거나 실제
        # 콘텐츠와 어긋나는 사고로 이어진다(이 프로젝트에서 network/
        # suppress_product_block 등으로 반복된 패턴) — platforms에 video 타입이
        # 있으면 "shorts", cards/text 타입이 있으면 "card_news"를 각각 독립적으로
        # 추가한다. WHY 리스트(둘 다 가능)인지(2026-08-07, "기존에 이미
        # 생성되었던 카드뉴스 형태 애들도 아예 새로 만든 탭으로 넣어 전부다"):
        # 처음엔 video 있으면 무조건 "숏츠"로만 분류했는데, 영상+카드뉴스를 같이
        # 가진 기존 topic도 카드뉴스 탭에서 찾을 수 있어야 한다 — 한 topic이
        # 두 탭에 동시에 나타날 수 있다(배타적 아님).
        tracks: list[str] = []
        caption_path = data_root / rel / "platform_captions.json"
        if caption_path.exists():
            try:
                caption_spec = json.loads(caption_path.read_text())
                title = caption_spec.get("title", topic)
                ad_tag_applied = bool(caption_spec.get("ad_tag"))
                season = caption_spec.get("season", []) or []
                platform_types = {p.get("type") for p in caption_spec.get("platforms", [])}
                if "video" in platform_types:
                    tracks.append("shorts")
                # WHY 페이스북 제외(2026-08-08): type이 "text"라 카드뉴스
                # 판별에 같이 걸렸는데, 실제로는 숏츠 영상을 올리는 플랫폼이라
                # (CLAUDE.md "영상 필요 플랫폼" 목록에 페이스북 포함) 카드뉴스
                # 이미지와 무관하다 — 카드뉴스 탭 판별에서 페이스북은 빼고 본다.
                card_news_types = {
                    p.get("type") for p in caption_spec.get("platforms", [])
                    if p.get("name") != "페이스북"
                }
                if card_news_types & {"cards", "text"}:
                    tracks.append("card_news")
            except (json.JSONDecodeError, OSError):
                pass
        # WHY(2026-08-01): 목록에서 폴더명만 보고는 어떤 topic인지 한눈에 안 들어온다는
        # 피드백 — 표지 카드가 있으면 썸네일로 같이 보여준다. WHY glob(2026-08-03): topic
        # 접두어가 없는 중첩 topic("00_표지.jpg")과 있는 flat topic(과거 관례,
        # "<topic>_00_표지.jpg") 둘 다 와일드카드로 매칭한다.
        cover_path = next((dash.parent / "card_news").glob("*00_표지.jpg"), None)
        thumbnail = f"output/{quote(topic)}/card_news/{quote(cover_path.name)}" if cover_path else None
        topics.append({
            "topic": topic, "title": title, "url": f"output/{quote(topic)}/dashboard.html",
            "thumbnail": thumbnail, "ad_tag": ad_tag_applied, "tracks": tracks,
            "season": season,
        })
    topics.sort(key=lambda t: t["topic"])
    (output_root / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2))
    _write_all_products(output_root, data_root)

    # WHY 여기서 통합 대시보드(output/<topic>/dashboard.html)도 같이 만드는지
    # (2026-08-03 최초 도입, 2026-08-04 전면 개편 — 아래 _generate_unified_dashboard
    # WHY 참고): 이 함수는 이미 output/ 전체를 스캔해서 base-topic별 언어 목록을
    # 알고 있으므로, topics.json 갱신 시점에 같이 재생성하면 별도 호출 지점을
    # 안 늘려도 된다. 다국어 topic(언어 서브폴더가 있는 topic)만 대상 — 단일
    # 언어 topic은 이미 그 자체가 output/<topic>/dashboard.html이라 만들 게 없음.
    for base in nested_bases:
        _generate_unified_dashboard(base, output_root, data_root)


# WHY 이 딕셔너리를 여기 두는지: data/global_channels.json과 값 형식이 다르다(그
# 파일은 code->메타 정보 dict이고 여기는 순서가 있는 표시용 라벨) — 이 페이지
# 전용이라 별도로 관리해도 두 파일이 어긋날 위험이 없다(코드만 겹치면 됨, 코드
# 자체의 출처는 typecast_voices_global.json이 정본).
GLOBAL_LANG_LABELS = {
    "en": "영어 English", "ja": "일본어 日本語", "zh-TW": "대만어 繁體中文",
    "es": "스페인어 Español", "pt": "포르투갈어 Português", "fr": "프랑스어 Français",
    "de": "독일어 Deutsch", "ru": "러시아어 Русский", "vi": "베트남어 Tiếng Việt",
    "ar": "아랍어 العربية", "bn": "벵골어 বাংলা", "tr": "터키어 Türkçe",
    "th": "태국어 ไทย", "id": "인도네시아어 Indonesia", "hi": "힌디어 हिन्दी",
}

# WHY 통합 대시보드를 별도 파일이 아니라 "언어별 dashboard.html을 그대로 iframe으로
# 보여주는 페이지"로 만드는지(2026-08-04, "글로벌도 합치자 한 페이지에 같이
# 있고 포맷도 기존과 동일하게 가야겠다... 기존에 관리하던 폼이랑 동일하게 가져가면
# 딱이네" — ko/글로벌을 따로 관리하던 두 페이지·두 버튼(한국/Global)을 없애고
# 하나로 합쳐달라는 요청): CARD_TEMPLATE 기반의 완성된 카드(캡션 편집·상품
# 링크 dock·고지문구 자동삽입·완료 체크 등)를 언어마다 다시 구현하면 두 벌을
# 유지보수해야 하고 필연적으로 기능이 어긋난다 — 이미 생성된 ko dashboard.html을
# 그대로 iframe에 넣으면 "완전히 동일한 폼"이 100% 보장되고, 앞으로
# CARD_TEMPLATE/JS를 고치면 ko 섹션에 자동으로 반영된다.
# ⚠️ WHY 탭 전환 UI를 아예 없앴는지(2026-08-05, "UI에 찌꺼기가 좀 많이남아있다
# ... 이제 항목도 줄었으니 글로벌도 버튼눌러서 이동해서 인스타 누르지말고 걍
# 하나로 병합해도될듯" → "1번은 한국이든 글로벌이든 전부 한 탭으로 가라고"로
# 확정): 언어마다 탭을 눌러 전환하던 방식을 버리고, 한국어(iframe)와 글로벌
# 언어들(가벼운 카드, 아래 _generate_unified_dashboard 참고)을 한 페이지에
# 전부 세로로 나열한다 — 스크롤 한 번으로 모든 언어를 다 볼 수 있어서 언어별로
# 탭을 오갈 필요가 없다.
UNIFIED_PAGE_TEMPLATE = """<!doctype html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — 업로드 대시보드</title>
<style>
  :root {{
    --bg-top: #fdf9f5; --bg-bottom: #f6ede6;
    --ink: #2b231f; --ink-soft: #8b7c6e;
    --accent: #c84a62; --accent-deep: #a3344a; --accent-soft: #fadee3;
    --panel: #fffdfa; --rule: #e9ddd0;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", -apple-system, sans-serif;
    background: linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
    color: var(--ink);
  }}
  header {{ padding: 32px 24px 8px; text-align: center; }}
  header h1 {{ margin: 0 0 6px; font-size: 22px; }}
  header p {{ margin: 0; color: var(--ink-soft); font-size: 13px; }}
  .back {{ display: inline-block; margin: 18px 0 0 20px; color: var(--ink-soft); font-size: 13px; text-decoration: none; }}
  /* WHY main이 row-wrap 플렉스인지(2026-08-05, "글로벌도 영상 쪽에 한국이랑
     병렬로 나열되게 해"): 한국어(iframe)와 글로벌(카드) 섹션을 위아래로 쌓지
     않고 나란히 두 칼럼으로 배치 — 좁은 화면에서는 flex-wrap으로 자연스럽게
     아래로 떨어진다. */
  main {{
    max-width: 1400px; margin: 0 auto; padding: 16px 20px 40px;
    display: flex; flex-wrap: wrap; align-items: flex-start; gap: 24px;
  }}
  .lang-section {{ display: flex; flex-direction: column; gap: 10px; flex: 1 1 420px; min-width: 320px; }}
  .lang-heading {{
    margin: 0; font-size: 13px; font-weight: 700; color: var(--ink-soft);
    text-transform: uppercase; letter-spacing: 0.04em;
  }}
  /* WHY 고정 650px인지(2026-08-05, "릴스 각 언어별로 카드 왜 없어졌어?" —
     실제로는 안 없어졌고 아래 글로벌 섹션이 화면 밖으로 밀려서 안 보인 것):
     탭 전환 방식일 땐 iframe 하나만 보이는 화면을 꽉 채워야 해서 80vh를 썼는데,
     지금은 이 iframe이 페이지 안 여러 섹션 중 하나라 80vh(대부분 화면 높이)를
     그대로 차지하면 바로 아래 글로벌 카드들이 스크롤 한참 뒤에야 보인다 —
     내용이 다 보이는 적당한 고정 높이로 줄인다. */
  iframe.dash-frame {{ width: 100%; height: 650px; border: 0; border-radius: 16px; background: var(--panel); display: block; }}
  .lang-body {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .plat-card {{
    flex: 1 1 280px; background: var(--panel); border: 1px solid var(--rule); border-radius: 12px;
    padding: 14px;
  }}
  .plat-card.is-done {{ opacity: 0.55; border-color: var(--accent); background: var(--accent-soft); }}
  .plat-lang {{
    display: block; font-size: 11px; font-weight: 700; color: var(--accent-deep);
    text-transform: uppercase; letter-spacing: 0.03em; margin-bottom: 2px;
  }}
  .plat-head {{ display: flex; align-items: flex-start; justify-content: space-between; gap: 8px; margin-bottom: 8px; }}
  .plat-card h3 {{ margin: 0; font-size: 14px; }}
  .plat-done-check {{
    display: flex; align-items: center; gap: 4px; font-size: 11px; color: var(--ink-soft);
    white-space: nowrap; cursor: pointer; flex: 0 0 auto;
  }}
  .plat-done-check input {{ width: 13px; height: 13px; accent-color: var(--accent); cursor: pointer; }}
  .plat-card textarea {{
    width: 100%; min-height: 120px; border: 1px solid var(--rule); border-radius: 8px; padding: 8px;
    font-size: 12px; font-family: inherit; resize: vertical;
  }}
  .plat-actions {{ display: flex; gap: 8px; margin-top: 8px; }}
  .plat-actions button, .plat-actions a {{
    font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 20px; border: none;
    text-decoration: none; cursor: pointer;
  }}
  .btn-copy {{ background: var(--accent-soft); color: var(--accent-deep); }}
  .btn-go {{ background: var(--accent); color: #fff; }}
  .empty {{ text-align: center; padding: 60px 20px; color: var(--ink-soft); }}
</style>
<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2/dist/umd/supabase.js"></script>
<script src="../../supabase_client.js"></script>
</head>
<body>
<a class="back" href="../../index.html">← 목록으로</a>
<header>
  <h1>{title}</h1>
  <p>언어별로 캡션·영상을 확인·업로드하세요 — 한 언어씩 완료해도 그대로 나머지가 이어집니다</p>
</header>
<main>
{lang_sections}
</main>
<script>
// WHY 이 페이지(다국어 topic 통합 허브)의 ?tab=도 ko iframe에 그대로
// 전달하는지(2026-08-07, 위 개별 topic dashboard.html과 같은 이유):
// index.html에서 "카드뉴스"/"숏츠" 탭을 눌러 들어왔으면, 이 허브 페이지 안의
// 한국어 iframe도 같은 트랙만 보여야 한다 — 빌드 시점엔 어느 탭에서 올지
// 알 수 없으므로(iframe src가 고정 문자열) 런타임에 현재 URL을 보고 붙인다.
(function () {{
  const tabParam = new URLSearchParams(location.search).get("tab");
  if (!tabParam) return;
  const frame = document.querySelector("iframe.dash-frame");
  if (frame) frame.src += (frame.src.includes("?") ? "&" : "?") + "tab=" + tabParam;
  // WHY 글로벌 라이트카드도 같이 필터링하는지(2026-08-08, "쇼츠쪽이랑
  // 카드뉴스쪽이랑 글로벌 인스타 릴스는 둘다 들어가있잖아" 버그 리포트): 위
  // iframe.src 갱신은 ko dashboard.html(iframe 내부)에만 적용되고, 글로벌
  // 언어의 라이트카드(_light_platform_card)는 필터링이 없어서 ?tab=으로
  // 뭘 눌러 들어와도 항상 전체 플랫폼을 그대로 보여줬다 — 카드뉴스 탭인데
  // 글로벌의 "Instagram Reels"(영상, video 타입)가 그대로 섞여 나오는 게
  // 문제였다. ko iframe 쪽과 같은 원칙(video → 숏츠, cards/text →
  // 카드뉴스)으로 plat-card를 개별 필터링하고, 카드가 전부 숨어서 빈
  // 섹션이 된 .lang-section은 통째로 숨긴다(글로벌은 현재 전부
  // shorts-only라 card_news 탭에서는 "글로벌" 섹션 자체가 사라짐).
  const wantVideo = tabParam === "shorts";
  document.querySelectorAll(".plat-card[data-plat-type]").forEach(card => {{
    const isVideo = card.dataset.platType === "video";
    card.style.display = (isVideo === wantVideo) ? "" : "none";
  }});
  document.querySelectorAll(".lang-section").forEach(section => {{
    const cards = section.querySelectorAll(".plat-card");
    if (cards.length === 0) return;
    const anyVisible = Array.from(cards).some(c => c.style.display !== "none");
    section.style.display = anyVisible ? "" : "none";
  }});
}})();
document.querySelectorAll(".btn-copy").forEach(btn => {{
  btn.addEventListener("click", () => {{
    const ta = document.getElementById(btn.dataset.target);
    navigator.clipboard.writeText(ta.value).then(() => {{
      const orig = btn.textContent;
      btn.textContent = "복사됨 ✓";
      setTimeout(() => btn.textContent = orig, 1500);
    }});
  }});
}});
document.querySelectorAll(".btn-go[data-copy-target]").forEach(btn => {{
  btn.addEventListener("click", () => {{
    const ta = document.getElementById(btn.dataset.copyTarget);
    navigator.clipboard.writeText(ta.value);
  }});
}});
// WHY 글로벌 카드에도 완료 체크를 다는지(2026-08-05, "인스타그램 릴스
// 글로벌꺼도 선택할 수 있게 해주고 그거 export할때도 확인가능하게"): ko
// dashboard.html(iframe 속, CARD_TEMPLATE)의 done-toggle과 정확히 같은
// hs_done_<topic>_<key> localStorage 키 스킴을 써서, index.html의 CSV
// 내보내기가 언어 상관없이 전부 픽업하게 한다.
const TOPIC_NAME = {topic_name_js};
const sb = window.supabase.createClient(window.HS_SUPABASE_URL, window.HS_SUPABASE_ANON_KEY);
const STORAGE_PREFIX = "hs_done_" + encodeURIComponent(TOPIC_NAME) + "_";
(async () => {{
  const {{ data: dbPosted }} = await sb.from("posting_log").select("platform").eq("topic", TOPIC_NAME);
  const dbPostedSet = new Set((dbPosted || []).map(r => r.platform));

  document.querySelectorAll(".plat-done-toggle").forEach(cb => {{
    const storageKey = STORAGE_PREFIX + cb.dataset.key;
    const card = cb.closest(".plat-card");
    if (localStorage.getItem(storageKey) || dbPostedSet.has(cb.dataset.name)) {{
      cb.checked = true;
      card.classList.add("is-done");
    }}
    cb.addEventListener("change", () => {{
      if (cb.checked) {{
        const postedAt = new Date().toISOString();
        const record = {{ topic: TOPIC_NAME, platform: cb.dataset.name, postedAt }};
        localStorage.setItem(storageKey, JSON.stringify(record));
        card.classList.add("is-done");
        sb.from("posting_log").upsert({{ topic: TOPIC_NAME, platform: cb.dataset.name, posted_at: postedAt }});
      }} else {{
        localStorage.removeItem(storageKey);
        card.classList.remove("is-done");
        sb.from("posting_log").delete().eq("topic", TOPIC_NAME).eq("platform", cb.dataset.name);
      }}
    }});
  }});
}})();
</script>
</body>
</html>
"""


def _light_platform_card(topic: str, lang: str, platform: dict, idx: int) -> str:
    """글로벌(비한국어) 언어 전용 경량 카드(2026-08-05부터 영상 조립 여부와
    무관하게 항상 이걸 씀 — 아래 _generate_unified_dashboard WHY 참고). WHY
    disclosure/product-link 동적 삽입 로직(_buildLinkBlock 등)을 안 쓰는지:
    그 로직은 쿠팡 파트너스 고지문구를 코드에서 그대로 끌어오는데, 글로벌
    topic은 아직 활성화된 제휴 프로그램이 없어서(2026-08-03 "아마존/알리는
    시간 좀 두고" 결정) 한국어 고지문이 영어/일본어 캡션에 섞여 붙는 사고를
    막으려면 이 카드는 그냥 저장된 캡션 텍스트를 그대로 보여주는 게 맞다.
    WHY 플랫폼을 인스타 릴스로 제한하지 않고 전부 보여주는지(2026-08-04,
    "포맷도 기존과 동일하게" 요청): 예전엔 Instagram Reels만 보여줬는데, ko
    대시보드처럼 실제 관리 대상인 전체 플랫폼을 보여주는 게 통합 취지에
    맞는다 — 어차피 UI 제외 목록(_UI_EXCLUDED_PLATFORMS) 적용 후엔 글로벌
    topic에 남는 플랫폼이 인스타그램 릴스 하나뿐이라 실질적으로는 카드 1장.
    WHY 영상 조립 상태 표시가 없는지(2026-08-05, "회색박스 텍스트 필요없잖아?
    이제 어차피 영상을 깃허브에 올려놓지를 않는데?"): mp4가 git에 없어서
    재생·다운로드가 안 되는 텍스트만 있는 박스였다 — 로컬 output/<topic>/<lang>/
    폴더에서 직접 작업하는 사람에게는 불필요한 안내라 아예 뺐다. WHY 언어
    라벨을 붙이는지(2026-08-05, "한국이든 글로벌이든 전부 한 탭으로" — 언어별
    탭 제거): 이제 여러 언어의 카드가 한 화면에 같이 나열되므로, 카드만 봐서는
    어떤 언어인지 구분이 안 돼서 카드마다 언어명을 표시한다.
    WHY "완료" 체크박스가 있는지(2026-08-05, "인스타그램 릴스 글로벌꺼도
    선택할 수 있게 해주고 그거 export할때도 확인가능하게"): ko 카드
    (CARD_TEMPLATE)에만 완료 체크가 있어서 글로벌 topic은 posting_log.csv
    내보내기(index.html)에 아예 안 잡혔다 — ko와 동일한 hs_done_ localStorage
    키 스킴을 그대로 써서(아래 UNIFIED_PAGE_TEMPLATE의 done-toggle 스크립트
    참고) CSV 내보내기가 언어 무관하게 전부 픽업하게 한다. done_key에 lang을
    섞는 이유: 5개 언어가 전부 같은 플랫폼명("Instagram Reels")을 쓰므로
    lang 없이는 완료 체크가 언어끼리 서로 덮어씀."""
    lang_label = GLOBAL_LANG_LABELS.get(lang, lang.upper())
    ta_id = f"g-cap-{lang}-{idx}"
    # WHY done_key와 data-name이 같은 원문 문자열에서 나오는지: index.html의
    # CSV 가져오기가 key = DONE_KEY_PREFIX + encodeURIComponent(topic) + "_" +
    # encodeURIComponent(platform) 식으로 "platform"(=CSV로 내보낸 dataset.name)
    # 값만으로 key를 재조립한다 — key와 name이 서로 다른 문자열이면 내보내기→
    # 가져오기 왕복 시 key가 어긋나서 체크 상태가 복원 안 된다(ko 카드의
    # done_key=quote(p["name"]) / data-name={name} 패턴과 동일하게 맞춤).
    done_name_raw = f"{platform['name']} ({lang.upper()})"
    done_key = quote(done_name_raw)
    done_name = _esc(done_name_raw)
    plat_type = platform.get("type", "text")
    return f"""
<div class="plat-card" data-done-key="{done_key}" data-plat-type="{plat_type}">
  <div class="plat-head">
    <h3><span class="plat-lang">{_esc(lang_label)}</span>{_esc(platform['name'])}</h3>
    <label class="plat-done-check">
      <input type="checkbox" class="plat-done-toggle" data-key="{done_key}" data-name="{done_name}">
      <span>완료</span>
    </label>
  </div>
  <textarea id="{ta_id}" spellcheck="false">{_esc(platform['caption'])}</textarea>
  <div class="plat-actions">
    <button class="btn-copy" data-target="{ta_id}">캡션 복사</button>
    <a class="btn-go" href="{platform['url']}" target="_blank" rel="noopener" data-copy-target="{ta_id}">열기 →</a>
  </div>
</div>
"""


def _generate_unified_dashboard(base_topic: str, output_root: Path, data_root: Path) -> None:
    """topic 하나(예: "관절_1")의 언어(ko 포함) 전체를 한 페이지로 통합한다 —
    언어마다 dashboard.html이 따로 있어서(+ko는 "한국" 버튼, 나머지는 "Global"
    버튼으로 갈라져 있던 것) 그때그때 다른 URL을 오가야 했던 것을,
    output/<topic>/dashboard.html 하나로 합친다(위 UNIFIED_PAGE_TEMPLATE WHY
    참고). ko는 언어별 dashboard.html을 그대로 iframe으로 보여준다(완전히 동일한
    폼 보장, 여러 플랫폼을 관리해야 해서 그 폼이 필요함).

    WHY 글로벌(비한국어) 언어는 iframe 대신 항상 가벼운 카드인지(2026-08-05,
    "UI에 찌꺼기가 좀 많이남아있다... 이제 항목도 줄었으니 글로벌도 버튼눌러서
    이동해서 인스타 누르지말고 걍 하나로 병합해도될듯"): 글로벌 topic은
    UI에서 유튜브 쇼츠가 자동 업로드로 빠지고 나면 플랫폼이 인스타그램 릴스
    하나만 남는데다, 제휴 프로그램이 아직 없어(CLAUDE.md "글로벌 확장" 참고)
    쿠팡/네이버 상품 링크 덕도 전부 빈 찌꺼기다 — iframe 속 "업로드 대시보드"
    전체 폼(빠른 도구 덕·상품 링크 섹션 등)으로 카드 하나를 또 감쌀 이유가 없다.

    WHY 언어별 탭 자체를 없앴는지(2026-08-05, "1번은 한국이든 글로벌이든 전부
    한 탭으로 가라고" — 탭 전환 UI 완전 폐지 확정): 한국어(iframe) 섹션과
    글로벌 언어 카드들을 전부 한 페이지에 세로로 나열한다 — 언어별로 버튼을
    눌러 전환할 필요 없이 스크롤만으로 전부 확인 가능."""
    topic_data_root = data_root / base_topic
    if not topic_data_root.exists():
        return
    all_langs = sorted(p.name for p in topic_data_root.iterdir() if p.is_dir())
    # WHY ko를 맨 앞에 고정하는지: 사용자가 한국어 화자라 한국어 섹션이 먼저
    # 보이는 게 자연스럽다 — 나머지는 알파벳 순서 그대로.
    langs = (["ko"] if "ko" in all_langs else []) + [l for l in all_langs if l != "ko"]

    sections = ""
    global_cards = ""
    for lang in langs:
        captions_path = topic_data_root / lang / "platform_captions.json"
        if not captions_path.exists():
            continue

        if lang == "ko":
            lang_dashboard = output_root / base_topic / "ko" / "dashboard.html"
            if lang_dashboard.exists():
                sections += (
                    '<section class="lang-section"><h2 class="lang-heading">한국어</h2>'
                    '<iframe class="dash-frame" src="ko/dashboard.html"></iframe></section>\n'
                )
                continue
            # WHY ko도 iframe 없으면 light card로 폴백하는지: 아직 영상 조립
            # 전이라 ko/dashboard.html 자체가 없는 극히 드문 상태(보통 ko는
            # 콘텐츠 완성과 동시에 전체 폼이 생김) — 그래도 빈 화면보다는
            # 캡션이라도 보이는 게 낫다.
            try:
                spec = json.loads(captions_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                spec = {}
            ko_cards = "".join(
                _light_platform_card(base_topic, lang, p, idx)
                for idx, p in enumerate(spec.get("platforms", []))
                if p["name"] not in _UI_EXCLUDED_PLATFORMS
            )
            if ko_cards:
                sections += (
                    '<section class="lang-section"><h2 class="lang-heading">한국어</h2>'
                    f'<div class="lang-body">{ko_cards}</div></section>\n'
                )
            continue

        try:
            spec = json.loads(captions_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            spec = {}
        global_cards += "".join(
            _light_platform_card(base_topic, lang, p, idx)
            for idx, p in enumerate(spec.get("platforms", []))
            if p["name"] not in _UI_EXCLUDED_PLATFORMS
        )

    if global_cards:
        sections += (
            '<section class="lang-section"><h2 class="lang-heading">글로벌</h2>'
            f'<div class="lang-body">{global_cards}</div></section>\n'
        )

    if not sections:
        sections = '<div class="empty">아직 준비된 언어 콘텐츠가 없어요</div>'

    ko_captions = topic_data_root / "ko" / "platform_captions.json"
    title = base_topic
    if ko_captions.exists():
        try:
            title = json.loads(ko_captions.read_text(encoding="utf-8")).get("title", base_topic)
        except json.JSONDecodeError:
            pass

    html = UNIFIED_PAGE_TEMPLATE.format(
        title=_esc(title), lang_sections=sections, topic_name_js=json.dumps(base_topic),
    )
    out_dir = output_root / base_topic
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dashboard.html").write_text(html, encoding="utf-8")


def generate(spec_path: str, card_news_dir: str, video_path: str | None, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    topic = spec.get("topic")
    if not isinstance(topic, str):
        # WHY(2026-08-05): 글로벌(비한국어) topic의 card_news_spec.json은 "topic"
        # 필드가 아예 없고 "title"도 영상 템플릿용으로 줄바꿈된 리스트라(문자열이
        # 아님), 기존 폴백(spec["title"])이 그대로 크래시했다 — spec_path의
        # data/<주제>/[<lang>/]card_news_spec.json 경로에서 <주제>[_<lang>] 슬러그를
        # 유도한다(CLAUDE.md "글로벌 확장"의 topic 필드 명명 규칙과 동일 형식).
        parts = Path(spec_path).resolve().parts
        try:
            idx = parts.index("data")
            rest = parts[idx + 1:-1]
        except ValueError:
            rest = ()
        topic = "_".join(rest) if rest else Path(spec_path).parent.name
    if isinstance(spec.get("title"), list):
        # WHY(2026-08-05): 영상 템플릿(before_after_transition 등)용으로 줄바꿈
        # 리스트로 저장된 title을 대시보드는 그대로 한 줄 문자열로 써야 한다
        # (_esc()가 .replace()를 호출하므로 리스트면 그대로 크래시) — 공백으로
        # 합쳐서 단일 문자열로 정규화, 아래 모든 title 사용처가 그대로 재사용.
        spec["title"] = " ".join(spec["title"])
    # WHY 여기서 한 번만 걸러내는지: _UI_EXCLUDED_PLATFORMS 정의부 WHY 참고 — 아래
    # 모든 코드가 spec["platforms"]/spec.get("platforms", ...)를 그대로 참조하므로,
    # spec 자체를 미리 걸러두면 호출부마다 따로 필터링할 필요가 없다.
    spec["platforms"] = [p for p in spec.get("platforms", []) if p["name"] not in _UI_EXCLUDED_PLATFORMS]

    # WHY 자동 경고(2026-07-31): 해시태그가 한 플랫폼만 빠진 채로 넘어간 적이 있었다
    # ("전반적으로 해시태그 있어야하는건 자동으로 넣어줘야하지않을까" 지적) — 매번
    # 수동으로 체크 스크립트를 돌리는 것보다, 대시보드 생성 시 자동으로 걸러서
    # 빠뜨렸으면 바로 눈에 띄게 한다.
    for p in spec.get("platforms", []):
        if "#" not in p.get("caption", ""):
            print(f"⚠️  경고: '{p['name']}' 캡션에 해시태그가 없습니다")
    affiliate_path = Path(__file__).resolve().parent.parent / "data" / "affiliate_accounts.json"
    affiliate = json.loads(affiliate_path.read_text()) if affiliate_path.exists() else {}
    disclosure = affiliate.get("disclosure", {})
    _product_links_loaded = _load_product_links()
    _naver_links_loaded = _load_naver_product_links()
    dock_products = _dock_products(
        spec.get("products", []), _product_links_loaded, _naver_links_loaded,
        naver_brandconnect_id=affiliate.get("naver_brandconnect_id"),
    )
    dock_products_bottom = _product_links_bottom_section(
        spec.get("products", []), _product_links_loaded, _naver_links_loaded
    )

    # WHY 다시 전체 글롭인지(2026-08-09, "지방간_1 이런건 왜 카드뉴스 형태
    # 내용물들이 다 사라졌지?"): 2026-08-05엔 표지(00_표지.jpg)만 git 추적해서
    # 전체 글롭을 쓰면 배포본에서 나머지가 깨진 이미지로 보였다 — 이후
    # "카드뉴스 개별 이미지도 git/Vercel에 포함"(2026-08-09) 결정으로 카드
    # 이미지 전체가 배포되므로, 이 제한이 남아있으면 "미리보기"/"카드 이미지
    # 다운로드"가 표지 1장만 보여주는(버튼 id는 downloadAllCards인데 실제로는
    # 1장뿐인) 불일치가 생긴다.
    card_imgs = sorted(Path(card_news_dir).glob("*.jpg")) if Path(card_news_dir).exists() else []
    card_thumbs = "".join(f'<img src="card_news/{quote(p.name)}" alt="{_esc(p.stem)}">' for p in card_imgs)

    # WHY video_path를 받고도 대시보드에서 안 쓰는지(2026-08-05, "회색박스
    # 텍스트 필요없잖아? 이제 어차피 영상을 깃허브에 올려놓지를 않는데?"): mp4가
    # git에 안 올라가서 UI에 뭘 표시해도 실제 재생·다운로드는 안 됐고, 로컬에서
    # 직접 작업하는 사람에게 "로컬에서 확인"류 안내는 잡음이라 전부 뺐다.
    # video_path 파라미터는 video_assembler.py 등 다른 호출부·테스트가 여전히
    # 4개 위치 인자로 호출하므로 시그니처만 유지한다(호출부까지 바꾸는 건 이
    # 정리의 범위 밖).

    # WHY glob(2026-07-31): card_news.py가 이제 파일명 앞에 topic 접두어를 붙이므로
    # ("<topic>_00_표지.jpg") 정확한 이름을 하드코딩하지 않고 패턴으로 찾는다 — 접두어
    # 없는 예전 topic("00_표지.jpg")과도 둘 다 호환.
    cover_path = next(Path(card_news_dir).glob("*00_표지.jpg"), None)

    platforms_by_type: dict[str, list[dict]] = {t: [] for t in TYPE_ORDER}
    for p in spec["platforms"]:
        platforms_by_type.setdefault(p.get("type", "text"), []).append(p)

    # WHY 페이스북을 "video" 그룹으로 옮기는지(2026-08-08): type은 "text"지만
    # (클립보드 붙여넣기 방식이라) 실제로는 숏츠 영상을 올리는 플랫폼이라
    # (CLAUDE.md "영상 필요 플랫폼" 목록에 포함) 카드뉴스 탭이 아니라 숏츠
    # 탭에 있어야 한다 — index.html의 tracks 판별 로직과 동일 원칙.
    fb_platforms = [p for p in platforms_by_type.get("text", []) if p.get("name") == "페이스북"]
    if fb_platforms:
        platforms_by_type["text"] = [p for p in platforms_by_type["text"] if p.get("name") != "페이스북"]
        platforms_by_type["video"].extend(fb_platforms)

    idx = 0
    # WHY 영상/카드뉴스+텍스트 두 탭으로 나누는지(2026-08-07, "숏츠형태랑
    # 카드뉴스형태의 콘텐츠 내용이 다 들어가있는데... 어떤 주제에 해당하는
    # 콘텐츠들이 다 만들어져있다고 그게 모두 한곳에 모여있을 필요 없어졌어"):
    # 숏츠·카드뉴스가 이제 독립 트랙(위 index.html 목록 분리와 동일 원칙)이라
    # 한 topic이 둘 다 갖고 있어도 페이지 안에서까지 섞여 보일 필요가 없다 —
    # video 타입은 "숏츠" 탭, cards+text 타입은 "카드뉴스" 탭으로 분리.
    shorts_sections_html = ""
    cardnews_sections_html = ""
    for t in TYPE_ORDER:
        group = platforms_by_type.get(t, [])
        if not group:
            continue
        cards_html = ""
        for p in group:
            cards_html += CARD_TEMPLATE.format(
                name=_esc(p["name"]),
                url=p["url"],
                idx=idx,
                caption=_esc(p["caption"]),
                type=t,
                type_label=TYPE_LABEL[t],
                action=_esc(p.get("action", "")),
                asset_link=_asset_link(t, topic, cover_path.name if cover_path else None),
                done_key=quote(p["name"]),
                no_caption_link_attr="1" if p.get("no_caption_link") else "",
                naver_button_attr="1" if p.get("network") == "naver" else "",
                profile_note_attr="1" if p.get("add_profile_note") else "",
                suppress_product_block_attr="1" if p.get("suppress_product_block") else "",
                comment_dm_attr="1" if p.get("comment_dm_automation") else "",
                link_in_comment_attr="1" if p.get("link_in_comment") else "",
                # WHY name=="네이버 클립"으로 직접 판별하는지(2026-08-06): network:"naver"
                # 플래그는 지금 네이버 블로그에만 붙어있음(클립은 캡션에 링크
                # 자체를 안 써서 이 플래그가 필요없음, 위 "네이버 블로그, 다시
                # 브랜드커넥트로" 절 참고) — 이 버튼은 대가성 문구를 댓글로 따로
                # 달아야 하는 클립 전용이라 이름으로 직접 잡는다.
                # suppress_product_block이 걸려있는 동안(제휴 보류 중)은 버튼
                # 자체를 숨긴다 — 재개 시점에 플래그만 지우면 이 버튼도 같이
                # 나타나게.
                naver_connect_comment_btn=(
                    '<button type="button" class="copy-naver-connect-comment">'
                    "📌 커넥트 댓글 문구 복사</button>"
                    if p.get("name") == "네이버 클립" and not p.get("suppress_product_block")
                    else ""
                ),
            )
            idx += 1
        section_html = SECTION_TEMPLATE.format(section_title=TYPE_SECTION_TITLE[t], cards=cards_html)
        if t == "video":
            shorts_sections_html += section_html
        else:
            cardnews_sections_html += section_html

    card_image_names_js = json.dumps([quote(p.name) for p in card_imgs])

    ad_tag_badge = '<span class="ad-tag-badge">🏷️ 광고표시 적용</span>' if spec.get("ad_tag") else ""

    # WHY 둘 다 있을 때만 탭 버튼을 보여주는지: 하나만 있으면(카드뉴스 전용
    # topic 등) 탭 자체가 무의미 — 있는 쪽만 그대로 보여준다.
    if shorts_sections_html and cardnews_sections_html:
        platform_sections = (
            '<div class="platform-tabs" id="topicTrackTabButtons">'
            '<button type="button" class="platform-tab-btn active" data-tab-target="shorts">🎬 숏츠</button>'
            '<button type="button" class="platform-tab-btn" data-tab-target="cardnews">🗞 카드뉴스</button>'
            "</div>"
            f'<div class="platform-tab-pane active" data-tab-pane="shorts">{shorts_sections_html}</div>'
            f'<div class="platform-tab-pane" data-tab-pane="cardnews">{cardnews_sections_html}</div>'
        )
    else:
        platform_sections = shorts_sections_html or cardnews_sections_html

    # WHY 상대경로로 계산하는지(2026-08-08, "index에 목록 아예 안보이는데?" —
    # GitHub Pages는 choijaaaaaa.github.io/health/처럼 서브경로에서 서빙되는데
    # 절대경로("/supabase_client.js")는 사이트 루트(choijaaaaaa.github.io/)를
    # 가리켜버려 404가 났다 — out_path 깊이(레거시 output/<topic>/dashboard.html
    # 2단계, 글로벌 output/<topic>/<lang>/dashboard.html 3단계)에 맞춰 "../" 개수를
    # 그때그때 계산해야 GitHub Pages·Vercel(진짜 루트) 양쪽에서 다 맞는다.
    project_root = Path(__file__).resolve().parent.parent
    out_dir = Path(out_path).resolve().parent
    asset_prefix = "../" * len(out_dir.relative_to(project_root).parts)

    html = PAGE_TEMPLATE.format(
        title=_esc(spec["title"]), card_thumbs=card_thumbs, ad_tag_badge=ad_tag_badge,
        platform_sections=platform_sections,
        topic=quote(topic), dock_products=dock_products, dock_products_bottom=dock_products_bottom,
        card_image_names_js=card_image_names_js, asset_prefix=asset_prefix,
        coupang_disclosure_js=json.dumps(disclosure.get("coupang", "")),
        naver_disclosure_js=json.dumps(disclosure.get("naver", "")),
        # WHY comment_keyword 우선(2026-07-31): 상품이 없는 topic(products: [])은
        # products[0] 방식으로는 빈 문자열이 되어 "댓글에 ''라고 남겨주세요" 같은
        # 깨진 문장이 나온다 — 명시적 comment_keyword 필드를 최우선으로 쓰고,
        # 없으면 기존처럼 products[0]로 폴백. 새 키워드는 반드시
        # ~/.claude/comment-keywords.md에서 중복 확인 후 등록할 것(인포크 등
        # 댓글→DM 자동화가 다른 프로젝트/채널과 전역으로 키워드를 공유하므로).
        comment_keyword_js=json.dumps(spec.get("comment_keyword") or (spec.get("products") or [""])[0]),
        topic_name_js=json.dumps(topic),
    )
    Path(out_path).write_text(html)
    _update_topics_index(out_path)
    print(f"대시보드 생성 완료: {out_path}")


if __name__ == "__main__":
    spec_path, card_news_dir, video_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    generate(spec_path, card_news_dir, video_path, out_path)
