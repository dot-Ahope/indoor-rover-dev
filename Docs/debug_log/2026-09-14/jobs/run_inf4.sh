#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 재기동 (job240) ==="
bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|^   (0\.9|1\.[0-4])0 |최소폭'
echo "=== 2. readback 게이트 ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for p in stvl_layer.voxel_decay inflation_layer.inflation_radius footprint_padding; do printf 'local  %-32s ' \$p; timeout 8 ros2 param get /local_costmap/local_costmap \$p 2>&1 | tail -1; done; for p in stvl_layer.voxel_decay inflation_layer.inflation_radius inflation_layer.cost_scaling_factor; do printf 'global %-32s ' \$p; timeout 8 ros2 param get /global_costmap/global_costmap \$p 2>&1 | tail -1; done; printf 'depth_relay 프로세스 '; pgrep -fc 'depth_relay.py' | head -1; printf 'STVL 구독 '; timeout 8 ros2 topic info /camera/depth/points_filtered 2>/dev/null | grep -a 'Subscription count'"
