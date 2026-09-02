#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===세션 재수립 확인==="
echo -n "  wheel_odom: "; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aE "average|does not" | tail -1
echo -n "  battery: "; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo NONE
echo -n "  imu_data_raw: "; timeout 5 ros2 topic hz /imu/data_raw 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1
echo "===odom 리셋 확인 (0 근처여야)==="; timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.position 2>/dev/null | grep -E "x:|y:" | head -2
echo "===slam 재시작(맵 초기화)==="
pkill -f slam_toolbox 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
ros2 node list | grep -q slam_toolbox && echo "  slam OK" || echo "  NO_SLAM"
echo -n "  map→odom TF: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo "===센서 파이프라인 확인==="
for t in /scan /scan_raw /odometry/filtered /camera/camera/imu; do printf "  %-22s %s\n" $t "$(timeout 4 ros2 topic hz $t 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)"; done
echo -n "  scan_deskew: "; ros2 node list | grep -q scan_deskew && echo "OK" || echo "없음"
