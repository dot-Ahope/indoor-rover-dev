# 복귀 길 출발점 상자 칸 — 밀린 기억 · 다시 못 봄 · 접촉(f2lp1) (8 기: 10-19 §20 ~ §22 · 10-22 §11 ~ §11.4 · §13 · §13.1 · §17)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회(10-22) — 원인 둘은 측정으로 확인, 둘 다 남음.** ① **기억 밀림**: 복귀 길 상자는 차체 옆에서는 시야 밖이라 지도의 상자 = 그 전에 본 것의 odom 기억이고, 그 사이 EKF 오차를 SLAM 이 고칠 때마다 지도에서 통째로 밀린다(f2x1 +2.7~+6.1 cm · f2y1 map→odom +41.7 cm · f2pr1 +4.2~+5.0 cm, 출발 기억은 +9.9 cm) ② **다시 못 봄**: 프로젝터 상시 끔 + 깊이 프리셋 3 에서 복귀 쪽 상자 화소의 83~100 % 가 깊이 0 → 새로 찍지도 비우지도 못함. 둘이 겹쳐 f2lp1 은 세 지도 모두 상자 0 칸인 채 **상자를 침**(10-22 §13). 대응 = 통합 거리 1.4 → 2.0(10-22 §14 ~ §15, [유령 칸 · 프리셋 카드](ghost-cells-depth-preset.md)) — f2pi1 1 회 접촉 0, 단 실제 여유 **1.1 cm**(지도 5.6 cm, §17) | 10-19 §20 ~ §22, 10-22 §11 ~ §11.4 · §13 · §13.1 · §17 (이 카드). 이후(10-23 ~): 경로 추종 · 재계획 쪽 | [10-19 §21](../debug_log/2026-10-19/SUMMARY.md)(사용자 "복귀 시 상자 근처에서 셀 번짐 문제가 있었는지 알수가 없다") · §22("복귀 시 상자 범위 내에 셀이 없는 것 같은데?") · [10-22 §11](../debug_log/2026-10-22/SUMMARY.md)("복귀 시 상자칸 밖에 노란색 칸이 찍힌 것") · §12.1("방금 상자를 치고 돌아가서") | 이 카드에서 바꾼 설정 없음. 통합 거리 2.0 은 `ros2_ws/src/rover_navigation/config/nvblox_local.yaml` 57 행(10-22 §15 — 근거 주석 54~56 행에 이 카드의 f2lp1 §13 · §14.2) | [카메라 상자 칸 과장의 근원](box-exaggeration-source.md)(같은 기전을 출발점 상자 · f2x1 로 분해한 카드) · [상자 옆 정지 — 기전](box-side-stall-cause.md)(10-13 §6.2 '기억 밀림 4~5 cm' 의 앞 줄기) · [상자 옆 정지 — 대책](box-side-stall-remedies.md) · [유령 칸 · 깊이 프리셋 · 통합 거리 2.0](ghost-cells-depth-preset.md)(10-21 ~ 22 결정 — 프리셋 3 의 대가가 이 카드의 '다시 못 봄') · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(감쇠 약 78 s · 지우기 반경 3.0) · [회전 중 장애물 번짐](rotation-obstacle-smear.md) · [경로 추종 · 재계획 · B0](path-tracking-replan-b0.md)(10-23 — 1.1 cm 근접의 다음 줄기) |

**한 줄**: 출발점의 라이다보다 낮은 시험 상자는 카메라만 본다. 복귀 길에서 로버는 상자 북쪽을 서쪽으로 지나는데, 그때 상자는 차체 옆이라 **시야 밖** — 지도의 상자는 문 쪽(남동)에서 회전하며 본 것의 odom 기억이다. 10-19 는 그 기억이 EKF 미끄러짐만큼 지도에서 밀려 '상자 안은 비고 둘레에 흩어진 칸' 이 되는 것을 쟀고(f2y1 상자 안 8 → 1 칸), 10-22 는 프리셋 3 주행에서 상자 밖 칸이 '밀린 기억 + 관측 수 cm + 칸 경계' 이며 그 자리를 다시 봐도 깊이가 0 이라 안 지워진다는 것, 그리고 같은 조건에서 상자를 **아예 못 다시 봐서**(1.4 m 통합 거리 안에 들 때는 회전 중 시야 밖) 로버가 상자를 친 것(f2lp1)을 밝혔다. 통합 거리 2.0 으로 접촉 37 s 전부터 상자를 갖게 됐으나(재생), 다음 주행 f2pi1 의 실제 여유는 1.1 cm — 이번엔 기억이 로버 반대쪽으로 약 3 cm 틀려 '여유가 더 있다' 고 본 것.

