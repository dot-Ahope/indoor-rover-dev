#!/bin/bash
set +u
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "########## 열화 상태 스냅샷 (재기동 전) ##########"
echo "  load: $(cut -d' ' -f1-3 /proc/loadavg) | 센서 기동 후 경과: $(( $(date +%s) - $(stat -c %Y /tmp/sensors.log) ))s 이후 갱신"
top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -9 | awk 'NR>1{printf "  %-24s %6s%%  RSS %sK\n", $12, $9, $6}'
echo "  slam 그래프: $(grep -ac 'Processed.*scans\|loop closure\|Loop closure' /tmp/slam.log)건 로그 | /map 크기: $(timeout 6 ros2 topic echo /map --once --field info 2>/dev/null | grep -aE 'width|height' | tr '\n' ' ')"
echo "  EKF 위반 누적 $(grep -ac 'Failed to meet update rate' /tmp/sensors.log) | slam 폐기 누적 $(grep -ac 'Message Filter dropping' /tmp/slam.log)"
echo "  controller 주기 경고: $(grep -ac 'Control loop missed its desired rate' /tmp/nav2.log)건 | TF 지연 경고: $(grep -aci 'transform.*timed out\|extrapolation' /tmp/nav2.log)건"
echo
echo "########## 출발 위치 복귀 (face 0 → back 0.21) ##########"
python3 /tmp/job225_face.py 0 2.0 2>&1 | tail -1 | sed 's/^/  /'
python3 /tmp/job218_back.py 0.21 2>&1 | tail -1 | sed 's/^/  /'
echo
echo "########## 재기동 (base 유지) ##########"
bash /tmp/job240_clean.sh 15 2>&1 | grep -avE "^\s+\[docker|create_|ProxyClient" | grep -aE "정리 후|base 계층|재기동 생략|wheel_odom|gyro bias|map->odom|active|decay_model|ExceptRegion|ZUPT|로버 자세|EKF 위반|^상자:|^   \[|최소폭" | sed 's/^/  /'
echo
echo "########## S4 2/3 재시도 ##########"
bash /tmp/job254_s4run.sh $1 1.8 0.87 -0.38 0.12 2>&1 | grep -avE "^ *[0-9]+\.[0-9] [+-]" | tail -34
