# 10-20 정리 페이지: 머리(10-19 스타일) + 본문 + 그림(data URI) → report_1020.html
import base64, sys, re
SP, FIG = sys.argv[1], sys.argv[2]
t = open(SP + '/report_1020_head.html', encoding='utf-8').read() + open(SP + '/report_1020_body.html', encoding='utf-8').read()
imgs = {'vslam': 'vslam_cmp_f2z2_a20.png', 'replay': 'ekf_replay_live_f2z1.png', 'shadow': 'shadow_f2v1.png', 'shm': 'shm_day_summary.png'}
for k, f in imgs.items():
    t = t.replace('{{img:%s}}' % k, 'data:image/png;base64,' + base64.b64encode(open(FIG + '/' + f, 'rb').read()).decode())
assert '{{' not in t, re.findall(r'\{\{[^}]+\}\}', t)
open(SP + '/report_1020.html', 'w', encoding='utf-8').write(t)
print('ok', len(t) // 1024, 'kB')
