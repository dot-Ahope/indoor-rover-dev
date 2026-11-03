# 프로젝터 끔의 유령 칸 — 깊이 프리셋 3 · nvblox 통합 거리 2.0 결정 (8 기: 10-21 §13 ~ §15 · §20 · §21 ~ §21.2, 10-22 §0 ~ §10 · §12 · §14 ~ §16 · §21)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회** — 증상(상자 너머 맨바닥 · 문 사이에 카메라만 본 LETHAL 칸)은 깊이 프리셋 3 기본으로 막힘: 맨바닥 영역 A 0 칸(f2pr1)·끝 상태 nvblox 칸 −68 %. 원인 기전('프로젝터 무늬가 없으면 무늬 없는 바닥에서 스테레오 짝이 틀린다')은 **추정**(깊이 영상 대조 없음). 대가 = 라이다 아래 낮은 상자 칸이 절반(15 → 7)이고, 1.4 m 와 겹치면 복귀 때 0 칸이 되어 접촉(f2lp1) → 통합 거리 2.0 으로 되살림(f2pi1 3/3 · 복귀 상자 칸 3~8). min_weight 1 · 2 · 프리셋 5 기각 | 10-21 ~ 10-22(이 카드). 앞 이력 09-22 ~ 09-23 테이프 유령([N6 카드](nvblox-n6-global-ghosts.md)), 프로젝터 상시 끔 결정 10-20 ~ 10-21 §20([번갈이 카드](projector-ir-alternation.md)) | [10-21 §13](../debug_log/2026-10-21/SUMMARY.md) 사용자 "출발점에서 상자 뒤 · 문 가운데에 장애물 칸이 찍히는데 실제로는 없음" | [`camera.launch.py`](../../ros2_ws/src/rover_bringup/launch/camera.launch.py) `depth_preset` 인자 신설(10-21, 기본 −1) → 기본 **3**(10-22 §10, 커밋 `70aaec3b`) · [`nvblox_local.yaml`](../../ros2_ws/src/rover_navigation/config/nvblox_local.yaml) `projective_integrator_max_integration_distance_m` 1.4 → **2.0**(10-22 §15, 커밋 `9087d936`) · `esdf_integrator_min_weight` 0.1 그대로(1 · 2 재생 기각) | [Phase N 후반 · 유령 셀](nvblox-n6-global-ghosts.md)(09-22 테이프 유령 · 통합 거리 1.4 의 출발점) · [프로젝터 · IR 번갈이 · 상시 끔](projector-ir-alternation.md)(유령이 커진 배경 — 10-21 §16~§20) · [상자 과장의 출처 · f2lp1 접촉](box-exaggeration-source.md)(10-22 §11 · §13 — 2.0 의 직접 이유) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(출발점 낮은 상자 = 라이다 아래 시험 물체) · [카메라 깊이 장애물](depth-obstacle-costmap.md)(카메라 층의 처음) · [상자 옆 정지 — 기전](box-side-stall-cause.md) · [상자 옆 정지 — 대책](box-side-stall-remedies.md)(통합 거리 1.4 ↔ 2.0 이력) · [경로 추종 · 재계획 · B0](path-tracking-replan-b0.md)(10-22 §4.1 · §16 멈칫) · [10-19 ~ 10-23 운용 · prep 실패](drive-ops-1019-1023.md)(10-22 §5.1~§5.3) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md)(같은 날 그림자 주행 f2sm1 · f2sm3) · [카메라 컨테이너 SHM](camera-container-shm.md) (8 기) |

**한 줄**: 10-20 에 프로젝터를 상시 끈 뒤 출발점 둘레(상자 너머 맨바닥 · 문 사이)에 지도에도 라이다에도 없는 LETHAL 칸이 쌓였다. bag 대조로 출처는 nvblox(카메라 깊이)이고 맨바닥 칸은 **끔 주행에서만** 28~99 칸(켬 0~3)임을 확인했다(10-21 §13~§15, 처음엔 '켬에서도 생긴다' 고 잘못 읽고 정정). 대책으로 카메라 안에서 확신 낮은 깊이를 버리는 깊이 프리셋 3(High Accuracy)을 정지 시험(pr1: 깜빡 복셀 101.5 → 2) · 주행(f2pr1: 맨바닥 A 0)으로 확인했으나 낮은 상자 칸이 절반(15 → 7)이 되어 선언 기준 3 미달. 같은 날 프리셋 없음 기록 주행 f2dr1 에서 맨바닥 유령이 목표 1 출구를 막아 **실주행 중단**(29 s)이 나오자, min_weight 재생 A/B(유령과 상자가 함께 줄어 기각) 뒤 프리셋 3 을 기본으로 정했다(사용자 결정). 그러나 프리셋 3 + 통합 1.4 m 는 두 바퀴 주행 f2lp1 복귀에서 상자를 0 칸으로 놓쳐 접촉 → 같은 bag 을 2.0 m 로 재생하니 접촉 37 s 전부터 상자 9 칸 · 유령 A 2 → **통합 거리 2.0**(사용자 결정), 검증 f2pi1 3/3. 남은 것: 기전 미확인, 낮은 물체 감지 여유가 얇음, 상자 옆 1.1 cm 근접(다른 카드).

## 1. 증상
- 사용자 관찰(10-21 §13): "출발점에서 상자 뒤 · 문 가운데에 장애물 칸이 찍히는데 실제로는 없음". 영상 [`f2sm2_v11.png`](../debug_log/2026-10-21/figures/f2sm2_v11.png) · [`f2sm2_v22.png`](../debug_log/2026-10-21/figures/f2sm2_v22.png)(빨간 네모 = 로컬 LETHAL).
- 출발점 둘레 창(x −1.5~3.5, y −2.5~1.5)의 '지도 밖 · 라이다 근거 없음' 전역 LETHAL 칸 — [`anal_phantom_cells_cmp.txt`](../debug_log/2026-10-21/outputs/anal_phantom_cells_cmp.txt):
  ```
  f2u1 t8:  … 창 안 LETHAL 936 칸: 지도에 있음 871 · 지도엔 없고 라이다 근처 43 · 둘 다 아님(카메라 층만) 22
  f2u1 t-2: … 로버 (0.20, 0.03, -183°) … 창 안 LETHAL 1356 칸: … 둘 다 아님(카메라 층만) 206
  f2sm1 t-2: … 로버 (0.23, 0.10, -161°) … 창 안 LETHAL 1430 칸: … 둘 다 아님(카메라 층만) 278
  ```
  프로젝터 켬(f2u1 · f2u3 · f2x1) 출발 17~22 → 끝 176~206, 끔(f2z1 · f2z2 · f2sm1) 24~40 → 265~278. 끝 상태 칸의 97~100 % 를 nvblox 조각이 점유로 봄(f2sm1 270/278 · f2u1 187/206 · f2sm2h 237/237, [`anal_phantom_layer.txt`](../debug_log/2026-10-21/outputs/anal_phantom_layer.txt)).
