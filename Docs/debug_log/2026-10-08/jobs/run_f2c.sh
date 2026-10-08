#!/bin/bash
# 10-07 §2: rf2o + G4 켠 F2 순회(10-02 f2b 와 같은 10 목표). 목표 문자열은 래퍼 안에(10-02 §6.2 wsl 인자 분리 실수). 인자: NAME NOTE GIT_HEAD [rest5]
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
REST5="1.6,-5.55,p;-1.6,-5.5,p;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"   # 10-07 §2.4: 목표 5~10(f2c1 목표 4 취소 뒤 이어 가기)
REST5F="1.6,-5.55,p;-1.6,-5.5,f;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"   # 10-07 §7: 남서는 위치만(f)
FULLF="2.25,-1.6,p;-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,f;1.6,-5.55,p;-1.6,-5.5,f;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"   # 10-08 §3: 남서 두 번 모두 위치만(f)
FULL="2.25,-1.6,p;-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,p;1.6,-5.55,p;-1.6,-5.5,p;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"
export LONG_REC=${LONG_REC:-1} JETSON_HOST=${JETSON_HOST:-172.30.1.8} BAG_PROFILE=nvblox G2_SKIP=${G2_SKIP:-0} GOAL_FRAME=map STAGE=${STAGE:-F2c} NOTE="$2" GIT_HEAD="$3" EXTRA_TOPICS="/odometry/ekf_a /odom_rf2o /odom_rf2o/gated"
G="$FULL"; [ "${4:-}" = rest5 ] && G="$REST5"; [ "${4:-}" = rest5f ] && G="$REST5F"; [ "${4:-}" = fullf ] && G="$FULLF"
bash $SPS/run_f0.sh "$1" "$G" 0.07
