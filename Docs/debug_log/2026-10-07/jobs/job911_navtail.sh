#!/bin/bash
# 10-07 §2.4: 주행 중 관찰(사용자: 전진하며 이상하게 움직임) — 로그만 읽음(DDS 참여자 만들지 않음)
date +%T; tail -4 /tmp/f0_f2c2.log | cut -c1-200
grep -aE "PathBlocked|nav_guard|Fail|fail|Abort|abort|Optimizer|collision|clear|Received a goal|stuck" /tmp/nav2.log | tail -14 | sed -E 's/^\[[a-z_.]+-[0-9]+\] //' | cut -c1-190
tail -3 /tmp/f2c2.csv 2>/dev/null | cut -c1-200
