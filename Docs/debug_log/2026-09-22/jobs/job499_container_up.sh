#!/bin/bash
# 09-22 재부팅 후 isaac 컨테이너 복구: 정지된 컨테이너가 남아 있으면 docker start(안의 apt nvblox 보존), 없으면 job472 로 재생성(apt 재설치, 수 분)
set +u
CN=isaac_ros_dev-aarch64-container
ST=$(docker ps -a --filter name=$CN --format '{{.Status}}' | head -1)
echo "== 컨테이너 상태(전): ${ST:-없음}"
if [ -n "$ST" ]; then
  docker start $CN >/dev/null 2>&1 && sleep 4
else
  bash /tmp/job472_container.sh 2>&1 | tail -6 | cut -c1-160
fi
cp -f /home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml /tmp/fastdds_udp_only.xml
X() { docker exec -u admin --workdir /workspaces/isaac_ros-dev $CN bash -lc "$1"; }
echo "== 컨테이너: $(docker ps --format '{{.Names}} {{.Status}}' | grep $CN || echo 미실행)"
echo "== 안 nvblox 패키지: $(X 'source /opt/ros/humble/setup.bash; ros2 pkg list 2>/dev/null | grep -cE "^nvblox"') 개 | GPU: $(X 'nvidia-smi -L 2>/dev/null | head -1 || ls /dev/nvhost-gpu 2>/dev/null' | cut -c1-60)"
echo "== /tmp 파일: $(ls /tmp/job*.sh /tmp/job*.py /tmp/*.yaml /tmp/*.xml 2>/dev/null | wc -l) 개; nvblox yaml: $(ls /tmp/nvblox_n0*.yaml 2>/dev/null | xargs -n1 basename | tr '\n' ' ')"
