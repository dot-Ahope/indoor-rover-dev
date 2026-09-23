#!/bin/bash
# 11:55~12:07 끊김 창 전체: mon.log LINK/EVENT/ARP_DUP, wpa CTRL-EVENT·reason, NM 상태 변화 이유, 커널
echo "## mon.log (BEACON 제외)"; awk '$2>="11:55:00" && $2<="12:08:00"' /var/log/wifi_mon/mon.log | grep -av BEACON | cut -c1-150 | awk '{k=$3" "$9; if (k!=p || /EVENT|ARP|SNAP/) {print; p=k}}' | head -30
echo "## wpa (CTRL-EVENT·reason·SA Query)"; grep -aE "12:0[0-7]:|11:5[5-9]:" /var/log/wifi_mon/wpa_debug.log | grep -aE "CTRL-EVENT|reason|SA Query|deauth|disassoc|Beacon loss|BEACON-LOSS" | head -30 | cut -c1-170
echo "## NM (reason 포함 줄)"; journalctl -u NetworkManager --since "11:55" --until "12:07" --no-pager 2>/dev/null | grep -aE "reason '[a-z-]+'|dhcp4|DISCONNECTED|deauth" | grep -av "reason 'none'" | head -20 | cut -c1-170
echo "## 커널"; journalctl -k --since "11:55" --until "12:07" --no-pager 2>/dev/null | tail -10 | cut -c1-170
