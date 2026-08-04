# 플랫폼별 업로드 결과물 대시보드 생성기. WHY: 포스팅 API가 없는 플랫폼이 대부분이라
# 자동 업로드는 불가능 — 대신 영상/카드뉴스 미리보기 + 캡션(수정 가능)을 한 페이지에
# 모아두고, 사람이 확인·수정한 뒤 버튼 눌러 플랫폼으로 이동해서 수동 업로드하는
# 흐름을 지원한다.
# 2026-07-30 개편: 플랫폼마다 "뭘 첨부하고 뭘 눌러야 하는지"가 한눈에 안 보인다는
# 피드백으로, type(video/cards/text)별 배지·행동 지침·바로가기 다운로드 링크를 추가하고
# 콘텐츠 유형별로 섹션을 나눠 스캔하기 쉽게 재구성.
from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote


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

# WHY 인스타그램 릴스만 별도 영상을 쓰는지(2026-08-04): generate()의
# instagram_video_path WHY 참고 — 인스타 릴스 카드에서만 안전 여백 버전 파일을
# 연결하기 위해 이름으로 매칭한다.
_INSTAGRAM_REELS_NAMES = {"인스타그램 릴스", "Instagram Reels"}

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
    <button class="btn-copy" data-target="cap-{idx}" data-cover="{cover_attr}">{copy_label}</button>
    <a class="btn-go" href="{url}" target="_blank" rel="noopener" data-copy-target="cap-{idx}">열기(캡션 자동복사) →</a>
    <span class="edit-hint">직접 수정 가능</span>
  </div>
