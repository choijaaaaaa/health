# 기존 칠판 숏츠의 지정 구간을 반투명 인체 클립(Flow)으로 갈아끼운다 — 새 포맷 시험용.
# WHY 재조립이 아니라 덧씌우기인지: 칠판본(shorts.mp4)은 이미 나레이션·자막·CTA·광고표시가 맞춰진
# 완성본이라, 그 위에 클립을 시간 구간으로 overlay하면(끝나면 eof_action=pass로 칠판이 다시 드러남)
# 타이밍을 새로 맞출 게 없다. 클립이 칠판을 가리는 구간엔 칠판에 박힌 자막·광고표시가 같이 가려지므로
# 그 둘은 클립 위에 다시 얹는다 — 광고표시는 공정위 "처음부터 끝까지 노출" 의무다.
#
# 사용: .venv/bin/python3 scripts/xray_splice.py <topic> <영상시각:클립.mp4> [...] [--out 파일명]
#   예) scripts/xray_splice.py 소화_9 0.2:assets_library/xray/output/pilot_B2.mp4 6.2:assets_library/xray/output/pilot_A.mp4
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.video_assembler import (NAVER_SAFE_RIGHT, NAVER_SAFE_TOP, W, H, XRAY_PANEL,  # noqa: E402
                                 _make_ad_tag_png, _make_chalk_caption_png, chunk_caption_entries)

TITLE_CARD_SEC = 0.2          # assemble() 기본값 — 나레이션은 이만큼 늦게 시작한다
# 클립 위 자막 — 머리 높이. 1차 시험(y=1250)에서 빛나는 위·장을 정통으로 덮었다: 인체가 화면을 세로로
# 꽉 채워서 어디에 둬도 몸과 겹치는데, 강조 부위(몸통)만은 피해야 한다. 광고 표시(y≈120) 바로 아래.
CAPTION_CENTER_Y = 330
CAPTION_MAX_LINES = 2         # 칠판은 한 문장을 통째로 띄우지만 클립 위에선 5줄이 돼 화면을 덮었다
CLIP_SFX_VOLUME = 0.35        # Flow 클립 자체 효과음(험·심장박동) — 나레이션을 덮지 않게 낮춘다


def _has_audio(path: Path) -> bool:
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                        "-of", "csv=p=0", str(path)], capture_output=True, text=True)
    return bool(r.stdout.strip())


def _dur(path: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                        str(path)], capture_output=True, text=True, check=True)
    return float(r.stdout)


def _srt(path: Path) -> list[tuple[float, float, str]]:
    cues = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        ls = block.strip().split("\n")
        m = re.match(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)", ls[1]) if len(ls) >= 3 else None
        if m:
            g = [int(x) for x in m.groups()]
            cues.append((g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000,
                         g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000, " ".join(ls[2:])))
    return cues


