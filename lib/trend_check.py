# 구글 트렌드로 topic 후보 키워드의 최근 관심도 추이를 확인한다.
#
# WHY discovery 모드(급상승 검색어 목록 자체를 가져오는 것)가 없는지(2026-08-10
# 실측 확인): pytrends의 trending_searches()/today_searches()/
# realtime_trending_searches() 전부 404 — 구글이 이 엔드포인트들을 없앤 것으로
# 보임(pytrends는 비공식 라이브러리라 구글 쪽 변경에 취약). interest_over_time()
# (특정 키워드 여러 개를 넣어 서로 비교)만 안정적으로 동작해서, 이 스크립트는
# "미리 정해둔 후보 키워드 목록을 매일 한 번씩 훑어서 비교"하는 용도로만 쓴다.
#
# WHY 하루 한 번 스냅샷 + 30일 롤링 로그인지(2026-08-10, "그 날 처음 딱 한번만
# 바짝 쫙 돌려가지고 전반적인 근황을 파악하면... 한달정도치의 근황 내용들을
# 계속 파악하고 한달 넘어가는 데이터들은 삭제하고... 그날 한번이라도 작업을
# 했었다면 그다음부터는 그 데이터까지만 확인해서 쭉 작업을 진행"): 매번 topic
# 고를 때마다 API를 새로 부르면 (a) pytrends rate limit에 걸리기 쉽고
# (b) 하루 안에서는 어차피 값이 크게 안 바뀐다 — 하루 첫 실행에만 전체 후보를
# 한 번에 조회해서 `data/trend_log.json`에 저장해두고, 그날 나머지 세션은
# 이미 있는 오늘자 스냅샷을 그대로 읽기만 한다. 30일 넘은 날짜는 매 저장 시
# 자동으로 정리된다.
#
# 사용법:
#   python3 -m lib.trend_check --daily          하루 첫 실행: 전체 후보 스냅샷(이미 있으면 스킵)
#   python3 -m lib.trend_check --daily --force   오늘자 스냅샷을 강제로 다시 조회
#   python3 -m lib.trend_check --show            마지막 스냅샷을 재조회 없이 출력
#   python3 -m lib.trend_check <키워드1> [키워드2] ...   즉석 비교(최대 5개, 로그에 안 남음)
import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

from pytrends.request import TrendReq

ROOT = Path(__file__).resolve().parent.parent
LOG_PATH = ROOT / "data" / "trend_log.json"
RETENTION_DAYS = 30

# WHY 이 목록을 data/seasonal_topics.md와 별도로 파이썬 상수로 두는지: 마크다운
# 절 제목·문구가 바뀌어도 이 스크립트가 안 깨지게 하려고(파싱 대신 직접 나열) —
# seasonal_topics.md를 고칠 때 이 목록도 같이 업데이트할 것(양쪽 다 git 추적).
SEASONAL_KEYWORDS = [
    # 여름
    "온열질환", "냉방병", "땀띠", "다한증", "식중독", "장염", "수족냉증", "다래끼",
    # 가을
    "환절기 비염", "꽃가루 알레르기", "피부 건조증", "관절통", "환절기 탈모",
    # 겨울
    "독감", "동상", "안구건조증", "겨울철 우울감", "노로바이러스",
    # 봄
    "춘곤증", "미세먼지", "새학기 스트레스",
    # 연중 상시
    "역류성 식도염", "수면 장애", "거북목", "눈 피로", "구강 건강",
]


def _fetch_batch(keywords: list[str], timeframe: str = "today 3-m", geo: str = "KR") -> dict[str, dict]:
    """keywords(최대 5개)를 한 번에 조회해서 {키워드: {recent_avg, momentum}} 반환.
    실패하면 빈 dict(호출부가 이어서 다음 배치를 시도할 수 있게, 전체를 막지 않음)."""
    try:
        pytrends = TrendReq(hl="ko-KR", tz=540)
        pytrends.build_payload(keywords, timeframe=timeframe, geo=geo)
        df = pytrends.interest_over_time()
    except Exception as e:
        print(f"⚠️ 구글 트렌드 조회 실패({type(e).__name__}: {e}) — 이 배치는 건너뜁니다.")
        return {}
    if df.empty:
        return {}

    results = {}
    for kw in keywords:
        if kw not in df.columns:
            continue
        series = df[kw]
        if len(series) < 6:
            recent, prior = series.iloc[-1:], series.iloc[:-1]
        else:
            recent, prior = series.iloc[-3:], series.iloc[-6:-3]
        recent_avg = float(recent.mean())
        prior_avg = float(prior.mean()) if len(prior) else 0.0
        results[kw] = {"recent_avg": round(recent_avg, 1), "momentum": round(recent_avg - prior_avg, 1)}
    return results


