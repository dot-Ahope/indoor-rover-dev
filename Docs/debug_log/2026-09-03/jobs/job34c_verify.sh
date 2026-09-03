#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 활성 컨트롤러 / tolerance / inflation ==="
timeout 8 ros2 param get /controller_server FollowPath.plugin 2>/dev/null || echo "  (조회 지연)"
timeout 8 ros2 param get /controller_server general_goal_checker.xy_goal_tolerance 2>/dev/null
timeout 8 ros2 param get /local_costmap/local_costmap inflation_layer.inflation_radius 2>/dev/null
echo "=== 기동 오류 재확인 ==="
grep -aE "ERROR" /tmp/nav2.log | grep -av "get_state\|get_parameters" | tail -3 || echo "  없음"
echo "  bt_navigator: $(timeout 8 ros2 lifecycle get /bt_navigator 2>/dev/null || echo 조회지연)"
