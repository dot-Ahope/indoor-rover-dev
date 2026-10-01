#!/bin/bash
# 09-30 §17: 점프 전(bag +699 s, 17:36:15)까지만 지도 되살리기 — 도메인 42 에서 office_v1 이어 그리기 slam(현 slam.yaml)을 sim time 으로 띄우고
#   job719_cutreplay.py 로 재생·저장. 저장 이름은 후보(cand_*) — 사용자 확인 전엔 office_v2 로 부르지 않는다.
#   라이브 스택(도메인 0): 깨진 SLAM·bag 기록기만 멈춤(부하 경쟁 방지), 센서·EKF·에이전트는 유지.
set +u
# 10-01: bag 은 재부팅에 안전한 ~/bags 사본 사용. 09-30 에 "재생: 앞 …" 이 5 분 넘게 안 보인 건 grep 이 파이프에서 출력을 모아 둔 탓(추정) → --line-buffered
# 10-01 §2: 인자 2 = 변형 이름(nolc = 루프 클로저 끔). SLAM_EXTRA 로 slam 매개변수 추가.
BAG=/home/jetson/bags/map_0930_1724; CUT=${1:-699}; V=${2:-}; OUT=/home/jetson/maps/office/cand_0930_cut${CUT}${V:+_$V}
case "$V" in nolc) SLAM_EXTRA="-p do_loop_closing:=false" ;; esac
echo "== 변형: ${V:-기본} | slam 추가 매개변수: ${SLAM_EXTRA:-없음} | 출력 $OUT"
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
echo "== bag: $(du -sh $BAG) | uptime $(uptime -p) | load $(cut -d' ' -f1-3 /proc/loadavg)"
echo "== 라이브 깨진 SLAM 정지"; pkill -INT -f "ros2 bag record"; pkill -f "slam.launch"; pkill -f "async_slam_toolbox_node --ros-args -r __node:=slam_toolbox"; sleep 3
for p in $(pgrep -f async_slam_toolbox_node); do grep -qa "use_sim_time:=true" /proc/$p/cmdline || kill $p; done; sleep 2
echo "  남은 slam: $(pgrep -fc async_slam_toolbox_node)"
export ROS_DOMAIN_ID=42
pkill -9 -f "async_slam_toolbox_node.*use_sim_time:=true" 2>/dev/null; sleep 1
Y=$(ros2 pkg prefix rover_bringup)/share/rover_bringup/config/slam.yaml
echo "  루프 창: $(grep -aoE 'loop_search_space_dimension: [0-9.]+' $Y)"
setsid ros2 run slam_toolbox async_slam_toolbox_node --ros-args --params-file $Y -p use_sim_time:=true \
  -p map_file_name:=/home/jetson/maps/office/office_v1 -p "map_start_pose:=[0.0, 0.0, 0.0]" -p map_start_at_dock:=false $SLAM_EXTRA > /tmp/cut_slam.log 2>&1 &
for i in $(seq 1 20); do ros2 param get /slam_toolbox use_sim_time >/dev/null 2>&1 && break; sleep 1; done
sleep 5; echo "  재생용 slam: $(readlink -f /proc/$(pgrep -f 'async_slam_toolbox_node.*use_sim_time:=true' | head -1)/exe)"
[ -e $OUT.posegraph ] && { echo "이미 있음: $OUT"; exit 1; }
python3 -u /tmp/job719_cutreplay.py $BAG $CUT $OUT 2>&1 | grep -av --line-buffered "^\["
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
