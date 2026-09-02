#!/bin/bash
# 검증(자이로/scan/imu) + TF 진단(odom->base, map->odom 브로드캐스트율) + 조이스틱 기동.
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 자이로 캘리브 재확인 ==="
grep -a "gyro bias\|not stationary" /tmp/sensors.log | tail -1 || echo "  아직 로그 없음"
echo -n "/imu/data (conditioner 출력, 캘리브 후 발행): "; timeout 5 ros2 topic hz /imu/data 2>&1 | grep -aE "average rate" | head -1 || echo "무발행(캘리브 미완?)"
echo -n "/camera/camera/imu: "; timeout 5 ros2 topic hz /camera/camera/imu 2>&1 | grep -aE "average rate" | head -1 || echo "무발행"
echo -n "/scan: "; timeout 5 ros2 topic hz /scan 2>&1 | grep -aE "average rate" | head -1 || echo "무발행"
echo ""
echo "=== ★ TF 진단 (핵심) ==="
echo "--- /tf 전체 발행율 ---"; timeout 5 ros2 topic hz /tf 2>&1 | grep -aE "average rate" | head -1
echo "--- odom->base_link 브로드캐스트 (EKF, 30Hz 기대) ---"
timeout 9 ros2 run tf2_ros tf2_monitor odom base_link 2>/dev/null | grep -aE "Average rate|Average delay|Buffer" | head -4
echo "--- map->odom 브로드캐스트 (slam) ---"
timeout 9 ros2 run tf2_ros tf2_monitor map odom 2>/dev/null | grep -aE "Average rate|Average delay" | head -3
echo ""
echo "=== 조이스틱 기동 ==="
pkill -f joy_linux; pkill -f teleop_twist_joy; sleep 2
setsid nohup ros2 launch rover_bringup joy_teleop.launch.py > /tmp/joy.log 2>&1 &
sleep 6
echo "노드: $(ros2 node list 2>/dev/null | grep -E 'joy|teleop' | tr '\n' ' ')"
echo "완료"
