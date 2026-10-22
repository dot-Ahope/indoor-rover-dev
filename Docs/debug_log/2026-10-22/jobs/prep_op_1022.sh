#!/bin/bash
# 10-22 §5 §10 운용 prep(인자에 depth_preset 없음) — camera.launch 기본값 3 이 적용되는지 확인
SENSORS_ADD="emitter_off:=true vslam:=shadow dds_shm:=true" bash /tmp/prep_patrol.sh lite 2>&1 | grep -a "PREP_OK\|PREP_FAIL\|불합격\|★\|위치 추정 검사\|SHM 고아\|cuVSLAM(컨테이너)\|wheel_odom\|nvblox_up" | tail -8
echo "visual_preset = $(source /opt/ros/humble/setup.bash; ros2 param get /camera/camera depth_module.visual_preset 2>&1)"
