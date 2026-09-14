#!/bin/bash
# inflation 0.55/2.0 검증 주행: 재감사(상자 위치·창) 게이트 → job254 (중복·보드·클리어·상자 게이트 → bag 주행 → 로그 분석)
NAME=${1:-inf1}; D=${2:-2.0}; BX=${3:-1.15}; BY=${4:--0.04}; TOL=${5:-0.06}
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@192.168.0.101
for f in job254_s4run.sh job231_drive.sh job125_avoid3.py job248_audit.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p <PW> scp $OPT -q /tmp/$f $J:/tmp/$f || exit 1; done
echo "=== 사전 감사: 상자 위치와 RPP 창 (BOX_HINT $BX $BY) ==="
A=$(timeout 150 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; BOX_HINT='$BX $BY' python3 /tmp/job248_audit.py 2>&1")
echo "$A" | grep -aE '^상자:|^   (0\.9|1\.[0-4])0 |최소폭'
W=$(echo "$A" | grep -aE '^   (0\.9|1\.[0-4])0 ' | awk '{print $3}' | sort -n | head -1)
echo "통로 창(기준1, x 0.9~1.4) 최소폭: ${W:-없음} m"
[ -n "$W" ] || { echo "★ 감사 출력 없음(ssh/감사 실패) — 주행하지 않음"; exit 1; }
# 2026-09-14 §2.16: 기준1 폭은 상자 inscribed 띠를 못 거른다 → 창 = 기준1 좌측 경계(x 1.0~1.3 최소) − (상자 코스트맵 최대 y + 0.195)
LB=$(echo "$A" | grep -aE '^   1\.[0-3]0 ' | grep -aoE '\[[-+0-9.]+~[-+0-9.]+\]' | head -4 | tr -d '[]' | cut -d'~' -f2 | sort -n | head -1)
tr -d '' < $SPS/job315_boxcells.py > /tmp/job315.py; sshpass -p <PW> scp $OPT -q /tmp/job315.py $J:/tmp/job315_boxcells.py
BM=$(timeout 60 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; python3 /tmp/job315_boxcells.py $BX $BY 2>/dev/null | tail -1")
W2=$(awk -v lb="$LB" -v bm="$BM" 'BEGIN{ if (bm=="nan"||bm=="") print "nan"; else printf "%.3f", lb - (bm + 0.195) }')
echo "창(기준1 좌측 경계 $LB − (상자 셀 최대 y $BM + 0.195)) = $W2 m  (≥0.20 필요)"
awk -v w="$W2" 'BEGIN{exit !(w+0 >= 0.20)}' || { echo "★ 창 < 0.20 m — 이 배치는 로버 중심 창이 부족하다. 상자를 오른쪽으로 옮기거나 재감사. 주행하지 않음"; exit 1; }
echo "=== 주행 $NAME D=$D ==="
timeout 560 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash; bash /tmp/job254_s4run.sh $NAME $D $BX $BY $TOL 2>&1 | tail -70"
