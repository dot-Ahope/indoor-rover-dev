#!/bin/bash
# 읽기 전용: nvblox 3.2 의 동적/사람 분리 모드 설정과 필요 입력·토픽 확인
R=/home/jetson/workspaces/isaac_ros-dev/src/isaac_ros_nvblox
echo "## nvblox_dynamics.yaml"; grep -vE '^\s*#|^\s*$' $R/nvblox_examples/nvblox_examples_bringup/config/nvblox/specializations/nvblox_dynamics.yaml | head -30
echo "## nvblox_segmentation.yaml"; grep -vE '^\s*#|^\s*$' $R/nvblox_examples/nvblox_examples_bringup/config/nvblox/specializations/nvblox_segmentation.yaml | head -30
echo "## 세그멘테이션 launch 가 요구하는 것(모델·입력)"; grep -rhoE "PeopleSemSeg[A-Za-z_]*|peoplesemsegnet[a-z_]*|model_name[^,]*|segmentation_mask|mask_topic|/segmentation/[a-z_/]*" $R/nvblox_examples/nvblox_examples_bringup/launch 2>/dev/null | sort | uniq -c | sort -rn | head -12
echo "## mapping_type 후보(코드)"; grep -rhoE '"(static_tsdf|static_occupancy|dynamic|human_with_static_tsdf|human_with_static_occupancy)"' $R/nvblox_ros/src 2>/dev/null | sort | uniq -c
echo "## 동적 모드 슬라이스 토픽"; grep -rhoE '"(~/)?(static_map_slice|dynamic_map_slice|combined_map_slice|dynamic_occupancy_layer|static_esdf_pointcloud)[a-z_]*"' $R/nvblox_ros/src 2>/dev/null | sort | uniq -c
echo "## 컨테이너 안 세그멘테이션 패키지 설치 여부"; docker exec isaac_ros_dev-aarch64-container bash -lc 'source /opt/ros/humble/setup.bash; ros2 pkg list 2>/dev/null | grep -E "segmentation|unet|tensor_rt|dnn" | tr "\n" " "; echo; apt-cache policy ros-humble-isaac-ros-image-segmentation 2>/dev/null | grep -m1 Candidate'
