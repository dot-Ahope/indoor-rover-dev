#!/bin/bash
# N6-1 nvblox yaml 재배포 → Nav2(nvblox) 재기동(래퍼가 새 yaml 로 노드 재시작) → 목표 부근 탐침(job522)·게이트 J·K·L·목표 여유(job377 2.0 0.0). 인자: BX BY [확인할 yaml 문자열]
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
BX=${1:-1.145}; BY=${2:--0.068}; CHK=${3:-esdf_slice_min_height: 0.12}
tr -d '\r' < $NSPS/n61_src/nvblox_local.yaml > /tmp/nvblox_local.yaml; tr -d '\r' < $NSPS/job522_goalprobe.py > /tmp/job522_goalprobe.py
sshpass -p <PW> scp $O -q /tmp/nvblox_local.yaml jetson@$H:~/ros2_ws/src/rover_navigation/config/ && sshpass -p <PW> scp $O -q /tmp/job522_goalprobe.py jetson@$H:/tmp/ || exit 1
cat > /tmp/job523_remote.sh <<EOF
export TERM=xterm FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
cd ~/ros2_ws && colcon build --symlink-install --packages-select rover_navigation 2>&1 | grep -aE 'Finished|Failed'; source ~/ros2_ws/install/setup.bash
echo "설치 yaml 확인: \$(grep -c '$CHK' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml)"
echo '## Nav2(nvblox) 재기동'; QUICK=1 bash /tmp/job488_layer_ab.sh nvblox $BX $BY 2>&1 | grep -aE '실행값|오류'; sleep 5
echo "  실효값: \$(docker exec -u admin isaac_ros_dev-aarch64-container bash -lc 'export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; for p in esdf_slice_min_height esdf_slice_height projective_integrator_max_integration_distance_m tsdf_decay_factor; do echo -n \"\$p=\"; timeout 12 ros2 param get /nvblox_node static_mapper.\$p 2>&1 | tail -1 | sed \"s/Double value is: //\"; done' | tr '\n' ' ')"
timeout 10 ros2 service call /global_costmap/clear_entirely_global_costmap nav2_msgs/srv/ClearEntireCostmap '{}' >/dev/null 2>&1; sleep 25
echo '## 목표 부근 탐침'; python3 /tmp/job522_goalprobe.py 2>&1 | grep -av '^\['
echo '## 게이트 J·K·L'; bash /tmp/job505_modeN_gate.sh node $BX $BY 2>&1 | grep -aE '^[JKL] |=='
echo '## 목표 여유(job377 2.0 0.0)'; timeout 60 python3 /tmp/job377_goalclear.py 2.0 0.0 2>&1 | grep -av '^\[' | tail -2
EOF
sshpass -p <PW> scp $O -q /tmp/job523_remote.sh jetson@$H:/tmp/ || exit 1
timeout 400 sshpass -p <PW> ssh $O jetson@$H "bash /tmp/job523_remote.sh"
