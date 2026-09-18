#!/bin/bash
# logrotate 설치·예약 여부, ~/.ros/log 구성 (읽기 전용)
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
echo "== logrotate"
dpkg -l logrotate 2>&1 | tail -1 | cut -c1-80 | sed 's/^/  dpkg: /'
ls -la /usr/sbin/logrotate /etc/cron.daily/logrotate /lib/systemd/system/logrotate.timer /lib/systemd/system/logrotate.service 2>&1 | sed 's/^/  /'
S ls -la /var/lib/logrotate/ 2>&1 | sed 's/^/  /'
S head -5 /var/lib/logrotate/status 2>&1 | sed 's/^/  status: /'
echo "  /var/log 파일 수 $(S find /var/log -type f | wc -l), 회전본(.1/.gz) $(S find /var/log -type f \( -name '*.1' -o -name '*.gz' \) | wc -l)"
S ls -la /var/log/syslog* /var/log/kern.log* /var/log/auth.log* 2>&1 | awk '{print "  ", $5, $6, $7, $8, $9}'
echo "  lastlog 실제 사용 $(S du -k /var/log/lastlog | cut -f1) KB (겉보기 $(S stat -c %s /var/log/lastlog) B — 희소 파일)"
echo "== ~/.ros/log"
L=/home/jetson/.ros/log
echo "  항목 $(ls -1 $L | wc -l), 파일 $(find $L -type f | wc -l), 디렉터리 $(find $L -mindepth 1 -type d | wc -l), 합계 $(du -sh $L | cut -f1)"
ls -1 $L | sed -E 's/_[0-9]+_[0-9]+\.log$//; s/^[0-9]{4}-[0-9]{2}-[0-9]{2}-.*/(launch 디렉터리)/' | sort | uniq -c | sort -rn | head -12 | sed 's/^/   /'
echo "  최근 7 일 파일 $(find $L -type f -mtime -7 | wc -l), 30 일 넘은 파일 $(find $L -type f -mtime +30 | wc -l) ($(find $L -type f -mtime +30 -printf '%s\n' | awk '{s+=$1} END {printf "%.1f MB", s/1048576}'))"
