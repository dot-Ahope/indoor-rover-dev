#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "################ 0. 후진 0.42 m (상자 1.27 m 로) ################"
python3 /tmp/job266_nudge.py -0.42 2>&1 | sed 's/^/  /'
sleep 2
echo "  상자 재측정: $(python3 /tmp/job248_audit.py 2>&1 | grep -a '^상자:' | head -1 | cut -c1-50)"
echo "################ 1. 코스 주행 D=1.85 (패딩 0.03, 상자 기준 1.27/-0.15 ±0.25) ################"
bash /tmp/job254_s4run.sh v5 1.85 1.27 -0.15 0.25 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자:|상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|clear except|Goal succeeded|backup|EKF 위반|게이트 실패|★|bag:"
echo -n "  최종 자세: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  정면 벽: $(bash /tmp/job21c_where.sh 2>&1 | grep -a 정면 | grep -aoE '[0-9]+cm') | 후면: $(bash /tmp/job21c_where.sh 2>&1 | grep -a 후면 | grep -aoE '[0-9]+cm')"
