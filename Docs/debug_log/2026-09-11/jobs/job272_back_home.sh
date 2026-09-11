#!/bin/bash
# 후진으로 원점 복귀 — 후방 투영(100) + 라이다 후방 게이트. 파서는 tf2_echo 의 대괄호 안만 읽는다.
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
pose() { timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | python3 -c "
import sys,re
t=sys.stdin.read()
tr=re.search(r'Translation: \[([^\]]+)\]',t); rp=re.search(r'RPY \(radian\) \[([^\]]+)\]',t)
if not tr or not rp: print('nan nan nan'); sys.exit()
x,y,_=[float(v) for v in tr.group(1).split(',')]; yaw=float(rp.group(1).split(',')[2])
print('%.3f %.3f %.4f'%(x,y,yaw))"; }
read X Y YAW <<< "$(pose)"
echo "  현재 map ($X, $Y) yaw $YAW rad"
python3 -c "import sys; sys.exit(0 if '$X'!='nan' else 1)" || { echo "  ★ 자세 파싱 실패 — 중단"; exit 1; }
# 후진 방향(= 로버 뒤쪽)이 원점을 향하는가: 원점 방위 vs (yaw+π)
read D ERR <<< "$(python3 -c "
import math; x,y,yaw=$X,$Y,$YAW
d=math.hypot(x,y); b=math.atan2(-y,-x); back=yaw+math.pi
e=math.degrees((b-back+math.pi)%(2*math.pi)-math.pi); print('%.3f %.1f'%(d,e))")"
echo "  원점까지 $D m, 후진 방향과 원점 방위 차 $ERR°"
python3 -c "import sys; sys.exit(0 if abs(float('$ERR'))<=15 else 1)" || { echo "  ★ 후진 방향이 원점과 15° 이상 어긋남 — 중단(사용자 확인 필요)"; exit 1; }
echo "=== 게이트: 후진 0~0.3 m 투영 (100=BLOCK) ==="
BK=$(python3 /tmp/job228_why.py 2>&1 | sed -n '/후진 투영/,/제자리 회전 투영/p' | grep -aE "^ +0\.[0-9]0 ")
echo "$BK" | sed 's/^/  /'
echo "$BK" | grep -aq BLOCK && { echo "  ★ 후진 경로에 LETHAL — 중단"; exit 1; }
RR=$(bash /tmp/job21c_where.sh 2>&1 | grep -a "후면" | grep -aoE "[0-9]+cm" | tr -d cm)
echo "  라이다 후면 ${RR:-?} cm"
[ "${RR:-0}" -lt 100 ] && { echo "  ★ 후면 1 m 미만 — 중단"; exit 1; }
echo "=== 후진 $D m ==="
python3 /tmp/job266_nudge.py -$D 2>&1 | sed 's/^/  /'
read X Y YAW <<< "$(pose)"
echo "  최종 map ($X, $Y) yaw $(python3 -c "import math; print('%.1f'%math.degrees($YAW))")°"
echo "  상자(로버 기준): $(python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1 | cut -c1-48)"
