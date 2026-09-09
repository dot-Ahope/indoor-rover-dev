#!/bin/bash
# 재부팅 후 /tmp 작업 스크립트 일괄 재전송
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
FILES="job20a_boot.sh job21a_reset.sh job21c_where.sh job24a_nav2up.sh job31_shutdown.sh
job43_mon.py job53_bench.py job56_osc.py job59g_costchk.py job60h_clear.sh job62c_boxdim.py
job63_planquery.py job64e_map.py job71_watchbox.py job73_probe.py job74_layers.sh
job75_forward.py job78_killnav.sh job88_pad.sh job90_infl.sh"
cd $SPS || exit 1
for t in 1 2 3; do
  if sshpass -p <PW> scp $OPT -q $FILES jetson@192.168.0.101:/tmp/ 2>&1; then
    sshpass -p <PW> ssh $OPT jetson@192.168.0.101 \
      'chmod +x /tmp/job*.sh; echo "/tmp 스크립트: $(ls /tmp/job* | wc -l)개"; for f in /tmp/job*.py; do python3 -m py_compile $f || echo "COMPILE FAIL $f"; done; echo "py 컴파일 OK"'
    exit 0
  fi; sleep 3
done; echo "전송 실패"; exit 1
