#!/bin/bash
# 10-07 §2: 재부팅 뒤 보조 스크립트 재전송(실행 안 함)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
OPT="-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
mkdir -p /tmp/up904; for f in job240_clean.sh job248_audit.py job386_slamalive.py job440_startclear.py job453_runmeta.sh job550_f0run.py job551_f0drive.sh job613_pathyaw.py job685_f1_teleop.sh job697_restore_chk.py job726_prep_map.sh job731_f2_prep.sh job760_nav2_restart.sh job780_prep_navmap.sh job852_prep_rf2o.sh job903_prep_rf2o_g4.sh; do tr -d "\r" < $SPS/$f > /tmp/up904/$f; done
sshpass -p <PW> scp $OPT -q /tmp/up904/* jetson@192.168.0.101:/tmp/ && sshpass -p <PW> ssh $OPT jetson@192.168.0.101 "ls /tmp/job*.sh /tmp/job*.py | wc -l; grep -c office_v3 /tmp/job726_prep_map.sh /tmp/job731_f2_prep.sh /tmp/job760_nav2_restart.sh"
