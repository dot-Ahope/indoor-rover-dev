#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 자세 / SLAM 보정 ==="
timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo -n "  map->odom: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo "=== RPP 충돌 판정 (100 기준) — 제자리 / 전진 / 회전 ==="
python3 /tmp/job228_why.py 2>&1 | sed -n '4,20p;27,36p;38,48p' | sed 's/^/  /'
echo "=== 로컬 코스트맵 격자 (차체 좌표) ==="
python3 /tmp/job230_map.py /local_costmap/costmap 2>&1 | sed -n '5,40p' | sed 's/^/  /'
echo "=== 복귀 중 마지막 충돌·복구 순서 ==="
grep -aE "detected collision|Running backup|backup completed|backup failed|Running wait|Goal failed|Aborting" /tmp/ret.log | tail -12 | grep -ao '\[[0-9.]*\].*' | cut -c1-90 | sed 's/^/  /'
