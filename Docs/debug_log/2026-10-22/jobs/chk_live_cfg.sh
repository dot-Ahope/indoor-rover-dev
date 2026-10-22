#!/bin/bash
# 10-22 §15 주행 전 실행 중 설정 확인: 카메라 프리셋 · 실시간 nvblox 통합 거리 — 로버 안 움직임(DDS 참여자 생성 — 주행 30 s 전엔 쓰지 않음)
source /opt/ros/humble/setup.bash
echo "visual_preset: $(timeout 8 ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
docker exec isaac_ros_dev-aarch64-container bash -lc "ls -t /tmp/*.log 2>/dev/null | head -3; grep -ah 'projective_integrator_max_integration_distance_m' \$(ls -t /tmp/nvblox*.log 2>/dev/null | grep -v replay | head -1) | head -1"