- 실주행 중단(10-22 §6, f2dr1 프리셋 없음): 목표 1 **ABORTED 29.0 s**, 로버 상자 북쪽 (0.73, 0.24) — [`run_f2dr1_2.txt`](../debug_log/2026-10-22/outputs/run_f2dr1_2.txt) `목표 1 ABORTED 29.0 s | 도착 map (0.727, 0.236, 19.6°)`. 사용자: "아무것도 없다"(§7) — 막은 칸 자리에 실물 없음.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-22 ~ 09-23(앞 이력) | 전역 nvblox 의 유령 셀 → 통합 거리 2.0 → 1.4 · 슬라이스 0.06, 원인 물체 = 초록 바닥 테이프(덮자 0 셀) | — | 테이프 제거 + 1.4 로 우회. IR 기전 추정 | [N6 카드](nvblox-n6-global-ghosts.md) §2 · §4.2 |
| 10-13 §14 · 10-14 §6 | 통합 거리 1.4 → 2.0 → 다시 1.4(상자 면이 멀리서 한 줄 두껍게) | — | 1.4 유지 — 유령과 무관한 이유로 오감 | [N6 카드 §7 이후](nvblox-n6-global-ghosts.md) · `nvblox_local.yaml` 49~53 행 |
| 10-20 ~ 10-21 §20 | 프로젝터 상시 끔(cuVSLAM 용 무늬 없는 IR) → 번갈이 시험들 뒤 상시 끔 유지 결정 | — | 사용자 "끈 것을 유지하고, 유령 셀에 대한 대응책을 생각해보자" | [번갈이 카드](projector-ir-alternation.md) |
| 10-21 §13.1 | 출발점 둘레 근거 없는 LETHAL 칸 근거별 분류(`anal_phantom_cells.py`) | 끝 상태 켬 176~206 · 끔 265~278, 97~100 % nvblox 점유. 출발 정면 (1.25, −0.10) 15 칸은 출발점 낮은 상자(실물) | 출처 = 카메라(nvblox) | `anal_phantom_cells*.txt` · `anal_phantom_layer.txt` · 그림 `figures/phantom_*.png` |
| 10-21 §13.2 | 가설 'map→odom 보정이 odom 기억을 옮겨 찍는다' 시험 · 탄생 순간 대조 | 두 시각 겹침 최적 이동 (0, 0)(map→odom 변화 0.34~0.51 m), 끝 칸을 관측 시각 좌표로 되돌려도 벽 위 ≤ 18.7 %(무작위 36.1 %). 새 칸 < 1.5 m 의 63~76 % 가 그 순간 조각에 있음, > 3 m 는 라이다 98~100 % | 이동 가설 **기각**. 출발점 유령 = 로버가 1.5 m 안으로 다가오며 카메라가 본 것 | [`anal_cells_shift_xcorr_f2sm1.txt`](../debug_log/2026-10-21/outputs/anal_cells_shift_xcorr_f2sm1.txt) · [`anal_phantom_shift_f2sm1.txt`](../debug_log/2026-10-21/outputs/anal_phantom_shift_f2sm1.txt) · [`anal_birth_vs_slice.txt`](../debug_log/2026-10-21/outputs/anal_birth_vs_slice.txt) |
| 10-21 §13.3 | 결론 | — | '프로젝터 켬에서도 매 주행 176~206 칸 → 끈 것은 원인이 아니라 키운 것(1.4 배)'(❌ §15 에서 맨바닥 · 문 영역에 대해 정정) | — |
| 10-21 §14 | 사용자 지목 두 곳(영상 11 s · 22 s)을 로컬 코스트맵으로 | t 22.5~44.5 근거 없는 칸 36~47 개 **100 % nvblox**. 상자 너머 (1.8~2.7, −0.2~0.6) 1~2 칸짜리 · 문 사이 (2.27, −0.60) 1 칸. 같은 창 켬 0~19 · 끔 6~40 | '켬에서도 생긴다'(❌ §15) | [`anal_phantom_local_f2sm2.txt`](../debug_log/2026-10-21/outputs/anal_phantom_local_f2sm2.txt) · [`anal_phantom_local_cmp.txt`](../debug_log/2026-10-21/outputs/anal_phantom_local_cmp.txt) |
| 10-21 §15 | 사용자 "테이프는 더 이상 없다. nvblox 만 쓸 때는 안 나왔다" → 구간 전체 · 위치 목록으로 다시 셈(`anal_zone_ghosts.py`) | 켬 5 주행 A 4~11 칸이지만 대부분 x 2.65 벽 옆 열, **맨바닥 0~3**. 끔 4 주행 A **28~99**. 문 B: 켬 0(f2u1 의 3 은 벽 끝), 끔 0 · 6 · 0 · 2 | **정정** — 맨바닥 · 문 사이 점은 프로젝터 **끔에서만**. 기전 추정: 무늬 없는 바닥 스테레오 오정합 | [`anal_zone_ghosts.txt`](../debug_log/2026-10-21/outputs/anal_zone_ghosts.txt) · 도구 [`anal_zone_ghosts.py`](../debug_log/2026-10-21/jobs/anal_zone_ghosts.py) |
| 10-21 §20 | 지금 경로 확인 | nvblox 는 드라이버 깊이를 필터 없이 받음(`do_depth_preprocessing: false`), `depth_relay` 필터는 점군에만, 깊이 프리셋 미지정 | 대응 후보 1 = 깊이 프리셋, 2 = nvblox min_weight | `nvblox_local.yaml` 48 행 · `nvblox_up.sh` 28 행 |
| 10-21 §21 선언 · §21.1 | 정지 시험 pr1: 프리셋 0 → 3 → 0, nvblox 기준 재현(≤ 1.4 m · 띠 0.06~0.30 · 5 cm 복셀 찍힘 비율) | 깜빡 복셀 108 · **2** · 95, 안정 11 · 4 · 11, 채움률 0.317 · **0.045** · 0.317 | 선언 1 · 2 · 3 **통과**. 대가: 바닥 · 벽 · 상자 옆면 깊이 거의 사라짐(상자 안정 11 → 4) → 주행 시험으로 | [`run_pr1.txt`](../debug_log/2026-10-21/outputs/run_pr1.txt) · 그림 [`figures/pr1/`](../debug_log/2026-10-21/figures/pr1/pr1_top.png) · 도구 `run_pr1.sh` · `anal_pr1.py` |
| 10-21 §21.2 | 주행 f2pr1 선언 | 판정 ① 3/3 ② 맨바닥 A(벽 옆 열 제외) ≤ 10 · B ≤ 2 ③ 상자 t0 뒤 2 s 안 ≥ 8 칸 | — | SUMMARY §21.2 |
| 10-22 §0 · §1 · §2 | 재부팅 확인 · prep(`depth_preset:=3`) · 기준 3 의 t0 해석(1.4 m 안 + 진행 ±40°) 주행 중 적음 | PREP_OK 0.005 m · −0.1°, `visual_preset = 3` | — | [`chk_day_start_1022.txt`](../debug_log/2026-10-22/outputs/chk_day_start_1022.txt) · [`prep_pr_1022_1.txt`](../debug_log/2026-10-22/outputs/prep_pr_1022_1.txt) |
| 10-22 §3 | f2pr1 결과 | 3/3 · **A 0 · B 0** · 끝 상태 nvblox 칸 77(f2sm1 244, −68 %) · 상자 **7 칸**(처음 ≥ 8 은 t0 + 10.8 s), 복귀 길 1~2 칸 | 기준 3 **미달** → 그대로 기본값은 불합격. 길: 중간 프리셋 · min_weight · 조합 | [`anal_zone_ghosts_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_zone_ghosts_f2pr1.txt) · [`anal_box_detect_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_box_detect_f2pr1.txt) · [`anal_box_series_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_box_series_f2pr1.txt) · [`anal_phantom_f2pr1_end.txt`](../debug_log/2026-10-22/outputs/anal_phantom_f2pr1_end.txt) · bag `bags/bag_f2pr1.tgz` |
| 10-22 §4.1 | 사용자 "복귀 시 문을 넘으면서 멈칫" | 문 안 0.20 · 0.15 s = TF 미래 외삽, 문 지난 뒤 4.9 s = 상자 옆 PathBlockedAhead → Wait | **유령 무관**(그 구간 문 영역 B 0) → [경로 추종 카드](path-tracking-replan-b0.md) | [`nav_events_ms_f2pr1.txt`](../debug_log/2026-10-22/outputs/nav_events_ms_f2pr1.txt) |
| 10-22 §5 | 깊이 기록 주행 선언(min_weight 재생 입력용, 프리셋 없음) | 기록 ≥ 14.5 Hz · 대표성(f2sm1 범위) · R0 재생 충실도 · min_weight 합격 = A ≤ 30 % 그리고 상자 ≥ 80 % | — | SUMMARY §5. prep 실패 3 회(§5.1~§5.3)는 [운용 카드](drive-ops-1019-1023.md) |
| 10-22 §6 | f2dr1(프리셋 없음) | 목표 1 ABORTED 29 s. 계획기 `failed to create plan with tolerance 0.25` 매초. 전역 통과 칸 연결이 t 22 s 부터 끊김(문 줄은 열려 있음). 막은 칸 111 개 **전부 nvblox** | 맨바닥 유령이 실제로 주행을 끊은 **첫 사례**. '상자 북쪽으로 돌았다(평소와 다른 길)'(❌ §7) · '실물일 수 있음'(❌ 사용자) | [`nav_events_ms_f2dr1.txt`](../debug_log/2026-10-22/outputs/nav_events_ms_f2dr1.txt) · [`anal_door_pass_f2dr1.txt`](../debug_log/2026-10-22/outputs/anal_door_pass_f2dr1.txt) · [`anal_phantom_f2dr1_abort.txt`](../debug_log/2026-10-22/outputs/anal_phantom_f2dr1_abort.txt) · 그림 [`phantom_f2dr1_abort.png`](../debug_log/2026-10-22/figures/phantom_f2dr1_abort.png) |
| 10-22 §7 | 사용자 "bag 기록이 영향을 끼친 것 아닌지" | 기록 안 한 f2sm1 이 유령 더 많음(북쪽 155 · A 49 vs f2dr1 110 · 21). 조각 8.60 vs 8.95 · 9.15 Hz, 지연 중앙 0.113~0.114 s 같음. 세 주행 같은 길(t 22 s 로버 (0.61~0.73, 0.20~0.24)) | 기록 탓 근거 없음(완전 배제는 못 함). 차이 = 유령의 **놓인 자리**(t 19~25 s 에 (1.95~2.10, 0.00~0.35) 줄이 출구를 메움) | [`anal_rec_effect.txt`](../debug_log/2026-10-22/outputs/anal_rec_effect.txt) · `anal_zone_ghosts_f2{dr1,sm1_0to42,pr1_0to42}.txt` · `anal_door_pass_f2{sm1,pr1,dr1}.txt` |
| 10-22 §8.1 | f2dr2(같은 구성, 깊이 기록) | 3/3, 깊이 3208 장 14.74 Hz(103 %), A 72 · B 2, 상자 13 칸 t0 + 0.10 s | 기록 기준 · 대표성 ✔ → 재생 입력 | [`run_f2dr2.txt`](../debug_log/2026-10-22/outputs/run_f2dr2.txt) · [`bag_f2dr2_counts.txt`](../debug_log/2026-10-22/outputs/bag_f2dr2_counts.txt) · [`anal_zone_ghosts_f2dr2.txt`](../debug_log/2026-10-22/outputs/anal_zone_ghosts_f2dr2.txt) · [`anal_box_detect_f2dr2.txt`](../debug_log/2026-10-22/outputs/anal_box_detect_f2dr2.txt) |
| 10-22 §9 · §9.1 | min_weight 재생 A/B 0.1 · 1 · 2(도메인 42) | R0 A 102 = 실시간 102. mw1 A 53(52 %) · 상자 11, mw2 A 27(26 %) · 상자 9(69 %) | **둘 다 미달** — 유령과 상자가 함께 준다 | [`rp_mw_1022.txt`](../debug_log/2026-10-22/outputs/rp_mw_1022.txt) · [`anal_slice_zones_mw.txt`](../debug_log/2026-10-22/outputs/anal_slice_zones_mw.txt) · 재생 출력 `bags/replay_f2dr2_mw{01,1,2}.tgz` |
| 10-22 §10 | **결정: 깊이 프리셋 3 기본**(내 권고 → 사용자 채택) · 배포 · 시각화 | Jetson sha 95fe7b16a70f → d5525810708d, prep(인자 없음) `visual_preset = 3` | 대가(낮은 상자 15 → 7 · 복귀 1~2 칸)를 안고 감. 프리셋 5 정지는 남은 일 | [`up_cam_1022.txt`](../debug_log/2026-10-22/outputs/up_cam_1022.txt) · [`prep_op_1022_1.txt`](../debug_log/2026-10-22/outputs/prep_op_1022_1.txt) · 그림 [`box_cells_preset.png`](../debug_log/2026-10-22/figures/box_cells_preset.png) · 영상 `videos/preset_cmp_f2dr2_f2pr1.mp4`(git 제외) · 커밋 `70aaec3b` |
| 10-22 §11 ~ §11.4 | 프리셋 3 복귀 때 상자 밖 노란 칸 | 유령이 아니라 상자 기억이 EKF 오차만큼 밀린 것 · 복귀 때 그 방향 화소 83~93 % 깊이 0 | → [상자 과장 카드](box-exaggeration-source.md) | SUMMARY §11 |
| 10-22 §12 · §12.1 | 두 바퀴 f2lp1(프리셋 3 + 1.4) | 사용자 정지 "상자를 치고 돌아가서 2 번째 주행에는 상자가 안 보인다" — 바퀴 비교 판정 무효 | 접촉 원인(§13: 복귀 t 100~200 s 세 지도 모두 상자 0 칸, 상자 쪽 화소 100 % 깊이 0) → [상자 과장 카드](box-exaggeration-source.md) | [`run_f2lp1.txt`](../debug_log/2026-10-22/outputs/run_f2lp1.txt) · [`stop_f2lp1.txt`](../debug_log/2026-10-22/outputs/stop_f2lp1.txt) · [`anal_box_maps_series_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_box_maps_series_f2lp1.txt) |
| 10-22 §14 · §14.1 | 중간 프리셋 P5 정지(pr2: 0 → 3 → 5) | P5 깜빡 11(P0 77 의 14 %) ✔, 상자 안정 **5 < 8** ✘, 채움률 0.117 | **P5 불합격** — 주행 단계 안 함 | [`run_pr2.txt`](../debug_log/2026-10-22/outputs/run_pr2.txt) · 그림 [`pr2_top.png`](../debug_log/2026-10-22/figures/pr2/pr2_top.png) |
| 10-22 §14.2 | f2lp1 깊이 bag 을 통합 거리 1.4 · 2.0 으로 재생 | 1.4 = 실시간과 같음(R0). **2.0: 복귀 상자 0 → 9 칸**(t 156.6 s 부터, 접촉 37 s 전), A 0 → 2 · B 0 → 3 | 합격(복귀 상자 ≥ 3 · A ≤ 20). 남은 위험: 멀리서 본 면이 두꺼움(10-14 §6) | [`anal_slice_zones_f2lp1_int.txt`](../debug_log/2026-10-22/outputs/anal_slice_zones_f2lp1_int.txt) · [`chk_rp_int2.txt`](../debug_log/2026-10-22/outputs/chk_rp_int2.txt) · [`anal_cell_timeline_f2lp1_i20.txt`](../debug_log/2026-10-22/outputs/anal_cell_timeline_f2lp1_i20.txt) |
| 10-22 §15 | **결정: 통합 거리 2.0**(사용자) · 배포(Jetson 판이 주석 3 줄만 달라 첫 시도 중단 → 대조 뒤) · f2pi1 기준 선언 | 새 sha bf8abc842b27, 설치본 링크, 값 2.0 | — | [`up_nvy_1022.txt`](../debug_log/2026-10-22/outputs/up_nvy_1022.txt) · [`nvblox_local_jetson_pre1022.yaml`](../debug_log/2026-10-22/outputs/nvblox_local_jetson_pre1022.yaml) · 커밋 `9087d936` |
| 10-22 §16 | f2pi1(프리셋 3 + 2.0) | 3/3, 접촉 최소 +0.012 m(✔ 형식), 복귀 상자 t 160 s 부터 조각 3 → 6~7, A 4(전부 x 2.60~2.65 벽 옆 열) · B 0, 상자 옆 PathBlockedAhead 2 · 스무더 충돌 2(기준 4 ✘) | 기준 1 · 2 · 3 통과, 4 는 '상자 옆 여유' 문제로 따로 → [상자 옆 정지](box-side-stall-cause.md) · 멈칫 14 번은 [경로 추종 카드](path-tracking-replan-b0.md) | [`run_f2pi1.txt`](../debug_log/2026-10-22/outputs/run_f2pi1.txt) · [`chk_live_cfg_f2pi1.txt`](../debug_log/2026-10-22/outputs/chk_live_cfg_f2pi1.txt) · [`anal_box_maps_series_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_box_maps_series_f2pi1.txt) · [`anal_zone_ghosts_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_zone_ghosts_f2pi1.txt) · [`anal_contact_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_contact_f2pi1.txt) · bag `bags/bag_f2pi1.tgz` |
| 10-22 §21 | 마무리 — 결정 2 개 · 기각 2 개 기록 | — | 프리셋 3 기본 · 통합 2.0. 기각 min_weight 1 · 2, 프리셋 5 | SUMMARY §21 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 출발점 유령 = SLAM 보정(map→odom)이 nvblox 의 odom 기억을 map 에서 옮겨 찍은 것 | 두 시각 칸 집합 겹침 최적 이동 · 끝 칸을 관측 시각 좌표로 되돌려 벽에 떨어지는 비율 | 최적 이동 (0, 0)(3 쌍 모두), 벽 위 최고 18.7 % < 무작위 평균 36.1 % | **기각**(10-21 §13.2) — 단 10-22 §11 에서 '상자 기억이 EKF 오차만큼 밀리는' 다른 현상은 확인(로컬 · 조각 기준, 전역은 미확인 — 10-22 §17 정정) |
| 출처 = 카메라(nvblox) | 끝 상태 칸 ↔ 조각 점유 · 탄생 순간 대조 | 97~100 % 조각 점유. 새 칸 < 1.5 m 63~76 % 조각 · 14~39 % 라이다 | **지지(측정)** |
| 맨바닥 · 문 사이 유령은 프로젝터 켬에서도 생긴다 | 같은 영역 · 구간 전체 · 위치 목록(`anal_zone_ghosts.py`) | 켬 맨바닥 0~3, 끔 28~99. 켬의 A 칸은 x 2.65 벽 옆 열 | **기각**(10-21 §15 정정 — 처음 결론을 뒤집음) |
| 기전 = 프로젝터 점무늬가 없으면 무늬 없는 바닥에서 스테레오 짝이 틀려 깊이가 튀고, 슬라이스 하한 0.06 을 넘는 점이 적분됨 | 깊이 영상 화소 ↔ 유령 칸 되짚기(10-21 §13.3 제안) | **안 함**. 간접: pr1 깜빡 복셀의 2/3 가 높이 ≥ 0.15(바닥 근처만이 아님), 프리셋 3(확신 낮은 짝 버림)에서 98 % 감소 | **미확인(추정)** — 프리셋 3 효과는 '확신 낮은 깊이' 쪽과 맞지만, 바닥 오정합이라는 직접 증거는 없음 |
| 테이프(09-23 기전)가 다시 원인 | 사용자 확인 | "테이프는 더 이상 없다" | **기각** |
| 깊이 기록(bag)이 nvblox 를 늦춰 f2dr1 유령을 키웠다 | 세 주행 조각 주기 · 지연 · 유령 수 | 지연 분포 같음, 기록 안 한 f2sm1 이 유령 더 많음, f2dr2(기록) 9.43 Hz | **기각(측정, 완전 배제 아님)** |
| f2dr1 만 막힌 것은 다른 길로 갔기 때문 | 같은 도구로 세 주행 로버 위치 | t 22 s (0.71, 0.21) · (0.61, 0.20) · (0.73, 0.24) 같은 길 | **기각**(10-22 §7 정정) — 유령의 놓인 자리 차이(추정, 칸 목록 대조 미완) |
| 깊이 프리셋 3 이 유령을 줄이고 실물을 지킨다 | pr1 정지 · f2pr1 주행 | 깜빡 2 %, A 0 · 끝 −68 %. 상자 안정 11 → 4, 주행 상자 15 → 7, 복귀 1~2 | **유령 감소 지지 · 실물 유지 부분 기각**(낮은 물체 칸 절반) |
| nvblox min_weight 를 올리면 깜빡 유령만 걸러진다 | f2dr2 재생 0.1 · 1 · 2 | A −48 % · −74 %, 상자 −15 % · −31 % — 함께 준다 | **기각**(10-22 §9.1) |
| 중간 프리셋 5 가 절충점 | pr2 정지 | 깜빡 14 %(✔) · 상자 안정 5(P3 와 같음, ✘) | **기각(정지 기준)** — 비스듬한 각에서의 이득은 주행 안 해서 미확인 |
| 프리셋 3 + 1.4 m 로 낮은 상자를 제때 본다 | f2lp1 실주행 | 복귀 상자 0 칸 → 접촉 | **기각** — 프리셋 3 이 '보이는 각 · 거리 창' 을 좁혀 1.4 m 안에서 각도가 나쁘면 못 봄(10-22 §13.1, 상세 [상자 과장 카드](box-exaggeration-source.md)) |
| 통합 거리 2.0 이 복귀 상자를 되살리면서 유령은 작게 유지 | f2lp1 재생 1.4 vs 2.0 · f2pi1 주행 | 재생 상자 0 → 9 · A 0 → 2 · B 0 → 3. f2pi1 복귀 상자 3~8 · A 4(벽 옆 열) | **지지**(재생 1 + 주행 1). 프리셋 없음 입력에선 2.0 이 A 102 → 132 로 늘림(10-22 §11.3) — 프리셋 3 과 묶여야 성립 |

## 4. 조치와 효과
### 4.1 판별 도구가 센 것 — 발췌
- 유령 영역 집계([`anal_zone_ghosts.py`](../debug_log/2026-10-21/jobs/anal_zone_ghosts.py) 42~54 행 — 로컬 LETHAL 칸 중 저장 지도 0.10 m 밖 · 직전 1 s 라이다 점 0.10 m 밖을 '근거 없음' 으로, 구간 안 한 번이라도):
  ```python
  ys, xs = np.nonzero(A >= 100); a = at(MO, MOt, tt)          # 로컬 코스트맵(odom) LETHAL → map
  ...
  if np.hypot(MPt[:, 0] - X[i], MPt[:, 1] - Y[i]).min() <= 0.10: continue      # 저장 지도 벽
  if len(LP) and np.hypot(LP[:, 0] - X[i], LP[:, 1] - Y[i]).min() <= 0.10: continue   # 그 순간 라이다
  key = (round(X[i] / 0.05) * 0.05, round(Y[i] / 0.05) * 0.05); d = cells[k].setdefault(key, [tt, 0]); d[1] += 1
  ```
  출력([`anal_zone_ghosts.txt`](../debug_log/2026-10-21/outputs/anal_zone_ghosts.txt), 켬 · 끔 각 1):
  ```
  bag bag_f2x1 · 구간 t 10~60 s · 로컬 코스트맵 83 장
    영역 x 1.45~2.65 y -0.35~0.45: 근거 없는 LETHAL 칸 10 개 — (2.65,-0.30)t24×11 (2.65,-0.25)t24×10 … (2.65,-0.35)t26×2
  bag bag_f2z1 · 구간 t 10~60 s · 로컬 코스트맵 83 장
    영역 x 1.45~2.65 y -0.35~0.45: 근거 없는 LETHAL 칸 99 개 — (1.85,0.40)t14×3 (1.85,0.45)t16×3 (1.70,-0.05)t16×1 (1.85,0.00)t16×1 …
  ```
  켬(f2x1)의 10 칸이 전부 x 2.65 열(벽 x ≈ 2.75 가장자리)이라는 것이 §15 정정의 근거.
- 정지 프리셋 시험([`anal_pr1.py`](../debug_log/2026-10-21/jobs/anal_pr1.py) 17 · 58~61 · 74 행 — 깊이 화소를 base_link 로, nvblox 와 같은 거리 · 높이 창에서 5 cm 복셀별 '찍힌 프레임 비율'):
  ```python
  RMAX, ZLO, ZHI, V = 1.4, 0.06, 0.30, 0.05
  r = np.hypot(P[:, 0], P[:, 1]); near = r <= RMAX
  b = P[near & (P[:, 2] >= ZLO) & (P[:, 2] < ZHI)]
  for k in set(map(tuple, np.floor(b / V).astype(int))): self.hits[k] = self.hits.get(k, 0) + 1
  flick = [k for k, f in fr.items() if f < 0.30]; stab = [k for k, f in fr.items() if f >= 0.80]
  ```
  출력([`run_pr1.txt`](../debug_log/2026-10-21/outputs/run_pr1.txt)):
  ```
  ======== P0a (depth_preset:=0) — Integer value is: 0 · Open profile: … Width: 640, Height: 480, FPS: 15
    채움률 중앙 0.317 · 바닥 점(|z|<0.04, ≤1.4 m) 중앙 1116 · 띠 점(0.06~0.30) 중앙 136 (5~95 % 122~155)
    복셀(띠 · ≤1.4 m): 찍힘 126 · 깜빡(<30 %) 108 · 중간 7 · 안정(≥80 %) 11
  ======== P3 (depth_preset:=3) — Integer value is: 3 · …
    채움률 중앙 0.045 · 바닥 점(|z|<0.04, ≤1.4 m) 중앙 85 · 띠 점(0.06~0.30) 중앙 48 (5~95 % 34~62)
    복셀(띠 · ≤1.4 m): 찍힘 8 · 깜빡(<30 %) 2 · 중간 2 · 안정(≥80 %) 4
    안정 묶음(복셀 수 ≥ 3): (1.16,-0.10)×4
  ======== P0b (depth_preset:=0) — … 깜빡(<30 %) 95 · 중간 7 · 안정(≥80 %) 11
  ```
- 주행 상자 감지([`anal_box_detect.py`](../debug_log/2026-10-22/jobs/anal_box_detect.py) 15 · 44 · 56 행 — t0 = 상자 중심이 1.4 m · ±40° 안에 처음 든 시각, 그 뒤 처음 ≥ 8 칸):
  ```python
  RMAX, FOV, NEED = 1.4, math.radians(40), 8
  if d <= RMAX and abs(b) <= FOV: t_in = (tt, d, math.degrees(b), p); break
  hit = next(((tt, n) for tt, n in rows if tt >= t_in[0] and n >= NEED), None)
  ```
  출력([`anal_box_detect_f2pr1.txt`](../debug_log/2026-10-22/outputs/anal_box_detect_f2pr1.txt) · [`_f2sm1.txt`](../debug_log/2026-10-22/outputs/anal_box_detect_f2sm1.txt) — 두 파일은 CP949 로 저장됨, 아래는 변환한 것):
  ```
  bag bag_f2pr1 · … t0 = 4.01 s (… 거리 1.26 m, 방위 -4°) · t0 뒤 처음 ≥ 8 칸: t 14.81 s (8 칸) · 지연 10.80 s · t0~t0+10 s 칸 수: 최대 7 · 중앙 7
  bag bag_f2sm1 · … t0 = 4.93 s (… 거리 1.26 m, 방위 -3°) · t0 뒤 처음 ≥ 8 칸: t 5.49 s (15 칸) · 지연 0.55 s · … 최대 16 · 중앙 15
  ```
- f2dr1 막힘 판별([`anal_door_pass.py`](../debug_log/2026-10-22/jobs/anal_door_pass.py) 34 · 40 행 — 전역 코스트맵 값 < 99 칸만 4-이웃 BFS):
  ```python
  s, g = ij(p[0], p[1]), ij(GX, GY); free = A < 99
  ... if 0 <= a < A.shape[0] and 0 <= b < A.shape[1] and free[a, b] and not seen[a, b]: seen[a, b] = True; q.append((a, b))
  ```
  출력([`anal_door_pass_f2dr1.txt`](../debug_log/2026-10-22/outputs/anal_door_pass_f2dr1.txt)):
  ```
   t 20.0 s 장 19.2 · 로버 (0.51, 0.18) … 통과 칸으로 닿음 예 · 문 줄 값 100 100 99 99 99 99 96 88 80 73 67 68 75 …
   t 22.0 s 장 21.2 · 로버 (0.65, 0.21) … 통과 칸으로 닿음 아니오 · 문 줄 값 100 100 99 99 99 99 96 88 80 75 76 75 75 …
  ```
  문 줄 가운데가 62~76 으로 열린 채 연결만 끊김 → 막힌 곳은 문이 아니라 로버와 문 사이. 같은 시각 막은 칸([`anal_phantom_f2dr1_abort.txt`](../debug_log/2026-10-22/outputs/anal_phantom_f2dr1_abort.txt)): `유령 후보 111 중 nvblox 가 점유로 봄 111 · nvblox 도 아님(라이다 층 기억 추정) 0`, 덩어리 `51 칸 · 중심 (1.72, 0.82)` · `14 칸 · 중심 (1.25, -0.10)`(상자, 실물) · `8 칸 · 중심 (2.50, -0.24)`. Nav2 쪽([`nav_events_ms_f2dr1.txt`](../debug_log/2026-10-22/outputs/nav_events_ms_f2dr1.txt)): `13:50:45.62 planner_server GridBased: failed to create plan with tolerance 0.25.` 부터 12 번.
- min_weight 재생([`rp_mw_1022.sh`](../debug_log/2026-10-22/jobs/rp_mw_1022.sh) 39~41 행 · 지표 [`anal_slice_zones.py`](../debug_log/2026-10-22/jobs/anal_slice_zones.py) 36 · 42 행 — 조각 거리 ≤ 0 칸이 영역 안에 한 번이라도):
  ```bash
  for c in "mw01 static_mapper.esdf_integrator_min_weight:=0.1" "mw1 …:=1.0" "mw2 …:=2.0"; do
    bash /tmp/run_nvblox_replay.sh $IN f2dr2_$1 $2
  ```
  ```python
  d = np.array(m.data, np.float32).reshape(m.height, m.width); iy, ix = np.nonzero((d <= 0) & (d != m.unknown_value))
  ever[k].update(zip(np.floor(gx[s] / 0.05).astype(int), np.floor(gy[s] / 0.05).astype(int)))
  ```
  적용 확인([`rp_mw_1022.txt`](../debug_log/2026-10-22/outputs/rp_mw_1022.txt)) `[nvblox_node]: static_mapper.esdf_integrator_min_weight: 2` · `Count: 2065`, 결과([`anal_slice_zones_mw.txt`](../debug_log/2026-10-22/outputs/anal_slice_zones_mw.txt)):
  ```
    live     조각 2053 · A 맨바닥 102 · B 문 3 · 북쪽 195 · 상자 중앙 15 최대 16 (조각 94)
    r0.1     조각 2048 · A 맨바닥 102 · B 문 4 · 북쪽 196 · 상자 중앙 13 최대 15 (조각 94)
    mw1      조각 2063 · A 맨바닥 53 · B 문 1 · 북쪽 173 · 상자 중앙 11 최대 14 (조각 95)
    mw2      조각 2065 · A 맨바닥 27 · B 문 1 · 북쪽 159 · 상자 중앙 9 최대 13 (조각 94)
  ```
- 중간 프리셋 P5([`run_pr2.txt`](../debug_log/2026-10-22/outputs/run_pr2.txt), 같은 `anal_pr1.py`):
  ```
  [P0c] … 복셀(띠 · ≤1.4 m): 찍힘 97 · 깜빡(<30 %) 77 · 중간 9 · 안정(≥80 %) 11
  [P3b] … 채움률 중앙 0.051 … 찍힘 9 · 깜빡(<30 %) 3 · 중간 1 · 안정(≥80 %) 5
  [P5]  … 채움률 중앙 0.117 … 찍힘 24 · 깜빡(<30 %) 11 · 중간 8 · 안정(≥80 %) 5
  ```
- 통합 거리 재생([`rp_int2_1022.sh`](../debug_log/2026-10-22/jobs/rp_int2_1022.sh) — `rp_mw_1022.sh` 와 머리말 2 행 · 입력 bag · 설정 목록(38~44 행)만 다름: `"i14 static_mapper.projective_integrator_max_integration_distance_m:=1.4" "i20 …:=2.0"`). 적용 확인([`chk_rp_int2.txt`](../debug_log/2026-10-22/outputs/chk_rp_int2.txt)) `… max_integration_distance_m: 2` · `Count: 2941`, 결과(`RET_WIN=160,193`, [`anal_slice_zones_f2lp1_int.txt`](../debug_log/2026-10-22/outputs/anal_slice_zones_f2lp1_int.txt)):
  ```
    live     조각 2952 · A 맨바닥 0 · B 문 0 · 북쪽 99 · 상자 복귀 0 · 상자 중앙 6 최대 6 (조각 94)
    i14      조각 2989 · A 맨바닥 0 · B 문 0 · 북쪽 99 · 상자 복귀 0 · 상자 중앙 6 최대 6 (조각 95)
    i20      조각 2941 · A 맨바닥 2 · B 문 3 · 북쪽 108 · 상자 복귀 9 · 상자 중앙 6 최대 6 (조각 93)
  ```
- f2pi1 복귀 상자([`anal_box_maps_series_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_box_maps_series_f2pi1.txt)) — 같은 시각대 f2lp1([`anal_box_maps_series_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_box_maps_series_f2lp1.txt))과 나란히:
  ```
  f2pi1  t  160.0 | S   3 · L   0 · G   3 | 로버 ( 2.94, -1.70,  161°) 상자 2.35 m 방위  -23°
  f2pi1  t  170.0 | S   7 · L   7 · G   8 | 로버 ( 2.35, -1.33,  124°) 상자 1.67 m 방위   +9°
  f2lp1  t  160.0 | S   0 · L   0 · G   0 | 로버 ( 2.61, -1.54,  150°) 상자 2.00 m 방위  -15°
  f2lp1  t  170.0 | S   0 · L   0 · G   0 | 로버 ( 2.25, -0.99,   98°) 상자 1.37 m 방위  +42°  ← 시야(±43°·1.4 m)
  ```

### 4.2 결정과 효과
| 조치 | 전 | 후 | 한계 |
|---|---|---|---|
| 깊이 프리셋 3 기본(10-22 §10) | 프리셋 없음: 맨바닥 A 28~102(로컬 · 조각), f2dr1 중단 1/3 | f2pr1 A 0 · B 0 · 3/3, 끝 nvblox 칸 −68 %, f2pi1 A 의 4 칸은 벽 옆 열 | 낮은 상자 칸 15 → 7 · 복귀 1~2(1.4 m 일 때 f2lp1 0 → 접촉). 바닥 · 벽 깊이 대부분 사라짐(채움률 0.317 → 0.045) — 벽은 라이다가 맡음 |
| 통합 거리 2.0(10-22 §15) | 프리셋 3 + 1.4: f2lp1 복귀 상자 0 칸 | 재생 9 칸(37 s 전부터) · f2pi1 3~8 칸 · 3/3 | 프리셋 3 과 묶여서만 유령이 작음(프리셋 없음 2.0 = A 102 → 132). 멀리서 처음 본 면이 두꺼움(10-14 §6) → 상자 옆 여유 1.1 cm(f2pi1 §16 · §17, [상자 옆 정지](box-side-stall-cause.md)) |
| min_weight 0.1 유지 | — | 1 · 2 기각 | 재생 1 입력(f2dr2) |
| 프리셋 5 기각 | — | 정지 상자 안정 5 < 8 | 비스듬한 각 · 주행 미시험 |
- 검증 범위: 프리셋 3 + 2.0 의 '유령 · 복귀 상자' 지표를 잰 주행은 **f2pi1 1 회**. 10-22 §21 '검증 f2pi1 · f2sm3 모두 … 복귀 상자 칸 있음 · 유령 A 4' 중 f2sm3 은 3/3 만 있고 그 지표 출력이 없다(§5-6).

### 4.3 지금 코드 확인(11-03)
- [`camera.launch.py`](../../ros2_ws/src/rover_bringup/launch/camera.launch.py) 118 행 `DeclareLaunchArgument('depth_preset', default_value='3', description='… 10-22 §10 사용자 결정으로 기본 3')` · 84~87 행 근거 주석(f2dr1 · f2pr1 · min_weight 수치, 10-22 와 같음) · 88~90 행 `if preset >= 0: cam_params['depth_module.visual_preset'] = preset`. 이 인자를 넘기는 launch · prep 은 저장소에 없음(grep `depth_preset` → camera.launch.py 뿐) → 모든 기동이 3. [`chk_prep.py`](../tools/chk_prep.py) 39 행이 `/camera/camera depth_module.visual_preset` 을 **출력만** 한다(값이 3 이 아니어도 PREP_FAIL 아님).
- ⚠ 경로 주의: 117 행 `emitter_off` 기본은 `'false'` — 운용 상시 끔은 prep 의 `SENSORS_ADD="emitter_off:=true …"` 가 준다(`prep_op_1022.sh` 3 행). 프리셋 3 의 유령 근거는 '끔' 조건에서만 잰 것.
- [`nvblox_local.yaml`](../../ros2_ws/src/rover_navigation/config/nvblox_local.yaml) 57 행 `projective_integrator_max_integration_distance_m: 2.0` · 54~56 행 10-22 근거 주석(f2lp1 · 재생 9 칸 · A 0 → 2 · B 0 → 3) · 13 행 머리말 이력 '→ 지금 2.0(10-22)' · 48 행 `do_depth_preprocessing: false` · 61 행 `esdf_integrator_min_weight: 0.1` · 68 행 `esdf_slice_min_height: 0.06` · 69 행 `esdf_slice_max_height: 0.30` · 70 행 `tsdf_decay_factor: 0.99`. 실행 중 값은 prep 이 조회하지 않음 — 10-22 는 `chk_live_cfg.sh`(nvblox 로그 줄)로 확인.
- ⚠ 낡은 · 어긋난 주석 2 곳:
  1. 62~64 행 `# 2026-10-15 §22~§23: 1.0(라이브러리 기본값)을 정지 A/B 로 시험 → 효과 없음, 2.0 유지(벤더 예제값).` 이 61 행 `esdf_integrator_min_weight: 0.1` 바로 밑에 있어 min_weight 설명처럼 읽힌다 — 내용은 65 행 `esdf_integrator_max_site_distance_vox` 의 것(10-15 §22 제목). min_weight 줄에는 10-22 §9 재생 A/B(1 · 2 기각) 주석이 없다.
  2. 57 행 같은 줄 꼬리 주석 `상자(≤1.3 m)·STVL 지평선(1.2)보다 여유. 원거리는 라이다·SLAM 지도가 맡음` 은 09-22 의 1.4 근거 — '(10-22 전: 1.4)' 표지가 앞에 있으나 2.0 값 옆이라 오독 소지.

## 5. 내 실수 · 기록 어긋남
1. **'프로젝터 켬에서도 생긴다'(10-21 §13.3 · §14 → §15 정정)** — 하려 한 것: 켬/끔 같은 창 비교(`anal_phantom_cells.py`, 창 x 1.45~3.2, 시각 3 점) · 본 것: 켬 0~19 · 끔 6~40 칸 · 처음 추론: 켬에서도 생기고 끔에서 약간 많다 → '끈 것은 원인이 아니라 키운 것' · 의심한 이유: 사용자 직접 관찰("nvblox 만 쓸 때는 안 나왔다")과 어긋남 · 판별: 구간 전체 · 위치 목록(`anal_zone_ghosts.py`) — 켬의 칸은 x 2.65 벽 옆 열 · 결론: 맨바닥 · 문 사이 점은 끔에서만 · 다음에 알아보는 법: 비교 창에 벽 · 상자 가장자리를 넣지 않는다, 칸 수가 아니라 위치 목록, 시각 몇 점이 아니라 구간 전체 · 데이터: [`anal_phantom_local_cmp.txt`](../debug_log/2026-10-21/outputs/anal_phantom_local_cmp.txt)(처음 수치) · [`anal_zone_ghosts.txt`](../debug_log/2026-10-21/outputs/anal_zone_ghosts.txt). ⚠ 정정 범위: §15 는 맨바닥 · 문 영역만 고쳤다 — §13.1 의 출발점 둘레 끝 상태(켬 176~206)는 벽 옆 칸 · 실물 가장자리가 섞인 넓은 창이라 '켬에서도 많다' 가 유령 몫인지는 다시 가르지 않았다(이 카드 판단).
2. **'f2dr1 은 평소와 다른 길(상자 북쪽)'(10-22 §6 → §7 정정)** — 판별: `anal_door_pass` 로버 위치를 세 주행에 같이 → 같은 길. 다음에 알아보는 법: '평소와 다르다' 는 같은 도구로 기준 주행을 함께 돌린 뒤에만. 데이터: `anal_door_pass_f2{sm1,pr1,dr1}.txt`.
3. **'막은 칸은 사람 · 의자 실물일 수 있음'(10-22 §6)** — 영상 없이 라이다 물체 옆이라는 정황으로 열어 둔 가능성. 사용자 "아무것도 없다" 로 기각(§7). 데이터: [`phantom_f2dr1_abort.png`](../debug_log/2026-10-22/figures/phantom_f2dr1_abort.png).
4. 기록 어긋남 — **pr1 판정 1 '드라이버 로그에 프리셋 설정 실패 없음'**: [`run_pr1.txt`](../debug_log/2026-10-21/outputs/run_pr1.txt) 각 단계에 `드라이버 경고: 2건` · `3건`(`grep -aciE 'failed|error'` 개수)이 찍혀 있고 내용은 출력되지 않았다. 프리셋 실패 문구 grep 은 비어 있어 판정은 맞을 가능성이 높으나 2~3 건의 정체는 미확인(드라이버 로그 Jetson `/tmp/pr1_cam_*.log` — 휘발, **원천 소실**). pr2 도 같음(`2건`).
5. 기록 어긋남 — **pr1 복셀 비율 `.npz` 없음**: 10-21 §23 표는 '복셀 비율 `figures/pr1/pr1_*.npz`' 라 적었지만 [`figures/pr1/`](../debug_log/2026-10-21/figures/pr1/pr1_top.png) 에는 png 8 장뿐(pr2 는 `figures/pr2/*.npz` 3 개 있음). pr1 을 다른 지표로 다시 셀 수 없다.
6. 기록 어긋남 — **10-22 §21 '검증 f2pi1 · f2sm3 모두 3/3 · 복귀 상자 칸 있음 · 유령 A 4'**: 복귀 상자 칸 · 유령 A 를 잰 출력은 f2pi1 뿐(`anal_box_maps_series_f2pi1.txt` · `anal_zone_ghosts_f2pi1.txt`). f2sm3 은 `run_f2sm3.txt`(3/3)와 그림자 · 멈칫 · CPU 출력만 있다(10-22 · 10-23 outputs 확인). f2sm3 을 '두 번째 검증' 으로 세면 안 된다.
7. 기록 어긋남 — **f2pi1 '맨바닥 A 4'**(10-22 §16 · §21): 4 칸 전부 x 2.60~2.65(`(2.65,0.25)t32×12 (2.60,0.25)t40×6 (2.60,0.20)t43×8 (2.65,0.20)t48×14`, [`anal_zone_ghosts_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_zone_ghosts_f2pi1.txt)) — 10-21 §21.2 가 '벽 옆 열 x ≥ 2.6 제외' 로 정의한 맨바닥으로는 **0**. 판정(≤ 20)은 어느 쪽이든 통과.
8. 기록 어긋남 — **'맨바닥 A' 두 지표가 같은 이름**: 로컬 코스트맵 근거 없는 LETHAL(`anal_zone_ghosts.py`, 지도 · 라이다 0.10 m 밖) vs 조각 거리 ≤ 0 칸 전부(`anal_slice_zones.py`, 지도 · 라이다 제외 없음). 같은 주행 f2sm1 50 vs 72, f2dr2 72 vs 102. 10-22 §9.1 표의 '(참고) f2sm1 … 72' 는 조각 쪽, §3 의 'f2sm1 A 50' 은 로컬 쪽 — 표끼리 섞어 비교하면 안 된다. 두 도구 모두 벽 옆 열을 빼지 않는다(사람이 읽음).
9. 기록 어긋남 — **`anal_slice_zones_pr1_sm1.txt` 머리줄 없음**: 이 출력엔 '상자 t0' 줄이 없어 f2pr1 · f2sm1 상자 창의 t0 가 무엇이었는지 모른다 — 도구 기본값 `BT0 = 2.88`(f2dr2 의 t0, `anal_slice_zones.py` 27 행)이 쓰였다면 두 주행 자신의 t0(4.01 · 4.93 s)와 다르다. 참고 행이라 판정엔 안 쓰였음.
10. 기록 어긋남(경미) — 출력 3 개(`anal_zone_ghosts_f2pr1.txt` · `anal_box_detect_f2pr1.txt` · `anal_box_detect_f2sm1.txt`)가 UTF-8 이 아니라 CP949 · CRLF 로 저장됨(PowerShell 리디렉션 추정). 저장소 다른 출력은 UTF-8.
11. 10-21 §20 의 'nvblox 는 드라이버 깊이를 필터 없이 받음(`nvblox_up.sh` 28 행, `do_depth_preprocessing: false`)' — 28 행은 깊이 토픽 리매핑 줄이고 `do_depth_preprocessing: false` 는 `nvblox_local.yaml` 48 행(지금 코드 확인). 내용은 맞음.

## 6. 남은 것 (10-23 시점)
- **기전 미확인** — 유령 칸을 깊이 영상 화소로 되짚는 시험(10-21 §13.3 제안: 출발점에서 그 방향을 보게 세우고 깊이 + IR + 조각 30 s)을 하지 않았다. f2dr1 · f2dr2 깊이 bag(`bags/bag_f2dr{1,2}.tgz`)이 있어 지금도 오프라인으로 가능.
- **낮은 물체 감지 여유** — 프리셋 3 에서 출발 상자 7~8 칸(게이트 L 문턱 8 에 걸침), 복귀 쪽은 통합 2.0 에 기대는 상태. 더 낮거나 비스듬한 물체 · 다른 조명은 미시험.
- 프리셋 5 의 비스듬한 각 이득 · 고급 모드 개별 값(신뢰도 문턱) 조절 — 미시험(10-22 §3 (가)).
- min_weight 가 상자 **처음 찍히는 시각**을 늦추는지 — 미계산(10-22 §9.1).
- `depth_relay` 의 고립점 · 지속성 필터를 nvblox 입력 쪽에 거는 길(10-21 §20 확인) · `do_depth_preprocessing` — 검토 안 함.
- 유령 칸 '목표 부근 근거 없는 칸' 주행 전 검사는 지금 없다(게이트 M 은 W1 코스용 job505, [N6 카드 §7](nvblox-n6-global-ghosts.md)).
- 정지 시험(pr1 · pr2)은 실시간 집계만 — 깊이 · IR 짧은 bag 을 남기지 않아 다른 지표로 다시 셀 수 없음(10-21 §23 '앞으로').

## 7. 이후 (10-23 ~): 다음 시기에서 채움
- 포인터만: 10-23 §20.2 서쪽 통로 왼쪽 덩어리 = 실물 상자(사용자, 유령 아님) · 10-27 §13~§15 상자 북쪽 '둥근 치명 덩어리' = 상자 내접 띠(유령 아님) · 10-28 §5 통로 남쪽 반복 막힘 칸 = 벽 · 물체 가장자리(유령 아님) · 10-28 정지 1.5 h 동안 생긴 띠(원인 미확인 — 정지 유령 누적도 후보) · 11-02 `nvblox_local.yaml` 머리말 정정.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 유령 출처 분석(주행 없음) | 출발점 둘레 · 사용자 지목 두 곳 · 켬/끔 9 주행 | `2026-10-21/outputs/anal_phantom_*.txt` · `anal_birth_vs_slice.txt` · `anal_cells_shift_xcorr_f2sm1.txt` · `anal_zone_ghosts.txt`, 입력 `2026-10-21/bags/bag_{f2u1,f2u3,f2v4,f2w1,f2x1,f2z1,f2z2,f2sm1,f2sm2,f2sm2h}.tgz` |
| pr1 | 정지 프리셋 0 → 3 → 0 | `2026-10-21/outputs/run_pr1.txt` · `figures/pr1/` |
| f2pr1 | 프리셋 3 주행 b910, 3/3 · A 0 · 상자 7 | `2026-10-22/outputs/run_f2pr1.txt` · bag `bags/bag_f2pr1.tgz` |
| f2dr1 | 프리셋 없음 깊이 기록, 목표 1 ABORTED 29 s(유령) | `outputs/run_f2dr1.txt`(기동 실패) · `run_f2dr1_2.txt` · `nav2_f2dr1.log` · bag `bags/bag_f2dr1.tgz` |
| f2dr2 | 프리셋 없음 깊이 기록 3/3(재생 입력) | `outputs/run_f2dr2.txt` · `bag_f2dr2_counts.txt` · bag `bags/bag_f2dr2.tgz` |
| mw 재생 | min_weight 0.1 · 1 · 2 | `outputs/rp_mw_1022.txt` · `anal_slice_zones_mw.txt` · `bags/replay_f2dr2_mw{01,1,2}.tgz` |
| f2lp1 | 프리셋 3 + 1.4 두 바퀴, 접촉 · 사용자 정지 | `outputs/run_f2lp1.txt` · `stop_f2lp1.txt` · 상세 [상자 과장 카드](box-exaggeration-source.md) |
| pr2 | 정지 프리셋 0 · 3 · 5 | `outputs/run_pr2.txt` · `figures/pr2/` |
| int 재생 | f2lp1 통합 1.4 · 2.0 | `outputs/rp_int2_1022.txt` · `chk_rp_int2.txt` · `anal_slice_zones_f2lp1_int.txt` · `anal_cell_timeline_f2lp1_i20.txt` · `bags/replay_f2lp1_i{14,20}.tgz` |
| f2pi1 | 프리셋 3 + 2.0 검증 3/3 | `outputs/run_f2pi1.txt` · `chk_live_cfg_f2pi1.txt` · `anal_box_maps_series_f2pi1.txt` · `anal_zone_ghosts_f2pi1.txt` · `anal_contact_f2pi1.txt` · bag `bags/bag_f2pi1.tgz` |
| 도구(10-21) | `anal_phantom_cells.py` · `anal_phantom_birth.py` · `anal_phantom_shift.py` · `anal_cells_shift_xcorr.py` · `anal_birth_vs_slice.py` · `anal_zone_ghosts.py` · `run_pr1.sh` · `anal_pr1.py` | `2026-10-21/jobs/` |
| 도구(10-22) | `prep_pr_1022.sh` · `prep_dr_1022.sh` · `prep_op_1022.sh` · `chk_preset_1022.sh` · `chk_live_cfg.sh` · `anal_box_detect.py` · `anal_box_series.py` · `anal_door_pass.py` · `anal_rec_effect.py` · `rp_mw_1022.sh` · `rp_int2_1022.sh` · `chk_rp_int2.sh` · `anal_slice_zones.py` · `run_pr2.sh` · `fig_pr2_top.py` · `fig_box_cells.py` · `fig_preset_video.py` · `up_cam_1022.sh` · `up_nvy_1022.sh` | `2026-10-22/jobs/` · 재생 본체 `2026-10-19/jobs/run_nvblox_replay.sh` |

## 9. 도구 해설
공통: 분석 도구(`anal_*` · `fig_*`)는 PC 에서 Python `rosbags` 로 bag(tgz 를 푼 것)을 읽는다 — 로버 안 움직임. 좌표는 bag 의 `/tf` 에서 map→odom · odom→base_link 를 시각순으로 모아 '직전 값' 으로 쓰고(보간 없음), 로컬 코스트맵 · 조각(odom)은 map 으로 옮겨 센다. Jetson 쪽(`run_pr*` · `rp_*` · `prep_*` · `up_*` · `chk_*`)은 PC 의 WSL 에서 `sshpass -p <PW>` 로 `/tmp` 에 올려 실행(호스트 192.168.0.110). 출발점 낮은 상자 기록 위치 = x 1.151~1.261, y −0.20~−0.02(10-19 실측), 판정 영역은 그보다 한 칸 넓은 (1.15~1.35, −0.20~0.05).

### anal_phantom_cells.py — LETHAL 칸 근거 나누기 (10-21 §13 · §14)
- 부른 형태: `anal_phantom_cells.py bag 시각t(음수 = 끝에서) 그림.png [창 x0,x1,y0,y1=-1.5,3.5,-2.5,1.5]`, 환경 `CTOP=/local_costmap/costmap` 이면 로컬(§14 추가).
- 왜: 사용자 "실제로는 없는 칸" — 그 칸이 지도 · 라이다 · 카메라 중 무엇에서 왔나.
- 하는 일: 그 시각 코스트맵 값 ≥ 100 칸을 ① 저장 지도 점유(≥ 65) 0.10 m 안 ② 최근 1 s 스캔 10 장 점 0.10 m 안 ③ 둘 다 아님 으로 나누고, ③ 을 같은 시각 nvblox 조각(거리 ≤ 0)과 대조, 0.15 m 연결로 덩어리 묶음 · 그림.
- 출력: `덩어리 N 칸 · 중심 (x, y) · 범위 … · 로버에서 d m` · `유령 후보 278 중 nvblox 가 점유로 봄 270`. 남은 곳 `2026-10-21/outputs/anal_phantom_cells*.txt` · `anal_phantom_layer.txt` · `anal_phantom_local_*.txt`, 10-22 `anal_phantom_f2pr1_end.txt` · `anal_phantom_f2dr1_abort.txt` · `anal_phantom_f2sm1_end_check.txt`.
- 결함: 한 시각 스냅숏 — 잠깐 생겼다 사라지는 칸을 놓친다(§15 실수 1 의 한 원인). 창에 벽이 들어가면 벽 옆 칸이 숫자를 채움. 계보: 다음 판 `anal_zone_ghosts.py`(구간 전체).

### anal_birth_vs_slice.py · anal_cells_shift_xcorr.py · anal_phantom_shift.py · anal_phantom_birth.py — 이동 가설 · 탄생 순간 (10-21 §13.2 · §13.3)
- `anal_birth_vs_slice.py bag [창]`: 전역 코스트맵 장마다 지도 밖 새 LETHAL 칸을 찾아, 로버 거리 < 1.5 · 1.5~3 · > 3 m 로 나눠 '그 순간 조각 점유(0.10 m 안)' · '직전 2 s 라이다 점 0.10 m 안' 비율. 출력 [`anal_birth_vs_slice.txt`](../debug_log/2026-10-21/outputs/anal_birth_vs_slice.txt) `로버에서 < 1.5 m: 새 칸 377 · 그 순간 슬라이스에도 점유 239 (63 %) · … 라이다 … 66 (18 %)`.
- `anal_cells_shift_xcorr.py bag t1 t2 [창]`: 두 시각 지도 밖 LETHAL 칸 집합을 0.05 m 격자 이동으로 겹쳐 가장 많이 겹치는 이동 상위 5. 출력 `map→odom … 변화 (-0.022, +0.343, -1.22°)` · `가장 잘 겹치는 이동 상위 5: (+0.00, +0.00) 20 칸 · …`.
- `anal_phantom_shift.py bag [T] [창]`: 끝 칸 p 를 관측 시각 s 좌표로 되돌려(p' = MO(s)·MO(T)⁻¹·p) 지도 벽 위 비율, 대조 = 같은 크기 무작위 방향 20 회. 출력 `최고 18.7 % @ s=20 · 대조 … 평균 36.1 % · 최대 61.5 %`.
- `anal_phantom_birth.py bag 영역들`: 영역 칸이 처음 100 이 된 시각과 그때 로버 거리 · 방위(§13.2-3 '통합 거리 1.4 근처 첫 관측'). 출력 `anal_phantom_birth_f2sm1.txt` · `_f2sm2h.txt`.
- 쓰인 곳: §13.2 이동 가설 기각 · 출처 = 1.5 m 안 카메라 관측. 재사용: 가능(같은 토픽이 든 bag). 결함: 전역 코스트맵은 지도 + nvblox + 라이다 층 합이라 '지도 밖' 판정에 0.10 m 여유 하나만 씀.

### anal_zone_ghosts.py — 영역 · 구간 전체 근거 없는 칸 (10-21 §15, 이후 10-22 기준 지표)
- 부른 형태: `anal_zone_ghosts.py bag t0 t1 'x0,x1,y0,y1;…'`. 10-21 은 `10 60 '1.45,2.65,-0.35,0.45;2.00,2.60,-0.85,-0.45'`(A · B), 10-22 §6 · §7 은 `0 42` 에 문 앞 · 북쪽 영역 추가.
- 하는 일: §4.1 발췌 — 로컬 코스트맵 장마다 LETHAL 칸을 map 으로, 저장 지도 0.10 m 밖 **그리고** 그 순간 직전 1 s 라이다 점 0.10 m 밖이면 칸(0.05 격자 반올림)별로 첫 시각 · 지속 장 수를 쌓음. 판정 문턱 없음(선언 기준과 사람이 비교).
- 출력: `영역 …: 근거 없는 LETHAL 칸 N 개 — (x,y)t첫시각×장수 …`(앞 12 개). 남은 곳 `2026-10-21/outputs/anal_zone_ghosts.txt`, 10-22 `anal_zone_ghosts_f2{pr1,dr1,dr2,pi1,sm1_0to42,pr1_0to42,dr2_0to42}.txt`.
- 결함: 벽 옆 열을 빼지 않음(§5-7). 라이다 근거는 '그 순간' 만 — 라이다가 잠깐 못 본 실물 가장자리도 유령으로 셈(북쪽 영역을 판정에서 뺀 이유). 재사용: 가능 — 이 카드의 '맨바닥 A' 대표 지표.

### run_pr1.sh · anal_pr1.py — 정지 깊이 프리셋 시험 (Jetson, 10-21 §21 · 10-22 §14 run_pr2.sh)
- 부른 형태: PC 가 `@@CAM@@`(camera.launch.py base64) · `@@ANAL@@` · `@@OLDSHA@@` 를 채워 Jetson `/tmp/run_pr1.sh` 로. 로버 안 움직임(스택 내림, base · robot_state_publisher 유지).
- 하는 일(`run_pr1.sh`): ① Jetson `camera.launch.py` sha 가 저장소 HEAD(2661541dcc16)와 같을 때만 depth_preset 판으로 교체(`PR1_ABORT` 보호) ② 주행 스택 프로세스 목록 TERM → 4 s → KILL ③ `for ph in P0a:0 P3:3 P0b:0` — `camera.launch.py emitter_off:=true depth_preset:=$PR` 기동 → 15 s → `ros2 param get … visual_preset` · 드라이버 로그 grep → `anal_pr1.py 20 $T` → 카메라 종료 ④ npz · png 를 base64 tar 로 PC 에.
- `anal_pr1.py`: §4.1 발췌 — 깊이(데시메이션 4, 160×120)를 camera_info 로 3D → 첫 TF 한 번으로 base_link → 수평 ≤ 1.4 m · 높이 0.06~0.30 · 5 cm 복셀. 프레임마다 찍힌 복셀 집합을 세어 비율 < 30 % = 깜빡, ≥ 80 % = 안정(0.10 m 연결 묶음). 채움률 = 0 아닌 화소 비율, 바닥 점 = |z| < 0.04.
- 출력: §4.1 발췌. 남은 곳 `2026-10-21/outputs/run_pr1.txt`(첫 줄 WSL 경고 깨진 글자) · `figures/pr1/*.png`(npz 없음 — §5-5), 10-22 `run_pr2.txt` · `figures/pr2/`(npz 있음).
- 결함 · 한계: nvblox 의 TSDF(광선으로 비우기 · 가중치 · 감쇠)는 흉내 내지 않음 — '찍힌 비율' 만. 정면 1 자세라 비스듬한 각은 못 잼. 드라이버 경고 내용 미출력(§5-4). 계보: pr2 는 같은 도구에 배포 단계만 뺀 판(`run_pr2.sh`, 프리셋 0 · 3 · 5). 재사용: 가능(Jetson 에 저장소 판 camera.launch 가 있을 때).

### anal_box_detect.py · anal_box_series.py — 출발 상자 감지 (10-22 §2 · §3)
- `anal_box_detect.py bag [중심 1.25,-0.075] [영역 1.15,1.35,-0.20,0.05]`: §4.1 발췌 — t0(1.4 m · ±40°) 뒤 처음 ≥ 8 칸 시각 · t0~t0+10 s 칸 수. 문턱 8 = 게이트 L. 출력 `outputs/anal_box_detect_f2{pr1,sm1,dr2,lp1,pi1}.txt`.
- `anal_box_series.py`: 같은 영역을 10 s 묶음으로 주행 전체(나가는 길 · 돌아오는 길 최소 거리). 출력 `anal_box_series_f2{pr1,sm1}.txt`.
- 결함: t0 를 '로버 자세 기준 시야 근사' 로 정의 — 실제 깊이 유효 여부는 안 봄(그것은 10-22 §13 `anal_carve.py`, [상자 과장 카드](box-exaggeration-source.md)). f2pr1 처럼 출발 자세에서 이미 1.26 m · −4° 면 t0 전 기억이 있음(`t0 전 상자 칸 최대 7`).

### anal_door_pass.py · anal_rec_effect.py — f2dr1 중단 판별 (10-22 §6 · §7)
- `anal_door_pass.py bag 시각들 목표x,y 문줄y 문x0,x1`: §4.1 발췌 — 전역 코스트맵 값 < 99 칸만 4-이웃 BFS 로 로버 → 목표 도달 여부, 문 줄 칸 값 나열. 끝에 깊이 · 조각 개수 · 주기. 출력 `anal_door_pass_f2{dr1,sm1,pr1}.txt`. 결함: 99(INSCRIBED)부터 막힘으로 세는 4-이웃 연결일 뿐 계획기(NavFn · tolerance 0.25)를 흉내 낸 것은 아님 — 계획 실패 시각과 맞는 것으로만 씀.
- `anal_rec_effect.py T bag들`: 처음 T s 의 조각 · 로컬 코스트맵 · 깊이 개수 · 주기 · 최대 간격 · 지연(bag 수신 − header.stamp). 출력 [`anal_rec_effect.txt`](../debug_log/2026-10-22/outputs/anal_rec_effect.txt) `/nvblox_node/static_map_slice 344 개 8.60 Hz · 최대 간격 0.41 s · 지연 중앙 0.113 s p95 0.155` · `_f2dr2.txt`.

### rp_mw_1022.sh · rp_int2_1022.sh → run_nvblox_replay.sh — 깊이 bag 재생 A/B (Jetson, 10-22 §9 · §14.2)
- 부른 형태: PC 가 올려 실행. 본체 `2026-10-19/jobs/run_nvblox_replay.sh <깊이 bag> <꼬리표> [name:=value …]` 를 heredoc 으로 `/tmp` 에 풀어 씀(재부팅으로 `/tmp` 판 소실).
- 하는 일: 설치본 `nvblox_local.yaml` 을 `/tmp/nvblox_replay.yaml` 로 → 컨테이너 안에 두 번째 `nvblox_node` 를 `ROS_DOMAIN_ID=42` · `use_sim_time` · 덮어쓸 파라미터로 기동 → `ros2 bag record` 조각 → `ros2 bag play --clock 100 --topics 깊이 · camera_info · /tf · /tf_static`(10-19 §6: 실시간 조각까지 재생하면 출력에 섞임) → 정리(10-19 §15: 래퍼만 죽이면 고아 → 패턴으로). 실시간 스택(도메인 0)은 그대로.
- 출력: `rp_mw_1022.txt` · `rp_int2_1022.txt`(러너 출력 스트림이 첫 머리말 뒤 끊김 — 확인은 `chk_rp_int2.sh` → `chk_rp_int2.txt`), 재생 bag `bags/replay_*.tgz`(PC) · Jetson `~/bags/replay_*`.
- R0 충실도: 같은 설정 재생이 실시간과 A 102 = 102 · 상자 차 2(f2dr2), f2lp1 은 1.4 재생 = 실시간 완전 일치. 한계: 프리셋은 카메라 안이라 재생으로 못 만듦(프리셋 비교는 다른 주행끼리).

### anal_slice_zones.py — 조각 기준 유령 · 상자 (10-22 §9 · §14.2)
- 부른 형태: `anal_slice_zones.py 주행bag [상자t0] 이름=조각bag|live …`, 환경 `RET_WIN=a,b` 면 복귀 접근 상자 영역(1.10~1.31, −0.25~0.03) 추가.
- 하는 일: §4.1 발췌 — 조각(odom, 거리 ≤ 0 · unknown 아님) 칸을 주행 bag 의 map→odom 으로 옮겨 영역별 '한 번이라도' 칸 수(0.05 floor 격자), 상자 영역 t0~t0+10 s 칸 수 중앙 · 최대. 시각축 = 조각 stamp − 주행 bag 시작(재생은 sim time 이라 같은 축).
- 결함: 지도 · 라이다 근거 제외 없음(§5-8), 상자 t0 기본값 2.88(§5-9). 재사용: 가능.

### fig_box_cells.py · fig_preset_video.py · fig_pr2_top.py — 시각화 (10-22 §10 · §14.1)
- `fig_box_cells.py 출력.png 이름=주행bag[@조각bag]@t0 …`: 상자 둘레 조각 칸을 위에서, 색 = 창 안 장애물 비율(초록 ≥ 80 · 노랑 30~80 · 주황 < 30 %), 창 = 출발 · 출발 길 · 복귀(상자 1.2 m 안). 출력 [`box_cells_preset.png`](../debug_log/2026-10-22/figures/box_cells_preset.png).
- `fig_preset_video.py`: 두 주행 나란히 같은 경과 시간 영상(전역 코스트맵 바탕 · 조각 자홍 · 라이다 · 경로 · 맨바닥 A 칸 수). 출력 `videos/preset_cmp_f2dr2_f2pr1.mp4`(git 제외) · [`fig_preset_video.txt`](../debug_log/2026-10-22/outputs/fig_preset_video.txt) `영상 videos/preset_cmp_f2dr2_f2pr1.mp4 1139 장`.
- `fig_pr2_top.py 출력.png 이름=npz …`: 정지 복셀 비율 위에서 본 그림. 출력 [`pr2_top.png`](../debug_log/2026-10-22/figures/pr2/pr2_top.png).
- 계보: 10-21 `pr1_top.png`(생성 코드는 저장소에 없음 — `fig_day_summary_1021.py` 는 그림을 넣기만 함) → 이것들 → 10-23 `Docs/tools/fig_drive_video.py`(기본 영상 도구).

### prep_*_1022.sh · chk_preset_1022.sh · chk_live_cfg.sh · up_cam_1022.sh · up_nvy_1022.sh — 구성 · 배포 · 확인 (Jetson)
- `prep_pr_1022.sh` / `prep_dr_1022.sh` / `prep_op_1022.sh`: `SENSORS_ADD="emitter_off:=true vslam:=shadow dds_shm:=true[ depth_preset:=3]" bash /tmp/prep_patrol.sh lite` 의 요약 줄 + `visual_preset = …`. 셋의 차이는 `depth_preset:=3` 유무(pr = 3 지정, dr = 없음 — 10-22 §10 전이라 장치 0, op = 없음 — §10 뒤 기본 3 확인).
- `chk_preset_1022.sh` · `chk_live_cfg.sh`: `ros2 param get /camera/camera depth_module.visual_preset` + 컨테이너 nvblox 로그의 `max_integration_distance_m` 줄(DDS 참여자를 만드므로 주행 30 s 전엔 안 씀). 출력 [`chk_live_cfg_f2pi1.txt`](../debug_log/2026-10-22/outputs/chk_live_cfg_f2pi1.txt) `visual_preset: Integer value is: 3` · `static_mapper.projective_integrator_max_integration_distance_m: 2`. chk_preset_1022 의 출력 파일은 없음(SUMMARY §1 서술뿐 — 원문 없음).
- `up_cam_1022.sh` · `up_nvy_1022.sh`: 이전 sha 확인(다르면 `UP_ABORT`) → `/tmp/*.pre_1022` 사본 → 교체 → 새 sha · 설치본 링크 · 값 grep. 출력 [`up_cam_1022.txt`](../debug_log/2026-10-22/outputs/up_cam_1022.txt) `이전 sha 95fe7b16a70f … 새 sha d5525810708d` · [`up_nvy_1022.txt`](../debug_log/2026-10-22/outputs/up_nvy_1022.txt) `… 설치본 lrwxrwxrwx … 값 max_integration_distance_m: 2.0`. 저장판 스크립트는 base64 본문을 뺀 사본(주석 '생략').

## 10. 용어
- **유령 칸(phantom)**: 코스트맵 LETHAL 인데 저장 지도 · 그 순간 라이다 어느 쪽 근거도 없고 실물도 없는 칸. 이 카드에서는 '근거 없음' 을 도구가, '실물 없음' 을 사용자가 확인한다.
- **맨바닥 영역 A · 문 영역 B**: A = 출발점 상자 너머 맨바닥 x 1.45~2.65, y −0.35~0.45(벽 옆 열 x ≥ 2.6 은 맨바닥 아님, 10-21 §21.2), B = 문 사이 x 2.00~2.60, y −0.85~−0.45. 로컬 코스트맵 기준(`anal_zone_ghosts`)과 조각 기준(`anal_slice_zones`) 두 값이 있다(§5-8).
- **깊이 프리셋(visual_preset)**: D455f 고급 모드 묶음 값. 이 장치 0 Custom · 1 Default · 2 Hand · 3 High Accuracy · 4 High Density · 5 Medium Density. High Accuracy 는 스테레오 짝 신뢰도 문턱을 높여 확신 낮은 깊이를 0(무효)으로 버린다(librealsense 설명 — 내부 값은 안 봄).
- **채움률**: 깊이 영상에서 0 아닌 화소 비율(P0 0.317 · P3 0.045 · P5 0.117).
- **깜빡 · 안정 복셀**: 정지 시험 20 s 동안 찍힌 프레임 비율 < 30 % · ≥ 80 % 인 5 cm 복셀.
- **통합 거리(projective_integrator_max_integration_distance_m)**: nvblox 가 깊이 화소를 TSDF 에 넣는 최대 거리. 밖의 깊이는 버린다 — 멀리서 본 상자도, 먼 바닥 잡음도.
- **esdf_integrator_min_weight**: TSDF 가중치가 이 값보다 작은 복셀은 ESDF(거리 지도 · 조각)에 표면으로 안 넣는다. 한두 번 찍힌 점을 거르려는 손잡이 — 여기선 상자도 같이 걸러짐.
- **R0(재생 충실도)**: 같은 설정 재생 출력이 실시간 출력과 같은지 먼저 보는 단계.
