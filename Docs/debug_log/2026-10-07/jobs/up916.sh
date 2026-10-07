#!/bin/bash
# 10-07 §4: 재부팅 뒤 재생 준비(호스트 인자) — bag_step1·합성·주행 재생 스크립트·게이트 소스 업로드, 빌드
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"; J=jetson@${JETSON_HOST:-172.30.1.8}
mkdir -p /tmp/u901; for f in occ_scan.py occ_rec.py occ_run.sh job876_g4.sh rp_run.sh job915_rp.sh; do tr -d '\r' < $SPS/$f > /tmp/u901/$f; done
for f in rf2o_gate.py ekf.launch.py; do tr -d '\r' < $SPS/r3src/$f > /tmp/u901/r3_$f; done
sshpass -p <PW> scp $OPT -q /tmp/u901/occ_* /tmp/u901/job876_g4.sh /tmp/u901/rp_*.sh /tmp/u901/job915_rp.sh $J:/tmp/ || exit 1
sshpass -p <PW> scp $OPT -q /tmp/u901/r3_rf2o_gate.py $J:/home/jetson/ros2_ws/src/rover_bringup/scripts/rf2o_gate.py || exit 1
sshpass -p <PW> scp $OPT -q /tmp/u901/r3_ekf.launch.py $J:/home/jetson/ros2_ws/src/rover_bringup/launch/ekf.launch.py || exit 1
echo "bag 전송 시작 $(date +%T)"; sshpass -p <PW> scp $OPT -q $SPS/up/bag_step1.tgz $J:/tmp/ || exit 1; echo "bag 전송 끝 $(date +%T)"
sshpass -p <PW> ssh $OPT $J "cd /tmp && tar xzf bag_step1.tgz && ls /tmp/bag_step1 | head; cd ~/ros2_ws && source /opt/ros/humble/setup.bash && colcon build --packages-select rover_bringup 2>&1 | tail -1; sha256sum install/rover_bringup/lib/rover_bringup/rf2o_gate.py | cut -c1-12"
