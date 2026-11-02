#!/usr/bin/env python3
# chk_leak_scan_1102 — .claude/settings.local.json 의 sshpass -p 값 종류를 뽑아(값 출력 없음) 지금 값과 같은지 · 공개 dev/main · 원본 이력과 현재 트리에서 어디에 있는지 센다 (11-02 §6, PC, 로버 안 움직임). 저장소 루트에서 실행.
import re, subprocess, os, sys
sys.stdout.reconfigure(encoding='utf-8')
s = open('.claude/settings.local.json', encoding='utf-8').read()
cur = open(os.path.expanduser('~/.config/rover_jetson/pw'), encoding='utf-8').read().strip()
vals = set(re.findall(r"sshpass -p (\S+) (?:ssh|scp) ", s))
print('서로 다른 값', len(vals), [('현재와 같음' if v == cur else '다름', len(v)) for v in vals])
for i, v in enumerate(sorted(vals)):
    for ref in ['public/dev', 'public/main', 'feature/nvblox-migration']:
        cs = subprocess.run(['git', 'log', ref, '--format=%h', '-S', v], capture_output=True, text=True).stdout.split()
        f = subprocess.run(['git', 'grep', '-l', '-F', v, ref], capture_output=True, text=True).stdout.split()
        print('값%d' % i, ref, '그 값을 넣거나 뺀 커밋', len(cs), '현재 트리 파일', [x.split(':', 1)[1] for x in f])
