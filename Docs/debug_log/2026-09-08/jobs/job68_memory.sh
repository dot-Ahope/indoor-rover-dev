#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
bash /tmp/job25e_nav2start.sh > /tmp/nav2start.out 2>&1; sleep 8
echo -n "local depth raytrace_min: "; timeout 8 ros2 param get /local_costmap/local_costmap voxel_layer.depth.raytrace_min_range 2>&1 | tail -1
echo -n "global depth raytrace_min: "; timeout 8 ros2 param get /global_costmap/global_costmap voxel_layer.depth.raytrace_min_range 2>&1 | tail -1
echo -n "stuck_monitor: "; grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | sed "s/.*, //"
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 4
echo "== 현재 장면 (상자 위치) =="; python3 /tmp/job62c_boxdim.py 2>/dev/null | sed -n '4,12p'
echo "== 주변 여유 =="; bash /tmp/job21c_where.sh 2>&1 | tail -4
