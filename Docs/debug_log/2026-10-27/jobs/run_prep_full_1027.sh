#!/bin/bash
# §24 prep 본체를 필터 없이(원인 확인). 로버 안 움직임
NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite > /tmp/prep_full_1027b.txt 2>&1; echo "rc $?"; grep -av "기다리는 것" /tmp/prep_full_1027b.txt | tail -45 | cut -c1-200