## 1. 증상
- **f2y1(10-19 §21 · §22, 번갈이 30 합성)**: 복귀 길 상자 확대 그림에서 상자가 꽉 찬 덩어리가 아니라 흩어진 칸, 서쪽 면 과장 **+18.2 cm** = 상자 서쪽 10~18 cm 에 떨어진 칸 3~4 개(x 0.97~1.07, y −0.08~−0.12). 상자 안 칸 출발 8 → 복귀 **1**. 주행은 3/3 · 정지 진단 0(이 칸들로 멈추지는 않음). 그림 [`box_zoom_f2x1_f2y1.png`](../debug_log/2026-10-19/figures/box_zoom_f2x1_f2y1.png) · [`f2y1_ir_drive_zoom_t200.png`](../debug_log/2026-10-19/figures/f2y1_ir_drive_zoom_t200.png).
- **f2pr1(10-22 §11, 프리셋 3)**: 복귀 창(t ≥ 120 s) 상자 둘레 칸 중 상자 밖 (1.20, 0.00) 21 % · (1.20, 0.05) 13 %(노랑 · 주황). 그림 [`box_cells_preset.png`](../debug_log/2026-10-22/figures/box_cells_preset.png).
- **f2lp1(10-22 §12.1 · §13, 프리셋 3, 두 바퀴 주행)**: 사용자 "그만 멈춰라. 방금 상자를 치고 돌아가서, 2번째 주행에는 상자가 안보인다." — 첫 겹침 t 193.8~204.2 s(1 바퀴 복귀, 목표 3), 그 순간 상자 영역 칸 로컬 · 전역 · 조각 **모두 0**, Nav2 사건 없음. [`anal_contact_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_contact_f2lp1.txt):
  ```
   15:48:13.82~15:48:24.22 (t 193.8~204.2 s) 최소 -0.010 m @ 15:48:15.16 t 195.1 · 로버 (1.53, -0.03, 175°) · 지령 v 0.080 ω -0.01 | 상자 영역 칸: 로컬 LETHAL 0 · 전역 LETHAL 0 · 조각 0
  ```
  러너 기준 목표 3 은 SUCCEEDED 101.2 s([`run_f2lp1.txt`](../debug_log/2026-10-22/outputs/run_f2lp1.txt)) — '성공' 안에 접촉이 있었다.
- **f2pi1(10-22 §16 · §17, 프리셋 3 + 통합 2.0)**: 접촉 없음(형식), 차체 ↔ 기록 상자 최소 **+0.012 m**, 영상 기준 실제 여유 1.1 cm @ t 210.2 s 인데 그 순간 지도 여유 5.6 cm.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 앞 시기 10-13 §6.2 | 출발점 상자 끝 칸을 층별 추적 | 상자는 1.5 m 에서 관측돼 odom 에 기억, 시야 밖 뒤 map→odom 변화 y +4.1 · +5.0 cm 만큼 밀림(추정) | 기억 밀림 4~5 cm | [기전 카드](box-side-stall-cause.md) |
| 10-19 §10 · §11 · §14 | f2x1 원시 점 · 기억 밀림 | 복귀 길 상자 옆에선 시야 밖, 지도의 상자 = 남동쪽 회전 중(t 154~165) 관측. 통과 순간까지 기억 밀림 북 +2.1~+7.3 cm | (c) 오도메트리 기억 밀림이 로버 쪽 몫의 주원인 | [과장 근원 카드](box-exaggeration-source.md) |
| 10-19 §20 | f2y1 IR 영상(다른 줄기 — cuVSLAM 입력 확인) | 영상 `figures/f2y1_ir_drive.mp4`(git 제외) | 이 영상에 §21 상자 확대 판을 붙임 | [`fig_ir_drive_video.py`](../debug_log/2026-10-19/jobs/fig_ir_drive_video.py) · [`f2y1_ir_drive_timeline.png`](../debug_log/2026-10-19/figures/f2y1_ir_drive_timeline.png) |
| 10-19 §21 | 상자 확대 판 · 두 주행 비교 그림(`fig_box_zoom_cmp.py`), 구간별 과장(`anal_slice_box.py` 구간 출력) | 출발 길 북 · 서 f2x1 +3.6 · −0.1 / f2y1 +5.8 · +0.9, 복귀 길 f2x1 +6.5 · +0.4 / f2y1 **+7.0 · +18.2**(서 범위 +5.2~+19.4). 두 주행 모두 복귀 길은 흩어진 칸, 남쪽 y −0.45~−0.65 창문틀 · 드론 띠 | f2y1 서쪽 +18 은 면이 부푼 게 아니라 **떨어진 칸**. 원인 후보 ① 번갈이 깊이 ② 관찰 경로 ③ 기억 밀림 — 미확정(1 회씩) | 그림 [`box_zoom_f2x1_f2y1.png`](../debug_log/2026-10-19/figures/box_zoom_f2x1_f2y1.png) · [`f2y1_ir_drive_zoom_t030.png`](../debug_log/2026-10-19/figures/f2y1_ir_drive_zoom_t030.png) · `_t200` · `_t206`. 구간별 표는 **원천 소실**(출력 파일 없음) |
| 10-19 §22 | 상자 안 칸 수 시간열(`anal_box_cells_in.py`) · f2y1 원시 점 | 상자 안 칸 출발 → 복귀 f2x1 7 → 3 · f2y1 8 → **1**, 주변 무리 중심 f2y1 (+4.6, **−10.5**) cm, map→odom 출발 → 복귀 f2x1 (−7.8, +17.3 cm, −3.0°) · f2y1 (−6.9, **+41.7** cm, −5.0°). f2y1 은 t 66 → 76 s 에 상자 안 6 → 1(같은 때 map→odom y +13 cm 점프 — SUMMARY). 누적 회전 휠 − EKF 차 f2y1 88.5° · f2x1 46.1° | 기전은 f2x1 과 같고 **크기가 2~3 배**(이번 주행의 미끄러짐이 큼). 번갈이 탓인지 주행마다 편차인지 미확정. '복귀 회전 중 관측이 상자를 남쪽으로 약 15.7 cm 옮겨 찍음' ⚠ **다른 지표 비교**(§5 어긋남 1) | [`anal_box_cells_in.txt`](../debug_log/2026-10-19/outputs/anal_box_cells_in.txt) · [`box_points_f2y1.csv`](../debug_log/2026-10-19/outputs/box_points_f2y1.csv) · [`run_f2x1.txt`](../debug_log/2026-10-19/outputs/run_f2x1.txt) 27 행 · [`run_f2y1.txt`](../debug_log/2026-10-19/outputs/run_f2y1.txt) 11 행. map→odom 1 s 점프 · IMU 끊김 비교는 **원문 없음** |
| 10-20 §3.2(다른 묶음) | 프로젝터 상시 끔 f2z1 · f2z2 | 복귀 길 주변 흩어진 칸 21 · 27(켬 8 · 번갈이 14), 무리 중심 상자 남쪽 12~13 cm | 흩어짐 증가는 2 회 재현 | [`anal_slice_box_f2z.txt`](../debug_log/2026-10-20/outputs/anal_slice_box_f2z.txt) |
| 10-22 §11 | 프리셋 3 f2pr1 복귀 창 상자 밖 칸(`anal_box_outside.py`) → 기억 이동(`anal_memory_shift.py`) | 상자 밖 두 칸 처음 찍힌 t **70.1 · 72.0 s**, 로버 (2.35~2.38, −1.43~−1.45), 칸까지 1.86~1.90 m · 방위 **+160~176°(로버 뒤)** → 새 관측일 수 없음. t 70 → 72 s 에 map→odom y +0.042 → +0.138, 출발(t 1.1 s) 기억 중심 **북 +9.9 cm** | 노란 칸 = 유령 아님, **상자 기억이 EKF 오차만큼 밀린 것**. 프리셋과 무관(f2dr2 프리셋 없음에도 북쪽 칸). ⚠ '복귀 창의 칸' 이라는 연결은 §11.2 에서 **정정** | [`anal_box_outside_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_box_outside_f2pr1.txt) · [`anal_memory_shift_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_memory_shift_f2pr1.txt) · [`anal_box_outside_f2dr2.txt`](../debug_log/2026-10-22/outputs/anal_box_outside_f2dr2.txt) |
| 10-22 §11.1 | 사용자 '로버 기준으로 실제 상자 자리인가' | 상자 기억 = odom, 로버 자세 = EKF odom → 상대 위치 오차 = 관측 뒤 EKF 누적 오차 = map→odom 변화(t 72 s +9.9 cm, t 160 s 0.26 m) | 로버 기준 **약 10 cm 틀린 자리** — §11.2 에서 '70~97 s 의 밀린 출발 기억' 에만 해당으로 수정 | 같은 파일 |
| 10-22 §11.2 | 칸별 장애물 구간 · 그때 시야(`anal_cell_timeline.py`) | 출발 기억은 t ≈ 97 s 에 모두 꺼지고 복귀까지 **75~100 s 비어 있음**. 복귀 (1.20, 0.00) 은 191~201 s(상자 '보임' 70/97 조각), 201~227 s 는 SLAM 1~1.5 cm 보정마다 한 칸씩 엇갈려 켜짐 | **§11 정정**: 복귀 창 칸은 복귀 중 새로 찍힌 것(→ §11.3 에서 다시 정정) | [`anal_cell_timeline_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_cell_timeline_f2pr1.txt) · [`anal_memory_shift_f2pr1_ret.txt`](../debug_log/2026-10-22/outputs/anal_memory_shift_f2pr1_ret.txt) |
| 10-22 §11.3 | 정정 1 건 + 원인 · 안 지워지는 이유(`anal_carve.py` f2dr2 깊이 bag, 상자 높이 z 0.06~0.11 기둥; `anal_memory_shift.py` t 172 기준; 재생 site 1.0 · 통합 2.0) | '보임' = 시야 판정일 뿐 깊이가 나왔다는 뜻 아님(**§11.2 정정**). 복귀 170~195 s 상자 몸통 점 **0** · 향한 화소 무효 **93 %**, 밖 칸 뒤로 닿은 광선 ≤ 1.4 m **0**. t 172 기억 → 190 s 북 +4.2 · 201.5 s +5.0 cm(칸 켜진 191.0 · 201.2 s 와 맞음). 재생 site 1.0 · 통합 2.0 둘 다 그 칸 179.2~217.5 s 그대로 | **원인** = 문 쪽 1.1~1.6 m 에서 본 상자의 odom 기억이 SLAM 보정(+4~5 cm 북)으로 칸 경계를 넘음 + 관측 수 cm(출발 원시 점 북 +2.6). **안 지워지는 이유** = 그 자리를 다시 본 게 아님 — 깊이 0 이라 새 관측도 비울 광선도 없음 → 감쇠(약 78 s)로만 사라짐. 대책 방향 (가) 오도메트리 (나) 그 면을 볼 깊이(프로젝터 끔과 충돌) → (가) 현실적(추정) | [`anal_carve_f2dr2_lowz.txt`](../debug_log/2026-10-22/outputs/anal_carve_f2dr2_lowz.txt) · [`anal_memory_shift_f2pr1_172.txt`](../debug_log/2026-10-22/outputs/anal_memory_shift_f2pr1_172.txt) · [`anal_box_points_f2dr2.txt`](../debug_log/2026-10-22/outputs/anal_box_points_f2dr2.txt) · [`rp_clr_1022.txt`](../debug_log/2026-10-22/outputs/rp_clr_1022.txt) · [`anal_cell_timeline_f2dr2_r0.txt`](../debug_log/2026-10-22/outputs/anal_cell_timeline_f2dr2_r0.txt) · `_site1.txt` · `_int2.txt` · [`anal_slice_zones_clr.txt`](../debug_log/2026-10-22/outputs/anal_slice_zones_clr.txt) |
| 10-22 §11.4 | '주행이 길어지면 더 많아지나'(`anal_mo_window.py`, 상자 중심 기억점 · 1 s 씩 미는 창) | 30 s 창 앞 · 뒤 절반 중앙 f2pr1 5.2 · 5.8 / f2dr2 1.7 · 5.6 / f2sm1 3.1 · 7.1 cm, 뒤 절반 95 % 23~34 cm | 기전상 '경과 시간에 비례' 가 아니라 '기억이 살아 있는 동안의 회전 · 미끄러짐'(추정). 뒤 절반엔 W3 큰 회전 · 긴 복귀가 있어 **시간 탓 vs 코스 탓 미분리** → 두 바퀴 주행 f2lp1 제안 | [`anal_mo_window.txt`](../debug_log/2026-10-22/outputs/anal_mo_window.txt) |
| 10-22 §12 · §12.1 | f2lp1 선언(바퀴별 비교 판정 0.7~1.3 배 = 코스 · ≥ 1.5 배 = 시간) → 사용자 정지 | 1 바퀴 3/3 · 2 바퀴 목표 4 64.4 s(12.6 s 김) · 목표 5 가던 중 정지(15:49:50.7 강제 종료, 남은 프로세스 0) | 상자가 밀려 **바퀴 비교 판정 무효** | [`run_f2lp1.txt`](../debug_log/2026-10-22/outputs/run_f2lp1.txt) · [`stop_f2lp1.txt`](../debug_log/2026-10-22/outputs/stop_f2lp1.txt) · [`chk_stop_f2lp1.txt`](../debug_log/2026-10-22/outputs/chk_stop_f2lp1.txt) |
| 10-22 §13 | 접촉 원인(`anal_contact.py` · `anal_box_maps_series.py` · `anal_carve.py`) | 접촉 = 1 바퀴 복귀 t 193.8~204.2 s, 세 지도 0 칸, Nav2 사건 없음. 상자 잃음: t 75 s 로컬 0(창 밖), t 95~100 s 조각 · 전역 0(감쇠) → **t 100~200 s 내내 0**. 복귀 중 상자 쪽 깊이: 164~167 s 1.46~1.67 m 44 점(**1.4 m 밖이라 nvblox 가 버림**), 167~171 s 1.22~1.44 m 0 점 · 무효 100 %, 185.7~195 s 0.72 → 0.1 m 4 점 · **무효 100 %**. 프리셋 없음 f2dr2 같은 구간 193 점. 복귀 중 유효 화소율 7~14 % | **시스템은 상자를 몰랐다**(측정). 프리셋 3 의 대가('낮은 상자 칸 절반 · 복귀 1~2 칸', §10)가 **0 칸 → 충돌** 로 나타남. 유령 = 멈춤, 놓침 = 충돌(더 나쁜 실패) | [`anal_contact_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_contact_f2lp1.txt) · [`nav_events_ms_f2lp1_contact.txt`](../debug_log/2026-10-22/outputs/nav_events_ms_f2lp1_contact.txt) · [`nav2_f2lp1.log`](../debug_log/2026-10-22/outputs/nav2_f2lp1.log) · [`anal_box_maps_series_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_box_maps_series_f2lp1.txt) · [`anal_carve_f2lp1_approach.txt`](../debug_log/2026-10-22/outputs/anal_carve_f2lp1_approach.txt) · [`anal_carve_f2lp1_box_full.txt`](../debug_log/2026-10-22/outputs/anal_carve_f2lp1_box_full.txt) · bag Jetson `~/bags/bag_f2lp1`(PC 사본은 스크래치패드 — 저장소 `bags/` 에 없음) · 로그 `2026-10-22/bags/logs_f2lp1/` |
| 10-22 §13.1 | 사용자 '접근 각도 문제' → 프리셋 3 두 주행 · 프리셋 없음 2.5 s 묶음 비교 | 167.5 s f2pr1 138° · 1.82 m · −5° · 0 칸 vs f2lp1 **113° · 1.59 m · +22°** · 0 칸. f2pr1 은 170 s 1.66 m · +10° 에서 1 칸 → 그 기억으로 경로 북쪽. f2dr2(프리셋 없음)는 +28~+40° · 1.39~1.53 m 에서도 3~5 칸 | f2lp1 은 약 2.5 s 일찍 북으로 꺾어 상자가 1.4 m 안에 들기 전 정면을 벗어남 → **사용자 판단과 맞음**. 단 각도 하나가 아니라 프리셋 3 의 '보이는 각 · 거리 창' 이 좁아져 드러난 것. 대책 방향 ① 통합 거리 2.0 ② 감쇠 늦추기 ③ 정면으로 다가오는 경로 | [`anal_approach_cmp.txt`](../debug_log/2026-10-22/outputs/anal_approach_cmp.txt) |
| 10-22 §14.2 · §15 · §16(다른 묶음) | f2lp1 통합 2.0 재생 → 배포 → f2pi1 | 재생: 복귀 접근 상자 영역 0 → **9** 칸(t 156.6 s 부터, 접촉 37 s 전), 맨바닥 A 0 → 2. f2pi1: 3/3, 최소 +0.012 m · 상자 칸 로컬 · 전역 · 조각 5, 상자 옆 PathBlockedAhead 2 · 스무더 충돌 2(판정 4 ✘). 옆 지날 때 지도 상자 칸은 실제 북쪽 면보다 **약 3 cm 남쪽**(로버 반대쪽) | 통합 2.0 채택 → [유령 칸 · 프리셋 카드](ghost-cells-depth-preset.md). 1.2 cm 근접 = 기억 오차(이번엔 반대 방향) + 칸 판정 여유 | [`anal_contact_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_contact_f2pi1.txt) · [`anal_cell_timeline_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_cell_timeline_f2pi1.txt) |
| 10-22 §17 | 복귀 상자 영상(`fig_return_video.py`, t 150~215 s) | 실제 여유 최소 **1.1 cm @ t 210.2 s**, 그 순간 로컬 코스트맵 치명 칸까지 **5.6 cm** — MPPI 는 4.5 cm 더 있다고 봄. **정정(말로 한 설명)**: '전역 코스트맵도 옮겨진 상자를 본다' 는 확인 안 한 말 — 10-21 §13.2 에선 전역 카메라 칸이 map→odom 만큼 안 움직임 | 측정한 밀림은 **조각(odom) · 로컬 코스트맵** 기준. 전역 nvblox 층의 칸 갱신 방식 미확인 | [`fig_return_video.txt`](../debug_log/2026-10-22/outputs/fig_return_video.txt) · 그림 [`f2pi1_return_210.png`](../debug_log/2026-10-22/figures/f2pi1_return_210.png) · 영상 `videos/f2pi1_return_box.mp4`(git 제외) |
| 10-22 §22 | 사용자 제안 '자홍칸이 적더라도 주황보다 노랑을 따르게' | 전역 감쇠 3.0 재검토 조건(통합 2.0 으로 상자가 37~50 s 전부터 지도에 있음) | 계산은 다음 날 → 10-23 §1.1 에서 0~5 cm(선언 ≥ 5 cm 미달) | [대책 카드](box-side-stall-remedies.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 복귀 길 상자 칸은 그때 새로 본 것 | 복귀 길 시야 · 원시 점(10-19 §10) | 상자 옆 통과 땐 차체 옆 = 시야 밖, 지도의 상자는 남동쪽 회전 중 관측의 기억 | **기각(f2x1 측정)** — 기억이다 |
| 기억이 오도메트리 오차만큼 지도에서 밀린다 | 관측 → 통과 map→odom 변화로 옮김(10-19 §11 · §14, 10-22 §11 · §11.3) | f2x1 +2.7~+6.1, f2pr1 출발 기억 +9.9(t 72 s) · 복귀 기억 +4.2~+5.0 cm — 칸이 켜진 시각 · 방향과 맞음 | **지지(측정, SLAM 이 참이라는 가정)** — SLAM 이 70 → 72 s 에 잘못 튀었을 가능성은 이 자료로 완전 배제 못 함(10-22 §11.1) |
| 상자 안 칸이 0 이 된 것 = 지워짐 | 상자 안 칸 수 시간열 vs map→odom(10-19 §22) | f2y1 t 66~76 s 6 → 1, 같은 때 map→odom y +13 cm(SUMMARY) | **밀림이 원인으로 지지(인과는 추정)**. t 81~164 s 의 0 은 조각 범위 밖일 수 있어 '잊음' 과 구분 못 함 |
| f2y1 의 큰 흩어짐 = 번갈이 구성 탓 | IMU 전달 비교(10-19 §22) | 198 Hz · 20 ms 넘는 끊김 54 vs 24 — 2.4 배 차이를 설명 못 함 | **미확인**(1 회씩) |
| 상자 밖 칸 = 프리셋 3 탓 | 프리셋 없음 f2dr2 복귀(10-22 §11) | f2dr2 에도 상자 북쪽 칸 | **기각** |
| 상자 밖 칸 = 출발 때 기억이 밀린 것 | 칸별 장애물 구간(10-22 §11.2) | 출발 기억은 97 s 에 꺼지고 75~100 s 공백 | **기각(§11 정정)** — 70~97 s 엔 맞으나 복귀 창 칸과는 다른 시간 |
| 상자 밖 칸 = 복귀 중 새 관측 | 시야 판정(§11.2) → 실제 유효 깊이 수(§11.3) | 그 방향 화소 83~93 % 깊이 0, 상자 몸통 점 0 | **기각(§11.3 정정)** — 172 s 기억의 밀림 + 관측 수 cm |
| 다시 보면 지워진다 · nvblox 설정으로 지워진다 | 칸 뒤로 닿은 광선 수(§11.3), 재생 site 1.0 · 통합 2.0 | ≤ 1.4 m 광선 0, 재생 둘 다 179.2~217.5 s 그대로 | **기각(측정)** — 2.0 에서 1.4 m 넘는 광선 105 개로도 못 지움(광선이 적어서인지 nvblox 가 안 비우는지 기전 미확인) |
| f2lp1 접촉 = Nav2 가 상자를 알고도 붙음 | 접촉 순간 세 지도 칸 · Nav2 사건(§13) | 0 · 0 · 0, 사건 없음 | **기각** — 모르고 지나감 |
| f2lp1 은 접근 각도 때문에 못 봄 | 프리셋 3 두 주행 · 프리셋 없음 비교(§13.1) | f2lp1 은 2.5 s 일찍 꺾음, 프리셋 없음은 같은 각에서도 3~5 칸 | **지지(부분)** — 각도 × 프리셋 3 의 좁은 창 |
| 주행이 길수록 기억 오차가 커진다 | 30 · 78 s 창 앞 · 뒤 절반(§11.4) | 뒤 절반이 큼(3 주행) | **미확인** — 코스(회전) 와 분리 못 함, 두 바퀴 시험은 접촉으로 무효 |

## 4. 조치와 효과
- **통합 거리 1.4 → 2.0**(10-22 §15, 사용자 결정 — 깊이 프리셋 3 과 함께, 결정 카드는 [유령 칸 · 프리셋](ghost-cells-depth-preset.md)): 근거가 이 카드의 f2lp1 접촉 — 같은 bag 재생에서 복귀 접근 상자 칸 0 → 9(접촉 37 s 전부터). 효과(측정 1 회): f2pi1 접촉 0 · 복귀 상자 칸 3 → 6~7(상자 2.35 m · −23° 에서 처음). 한계: 실제 여유 1.1 cm(지도는 5.6 cm) — 기억이 이번엔 로버 반대쪽으로 약 3 cm 틀림. 10-14 §6 에 1.4 로 줄였던 이유(멀리서 처음 본 면이 한 줄 두껍게 · 각 오차가 거리에 비례)는 그대로 남음 — 상자 옆 여유를 줄일 수 있음([기전 카드](box-side-stall-cause.md)).
- 그 밖엔 바꾼 것 없음. 이 카드의 결론이 가리키는 대책은 **오도메트리**(기억이 덜 밀리게) — 10-23 §16 cuVSLAM 병진 속도 융합 기본 채택(다른 묶음). 그 뒤에도 상자 옆 근접은 남아 '경로 추종 · 재계획' 줄기로 넘어감([경로 추종 · B0](path-tracking-replan-b0.md)).

### 4.1 지금 저장소 코드(11-03 확인, 고치지 않음)
| 항목 | 지금 | 이 시기 | 위치 |
|---|---|---|---|
| nvblox 통합 거리 | **2.0**(근거 주석에 f2lp1 §13 · §14.2) | 10-19 · 10-22 오전 1.4 → 10-22 §15 부터 2.0 | `ros2_ws/src/rover_navigation/config/nvblox_local.yaml` 57 행(주석 54~56 행) |
| nvblox 기억 좌표 · 감쇠 · 지우기 반경 | `global_frame: "odom"` · `tsdf_decay_factor 0.99`(약 78 s) · `map_clearing_radius_m 3.0` | 같음 | 같은 파일 16 · 70 · 42 행 |
| 깊이 프리셋 | `depth_preset` 기본 **3** | 10-22 §10 부터 | `ros2_ws/src/rover_bringup/launch/camera.launch.py` 118 행 |
| 프로젝터 | 표준 prep `ODOM=vslam` → `emitter_off:=true`(상시 끔) | 10-19 f2x1 켬 · f2y1 번갈이 → 10-21 §20 상시 끔 결정 | `Docs/tools/prep_patrol.sh` 11 행 · `camera.launch.py` 36~38 행 |
| 데시메이션 | 기본 4(160×120) | 같음 | `camera.launch.py` 120 행 |
| 오도메트리 | 주 EKF 병진 속도 = cuVSLAM(`vslam:=on`, 10-23 §16) | 이 시기 wheel + IMU(그림자 cuVSLAM 시험) | `prep_patrol.sh` 10~11 행 |
| 전역 nvblox 층 · inflation | 이진 · `max_obstacle_distance 0.40`, 전역 inflation 0.70 / 2.0 | 같음 | `config/nav2_params.yaml` 569~571 · 720~721 행. 전역 nvblox 층 칸이 map→odom 에 따라 어떻게 바뀌는지는 미확인(§17 정정) — 10-27 호스트 층 TF 실패 시 슬라이스 버림 패치(CLAUDE.md §6 ②)와 관계 미확인 |
| MPPI 경로 크리틱 | PathAlign 28 · PathFollow 5(10-26) | 14 · 10 | `nav2_params.yaml` 281 · 285 행 |

## 5. 내 실수 · 기록 어긋남
### 실수 ① '처음 찍힌 시각' 을 창 앞 60 s 부터만 읽음 (10-22 §11 같은 §)
- 본 것: 도구 첫 판이 상자 안 칸도 60.1 s 로버 뒤(방위 −138°)에서 생긴 것처럼 냄. 의심한 이유: 카메라가 못 보는 방위. 판별: 주행 처음부터 읽게 고침 → 상자 안 칸 t 1.1 s 정면(−4~−6°), 상자 밖 두 칸만 70~72 s 로버 뒤. 다음에 알아보는 법: '처음 찍힌' 은 bag 처음부터, 방위가 시야 밖이면 관측이 아니라 **기억 이동**을 먼저 의심. 데이터: [`anal_box_outside_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_box_outside_f2pr1.txt)(고친 판 출력만 남음 — 첫 판 출력 원문 없음).

### 실수 ② 출발 기억 밀림을 복귀 창 칸의 원인으로 이음 (10-22 §11 → §11.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 복귀 창 상자 밖 노란 칸의 출처 |
| 본 것 | 상자 밖 두 칸 처음 찍힌 시각 70~72 s 에 map→odom 이 +9.6 cm 뛰고 출발 기억이 북 +9.9 cm |
| 처음 추론 | 복귀 그림의 칸 = 출발 기억이 밀려 남은 것 |
| 의심한 이유 | 사용자 "출발 시 기억하던 셀을 복귀 시 다시 찍은 것인가?" — 칸의 **시간 구간**을 처음 봄 |
| 판별 시험 | `anal_cell_timeline.py` 로 칸마다 장애물 구간 |
| 결론 | 출발 기억은 97 s 에 꺼지고 75~100 s 공백 — 기전 계산은 맞지만 복귀 창 칸과는 다른 시간 |
| 다음에 알아보는 법 | '복귀 때 칸' 의 출처를 말하기 전에 칸의 시간 구간 · 그때 시야를 먼저 본다 |
| 스크립트 핵심 | [`anal_cell_timeline.py`](../debug_log/2026-10-22/jobs/anal_cell_timeline.py) 머리말 "'보임' = 상자 중심이 로버 진행 방향 ±43° … 안 · 1.4 m(통합 거리) 안. 구간은 0.5 s 넘게 끊기면 나눔" |
| 나온 결과 | [`anal_cell_timeline_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_cell_timeline_f2pr1.txt) `칸 (1.20, 0.00): … t 70.1 ~ 75.4 s · 조각 51 · 그중 상자 보임 0 …` · `t 191.0 ~ 201.1 s · 조각 97 · 그중 상자 보임 70 · 시작 때 상자 거리 0.76 m 방위 +28°` |
| 데이터 | 위 파일, 입력 `2026-10-22/bags/bag_f2pr1.tgz`(git 제외 — 로컬) |

### 실수 ③ '시야 안' 을 '보였다' 로 읽음 (10-22 §11.2 → §11.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 복귀 창 칸 = 복귀 중 새 관측인지 |
| 본 것 | 191~201 s 에 상자가 '보임'(시야 판정) 70/97 조각 |
| 처음 추론 | 그 칸은 복귀 중 새로 찍힌 것(§11.2 결론 2) |
| 의심한 이유 | 사용자 "해당 위치를 다시 보았을 때, 지워지지 않는 이유는?" — 다시 봤다면 TSDF 가 비웠어야 함 |
| 판별 시험 | `anal_carve.py` 로 그 방향 화소의 **유효 깊이 수**와 칸을 지나 뒤에 닿은 광선 수 |
| 결론 | 복귀 170~195 s 상자 몸통 점 0 · 향한 화소 무효 93 %, 밖 칸 뒤 광선(≤ 1.4 m) 0 → 다시 본 것이 아님. 칸 = t 172 기억의 밀림(+4.2 · +5.0 cm) |
| 다음에 알아보는 법 | '보였다' 를 말하려면 시야 판정이 아니라 **그 방향 화소의 유효 깊이 수**를 센다(SUMMARY §11.3 에 같은 문구) |
| 스크립트 핵심 | [`anal_carve.py`](../debug_log/2026-10-22/jobs/anal_carve.py) 58~61 행 `valid = zz > 0` · `ptin = valid & hit & (zz >= zin - 0.01) & (zz <= zout + 0.01)` · `carve = valid & hit & (zz > zout + 0.05)` · `far = carve & (zz * np.linalg.norm(d, axis=1) > 1.4)` |
| 나온 결과 | [`anal_carve_f2dr2_lowz.txt`](../debug_log/2026-10-22/outputs/anal_carve_f2dr2_lowz.txt) `== t 170 195 기둥 1.15,1.30,-0.20,-0.05 z 0.06~0.11` → `합: 기둥 안 점 0 · 뒤에 닿은 광선 ≤1.4 m 0 · >1.4 m 78 · 기둥 향한 무효 화소 969 / 1047` |
| 데이터 | 위 파일, 입력 `2026-10-22/bags/bag_f2dr2.tgz`(로컬) |
- 같은 도구의 두 실수(도구 머리말에 적힘): ① z 0.06~0.30 기둥이 낮은 상자(0.114 m) **위**를 지난 광선까지 '비우는 광선' 으로 셈 → 상자 높이 기둥으로 다시(§11.3) ② 광선 표본을 1.0 m 까지만 → 0.8 m 넘는 접근을 못 봄 → 1.6 m(§13, 44 행 `S = np.arange(0.02, 1.6, 0.02)`).

### 기록 어긋남 (이번 확인)
| # | 기록 | 원문 · 재계산 | 판정 |
|---|---|---|---|
| 1 | 10-19 §22 '복귀 때는 회전 중(로버 yaw 103~149°, 1.1~1.6 m)에만 보였고 **그 관측이 상자를 남쪽으로 약 15.7 cm 옮겨 찍음**(f2x1 은 남동 3~5 cm, §14)' | 11-03 카드 작성 중 [`box_points_f2y1.csv`](../debug_log/2026-10-19/outputs/box_points_f2y1.csv) 재계산(t > 100 s 76 프레임, 결과 파일 없음 — 발췌가 전부): `north_off 중앙 -15.659 · south_off +2.652 · east_off +2.225 · 상자 점 중심 y -0.188(기록 -0.110)`, 로버 (2.23~2.54, −1.07~−1.52) = 상자 **남동쪽**. 같은 지표로 f2x1 남동 관측도 북 **−15.2**([`anal_box_points_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_points_f2x1.txt) 구간 t 154~165 줄) | 15.7 은 남동쪽에서 **안 보이는 북 면**의 백분위 값 — §14 는 같은 상황에서 이 값을 버리고 남 · 동 면(+2.9 · +4.8)을 썼다. 같은 방법이면 f2y1 남동 관측 = 남 +2.7 · 동 +2.2 cm(점 중심 남쪽 7.8 cm — f2x1 은 7.1 cm). '관측이 f2x1 보다 훨씬 틀렸다' 는 근거가 아님. §22 의 '크기 2~3 배' 는 map→odom(+41.7 vs +17.3) · 휠 − EKF(88.5 vs 46.1°) 쪽 근거로는 유지 |
| 2 | 10-19 §21 구간별 과장 표(f2x1 +3.6 · +6.5 / f2y1 +5.8 · +7.0 · +18.2) | 출력 파일 없음(`anal_slice_box.py` 구간 출력을 저장 안 함) | **원천 소실**(그림 2 장은 남음) |
| 3 | 10-19 §22 'map→odom y 1 s 안 6.6 · 8.2 cm 점프', 'IMU 20 ms 넘는 끊김 54 vs 24 · 최대 205 vs 181 ms' | `anal_box_cells_in.txt` 에 없음, 다른 출력 파일 없음 | **원문 없음** |
| 4 | 10-19 §25 '상자를 치우고 주행' | 10-20 §3.2 사용자 정정: 치우지 않았다 | 이미 정정됨(f2z1 출발 상자 칸 8 = 실물) |
| 5 | 10-22 §11 · §11.1 '복귀 창 상자 밖 칸 = 출발 기억 밀림 · 로버 기준 약 10 cm' | §11.2 · §11.3 두 번 정정 | 이미 정정됨 — 최종: 172 s 기억의 +4~5 cm 밀림 + 관측 수 cm, 로버 기준 수 cm |
| 6 | 10-22 §17 이전 대화 '전역 코스트맵도 옮겨진 상자를 본다' | §17 정정(10-21 §13.2 와 다름) | 이미 정정됨 — 전역 nvblox 층 갱신 방식 미확인 |

## 6. 남은 것 (10-22 시점)
- **기억 밀림 자체** — nvblox 가 odom 좌표로 기억하는 한 남는다. map 좌표 기억은 10-19 §12 에서 나빠짐(+7.0 vs +5.3). 줄일 길은 오도메트리(10-23 vslam:=on) — 그 뒤 복귀 상자 기억 밀림을 같은 도구(`anal_memory_shift.py` · `anal_mo_window.py`)로 다시 잰 기록은 이 시기에 없음.
- **프리셋 3 · 프로젝터 끔의 '다시 못 봄'** — 복귀 쪽 상자 화소 무효 83~100 %. 무늬 없는 · 더 낮은 물체는 더 못 볼 수 있음(추정). 통합 2.0 은 멀리서 정면일 때 보게 해 준 것이지 가까이서 다시 보게 한 것이 아님.
- 칸 뒤로 닿은 광선으로 nvblox 가 칸을 비우는지(1.4 m 넘는 광선 포함) 기전 미확인(10-22 §11.3).
- 전역 nvblox 층의 칸이 map→odom 변화에 따라 어떻게 바뀌는지 미확인(10-22 §17 정정).
- '주행이 길수록' (시간 vs 코스) 판별 — f2lp1 이 접촉으로 무효, 재시험 없음(10-22 §12.1).
- f2pi1 1.1 cm 근접(통합 2.0 뒤) — 지도 여유 5.6 cm 와 실제 1.1 cm 의 차 4.5 cm = 기억 오차 약 3 cm + 칸 판정. 다음 줄기(10-23)는 이를 '경로 추종' 으로 다룸.

## 7. 이후 (10-23 ~)
- 10-23 §1.1(다른 묶음): 사용자 제안(10-22 §22) 계산 — 전역 감쇠 2 → 3 은 경로를 0~5 cm 만 밀어냄(선언 ≥ 5 cm 미달), 기록된 전역 경로는 이미 상자에서 10~14 cm — [`anal_ginfl_path_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_ginfl_path_f2pi1.txt). §2 ~ §4 '붙은 것은 로버(추종)' → [경로 추종 · B0](path-tracking-replan-b0.md).
- 10-23 §10 ~ §11 · §16: cuVSLAM 병진 속도 융합 기본 채택 — 위치 추정은 좋아졌으나 상자 옆 실제 여유 3.3 · 0.3 cm(다른 묶음).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2x1 · f2y1 | 10-19 깊이 기록(켬) · IR 기록(번갈이 30 합성) b910 | 10-19 §6 · §19, [`run_f2x1.txt`](../debug_log/2026-10-19/outputs/run_f2x1.txt) · [`run_f2y1.txt`](../debug_log/2026-10-19/outputs/run_f2y1.txt) · [`anal_box_cells_in.txt`](../debug_log/2026-10-19/outputs/anal_box_cells_in.txt), bag Jetson `~/bags/bag_f2x1` · `bag_f2y1`(PC 로컬 없음) |
| f2pr1 · f2dr2 | 10-21 · 22 프리셋 3 · 프리셋 없음 b910 | 10-22 §11 ~ §11.4, `anal_box_outside_*.txt` · `anal_memory_shift_f2pr1*.txt` · `anal_cell_timeline_*.txt` · `anal_carve_f2dr2_lowz.txt`, bag `2026-10-22/bags/bag_f2pr1.tgz` · `bag_f2dr2.tgz`(로컬) |
| f2dr2 재생 r0 · site1 · int2 | 상자 밖 칸이 설정으로 지워지나 | 10-22 §11.3, [`rp_clr_1022.txt`](../debug_log/2026-10-22/outputs/rp_clr_1022.txt) · `anal_cell_timeline_f2dr2_{r0,site1,int2}.txt` · `anal_slice_zones_clr.txt`, 재생 `bags/replay_f2dr2_int2.tgz` |
| 창 이동 | f2pr1 · f2dr2 · f2sm1 map→odom 30 · 78 s 창 | 10-22 §11.4, [`anal_mo_window.txt`](../debug_log/2026-10-22/outputs/anal_mo_window.txt) |
| f2lp1 | 두 바퀴 b910x2, 1 바퀴 복귀에서 상자 접촉 → 사용자 정지 | 10-22 §12 ~ §13.1, `run_f2lp1.txt` · `stop_f2lp1.txt` · `anal_contact_f2lp1.txt` · `anal_box_maps_series_f2lp1.txt` · `anal_carve_f2lp1_*.txt` · `anal_approach_cmp.txt` · `nav2_f2lp1.log`, bag Jetson `~/bags/bag_f2lp1`(470 MB) |
| f2pi1 | 프리셋 3 + 통합 2.0 검증(다른 묶음) — 복귀 상자 영상 | 10-22 §16 · §17, `anal_contact_f2pi1.txt` · `anal_cell_timeline_f2pi1.txt` · `fig_return_video.txt`, bag `bags/bag_f2pi1.tgz` |
| 도구(10-19) | `fig_ir_drive_video.py` · `fig_box_zoom_cmp.py` · `anal_box_cells_in.py` · `anal_box_points.py` · `anal_slice_box.py`(구간 출력) | `2026-10-19/jobs/`, §9 |
| 도구(10-22) | `anal_box_outside.py` · `anal_memory_shift.py` · `anal_cell_timeline.py` · `anal_carve.py` · `anal_mo_window.py` · `anal_contact.py` · `anal_box_maps_series.py` · `fig_return_video.py` · `fig_box_cells.py` · `stop_now.sh` · `chk_stop.sh` · `get_bag_f2lp1.sh` | `2026-10-22/jobs/`, §9 |

## 9. 도구 해설
공통: 모두 PC `rosbags`(AnyReader, Humble 타입, `nvblox_msgs/DistanceMapSlice` 손 등록). 조각 · 로컬 코스트맵 = odom → 그 시각 map→odom 으로 지도에. 상자(기록) x 1.151~1.261 · y −0.20~−0.02, 중심 (1.206, −0.110). t = 주행 bag 첫 tf(또는 bag 시작) 기준 초. '보임'(시야 판정) = 상자 중심이 ±43° · 1.4 m 안 — **유효 깊이를 뜻하지 않음**(실수 ③). 앞 줄기 도구(`anal_slice_box.py` · `anal_box_points.py` · `run_nvblox_replay.sh`)는 [과장 근원 카드 §9](box-exaggeration-source.md).

### 9.1 `anal_box_cells_in.py` — 상자 안 칸 수 · 주변 무리 (10-19 §22)
- 형태: `anal_box_cells_in.py 이름=주행bag …`. 왜: 사용자 '복귀 때 상자 범위 안에 칸이 없다' — 지워졌나 밀렸나.
- 하는 일: 조각 거리 ≤ 0 칸 중심을 지도로, 로버가 상자 옆(x 0.9~1.7, |y| < 0.6)일 때만. 상자 안 = 칸 중심이 기록 상자 안(최대 ≈ 2 × 4 = 8 칸), 주변 무리 = x 0.9~1.5 · y −0.35~+0.15(남쪽 띠 제외) 칸의 개수 · 중심. 5 s 넘게 끊기면 구간(출발 길 · 복귀 길), 구간 가운데 조각의 map→odom 을 출발 길 대비로. 끝에 4~5 s 간격 '상자 안 칸 수' 시간열(상자 옆 조건 없이).
- 출력 [`anal_box_cells_in.txt`](../debug_log/2026-10-19/outputs/anal_box_cells_in.txt): `복귀 길 t 189.0~209.1 s · 조각 191 · 상자 안 칸 중앙 1 (범위 1~1 …) · 주변 무리 중심 (1.252, -0.215) = 상자 중심 대비 (+4.6, -10.5) cm · map→odom 출발 길 대비 (-6.9, +41.7 cm, -4.95°)`.
- 결함: 시간열의 0 은 '조각 범위 밖' 과 '잊음' 을 못 가름(10-19 §22 자체가 적음). 재사용 가능. 계보: 10-22 `anal_box_maps_series.py`(세 지도 · 묶음 판).

### 9.2 `fig_box_zoom_cmp.py` · `fig_ir_drive_video.py` — 상자 확대 그림 · IR 주행 영상 (10-19 §20 · §21)
- `fig_box_zoom_cmp.py 출력.png 이름=주행bag …`: 출발 · 복귀 통과 순간(상자 옆 구간에서 상자 중심에 가장 가까웠던 조각)의 조각 칸(거리 색) · 실제 상자 · 차체를 나란히. 출력 [`box_zoom_f2x1_f2y1.png`](../debug_log/2026-10-19/figures/box_zoom_f2x1_f2y1.png).
- `fig_ir_drive_video.py`: Jetson `fig_ir_extract.py` 가 뽑은 IR 짝 프레임 + 주행 bag 지도 · 자세 · 시야 · 시간축, §21 에 아래 가운데 상자 확대 판(조각 칸 · 실제 상자 · 그 순간 북/서 면 과장) 추가. 영상 `figures/f2y1_ir_drive.mp4`(git 제외), 정지 화면 `f2y1_ir_drive_zoom_t030/t200/t206.png`. 계보: 10-23 `Docs/tools/fig_drive_video.py` 가 기본 영상 도구로.

### 9.3 `anal_box_outside.py` — 상자 밖 칸이 언제 · 어디서 (10-22 §11)
- 형태: `anal_box_outside.py 주행bag [창 시작 s=120] [영역 x0,x1,y0,y1]`. 하는 일: 창 안 조각에서 영역 칸별 장애물 비율, 칸마다 **bag 처음부터**(실수 ① 뒤) 처음 찍힌 시각과 그때 로버 자세 · 칸까지 거리 · 방위, 그 뒤 창 끝까지 map→odom 이동.
- 출력 [`anal_box_outside_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_box_outside_f2pr1.txt): `(1.20,  0.00) | 밖 |  21 % |   70.1 s | ( 2.35, -1.45,   -49°) · 1.86 m · +176° | 0.324 m · -2.9°`. 결함: '처음' 만 보고 중간 꺼짐 · 다시 찍힘을 모름 → `anal_cell_timeline.py`.

### 9.4 `anal_memory_shift.py`(10-22 판) — 기준 시각 기억을 map→odom 만 바꿔 옮김
- 형태: `anal_memory_shift.py 주행bag 기준시각s 시각들s(쉼표)`. 상자 중심 → 기준 시각 map→odom 역변환(odom 점) → 각 시각 map→odom 으로 지도. 24 행짜리.
- 출력: `t  72.0 s · map→odom (0.028, 0.138, -1.94°) · 기억된 상자 중심 → (1.233, -0.016) · 밀림 Δx +0.027 Δy +0.094 (0.098 m)`([`anal_memory_shift_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_memory_shift_f2pr1.txt)) · `t 201.5 s … 밀림 Δx -0.002 Δy +0.050`([`_172.txt`](../debug_log/2026-10-22/outputs/anal_memory_shift_f2pr1_172.txt)). 가정: 기억된 것이 상자 중심 한 점 · SLAM 이 참. 계보: 10-15 같은 이름(칸별 판) · 10-19 `anal_box_memory.py`.

### 9.5 `anal_cell_timeline.py` — 칸별 장애물 구간 · 그때 시야 (10-22 §11.2)
- 형태: `anal_cell_timeline.py 주행bag 'x,y;x,y' [조각bag]`(칸 왼아래, 0.05 m; 조각bag = 재생 출력이면 그 칸이 재생에서 어떻게 되는지). 0.5 s 넘게 끊기면 구간을 나누고 구간마다 조각 수 · '보임' 조각 수 · 시작 때 상자 거리 · 방위 · 출발 기억이 옮겨 갔을 지도 위치.
- 출력 [`anal_cell_timeline_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_cell_timeline_f2pr1.txt)(§5 실수 ② 발췌). 쓰인 곳 §11.2 · §11.3(재생 r0 · site1 · int2) · §14.2 · §16. 결함: '보임' 정의(실수 ③).

### 9.6 `anal_carve.py` — 칸 기둥을 찍는 점 · 비우는 광선 (10-22 §11.3 · §13)
- 형태: `anal_carve.py 깊이bag 시작s 끝s 'x0,x1,y0,y1' [z0,z1=0.06,0.30]`. 하는 일: 깊이 화소마다 광선을 2 cm 간격 표본(광학 z 1.6 m 까지)으로 기둥 통과 여부 → 기둥 안 점(`ptin`) · 기둥을 지나 5 cm 넘게 뒤에서 끝난 광선(`carve`, 끝이 1.4 m 넘으면 `far` 따로) · 기둥을 향했는데 깊이 0 인 화소. 프레임 줄 + 합.
- 출력: [`anal_carve_f2lp1_approach.txt`](../debug_log/2026-10-22/outputs/anal_carve_f2lp1_approach.txt) `164.4 | 1.65 m ·   -9° | 11.2 |    6 |    0 ·    0 |   11 / 18` · [`anal_carve_f2lp1_box_full.txt`](../debug_log/2026-10-22/outputs/anal_carve_f2lp1_box_full.txt) 끝 줄 `합: 기둥 안 점 4 · 뒤에 닿은 광선 ≤1.4 m 0 · >1.4 m 0 · 기둥 향한 무효 화소 46902 / 46906`.
- 결함: nvblox 가 1.4 m 넘는 광선을 어떻게 다루는지 · 광선 몇 개가 있어야 칸을 비우는지 모름(도구가 스스로 적음). 첫 판 실수 2 건(§5). 재사용 가능(깊이 bag).

### 9.7 `anal_mo_window.py` — 창 안 map→odom 변화 = 기억이 틀어지는 양 (10-22 §11.4)
- 형태: `anal_mo_window.py W(s) bag …`. 기억점 = 상자 중심, 창을 1 s 씩 밀며 창 시작 → 끝 map→odom 이 그 점을 지도에서 옮기는 양, 앞 · 뒤 절반의 중앙 · 95 % · 최대. 출력 [`anal_mo_window.txt`](../debug_log/2026-10-22/outputs/anal_mo_window.txt) `bag_f2sm1 · 길이 221 s · … 창 30 s 이동: 앞 절반 중앙  3.1 · 95 %  8.4 · 최대 12.8 cm | 뒤 절반 중앙  7.1 · 95 % 33.7 · 최대 36.4 cm`. 한계: 그 시간에 기억된 물체가 옆에 있었는지는 따로.

### 9.8 `anal_contact.py` · `anal_box_maps_series.py` — 접촉 순간 · 상자를 언제 잃었나 (10-22 §13)
- `anal_contact.py bag [D=0.10]`: map 기준 차체 사각형 ↔ 기록 상자 사각형 최소 거리 시계열, D 이하 구간마다 최소 순간의 로버 자세 · 지령 · 상자 영역(±0.10 m) 칸 수(로컬 LETHAL · 전역 LETHAL · 조각). 0 이하 = 겹침(SLAM 오차 수 cm 포함, 상자가 밀린 뒤 값은 의미 없음). 출력 §1 발췌. 10-22 §15 부터 주행 판정 도구로 반복 사용(f2pi1 · 10-23).
- `anal_box_maps_series.py bag 시작s 끝s [묶음 s=5]`: 상자 ±0.05 m 영역 칸 수를 세 지도에서 묶음 최대로 + 로버 · 상자 거리 · 방위 · 시야 표시. 출력 [`anal_box_maps_series_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_box_maps_series_f2lp1.txt) `t  190.0 | S   0 · L   0 · G   0 | 로버 ( 1.74, -0.05,  175°) 상자 0.53 m 방위  +12°  ← 시야(±43°·1.4 m)`, 2.5 s 판 [`anal_approach_cmp.txt`](../debug_log/2026-10-22/outputs/anal_approach_cmp.txt).

### 9.9 `fig_return_video.py` — 복귀 상자 영상 (10-22 §17)
- 왼쪽 상자 둘레 확대(로컬 코스트맵 = MPPI 가 보는 값 · 조각 칸 자홍 · 실제 상자 · 전역 `/plan_smoothed` · `/transformed_global_plan` · 카메라 시야 ±43° · 2.0 m), 오른쪽 위 깊이 영상(160×120, 프리셋 3)과 상자 모서리 투영 · 유효 화소 수, 오른쪽 아래 실제 여유 · 지도 여유 · 전진 명령 + nav2 사건. 출력 [`fig_return_video.txt`](../debug_log/2026-10-22/outputs/fig_return_video.txt) 끝 줄 `영상 videos/f2pi1_return_box.mp4 651 장 · 실제 여유 최소 1.1 cm @ t 210.2 · 지도 여유 그때 5.6 cm`. 계보: 10-23 `fig_return_video2.py`(MPPI 최적 궤적 추가) → `Docs/tools/fig_drive_video.py`.

## 10. 용어
- **odom 기억 · 기억 밀림**: nvblox 칸은 odom 좌표로 쌓인다. 로버도 odom(EKF) 위에서 움직이므로, 관측 뒤 EKF 가 잘못 센 이동만큼 '로버 기준 상자 위치' 가 틀어진다 — 지도(map)에서는 SLAM 이 map→odom 을 고치는 순간 칸이 통째로 옮겨 보인다.
- **TSDF 비우기(carving)**: 칸을 지나 그 뒤에서 끝난 깊이 광선이 있어야 그 칸이 자유 공간으로 갱신된다. 깊이 0(무효) 화소는 광선이 없으니 칸을 못 비운다 — 남은 기억은 감쇠(약 78 s)로만 사라짐.
- **통합 거리(max_integration_distance)**: nvblox 가 이 거리보다 먼 깊이를 지도에 넣지 않는 한도. 1.4 → 2.0 은 '멀리서 정면일 때 보는' 기회를 늘림.
- **깊이 프리셋 3(High Accuracy)**: 확신 낮은 깊이를 카메라 쪽에서 버리는 설정 — 맨바닥 유령이 0 이 된 대신 채움률 0.317 → 0.045(10-21 §21.1), 무늬 없는 면 · 비스듬한 면은 더 비게 됨.
- **'보임'(시야 판정) vs 유효 깊이**: 물체 중심이 카메라 시야각 · 거리 안에 든 것과, 그 방향 화소에 실제로 깊이가 나온 것은 다르다(10-22 §11.3).
