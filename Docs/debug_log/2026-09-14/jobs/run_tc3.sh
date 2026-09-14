#!/bin/bash
NAME=${1:-tc3}; D=${2:-1.8}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 재기동 ==="; bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|최소폭'
echo "=== 2. 릴레이 고아 정리 ==="; bash $SPS/run_j.sh job314_relay_orphan.sh 2>&1 | grep -aE '남은 릴레이|발행자'
echo "=== 3. readback ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for p in max_allowed_time_to_collision_up_to_carrot cost_scaling_dist regulated_linear_scaling_min_speed; do printf 'RPP %-42s ' \$p; timeout 8 ros2 param get /controller_server FollowPath.\$p 2>&1 | tail -1; done; printf 'local moh '; timeout 8 ros2 param get /local_costmap/local_costmap stvl_layer.depth_mark.min_obstacle_height 2>&1 | tail -1"
echo "=== 4. 정지 표본: 상자 앞 띠 (회전 없음, 필터 토픽 15 s) ==="
L=$(timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; BOX_HINT='1.1 -0.08' python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:'"); echo "$L"
BX=$(echo "$L" | grep -aoE 'x=[0-9.]+' | cut -d= -f2); BY=$(echo "$L" | grep -aoE 'y=[-+0-9.]+' | cut -d= -f2)
timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; TOPIC=/camera/depth/points_filtered ZTH=0.08 python3 /tmp/job312_box_edge.py $BX $BY 15 2>&1 | grep -aE '^  (핵심|앞쪽|좌측)|코스트맵'"
echo "=== 5. 주행 $NAME D=$D (게이트: 상자 y $BY ±0.06, 창 ≥0.20) ==="
bash $SPS/run_inf1.sh $NAME $D $BX $BY 0.06 2>&1 | grep -avE '^ +[0-9]+\.[0-9] \+'
