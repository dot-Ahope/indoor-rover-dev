#!/bin/bash
# 10-06 §9 T1: bag 기록 + 정지 관찰 60 s(사람이 움직임) + 게이트 판정 변화
G0=$(grep -a "게이트 통과" /tmp/sensors.log | tail -1 | grep -oE "통과 [0-9]+ · G1 거부 [0-9]+ · G2 거부 [0-9]+")
rm -rf /tmp/bag_t1; setsid nohup ros2 bag record -o /tmp/bag_t1 /scan /tf /tf_static /imu/data /wheel_odom /odom_rf2o /odom_rf2o/gated /odometry/filtered /odometry/ekf_a > /dev/null 2>&1 < /dev/null & BP=$!
sleep 3; python3 -u /tmp/t1_still.py 60 2>&1 | grep -av "^\["
sleep 31; G1=$(grep -a "게이트 통과" /tmp/sensors.log | tail -1 | grep -oE "통과 [0-9]+ · G1 거부 [0-9]+ · G2 거부 [0-9]+")
echo "  게이트 누계 전: $G0 → 후: $G1"
kill -INT $BP; sleep 3; cd /tmp && tar -czf bag_t1.tgz bag_t1 && ls -la /tmp/bag_t1.tgz
