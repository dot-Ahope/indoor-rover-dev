#!/bin/bash
echo "status: $(cat /var/lib/nvpmodel/status 2>&1)  mtime: $(stat -c %y /var/lib/nvpmodel/status 2>&1 | cut -c1-19)"
echo "conf 기본: $(grep -aE '^< PM_CONFIG DEFAULT' /etc/nvpmodel.conf)"
grep -aE "POWER_MODEL ID" /etc/nvpmodel.conf | tr '\n' ' '; echo
echo "부팅 기록:"; last -x reboot 2>/dev/null | head -4
echo "syslog nvpmodel/Power mode (9/15~):"; grep -ahE "nvpmodel|Power Mode|power mode" /var/log/syslog /var/log/syslog.1 2>/dev/null | grep -avE "Starting|Finished|Deactivated" | tail -6 | cut -c1-160
echo "nvpmodel 로그: $(ls -la /var/log/nvpmodel* 2>/dev/null)"
