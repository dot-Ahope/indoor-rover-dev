#!/bin/bash
# 10-28 prep — f2tt1 과 같은 구성(prep_patrol: vslam · 프로젝터 끔 · SHM + 재계획 0.01 + planner:=smac). 원문은 /tmp/prep_full_<n>.txt 로 남기고 요약만 출력(10-27 §24). 로버 안 움직임
for f in prep_fast.sh prep_patrol.sh chk_prep.py chk_drive_gate.py; do chmod +x /tmp/$f; echo "$f blob $(git hash-object /tmp/$f | cut -c1-10) CR $(grep -c $'\r' /tmp/$f)"; done
N=${1:-1}; NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite > /tmp/prep_full_$N.txt 2>&1; echo "rc $?"
grep -av "기다리는 것" /tmp/prep_full_$N.txt | grep -a "prep_patrol:\|에이전트\|gyro bias\|위치 추정 검사\|준비까지\|wheel_odom\|server:\|camera:\|filter_node:\|slam_toolbox:\|navigator:\|PREP_\|★\|⏱ +[0-9]* s prep" | cut -c1-200
