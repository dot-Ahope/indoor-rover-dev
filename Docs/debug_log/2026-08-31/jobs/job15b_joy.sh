#!/bin/bash
# 조이스틱 teleop 기동 + 검증. 모션은 스틱 움직일 때만 발생.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 조이스틱 장치 ==="
ls -l /dev/input/js0 2>/dev/null || echo "js0 없음! USB 재연결 필요"
echo "=== 기존 joy/teleop 정리 ==="
pkill -f joy_linux; pkill -f teleop_twist_joy; pkill -f joy_teleop; sleep 2
echo "=== joy_teleop 기동 ==="
setsid nohup ros2 launch rover_bringup joy_teleop.launch.py > /tmp/joy.log 2>&1 &
sleep 6
echo "노드: $(ros2 node list 2>/dev/null | grep -E 'joy|teleop' | tr '\n' ' ')"
echo -n "/odometry/filtered: "; timeout 4 ros2 topic hz /odometry/filtered 2>&1 | grep -aE "average rate" | head -1
echo "=== /joy 현재값 (스틱 중립 확인) ==="
timeout 4 ros2 topic echo /joy --once 2>/dev/null | grep -aA2 "axes" | head -6 || echo "  (joy 무발행 — 스틱 한번 살짝 움직이면 나옴)"
echo -n "=== /cmd_vel (중립이면 0 또는 무발행): "; timeout 3 ros2 topic echo /cmd_vel --once 2>/dev/null | grep -aE "x:|z:" | head -3 || echo "무발행(정상)"
echo "map->odom: $(timeout 4 ros2 run tf2_ros tf2_echo map odom 2>/dev/null | grep -aE 'Translation' | head -1)"