</div>
"""

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

  section {{ max-width: 1040px; margin: 0 auto; padding: 0 24px 28px; }}
  section > h2 {{
    font-size: 14px; letter-spacing: 0.04em; color: var(--ink-soft); text-transform: uppercase;
    margin: 0 0 14px; display: flex; align-items: center; gap: 8px;
  }}
  section > h2::before {{ content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }}

  .preview-row {{ display: flex; gap: 24px; flex-wrap: wrap; }}
  .video-panel {{
    background: var(--panel); border: 1px solid var(--rule); border-radius: 18px; padding: 16px;
    flex: 0 0 auto;
  }}
  .video-panel video {{
    width: 260px; aspect-ratio: 9/16; border-radius: 12px; background: #000; display: block;
  }}
  .video-panel .dl {{
    display: block; text-align: center; margin-top: 10px; font-size: 13px; font-weight: 700;
    color: var(--accent-deep); text-decoration: none;
  }}

  .card-gallery {{
    flex: 1; min-width: 280px;
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

  .lightbox {{
    display: none; position: fixed; inset: 0; background: rgba(20,14,10,0.85);
    align-items: center; justify-content: center; z-index: 100; padding: 24px;
  }}
  .lightbox.open {{ display: flex; }}
  .lightbox img {{ max-width: 100%; max-height: 90vh; border-radius: 12px; }}
</style>
</head>
<body>
<header>
  <div class="eyebrow">업로드 대시보드</div>
  <h1>{title}</h1>
</header>

<div class="quick-dock" id="quickDock">
  <div class="dock-head">
    <span>빠른 도구</span>
  </div>
  <div class="dock-section">
    <h4>다운로드</h4>
    <div class="dock-links">
      {video_download_link}
      <button class="dock-links-btn" id="downloadAllCards">🖼 카드뉴스 전체 다운로드</button>
    </div>
  </div>
  <div class="dock-section">
    <h4>실사진 소싱</h4>
    <div class="dock-links">
      <a href="{unsplash_url}" target="_blank" rel="noopener">🔍 Unsplash</a>
      <a href="{pexels_url}" target="_blank" rel="noopener">🔍 Pexels</a>
    </div>
  </div>
  <div class="dock-section">
    <h4>제작 도구</h4>
    <div class="dock-links">
      <a href="https://link.inpock.co.kr/admin" target="_blank" rel="noopener">🔗 인포크 관리자</a>
      <a href="https://partners.coupang.com/" target="_blank" rel="noopener">🛒 쿠팡파트너스</a>
      <a href="https://studio.typecast.ai/" target="_blank" rel="noopener">🎙 타입캐스트</a>
    </div>
  </div>
  {dock_products}
</div>

<section>
  <h2>미리보기</h2>
  <div class="preview-row">
    <div class="video-panel">
      {video_block}
    </div>
    <div class="card-gallery" id="card-gallery">
      <div class="card-scroll">{card_thumbs}</div>
    </div>
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
// WHY 중복 접두어 방지: card_news.py가 이제 파일명에 topic을 직접 붙이므로(예전
// topic은 안 붙어있음), 이미 붙어있으면 또 붙이지 않는다.
function _withTopicPrefix(name) {{
  return name.startsWith(TOPIC_NAME + "_") ? name : TOPIC_NAME + "_" + name;
}}
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

function _escapeHtml(s) {{
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}}

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
    const cover = btn.dataset.cover;
    if (cover && window.ClipboardItem) {{
      // WHY font-size를 인라인으로: 붙여넣기 대상 에디터(네이버 블로그·티스토리)가
      // 기본 폰트 크기를 작게 잡는 경우가 많아서, 처음부터 읽기 편한 크기로 넣어준다
      // (리치에디터는 대개 인라인 스타일까지 그대로 붙여넣음).
      const bodyHtml = text.split("\\n").map(line => line.trim() ? `<p style="font-size:17px;line-height:1.7;">${{_escapeHtml(line)}}</p>` : "<br>").join("");
      const html = `<p><img src="${{cover}}" style="max-width:100%;"></p>` + bodyHtml;
      const item = new ClipboardItem({{
        "text/plain": new Blob([text], {{type: "text/plain"}}),
        "text/html": new Blob([html], {{type: "text/html"}}),
      }});
      navigator.clipboard.write([item]).then(onCopied).catch(() => navigator.clipboard.writeText(text).then(onCopied));
    }} else {{
      navigator.clipboard.writeText(text).then(onCopied);
    }}
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
    const result = suppressBlock ? null : (linkInComment ? {{text: "", disclosure: COUPANG_DISCLOSURE}} : (noCaptionLink ? _buildCtaBlock(hasCommentDm) : _buildLinkBlock(hasNaverButton)));
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
    let withTop;
    if (linkInComment) {{
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
    const bottomWrapped = AUTO_BOTTOM_START + result.disclosure + (blockText ? "\\n\\n" + blockText : "") + AUTO_BOTTOM_END;
    box.value = withTop + "\\n\\n" + bottomWrapped;
  }});
}}

document.querySelectorAll(".product-link-input").forEach(inp => {{
  const row = inp.closest(".dock-product-row");
  const storageKey = LINK_STORAGE_PREFIX + inp.dataset.market + "_" + inp.dataset.product;
  const saved = localStorage.getItem(storageKey);
  if (saved) {{
    inp.value = saved;
    row.classList.add("linked");
  }}
  inp.addEventListener("input", () => {{
    if (inp.value.trim()) {{
      localStorage.setItem(storageKey, inp.value.trim());
      row.classList.add("linked");
    }} else {{
      localStorage.removeItem(storageKey);
      row.classList.remove("linked");
    }}
    applyProductLinks();
  }});
  inp.addEventListener("keydown", e => {{
    if (e.key === "Enter") {{ row.classList.remove("row-expanded"); inp.blur(); }}
  }});
}});

applyProductLinks();

// WHY JSON으로 저장(2026-08-02): 예전엔 이 키에 그냥 "1"만 넣었는데, 이러면
// 나중에 CSV로 내보낼 때 topic/플랫폼명을 키 문자열에서 역으로 파싱해야 하고
// topic 이름 자체에 "_"가 들어있어서(예: 눈_1) 안전하게 쪼갤 방법이 없다 — 값
// 안에 topic/platform/게시시각을 자체적으로 담아서 내보내기가 파싱 없이 바로
// 되게 한다(포스팅 스케줄 로그 — index.html의 CSV 내보내기/가져오기 참고).
const STORAGE_PREFIX = "hs_done_{topic}_";
document.querySelectorAll(".done-toggle").forEach(cb => {{
  const storageKey = STORAGE_PREFIX + cb.dataset.key;
  const card = cb.closest(".platform-card");
  if (localStorage.getItem(storageKey)) {{
    cb.checked = true;
    card.classList.add("is-done");
  }}
  cb.addEventListener("change", () => {{
    if (cb.checked) {{
      const record = {{ topic: TOPIC_NAME, platform: cb.dataset.name, postedAt: new Date().toISOString() }};
      localStorage.setItem(storageKey, JSON.stringify(record));
      card.classList.add("is-done");
    }} else {{
      localStorage.removeItem(storageKey);
      card.classList.remove("is-done");
    }}
  }});
}});
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


def _asset_link(platform_type: str, has_video: bool, video_name: str, topic: str, cover_name: str | None) -> str:
    topic_attr = _esc(topic)
    if platform_type == "video":
        if has_video:
            return f'<a class="asset-link" href="{video_name}" download="{_prefixed(video_name, topic_attr)}">🎬 영상 다운로드</a>'
        return '<span class="asset-link disabled">🎬 영상 준비 중 — 나중에 다시 확인</span>'
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
) -> str:
    if not products:
        return ""
    product_links = product_links or {}
    naver_links = naver_links or {}
    rows = ""
    for idx, name in enumerate(products):
        coupang_url = f"https://www.coupang.com/np/search?component=&q={quote(name)}&channel=user"
        naver_search_url = f"https://search.shopping.naver.com/search/all?query={quote(name)}"
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
        caption_path = data_root / rel / "platform_captions.json"
        if caption_path.exists():
            try:
                title = json.loads(caption_path.read_text()).get("title", topic)
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
            "thumbnail": thumbnail,
        })
    topics.sort(key=lambda t: t["topic"])
    (output_root / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2))

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
# 보여주는 탭 페이지"로 만드는지(2026-08-04, "글로벌도 합치자 한 페이지에 같이
# 있고 포맷도 기존과 동일하게 가야겠다... 기존에 관리하던 폼이랑 동일하게 가져가면
# 딱이네" — ko/글로벌을 따로 관리하던 두 페이지·두 버튼(한국/Global)을 없애고
# 하나로 합쳐달라는 요청): CARD_TEMPLATE 기반의 완성된 카드(캡션 편집·상품
# 링크 dock·고지문구 자동삽입·완료 체크 등)를 언어마다 다시 구현하면 두 벌을
# 유지보수해야 하고 필연적으로 기능이 어긋난다 — 이미 생성된 언어별
# dashboard.html을 그대로 iframe에 넣으면 "완전히 동일한 폼"이 100% 보장되고,
# 앞으로 CARD_TEMPLATE/JS를 고치면 모든 언어 탭에 자동으로 반영된다. 아직 영상이
# 없어서(1단계 콘텐츠만 완료) 그 언어의 dashboard.html 자체가 없는 경우에만
# 가벼운 폴백 카드(_light_platform_card)를 대신 보여준다.
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
  html, body {{ height: 100%; }}
  body {{
    margin: 0; font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", -apple-system, sans-serif;
    background: linear-gradient(180deg, var(--bg-top), var(--bg-bottom));
    color: var(--ink);
    display: flex; flex-direction: column; min-height: 100vh;
  }}
  header {{ padding: 32px 24px 8px; text-align: center; flex: 0 0 auto; }}
  header h1 {{ margin: 0 0 6px; font-size: 22px; }}
  header p {{ margin: 0; color: var(--ink-soft); font-size: 13px; }}
  .back {{ display: inline-block; margin: 18px 0 0 20px; color: var(--ink-soft); font-size: 13px; text-decoration: none; }}
  .lang-tabs {{
    max-width: 1040px; margin: 20px auto 0; padding: 0 20px;
    display: flex; gap: 8px; flex-wrap: wrap; flex: 0 0 auto; width: 100%;
  }}
  .lang-tab {{
    font-size: 14px; font-weight: 700; padding: 10px 18px; border-radius: 22px; border: none;
    background: var(--panel); color: var(--ink-soft); cursor: pointer; white-space: nowrap;
    border: 1px solid var(--rule);
  }}
  .lang-tab.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
  /* WHY main도 flex:1로 나머지 높이를 다 차지하는지: iframe 패널이 여기 아래에
     실제 뷰포트에 가까운 높이를 확보해야 그 안의 상품 링크 dock(position:fixed,
     아래 iframe WHY 참고)이 좁은 박스에 눌리지 않고 편하게 클릭할 수 있는
     크기로 뜬다. */
  main {{ max-width: 1040px; margin: 0 auto; padding: 16px 20px 40px; flex: 1 1 auto; min-height: 0; width: 100%; display: flex; flex-direction: column; }}
  .lang-panel {{ display: none; }}
  .lang-panel.active {{ display: flex; flex-direction: column; flex: 1 1 auto; min-height: 0; }}
  /* WHY iframe이 뷰포트 대부분을 채우는 고정 높이(자동 리사이즈 없음)인지
     (2026-08-04, 실제 버그로 두 번 발견됨): ① 예전엔 iframe 높이를 내용물
     실측 높이로 늘려서(load 시 scrollHeight 적용) 페이지 전체가 하나의
     스크롤처럼 보이게 했는데, 그러면 iframe 내부 문서 입장에서 "뷰포트 =
     전체 문서 높이"가 되어 스크롤 자체가 안 생기고, 언어별 dashboard.html
     안의 상품 링크 dock(position: fixed)이 스크롤을 전혀 못 따라오게 됐다 —
     position:fixed는 항상 자기 문서 자신의 뷰포트 기준으로만 동작해서 부모
     페이지 스크롤과 연동될 수 없다. ② 그래서 82vh 고정 높이로 되돌렸더니
     이번엔 "따라오고아니고 보다 바깥으로 빠져서 좀더 편하게 버튼을 누르는거
     더 중요해" — dock이 좁은 82vh 박스 안에 눌려서 버튼을 누르기 불편하다는
     지적. iframe은 어떤 경우든 자기 박스 밖으로 내용을 못 내보내므로(다른
     documents라 CSS로 못 뚫음), 박스 자체를 실제 브라우저 창에 최대한
     가깝게 키우는 게 유일한 실용적 해법 — 위 body/main의 flex 레이아웃으로
     header·탭을 뺀 나머지 뷰포트 전체를 iframe에 준다. */
  iframe.dash-frame {{ width: 100%; flex: 1 1 auto; min-height: 600px; border: 0; border-radius: 16px; background: var(--panel); }}
  .lang-body {{ display: flex; gap: 16px; flex-wrap: wrap; }}
  .plat-card {{
    flex: 1 1 280px; background: var(--panel); border: 1px solid var(--rule); border-radius: 12px;
    padding: 14px;
  }}
  .plat-card h3 {{ margin: 0 0 8px; font-size: 14px; }}
  .plat-card video {{ width: 150px; aspect-ratio: 9/16; border-radius: 8px; background: #000; display: block; margin-bottom: 8px; }}
  .g-video-ph {{
    width: 150px; aspect-ratio: 9/16; border-radius: 8px; background: #efe3d8; display: flex;
    align-items: center; justify-content: center; font-size: 12px; color: var(--ink-soft); margin-bottom: 8px;
  }}
  .plat-card .dl {{
    display: block; font-size: 12px; font-weight: 700; color: var(--accent-deep); text-decoration: none;
    margin: -4px 0 8px;
  }}
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
</head>
<body>
<a class="back" href="../../index.html">← 목록으로</a>
<header>
  <h1>{title}</h1>
  <p>언어를 골라 캡션·영상을 확인·업로드하세요 — 한 언어씩 완료해도 그대로 나머지가 이어집니다</p>
</header>
<div class="lang-tabs">{tab_buttons}</div>
<main>
{lang_panels}
</main>
<script>
document.querySelectorAll(".lang-tab").forEach(btn => {{
  btn.addEventListener("click", () => {{
    document.querySelectorAll(".lang-tab").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".lang-panel").forEach(p => p.classList.remove("active"));
    btn.classList.add("active");
    document.getElementById(btn.dataset.panel).classList.add("active");
  }});
}});
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
</script>
</body>
</html>
"""


