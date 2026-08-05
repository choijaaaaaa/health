# 기존 topic의 숏폼 영상을 최신 스타일(칠판 배경+배너 실사진+엔딩 CTA)로 다시
# 조립할 때 필요한 인자를 data/*의 spec·캡션·자막에서 그대로 유도한다.
# WHY(2026-08-02): 원래 조립 시 어떤 인자(모션 스케줄 타이밍 등)를 썼는지 기록해둔
# 매니페스트가 없어서, 기존 spec/narration.srt에서 매번 같은 방식으로 재유도해야
# 여러 topic에 걸쳐 일관되게 재현할 수 있다.
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from collections import Counter
from functools import lru_cache
from pathlib import Path

from PIL import Image

from lib.video_assembler import _parse_srt, assemble, DEFAULT_END_CARD_TEXT
from lib.templates.proto_before_after_transition import render as _render_before_after_transition
from lib.templates.proto_checklist import render as _render_checklist

ROOT = Path(__file__).resolve().parent.parent
ILLUST_DIR = ROOT / "assets_library" / "illust"
MOTION_DIR = ROOT / "assets_library" / "motion"
REAL_DIR = ROOT / "assets_library" / "real"

# WHY 이 3개·이 순서인지(2026-08-04, CLAUDE.md "영상 포맷 다각화" 절 참고):
# 판서형(기존)은 시그니처가 달라 아래 select_format()이 이름만 반환하고
# rebuild()가 별도 분기로 처리한다 — 나머지는 전부
# render(topic_dir, lang, audio_path, srt_path, spec_path, out_path) 시그니처로
# 통일돼 있어서 딕셔너리 하나로 매핑할 수 있다.
# WHY timeline 빠졌는지(2026-08-05, "타임라인이거 포맷 빼는게 낫겠다 모션이
# 일치하지가않아"): 육안 검토 결과 진행 라인/스톱 애니메이션 타이밍이 나레이션과
# 안 맞는 문제 발견 — 로스터에서 제외. 코드(`lib/templates/proto_timeline.py`)는
# 그대로 남겨둠, 나중에 타이밍 문제 고치면 다시 로스터에 넣는 것도 가능.
# WHY ranking_countdown 빠졌는지(2026-08-05, "사진도 없고 이상하게 만들어놨던데.
# 그리고 뭐 7개씩 넣고 이래버리니까"): 실사진 없이 텍스트·배지만으로 구성되고
# item 개수를 spec 그대로(최대 7개) 다 렌더링해서 화면이 과밀해 보이는 문제로
# 로스터에서 제외. 코드(`lib/templates/proto_ranking_countdown.py`)는 그대로
# 남겨둠.
FORMAT_ROSTER = ["chalkboard", "before_after_transition", "checklist"]
_TEMPLATE_RENDERERS = {
    "before_after_transition": _render_before_after_transition,
    "checklist": _render_checklist,
}


def select_format(topic: str) -> str:
    """topic(+언어) 문자열만으로 결정론적으로 영상 포맷 하나를 고른다 — 진짜
    랜덤이 아니라 같은 topic은 재생성해도 항상 같은 포맷이 나와야 재현 가능함
    (프로젝트 전역에서 이미 쓰는 topic-시드 변주 패턴과 동일한 공식). 다른
    topic·다른 언어가 이미 뭘 골랐는지는 전혀 참고하지 않는다(2026-08-04
    확정 — "다른 국가에서 어떻게 선정되어있는지까지 확인할필요까진 없다") —
    그래서 이 함수는 topic 하나만 받고 순수 함수다, 전역 상태·레지스트리 없음."""
    seed_val = sum(ord(c) * (i * 7 + 3) for i, c in enumerate(topic))
    return FORMAT_ROSTER[seed_val % len(FORMAT_ROSTER)]

# WHY 언어 코드 프리픽스로 topic의 언어를 감지하는지(2026-08-03 버그 수정,
# "en_heartburn_1 다시 만들었더니 우상단 라벨/명패가 전부 한글로 나옴" 실제
# 확인): assemble()은 lang="kor" 기본값이라 이 함수가 명시로 안 넘기면 항상
# 한국어 취급된다 — video_assembler.py 쪽엔 lang별 명패 풀(_NAMEPLATE_POOL_EN
# 등)·item_label_overrides 플러밍이 이미 만들어져 있었는데, 정작 이 함수(실제
# 재생성에 쓰는 진입점)가 그 파라미터들을 계산해서 넘기질 않아서 기능이
# "만들어져 있지만 연결 안 된" 상태였다. topic 폴더명이 "<langcode>_<topic>_<n>"
# 규칙(예: en_heartburn_1)을 따른다는 걸 이용해 프리픽스로 감지한다 — 매칭
# 안 되면(프리픽스 없음) 기존 한국어 topic 그대로 "kor".
_GLOBAL_CHANNELS_PATH = ROOT / "data" / "global_channels.json"


