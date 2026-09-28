cmake_minimum_required(VERSION 3.8)
project(rover_bringup)

find_package(ament_cmake REQUIRED)
# 2026-09-28: sensor_conditioner C++ 이식(Python 판 CPU 42 % — Docs/debug_log/2026-09-28/SUMMARY.md §10~)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

add_executable(sensor_conditioner_node src/sensor_conditioner.cpp)
target_include_directories(sensor_conditioner_node PUBLIC $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>)
target_compile_features(sensor_conditioner_node PUBLIC cxx_std_17)
ament_target_dependencies(sensor_conditioner_node rclcpp sensor_msgs nav_msgs)
install(TARGETS sensor_conditioner_node DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_conditioner_core test/test_conditioner_core.cpp)
  target_include_directories(test_conditioner_core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
endif()

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

install(PROGRAMS scripts/sensor_conditioner.py scripts/scan_restamp.py scripts/scan_deskew.py scripts/stuck_monitor.py scripts/depth_relay.py scripts/display_info_pub.py DESTINATION lib/${PROJECT_NAME})

ament_package()
