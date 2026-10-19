#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $SPS/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
JX_TIMEOUT=400 JX_WHY='§23 cuVSLAM 결과 내보내기' bash $SPS/run_jn.sh vso_export.sh
mkdir -p $SPS/vso; for I in true false; do for k in off on; do for s in "" _state; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/home/jetson/workspaces/isaac_ros-dev/vslam/vslam_${I}_vs_${k}${s}.csv $SPS/vso/ 2>/dev/null; done; done; done; ls $SPS/vso
