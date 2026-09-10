#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/stuck_monitor.py
cp /tmp/stuck_monitor.py ~/ros2_ws/src/rover_bringup/scripts/
cp /tmp/stuck_monitor.py ~/ros2_ws/install/rover_bringup/lib/rover_bringup/
chmod +x ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py
python3 -m py_compile ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py && echo "  컴파일 OK"
echo "  배포: recovery_active $(grep -c recovery_active ~/ros2_ws/install/rover_bringup/lib/rover_bringup/stuck_monitor.py)곳"
for p in navigation.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor; do pkill -TERM -f "$p" 2>/dev/null; done
sleep 6
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
echo "  stuck_monitor: $(ros2 node list 2>/dev/null | grep -a stuck_monitor || echo 없음)"
echo "  구독 목록:"; timeout 8 ros2 node info /stuck_monitor 2>/dev/null | sed -n '/Subscribers/,/Publishers/p' | grep -a "_action/status\|cmd_vel\|scan" | sed 's/^/    /'
echo "  /backup/_action/status 구독자 수: $(timeout 6 ros2 topic info /backup/_action/status 2>/dev/null | grep -aoE 'Subscription count: [0-9]+')"
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"; done
