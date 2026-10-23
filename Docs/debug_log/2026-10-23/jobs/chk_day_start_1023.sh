#!/bin/bash
# 10-23 하루 시작 점검(prep 무출력 뒤): 신원 · 가동 시간 · /tmp prep 파일 · 스택 프로세스 · 배터리 — 로버 안 움직임
hostname; uptime -p; date
ls -la /tmp/prep_fast.sh /tmp/prep_patrol.sh /tmp/prep_patrol_pad.sh /tmp/pad_relief.py /tmp/chk_prep.py 2>&1 | awk '{print $1, $5, $NF}'
echo "프로세스: camera $(pgrep -fc realsense2_camera) · nav2 controller $(pgrep -fc controller_server) · slam $(pgrep -fc slam_toolbox) · agent $(pgrep -fc micro_ros_agent)"
docker ps --format '{{.Names}} {{.Status}}' | head
df -h / | tail -1