@lru_cache(maxsize=1)
def _lang_codes() -> list[str]:
    if not _GLOBAL_CHANNELS_PATH.exists():
        return []
    channels = json.loads(_GLOBAL_CHANNELS_PATH.read_text())
    return [v["code"] for v in channels.values() if v.get("code") and v["code"] != "ko"]


def _detect_lang(topic: str) -> str:
    # WHY "/" 먼저 확인(2026-08-03, 다른 세션이 <topic>/<lang>/ 중첩 구조로
    # 재편함 — "가슴쓰림_1" 파일럿에서 실제 확인): 새 구조에선 topic 인자가
    # "가슴쓰림_1/en"처럼 경로로 들어온다 — 마지막 세그먼트가 언어 코드와
    # 정확히 일치하면(부분 프리픽스 매칭이 아니라 완전 일치) 그걸 쓴다. 옛
    # 플랫 프리픽스 규칙("en_heartburn_1")도 하위호환으로 계속 지원.
    if "/" in topic:
        last = topic.rsplit("/", 1)[-1]
        if last == "ko" or last in _lang_codes():
            return "kor" if last == "ko" else last
    for code in _lang_codes():
        if topic.startswith(f"{code}_"):
            return code
    return "kor"


def _resolve_output_file(topic_dir: Path, suffix: str) -> Path:
    """WHY glob으로 찾는지(2026-08-03, <topic>/<lang>/ 중첩 구조에서 실제 발견):
    파일명 규칙이 폴더 구조와 안 맞는 경우가 실제로 있었다 — output/가슴쓰림_1/ko/는
    파일명이 "가슴쓰림_1_*"(새 topic 이름과 일치)인데, output/가슴쓰림_1/en/은
    "en_heartburn_1_*"(마이그레이션 전 옛 플랫 topic 이름 그대로, 폴더만 옮겨지고
    파일명은 안 바뀜)라 규칙이 서로 다르다. topic 문자열에서 파일명을 그대로
    유도하면 en 쪽은 틀린 경로가 나오므로, 실제 폴더 안의 파일을 glob으로 찾는다
    (topic 문자열 기반 유도는 폴백으로만 남김).
    WHY 접두어 없는 파일명도 확인하는지(2026-08-03 버그 수정, 갑상선_1/en 영상
    조립 중 실제 발견): `*{suffix}`(예: "*_narration.mp3")는 파일명 앞에 밑줄
    포함 최소 한 글자가 있어야 매치된다 — 그런데 `lib/typecast_tts.py`는 처음부터
    중첩 경로로 만든 신규 topic엔 접두어 없이 그냥 "narration.mp3"로 저장한다
    (그 폴더 안에서 이미 유일해서 접두어가 필요 없다는 설계, CLAUDE.md에도 명시).
    가슴쓰림_1/en처럼 마이그레이션 이력이 있어 접두어가 남은 topic만 위 glob으로
    잡히고, 신규 topic은 하나도 안 잡혀서 폴백(전혀 엉뚱한 "en_narration.srt" 같은
    경로)으로 빠졌다 — 접두어 버전이 없으면 접두어 없는 정확한 파일명도 확인한다."""
    matches = sorted(topic_dir.glob(f"*{suffix}"))
    if matches:
        return matches[0]
    bare = topic_dir / suffix.lstrip("_")
    return bare if bare.exists() else None


def _strip_lang_prefix(topic: str, lang: str) -> str:
    return topic[len(lang) + 1:] if lang != "kor" and topic.startswith(f"{lang}_") else topic

BG_CANDIDATES = [
    ("0x00FF00", (0, 255, 0)),
    ("0x0000FF", (0, 0, 255)),
    ("0xFF00FF", (255, 0, 255)),
    ("0x00FFFF", (0, 255, 255)),
    ("0xAA00FF", (170, 0, 255)),
    ("0xFFFFFF", (255, 255, 255)),
]


def _char_name(char_file: str) -> str:
    return char_file.replace("_illust.jpg", "")


def _char_media_path(name: str) -> str:
    """이 캐릭터에 쓸 실제 파일 — 모션 mp4가 있으면 그걸(과거 Kling 시절 자산),
    없으면 정지 illust jpg를 그대로 반환한다(2026-08-05, 모션 생성 자체를
    중단하기로 확정 — Kling도 정지 루프 mp4도 더 이상 새로 안 만듦). 어느 쪽이든
    video_assembler.py의 _build_character_loop/_build_character_segment가
    `_is_static_image()`로 확장자를 보고 알아서 분기한다."""
    motion_path = MOTION_DIR / f"{name}_motion.mp4"
    if motion_path.exists():
        return str(motion_path)
    return str(ILLUST_DIR / f"{name}_illust.jpg")


