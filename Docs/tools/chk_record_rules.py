#!/usr/bin/env python3
"""chk_record_rules — 작업 규약(Docs/debug_log/README.md)의 기계로 볼 수 있는 부분을 점검하고 **경고만** 한다 (2026-11-02, PC, 로버 안 움직임).
  보는 것(규약 절):
    T  날짜 폴더(10-13~)에 TOOLS.md 가 없음                         (§3.3)
    N  jobs/ · Docs/tools/ 새 .py/.sh 이름에 용도 앞머리가 없음         (§3.1; 옛 이름 사본 job<숫자>… 은 제외)
    H  스크립트 첫 10 줄에 설명 주석이 없음                            (§3.2)
    L  md 의 상대 링크 [..](경로) 가 가리키는 파일이 없음               (깨진 링크)
    P  SUMMARY · TOOLS 에 적힌 jobs/ · outputs/ · figures/ 경로가 없음   (§2.3 데이터 칸; bags/ 는 git 제외라 안 봄)
    S  staged · 추적 작업 트리에 Jetson 비밀번호(지금 값 · 옛 값)가 있음  (§8; 저장소 밖 ~/.config/rover_jetson/pw 또는 ROVER_PW_FILE, 값은 출력 안 함)
    D  README §0 표와 CLAUDE.md 의 사본 표가 다름                       (11-02; 표지 RULES_TABLE_BEGIN/END)
    C  주제 폴더 Docs/0*/figures/<날짜>_*.html 의 날짜 폴더 사본이 없거나 다름 (§7.1)
    K  .claude/skills/*/SKILL.md 의 "읽을 절" 이 README 에 없는 절 제목 (11-04)
  대상: 기본 = git 에서 바뀐 파일(staged + unstaged + 새 파일)과 그 날짜 폴더. --all = 10-13 이후 날짜 폴더 전부.
  인자: [--all] [--strict(경고가 있으면 종료 코드 1)]
        [--every(추적 · 새 파일 전부 — 기준선용)] [--write-baseline(--every 결과를 BASELINE 에 씀)] [--new-only(기준선에 없는 경고만 내고, 있으면 종료 코드 1)]
  출력: 표준 출력에 '[분류] 경로 — 내용' 한 줄씩, 마지막 줄 'RULES_OK' 또는 'RULES_WARN <개수>'(--new-only 는 'RULES_NEW 0|<개수>').
  기준선(11-04): Docs/tools/rules_baseline.txt = 그때 있던 경고(옛 기록 결함). 커밋 훅(chk_commit_gate.py)은 --new-only 로 새 경고만 막는다.
    옛 결함을 고치면 기준선에서 저절로 빠질 뿐 막지 않는다. 기준선을 다시 쓰는 것은 사용자 확인 뒤(--every --write-baseline)."""
import os, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DL = ROOT / 'Docs/debug_log'
PREFIX = ('prep_', 'chk_', 'anal_', 'fig_', 'up_', 'run_', 'lib_')   # lib_ = import 전용 부품(11-19)
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
    pf = Path(os.environ.get('ROVER_PW_FILE') or Path.home() / '.config/rover_jetson/pw')
    try: pws = [l.strip() for l in pf.read_text(encoding='utf-8').splitlines() if l.strip()]   # 첫 줄 지금 값, 다음 줄 옛 값
    except OSError: pws = []
    if not pws:
        warn('S', str(pf), '비밀번호 파일 없음 — 게이트를 손으로 돌릴 것'); return
    for pw in pws:
        for h in set(git('grep', '--cached', '-l', '-F', pw).split() + git('grep', '-l', '-F', pw).split()):
            warn('S', h, '커밋될 수 있는 곳(staged · 추적 작업 트리)에 비밀번호 있음 — 커밋 금지')

BASELINE = ROOT / 'Docs/tools/rules_baseline.txt'
def tracked():
    out = git('ls-files', '-co', '--exclude-standard')
    return [ROOT / p for p in out.splitlines() if (ROOT / p).is_file()]
if '--every' in ARGS:
    files = [p for p in tracked() if p.relative_to(ROOT).as_posix().startswith('Docs/') and 'bags' not in p.parts]
    days = date_dirs()
elif '--all' in ARGS:
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

def table(p):   # RULES_TABLE_BEGIN ~ END 사이 표 줄
    try: s = p.read_text(encoding='utf-8')
    except OSError: return None
    m = re.search(r'RULES_TABLE_BEGIN[^\n]*\n(.*?)\n<!-- RULES_TABLE_END', s, re.S)
    return m.group(1).strip() if m else None
ta, tb = table(DL / 'README.md'), table(ROOT / 'CLAUDE.md')
if ta is None or tb is None: warn('D', 'CLAUDE.md', '규약 표 표지(RULES_TABLE_BEGIN/END)를 못 찾음')
elif ta != tb: warn('D', 'CLAUDE.md', 'README §0 표와 CLAUDE.md 사본이 다름 — 둘을 맞출 것')

# K (11-04): .claude/skills/*/SKILL.md 의 '읽을 절: `## …`' 가 README 에 실제로 있는 절 제목인지(README 절 이름을 바꾸면 Skill 도)
try: readme_heads = set(l.strip() for l in (DL / 'README.md').read_text(encoding='utf-8').splitlines() if l.startswith('#'))
except OSError: readme_heads = set()
for sk in sorted((ROOT / '.claude/skills').glob('*/SKILL.md')):
    for h in re.findall(r'읽을 절: `([^`]+)`', sk.read_text(encoding='utf-8')):
        if h.strip() not in readme_heads: warn('K', sk, 'README 에 없는 절 제목 %s' % h)

# 주제 폴더(Docs/0*/figures/)의 날짜 이름 정리 페이지는 날짜 폴더 figures/ 에도 같은 사본이 있어야 한다(README §7.1)
for fp in sorted(ROOT.glob('Docs/0*/figures/20??-??-??_*.html')):
    cp = DL / fp.name[:10] / 'figures' / fp.name
    if not cp.exists(): warn('C', fp, '날짜 폴더 사본 없음 → %s' % cp.relative_to(ROOT).as_posix())
    elif cp.read_bytes() != fp.read_bytes(): warn('C', fp, '날짜 폴더 사본과 내용이 다름 — 같은 판으로 맞출 것')
check_secret()

warns = sorted(set(warns))
if '--write-baseline' in ARGS:
    NL = chr(10)
    BASELINE.write_text('# chk_record_rules 기준선 — 이 목록에 있는 경고는 커밋을 막지 않는다(옛 결함). 손으로 고치지 말고 --every --write-baseline 으로 다시 씀.' + NL + ''.join(w + NL for w in warns), encoding='utf-8')
    print('기준선 %d 건 → %s' % (len(warns), BASELINE.relative_to(ROOT).as_posix())); sys.exit(0)
if '--new-only' in ARGS:
    try: base = set(l for l in BASELINE.read_text(encoding='utf-8').splitlines() if l and not l.startswith('#'))
    except OSError: base = set()
    new = [w for w in warns if w not in base]
    for w in new: print(w)
    print('RULES_NEW %d' % len(new)); sys.exit(1 if new else 0)
for w in warns: print(w)
print('RULES_OK' if not warns else 'RULES_WARN %d' % len(warns))
sys.exit(1 if warns and '--strict' in ARGS else 0)