def _light_platform_card(topic: str, lang: str, platform: dict, idx: int) -> str:
    """언어 대시보드(dashboard.html)가 아직 없는 언어(콘텐츠는 있지만 영상 조립
    전 — 1단계만 끝난 상태)용 경량 카드. WHY disclosure/product-link 동적 삽입
    로직(_buildLinkBlock 등)을 안 쓰는지: 그 로직은 쿠팡 파트너스 고지문구를
    코드에서 그대로 끌어오는데, 글로벌 topic은 아직 활성화된 제휴 프로그램이
    없어서(2026-08-03 "아마존/알리는 시간 좀 두고" 결정) 한국어 고지문이
    영어/일본어 캡션에 섞여 붙는 사고를 막으려면 이 카드는 그냥 저장된 캡션
    텍스트를 그대로 보여주는 게 맞다. WHY 플랫폼을 인스타 릴스로 제한하지 않고
    전부 보여주는지(2026-08-04, "포맷도 기존과 동일하게" 요청): 예전엔
    Instagram Reels만 보여줬는데, ko 대시보드처럼 실제 관리 대상인 전체
    플랫폼을 보여주는 게 통합 취지에 맞는다."""
    video_dir = Path(__file__).resolve().parent.parent / "output" / topic / lang
    # WHY 두 글롭 다 시도하는지: 대부분 "<topic>_shorts.mp4"(topic 접두어) 규칙을
    # 따르지만, 일부 언어 topic은 접두어 없이 그냥 "shorts.mp4"로도 만들어져 있었다
    # (실측: 갑상선_1/en) — 폴더 자체가 이미 topic+언어를 구분해주므로 둘 다 허용.
    candidates = sorted(video_dir.glob("*shorts.mp4")) if video_dir.exists() else []
    # WHY 인스타그램 릴스 카드만 별도로 *shorts_instagram.mp4를 찾는지(2026-08-04,
    # "instagram이라고 되어있는것들도 ui에서 다운로드 할수있게 해줘야 해" 요청):
    # generate()(ko/완성된 언어 대시보드)는 이미 이 안전 여백 버전을 인스타 릴스
    # 카드에 자동 연결하는데(위 instagram_video_path 참고), 이 경량 카드는 아직
    # 그 로직이 없어서 shorts_instagram.mp4가 폴더에 있어도 다운로드할 방법이
    # 없었다 — 같은 규칙을 그대로 적용해서 형식을 맞춘다.
    if platform["name"] in _INSTAGRAM_REELS_NAMES and video_dir.exists():
        ig_candidates = sorted(video_dir.glob("*shorts_instagram.mp4"))
        if ig_candidates:
            candidates = ig_candidates
    if candidates:
        video_name = quote(candidates[0].name)
        dl_name = _prefixed(candidates[0].name, _esc(f"{topic}_{lang}"))
        # WHY 다운로드 버튼을 추가했는지(2026-08-04, "동영상도 위젯같은데 다운받을
        # 수 있는 버튼을 넣는다던지 하면 될듯" 요청): ko CARD_TEMPLATE(_asset_link)엔
        # 이미 있던 "🎬 영상 다운로드 ↓" 링크가 이 경량 카드엔 없어서 <video controls>의
        # 브라우저 기본 메뉴에 의존해야 했다 — 같은 패턴(다운로드 파일명에 topic
        # 접두어)으로 명시적 버튼을 추가해 형식을 맞춘다.
        video_html = (
            f'<video src="{lang}/{video_name}" controls playsinline></video>'
            f'<a class="dl" href="{lang}/{video_name}" download="{dl_name}">🎬 영상 다운로드 ↓</a>'
        )
    else:
        video_html = '<div class="g-video-ph">🎬 영상 준비 중</div>'
    ta_id = f"g-cap-{lang}-{idx}"
    return f"""
<div class="plat-card">
  <h3>{_esc(platform['name'])}</h3>
  {video_html}
  <textarea id="{ta_id}" spellcheck="false">{_esc(platform['caption'])}</textarea>
  <div class="plat-actions">
    <button class="btn-copy" data-target="{ta_id}">캡션 복사</button>
    <a class="btn-go" href="{platform['url']}" target="_blank" rel="noopener" data-copy-target="{ta_id}">열기 →</a>
  </div>
</div>
"""


