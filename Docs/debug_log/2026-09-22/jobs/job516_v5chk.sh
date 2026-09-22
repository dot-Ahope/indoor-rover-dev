#!/bin/bash
CN=isaac_ros_dev-aarch64-container; BIN=/opt/ros/humble/lib/nvblox_ros/nvblox_node
echo "prep 후 nvblox pid: $(docker exec $CN bash -c "pgrep -f '^$BIN' || true" | tr '\n' ' ') | 래퍼: $(pgrep -f 'bash .*nvblox_up.sh' | tr '\n' ' ')"
echo "래퍼 로그 꼬리: $(tail -4 /tmp/nvblox_node_up.log 2>/dev/null | sed 's/.*\[nvblox_up\] //' | cut -c1-90 | tr '\n' '|')"
echo "nav2.log 의 nvblox_up 줄: $(grep -a 'nvblox_up\]' /tmp/nav2.log | tail -2 | sed 's/.*\[nvblox_up\] //' | cut -c1-90 | tr '\n' '|')"
echo "활성 yaml: $(head -1 /tmp/nav2_params_active.yaml | cut -c1-80) | 배터리·로드: $(cut -d' ' -f1-3 /proc/loadavg)"
echo "job240 정리 로그(정리 전/후): $(grep -aE '정리 (전|후)' /tmp/nav2.log /tmp/sensors.log 2>/dev/null | head -2 | tr '\n' '|')"
