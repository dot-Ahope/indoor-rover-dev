#!/bin/bash
echo "=== nvpmodel.conf POWER_MODEL 블록 (CPU/GPU/EMC) ==="
awk '/POWER_MODEL ID=/{p=1} p && /CPU_ONLINE|FREQ|POWER_MODEL|EMC|GPU_POWER|CPU_A78/ {print}' /etc/nvpmodel.conf | grep -avE "^#" | head -60
echo "=== 현재 (10 s 뒤) ==="; sleep 10
for c in 0 1 2 3 4 5; do printf "cpu%s cur/max/min %s/%s/%s  " $c $(( $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_cur_freq)/1000 )) $(( $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_max_freq)/1000 )) $(( $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_min_freq)/1000 )); done; echo
echo "available: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_frequencies)"
echo "nvpmodel -q --verbose:"; nvpmodel -q --verbose 2>&1 | grep -aiE "cpu|freq|power mode" | head -12
