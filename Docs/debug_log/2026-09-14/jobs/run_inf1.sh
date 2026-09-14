#!/bin/bash
# inflation 0.55/2.0 검증 주행: 재감사(상자 위치·창) 게이트 → job254 (중복·보드·클리어·상자 게이트 → bag 주행 → 로그 분석)
NAME=${1:-inf1}; D=${2:-2.0}; BX=${3:-1.15}; BY=${4:--0.04}; TOL=${5:-0.06}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job254_s4run.sh job231_drive.sh job125_avoid3.py job248_audit.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
echo "=== 사전 감사: 상자 위치와 RPP 창 (BOX_HINT $BX $BY) ==="
timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^상자:|^   (0\.9|1\.[0-4])0 |최소폭'"
W=$(timeout 120 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1 | grep -aE '^   (0\.9|1\.[0-4])0 ' | awk '{print \$3}' | sort -n | head -1")
echo "통로 창(기준1, x 0.9~1.4) 최소폭: $W m"
awk -v w="$W" 'BEGIN{exit !(w+0 >= 0.20)}' || { echo "★ 창 < 0.20 m — 코스트맵이 통로를 닫고 있다. 주행하지 않음 (클리어 후 재감사 필요)"; exit 1; }
echo "=== 주행 $NAME D=$D ==="
timeout 560 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash /tmp/job254_s4run.sh $NAME $D $BX $BY $TOL 2>&1 | tail -70"
