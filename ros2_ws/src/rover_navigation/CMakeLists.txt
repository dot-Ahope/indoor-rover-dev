cmake_minimum_required(VERSION 3.8)
project(rover_navigation)

find_package(ament_cmake REQUIRED)

# 2026-10-01 §8.39: BT 조건 노드 PathBlockedAhead(앞 경로가 2 s 이상 막히면 주행 중단 → 재계획). bt_navigator 가 plugin_lib_names 로 불러온다.
find_package(rclcpp REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(nav2_util REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
add_library(rover_path_blocked_ahead_bt_node SHARED src/path_blocked_ahead_condition.cpp)
target_compile_definitions(rover_path_blocked_ahead_bt_node PRIVATE BT_PLUGIN_EXPORT)
ament_target_dependencies(rover_path_blocked_ahead_bt_node rclcpp behaviortree_cpp_v3 nav2_util nav_msgs geometry_msgs tf2_ros)
install(TARGETS rover_path_blocked_ahead_bt_node
  ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)

install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})
# 2026-09-22 N6-0: 컨테이너 nvblox 기동 래퍼(launch 의 ExecuteProcess 가 bash 로 부름)
install(PROGRAMS scripts/nvblox_up.sh DESTINATION share/${PROJECT_NAME}/scripts)

ament_package()
