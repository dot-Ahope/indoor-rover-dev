#!/bin/bash
D=/opt/ros/humble/share/nav2_bt_navigator/behavior_trees; ls $D | grep -i invalid
cat $D/navigate_w_replanning_only_if_path_becomes_invalid.xml 2>/dev/null | grep -v "^ *<!--" | head -40
ls /opt/ros/humble/lib/ | grep -E "is_path_valid|updated_goal"
