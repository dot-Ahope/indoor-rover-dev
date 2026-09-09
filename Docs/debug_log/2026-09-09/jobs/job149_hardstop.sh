#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 지령 주체 확인 ==="
ros2 topic info /cmd_vel 2>/dev/null | grep -a "Publisher count"
echo "=== 0 지령 반복 발행 ==="
for i in $(seq 1 20); do ros2 topic pub -1 /cmd_vel geometry_msgs/msg/Twist "{}" >/dev/null 2>&1; done
echo "=== 보드가 보고하는 실제 모터 상태 ==="
for i in 1 2 3; do
  timeout 5 ros2 topic echo /rover/status --once 2>/dev/null | grep -aE "message:|value: tgt" | sed 's/^/  /'
  sleep 1
done
echo "=== 휠 오도메트리 변화 (5초) ==="
timeout 5 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aE "^      x:|^      y:" | sed 's/^/  전: /'
sleep 5
timeout 5 ros2 topic echo /wheel_odom --once 2>/dev/null | grep -aE "^      x:|^      y:" | sed 's/^/  후: /'
