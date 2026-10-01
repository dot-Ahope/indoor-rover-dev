#!/bin/bash
# 10-01 §8.7: ① 고아 nav_guard 정리(55 분 전 것) ② polkitd CPU 가 nmcli(OLED 정보 노드 3 s 마다) 때문인지 — polkitd 누적 CPU 를 20 s 그냥 vs nmcli 20 회 호출하며 비교
O=$(ps -eo pid,etimes,args | awk '/nav_guard.py/ && !/awk/ && $2>1200 {print $1}'); echo "고아 nav_guard: ${O:-없음}"; [ -n "$O" ] && kill $O; sleep 1; echo "nav_guard 남은 수: $(pgrep -fc nav_guard.py)"
P=$(pgrep -x polkitd); tick() { awk '{print $14+$15}' /proc/$P/stat; }
a=$(tick); sleep 20; b=$(tick); echo "polkitd 20 s(평소, OLED 노드 동작 중): $(( (b-a) ))틱 = $(awk -v t=$((b-a)) 'BEGIN{printf "%.1f", t/100/20*100}') %"
a=$(tick); for i in $(seq 1 20); do nmcli -t -f DEVICE,TYPE,CONNECTION device >/dev/null; sleep 1; done; b=$(tick); echo "polkitd 20 s(nmcli 추가 20 회): $(( (b-a) ))틱 = $(awk -v t=$((b-a)) 'BEGIN{printf "%.1f", t/100/20*100}') %"
a=$(tick); for i in $(seq 1 20); do ip -4 route get 1.1.1.1 >/dev/null; sleep 1; done; b=$(tick); echo "polkitd 20 s(ip route 20 회 — 비교): $(( (b-a) ))틱 = $(awk -v t=$((b-a)) 'BEGIN{printf "%.1f", t/100/20*100}') %"
echo "%Cpu 요약(2 s): $(top -b -n2 -d2 | grep '%Cpu' | tail -1)"
