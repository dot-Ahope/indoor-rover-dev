#!/bin/bash
# 센서 통합 launch로 전환 + slam_toolbox 스모크 테스트 + foxglove
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
echo "===STOP individual sensor launches==="
for p in "camera.launch" "lidar.launch" "ekf.launch" "realsense2_camera_node" "rplidar_node" "ekf_node" "sensor_conditioner" "foxglove"; do pkill -f "$p" 2>/dev/null; done
sleep 3
echo "===START sensors.launch.py==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 35
ros2 node list
grep -aE "bias calibrated|not stationary" /tmp/sensors.log | tail -1 | cut -c60-200
grep -aiE "\] error|died|failed" /tmp/sensors.log | head -3 || echo "no errors"
echo "===rates==="
for t in /scan /camera/camera/imu /camera/camera/depth/image_rect_raw /odometry/filtered /wheel_odom; do printf "  %-40s %s\n" $t "$(timeout 6 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
echo "===START slam.launch.py (smoke)==="
pkill -f slam_toolbox 2>/dev/null; sleep 1
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 15
echo "-- /map:"; timeout 8 ros2 topic hz /map 2>&1 | grep -aE "average|does not" | tail -1
echo "-- map→odom TF:"; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation|RPY \(degree\)" | head -2
echo "-- map→lidar_link chain:"; timeout 6 ros2 run tf2_ros tf2_echo map lidar_link 2>&1 | grep -aE "Translation" | head -1
echo "-- map info:"; timeout 6 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE "resolution|width|height" | tr '\n' ' '; echo
echo "-- slam log:"; grep -aiE "error|warn|fail" /tmp/slam.log | head -4 || echo "clean"
echo "===foxglove==="; ss -ltnp 2>/dev/null | grep 8765 | head -1; hostname -I | awk '{print "ws://"$1":8765"}'
