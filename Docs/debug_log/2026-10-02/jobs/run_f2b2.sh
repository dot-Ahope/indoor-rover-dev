#!/bin/bash
# 10-02 §6.2: 목표 문자열을 파일 안에 적어 wsl 인자 분리 문제를 피함(f2b1 실수). 인자: NAME GOALS_KEY(rest|full)
SPS=/mnt/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad
FULL="2.25,-1.6,p;-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,p;1.6,-5.55,p;-1.6,-5.5,p;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"
REST="-1.6,-2.0,p;-1.65,-3.7,p;-1.6,-5.5,p;1.6,-5.55,p;-1.6,-5.5,p;-1.65,-3.7,p;-1.6,-2.1,p;5.5,-2.2,p;0,0,p"
case "$2" in rest) G="$REST" ;; full) G="$FULL" ;; *) echo "rest|full"; exit 1 ;; esac
export BAG_PROFILE=nvblox G2_SKIP=${G2_SKIP:-0} GOAL_FRAME=map STAGE=F2b NOTE="$3" GIT_HEAD="$4"
bash $SPS/run_f0.sh "$1" "$G" 0.07
