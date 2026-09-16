#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=15"
J=jetson@${JETSON_HOST:-192.168.0.101}
tr -d '\r' < $SPS/job333_voxstat.py > /tmp/job333_voxstat.py; sshpass -p <PW> scp $OPT -q /tmp/job333_voxstat.py $J:/tmp/ || exit 1
timeout 240 sshpass -p <PW> ssh $OPT $J "source /opt/ros/humble/setup.bash; echo '=== STVL voxel_min_points 지원 여부 ==='; SO=\$(find /opt/ros/humble -name 'libspatio_temporal_voxel_layer*.so*' 2>/dev/null | head -1); echo \"so: \$SO\"; strings \$SO 2>/dev/null | grep -aiE 'voxel_min_points|^filter\$|clear_after_reading|mark_threshold' | sort -u | head; ros2 param list /local_costmap/local_costmap 2>/dev/null | grep -aiE 'depth_mark\.(filter|voxel_min|min_obs|mark)' ; echo '=== job333 (필터 출력, odom 월드 복셀) ==='; python3 /tmp/job333_voxstat.py $1 $2 $3 $4 ${5:-40} 2>&1 | grep -av '^\['"
