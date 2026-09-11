#!/bin/bash
# Nav2 복귀 실패 후 수동 직진 복귀 — 전진 투영(RPP 기준 100) + 라이다 정면 게이트
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
P=$(timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' ')
echo "  현재: $P"
echo "=== 게이트: 전진 0~0.6 m 투영 (100=BLOCK) ==="
FWD=$(python3 /tmp/job228_why.py 2>&1 | sed -n '/전진 투영/,/후진 투영/p' | grep -aE "^ +0\.[0-6]0 ")
echo "$FWD" | sed 's/^/  /'
echo "$FWD" | grep -aq BLOCK && { echo "  ★ 전진 경로에 LETHAL — 수동 복귀 중단"; exit 1; }
FR=$(bash /tmp/job21c_where.sh 2>&1 | grep -a "정면" | grep -aoE "[0-9]+cm" | tr -d cm)
echo "  라이다 정면 ${FR:-?} cm"
[ "${FR:-0}" -lt 100 ] && { echo "  ★ 정면 1 m 미만 — 중단"; exit 1; }
# 원점까지 거리·방향
python3 - <<'PY' > /tmp/ret_plan.txt
import subprocess,re,math
out=subprocess.run("source /opt/ros/humble/setup.bash; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE 'Translation|RPY' | head -2",shell=True,capture_output=True,text=True,executable='/bin/bash').stdout
nums=re.findall(r'[-0-9.]+',out.replace('Translation','').replace('RPY','').replace('radian',''))
x,y=float(nums[0]),float(nums[1]); yaw=float(nums[5])
d=math.hypot(x,y); bearing=math.atan2(-y,-x)
err=math.degrees((bearing-yaw+math.pi)%(2*math.pi)-math.pi)
print("%.3f %.1f %.1f"%(d,math.degrees(bearing),err))
PY
read D BR ERR < /tmp/ret_plan.txt
echo "  원점까지 $D m, 방위 $BR°, 현재 heading 과의 차 $ERR°"
python3 -c "import sys; sys.exit(0 if abs(float('$ERR'))<=12 else 1)" || { echo "  heading 차 12° 초과 → 먼저 정렬"; python3 /tmp/job225_face.py $BR 2.0 2>&1 | tail -1 | sed 's/^/    /'; }
echo "=== 직진 $D m ==="
python3 /tmp/job266_nudge.py $D 2>&1 | sed 's/^/  /'
echo "=== 원점에서 0° 정렬 ==="
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
echo -n "  최종: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  상자(로버 기준): $(python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1 | cut -c1-48)"
