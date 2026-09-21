#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "프로세스: realsense $(pgrep -fc realsense2_camera) rplidar $(pgrep -fc rplidar) relay $(pgrep -fc depth_relay) ekf $(pgrep -fc ekf_node) slam $(pgrep -fc slam_toolbox) nvblox(컨테이너) $(pgrep -fc nvblox_node)"
for t in /scan /camera/camera/depth/color/points /camera/depth/points_filtered /camera/camera/depth/image_rect_raw; do printf "  %-42s %s\n" $t "$(timeout 7 ros2 topic hz $t 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1)"; done
echo "sensors.log 끝: $(tail -2 /tmp/sensors.log | cut -c1-120 | tr '\n' '|')"
echo "== 물리 상자(job478)"; python3 /tmp/job478_boxphys.py 10 2>&1 | grep -av '^\['
