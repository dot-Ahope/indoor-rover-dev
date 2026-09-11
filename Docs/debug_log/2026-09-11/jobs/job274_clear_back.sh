#!/bin/bash
# 유령(센서 근거 없는 LETHAL) 제거 → 감사 → 게이트 후진 복귀
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "=== 코스트맵 클리어 → 8초 재마킹 ==="
timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap "{}" >/dev/null 2>&1
sleep 8
python3 /tmp/job248_audit.py 2>&1 | grep -aE "^  (로컬|전역): 전방" | sed 's/^/ /'
echo "=== 후진 게이트 (100=BLOCK) ==="
BK=$(python3 /tmp/job228_why.py 2>&1 | sed -n '/후진 투영/,/제자리 회전 투영/p' | grep -aE "^ +0\.[0-9]0 ")
echo "$BK" | sed 's/^/  /'
echo "$BK" | grep -aq BLOCK && { echo "  ★ 여전히 LETHAL — 중단 (실물 가능성, 사용자 확인)"; exit 1; }
RR=$(bash /tmp/job21c_where.sh 2>&1 | grep -a "후면" | grep -aoE "[0-9]+cm" | tr -d cm)
echo "  라이다 후면 ${RR:-?} cm"; [ "${RR:-0}" -lt 100 ] && { echo "  ★ 후면 1 m 미만 — 중단"; exit 1; }
pose() { timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | python3 -c "
import sys,re
t=sys.stdin.read(); tr=re.search(r'Translation: \[([^\]]+)\]',t); rp=re.search(r'RPY \(radian\) \[([^\]]+)\]',t)
x,y,_=[float(v) for v in tr.group(1).split(',')]; print('%.3f %.3f %.4f'%(x,y,float(rp.group(1).split(',')[2])))"; }
read X Y YAW <<< "$(pose)"
read D ERR <<< "$(python3 -c "
import math; x,y,yaw=$X,$Y,$YAW; d=math.hypot(x,y); b=math.atan2(-y,-x); back=yaw+math.pi
print('%.3f %.1f'%(d, math.degrees((b-back+math.pi)%(2*math.pi)-math.pi)))")"
echo "  현재 ($X, $Y) → 원점 $D m, 후진 방향 오차 $ERR°"
python3 -c "import sys; sys.exit(0 if abs(float('$ERR'))<=15 else 1)" || { echo "  ★ 후진 방향 어긋남 — 중단"; exit 1; }
echo "=== 후진 $D m ==="
python3 /tmp/job266_nudge.py -$D 2>&1 | sed 's/^/  /'
read X Y YAW <<< "$(pose)"
echo "  최종 map ($X, $Y) yaw $(python3 -c "import math; print('%.1f'%math.degrees($YAW))")°"
echo "  상자(로버 기준): $(python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1 | cut -c1-48)"
