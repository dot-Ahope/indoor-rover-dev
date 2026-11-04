# MPPI 굽은 곳 안쪽 깎기 — 컨트롤러 탓 판별 · 오프라인 모의 · PathAlign 28 / PathFollow 5 채택 (9 기: 10-26 §7.4(배경) · §8 ~ §17, 10-27 §11 ~ §14 · §19 · §25(28 · 5 운용 기록), 10-28 §4 · §5(통로 쪽 참고))

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회(설정 채택 · 기전 미확인)** — Smac 경로에서도 MPPI 가 받은 경로의 굽은 곳 안쪽으로 +10.7 · +15.7 cm 깎는 것을 컨트롤러 자기 좌표(odom)로 확인했고(10-26 §9), PathAlign 14 → 28 · PathFollow 10 → 5 로 b910 2 회 +4.6 · +1.6 cm 로 줄여 저장소에 채택했다(§14). 해결 아님: ① 깎는 **기전**(먼 경로점 당김 > 경로 크리틱)은 추정이고 오프라인 모의로는 평균 차가 씨앗 잡음과 '구분 불가'(§10.5) ② 같은 값이 NavFn 대체 경로(서쪽 통로)를 따라갈 땐 통로 최소 여유 0.8 cm · 정지 5 번(f2sa3, 1 회 · 날짜 다름)이었다 ③ 채택 뒤 주행에서 굽은 곳 이탈 지표를 다시 잰 적이 없다 ④ **지금 기본 구성(NavFn · 재계획 0.5 Hz)** 에 28 · 5 가 함께 들어갔지만 그 조합으로 달린 기록은 없다 | 10-26 §7.4 ~ 10-28 §5 | [10-26 §9](../debug_log/2026-10-26/SUMMARY.md) 사용자 "로버가 그 수정된 경로보다 상자쪽으로 꺾어 움직이려고 한 움직임이 컨트롤러 부분 문제라는 것인가?" | [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 278 ~ 281 행 PathAlign `cost_weight: 28.0` · 285 행 PathFollow `cost_weight: 5.0`(브랜치 `feature/smac-hybrid`, 10-26 §14, Jetson 배포 [`up_params_1026.sh`](../debug_log/2026-10-26/jobs/up_params_1026.sh)). 시험 중엔 Jetson yaml 만([`up_mppi_path_1026.sh`](../debug_log/2026-10-26/jobs/up_mppi_path_1026.sh)). 도구 [`Docs/tools/anal_mppi_sim.py`](../tools/anal_mppi_sim.py) 에 `resample` · `wheel_max` · 굽은 곳 이탈 기록 추가(9 ~ 11 · 117 ~ 144 · 362 ~ 365 행) | [경로 추종 · 재계획 → B0](path-tracking-replan-b0.md)(10-23 의 '굽은 곳 안쪽 69~91 %' · f2pa1/f2pa2 PathAlign 28 첫 시험 — 이 카드의 앞 이야기) · [Smac Hybrid 채택](smac-hybrid-adoption.md)(같은 주행 f2sh · f2sa · f2st 의 계획기 쪽, NavFn 대체 · tolerance 0.35) · [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md)(§10 의 구동계 정정 M2) · [MPPI 상자 옆 통로 튜닝](mppi-passage-tuning.md)(PathFollow 10 · offset 20 을 정한 09-16) · [PathBlockedAhead · only_new](pathblocked-only-new.md)(f2sa3 · f2st1 막힘 판정 · 10-28 §5) · [복귀 길 상자 칸](box-return-cells.md)(상자를 잊고 다시 봄 · f2tf1 접촉) · [상자 옆 정지 — 기전](box-side-stall-cause.md)(칸 판정 뒤집힘 2.7~4.4 cm — 통로 여유의 읽기 기준) · [회전 방식 · 앞 회전 우선](rotation-method-track-ratio.md)(PreferForward 15 효과가 28 · 5 아래에서 미측정) · [nvblox 층 TF 실패](nvblox-layer-tf-drop.md)(f2st1 상자 앞 전역 값 깜빡임 · 10-27 §15) |

**한 줄**: Smac 으로 계획 경로를 상자에서 멀리 둔 뒤에도(17.1 cm) f2sh2 는 복귀 상자 동쪽 대각선에서 10.8 cm 까지 붙었다. 컨트롤러 좌표(odom)로 다시 재니 로버가 받은 경로보다 상자 쪽(=굽은 곳 안쪽) +15.7 cm 를 달렸고 그동안 위치 보정은 5 cm 이하였다 — **MPPI 가 경로를 깎은 것**. 오프라인 모의는 처음엔 재현조차 못 했는데, 원인은 시뮬 구동계(회전만 0.7 배)였고 실제는 **바깥 바퀴가 펌웨어 한계 0.085 m/s 에 걸려 v · ω 가 같은 비율로 줄어드는 것**이었다. 고친 모의에서 어느 변형도 평균을 5 cm 줄이지 못했지만 PathAlign 28 + PathFollow 5 가 나쁜 꼬리(19.8 → 11.2 cm)를 줄였고, 실주행 A/B 2 회에서 안쪽 이탈 10.7 · 15.7 → 4.6 · 1.6 cm · 상자 옆 14.6 · 14.9 cm · 정지 0 이 나와 채택했다. 그 직후 no5(f2sa3)에서 Smac 이 실패해 NavFn 원경로를 따라간 서쪽 통로는 여유 0.8 cm · 정지 15.3 s 였다 — 같은 가중치가 경로 품질에 따라 반대로 작용한다는 읽기(추정, 1 회).

## 1. 증상
- **10-26 §7.4 f2sh2**(b910, Smac Hybrid + MPPI 14 · 10, 재계획 0.01): 3/3 성공, 복귀 상자 실제 최소 **10.8 cm**(13:18:32.9, 로버 (1.63, 0.09, 152°) — 상자 옆 직선이 아니라 **상자 동쪽으로 비스듬히 꺾어 들어오는 굽은 곳**). 그 경로(13:18:09 TF 외삽 중단 뒤 Smac 재계획)는 상자에서 17.1 cm 였다(`anal_plan_series_f2sh2.txt`). 같은 Smac 의 f2sh1 은 18.4 cm. 데이터 [`anal_contact_f2sh2_d30.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/anal_contact_f2sh2_d30.txt) · [`anal_plan_series_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/anal_plan_series_f2sh2.txt).
- 10-26 §8 비교 그림 [`box_compare_b0_smac.png`](../debug_log/2026-10-26/figures/compare/box_compare_b0_smac.png) · 장면 [`f2sh2_return_box_frame.png`](../debug_log/2026-10-26/figures/compare/f2sh2_return_box_frame.png): B0 경로 y ≈ 0.25~0.30 · 로버 y 0.15~0.23, Smac 경로 y ≈ 0.31~0.36(더 북쪽 · 큰 호). f2sh2 의 10.8 cm 는 x ≈ 1.6 대각선.
- 사용자 질문(§9): 경로가 상자를 알고 고쳐진 뒤에도 로버가 상자 쪽으로 꺾어 든 것이 컨트롤러 문제인가.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-26 §7.3 · §7.4 | f2sh1 · f2sh2(Smac, MPPI 14 · 10) | 상자 18.4 · 10.8 cm, 경로 17.1~18.5(NavFn 8.9~13.3). f2sh2 t 183~188 경로보다 상자 쪽 +13~15.6 cm(map), 상자 옆 직선 +0.7~2.6 | 남은 손실 = 컨트롤러 굽은 곳 깎기(10-23 §22.3 과 같은 성질). 계획기 쪽 본체는 [Smac 카드](smac-hybrid-adoption.md) | [`anal_track_dev_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/anal_track_dev_f2sh2.txt) · [`run_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/run_f2sh2.txt) |
| 10-26 §8 | 시각화(B0 3 대 Smac 2) | 위 §1 그림 · 영상 `videos/f2sh{1,2}_return_box.mp4`(git 제외). 첫 판 점선이 '복귀 구간 시작 직전 경로' 라 B0 가 막힘 전 상자 관통 경로로 그려짐 → '최소 여유 순간에 쓰이던 경로' 로 고침 | 그림 판독(판정 아님) | [`fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt) · [`fig_drive_video_f2sh2.txt`](../debug_log/2026-10-26/outputs/fig_video/fig_drive_video_f2sh2.txt) |
| 10-26 §9 | **컨트롤러 탓인가 — odom 좌표로 다시 잼** | 로버 ↔ `/transformed_global_plan`(odom) 옆 거리 13:18:25 +9.3 → 30.5 **+15.7** → 37.5 +5.2 cm, 같은 창 map→odom 변화 x ≤ 4.5 · y ≤ 2.7 cm. 전제 정정: 복귀 재계획은 상자 막힘이 아니라 13:18:09 **TF 외삽 중단** 뒤 | **MPPI 가 받은 경로 안쪽을 깎음**(측정). 위치 보정 몫 ≤ 5 cm. 기전(지평 3.2 s 의 먼 경로점 당김 > PathAlign · PathFollow)은 추정 | [`chk_dev_frame_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/chk_dev_frame_f2sh2.txt) · 도구 [`chk_dev_frame_f2sh2.py`](../debug_log/2026-10-26/jobs/chk_dev_frame_f2sh2.py) |
| 10-26 §10 · §10.1 | 오프라인 모의 선언(f2sh2 13:18:22 부터 16 s) — 재현 판정 '실제 15.7 ± 5', 변형 9 개 | **첫 판 9 변형 모두 시작 9.6 cm 에서 줄어듦**(중앙 0.7~2.5 cm) — 실제는 9.3 → 15.7 로 커짐 | 재현 ✘(판정 ①) → 변형 비교에 못 씀 | [`sim_corner_1026.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026.txt) · [`run_sim_corner_1026.sh`](../debug_log/2026-10-26/jobs/run_sim_corner_1026.sh) |
| 10-26 §10.2 | 실제 명령 대 움직임 | 굽은 곳 13:18:24~28 명령 v 0.080 · ω +0.17~0.20, 실제(휠 · EKF · cuVSLAM · 자이로 일치) v 0.055~0.061 · ω +0.10~0.13. 바깥 바퀴 0.058 + 0.125 × 0.2215 ≈ **0.086 = 펌웨어 한계 0.085**. 펌웨어 계산 (0.08, 0.19) → ×0.70 → (0.056, 0.132) = 실측 | 시뮬 구동계 `w_gain 0.7`(회전만)은 곡률을 바꿔(덜 돌아 바깥으로) 깎기를 가렸음 → **`wheel_max=0.085` 비례 축소**(측정 + 펌웨어 코드). 재현 판 씨앗 1·2·3 안쪽 최대 9.7 · 9.6 · **20.2**, 실제 15.7 이 범위 안 | [`chk_cmd_vs_motion_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/chk_cmd_vs_motion_f2sh2.txt) · [`sim_corner_1026b.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026b.txt) · 펌웨어 [`microros_task.c`](../../firmware/rover_jupiter_fw/App/microros/microros_task.c) 171 ~ 183 행 |
| 10-26 §10.3 | 바퀴 포화 구동계 · 씨앗 6 × 7 변형(같은 13:18:22 장면) | 평균 감소 최대 0.8 cm(기준 5). vx_max 0.06(포화 줄임)도 안 줄어듦(11.7). ESS 10~20 | ✘ 기준 미달. **포화는 '느려지는' 원인이지 깎기 주원인 아님**(시뮬, 추정). 장면 시작이 이미 9.3 cm 벗어난 뒤라 '최대' 의 바닥이 9.6 — 지표 한계 | [`sim_corner_1026c_summary.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026c_summary.txt) · [`sim_corner_1026c.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026c.txt) |
| 10-26 §10.4 · §10.5 | 시작을 재계획 직후 13:18:10 으로 · 26 s · 씨앗 10 × 7 변형(해 잡음 줄이는 batch 2000 · wz_std 0.3 · iteration 3 포함) | base 7.9 ± 5.2(최악 19.8) · **A28Fw5 5.5 ± 2.1(최악 11.2)** · 차 −2.4 / 표준오차 1.8. batch 2000 은 표준편차만 줄고 평균 9.4. 모든 판 정지 0 | 판정 ✘(평균 ≥ 5 cm 감소 없음) · 차는 표준오차 1.3 배 이하 = **구분 불가**. 28 + 5 는 꼬리를 줄이는 경향. 깎기는 표본 잡음이 아니라 비용 구조가 고르는 해(추정) | [`sim_corner_1026d_summary.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026d_summary.txt) · [`sim_corner_1026d.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026d.txt) · [`run_sim_corner_1026d.sh`](../debug_log/2026-10-26/jobs/run_sim_corner_1026d.sh) · [`anal_sim_corner_summary.py`](../debug_log/2026-10-26/jobs/anal_sim_corner_summary.py) |
| 10-26 §10.6 · §10.7 | 10-23 f2pa2 5.5 s 정지 장면(t 94 s ~ 16 s, NavFn /plan_smoothed)에 A14 · A28 · A28Fw5 × 씨앗 10 | 셋 다 1 s 넘는 정지 **0**, 16 s 전진 0.96~0.97 m. 실제(A28)는 t 100.6~105.6 s 정지 | 재현 ✘ → **'28 이 정지를 부르나' 는 시뮬로 판단 불가**. 차이 후보(목표 자세 · warm start · 경로 전환 시각) 미확인 → 실주행 여부는 사용자 결정 | [`sim_stall_1026_summary.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_stall_1026_summary.txt) · [`chk_sim_head_f2pa2.txt`](../debug_log/2026-10-26/outputs/mppi_sim/chk_sim_head_f2pa2.txt) · [`run_sim_stall_1026.sh`](../debug_log/2026-10-26/jobs/run_sim_stall_1026.sh) |
| 10-26 §11 · §11.1 | **실주행 A/B 선언** → f2sa1(Smac + 28 · 5, Jetson yaml 만) | 3/3 · 1 s 넘는 정지 0 · 상자 복귀 14.6 cm · **굽은 곳 안쪽 이탈(odom) +4.6 cm**(f2sh1 +10.7 · f2sh2 +15.7). 복귀 출발 Smac 'no valid path' → NavFn 대체(상자 관통 −15.5) → 재계획 Smac 17.0 cm | 1 회라 보류. ⚠ 재계획 '계기 미확인' 이라 적었으나 시각 대조로는 15:14:14.64 TF 외삽 중단 뒤 재시작과 맞음(아래 §5 어긋남 3) | [`run_f2sa1.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/run_f2sa1.txt) · [`anal_bend_dev_odom_sa1.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/anal_bend_dev_odom_sa1.txt) · [`anal_stops_f2sa1.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/anal_stops_f2sa1.txt) · [`prep_smac_1026_5.txt`](../debug_log/2026-10-26/outputs/setup/prep_smac_1026_5.txt) |
| 10-26 §11.2 | f2sa2 · A/B 정리 | 3/3 · 정지 0 · 상자 14.9 · 이탈 **+1.6 cm**. 막힘 1(상자 (1.24, 0.07)) → 재계획 15.7 cm | 판정 ①~⑤ ✔ — 깎기가 줄고 상자 옆이 두 번 다 ~15 cm 로 고름(14 · 10 판은 18.4 · 10.8 로 흩어짐). 각 2 회 | [`run_f2sa2.txt`](../debug_log/2026-10-26/outputs/drives/f2sa2/run_f2sa2.txt) · [`anal_bend_dev_odom_sa2.txt`](../debug_log/2026-10-26/outputs/drives/f2sa2/anal_bend_dev_odom_sa2.txt) · [`anal_contact_f2sa2_d30.txt`](../debug_log/2026-10-26/outputs/drives/f2sa2/anal_contact_f2sa2_d30.txt) |
| 10-26 §12 | 영상 · 비교 그림 | f2sh2(파랑)는 대각선에서 경로 안쪽으로 깎음, f2sa1 · f2sa2 는 점선 바깥 호를 따름. 영상 도구가 NavFn 대체가 한 번이라도 있으면 Smac 경로를 빠뜨리던 규칙 고침 | 그림 판독 | [`box_compare_b0_smac_mppi.png`](../debug_log/2026-10-26/figures/compare/box_compare_b0_smac_mppi.png) · [`fig_box_compare_mppi.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare_mppi.txt) · [`f2sa2_return_box_frame.png`](../debug_log/2026-10-26/figures/compare/f2sa2_return_box_frame.png) · `videos/cmp_f2sh2_vs_f2sa2.mp4`(git 제외) |
| 10-26 §13 | 사용자 "28/5 에서 경로와 어긋나 멈췄다 다시 움직였나" | 멈칫 f2sh1 5 · f2sh2 4 · f2sa1 6 · f2sa2 7. 긴 것은 모두 W3 도착 → 복귀 출발 0.9~2.35 s 로, 그동안 회전 명령 −0.21~−0.37 · 실제 −0.10~−0.35 rad/s = **제자리 돌아서기**. TF 외삽 중단 0.15~0.35 s 각 2 | 10-23 f2pa2 형 '어긋나 1 s 넘게 서 있는' 정지 **없음**. 1~3 개 많은 것은 돌아서기를 둘로 센 것 · 0.05 s 스침 | [`anal_dip_events_f2sa1.txt`](../debug_log/2026-10-26/outputs/compare/anal_dip_events_f2sa1.txt) · [`_f2sa2.txt`](../debug_log/2026-10-26/outputs/compare/anal_dip_events_f2sa2.txt) · [`_f2sh1.txt`](../debug_log/2026-10-26/outputs/compare/anal_dip_events_f2sh1.txt) · [`_f2sh2.txt`](../debug_log/2026-10-26/outputs/compare/anal_dip_events_f2sh2.txt) · [`chk_w3_turn.txt`](../debug_log/2026-10-26/outputs/compare/chk_w3_turn.txt) |
| 10-26 §14 · §14.1 | **28 · 5 채택**(사용자) · no5 선언 | 저장소 yaml 14 → 28 · 10 → 5, Jetson sha 5ba19dfdb99f → 7bce0cb94734(설치본은 **일반 파일**). NavFn 판도 같은 값을 쓰게 됨 — B0 는 태그에 14 · 10 | — | [`up_params_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_params_1026.txt) |
| 10-26 §15 | **f2sa3**(no5) | 8/8 · 서쪽 통로 계획 5 번 모두 Smac 실패 → NavFn 원경로(스무딩 충돌). 통로 로컬 정확 여유 최소 **0.8 cm**(16:12:15.7), < 2.7 cm 7 프레임, 정지 5 번 15.3 s · Wait 2. 통로 추종 \|이탈\| 중앙 **4.1(B0 f2rp4) → 1.0 cm**, 로버 자리 비용 분포 같음(중앙 71) | 판정 ③ ✘. 읽기(추정): **NavFn 원경로를 28 이 더 바짝 따라** MPPI 가 통로 가운데로 비킬 여지가 줄었다 — 상자(Smac 경로)에선 이득 · 통로(NavFn)에선 손해 | [`run_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/run_f2sa3.txt) · [`anal_band_run_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_band_run_f2sa3.txt) · [`anal_stops_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_stops_f2sa3.txt) · [`anal_corridor_track.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_corridor_track.txt) · [`nav_events_ms_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/nav_events_ms_f2sa3.txt) |
| 10-26 §16 · §17 | 사용자 촬영 영상(4K 445 s) 판독 · 시각화와 합본 | 통로 좁은 곳 = 왼쪽 의자 받침 · 빨간 쇼핑백, 오른쪽 프린터 · **날개 열린 상자**. 16:12:17 로버가 비스듬히 끼임(시각화도 로버 −61° · 경로 −100°). 전역 코스트맵 치명 칸 사이 **0.50 m — 두 날 같음**. 사용자(§17): **닿지 않았다** | f2rp4 비교 유효(치명 간격 기준 — 아래 §5 어긋남 2). 0.8 cm 는 칸 단위 · 기억 오차를 품은 값 | [`anal_corridor_gap.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_corridor_gap.txt) · [`cmp_corridor_161217.png`](../debug_log/2026-10-26/figures/real_video/cmp_corridor_161217.png) · [`real_rviz_corridor_hd_x2.png`](../debug_log/2026-10-26/figures/real_video/real_rviz_corridor_hd_x2.png) · [`fig_rviz_video_f2sa3_corridor.txt`](../debug_log/2026-10-26/outputs/fig_video/fig_rviz_video_f2sa3_corridor.txt) |
| 10-27 §9 ~ §11 | f2st1(no5, Smac **tolerance 0.35**, 28 · 5 그대로) | 통로 **남행 Smac 성공**(실패 0) → 남행 좁은 곳 최소 **4.1 cm**(f2sa3 0.8) · 남행 24.7 s(39.7). 북행은 Smac 실패 3 → NavFn → 최적화 실패 2 · MonotoneEscape, 전체 최소 2.9 cm(북행 출발 회전 중). 상자 복귀 16.3 cm | 같은 28 · 5 에서 **경로가 Smac 이면 통로 여유가 돌아옴**(1 회) — §15 '경로 품질' 읽기와 맞는 방향. 계획기 쪽은 [Smac 카드](smac-hybrid-adoption.md) | [10-27 `run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/run_f2st1.txt) · [`anal_band_run_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/anal_band_run_f2st1.txt) · [`chk_corr_paths_f2st1.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/chk_corr_paths_f2st1.txt) |
| 10-27 §12 | f2st1 요약 그림 · 영상 | 목표별 시간 f2rp4 · f2sa3 · f2st1 막대 + 통로 · 정지 · 상자 지표. 상자 앞 영상: 11:24:46 PathBlockedAhead (1.13, 0.14) 99 → 48 중단 · Wait 5 s → 53 재계획 → 57 TF 외삽 중단 1 회 → 상자 북쪽으로 지나감(16.3 cm) | MPPI 쪽 이상 없음 — 정지는 막힘 판정 · 복구 차례(→ [PathBlockedAhead 카드](pathblocked-only-new.md)) | [`f2st1_summary.png`](../debug_log/2026-10-27/figures/f2st1_summary.png) · 도구 [`fig_f2st1_summary.py`](../debug_log/2026-10-27/jobs/fig_f2st1_summary.py) |
| 10-27 §14 | 막힘 판정 칸 원자료 대조 | 그 점은 상자 자체의 내접 띠(상자 칸까지 13~18 cm). 원인 = 멀어지면 상자를 잊는 전역 지도 | 막힘 노드 정상 → [PathBlockedAhead 카드](pathblocked-only-new.md) · [복귀 길 상자 칸](box-return-cells.md) | [`anal_block_cell_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/anal_block_cell_f2st1.txt) |
| 10-27 §19 · §20 · §25, 10-28 §4 | 28 · 5 그대로 no5 3 회 더(f2tf1 · f2tt1 · f2tt2) | 상자 복귀 −1.0(**접촉** · 상자 밀림, 사용자 확인) · 14.4 · 14.0 cm. 통로 최소 3.8 · 3.1 · 4.2 cm(< 2.7 cm 0). f2tf1 접촉은 복귀 때 상자가 카메라 시야(±43°) 밖이라 지도에 없던 것 | 접촉은 컨트롤러가 아니라 상자 미관측(→ [복귀 길 상자 칸](box-return-cells.md)). 굽은 곳 이탈 지표는 이 주행들에서 다시 재지 않음 | [10-27 `anal_contact_f2tf1_d30.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/anal_contact_f2tf1_d30.txt) · [`anal_contact_f2tt1_d30.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/anal_contact_f2tt1_d30.txt) · [10-28 `anal_contact_f2tt2_d30.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_contact_f2tt2_d30.txt) · 통로 [`anal_band_run_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/anal_band_run_f2tf1.txt) · [`_f2tt1.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/anal_band_run_f2tt1.txt) · [10-28 `_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_band_run_f2tt2.txt) |
| 10-28 §5 | 통로 남쪽 좁은 곳 반복 막힘 칸 | 북행 출발 제자리 회전 중 가장자리가 한 칸 더 안쪽으로 찍혀 경로 점 96 → 99 | 계획 경로가 이미 내접 띠 옆(96)이라는 것 — 컨트롤러가 아니라 계획 · 막힘 판정 쪽(→ [PathBlockedAhead 카드](pathblocked-only-new.md)) | [10-28 `anal_corridor_cell_f2tt2.txt`](../debug_log/2026-10-28/outputs/corridor_cell/anal_corridor_cell_f2tt2.txt) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| f2sh2 굽은 곳 이탈은 위치 보정(map→odom)이 경로를 로버 밑에서 옮긴 탓 | 컨트롤러 좌표(odom)에서 받은 경로 대비 이탈 · 같은 창 map→odom 변화(§9) | odom 이탈 +15.7 cm, map→odom 변화 ≤ 4.5 cm | **기각** — MPPI 가 깎음(측정) |
| 이상적 차동구동 + 회전 이득 0.7 시뮬이 실제를 흉내 낸다 | 재현 판정(§10.1) | 9 변형 모두 이탈이 줄어듦, 실제는 커짐 | **기각** → 구동계 정정 |
| 실제 회전이 덜 나오는 것은 바퀴 포화(비례 축소) | 명령 · 휠 · EKF · cuVSLAM · 자이로 대조 + 펌웨어 코드(§10.2) | 바깥 바퀴 0.086 ≈ 한계 0.085, 펌웨어 계산 = 실측. 비례 축소 시뮬에서 실제 15.7 이 씨앗 범위 안 | **지지(측정 + 코드)** |
| 바퀴 포화가 깎기의 주원인 | vx_max 0.06 변형(§10.3) | 안쪽 최대 평균 11.7(base 11.4) | **기각 쪽(시뮬, 추정)** — 포화는 속도를 늦출 뿐 |
| 깎기는 MPPI 표본 잡음(ESS 10~20) | batch 2000 · iteration 3(§10.5) | batch 2000 표준편차 5.2 → 2.2 인데 평균 7.9 → 9.4 | **기각 쪽(시뮬)** — 비용 구조가 고르는 해(추정) |
| PathFollow 당김(offset 20 점 ≈ 0.6 m 앞)을 줄이면 깎기가 준다 | offset 10 · 5, 가중 5(§10.3 · §10.5) | 평균 감소 0.3~0.7 cm(§10.3) · 가중 5 단독 0.0(§10.5) | **미확인**(구분 불가) |
| PathAlign 28 + PathFollow 5 가 깎기를 줄인다 | 시뮬 씨앗 10(§10.5) · 실주행 A/B 2 + 2(§11) | 시뮬 평균 −2.4 / 표준오차 1.8(구분 불가) · 최악 19.8 → 11.2. 실주행 +10.7 · +15.7 → +4.6 · +1.6 cm | **지지(실주행 2/2, 표본 작음)** — 시뮬은 방향만 |
| PathAlign 28 이 '경로 · 목표 어긋남' 정지(f2pa2 5.5 s)를 부른다 | f2pa2 장면 시뮬(§10.7) · 실주행 정지 수(§11 · §13) | 시뮬 재현 불가. 실주행 b910 2 회 정지 0, no5 5 회(f2sa3 · f2st1 · f2tf1 · f2tt1 · f2tt2)의 1 s 넘는 정지는 모두 막힘 판정 · TF 중단 · 통로 최적화 실패 뒤 복구 | **미확인** — Smac 경로 · 채택 뒤 주행에선 그 서명 0 회. NavFn 경로 + 28 · 5 조합은 통로 구간 말고는 기록 없음 |
| 같은 28 · 5 가 NavFn 원경로(통로)에선 손해 | f2sa3 대 B0 f2rp4 통로 추종 · 여유(§15), f2st1 Smac 경로 통로(10-27 §11) | 이탈 중앙 4.1 → 1.0 · 여유 4.8 → 0.8 cm / Smac 경로면 4.1 cm | **추정**(각 1 회 · 날짜 · 지도 · 물건 배치 · tolerance 다름) |
| 깎기 기전 = 지평 3.2 s 끝을 앞 경로점이 당기는 힘(PathFollow · Goal · 진행)이 경로에 붙이는 힘(PathAlign)보다 큼 | 크리틱별 비용 분해는 안 함 | — | **미확인(추정)** |

## 4. 조치와 효과
### 4.1 바꾼 것
- 10-26 §11: Jetson yaml 만 `up_mppi_path_1026.sh 28 5`(실행 중 값은 안 바꾸고 다음 prep 으로 — 10-14 실행 중 변경 멈칫 교훈). prep 이 실행 중 값을 확인: [`prep_smac_1026_5.txt`](../debug_log/2026-10-26/outputs/setup/prep_smac_1026_5.txt) 18 행 `MPPI PathAlign = Double value is: 28.0 · PathFollow = Double value is: 5.0`(prep 래퍼 [`prep_smac_1026.sh`](../debug_log/2026-10-26/jobs/prep_smac_1026.sh) 9 행이 `ros2 param get` 으로 찍음; 같은 래퍼 3 행 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite`).
- 10-26 §14: 저장소 [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) — 지금 줄:
  ```yaml
  # ★ 2026-10-26 §11~§14(사용자 채택, Smac 구성): PathAlign 14 → 28 · PathFollow 10 → 5 — 굽은 곳 안쪽 깎기 10.7 · 15.7 → 4.6 · 1.6 cm,   # 278 행
  PathAlignCritic: {enabled: true, cost_power: 1, cost_weight: 28.0, max_path_occupancy_ratio: 0.05, trajectory_point_step: 3, threshold_to_consider: 0.20, offset_from_furthest: 3}   # 281 행
  PathFollowCritic: {enabled: true, cost_power: 1, cost_weight: 5.0, offset_from_furthest: 20, threshold_to_consider: 0.2}   # 10-26: 10 → 5(앞 20 점 당김 = 굽은 곳 지름길 줄임)   # 285 행
  ```
  Jetson 배포 출력([`up_params_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_params_1026.txt)): `이전 src 5ba19dfdb99f · 설치본 5ba19dfdb99f 일반파일` → `새 src 7bce0cb94734 · 설치본 7bce0cb94734`.

### 4.2 전후 수치 (b910 복귀 상자, Smac 구성 · 재계획 0.01)
| 주행 | MPPI PathAlign · PathFollow | 상자 옆 실제 최소(복귀) | 굽은 곳 안쪽 이탈 최대(odom) · 95 % · 중앙 | 1 s 넘는 정지 | 총 시간 |
|---|---|---|---|---|---|
| f2sh1 | 14 · 10 | 18.4 | +10.7 · +10.3 · +1.3 | 0 | 205.8 |
| f2sh2 | 14 · 10 | 10.8 | +15.7 · +15.4 · +9.0 | 0 | 201.7 |
| f2sa1 | **28 · 5** | 14.6 | **+4.6** · +4.3 · +0.9 | 0 | 205.8 |
| f2sa2 | **28 · 5** | 14.9 | **+1.6** · +0.9 · −0.5 | 0 | 199.1 |

원문([`anal_bend_dev_odom_sa1.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/anal_bend_dev_odom_sa1.txt) — 같은 도구로 세 주행, f2sa2 는 [`_sa2.txt`](../debug_log/2026-10-26/outputs/drives/f2sa2/anal_bend_dev_odom_sa2.txt)):
```
f2sh1 · 복귀 상자 둘레 12:49:55~12:50:34 · 굽은 곳 안쪽 이탈(odom) 최대 +10.7 cm @ 12:50:11 · 95 % +10.3 · 중앙 +1.3 cm · 같은 창 map→odom 변화 x 4.9 · y 3.6 cm
f2sh2 · 복귀 상자 둘레 13:18:16~13:18:50 · 굽은 곳 안쪽 이탈(odom) 최대 +15.7 cm @ 13:18:30 · 95 % +15.4 · 중앙 +9.0 cm · 같은 창 map→odom 변화 x 5.8 · y 5.4 cm
f2sa1 · 복귀 상자 둘레 15:14:26~15:15:00 · 굽은 곳 안쪽 이탈(odom) 최대 +4.6 cm @ 15:14:40 · 95 % +4.3 · 중앙 +0.9 cm · 같은 창 map→odom 변화 x 7.0 · y 5.6 cm
f2sa2 · 복귀 상자 둘레 15:36:31~15:37:07 · 굽은 곳 안쪽 이탈(odom) 최대 +1.6 cm @ 15:36:47 · 95 % +0.9 · 중앙 -0.5 cm · 같은 창 map→odom 변화 x 5.0 · y 4.8 cm
```
지표 핵심 줄([`anal_bend_dev_odom.py`](../debug_log/2026-10-26/jobs/anal_bend_dev_odom.py) 18 ~ 19 행 — 경로가 ±0.5 m 에서 15° 넘게 휠 때만, 휘는 쪽을 + 로):
```python
h = np.unwrap(np.arctan2(ab[i0:i1 + 1, 1], ab[i0:i1 + 1, 0])); turn = h[-1] - h[0] if len(h) > 1 else 0.0
return float('nan') if abs(turn) < math.radians(15) else d * side * np.sign(turn)
```

### 4.3 판단에 쓴 핵심 출력
- **컨트롤러 탓(§9)** — [`chk_dev_frame_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/chk_dev_frame_f2sh2.txt)(열: 시각 · odom 이탈(+ 상자 쪽) · map→odom 변화):
  ```
   13:18:25.0 |   +9.3 cm |  +0.0  +0.0 cm +0.00°
   13:18:30.5 |  +15.7 cm |  -2.8  -1.7 cm +0.43°
   13:18:37.5 |   +5.2 cm |  -4.5  -2.7 cm +0.55°
  ```
- **바퀴 포화(§10.2)** — [`chk_cmd_vs_motion_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/chk_cmd_vs_motion_f2sh2.txt)(명령 v ω | 휠 | EKF | vslam | 자이로 | ω 실제/명령):
  ```
   13:18:24.5 | +0.080 +0.196 | +0.056 +0.128 | +0.055 +0.001 +0.121 | +0.056 +0.002 | +0.118 | 0.60
   13:18:26.0 | +0.084 +0.170 | +0.061 +0.106 | +0.062 -0.000 +0.076 | +0.063 +0.000 | +0.076 | 0.45
  ```
  펌웨어([`microros_task.c`](../../firmware/rover_jupiter_fw/App/microros/microros_task.c) 178 ~ 183 행, `V_MAX_MPS` = [`rover_platform.h`](../../firmware/rover_jupiter_fw/App/app/rover_platform.h) 82 행 0.085, `HALF_WHEEL_BASE` 0.2215 = `microros_task.c` 71 행):
  ```c
  float peak = fmaxf(fabsf(v_l), fabsf(v_r));
  if (peak > V_MAX_MPS) {
      const float scale = V_MAX_MPS / peak;
      v_l *= scale;
      v_r *= scale;
  }
  ```
  시뮬에 옮긴 줄([`anal_mppi_sim.py`](../tools/anal_mppi_sim.py) 362 ~ 365 행): `if P['wheel_max'] > 0:` … `if _pk > P['wheel_max']: _vl *= P['wheel_max'] / _pk; _vr *= P['wheel_max'] / _pk`. 재현 판([`sim_corner_1026b.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026b.txt) SAT · SAT_s2 · SAT_s3): `최대 +0.097 · 중앙 +0.049` · `최대 +0.096 · 중앙 +0.019` · `최대 +0.202 · 중앙 +0.175 m`.
- **변형 비교(§10.5)** — [`sim_corner_1026d_summary.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026d_summary.txt):
  ```
  변형 | n | 안쪽 최대 평균 ± 표준편차 · 최악 (cm) | 95% 평균 | 중앙 평균 | 정지 합 s | 평균 속도 | 실패 | base 대비 평균 차 / 표준오차
  base    | 10 |   7.9 ±  5.2 ·  19.8 |   6.9 |   3.7 | 0.0 | 0.079 | 0 |  +0.0 / 2.3
  A28     | 10 |   6.1 ±  3.9 ·  15.7 |   5.0 |   2.3 | 0.0 | 0.079 | 0 |  -1.8 / 2.1
  A28Fw5  | 10 |   5.5 ±  2.1 ·  11.2 |   4.6 |   1.9 | 0.0 | 0.080 | 0 |  -2.4 / 1.8
  B2000   | 10 |   9.4 ±  2.2 ·  12.4 |   8.9 |   5.6 | 0.0 | 0.079 | 0 |  +1.6 / 1.8
  ```
  표준오차 계산([`anal_sim_corner_summary.py`](../debug_log/2026-10-26/jobs/anal_sim_corner_summary.py) 13 행): `se = np.sqrt(x.var(ddof=1) / len(x) + b.var(ddof=1) / len(b))` — 판정 '차가 표준오차보다 작으면 구분 불가' 는 §10.4 선언.
- **정지 장면(§10.7)** — [`sim_stall_1026_summary.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_stall_1026_summary.txt): `A14 | 10 | 0.0 · 0 · 0.0 | 0.076 | 0 | 0.97` · `A28 … 0.96` · `A28Fw5 … 0.97`.
- **통로(§15)** — [`anal_corridor_track.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_corridor_track.txt):
  ```
  f2rp4_B0_14x10 · 통로 안 347 틱 · |경로 이탈| 중앙 4.1 · 95 % 13.9 cm · 로버 중심 로컬 비용 중앙 71 · 95 % 80 · ≥ 99 비율 0 %
  f2sa3_28x5 · 통로 안 488 틱 · |경로 이탈| 중앙 1.0 · 95 % 10.4 cm · 로버 중심 로컬 비용 중앙 71 · 95 % 80 · ≥ 99 비율 0 %
  ```
  [`anal_band_run_f2sa3.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_band_run_f2sa3.txt) 3 · 4 행: `최소 정확 여유 0.8 cm · 16:12:15.7 · 자세 odom (-1.438, -4.672, -57.0°)` · `여유 구간 프레임: < 2.7 cm 7 · 2.7~4.4 10 · 4.4~6 36 · ≥ 6 707`.

### 4.4 채택 뒤 같은 구성(Smac · 28 · 5 · 재계획 0.01)의 기록
| 주행 | 코스 | 상자 복귀 실제 최소 | 통로 최소(로컬 정확) | 1 s 넘는 정지 | 비고 |
|---|---|---|---|---|---|
| f2sa3(10-26) | no5 | 13.2 | **0.8**(남행, NavFn 경로) | 5 · 15.3 s | Smac 통로 실패 5/5 |
| f2st1(10-27) | no5 | 16.3 | 4.1 남행 · 2.9 전체 | 1 · 4.7 s(상자 막힘 Wait) | tolerance 0.35 |
| f2tf1(10-27) | no5 | **−1.0(접촉)** | 3.8 | 1 · 5.1 s(TF 중단 Wait) | 상자 시야 밖 · 지도에 없음 |
| f2tt1(10-27) | no5 | 14.4 | 3.1 | 0 | timeout 1.5 |
| f2tt2(10-28) | no5 | 14.0 | 4.2 | 1 · 4.9 s(막힘 Wait) | |

수치 원문: [10-27 `anal_contact_f2st1_d30.txt`](../debug_log/2026-10-27/outputs/drives/f2st1/anal_contact_f2st1_d30.txt) 3 행 `최소 +0.163 m @ 11:25:15.63` · [`anal_contact_f2tt1_d30.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/anal_contact_f2tt1_d30.txt) 3 행 `+0.144 m` · [10-28 `anal_contact_f2tt2_d30.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/anal_contact_f2tt2_d30.txt) 3 행 `+0.140 m`. 통로 값은 각 `anal_band_run_*.txt`(위 §2 표 링크). **굽은 곳 이탈(odom)은 이 다섯 주행에서 재지 않았다.**

### 4.5 한계
- A/B 는 b910 에서 구성마다 2 회 · 같은 날. 상자 옆 '실제 여유' 는 SLAM 지도 위 차체 ↔ 기록 상자(수 cm SLAM 오차 포함).
- 굽은 곳 이탈 지표는 '경로가 ±0.5 m 에서 15° 넘게 휜 곳' 만 본다. 주행마다 Smac 경로 모양이 달라(재계획 시점 · 출발 자리) 같은 굽은 곳을 비교한 것은 아니다.
- 시뮬은 크기를 믿지 않는다([시뮬레이터 카드 §6](mppi-offline-simulator.md)) — 이번에도 실제 15.7 은 base 씨앗 분포의 위쪽 꼬리(10 개 중 2 개 ≥ 12).

### 4.6 지금 코드 영향(11-04 확인)
- **MPPI 28 · 5 는 계획기와 무관하게 늘 켜져 있다**: [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 281 · 285 행은 controller_server 의 FollowPathMPPI 하나에 걸린 값. 그런데 [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 203 행 `planner` 기본 `navfn` · [`prep_patrol.sh`](../tools/prep_patrol.sh) 17 행 `replan_hz:=${REPLAN_HZ:-0.5}` → **표준 prep 은 NavFn + 0.5 Hz + 28 · 5**. 28 · 5 로 달린 주행 7 번(f2sa1 · f2sa2 · f2sa3 · f2st1 · f2tf1 · f2tt1 · f2tt2)은 모두 `NAV_ADD="planner:=smac" REPLAN_HZ=0.01`(10-26 [`prep_smac_1026.sh`](../debug_log/2026-10-26/jobs/prep_smac_1026.sh) 3 행 · 10-27 `prep_smac_1027.sh` · 10-28 `prep_smac_1028.sh`)였다. NavFn 경로 + 28 은 10-23 f2pa2(PathFollow 10)의 5.5 s 정지 1 회와 f2sa3 통로 구간뿐 — **표준 prep 조합은 미시험**.
- B0 를 다시 띄우려면 태그 `navfn-baseline-20261023` 의 yaml(14 · 10) + `REPLAN_HZ=0.01` — 지금 작업 트리로는 B0 가 재현되지 않는다(MPPI 값이 다름).
- Smac 경로 점 간격: launch 123 행 `CopyPath … step="0.03"` 이 Smac 경로를 0.03 m 로 다시 찍는다(102 ~ 104 행 주석 '경로 크리틱 점 간격을 NavFn 판과 맞춤'). PathFollow `offset_from_furthest: 20` 점 ≈ 0.6 m(Smac) · NavFn 0.025 m 간격이면 ≈ 0.5 m.
- prep 의 파라미터 확인: [`chk_prep.py`](../tools/chk_prep.py) 33 행이 `FollowPathMPPI.PathAlignCritic.cost_weight` · `PathFollowCritic.cost_weight` 를 읽는다(10-27 §24).
- 펌웨어 바퀴 한계 0.085 · 비례 축소(위 §4.3)는 그대로 — v 0.08 로 달리며 회전을 조금만 섞어도 포화된다(계산: 0.08 + |ω| × 0.2215 > 0.085 ⇔ |ω| > 0.023 rad/s; 실측으로 v 가 0.055~0.061 로 깎인 것은 ω 명령 0.17~0.20 구간).

## 5. 내 실수 · 기록 어긋남
1. **시뮬 구동계를 '회전만 0.7 배' 로 둔 채 재현 판정**(10-26 §10.1 → §10.2) — 칸 형식 전문은 [시뮬레이터 카드 M2](mppi-offline-simulator.md). 요지: 09-17 의 회전 이득 측정을 형태(회전만 · 상수)까지 그대로 믿었다 · 다음에 알아보는 법: 구동계 손실을 넣기 전에 펌웨어 명령 경로(클램프 · 포화 · 데드밴드)를 코드로 보고 v 와 ω 손실이 같은 비율인지 잰다.
2. **§10.3 장면 시작을 이탈이 이미 9.3 cm 인 13:18:22 로 잡음** — 하려 한 것: 깎기를 줄이는 변형 고르기 · 본 것: 어느 변형도 '안쪽 최대' 가 9.6 cm 밑으로 안 내려감 · 처음 추론: 변형 효과 없음 · 의심한 이유: 최대값의 바닥이 시작 이탈과 같음 · 판별: §10.4 에서 재계획 직후(13:18:10, 이탈 ≈ 0)로 다시 · 결론: §10.3 의 '효과 없음' 은 지표 바닥 탓이 섞임(§10.5 에선 base 평균 7.9 · 변형 간 차 2.4 까지 보임) · 다음에 알아보는 법: '최대' 지표는 시작값이 0 근처인 장면에서만 쓴다 · 데이터 [`sim_corner_1026c.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026c.txt) → [`sim_corner_1026d.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026d.txt).
3. **요약 도구 첫 판이 병렬 출력이 한 줄에 섞인 판 1 개를 놓쳐 base n 9**(§10.5) — '라벨 s씨앗 \|' 경계로 나눠 고침([`anal_sim_corner_summary.py`](../debug_log/2026-10-26/jobs/anal_sim_corner_summary.py) 2 · 5 행). 첫 요약 출력은 덮어써 원천 소실. 다음에 알아보는 법: 요약 표의 n 을 선언한 씨앗 수와 대조한다.
4. **비교 그림 첫 판 점선 = 복귀 구간 시작 직전 경로**(§8) — B0 가 막힘 전 상자 관통 경로로 그려짐 → 최소 여유 순간의 경로로 고침([`fig_box_compare.py`](../debug_log/2026-10-26/jobs/fig_box_compare.py) 54 행 주석). ⚠ 같은 파일 머리말 5 행은 아직 '그 구간 시작 직전에 받은 BT 경로' 라 적혀 있다(아래 어긋남 4).
5. **영상 도구가 스무더 사건이 하나라도 있으면 Smac 경로 규칙을 건너뜀**(§12) — NavFn 대체가 한 번 있던 f2sa1 첫 영상에 Smac 경로가 빠짐 → 두 규칙 합침(도구 본체 해설은 [기록 · 도구 카드 쪽](record-conventions-evolution.md) 시기 범위 밖, 10-26 §12 원문).
6. **합본 영상 `-t` 위치 · `-shortest`**(§17.1) — 원본 220 s 를 잘라 시각화 끝 장면이 55 s 멈춤 → `-t` 를 입력 앞, hstack `shortest=1`. 다음에 알아보는 법: 자른 뒤 ffprobe 로 길이 · 장 수를 기대값과 대조(SUMMARY 칸 그대로).
7. **기록 어긋남**:
   1. **§11 선언 '시험 뒤 14 10 으로 되돌림'**([`up_mppi_path_1026.sh`](../debug_log/2026-10-26/jobs/up_mppi_path_1026.sh) 3 행 주석 '저장소 기본값은 그대로(시험 뒤 되돌림)') — 실제로는 되돌리지 않고 §14 에서 저장소에 채택(§11.2 '아직 28 · 5'). 선언과 다른 경로지만 사용자 결정으로 바뀐 것이라 결과 해석엔 영향 없음.
   2. **§16 '지도상 통로 폭은 같아 f2rp4 와의 비교는 유효'** — 치명 칸 사이(0.50 m)는 같지만 같은 출력의 y −4.7 줄은 다르다([`anal_corridor_gap.txt`](../debug_log/2026-10-26/outputs/drives/f2sa3/anal_corridor_gap.txt)): f2rp4 `99 미만 폭 -0.05 m · 가운데 칸 값 99` · f2sa3 `99 미만 폭 0.20 m · 가운데 칸 값 96`. 즉 **f2sa3 쪽이 그 단면에선 더 열려 있었는데도** 여유가 나빴다 — §15 의 '경로 · 추종 탓' 읽기를 약하게나마 지지하는 쪽이고, '두 날 같음' 은 치명 간격에 한정된 말.
   3. **§11.1 'Smac 재계획 성공(17.0 cm, 계기 미확인 — 막힘 로그 0)'** — 그 경로는 [`anal_plan_series_f2sa1.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/anal_plan_series_f2sa1.txt) `164.2 /plan 출발 ( 2.44, -1.43) · 여유 +17.0 cm`. bag 시작은 [`anal_contact_f2sa1_d30.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/anal_contact_f2sa1_d30.txt) 3 행 `15:14:40.72 … (t 190.1` 에서 15:11:30.6 → t 164.2 = 15:14:14.8. [`nav_events_ms_f2sa1.txt`](../debug_log/2026-10-26/outputs/drives/f2sa1/nav_events_ms_f2sa1.txt) 132 ~ 135 행 `15:14:14.64 … extrapolation into the future … Aborting handle` → `15:14:14.85 Received a goal` 와 0.2 s 안 — **계기는 TF 외삽 컨트롤러 중단으로 보임(시각 일치, 추정)**. 그 10 s 전 15:14:04.59 중단 뒤엔 새 /plan 이 없었다(재시도만) — 왜 한 번은 재계획 · 한 번은 재시도였는지는 미확인.
   4. **[`fig_box_compare.py`](../debug_log/2026-10-26/jobs/fig_box_compare.py) 머리말 5 행**('경로: 그 구간 시작 직전에 받은 BT 경로') 이 54 행에서 고친 동작('최소 여유 순간에 쓰이던 경로')과 다름 — 도구 설명이 낡음.
   5. **yaml 278 ~ 280 행 채택 근거 주석**은 f2sa1 · f2sa2 와 시뮬만 적고, 같은 날 바로 뒤 f2sa3 통로 0.8 cm · 정지 15.3 s(§15)는 적지 않았다 — 주석이 채택 순간의 근거라 틀린 것은 아니지만 반대 증거가 코드 옆에 없다.
   6. 출력 몇 개의 첫 줄이 깨진 UTF-16 WSL 경고 문구(`w s l : …localhostForwarding…`)다 — [`sim_corner_1026b.txt`](../debug_log/2026-10-26/outputs/mppi_sim/sim_corner_1026b.txt) 1 행 · [`up_mppi_path_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_mppi_path_1026.txt) 1 행 · [`up_params_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_params_1026.txt) 1 행. 수치 줄엔 영향 없음.
   7. 10-26 §10 '설정 대조' 의 'PathFollow offset 20 점(0.03 m 간격이면 ≈ 0.6 m)' 와 yaml 284 행 09-16 주석 'offset 5→20(0.5 m)' 은 점 간격(Smac 0.03 · NavFn 0.025) 차이 — 둘 다 맞음, 어느 경로 기준인지가 빠졌을 뿐.

## 6. 남은 것
- **깎는 기전**: 크리틱별 비용(PathAlign · PathFollow · Goal · Cost · PreferForward)을 최적 궤적 · 안쪽 궤적에서 나눠 본 적 없음 — 시뮬 출력에 크리틱 분해를 더하면 판별 가능.
- **표준 prep(NavFn · 0.5 Hz) + 28 · 5** 주행 기록 0. f2pa2 형 정지가 NavFn 경로에서 다시 나오는지 미확인.
- **NavFn 대체 경로 + 28 · 5 의 통로 손해**(f2sa3) — 1 회. tolerance 0.35 뒤엔 통로 남행이 Smac 경로라 같은 조건이 다시 안 생김. 북행은 여전히 Smac 실패 → NavFn 이 남아 있었다(f2st1; f2tf1 · f2tt1 은 북행도 Smac).
- 채택 뒤 굽은 곳 이탈(odom) 지표 재측정 없음 — no5 다섯 주행 상자 복귀 13.2~16.3 cm(접촉 1 은 상자 미관측)로 간접 확인뿐.
- 바퀴 포화(굽은 곳에서 v 0.08 → 0.055~0.061)는 그대로. 시뮬은 '깎기 주원인 아님' 이라 했지만 실제 영향(포화 중 MPPI 예측 ↔ 실제 곡률 어긋남)은 실주행으로 분리 안 함.
- PreferForward 15 · temperature 0.15 등 다른 크리틱이 28 · 5 아래에서 어떻게 작용하는지 미측정([회전 방식 카드](rotation-method-track-ratio.md) '이후').

## 7. 이후 (10-29 ~)
- 다음 시기 카드에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2sh1 · f2sh2(10-26) | Smac + MPPI 14 · 10, b910 — 깎기 +10.7 · +15.7 | `2026-10-26/outputs/drives/f2sh{1,2}/` · bag `bags/bag_f2sh{1,2}.tgz`(git 제외) |
| f2sa1 · f2sa2(10-26) | Smac + 28 · 5, b910 — +4.6 · +1.6 | `outputs/drives/f2sa{1,2}/` · bag `bags/bag_f2sa{1,2}.tgz` |
| f2sa3(10-26) | Smac + 28 · 5, no5 — 통로 0.8 cm | `outputs/drives/f2sa3/` · 사용자 촬영 `videos/20261026_160944.mp4`(2.7 GB, git 제외) |
| f2st1 · f2tf1 · f2tt1(10-27) · f2tt2(10-28) | 채택 뒤 같은 MPPI 값 | `2026-10-27/outputs/drives/<주행>/` · `2026-10-28/outputs/drives/f2tt2/` |
| 시뮬 sim_corner a~d · sim_stall | 굽은 곳 · 정지 장면 | `2026-10-26/outputs/mppi_sim/` · `jobs/run_sim_corner_1026{,b,c,d}.sh` · `run_sim_stall_1026.sh` |
| `chk_dev_frame_f2sh2.py` · `anal_bend_dev_odom.py` | odom 좌표 이탈 | `2026-10-26/jobs/` |
| `chk_cmd_vs_motion_f2sh2.py` | 명령 대 실제 움직임 | 같은 곳 |
| `anal_sim_corner_summary.py` | 시뮬 요약 · 표준오차 | 같은 곳 |
| `up_mppi_path_1026.sh` · `up_params_1026.sh` · `prep_smac_1026.sh` | 시험 배포 · 채택 배포 · prep | 같은 곳 → `outputs/setup/` |
| `fig_box_compare.py` · `chk_w3_turn.py` · `fig_real_tiles.py` | 비교 그림 · 돌아서기 · 촬영 장면 묶음 | 같은 곳 → `outputs/compare/` · `figures/compare/` · `figures/real_video/` |
| `anal_corridor_track.py` · `anal_corridor_gap.py` | 통로 추종 · 단면 폭 | 같은 곳 → `outputs/drives/f2sa3/` |
| `anal_dip_events.py`(10-21) | 멈칫 사건 | `2026-10-21/jobs/` → `2026-10-26/outputs/compare/anal_dip_events_*.txt` |
| `fig_f2st1_summary.py`(10-27) | f2rp4 · f2sa3 · f2st1 한 장 | `2026-10-27/jobs/` → `figures/f2st1_summary.png` |
| `Docs/tools/anal_mppi_sim.py` | 오프라인 MPPI(10-26 판) | 해설 [시뮬레이터 카드](mppi-offline-simulator.md) · 아래 §9 |
| `Docs/tools/fig_drive_video.py` · `fig_rviz_video.py` | 영상 | 이 시기 도구 변화는 10-26 §8 · §12 · §17, 10-27 §13 원문 |

## 9. 도구 해설
공통: PC(Git Bash · Python rosbags), 로버 안 움직임 — 단 `run_sim_*` · `up_*` · `prep_*` 는 Jetson(스크래치패드 러너 경유, bag 은 Jetson `/tmp/bag_<주행>` 로 풀어 둠). 시각은 KST.

### chk_dev_frame_f2sh2.py — 굽은 곳 이탈이 컨트롤러 탓인가 (10-26 §9)
- 부른 형태: `chk_dev_frame_f2sh2.py bag_f2sh2`(폴더).
- 왜: map 기준 이탈(+13~15.6 cm)은 SLAM 보정이 경로를 로버 밑에서 옮겨도 생긴다 — 컨트롤러가 실제로 본 좌표에서 다시 재려고.
- 하는 일: `/tf` 에서 map→odom · odom→base_link, `/transformed_global_plan`(컨트롤러가 그 틱에 쓴 odom 경로) — 0.5 s 마다 로버 ↔ 그 경로 최근접 선분 거리, 부호 = 상자(map (1.206, −0.11) 을 그 순간 map→odom 으로 odom 에 옮긴 점, 27 · 37 행) 쪽 +. map→odom 의 13:18:25 대비 변화(x · y · yaw)를 같은 줄에.
- 출력: [`chk_dev_frame_f2sh2.txt`](../debug_log/2026-10-26/outputs/drives/f2sh2/chk_dev_frame_f2sh2.txt) 27 줄(위 §4.3). 쓰인 곳: §9 '컨트롤러 탓'. 계보 → `anal_bend_dev_odom.py`(부호를 '굽은 곳 안쪽' 으로 일반화, 주행 공통). 이 판은 f2sh2 전용 — 다시 쓰려면 상자 좌표 · 시각을 고쳐야 함.

### anal_bend_dev_odom.py — 굽은 곳 안쪽 이탈(odom) (10-26 §11)
- 부른 형태: `anal_bend_dev_odom.py f2sh1=bag … f2sa1=bag`(이름=bag 여러 개).
- 하는 일: 0.2 s 마다 map 자세(map→odom ∘ odom→base_link)로 '복귀 상자 둘레'(map x 0.5~2.4 · y −0.8~0.8)의 **마지막 연속 구간**을 고르고, 그 시각 odom 로버 ↔ 최신 `/transformed_global_plan`(점 4 개 이상) 거리 — 최근접 점 앞뒤 0.5 m 경로 방향 변화가 15° 미만이면 nan(직선 제외), 넘으면 휘는 쪽 + (위 §4.2 발췌 18 ~ 19 행). 최대 · 95 % · 중앙 · 같은 창 map→odom 범위(ptp).
- 출력: 주행당 한 줄(위 §4.2). 쓰인 곳: §11 판정 ④ · yaml 278 행 근거 수치.
- 결함: '마지막 연속 구간' 은 구간 사이 1 s(5 표본) 넘는 끊김으로 가름 — 상자 둘레를 두 번 지나는 코스(no5 는 상자 둘레를 출발 · 복귀에만 지남)엔 맞지만 다른 코스엔 확인 필요. 경로 모양이 주행마다 달라 같은 굽은 곳 비교가 아님(§4.5). `/transformed_global_plan` 은 MPPI 시각화를 켠 구성에서만 발행된다(launch 130 행 10-07 §11 주석, 표준 prep 은 `lite`). 지금 다시 쓸 수 있음.

### chk_cmd_vs_motion_f2sh2.py — 명령 대 실제 움직임 (10-26 §10.2)
- 부른 형태: `chk_cmd_vs_motion_f2sh2.py bag_f2sh2`.
- 왜: 시뮬(이상 차동구동 + 회전 이득 0.7)은 이탈을 바로잡는데 실제는 키움 → 명령한 v · ω 가 실제로 나왔나.
- 하는 일: 13:18:22~38 0.5 s 평균 — `/cmd_vel`(v · ω) · `/wheel_odom` · `/odometry/filtered`(v · vy · ω) · `/vslam/odom` · `/imu/data` 자이로(`/tf_static` 으로 base_link 축) · ω 실제/명령 비(명령 |ω| 작으면 '-').
- 출력: 위 §4.3 발췌. 쓰인 곳: §10.2 구동계 정정 — 휠 · 자이로 · cuVSLAM 세 독립 원천이 같은 v · ω 를 보여 '센서 오차' 가 아니라 실제 움직임임을 받침. f2sh2 전용 시각.

### Docs/tools/anal_mppi_sim.py — 10-26 판에서 더한 것 (Jetson, 411 행)
- 부른 형태(§10.4, [`run_sim_corner_1026d.sh`](../debug_log/2026-10-26/jobs/run_sim_corner_1026d.sh) 4 ~ 6 행): `python3 /tmp/anal_mppi_sim.py /tmp/bag_f2sh2 0 label=<변형> t_abs=1792988290.0 <COM> seed=<1~10> <변형 인자>`, COM = `vx_std=0.08 wz_std=0.4 follow_w=10 follow_off=20 goal_w=10 … iters=2 cycles=260 … humble=1 temperature=0.15 … fwd_w=15 vx_min=-0.06 fpchk=1 resample=0.03 w_gain=1.0 wheel_max=0.085`, `xargs -P 4` 로 4 판 병렬. 정지 장면(§10.6)은 `path_topic=smoothed`(NavFn 판 BT 경로 = `/plan_smoothed`, 75 행).
- 10-26 추가: ① `resample=s`(117 ~ 123 행) — 경로를 호 길이 s 간격으로 다시 찍음. 이유: 경로 크리틱 offset 이 **점 개수**라 실주행 CopyPath step 0.03 과 같게 해야 함 ② `wheel_max`(362 ~ 365 행) — 펌웨어 비례 축소 ③ 매 주기 `dev_inside`(125 행~, '굽은 곳 안쪽 +', ±0.5 m 15° 미만 nan — `anal_bend_dev_odom.py` 와 같은 정의) · 1 s 넘는 정지 · '첫 굽은 곳 이탈' · '굽은 곳 95 %' 출력(387 ~ 388 행).
- 출력 줄 형태: `굽은 곳 경로 이탈(안쪽 +): 최대 +0.096 · 중앙 +0.025 m (굽은 곳 주기 160/160) · 1 s 넘는 정지 0.0 s · 평균 속도 0.079 m/s · resample 0.03` + `후보 전부 충돌(실패) 주기 0 회` + `ESS 중앙 21.7`.
- 쓰인 곳 · 한계: §10 전부. 경로 · 코스트맵은 bag 재생(재계획은 bag 의 /plan 을 따라 바뀜, 계획기를 돌리지 않음). f2pa2 정지를 재현 못 함(§10.7) — 목표 자세 · warm start 차이 후보. 크기는 믿지 않는다. 계보 · 앞판은 [시뮬레이터 카드 §4.7](mppi-offline-simulator.md).

### run_sim_corner_1026{,b,c,d}.sh · run_sim_stall_1026.sh · anal_sim_corner_summary.py — 시뮬 묶음 (Jetson · PC)
- a(§10.1): 13:18:22(`TA=1792988302.0`) · 16 s · `w_gain=0.7` · 9 변형 × 씨앗 1 → `sim_corner_1026.txt`. b(§10.2): 같은 장면에 `W07_old` · `SAT`(wheel_max) 씨앗 1~3 → `_b.txt`. c(§10.3): SAT 구동계 · 7 변형 × 씨앗 6 → `_c.txt` · `_c_summary.txt`. d(§10.4): 13:18:10 · 26 s · 7 변형 × 씨앗 10 · 4 병렬 → `_d.txt`. stall(§10.6): f2pa2 t 94 · 16 s · 3 변형 × 10.
- `anal_sim_corner_summary.py 원문 출력`(PC): 정규식으로 '라벨 s씨앗 \|' 경계를 나눠(병렬 출력이 한 줄에 섞임) 판마다 최대 · 중앙 · 정지 · 속도 · 첫 이탈 · 95 % · 실패를 모아 변형별 평균 ± 표준편차 · 최악 · base 대비 차 / 표준오차(Welch 형 합성).
- 결함: c 판의 요약(`_c_summary.txt`)은 표준오차 열이 없다(d 판부터). 각 sh 는 Jetson `/tmp` 에 bag · 시뮬이 있어야 함(재부팅으로 지워짐).

### up_mppi_path_1026.sh · up_params_1026.sh — 배포 (Jetson, 로버 안 움직임)
- `up_mppi_path_1026.sh [A=28.0] [F=5.0]`: Jetson `~/ros2_ws/{src,install}` 아래 `nav2_params.yaml` 을 찾아 **링크면 건너뛰고** 일반 파일이면 정규식으로 PathAlign · PathFollow `cost_weight` 숫자만 바꿈 · 결과 값과 '바뀜/같음'. 실행 중 값은 안 바꿈. 출력 [`up_mppi_path_1026.txt`](../debug_log/2026-10-26/outputs/setup/up_mppi_path_1026.txt) — src · 설치본 둘 다 '바뀜'(= 설치본이 일반 파일이었다는 뜻).
- `up_params_1026.sh`: 저장소 yaml(base64 로 실어 보낸 `/tmp/up_nav2_params.yaml`)을 src 에 복사, 설치본이 링크가 아니면 설치본에도 복사, 전후 sha256 앞 12 자 · 링크 여부 · 두 크리틱 값 grep. 출력 위 §4.1. ⚠ 설치본 '일반파일' 은 10-15 §30 `sed -i` 흔적으로, 11-04 §1 에서 링크로 복구됐다([빠른 prep 카드](prep-fast-startup.md)).

### fig_box_compare.py — B0 대 Smac 상자 옆 (10-26 §8 · §12)
- 부른 형태: `fig_box_compare.py 출력.png 이름=bag …`(B0 3 · Smac 2 또는 4). 데이터: 각 bag `/tf` · `/plan` · `/plan_smoothed`. 복귀 구간 = 상자 둘레(x 0.5~2.3 · y −0.6~0.8)에 들어온 마지막 덩어리. 경로 = 최소 여유 순간 이전 마지막 BT 경로 — B0 는 `/plan_smoothed`(없으면 `/plan` 중 점 간격 ≤ 0.04), Smac 은 `/plan` 중 점 간격 > 0.04(러너 조회 NavFn 0.025 제외). 여유 = 차체 사각형(16 행 `FP`) ↔ 기록 상자(16 행 `BOX = (1.151, 1.261, -0.20, -0.02)`) 최소 거리.
- 출력: 그림 + 한 줄 기록(`B0 f2rp1 15.2 cm · …` / `Smac f2sh1 18.4 cm · f2sh2 10.8 cm · f2sa1 14.6 cm · f2sa2 14.9 cm`). 결함: 머리말 5 행 낡음(§5 어긋남 4). 지금 다시 쓸 수 있음.

### anal_dip_events.py(10-21) · chk_w3_turn.py — 멈칫 (10-26 §13)
- `anal_dip_events.py bag nav_events.txt`: 전진 명령이 < 0.01 로 떨어진 묶음마다 '명령 0 근처 n 개 · 길이' 와 앞 2 s ~ 뒤 0.5 s nav2 사건(해설은 [B0 카드 §9](path-tracking-replan-b0.md)). 출력 `outputs/compare/anal_dip_events_f2*.txt` — 머리 줄 `== 멈칫 15:35:34.01 (명령 0 근처 42 개 · 2.35 s)` 처럼.
- `chk_w3_turn.py bag 시작 끝`: 그 창 0.5 s 마다 명령 v · ω 와 실제(EKF) v · ω — '전진 0' 이 정지인지 제자리 돌아서기인지. 출력 [`chk_w3_turn.txt`](../debug_log/2026-10-26/outputs/compare/chk_w3_turn.txt) 예 `15:35:33.5 명령 v -0.014 ω -0.334 | 실제 v -0.019 ω -0.355`.

### anal_corridor_track.py · anal_corridor_gap.py — 서쪽 통로 (10-26 §15 · §16)
- `anal_corridor_track.py 이름=bag …`: 통로 상자(map x −2.3~−0.9 · y −5.7~−3.4) 안 틱마다 로버 ↔ `/transformed_global_plan` |이탈| 과 로버 자리 로컬 코스트맵 값 → 중앙 · 95 % · ≥ 99 비율(40 행 출력). 왜: '28 이 NavFn 경로를 바짝 따라 여유를 잃었나' 가설. 결함: 방향 없는 거리 · 지도 · 물건 배치가 다른 두 날 비교.
- `anal_corridor_gap.py 이름=bag=HH:MM:SS …`: 남행 직전 전역 코스트맵에서 y −4.4 ~ −5.0(0.1 m) 단면마다 치명 칸 사이 · 99 미만 폭 · 가운데 칸 값. 출력 위 §5 어긋남 2. 결함: x 방향 단면만(통로가 비스듬하면 폭을 넓게 잼).

### fig_real_tiles.py — 촬영 장면 묶음 (10-26 §16)
- `fig_real_tiles.py 작업본.mp4 작업본시작 출력.png 열수 HH:MM:SS.s=설명 …`: ffmpeg 로 지정 시각 장면을 뽑아 시각 글씨를 붙인 격자 한 장(토큰 절약 — 6 장 = 그림 1 장). 출력 [`corridor_a.png`](../debug_log/2026-10-26/figures/real_video/corridor_a.png) 등. 영상 시각 맞춤은 파일 이름 · 생성 시각으로 ±1 s 추정(프레임 대조 안 함).

### fig_f2st1_summary.py — 10-27 §12 요약 그림 (PC)
- 값은 손으로 옮김(머리말 3 ~ 5 행에 원문 위치) — 목표별 시간 · 통로 · 정지 · 상자 지표. 출력 [`f2st1_summary.png`](../debug_log/2026-10-27/figures/f2st1_summary.png). 결함: 값 복사본이라 원문이 바뀌면 그림이 낡음.

## 10. 용어
- **굽은 곳 안쪽 깎기(이탈)**: MPPI 가 굽은 경로의 안쪽(경로가 휘는 쪽)으로 질러가는 것. 이 카드의 지표는 컨트롤러 좌표(odom)에서 로버 ↔ 컨트롤러가 그 틱에 쓴 경로 거리, 경로가 ±0.5 m 에서 15° 넘게 휘는 곳만, 휘는 쪽 +.
- **PathAlignCritic · PathFollowCritic(Humble 1.1.20)**: PathAlign = 후보 궤적 점들이 경로에서 떨어진 평균 거리 벌점(경로에 붙임, `offset_from_furthest 3`). PathFollow = 궤적 끝점과 '가장 멀리 도달한 경로점 + offset(20 점)' 사이 거리 벌점(앞으로 당김) — 굽은 곳에선 그 점으로 가는 지름길이 안쪽이라 깎기를 부를 수 있다(10-26 §10 추정).
- **바퀴 포화 · 비례 축소**: 펌웨어가 v 를 ±0.085 로 자른 뒤, 한쪽 바퀴(v ± ω × 0.2215)가 0.085 를 넘으면 두 바퀴를 같은 비율로 줄인다 — 곡률(ω/v)은 유지, 속도만 준다. 예전 시뮬의 '회전만 0.7 배' 는 곡률을 바꾸는 다른 모형.
- **씨앗 · 표준오차 · '구분 불가'**: 시뮬 결과가 잡음 씨앗마다 크게 흔들려(ESS 10~20), 변형 간 평균 차를 √(분산/n) 합성 표준오차와 견줘 그보다 작으면 효과를 말하지 않는다(10-26 §10.4 선언).
- **warm start**: MPPI 가 직전 주기의 최적 제어열을 한 칸 밀어 다음 주기 출발점으로 쓰는 것 — 시뮬과 실제의 정지 재현 차이 후보(§10.7, 미확인).
- **NavFn 대체(PlanSmacOrNavFn)**: `planner:=smac` 일 때 BT 가 Smac Hybrid 를 먼저 부르고 실패하면 NavFn + SimpleSmoother(실패 시 원경로)로 넘어가는 분기(launch 115 ~ 125 행) — 그래서 한 주행 안에서 MPPI 가 두 종류 경로를 따른다.
