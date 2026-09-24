#!/bin/bash
# 앞 큐가 끝난 뒤 여섯 개를 최신 코드·설정으로 다시 조립한다.
# 라벨 위치(오른쪽 아래)와 결론 구간 건너뛰기는 코드 변경이라 rebuild_stale이 못 잡는다.
cd /Users/chlwjddms16/Desktop/project/health-shorts
while pgrep -f "[r]edo_all" >/dev/null; do sleep 20; done
for t in 비뇨기_16 대사_22 순환_12 눈_8 머리_14 고령_15; do
  echo "=== $t ==="
  .venv/bin/python3 scripts/xray_build.py "$t" --preview 2>&1 | grep -E "미리보기|shorts_xray|실패|부족"
done
echo "여섯 개 끝 — deploy 자동 반영됨"
