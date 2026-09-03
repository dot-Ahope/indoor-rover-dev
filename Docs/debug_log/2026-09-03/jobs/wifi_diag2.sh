#!/bin/bash
IF=wlP1p1s0
echo "== station dump =="; iw dev $IF station dump 2>/dev/null | grep -E "inactive|rx packets|tx packets|tx retries|tx failed|beacon loss|rx drop|signal:|rx bitrate|tx bitrate|connected time"
echo "== 같은 SSID의 AP 목록 (로밍 후보) =="; nmcli -f IN-USE,BSSID,SSID,CHAN,SIGNAL,FREQ dev wifi list --rescan no 2>/dev/null | grep -E "IN-USE|WEB_DEV" | head -8
echo "== kernel wifi 로그 30분 =="; journalctl -k --since "30 min ago" --no-pager 2>/dev/null | grep -iE "wlP1p1s0|rtw|rtl|wlan|deauth|disassoc|beacon" | tail -8
echo "== 이웃(라우터) 상태 =="; ip neigh show dev $IF | head -5
echo "== 5초 트래픽 =="; a=$(awk -v i=$IF '$1==i":"{print $2,$10}' /proc/net/dev); sleep 5; b=$(awk -v i=$IF '$1==i":"{print $2,$10}' /proc/net/dev); echo "$a $b" | awk '{printf "rx %.0f kB/s  tx %.0f kB/s\n", ($3-$1)/5/1024, ($4-$2)/5/1024}'
echo "== 실행 중 노드 =="; pgrep -af "foxglove|controller_server|slam_toolbox|ekf_node|rplidar|realsense" | awk '{print $2}' | sort | uniq -c | sort -rn | head -6
echo "== 접속 중 TCP 피어 (foxglove 8765 등) =="; ss -tn state established 2>/dev/null | awk 'NR>1{print $4" <- "$5}' | grep -vE "127\.0\.0\.1|::1" | head -6
