#!/bin/bash
# chk_ml_capacity_1110 — 11-10 §2: 학습식 6D 자세 추정(CenterPose · DOPE · FoundationPose)을 이 Jetson 에 올릴 수 있는지 자원 확인(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: Isaac ROS 공식 성능표(release-5.0)에 Orin Nano Super 8GB 의 FoundationPose 값이 없고, 포럼은 변환에 GPU 여유 7.5 GB 가 필요하다고 함.
#   보는 것: JetPack · TensorRT · CUDA 판 · 전원 모드 · 메모리/스왑(지금은 스택 안 떠 있음 = 최대 여유) · 디스크 · 설치된 Isaac ROS 이미지 판.
#   인자: 없음. 출력: 표준 출력.
echo "== 판"
echo "L4T $(head -1 /etc/nv_tegra_release | cut -c1-40)"
dpkg-query -W -f='${Package} ${Version}\n' nvidia-jetpack nvidia-l4t-core tensorrt libnvinfer10 cuda-toolkit-12-6 2>/dev/null | sed 's/^/  /'
ls -d /usr/local/cuda-* 2>/dev/null | sed 's/^/  cuda dir: /'
echo "  전원 모드: $(nvpmodel -q 2>/dev/null | head -2 | tr '\n' ' ' || echo '(조회 불가)')"
echo "== 메모리 · 디스크(스택 미기동 상태)"
free -m | sed 's/^/  /'
df -h / | sed 's/^/  /'
echo "== Isaac ROS 이미지 · 컨테이너"
docker images --format '{{.Repository}}:{{.Tag}} {{.Size}} {{.CreatedSince}}' 2>/dev/null | grep -iE 'isaac|ros|nvblox|vslam' | sed 's/^/  /'
ls ~/workspaces/isaac_ros-dev/src 2>/dev/null | sed 's/^/  src: /'
echo "== tegrastats 1 회"
timeout 3 tegrastats --interval 1000 2>/dev/null | head -1 | cut -c1-220
