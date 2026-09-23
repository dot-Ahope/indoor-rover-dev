#!/bin/bash
# 재부팅 후 /tmp 작업 스크립트 일괄 재전송 (2026-09-10 갱신)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/82ce61d4-f5f7-4a25-b2e7-1279291348a9/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR -o ConnectTimeout=8"
FILES="job20a_boot.sh job21a_reset.sh job21c_where.sh job24a_nav2up.sh job31_shutdown.sh
job43_mon.py job59g_costchk.py job60h_clear.sh job62c_boxdim.py job91_query.py
job118_verify.sh job125_avoid3.py job154_reinit.sh job156_stop.sh job166_nav2only.sh
job168_pre.sh job171_chk.sh job176_who.sh job177_env.sh job179_clean.sh job181_dedup.sh job189_wait.sh job194_bagdrive.sh job201_base.sh job209_static.py job210_cluster.py job213_axis.py job218_approach.py job218_back.py job225_face.py job230_map.py job233_pass.py job231_drive.sh job240_clean.sh job248_audit.py"
cd $SPS || exit 1
for t in 1 2 3; do
  if sshpass -p <PW> scp $OPT -q $(for f in $FILES; do [ -f $f ] && echo $f; done) jetson@${JETSON_HOST:-192.168.0.101}:/tmp/ 2>&1; then
    sshpass -p <PW> ssh $OPT jetson@${JETSON_HOST:-192.168.0.101} \
      'sed -i "s/\r$//" /tmp/job*.sh /tmp/job*.py 2>/dev/null; chmod +x /tmp/job*.sh
       echo "/tmp 스크립트: $(ls /tmp/job* | wc -l)개"
       for f in /tmp/job*.py; do python3 -m py_compile $f || echo "COMPILE FAIL $f"; done
       echo "py 컴파일 OK"'
    exit 0
  fi; sleep 3
done; echo "전송 실패"; exit 1
