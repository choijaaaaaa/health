# 콘텐츠의 "검증이 필요한 주장"을 기계적으로 찾아내는 감사기.
#
# WHY(2026-08-28): blog_seo를 8개 언어로 확장하면서 각 언어권 공식기관 원문과 대조했더니
# ko 캡션에서 여덟 가지 유형의 오류가 나왔다 — 출처 없는 수치, 존재하지 않는 논문,
# 실존 논문 수치 부풀리기(PREDIMED 30%→39%), 무관한 연구 갖다 붙이기(IARC 대장암 수치를
# 새치 근거로), 맥락 오용, 전제 자체가 반박됨, 보도자료 수치를 논문 수치처럼 인용,
# 원문 오독("150에서 250으로"→"150~250 증가").
#
# 다국어판은 언어권마다 재검증하니 걸러지지만 ko는 아무도 다시 안 본다. 사람이 매번
# 눈으로 볼 수 없으므로, "이미 틀린 것으로 판정된 문구"와 "검증 없이 쓰인 정밀 수치"를
# 기계가 잡아낸다. 완벽한 사실 검증은 불가능하지만 재발과 신규 유입은 막을 수 있다.
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIT_DIR = ROOT / "data" / "_audit"
KNOWN_ISSUES = AUDIT_DIR / "ko_known_issues.json"

# 근거 없이 쓰이면 위험한 신호들. WHY 소수점 수치를 따로 보는지: 실측에서 "17.89mg",
# "14.8%"처럼 소수점까지 정밀한 값일수록 원출처가 없는 경우가 많았다(있는 척하는 정밀도).
_DECIMAL_STAT = re.compile(r"\d+\.\d+\s*(?:%|퍼센트|배|mg|g\b|mmHg|kcal|µg|pg)")
_MULTIPLIER = re.compile(r"\d+(?:\.\d+)?\s*배")
_PERCENT = re.compile(r"\d+(?:\.\d+)?\s*(?:%|퍼센트)")
# 연구를 인용하는 형태. 저널명·기관명이 붙으면 원문 대조가 가능해야 한다.
_STUDY_REF = re.compile(
    r"(?:JAMA|Lancet|NEJM|BMJ|AJCN|Nature|Cell|Diabetes Care|Circulation|PLOS|Cochrane"
    r"|메타분석|무작위|코호트|추적\s*연구|임상시험|체계적\s*문헌고찰)")
# WHY 한국 공식기관을 따로 넣는지(2026-08-31): 원래 패턴이 "대학·학회·연구소"류뿐이라
# **질병관리청·식약처·환경부처럼 가장 신뢰도 높은 1차 출처를 밝힌 문장이 오히려 "출처
# 없음"으로 잡혔다** — 실측에서 남은 경고 4건이 전부 이 오탐이었다. 경고가 오탐투성이면
# 사람이 통째로 무시하게 되고, 그러면 진짜 미출처 수치가 그 뒤에 숨는다.
_INSTITUTION = re.compile(
    r"(?:대학교?|학회|연구팀|연구소|재단|センター|Institute|University"
    r"|질병관리청|식품의약품안전처|식약처|식품의약품안전평가원|보건복지부|환경부"
    r"|국가건강정보포털|건강보험심사평가원|심평원|국민건강보험공단|건강보험공단"
    r"|국립암센터|국가암정보센터|농촌진흥청|기상청|소비자원|소비자연맹|소비자24"
    r"|국민건강영양조사|WHO|세계보건기구|FDA|NIH|NHS|CDC|EFSA)")


def _iter_texts(spec: dict):
    """플랫폼 캡션과 blog_seo 본문에서 검사할 텍스트를 뽑는다."""
    for p in spec.get("platforms", []):
        if p.get("caption"):
            yield p.get("name") or p.get("platform") or "?", p["caption"]
        if p.get("body_html"):
            yield (p.get("platform") or "blog_seo"), re.sub(r"<[^>]+>", " ", p["body_html"])


def load_known_issues() -> list[dict]:
    if not KNOWN_ISSUES.exists():
        return []
    return json.loads(KNOWN_ISSUES.read_text(encoding="utf-8")).get("issues", [])


