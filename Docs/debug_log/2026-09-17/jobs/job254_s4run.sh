#!/bin/bash
# S4 1회차 절차: 게이트(중복·보드·통과폭) → 주행 D=1.8 (bag+로그분석)
set +u
NAME=${1:-s4run}; D=${2:-1.8}; BX=${3:-0.87}; BY=${4:--0.38}; TOL=${5:-0.12}
# ★ 2026-09-11: 출발 판정은 map 원점이 아니라 **상자 상대 위치**로 한다.
#   s4r3 에서 Nav2 복귀가 map 상 원점 0.136m 안에 도착했는데 상자는 0.64/-0.08(기준 0.87/-0.38)에
#   있었다 — SLAM 보정(map->odom 18cm)이 회차 사이에 바뀌어 같은 map 좌표가 다른 물리 위치가 됐다.
#   "같은 코스" 는 상자를 기준으로만 보장된다. 허용 ±TOL.
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 게이트 ##########"
DUP=0
for p in microros_agent robot_state_publisher realsense2_camera rplidar sensor_conditioner ekf_node scan_deskew slam_toolbox controller_server planner_server bt_navigator behavior_server lifecycle_manager stuck_monitor; do
  c=$(pgrep -fc "$p" 2>/dev/null | head -1); c=${c:-0}; [ "$c" != "1" ] && { DUP=1; echo "  ★ $p = $c개"; }
done
[ "$DUP" = "1" ] && { echo "  중복/누락 — 중단"; exit 1; }
BR=$(timeout 6 ros2 topic hz /wheel_odom 2>&1 | grep -aoE 'average rate: [0-9.]+' | tail -1)
[ -z "$BR" ] && { echo "  ★ 보드 무발행 — 중단"; exit 1; }
echo "  프로세스 14/14 단일, 보드 $BR"
SA=$(python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\[")
echo "  SLAM: $(echo "$SA" | head -1)"
[ "$(echo "$SA" | tail -1)" = "OK" ] || { echo "  ★ SLAM map->odom 불량 — 중단 (09-17 mp7: 끊긴 채 출발하면 BT 타임아웃·복구·실패)"; exit 1; }
[ "$(pgrep -fc 'ros2 bag record' | head -1)" != "0" ] && { echo "  ★ 이전 bag record 잔존 — 정리"; pkill -INT -f 'ros2 bag record'; sleep 3; }
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 15
echo -n "  출발 자세: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
AUD=$(BOX_HINT="$BX $BY" python3 /tmp/job248_audit.py 2>&1)
echo "$AUD" | grep -aE "^상자:|^   \[|→ 전방 2.2m" | sed 's/^/  /'
BOXLINE=$(echo "$AUD" | grep -a "^상자:" | head -1)
python3 - "$BOXLINE" "$BX" "$BY" "$TOL" <<'PYG'
import sys,re
m=re.search(r'x=([-+0-9.]+)\s+중심 y=([-+0-9.]+)', sys.argv[1])   # 2026-09-14: y=+0.008 처럼 + 부호도 허용
if not m: print("  ★ 상자 검출 실패 — 주행 불가"); sys.exit(1)
x,y=float(m.group(1)),float(m.group(2)); bx,by,tol=[float(v) for v in sys.argv[2:5]]
dx,dy=x-bx,y-by
ok=abs(dx)<=tol and abs(dy)<=tol
print("  상자 기준선 대비 dx %+.2f dy %+.2f (허용 ±%.2f) → %s"%(dx,dy,tol,"OK" if ok else "★ 벗어남 — 출발 위치 재조정 필요"))
sys.exit(0 if ok else 1)
PYG
[ $? -ne 0 ] && { echo "  게이트 실패 — 주행하지 않음"; exit 1; }
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
echo
echo "########## 주행 D=$D ##########"
bash /tmp/job231_drive.sh $NAME $D 90
