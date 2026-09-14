#!/bin/bash
# min_obstacle_height 0.08 배포 → nav2 재기동(job249) → readback → 정지 검증(job312: 코스트맵 상자 범위) → 회전 게이트 → 정렬 → 상자 재검출
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
FACE=${1:--3.7}
tr -d '\r' < $SPS/nav2_params.yaml > /tmp/nav2_params.yaml
sshpass -p <PW> scp $OPT -q /tmp/nav2_params.yaml $J:/tmp/nav2_params.yaml || exit 1
echo "=== 1. nav2 재기동 (job249) ==="
timeout 240 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash /tmp/job249_nav2only.sh 2>&1 | grep -aE '검증|중복|자세:|상자:|최소폭' | head -8"
echo "=== 2. readback ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for n in /local_costmap/local_costmap /global_costmap/global_costmap; do printf '%-32s ' \$n; timeout 8 ros2 param get \$n stvl_layer.depth_mark.min_obstacle_height 2>&1 | tail -1; done; printf 'RPP cost_scaling_dist '; timeout 8 ros2 param get /controller_server FollowPath.cost_scaling_dist 2>&1 | tail -1"
echo "=== 3. 정지 검증: 상자 코스트맵 범위 (20 s 뒤) ==="
timeout 200 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; sleep 10; L=\$(BOX_HINT='1.06 0.03' python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:'); echo \"\$L\"; BX=\$(echo \"\$L\" | grep -aoE 'x=[0-9.]+' | cut -d= -f2); BY=\$(echo \"\$L\" | grep -aoE 'y=[-+0-9.]+' | cut -d= -f2); TOPIC=/camera/depth/points_filtered ZTH=0.08 python3 /tmp/job312_box_edge.py \$BX \$BY 12 2>&1 | grep -aE '코스트맵|y 열별'"
echo "=== 4. 회전 게이트 + 정렬 $FACE° + 재검출 ==="
timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; python3 /tmp/job228_why.py 2>&1 | sed -n '/제자리 회전 투영/,/라이다 방위별/p' | grep -aE '^ +[-+] ?[0-9]+ ' | awk '{m=(\$2>m)?\$2:m} END{print \"  ±60° 최대비용 \" m (m>=100?\"  → BLOCK, 회전 금지\":\"  → 통과\")}'; python3 /tmp/job225_face.py $FACE 1.5 2>&1 | tail -1; sleep 3; BOX_HINT='1.05 -0.06' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자:'"
