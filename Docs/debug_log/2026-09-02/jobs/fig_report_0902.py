#!/usr/bin/env python3
# fig_report_0902 — 09-02 정리 페이지 사후 조립(11-04): VX_SCALE 검증 · 루프 드리프트 · Nav2 도입 · 회전 데드락 · N1 1 차 — 그날 SUMMARY 를 원천으로, 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0902.html (로컬 사본 = 게시 원본, 그림 없음). PC, 로버 안 움직임.
import os
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>09-02 Nav2 첫 자율주행</title>', 1)
assert '09-02 Nav2 첫 자율주행' in h
t = h + open(D + '/2026-09-02/jobs/report_0902_body.html', encoding='utf-8').read()
os.makedirs(D + '/2026-09-02/figures', exist_ok=True)
open(D + '/2026-09-02/figures/day_summary_0902.html', 'w', encoding='utf-8', newline=chr(10)).write(t)
print('ok', len(t) // 1024, 'kB')
