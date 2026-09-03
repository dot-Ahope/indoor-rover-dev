#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 1) 보드 세션 (RESET 후) ==="
bash /tmp/chk_board.sh
echo -n "  fault 상태: "; timeout 6 ros2 topic echo /rover/status --once 2>/dev/null | grep -aoE "message: .*" | head -1 || echo "조회실패"
echo ""
echo "=== 2) EKF/slam 초기화 ==="
bash /tmp/job33a_reset_noagent.sh | grep -aE "gyro bias|odometry/filtered|odom 원점|/scan"
echo ""
echo "=== 3) Nav2 기동 (RPP + no-spin BT) ==="
bash /tmp/job25e_nav2start.sh | grep -aE "active|미기동|ERROR" | grep -av "get_state"
echo -n "  FollowPath.plugin: "; timeout 8 ros2 param get /controller_server FollowPath.plugin 2>/dev/null | grep -aoE "nav2_[a-z_]+::[A-Za-z]+" || echo "조회지연"
echo -n "  BT xml: "; timeout 8 ros2 param get /bt_navigator default_nav_to_pose_bt_xml 2>/dev/null | grep -aoE "[a-z_]+\.xml" || echo "조회지연"
echo -n "  inflation: "; timeout 8 ros2 param get /local_costmap/local_costmap inflation_layer.inflation_radius 2>/dev/null | grep -aoE "[0-9.]+$"
echo "  설정 오류: $(grep -aE 'ERROR' /tmp/nav2.log | grep -av 'get_state\|get_param' | wc -l)건"
echo ""
echo "=== 4) 공간 ==="
bash /tmp/job21c_where.sh | sed -n '3,18p'
bash /tmp/job27b_profile.sh | grep -aE "직진 경로상|우회 방향"
