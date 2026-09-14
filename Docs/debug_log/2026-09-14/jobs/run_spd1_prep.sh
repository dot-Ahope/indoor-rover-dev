#!/bin/bash
# 손 배치 후: 재기동(job240) → 릴레이 중복 정리(job313) → readback 게이트(RPP 감속·decay·inflation)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
echo "=== 1. 재기동 (job240) ==="
bash $SPS/run_j.sh job240_clean.sh 15 2>&1 | grep -aE '에이전트|세션|중복|자세:|상자:|^   (0\.9|1\.[0-4])0 |최소폭'
echo "=== 2. 릴레이 중복 정리 ==="
bash $SPS/run_j.sh job313_relay_dedup.sh 2>&1 | grep -aE '릴레이 수|out hz|발행자'
echo "=== 3. readback 게이트 ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for p in FollowPath.cost_scaling_dist FollowPath.cost_scaling_gain FollowPath.inflation_cost_scaling_factor FollowPath.regulated_linear_scaling_min_speed FollowPath.desired_linear_vel FollowPath.max_allowed_time_to_collision_up_to_carrot; do printf 'RPP    %-46s ' \$p; timeout 8 ros2 param get /controller_server \$p 2>&1 | tail -1; done; for p in stvl_layer.voxel_decay inflation_layer.cost_scaling_factor footprint_padding; do printf 'local  %-46s ' \$p; timeout 8 ros2 param get /local_costmap/local_costmap \$p 2>&1 | tail -1; done; for p in inflation_layer.inflation_radius inflation_layer.cost_scaling_factor; do printf 'global %-46s ' \$p; timeout 8 ros2 param get /global_costmap/global_costmap \$p 2>&1 | tail -1; done"
