#!/bin/bash
# (PC·WSL) §26 SLAM 재생 도구 전송 후 실행 — 비밀번호는 run_jn.sh 에서 읽음(출력 안 함). 인자: 변형 bag 오프셋 길이 ["SLAM_EXTRA"]
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
for f in run_slam_replay.sh slam_replay_feed.py; do sed 's/\r$//' $N/$f > /tmp/$f; sshpass -p "$PW" scp $O /tmp/$f jetson@192.168.0.110:/tmp/$f; done
printf '#!/bin/bash\nSLAM_EXTRA="%s" bash /tmp/run_slam_replay.sh %s %s %s %s\n' "$5" "$1" "$2" "$3" "$4" > $N/_rep_call.sh
JX_TIMEOUT=900 JX_WHY="SLAM 재생 $1(10-27 §26, 로버 안 움직임, 도메인 42)" bash $N/run_jn.sh _rep_call.sh
