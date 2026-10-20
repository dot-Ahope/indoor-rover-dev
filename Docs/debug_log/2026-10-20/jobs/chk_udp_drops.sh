#!/bin/bash
# 소켓별 UDP 버림(drops) 10 s 증가 → inode → 프로세스. 읽기만
snap() { awk 'NR>1 {print $10, $NF}' /proc/net/udp; }   # inode drops
declare -A M; for p in /proc/[0-9]*; do for f in $p/fd/*; do l=$(readlink $f 2>/dev/null); case "$l" in socket:*) i=${l#socket:[}; M[${i%]}]="${p#/proc/} $(cat $p/comm 2>/dev/null)";; esac; done; done 2>/dev/null
snap > /tmp/ud0; sleep 10; snap > /tmp/ud1
join <(sort /tmp/ud0) <(sort /tmp/ud1) | awk '{d=$3-$2; if (d>0) print d, $1}' | sort -rn | head -8 | while read d i; do echo "  10 s 버림 $d · inode $i · ${M[$i]:-(컨테이너 안이거나 모름)}"; done
echo "  전체 RcvbufErrors 증가: $(awk '/^Udp:/{n++} n==2 && /^Udp:/{print $6; exit}' /proc/net/snmp)"
