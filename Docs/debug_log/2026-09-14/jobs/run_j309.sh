#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. YAML 배포 (src + install) ==="
tr -d '\r' < $SPS/nav2_params.yaml > /tmp/nav2_params.yaml
sshpass -p <PW> scp $OPT -q /tmp/nav2_params.yaml $J:~/ros2_ws/src/rover_navigation/config/nav2_params.yaml || exit 1
sshpass -p <PW> ssh $OPT $J "cp ~/ros2_ws/src/rover_navigation/config/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/ && grep -nE '^\s+(inflation_radius|cost_scaling_factor):' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml"
echo "=== 2. nav2 재기동 (job249) ==="
tr -d '\r' < $SPS/job249_nav2only.sh > /tmp/job249.sh; sshpass -p <PW> scp $OPT -q /tmp/job249.sh $J:/tmp/job249_nav2only.sh
timeout 240 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash /tmp/job249_nav2only.sh 2>&1 | tail -25"
echo "=== 3. 라이브 readback 게이트 ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for p in inflation_layer.inflation_radius inflation_layer.cost_scaling_factor footprint_padding; do printf 'global %-36s ' \$p; timeout 8 ros2 param get /global_costmap/global_costmap \$p 2>&1 | tail -1; done; for p in inflation_layer.inflation_radius inflation_layer.cost_scaling_factor; do printf 'local  %-36s ' \$p; timeout 8 ros2 param get /local_costmap/local_costmap \$p 2>&1 | tail -1; done"
echo "=== 4. 라이다 고정점 판정 (정지 6 s) ==="
tr -d '\r' < $SPS/job309_lidar_fixed.py > /tmp/job309.py; sshpass -p <PW> scp $OPT -q /tmp/job309.py $J:/tmp/job309_lidar_fixed.py
timeout 60 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job309_lidar_fixed.py 2>&1 | grep -av '^\[INFO\]'"
