#!/bin/bash
echo "=== 현재 상태 ==="; uptime; free -m | sed -n '2p'; nproc
echo "=== ~/.bashrc 꼬리 (자동 실행 의심 구간) ==="; tail -25 ~/.bashrc | grep -vE '^\s*#|^\s*$' | cut -c1-140
echo "=== ~/.profile / ~/.bash_profile 사용자 추가 ==="; for f in ~/.profile ~/.bash_profile ~/.bash_login; do [ -f $f ] && { echo "-- $f"; grep -vE '^\s*#|^\s*$' $f | tail -8 | cut -c1-140; }; done
echo "=== 이전 부팅 종료 원인 (journal -b -1) ==="; journalctl -b -1 --no-pager -p 3 2>/dev/null | tail -12 | cut -c1-160
echo "--- OOM/hung/wlan 키워드 ---"; journalctl -b -1 --no-pager 2>/dev/null | grep -iaE 'out of memory|oom-kill|killed process|hung task|wlan0|brcmfmac|iwlwifi|rtw|thermal|throttl|watchdog' | tail -12 | cut -c1-160
echo "--- 이전 부팅 마지막 20줄 ---"; journalctl -b -1 --no-pager 2>/dev/null | tail -20 | cut -c1-160
echo "=== 이번 부팅 오류 ==="; journalctl -b 0 --no-pager -p 3 2>/dev/null | tail -8 | cut -c1-160
echo "=== 네트워크 ==="; nmcli -t dev status 2>/dev/null; nmcli -t -f NAME,DEVICE,STATE con show --active 2>/dev/null; ip -4 -br addr 2>/dev/null; iw dev 2>/dev/null | grep -E 'Interface|ssid|txpower' ; cat /sys/module/*/parameters/power_save 2>/dev/null | head -2; iw dev wlan0 get power_save 2>/dev/null
echo "=== 프로세스 ==="; docker ps --format '{{.Names}} {{.Status}}' 2>/dev/null; ps -eo pid,etimes,rss,args --sort=-rss | grep -aE 'ros2|python3|slam|nav2|realsense|rplidar|micro' | grep -av grep | head -8 | cut -c1-140
echo "=== sshd 로그(이번 부팅, 최근) ==="; journalctl -b 0 -u ssh --no-pager 2>/dev/null | tail -6 | cut -c1-160
