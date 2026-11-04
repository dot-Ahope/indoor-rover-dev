#!/usr/bin/env python3
"""chk_commit_gate — 커밋 직전 비밀번호 게이트: 커밋될 수 있는 내용에 Jetson 비밀번호(지금 값 · 옛 값)가 있으면 **막는다** (2026-11-02, PC, 로버 안 움직임).
  두 곳에서 부른다:
    ① Claude Code PreToolUse 훅(.claude/settings.json, Bash · PowerShell): stdin 훅 JSON 의 tool_input.command 에 `git commit` 이 있을 때만 검사.
    ② git 자체 pre-commit 훅(터미널 커밋 포함, 이 PC 만): `python Docs/tools/chk_commit_gate.py --git-hook` — 설치는 README §8.
  비밀번호 = 저장소 밖 ~/.config/rover_jetson/pw (ROVER_PW_FILE 로 바꿀 수 있음). 한 줄에 하나 — 첫 줄 = 지금 값, 다음 줄부터 감시할 옛 값. 값은 어디에도 출력하지 않는다.
  검사 범위: staged(index) + 추적 중인 작업 트리 파일 — `git commit -a` · `git commit <파일>` 은 훅이 끝난 뒤 작업 트리 내용을 담으므로 staged 만 보면 샌다(11-02 다른 세션 평가로 확인).
  판정: 파일 없음 · 빈 값 → 막음 · 어느 값이든 있음 → 막음(파일 이름 · 몇 번째 줄 값인지만) · 없음 → 통과(①은 규약 점검 경고 개수 알림).
  종료 코드: 0 통과 · ① 2 막음 / ② 1 막음 (이유는 stderr)."""
import json, os, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

GIT_HOOK = '--git-hook' in sys.argv[1:]
BLOCK = 1 if GIT_HOOK else 2

if not GIT_HOOK:
    raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')   # 한글 커밋 메시지 — 콘솔 기본 cp949 로 읽으면 깨져 통과해 버림
    try: cmd = (json.loads(raw).get('tool_input') or {}).get('command', '')
    except Exception: cmd = raw   # JSON 이 깨져도 원문에서 git commit 을 찾는다(통과로 새지 않게)
    if not re.search(r'\bgit\b[^|;&\n]*\bcommit\b', cmd):
        sys.exit(0)

root = Path.cwd() if GIT_HOOK else Path(os.environ.get('CLAUDE_PROJECT_DIR') or Path(__file__).resolve().parents[2])
pwf = Path(os.environ.get('ROVER_PW_FILE') or Path.home() / '.config/rover_jetson/pw')
try: pws = [l.strip() for l in pwf.read_text(encoding='utf-8').splitlines() if l.strip()]
except OSError: pws = []
if not pws:
    print('커밋 게이트: 비밀번호 파일 %s 이 없거나 비어 있음 — 게이트를 손으로 돌리고 사용자에게 알릴 것(Docs/debug_log/README.md §8)' % pwf, file=sys.stderr)
    sys.exit(BLOCK)

def grep(pw, cached):
    a = ['git', 'grep', '--cached', '-l', '-F', pw] if cached else ['git', 'grep', '-l', '-F', pw]
    return subprocess.run(a, cwd=root, capture_output=True, text=True, encoding='utf-8', errors='replace').stdout.split()

bad = set()
for i, pw in enumerate(pws):
    for where, cached in (('staged', True), ('작업 트리', False)):
        for f in grep(pw, cached):
            bad.add('%s(%s, %s)' % (f, where, '지금 값' if i == 0 else '옛 값 %d' % i))
if bad:
    print('커밋 게이트: Jetson 비밀번호가 커밋될 수 있는 곳에 있다 — 커밋 금지, <PW> 로 가리거나 추적에서 뺀 뒤 다시: %s' % ', '.join(sorted(bad)), file=sys.stderr)
    sys.exit(BLOCK)

# 11-04: 기록 규칙 — 기준선(Docs/tools/rules_baseline.txt, 옛 결함)에 없는 **새 경고**가 있으면 막는다(①② 둘 다).
#   예전(11-02 ~ 11-03)엔 ① 에서 경고 개수만 알렸다. 우회: 새 경고를 고치거나, 사용자 확인 뒤 기준선을 다시 씀(README §8).
w = subprocess.run([sys.executable, str(root / 'Docs/tools/chk_record_rules.py'), '--new-only'], cwd=root, capture_output=True, text=True, encoding='utf-8')
lines = w.stdout.strip().splitlines()
if w.returncode != 0:
    print('커밋 게이트: 기록 규칙 새 경고 %s — 고친 뒤 다시 커밋(기준선에 없는 경고만 막음):\n%s' % ((lines or ['?'])[-1].split()[-1], '\n'.join(lines[:-1][:20])), file=sys.stderr)
    sys.exit(BLOCK)
sys.exit(0)
