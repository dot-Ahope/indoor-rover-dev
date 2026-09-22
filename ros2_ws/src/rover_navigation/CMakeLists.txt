cmake_minimum_required(VERSION 3.8)
project(rover_navigation)

find_package(ament_cmake REQUIRED)

install(DIRECTORY config launch DESTINATION share/${PROJECT_NAME})
# 2026-09-22 N6-0: 컨테이너 nvblox 기동 래퍼(launch 의 ExecuteProcess 가 bash 로 부름)
install(PROGRAMS scripts/nvblox_up.sh DESTINATION share/${PROJECT_NAME}/scripts)

ament_package()
