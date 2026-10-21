#!/bin/bash
# nav2.log 사건을 0.01 s 시각으로 — 인자: 시작HH:MM:SS 끝HH:MM:SS
A=$1; B=$2
grep -av "Message Filter\|tick rate" /tmp/nav2.log | grep -aE "\[(controller_server|planner_server|bt_navigator|behavior_server|smoother_server|velocity_smoother|bt_navigator_navigate_to_pose_rclcpp_node)\]" | while read -r l; do
  t=$(echo "$l" | grep -o '\[17[0-9]*\.[0-9]*' | head -1 | tr -d '['); [ -z "$t" ] && continue
  s=$(date -d @${t%.*} +%T); [[ "$s" < "$A" || "$s" > "$B" ]] && continue
  n=$(echo "$l" | grep -o '\] \[[a-z_]*\]:' | head -1 | tr -d '[]: '); echo "$s.${t#*.}" | cut -c1-11 | tr '\n' ' '; echo "$n ${l#*]: }" | cut -c1-170
done
