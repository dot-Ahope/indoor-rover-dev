#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 라이다 방위별 (차체 외곽 기준) ==="
bash /tmp/job21c_where.sh 2>&1 | sed -n '3,16p' | sed 's/^/  /'
echo "=== 로컬 코스트맵 격자 + 차체 근처 센서 점 ==="
python3 /tmp/job230_map.py /local_costmap/costmap 2>&1 | sed -n '5,8p;18,32p;41,58p' | sed 's/^/  /'
echo "=== LETHAL 셀 센서 근거 (job248 B) ==="
python3 /tmp/job248_audit.py 2>&1 | sed -n '/########## B/,/########## C/p' | sed 's/^/  /'
