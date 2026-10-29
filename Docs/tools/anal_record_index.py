#!/usr/bin/env python3
"""anal_record_index — 실험 기록 자동 색인 3 종 (2026-10-29, PC). 기록이 늘면 다시 돌려 덮어쓴다(손으로 고치지 않는다).
  입력: Docs/debug_log/<날짜>/{SUMMARY.md, jobs/, outputs/drives/, bags/(로컬)}  · Docs/tools/
  출력: Docs/issues/index/
    SECTIONS.md  날짜별 SUMMARY 제목(## · ###) — 검색 한 번으로 '그 얘기가 어느 날 몇 § 인지'
    RUNS.md      실험(주행 · 기록) 이름 대장 — bag_<이름> · outputs/drives/<이름> 에서 이름을 모으고, SUMMARY 에서 처음 · 마지막으로 나온 § 와 횟수
    JOBS.md      도구 사전 — jobs/ · Docs/tools/ 의 파일마다 첫 설명 줄 + SUMMARY 에서 언급된 § (번호 이름 job4xx 도 뜻을 찾게)
  한계: 이름 대장은 bag · drives 폴더가 있는 주행만(대략 09-1x 이후 — 그 전 주행 이름은 SECTIONS 에서 찾는다). bags/ 는 git 제외라 이 PC 에서 돌려야 한다.
  사용: python Docs/tools/anal_record_index.py   (저장소 루트 어디서든)"""
import os, re, sys
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]; LOG = ROOT / 'Docs' / 'debug_log'; OUT = ROOT / 'Docs' / 'issues' / 'index'
DATES = sorted(p.name for p in LOG.iterdir() if p.is_dir() and re.match(r'\d{4}-\d\d-\d\d$', p.name))
TOK = re.compile(r'[A-Za-z0-9_][A-Za-z0-9_.\-]*')
OUT.mkdir(parents=True, exist_ok=True)

def sec_short(h):   # 제목 줄 → 짧은 표기(§ 번호가 있으면 그것, 없으면 앞 40 자)
    m = re.match(r'#+\s*(§\s*[\d.]+|\d+(?:\.\d+)*\.?)', h)
    return (m.group(1).replace(' ', '') if m else h.lstrip('# ')[:40]).rstrip('.')

# ---- SUMMARY 읽기: 제목 목록 + 토큰 → (날짜, 제목) 위치
heads, where = [], defaultdict(list)   # where[token] = [(date, short, line)]
for d in DATES:
    f = LOG / d / 'SUMMARY.md'
    if not f.exists(): continue
    cur = '(머리)'
    for n, line in enumerate(f.read_text(encoding='utf-8', errors='replace').splitlines(), 1):
        if re.match(r'#{2,3}\s', line):
            cur = line.strip(); heads.append((d, n, cur))
        for t in set(TOK.findall(line)):
            if len(t) >= 3: where[t].append((d, sec_short(cur), n))

def mentions(name, limit=4):
    L = list(where.get(name, []))
    stem = os.path.splitext(name)[0]   # 옛 기록은 확장자 없이 부름(job4y) — 이름 대장은 stem == name 이라 겹치지 않음
    if stem != name and len(stem) >= 4: L += where.get(stem, [])
    L.sort()
    seen, out = set(), []
    for d, s, n in L:
        if (d, s) in seen: continue
        seen.add((d, s)); out.append('%s %s' % (d[5:], s))
    return len(L), out[:limit] + (['… +%d' % (len(out) - limit)] if len(out) > limit else [])

link = lambda d, n=None: '[%s](../../debug_log/%s/SUMMARY.md%s)' % (d, d, '#L%d' % n if n else '')
esc = lambda s: s.replace('|', '\\|')

# ---- SECTIONS.md
with open(OUT / 'SECTIONS.md', 'w', encoding='utf-8', newline='\n') as w:
    w.write('# SUMMARY 제목 색인 (자동 — `Docs/tools/anal_record_index.py`, 손으로 고치지 않음)\n\n')
    w.write('날짜 %d 개 · 제목 %d 개. 줄 번호는 생성 시점 기준.\n\n' % (len(DATES), len(heads)))
    for d in DATES:
        H = [h for h in heads if h[0] == d]
        if not H: continue
        w.write('## %s\n' % d)
        for _, n, h in H:
            ind = '  ' if h.startswith('###') else ''
            w.write('%s- [L%d](../../debug_log/%s/SUMMARY.md) %s\n' % (ind, n, d, esc(h.lstrip('# ')[:160])))
        w.write('\n')

