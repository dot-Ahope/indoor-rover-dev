#!/bin/bash
# (PC·WSL) §29 계측판 SLAM 재생(f2tt1 첫 210 s) — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 로버 안 움직임, 도메인 42
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in run_slam_replay.sh slam_replay_feed.py; do sed 's/\r$//' $N/$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/$f; done
printf '#!/bin/bash\nSLAM_WS=/home/jetson/slam_dbg_ws bash /tmp/run_slam_replay.sh T0dbg /tmp/bag_f2tt1 0 210\necho "본 스택 SLAM: $(pgrep -fc lib/slam_toolbox/localization_slam_toolbox_node.*launch_params)"\n' > $N/_rep_dbg.sh
JX_TIMEOUT=600 JX_WHY='SLAM 계측판 재생(10-27 §29, 도메인 42, 로버 안 움직임)' bash $N/run_jn.sh _rep_dbg.sh
mkdir -p $N/slamrep; sshpass -p "$PW" scp $O "jetson@192.168.0.110:/tmp/slamrep/T0dbg.*" $N/slamrep/ && echo 회수
