#!/usr/bin/env python3
# fig_report_0917 — 09-17 정리 페이지 조립(11-04 사후 작성, 원천 = 그날 SUMMARY): 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0917.html (그림 없음). PC, 로버 안 움직임.
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>09-17 상자 뒤 목표 3/3</title>', 1)
assert '09-17' in h
t = h + open(D + '/2026-09-17/jobs/report_0917_body.html', encoding='utf-8').read()
open(D + '/2026-09-17/figures/day_summary_0917.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
