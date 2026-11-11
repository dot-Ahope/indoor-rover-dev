#!/bin/bash
# chk_f2dm2_left_1111 — 11-11: 11-10 f2dm2 주행이 강제 종료(사용자)로 끝난 뒤 Jetson 에 남은 기록 확인(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: PC 러너가 출발(17:55:17) 뒤 끊겨 회수를 못 함. 기록 원천은 Jetson /tmp(job551 이 bag_<이름>/ · f0_<이름>.log · tegra · top 등을 씀) —
#       재부팅이면 /tmp 가 지워졌을 수 있다.
#   보는 것: 부팅 시각 · /tmp 의 f2dm2 파일 · bag 폴더(metadata.yaml 유무 = 정상 종료 여부, db3/mcap 크기) · 홈의 bags 사본 · prep logkeep.
#   인자: 없음. 출력: 표준 출력.
echo "== 부팅 $(uptime -s) · 지금 $(date '+%F %T') · 가동 $(uptime -p)"
echo "== /tmp 의 f2dm2"; ls -la --time-style=+%m-%d_%H:%M /tmp/*f2dm2* 2>/dev/null | awk '{print "  "$1, $5, $6, $7}'
echo "== bag 폴더"; ls -la --time-style=+%m-%d_%H:%M /tmp/bag_f2dm2/ 2>/dev/null | awk '{print "  "$5, $6, $7}'
echo "== 홈 bags"; ls -d /home/jetson/bags/*f2dm2* 2>/dev/null
echo "== /tmp/logkeep 최근"; ls -1t /tmp/logkeep 2>/dev/null | head -4
echo "== /tmp 파일 수 $(ls /tmp | wc -l)"
