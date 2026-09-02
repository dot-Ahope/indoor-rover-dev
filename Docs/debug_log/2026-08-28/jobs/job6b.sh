#!/bin/bash
# 재부팅 여부 확인 + 스택 전체 재시작 (base → sensors), 세션 검증
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "===UPTIME==="; uptime; uptime -s
echo "===DEVICES==="; ls -l /dev/rover /dev/rplidar 2>&1; lsusb | grep -iE "8086|10c4|1a86" | sed 's/^/  /'
echo "===HID MODULES (재부팅 시 유지 확인)==="; lsmod | grep -c hid_sensor; ls /sys/bus/iio/devices/ 2>/dev/null | tr '\n' ' '; echo
echo "===RUNNING NODES==="; ros2 node list 2>/dev/null | tr '\n' ' '; echo
echo "===STOP any stale==="; for p in "sensors.launch" "base.launch" "slam.launch" realsense2_camera_node rplidar_node ekf_node sensor_conditioner foxglove_bridge robot_state_publisher; do pkill -f "$p" 2>/dev/null; done; docker rm -f microros_agent >/dev/null 2>&1; sleep 3
echo "===START base.launch==="; setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/bringup.log 2>&1 &
sleep 10
docker ps --format '{{.Names}} {{.Status}}' | grep microros_agent || echo AGENT_DOWN
echo "===START sensors.launch==="; setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 35
grep -aE "bias calibrated|not stationary" /tmp/sensors.log | tail -1 | cut -c60-200
echo "===nodes==="; ros2 node list | tr '\n' ' '; echo
echo "===rates==="; for t in /wheel_odom /scan /camera/camera/imu /odometry/filtered; do printf "  %-24s %s\n" $t "$(timeout 5 ros2 topic hz $t 2>&1 | grep -aE 'average|does not' | tail -1)"; done
echo "===wheel_odom 세션 확인==="; timeout 5 ros2 topic echo /battery --once --field voltage 2>/dev/null || echo "no board session — 보드 RESET 필요할 수 있음"
