#!/bin/bash
# (10-19 §1) 정지 30 s 깊이 bag 시험 기록 — 깊이 · camera_info · tf · tf_static, 깊이 · tf 는 best effort 구독. 저장은 재부팅에도 남는 ~/bags. 로버 안 움직임
B=/home/jetson/bags/depth_test_$(date +%m%d_%H%M%S); mkdir -p /home/jetson/bags
printf '/camera/camera/depth/image_rect_raw:\n  reliability: best_effort\n  history: keep_last\n  depth: 10\n  durability: volatile\n/tf:\n  reliability: best_effort\n  history: keep_last\n  depth: 100\n  durability: volatile\n' > /tmp/qos_depth.yaml
timeout -s INT 30 ros2 bag record -o $B --qos-profile-overrides-path /tmp/qos_depth.yaml /camera/camera/depth/image_rect_raw /camera/camera/depth/camera_info /tf /tf_static > /tmp/rec_depth_test.log 2>&1 &
RP=$!; sleep 12; top -b -n1 | grep -E "ros2|record" | head -3; wait $RP
ros2 bag info $B 2>/dev/null | grep -E "Bag size|Duration|Topic:" | sed 's/Serialization Format: cdr//'
echo "저장 $B"