def _chunk(cues: list[tuple[float, float, str]]) -> list[tuple[float, float, str]]:
    """문장을 쉼표 단위로 잘라 CAPTION_MAX_LINES 이하 조각으로 만들고, 글자 수 비례로 시간을 나눈다.
    나레이션 타이밍 원본이 문장 단위라 조각 경계는 근사치다(글자 수 ∝ 발화 시간)."""
    from PIL import ImageDraw, ImageFont
    from lib.video_assembler import _chalk_font_for_lang, _wrap_text_for_lang
    font = ImageFont.truetype(_chalk_font_for_lang("kor"), 68)
    d = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    fits = lambda t: len(_wrap_text_for_lang(d, t, font, 720, "kor")) <= CAPTION_MAX_LINES
    out = []
    for cs, ce, text in cues:
        # 단어 단위로 두 줄이 찰 때까지 채운다. 쉼표 우선 분할은 "위염," 한 단어짜리 조각이 생기고
        # 쉼표 없는 긴 구간은 4줄로 남았다(2차 시험). 조각이 넘치기 직전 쉼표가 있으면 거기서 끊는다.
        words = text.split()
        pieces, cur = [], []
        for w in words:
            if cur and not fits(" ".join(cur + [w])):
                # 구절이 끝나는 어절 뒤에서 끊는다 — 그냥 넘치는 자리에서 자르면 "이 세 / 가지부터"처럼
                # 한 덩어리 말이 쪼개졌다(2026-09-19). 쉼표·연결어미로 끝나는 마지막 어절을 찾는다.
                ends = (",", "다면", "라면", "으면", "하면", "고", "서", "는데", "지만")
                cut = max((k for k, x in enumerate(cur) if x.endswith(ends)), default=None)
                if cut is not None and cut >= len(cur) // 3:
                    pieces.append(" ".join(cur[:cut + 1])); cur = cur[cut + 1:]
                else:
                    pieces.append(" ".join(cur)); cur = []
            cur.append(w)
        if cur:
            pieces.append(" ".join(cur))
        total = sum(len(p) for p in pieces) or 1
        t = cs
        for p in pieces:
            dt = (ce - cs) * len(p) / total
            out.append((t, t + dt, p)); t += dt
    return out


def _caption_png(text: str, out: Path) -> Image.Image:
    """칠판 자막과 같은 폰트·폭으로 그리되, 밝게 빛나는 인체 위에서도 읽히게 어두운 번짐을 깐다.
    칠판 위에선 배경이 이미 어두워 그림자만으로 충분했지만 클립 위에선 흰 글자가 청록 몸에 묻힌다."""
    _make_chalk_caption_png(text, out, lang="kor", max_width=720)
    fg = Image.open(out).convert("RGBA")
    halo = Image.new("RGBA", fg.size, (0, 0, 0, 0))
    halo.putalpha(fg.getchannel("A").point(lambda a: 200 if a > 20 else 0))
    halo = halo.filter(ImageFilter.GaussianBlur(10))
    Image.alpha_composite(halo, fg).save(out)
    return fg


PANEL_SPEED = 0.5      # 기전 클립 재생 속도 — "보는 사람들이 나이대가 좀 있는분들이 많아서… 느린게 더좋아"(2026-09-19)