def check_known_regressions(topic: str, spec: dict) -> list[str]:
    """이미 틀린 것으로 판정된 문구가 다시 나타났는지 본다.

    WHY 숫자만 비교하는지: 문장은 고쳐 써도 핵심 수치는 그대로 남는 경우가 많다.
    '치즈 70%'가 '숙성 치즈를 지목한 비율이 70%'로 바뀌어도 70이라는 값이 남으면
    같은 오류다."""
    hits = []
    for issue in load_known_issues():
        if issue["topic"] != topic:
            continue
        # WHY 한 자리 숫자를 버리는지: "오메가3", "TRPV1", "비타민C 3종"처럼 성분명·서수에
        # 섞인 1~9가 오탐을 만든다. 두 자리 이상이라야 주장 고유의 수치로 볼 수 있다.
        nums = [n for n in re.findall(r"\d+(?:\.\d+)?", issue["claim"])
                if len(n.replace(".", "")) >= 2 or "." in n]
        # 수치가 없는 주장(전제 오류 등)은 특징 어구로 찾는다
        keywords = [w for w in re.findall(r"[가-힣]{3,}", issue["claim"])
                    if w not in ("이상", "이하", "정도", "경우", "사용", "가능")][:4]
        for where, text in _iter_texts(spec):
            body_nums = set(re.findall(r"\d+(?:\.\d+)?", text))
            common = [n for n in nums if n in body_nums]
            # 고유 수치가 2개 이상 함께 남아 있으면 그 주장이 그대로일 확률이 높다
            if len(common) >= 2 or (len(nums) == 1 and common):
                hits.append(f"[{where}] 폐기 판정된 주장의 수치가 남아 있음 "
                            f"({', '.join(common)}) — {issue['claim'][:60]} "
                            f"→ {issue['fact'][:60]}")
            elif not nums and keywords:
                # WHY corrected_marker(2026-08-31): 전제가 틀린 topic을 제대로 고치는
                # 방법은 그 통념을 본문에서 직접 반박하는 것인데, 그러면 어구는 그대로
                # 남아 어구 매칭이 통째로 오탐이 된다 — 실측: 근골격_20을 "마우스 탓이
                # 아니다"로 다시 쓰자 '마우스'·'키보드'가 그대로 걸렸다. 반박이 실제로
                # 들어갔음을 증명하는 문구를 issue에 적어두고, 그게 본문에 있으면 통과.
                marker = issue.get("corrected_marker")
                if marker and marker in text:
                    continue
                matched = [k for k in keywords if k in text]
                if len(matched) >= max(2, len(keywords) - 1):
                    hits.append(f"[{where}] 폐기 판정된 주장의 어구가 남아 있음 "
                                f"({', '.join(matched)}) — {issue['claim'][:60]} "
                                f"→ {issue['fact'][:60]}")
    return hits


def scan_unsourced_claims(spec: dict) -> list[str]:
    """출처 표시 없이 쓰인 정밀 수치·연구 인용을 신호로 낸다(경고, 실패 아님)."""
    warns = []
    for where, text in _iter_texts(spec):
        has_ref = bool(_STUDY_REF.search(text) or _INSTITUTION.search(text))
        decimals = _DECIMAL_STAT.findall(text)
        multipliers = _MULTIPLIER.findall(text)
        if decimals and not has_ref:
            warns.append(f"[{where}] 출처 언급 없는 소수점 수치: {', '.join(decimals[:5])}")
        if multipliers and not has_ref:
            warns.append(f"[{where}] 출처 언급 없는 배수 표현: {', '.join(multipliers[:5])}")
        if _STUDY_REF.search(text) and not _PERCENT.search(text) and "배" not in text:
            continue
    return warns


def check_title_variety(spec: dict) -> list[str]:
    """ko 제목이 과용 패턴에 몰렸는지 본다.

    WHY(2026-08-30): 아키타입이 5종으로 갈라져 있어도 문장 뼈대가 같으면 다양성이
    없다. 실측에서 342건 중 93%가 "A - B" 대시 구조, 74%가 조건절 마무리였다 —
    제목만 나란히 놓으면 한 템플릿을 342번 채운 게 그대로 보인다."""
    from lib.content_review import KO_TITLE_OVERUSED
    warns = []
    for p in spec.get("platforms", []):
        if p.get("name") != "네이버 블로그" or not p.get("caption"):
            continue
        title = p["caption"].split("\n")[0].strip()
        hits = [label for pat, label in KO_TITLE_OVERUSED if re.search(pat, title)]
        if len(hits) >= 2:
            warns.append(f"제목이 과용 패턴 {len(hits)}개에 걸림 — {' / '.join(hits)}\n"
                         f"     「{title[:60]}」")
    return warns


