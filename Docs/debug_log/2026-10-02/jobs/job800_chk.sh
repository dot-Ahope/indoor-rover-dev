#!/bin/bash
# 10-02 §1: 지도 보완 전 확인 — bag 유무·시작 시각·토픽, 지도 파일, 가동 상태
source /opt/ros/humble/setup.bash
echo "== uptime $(uptime -p) | load $(cut -d' ' -f1-3 /proc/loadavg)"
ls -la /tmp/bag_f2a12 ~/bags 2>&1 | head -20
ros2 bag info /tmp/bag_f2a12 2>/dev/null | grep -aE "Duration|Start|End|Topic:" | cut -c1-150
ls -la ~/maps/office/ | head -30
echo "== 라이브: slam $(pgrep -fc localization_slam) nav2 $(pgrep -fc controller_server) agent $(pgrep -fc micro_ros_agent) rplidar $(pgrep -fc rplidar)"
df -h /home | tail -1
