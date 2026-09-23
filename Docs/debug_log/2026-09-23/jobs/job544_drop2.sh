#!/bin/bash
echo "## 트레이스 12:17~12:21"; awk '$1>="12:17:00" && $1<="12:21:30"' /tmp/j540_trace.txt
echo "## wpa/NM/kernel 12:17~12:21"; grep -aE "Sep 23 12:(1[7-9]|2[01]):" /var/log/wifi_mon/wpa_debug.log | grep -aE "CTRL-EVENT|reason|deauth|disassoc" | head -10 | cut -c1-160; journalctl -u NetworkManager --since 12:17 --until 12:22 --no-pager | grep -av "reason .none." | tail -8 | cut -c1-160; journalctl -k --since 12:17 --until 12:22 --no-pager | tail -5 | cut -c1-160
echo "## sshd 12:17~12:21"; journalctl -u ssh --since 12:17 --until 12:22 --no-pager | tail -8 | cut -c1-160
echo "ARP_DUP: $(grep -ac ARP_DUP /var/log/wifi_mon/mon.log)"
