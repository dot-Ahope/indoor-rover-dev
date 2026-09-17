#!/bin/bash
# Wi-Fi 진단 3 (2026-09-17): 전체 기간 AP 별 끊김 집계 + AP 강제 끊김(reason=2) 전후 ±90 s 의 다른 syslog 사건. 읽기 전용.
L=/var/log/syslog
echo "######## A. 전체 기간 DISCONNECTED 집계 (bssid·reason·locally_generated)"
grep -aoE 'CTRL-EVENT-DISCONNECTED bssid=[0-9a-f:]+ reason=[0-9]+( locally_generated=1)?' $L | sed 's/CTRL-EVENT-DISCONNECTED //' | sort | uniq -c | sed 's/^/  /'
echo "  -- AP 가 보낸 끊김(locally_generated 없음) 날짜별"
grep -aE 'CTRL-EVENT-DISCONNECTED bssid=[0-9a-f:]+ reason=[0-9]+$' $L | awk '{print $1, $2, $NF, $(NF-1)}' | sort | uniq -c | sed 's/^/  /'
echo "  -- WRONG_KEY / 4-Way Handshake failed 날짜"
grep -aE 'WRONG_KEY|4-Way Handshake failed' $L | awk '{print $1, $2, $3}' | sed 's/^/  /'
echo "  -- 연결 성공(CTRL-EVENT-CONNECTED) bssid 별·월별"
grep -aoE '^[A-Z][a-z]{2} .*CTRL-EVENT-CONNECTED - Connection to [0-9a-f:]+' $L | awk '{print $1, $NF}' | sort | uniq -c | sed 's/^/  /'
echo "######## B. AP 강제 끊김(reason=2) 전후 ±90 s 사건 (Wi-Fi 이벤트·반복 잡음 제외)"
for ts in "Sep 15 14:03:13" "Sep 16 15:57:34" "Sep 17 13:38:42"; do
  e=$(date -d "2026-${ts#* }" +%s 2>/dev/null || date -d "$ts 2026" +%s)
  echo "  == $ts"
  grep -aE "^${ts:0:6} " $L | awk -v e=$e -v y=2026 '{
      cmd = "date -d \"" $1 " " $2 " " y " " $3 "\" +%s"; cmd | getline s; close(cmd);
      d = s - e; if (d >= -90 && d <= 90) print d, $0 }' 2>/dev/null | \
    grep -avE 'dhcp4 .*new lease|CTRL-EVENT-SSID-TEMP-DISABLED|CTRL-EVENT-DISCONNECTED bssid=b0:38:6c:37:1b:4c reason=23|gnome-shell|tracker-miner|org.gnome|pulseaudio|rtkit|gsd-|dbus-daemon.*activating|systemd-resolved.*Using degraded' | \
    sed -E 's/jetson-desktop //' | cut -c1-200 | head -40 | sed 's/^/    /'
done
echo "######## C. 로버 스택 기동 시각 vs AP 끊김 — 같은 날 docker 에이전트·launch 사건"
grep -aE '^Sep 1[5-7] .*(docker(d)?\[[0-9]+\]|containerd).*(start|create|veth|Starting|container)' $L | awk '{print $1, $2, $3}' | uniq -c | tail -20 | sed 's/^/  /'
grep -aE '^Sep 1[5-7] .*kernel: .*(veth|docker0|br-)' $L | sed -E 's/jetson-desktop //' | cut -c1-150 | tail -20 | sed 's/^/  /'
echo "######## 끝"
