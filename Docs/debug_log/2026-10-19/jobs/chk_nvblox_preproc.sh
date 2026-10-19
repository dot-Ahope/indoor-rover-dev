#!/bin/bash
# (10-19 §7) nvblox 깊이 전처리 관련 파라미터 이름 · 기본값(컨테이너 헤더 · 실행 로그) — 로버 안 움직임
CN=isaac_ros_dev-aarch64-container
docker exec $CN bash -c "grep -rhoE '(depth_preprocessing[a-z_]*|do_depth_preprocessing)[^;]{0,60}' /opt/ros/humble/include/nvblox* /opt/ros/humble/share/nvblox* 2>/dev/null | sort -u | head -12"
grep -aoE "depth_preprocessing[a-z_]*[^,]{0,20}" /tmp/nvblox_replay_f2x1_base.log | sort -u | head
