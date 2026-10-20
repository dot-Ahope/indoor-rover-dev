#!/bin/bash
head -3 /proc/net/udp | cut -c1-200; echo "소켓 수 $(($(wc -l < /proc/net/udp)-1)) · drops>0 소켓: $(awk 'NR>1 && $NF>0' /proc/net/udp | wc -l)"
e() { awk '/^Udp:/{n++} n==2 && /^Udp:/{print $6; exit}' /proc/net/snmp; }
a=$(e); awk 'NR>1 {s+=$NF} END {print s}' /proc/net/udp > /tmp/sd0; sleep 10; b=$(e); awk 'NR>1 {s+=$NF} END {print s}' /proc/net/udp > /tmp/sd1
echo "10 s: RcvbufErrors +$((b-a)) · 소켓 drops 합 $(cat /tmp/sd0) → $(cat /tmp/sd1)"
awk 'NR>1 && $NF>0 {print $NF, $2, $10}' /proc/net/udp | sort -rn | head -5
