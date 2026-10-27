# 10-27 정리 페이지: 머리(10-26 틀, 제목만) + 본문 + 그림(data URI, figures/report/*.jpg) → figures/day_summary_1027.html (로컬 사본 = 게시 원본)
import base64, re
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-27'
t = open(D + '/jobs/report_1027_head.html', encoding='utf-8').read() + open(D + '/jobs/report_1027_body.html', encoding='utf-8').read()
for k in ('tt1', 'block', 'gcm', 'exp'):
    t = t.replace('{{img:%s}}' % k, 'data:image/jpeg;base64,' + base64.b64encode(open(D + '/figures/report/%s.jpg' % k, 'rb').read()).decode())
assert '{{' not in t, re.findall(r'\{\{[^}]+\}\}', t)
open(D + '/figures/day_summary_1027.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
