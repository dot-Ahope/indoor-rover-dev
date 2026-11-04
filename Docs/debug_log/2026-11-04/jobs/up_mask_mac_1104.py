# up_mask_mac_1104 — 11-04 §6: 추적 파일의 실제 MAC/BSSID 뒤 3 바이트를 XX 로 가림(README §4 '출력에 MAC 주소가 나오면 가린다'). 날짜 · 시각 모양(26-10-23-…)은 제외.
#   PC 한 번, 로버 안 움직임. 인자 없음. 출력: 파일 수 · 바꾼 수. 이력(git 과거 커밋)은 그대로 — 지금 판만.
#   (-I 라 git 이 바이너리로 보는 텍스트 로그는 빠짐 — 11-04 에는 2026-10-22/outputs/chk_wifi_1022.txt 1 개를 같은 식으로 따로 가림. -a 로 바꾸면 png 등도 건드려 위험)
import re, subprocess, sys
sys.stdout.reconfigure(encoding='utf-8')
R = 'F:/6_Indoor_Rover/Rover/'
pat = re.compile(r'\b((?:[0-9A-Fa-f]{2}([:-])){2}[0-9A-Fa-f]{2})\2([0-9A-Fa-f]{2})\2([0-9A-Fa-f]{2})\2([0-9A-Fa-f]{2})\b')
skip = re.compile(r'^(2[0-9]-[01][0-9]-[0-3][0-9]|70-01-01|00:00:00)')
files = subprocess.run(["git", "-C", R, "grep", "-I", "-l", '-E', r'([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}', '--', '.'], capture_output=True, text=True, encoding='utf-8').stdout.split('\n')
nf = nr = 0
for f in filter(None, files):
    b = open(R + f, 'rb').read()
    s = b.decode('latin-1'); enc = 'latin-1'   # 바이트 그대로 왕복(MAC 은 ASCII), 인코딩이 섞인 로그도 안 깨짐
    c = 0
    def rep(m):
        global c
        if skip.match(m.group(0)): return m.group(0)
        c += 1; d = m.group(2); return m.group(1) + d + 'XX' + d + 'XX' + d + 'XX'
    t = pat.sub(rep, s)
    if c:
        open(R + f, 'wb').write(t.encode(enc)); nf += 1; nr += c
print('MAC 가림: 파일', nf, '· 바꾼 곳', nr)
