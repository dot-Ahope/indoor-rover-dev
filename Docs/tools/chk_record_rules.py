#!/usr/bin/env python3
"""chk_record_rules — 작업 규약(Docs/debug_log/README.md)의 기계로 볼 수 있는 부분을 점검하고 **경고만** 한다 (2026-11-02, PC, 로버 안 움직임).
  보는 것(규약 절):
    T  날짜 폴더(10-13~)에 TOOLS.md 가 없음                         (§3.3)
    N  jobs/ · Docs/tools/ 새 .py/.sh 이름에 용도 앞머리가 없음         (§3.1; 옛 이름 사본 job<숫자>… 은 제외)
    H  스크립트 첫 10 줄에 설명 주석이 없음                            (§3.2)
    L  md 의 상대 링크 [..](경로) 가 가리키는 파일이 없음               (깨진 링크)
    P  SUMMARY · TOOLS 에 적힌 jobs/ · outputs/ · figures/ 경로가 없음   (§2.3 데이터 칸; bags/ 는 git 제외라 안 봄)
    S  커밋 대상(staged)에 Jetson 비밀번호가 있음                       (§8; ROVER_RUNNER=<run_jn.sh 경로> 일 때만, 값은 출력 안 함)
  대상: 기본 = git 에서 바뀐 파일(staged + unstaged + 새 파일)과 그 날짜 폴더. --all = 10-13 이후 날짜 폴더 전부.
  인자: [--all] [--strict(경고가 있으면 종료 코드 1)]
  출력: 표준 출력에 '[분류] 경로 — 내용' 한 줄씩, 마지막 줄 'RULES_OK' 또는 'RULES_WARN <개수>'."""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DL = ROOT / 'Docs/debug_log'
PREFIX = ('prep_', 'chk_', 'anal_', 'fig_', 'up_', 'run_')
SINCE = '2026-10-13'          # 도구 규약 적용 시작(10-12 결정, 다음 세션부터)
ARGS = set(sys.argv[1:])
sys.stdout.reconfigure(encoding="utf-8")
warns = []

def warn(kind, path, msg):
    warns.append('[%s] %s — %s' % (kind, Path(path).relative_to(ROOT).as_posix() if Path(path).is_absolute() else path, msg))

def git(*a):
    return subprocess.run(['git', *a], cwd=ROOT, capture_output=True, text=True, encoding='utf-8').stdout

def changed():
    out = git('status', '--porcelain', '-uall')
    fs = []
    for ln in out.splitlines():
        p = ln[3:].strip().strip('"')
        if ' -> ' in p: p = p.split(' -> ')[1]
        if (ROOT / p).is_file(): fs.append(ROOT / p)
    return fs

def date_dirs():
    return sorted(d for d in DL.iterdir() if d.is_dir() and re.match(r'\d{4}-\d{2}-\d{2}$', d.name) and d.name >= SINCE)

def check_script(f):
    if f.suffix not in ('.py', '.sh'): return
    n = f.name
    if not n.startswith(PREFIX) and not re.match(r'job\d', n):
        warn('N', f, '용도 앞머리(%s) 없음' % '/'.join(p[:-1] for p in PREFIX))
    try: head = f.read_text(encoding='utf-8', errors='replace').splitlines()[:10]
    except OSError: return
    body = [l for l in head if not l.startswith('#!') and not l.startswith('# -*-')]
    if not any(l.lstrip().startswith(('#', '"""', "'''")) for l in body):
        warn('H', f, '첫 10 줄에 설명 주석 없음(무엇을 · 왜 · 로버 움직임 · 인자 · 출력)')

LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
PATH = re.compile(r'`((?:jobs|outputs|figures)/[^`\s]+)`')
def check_md(f):
    try: s = f.read_text(encoding='utf-8', errors='replace')
    except OSError: return
    for m in LINK.findall(s):
        if re.match(r'[a-z]+:', m) or m.startswith('#'): continue
        t = m.split('#')[0]
        if t and not (f.parent / t).exists():
            warn('L', f, '깨진 링크 %s' % m)
    if f.name in ('SUMMARY.md', 'TOOLS.md') and f.parent.parent == DL:
        for m in PATH.findall(s):
            t = m.rstrip('.,;:)')
            if any(c in t for c in '*{<~'): continue      # 패턴 · 자리표시는 건너뜀
            if not (f.parent / t).exists():
                warn('P', f, '적힌 경로가 없음 %s' % t)

def check_day(d):
    has_work = (d / 'jobs').is_dir() and any((d / 'jobs').iterdir())
    if has_work and not (d / 'TOOLS.md').exists():
        warn('T', d, 'jobs/ 가 있는데 TOOLS.md 없음')

def check_secret():
    rn = os.environ.get('ROVER_RUNNER')
    if not rn: return
    try: m = re.search(r'sshpass -p (\S+)', Path(rn).read_text(encoding='utf-8', errors='replace'))
    except OSError: m = None
    if not m:
        warn('S', rn, '러너에서 비밀번호를 못 읽음 — 게이트를 손으로 돌릴 것'); return
    hit = git('grep', '--cached', '-l', '-F', m.group(1)).split()
    for h in hit: warn('S', h, '커밋 대상에 비밀번호 있음 — 커밋 금지')

if '--all' in ARGS:
    files = [p for d in date_dirs() for p in d.rglob('*') if p.is_file() and 'bags' not in p.parts]
    files += [p for p in (ROOT / 'Docs/tools').glob('*') if p.is_file()]
    days = date_dirs()
else:
    files = changed()
    days = sorted({p.relative_to(DL).parts[0] for p in files if DL in p.parents})
    days = [DL / d for d in days if re.match(r'\d{4}-\d{2}-\d{2}$', d) and d >= SINCE]

for f in files:
    rel = f.relative_to(ROOT).as_posix()
    if '/jobs/' in rel and rel.startswith('Docs/debug_log/') and rel.split('/')[2] >= SINCE or rel.startswith('Docs/tools/'):
        check_script(f)
    if f.suffix == '.md' and rel.startswith('Docs/'):
        check_md(f)
for d in days: check_day(d)
check_secret()

for w in warns: print(w)
print('RULES_OK' if not warns else 'RULES_WARN %d' % len(warns))
sys.exit(1 if warns and '--strict' in ARGS else 0)
