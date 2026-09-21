#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10 -o ServerAliveInterval=5"
N=${1:-mp7}
tr -d '\r' < $SPS/job379_navevents.sh > /tmp/job379_navevents.sh; sshpass -p <PW> scp $O -q /tmp/job379_navevents.sh jetson@$H:/tmp/ || exit 1
timeout 200 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job379_navevents.sh $N"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/bag_$N.tgz $SPS/bags/bag_$N.tgz && echo "bag 회수 OK $(stat -c %s $SPS/bags/bag_$N.tgz)"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/drive_$N.log $SPS/drive_${N}_remote.log && echo "drive log OK"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/$N.csv $SPS/$N.csv && echo "csv OK"
# 09-18: 주행 구간 nav2 로그 원본·top 기록도 회수(재부팅 시 /tmp 소실)
sshpass -p <PW> scp $O -q jetson@$H:/tmp/nav2_seg.log $SPS/nav2_${N}.log && echo "nav2 구간 로그 OK $(wc -l < $SPS/nav2_${N}.log) 줄"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/top_$N.log $SPS/top_${N}.log && echo "top 로그 OK"
# 09-18 §17: 재현 메타(실행 파라미터·파일 해시·단계) 회수 — outputs 에 커밋할 것
sshpass -p <PW> scp $O -q jetson@$H:/tmp/bag_$N/run_meta.txt $SPS/meta_${N}.txt && echo "meta OK"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/bag_$N/params.txt $SPS/params_${N}.txt && echo "params OK"
sshpass -p <PW> scp $O -q jetson@$H:/tmp/${N}_refix.csv $SPS/${N}_refix.csv && echo "refix csv OK"   # 09-18 러너 1안: 상자 재고정 기록
sshpass -p <PW> scp $O -q jetson@$H:/tmp/tegra_$N.log $SPS/tegra_${N}.log && echo "tegrastats OK $(wc -l < $SPS/tegra_${N}.log) 줄"   # 09-21 S5
sshpass -p <PW> scp $O -q jetson@$H:/tmp/rss_$N.txt $SPS/rss_${N}.txt && echo "rss OK"