# ---- RUNS.md
runs = defaultdict(set)
for d in DATES:
    b = LOG / d / 'bags'
    if b.exists():
        for p in b.iterdir():
            m = re.match(r'bag_([A-Za-z0-9_\-]+?)(\.tgz|\.tar\.gz)?$', p.name)
            if m: runs[m.group(1)].add(d)
    dr = LOG / d / 'outputs' / 'drives'
    if dr.exists():
        for p in dr.iterdir():
            if p.is_dir(): runs[p.name].add(d)
with open(OUT / 'RUNS.md', 'w', encoding='utf-8', newline='\n') as w:
    w.write('# 실험 이름 대장 (자동 — `Docs/tools/anal_record_index.py`)\n\n')
    w.write('이름 = bag_<이름> 또는 outputs/drives/<이름>. 언급 = SUMMARY 에서 그 이름이 나온 날짜 · § (처음 4 곳). bag 은 git 제외(이 PC 의 `bags/`).\n\n')
    w.write('| 이름 | 기록 폴더 | SUMMARY 언급 수 | 나온 곳 |\n|---|---|---|---|\n')
    for nm in sorted(runs, key=lambda k: (min(runs[k]), k)):
        c, ms = mentions(nm)
        w.write('| `%s` | %s | %d | %s |\n' % (nm, ' · '.join(sorted(runs[nm])), c, esc(' · '.join(ms)) or '—'))

# ---- JOBS.md
def desc(p):
    """첫 설명 줄: docstring 첫 줄 또는 앞 30 줄 안 첫 주석(셰뱅 · 인코딩 · 구분선 제외). 코드 줄이 먼저 와도 주석을 찾는다."""
    try: t = p.read_text(encoding='utf-8', errors='replace').splitlines()[:30]
    except Exception: return ''
    for i, l in enumerate(t):
        s = l.strip()
        if s.startswith(('"""', "'''")):
            s = s.strip('"\' ')
            if not s and i + 1 < len(t): s = t[i + 1].strip()
            if s: return s[:140]
        if s.startswith('#!') or s.startswith('# -*-'): continue
        if s.startswith(('#', '//', 'REM ', '::')):
            c = s.lstrip('#/: ').strip()
            if len(c) >= 4 and not set(c) <= set('-=*#~ '): return c[:140]
    # 주석이 없으면 셸 스크립트의 단계 제목(echo "===…===") 앞 3 개로 대신 — 표시 '(단계)'
    try: full = p.read_text(encoding='utf-8', errors='replace')
    except Exception: return ''
    st = [x.strip(' =-:') for x in re.findall(r'echo\s+(?:-e\s+)?["\']?\s*={2,}\s*([^"\'=\n]{2,60}?)\s*={2,}', full)]
    st = [x for x in st if x][:3]
    return ('(단계) ' + ' · '.join(st))[:140] if st else ''
rows = []
for d in DATES:
    j = LOG / d / 'jobs'
    if j.exists():
        for p in sorted(j.iterdir()):
            if p.is_file(): rows.append((d, p))
tools = sorted(p for p in (ROOT / 'Docs' / 'tools').iterdir() if p.is_file())
with open(OUT / 'JOBS.md', 'w', encoding='utf-8', newline='\n') as w:
    w.write('# 도구 사전 (자동 — `Docs/tools/anal_record_index.py`)\n\n')
    w.write('설명 = 파일 첫 설명 줄(docstring · 주석). 언급 = SUMMARY 에서 파일 이름이 나온 날짜 · §. 옛 번호 이름(job4xx)은 Docs/tools/README.md 의 대응표도 함께 본다.\n\n')
    w.write('## 상시 도구 Docs/tools/ (%d)\n\n| 파일 | 설명 | 언급 |\n|---|---|---|\n' % len(tools))
    for p in tools:
        c, ms = mentions(p.name, 3); w.write('| [`%s`](../../tools/%s) | %s | %s |\n' % (p.name, p.name, esc(desc(p)), esc(' · '.join(ms)) or '—'))
    cur = None
    for d, p in rows:
        if d != cur:
            cur = d; w.write('\n## %s (%d)\n\n| 파일 | 설명 | 언급 |\n|---|---|---|\n' % (d, sum(1 for x in rows if x[0] == d)))
        c, ms = mentions(p.name, 3)
        w.write('| [`%s`](../../debug_log/%s/jobs/%s) | %s | %s |\n' % (p.name, d, p.name, esc(desc(p)), esc(' · '.join(ms)) or '—'))
print('SECTIONS 제목 %d · RUNS 이름 %d · JOBS 파일 %d(+상시 %d) → %s' % (len(heads), len(runs), len(rows), len(tools), OUT))
