#!/bin/bash
# up_tools — Jetson /tmp 로 도구 전송(실행 안 함). 비밀번호는 run_jn.sh 에서 읽는다. 재부팅 뒤 한 번.
N=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad; H=${JETSON_HOST:-192.168.0.101}
PW=$(grep -o "sshpass -p [^ ]*" $N/run_jn.sh | head -1 | awk '{print $3}'); O="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
rm -rf /tmp/upt; mkdir -p /tmp/upt; for f in prep_fast.sh chk_prep.py prep_patrol.sh anal_rtps_pcap.py; do tr -d '\r' < $N/tools/$f > /tmp/upt/$f; done
for f in job240_clean.sh job386_slamalive.py job440_startclear.py job451_paramsnap.py job453_runmeta.sh job956_gcmchk.py; do [ -f $N/up950/$f ] && cp $N/up950/$f /tmp/upt/ || tr -d '\r' < $N/$f > /tmp/upt/$f; done
sshpass -p $PW scp $O -q /tmp/upt/* jetson@$H:/tmp/ && sshpass -p $PW ssh $O jetson@$H "ls /tmp/*.sh /tmp/*.py 2>/dev/null | wc -l" | sed 's/^/  Jetson \/tmp 스크립트 /'
