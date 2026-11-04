#!/usr/bin/env python3
# fig_report_0909 — 09-09 정리 페이지 사후 조립(11-04): 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0909.html (로컬 사본 = 게시 원본, 그림 없음 — 09-09 outputs/ 비어 있음). 왜: 그날 SUMMARY 를 본 것→추론→결론 · 발췌 형식으로 다시 보기 위해. PC, 로버 안 움직임.
import os
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>09-09 odom 소실 · STVL 도입</title>', 1)
assert '09-09' in h
t = h + open(D + '/2026-09-09/jobs/report_0909_body.html', encoding='utf-8').read()
os.makedirs(D + '/2026-09-09/figures', exist_ok=True)
open(D + '/2026-09-09/figures/day_summary_0909.html', 'w', encoding='utf-8', newline='\n').write(t)
print('ok', len(t) // 1024, 'kB')
