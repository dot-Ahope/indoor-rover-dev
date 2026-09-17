#!/bin/bash
echo "nvpmodel: $(nvpmodel -q 2>&1 | tr '\n' ' ' | cut -c1-120)"
echo "online CPUs: $(cat /sys/devices/system/cpu/online)  governor: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null)"
for c in /sys/devices/system/cpu/cpu[0-9]*; do printf "%s:%s/%s " $(basename $c) $(( $(cat $c/cpufreq/scaling_cur_freq 2>/dev/null || echo 0)/1000 )) $(( $(cat $c/cpufreq/scaling_max_freq 2>/dev/null || echo 0)/1000 )); done; echo " (MHz cur/max)"
echo "cpuinfo_max: $(( $(cat /sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq)/1000 )) MHz"
echo "jetson_clocks 흔적: $(systemctl is-active jetson-clocks 2>/dev/null) / nvfancontrol $(systemctl is-active nvfancontrol 2>/dev/null)"
grep -aE "nvpmodel|NV Power Mode" /var/log/syslog 2>/dev/null | grep -aE "^Sep 1[67]" | tail -4 | cut -c1-140
echo "thermal: $(for z in /sys/class/thermal/thermal_zone*; do printf "%s=%s " $(cat $z/type) $(( $(cat $z/temp)/1000 )); done)"
echo "throttle(cpufreq stats 없음 시 생략):"; cat /sys/devices/system/cpu/cpu0/cpufreq/stats/time_in_state 2>/dev/null | sort -k2 -n | tail -3 | tr '\n' ' '; echo
echo "load $(cut -d' ' -f1-3 /proc/loadavg)  uptime $(uptime -p)"
