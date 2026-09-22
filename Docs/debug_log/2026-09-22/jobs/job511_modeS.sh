#!/bin/bash
# 09-22 N4 팔 S 준비(Jetson 측, prep 뒤): 로컬 코스트맵을 STVL 층으로 복귀(Nav2 만 재기동) → nvblox 정지 → 클리어·8 s 재관측 → plugins 실효값 확인. 인자: BX BY
set +u
BX=$1; BY=$2; CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "== 현재 plugins: $(timeout 12 ros2 param get /local_costmap/local_costmap plugins 2>&1 | tail -1 | cut -c1-80)"
QUICK=1 bash /tmp/job488_layer_ab.sh stvl $BX $BY 2>&1 | grep -aE '실행값|오류'
nv_pids() { docker exec $CN bash -c "pgrep -f '^$BIN' || true"; }
for p in $(nv_pids); do docker exec $CN kill -INT $p 2>/dev/null; done; sleep 3; for p in $(nv_pids); do docker exec $CN kill -9 $p 2>/dev/null; done; sleep 1; echo "== nvblox 정지 (남은 pid '$(nv_pids | tr '\n' ' ')')"
bash /tmp/job442_clearwait.sh 2>&1 | tail -1
echo "== 상자·창(job248 1 표본): $(BOX_HINT="$BX $BY" timeout 100 python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자|최소폭' | head -2 | tr '\n' ' ' | cut -c1-200)"
