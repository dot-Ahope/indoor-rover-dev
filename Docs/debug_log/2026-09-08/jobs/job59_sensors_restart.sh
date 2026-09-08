#!/bin/bash
# Jetson 측: 센서(camera/lidar/foxglove/EKF)+slam 재시작, agent 유지. 로버 정지 필수(자이로 캘리브 10s).
# ⚠ ssh 인라인으로 실행하지 말 것 — pkill -f 가 명령 문자열 속 이름과 자기매칭해 셸을 죽임(09-08 실사례). 파일로 실행.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pkill -f "ros2 launch rover_navigation" 2>/dev/null
for p in controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor; do pkill -9 -f "$p" 2>/dev/null; done
pkill -f "ros2 launch rover_bringup sensors" 2>/dev/null; pkill -f "ros2 launch rover_bringup slam" 2>/dev/null
for p in realsense2_camera_node rplidar_node foxglove_bridge ekf_node sensor_conditioner scan_deskew scan_restamp async_slam_toolbox depthimage_to_laserscan; do pkill -9 -f "$p" 2>/dev/null; done
sleep 4
echo "잔존: $(pgrep -f 'realsense2_camera_node|rplidar_node|ekf_node|async_slam' | wc -l)"
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 26
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 10
echo "== 검증 =="
echo -n "  /camera/scan: "; timeout 6 ros2 topic hz /camera/scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo -n "  /scan: "; timeout 6 ros2 topic hz /scan 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo -n "  /odometry/filtered: "; timeout 6 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo -n "  /wheel_odom(보드): "; timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | head -1; echo
echo -n "  depth_scan 로그 오류: "; grep -aiE "depth_scan|depthimage" /tmp/sensors.log | grep -aicE "error|exception|fail"; echo
grep -aiE "depth_scan|depthimage" /tmp/sensors.log | grep -aiE "error|warn|fail" | head -3
echo -n "  load: "; cut -d" " -f1-3 /proc/loadavg
