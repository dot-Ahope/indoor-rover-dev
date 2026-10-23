#!/bin/bash
# 10-23 §17 A 시험 prep — 운용 기본(prep_patrol: vslam on · 프로젝터 끔 · SHM) + 주기 재계획 끔(REPLAN_HZ 0.01 = 목표당 1 회, 막힘 · 목표 변경 때만 재계획)
REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "prep_patrol:\|PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|SHM 고아\|cuVSLAM(컨테이너)\|wheel_odom\|nvblox_up" | tail -9
source /opt/ros/humble/setup.bash
echo "visual_preset = $(ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
echo "주 EKF odom1 = $(timeout 8 ros2 param get /ekf_filter_node odom1 2>&1 | tail -1) · rf2o $(pgrep -fc rf2o_laser_odometry_node)"
echo "BT RateController: $(grep -ao 'RateController hz="[0-9.]*"' /tmp/nav_to_pose_active.xml 2>/dev/null || echo '사본 없음(기본 BT 0.01)') · bt_navigator 인자 $(pgrep -fa bt_navigator | grep -o 'default_nav_to_pose_bt_xml[^ ]*' | head -1)"
