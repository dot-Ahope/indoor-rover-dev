#!/bin/bash
# 손 이동 후 S4 회차: 재기동 → 상자 측정 → dy 벗어나면 중단 / dx 만 벗어나면 직진 보정 → 게이트 → 주행
set +u
NAME=${1:-s4rX}; BX=0.87; BY=-0.38; TOL=0.12
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 재기동 (base 유지) ##########"
bash /tmp/job240_clean.sh 15 2>&1 | grep -aE "정리 후|재기동 생략|wheel_odom|gyro bias|active \[3\]|로버 자세|EKF 위반" | sed 's/^/  /'
echo "########## 상자 측정 → dx 보정 ##########"
BOX=$(python3 /tmp/job248_audit.py 2>&1 | grep -a "^상자:" | head -1); echo "  $BOX"
read DX DY <<< $(python3 -c "
import re,sys; m=re.search(r'x=([-0-9.]+)\s+중심 y=([-0-9.]+)', '''$BOX''')
print('%.3f %.3f'%(float(m.group(1))-$BX, float(m.group(2))-($BY)) if m else 'nan nan')")
echo "  기준선 대비 dx $DX dy $DY"
python3 -c "import sys; sys.exit(0 if abs(float('$DY'))<=$TOL else 1)" || { echo "  ★ dy 가 ±$TOL 을 벗어남 — 손 이동 필요 (왼쪽으로 $(python3 -c "print('%.0f'%(abs(float('$DY'))*100))") cm $(python3 -c "print('더' if float('$DY')>0 else '반대로')"))"; exit 1; }
if python3 -c "import sys; sys.exit(0 if abs(float('$DX'))>$TOL else 1)"; then
  echo "  dx 보정: $(python3 -c "print('전진' if float('$DX')>0 else '후진')") $(python3 -c "print('%.2f'%abs(float('$DX')))") m"
  python3 /tmp/job266_nudge.py $DX 2>&1 | sed 's/^/    /'
  sleep 3
  BOX=$(python3 /tmp/job248_audit.py 2>&1 | grep -a "^상자:" | head -1); echo "  재측정: $BOX"
fi
echo "########## S4 3/3 ##########"
bash /tmp/job254_s4run.sh $NAME 1.8 $BX $BY $TOL 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|clear except|Goal succeeded|backup failed|EKF 위반|게이트 실패|★|bag:"
