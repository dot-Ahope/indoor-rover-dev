#!/bin/bash
# 10-26 §14 저장소 nav2_params.yaml(28 · 5 채택판)을 Jetson src · 설치본에 — 로버 안 움직임. 실행본 = 이 머리 + 스크래치패드가 붙인 base64(/tmp/up_nav2_params.yaml)
R=~/ros2_ws/src/rover_navigation/config/nav2_params.yaml; I=~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml
echo "이전 src $(sha256sum < $R | cut -c1-12) · 설치본 $(sha256sum < $I | cut -c1-12) $( [ -L $I ] && echo 링크 || echo 일반파일)"
cp /tmp/up_nav2_params.yaml $R; [ -L $I ] || cp $R $I
echo "새 src $(sha256sum < $R | cut -c1-12) · 설치본 $(sha256sum < $I | cut -c1-12)"; grep -o "PathAlignCritic: {enabled: true, cost_power: 1, cost_weight: [0-9.]*\|PathFollowCritic: {enabled: true, cost_power: 1, cost_weight: [0-9.]*" $I
