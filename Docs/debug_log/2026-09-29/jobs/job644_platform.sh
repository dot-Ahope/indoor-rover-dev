#!/bin/bash
# 09-29 §8: JetPack·L4T·CUDA·TensorRT 버전, 컨테이너 Isaac ROS 패키지 버전, 영상 경로(누가 어디서 도나) 확인
echo "== 호스트"
head -1 /etc/nv_tegra_release
dpkg-query -W -f='${Package} ${Version}\n' nvidia-jetpack nvidia-l4t-core cuda-toolkit-12-6 tensorrt libnvinfer10 2>/dev/null
ls -d /usr/local/cuda-* 2>/dev/null
echo "== 컨테이너"
CN=isaac_ros_dev-aarch64-container
docker inspect -f '이미지 {{.Config.Image}}' $CN
docker exec $CN bash -lc "dpkg-query -W -f='\${Package} \${Version}\n' 2>/dev/null | grep -E 'isaac-ros-(nvblox|visual-slam|cuvslam|nitros|common|realsense|managed-nitros)|ros-humble-nvblox|negotiated' | sort | head -30"
docker exec $CN bash -lc "ls /usr/local/cuda*/version* 2>/dev/null; nvcc --version 2>/dev/null | tail -1"
echo "== 영상 경로(프로세스)"
ps -eo pid,pcpu,args --sort=-pcpu | grep -aE "realsense|nvblox|depth_relay|component_container|scan_deskew|slam_toolbox|controller_server|ekf_node|sensor_conditioner|rplidar" | grep -v grep | cut -c1-170 | head -20
