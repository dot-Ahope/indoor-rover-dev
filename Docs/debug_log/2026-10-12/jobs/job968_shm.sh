#!/bin/bash
# 10-12 §8.3: 공유메모리 전송 재사용 검토용 사실 확인(로버 안 움직임)
for c in isaac_ros_dev-aarch64-container microros_agent; do echo "  $c: ipc $(docker inspect --format '{{.HostConfig.IpcMode}}' $c 2>/dev/null) · net $(docker inspect --format '{{.HostConfig.NetworkMode}}' $c 2>/dev/null) · /dev/shm 공유 $(docker inspect --format '{{range .Mounts}}{{.Source}}:{{.Destination}} {{end}}' $c 2>/dev/null | grep -o '/dev/shm[^ ]*' | head -1)"; done
echo "  호스트 Fast DDS: $(dpkg -l | grep -a 'ros-humble-fastrtps ' | awk '{print $3}') · rmw: ${RMW_IMPLEMENTATION:-기본(fastrtps)}"
echo "  컨테이너 안 프로파일: $(docker exec isaac_ros_dev-aarch64-container bash -c 'echo ${FASTRTPS_DEFAULT_PROFILES_FILE:-없음}; ls /dev/shm | wc -l' 2>/dev/null | tr '\n' ' ')"
echo "  호스트 /dev/shm: $(df -h /dev/shm | tail -1 | awk '{print $2, "중", $3, "사용"}') · fastrtps 잔류 파일 $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
