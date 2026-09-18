#!/bin/bash
# wpa_supplicant debug 로그 양 측정 60 s 후 원래 수준 복귀. 핸드셰이크 줄이 나오는지 보려고 중간에 scan 1 회.
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
ORIG=$(S wpa_cli log_level 2>&1 | awk -F': ' '/Current level/{print $2}'); echo "원래 수준: ${ORIG:-?}"
N0=$(wc -l < /var/log/syslog); B0=$(stat -c %s /var/log/syslog)
S wpa_cli log_level DEBUG | sed 's/^/  set: /'
sleep 10; S wpa_cli -i wlP1p1s0 scan >/dev/null; sleep 50
S wpa_cli log_level "${ORIG:-INFO}" | sed 's/^/  restore: /'
echo "복귀 후 수준: $(S wpa_cli log_level 2>&1 | awk -F': ' '/Current level/{print $2}')"
N1=$(wc -l < /var/log/syslog); B1=$(stat -c %s /var/log/syslog)
echo "60 s 동안 syslog +$((N1-N0)) 줄, +$(( (B1-B0)/1024 )) KiB → 하루 추정 $(( (B1-B0)*1440/1024/1024 )) MiB"
tail -n $((N1-N0)) /var/log/syslog | grep -a 'wpa_supplicant' | sed -E 's/^([A-Z][a-z]{2} +[0-9]+ [0-9:]+) [^ ]+ wpa_supplicant\[[0-9]+\]: /\1 /' | cut -c1-150 | awk '{c[$0 ~ /scan|Scan|BSS|bss/ ? "scan" : "other"]++} END {for (k in c) print "  종류", k, c[k]}'
tail -n $((N1-N0)) /var/log/syslog | grep -a 'wpa_supplicant' | grep -avE 'psk|passphrase|PMK|PTK' | sed -E 's/^([A-Z][a-z]{2} +[0-9]+ [0-9:]+) [^ ]+ wpa_supplicant\[[0-9]+\]: /\1 /' | cut -c1-150 | head -15 | sed 's/^/  /'
