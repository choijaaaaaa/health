#!/bin/bash
cd /Users/chlwjddms16/Desktop/project/health-shorts
for t in 순환_12 대사_22 비뇨기_16 눈_8 머리_14 고령_15; do
  echo "=== $t ==="
  .venv/bin/python3 scripts/xray_build.py "$t" --preview 2>&1 | grep -E "미리보기|shorts_xray|실패|부족"
done
echo "여섯 개 완료 — deploy 자동 반영"
