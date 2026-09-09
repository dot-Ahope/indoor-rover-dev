#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
sed -i 's/\r$//' /tmp/nav2_params.yaml
cp /tmp/nav2_params.yaml ~/ros2_ws/src/rover_navigation/config/
cp /tmp/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/
echo "배포: stvl_layer $(grep -c 'stvl_layer:' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml)곳"
echo "=== 스택 기동 (base → sensors → slam) ==="
for p in "ros2 launch" navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove robot_state_publisher; do pkill -TERM -f "$p" 2>/dev/null; done
sleep 8
docker rm -f microros_agent >/dev/null 2>&1
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 12
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 26
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
echo "=== Nav2 기동 (STVL 로드 확인) ==="
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
for nd in /controller_server /planner_server /bt_navigator /behavior_server; do
  printf "  %-20s " "$nd"; timeout 6 ros2 lifecycle get "$nd" 2>/dev/null || echo "?"
done
echo "  로컬 레이어: $(timeout 8 ros2 param get /local_costmap/local_costmap plugins 2>/dev/null | sed 's/^.*is: //')"
echo "  전역 레이어: $(timeout 8 ros2 param get /global_costmap/global_costmap plugins 2>/dev/null | sed 's/^.*is: //')"
for t in /local_costmap/costmap /global_costmap/costmap; do printf "  %-26s " "$t"; timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행; done
echo "  STVL 오류: $(grep -aiE 'stvl|spatio|openvdb' /tmp/nav2.log | grep -aiE 'error|fail|exception' | tail -3 | cut -c1-140 | tr '\n' ' ')"
echo "  nav2 오류: $(grep -aiE 'error|died|exception' /tmp/nav2.log | tail -3 | cut -c1-140 | tr '\n' ' ')"
echo "  foxglove CPU: $(ps -p $(pgrep -f foxglove_bridge | head -1) -o %cpu= 2>/dev/null | tr -d ' ')%   load: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  보드: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음 — RESET 필요')"
