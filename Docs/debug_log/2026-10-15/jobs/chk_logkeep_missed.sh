#!/bin/bash
# (10-15 §29.2) /tmp/logkeep 의 지난 nav2 로그마다 제어 주기 놓침 · 목표 성공 수 — 로버 안 움직임
for f in /tmp/logkeep/*_nav2.log; do echo "$(basename $f) 놓침 $(grep -ac 'Control loop missed' $f) · 성공 $(grep -ac 'Goal succeeded' $f) · 실패 $(grep -ac 'Goal failed' $f) · 크기 $(stat -c %s $f)"; done | tail -25
