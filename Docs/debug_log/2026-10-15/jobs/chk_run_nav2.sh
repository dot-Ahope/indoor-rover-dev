#!/bin/bash
# (10-15 §29.2) 주행 뒤 nav2.log 요약: 제어 주기 놓침 · 컨트롤러 실패 · 복구 · 탈출 · 목표 결과 — 로버 안 움직임
L=/tmp/nav2.log
echo "제어 주기 놓침: $(grep -ac 'Control loop missed' $L)"
echo "후보 전부 충돌(Optimizer fail): $(grep -ac 'fail to compute path' $L)"
echo "복구 · 탈출: $(grep -ac 'Running monotone_escape' $L) 탈출 · $(grep -ac 'Running wait' $L) 대기 · $(grep -ac 'Running backup' $L) 후진"
grep -a "Goal succeeded\|Goal failed\|aborted\|Aborting" $L | tail -8 | cut -c1-200
grep -a "Control loop missed" $L | tail -3 | cut -c1-200
