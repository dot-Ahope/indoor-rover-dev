#!/usr/bin/env python3
"""chk_commit_gate — Claude Code PreToolUse 훅: `git commit` 명령 직전에 커밋 대상(staged)에 Jetson 비밀번호가 있으면 **막는다** (2026-11-02, PC, 로버 안 움직임).
  등록: .claude/settings.json hooks.PreToolUse(Bash · PowerShell). 입력 = 훅 JSON(stdin, tool_input.command). git commit 이 아니면 바로 통과.
  비밀번호 = 저장소 밖 파일 ~/.config/rover_jetson/pw (환경 변수 ROVER_PW_FILE 로 바꿀 수 있음). 값은 어디에도 출력하지 않는다.
  판정: 파일 없음 · 빈 값 → 막음(손으로 게이트를 돌리라는 안내) · staged 에 값이 있음 → 막음(파일 이름만 표시) · 없음 → 통과.
  통과할 때 chk_record_rules.py 경고가 있으면 개수만 알린다(막지 않음, README §8).
  종료 코드: 0 통과 · 2 막음(이유는 stderr — Claude 에게 전달됨)."""
import json, os, re, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8'); sys.stderr.reconfigure(encoding='utf-8')

raw = sys.stdin.buffer.read().decode('utf-8', errors='replace')   # 한글 커밋 메시지 — 콘솔 기본 cp949 로 읽으면 깨져 통과해 버림
try: cmd = (json.loads(raw).get('tool_input') or {}).get('command', '')
except Exception: cmd = raw   # JSON 이 깨져도 원문에서 git commit 을 찾는다(통과로 새지 않게)
if not re.search(r'\bgit\b[^|;&\n]*\bcommit\b', cmd):
    sys.exit(0)

root = Path(os.environ.get('CLAUDE_PROJECT_DIR') or Path(__file__).resolve().parents[2])
pwf = Path(os.environ.get('ROVER_PW_FILE') or Path.home() / '.config/rover_jetson/pw')
try: pw = pwf.read_text(encoding='utf-8').strip()
except OSError: pw = ''
if not pw:
    print('커밋 게이트: 비밀번호 파일 %s 이 없거나 비어 있음 — 게이트를 손으로 돌리고 사용자에게 알릴 것(README §8)' % pwf, file=sys.stderr)
    sys.exit(2)

r = subprocess.run(['git', 'grep', '--cached', '-l', '-F', pw], cwd=root, capture_output=True, text=True, encoding='utf-8')
hits = r.stdout.split()
if hits:
    print('커밋 게이트: 커밋 대상에 Jetson 비밀번호가 있다 — 커밋 금지, <PW> 로 가린 뒤 다시: %s' % ', '.join(hits), file=sys.stderr)
    sys.exit(2)

w = subprocess.run([sys.executable, str(root / 'Docs/tools/chk_record_rules.py')], cwd=root, capture_output=True, text=True, encoding='utf-8')
last = (w.stdout.strip().splitlines() or [''])[-1]
if last.startswith('RULES_WARN'):
    print(json.dumps({'systemMessage': '커밋 게이트 통과(비밀번호 0). 규약 점검 경고 %s 건 — python Docs/tools/chk_record_rules.py 로 확인' % last.split()[-1]}, ensure_ascii=False))
sys.exit(0)
