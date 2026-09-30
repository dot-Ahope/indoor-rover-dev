#!/bin/bash
# 09-30 §10: office_v1 불러와 prep(viz:=map) → F1-2 재확인(테이프 재정렬) → 매핑 조종 기동
set +u
SLAM_ARGS="map_file:=/home/jetson/maps/office/office_v1" SENSORS_ARGS="viz:=map" bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|slam 인자|sensors 인자|map->odom|_server|배터리"
grep -a "Load From File" /tmp/slam.log | head -1 | cut -c1-120
python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\[" | grep -a "map \|마지막\|/map"
bash /tmp/job685_f1_teleop.sh
