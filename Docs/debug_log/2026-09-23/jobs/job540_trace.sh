#!/bin/bash
# 끊김 중 온보드 기록(읽기 전용): 1) 끊김 시각대 로그 요약(job539) 2) 2 s 마다 IP·링크·게이트웨이 핑·ARP 테이블 게이트웨이 MAC 을 30 분간
bash /tmp/job539.sh > /tmp/j539.txt 2>&1
END=$(( $(date +%s) + 1800 ))
while [ $(date +%s) -lt $END ]; do
  ip4=$(ip -4 -o addr show dev wlP1p1s0 | awk '{print $4}')
  lk=$(iw dev wlP1p1s0 link | awk '/Connected/{print $3} /signal/{print $2}' | tr '\n' ' ')
  gw=$(ping -c1 -W1 192.168.0.1 >/dev/null 2>&1 && echo ok || echo X)
  gmac=$(ip neigh show 192.168.0.1 | awk '{print $5, $NF}')
  echo "$(date +%T) ip=$ip4 link=$lk gw=$gw neigh=$gmac"
  sleep 2
done > /tmp/j540_trace.txt 2>&1
