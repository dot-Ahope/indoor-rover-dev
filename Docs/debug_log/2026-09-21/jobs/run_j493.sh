#!/bin/bash
# §10.5: 층 결함(round→floor) 수정·재빌드 → 같은 배치에서 STVL(stvl2) / 수정 nvblox 층(nvfix) 코스트맵·슬라이스 JSON 재캡처 → STVL 복귀·nvblox 정지 → JSON·감사 출력 회수
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
for f in job493_fixfloor.sh job489_gridcmp.py job488_layer_ab.sh job473_nvblox_run.sh; do tr -d '\r' < $NSPS/$f > /tmp/$f; sshpass -p <PW> scp $O -q /tmp/$f jetson@$H:/tmp/ || exit 1; done
timeout 840 sshpass -p <PW> ssh $O jetson@$H "export TERM=xterm FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo '## 수정·재빌드'; bash /tmp/job493_fixfloor.sh 2>&1
echo '## STVL 모드 코스트맵(stvl2)'; timeout 10 ros2 service call /local_costmap/clear_entirely_local_costmap nav2_msgs/srv/ClearEntireCostmap '{}' >/dev/null 2>&1; sleep 12; python3 /tmp/job489_gridcmp.py stvl2 0 2>&1 | grep -aE '^====|LETHAL 셀'
echo '## nvblox 모드(수정 층, nvfix)'; bash /tmp/job473_nvblox_run.sh start >/dev/null 2>&1; bash /tmp/job488_layer_ab.sh nvblox 1.153 -0.079 2>&1 | tee /tmp/j493_ab_nvfix.txt | grep -aE '실행값|오류|최소폭|상자 셀|근거|CPU'; sleep 5; python3 /tmp/job489_gridcmp.py nvfix 1 2>&1 | grep -aE '^====|LETHAL 셀'
echo '## STVL 복귀'; QUICK=1 bash /tmp/job488_layer_ab.sh stvl 1.153 -0.079 2>&1 | grep -aE '실행값|오류'; bash /tmp/job473_nvblox_run.sh stop >/dev/null 2>&1; ls -la /tmp/grid_stvl2_*.json /tmp/grid_nvfix_*.json | awk '{print \$5, \$9}'"
for f in grid_stvl2_costmap.json grid_nvfix_costmap.json grid_nvfix_slice.json j493_ab_nvfix.txt; do sshpass -p <PW> scp $O -q jetson@$H:/tmp/$f $NSPS/$f && echo "회수 $f $(stat -c %s $NSPS/$f) B"; done
