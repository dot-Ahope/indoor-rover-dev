#!/bin/bash
S() { echo "$SPW" | sudo -S -p '' "$@"; }
S true; S tail -n 15 /var/log/wifi_mon/mon.log | cut -c1-230; echo "--"; P=$(systemctl show -p MainPID --value wifi-mon); ps -o pid,ppid,stat,etime,args --ppid $P; for c in $(pgrep -P $P); do ps -o pid,ppid,stat,etime,args --ppid $c; done
S journalctl -u wifi-mon --no-pager -n 10 2>&1 | tail -6
