#!/bin/bash
# yaw=π 재적용 + 전체 스택 완전 재시작(base+sensors+foxglove) — stale TF 제거
source /opt/ros/humble/setup.bash
cp /tmp/rover_src/rover_description/urdf/rover.urdf ~/ros2_ws/src/rover_description/urdf/rover.urdf
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_description 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
echo "===전체 노드 종료==="
for p in "sensors.launch" "base.launch" "slam.launch" "description.launch" realsense2_camera_node rplidar_node ekf_node sensor_conditioner foxglove_bridge robot_state_publisher slam_toolbox; do pkill -f "$p" 2>/dev/null; done
docker rm -f microros_agent >/dev/null 2>&1; sleep 4
pgrep -af "robot_state_publisher|foxglove|ekf_node" | wc -l
echo "===base.launch 시작==="; setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 10; docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_DOWN
echo "===sensors.launch 시작==="; setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 35
echo "===검증==="
echo "RSP 개수: $(pgrep -f robot_state_publisher | wc -l), foxglove: $(pgrep -f foxglove_bridge | wc -l)"
echo "TF base_link→lidar_link:"; timeout 5 ros2 run tf2_ros tf2_echo base_link lidar_link 2>&1 | grep -aE "RPY \(degree\)" | head -1
for t in /wheel_odom /scan /camera/camera/imu /odometry/filtered; do printf "  %-24s %s\n" $t "$(timeout 5 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
echo "foxglove: ws://$(hostname -I | awk '{print $1}'):8765"
echo "DONE — Foxglove에서 로버모델(RobotModel)+TF축 켜고 base_link +x(빨강) 방향 = 로버 전방 기준으로 스캔 확인"
