#!/usr/bin/env python3
"""chk_secret_read — 비밀번호가 든 파일을 가림 없이 화면(대화)으로 읽는 명령을 실행 전에 막는다 (2026-11-04, PC, 로버 안 움직임).
  왜: 11-03 §5 — 러너 run_f0.sh 를 가림 없이 grep 해 Jetson 비밀번호가 대화에 출력됐다(규칙은 문장으로만 있었음).
  부르는 곳: Claude Code PreToolUse 훅(.claude/settings.json) — Bash · PowerShell · Read · Grep. stdin = 훅 JSON.
  판정:
    ① 대상 찾기 — 명령 문자열 · file_path · path 의 낱말 중 파일 경로(글로브 포함, /mnt/c/… 는 C:/… 로)를 펼쳐,
       내용에 비밀번호(~/.config/rover_jetson/pw 의 아무 줄)가 든 파일. 변수 경로($W/…)처럼 펼칠 수 없는 것은
       이름으로 봄: run_jn.sh · run_f0.sh · run_f2c.sh · rover_jetson/pw · settings.local*.json.
    ② 읽기인지 — Read · Grep 도구, 또는 명령에 읽는 명령어(cat · head · tail · less · more · grep · rg · sed · awk · cut · tr · sort ·
       uniq · nl · diff · strings · xxd · od · type · Get-Content · gc · Select-String · sls)가 있음. `bash x.sh` 처럼 실행만 하는 것은 통과.
    ③ 가림이 있으면 통과 — 명령에 '<PW>' 치환이 있음, 또는 grep 이 -c · -l · -L · -q(개수 · 파일 이름만).
  막을 때: 종료 2 + stderr 에 이유(값은 출력하지 않음). 비밀번호 파일이 없으면 이름 기준만 본다.
  인자 없음(훅 전용). 시험: echo '{"tool_name":"Bash","tool_input":{"command":"cat run_jn.sh"}}' | python Docs/tools/chk_secret_read.py"""
import glob, json, os, re, shlex, sys
from pathlib import Path
sys.stderr.reconfigure(encoding='utf-8')

raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')
try: d = json.loads(raw)
except Exception: sys.exit(0)
tool = d.get('tool_name', '')
ti = d.get('tool_input') or {}
cwd = d.get('cwd') or os.getcwd()   # Git Bash 형식(/c/…)이면 아래 norm 으로 C:/… 로 바꿈

pwf = Path(os.environ.get('ROVER_PW_FILE') or Path.home() / '.config/rover_jetson/pw')
try: pws = [l.strip() for l in pwf.read_text(encoding='utf-8').splitlines() if l.strip()]
except OSError: pws = []
NAMES = re.compile(r'(^|[\\/])(run_jn\.sh|run_f0\.sh|run_f2c\.sh|settings\.local[^\\/]*\.json)$|rover_jetson[\\/]pw$')

def has_pw(p):
    try:
        if os.path.getsize(p) > 5_000_000: return False
        b = open(p, 'rb').read().decode('utf-8', errors='replace')
    except OSError: return False
    return any(pw in b for pw in pws)

def norm(t):
    t = t.strip('\'"()<>;|&')
    m = re.match(r'^/mnt/([a-z])/(.*)', t)
    if m: t = '%s:/%s' % (m.group(1).upper(), m.group(2))
    m = re.match(r'^/([a-z])/(.*)', t)          # Git Bash /f/… → F:/…
    if m and len(m.group(1)) == 1: t = '%s:/%s' % (m.group(1).upper(), m.group(2))
    if t.startswith('~'): t = str(Path.home()) + t[1:]
    return t

def secret_targets(words):
    global cwd
    cwd = norm(cwd)
    hit = []
    for w in words:
        if '$' in w:                               # 펼칠 수 없음 → 이름으로
            if NAMES.search(w.split('/')[-1] and w): hit.append(w)
            continue
        t = norm(w)
        if not t or t.startswith('-'): continue
        pat = t if os.path.isabs(t) else os.path.join(cwd, t)
        for p in (glob.glob(pat) if any(c in pat for c in '*?[') else [pat]):
            if os.path.isfile(p) and (NAMES.search(p.replace('\\', '/')) or has_pw(p)): hit.append(p)
    return hit

def block(why):
    print('비밀 읽기 차단: %s — 러너 · 비밀번호 파일은 `| sed \'s/sshpass -p [^ ]*/sshpass -p <PW>/g\'` 로 가리거나 grep -c · -l 로 개수만(README §4 · 11-03 §5)' % why, file=sys.stderr)
    sys.exit(2)

if tool in ('Read',):
    t = secret_targets([ti.get('file_path', '')])
    if t: block('Read 도구로 %s 을(를) 열려 함' % Path(t[0]).name)
    sys.exit(0)
if tool in ('Grep',):
    mode = ti.get('output_mode', 'files_with_matches')
    if mode == 'content':
        t = secret_targets([ti.get('path', '') or cwd]) if ti.get('path') else []
        if t: block('Grep 도구 내용 출력으로 %s 을(를) 봄' % Path(t[0]).name)
    sys.exit(0)

cmd = ti.get('command', '') or ''
if not cmd: sys.exit(0)
# 11-04 보강: heredoc 본문(<<EOF … EOF)은 파일로 쓰일 글이지 지금 실행되는 읽기가 아니므로 뺀다(첫 판이 내 배포 명령을 오탐).
def strip_heredocs(c):
    out, lines, i = [], c.split('\n'), 0
    while i < len(lines):
        ln = lines[i]; out.append(ln)
        m = re.search(r"<<-?\s*['\"]?(\w+)['\"]?", ln)
        if m:
            tag = m.group(1); i += 1
            while i < len(lines) and lines[i].strip() != tag: i += 1
        i += 1
    return '\n'.join(out)
cmd = strip_heredocs(cmd)
READ = re.compile(r'(^|[\s|;&(`$])(cat|head|tail|less|more|grep|egrep|fgrep|rg|sed|awk|cut|tr|sort|uniq|nl|diff|strings|xxd|od|type|Get-Content|gc|Select-String|sls)(\s|$)', re.I)
if not READ.search(cmd): sys.exit(0)
if '<PW>' in cmd: sys.exit(0)
# 11-04 보강: 파이프 · ; · && · || · 줄바꿈으로 나눈 '조각' 마다 본다 — 읽는 명령어와 비밀 파일이 같은 조각에 있을 때만.
#   (예: `bash run_jn.sh job.sh | grep -v x` 는 run_jn.sh 를 실행만 하고 grep 은 그 출력을 거를 뿐 → 통과)
hits = set()
for seg in re.split(r'\|\||&&|[|;\n]', cmd):
    if not READ.search(seg): continue
    if re.search(r'\bgrep\b[^|;&]*\s-[A-Za-z]*[clLq]', seg) and not re.search(r'\b(cat|head|tail|sed|awk|less|more|Get-Content|type)\b', seg):
        continue                                           # grep 이 개수 · 이름만
    try: words = shlex.split(seg, posix=(tool != 'PowerShell'))   # PowerShell 경로의 역슬래시를 지우지 않게
    except ValueError: words = seg.split()
    words = [x for w in words for x in re.split(r'[<>]', w) if x]
    hits |= {Path(x).name for x in secret_targets(words)}
if hits: block('가림 없이 %s 을(를) 읽는 명령' % ', '.join(sorted(hits)))
sys.exit(0)
