#!/usr/bin/env python3
# fig_report_0827 — 08-27 정리 페이지 사후 조립(11-04): 커널 HID 모듈 · D455f IMU 융합 · EKF 축 설정 · W4 슬립 — 그날 SUMMARY 를 원천으로, 머리(10-28 틀, 제목만 바꿈) + 본문 → figures/day_summary_0827.html (로컬 사본 = 게시 원본, 그림 없음). PC, 로버 안 움직임.
import os
D = 'F:/6_Indoor_Rover/Rover/Docs/debug_log'
h = open(D + '/2026-10-28/jobs/report_1028_head.html', encoding='utf-8').read()
h = h.replace('<title>10-28 장소 이름 이동</title>', '<title>08-27 카메라 자이로 융합</title>', 1)
assert '08-27 카메라 자이로 융합' in h
t = h + open(D + '/2026-08-27/jobs/report_0827_body.html', encoding='utf-8').read()
os.makedirs(D + '/2026-08-27/figures', exist_ok=True)
open(D + '/2026-08-27/figures/day_summary_0827.html', 'w', encoding='utf-8', newline=chr(10)).write(t)
print('ok', len(t) // 1024, 'kB')
