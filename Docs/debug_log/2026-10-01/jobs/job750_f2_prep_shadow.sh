#!/bin/bash
# 10-01 §8.12: F2 순회 prep — stuck_monitor 관찰 모드(사용자 결정, §8.11 오판). 나머지는 job731 과 같음
export STUCK_SHADOW=true
bash /tmp/job731_f2_prep.sh
echo "  stuck_monitor shadow_mode: $(timeout 15 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1) · nav_guard $(pgrep -fc nav_guard.py)"
