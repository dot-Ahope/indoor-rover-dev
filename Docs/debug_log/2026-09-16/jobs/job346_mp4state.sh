#!/bin/bash
source /opt/ros/humble/setup.bash
echo "=== 로버 자세/명령 ==="; timeout 10 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
printf "cmd_vel: "; timeout 4 ros2 topic hz /cmd_vel 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "없음(정지)"
echo "프로세스: controller $(pgrep -fc controller_server) planner $(pgrep -fc planner_server) bt $(pgrep -fc bt_navigator) slam $(pgrep -fc slam_toolbox) relay $(pgrep -fc depth_relay)"
echo "=== nav2.log goal 이후 ==="; bash /tmp/job328_navlog.sh 1789541740 2>/dev/null | grep -aE "Begin|Abort|Cancel|cancel|progress|Optimizer|collision|Received|Passing" | head -14 | cut -c1-170
echo "=== syslog 15:56~15:59 wpa/NM ==="; grep -aE "15:5[6-9]" /var/log/syslog | grep -aiE "wpa_supplicant|NetworkManager" | grep -aiE "deauth|disconnect|reason|AUTH|assoc|CTRL-EVENT" | head -8 | cut -c1-170
echo "=== bag 토픽 ==="; ros2 bag info /tmp/bag_mp4 2>/dev/null | grep -aE "trajectories|transformed_global_plan|Duration" | sed 's/ *| Type.*Count: / n=/; s/ *| Serial.*//' | cut -c1-80
