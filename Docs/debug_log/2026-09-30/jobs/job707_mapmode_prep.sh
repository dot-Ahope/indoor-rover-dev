#!/bin/bash
# 09-30 §11: 매핑 전용 모드 prep(office_v1 불러오기, Nav2·nvblox 없음) → 복원 확인 → 조종 → 30 s 부하·EKF 미달 확인
set +u
MAPPING=1 SLAM_ARGS="map_file:=/home/jetson/maps/office/office_v1" SENSORS_ARGS="viz:=map" bash /tmp/job657_prep_f0b.sh 2>&1 | grep -aE "wheel_odom|gyro bias|odometry/filtered|slam 인자|map->odom|매핑 전용|stuck_monitor|배터리"
python3 /tmp/job697_restore_chk.py 2>&1 | grep -av "^\[" | grep -a "마지막\|/map"
bash /tmp/job685_f1_teleop.sh | grep -a "joy\|scale"
bash /tmp/job695_loadab.sh mapping_mode
