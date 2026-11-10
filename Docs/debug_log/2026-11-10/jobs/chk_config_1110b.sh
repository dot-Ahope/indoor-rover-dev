#!/bin/bash
# chk_config_1110b — 11-10 §0 이어서(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: chk_config_1110 에서 ① src 4 파일이 저장소 HEAD 와 다름 ② 부팅 25 분인데 에이전트 컨테이너가 'Up 5 days' ③ rover-base 서비스 inactive 인데 에이전트 · RSP 가 떠 있음.
#   보는 것: 4 파일 원문(PC 에서 HEAD 와 diff) · 시계(timedatectl) · 컨테이너 시작 시각 · 스택 프로세스의 시작 시각과 명령 · 자동 기동 경로(서비스 · autostart · crontab).
#   인자: 없음. 출력: 표준 출력(PC 에서 outputs/chk_config_1110b.txt 로 tee). '@@FILE <경로>' 줄 뒤가 파일 원문.
cd ~/ros2_ws/src || exit 1
for f in rover_description/launch/description.launch.py rover_description/urdf/rover.urdf.xacro \
         rover_navigation/launch/localization.launch.py rover_navigation/scripts/place_web.py; do
  echo "@@FILE $f $(stat -c %y $f | cut -c1-16)"; tr -d '\r' < $f; echo "@@END"; done

echo "== 시계"
timedatectl 2>/dev/null | grep -E 'Local time|synchronized|NTP service|RTC time'
echo "date $(date '+%F %T') · 부팅 $(uptime -s)"
echo "== 컨테이너"
docker inspect -f 'microros_agent Created {{.Created}} · StartedAt {{.State.StartedAt}} · Restart {{.HostConfig.RestartPolicy.Name}} · AutoRemove {{.HostConfig.AutoRemove}}' microros_agent 2>&1
docker ps -a --format '{{.Names}} {{.Status}}' 2>/dev/null | sed 's/^/  ps -a: /'
echo "== 스택 프로세스(시작 시각 · 경과 · 명령)"
ps -eo pid,ppid,lstart,etime,args --sort=start_time | grep -E 'ros2|robot_state|micro|docker run|display_info' | grep -v grep | cut -c1-220
echo "== 자동 기동 경로"
systemctl list-unit-files 2>/dev/null | grep -iE 'rover|ros' | sed 's/^/  unit: /'
ls /etc/systemd/system 2>/dev/null | grep -iE 'rover|ros' | sed 's/^/  /etc\/systemd\/system: /'
ls ~/.config/autostart 2>/dev/null | sed 's/^/  autostart: /'
crontab -l 2>/dev/null | grep -v '^#' | sed 's/^/  crontab: /'
echo "== 에이전트 로그 끝"
docker logs --tail 6 microros_agent 2>&1 | cut -c1-160
