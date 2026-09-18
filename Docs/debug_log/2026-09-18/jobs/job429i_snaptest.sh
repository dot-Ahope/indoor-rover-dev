#!/bin/bash
# 사건 스냅샷 함수 단독 시험(네트워크 변경 없음). 결과 파일은 확인 후 test_ 접두로 남긴다.
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
cat > /tmp/snaptest.sh <<'T'
IF=wlP1p1s0; AP=b0:38:6c:37:1b:4c; D=/var/log/wifi_mon; M=/tmp/snaptest_mon.log
log() { echo "$(date '+%F %T') $*" >> $M; }
T
sed -n '/^snapshot() {/,/^}/p' /usr/local/sbin/wifi_mon.sh >> /tmp/snaptest.sh
echo 'snapshot "TEST (수동 시험, 사건 아님)"' >> /tmp/snaptest.sh
S bash /tmp/snaptest.sh
F=$(S ls -t /var/log/wifi_mon/ | grep '^event_' | head -1)
S mv /var/log/wifi_mon/$F /var/log/wifi_mon/test_$F
echo "파일 test_$F: $(S wc -l < /var/log/wifi_mon/test_$F) 줄, 크기 $(S stat -c %s /var/log/wifi_mon/test_$F) B"
S grep -aE '^(###|---)' /var/log/wifi_mon/test_$F
echo "비밀 문자열 검사(psk|passphrase|password 값): $(S grep -aciE 'psk=|passphrase=|password' /var/log/wifi_mon/test_$F)"
echo "wpa debug 발췌:"; S grep -aE 'wpa_supplicant' /var/log/wifi_mon/test_$F | head -3 | cut -c1-150
