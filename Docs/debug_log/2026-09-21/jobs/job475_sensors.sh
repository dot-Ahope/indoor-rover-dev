#!/bin/bash
# N0 용 호스트 스택: 센서(카메라·라이다·컨디셔너·EKF·릴레이) + SLAM 만 (Nav2 없음). job240 과 같은 기동 명령.
set +u
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for p in sensors.launch slam.launch navigation.launch depth_relay.py realsense2_camera rplidar sensor_conditioner ekf_node scan_deskew slam_toolbox; do pkill -TERM -f "$p" 2>/dev/null; done; sleep 4
: > /tmp/sensors.log; : > /tmp/slam.log
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 28
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 15
echo "센서: realsense $(pgrep -fc realsense2_camera) rplidar $(pgrep -fc rplidar) ekf $(pgrep -fc ekf_node) relay $(pgrep -fc depth_relay) slam $(pgrep -fc slam_toolbox) | 에이전트 $(docker ps --format '{{.Names}}' | grep -c microros_agent)"
echo "깊이 이미지 hz: $(timeout 8 ros2 topic hz /camera/camera/depth/image_rect_raw 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1) | camera_info: $(timeout 6 ros2 topic echo /camera/camera/depth/camera_info --once --field header.frame_id 2>/dev/null | head -1) | 인코딩: $(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field encoding 2>/dev/null | head -1) $(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field width 2>/dev/null | head -1)x$(timeout 6 ros2 topic echo /camera/camera/depth/image_rect_raw --once --field height 2>/dev/null | head -1)"
echo "TF odom→base_link: $(timeout 6 ros2 run tf2_ros tf2_echo odom base_link 2>&1 | grep -a Translation | head -1) | odom→camera_depth_optical_frame: $(timeout 6 ros2 run tf2_ros tf2_echo odom camera_depth_optical_frame 2>&1 | grep -a Translation | head -1)"
echo "load $(cut -d' ' -f1-3 /proc/loadavg) | EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)"
