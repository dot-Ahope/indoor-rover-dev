#!/bin/bash
# 전역에 depth 가 안 찍히는 원인 후보를 런타임으로 하나씩 배제한다. 주행 없음.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
probe(){ echo "  → $1"; python3 /tmp/job73_probe.py 2>/dev/null | sed -n '1p;4p'; }
clear_g(){ timeout 15 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1; sleep 5; }
echo "=== A. 기준 상태 ==="; clear_g; probe "static_layer ON, 기본"
echo "=== B. static_layer 끄기 (SLAM 라이다 지도가 depth 마킹을 덮는지) ==="
timeout 10 ros2 param set /global_costmap/global_costmap static_layer.enabled false >/dev/null 2>&1
clear_g; probe "static_layer OFF"
echo "=== C. static 복구 + depth 높이/사거리 완화 ==="
timeout 10 ros2 param set /global_costmap/global_costmap static_layer.enabled true >/dev/null 2>&1
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.min_obstacle_height -1.0 >/dev/null 2>&1
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.obstacle_max_range 3.0 >/dev/null 2>&1
clear_g; probe "min_h -1.0, max_range 3.0"
echo "=== D. 원복 ==="
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.min_obstacle_height 0.08 >/dev/null 2>&1
timeout 10 ros2 param set /global_costmap/global_costmap voxel_layer.depth.obstacle_max_range 1.2 >/dev/null 2>&1
clear_g; probe "원복 확인"
