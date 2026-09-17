#!/bin/bash
# 사용자 승인(09-17): ros-humble-fastrtps 2.6.11 → 2.6.12 (StatefulWriter 락 순서 역전 수정 #6463)
echo "=== 1. 호스트 ROS 노드 정지 (micro-ROS 에이전트 컨테이너는 유지) ==="
PATS="navigation.launch slam.launch sensors.launch description.launch navigation_launch controller_server planner_server bt_navigator behavior_server velocity_smoother smoother_server waypoint_follower lifecycle_manager stuck_monitor slam_toolbox ekf_node sensor_conditioner scan_deskew rplidar realsense depth_relay robot_state_publisher foxglove"
for p in $PATS; do pkill -TERM -f "$p" 2>/dev/null; done
for i in $(seq 1 15); do n=0; for p in $PATS; do c=$(pgrep -fc "$p"); n=$((n+c)); done; [ "$n" = "0" ] && break; sleep 1; done
for p in $PATS; do pkill -9 -f "$p" 2>/dev/null; done; sleep 1
echo "  남은 호스트 ROS 프로세스: $(ps -eo args | grep -aE '/opt/ros/humble/lib|ros2_ws/install' | grep -av grep | wc -l)   에이전트: $(docker ps --format '{{.Names}}' | grep -c microros_agent)"
echo "=== 2. 설치 전 ==="; dpkg -s ros-humble-fastrtps | awk '/^Version/{print "  fastrtps", $2}'
echo "=== 3. 시뮬레이션 ==="
S=$(echo "__PW__" | sudo -S -p "" apt-get -s install --only-upgrade --no-install-recommends ros-humble-fastrtps 2>&1)
echo "$S" | grep -aE "^Inst|^Remv|upgraded," | sed 's/^/  /'
BAD=$(echo "$S" | grep -aE "^(Inst|Remv)" | grep -avE "^Inst ros-humble-fastrtps |^Inst ros-humble-fastcdr " | wc -l)
if [ "$BAD" != "0" ]; then echo "  ★ fastrtps/fastcdr 외 패키지 변경 $BAD 건 — 설치 중단(사용자 확인 필요)"; exit 2; fi
echo "=== 4. 설치 ==="
echo "__PW__" | sudo -S -p "" sh -c 'DEBIAN_FRONTEND=noninteractive apt-get install -y --only-upgrade --no-install-recommends ros-humble-fastrtps < /dev/null' 2>&1 | grep -aE "Unpacking|Setting up|upgraded,|^E:" | sed 's/^/  /'
echo "=== 5. 설치 후 ==="; dpkg -s ros-humble-fastrtps | awk '/^Version/{print "  fastrtps", $2}'
ls -la /opt/ros/humble/lib/libfastrtps.so* | awk '{print "  " $NF, $6, $7, $8}'
