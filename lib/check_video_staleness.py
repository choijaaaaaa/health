# 영상 생성 코드(video_assembler.py/lib/templates/proto_*.py)가 수정된 이후에
# 만들어진(=구버전 코드로 렌더된) topic 영상을 찾아낸다. WHY(2026-08-04, "산출물이
# 업데이트된 시기와 기능 업데이트된 시기를 서로 확인해서 추가로 수정되어야할
# 부분이 있을 때 수정 진행하는 그런 로직도 필요할것같은데"): 판서형 버그를
# 고치고서 이미 만들어둔 13개 topic을 전부 손으로 찾아서 재생성했던 적이 있고,
# 지금 5개 포맷 시스템 자체도 기존 topic들 입장에선 "코드가 바뀌었는데 영상은
# 그대로"인 상태다 — 이런 걸 매번 기억해뒀다가 수동으로 확인하는 대신 자동으로
# 목록을 뽑아주는 스크립트.
#
# ⚠️ 이 파일은 한 번 유실됐다가 재작성됨(2026-08-04) — 처음 만들었을 때 커밋을
# 안 해서 동시 세션들의 git 작업에 휩쓸려 사라졌었다. 재작성 즉시 커밋할 것.
#
# 스코프(의도적으로 좁힘, 2026-08-04): 영상(shorts.mp4)만 본다 — 나레이션/캡션
# 등 다른 산출물까지 넓히는 건 나중에. 그리고 **재생성은 절대 자동으로 안 한다**
# — 목록만 뽑아주고, 실제로 다시 만들지는 사람이 topic별로 판단해서 진행한다
# (이미 다른 곳에 게시된 콘텐츠를 조용히 덮어쓰면 위험하기 때문).
from __future__ import annotations

from pathlib import Path

from lib.mission_control_log import report_issue
from lib.rebuild_video import ROOT, select_format
from lib.youtube_upload import _is_already_uploaded, _sb_fetch_uploaded

_VIDEO_ASSEMBLER_SOURCES = [ROOT / "lib" / "video_assembler.py", ROOT / "lib" / "rebuild_video.py"]


def _uploaded_topics() -> set[str]:
    """WHY Supabase(2026-08-15): 로컬 output/youtube_uploaded.json은 더 이상
    쓰지 않는다(lib/youtube_upload.py 상단 WHY 참고) — 업로드된 topic은
    이제 그 테이블이 유일한 근거."""
    return _sb_fetch_uploaded()


def _source_mtime(fmt: str) -> float:
    """이 포맷을 만드는 코드가 마지막으로 수정된 시각. 판서형은 assemble()
    (video_assembler.py) + 인자 유도 로직(rebuild_video.py) 둘 다 걸린다 —
    둘 중 더 최근에 바뀐 쪽을 기준으로 삼는다."""
    if fmt == "chalkboard":
        paths = _VIDEO_ASSEMBLER_SOURCES
    else:
        paths = [ROOT / "lib" / "templates" / f"proto_{fmt}.py"]
    return max(p.stat().st_mtime for p in paths if p.exists())


def _find_video_file(lang_dir: Path) -> Path | None:
    candidates = [
        f for f in lang_dir.glob("*shorts*.mp4")
        if "instagram" not in f.name.lower()
    ]
    return candidates[0] if candidates else None


def find_stale_topics() -> list[dict]:
    """이미 유튜브에 업로드(예약 포함)된 topic은 제외 — 게시 끝난 콘텐츠는
    코드가 바뀌어도 재생성 대상이 아니라는 판단(2026-08-04, "유튜브에 이미
    업로드되었거나 예약되어있는 영상들은 어차피 신경안써도 되거든")."""
    uploaded = _uploaded_topics()
    stale: list[dict] = []
    output_dir = ROOT / "output"
    for topic_dir in sorted(output_dir.iterdir()):
        if not topic_dir.is_dir() or topic_dir.name.startswith("_"):
            continue
        for lang_dir in sorted(topic_dir.iterdir()):
            if not lang_dir.is_dir():
                continue
            topic = f"{topic_dir.name}/{lang_dir.name}"
            if _is_already_uploaded(topic, uploaded):
                continue
            video_file = _find_video_file(lang_dir)
            if video_file is None:
                continue
            fmt = select_format(topic)
            src_mtime = _source_mtime(fmt)
            video_mtime = video_file.stat().st_mtime
            if src_mtime > video_mtime:
                gap_hours = round((src_mtime - video_mtime) / 3600, 1)
                stale.append({
                    "topic": topic,
                    "format": fmt,
                    "video_path": str(video_file),
                    "video_mtime": video_mtime,
                    "code_mtime": src_mtime,
                    "gap_hours": gap_hours,
                })
                # mission-control에도 보고 — 미설정 세션이 대부분이라 실패해도
                # 조용히 넘어간다(lib/mission_control_log.py 상단 WHY 참고).
                report_issue(
                    severity="warning",
                    category="video_staleness",
                    entity=topic,
                    message=f"{topic} [{fmt}] 영상이 코드보다 {gap_hours}시간 오래됨(재생성 검토 대상)",
                )
    stale.sort(key=lambda x: -x["gap_hours"])
    return stale


def main() -> None:
    import datetime

    stale = find_stale_topics()
    if not stale:
        print("코드보다 오래된(재생성 필요) 미게시 topic 없음.")
        return
    print(f"{len(stale)}개 topic이 현재 코드보다 오래됨 (재생성 검토 대상, 미게시 topic만):\n")
    for item in stale:
        video_dt = datetime.datetime.fromtimestamp(item["video_mtime"]).strftime("%Y-%m-%d %H:%M")
        code_dt = datetime.datetime.fromtimestamp(item["code_mtime"]).strftime("%Y-%m-%d %H:%M")
        print(f"  {item['topic']:<20} [{item['format']}]  영상={video_dt}  코드={code_dt}  ({item['gap_hours']}시간 차이)")


if __name__ == "__main__":
    main()
