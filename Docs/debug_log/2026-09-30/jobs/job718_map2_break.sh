#!/bin/bash
# 09-30 §16: 두 번째 매핑도 지도 깨짐(사용자) — 지도 저장 안 함. bag 을 닫고(SIGINT) 사후 분석.
set +u
echo "== bag 닫기"; pkill -INT -f "ros2 bag record"; sleep 4; B=$(ls -d /tmp/bags/map_* | tail -1); echo "  $B"; ros2 bag info $B 2>/dev/null | grep -aE "Duration|Start|End|Count|/scan|/tf |/odometry|/imu|/cmd_vel"
echo "== SLAM 최적화(Ceres) 흔적:"; grep -a 'preprocessor.cc' /tmp/slam.log | grep -aoE '[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{3}'
echo "  slam 버림 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | EKF 미달 $(grep -ac 'Failed to meet' /tmp/sensors.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "  slam 경고/오류:"; grep -aiE "warn|error" /tmp/slam.log | grep -av "Message Filter" | tail -10
echo "== stuck(관찰) 발동:"; grep -a STUCK /tmp/nav2.log | tail -10
python3 /tmp/job718_ana.py $B
