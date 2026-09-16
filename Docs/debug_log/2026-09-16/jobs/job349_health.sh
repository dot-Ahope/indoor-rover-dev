#!/bin/bash
source /opt/ros/humble/setup.bash
echo "=== 노드 ==="; timeout 12 ros2 node list 2>/dev/null | tr '\n' ' ' | cut -c1-400; echo
for n in controller_server planner_server bt_navigator smoother_server; do printf "  %-18s " $n; timeout 8 ros2 lifecycle get /$n 2>&1 | tail -1; done
echo "=== TF ==="; printf "  odom->base: "; timeout 8 ros2 run tf2_ros tf2_echo odom base_link 2>&1 | grep -a Translation | head -1; printf "  map->odom: "; timeout 8 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -a Translation | head -1
echo "=== 토픽 hz ==="; for t in /odometry/filtered /scan /wheel_odom; do printf "  %-20s " $t; timeout 6 ros2 topic hz $t 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행; done
echo "=== nav2.log 마지막 오류/경고 ==="; grep -aE "ERROR|WARN" /tmp/nav2.log | tail -8 | cut -c1-180
echo "=== slam.log 끝 ==="; tail -3 /tmp/slam.log | cut -c1-160
echo "=== 프로세스 ==="; for p in slam_toolbox ekf_node realsense rplidar depth_relay controller_server planner_server bt_navigator lifecycle_manager; do printf "%s:%s " $p $(pgrep -fc $p); done; echo; echo "load $(cut -d' ' -f1-3 /proc/loadavg)"
