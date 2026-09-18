#!/bin/bash
echo "호스트 $(hostname), $(uptime -p), 부팅 $(uptime -s)"
ip -4 -o addr show wlP1p1s0 | awk '{print "IPv4", $4}'
iw dev wlP1p1s0 link | grep -E "Connected|SSID|freq|signal|bitrate" | sed 's/^/  /'
echo "  power_save: $(iw dev wlP1p1s0 get power_save 2>&1)"
echo "-- 09-17 18:00 이후 Wi-Fi 이벤트"
grep -aE '^Sep 1[78] ' /var/log/syslog | grep -aE 'wpa_supplicant\[[0-9]+\]: wlP1p1s0: (CTRL-EVENT|Associated|Trying)|NetworkManager.*(Activation: starting|state change: activated|new lease|no-secrets|link timed out)|systemd\[1\]: (Started Network Manager|Reached target Shutdown|Shutting down)' | \
  awk '{split($3,t,":"); if ($2 == 18 || ($2 == 17 && t[1] >= 18)) print}' | sed -E 's/jetson-desktop //' | cut -c1-190 | head -40
