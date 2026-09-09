#!/bin/bash
echo "=== foxglove_bridge 설치 위치 ==="
ls /opt/ros/humble/lib/foxglove_bridge/ 2>/dev/null | sed 's/^/  /'
echo "=== 선언된 파라미터 이름 (바이너리/라이브러리에서 추출) ==="
for f in /opt/ros/humble/lib/foxglove_bridge/foxglove_bridge /opt/ros/humble/lib/libfoxglove_bridge*.so /opt/ros/humble/lib/foxglove_bridge/*.so; do
  [ -f "$f" ] && strings "$f" 2>/dev/null
done | grep -aoE "^(port|address|tls|certfile|keyfile|topic_whitelist|param_whitelist|service_whitelist|client_topic_whitelist|min_qos_depth|max_qos_depth|num_threads|send_buffer_limit|use_compression|capabilities|asset_uri_allowlist|include_hidden|disable_load_message|ignore_unresponsive_param_nodes)$" | sort -u | sed 's/^/  /'
echo "=== 버전 ==="
cat /opt/ros/humble/share/foxglove_bridge/package.xml 2>/dev/null | grep -aoE "<version>[^<]+" | sed 's/^/  /'
echo "=== sensors.launch 의 imu 리매핑 ==="
grep -nE "imu|remap" ~/ros2_ws/install/rover_bringup/share/rover_bringup/launch/sensors.launch.py 2>/dev/null | head -12
