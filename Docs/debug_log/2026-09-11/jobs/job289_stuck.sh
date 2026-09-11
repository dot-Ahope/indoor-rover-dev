#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 자세 ==="
echo -n "  map: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo -n "  map->odom: "; timeout 6 ros2 run tf2_ros tf2_echo map odom 2>&1 | grep -aE "Translation" | head -1
echo "=== 상자 (로버 기준, 지금 헤딩 178°) ==="
python3 /tmp/job248_audit.py 2>&1 | grep -aE "^상자:|^   \[|로컬\[|전역\[" | sed 's/^/  /'
echo "=== 라이다 방위별 ==="
bash /tmp/job21c_where.sh 2>&1 | sed -n '3,16p' | sed 's/^/  /'
echo "=== RPP 기준(100) 제자리/전진/회전 (프레임 정정된 도구) ==="
python3 /tmp/job228_why.py 2>&1 | sed -n '4,6p;9,18p;28,37p' | sed 's/^/  /'
echo "=== 로컬 격자 (odom 프레임, 차체 좌표) ==="
python3 /tmp/job230_map.py /local_costmap/costmap 2>&1 | sed -n '7,30p' | sed 's/^/  /'
echo "=== 복귀 중 충돌 감지 시각·복구 순서 ==="
grep -aE "detected collision|Running backup|backup completed|Running wait|Goal failed" /tmp/ret.log | grep -ao '\[1789[0-9.]*\].*' | sed 's/\[controller_server\]: RegulatedPurePursuitController //; s/\[behavior_server\]: //' | cut -c1-70 | awk 'NR==1{split($1,a,"[][]"); c0=a[2]} {split($1,a,"[][]"); printf "  +%5.1fs %s\n", a[2]-c0, substr($0, index($0,$2))}'
