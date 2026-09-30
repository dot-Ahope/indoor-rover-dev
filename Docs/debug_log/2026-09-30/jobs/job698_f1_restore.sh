#!/bin/bash
# 09-30 §4 F1-2: office_v1 불러와 prep(viz:=map) → 복원 확인
set +u
SLAM_ARGS="map_file:=/home/jetson/maps/office/office_v1" SENSORS_ARGS="viz:=map" bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|slam 인자|sensors 인자|map->odom|_server|배터리"
echo "== slam.log 불러오기"; grep -aiE "이어 그리기|deserializ|loading|posegraph|map_file|Failed|error" /tmp/slam.log | cut -c1-200 | head -8
python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\["
