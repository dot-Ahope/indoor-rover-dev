#!/bin/bash
# 10-01 §1: 후보 포즈 그래프(cand_0930_cut699)에서 격자 지도(pgm/yaml) 만들기 — job719 의 save_map 이 255 로 실패(sim time 재생 뒤, 원인 미확정)
#   도메인 42·벽시계로 slam 이 그래프만 불러오게 하고 /map 이 나오면 map_saver_cli 로 저장. 라이브(도메인 0)는 건드리지 않음.
set +u; N=${1:-cand_0930_cut699}; D=/home/jetson/maps/office
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
export ROS_DOMAIN_ID=42
grep -a "result\|Error\|error\|save\|Save" /tmp/cut_slam.log | tail -5 | sed 's/^/  (job719 slam 로그) /'
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
setsid ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file $Y -p map_file_name:=$D/$N -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false -r __node:=slam_toolbox > /tmp/cand_grid_slam.log 2>&1 &
for i in $(seq 1 40); do timeout 3 ros2 topic echo --once /map_metadata >/dev/null 2>&1 && break; sleep 2; done
echo "  /map_metadata: $(timeout 5 ros2 topic echo --once /map_metadata 2>/dev/null | grep -aE 'width|height' | tr '\n' ' ')"
timeout 40 ros2 run nav2_map_server map_saver_cli -f $D/$N --ros-args -p map_subscribe_transient_local:=true 2>&1 | grep -aiE "saved|error|fail" | head -5
pkill -INT -f "async_slam_toolbox_node.*$N"; sleep 2; pkill -9 -f "async_slam_toolbox_node.*$N" 2>/dev/null
ls -la $D/$N.* ; cat $D/$N.yaml 2>/dev/null
python3 -c "
import cv2; cv2.imwrite('/tmp/$N.png', cv2.imread('$D/$N.pgm', -1)); print('  /tmp/$N.png')"
python3 -c "
import cv2; cv2.imwrite('/tmp/office_v1.png', cv2.imread('$D/office_v1.pgm', -1)); print('  /tmp/office_v1.png')"
