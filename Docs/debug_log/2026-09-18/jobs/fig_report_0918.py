#!/usr/bin/env python3
# fig_report_0918 — 09-18 정리 페이지 사후 조립(11-04): 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0918.html (로컬 사본 = 게시 원본, 그림 없음). 근거는 그날 SUMMARY · outputs. PC, 로버 안 움직임.
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>09-18 센서 데크 −2.68°</title>', 1)
assert '09-18' in h
t = h + open(D + '/2026-09-18/jobs/report_0918_body.html', encoding='utf-8').read()
open(D + '/2026-09-18/figures/day_summary_0918.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
