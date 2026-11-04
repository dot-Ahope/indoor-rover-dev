#!/usr/bin/env python3
# fig_report_0831 — 08-31 정리 페이지 사후 조립(11-04): deskew · 조이스틱 지도 · Foxglove 4 초 스냅 · 휠 오도 27.8 % 과대(09-01 세션 포함) — 그날 SUMMARY 를 원천으로, 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0831.html (로컬 사본 = 게시 원본, 그림 없음). PC, 로버 안 움직임.
import os
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>08-31 스캔 끌림 · 휠 스케일</title>', 1)
assert '08-31 스캔 끌림 · 휠 스케일' in h
t = h + open(D + '/2026-08-31/jobs/report_0831_body.html', encoding='utf-8').read()
os.makedirs(D + '/2026-08-31/figures', exist_ok=True)
open(D + '/2026-08-31/figures/day_summary_0831.html', 'w', encoding='utf-8', newline=chr(10)).write(t)
print('ok', len(t) // 1024, 'kB')
