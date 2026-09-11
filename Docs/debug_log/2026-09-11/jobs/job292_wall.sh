#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 현재 자세 / 전방 벽 ==="
timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
bash /tmp/job21c_where.sh 2>&1 | grep -aE "정면|좌30|우30" | sed 's/^/  /'
echo "=== 전역 코스트맵: 전방 단면별 RPP 기준 폭 (2.2 m 까지) — 목표를 어디까지 둘 수 있나 ==="
python3 /tmp/job248_audit.py 2>&1 | sed -n '/########## C/,$p' | grep -aE "^   [12]\.[0-9]0 |최소폭" | awk '{print "  "$1"  RPP기준: "$4" "$5}'
