#!/bin/bash
# 10-02 §6: prep 뒤 Nav2 상태·BT 플러그인·/map_nav 크기 확인
for n in controller_server planner_server bt_navigator behavior_server smoother_server velocity_smoother; do printf "  /%-18s %s\n" $n "$(timeout 15 ros2 lifecycle get /$n 2>&1 | tail -1)"; done
echo "  plugin_lib_names: $(timeout 15 ros2 param get /bt_navigator plugin_lib_names 2>&1 | grep -o '_bt_node' | wc -l) 개 · rover 노드 $(timeout 15 ros2 param get /bt_navigator plugin_lib_names 2>&1 | grep -c rover_path_blocked)"
echo "  /map_nav: $(timeout 10 ros2 topic echo --once /map_nav/info 2>/dev/null | grep -aE 'width|height' | tr '\n' ' ')"
grep -aiE "Failed to load|Error loading|exception|PathBlocked" /tmp/nav2.log | head -5
echo "  load $(cut -d' ' -f1-3 /proc/loadavg)"
