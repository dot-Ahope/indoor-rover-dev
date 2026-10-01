#!/bin/bash
# 10-01 §8.1 F2 첫 주행 prep: office_v2 + slam_toolbox 위치 추정 모드(LOC=slamloc), 전체 스택 → 시작 자세 확인(L-d)
set +u
LOC=slamloc MAP=office_v2 MAPPING=0 bash /tmp/job726_prep_map.sh 2>&1 | grep -aE "지도|wheel_odom|gyro bias|odometry/filtered|slam 인자|위치 추정|map->odom|_server|배터리|EKF 위반|프로세스|  [a-z_\" ]+ +[0-9]+$"
python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\[" | grep -aE "/map|^ +[1-9]\.0 s|^ +1[0-6]\.0 s|마지막"
echo "  배터리: $(timeout 5 ros2 topic echo --once /battery 2>/dev/null | grep -aE '^voltage' )"
