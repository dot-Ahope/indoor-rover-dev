#!/bin/bash
# chk_config_1110c — 11-10 §0 이어서(읽기만 · 로버 안 움직임 · DDS 참여자 안 만듦).
#   왜: 1110b 에서 base.launch 의 부모 PID 1388 을 못 밝힘 + 자동 기동 경로 줄이 내 sed 오류(구분자 '/' 와 경로 충돌)로 깨짐 → 구분자 '|' 로 다시.
#   보는 것: base.launch 부모 사슬(PID · 명령) · rover 관련 systemd 단위 · ~/.config/autostart · crontab. 인자: 없음. 출력: 표준 출력.
P=$(pgrep -f 'ros2 launch rover_bringup base.launch.py' | head -1)
echo "== base.launch 부모 사슬 (시작 PID $P)"
while [ -n "$P" ] && [ "$P" != 0 ]; do ps -o pid=,ppid=,user=,args= -p $P | cut -c1-200; P=$(ps -o ppid= -p $P | tr -d ' '); [ "$P" = 1 ] && { ps -o pid=,args= -p 1 | cut -c1-80; break; }; done
echo "== systemd(시스템 · 사용자)"
systemctl list-unit-files --no-legend 2>/dev/null | grep -iE 'rover|ros2|micro' | sed 's|^|  sys: |'
systemctl --user list-unit-files --no-legend 2>/dev/null | grep -iE 'rover|ros2|micro' | sed 's|^|  user: |'
echo "== autostart"
for f in ~/.config/autostart/*.desktop; do [ -e "$f" ] && echo "  $(basename $f): $(grep -E '^(Exec|Hidden|X-GNOME-Autostart-enabled)=' $f | tr '\n' ' ' | cut -c1-200)"; done
echo "== crontab"
crontab -l 2>/dev/null | grep -v '^#' | sed 's|^|  |'
