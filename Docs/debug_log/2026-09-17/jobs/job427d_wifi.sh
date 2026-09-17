#!/bin/bash
# Wi-Fi 진단 4 (2026-09-17): SSH 세션 빈도(러너 폴링) vs AP 강제 끊김 시각. 읽기 전용.
L=/var/log/syslog
echo "######## A. 날짜별 SSH 세션 수·최대 10 분 세션 수 (Sep 1~17, systemd 'Started Session N of User jetson')"
grep -aE '^(Aug 2[5-9]|Aug 3[01]|Sep ( [0-9]|1[0-7])) .*systemd\[1\]: Started Session [0-9]+ of User jetson' $L | \
  awk '{d=$1" "$2; split($3,t,":"); b=t[1]":"int(t[2]/10)"0"; n[d]++; k[d" "b]++} END {for (x in k) {split(x,a," "); dd=a[1]" "a[2]; if (k[x]>mx[dd]) {mx[dd]=k[x]; at[dd]=a[3]}} for (d in n) printf "  %-7s 세션 %5d  | 최대 10분 %4d (@%s)\n", d, n[d], mx[d], at[d]}' | sort -k2,2n
echo "######## B. AP 끊김 전 60 분의 10 분 단위 세션 수"
for ts in "Sep 15 14:03" "Sep 16 15:57" "Sep 17 13:38"; do
  d="${ts:0:6}"; hh=${ts:7:2}; mm=${ts:10:2}; end=$((10#$hh*60+10#$mm)); start=$((end-60))
  printf '  %s →' "$ts"
  grep -aE "^$d .*systemd\[1\]: Started Session [0-9]+ of User jetson" $L | awk -v s=$start -v e=$end '{split($3,t,":"); m=t[1]*60+t[2]; if (m>=s && m<=e) c[int((m-s)/10)]++} END {for (i=0;i<=6;i++) printf " %d", c[i]+0; print ""}'
done
echo "  (비교: 끊김 없던 날의 가장 바쁜 10 분 — A 표의 최대값)"
echo "######## C. 끊김 당일 WEB_DEV_5G 연결 유지 시간 (연결 → reason=2)"
grep -aE 'CTRL-EVENT-CONNECTED - Connection to b0:38:6c:37:1b:4c|CTRL-EVENT-DISCONNECTED bssid=b0:38:6c:37:1b:4c reason=2$' $L | grep -aE '^(Sep 1[4-7]) ' | awk '{print "  ", $1, $2, $3, ($0 ~ /CONNECTED -/ ? "연결" : "AP 끊김 reason=2")}'
echo "######## 끝"
