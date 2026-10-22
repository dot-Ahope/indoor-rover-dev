#!/bin/bash
# 10-22 §15 nvblox_local.yaml 배포: 통합 거리 1.4 → 2.0 (사용자 결정). 이전 sha 확인(e86434bd8921 = Jetson 판 — 저장소 HEAD 와 머리 주석 3 줄(10-19 정정)만 다름, 값 같음) → /tmp 사본 → 교체 → sha · 설치본 링크 확인. 로버 안 움직임
T=/home/jetson/ros2_ws/src/rover_navigation/config/nvblox_local.yaml; I=/home/jetson/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml
O=$(sha256sum < $T | cut -c1-12); echo "이전 sha $O (기대 e86434bd8921)"; [ "$O" = e86434bd8921 ] || { echo "UP_ABORT: Jetson 판이 저장소 이전 판과 다름 — 덮어쓰지 않음"; exit 3; }; cp $T /tmp/nvblox_local.yaml.pre_1022
# (base64 본문 생략 — 저장소 판과 같음)
echo "새 sha $(sha256sum < $T | cut -c1-12) (기대 bf8abc842b27) · 설치본 $(ls -l $I | awk '{print $1, $NF}') · 같음? $(cmp -s $T $I && echo 예 || echo 아니오) · 값 $(grep -o 'max_integration_distance_m: [0-9.]*' $I)"
