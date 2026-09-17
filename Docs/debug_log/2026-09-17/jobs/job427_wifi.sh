#!/bin/bash
# Wi-Fi 끊김·IP 전환 진단 (2026-09-17, 사용자 요청). 읽기 전용 — 설정 변경 없음, sudo 없음, 비밀번호 출력 금지.
IF=$(iw dev 2>/dev/null | awk '/Interface/{print $2; exit}'); IF=${IF:-wlP1p1s0}
echo "######## 1. 현재 상태 ($(date '+%F %T'), uptime $(uptime -p))"
echo "인터페이스 $IF"
iw dev $IF link 2>&1 | sed 's/^/  /'
echo "  power_save: $(iw dev $IF get power_save 2>&1)"
ip -4 addr show $IF | awk '/inet /{print "  IPv4", $2}'
ip route | sed 's/^/  route: /'
echo "  드라이버: $(basename $(readlink /sys/class/net/$IF/device/driver) 2>/dev/null), 펌웨어/모듈: $(lsmod | grep -E '^rtw|^rtl|^iwl|^brcm|^mt7' | awk '{print $1}' | tr '\n' ' ')"
echo "  MAC: $(cat /sys/class/net/$IF/address)"
iw reg get 2>&1 | head -3 | sed 's/^/  reg: /'

echo "######## 2. 저장 연결 (비밀 제외)"
nmcli -f NAME,TYPE,AUTOCONNECT,AUTOCONNECT-PRIORITY,DEVICE,ACTIVE con show 2>&1 | sed 's/^/  /'
for c in $(nmcli -t -f NAME,TYPE con show | awk -F: '$2=="802-11-wireless"{print $1}'); do
  echo "  -- $c"
  nmcli con show "$c" 2>/dev/null | grep -E '^(connection\.(autoconnect|autoconnect-priority|autoconnect-retries|auth-retries|timestamp)|802-11-wireless\.(ssid|mode|band|channel|bssid|mac-address|cloned-mac-address|powersave|seen-bssids|mac-address-randomization)|802-11-wireless-security\.(key-mgmt|pmf|proto|pairwise|group)|ipv4\.(method|addresses|dhcp-client-id)):' | grep -viE 'psk|password|secret|wep-key' | sed 's/^/     /'
done
grep -hE '^\s*(wifi\.|\[device|\[connection|mac-address)' /etc/NetworkManager/NetworkManager.conf /etc/NetworkManager/conf.d/*.conf 2>/dev/null | sed 's/^/  NM conf: /'

echo "######## 3. 주변 AP 스캔 (캐시; SSID·BSSID·채널·신호·보안)"
nmcli -f IN-USE,SSID,BSSID,CHAN,FREQ,SIGNAL,RATE,SECURITY dev wifi list 2>&1 | head -25 | sed 's/^/  /'

echo "######## 4. Wi-Fi 송수신량 (스택 가동 중 10 s)"
S=/sys/class/net/$IF/statistics
read t0 r0 m0 d0 e0 < <(echo $(cat $S/tx_bytes $S/rx_bytes $S/multicast $S/tx_dropped $S/tx_errors))
tp0=$(cat $S/tx_packets); rp0=$(cat $S/rx_packets)
sleep 10
read t1 r1 m1 d1 e1 < <(echo $(cat $S/tx_bytes $S/rx_bytes $S/multicast $S/tx_dropped $S/tx_errors))
tp1=$(cat $S/tx_packets); rp1=$(cat $S/rx_packets)
echo "  TX $(( (t1-t0)/10240 )) KiB/s ($(( (tp1-tp0)/10 )) pkt/s) | RX $(( (r1-r0)/10240 )) KiB/s ($(( (rp1-rp0)/10 )) pkt/s) | multicast rx +$((m1-m0)) | tx_dropped +$((d1-d0)) tx_errors +$((e1-e0))"
echo "  누적: tx_errors $(cat $S/tx_errors), tx_dropped $(cat $S/tx_dropped), rx_errors $(cat $S/rx_errors), rx_dropped $(cat $S/rx_dropped)"
echo "  wlan 소켓 상위(목적지별, UDP/TCP):"
ss -tunp 2>/dev/null | awk 'NR>1{print $1, $6}' | awk '{split($2,a,":"); ip=a[1]; if (ip !~ /^(127\.|\[::1\]|\*|0\.0\.0\.0)/) print $1, ip}' | sort | uniq -c | sort -rn | head -8 | sed 's/^/    /'
IP4=$(ip -4 addr show $IF | awk '/inet /{split($2,a,"/"); print a[1]}')
echo "  DDS 참가자 수신 주소(멀티캐스트 가입): $(ip maddr show $IF 2>/dev/null | grep -c inet) 그룹 — $(ip maddr show $IF 2>/dev/null | awk '/inet /{print $2}' | tr '\n' ' ')"

echo "######## 5. 부팅 이력"
last -x reboot 2>/dev/null | head -8 | sed 's/^/  /'

echo "######## 6. syslog Wi-Fi 이벤트 타임라인 (전 기간, 회전 파일 포함)"
PAT='CTRL-EVENT-(CONNECTED|DISCONNECTED|SSID-TEMP-DISABLED|SSID-REENABLED|ASSOC-REJECT|AUTH-REJECT|BEACON-LOSS|NETWORK-NOT-FOUND|SIGNAL-CHANGE)|WPA: 4-Way Handshake failed|pre-shared key may be incorrect|Activation: starting connection|state change: activated -> |device \(wl[^)]*\): state change: (disconnected|failed|prepare) |dhcp4 \([^)]*\): +address|new Wi-Fi network|Connection to AP|deauthenticat|disassociat|rtw88|rtw_8822|firmware.*(crash|error)|beacon loss|reason=[0-9]+'
for f in $(ls -1tr /var/log/syslog* 2>/dev/null); do
  echo "  == $f"
  if [[ $f == *.gz ]]; then zcat $f; else cat $f; fi 2>/dev/null | grep -aE "$PAT" | grep -avE 'SIGNAL-CHANGE' | \
    sed -E 's/^([A-Z][a-z]{2} +[0-9]+ [0-9:]{8}|[0-9T:.+-]{19,32}) [^ ]+ /\1 /' | cut -c1-230 | head -150 | sed 's/^/    /'
done
echo "  (읽기 권한: $(ls -l /var/log/syslog 2>&1 | awk '{print $1, $3, $4}'), 사용자 그룹: $(id -nG))"

echo "######## 7. 커널 메시지 (dmesg, 권한 있을 때)"
dmesg -T 2>&1 | grep -aiE 'rtw|wlan|wlP|802\.11|deauth|disassoc|firmware|pcie.*(error|AER)' | tail -30 | sed 's/^/  /'
grep -haiE 'rtw|wlP1p1s0: (deauth|disassoc|Connection|authenticate)|AER' /var/log/kern.log* 2>/dev/null | tail -30 | sed 's/^/  kern: /'
echo "######## 끝"
