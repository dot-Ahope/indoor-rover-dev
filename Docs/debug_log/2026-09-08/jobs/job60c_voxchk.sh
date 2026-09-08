#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "pointcloud Hz: "; timeout 8 ros2 topic hz /camera/camera/depth/color/points 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo -n "pointcloud 크기: "; timeout 8 ros2 topic echo --once /camera/camera/depth/color/points --field width 2>/dev/null | head -1
bash /tmp/job25e_nav2start.sh > /tmp/nav2start.out 2>&1; grep -ac "active \[3\]" /tmp/nav2start.out | sed "s/^/  Nav2 active 노드: /"
echo -n "local plugins: "; timeout 10 ros2 param get /local_costmap/local_costmap plugins 2>/dev/null | tail -1
echo -n "local sources: "; timeout 10 ros2 param get /local_costmap/local_costmap voxel_layer.observation_sources 2>/dev/null | tail -1
echo -n "costmap 오류: "; grep -aiE "voxel|depth|pointcloud" /tmp/nav2.log | grep -aicE "error|fail|exception"
grep -aiE "voxel|depth|pointcloud" /tmp/nav2.log | grep -aiE "error|fail|warn" | head -3
sleep 5; echo "== CPU (3초 평균) =="; top -bn4 -d1 | awk '/^top/{i++} i>=2 && /python3|realsen|async_s|rplidar|ekf_node|controller|planner|foxglove/ {c[$12]+=$9; n[$12]++} END{for(k in c) printf "%5.1f%% %s\n", c[k]/n[k], k}' | sort -rn | head -8
echo -n "load: "; cut -d" " -f1-3 /proc/loadavg
echo -n "배터리: "; timeout 5 ros2 topic echo --once /battery 2>/dev/null | grep -E "^voltage"
