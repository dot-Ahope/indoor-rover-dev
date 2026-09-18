#!/bin/bash
# 로그·산출물 누적 조사 (2026-09-18, 읽기 전용 — 삭제 없음). sudo 는 크기 읽기에만.
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
H=/home/jetson
echo "######## 1. 디스크"; df -h / /tmp 2>/dev/null | sed 's/^/  /'
echo "######## 2. 큰 디렉터리 (du, MB)"
for d in /var/log /var/log/journal /var/crash /var/cache/apt /var/lib/docker /var/lib/snapd /tmp $H/.ros $H/.ros/log $H/ros2_ws $H/ros2_ws/build $H/ros2_ws/install $H/ros2_ws/log $H/.cache $H/Downloads $H/bags $H/rosbag2 /opt/ros; do
  [ -e "$d" ] && printf '  %8s MB  %s\n' "$(S du -sm "$d" 2>/dev/null | cut -f1)" "$d"
done
echo "######## 3. /var/log 상위 파일"; S find /var/log -type f -size +5M -printf '%s %p\n' 2>/dev/null | sort -rn | head -15 | awk '{printf "  %8.1f MB  %s\n", $1/1048576, $2}'
echo "######## 4. logrotate 상태"
systemctl is-enabled logrotate.timer 2>&1 | sed 's/^/  timer enabled: /'; systemctl is-active logrotate.timer 2>&1 | sed 's/^/  timer active: /'
systemctl list-timers --all 2>/dev/null | grep -i logrotate | sed 's/^/  /'
ls -la /etc/cron.daily/ 2>/dev/null | grep -i logrotate | sed 's/^/  cron.daily: /'
S grep -E 'syslog|messages' /var/lib/logrotate/status 2>/dev/null | head -3 | sed 's/^/  마지막 회전 기록: /'
S sed -n '1,20p' /etc/logrotate.d/rsyslog 2>/dev/null | sed 's/^/  rsyslog conf: /'
echo "  journald: $(S journalctl --disk-usage 2>&1 | tail -1)"
echo "######## 5. /tmp 내용 (크기순 상위, 종류별)"
S du -sm /tmp/* 2>/dev/null | sort -rn | head -20 | sed 's/^/  /'
echo "  -- 종류별 개수·합계"
for pat in 'bag_*' '*.tgz' 'job*' 'run_*' '*.log' '*.txt' '*.csv' '*.npy' '*.py' '*.sh'; do
  n=$(ls -d /tmp/$pat 2>/dev/null | wc -l); [ $n -gt 0 ] && printf '  %-8s %4d 개 %8s MB\n' "$pat" $n "$(du -scm /tmp/$pat 2>/dev/null | tail -1 | cut -f1)"
done
echo "######## 6. ~/.ros/log (ROS 실행 로그)"
if [ -d $H/.ros/log ]; then
  echo "  디렉터리 $(ls -1 $H/.ros/log | wc -l) 개, 가장 오래된 $(ls -1tr $H/.ros/log | head -1), 최신 $(ls -1t $H/.ros/log | head -1)"
  ls -1 $H/.ros/log | sed -E 's/^([0-9]{4}-[0-9]{2})-.*/\1/' | grep -E '^[0-9]{4}-[0-9]{2}$' | sort | uniq -c | sed 's/^/   월별 /'
  find $H/.ros/log -type f -size +20M -printf '%s %p\n' 2>/dev/null | sort -rn | head -5 | awk '{printf "   큰 파일 %8.1f MB %s\n", $1/1048576, $2}'
fi
echo "######## 7. docker"
docker system df 2>&1 | sed 's/^/  /'
docker ps -a --format '  {{.Names}} {{.Status}} {{.Size}}' 2>/dev/null | head -10
docker images --format '  {{.Repository}}:{{.Tag}} {{.Size}} {{.CreatedSince}}' 2>/dev/null | head -12
echo "######## 8. 홈·/var 의 100 MB 넘는 파일"
S find $H /var /opt /usr/local -xdev -type f -size +100M -printf '%s %TY-%Tm-%Td %p\n' 2>/dev/null | sort -rn | head -25 | awk '{printf "  %8.1f MB %s %s\n", $1/1048576, $2, $3}'
echo "######## 9. bag·db3 흩어진 것"
S find $H /tmp /var/tmp -xdev \( -name '*.db3' -o -name '*.mcap' -o -name 'metadata.yaml' \) -printf '%s %TY-%Tm-%Td %h\n' 2>/dev/null | awk '{s[$3]+=$1; d[$3]=$2} END {for (k in s) printf "  %8.1f MB %s %s\n", s[k]/1048576, d[k], k}' | sort -rn | head -25
echo "######## 끝"
