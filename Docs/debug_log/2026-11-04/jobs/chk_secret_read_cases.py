# chk_secret_read_cases — 11-04 §13: chk_secret_read 훅 판정 16 경우 시험(막아야 7 · 통과 9 — 11-04 보강 3 포함). PC, 로버 안 움직임, 인자 없음, 출력 ALL_OK 또는 FAIL n. 스크래치패드 러너 경로를 씀.
import json, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
SP = r'C:\Users\magma\AppData\Local\Temp\claude\F--6-Indoor-Rover-Rover\21d4aa9f-8412-4905-b23d-17554af330ea\scratchpad'
SPG = '/c/Users/magma/AppData/Local/Temp/claude/F--6-Indoor-Rover-Rover/21d4aa9f-8412-4905-b23d-17554af330ea/scratchpad'
cases = [
 ({'tool_name': 'Bash', 'cwd': SPG, 'tool_input': {'command': 'grep -n "job551" run_f0.sh run_f2c.sh'}}, 2, '11-03 실수 재현(Git Bash cwd)'),
 ({'tool_name': 'Bash', 'cwd': SP, 'tool_input': {'command': 'grep -n "job551" run_f0.sh run_f2c.sh'}}, 2, '11-03 실수 재현(Windows cwd)'),
 ({'tool_name': 'Bash', 'tool_input': {'command': "sed 's/sshpass -p [^ ]*/sshpass -p <PW>/g' " + SPG + '/run_jn.sh | head'}}, 0, '가림 있음'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'grep -c sshpass ' + SPG + '/run_jn.sh'}}, 0, '개수만'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'bash ' + SPG + '/run_jn.sh chk.sh'}}, 0, '실행만'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'cat ~/.config/rover_jetson/pw'}}, 2, '비밀번호 파일'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'cat "$SP/run_f0.sh"'}}, 2, '변수 경로'),
 ({'tool_name': 'Read', 'tool_input': {'file_path': SP + '\\run_jn.sh'}}, 2, 'Read 도구'),
 ({'tool_name': 'Grep', 'tool_input': {'pattern': 'sshpass', 'path': SP + '\\run_f0.sh', 'output_mode': 'content'}}, 2, 'Grep 내용'),
 ({'tool_name': 'Grep', 'tool_input': {'pattern': 'sshpass', 'path': SP + '\\run_f0.sh', 'output_mode': 'count'}}, 0, 'Grep 개수'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'cat Docs/tools/prep_fast.sh | head'}}, 0, '일반 파일'),
 ({'tool_name': 'PowerShell', 'tool_input': {'command': 'Get-Content ' + SP + '\\run_f0.sh'}}, 2, 'PowerShell'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'git commit -m "x"'}}, 0, '무관 명령'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'cat > x.sh <<EOF\nPW=$(grep -o sshpass ' + SPG + '/run_jn.sh)\nEOF\nbash x.sh'}}, 0, 'heredoc 본문(11-04 보강)'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'bash ' + SPG + '/run_jn.sh job.sh | grep -v x | tee out.txt'}}, 0, '실행 + 출력 거르기(보강)'),
 ({'tool_name': 'Bash', 'tool_input': {'command': 'cat ' + SPG + '/run_jn.sh | grep sshpass'}}, 2, 'cat 를 grep 으로(보강)'),
]
bad = 0
for d, want, name in cases:
    r = subprocess.run([sys.executable, 'Docs/tools/chk_secret_read.py'], input=json.dumps(d).encode(), capture_output=True)
    ok = r.returncode == want; bad += not ok
    print('%s %-28s exit %d (want %d)' % ('ok ' if ok else 'BAD', name, r.returncode, want))
print('FAIL', bad) if bad else print('ALL_OK')
