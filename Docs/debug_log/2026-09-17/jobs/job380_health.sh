#!/bin/bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash
echo "now $(date +%T.%N | cut -c1-12)  epoch $(date +%s.%N | cut -c1-14)"
echo "=== 프로세스 ==="; for p in micro_ros_agent robot_state_publisher sensor_conditioner ekf_node slam_toolbox depth_relay realsense2_camera rplidar controller_server planner_server bt_navigator ros2\ bag; do printf "%s:%s " "$p" "$(pgrep -fc "$p")"; done; echo
echo "=== 토픽 hz ==="; for t in /wheel_odom /imu/data /odometry/filtered /scan /camera/depth/points_filtered /tf; do printf "  %-34s " $t; timeout 6 ros2 topic hz $t 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo; done
echo "=== TF 지연 ==="; for pair in "odom base_link" "map odom"; do printf "  %-16s " "$pair"; timeout 6 ros2 run tf2_ros tf2_echo $pair 2>&1 | grep -aE "At time|Translation" | head -2 | tr '\n' ' '; echo; done
printf "  /odometry/filtered stamp: "; timeout 5 ros2 topic echo /odometry/filtered --once 2>/dev/null | grep -aE "^  stamp:" -A2 | grep -aoE "[0-9]+" | head -2 | tr '\n' '.'; echo
printf "  /scan stamp: "; timeout 5 ros2 topic echo /scan --once 2>/dev/null | grep -aE "sec:" | head -2 | grep -aoE "[0-9]+" | tr '\n' '.'; echo
echo "=== CPU top ==="; top -bn1 | head -16 | tail -10 | awk '{printf "%s %s | ", $9, $12}'; echo; echo "load $(cut -d' ' -f1-3 /proc/loadavg)  temp $(cat /sys/class/thermal/thermal_zone*/temp 2>/dev/null | sort -n | tail -1)"
echo "=== ekf/slam 로그 끝 ==="; grep -aE "WARN|ERROR" /tmp/sensors.log | tail -3 | cut -c1-170; tail -2 /tmp/slam.log | cut -c1-170
echo "=== syslog Wi-Fi 11:0x ==="; grep -aE "^Sep 17 11:0" /var/log/syslog | grep -aiE "CTRL-EVENT-DISCONNECTED|AUTH|deauth" | tail -3 | cut -c1-140; echo "ip $(ip -4 -o addr show wlP1p1s0 | awk '{print $4}')"
