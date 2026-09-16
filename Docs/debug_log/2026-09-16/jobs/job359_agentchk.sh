#!/bin/bash
# 에이전트 컨테이너가 루프백 프로파일을 받았는지 + 세션/토픽 가시성 (루프백 CLI vs 전체 인터페이스 CLI)
echo "=== 컨테이너 env/mount ==="; docker inspect microros_agent --format '{{range .Config.Env}}{{println .}}{{end}}' 2>/dev/null | grep -aE "FASTRTPS|MICROROS"; docker inspect microros_agent --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}' 2>/dev/null | grep -a fastdds
echo "=== 에이전트 세션 ==="; docker logs microros_agent 2>&1 | grep -ac "session established"; docker logs --tail 2 microros_agent 2>&1 | cut -c1-100
echo "=== /wheel_odom 가시성 ==="
export FASTRTPS_DEFAULT_PROFILES_FILE=$HOME/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
ros2 daemon stop >/dev/null 2>&1
printf "  루프백 CLI  hz: "; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo
unset FASTRTPS_DEFAULT_PROFILES_FILE; ros2 daemon stop >/dev/null 2>&1
printf "  전체IF CLI  hz: "; timeout 8 ros2 topic hz /wheel_odom 2>&1 | grep -aoE "average rate: [0-9.]+" | tail -1; echo
ros2 daemon stop >/dev/null 2>&1
