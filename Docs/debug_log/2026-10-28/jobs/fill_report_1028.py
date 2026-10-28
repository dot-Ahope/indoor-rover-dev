# 10-28 정리 페이지: 머리(10-27 틀, 제목만) + 본문 + 그림(data URI, outputs/*.png) → figures/day_summary_1028.html (로컬 사본 = 게시 원본)
import base64, re
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log/2026-10-28'
t = open(D + '/jobs/report_1028_head.html', encoding='utf-8').read() + open(D + '/jobs/report_1028_body.html', encoding='utf-8').read()
for k, f in (('run', 'fig_place_run_f2pl5.png'), ('reach', 'gcm_reach_1610.png')):
    t = t.replace('{{img:%s}}' % k, 'data:image/png;base64,' + base64.b64encode(open(D + '/outputs/' + f, 'rb').read()).decode())
assert '{{' not in t, re.findall(r'\{\{[^}]+\}\}', t)
open(D + '/figures/day_summary_1028.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
