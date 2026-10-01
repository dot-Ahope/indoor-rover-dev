#!/bin/bash
grep -n "map_topic" /tmp/nav2_params_active.yaml
echo "/map_nav 구독: $(timeout 15 ros2 topic info /map_nav 2>&1 | grep -a "Subscription count") | /map 구독: $(timeout 15 ros2 topic info /map 2>&1 | grep -a "Subscription count")"
echo "static_layer.map_topic = $(timeout 20 ros2 param get /global_costmap/global_costmap static_layer.map_topic 2>&1 | tail -1)"
grep -ai "static_layer\|map_nav\|Subscribing" /tmp/nav2.log | head -5 | cut -c1-200
