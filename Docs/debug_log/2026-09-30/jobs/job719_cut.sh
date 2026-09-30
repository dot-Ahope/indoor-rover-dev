#!/bin/bash
# 09-30 §17: 점프 전(bag +699 s, 17:36:15)까지만 지도 되살리기 — 도메인 42 에서 office_v1 이어 그리기 slam(현 slam.yaml)을 sim time 으로 띄우고
#   job719_cutreplay.py 로 재생·저장. 저장 이름은 후보(cand_*) — 사용자 확인 전엔 office_v2 로 부르지 않는다.
#   라이브 스택(도메인 0): 깨진 SLAM·bag 기록기만 멈춤(부하 경쟁 방지), 센서·EKF·에이전트는 유지.
set +u
BAG=/tmp/bags/map_0930_1724; CUT=${1:-699}; OUT=/home/jetson/maps/office/cand_0930_cut${CUT}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
echo "== bag 보존: ~/bags 로 복사(재부팅 시 /tmp 소실)"; mkdir -p ~/bags; [ -d ~/bags/map_0930_1724 ] || cp -r $BAG ~/bags/; du -sh ~/bags/map_0930_1724
echo "== 라이브 깨진 SLAM 정지"; pkill -INT -f "ros2 bag record"; pkill -f "slam.launch"; pkill -f "async_slam_toolbox_node --ros-args -r __node:=slam_toolbox"; sleep 3
for p in $(pgrep -f async_slam_toolbox_node); do grep -qa "use_sim_time:=true" /proc/$p/cmdline || kill $p; done; sleep 2
echo "  남은 slam: $(pgrep -fc async_slam_toolbox_node)"
export ROS_DOMAIN_ID=42
pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 1
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
echo "  루프 창: $(grep -aoE 'loop_search_space_dimension: [0-9.]+' $Y)"
setsid ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file $Y -p use_sim_time:=true \
  -p map_file_name:=/home/jetson/maps/office/office_v1 -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false > /tmp/cut_slam.log 2>&1 &
for i in $(seq 1 20); do ros2 param get /slam_toolbox use_sim_time >/dev/null 2>&1 && break; sleep 1; done
sleep 5; echo "  재생용 slam: $(readlink -f /proc/$(pgrep -f 'async_slam_toolbox_node.*use_sim_time:=true' | head -1)/exe)"
[ -e $OUT.posegraph ] && { echo "이미 있음: $OUT"; exit 1; }
python3 /tmp/job719_cutreplay.py $BAG $CUT $OUT 2>&1 | grep -av "^\["
echo "== Ceres(루프 클로저) 흔적: $(grep -ac preprocessor.cc /tmp/cut_slam.log)건"
pkill -INT -f "async_slam_toolbox_node.*use_sim_time:=true"; sleep 2; pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null
ls -la $OUT.* 2>&1; grep -aE "resolution|origin" $OUT.yaml 2>/dev/null
echo "== PNG 변환(확인용)"
python3 - $OUT <<'EOF'
import sys
o = sys.argv[1]
try:
    from PIL import Image; Image.open(o + '.pgm').save(o + '.png'); print('  PIL', o + '.png')
except Exception as e:
    import cv2; cv2.imwrite(o + '.png', cv2.imread(o + '.pgm', -1)); print('  cv2', o + '.png', e)
EOF
python3 - /home/jetson/maps/office/office_v1 <<'EOF'
import sys
o = sys.argv[1]
try:
    from PIL import Image; Image.open(o + '.pgm').save('/tmp/office_v1.png')
except Exception:
    import cv2; cv2.imwrite('/tmp/office_v1.png', cv2.imread(o + '.pgm', -1))
print('  /tmp/office_v1.png')
EOF
