#!/usr/bin/env python3
# up_pw_old_1102 — settings.local.json 의 옛 sshpass 값을 저장소 밖 ~/.config/rover_jetson/pw 둘째 줄부터 더함(값 출력 없음, 11-02 §6 · README §8). 저장소 루트에서 실행.
import re, os
p = os.path.expanduser('~/.config/rover_jetson/pw')
lines = [l.strip() for l in open(p, encoding='utf-8').read().splitlines() if l.strip()]
s = open('.claude/settings.local.json', encoding='utf-8').read()
old = sorted(set(re.findall(r"sshpass -p (\S+) (?:ssh|scp) ", s)))
for v in old:
    if v not in lines: lines.append(v)
open(p, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')
print('줄 수', len(lines), '(첫 줄 = 지금 값)')
