#!/usr/bin/env python3
# fig_report_0914 — 09-14 정리 페이지 사후 조립(11-04): 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0914.html (로컬 사본 = 게시 원본, 그림 없음). 근거는 그날 SUMMARY · CSV. PC, 로버 안 움직임.
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>09-14 중앙 상자 통로</title>', 1)
assert '09-14' in h
t = h + open(D + '/2026-09-14/jobs/report_0914_body.html', encoding='utf-8').read()
open(D + '/2026-09-14/figures/day_summary_0914.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
