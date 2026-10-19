#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $SPS/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -q"
for f in mk_vslam_bag.py vslam_offline.launch.py vslam_run_in.sh export_vslam.py; do tr -d '\r' < $SPS/$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/ || exit 1; done
JX_TIMEOUT=2400 JX_WHY='§23 오프라인 cuVSLAM 켬/끔 비교(스택 내림, 로버 정지)' bash $SPS/run_jn.sh run_vslam_offline.sh
