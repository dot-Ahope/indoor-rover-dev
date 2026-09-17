import sys
p = sys.argv[1]; NL = chr(10)
s = open(p, encoding='utf-8').read()
old = 'echo "  프로세스 14/14 단일, 보드 $BR"' + NL
new = old + ('SA=$(python3 /tmp/job386_slamalive.py 2>&1 | grep -av "^\[")' + NL).replace('\\', chr(92)) + \
      'echo "  SLAM: $(echo "$SA" | head -1)"' + NL + \
      '[ "$(echo "$SA" | tail -1)" = "OK" ] || { echo "  ★ SLAM map->odom 불량 — 중단 (09-17 mp7: 끊긴 채 출발하면 BT 타임아웃·복구·실패)"; exit 1; }' + NL
assert s.count(old) == 1
open(p, 'w', encoding='utf-8', newline=NL).write(s.replace(old, new)); print('job254 patched')
q = sys.argv[2]
t = open(q, encoding='utf-8').read()
old2 = 'for f in job254_s4run.sh job231_drive.sh job125_avoid3.py job248_audit.py job315_boxcells.py; do'
assert t.count(old2) == 1
open(q, 'w', encoding='utf-8', newline=NL).write(t.replace(old2, 'for f in job254_s4run.sh job231_drive.sh job125_avoid3.py job248_audit.py job315_boxcells.py job386_slamalive.py; do')); print('runner patched')
