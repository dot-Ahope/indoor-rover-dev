#!/bin/bash
NAME=${1:-pd1}; GL=${2:-0.35}; D=${3:-1.8}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 재기동 ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|최소폭'
echo "=== 2. 릴레이 정리 ==="; bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|발행자'
echo "=== 3. readback ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for n in /local_costmap/local_costmap /global_costmap/global_costmap; do printf '%-32s padding ' \$n; timeout 8 ros2 param get \$n footprint_padding 2>&1 | tail -1; done; printf 'BT planner_id '; grep -oE 'planner_id=\"[A-Za-z]+\"/>' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml"
L=$(timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; BOX_HINT='1.1 0.0' python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:'"); echo "$L"
BX=$(echo "$L" | grep -aoE 'x=[0-9.]+' | cut -d= -f2); BY=$(echo "$L" | grep -aoE 'y=[-+0-9.]+' | cut -d= -f2 | tr -d +)
echo "=== 4. 주행 $NAME (Smac BT, D $D, 횡 $GL, 게이트: 상자 $BX $BY ±0.06, 창 ≥0.20, 근거 없는 셀 ≤1) ==="
bash $SPS/run_inf1.sh $NAME $D $BX $BY 0.06 $GL 2>&1 | grep -avE '^ +[0-9]+\.[0-9] \+|^   (0\.9|1\.[0-4])0 '
