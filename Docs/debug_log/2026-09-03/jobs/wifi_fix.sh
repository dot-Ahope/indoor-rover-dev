#!/bin/bash
# Jetson: Wi-Fi power save OFF (런타임 + NM 영구), 근거: 절약모드 ON + NM 끊김 로그 없음 + 간헐 무응답
IF=wlP1p1s0
CON=$(nmcli -t -f DEVICE,CONNECTION dev status | grep "^$IF" | cut -d: -f2)
echo "<PW>" | sudo -S iw dev $IF set power_save off 2>/dev/null
echo "<PW>" | sudo -S nmcli con modify "$CON" 802-11-wireless.powersave 2 2>/dev/null
echo "power_save now: $(iw dev $IF get power_save)   NM(영구): $(nmcli -t -f 802-11-wireless.powersave con show "$CON")"
