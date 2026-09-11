#!/bin/bash
# v5: 전진 0.39 (상자 1.27 m 복원) → 힌트 게이트 → 목표 지점 RPP 폭 게이트 → 코스 D=1.85
set +u
D=1.85
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "################ 0. 전진 0.39 m (오탐 기반 후진 취소) ################"
python3 /tmp/job266_nudge.py 0.39 2>&1 | sed 's/^/  /'
sleep 2
echo "################ 1. 재탐지 + 목표 지점 폭 ################"
AUD=$(BOX_HINT="1.27 -0.15" python3 /tmp/job248_audit.py 2>&1)
echo "$AUD" | grep -aE "낮은 클러스터|^상자:|^   \[" | sed 's/^/  /'
echo "$AUD" | sed -n '/########## C/,$p' | grep -aE "^   (1\.[4-9]0|2\.[0-2]0) " | awk '{print "  전방 "$1"  RPP폭 "$5}'
W=$(echo "$AUD" | sed -n '/########## C/,$p' | grep -aE "^   1\.80 " | awk '{print $5}')
echo "  목표 거리 $D 부근(1.80 행) RPP 기준 폭: ${W:-?} m"
python3 -c "import sys; sys.exit(0 if float('${W:-0}')>=0.25 else 1)" || { echo "  ★ 목표 지점 폭 0.25 미만 — 목표가 벽에 걸림. 주행하지 않음"; exit 1; }
echo "################ 2. 코스 주행 D=$D (패딩 0.03, 상자 기준 1.27/-0.15 ±0.25) ################"
bash /tmp/job254_s4run.sh v5 $D 1.27 -0.15 0.25 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자:|상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|clear except|Goal succeeded|backup|EKF 위반|게이트 실패|★|bag:"
echo -n "  최종 자세: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
