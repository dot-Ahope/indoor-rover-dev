#!/usr/bin/env python3
"""리포의 md 상대 링크 존재 검사 (debug_log·로컬 전용 폴더 제외). 인자: REPO_ROOT"""
import os, re, io, sys
ROOT = sys.argv[1]; LINK = re.compile(r'\]\(([^)\s#]+)(#[^)]*)?\)'); bad = 0; n = 0
SKIP = ('/.git', 'debug_log', 'Docs_Beginner', '전자회로기초', 'rover_jupiter_fw')
for dp, dn, fn in os.walk(ROOT):
    d = dp.replace(os.sep, '/')
    if any(k in d for k in SKIP):
        continue
    for f in fn:
        if not f.endswith('.md'):
            continue
        p = os.path.join(dp, f); s = io.open(p, encoding='utf-8', errors='replace').read()
        for m in LINK.finditer(s):
            t = m.group(1)
            if re.match(r'^[a-z]+:', t) or t.startswith('/'):
                continue
            n += 1
            if not os.path.exists(os.path.normpath(os.path.join(dp, t))):
                bad += 1; print('  깨짐 %s -> %s' % (os.path.relpath(p, ROOT).replace(os.sep, '/'), t))
print('상대 링크 %d 검사, 깨진 것 %d' % (n, bad))
sys.exit(1 if bad else 0)
