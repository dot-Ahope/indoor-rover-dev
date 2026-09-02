#!/bin/bash
# 슬립 계수 0.46 배포 → 컨디셔너/EKF 재시작 → 정적 확인 + conditioned vs gyro 정합 스팟체크
source /opt/ros/humble/setup.bash
cp /tmp/rover_src/rover_bringup/scripts/sensor_conditioner.py ~/ros2_ws/src/rover_bringup/scripts/
chmod +x ~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_bringup 2>&1 | tail -1
source ~/ros2_ws/install/setup.bash
grep SLIP_PTS ~/ros2_ws/install/rover_bringup/lib/rover_bringup/sensor_conditioner.py
pkill -f "sensors.launch" 2>/dev/null; pkill -f ekf_node 2>/dev/null; pkill -f sensor_conditioner 2>/dev/null; sleep 2
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 35
grep -aE "bias calibrated|not stationary" /tmp/sensors.log | tail -1 | cut -c60-200
echo "-- rates:"; for t in /odometry/filtered /wheel_odom/conditioned /imu/data; do printf "  %-26s %s\n" $t "$(timeout 5 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
echo "-- static filtered yaw (30s drift):"
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -aE "^[zw]"
sleep 30
timeout 5 ros2 topic echo /odometry/filtered --once --field pose.pose.orientation 2>/dev/null | grep -aE "^[zw]"
