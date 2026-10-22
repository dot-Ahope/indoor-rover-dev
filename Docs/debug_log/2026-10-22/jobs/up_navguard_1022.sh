#!/bin/bash
# 10-22 §18 nav_guard.py 배포: 피드백 기록 0.2 s 간격 · 앞에서부터 버림(CPU 25 % 대책). 이전 sha 6b7381c5d260 확인 → /tmp 사본 → 교체(실행 권한 유지). 다음 prep 부터 적용. 로버 안 움직임
T=/home/jetson/ros2_ws/src/rover_bringup/scripts/nav_guard.py
O=$(sha256sum < $T | cut -c1-12); echo "이전 sha $O (기대 6b7381c5d260)"; [ "$O" = 6b7381c5d260 ] || { echo UP_ABORT; exit 3; }; cp -p $T /tmp/nav_guard.py.pre_1022
# (base64 본문 생략 — 저장소 판과 같음)
chmod +x $T; echo "새 sha $(sha256sum < $T | cut -c1-12) (기대 a23e0b3427ee) · $(ls -l $T | awk '{print $1}')"; python3 -m py_compile $T && echo 'Jetson 문법 OK'