@lru_cache(maxsize=None)
def nearest_bg_color_for_motion(name: str) -> str:
    """캐릭터 미디어(모션 mp4 또는 정지 illust jpg) 모서리 픽셀을 5색 크로마키
    후보 중 가장 가까운 색으로 매핑한다.
    ⚠️ WHY 일러스트가 아니라 모션 클립에서 직접 읽는지(2026-08-02, 눈_1 재조립
    실사 확인 중 발견): 기존 캐릭터 일러스트는 카드뉴스 표지 중복 방지를 위해
    나중에 배경색을 다양하게 리컬러했지만(recolor_background), 그 리컬러는 정지
    이미지 파일에만 적용됐고 이미 Kling으로 만들어둔 모션 mp4는 그대로 원래
    배경색(대부분 초록)으로 남아있다 — 일러스트 모서리 색으로 bg_color를
    유도하면 실제 모션 클립 배경과 안 맞아서 크로마키 제거가 안 되고 초록
    사각형이 그대로 화면에 노출되는 사고가 난다. 모션 클립이 있으면 그 클립의
    첫 프레임을, 모션 자체가 없는(2026-08-05 이후 신규) 캐릭터는 illust jpg
    자체를 읽는다 — 어차피 같은 파일을 그대로 코너에 쓸 것이므로 그 파일의
    실제 배경색을 읽는 게 맞다."""
    media_path = _char_media_path(name)
    with tempfile.TemporaryDirectory() as tmp:
        frame_path = Path(tmp) / "frame.png"
        subprocess.run(
            ["ffmpeg", "-y", "-i", media_path, "-vframes", "1", str(frame_path)],
            check=True, capture_output=True,
        )
        img = Image.open(frame_path).convert("RGB")
        r, g, b = img.getpixel((2, 2))
    best = min(BG_CANDIDATES, key=lambda c: sum((a - b) ** 2 for a, b in zip(c[1], (r, g, b))))
    return best[0]


def find_real_photo(char_name: str) -> str | None:
    exact = REAL_DIR / f"{char_name}.jpg"
    if exact.exists():
        return str(exact)
    cands = sorted(REAL_DIR.glob(f"{char_name}_real_*.jpg"))
    return str(cands[0]) if cands else None


# WHY \w+(2026-08-03 버그 수정, en_heartburn_1 재생성 로그에서 스퓨리어스 세그먼트
# 발견): 원래 [가-힣A-Za-z0-9]+였는데 아랍어·벵골어·힌디어·태국어·일본어·
# 중국어·러시아어 나레이션은 이 범위 밖 문자라 키워드가 하나도 안 뽑혔다.
# Python str 정규식은 \w가 기본적으로 유니코드 문자 범주를 다 포함하므로(한글·
# 키릴·아랍·데바나가리·벵골·타이 문자 전부 포함) 언어 무관하게 쓸 수 있다.
_WORD_RE = re.compile(r"\w+")

