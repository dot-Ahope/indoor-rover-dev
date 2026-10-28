# 2026-10-28 도구 (상황 → 도구 → 나온 값 → 그때의 추론, 나중에 ✔/✘/？)
⚠ 이 파일은 §8 시점에 늦게 만들었다(작업하면서 채우는 규칙을 앞 § 에서 놓침). §0~§7 은 SUMMARY 에서 옮겨 적음.

| § | 상황 | 도구 | 나온 값 | 그때의 추론 | 판정 |
|---|---|---|---|---|---|
| 0 | 하루 시작 상태 | `jobs/chk_day_start_1028.sh` | `outputs/chk_day_start_1028.txt` | 스택 · 지도 정상 | ✔ |
| 1~2 | 확인 주행 준비 | `jobs/up_prep_1028.sh` → `jobs/prep_smac_1028.sh` | `outputs/prep_smac_1028_1.txt` PREP_OK | 출발 가능 | ✔ |
| 3~4 | f2tt2 회수 | `jobs/get_f2tt2.sh` | `outputs/drives/f2tt2/*` | 처음엔 '러너 미실행' 으로 봄 | ✘(§3.1 정정) |
| 5 | 통로 반복 막힘 칸 출처 | `jobs/anal_corridor_cell.py` | `outputs/corridor_cell/*` | 회전 중 가장자리 한 칸 더 찍힘 | ✔ |
| 7 | place_server dry_run | `jobs/up_place_dry_1028.sh` → `jobs/chk_place_dry_1028.sh` | `outputs/chk_place_dry_1028{,b}.txt` 5 checked | 등록부 전부 통과 | ✘(통로 북쪽 빠짐, §8.1) |
| 7.1 · 8 | S1 실주행 f2pl1 | `jobs/up_place_s1_1028.sh` → `jobs/run_place_s1_1028.sh` | `outputs/drives/f2pl1/place_s1.log` 2 arrived · 통로 북쪽 rejected | 검사가 명목 자세를 봄 | ✔(§8.2) |
| 8 | 거절 순간 방향별 여유 | `jobs/anal_place_clear.py` | `outputs/place_clear_f2pl1.txt` −90° 0.110 · 비스듬 0.000 | 동쪽 물체 칸 x −1.365 | ✔ |
| 8 | 같은 자리 재현 · 수정 확인 | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh` | `outputs/chk_place_dry_1028c1.txt`(−51° 거절 3/3) · `c2.txt`(−86° 수락, 여유 0.10) | 방향 고침으로 통과, 경계값 | ？(f2pl2 에서) |
| 9 | f2pl2 두 번째 통로 북쪽 거절 | `jobs/anal_place_clear.py` | `outputs/place_clear_f2pl2.txt` 동쪽 칸 x −1.465, +90° 0.010 | 방향으로는 못 풂 | ✔ |
| 9 | 그 칸 출처 | `jobs/anal_cell_src.py` | `outputs/cell_src_f2pl2.txt` 라이다 27~184 점 · nvblox 0.21~0.28 | 실재 물체 가장자리, 99↔100 흔들림 | ✔ |
| 9 | 옮길 자리 | `jobs/anal_place_clear.py`(x 여러 개, 두 bag) | `outputs/place_clear_center.txt` −1.78 에서 0.10~0.16 | 가운데로 | ？(f2pl3) |
| 9 | 6 곳 전부 dry_run(남서에서) | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh`(목록 바꿈) | `outputs/chk_place_dry_1028c3.txt` 6 checked | 실주행 준비 | ？(f2pl3) |
| 10 | f2pl3 where 응답 없음 | bag /place/* 개수 확인(인라인 rosbags) | command 1 · status 0, f2pl2 command 4 중 2 기록 | 첫 메시지 연결 경쟁 | ？(원인 미확인, 수정 뒤 f2pl4) |
| 10 | 창구 수정 확인 | `jobs/up_place_dry_1028c.sh` | `outputs/chk_place_dry_1028c4.txt` 9/9 | 양방향 확인 동작 | ✔ |
| 11 | f2pl4 정지 지연 | 인라인 rosbags(/place/command · /cmd_vel · /odometry/filtered) | `outputs/stop_cmdvel_f2pl4.txt` cmd_vel 0 +0.29 s · 정지 +0.47 s | 판정 ② 통과 | ✔ |
| 11 | 구간별 nav2 사건 | 인라인 nav2.log 시간 창 집계 | 위 복도 구간 0 건, 통로 · 복귀 막힘 각 1 | 위 복도 느림은 막힘 탓 아님 | ？ |
| 12 | 위 복도 구간 비교 | `jobs/anal_leg_compare.py` | `outputs/leg_compare_C.txt` · `leg_compare_other.txt` 이 구간만 평균 0.060 m/s | MPPI 감속 | ✔ |
| 12 | 그때 주변 · 주기 | `jobs/anal_leg_env.py` | `outputs/leg_env_C.txt` 주기 20/s 같음, 오른쪽 라이다 0.06~0.07(no5 0.11~0.15) | 동쪽에 가까움 | ？(앞쪽 감속은 설명 안 됨) |
| 12 | 경로 가로 위치 | `jobs/anal_plan_x.py` | `outputs/plan_x_C.txt` 4 cm 동쪽 | 목표 10 cm 북쪽 탓 | ？(판별 시험 전) |
| 12 | 동쪽 가장자리 이력 | `jobs/anal_place_clear.py` 여러 판 | `outputs/east_edge_history.txt` · `corridor_grid_y29.txt` 한 칸 안쪽 | 환경 변화 또는 흔들림 | ？ |
| 13 | 위 복도 (−1.60, −2.10) 사전 여유 | `jobs/anal_place_clear.py`(f2pl4 bag 13:40:18) | `outputs/place_clear_upB_f2pl4.txt` 40~55° 0.124~0.111 · 90° 0.010 | 경로 끝 ≈ 50° 면 통과, 여유 1.8 cm | ？(f2pl5) |
| 13.1 | 위 복도 넣은 dry_run | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh` | `outputs/chk_place_dry_1028c5.txt` 경로 조회 전부 상태 6 | 계획기 쪽 문제 | ✔ |
| 13.1 | 계획기 상태 | `jobs/chk_nav_alive_1028.sh` | (대화 기록) GridBased tolerance 0.25 실패 · 프로세스 살아 있음 | 시작 · 목표 칸 문제 | ✔ |
| 13.1 | 로버 둘레 전역 칸 | `jobs/chk_costmap_robot.py`(+ `chk_costmap_robot_1028.sh`) | `outputs/costmap_robot_1519b.txt` 남쪽 y −0.57 치명 띠 2.4 m | 출발점에 갇힘 | ✔ |
| 13.1 | 같은 자리 f2pl4 끝 | `jobs/anal_place_clear.py` | `outputs/costmap_start_f2pl4_end.txt` 띠 없음 | 13:44 이후 생김 | ✔ |
| 13.1 | 라이다가 보나 | `jobs/chk_scan_band.py` | `outputs/scan_band_1519.txt` 띠 자리 점 없음 | 라이다 아님 | ✔ |
| 13.1 | 비우면 사라지나 | `jobs/chk_clear_global_1028.sh` | `outputs/clear_global_1528.txt` 5 · 20 s 뒤 그대로 | nvblox 기억 | ？(층별 미확인) |
| 14 | prep #2 | `jobs/up_prep_1028.sh 2` | `outputs/prep_smac_1028_2.txt` PREP_OK 0.010 m | 재기동으로 갇힘 풀림 기대 | ✔ |
| 14 | prep 뒤 dry_run | `jobs/up_place_dry_1028c.sh` → `jobs/chk_place_dry_1028c.sh`(목록: W3 먼저) | `outputs/chk_place_dry_1028c6.txt` 8/8 | 경로 조회 정상 | ✔ |
| 14.1 | f2pl5 W3 왕복 | `jobs/up_place_s1_1028.sh f2pl5 w3` | `outputs/drives/f2pl5/place_s1.log` 91.7 · 100.2 s arrived | 통과 | ✔(접촉 0, 사용자) |
| 14.1 | 명령 · 결과 그림 | `Docs/tools/fig_place_run.py`(새 상시 도구) | `outputs/fig_place_run_f2pl5.png` | 막힘 재계획 1 회 위치 · 시각 표시 | ✔ |
| 16 | 휴대폰 웹 창구 확인 | `jobs/up_place_web_1028.sh` → `jobs/chk_place_web_1028.sh` | `outputs/place_web_chk1.txt` 403/200 · 명령 5/5 · PC 200 | 동작 | ✔(휴대폰 미확인) |
| 16.1 | 경로 없음 재발 · 둘레 | `jobs/chk_costmap_robot.py` · `jobs/chk_scan_band.py` | `outputs/chk_costmap_robot_1607.txt` · `chk_scan_band_1607.txt` | §13.1 과 같음 | ✔ |
| 16.1 | 어디서 닫혔나 | `jobs/chk_costmap_dump.py` → `jobs/fig_gcm_reach.py` | `outputs/gcm_reach_1610.png` 닿는 칸 1.3 m² | 출발 방 닫힘 | ✔ |
| 16.1 | 닫은 칸이 정적 벽인가 | `jobs/anal_gcm_vs_static.py` | `outputs/gcm_vs_static_1610.txt` N 185 칸 · 남쪽 띠는 # | 돌아간 벽 | ✔ — §13.1 해석 정정(§16.2) |
| 16.1 | 방향 추정 오차 | `jobs/chk_scan_align.py` | `outputs/scan_align_1615.txt` 0.140 → −32.5° 에서 0.295 | yaw 약 30° 틀림 | ✔ |
| 16.1 | 정지 중 어느 TF 가 돌았나 | 인라인 rosbags(f2pl5 bag 끝) | `outputs/odom_yaw_end_f2pl5.txt` odom→base −161.4° → 지금 −144.8°, map→odom 불변 | odom yaw 드리프트 + SLAM 미보정 | ？(자이로/cuVSLAM 미확인) |
