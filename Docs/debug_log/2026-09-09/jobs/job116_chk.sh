#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "노드: $(ros2 node list 2>/dev/null | tr '\n' ' ')"
echo "토픽 수: $(ros2 topic list 2>/dev/null | wc -l)"
for t in /wheel_odom /rover/status /battery /imu/data_raw; do
  printf "  %-16s " "$t"
  r=$(timeout 8 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1)
  echo "${r:-무발행}"
done
echo "--- agent 세션 ---"
docker logs microros_agent 2>&1 | sed -E 's/\x1b\[[0-9;]*m//g' | grep -a "establish_session" | tail -2 | cut -c1-110
echo "--- 프로세스 ---"
echo "  ros 노드 프로세스: $(pgrep -fc 'ros2|robot_state_publisher|micro_ros' 2>/dev/null)"