# WHY 언어별 불용어 제거(2026-08-03 버그 수정, en_heartburn_1 재생성 로그 디버깅
# 중 실제 확인): 공백으로 단어를 구분하는 언어는 "it/of/the/and" 같은 기능어가
# 그대로 독립 토큰으로 뽑히는데, 한국어는 조사가 명사에 붙어 나오는 구조라 이런
# 짧은 독립 기능어 토큰이 애초에 안 생겨서 원래 코드에서 문제가 안 보였다. 이
# 기능어들이 관련 없는 문단에 우연히 여러 개 겹치면서 컷오프를 넘겨 엉뚱한
# 항목이 조기 배정되는 게 실제 스퓨리어스 세그먼트의 주 원인이었다(디버깅으로
# 확인: "it/of/the/and" 매치만으로 무관한 문단이 score 5~6 획득, 컷오프 통과).
# 표준 불용어가 확인된 언어(로마자/키릴 문자, 띄어쓰기로 단어 구분)만 채워뒀다 —
# 그 외 언어(아랍어·벵골어·힌디어·태국어·일본어·중국어처럼 띄어쓰기 관행이
# 다르거나 직접 검증 못 한 언어)는 빈 셋이라 기존과 동일하게 동작(필터링 없음).
_STOPWORDS_BY_LANG: dict[str, set[str]] = {
    "en": {
        "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "at", "for",
        "with", "as", "is", "are", "was", "were", "be", "been", "it", "its", "this",
        "that", "these", "those", "you", "your", "he", "she", "they", "we", "i",
        "not", "no", "do", "does", "did", "so", "if", "than", "then", "from", "by",
        "about", "into", "up", "down", "out", "over", "under", "again", "more",
        "most", "some", "such", "own", "same", "too", "very", "can", "will", "just",
        "should", "now", "there", "here", "one",
    },
    "es": {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero",
        "de", "del", "a", "en", "por", "para", "con", "sin", "es", "son", "era",
        "fue", "ser", "esta", "este", "estos", "estas", "que", "se", "su", "sus",
        "lo", "le", "les", "no", "si", "muy", "mas", "como", "cuando", "donde",
        "porque", "ya", "tambien", "entonces",
    },
    "pt": {
        "o", "a", "os", "as", "um", "uma", "uns", "umas", "e", "ou", "mas", "de",
        "do", "da", "dos", "das", "em", "por", "para", "com", "sem", "e", "sao",
        "era", "foi", "ser", "esta", "este", "estes", "estas", "que", "se", "seu",
        "sua", "seus", "suas", "lhe", "lhes", "nao", "sim", "muito", "mais", "como",
        "quando", "onde", "porque", "ja", "tambem", "entao",
    },
    "fr": {
        "le", "la", "les", "un", "une", "des", "et", "ou", "mais", "de", "du", "à",
        "en", "par", "pour", "avec", "sans", "est", "sont", "était", "être", "ce",
        "cet", "cette", "ces", "que", "qui", "se", "son", "sa", "ses", "leur",
        "leurs", "ne", "pas", "oui", "non", "très", "plus", "comme", "quand", "où",
        "parce", "si", "déjà", "aussi", "alors",
    },
    "de": {
        "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem",
        "einer", "eines", "und", "oder", "aber", "von", "zu", "in", "auf", "an",
        "für", "mit", "ohne", "ist", "sind", "war", "waren", "sein", "dies", "diese",
        "dieser", "dieses", "dass", "sich", "ihr", "ihre", "nicht", "ja", "nein",
        "sehr", "mehr", "wie", "wenn", "wo", "weil", "schon", "auch", "dann",
    },
    "ru": {
        "и", "в", "во", "не", "что", "он", "на", "я", "с", "со", "как", "а", "то",
        "все", "она", "так", "его", "но", "да", "ты", "к", "у", "же", "вы", "за",
        "бы", "по", "только", "её", "мне", "было", "вот", "от", "меня", "ещё",
        "нет", "о", "из", "ему", "когда", "уже", "или", "быть", "был", "для", "мы",
        "тебя", "их", "чем", "была", "без", "себя", "под", "будет", "этот", "того",
    },
    "tr": {
        "ve", "veya", "ama", "bir", "bu", "şu", "o", "de", "da", "ki", "ile",
        "için", "gibi", "çok", "daha", "en", "ise", "ya", "hem", "ne", "değil",
        "var", "yok", "her", "bazı", "kadar", "sonra", "önce", "çünkü", "eğer",
        "artık", "hiç", "şey", "biz", "siz", "ben", "sen", "onlar",
    },
    "id": {
        "yang", "dan", "di", "ke", "dari", "untuk", "pada", "dengan", "adalah",
        "ini", "itu", "atau", "juga", "akan", "tidak", "ada", "saya", "kamu", "dia",
        "mereka", "kita", "kami", "sudah", "belum", "bisa", "harus", "karena",
        "jika", "tapi", "tetapi", "agar", "supaya", "sangat", "lebih", "paling",
        "saja", "pun", "nya",
    },
    "vi": {
        "và", "hoặc", "nhưng", "là", "của", "cho", "với", "không", "có", "này",
        "đó", "những", "các", "một", "ở", "tại", "khi", "nếu", "vì", "do", "để",
        "cũng", "đã", "sẽ", "đang", "rất", "hơn", "nhất", "thì", "mà", "ai", "gì",
        "sao",
    },
}


def _is_alt_item(item: dict, items: list[dict]) -> bool:
    """이 항목이 "원인 대신 이걸 드세요" 식 대안 항목인지 판단.
    WHY 한국어 '대신' 문자열 검사 대신 접두어 구조로 판단하는지(2026-08-03
    버그 수정): '~ 대신'(한국어)/'— try this instead'(영어)처럼 언어마다 대안
    표현이 달라서 문자열 매칭으론 한국어 topic만 걸러지고 다른 언어는 전부
    빠져나갔다 — 콘텐츠 생성 규칙상 대안 항목 이름은 항상 원인 항목 이름을
    그대로 접두어로 갖고 뒤에 대안 문구만 붙으므로, 같은 항목 목록 안 다른
    항목 이름이 접두어인지로 언어 무관하게 판단한다."""
    name = item["name"]
    return any(o is not item and o["name"] and name.startswith(o["name"]) for o in items)


