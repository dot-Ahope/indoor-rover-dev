#!/bin/bash
echo "호스트: $(id jetson)"
echo "컨테이너 admin: $(docker exec isaac_ros_dev-aarch64-container id admin)"
echo "/dev/shm fastrtps 지금: $(ls /dev/shm | grep -c fastrtps)"
ls -la /dev/shm | head -8
