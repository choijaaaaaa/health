#!/usr/bin/env python3
"""해결책 칸용 '확인할 것' 메모지 — 브랜드 없이 종이에 손글씨로 적고, 대본이 말하는 줄을 차례로 호박색 테두리로 짚는다.

WHY(2026-10-07 사용자 "설마 실제 제품을 그대로 갖다 박은 거야? 이러면 너무 광고가 되는데" → "뭔가 종이 같은 거에 너가 글로
써서 표현해서 설명할 방법 없어?"): 라벨 칸에 링크한 상품 사진을 그대로 넣었더니 설명 중간에 특정 브랜드가 크게 떠 광고처럼
보였다. 고르는 기준(기능성 표시·농도·전성분)을 브랜드 없이 메모로 적는다. 글자는 코드로 쓴다(AI가 그린 글자는 뭉개진다).
실제 상품 사진은 마지막 칠판의 제품 사진·제품 보러 가기에만 남는다.

    .venv/bin/python3 scripts/make_note_card.py <out.mp4> "라벨에서 볼 것" "주름개선 기능성화장품" "레티놀 0.1%"
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets_library" / "fonts" / "Gaegu-Bold.ttf"   # 칠판 자막과 같은 손글씨
CARD_W, CARD_H = 900, 620
BG = (22, 32, 44)
PAPER = (246, 240, 226)
INK = (48, 52, 64)


def _fit_font(d: ImageDraw.ImageDraw, lines: list[str], width: int, start: int) -> ImageFont.FreeTypeFont:
    """가장 긴 줄이 종이 폭에 들어오는 가장 큰 글자 크기."""
    size = start
    while size > 30:
        f = ImageFont.truetype(str(FONT), size)
        if max(d.textlength(t, font=f) for t in lines) <= width:
            return f
        size -= 2
    return ImageFont.truetype(str(FONT), size)


def _check(d: ImageDraw.ImageDraw, x: float, y: float, s: float) -> None:
    """펜으로 그은 체크 — 손글씨 글꼴엔 ✓ 글리프가 없다(빈칸으로 나왔다, 2026-10-07)."""
    d.line([(x, y + s * 0.55), (x + s * 0.38, y + s * 0.9), (x + s, y + s * 0.1)], fill=INK, width=max(4, int(s * 0.12)), joint="curve")


def card(title: str, lines: list[str], out_png: Path) -> list[str]:
    """메모지 이미지를 그리고, 줄마다 make_label_clip --box 값(사진 안 비율)을 돌려준다."""
    im = Image.new("RGB", (CARD_W, CARD_H), BG)
    d = ImageDraw.Draw(im)
    pw = int(CARD_W * 0.86)
    lf = _fit_font(d, lines, pw - 150, 64)
    tf = ImageFont.truetype(str(FONT), min(62, lf.size + 6))
    lh = int(lf.size * 1.7)
    ph = min(int(CARD_H * 0.92), 110 + lh * len(lines) + 40)
    px, py = (CARD_W - pw) // 2, (CARD_H - ph) // 2
    shadow = Image.new("L", (CARD_W, CARD_H), 0)
    ImageDraw.Draw(shadow).rounded_rectangle([px + 10, py + 14, px + pw + 10, py + ph + 14], radius=18, fill=150)
    im.paste((8, 12, 18), (0, 0), shadow.filter(ImageFilter.GaussianBlur(14)))
    d.rounded_rectangle([px, py, px + pw, py + ph], radius=18, fill=PAPER)
    y = py + 100
    while y < py + ph - 16:                     # 공책 줄
        d.line([(px + 30, y), (px + pw - 30, y)], fill=(222, 214, 196), width=2)
        y += lh
    d.text((px + 44, py + 22), title, font=tf, fill=INK)
    boxes, y = [], py + 100 + (lh - lf.size) // 2 - 6
    for line in lines:
        _check(d, px + 46, y + lf.size * 0.15, lf.size * 0.7)
        tx = px + 46 + lf.size * 0.95
        bb = d.textbbox((tx, y), line, font=lf)
        d.text((tx, y), line, font=lf, fill=INK)
        x0, y0, x1, y1 = px + 34, bb[1] - 10, bb[2] + 12, bb[3] + 10
        boxes.append(f"{x0 / CARD_W:.3f},{y0 / CARD_H:.3f},{(x1 - x0) / CARD_W:.3f},{(y1 - y0) / CARD_H:.3f}")
        y += lh
    im.save(out_png)
    return boxes


def main() -> None:
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    out, title, lines = sys.argv[1], sys.argv[2], sys.argv[3:]
    with tempfile.TemporaryDirectory() as td:
        png = Path(td) / "card.png"
        boxes = card(title, lines, png)
        cmd = [sys.executable, str(ROOT / "scripts" / "make_label_clip.py"), str(png), out, "--zoom", "1.12",
               "--seconds", str(max(5.0, 2.0 + 2.0 * len(lines)))]
        for b in boxes:
            cmd += ["--box", b]
        subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()
