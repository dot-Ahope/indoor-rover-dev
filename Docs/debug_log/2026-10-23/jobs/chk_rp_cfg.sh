#!/bin/bash
# 10-23 §17 f2rp1 prep 뒤 설정 확인(출력 끊김 대비 따로) — 로버 안 움직임
echo "visual_preset = $(ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
echo "주 EKF odom1 = $(timeout 8 ros2 param get /ekf_filter_node odom1 2>&1 | tail -1) · rf2o $(pgrep -fc rf2o_laser_odometry_node)"
echo "BT RateController: $(grep -ao 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml 2>/dev/null || echo '사본 없음(기본 BT 0.01)') · bt_navigator 인자 $(pgrep -fa bt_navigator | grep -o 'default_nav_to_pose_bt_xml[^ ]*' | head -1)"
