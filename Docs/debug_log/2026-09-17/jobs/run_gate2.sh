#!/bin/bash
# 재부팅 뒤 /tmp 소실 대비: 감사 도구 전송 → 릴레이 고아 → readback → 게이트 (재기동 없음)
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job248_audit.py job315_boxcells.py job314_relay_orphan.sh job348_readback2.sh; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/$f || { echo "scp 실패 $f"; exit 1; }; done
echo "=== 릴레이 ==="; timeout 60 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job314_relay_orphan.sh" 2>&1 | grep -aE "남은 릴레이|발행자"
echo "=== readback ==="; timeout 150 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job348_readback2.sh" 2>&1 | grep -avE "stuck_monitor 파라미터|    (shadow|stuck_shadow|ratio_threshold|min_cmd_dist|window_sec):"
echo "=== 프로세스·부하 ==="; timeout 30 sshpass -p <PW> ssh $O jetson@$H 'for p in robot_state_publisher slam_toolbox ekf_node depth_relay controller_server planner_server bt_navigator; do printf "%s:%s " $p $(pgrep -fc $p); done; echo; echo "load $(cut -d" " -f1-3 /proc/loadavg)  shadow_mode: $(grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | grep -aoE "SHADOW|ACTIVE")"'
echo "=== 게이트 ==="; JETSON_HOST=$H bash $SPS/run_gate.sh ${1:-1.17} ${2:-0.0}
