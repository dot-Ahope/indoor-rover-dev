#!/bin/bash
# chk_nav2_run_1111 — 11-11 §5: 반복 회차의 nav2 로그 집계(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦). 판정 ③ TF 외삽 실패 0 확인용.
#   보는 것: /tmp/nav2.log(prep 이 다음 기동 때 비움 — 회차 끝나자마자 돌린다) 의 TF 외삽 · 목표 실패 · 막힘 정지 · 복구 · 주기 놓침 · Smac 실패 수,
#            막힘 정지 · 복구 줄 원문. 인자: 없음. 출력: 표준 출력.
F=/tmp/nav2.log; echo "== $F $(wc -l < $F) 줄"
c(){ printf '  %-28s %s\n' "$1" "$(grep -ac "$2" $F)"; }
c 'TF 외삽(extrapolat)' 'xtrapolat'
c 'Goal failed · ABORT' 'Goal failed'
c '막힘 정지(지속 → 중단)' '지속 → 주행 중단'
c 'monotone_escape 실행' 'Running monotone_escape'
c 'Wait 실행' 'Running wait'
c '주기 놓침' 'missed its desired rate'
c 'Smac 실패' 'SmacHybrid failed'
c '스무더 충돌' 'Smoothed path leads to a collision'
c 'nav_guard 개입' 'nav_guard 개입'
echo "== 막힘 정지 · 복구 줄"; grep -aE '지속 → 주행 중단|Running (monotone_escape|wait)|nav_guard 개입' $F | sed -E 's/^\[[^]]*\] //' | cut -c1-190
