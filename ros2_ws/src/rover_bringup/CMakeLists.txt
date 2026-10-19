cmake_minimum_required(VERSION 3.8)
project(rover_bringup)

find_package(ament_cmake REQUIRED)
# 2026-09-28: sensor_conditioner C++ 이식(Python 판 CPU 42 % — Docs/debug_log/2026-09-28/SUMMARY.md §10~)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
# 2026-10-19 §15: 프로젝터 번갈이 분리 노드(메타데이터 메시지)
find_package(realsense2_camera_msgs REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(rosbag2_cpp REQUIRED)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_executable(sensor_conditioner_node src/sensor_conditioner.cpp)
target_include_directories(sensor_conditioner_node PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
target_compile_features(sensor_conditioner_node PUBLIC cxx_std_17)
ament_target_dependencies(sensor_conditioner_node rclcpp sensor_msgs nav_msgs)
install(TARGETS sensor_conditioner_node DESTINATION lib/${PROJECT_NAME})

# 10-19 §17: 컴포넌트(드라이버와 한 component container — 같은 프로세스 전달) + 프로세스 안 기록(rosbag2_cpp). 단독 실행 파일도 같이 만든다
add_library(emitter_splitter_component SHARED src/emitter_splitter.cpp)
target_compile_features(emitter_splitter_component PUBLIC cxx_std_17)
ament_target_dependencies(emitter_splitter_component rclcpp rclcpp_components sensor_msgs realsense2_camera_msgs rosbag2_cpp)
rclcpp_components_register_node(emitter_splitter_component PLUGIN "rover_bringup::EmitterSplitter" EXECUTABLE emitter_splitter_node)
install(TARGETS emitter_splitter_component ARCHIVE DESTINATION lib LIBRARY DESTINATION lib RUNTIME DESTINATION bin)

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_conditioner_core test/test_conditioner_core.cpp)
  target_include_directories(test_conditioner_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
endif()

install(DIRECTORY launch config systemd DESTINATION share/${PROJECT_NAME})

install(PROGRAMS scripts/sensor_conditioner.py scripts/scan_restamp.py scripts/scan_deskew.py scripts/stuck_monitor.py scripts/pad_relief.py scripts/depth_relay.py scripts/display_info_pub.py scripts/install_rover_base_service.sh scripts/nav_guard.py scripts/rf2o_gate.py DESTINATION lib/${PROJECT_NAME})

ament_package()
