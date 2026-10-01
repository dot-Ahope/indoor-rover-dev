#!/bin/bash
# 10-01 §8.9: 정지 상태(전체 스택 기동, Foxglove 닫음) 30 s 부하 기준선 — 코어 평균·us/sy, 프로세스별 CPU(전체 목록, 누적 틱 차),
#   ollama 모델 적재 여부, 화면 세션, 8765 연결
echo "8765 연결: $(ss -tn 2>/dev/null | grep -ac ':8765 ')"
echo "ollama: $(ollama ps 2>&1 | tail -n +2 | head -3 | tr '\n' ' ') | 프로세스 $(pgrep -fc 'ollama')"
declare -A T0; for p in /proc/[0-9]*; do id=${p#/proc/}; s=$(awk '{print $14+$15}' $p/stat 2>/dev/null) && T0[$id]=$s; done
S0=$(head -1 /proc/stat); sleep 30; S1=$(head -1 /proc/stat)
python3 - "$S0" "$S1" <<'PY'
import sys
a = list(map(int, sys.argv[1].split()[1:])); b = list(map(int, sys.argv[2].split()[1:])); d = [y - x for x, y in zip(a, b)]; tot = sum(d)
print('30 s 전체: us %.0f %% · sy %.0f %% · idle %.0f %% · irq+softirq %.0f %% (코어 평균 사용 %.0f %%)' % (d[0]/tot*100, d[2]/tot*100, d[3]/tot*100, (d[5]+d[6])/tot*100, (1-(d[3]+d[4])/tot)*100))
PY
echo "-- 프로세스별(30 s 평균, 2 % 이상):"
for p in /proc/[0-9]*; do id=${p#/proc/}; s=$(awk '{print $14+$15}' $p/stat 2>/dev/null) || continue; [ -n "${T0[$id]}" ] || continue
  d=$((s-${T0[$id]})); [ $d -ge 60 ] && printf "%6.1f %%  %-7s %s\n" $(awk -v d=$d 'BEGIN{print d/30}') $id "$(tr '\0' ' ' < $p/cmdline | cut -c1-110)"; done | sort -rn | head -30
