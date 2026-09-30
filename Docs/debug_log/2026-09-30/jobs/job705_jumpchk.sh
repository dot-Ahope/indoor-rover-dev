#!/bin/bash
# 09-30 §11: 이어 그리기 중 Foxglove 에서 로버가 멈췄다 점프 — 메모리·부하·TF 지연·SLAM/EKF 로그
set +u; source /opt/ros/humble/setup.bash; export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
echo "== 메모리"; free -m | head -3; grep -E "SwapTotal|SwapFree" /proc/meminfo | tr -s ' '
echo "== 메모리 상위(RSS MB)"; ps -eo rss,pcpu,comm --sort=-rss | head -9 | awk 'NR==1{print "  RSS_MB  %CPU  이름"; next} {printf "  %6.0f  %5.1f  %s\n", $1/1024, $2, $3}'
echo "== 부하 $(cut -d' ' -f1-3 /proc/loadavg)"
echo "== 로그 누계: EKF 주기 미달 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log) · SLAM 스캔 버림 $(grep -ac 'Message Filter dropping' /tmp/slam.log)"
grep -aiE "Message Filter dropping|queue|behind|timeout|Failed" /tmp/slam.log | tail -3 | cut -c1-200
e0=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); s0=$(grep -ac 'Message Filter dropping' /tmp/slam.log)
echo "== TF 지연(10 s): odom→base_link, map→odom"
timeout 12 ros2 run tf2_ros tf2_monitor odom base_link 2>&1 | grep -aE "Average Delay|Max Delay|Frequency" | tail -3
timeout 12 ros2 run tf2_ros tf2_monitor map odom 2>&1 | grep -aE "Average Delay|Max Delay|Frequency" | tail -3
e1=$(grep -ac 'Failed to meet update rate' /tmp/sensors.log); s1=$(grep -ac 'Message Filter dropping' /tmp/slam.log)
echo "== 이 24 s 동안: EKF 미달 +$((e1-e0)) · SLAM 버림 +$((s1-s0))"
echo "== 브리지 클라이언트 $(ss -tn state established '( sport = :8765 )' 2>/dev/null | tail -n +2 | wc -l)개, 설정 $(timeout 6 ros2 param get /foxglove_bridge topic_whitelist 2>&1 | tail -1 | cut -c1-120)"
