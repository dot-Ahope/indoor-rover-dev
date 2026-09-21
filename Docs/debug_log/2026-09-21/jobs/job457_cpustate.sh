#!/bin/bash
echo "nvpmodel: $(nvpmodel -q 2>/dev/null | tr '\n' ' ') | jetson_clocks 상태: $(sudo -n jetson_clocks --show 2>/dev/null | grep -c MaxFreq= || echo 'sudo 불가')"
echo "CPU governor/freq: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor) $(for c in 0 1 2 3 4 5; do printf '%s ' $(( $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_cur_freq 2>/dev/null || echo 0) / 1000 )); done)MHz (max $(( $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq) / 1000 )))"
echo "online cpus: $(cat /sys/devices/system/cpu/online) | load $(cut -d' ' -f1-3 /proc/loadavg) | 온도 $(cat /sys/devices/virtual/thermal/thermal_zone0/temp 2>/dev/null)"
echo "idle top 8:"; top -b -n2 -d1 -o %CPU 2>/dev/null | awk '/PID +USER/{f++} f==2' | head -9 | awk 'NR>1{printf "  %-26s %6s%%\n", $12, $9}'
echo "sensors.log EKF 위반 누적: $(grep -ac 'Failed to meet update rate' /tmp/sensors.log) | slam 폐기 $(grep -ac 'Message Filter dropping' /tmp/slam.log)"
echo "ekf 주기 관련 마지막 3줄:"; grep -a "update rate\|Timestamp" /tmp/sensors.log | tail -3 | cut -c1-150
echo "docker stats(에이전트):"; timeout 8 docker stats --no-stream --format '  {{.Name}} {{.CPUPerc}}' 2>/dev/null
echo "dmesg 최근(throttle/thermal/usb):"; dmesg 2>/dev/null | tail -300 | grep -aiE "thermal|throttl|usb.*(reset|disconnect)|over-current" | tail -4 | cut -c1-140
