cmake_minimum_required(VERSION 3.8)
project(rover_bringup)

find_package(ament_cmake REQUIRED)

install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})

install(PROGRAMS scripts/sensor_conditioner.py scripts/scan_restamp.py scripts/scan_deskew.py scripts/stuck_monitor.py DESTINATION lib/${PROJECT_NAME})

ament_package()
