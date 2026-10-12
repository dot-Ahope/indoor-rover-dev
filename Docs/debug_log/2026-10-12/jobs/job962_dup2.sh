#!/bin/bash
# 10-12 §3.4: 중복 확인 보강 — nvblox 실행 파일 수, 데몬 없이 본 노드 목록, 주행 러너 잔류물. 로버 안 움직임
echo "== 컨테이너 nvblox 프로세스:"; docker exec isaac_ros_dev-aarch64-container bash -c "ps -eo pid,lstart,args --no-headers | grep -a nvblox | grep -v grep | cut -c1-150" 2>/dev/null | sed 's/^/  /'
echo "== 데몬 없이 본 노드 이름 중복(--no-daemon, 12 s 탐색):"
timeout 40 ros2 node list --no-daemon --spin-time 12 2>/dev/null | sort | uniq -c | awk '$1>1{print "  ★ "$0}'; echo "  (위에 ★ 가 없으면 중복 없음)"
echo "== rf2o 프로세스: $(pgrep -fa rf2o_laser_odometry_node | cut -c1-120)"
echo "== 주행 러너 잔류물(bag 기록·tail·top·tegrastats·job 스크립트):"
ps -eo pid,lstart,etimes,args --no-headers | grep -aE "ros2 bag|tail -n|tegrastats|top -b|job5[0-9][0-9]|job9[0-9][0-9]|job6[0-9][0-9]|/tmp/job" | grep -av "grep\|job962" | cut -c1-170 | sed 's/^/  /'
echo "== ros2 데몬: $(pgrep -fa 'ros2.*daemon\|_ros2_daemon' | cut -c1-100)"
