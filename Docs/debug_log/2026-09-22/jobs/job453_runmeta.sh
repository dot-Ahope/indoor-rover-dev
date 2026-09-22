#!/bin/bash
# 주행 재현 메타 (2026-09-18 §17): "무엇으로 달렸는지" 를 bag 옆에 남긴다 — 실행 중 노드의 실제 파라미터(job451), 배포 파일 해시, 단계·메모, 기록 토픽.
# 인자: NAME [주행 인자 ...]   환경: TOPICS BAG_EXTRA STAGE NOTE GIT_HEAD   출력: /tmp/meta_NAME/{run_meta.txt,params.txt} (job231 이 bag 폴더로 옮김)
NAME=$1; shift
M=/tmp/meta_$NAME; rm -rf $M; mkdir -p $M
{
echo "name: $NAME"; echo "date: $(date '+%F %T %z')"; echo "drive_args: $*"; echo "box_hint: ${BX:-} ${BY:-} tol ${TOL:-}"
echo "stage: ${STAGE:-}"; echo "note: ${NOTE:-}"; echo "git_head_pc: ${GIT_HEAD:-}"
echo "bag_topics: $TOPICS"; echo "bag_extra: ${BAG_EXTRA:-}"
echo "nvpmodel: $(nvpmodel -q 2>/dev/null | tr '\n' ' ')"; echo "load_uptime: $(cut -d' ' -f1-3 /proc/loadavg) / up $(cut -d' ' -f1 /proc/uptime) s"
echo "pkg: nav2-mppi $(dpkg-query -W -f='${Version}' ros-humble-nav2-mppi-controller 2>/dev/null) costmap-2d $(dpkg-query -W -f='${Version}' ros-humble-nav2-costmap-2d 2>/dev/null) slam-toolbox $(dpkg-query -W -f='${Version}' ros-humble-slam-toolbox 2>/dev/null)"
echo "files:  # sha256 앞 12 자리, 수정 시각"
for f in /tmp/nav2_params_active.yaml /tmp/nvblox_active.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nvblox_local.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav2_params.yaml ~/ros2_ws/install/rover_navigation/share/rover_navigation/config/nav_to_pose_no_spin.xml \
         $(find ~/ros2_ws/install/rover_description ~/ros2_ws/install/rover_bringup -name 'rover.urdf' -o -name 'stuck_monitor.py' -o -name 'camera.launch.py' -o -name 'fastdds_udp_only.xml' -o -name 'depth_relay.py' 2>/dev/null | sort -u) \
         /tmp/job125_avoid3.py /tmp/job254_s4run.sh /tmp/job231_drive.sh; do
  [ -f "$f" ] && echo "  $(sha256sum "$f" | cut -c1-12)  $(stat -c %y "$f" | cut -c1-19)  $f"
done
echo "firmware_status: $(timeout 6 ros2 topic echo /rover/status --once 2>/dev/null | tr '\n' ' ' | tr -s ' ' | cut -c1-400)"
echo "topics_live: $(timeout 8 ros2 topic list 2>/dev/null | tr '\n' ' ')"
} > $M/run_meta.txt
timeout 45 python3 /tmp/job451_paramsnap.py > $M/params.txt 2>&1
echo "  메타: run_meta $(wc -l < $M/run_meta.txt) 줄, params $(wc -l < $M/params.txt) 줄 ($(grep -c '(없음)' $M/params.txt) 노드 응답 없음)"
