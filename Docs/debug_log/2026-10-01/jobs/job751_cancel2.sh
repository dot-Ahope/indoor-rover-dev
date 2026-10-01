#!/bin/bash
# 10-01 §8.13: f2a5 목표 2 CANCELED(34.3 s) — 누가 취소했나
grep -aE "STUCK|nav_guard|cancel|Cancel|취소|한도|trip" /tmp/nav2.log | tail -14 | cut -c1-230
bash /tmp/job732_abort_why.sh 14 19 0 50 | head -30