def _keywords(item: dict, items: list[dict], lang: str = "kor") -> set[str]:
    """항목의 name+body 문장에서 뽑은 내용어 — narration.srt 문장과 겹치는 단어를
    찾아 그 항목이 실제로 언급되는 구간을 잡는 근거로 쓴다. char_file 베이스 이름
    (예: 탄산음료)은 일러스트용 대표 명칭일 뿐 나레이션엔 그 단어 그대로 안 나오는
    경우가 많아서(예: "단 음료"라고만 씀) name/body 쪽이 훨씬 신뢰도 높다.
    WHY 대안 항목은 name을 아예 안 쓰는지: "튀김 대신"처럼 대안 항목 이름은
    원인 항목 이름("기름진 튀김·가공식품")의 단어를 그대로 재사용해서, name까지
    키워드로 넣으면 원인 문단에서 대안 항목이 잘못 잡힌다(둘 다 "튀김" 매치) —
    대안 항목은 body(실제로 그 대안 식품을 설명하는 문장)만 신뢰한다."""
    text = " ".join(item["body"]) if _is_alt_item(item, items) else item["name"] + " " + " ".join(item["body"])
    stopwords = _STOPWORDS_BY_LANG.get(lang, set())
    return {w for w in _WORD_RE.findall(text) if len(w) >= 2 and w.lower() not in stopwords}


def _group_by_paragraph(narration_txt: str, srt_entries: list[tuple[float, float, str]]):
    """narration.txt 문단(빈 줄 구분)과 narration.srt 문장을 다시 짝짓는다 — SRT는
    문장 단위, spec item은 문단(원인 1개~해결책 여러 개) 단위라 둘의 경계가 다르다.
    같은 원본 텍스트를 그대로 문장 단위로 쪼갠 것뿐이라 문단 텍스트에 그 문장이
    부분 문자열로 포함되는지로 안전하게 다시 묶을 수 있다."""
    paragraphs = [p.strip() for p in narration_txt.split("\n\n") if p.strip()]
    groups = [[] for _ in paragraphs]
    pi = 0
    for entry in srt_entries:
        text = entry[2].strip()
        while pi < len(paragraphs) - 1 and text not in paragraphs[pi]:
            pi += 1
        groups[pi].append(entry)
    return [g for g in groups if g]


