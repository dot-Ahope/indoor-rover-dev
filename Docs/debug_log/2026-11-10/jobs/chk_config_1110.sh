#!/bin/bash
# chk_config_1110 — 11-10 §0: Jetson 의 지금 구성 점검(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: 저장소 CURRENT_STACK.md(11-04 판)는 코드와 일치를 확인했으나, Jetson 에 실제로 배포 · 실행 중인 판은 11-04 이후 미확인.
#   보는 것: ① 신원(호스트 · 커널 · L4T · /dev/rover · 주소 · SSID · 가동 시간) ② src 전 파일 md5(CR 제거, 앞 12 자 — PC 의 git HEAD 판과 비교)
#            ③ 설치본 share 설정이 src 링크인지 · C++ 빌드물이 src 보다 새것인지 ④ /tmp prep 도구 md5(up_tools.sh 7 개)
#            ⑤ 실행 상태(프로세스 개수 · 컨테이너 · 에이전트 세션) ⑥ 지도 · 포크 존재.
#   인자: 없음. 출력: 표준 출력(PC 에서 Docs/debug_log/2026-11-10/outputs/chk_config_1110.txt 로 tee).
echo "== ① 신원"
echo "host $(hostname) · user $(whoami) · $(uname -r) · $(head -1 /etc/nv_tegra_release | cut -c1-30)"
echo "rover -> $(readlink /dev/rover) · rplidar -> $(readlink /dev/rplidar)"
echo "주소: $(ip -4 -o addr show | awk '{print $2, $4}' | grep -v '^lo' | tr '\n' ' ')"
echo "SSID: $(nmcli -t -f active,ssid dev wifi 2>/dev/null | grep '^yes' | cut -d: -f2)"
echo "가동 $(uptime -p) · 부팅 $(uptime -s) · 디스크 / 남음 $(df -h / | awk 'NR==2{print $4}')"

echo "== ② src md5"
cd ~/ros2_ws/src || exit 1
find rover_bringup rover_description rover_navigation -type f ! -name '*.stl' | sort | while read f; do
  echo "SRC $(tr -d '\r' < "$f" | md5sum | cut -c1-12) $f"; done
echo "src git: $(git -C ~/ros2_ws log -1 --format='%h %cd' 2>/dev/null || echo '(git 아님)')"

echo "== ③ 설치본"
for p in rover_bringup rover_navigation rover_description; do
  for f in $(find ~/ros2_ws/install/$p/share/$p -type f -o -type l | grep -E '\.(yaml|xml|py|urdf|xacro)$' | sort); do
    if [ -L "$f" ]; then echo "LINK $p/${f##*/share/$p/}"; else echo "FILE $p/${f##*/share/$p/} $(stat -c %y "$f" | cut -c1-16)"; fi
  done
done | awk '{print $1}' | sort | uniq -c | sed 's/^/  종류별 개수 /'
find ~/ros2_ws/install/rover_*/share -type f \( -name '*.yaml' -o -name '*.xml' -o -name '*.py' \) 2>/dev/null | sed "s|$HOME/ros2_ws/install/||" | sed 's/^/  링크 아닌 파일: /'
echo "-- C++ 빌드물(설치 시각) vs 소스(수정 시각)"
for x in rover_bringup/lib/rover_bringup/sensor_conditioner_node rover_bringup/lib/libemitter_splitter_component.so \
         rover_navigation/lib/librover_path_blocked_ahead_bt_node.so rover_navigation/lib/librover_copy_path_bt_node.so \
         rover_navigation/lib/librover_monotone_escape_behavior.so rover_navigation/lib/librover_clearance_band_critic.so; do
  [ -e ~/ros2_ws/install/$x ] && echo "  BIN $(stat -c %y ~/ros2_ws/install/$x | cut -c1-16) $x" || echo "  BIN 없음 $x"; done
for s in rover_bringup/src/*.cpp rover_navigation/src/*.cpp; do echo "  CPP $(stat -c %y $s | cut -c1-16) $s"; done

echo "== ④ /tmp prep 도구"
for f in prep_fast.sh prep_patrol.sh chk_prep.py chk_drive_gate.py anal_rtps_pcap.py anal_rtps_onset.py anal_rtps_acklag.py; do
  [ -e /tmp/$f ] && echo "TMP $(tr -d '\r' < /tmp/$f | md5sum | cut -c1-12) $f" || echo "TMP 없음 $f"; done

echo "== ⑤ 실행 상태"
for p in micro_ros_agent robot_state_publisher realsense2_camera rplidar_node sensor_conditioner ekf_node vslam_twist slam_toolbox \
         controller_server planner_server bt_navigator nvblox stuck_monitor nav_guard place_server place_web foxglove_bridge ros2; do
  printf '  %-22s %s\n' "$p" "$(pgrep -fc "$p")"; done
echo "  컨테이너: $(docker ps --format '{{.Names}}({{.Status}})' 2>/dev/null | tr '\n' ' ')"
echo "  에이전트 세션 수립 기록 $(docker logs microros_agent 2>&1 | grep -ac 'session established') 건"
echo "  rover-base 서비스: $(systemctl is-active rover-base 2>/dev/null) · 사용 설정 $(systemctl is-enabled rover-base 2>/dev/null)"
echo "  /tmp/nav2_params_active.yaml: $(stat -c %y /tmp/nav2_params_active.yaml 2>/dev/null | cut -c1-16 || echo 없음)"

echo "== ⑥ 지도 · 포크"
ls ~/maps/office/office_v3.* 2>/dev/null | sed 's/^/  /'
echo "  slam 포크: $(ls ~/slam_ws/install/slam_toolbox/lib/slam_toolbox/localization_slam_toolbox_node 2>/dev/null || echo 없음)"
