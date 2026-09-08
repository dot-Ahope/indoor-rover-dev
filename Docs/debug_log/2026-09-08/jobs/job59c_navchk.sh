#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo -n "local obstacle sources: "; timeout 10 ros2 param get /local_costmap/local_costmap obstacle_layer.observation_sources 2>/dev/null | tail -1
echo -n "global obstacle sources: "; timeout 10 ros2 param get /global_costmap/global_costmap obstacle_layer.observation_sources 2>/dev/null | tail -1
echo -n "/camera/scan 구독자: "; timeout 8 ros2 topic info /camera/scan 2>/dev/null | grep -aoE "Subscription count: [0-9]+"
echo -n "costmap 로그 depth_scan: "; grep -ac "depth_scan" /tmp/nav2.log
grep -aiE "depth_scan|camera/scan" /tmp/nav2.log | grep -aiE "error|warn" | head -3
echo -n "stuck_monitor: "; grep -a "stuck_monitor 시작" /tmp/nav2.log | tail -1 | sed "s/.*(//"
echo "== CPU (2초 평균) =="; top -bn3 -d1 | awk '/^top/{i++} i==3 && /python3|realsen|depthimag|async_s|rplidar|ekf_node|controller|planner/ {printf "%5s%% %s\n",$9,$12}' | head -10
echo -n "stuck_monitor CPU: "; ps -eo pcpu,args | grep "[s]tuck_monitor.py" | awk '{print $1"%"}'
echo -n "load: "; cut -d" " -f1-3 /proc/loadavg
echo -n "배터리: "; timeout 5 ros2 topic echo --once /battery 2>/dev/null | grep -E "^voltage"
