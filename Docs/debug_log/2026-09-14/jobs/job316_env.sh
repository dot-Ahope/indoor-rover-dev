#!/bin/bash
# N1/N0 환경 조사 (읽기 전용, sudo 없음) + 계획·컨트롤러 A/B 에 필요한 패키지 확인
source /opt/ros/humble/setup.bash
echo "=== Nav2 플러그인 패키지 ==="
for p in nav2_smac_planner nav2_mppi_controller nav2_smoother nav2_navfn_planner nav2_regulated_pure_pursuit_controller nav2_theta_star_planner; do printf '%-40s %s\n' $p "$(ros2 pkg prefix $p 2>/dev/null || echo 없음)"; done
echo "=== Jetson 환경 ==="
head -1 /etc/nv_tegra_release 2>/dev/null; cat /etc/os-release | grep -E '^PRETTY'; uname -r
dpkg -l 2>/dev/null | grep -E 'nvidia-jetpack |cuda-toolkit|nvidia-l4t-core' | awk '{print $2, $3}' | head -5
which docker nvidia-ctk 2>/dev/null; docker --version 2>/dev/null; dpkg -l | grep -c nvidia-container-toolkit
echo "디스크: $(df -h / | tail -1 | awk '{print $4" free / "$2}')  메모리: $(free -g | awk '/Mem/{print $7" GB avail / "$2" GB"}')"
echo "=== Isaac ROS 흔적 ==="
ls /etc/apt/sources.list.d/ 2>/dev/null | grep -iE 'isaac|nvidia' ; apt-cache policy ros-humble-isaac-ros-nvblox 2>/dev/null | head -3; ls ~/workspaces 2>/dev/null | head; ros2 pkg list 2>/dev/null | grep -ciE 'nvblox|isaac'
echo "=== GPU ==="
nvidia-smi 2>/dev/null | head -3 || (cat /sys/devices/gpu.0/load 2>/dev/null; echo "(nvidia-smi 없음 — tegrastats 사용)"; timeout 3 tegrastats 2>/dev/null | head -1 | grep -oE 'GR3D_FREQ [0-9]+%|RAM [0-9]+/[0-9]+MB')
