#!/bin/bash
# 09-29 §13.1: stuck_monitor(자이로 우선) 빌드·자체시험 → 설치본 로직으로 20 bag 오판 재확인(OLD=설치본 판정식 재현 경로 아님, 참고)
set +u; cd ~/ros2_ws; colcon build --packages-select rover_bringup 2>&1 | tail -1
source install/setup.bash
grep -c "자이로 우선\|2026-09-29 변경" install/rover_bringup/lib/rover_bringup/stuck_monitor.py
python3 install/rover_bringup/lib/rover_bringup/stuck_monitor.py --selftest 2>&1 | tail -4
