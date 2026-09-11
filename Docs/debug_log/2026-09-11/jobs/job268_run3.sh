#!/bin/bash
# S4 3/3 — 사용자 판단: 좌우 17cm 오프셋은 동등 처리. dx 만 직진 보정. 재기동 생략(6분 전 완료, 이후 주행 없음).
set +u
NAME=${1:-s4r7}; BX=0.87; BY=-0.38
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 상자 측정 → dx 보정 ##########"
BOX=$(python3 /tmp/job248_audit.py 2>&1 | grep -a "^상자:" | head -1); echo "  $BOX"
DX=$(python3 -c "
import re; m=re.search(r'x=([-0-9.]+)\s+중심 y=([-0-9.]+)', '''$BOX'''); print('%.3f'%(float(m.group(1))-$BX) if m else 'nan')")
DY=$(python3 -c "
import re; m=re.search(r'x=([-0-9.]+)\s+중심 y=([-0-9.]+)', '''$BOX'''); print('%.3f'%(float(m.group(2))-($BY)) if m else 'nan')")
echo "  기준선 대비 dx $DX dy $DY  (dy 는 사용자 판단으로 허용)"
if python3 -c "import sys; sys.exit(0 if abs(float('$DX'))>0.08 else 1)"; then
  echo "  dx 보정: $(python3 -c "print('전진' if float('$DX')>0 else '후진')") $(python3 -c "print('%.2f'%abs(float('$DX')))") m"
  python3 /tmp/job266_nudge.py $DX 2>&1 | sed 's/^/    /'
  sleep 3
  BOX=$(python3 /tmp/job248_audit.py 2>&1 | grep -a "^상자:" | head -1); echo "  재측정: $BOX"
fi
echo "########## S4 3/3 (dy 허용 0.25) ##########"
bash /tmp/job254_s4run.sh $NAME 1.8 $BX $BY 0.25 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|clear except|Goal succeeded|backup failed|EKF 위반|게이트 실패|★|bag:"
