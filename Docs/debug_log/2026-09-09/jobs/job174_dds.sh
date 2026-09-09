#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
for f in fastdds_udp_only.xml base.launch.py sensors.launch.py slam.launch.py navigation.launch.py; do sed -i 's/\r$//' /tmp/$f; done
mkdir -p ~/ros2_ws/src/rover_bringup/config ~/ros2_ws/install/rover_bringup/share/rover_bringup/config
cp /tmp/fastdds_udp_only.xml ~/ros2_ws/src/rover_bringup/config/
cp /tmp/fastdds_udp_only.xml ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/
for f in base.launch.py sensors.launch.py slam.launch.py; do
  cp /tmp/$f ~/ros2_ws/src/rover_bringup/launch/; cp /tmp/$f ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/
done
cp /tmp/navigation.launch.py ~/ros2_ws/src/rover_navigation/launch/
cp /tmp/navigation.launch.py ~/ros2_ws/install/rover_navigation/share/rover_navigation/launch/
echo "배포 확인: XML $(ls ~/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml >/dev/null 2>&1 && echo OK || echo 없음), launch $(grep -lc FASTRTPS_DEFAULT_PROFILES_FILE ~/ros2_ws/install/*/share/*/launch/*.launch.py 2>/dev/null | wc -l)개"

echo "=== 전체 종료 (SIGTERM) + SHM 완전 정리 ==="
pkill -TERM -f "ros2 launch" 2>/dev/null
for p in navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense foxglove robot_state_publisher; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do
  [ "$(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server|robot_state_publisher' 2>/dev/null || echo 0)" = "0" ] && break; sleep 1
done
echo "  잔존: $(pgrep -fc 'ekf_node|slam_toolbox|realsense|rplidar|foxglove|sensor_conditioner|controller_server|robot_state_publisher' 2>/dev/null || echo 0)"
docker rm -f microros_agent >/dev/null 2>&1
ros2 daemon stop >/dev/null 2>&1; sleep 2
rm -f /dev/shm/fastrtps_* /dev/shm/sem.fastrtps_* 2>/dev/null
echo "  SHM 정리 후: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)개"
echo "=== 재기동 ==="
setsid nohup ros2 launch rover_bringup base.launch.py > /tmp/base.log 2>&1 &
sleep 12
setsid nohup ros2 launch rover_bringup sensors.launch.py > /tmp/sensors.log 2>&1 &
sleep 26
setsid nohup ros2 launch rover_bringup slam.launch.py > /tmp/slam.log 2>&1 &
sleep 12
setsid nohup ros2 launch rover_navigation navigation.launch.py > /tmp/nav2.log 2>&1 &
sleep 30
echo "=== 검증 ==="
echo "  SHM 재생성: $(ls /dev/shm 2>/dev/null | grep -c fastrtps)개  ← 0 이면 SHM 미사용(의도한 상태)"
echo "  SHM 오류: $(grep -ac 'RTPS_TRANSPORT_SHM' /tmp/sensors.log /tmp/slam.log /tmp/nav2.log 2>/dev/null | tr '\n' ' ')"
for t in /tf /odometry/filtered /map /scan /local_costmap/costmap /global_costmap/costmap; do
  printf "  %-26s " "$t"; timeout 9 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo 무발행
done
echo "  /tf 퍼블리셔: $(timeout 6 ros2 topic info /tf 2>/dev/null | grep -aoE 'Publisher count: [0-9]+')  (ekf+slam+RSP = 3 이 정상)"
echo "  노드: $(ros2 node list 2>/dev/null | grep -acE 'slam|ekf|camera|rplidar|controller|planner')개"
echo "  보드: $(ros2 node list 2>/dev/null | grep -a rover_jupiter || echo '없음 — RESET 필요')"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg)"
