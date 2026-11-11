#!/bin/bash
# chk_live_marks_1111 — 11-11 §5: 사용자 질문 "시작 뒤 실제로 움직일 때까지 얼마나 걸렸나" — 러너 · prep 의 단계 시각만 뽑음(읽기만 · 로버 영향 없음 · DDS 참여자 안 만듦).
#   보는 것: /tmp/live/current.log 의 '=====' 머리글(run_jn · run_f0 가 찍는 시작 · 끝 시각), prep 원문의 단계 머리줄 · ⏱ 줄,
#            러너 원문의 게이트 · 주행 · 상주 경로 조회기 · 목표 1 출발 줄. 인자: $1 주행 이름(기본 f2rr1) · $2 prep 번호(기본 rr1). 출력: 표준 출력.
N=${1:-f2rr1}; P=${2:-rr1}
echo "== live 머리글(오늘)"; grep -a '^=====' /tmp/live/current.log | tail -8 | cut -c1-170
echo "== prep 단계(/tmp/prep_full_smac_$P.txt)"; grep -aE '^##########|⏱' /tmp/prep_full_smac_$P.txt | cut -c1-120
echo "== 러너 앞부분(/tmp/f0_$N.log)"; grep -aE '##########|상주 경로|목표 1 출발|경로 자동 yaw' /tmp/f0_$N.log | head -5 | cut -c1-170
echo "== nav2 첫 목표"; grep -a 'Begin navigating' /tmp/nav2.log | head -1 | cut -c1-170
echo "== /cmd_vel 첫 0 아닌 값 시각은 bag 에서(주행 뒤)"
