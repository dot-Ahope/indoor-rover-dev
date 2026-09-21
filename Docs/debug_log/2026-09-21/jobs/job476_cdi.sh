#!/bin/bash
echo "== 전체 오류(CDI 지정 그대로):"; docker run --rm --runtime nvidia -e NVIDIA_VISIBLE_DEVICES=nvidia.com/gpu=all,nvidia.com/pva=all isaac_ros_dev-aarch64 true 2>&1 | head -3 | cut -c1-300
echo "== CDI 상태: /etc/cdi: $(ls /etc/cdi 2>/dev/null | tr '\n' ' ') | /var/run/cdi: $(ls /var/run/cdi 2>/dev/null | tr '\n' ' ') | nvidia-ctk $(nvidia-ctk --version 2>/dev/null | head -1)"
nvidia-ctk cdi list 2>&1 | head -4
echo "== 레거시 모드 시험(NVIDIA_VISIBLE_DEVICES=all):"; docker run --rm --runtime nvidia -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=all isaac_ros_dev-aarch64 bash -c 'echo ok; ls /dev | grep -cE "nvhost|nvmap|nvgpu"; ldconfig -p | grep -cE "libcuda|libnvrm"; ls /usr/local/cuda/bin/nvcc 2>/dev/null; ls /usr/lib/aarch64-linux-gnu/tegra | head -3 | tr "\n" " "' 2>&1 | head -6 | cut -c1-200
echo "== 호스트 /dev nvhost: $(ls /dev | grep -cE 'nvhost|nvmap|nvgpu') | daemon.json runtimes: $(grep -o '"nvidia"' /etc/docker/daemon.json | wc -l)"
