#!/bin/bash
# 복귀 → heading 정렬 → 위치 확인 → S4 다음 회차
set +u
NAME=${1:-s4rN}
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 복귀 (Nav2 → 원점) ##########"
python3 /tmp/job207_return.py 0.0 0.0 0 120 2>&1 | tail -2 | sed 's/^/  /'
grep -a "STUCK" /tmp/nav2.log | tail -1 | cut -c1-140 | sed 's/^/  stuck_monitor: /'
echo "########## heading 정렬 ##########"
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
P=$(timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -a Translation | head -1 | grep -oE '\[[-0-9., ]+\]')
echo "  위치: $P"
python3 - "$P" <<'PY'
import sys,re,math
x,y,_=[float(v) for v in re.findall(r'[-0-9.]+', sys.argv[1])[:3]]
d=math.hypot(x,y)
print("  원점 오차 %.3f m %s"%(d, "(허용 0.15 안)" if d<=0.15 else "← 0.15 초과, 회차 무효 위험"))
sys.exit(0 if d<=0.20 else 1)
PY
[ $? -ne 0 ] && { echo "  ★ 위치 오차 0.20 초과 — 이 회차 진행하지 않음"; exit 1; }
echo
bash /tmp/job254_s4run.sh $NAME 1.8
