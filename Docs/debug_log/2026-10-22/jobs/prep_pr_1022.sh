#!/bin/bash
# 10-22 f2pr1 구성 prep: 운용(프로젝터 상시 끔 · 그림자 · SHM) + 깊이 프리셋 3
SENSORS_ADD="emitter_off:=true vslam:=shadow dds_shm:=true depth_preset:=3" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|SHM 고아\|cuVSLAM(컨테이너)\|wheel_odom\|nvblox_up" | tail -8
echo "visual_preset = $(source /opt/ros/humble/setup.bash; ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
