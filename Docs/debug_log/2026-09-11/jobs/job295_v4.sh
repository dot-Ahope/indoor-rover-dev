#!/bin/bash
# v2: 목표를 벽 앞 창 안에 둔다. 상자 뒷면(map≈1.51)+0.45 ≤ 목표 ≤ 벽 inscribed 직전(map≈2.04) → 현재 x 0.139 기준 D=1.85.
# dx 자동 보정은 쓰지 않는다(전진시키면 목표가 다시 벽으로 간다). heading 을 0 으로 맞춘 뒤 곧장 게이트→주행.
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "################ 0. face 0 ################"
python3 /tmp/job225_face.py 0 1.5 2>&1 | tail -1 | sed 's/^/  /'
P=$(timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '); echo "  자세: $P"
echo "################ 1. 코스 주행 D=1.85 패딩 0.03 ################"
bash /tmp/job254_s4run.sh v4 1.85 1.27 -0.15 0.25 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자:|상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|clear except|Goal succeeded|backup|EKF 위반|게이트 실패|★|bag:"
echo "################ 2. 복귀 → (0, 0, 180°) ################"
bash /tmp/job288_return_bag.sh v4_ret 0.0 0.0 180 2>&1
echo "################ 3. face 0 ################"
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
echo -n "  최종: "; timeout 6 ros2 run tf2_ros tf2_echo map base_link 2>&1 | grep -aE "Translation|RPY" | head -2 | tr '\n' ' '; echo
echo "  EKF 위반 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log)회 | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)회 | load $(cut -d' ' -f1-3 /proc/loadavg)"
