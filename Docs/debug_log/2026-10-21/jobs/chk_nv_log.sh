#!/bin/bash
# nv1 0 Hz 원인: 기동 로그 · 오류 앞뒤 · 환경
for m in flash off; do echo "======== $m ($(wc -l < /tmp/nv_static_$m.log) 줄)"; grep -av "re-enable\|^\s*$" /tmp/nv_static_$m.log | sed 's/\x1b\[[0-9;]*m//g' | cut -c1-230 | head -70; done
echo "======== 환경"; docker exec -u admin isaac_rs_test bash -c 'env | grep -E "ROS|RMW|FASTRTPS|CYCLONE" | sort'
echo "--- 호스트 기본 환경"; grep -hE "ROS_DOMAIN|RMW|FASTRTPS|LOCALHOST" ~/.bashrc 2>/dev/null
echo "--- 옛 컨테이너 env"; docker exec -u admin isaac_ros_dev-aarch64-container bash -c 'env | grep -E "ROS|RMW|FASTRTPS" | sort'
ls -l /dev/shm | head; rs-enumerate-devices -s 2>/dev/null | head -4
