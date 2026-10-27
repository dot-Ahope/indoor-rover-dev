#!/bin/bash
# run_slam_replay — 위치 추정 SLAM 을 주행 bag 입력으로 다시 돌려 map→odom stamp 정체를 잰다 (2026-10-27 §26, Jetson, 로버 안 움직임).
#   ROS_DOMAIN_ID=42(떠 있는 스택과 분리) · 포크 slam_toolbox localization_slam_toolbox_node · slam.yaml + slam.launch.py 의 위치 추정 덮어쓰기와 같은 값
#   + use_sim_time. 변형 파라미터는 환경 SLAM_EXTRA(예 "-p do_loop_closing:=false"). 입력 공급 · 기록은 slam_replay_feed.py.
#   인자: 변형이름 bag폴더 [시작 오프셋 s=0] [길이 s=전체]   출력: /tmp/slamrep/<변형>.txt(MO · CPU 줄) · <변형>.log(SLAM 로그)
set +u
V=$1; BAG=$2; OFF=${3:-0}; DUR=${4:-100000}; O=/tmp/slamrep; mkdir -p $O
export ROS_DOMAIN_ID=42 FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; source ~/slam_ws/install/setup.bash
Y=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/slam.yaml
setsid nohup ~/slam_ws/install/slam_toolbox/lib/slam_toolbox/localization_slam_toolbox_node --ros-args -r __node:=slam_toolbox --params-file $Y \
  -p mode:=localization -p map_file_name:=/home/jetson/maps/office/office_v3 -p "map_start_pose:=[0.0,0.0,0.0]" -p map_start_at_dock:=false \
  -p minimum_travel_distance:=0.30 -p minimum_travel_heading:=0.15 -p map_update_interval:=10.0 -p transform_timeout:=1.5 -p use_sim_time:=true \
  ${SLAM_EXTRA:-} > $O/$V.log 2>&1 &
P=$!   # setsid 는 백그라운드 작업에서 fork 없이 exec → $! 가 곧 SLAM pid. ⚠ pgrep/pkill 패턴 금지 — 본 스택 SLAM 도 같은 명령줄 꼴(launch)이라 함께 걸림
for i in $(seq 1 60); do grep -aq "Registering sensor\|Finished serializing Dataset" $O/$V.log && break; sleep 0.5; done
echo "[$V] SLAM pid $P($(cat /proc/$P/comm 2>/dev/null)) · 기동 $(grep -ac 'Finished serializing Dataset' $O/$V.log) · 추가 인자: ${SLAM_EXTRA:-없음}"
SLAM_PID=$P python3 /tmp/slam_replay_feed.py $BAG $O/$V.txt $OFF $DUR 2>&1 | grep -av "^\["
kill -INT $P 2>/dev/null; sleep 2; kill -9 $P 2>/dev/null
echo "[$V] MO $(grep -c '^MO' $O/$V.txt) 줄 · 스캔 버림 $(grep -ac 'Message Filter dropping' $O/$V.log) · 오류 $(grep -aci 'error\|exception' $O/$V.log)"
