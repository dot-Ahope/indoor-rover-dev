#!/bin/bash
# 문제 위치 판별: 컨테이너 내부(agent 와 같은 DDS 참가자 호스트)에서 본 주기 vs 젯슨 호스트에서 본 주기
#   내부 정상 / 외부 0  → 보드-agent 구간은 멀쩡, 컨테이너<->호스트 DDS 전달이 문제
#   내부도 0            → 보드가 실제로 안 보냄 (또는 agent 가 못 받음)
source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash

echo "=== 컨테이너 실행 옵션 (네트워크/IPC/SHM) ==="
docker inspect -f 'NetworkMode={{.HostConfig.NetworkMode}} IpcMode={{.HostConfig.IpcMode}} Pid={{.HostConfig.PidMode}}' microros_agent 2>/dev/null | sed 's/^/  /'
docker inspect -f '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}' microros_agent 2>/dev/null | sed 's/^/  mount: /'
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' microros_agent 2>/dev/null | grep -aiE "ROS_|RMW|FASTRTPS|DDS" | sed 's/^/  env: /'
echo "  호스트 env: ROS_DOMAIN_ID=${ROS_DOMAIN_ID:-미설정} RMW=${RMW_IMPLEMENTATION:-기본}"
echo "  호스트 /dev/shm: $(df -h /dev/shm 2>/dev/null | tail -1)"
echo "  컨테이너 /dev/shm: $(docker exec microros_agent df -h /dev/shm 2>/dev/null | tail -1)"
echo ""

echo "=== 컨테이너 내부에서 본 주기 (각 12초) ==="
docker exec microros_agent bash -lc '
  source /opt/ros/humble/setup.bash 2>/dev/null
  for t in /wheel_odom /rover/status /battery; do
    printf "  내부 %-16s " "$t"
    timeout 14 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
  done' 2>&1
echo ""
echo "=== 같은 시각 호스트에서 본 주기 ==="
for t in /wheel_odom /rover/status /battery; do
  printf "  호스트 %-16s " "$t"
  timeout 14 ros2 topic hz "$t" 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1 || echo "무발행"
done
