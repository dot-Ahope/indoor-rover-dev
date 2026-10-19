#!/bin/bash
# 10-19 §19: f2y1 결과 — 러너 로그 요약, IR bag 토픽 수, 부하 지표(읽기만)
L=/tmp/f0_f2y1.log
grep -aE "통과|불합격|SUCCEEDED|ABORTED|결과:|놓침|missed|EKF|IR " $L | cut -c1-200 | head -30
echo "== IR bag"; ros2 bag info /home/jetson/bags/bag_f2y1_ir 2>/dev/null | grep -aE "Duration|Bag size|Count" | sed 's/Serialization Format: cdr//' | cut -c1-140
echo "== 깊이 bag"; ros2 bag info /home/jetson/bags/bag_f2y1 2>/dev/null | grep -aE "Duration|Bag size|depth|slice" | sed 's/Serialization Format: cdr//' | cut -c1-140
echo "== 주행 중 EKF 위반 · slam 폐기 · 제어 놓침(로그 누계)"; echo "  sensors EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log) · slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log) · controller 'Control loop missed' $(grep -ac 'Control loop missed' /tmp/nav2.log)"
grep -a "10 s:" /tmp/sensors.log | tail -20 | grep -aoE "IR1\(끔\) 입력 [0-9]+|기록 [0-9]+|교대깨짐 [0-9]+" | paste -sd' ' | cut -c1-600
