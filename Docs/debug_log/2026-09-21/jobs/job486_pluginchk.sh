#!/bin/bash
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash
echo "== package.xml export:"; grep -E "nav2_costmap_2d|plugin" ~/ros2_ws/install/nvblox_nav2/share/nvblox_nav2/package.xml | head -3
echo "== ament_index 플러그인 리소스:"; ls ~/ros2_ws/install/nvblox_nav2/share/ament_index/resource_index/ 2>/dev/null | tr '\n' ' '; echo; cat ~/ros2_ws/install/nvblox_nav2/share/ament_index/resource_index/nav2_costmap_2d__pluginlib__plugin/nvblox_nav2 2>/dev/null
echo "== pluginlib 로드 시험(파이썬 없음 → 클래스 목록 xml):"; grep -oE 'name="[^"]+"|type="[^"]+"|base_class_type="[^"]+"' ~/ros2_ws/install/nvblox_nav2/share/nvblox_nav2/nvblox_costmap_layer.xml | tr '\n' ' '; echo
echo "== 호스트에서 슬라이스 타입 인식: $(ros2 interface show nvblox_msgs/msg/DistanceMapSlice 2>/dev/null | head -1)"
