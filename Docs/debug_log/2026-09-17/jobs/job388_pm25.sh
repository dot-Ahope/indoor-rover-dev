#!/bin/bash
# 사용자 승인(09-17): 전력 모드 15W(0) → 25W(1). 전후 확인.
echo "=== DDS 패키지 버전 ==="
for p in ros-humble-fastrtps ros-humble-fastcdr ros-humble-rmw-fastrtps-cpp ros-humble-rmw-cyclonedds-cpp ros-humble-cyclonedds; do printf "  %-34s 설치 %-28s 후보 %s\n" $p "$(dpkg-query -W -f='${Version}' $p 2>/dev/null || dpkg -s $p 2>/dev/null | awk '/^Version/{print $2}')" "$(apt-cache policy $p 2>/dev/null | awk '/Candidate/{print $2}')"; done
echo "=== 전력 모드 전환 ==="
echo "  전: $(nvpmodel -q 2>&1 | head -1)  cpu0 max $(( $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_max_freq)/1000 )) MHz"
echo "__PW__" | sudo -S -p "" sh -c 'nvpmodel -m 1 < /dev/null' 2>&1 | tail -3
sleep 3
echo "  후: $(nvpmodel -q 2>&1 | head -1)  cpu max: $(for c in 0 1 2 3 4 5; do printf "%s " $(( $(cat /sys/devices/system/cpu/cpu$c/cpufreq/scaling_max_freq)/1000 )); done) MHz  online $(cat /sys/devices/system/cpu/online)"
echo "  온도: $(for z in /sys/class/thermal/thermal_zone0 /sys/class/thermal/thermal_zone1; do printf "%s=%s " $(cat $z/type) $(( $(cat $z/temp)/1000 )); done)"
export FASTRTPS_DEFAULT_PROFILES_FILE=/home/jetson/ros2_ws/install/rover_bringup/share/rover_bringup/config/fastdds_udp_only.xml; source /opt/ros/humble/setup.bash
printf "  배터리: "; timeout 6 ros2 topic echo /battery --once 2>/dev/null | grep -aoE "voltage: [0-9.]+" || echo "(읽기 실패)"
