#!/bin/bash
# 10-22 §18 nav_guard 설치 형태 확인(설치본이 src 링크인지) · Jetson src 판 sha — 로버 안 움직임
for f in /home/jetson/ros2_ws/install/rover_bringup/lib/rover_bringup/nav_guard.py /home/jetson/ros2_ws/src/rover_bringup/scripts/nav_guard.py; do ls -l $f | awk '{print $1, $9, $10, $11}'; sha256sum < $f | cut -c1-12; done
