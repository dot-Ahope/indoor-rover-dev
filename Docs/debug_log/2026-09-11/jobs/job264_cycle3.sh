#!/bin/bash
# S4 3/3: Nav2 복귀 → heading 정렬 → 재기동(base 유지, 새 원점) → 상자 게이트 → 주행
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 복귀 (Nav2 → 원점) ##########"
python3 /tmp/job207_return.py 0.0 0.0 0 120 2>&1 | tail -2 | sed 's/^/  /'
grep -a "STUCK" /tmp/nav2.log | tail -1 | cut -c1-120 | sed 's/^/  stuck_monitor: /'
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
echo "########## 재기동 (base 유지) ##########"
bash /tmp/job240_clean.sh 15 2>&1 | grep -aE "정리 후|재기동 생략|wheel_odom|gyro bias|active|로버 자세|EKF 위반" | sed 's/^/  /'
echo "########## S4 3/3 ##########"
bash /tmp/job254_s4run.sh $1 1.8 0.87 -0.38 0.12 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | grep -aE "상자 기준선|출발 자세|^결과|^  [①②③④⑤⑥]|조향|detected collision|clear entirely|Goal succeeded|backup failed|EKF 위반|게이트 실패|★"