def build_motion_schedule(
    items: list[dict],
    srt_entries: list[tuple[float, float, str]],
    narration_txt: str,
    lang: str = "kor",
):
    """narration.txt 문단 단위로 각 항목의 name/body 키워드 겹침 점수를 매겨 어느
    항목이 그 문단에 해당하는지 정한다(문장 단위로 하면 도입부 훅 문장이 뒷부분
    품목명을 미리 한 번 언급하는 것만으로 엉뚱하게 일찍 전환되는 문제가 있었다 —
    문단 전체 겹침 점수를 보면 그런 스침 언급 한 단어에 흔들리지 않는다). 한
    문단에 여러 항목이 걸리면(마무리 문단에서 대안들을 한 번에 나열하는 경우 등)
    문단 내 키워드 등장 위치 비율로 시간을 비례 배분한다 — 정확한 원본 타이밍
    기록이 없어서 택한 근사치다."""
    keyword_sets = [_keywords(it, items, lang) for it in items]
    names = [_char_name(it["char_file"]) for it in items]
    # WHY item["name"]도 매치 후보로 추가하는지(2026-08-03 버그 수정, en_heartburn_1
    # 재생성 로그에서 실제 확인): names는 char_file 파생 내부 식별자라 한국어다 —
    # 번역된 나레이션(영어 등)엔 절대 등장하지 않아 name_hit(가중치 10, 가장 강한
    # 신호)이 비한국어 topic에서 항상 죽어있었다. item["name"]은 이미 언어별로
    # 번역돼 있어 훨씬 강한 신호지만, 대안 항목("Coffee — try this instead")은
    # 꼬리표가 붙어 나레이션과 그대로 안 겹치고 원인 항목 이름과도 겹쳐 혼선을
    # 주므로(원인 문단에서 대안 항목이 잘못 잡힘) 대안 항목은 이 보조 신호에서
    # 제외한다 — 대안 항목은 기존처럼 names(char_file 이름)만으로 판단.
    alt_flags = [_is_alt_item(it, items) for it in items]
    match_names = [None if alt_flags[i] else it["name"] for i, it in enumerate(items)]
    n = len(items)

    para_groups = _group_by_paragraph(narration_txt, srt_entries)

    points: list[tuple[float, int]] = [(0.0, 0)]
    assigned = {0}
    for gi, group in enumerate(para_groups):
        if gi == 0:
            continue  # 첫 문단은 항상 도입부(item[0])
        full_text = "".join(e[2] for e in group)

        # WHY 캐릭터 이름 직접 등장에 가중치 10을 주는지: "케일"/"고등어"처럼 대안
        # 캐릭터는 실제 음식명이라 나레이션에 그대로 등장해 강한 신호가 되지만,
        # "탄산음료"/"라면"처럼 원인 캐릭터가 추상적 대표 명칭인 경우엔 등장 안
        # 하고 body 키워드(성분·수치 등) 여러 개가 겹치는 걸로만 판단해야 한다 —
        # 이름 매치 1개 또는 body 키워드 3개 이상을 "확실한 매치" 기준(임계값 3)으로
        # 삼아서, 우연히 겹치는 단어 1~2개짜리 스침 매치를 걸러낸다.
        raw = []
        for idx in range(n):
            if idx in assigned:
                continue
            name_hit = names[idx] in full_text or bool(match_names[idx]) and match_names[idx] in full_text
            body_hits = sum(1 for kw in keyword_sets[idx] if kw in full_text)
            score = (10 if name_hit else 0) + body_hits
            if score > 0:
                raw.append((score, idx))
        if not raw:
            continue
        # WHY 절대 임계값 대신 최고점 대비 상대 임계값(2026-08-02, 관절_1/다리쥐_1에서
        # 실제 발견): 진짜 매치 점수 폭이 topic마다 크게 달라서(캐릭터 이름이 나레이션에
        # 그대로 나오면 10+, 안 나오면 body 단어 몇 개 겹치는 정도로 4~5) 고정 임계값
        # 하나로는 어떤 topic에선 스침 매치를 못 거르고 어떤 topic에선 진짜 매치까지
        # 걸러버렸다 — 이 문단의 최고 점수 대비 50% 이상인 후보만 남기면(최소 3점)
        # "우연히 단어 하나 겹친 것"과 "이 문단이 진짜 다루는 항목(들)"이 안정적으로
        # 갈린다. 문단 하나가 여러 항목을 같이 언급하는 경우(마무리 문단, 원인+대안을
        # 한 문단에 묶어 쓴 topic 등)엔 최고점과 비등한 후보가 여럿 남아 자연스럽게
        # 다중 선택된다.
        best = max(s for s, _ in raw)
        cutoff = max(3, best * 0.5)
        scored = []
        for score, idx in raw:
            if score < cutoff:
                continue
            if names[idx] in full_text:
                pos = full_text.find(names[idx])
            elif match_names[idx] and match_names[idx] in full_text:
                pos = full_text.find(match_names[idx])
            else:
                pos = min(full_text.find(kw) for kw in keyword_sets[idx] if kw in full_text)
            scored.append((pos, score, idx))
        if not scored:
            continue
        scored.sort()

        # 문단 내 절대 위치 → 절대 시각으로 변환(문장마다 길이가 달라 문단을 한
        # 덩어리로 이어붙인 뒤 누적 길이로 각 문장의 오프셋을 구한다)
        offsets = []
        acc = 0
        for e in group:
            offsets.append((acc, acc + len(e[2]), e[0], e[1]))
            acc += len(e[2])

        def pos_to_time(pos):
            for lo, hi, s, e in offsets:
                if lo <= pos < hi or (hi == acc and pos >= hi):
                    frac = (pos - lo) / max(hi - lo, 1)
                    return s + (e - s) * frac
            return group[0][0]

        for pos, score, idx in scored:
            t = pos_to_time(pos)
            points.append((t, idx))
            assigned.add(idx)

    total_end = srt_entries[-1][1] if srt_entries else 0.0
    segments = []
    for i, (t, idx) in enumerate(points):
        seg_end = points[i + 1][0] if i + 1 < len(points) else total_end
        if seg_end <= t:
            continue
        name = names[idx]
        char_file = f"{name}_illust.jpg"
        motion_path = _char_media_path(name)
        bg_color = nearest_bg_color_for_motion(name)
        segments.append((round(t, 3), round(seg_end, 3), motion_path, bg_color))
    return segments