def _generate_unified_dashboard(base_topic: str, output_root: Path, data_root: Path) -> None:
    """topic 하나(예: "관절_1")의 언어(ko 포함) 전체를 탭 하나짜리 페이지로
    통합한다 — 언어마다 dashboard.html이 따로 있어서(+ko는 "한국" 버튼, 나머지는
    "Global" 버튼으로 갈라져 있던 것) 그때그때 다른 URL을 오가야 했던 것을,
    output/<topic>/dashboard.html 하나로 합친다(위 UNIFIED_PAGE_TEMPLATE WHY
    참고). 이미 있는 언어별 dashboard.html은 그대로 iframe으로 보여주고
    (완전히 동일한 폼 보장), 아직 영상이 없어 dashboard.html 자체가 없는 언어만
    가벼운 폴백 카드를 보여준다."""
    topic_data_root = data_root / base_topic
    if not topic_data_root.exists():
        return
    all_langs = sorted(p.name for p in topic_data_root.iterdir() if p.is_dir())
    # WHY ko를 맨 앞에 고정하는지: 사용자가 한국어 화자라 ko 탭이 기본으로
    # 먼저 보이는 게 자연스럽다 — 나머지는 알파벳 순서 그대로.
    langs = (["ko"] if "ko" in all_langs else []) + [l for l in all_langs if l != "ko"]

    tab_buttons = ""
    lang_panels = ""
    for i, lang in enumerate(langs):
        captions_path = topic_data_root / lang / "platform_captions.json"
        if not captions_path.exists():
            continue
        label = "한국어" if lang == "ko" else GLOBAL_LANG_LABELS.get(lang, lang.upper())
        panel_id = f"panel-{lang}"
        active = " active" if i == 0 else ""
        tab_buttons += f'<button class="lang-tab{active}" data-panel="{panel_id}">{_esc(label)}</button>\n'

        lang_dashboard = output_root / base_topic / lang / "dashboard.html"
        if lang_dashboard.exists():
            panel_body = f'<iframe class="dash-frame" src="{lang}/dashboard.html"></iframe>'
        else:
            try:
                spec = json.loads(captions_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                spec = {}
            cards = ""
            for idx, p in enumerate(spec.get("platforms", [])):
                if p["name"] in _UI_EXCLUDED_PLATFORMS:
                    continue
                cards += _light_platform_card(base_topic, lang, p, idx)
            panel_body = (
                f'<div class="lang-body">{cards}</div>' if cards
                else '<div class="empty">아직 준비된 콘텐츠가 없어요</div>'
            )
        lang_panels += f'<div class="lang-panel{active}" id="{panel_id}">{panel_body}</div>\n'

    if not tab_buttons:
        tab_buttons = ""
        lang_panels = '<div class="empty">아직 준비된 언어 콘텐츠가 없어요</div>'

    ko_captions = topic_data_root / "ko" / "platform_captions.json"
    title = base_topic
    if ko_captions.exists():
        try:
            title = json.loads(ko_captions.read_text(encoding="utf-8")).get("title", base_topic)
        except json.JSONDecodeError:
            pass

    html = UNIFIED_PAGE_TEMPLATE.format(
        title=_esc(title), tab_buttons=tab_buttons, lang_panels=lang_panels,
    )
    out_dir = output_root / base_topic
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dashboard.html").write_text(html, encoding="utf-8")


def generate(spec_path: str, card_news_dir: str, video_path: str | None, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    topic = spec.get("topic", spec["title"])
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
    dock_products = _dock_products(spec.get("products", []), _product_links_loaded, _naver_links_loaded)
    dock_products_bottom = _product_links_bottom_section(
        spec.get("products", []), _product_links_loaded, _naver_links_loaded
    )

    asset_imgs = sorted(Path(card_news_dir).glob("*.jpg")) if Path(card_news_dir).exists() else []
    # WHY quote(p.name): 파일명에 "?" 같은 URL 특수문자가 있으면(예: "돼지감자란?.jpg")
    # 브라우저가 쿼리스트링으로 오해해서 이미지가 깨진다(2026-07-30 확인).
    card_thumbs = "".join(f'<img src="card_news/{quote(p.name)}" alt="{_esc(p.stem)}">' for p in asset_imgs)

    keyword = re.sub(r"_\d+$", "", topic).replace("_", " ")
    unsplash_url = f"https://unsplash.com/s/photos/{quote(keyword)}"
    pexels_url = f"https://www.pexels.com/search/{quote(keyword)}/"

    has_video = bool(video_path and Path(video_path).exists())
    video_name = Path(video_path).name if video_path else "shorts.mp4"
    video_download_attr = _prefixed(video_name, _esc(topic))

    # WHY 인스타그램용 별도 영상을 자동으로 찾는지(2026-08-04, "인스타 숏츠로
    # 업로드할거를 양옆, 상하 더 키워가지고 만들어놓으면... 데스크탑에서 업로드해도
    # 딱 맞게"): 칠판 나무 프레임이 캔버스 가장자리에 여백 없이 꽉 차서 인스타
    # 릴스 UI(세이프존)와 겹쳐 잘려 보이는 문제 — build_instagram_safe_video()로
    # 안전 여백을 더한 별도 파일(<...>_shorts_instagram.mp4)을 같은 폴더에 만들어두면
    # 여기서 자동으로 찾아서 인스타그램 릴스 카드에만 그 파일을 연결한다. CLI
    # 인자를 안 늘리는 이유: video_path만 넘기면 나머지 호출부(테스트 등) 수정 없이
    # 그대로 호환된다.
    instagram_video_path = None
    if video_path:
        ig_candidates = sorted(Path(video_path).parent.glob("*shorts_instagram.mp4"))
        if ig_candidates:
            instagram_video_path = ig_candidates[0]
    instagram_video_name = instagram_video_path.name if instagram_video_path else video_name
    if has_video:
        video_block = f'<video src="{video_name}" controls playsinline></video><a class="dl" href="{video_name}" download="{video_download_attr}">영상 다운로드 ↓</a>'
        video_download_link = f'<a href="{video_name}" download="{video_download_attr}">🎬 영상 다운로드</a>'
    else:
        video_block = '<div style="width:260px;aspect-ratio:9/16;background:#f1e6dc;border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--ink-soft);font-size:13px;">영상 준비 중</div>'
        video_download_link = '<span style="color:var(--ink-soft);font-size:12px;padding:8px 10px;">🎬 영상 준비 중</span>'

    # WHY base64로 직접 embed: 원격 URL(src="https://...")은 네이버/티스토리 에디터가
    # 붙여넣기 시 외부 이미지를 거부하거나 못 불러오는 경우가 있었다(2026-07-30 확인) —
    # 이미지 바이트를 클립보드 HTML에 직접 박아넣으면 어느 사이트에 붙여도 안정적으로 뜬다.
    # WHY glob(2026-07-31): card_news.py가 이제 파일명 앞에 topic 접두어를 붙이므로
    # ("<topic>_00_표지.jpg") 정확한 이름을 하드코딩하지 않고 패턴으로 찾는다 — 접두어
    # 없는 예전 topic("00_표지.jpg")과도 둘 다 호환.
    cover_path = next(Path(card_news_dir).glob("*00_표지.jpg"), None)
    has_cover = cover_path is not None
    cover_url = ""
    if has_cover:
        cover_b64 = base64.b64encode(cover_path.read_bytes()).decode("ascii")
        cover_url = f"data:image/jpeg;base64,{cover_b64}"

    platforms_by_type: dict[str, list[dict]] = {t: [] for t in TYPE_ORDER}
    for p in spec["platforms"]:
        platforms_by_type.setdefault(p.get("type", "text"), []).append(p)

    idx = 0
    sections_html = ""
    for t in TYPE_ORDER:
        group = platforms_by_type.get(t, [])
        if not group:
            continue
        cards_html = ""
        for p in group:
            # WHY p.get("rich_paste") 대신 t=="text" 전체를 안 쓰는지: 쓰레드·페이스북은
            # 리치에디터가 아니라 단순 텍스트 입력창이라 HTML 붙여넣기로 이미지가 안 들어감
            # (2026-07-30 확인) — 실제로 되는 네이버블로그·티스토리 같은 블로그 에디터만
            # rich_paste: true로 표시해서 이 기능을 켠다.
            cover_attr = cover_url if (p.get("rich_paste") and has_cover) else ""
            # WHY has_video는 그대로 쓰고 video_name만 바꾸는지: instagram_video_name이
            # 안전 여백 버전이 없으면 이미 video_name으로 폴백해두므로(위 WHY 참고),
            # has_video까지 has_instagram_video로 바꾸면 안전 여백 버전이 아직
            # 없는 topic에서 원본 영상이 있는데도 "영상 준비 중"으로 잘못 뜬다.
            is_instagram_reels = p["name"] in _INSTAGRAM_REELS_NAMES
            card_video_name = instagram_video_name if is_instagram_reels else video_name
            cards_html += CARD_TEMPLATE.format(
                name=_esc(p["name"]),
                url=p["url"],
                idx=idx,
                caption=_esc(p["caption"]),
                type=t,
                type_label=TYPE_LABEL[t],
                action=_esc(p.get("action", "")),
                asset_link=_asset_link(t, has_video, card_video_name, topic, cover_path.name if cover_path else None),
                done_key=quote(p["name"]),
                cover_attr=cover_attr,
                copy_label="캡션+이미지 복사" if cover_attr else "캡션 복사",
                no_caption_link_attr="1" if p.get("no_caption_link") else "",
                naver_button_attr="1" if p.get("network") == "naver" else "",
                profile_note_attr="1" if p.get("add_profile_note") else "",
                suppress_product_block_attr="1" if p.get("suppress_product_block") else "",
                comment_dm_attr="1" if p.get("comment_dm_automation") else "",
                link_in_comment_attr="1" if p.get("link_in_comment") else "",
            )
            idx += 1
        sections_html += SECTION_TEMPLATE.format(section_title=TYPE_SECTION_TITLE[t], cards=cards_html)

    card_image_names_js = json.dumps([quote(p.name) for p in asset_imgs])

    html = PAGE_TEMPLATE.format(
        title=_esc(spec["title"]), video_block=video_block, card_thumbs=card_thumbs,
        platform_sections=sections_html, unsplash_url=unsplash_url, pexels_url=pexels_url,
        topic=quote(topic), dock_products=dock_products, dock_products_bottom=dock_products_bottom,
        video_download_link=video_download_link,
        card_image_names_js=card_image_names_js,
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