def scan_title_frames(min_share: float = 0.12) -> list[str]:
    """전체 ko 제목을 훑어 특정 프레임에 쏠렸는지 본다.

    WHY 고정 패턴 검사와 별도로 두는지(2026-08-30): KO_TITLE_OVERUSED는 "이미 아는
    나쁜 패턴"만 잡는다. 그런데 템플릿을 바꾸는 작업이 **새 템플릿을 만드는** 일이
    실제로 벌어졌다 — 재작성 1차안에서 원인지목형 13건 중 9건이 "…, 범인은 X예요"로
    수렴했다. 무엇이 과용될지는 미리 알 수 없으므로, 어구 빈도를 매번 세어서
    임계 이상 쏠린 것을 그때그때 찾아낸다."""
    root = ROOT / "data"
    titles = []
    for d in sorted(root.iterdir()):
        f = d / "platform_captions.json"
        if not d.is_dir() or not f.exists():
            continue
        try:
            spec = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for pl in spec.get("platforms", []):
            if pl.get("name") == "네이버 블로그" and pl.get("caption"):
                titles.append(pl["caption"].split("\n")[0].strip())
    if not titles:
        return []
    from collections import Counter
    # 말미 2어절과 특징 연결어구를 각각 센다
    tails = Counter()
    for ti in titles:
        m = re.search(r"([가-힣]{2,6})(예요|이에요|에요|어요|아요|까요|해요)\s*$", ti)
        if m:
            tails[m.group(0)] += 1
    hits = []
    for frag, n in tails.most_common():
        share = n / len(titles)
        if share >= min_share:
            hits.append(f"제목 말미 '{frag}'가 {n}건({share:.0%})으로 쏠림 — 다른 마무리로 분산할 것")
    return hits


def audit_topic(topic: str) -> dict:
    """topic 하나를 감사한다. regressions는 반드시 고쳐야 하고 warnings는 사람이 판단."""
    path = ROOT / "data" / topic / "platform_captions.json"
    if not path.exists():
        return {"topic": topic, "skipped": "platform_captions.json 없음"}
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return {"topic": topic, "error": f"JSON 파싱 실패: {e}"}
    return {
        "topic": topic,
        "regressions": check_known_regressions(topic, spec),
        "warnings": scan_unsourced_claims(spec) + check_title_variety(spec),
    }


def _cli() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="ko 콘텐츠의 검증 필요 주장 감사")
    ap.add_argument("topics", nargs="*", help="생략 시 known_issues에 등록된 topic 전부")
    ap.add_argument("--all", action="store_true", help="data/ 아래 모든 topic")
    ap.add_argument("--warnings", action="store_true", help="경고까지 출력")
    ap.add_argument("--frames", action="store_true",
                    help="전체 ko 제목의 프레임 쏠림 검사(새 템플릿이 생겼는지)")
    a = ap.parse_args()

    if a.all:
        topics = sorted(p.name for p in (ROOT / "data").iterdir()
                        if p.is_dir() and (p / "platform_captions.json").exists())
    elif a.topics:
        topics = a.topics
    else:
        topics = sorted({i["topic"] for i in load_known_issues()})

    if a.frames:
        for m in scan_title_frames():
            print(f"⚠️  {m}")
        else:
            pass
        print("프레임 쏠림 검사 완료(경고 없으면 정상)")
        raise SystemExit(0)

    bad = 0
    for t in topics:
        r = audit_topic(t)
        if r.get("skipped") or r.get("error"):
            if r.get("error"):
                print(f"❌ {t}: {r['error']}"); bad += 1
            continue
        if r["regressions"]:
            bad += 1
            print(f"❌ {t}")
            for m in r["regressions"]:
                print(f"     {m}")
        if a.warnings and r["warnings"]:
            print(f"⚠️  {t}")
            for m in r["warnings"][:6]:
                print(f"     {m}")
    print(f"\n{len(topics)}개 topic 검사 · 폐기 주장 잔존 {bad}개")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    _cli()
