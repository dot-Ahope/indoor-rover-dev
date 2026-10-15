#!/bin/bash
# (10-15 §26) Nav2 humble behavior 플러그인 구조 확인 — 헤더 읽기만, 로버 안 움직임
I=/opt/ros/humble/include
echo "=== 판"; dpkg -l | grep -E "ros-humble-nav2-behaviors |ros-humble-nav2-behavior-tree |ros-humble-nav2-costmap-2d " | awk '{print $2, $3}'
for f in $I/nav2_behaviors/timed_behavior.hpp $I/nav2_behaviors/plugins/drive_on_heading.hpp $I/nav2_behaviors/plugins/back_up.hpp; do echo "=== $f"; [ -f $f ] && grep -v '^ *//' $f | grep -v '^ *$' | head -230; done
echo "=== bt back_up action"; grep -n "server_name\|providedPorts\|backup_dist\|backup_speed\|time_allowance" $I/nav2_behavior_tree/plugins/action/back_up_action.hpp $I/nav2_behavior_tree/bt_action_node.hpp | head -20
echo "=== costmap_topic_collision_checker"; grep -n "class\|footprintCost\|getCostmap\|scoreFootprint\|public:" $I/nav2_costmap_2d/costmap_topic_collision_checker.hpp $I/nav2_costmap_2d/costmap_subscriber.hpp | head -20
echo "=== behavior_server 설정(설치본)"; awk '/^behavior_server:/{f=1} f{print} /^[a-z_]+:/&&!/^behavior_server:/{if(f)exit}' ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml | head -40
