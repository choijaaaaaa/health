#!/bin/bash
# 오늘 바뀐 것(도입부 겹침 제거·라벨·기전 다양화·요약 배지)이 전부 반영되게 xray topic 전체 재조립.
cd /Users/chlwjddms16/Desktop/project/health-shorts
for t in 비뇨기_16 순환_12 대사_22 눈_8 머리_14 고령_15 대사_14 비뇨기_18 소화_1 소화_11 소화_13 소화_14 소화_18 소화_20 소화_21 소화_24 소화_9 순환_3 어지럼증_16 여성_4 여성_6 여성_7; do
  echo "=== $t ==="
  .venv/bin/python3 scripts/xray_build.py "$t" --preview 2>&1 | grep -E "미리보기|shorts_xray|실패|부족"
done
echo "전체 재조립 끝"
