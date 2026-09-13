#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
tr -d '\r' < $SPS/job306_depth_live.py > /tmp/job306.py
sshpass -p <PW> scp $OPT -q /tmp/job306.py $J:/tmp/job306_depth_live.py || exit 1
echo "=== 스택 상태 (노드 수) ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; timeout 10 ros2 node list 2>/dev/null | grep -cE 'camera|controller_server|planner_server|slam|ekf'; timeout 6 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1"
echo "=== RealSense 필터/프로파일 파라미터 (live) ==="
sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; for p in depth_module.depth_profile depth_module.visual_preset decimation_filter.enable spatial_filter.enable temporal_filter.enable hole_filling_filter.enable disparity_filter.enable pointcloud.enable pointcloud.stream_filter pointcloud.allow_no_texture_points pointcloud.ordered_pc clip_distance align_depth.enable depth_module.exposure depth_module.enable_auto_exposure; do printf '%-40s ' \$p; timeout 5 ros2 param get /camera/camera \$p 2>&1 | tail -1; done"
echo "=== 정지 깊이 표본 8 s ==="
timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job306_depth_live.py 8 2>&1 | grep -av '^\[INFO\]'"
echo "=== v5 정체 직후 프레임(T+0.35) 모서리 ==="
timeout 300 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job303_bagstall.py /tmp/bag_v5 1789116146.35 2>&1 | grep -av 'Opened database' | grep -aE '로컬|둘레|최근접|틈'"
