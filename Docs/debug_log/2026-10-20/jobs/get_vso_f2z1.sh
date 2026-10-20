#!/bin/bash
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $SPS/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
mkdir -p $SPS/vso_f2z1
for I in true false; do for s in "" _state; do sshpass -p "$PW" scp $O jetson@192.168.0.110:/home/jetson/workspaces/isaac_ros-dev/vslam/vslam_f2z1_${I}_vs_off${s}.csv $SPS/vso_f2z1/vslam_${I}_vs_off${s}.csv; done; done
for I in true false; do sshpass -p "$PW" ssh $O jetson@192.168.0.110 "grep -av '^\[INFO\]' /home/jetson/workspaces/isaac_ros-dev/vslam/run_f2z1_$I.out"; done
ls $SPS/vso_f2z1
