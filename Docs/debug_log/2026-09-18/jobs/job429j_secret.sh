#!/bin/bash
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
F=$(S ls -t /var/log/wifi_mon/ | grep '^test_event_' | head -1)
S grep -aiE 'psk=|passphrase=|password' /var/log/wifi_mon/$F | sed -E 's/(psk=|passphrase=)[^ ]*/\1<MASK>/Ig' | cut -c1-200
echo "wpa_debug.log 전체에서 같은 검사: $(S grep -aciE 'psk=|passphrase=' /var/log/wifi_mon/wpa_debug.log) 줄 (password 단어 제외)"
S grep -aiE 'psk=|passphrase=' /var/log/wifi_mon/wpa_debug.log | sed -E 's/(psk=|passphrase=)[^ ]*/\1<MASK>/Ig' | cut -c1-160 | head -5
