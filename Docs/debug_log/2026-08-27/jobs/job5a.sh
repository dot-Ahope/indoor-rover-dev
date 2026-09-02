#!/bin/bash
# W3: 확정 URDF 반영 → colcon → base.launch 재시작(agent 포함) → sensors.launch 재시작(컨디셔너 1.0)
source /opt/ros/humble/setup.bash
cp -r /tmp/rover_src/rover_description /tmp/rover_src/rover_bringup ~/ros2_ws/src/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws && colcon build --symlink-install 2>&1 | tail -2
source ~/ros2_ws/install/setup.bash
python3 -c "import xml.dom.minidom as m; d=m.parse('$HOME/ros2_ws/install/rover_description/share/rover_description/urdf/rover.urdf'); print('URDF valid, links:', len(d.getElementsByTagName('link')))"
echo "===STOP slam / sensors / base==="
for p in slam_toolbox "slam.launch" "sensors.launch" realsense2_camera_node rplidar_node ekf_node sensor_conditioner foxglove_bridge "base.launch" robot_state_publisher; do pkill -f "$p" 2>/dev/null; done
docker rm -f microros_agent >/dev/null 2>&1; sleep 3
echo "===START base.launch (agent + RSP with WT-600 URDF)==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 10
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_CONTAINER_DOWN
grep -a "got segment" /tmp/bringup.log | sed 's/.*got segment //' | tr '\n' ' '; echo
echo "===START sensors.launch==="
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 35
grep -aE "bias calibrated|not stationary" /tmp/sensors.log | tail -1 | cut -c60-200
echo "===TF tree (static, base_link 기준)==="
for f in sensor_deck_link lidar_link camera_link camera_imu_optical_frame imu_link left_track; do printf "  %-26s " $f; timeout 5 ros2 run tf2_ros tf2_echo base_link $f 2>&1 | grep -aE "Translation" | head -1; done
echo "===nodes==="; ros2 node list | tr '\n' ' '; echo
echo "===rates (wheel_odom은 보드 RESET 전엔 없음)==="
for t in /wheel_odom /scan /camera/camera/imu /odometry/filtered; do printf "  %-24s %s\n" $t "$(timeout 5 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
