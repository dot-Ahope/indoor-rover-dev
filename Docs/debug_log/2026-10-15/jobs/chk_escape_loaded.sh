#!/bin/bash
# (10-15 §26) MonotoneEscape 가 behavior_server 에 올라왔는지 · BT 가 새 xml 을 읽었는지 — 로버 안 움직임
grep -a "monotone_escape\|MonotoneEscape\|Failed to create\|PluginlibFactory\|error" /tmp/nav2.log | grep -av "fail to compute" | tail -12
echo "--- 액션 서버"; timeout 15 ros2 action list 2>/dev/null | grep -E "monotone|backup"
echo "--- 파라미터"; timeout 15 ros2 param get /behavior_server monotone_escape.target_clearance 2>&1 | tail -1
echo "--- BT xml 의 server_name"; grep -c 'server_name="monotone_escape"' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml
