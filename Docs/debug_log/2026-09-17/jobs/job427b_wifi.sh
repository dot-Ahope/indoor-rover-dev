#!/bin/bash
# Wi-Fi 진단 2 (2026-09-17): 9월 syslog 이벤트 타임라인 + 새 스캔. 읽기 전용, sudo 없음, 비밀 출력 없음.
IF=wlP1p1s0
echo "######## A. syslog 크기·기간"
ls -la /var/log/syslog* 2>&1 | sed 's/^/  /'
head -c 200 /var/log/syslog | head -1 | cut -c1-60 | sed 's/^/  첫 줄: /'
echo "######## B. 9월 Wi-Fi 이벤트 (wpa_supplicant 전부 + NM 핵심)"
grep -aE '^Sep ( [0-9]|1[0-9]) ' /var/log/syslog | grep -aE \
 'wpa_supplicant\[[0-9]+\]: wlP1p1s0: (CTRL-EVENT-(CONNECTED|DISCONNECTED|SSID-TEMP-DISABLED|SSID-REENABLED|ASSOC-REJECT|AUTH-REJECT|BEACON-LOSS|NETWORK-NOT-FOUND|SCAN-FAILED|REGDOM-CHANGE)|WPA: |SME: |Trying to associate|Associated with|Authentication with .* timed out|PMKSA)|NetworkManager\[[0-9]+\]: .*(wlP1p1s0|Wi-Fi|wifi).*(Activation: starting connection|state change: activated -> |state change: [a-z]+ -> failed|supplicant interface state: completed|new lease|address=|auto-activating|association took too long|secrets|link timed out|disconnected .*reason|Activation: failed)|NetworkManager\[[0-9]+\]: <info>  \[[0-9.]+\] manager: (NetworkManager state is now|startup complete)|kernel: .*wlP1p1s0' | \
 sed -E 's/jetson-desktop //; s/NetworkManager\[[0-9]+\]: <[a-z]+> +\[[0-9.]+\] /NM: /; s/wpa_supplicant\[[0-9]+\]: wlP1p1s0: /wpa: /' | cut -c1-200 > /tmp/wifi_sep.txt
echo "  이벤트 $(wc -l < /tmp/wifi_sep.txt) 줄"
grep -aE 'wpa: CTRL-EVENT-(DISCONNECTED|SSID-TEMP-DISABLED|ASSOC-REJECT|AUTH-REJECT|BEACON-LOSS|NETWORK-NOT-FOUND)|Activation: starting connection|new lease|address=|state change: activated -> |failed' /tmp/wifi_sep.txt | sed 's/^/  /' | head -220
echo "######## C. 날짜별 요약 (DISCONNECTED reason / TEMP-DISABLED / ASSOC-REJECT)"
for d in $(awk '{print $1"_"$2}' /tmp/wifi_sep.txt | sort -u); do
  dd=${d/_/ }; L=$(grep -a "^$dd " /tmp/wifi_sep.txt)
  printf '  %-7s DISCONNECTED %2d (%s) | TEMP-DISABLED %d | ASSOC-REJECT %d | 연결 시작: %s\n' "$dd" \
    "$(echo "$L" | grep -ac 'CTRL-EVENT-DISCONNECTED')" "$(echo "$L" | grep -aoE 'DISCONNECTED bssid=[0-9a-f:]+ reason=[0-9]+( locally_generated=1)?' | sed -E 's/DISCONNECTED bssid=//' | sort | uniq -c | tr -s ' ' | tr '\n' ';')" \
    "$(echo "$L" | grep -ac 'TEMP-DISABLED')" "$(echo "$L" | grep -ac 'ASSOC-REJECT')" \
    "$(echo "$L" | grep -aoE "starting connection '[^']+'" | sed -E "s/starting connection //" | sort | uniq -c | tr -s ' ' | tr '\n' ' ')"
done
echo "######## D. 새 스캔"
nmcli -f IN-USE,SSID,BSSID,CHAN,FREQ,SIGNAL,SECURITY dev wifi list --rescan yes 2>&1 | head -30 | sed 's/^/  /'
echo "  -- iw scan dump (캐시, 5 GHz 포함)"
iw dev $IF scan dump 2>&1 | awk '/^BSS /{b=$2} /freq:/{f=$2} /signal:/{s=$2" "$3} /SSID:/{print "  ", b, f, s, $0} /Authentication suites/{print "      auth:", $0} /Capabilities:.*MFP|PMF|MFP-/{print "      ", $0}' | head -40
echo "######## E. NM 동작 설정"
nmcli general 2>&1 | sed 's/^/  /'
NetworkManager --version 2>/dev/null | sed 's/^/  NM /'; wpa_supplicant -v 2>/dev/null | head -1 | sed 's/^/  /'
modinfo rtl88x2ce 2>/dev/null | grep -E '^(version|filename|srcversion)' | sed 's/^/  /'
cat /sys/module/rtl88x2ce/parameters/rtw_power_mgnt /sys/module/rtl88x2ce/parameters/rtw_ips_mode /sys/module/rtl88x2ce/parameters/rtw_lps_level 2>/dev/null | tr '\n' ' ' | sed 's/^/  드라이버 절전 파라미터(power_mgnt ips_mode lps_level): /'; echo
ls /sys/module/rtl88x2ce/parameters/ 2>/dev/null | tr '\n' ' ' | cut -c1-400 | sed 's/^/  파라미터 목록: /'; echo
echo "######## 끝"