def derive(topic: str) -> dict:
    spec = json.loads((ROOT / "data" / topic / "card_news_spec.json").read_text())
    items = spec["items"]
    hook = " ".join(spec["title"][:-1])
    subject = spec["title"][-1]

    lead_name = _char_name(items[0]["char_file"])
    banner_photo = find_real_photo(lead_name)
    if banner_photo is None:
        counts = Counter(_char_name(it["char_file"]) for it in items)
        for name, _ in counts.most_common():
            banner_photo = find_real_photo(name)
            if banner_photo:
                break

    cover_char_file = spec.get("cover_char_file") or items[0]["char_file"]

    topic_dir = ROOT / "output" / topic
    # WHY glob 우선 + 폴백(2026-08-03): 위 _resolve_output_file WHY 참고 — 파일명
    # 규칙이 폴더 구조랑 안 맞는 실제 사례(가슴쓰림_1/en)가 있어서, 먼저 폴더
    # 안을 뒤져서 실제 있는 파일을 쓰고, 아직 아무것도 없는 새 topic이면(첫
    # 생성) topic 문자열 기반 이름으로 폴백한다. 출력(out) mp4는 오디오/자막과
    # 같은 접두어를 써야 세 파일이 한 세트로 보이므로, 실제로 찾은 오디오
    # 파일의 접두어를 그대로 재사용한다.
    found_audio = _resolve_output_file(topic_dir, "_narration.mp3")
    # WHY base_name이 빈 문자열일 수 있는지(2026-08-03 버그 수정): found_audio가
    # 접두어 없는 "narration.mp3"(신규 중첩 topic 관례)이면 "_narration.mp3"를
    # 떼어내는 슬라이싱이 음수 길이만큼 잘라내서 빈 문자열이 나온다 — 그대로
    # f"{base_name}_shorts.mp4"에 쓰면 "_shorts.mp4"처럼 이름이 깨진다. 접두어가
    # 있는 파일(가슴쓰림_1/en처럼 마이그레이션 이력이 있는 topic)만 실제로
    # 잘라내고, 빈 결과면 "접두어 없음"으로 간주해 아래에서 언더스코어 없이
    # 이어붙인다.
    fallback_base = topic.rsplit("/", 1)[-1] if "/" in topic else topic
    if found_audio:
        stripped = found_audio.name[: -len("_narration.mp3")]
        base_name = stripped if stripped else None
    else:
        base_name = fallback_base
    prefix = f"{base_name}_" if base_name else ""
    audio = found_audio or (topic_dir / f"{prefix}narration.mp3")
    srt = _resolve_output_file(topic_dir, "_narration.srt") or (topic_dir / f"{prefix}narration.srt")
    out = topic_dir / f"{prefix}shorts.mp4"

    # WHY 여기서 lang/item_label_overrides/topic_word를 계산하는지: 위 파일 상단
    # WHY 참고 — assemble() 쪽 파라미터는 이미 있었지만 이 함수가 안 넘겨서 실제
    # 재생성 결과물엔 한 번도 반영된 적이 없었다.
    lang = _detect_lang(topic)
    # WHY char_display_names 우선(2026-08-03 버그 수정, "가슴쓰림_1/en 표지에
    # 'Spicy food — try this instead'가 그대로 뜬 걸 발견해서 수동으로 고침" —
    # 그 수동 수정이 derive()엔 반영 안 돼서 이 함수로 재생성하면 되돌아갈 뻔함):
    # 최단 이름 휴리스틱은 같은 char_file을 여러 항목이 공유할 때만 통한다 —
    # 그 char_file을 쓰는 항목이 "대안" 하나뿐이면(예: 바질_illust.jpg가
    # "Spicy food — try this instead"에만 쓰이는 경우) 비교할 더 짧은 후보 자체가
    # 없어서 그 긴 문장이 그대로 남는다. card_news_spec.json에 이미 카드뉴스
    # 배지용 짧은 이름(char_display_names, 예: "바질_illust.jpg": "Herbs")이
    # 있으면 그걸 최우선으로 쓰고, 없는 캐릭터만 기존 최단-이름 휴리스틱으로
    # 폴백한다 — 두 라벨이 같은 캐릭터에 서로 다른 문구로 나오는 것도 방지됨.
    char_display_names = spec.get("char_display_names", {})
    item_label_overrides = None
    if lang != "kor":
        item_label_overrides = {}
        for it in items:
            key = _char_name(it["char_file"])
            if it["char_file"] in char_display_names:
                item_label_overrides[key] = char_display_names[it["char_file"]]
                continue
            if key not in item_label_overrides or len(it["name"]) < len(item_label_overrides[key]):
                item_label_overrides[key] = it["name"]
    # WHY spec["topic_word"] 우선(2026-08-03 버그 수정, 갑상선_1/en 영상 조립
    # 중 실제 발견): base_name에서 뽑는 방식은 파일명에 언어 단어가 실제로 박혀
    # 있는 topic(가슴쓰림_1/en처럼 예전에 flat 구조였다가 마이그레이션된 경우,
    # base_name="en_heartburn_1")에만 통했다 — typecast_tts.py가 처음부터 중첩
    # 경로로 만든 신규 topic은 파일명이 접두어 없는 "narration.mp3"라 base_name이
    # None이 되고, re.sub(r"_\d+$", "", None)이 그대로 터진다. 애초에 파일명에서
    # 영어 단어를 "역추출"하는 방식 자체가 우연에 기댄 것이었으므로, 이제
    # card_news_spec.json에 명시적으로 적어둔 topic_word를 최우선으로 쓰고
    # (char_display_names와 같은 패턴), base_name이 실제로 언어 단어를 담고
    # 있는 옛 topic만 폴백으로 그 방식을 쓴다.
    if lang == "kor":
        topic_word = None
    elif spec.get("topic_word"):
        topic_word = spec["topic_word"]
    elif base_name:
        topic_word = _strip_lang_prefix(re.sub(r"_\d+$", "", base_name), lang)
    else:
        topic_word = None

    # WHY closing.cta 우선(2026-08-03 버그 수정): DEFAULT_END_CARD_TEXT는 한국어
    # 고정 문구라, 언어 감지가 됐어도 엔드카드만 한국어로 나오는 사고가 날 뻔했다
    # (가슴쓰림_1/en 수동 조립 때는 English CTA를 직접 넘겨서 피했지만 derive()엔
    # 반영 안 됨) — spec["closing"]["cta"]가 이미 그 언어로 작성된 동일한 문구이니
    # 비한국어 topic은 이걸 그대로 쓰고, 없으면(옛 flat topic) 기존 기본값 유지.
    end_card_text = spec.get("closing", {}).get("cta") if lang != "kor" else None
    end_card_text = end_card_text or DEFAULT_END_CARD_TEXT

    distinct_chars = {it["char_file"] for it in items}
    kwargs = dict(
        images=None,
        audio_path=str(audio),
        srt_path=str(srt),
        out_path=str(out),
        title=f"{hook} {subject}",
        title_card_text=hook,
        title_card_char_path=str(ILLUST_DIR / cover_char_file),
        title_banner_photo_path=banner_photo,
        end_card_text=end_card_text,
        end_card_char_path=str(ILLUST_DIR / cover_char_file),
        lang=lang,
        item_label_overrides=item_label_overrides,
        topic_word=topic_word,
    )

    if len(distinct_chars) == 1:
        name = _char_name(items[0]["char_file"])
        kwargs["motion_path"] = _char_media_path(name)
        kwargs["motion_schedule"] = None
        kwargs["bg_color"] = nearest_bg_color_for_motion(_char_name(items[0]["char_file"]))
    else:
        srt_entries = _parse_srt(str(srt))
        narration_txt = (ROOT / "data" / topic / "narration.txt").read_text()
        kwargs["motion_path"] = None
        kwargs["motion_schedule"] = build_motion_schedule(items, srt_entries, narration_txt, lang=lang)
        kwargs["bg_color"] = nearest_bg_color_for_motion(_char_name(items[0]["char_file"]))

    return kwargs