def _panel_track(topic, td, inputs, fc, cur, n, ad_png, covered=None):  # ad_png=None이면 광고 표시를 얹지 않는다
    """xray.json timeline 구간마다 위쪽 영상 칸에 기전 클립을 반복 재생한다.

    WHY 반복·저속인지(2026-09-19 "그 영상을 느리게 길게 빼고 여러번 반복재생을 하자"): 4초 클립을 한 번 틀고
    칠판(부위 맥동)으로 돌아가면 칸이 자꾸 바뀌어 산만하다. 항목을 설명하는 동안은 그 항목의 기전을 계속
    보여준다. 클립마다 칸 크기로 잘라 반속으로 늘린 파일을 먼저 만들고(`minterpolate`로 부드럽게), 그 파일을
    구간 길이만큼 반복 입력한다 — 필터 안에서 반복하면 보간된 프레임 전체를 메모리에 쌓아야 해서 무겁다.
    WHY "위" 라벨을 여기 얹는지: 기전 장면만으로는 어느 장기인지 모르므로 부위 이름을 칸 위에 계속 둔다
    ("새로뽑은세개영상에 위라고 적어놓고 사람들 이해를 돕는게 훨씬낫지")."""
    from lib.xray_timeline import resolve
    from lib.video_assembler import _make_pill_label_png
    cfg = json.loads((ROOT / "data" / topic / "xray.json").read_text(encoding="utf-8"))
    tl = resolve(topic)
    if not tl:
        return cur, n
    # 결론 구간은 영상 칸 없는 칠판으로 가므로 패널 트랙은 결론 구절 직전까지만
    summary = cfg.get("summary_from")
    if summary:
        from lib.xray_timeline import _cues, _time_of
        t_sum = _time_of(summary, _cues(topic))
        tl = [dict(r, end=min(r["end"], t_sum)) for r in tl if r["start"] < t_sum - 0.05]
    px, py, pw, ph = XRAY_PANEL
    focus = cfg.get("mech_focus", {})
    def _is_covered(r) -> bool:
        t0 = round((r["start"] + TITLE_CARD_SEC) * 30) / 30
        t1 = round((r["end"] + TITLE_CARD_SEC) * 30) / 30
        return any(t0 < e and s < t1 for s, e in (covered or []))

    made = {}
    for r in tl:
        name = r["mech"]
        # 덮을 구간의 기전은 느리게 늘린 파일을 만들 필요가 없다 — minterpolate이 구간마다 몇십 초씩 걸린다
        if name in made or _is_covered(r):
            continue
        src = ROOT / "assets_library" / "xray" / "output" / f"{name}.mp4"
        f = focus.get(name, 0.35)
        out = Path(td) / f"slow_{name}.mp4"
        subprocess.run(["ffmpeg", "-y", "-i", str(src), "-an", "-vf",
                        f"scale={pw}:-2,crop={pw}:{ph}:0:'min(ih-{ph},ih*{f})',"
                        f"setpts={1 / PANEL_SPEED:.3f}*PTS,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc",
                        "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)],
                       check=True, capture_output=True)
        made[name] = out
    mask = Path(td) / "panel_mask.png"
    mm = Image.new("L", (pw, ph), 0)
    ImageDraw.Draw(mm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=28, fill=255)
    mm.save(mask)
    t_first = t_last = None
    for k, r in enumerate(tl):
        t0 = round((r["start"] + TITLE_CARD_SEC) * 30) / 30
        t1 = round((r["end"] + TITLE_CARD_SEC) * 30) / 30
        if k == 0:
            t_first = t0
        t_last = t1
        # 🚨 호출부가 이 구간에 칸 클립을 직접 넣어줬으면 여기서 다시 칠하지 않는다.
        # WHY(2026-09-24 실측): 이 함수가 명시 오버레이보다 **뒤에** 돌아서, xray_build가 만든
        # 왼쪽 행위·오른쪽 기전 합성본을 기전 단독 화면으로 전부 덮어썼다. 결론 구절 뒤 두 구간만
        # 살아남았는데, 그건 이 트랙이 summary_from 앞에서 멈추기 때문이었다 — 그래서 "분할이
        # 일부 구간만 들어간다"로 보였다.
        if _is_covered(r):
            continue
        dur = t1 - t0 + 2 / 30
        inputs += ["-stream_loop", "-1", "-t", f"{dur:.3f}", "-i", str(made[r["mech"]])]
        inputs += ["-loop", "1", "-t", f"{dur:.3f}", "-i", str(mask)]
        fc.append(f"[{n}:v]setpts=PTS-STARTPTS+{t0}/TB,format=rgba[q{k}];[{n + 1}:v]format=gray,"
                  f"setpts=PTS-STARTPTS+{t0}/TB[qm{k}];[q{k}][qm{k}]alphamerge[qa{k}]")
        fc.append(f"[{cur}][qa{k}]overlay={px}:{py}:eof_action=pass:"
                  f"enable='between(t,{t0:.4f},{t1 + 1 / 30:.4f})'[pt{k}]")
        cur, n = f"pt{k}", n + 2
    label = cfg.get("inset", {}).get("label")
    if label:
        lp = Path(td) / "panel_label.png"
        _make_pill_label_png(label, lp)
        inputs += ["-i", str(lp)]
        fc.append(f"[{cur}][{n}:v]overlay=x={px + 18}:y={py + ph - 18}-h:"
                  f"enable='between(t,{t_first:.4f},{t_last + 1 / 30:.4f})'[plb]")
        cur, n = "plb", n + 1
    if ad_png is None:
        return cur, n
    inputs += ["-i", str(ad_png)]
    fc.append(f"[{cur}][{n}:v]overlay=x={px + pw - 14}-w:y={py + 14}:"
              f"enable='between(t,{t_first:.4f},{t_last + 1 / 30:.4f})'[pad]")
    return "pad", n + 1


SUMMARY_XFADE = 0.3     # 영상 칸 레이아웃 → 칠판 전체로 넘어갈 때 칠판이 갑자기 커져 튀지 않게


def _summary_board(topic, inputs, fc, cur, n, base_dir: str = ""):
    """xray.json summary_from 구절부터 끝까지를 칠판 전체 버전(board/shorts.mp4)으로 덮는다.

    WHY(2026-09-19 "기전 세개 쫙 나오고 그다음에 써머리… 거기는 기존이랑 동일하게 가야지 결론적으로 어떤걸
    해줘야하는지는 기존 포맷이 더 맞지"): 결론은 "그래서 뭘 하면 되는지"를 읽히는 게 목적이라 영상 칸 없이
    칠판을 크게 쓰고 자막도 넉넉하게(두 줄 제한 없이) 둔다. 칠판 전체 버전은 같은 나레이션으로 따로 조립한
    완성본이라 타이밍이 그대로 맞는다 — 그 시각부터 화면 전체를 덮기만 하면 된다."""
    cfg = json.loads((ROOT / "data" / topic / "xray.json").read_text(encoding="utf-8"))
    summary = cfg.get("summary_from")
    board = ROOT / "output" / topic / base_dir / "board" / "shorts.mp4"  # rebuild_video --board 결과(같은 시드)
    if not summary or not board.exists():
        return cur, n
    from lib.xray_timeline import _cues, _time_of
    ts = round((_time_of(summary, _cues(topic)) + TITLE_CARD_SEC) * 30) / 30
    inputs += ["-i", str(board)]
    fc.append(f"[{n}:v]format=rgba,fade=t=in:st={ts - SUMMARY_XFADE:.3f}:d={SUMMARY_XFADE}:alpha=1[sb]")
    fc.append(f"[{cur}][sb]overlay=0:0:enable='gte(t,{ts - SUMMARY_XFADE:.3f})'[sbo]")
    return "sbo", n + 1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("topic")
    ap.add_argument("inserts", nargs="+", help="영상시각:클립경로")
    ap.add_argument("--out", default="shorts_xray_test.mp4")
    ap.add_argument("--ad-tag", action="store_true",
                    help="클립이 칠판을 가리는 구간에 광고 표시를 다시 얹는다(유튜브용 nocta 판에서만 켠다)")
    ap.add_argument("--base", default="", help="덧씌울 원본이 output/<topic>/<여기>/shorts.mp4 (예: nocta)")
    ap.add_argument("--panel", action="store_true",
                    help="도입부 묶음 밖의 클립(기전 등)을 화면 전체가 아니라 위쪽 영상 칸(XRAY_PANEL) 안에 넣는다")
    ap.add_argument("--fill-until", type=float, default=None,
                    help="클립들을 첫 시각부터 이어 붙이고, 이 영상 시각까지 채우도록 전부 같은 비율로 느리게 늘린다")
    a = ap.parse_args()

    base = ROOT / "output" / a.topic / a.base / "shorts.mp4"
    cues = _srt(next((ROOT / "output" / a.topic).glob("*narration.srt")))
    inserts = []
    trims, foci = [], []
    for spec in a.inserts:
        # "시각:클립경로" 또는 "시각:클립경로@시작-끝" — 클립에서 가장 강한 구간만 잘라 쓸 때(2026-09-19:
        # 도입부가 훅 한 문장(약 4.4초)으로 짧아져서 4초 클립 두 개를 통째로 쓰면 넘친다)
        t, clip = spec.split(":", 1)
        rng, focus = None, 0.35
        if "#" in clip:
            clip, fz = clip.rsplit("#", 1); focus = float(fz)
        if "@" in clip:
            clip, r = clip.rsplit("@", 1)
            rng = tuple(float(x) for x in r.split("-"))
        clip = (ROOT / clip).resolve()
        d = (rng[1] - rng[0]) if rng else _dur(clip)
        inserts.append((float(t), clip, d)); trims.append(rng); foci.append(focus)
    # WHY --fill-until(2026-09-18 사용자 지시 "이 세 가지가 그 손상을 더 키워요 여기까지가 구글플로우 영상으로
    # 들어가야 하는데… 영상 길이를 좀 길게 빼 느리게 해가지고"): Flow 클립은 4/6/8/10초 고정이라 나레이션의
    # "원인 도입" 문장 끝과 안 맞는다. 문장 중간에 칠판으로 넘어가면 어색하므로 클립을 늘려 문장 끝에 맞춘다.
    # 시각을 0으로 준 클립은 "앞 클립에 이어 붙이기". 첫 클립부터 이어진 묶음(도입부)만 --fill-until로
    # 늘리거나 줄이고, 나머지(기전 컷어웨이 등)는 지정 시각에 원래 속도로 넣는다(2026-09-19 — 도입부 두 컷 +
    # 설명 문장마다 기전 4초 컷을 한 번에 합성하려고 분리).
    # WHY 0.2초부터(2026-09-21 사용자 "첫장면 썸네일 0.2초 들어가던거 아예없어져버렸네"): 칠판본 맨 앞
    # 0.2초는 썸네일로 잡히는 제목 카드다(CLAUDE.md 영상 포맷 2번). 도입부 클립을 0초부터 덮으면 그 카드가
    # 사라져 네이버 클립 썸네일이 Flow 클립 첫 프레임으로 바뀐다.
    if inserts and inserts[0][0] == 0.0:
        inserts[0] = (TITLE_CARD_SEC, inserts[0][1], inserts[0][2])

    speeds = [1.0] * len(inserts)
    if a.fill_until:
        chain = [0] + [k for k in range(1, len(inserts)) if inserts[k][0] == 0 and all(inserts[j][0] == 0 for j in range(1, k + 1))]
        t0 = inserts[0][0]
        sp = (a.fill_until - t0) / sum(inserts[k][2] for k in chain)
        # 클립 경계를 30fps 프레임 격자에 맞춘다 — 격자에서 어긋난 시작 시각(8.3358초)은 직전 프레임(8.3333초)을
        # 아무 클립도 안 덮어 칠판이 한 프레임 비쳤다(2026-09-18 실측).
        cur_f = round(t0 * 30)
        for k in chain:
            _, clip, d = inserts[k]
            nf = round(d * sp * 30)
            inserts[k] = (cur_f / 30, clip, nf / 30); speeds[k] = sp; cur_f += nf
    chain_set = set(chain) if a.fill_until else {0}
    chain_flags = [k in chain_set for k in range(len(inserts))]
    for k, (t, clip, d) in enumerate(inserts):
        if speeds[k] == 1.0:
            inserts[k] = (round(t * 30) / 30, clip, d)

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        ad = td / "ad.png"
        # 네이버 클립판은 화면 표시가 없고(플랫폼 배너가 자체 표기), 유튜브판(--ad-tag)에만 얹는다
        if a.ad_tag:
            _make_ad_tag_png(ad, lang="kor")
        ad_h = Image.open(ad).height if a.ad_tag else 0
        inputs = ["-i", str(base)]
        fc, cur, n = [], "0:v", 1
        amix = ["[0:a]"]
        for i, (t0, clip, d) in enumerate(inserts):
            speed = speeds[i]
            t1 = t0 + d
            inputs += ["-i", str(clip)]
            # 늘릴 때 프레임 보간(minterpolate) — 그냥 setpts만 늘리면 같은 프레임이 반복돼 뚝뚝 끊긴다
            slow = (f"setpts={speed:.4f}*(PTS-STARTPTS),minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc"
                    if speed != 1.0 else "setpts=PTS-STARTPTS")
            # WHY 프레임 번호로 길이를 강제하는지(2026-09-18 "8초~9초 사이에… 칠판이 잠깐 노출"): 늘린 클립이
            # 계산상 끝(8.34초)보다 이르게(8.23초) 끝나 그 틈으로 밑의 칠판이 비쳤다. 프레임 보간 필터가 첫
            # 프레임을 늦게 내보내 타임스탬프 기준 trim이 앞부분 길이를 잃은 것 — tpad+시간 trim으로도 안 잡혔다.
            # 프레임을 0부터 다시 번호 매기고, 마지막 프레임을 복제해 늘린 뒤 필요한 프레임 수로 정확히 자른다.
            nf = round(d * 30) + 1      # 다음 클립과 1프레임 겹치게 — 경계에서 둘 다 없는 순간이 없도록
            rng = trims[i]
            cut = f"trim=start={rng[0]}:end={rng[1]},setpts=PTS-STARTPTS" if rng else ""
            in_panel = a.panel and chain_flags[i] is False
            # ⚠️ 칸에 들어갈 클립을 먼저 720x1280(세로)으로 밀어 넣으면, **이미 칸 비율(960x680 가로)로
            # 만들어 온 합성본**이 찌그러진다(2026-09-24 실측: 왼쪽 행위·오른쪽 기전을 붙여 넣었더니 세로로
            # 늘어나 한쪽만 남았다). 칸 쪽은 아래 `scale={pw}:-2,crop`이 비율을 지키며 알아서 맞춘다.
            fit = "" if in_panel else f"scale={W}:{H}"
            # 빈 조각을 걸러서 잇는다 — 예전엔 조각마다 쉼표를 손으로 붙였는데, 칸 클립은 `fit`이 비어서
            # `[1:v],setpts=...`가 만들어졌고 ffmpeg가 "No such filter: ''"로 죽었다(2026-09-24 실측).
            head = ",".join(x for x in (cut, fit, slow) if x)
            fc.append(f"[{n}:v]{head},fps=30,setpts=N/30/TB,tpad=stop_mode=clone:stop=60,"
                      f"trim=end_frame={nf},setpts=N/30/TB+{t0}/TB[c{i}]")
            if in_panel:
                # WHY 칸 안에 넣는지(2026-09-19 "너무 정신사납잖어… 남는공간에다가 영상"): 화면 전체를 칠판↔영상으로
                # 뒤집지 않고, 칠판 위 영상 칸 안의 내용만 바꾼다. 세로 클립을 칸 폭에 맞추고 초점 높이에서 잘라낸다.
                px, py, pw, ph = XRAY_PANEL
                mask = td / f"pmask{i}.png"
                mm = Image.new("L", (pw, ph), 0)
                from PIL import ImageDraw as _D
                _D.Draw(mm).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=28, fill=255); mm.save(mask)
                inputs += ["-loop", "1", "-t", f"{d + 1:.3f}", "-i", str(mask)]
                fc.append(f"[c{i}]scale={pw}:-2,crop={pw}:{ph}:0:'min(ih-{ph},ih*{foci[i]})',format=rgba[pc{i}];"
                          f"[{n + 1}:v]format=gray[pm{i}];[pc{i}][pm{i}]alphamerge[pa{i}]")
                fc.append(f"[{cur}][pa{i}]overlay={px}:{py}:eof_action=pass:"
                          f"enable='between(t,{t0:.4f},{t1 + 1 / 30:.4f})'[v{i}]")
            else:
                fc.append(f"[{cur}][c{i}]overlay=0:0:eof_action=pass:enable='between(t,{t0:.4f},{t1 + 1 / 30:.4f})'[v{i}]")
            cur = f"v{i}"
            # WHY 오디오 유무를 확인하는지(2026-09-21): Flow 클립엔 효과음이 들어 있지만, 부위 점등 클립은
            # scripts/make_part_clip.py가 스틸에서 만든 것이라 오디오 트랙이 아예 없다. 없는 [n:a]를 참조하면
            # ffmpeg가 "matches no streams"로 전체 조립을 실패시킨다(소화_14에서 실측).
            if _has_audio(clip):
                tempo = f"atempo={1 / speed:.4f}," if speed != 1.0 else ""
                acut = f"atrim=start={rng[0]}:end={rng[1]},asetpts=PTS-STARTPTS," if rng else ""
                fc.append(f"[{n}:a]{acut}{tempo}volume={CLIP_SFX_VOLUME},"
                          f"adelay={int(t0 * 1000)}|{int(t0 * 1000)}[s{i}]")
                amix.append(f"[s{i}]")
            n += 2 if in_panel else 1
            if in_panel:
                # 칠판에 자막이 이미 있으니 건너뛰고, 칸 위에 가려지는 광고 표시만 다시 얹는다(유튜브판만)
                if a.ad_tag:
                    inputs += ["-i", str(ad)]
                    fc.append(f"[{cur}][{n}:v]overlay=x={XRAY_PANEL[0] + XRAY_PANEL[2] - 14}-w:"
                              f"y={XRAY_PANEL[1] + 14}:enable='between(t,{t0},{t1})'[a{i}]")
                    cur, n = f"a{i}", n + 1
                continue
            # 이 구간에 걸치는 자막(영상 시각 = srt 시각 + 제목카드 길이)
            for j, (cs, ce, text) in enumerate(chunk_caption_entries(cues)):
                s, e = max(cs + TITLE_CARD_SEC, t0), min(ce + TITLE_CARD_SEC, t1)
                if e - s < 0.2:
                    continue
                png = td / f"cap_{i}_{j}.png"
                fg = _caption_png(text, png)
                inputs += ["-i", str(png)]
                fc.append(f"[{cur}][{n}:v]overlay=x=(W-w)/2:y={CAPTION_CENTER_Y}-h/2:"
                          f"enable='between(t,{s:.3f},{e:.3f})'[k{i}_{j}]")
                cur, n = f"k{i}_{j}", n + 1
            if a.ad_tag:
                inputs += ["-i", str(ad)]
                fc.append(f"[{cur}][{n}:v]overlay=x={NAVER_SAFE_RIGHT}-w:y={NAVER_SAFE_TOP}:"
                          f"enable='between(t,{t0},{t1})'[a{i}]")
                cur, n = f"a{i}", n + 1
        if a.panel:
            panel_windows = [(t, t + d) for (t, _c, d), f in zip(inserts, chain_flags) if f is False]
            cur, n = _panel_track(a.topic, td, inputs, fc, cur, n, ad if a.ad_tag else None, panel_windows)
            cur, n = _summary_board(a.topic, inputs, fc, cur, n, a.base)
        fc.append(f"{''.join(amix)}amix=inputs={len(amix)}:duration=first:normalize=0[aout]")
        # --base nocta면 결과도 nocta/ 안에 둔다 — 안 그러면 유튜브판이 네이버판을 덮어쓴다(2026-09-21 실측)
        out = ROOT / "output" / a.topic / a.base / a.out
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc),
                            "-map", f"[{cur}]", "-map", "[aout]", "-c:v", "libx264", "-crf", "19",
                            "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", str(out)],
                           capture_output=True, text=True)
        if r.returncode:
            # WHY stderr를 보여주는지(2026-09-21): capture_output이 삼켜서 실패하면 필터 문자열만 길게 뜨고
            # 정작 원인(어느 필터가 왜 틀렸는지)이 안 보였다.
            import sys as _s
            print(r.stderr[-2500:], file=_s.stderr)
            raise SystemExit(f"[xray_splice] ffmpeg 실패(exit {r.returncode})")
        print(out)


if __name__ == "__main__":
    main()
