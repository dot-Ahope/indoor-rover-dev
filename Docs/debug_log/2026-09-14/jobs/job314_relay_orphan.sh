#!/bin/bash
# depth_relay 고아 정리: sensors.launch 를 죽였을 때 자식 릴레이가 살아남아(robot_state_publisher 와 같은 부류)
# 새 launch 의 릴레이와 함께 같은 토픽에 둘이 발행한다. 부모가 살아 있는 'ros2 launch' 가 아닌 릴레이를 종료한다.
source /opt/ros/humble/setup.bash
echo "--- 릴레이 프로세스 (pid ppid 시작시각 | 부모 명령) ---"
for PID in $(pgrep -f 'lib/rover_bringup/depth_relay.py'); do
  PP=$(ps -o ppid= -p $PID | tr -d ' '); ST=$(ps -o lstart= -p $PID)
  PCMD=$(ps -o args= -p $PP 2>/dev/null | sed -E 's/(.{0,60}).*/\1/')
  echo "  $PID $PP [$ST] | $PCMD"
  if ! echo "$PCMD" | grep -q 'ros2 launch'; then echo "    → 부모가 launch 아님(고아) → TERM"; kill -TERM $PID; fi
done
sleep 3
echo "남은 릴레이: $(pgrep -fc 'lib/rover_bringup/depth_relay.py')"
printf 'out hz '; timeout 8 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1
printf '발행자 '; timeout 8 ros2 topic info /camera/depth/points_filtered 2>/dev/null | grep -a 'Publisher count'
