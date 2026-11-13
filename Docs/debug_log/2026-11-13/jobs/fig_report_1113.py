#!/usr/bin/env python3
# fig_report_1113 — 11-13 정리 페이지 조립: 머리(10-28 틀, 제목만 바꿈) + 본문 + 그림 3 장(data URI) → figures/day_summary_1113.html (로컬 사본 = 게시 원본). PC, 로버 안 움직임.
#   그림: figures/corridor_cmp_f2rr1_f2rd1.png(§3) · f2rd1_color_154802.jpg(§3) · f2rd2_color_161049.jpg(§5) — 사람이 찍힌 장면은 쓰지 않음(§11).
import base64
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>11-13 시각화 기록과 교착</title>', 1)
assert '11-13' in h
b = open(D + '/2026-11-13/jobs/report_1113_body.html', encoding='utf-8').read()
for key, f, mime in (('corr', 'corridor_cmp_f2rr1_f2rd1.png', 'png'), ('c1', 'f2rd1_color_154802.jpg', 'jpeg'), ('c2', 'f2rd2_color_161049.jpg', 'jpeg')):
    k = f'@@IMG_{key}@@'; assert k in b, k
    b = b.replace(k, f'data:image/{mime};base64,' + base64.b64encode(open(D + '/2026-11-13/figures/' + f, 'rb').read()).decode())
assert '@@IMG_' not in b
t = h + b
open(D + '/2026-11-13/figures/day_summary_1113.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
