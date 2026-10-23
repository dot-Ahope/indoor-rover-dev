#!/bin/bash
# 10-23 §10 vslam:=on prep — 운용(프로젝터 상시 끔 · SHM · 프리셋 3 기본 · 통합 2.0)에서 주 EKF 의 odom1 을 rf2o 대신 cuVSLAM 병진 속도로(ekf.launch vslam:=on)
SENSORS_ADD="emitter_off:=true vslam:=on dds_shm:=true" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|SHM 고아\|cuVSLAM(컨테이너)\|wheel_odom\|nvblox_up" | tail -8
source /opt/ros/humble/setup.bash
echo "visual_preset = $(ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
echo "주 EKF odom1 = $(timeout 8 ros2 param get /ekf_filter_node odom1 2>&1 | tail -1) · rf2o 노드 $(pgrep -fc rf2o_laser_odometry_node) · vslam_twist $(pgrep -fc vslam_twist.py)"
