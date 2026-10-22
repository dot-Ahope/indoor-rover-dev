#!/bin/bash
# 10-22 §10 camera.launch.py 배포: depth_preset 기본 -1 → 3 (사용자 결정). 이전 판 sha 확인 → /tmp 사본 → 교체 → sha 확인. 로버 안 움직임
T=/home/jetson/ros2_ws/src/rover_bringup/launch/camera.launch.py
echo "이전 sha $(sha256sum $T | cut -c1-12) (기대 95fe7b16a70f)"; cp $T /tmp/camera.launch.py.pre_1022
# (base64 본문 생략 — 저장소 판과 같음)
echo "새 sha $(sha256sum $T | cut -c1-12) (기대 d5525810708d)"; ls -l /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/launch/camera.launch.py | awk '{print $NF, $(NF-1), $(NF-2)}'
