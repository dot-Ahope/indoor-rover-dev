#!/bin/bash
# depth_relay 중복 정리: job240 이 sensors(camera.launch)를 재기동하면 launch 가 릴레이를 띄우는데,
# 오전에 standalone(ros2 run, -p min_range:=)으로 띄운 것이 setsid 라 살아남아 같은 토픽에 둘이 발행한다.
source /opt/ros/humble/setup.bash
echo "--- depth_relay 프로세스 (pid, 인자 일부) ---"
ps -eo pid,args | grep -a 'depth_relay.py' | grep -av grep | sed -E 's/(.{0,110}).*/\1/'
N=$(ps -eo args | grep -a 'depth_relay.py' | grep -av grep | grep -ac python3)
echo "python3 릴레이 수: $N"
if [ "$N" -gt 1 ]; then
  for PID in $(ps -eo pid,args | grep -a 'depth_relay.py' | grep -a 'min_range:=' | grep -av grep | awk '{print $1}'); do
    echo "standalone 릴레이 PID $PID 종료(TERM)"; kill -TERM $PID; done
  sleep 3
  ps -eo pid,args | grep -a 'depth_relay.py' | grep -av grep | grep -ac python3 | sed 's/^/남은 python3 릴레이 수: /'
fi
printf 'out hz '; timeout 8 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -aoE 'average rate: [0-9.]+' | head -1
printf '발행자 '; timeout 8 ros2 topic info /camera/depth/points_filtered 2>/dev/null | grep -a 'Publisher count'
