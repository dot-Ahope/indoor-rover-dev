#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for cm in local_costmap global_costmap; do
  timeout 10 ros2 param set /$cm/$cm inflation_layer.inflation_radius 0.22 >/dev/null 2>&1
  timeout 10 ros2 param set /$cm/$cm inflation_layer.cost_scaling_factor 3.0 >/dev/null 2>&1
  echo -n "  $cm inflation: "; timeout 8 ros2 param get /$cm/$cm inflation_layer.inflation_radius 2>&1 | tail -1
done
timeout 15 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 5
echo "== 코스트맵 광선 (0.22) =="; python3 /tmp/job59g_costchk.py | tail -4
echo -n "Nav2 오류: "; grep -aicE "inflation.*inscribed|error" /tmp/nav2.log
