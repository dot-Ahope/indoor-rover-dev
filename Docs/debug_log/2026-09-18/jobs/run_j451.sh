#!/bin/bash
H=${JETSON_HOST:-192.168.0.101}; NSPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=10"
tr -d '\r' < $NSPS/job451_paramsnap.py > /tmp/job451_paramsnap.py; sshpass -p <PW> scp $O -q /tmp/job451_paramsnap.py jetson@$H:/tmp/ || exit 1
timeout 90 sshpass -p <PW> ssh $O jetson@$H "export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash; T0=\$(date +%s.%N); python3 /tmp/job451_paramsnap.py > /tmp/paramsnap_test.txt 2>&1; echo \"rc \$? 소요 \$(echo \"\$(date +%s.%N) - \$T0\" | bc) s, \$(wc -l < /tmp/paramsnap_test.txt) 줄\"; grep -aE '^/|없음' /tmp/paramsnap_test.txt; grep -aE 'critics|CostCritic|temperature|inflation_radius|cost_scaling|footprint_padding|deck|LIDAR' /tmp/paramsnap_test.txt | head -12"
