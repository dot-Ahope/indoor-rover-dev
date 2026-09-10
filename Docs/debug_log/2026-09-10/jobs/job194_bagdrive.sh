#!/bin/bash
# 주행 + rosbag 기록 (2026-09-10).
#   사용자 요청: 플래너의 실시간 경로와, 장애물이 카메라 화각을 벗어났을 때 코스트맵이
#   어떻게 변하는지를 **사후에** 본다. 실시간 Foxglove 연결은 CPU 를 1코어 가까이 먹어
#   EKF 를 굶기고 주행 자체를 망가뜨린다(09-10 §4). 파일로 남겨 나중에 연다.
#
#   기록 토픽은 시각화에 필요한 최소 집합. 코스트맵은 1.7/0.7Hz, /plan 은 1Hz 라 가볍다.
#   포인트클라우드·영상은 제외한다(용량·CPU).
#   사용: bash job194_bagdrive.sh <거리> <타임아웃> <이름>
# ⚠ set -u 금지 — ROS 의 setup.bash 가 미정의 변수를 참조해 즉시 죽는다
#   (AMENT_TRACE_SETUP_FILES: unbound variable)
D=${1:-1.60}; TMO=${2:-90}; NAME=${3:-job194}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

TOPICS="/tf /tf_static /map /scan /plan /local_plan \
/local_costmap/costmap /global_costmap/costmap \
/odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck"

BAG=/tmp/bag_$NAME
rm -rf $BAG
echo "=== rosbag 기록 시작 → $BAG ==="
setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &
sleep 4
echo "  기록 프로세스: $(pgrep -fc 'ros2 bag record')"

echo "=== 주행 ==="
python3 /tmp/job125_avoid3.py $D $TMO $NAME 2>&1 | tail -45
RC=$?

sleep 2
echo "=== rosbag 종료 ==="
pkill -INT -f "ros2 bag record" 2>/dev/null
for i in $(seq 1 10); do [ "$(pgrep -fc 'ros2 bag record' 2>/dev/null | head -1)" = "0" ] && break; sleep 1; done
sync
echo "  크기: $(du -sh $BAG 2>/dev/null | cut -f1)"
echo "  파일: $(ls $BAG 2>/dev/null | tr '\n' ' ')"
ros2 bag info $BAG 2>/dev/null | grep -aE "Duration|Messages|Topic information" | head -3 | sed 's/^/  /'
echo ""
echo "  ※ 사후 검토: 이 폴더를 PC 로 내려받아 Foxglove Studio 에서 'Open local file' 로 연다."
exit $RC
