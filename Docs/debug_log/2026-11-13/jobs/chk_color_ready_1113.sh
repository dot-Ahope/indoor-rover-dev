#!/bin/bash
# chk_color_ready_1113 — 컬러 5 fps 정지 기록 시험 전 읽기 확인(11-13 §0). 로버 안 움직임, 아무것도 띄우거나 끄지 않음.
#   왜: 기록기를 SHM+UDP 로 띄워 컬러를 5 fps 로 남기려면 ① 지금 스택이 떠 있는지 ② 5 fps 를 만들 수단(throttle 노드 설치 여부 ·
#       카메라가 640x480 5 fps 를 지원하는지) ③ 압축 전송 플러그인 ④ 디스크 여유 를 먼저 알아야 함.
#   인자 없음. 출력은 러너가 PC 로 가져옴 → outputs/chk_color_ready_1113.txt
echo "== 부팅 $(uptime -s) · 지금 $(date '+%F %T') · $(uptime -p)"
echo "== rover-base(user) $(systemctl --user is-active rover-base 2>&1)"
echo "== 스택 프로세스"
for p in realsense2_camera slam_toolbox controller_server bt_navigator ekf_node nvblox_node; do echo "  $p $(pgrep -fc $p)"; done
echo "== topic_tools(throttle)"
ls /opt/ros/humble/lib/topic_tools/ 2>/dev/null | tr '\n' ' '; echo
dpkg -l 2>/dev/null | awk '/ros-humble-(topic-tools|image-transport-plugins|compressed-image-transport|image-transport )/{print "  "$2, $3}'
echo "== image_transport 플러그인 목록"
timeout 20 ros2 run image_transport list_transports 2>/dev/null | grep -E "^\s*\"?image_transport/|compressed|raw" | head -10
echo "== 카메라 컬러 지원 프로파일(librealsense 표 — 장치를 열지 않는 방법이 없어 스택이 떠 있으면 생략)"
if [ "$(pgrep -fc realsense2_camera)" = 0 ] && command -v rs-enumerate-devices >/dev/null; then
  timeout 20 rs-enumerate-devices 2>/dev/null | grep -E "Color.*640x480" | head -10
else echo "  생략(카메라 사용 중 또는 rs-enumerate-devices 없음: $(command -v rs-enumerate-devices || echo 없음))"; fi
echo "== 디스크"
df -h /tmp /home/jetson | sed 's/^/  /'
echo "== /dev/shm fastrtps $(ls /dev/shm 2>/dev/null | grep -c fastrtps)"
