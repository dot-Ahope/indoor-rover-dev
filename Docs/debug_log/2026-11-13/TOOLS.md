# 2026-11-13 TOOLS

규약 README §3.3. Jetson 실행은 스크래치패드 러너 `run_jn.sh`(JETSON_HOST=<LAN-B>.110).

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 뒤 판정 |
|---|---|---|---|---|---|
| §0 | 컬러 기록 전 읽기 확인 | `jobs/chk_color_ready_1113.sh` → `outputs/chk_color_ready_1113.txt` | 14:29 부팅 · base 만 · topic_tools 없음 · 컬러 640x480 @ 60/30/15/5 Hz · 디스크 122 GB | 5 fps 는 카메라 프로파일로 | ✔ |
| §0 | 재부팅 뒤 도구 전송 | `Docs/tools/up_tools.sh` → `outputs/up_tools_1113.txt` | Jetson /tmp 7 개 | — | ✔ |
| §0 | camera.launch color_fps 배포 | `jobs/up_cam_1113.sh`(base64 내장) → `outputs/up_cam_1113.txt` | md5 87af89ff04b8 일치 · 기본 15 | 배포 반영 | ✔ |
| §1 | 표준 prep + 컬러 5 fps | `jobs/prep_color_1113.sh 1` → `outputs/prep_color_1113_1.txt` | PREP_OK · RateController 0.01 · Smac | 새 기본값으로 뜸 | ✔ |
| §1 | 정지 기록 A/B | `jobs/chk_rec_ab_1113.sh 60` → `outputs/chk_rec_ab_1113.txt` | 컬러 4.73(개수 ÷ 길이) · /tf 49.0 · CPU +4.5 %p · nvblox 35 → 58 % | 컬러 미달처럼 보임 | ✘ 계산 방법 탓 → 아래 |
| §1 | 컬러 프레임 간격 | `jobs/anal_color_gaps_1113.py` → `outputs/anal_color_gaps_1113.txt` | 간격 208.0 ms · 1.5 배 넘는 간격 0 | 손실 0, 실제 4.81 Hz | ✔ |
| §1 | A 다시(순서 영향) | `jobs/chk_rec_ab_1113.sh 60 A2` → `outputs/chk_rec_ab_1113_A2.txt` | nvblox 35 % · CPU 47.3 % | nvblox 증가는 B 조건과 같이 움직임 | ？(기전 미확인) |
| §3 | f2rd1 nav2 사건 | `jobs/up_nav_events_1113.sh`(11-11 판 날짜만 바꿈) → `outputs/nav_events_f2rd1_live.txt` | 347 줄 · 주기 놓침 127 · lethal 6 | 서쪽 통로 집중 | ✔ |
| §3 | 구간 CPU | `jobs/anal_proc_window_1113.py` → `outputs/anal_proc_window_1113.txt` | 통로 70.5 대 68.1 % | 부하 가설 약함 | ✔ |
| §3 | 통로 코스트맵 잘라 오기 | `jobs/anal_costmap_crop_1113.py` → `outputs/anal_costmap_crop_f2rd1.txt` | 9 시각 · 창 88×40 | — | ✔ |
| §3 | 통로 비교 그림 · 폭 | `jobs/fig_corridor_cmp_1113.py` → `figures/corridor_cmp_f2rr1_f2rd1.png`, `jobs/anal_corridor_width_1113.py` → `outputs/anal_corridor_width_1113.txt` | 입구 동쪽 0.1 ~ 0.25 m 좁음 · 안쪽 15 cm | 배치 차이 | ✘ 안쪽은 비교 시각 오류(§7) |
| §3 | 컬러 장면 | `jobs/anal_color_frames_1113.py` → `figures/f2rd1_color_*.jpg` | 입구 동쪽 종이 상자 | 배치 확인 재료 | ✔ |
| §2 | prep 원문 다시 읽기 | `jobs/chk_prep_tail_1113.sh rd1` → `outputs/prep_color_1113_rd1.txt` | PREP_OK | PC 필터 깨짐 우회 | ✔ |
| §5 | f2rd2 사건 · 장면 · 코스트맵 | `up_nav_events_1113.sh` → `outputs/nav_events_f2rd2.txt` · `anal_color_frames_1113.py` · `anal_costmap_crop_1113.py` → `outputs/anal_costmap_crop_f2rd2.txt` | 목표 5 nav_guard 취소 | 안쪽 배치 차이 추정 | ？(§8 에서 시간 구조로) |
| §6 | 시계열 뽑기 | `jobs/anal_series_1113.py` → `outputs/anal_series_f2rd2.csv` | 59 662 줄 | — | ✔ |
| §6 | 1 s 칸 요약 | `jobs/anal_series_bins_1113.py` → `outputs/anal_series_bins_f2rd2_goal5.txt` · `_goal34.txt` | 목표 ≈ 측정 · v≈0 w± | 바퀴 정상 · MPPI 떨림 | ✔ |
| §6 | 지령 간격 · 방향 비교 | (인라인 파이썬) → `outputs/anal_cmd_gaps_f2rd2.txt` · `anal_goal4_yaw_cmp.txt` · `anal_goal5_turn_cmp.txt` | 간격 0.85 · 0.75 s · S 자 ±35° f2rr1 과 같음 | 큰 이상 전환 없음 | ✔ |
| §6 | 통로 줄별 최대 폭 | `jobs/anal_corridor_rows_1113.py [--rr1t]` → `outputs/anal_corridor_rows_f2rd2.txt` · `_after.txt` | 지나간 뒤 비교 5 ~ 10 cm | §3 정정 | ✔ |
| §10 | bag 크기 | `jobs/chk_bags_1113.sh` → `outputs/chk_bags_1113.txt` | 컬러 76 % · /tmp 중복 4.3 G | 경량판 제안 | ✔ |
| §11 | 하루 정리 페이지 조립 | `jobs/fig_report_1113.py` → `figures/day_summary_1113.html` | 307 kB | 게시 원본 | ✔ |
