#!/bin/bash
# 10-06 §9.2 T1b: 정지 + 사용자가 몸으로 라이다 시야 약 70 % 를 가림 — 백그라운드로 90 s 기록·관찰(시작 알림 뒤 사용자가 가림)
cat > /tmp/t1b_run.sh <<'X'
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
G0=$(grep -a "게이트 통과" /tmp/sensors.log | tail -1 | grep -oE "통과 [0-9]+ · G1 거부 [0-9]+ · G2 거부 [0-9]+")
rm -rf /tmp/bag_t1b; ros2 bag record -o /tmp/bag_t1b /scan /tf /tf_static /imu/data /wheel_odom /odom_rf2o /odom_rf2o/gated /odometry/filtered /odometry/ekf_a > /dev/null 2>&1 & BP=$!
sleep 2; echo "기록 시작 $(date +%T)"; python3 -u /tmp/t1_still.py 90 2>&1 | grep -av "^\["
sleep 31; G1=$(grep -a "게이트 통과" /tmp/sensors.log | tail -1 | grep -oE "통과 [0-9]+ · G1 거부 [0-9]+ · G2 거부 [0-9]+")
echo "  게이트 누계 전: $G0 → 후: $G1"; kill -INT $BP; sleep 3; cd /tmp && tar -czf bag_t1b.tgz bag_t1b; echo "=== 끝 $(date +%T)"
X
setsid nohup bash /tmp/t1b_run.sh > /tmp/t1b.txt 2>&1 < /dev/null &
sleep 6; cat /tmp/t1b.txt
