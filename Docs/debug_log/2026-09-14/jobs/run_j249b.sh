#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/nav2_params.yaml > /tmp/nav2_params.yaml
sshpass -p <PW> scp $OPT -q /tmp/nav2_params.yaml $J:/tmp/nav2_params.yaml || exit 1
echo "=== nav2 재기동 (job249, /tmp/nav2_params.yaml 검증→배포→재기동) ==="
timeout 240 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash /tmp/job249_nav2only.sh 2>&1 | tail -22"
echo "=== 라이브 readback 게이트 ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for p in inflation_layer.inflation_radius inflation_layer.cost_scaling_factor footprint_padding; do printf 'global %-36s ' \$p; timeout 8 ros2 param get /global_costmap/global_costmap \$p 2>&1 | tail -1; done; for p in inflation_layer.inflation_radius inflation_layer.cost_scaling_factor footprint_padding; do printf 'local  %-36s ' \$p; timeout 8 ros2 param get /local_costmap/local_costmap \$p 2>&1 | tail -1; done; printf 'RPP max_allowed_time_to_collision_up_to_carrot '; timeout 8 ros2 param get /controller_server FollowPath.max_allowed_time_to_collision_up_to_carrot 2>&1 | tail -1"
