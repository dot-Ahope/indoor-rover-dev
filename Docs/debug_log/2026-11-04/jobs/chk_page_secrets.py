# chk_page_secrets — 11-04 §11: 정리 페이지 게시 전 검사(비밀번호 파일 모든 줄 · 금지 문구 · NUL/U+FFFD · MAC · sshpass 값 · title). PC, 인자 = 페이지 경로들. 비밀번호 값은 출력하지 않고 개수만.
# 정리 페이지 게시 전 검사: 비밀번호 줄 · 금지 문구 · NUL/U+FFFD · MAC · 크기 · title
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
pw = [l.strip() for l in open('C:/Users/magma/.config/rover_jetson/pw', encoding='utf-8') if l.strip()]
for p in sys.argv[1:]:
    s = open(p, encoding='utf-8').read()
    bad = sum(s.count(x) for x in pw)
    ban = len(re.findall('<private-plan-words>', s))
    nul = s.count('\x00') + s.count('\ufffd')
    mac = len([m for m in re.findall(r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}', s) if not re.match(r'^(2[0-9]-[01][0-9]-[0-3][0-9]|70-01-01|00:00:00)', m)])
    sp = len(re.findall(r'sshpass -p [^<\s]', s))
    t = re.search(r'<title>([^<]*)', s)
    print(('OK ' if bad + ban + nul + mac == 0 else 'BAD'), p.split('/')[-1], len(s) // 1024, 'kB · 비번', bad, '· 금지', ban, '· 깨짐', nul, '· MAC', mac, '· sshpass', sp, '·', t.group(1) if t else '제목없음')
