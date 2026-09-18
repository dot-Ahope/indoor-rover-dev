#!/bin/bash
# wpa_cli 모니터 재시험: 줄 버퍼(stdbuf -oL) + level 2. 5 s 뒤 scan 1 회. 설정 변경 없음.
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
( (echo "level 2"; sleep 20) | S timeout 22 stdbuf -oL -eL wpa_cli -i wlP1p1s0 2>&1 ) > /tmp/wpamon_test.txt &
sleep 5; S wpa_cli -i wlP1p1s0 scan >/dev/null 2>&1; wait
echo "받은 줄 $(wc -l < /tmp/wpamon_test.txt)"
echo "<수준> 분포: $(grep -aoE '<[0-9]>' /tmp/wpamon_test.txt | sort | uniq -c | tr '\n' ' ')"
grep -aE '<[0-9]>' /tmp/wpamon_test.txt | grep -avE 'passphrase|psk=' | head -30 | cut -c1-170 | sed 's/^/  /'
rm -f /tmp/wpamon_test.txt
