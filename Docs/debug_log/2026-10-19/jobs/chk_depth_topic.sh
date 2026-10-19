#!/bin/bash
# (10-19 §1) 깊이 토픽 실측: QoS · 해상도 · 주기 · 대역폭, bag 저장 형식 플러그인 — 로버 안 움직임
D=/camera/camera/depth/image_rect_raw; I=/camera/camera/depth/camera_info
ros2 topic info -v $D 2>/dev/null | grep -E "Node name|Reliability|Durability|History|Depth|Endpoint type" | head -12
timeout 6 ros2 topic echo --once $I 2>/dev/null | grep -E "^height|^width|frame_id|distortion_model" | head -4
timeout 8 ros2 topic hz $D 2>/dev/null | grep -E "average rate" | tail -1
timeout 8 ros2 topic bw $D 2>/dev/null | grep -E "B/s" | tail -1
timeout 6 ros2 topic echo --once --field encoding $D 2>/dev/null | head -1
ls /opt/ros/humble/lib | grep -i "rosbag2_storage" ; ros2 pkg list 2>/dev/null | grep -i "mcap\|compressed_depth\|image_transport_plugins" | head
