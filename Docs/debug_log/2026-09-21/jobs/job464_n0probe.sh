#!/bin/bash
# N0 사전 조사(읽기 전용, sudo 없음): docker/nvidia 런타임, 이미지, 디스크, 네트워크(nvcr.io·github·apt 저장소), JetPack, 전원 모드, 기존 isaac 흔적
echo "== L4T: $(head -1 /etc/nv_tegra_release 2>/dev/null | cut -c1-60) | JetPack: $(apt-cache policy nvidia-jetpack 2>/dev/null | grep -m1 Installed)"
echo "== CUDA: $(ls -d /usr/local/cuda-* 2>/dev/null | tr '\n' ' ') | nvcc: $(/usr/local/cuda/bin/nvcc --version 2>/dev/null | grep -o 'release [0-9.]*')"
echo "== docker: $(docker --version 2>/dev/null) | 사용자 그룹: $(id -nG | tr ' ' ',')"
echo "== nvidia runtime: $(docker info 2>/dev/null | grep -iE 'Runtimes|Default Runtime' | tr '\n' ' ')"
echo "== images:"; docker images --format '  {{.Repository}}:{{.Tag}} {{.Size}}' 2>/dev/null | head -8
echo "== 디스크: $(df -h / | tail -1 | awk '{print $4" 여유 / "$2}') | docker root: $(docker info 2>/dev/null | grep -i 'Docker Root Dir' | cut -d: -f2)"
echo "== 메모리: $(free -m | awk '/Mem:/{print $2" MB, 가용 "$7}') | swap $(free -m | awk '/Swap:/{print $2}') MB | nvpmodel: $(nvpmodel -q 2>/dev/null | head -1)"
for u in https://nvcr.io/v2/ https://github.com https://isaac.download.nvidia.com/isaac-ros/release-3/ubuntu/jammy/dists/ https://nvidia-isaac-ros.github.io/; do printf "  net %-70s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code} %{time_total}s' --max-time 10 $u)"; done
echo "== apt isaac 흔적: $(grep -rl isaac /etc/apt/sources.list.d/ 2>/dev/null | wc -l) 파일 | 패키지: $(apt-cache search isaac-ros 2>/dev/null | wc -l) 개 검색됨"
echo "== ~/workspaces: $(ls -d ~/workspaces* 2>/dev/null) | isaac_ros 디렉토리: $(find ~ -maxdepth 3 -iname '*isaac*' 2>/dev/null | head -3 | tr '\n' ' ')"
echo "== realsense: $(dpkg -l | grep -E 'librealsense2 |ros-humble-realsense2-camera ' | awk '{print $2"="$3}' | tr '\n' ' ')"
echo "== 커널/모듈: $(uname -r) | nvidia-container-toolkit: $(dpkg -l | grep -E 'nvidia-container-toolkit ' | awk '{print $3}')"
