#!/bin/bash
# 10-01 §8.7: CPU 포화(sy 30~40 %) 원인 찾기 — 지금(로버 정지, 스택 기동 상태) 상위 프로세스·python 명령줄·polkitd 호출자
echo "load $(cut -d' ' -f1-3 /proc/loadavg)"; top -b -n2 -d2 | awk '/^top -/{k++} k==2' | head -32 | tail -26
echo "-- python3 프로세스(명령줄·CPU):"; ps -eo pid,etimes,pcpu,args --sort=-pcpu | grep -a python3 | grep -av grep | cut -c1-170 | head -20
echo "-- tail -F·timeout 남은 것: $(pgrep -fc 'tail -n +1 -F') · ros2 cli: $(pgrep -fc 'ros2 (topic|param|lifecycle|service|run tf2)')"
echo "-- polkitd 최근 로그:"; journalctl -u polkit --since "-30 min" --no-pager 2>/dev/null | tail -8 | cut -c1-200
grep -a polkit /var/log/syslog | tail -8 | cut -c1-200
