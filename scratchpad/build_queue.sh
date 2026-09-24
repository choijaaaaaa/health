#!/bin/bash
# 순차 조립 — 병렬로 돌리면 ffmpeg가 CPU를 다 먹어 다른 작업이 멈춘다(로드 32 실측).
cd /Users/chlwjddms16/Desktop/project/health-shorts
for t in 대사_22 순환_12 머리_14 눈_8 고령_15; do
  echo "=== $t ==="
  .venv/bin/python3 scripts/xray_build.py "$t" --preview 2>&1 | grep -E "미리보기|shorts_xray|⚠️|실패|장면 부족"
done
echo "큐 끝"
