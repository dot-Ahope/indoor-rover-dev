#!/bin/bash
# WEB_DEV_5G(ipTIME AX3000R, 5 GHz ch36·160 MHz = DFS 52~64 포함) 끊김이 DFS/채널 전환과 관련되는지 (2026-09-18). 읽기 전용.
L=/var/log/syslog
echo "######## A. 9월 채널 전환·규제 영역·비콘 관련 wpa_supplicant 이벤트 전부"
grep -aE '^(Aug|Sep) ' $L | grep -aE 'wpa_supplicant\[[0-9]+\]: wlP1p1s0: (CTRL-EVENT-(STARTED-CHANNEL-SWITCH|CHANNEL-SWITCH|REGDOM-CHANGE|BEACON-LOSS|BSS-REMOVED|DFS)|Associated with|CTRL-EVENT-CONNECTED)' | \
  grep -aE '^(Aug 2[5-9]|Aug 3[01]|Sep)' | sed -E 's/jetson-desktop //; s/wpa_supplicant\[[0-9]+\]: wlP1p1s0: //' | cut -c1-170 > /tmp/dfs_ev.txt
echo "  줄 수 $(wc -l < /tmp/dfs_ev.txt)"
echo "  -- 종류별 개수"
sed -E 's/^[A-Z][a-z]{2} +[0-9]+ [0-9:]+ //' /tmp/dfs_ev.txt | sed -E 's/(bssid=|with |to )[0-9a-f:]+/\1X/; s/\[id=[0-9]+ id_str=\]//' | sort | uniq -c | sort -rn | head -20 | sed 's/^/   /'
echo "######## B. AP 강제 끊김(reason=2) 직전 60 s ~ 직후 20 s 의 wpa_supplicant·NM·커널 무선 줄"
for ts in "Sep 15 14:03:13" "Sep 16 15:57:34" "Sep 17 13:38:42"; do
  e=$(date -d "2026-${ts:0:3}-${ts:4:2} ${ts:7}" +%s 2>/dev/null || date -d "$ts 2026" +%s)
  echo "  == $ts"
  grep -aE "^${ts:0:6} " $L | grep -aE 'wpa_supplicant|NetworkManager.*wlP1p1s0|kernel: .*(wlP|rtw|ACK|RTW|halrf|phydm|DFS|radar|CSA|channel)' | \
    while IFS= read -r line; do t="${line:0:15}"; s=$(date -d "2026 $t" +%s 2>/dev/null); d=$((s - e)); [ $d -ge -60 ] && [ $d -le 20 ] && echo "   $d  ${line:7}"; done | \
    sed -E 's/jetson-desktop //' | cut -c1-190 | head -30
done
echo "######## C. 정상 접속 때의 채널 전환 이벤트(드라이버가 접속마다 내는 것인지) — Associated 전후 3 s"
grep -aE '^(Aug|Sep) .*wpa_supplicant.*(Associated with b0:38:6c|STARTED-CHANNEL-SWITCH|CTRL-EVENT-CHANNEL-SWITCH)' $L | grep -aE '^(Aug 2[5-9]|Aug 3|Sep)' | sed -E 's/jetson-desktop //; s/wpa_supplicant\[[0-9]+\]: wlP1p1s0: //' | cut -c1-170 | tail -40 | sed 's/^/  /'
echo "######## 끝"
