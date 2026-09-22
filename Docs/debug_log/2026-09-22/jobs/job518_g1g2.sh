#!/bin/bash
# N6-1 정지 검증(Jetson, 2026-09-22): 현재 모드에서 G1(전역·로컬 코스트맵 상자 셀, 감사)·G2(CPU: depth_relay·nvblox·controller·planner, STVL 갱신 유무)를 잰다. 인자: NAME BX BY
set +u
NM=$1; BX=$2; BY=$3
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "## $NM: 활성 plugins 로컬 $(python3 -c "import yaml; p=yaml.safe_load(open('/tmp/nav2_params_active.yaml')); print(p['local_costmap']['local_costmap']['ros__parameters']['plugins'][0], '| 전역', p['global_costmap']['global_costmap']['ros__parameters']['plugins'][1])")"
echo "  릴레이 구독자: $(timeout 8 ros2 topic info /camera/depth/points_filtered 2>&1 | grep -a 'Subscription count' | grep -ao '[0-9]*') | 릴레이 발행 Hz: $(timeout 6 ros2 topic hz /camera/depth/points_filtered 2>&1 | grep -ao 'average rate: [0-9.]*' | head -1 | cut -d' ' -f3)"
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1; timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1; sleep 15
echo "  전역 코스트맵:"; python3 /tmp/job489_gridcmp.py ${NM}g 0 /global_costmap/costmap 2>&1 | grep -aE '^====|LETHAL 셀' | cut -c1-160
echo "  로컬 코스트맵:"; python3 /tmp/job489_gridcmp.py ${NM}l 0 /local_costmap/costmap 2>&1 | grep -aE '^====|LETHAL 셀' | cut -c1-160
echo "  감사(job248):"; BOX_HINT="$BX $BY" timeout 100 python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자|최소폭|전역' | head -4 | cut -c1-160
echo "  CPU 20 s(top 2 회 평균): $(top -b -n2 -d10 2>/dev/null | awk '/PID +USER/{f++} f==2' | awk '$12 ~ /depth_relay|python3|nvblox|controller|planner|realsense/ {printf "%s %s%% | ", $12, $9}')"
echo "  CPU 합(전 프로세스, top 1 회): $(top -b -n2 -d5 2>/dev/null | awk '/PID +USER/{f++} f==2 && $9+0>0 {s+=$9} END {printf "%.0f", s}') %"
