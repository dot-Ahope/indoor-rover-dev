#!/bin/bash
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true
for p in $(pgrep -f /usr/local/sbin/wifi_mon.sh); do echo "== $p: wchan=$(cat /proc/$p/wchan 2>/dev/null) stat=$(awk '{print $3}' /proc/$p/stat)"; S ls -la /proc/$p/fd 2>/dev/null | awk '{print "   ", $9, $10, $11}' | tail -n +2; done
echo "== scan_ap 함수만 떼어 bash -x 로 20 s"
sed -n '/^scan_ap() {/,/^}/p' /usr/local/sbin/wifi_mon.sh > /tmp/scan_ap_fn.sh
cat > /tmp/scan_ap_test.sh <<'T'
IF=wlP1p1s0; AP=b0:38:6c:37:1b:4c
source /tmp/scan_ap_fn.sh
scan_ap 5180
T
S timeout 20 bash -x /tmp/scan_ap_test.sh 2>&1 | cut -c1-160 | tail -25; echo "rc=${PIPESTATUS[0]}"
