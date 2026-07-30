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
<div class="dock-product-row" id="dock-row-{idx}">
  <div class="dock-product-head">
    <button class="row-toggle" data-row="dock-row-{idx}" title="링크 넣기">🔗</button>
    <span class="dock-product-name">{name}</span>
  </div>
  <div class="dock-product-market">
    <a href="{coupang_url}" target="_blank" rel="noopener">🛒 쿠팡 검색</a>
    <input type="text" class="product-link-input" data-market="coupang" data-product="{name_attr}" placeholder="쿠팡 링크 붙여넣고 Enter">
  </div>
  <div class="dock-product-market">
    <a href="{naver_url}" target="_blank" rel="noopener">🔵 브랜드커넥트 검색</a>
    <input type="text" class="product-link-input" data-market="naver" data-product="{name_attr}" placeholder="네이버 링크 붙여넣고 Enter">
  </div>
</div>
"""

MARKET_TOGGLE_TEMPLATE = """
<div class="market-toggle" data-market-key="{market_key}" data-default-market="{default_market}">
  <span class="market-label">상품 링크</span>
  <button class="market-btn{coupang_active}" data-market="coupang">🛒 쿠팡</button>
  <button class="market-btn{naver_active}" data-market="naver">🔵 네이버</button>
</div>
"""

CARD_TEMPLATE = """
<div class="platform-card" data-done-key="{done_key}" data-market-key="{market_key}">
  <div class="platform-head">
    <div class="platform-name-wrap">
      <span class="type-badge badge-{type}">{type_label}</span>
      <h3>{name}</h3>
    </div>
    <div class="head-actions">
      <label class="done-check">
        <input type="checkbox" class="done-toggle" data-key="{done_key}">
        <span>완료</span>
      </label>
      <a class="btn-go" href="{url}" target="_blank" rel="noopener">열기 →</a>
    </div>
  </div>
  {market_toggle}
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
  .product-link-input {{
    display: block; width: 100%; border: 1px solid var(--rule); border-radius: 6px;
    padding: 7px 9px; font-size: 12px; font-family: inherit; color: var(--ink); box-sizing: border-box;
  }}
  .product-link-input:focus {{ outline: 2px solid var(--accent-soft); }}
  .market-toggle {{ display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }}
  .market-label {{ font-size: 11px; color: var(--ink-soft); font-weight: 700; }}
  .market-btn {{
    border: 1px solid var(--rule); background: var(--panel); color: var(--ink-soft);
    font-size: 12px; font-weight: 700; padding: 6px 12px; border-radius: 999px; cursor: pointer;
  }}
  .market-btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
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
const downloadAllBtn = document.getElementById("downloadAllCards");
if (downloadAllBtn) {{
  downloadAllBtn.addEventListener("click", () => {{
    const originalLabel = downloadAllBtn.textContent;
    downloadAllBtn.textContent = "다운로드 중…";
    CARD_IMAGE_NAMES.forEach((name, i) => {{
      setTimeout(() => {{
        const a = document.createElement("a");
        a.href = "card_news/" + name;
        a.download = "";
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
    // WHY replace: 링크 구간 안내 줄은 실제 게시물에 들어가면 안 되는 내부 표시일
    // 뿐이라 복사할 때만 그 줄을 지우고 링크·고지문구 내용은 그대로 남긴다.
    const text = document.getElementById(btn.dataset.target).value.replace(AUTO_LINKS_MARKER_LINE + "\\n", "");
    const cover = btn.dataset.cover;
    if (cover && window.ClipboardItem) {{
      const bodyHtml = text.split("\\n").map(line => line.trim() ? `<p>${{_escapeHtml(line)}}</p>` : "<br>").join("");
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
const LINK_STORAGE_PREFIX = "hs_link_{topic}_";
// WHY 사람이 읽을 수 있는 안내 줄: 대시보드에서 캡션을 볼 때 이게 뭔지 바로 알 수 있게
// (2026-07-30 "이건 뭐야" 피드백) — 복사 버튼을 누르면 이 줄만 자동으로 빠지고
// 그 아래 링크·고지문구는 그대로 남는다. 정규식 대신 indexOf/slice만 써서
// 이스케이프 실수 위험을 없앤다(2026-07-30 \\n 이스케이프 버그 재발 방지).
const AUTO_LINKS_MARKER_LINE = "▼ 자동 추가된 상품 링크 (복사하면 이 줄만 자동으로 빠져요) ▼";

function _stripAutoLinks(text) {{
  const idx = text.indexOf(AUTO_LINKS_MARKER_LINE);
  if (idx === -1) return text;
  return text.slice(0, idx).replace(/\\n\\n$/, "");
}}

function _buildMarketBlock(market) {{
  const lines = [];
  document.querySelectorAll(`.product-link-input[data-market="${{market}}"]`).forEach(inp => {{
    const url = inp.value.trim();
    if (url) lines.push("🔗 " + inp.dataset.product + " 구매: " + url);
  }});
  if (lines.length === 0) return "";
  const disclosure = market === "coupang" ? COUPANG_DISCLOSURE : NAVER_DISCLOSURE;
  return "\\n\\n" + AUTO_LINKS_MARKER_LINE + "\\n" + lines.join("\\n") + "\\n\\n" + disclosure;
}}

function applyProductLinks() {{
  const coupangBlock = _buildMarketBlock("coupang");
  const naverBlock = _buildMarketBlock("naver");
  document.querySelectorAll(".caption-box").forEach(box => {{
    const card = box.closest(".platform-card");
    const activeBtn = card.querySelector(".market-toggle .market-btn.active");
    const market = activeBtn ? activeBtn.dataset.market : null;
    const block = market === "naver" ? naverBlock : market === "coupang" ? coupangBlock : "";
    const stripped = _stripAutoLinks(box.value);
    box.value = block ? stripped + block : stripped;
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

const MARKET_STATE_PREFIX = "hs_market_{topic}_";
document.querySelectorAll(".market-toggle").forEach(toggle => {{
  const storageKey = MARKET_STATE_PREFIX + toggle.dataset.marketKey;
  const saved = localStorage.getItem(storageKey);
  if (saved) {{
    toggle.querySelectorAll(".market-btn").forEach(b => b.classList.toggle("active", b.dataset.market === saved));
  }}
  toggle.querySelectorAll(".market-btn").forEach(btn => {{
    btn.addEventListener("click", () => {{
      toggle.querySelectorAll(".market-btn").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      localStorage.setItem(storageKey, btn.dataset.market);
      applyProductLinks();
    }});
  }});
}});

applyProductLinks();

const STORAGE_PREFIX = "hs_done_{topic}_";
document.querySelectorAll(".done-toggle").forEach(cb => {{
  const storageKey = STORAGE_PREFIX + cb.dataset.key;
  const card = cb.closest(".platform-card");
  if (localStorage.getItem(storageKey) === "1") {{
    cb.checked = true;
    card.classList.add("is-done");
  }}
  cb.addEventListener("change", () => {{
    if (cb.checked) {{
      localStorage.setItem(storageKey, "1");
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


def _asset_link(platform_type: str, has_video: bool, video_name: str) -> str:
    if platform_type == "video":
        if has_video:
            return f'<a class="asset-link" href="{video_name}" download>🎬 영상 다운로드</a>'
        return '<span class="asset-link disabled">🎬 영상 준비 중 — 나중에 다시 확인</span>'
    if platform_type == "cards":
        return '<a class="asset-link" href="#card-gallery">🖼 위 카드뉴스 미리보기로 이동 ↑</a>'
    return '<a class="asset-link" href="card_news/00_표지.jpg" download>🖼 표지 이미지 다운로드 (선택)</a>'


def _dock_products(products: list[str], affiliate_path: Path) -> str:
    if not products:
        return ""
    affiliate = json.loads(affiliate_path.read_text()) if affiliate_path.exists() else {}
    creator_id = affiliate.get("naver_brandconnect_id", "")
    rows = ""
    for idx, name in enumerate(products):
        naver_url = f"https://brandconnect.naver.com/{creator_id}/affiliate/products/search?query={quote(name)}&tab=product"
        coupang_url = f"https://www.coupang.com/np/search?component=&q={quote(name)}&channel=user"
        rows += DOCK_PRODUCT_ROW_TEMPLATE.format(
            name=_esc(name), naver_url=naver_url, coupang_url=coupang_url, name_attr=_esc(name), idx=idx,
        )
    return (
        '<div class="dock-section"><h4>상품 링크</h4>'
        f'{rows}'
        '<p class="dock-hint">쿠팡/네이버 링크를 각각 붙여넣으면, 아래 각 플랫폼 카드에서 고른 쪽(쿠팡/네이버)에 맞춰 고지 문구와 함께 자동 반영돼요.</p>'
        '</div>'
    )


def generate(spec_path: str, card_news_dir: str, video_path: str | None, out_path: str):
    spec = json.loads(Path(spec_path).read_text())
    topic = spec.get("topic", spec["title"])
    affiliate_path = Path(__file__).resolve().parent.parent / "data" / "affiliate_accounts.json"
    affiliate = json.loads(affiliate_path.read_text()) if affiliate_path.exists() else {}
    disclosure = affiliate.get("disclosure", {})
    has_products = bool(spec.get("products"))
    dock_products = _dock_products(spec.get("products", []), affiliate_path)

    asset_imgs = sorted(Path(card_news_dir).glob("*.jpg")) if Path(card_news_dir).exists() else []
    # WHY quote(p.name): 파일명에 "?" 같은 URL 특수문자가 있으면(예: "돼지감자란?.jpg")
    # 브라우저가 쿼리스트링으로 오해해서 이미지가 깨진다(2026-07-30 확인).
    card_thumbs = "".join(f'<img src="card_news/{quote(p.name)}" alt="{_esc(p.stem)}">' for p in asset_imgs)

    keyword = re.sub(r"_\d+$", "", topic).replace("_", " ")
    unsplash_url = f"https://unsplash.com/s/photos/{quote(keyword)}"
    pexels_url = f"https://www.pexels.com/search/{quote(keyword)}/"

    has_video = bool(video_path and Path(video_path).exists())
    video_name = Path(video_path).name if video_path else "shorts.mp4"
    if has_video:
        video_block = f'<video src="{video_name}" controls playsinline></video><a class="dl" href="{video_name}" download>영상 다운로드 ↓</a>'
        video_download_link = f'<a href="{video_name}" download>🎬 영상 다운로드</a>'
    else:
        video_block = '<div style="width:260px;aspect-ratio:9/16;background:#f1e6dc;border-radius:12px;display:flex;align-items:center;justify-content:center;color:var(--ink-soft);font-size:13px;">영상 준비 중</div>'
        video_download_link = '<span style="color:var(--ink-soft);font-size:12px;padding:8px 10px;">🎬 영상 준비 중</span>'

    # WHY base64로 직접 embed: 원격 URL(src="https://...")은 네이버/티스토리 에디터가
    # 붙여넣기 시 외부 이미지를 거부하거나 못 불러오는 경우가 있었다(2026-07-30 확인) —
    # 이미지 바이트를 클립보드 HTML에 직접 박아넣으면 어느 사이트에 붙여도 안정적으로 뜬다.
    cover_path = Path(card_news_dir) / "00_표지.jpg"
    has_cover = cover_path.exists()
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
            cover_attr = cover_url if (t == "text" and has_cover) else ""
            market_key = quote(p["name"])
            default_market = "naver" if p.get("network") == "naver" else "coupang"
            market_toggle = ""
            if has_products:
                market_toggle = MARKET_TOGGLE_TEMPLATE.format(
                    market_key=market_key,
                    default_market=default_market,
                    coupang_active=" active" if default_market == "coupang" else "",
                    naver_active=" active" if default_market == "naver" else "",
                )
            cards_html += CARD_TEMPLATE.format(
                name=_esc(p["name"]),
                url=p["url"],
                idx=idx,
                caption=_esc(p["caption"]),
                type=t,
                type_label=TYPE_LABEL[t],
                action=_esc(p.get("action", "")),
                asset_link=_asset_link(t, has_video, video_name),
                done_key=quote(p["name"]),
                cover_attr=cover_attr,
                copy_label="캡션+이미지 복사" if cover_attr else "캡션 복사",
                market_key=market_key,
                market_toggle=market_toggle,
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
    )
    Path(out_path).write_text(html)
    print(f"대시보드 생성 완료: {out_path}")


if __name__ == "__main__":
    spec_path, card_news_dir, video_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    generate(spec_path, card_news_dir, video_path, out_path)
