#!/bin/bash
# 컨디셔너 V1 래퍼(Jetson, 2026-09-28 §11). 모드:
#   rec SEC      — 라이브(도메인 0)에서 원시 입력 /camera/camera/imu, /wheel_odom 을 SEC 초 녹화 → /tmp/bag_condraw (로버는 움직이지 않음)
#   ab  BAG      — 도메인 42 에서 Python 판·C++ 판을 출력 remap(/py, /cpp) 해 띄우고 job594 로 재생·비교
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
if [ "$1" = rec ]; then
  rm -rf /tmp/bag_condraw
  timeout $(( $2 + 5 )) ros2 bag record -o /tmp/bag_condraw /camera/camera/imu /wheel_odom > /tmp/bag_condraw.log 2>&1 &
  sleep $(( $2 + 7 )); ros2 bag info /tmp/bag_condraw 2>/dev/null | grep -aE "Duration|Topic:" | sed -E 's/\| Serialization.*//'
  exit 0
fi
export ROS_DOMAIN_ID=42
pkill -9 -f "cond_ab_(py|cpp)" 2>/dev/null; sleep 1
R="-r /imu/data_raw:=/camera/camera/imu"
setsid ros2 run rover_bringup sensor_conditioner.py --ros-args -r __node:=cond_ab_py $R -r /imu/data:=/py/imu/data -r /wheel_odom/conditioned:=/py/wheel_odom/conditioned > /tmp/cond_ab_py.log 2>&1 &
setsid ros2 run rover_bringup sensor_conditioner_node --ros-args -r __node:=cond_ab_cpp $R -r /imu/data:=/cpp/imu/data -r /wheel_odom/conditioned:=/cpp/wheel_odom/conditioned > /tmp/cond_ab_cpp.log 2>&1 &
sleep 4
python3 /tmp/job594_condab.py $2 2>&1 | grep -av "^\["
echo "== 로그(캘리브·ZUPT) Python"; grep -aE "calibrated|not stationary|ZUPT" /tmp/cond_ab_py.log | cut -c1-200 | tail -4
echo "== 로그(캘리브·ZUPT) C++";    grep -aE "calibrated|not stationary|ZUPT" /tmp/cond_ab_cpp.log | cut -c1-200 | tail -4
pkill -INT -f "cond_ab_(py|cpp)" 2>/dev/null; sleep 1; pkill -9 -f "cond_ab_(py|cpp)" 2>/dev/null
echo "  남은 비교용 노드: $(pgrep -fc 'cond_ab_(py|cpp)')"