def _print_results(results: dict[str, dict]) -> None:
    if not results:
        print("데이터 없음.")
        return
    # WHY 이 안내를 매번 출력하는지: 구글 트렌드의 0~100 척도는 "이번 조회에
    # 같이 넣은 키워드들 중 최댓값" 기준 상대값이라, 같은 키워드라도 무엇과
    # 같이 비교했는지에 따라 절대 수치가 달라진다 — 절대 수치가 아니라 순위·
    # 모멘텀(▲▼)만 참고할 것.
    print("(0~100 척도는 같이 조회한 키워드 중 최댓값 기준 상대값 — 절대 수치 아님, 순위·모멘텀만 참고)")
    ordered = sorted(results.items(), key=lambda kv: kv[1]["momentum"], reverse=True)
    print(f"{'키워드':<14} {'최근 관심도':>10} {'모멘텀':>10}")
    for kw, v in ordered:
        arrow = "▲" if v["momentum"] > 3 else ("▼" if v["momentum"] < -3 else "-")
        print(f"{kw:<14} {v['recent_avg']:>10.1f} {v['momentum']:>+9.1f} {arrow}")


def _load_log() -> dict[str, dict]:
    if not LOG_PATH.exists():
        return {}
    try:
        return json.loads(LOG_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_log(log: dict[str, dict]) -> None:
    cutoff = date.today() - timedelta(days=RETENTION_DAYS)
    pruned = {d: v for d, v in log.items() if date.fromisoformat(d) >= cutoff}
    LOG_PATH.write_text(json.dumps(pruned, ensure_ascii=False, indent=2), encoding="utf-8")


def daily_snapshot(force: bool = False) -> None:
    log = _load_log()
    today = date.today().isoformat()
    if today in log and not force:
        print(f"오늘({today})자 스냅샷이 이미 있습니다 — 재조회 없이 기존 결과를 보여줍니다.")
        _print_results(log[today])
        return

    # WHY 배치 사이에 sleep을 두는지(2026-08-10 실측 — 딜레이 없이 5개씩 연속
    # 조회했더니 3번째 배치부터 429 Too Many Requests): 비공식 API라 짧은
    # 간격의 연속 요청에 특히 민감하다 — 배치당 몇 초씩 쉬어서 완화.
    all_results: dict[str, dict] = {}
    batches = [SEASONAL_KEYWORDS[i:i + 5] for i in range(0, len(SEASONAL_KEYWORDS), 5)]
    for i, batch in enumerate(batches):
        if i > 0:
            time.sleep(5)
        all_results.update(_fetch_batch(batch))

    if not all_results:
        print("전체 조회 실패 — WebSearch로 수동 확인할 것.")
        return

    log[today] = all_results
    _save_log(log)
    print(f"{today}자 스냅샷 저장 완료 ({len(all_results)}개 키워드).")
    _print_results(all_results)


def show_latest() -> None:
    log = _load_log()
    if not log:
        print("저장된 스냅샷이 없습니다 — 먼저 `python3 -m lib.trend_check --daily`를 실행할 것.")
        return
    latest_date = max(log.keys())
    print(f"최신 스냅샷: {latest_date}")
    _print_results(log[latest_date])


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("사용법: --daily | --daily --force | --show | <키워드1> [키워드2] ...")
    elif args[0] == "--daily":
        daily_snapshot(force="--force" in args)
    elif args[0] == "--show":
        show_latest()
    else:
        kws = args[:5]
        if len(args) > 5:
            print("⚠️ pytrends는 한 번에 최대 5개 키워드까지만 비교 가능 — 앞 5개만 사용합니다.")
        _print_results(_fetch_batch(kws))
