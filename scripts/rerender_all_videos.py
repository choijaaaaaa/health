# 영상 레이아웃·오버레이 코드를 바꾼 뒤 기존 숏츠 전량을 다시 조립한다(TTS 재호출 없음).
# WHY: rebuild_video는 기존 narration.mp3를 재사용하므로 비용 없이 반영된다. 레이아웃 수정
# (배너 제거·CTA 지연·네이버 안전영역 등)은 코드만 고치고 끝내면 실제 영상엔 안 들어간다 —
# 이미 한 번 스크래치패드 스크립트로 돌렸다가 세션 재시작 때 사라져서 저장소로 옮겼다.
#
# 사용: .venv/bin/python3 scripts/rerender_all_videos.py [topic ...]   # 인자 없으면 output/*/shorts.mp4 전부
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python3")


def main() -> None:
    topics = sorted(p.parent.name for p in (ROOT / "output").glob("*/shorts.mp4"))
    if sys.argv[1:]:
        topics = [t for t in topics if t in sys.argv[1:]]
    ok, fail = [], []
    t0 = time.time()
    for i, t in enumerate(topics, 1):
        r = subprocess.run([PY, "-m", "lib.rebuild_video", t], cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0:
            ok.append(t)
        else:
            err = (r.stderr or r.stdout).strip().splitlines()
            fail.append((t, err[-1][:160] if err else "?"))
            print(f"FAIL {t}: {fail[-1][1]}", flush=True)
        if i % 5 == 0 or i == len(topics):
            el = time.time() - t0
            print(f"  {i}/{len(topics)}  경과 {el / 60:.0f}분  남은 예상 {el / i * (len(topics) - i) / 60:.0f}분", flush=True)
    print(f"\n재조립 완료 {len(ok)}/{len(topics)}, 실패 {len(fail)}")
    for t, e in fail:
        print(f"  {t}: {e}")


if __name__ == "__main__":
    main()
