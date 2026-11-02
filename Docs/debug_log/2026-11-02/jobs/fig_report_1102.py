#!/usr/bin/env python3
# fig_report_1102 — 11-02 정리 페이지 조립: 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_1102.html (로컬 사본 = 게시 원본, 그림 없음). PC, 로버 안 움직임.
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>11-02 규약 한 곳으로</title>', 1)
assert '11-02' in h
t = h + open(D + '/2026-11-02/jobs/report_1102_body.html', encoding='utf-8').read()
open(D + '/2026-11-02/figures/day_summary_1102.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
