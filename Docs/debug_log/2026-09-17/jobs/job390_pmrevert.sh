#!/bin/bash
# 25W 가 CPU 상한을 1344 MHz 로 낮춤(15W 는 1497) → 사용자 승인 범위의 원복: 15W(0)
echo "=== 모드별 CPU0 MAX_FREQ / GPU MAX / EMC (nvpmodel.conf) ==="
awk '/< POWER_MODEL ID=/{mode=$0} /CPU_A78_0 MAX_FREQ|GPU MAX_FREQ|EMC MAX_FREQ|CPU_ONLINE CORE_5/{print mode " :: " $0}' /etc/nvpmodel.conf | sed 's/< POWER_MODEL //; s/ >//' | head -12
echo "__PW__" | sudo -S -p "" sh -c 'nvpmodel -m 0 < /dev/null' 2>&1 | tail -2
sleep 3
echo "원복 후: $(nvpmodel -q 2>&1 | head -1)  cpu max: $(for c in 0 1 2 3 4 5; do printf "%s " $(( $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_max_freq)/1000 )); done) MHz"
