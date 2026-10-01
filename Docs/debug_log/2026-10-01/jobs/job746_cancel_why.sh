#!/bin/bash
# 10-01 §8.11: f2a4 목표 2 CANCELED(12.9 s) — 누가 취소했나(stuck_monitor·nav_guard·러너), 같은 구간 Nav2 로그
grep -aE "STUCK|nav_guard|guard|취소|cancel" /tmp/nav2.log | tail -15 | cut -c1-220
bash /tmp/job732_abort_why.sh 14 2 20 40 | head -30
