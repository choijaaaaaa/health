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
    const text = document.getElementById(btn.dataset.target).value.split(AUTO_LINKS_START).join("").split(AUTO_LINKS_END).join("");
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
    const text = target.value.split(AUTO_LINKS_START).join("").split(AUTO_LINKS_END).join("");
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

function _stripAutoLinks(text) {{
  const startIdx = text.indexOf(AUTO_LINKS_START);
  if (startIdx === -1) return text;
  const endIdx = text.indexOf(AUTO_LINKS_END, startIdx);
  const before = text.slice(0, startIdx).replace(/\\n+$/, "");
  const after = endIdx === -1 ? "" : text.slice(endIdx + AUTO_LINKS_END.length).replace(/^\\n+/, "");
  if (!before) return after;
  if (!after) return before;
  return before + "\\n\\n" + after;
}}

// WHY 마커/줄바꿈을 여기서 안 붙이는지(2026-08-02 리팩터): 예전엔 이 함수들이 직접
// "\\n\\n"+마커까지 붙여서 반환했는데, 그러면 "캡션 맨 끝에 이어붙이기"만 가능했다
// — 이제 삽입 위치(제목 바로 다음)를 applyProductLinks 쪽에서 결정해야 해서, 이
// 함수들은 순수 내용만 반환하고 마커·위치는 호출부에서 감싼다.
function _buildLinkBlock(hasNaverButton) {{
  if (hasNaverButton) {{
    // WHY URL은 안 넣지만 상품명은 넣는지(2026-07-31 정정, 2026-08-01 단순화): 네이버
    // 클립처럼 에디터에 진짜 "상품" 버튼이 있는 곳(data-naver-button="1")은 URL을
    // 본문에 붙여넣는 방식이 아니라 그 버튼으로 직접 추가해야 한다(2026-07-30 확인).
    // 예전엔 "네이버 링크 입력창에 뭐라도 입력해야" 그 상품이 목록에 포함됐는데,
    // 그 입력창 자체가 성가시기만 하고 실제로 쓰는 링크도 아니었다는 피드백(2026-08-01)
    // 으로 입력창을 없애고 이 topic의 전체 상품을 조건 없이 나열한다.
    const products = [];
    document.querySelectorAll('.product-link-input[data-market="coupang"]').forEach(inp => products.push(inp.dataset.product));
    if (products.length === 0) return "";
    return "🔵 상품: " + products.join(", ") + "\\n\\n" + NAVER_DISCLOSURE;
  }}
  const lines = [];
  document.querySelectorAll('.product-link-input[data-market="coupang"]').forEach(inp => {{
    const url = inp.value.trim();
    if (url) lines.push("🔗 " + inp.dataset.product + " 구매: " + url);
  }});
  if (lines.length === 0) return "";
  return lines.join("\\n") + "\\n\\n" + COUPANG_DISCLOSURE;
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
function _buildCtaBlock(hasCommentDm, linkInComment) {{
  // WHY linkInComment(2026-08-02, "댓글에는 링크 넣어도 돼?"): 쓰레드·페이스북처럼
  // 인포크 자동화도 없고 프로필 링크 도달 문제도 있는 플랫폼은, 캡션 본문엔 링크를
  // 안 넣고(메타 계열이 아웃바운드 링크 있는 게시물 도달을 낮춘다고 알려져 있음)
  // "댓글에 남겨둘게요"로 안내한다 — 실제 링크는 게시자가 게시 직후 댓글로 직접
  // 추가하는 수동 흐름(이 파이프라인은 원래 전부 수동 게시라 흐름이 자연스럽게 이어짐).
  if (linkInComment) {{
    return "🔗 구매 링크는 댓글에 남겨둘게요!\\n\\n" + COUPANG_DISCLOSURE;
  }}
  if (!hasCommentDm) {{
    return "🔗 상품 링크는 프로필에서 확인해주세요!\\n\\n" + COUPANG_DISCLOSURE;
  }}
  // WHY "이라고"(받침 있는 조사) 고정(2026-08-01 오타 수정): COMMENT_KEYWORD가
  // 항상 "쿠팡"(받침 ㅇ으로 끝남)으로 고정된 이후로 "라고"를 쓰면 "쿠팡라고"처럼
  // 문법이 틀린다 — 키워드가 이 정책 밖에서 바뀔 일이 없으므로 조사를 하드코딩한다.
  const cta = `💬 댓글에 "${{COMMENT_KEYWORD}}"이라고 치시면 제품 목록으로 이동할 수 있는 링크 바로 전송해드릴게요!`;
  return cta + "\\n\\n" + COUPANG_DISCLOSURE;
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
    const suppressBlock = card.dataset.suppressProductBlock === "1";
    let block = suppressBlock ? "" : (noCaptionLink ? _buildCtaBlock(hasCommentDm, linkInComment) : _buildLinkBlock(hasNaverButton));
    // WHY profile-note(2026-07-31): 유튜브 쇼츠 설명란 링크는 클릭이 안 된다는
    // 피드백 — 그렇다고 링크 텍스트 자체를 빼는 게 아니라(요청: "링크도 있지만
    // 프로필도 안내해주는 걸로"), 링크는 그대로 두고 프로필 확인 안내를 덧붙인다.
    if (block && card.dataset.profileNote === "1") {{
      block += "\\n\\n🔗 링크가 눌리지 않으면 채널 프로필에서 확인해주세요";
    }}
    const stripped = _stripAutoLinks(box.value);
    if (!block) {{
      box.value = stripped;
      return;
    }}
    // WHY 제목 바로 다음에 삽입(2026-08-02, 공정위 표시광고 지침 — 고지문이
    // "게시물 첫 부분/제목 근처"에 있어야 함): 예전엔 이 블록을 캡션 맨 끝에
    // 이어붙여서 고지문이 항상 스크롤을 다 내려야 보이는 위치에 있었다. 첫 줄
    // (훅/제목) 바로 다음, 본문 시작 전에 끼워 넣는다.
    const wrapped = AUTO_LINKS_START + block + AUTO_LINKS_END;
    const firstBreak = stripped.indexOf("\\n");
    box.value = firstBreak === -1
      ? stripped + "\\n\\n" + wrapped
      : stripped.slice(0, firstBreak) + "\\n\\n" + wrapped + stripped.slice(firstBreak);
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


def _dock_products(products: list[str], product_links: dict[str, str] | None = None) -> str:
    if not products:
        return ""
    product_links = product_links or {}
    rows = ""
    for idx, name in enumerate(products):
        coupang_url = f"https://www.coupang.com/np/search?component=&q={quote(name)}&channel=user"
        link = product_links.get(name, "")
        rows += DOCK_PRODUCT_ROW_TEMPLATE.format(
            name=_esc(name), coupang_url=coupang_url, name_attr=_esc(name), idx=idx,
            link_value=_esc(link), row_class=" linked" if link else "",
        )
    # WHY 네이버 언급 없음(2026-08-01): 네이버 블로그도 브랜드커넥트 대신 쿠팡 링크를
    # 쓰기로 바뀌면서 상품 링크는 쿠팡 하나만 필요해졌다 — 네이버 클립은 이 링크값과
    # 무관하게 상품명이 자동으로 들어가므로 별도 안내가 필요 없다.
    return (
        '<div class="dock-section"><h4>상품 링크</h4>'
        f'{rows}'
        '<p class="dock-hint">쿠팡 링크를 붙여넣으면 아래 각 플랫폼 카드 캡션에 자동 반영돼요.</p>'
        '</div>'
    )


def _update_topics_index(out_path: str):
    """WHY(2026-07-31): 매번 output/<topic>/dashboard.html 전체 경로를 외워서 들어가야
    했다("루트로 들어가면 안되나?") — output/ 밑의 모든 대시보드를 스캔해서
    output/topics.json을 갱신하면, 루트 index.html이 이걸 읽어 목록을 보여줄 수 있다."""
    out_dir = Path(out_path).resolve().parent
    output_root = out_dir.parent
    topics = []
    for dash in sorted(output_root.glob("*/dashboard.html")):
        topic = dash.parent.name
        title = topic
        caption_path = output_root.parent / "data" / topic / "platform_captions.json"
        if caption_path.exists():
            try:
                title = json.loads(caption_path.read_text()).get("title", topic)
            except (json.JSONDecodeError, OSError):
                pass
        # WHY(2026-08-01): 목록에서 폴더명만 보고는 어떤 topic인지 한눈에 안 들어온다는
        # 피드백 — 표지 카드(항상 "<topic>_00_표지.jpg")가 있으면 썸네일로 같이 보여준다.
        cover_path = dash.parent / "card_news" / f"{topic}_00_표지.jpg"
        thumbnail = f"output/{quote(topic)}/card_news/{quote(cover_path.name)}" if cover_path.exists() else None
        topics.append({
            "topic": topic, "title": title, "url": f"output/{quote(topic)}/dashboard.html",
            "thumbnail": thumbnail,
        })
    topics.sort(key=lambda t: t["topic"])
    (output_root / "topics.json").write_text(json.dumps(topics, ensure_ascii=False, indent=2))


def generate(spec_path: str, card_news_dir: str, video_path: str | None, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    topic = spec.get("topic", spec["title"])

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
    dock_products = _dock_products(spec.get("products", []), _load_product_links())

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
            cards_html += CARD_TEMPLATE.format(
                name=_esc(p["name"]),
                url=p["url"],
                idx=idx,
                caption=_esc(p["caption"]),
                type=t,
                type_label=TYPE_LABEL[t],
                action=_esc(p.get("action", "")),
                asset_link=_asset_link(t, has_video, video_name, topic, cover_path.name if cover_path else None),
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
        topic=quote(topic), dock_products=dock_products, video_download_link=video_download_link,
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
