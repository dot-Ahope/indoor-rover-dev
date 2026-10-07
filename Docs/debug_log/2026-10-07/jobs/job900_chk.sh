#!/bin/bash
# 10-07 시작 점검: 가동 시간, 스택 프로세스, 재생에 필요한 파일
echo "uptime: $(uptime -p)"; echo "프로세스: ekf $(pgrep -fc '[e]kf_node') · 게이트 $(pgrep -fc '[r]f2o_gate') · agent $(pgrep -fc '[m]icro_ros_agent') · slam $(pgrep -fc '[s]lam_toolbox') · nav2 $(pgrep -fc '[c]ontroller_server')"
for f in /tmp/bag_step1/metadata.yaml /tmp/occ_scan.py /tmp/occ_rec.py /tmp/occ_run.sh; do [ -e $f ] && echo "있음 $f" || echo "없음 $f"; done
grep -c v_mode ~/ros2_ws/install/rover_bringup/lib/rover_bringup/rf2o_gate.py; free -m | sed -n 2p; df -h /tmp | tail -1
