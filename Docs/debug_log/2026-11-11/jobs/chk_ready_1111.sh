#!/bin/bash
# chk_ready_1111 — 11-11 §5 반복 시험 전 Jetson 준비 상태(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   보는 것: 부팅 시각 · 주소 · /dev/rover · 사용자 서비스 rover-base · 에이전트 컨테이너 · 보드 세션 수립 · 에이전트 로그 끝(토픽 생성) · /tmp prep 도구 수 · 디스크.
#   인자: 없음. 출력: 표준 출력.
echo "부팅 $(uptime -s) · $(ip -4 -o addr show wlP1p1s0 | awk '{print $4}') · rover -> $(readlink /dev/rover) · 디스크 남음 $(df -h / | awk 'NR==2{print $4}')"
echo "rover-base(사용자 서비스): $(systemctl --user is-active rover-base 2>/dev/null)"
echo "컨테이너: $(docker ps --format '{{.Names}}' | tr '\n' ' ')"
echo "보드 세션 수립 $(docker logs microros_agent 2>&1 | grep -ac 'session established') 건 · 발행자 생성 $(docker logs microros_agent 2>&1 | grep -ac 'publisher created') 건"
echo "/tmp prep 도구: $(ls /tmp/prep_fast.sh /tmp/prep_patrol.sh /tmp/chk_prep.py /tmp/chk_drive_gate.py 2>/dev/null | wc -l)/4"