def rebuild(topic: str):
    fmt = select_format(topic)
    kwargs = derive(topic)
    print(f"=== {topic} ===")
    print("format:", fmt)
    print("title:", kwargs["title"])
    if fmt != "chalkboard":
        # WHY derive()를 그대로 재사용하는지: 새 템플릿도 오디오/자막 접두어
        # 유무·언어 감지 같은 derive()의 경로 유도 로직이 그대로 필요하다 —
        # 중복 구현하는 대신 derive()가 이미 계산해둔 audio/srt/out/lang을
        # 재사용하고, 새 템플릿 시그니처에 맞는 spec_path만 추가로 계산한다.
        spec_path = ROOT / "data" / topic / "card_news_spec.json"
        try:
            _TEMPLATE_RENDERERS[fmt](
                topic_dir=str(ROOT / "output" / topic),
                lang=kwargs["lang"],
                audio_path=kwargs["audio_path"],
                srt_path=kwargs["srt_path"],
                spec_path=str(spec_path),
                out_path=kwargs["out_path"],
            )
        except RuntimeError as e:
            # WHY(2026-08-05): 4개 신규 템플릿은 각자 특정 items 구조를 전제한다
            # (예: checklist는 items[1:]가 (원인,대안) 짝수 쌍이어야 함) — 모든
            # topic의 콘텐츠가 이 전제를 만족하진 않는다(예: 당뇨_1/ja는 원인
            # 카드 1개 + 독립 증상 카드 3개, 짝이 안 맞음). select_format()은
            # topic 문자열만 보고 결정론적으로 고르므로 데이터 구조까지는 알 수
            # 없다 — 템플릿이 구조 불일치로 RuntimeError를 던지면, items 구조
            # 제약이 없는 판서형(chalkboard)으로 그 topic만 폴백한다.
            print(f"⚠️  {fmt} 템플릿이 이 topic 데이터 구조와 안 맞아 폴백: {e}")
            assemble(**kwargs)
            print(f"완료(chalkboard 폴백): {kwargs['out_path']}")
            return
        print(f"완료: {kwargs['out_path']}")
        return
    print("banner photo:", kwargs["title_banner_photo_path"])
    if kwargs["motion_schedule"]:
        for seg in kwargs["motion_schedule"]:
            print("  segment:", seg)
    else:
        print("motion:", kwargs["motion_path"], "bg_color:", kwargs["bg_color"])
    assemble(**kwargs)
    print(f"완료: {kwargs['out_path']}")


if __name__ == "__main__":
    rebuild(sys.argv[1])
