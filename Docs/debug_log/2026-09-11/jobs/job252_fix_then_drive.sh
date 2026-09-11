#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 고아 robot_state_publisher 정리 ==="
CUR=$(grep -ao 'robot_state_publisher-2\]: process started with pid \[[0-9]*\]' /tmp/base.log | grep -o '[0-9]*\]$' | tr -d ']')
echo "  현재 base.launch 의 자식 PID: ${CUR:-?}"
for pid in $(pgrep -f robot_state_publisher); do
  if [ "$pid" != "$CUR" ]; then
    PP=$(ps -o ppid= -p $pid | tr -d ' '); ST=$(ps -o lstart= -p $pid)
    echo "  고아 PID $pid (ppid $PP, 시작 $ST) → SIGTERM"
    kill -TERM $pid 2>/dev/null
  fi
done
sleep 3
for pid in $(pgrep -f robot_state_publisher); do
  [ "$pid" != "$CUR" ] && { echo "  잔존 $pid → SIGKILL"; kill -9 $pid 2>/dev/null; }
done
sleep 2
N=$(pgrep -fc robot_state_publisher | head -1); N=${N:-0}
echo "  프로세스: $N개"
[ "$N" != "1" ] && { echo "  ★ 여전히 $N개 — 중단"; exit 1; }
echo "  /tf_static 발행 확인: $(timeout 6 ros2 topic info /tf_static 2>/dev/null | grep -a 'Publisher count')"
echo "  URDF TF 생존: $(timeout 6 ros2 run tf2_ros tf2_echo base_link camera_link 2>&1 | grep -a Translation | head -1)"
echo "=== 전 스택 중복 재감사 ==="
DUP=0
for p in microros_agent robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node scan_deskew slam_toolbox controller_server planner_server bt_navigator behavior_server lifecycle_manager stuck_monitor; do
  c=$(pgrep -fc "$p" 2>/dev/null | head -1); c=${c:-0}; [ "$c" != "1" ] && DUP=1
  printf "  %-20s %s%s\n" "$p" "$c" "$([ "$c" != "1" ] && echo '  ← !!')"
done
[ "$DUP" = "1" ] && { echo "  ★ 중복/누락 — 주행 금지"; exit 1; }
echo "  이상 없음 → 주행"
echo
bash /tmp/job231_drive.sh job251 1.60 90
