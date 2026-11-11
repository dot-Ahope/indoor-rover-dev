#!/usr/bin/env python3
# fig_report_1111 — 11-11 정리 페이지 조립: 머리(10-28 틀, 제목만 바꿈) + 본문 + 탈출 장면 그림 3 장(data URI) → figures/day_summary_1111.html (로컬 사본 = 게시 원본). PC, 로버 안 움직임.
import base64
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>11-11 Smac 표준 채택</title>', 1)
assert '11-11' in h
b = open(D + '/2026-11-11/jobs/report_1111_body.html', encoding='utf-8').read()
for t in ('t11_8', 't12_2', 't16_0'):  # 그림 원본 = figures/f2rr1_escape_<t>.png(§6)
    raw = open(D + f'/2026-11-11/figures/f2rr1_escape_{t}.png', 'rb').read()
    key = f'@@IMG_{t}@@'
    assert key in b, key
    b = b.replace(key, 'data:image/png;base64,' + base64.b64encode(raw).decode())
assert '@@IMG_' not in b
t = h + b
open(D + '/2026-11-11/figures/day_summary_1111.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
