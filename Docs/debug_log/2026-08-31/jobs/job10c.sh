#!/bin/bash
# 깨끗한 odom: EKF 재시작(odom→0, 자이로 캘리브 10s, 로버 정지 유지) → slam 재시작
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "★ 로버를 15초간 가만히 두세요 (자이로 캘리브레이션)"
pkill -f "ekf.launch" 2>/dev/null; pkill -f ekf_node 2>/dev/null; pkill -f sensor_conditioner 2>/dev/null; pkill -f slam_toolbox 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup ekf.launch.py > /tmp/ekf.log 2>&1 &
sleep 16
grep -aE "bias calibrated|not stationary" /tmp/ekf.log | tail -1 | cut -c55-160
echo -n "  odom 위치(0 근처여야): "; timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.position 2>/dev/null | grep -E "x:|y:" | tr '\n' ' '; echo
echo "===slam 재시작(맵 초기화)==="
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
ros2 node list | grep -q slam_toolbox && echo "  slam OK" || echo "  NO_SLAM"
echo -n "  map→odom TF: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo "===전체 노드 확인==="; ros2 node list | grep -E "rover_jupiter|ekf|slam|scan_deskew|rplidar|camera|robot_state|sensor_cond" | tr '\n' ' '; echo
echo -n "  /odometry/filtered: "; timeout 5 ros2 topic hz /odometry/filtered 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
