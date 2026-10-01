#!/bin/bash
# 10-01 §8.33: 저장 지도 전역 정적 층 + 위치 추정(slamloc) prep — stuck 관찰 모드. 확인: /map_nav 발행·static_layer map_topic·전역 plugins
set +u; export STUCK_SHADOW=true
bash /tmp/job731_f2_prep.sh
echo "  static map_topic: $(timeout 15 ros2 param get /global_costmap/global_costmap static_layer.map_topic 2>&1 | tail -1)"
echo "  /map_nav: $(timeout 10 ros2 topic echo --once /map_nav/info 2>/dev/null | grep -aE 'width|height' | tr '\n' ' ')$(timeout 10 ros2 topic info /map_nav 2>&1 | grep -a 'Publisher count')"
echo "  전역 plugins: $(timeout 10 ros2 param get /global_costmap/global_costmap plugins 2>&1 | tail -1) · stuck shadow $(timeout 10 ros2 param get /stuck_monitor shadow_mode 2>&1 | tail -1) · nav_guard $(pgrep -fc nav_guard.py)"
