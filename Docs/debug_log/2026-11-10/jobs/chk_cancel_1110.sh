#!/bin/bash
# chk_cancel_1110 — 11-10 §6: f2dm1 목표 5 CANCELED(49.8 s, 러너 한도 81 s 전) 는 누가 취소했나(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   보는 것: /tmp/nav2.log 에서 nav_guard · stuck_monitor · bt_navigator · controller_server 의 경고 · 오류 · 취소 줄(목표 4 끝 무렵 17:30 ~ 17:31:30),
#            /tmp/f0_f2dm1.log 원문. 인자: $1 = 시작 시각 HH:MM(기본 17:30). 출력: 표준 출력.
#   nav2.log 는 다음 prep 이 비우므로(prep_fast 가 /tmp/logkeep 에 보관) PC outputs/ 로 회수할 원문은 아래 줄 전부.
S=${1:-17:30}
echo "== nav2.log 줄 수 $(wc -l < /tmp/nav2.log)"
echo "== nav_guard · stuck_monitor 전체(WARN 이상 · 판정 줄)"
grep -aE '\[nav_guard\]|\[stuck_monitor\]' /tmp/nav2.log | grep -avE 'INFO\] \[[0-9.]+\] \[stuck_monitor\]: (ok|tick)' | tail -40 | cut -c1-230
echo "== bt_navigator · controller · planner · behavior 경고/오류(끝 60)"
grep -aE '\[(bt_navigator|controller_server|planner_server|behavior_server|smoother_server)' /tmp/nav2.log | grep -aE 'WARN|ERROR|cancel|Cancel|abort|Abort|fail|Fail|blocked|Blocked|escape|Escape' | tail -60 | cut -c1-230
# 1 차 실행이 중단된 뒤 덧붙임(f2dm1h 가 '경로 없음' 으로 ABORTED): 계획기가 왜 못 찾았나 — 시작 · 목표 칸 비용 경고
echo "== planner_server 시작/목표 칸 관련(끝 20)"
grep -aE '\[planner_server' /tmp/nav2.log | grep -aiE 'start|goal|lethal|occupied|no valid|failed to create|out of bounds' | tail -20 | cut -c1-230
