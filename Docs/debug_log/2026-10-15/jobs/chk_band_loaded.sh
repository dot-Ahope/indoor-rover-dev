#!/bin/bash
# (10-15 §29) ClearanceBandCritic 적재 · 오류 · 제어 주기 경고 — 로버 안 움직임
grep -a "ClearanceBandCritic\|Failed to create\|critic\|Control loop missed" /tmp/nav2.log | grep -v "^$" | tail -n 15 | cut -c1-240
echo "missed 경고 수: $(grep -ac 'Control loop missed' /tmp/nav2.log)"
