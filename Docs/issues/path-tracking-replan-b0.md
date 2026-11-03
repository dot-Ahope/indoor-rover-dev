# 상자 옆 근접은 '경로 추종 · 재계획' 문제 — B0(NavFn 결함 기준선) · Phase P 착수 (8 기: 10-22 §16 · §18(배경) · §22, 10-23 §0~§15 · §17~§19 · §20.1 · §20.8~§24)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **조사 중(기전 일부 측정 · B0 결함 기준선 고정)** — 상자 옆 근접의 몫을 '계획 경로 여유(NavFn 9~16 cm) − 로버 자리 재계획 톱니 누적 − MPPI 굽은 곳 안쪽 깎기(+7~11 cm)' 로 나눠 재고, 그 상태를 **B0 = 태그 `navfn-baseline-20261023`**(커밋 `9ce20486`) 로 고정했다. 해결 아님: B0 의 b910 상자 옆 실제 여유는 15.2(1 s 표본 15.4) · 5.5 · 3.1 cm. 10-23 의 Smac 오프라인 첫 비교는 **10-26 §6.1 에서 무효**(도구 결함, 아래 §5). 이후 10-26 PathAlign 28 · PathFollow 5 채택 · 10-27 `planner:=smac`(시험 인자, 기본 아님) | 10-22 §16(f2pi1 1.1 cm · 멈칫) ~ 10-23 §24 | [10-22 §22](../debug_log/2026-10-22/SUMMARY.md) 사용자 "자홍칸이 적더라도 주황칸보다 노랑칸을 더 추종하게 한다면 상자를 치고 가지 않았을 것" | 10-23 주행 중엔 저장소 코드 변경 없음(PathAlign 28 은 Jetson yaml 만 · 되돌림 — [`up_palign_1023.sh`](../debug_log/2026-10-23/jobs/up_palign_1023.sh)). 운용 기본 변경: [`Docs/tools/prep_patrol.sh`](../tools/prep_patrol.sh) `REPLAN_HZ` 환경 변수(기본 0.5, §16 커밋 `dcfdb0b6`) · `ODOM=vslam` 기본. 막힘 판정 [`path_blocked_ahead_condition.cpp`](../../ros2_ws/src/rover_navigation/src/path_blocked_ahead_condition.cpp) `only_new`(→ [PathBlockedAhead 카드](pathblocked-only-new.md)). 새 도구 묶음 [`Docs/tools/plan_offline/`](../tools/plan_offline/) · 계획서 [`SMAC_HYBRID_PLAN.md`](../06_planner/SMAC_HYBRID_PLAN.md) | [PathBlockedAhead 99/100 · only_new](pathblocked-only-new.md)(같은 날 B0 확정 조건) · [상자 옆 정지 — 기전](box-side-stall-cause.md)(10-13 · 10-15 의 '정지'; 여기는 '닿을 듯 지나감') · [상자 옆 정지 — 대책](box-side-stall-remedies.md)(ClearanceBandCritic · 전역 감쇠 3.0 · cost_weight 3 배 — 10-23 §13 표가 다시 씀) · [상자 과장 · 기억 밀림](box-exaggeration-source.md)(10-22 §16 · §17 '기억 3 cm 남쪽' · 1.1 vs 5.6 cm 영상) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md)(10-23 §9~§11 · §16 — 상자 옆은 못 풂) · [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md)(이 시기 구성: 프리셋 3 · 통합 2.0) · [전역 계획기 NavFn vs Smac](global-planner-choice.md)(Phase P 의 앞 이야기) · [MPPI 상자 옆 통로 튜닝](mppi-passage-tuning.md)(PathAlign · PathFollow offset 의 출처) · [F2 기준선 no5](f2-baseline-no5.md)(no5 · b910 코스, 앞 기준선 3/6) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(재계획 0.5 Hz 를 들인 10-08 결정) · [W3 떨림 · TF 지연](tf-lag-w3-wobble.md)(멈칫 A TF 외삽) · [CPU 부하](cpu-load-stalls.md)(10-22 §18 노드별) · [nav_guard](onboard-stop-nav-guard.md)(10-22 §18 · §20) · [BT 끝 방향 CopyPath](bt-copypath-end-yaw.md)(BT 경로의 절반이 원경로 — §20.7) · [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md)(10-26 §10 깎기 모의) · [주행 운영 10-19 ~ 10-23](drive-ops-1019-1023.md)(영상 도구 · prep 재전송) |

**한 줄**: 10-22 f2pi1 복귀에서 로버가 출발점 낮은 상자 옆을 실제 여유 **1.1 cm** 로 지나갔다. 사용자 제안('노랑 쪽을 따르게')을 계산해 보니 전역 감쇠로는 경로가 0~5 cm 만 멀어졌고(10-23 §1.1), 기록된 전역 경로는 이미 상자에서 11~16 cm 였다(§4) — 붙은 것은 **로버**였다. 한 경로(2 s) 동안 추종 오차는 상자 둘레 3~5 cm 로 작지만, 0.5 Hz 재계획이 매번 **로버 자리에서** 경로를 새로 시작해 작은 안쪽 치우침이 톱니처럼 쌓였다(§14, 사용자 판단 "추종 문제지 인식 문제가 아니다"). 재계획을 끄자(0.01 Hz + 막힘 때만) 상자 쪽 치우침이 0 이 되고 15.4 cm(f2rp1)가 나왔지만, 반복에선 경로 자체가 상자에 가깝게 다시 그려지거나(f2rp2 5.5 cm) 굽은 곳 안쪽을 깎아(f2rp5 3.1 cm) 선언 기준 '≥ 8 cm' 를 못 넘었다. 사용자 결정으로 이 상태를 **B0 = NavFn 결함 기준선**으로 확정하고 Phase P(Smac Hybrid) 를 시작했다. 같은 날 오프라인 첫 비교는 'Smac 기준 미달' 이었으나 그 Smac 변형 간 비교는 10-26 에 도구 결함(같은 서버에 여러 Smac 을 올리면 설정을 공유)으로 무효 처리됐다.

## 1. 증상
- **10-22 §16 · §17 f2pi1**(b910, 프리셋 3 + 통합 2.0): 3/3 성공, 그러나 복귀 상자 옆 실제 여유 최소 **+0.012 m** @ t 210.1 s 로버 (0.99, 0.14, −173°)(`anal_contact_f2pi1.txt`) — '1.2 cm 는 SLAM 오차 범위, 닿았는지 미확인'. 그 순간 로컬 코스트맵 치명 칸까지는 5.6 cm(§17 영상) — 상자 기억이 실제보다 약 3 cm 남쪽(→ [상자 과장 · 기억 밀림 카드](box-exaggeration-source.md)).
- 같은 주행에서 사용자 요청 "주행 중 멈칫멈칫하는 현상 분석"(§16) — 0.5 s 넘는 정지 0, 짧은 멈칫 14 번(아래 §2 표의 A · B · C).
- **10-22 §22** 사용자 제안(영상 t 210 s 장면): 경로가 상자 쪽 주황(높은 팽창 비용) 띠 가장자리를 따라감 → 노랑(낮은 비용) 쪽을 따르게 하면 상자 칸이 적어도 안 쳤을 것.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-22 §16 | f2pi1 멈칫 분해(0.01 s nav2 사건 ↔ 명령 바닥) | 짧은 멈칫 14 = **A TF 외삽 5**(`Lookup would require extrapolation into the future` → `follow_path Aborting` → 0.02~0.26 s 뒤 재수신) · **B 제어 주기 늦음 5**(`Control loop missed` 와 명령 바닥이 0.01~0.11 s 안, 5/5) · **C 목표 바뀜 4**(정상). 주기 늦음 · TF 외삽(prep 이후 로그 전체) f2pr1 60 · 37, f2pi1 72 · 36, f2lp1 72 · 63. CPU 평균 76 % | A · B 모두 '시간이 늦다'(CPU 바쁨일 수 있음 — 추정). 10-21 §12.2 와 같은 서명, 새 문제 아님. B 의 기전(velocity_smoother `velocity_timeout 0.3 s` → 0 으로 감속)은 추정 — 컨트롤러 출력 토픽이 bag 에 없음 | [`anal_stops_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_stops_f2pi1.txt) · [`anal_dip_events_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_dip_events_f2pi1.txt) · [`nav_events_ms_f2pi1.txt`](../debug_log/2026-10-22/outputs/nav_events_ms_f2pi1.txt) · [`anal_hesitation_counts.txt`](../debug_log/2026-10-22/outputs/anal_hesitation_counts.txt) · [`anal_cpu_f2pi1_cmp.txt`](../debug_log/2026-10-22/outputs/anal_cpu_f2pi1_cmp.txt) |
| 10-22 §18 | CPU 노드별(멈칫 A · B 배경) | Nav2 ≈ 100 %(controller 28.0) · bag 기록기 · 러너 ≈ 60 · nav_guard 24.8 · 합 401 %(600 중) | 배경 기록 — 본체는 [CPU 카드](cpu-load-stalls.md) · [nav_guard 카드](onboard-stop-nav-guard.md) | [`anal_cpu_nodes_f2pi1.txt`](../debug_log/2026-10-22/outputs/anal_cpu_nodes_f2pi1.txt) |
| 10-22 §22 | 사용자 제안 기록 | 10-13 시험 ① 전역 감쇠 2 → 3(계산 +5 cm, 주행 f2p1 효과 미확인 → 되돌림) ② CostCritic 3 배(머뭇거림 → 되돌림) | 통합 2.0 으로 상자가 37~50 s 전부터 지도에 있으니 ① 이 효과를 낼 조건 — 계산은 다음 날 | SUMMARY §22 |
| 10-23 §1 · §1.1 | **선언 → 계산**: 기록 전역 코스트맵 치명 칸에서 inflation 재계산(k 2 · 3 · 4 · 5) + 8 방향 Dijkstra(계획기 흉내). 판정 '≥ 5 cm 늘고 길이 +10 % 이내' | 경로 ↔ 실제 상자 여유: k 2 → 3 에서 0~5 cm, 4 · 5 는 더 안 늚. 기록된 /plan 자체가 +10~14 cm(f2pi1 t 203 만 +4.3). 길이 +2~7 % | **선언 기준 미달** — 단독 대책 아님 | [`anal_ginfl_path_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_ginfl_path_f2pi1.txt) · [`_f2sm3.txt`](../debug_log/2026-10-23/outputs/anal_ginfl_path_f2sm3.txt) |
| 10-23 §2 | 계획 경로 대 실제 길 | 첫 실행(최신 경로 대비) ±1~4 cm → **지표 오류 의심**(경로가 로버 자리에서 다시 그려짐) → 상자 앞 경로 고정(FREEZE): t 198 경로 대비 로버가 t 210 에 **+15.7 cm** 상자 쪽. f2sm3 은 −2~+3 cm | 1.1 cm 는 '계획기가 붙인 것이 아니라 MPPI 가 질러간 것'(측정 + 추론). 손잡이는 MPPI 쪽 — 후보 PathAlign 꺼짐 · 가중 · 로컬 inflation · cuVSLAM | [`anal_track_dev_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2pi1.txt) · [`anal_track_dev_f2pi1_freeze.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2pi1_freeze.txt) · [`anal_track_dev_f2sm3.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2sm3.txt) |
| 10-23 §3 | 가설 1 'PathAlign 이 상자 옆에서 꺼졌다' | f2pi1 · f2sm3 t 196~214 s 19 시각 모두 내접 · 치명 점 0 → 꺼짐 0 | **기각** | [`anal_pathalign_occ_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_pathalign_occ_f2pi1.txt) · [`_f2sm3.txt`](../debug_log/2026-10-23/outputs/anal_pathalign_occ_f2sm3.txt) |
| 10-23 §4 | 다시 그려진 경로마다 여유(출발 0.3 m 밖 점만) | 경로 +11~16 cm(f2pi1) · +12~15(f2sm3) — 비슷. 차이는 로버 자리: 상자 옆 로버 y f2pi1 0.14~0.19 · f2sm3 0.19~0.24, 경로 선 y ≈ 0.26~0.28 → **상자 쪽 8~12 · 3~5 cm** | '곡선 안쪽 질러가기 + 다시 그리기 고정'(추정). §2 의 '최신 경로 여유' 칸도 출발점을 포함한 지표 오류였음(정정) | [`anal_plan_series_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_plan_series_f2pi1.txt) · [`_f2sm3.txt`](../debug_log/2026-10-23/outputs/anal_plan_series_f2sm3.txt) |
| 10-23 §5 · §5.1 · §5.2 | **f2pa1**: PathAlign 14 → 28(Jetson yaml 만) | 상자 쪽 1~5 cm ✔ · 실제 최소 **12.3 cm** ✔ · 멈칫 12 · 0.5 s 정지 1(0.8 s, W3 길) · 시간 +1~3 %. 출발 전 Jetson 밤사이 재부팅 → prep 재전송 | '해 없음 + 좋은 방향'(1 회, f2sm3 도 통과 범위) | [`run_f2pa1.txt`](../debug_log/2026-10-23/outputs/run_f2pa1.txt) · [`anal_plan_series_f2pa1.txt`](../debug_log/2026-10-23/outputs/anal_plan_series_f2pa1.txt) · [`anal_contact_f2pa1.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2pa1.txt) · [`anal_stops_f2pa1.txt`](../debug_log/2026-10-23/outputs/anal_stops_f2pa1.txt) · [`chk_day_start_1023.txt`](../debug_log/2026-10-23/outputs/chk_day_start_1023.txt) |
| 10-23 §6 · §6.1 | **f2pa2** 반복(같은 구성) | 상자 쪽 **6~8 cm ✘** · 실제 **6.7 cm ✘**. t 196 s 이미 f2pa1 보다 10 cm 남쪽. **5.5 s 거의 정지**(t 97~102.5, (4.72, −1.92) W3 가는 길) — nav2 사건 0 · 앞 라이다 1.06 m | **채택 보류**(선언대로). 정지 원인 미확인 | [`run_f2pa2.txt`](../debug_log/2026-10-23/outputs/run_f2pa2.txt) · [`anal_plan_series_f2pa2.txt`](../debug_log/2026-10-23/outputs/anal_plan_series_f2pa2.txt) · [`anal_contact_f2pa2.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2pa2.txt) · [`anal_stops_f2pa2.txt`](../debug_log/2026-10-23/outputs/anal_stops_f2pa2.txt) |
| 10-23 §6.2 | 사용자 "가중치를 올려서 이유 없는 정지가 있었다고 보는가?" | 가중 14 주행의 긴 정지(f2pr1 4.9 · f2sm3 1.1 · f2sm2h 5.1 s)는 모두 명령 발행이 끊긴 것(복구 Wait 등). f2pa2 는 명령 109 개 중 90 개 ≈ 0 = **MPPI 가 스스로 0 을 고름**. 앞 ±60° 1.2 m 안 점 수 0 → 141 뒤 141~145 고정 | **근거 없음**(28 은 후보 중 하나). 지나가는 사람 모양 아님, 서 있는 사람은 배제 못 함 | [`chk_scan_window_f2pa2.txt`](../debug_log/2026-10-23/outputs/chk_scan_window_f2pa2.txt) |
| 10-23 §7 · §8 | 정지 bag 분석 · 그림 | 컨트롤러는 계속 계산(/trajectories 110 개 ≈ 10 Hz). 최적 궤적 첫 4 단계 0.001~0.03 → 5 단계째부터 0.05~0.08 m/s('0.4 s 뒤 출발' 해 5 s 반복). t 99.76 s 새 경로로 0.3 m 앞 경로 방향 −4° → **−43°**, 목표 W3 0.85 m · 방위 **+14°** → 엇갈림 **57°**. 가중 14 주행 같은 자리 30~37°, f2pa1 약 20° — 멈춤 없음. 그림: 경로가 로버 뒤에서 시작해 목표 아래로 내려갔다 올라오는 U 자 | 경로 크리틱과 목표 크리틱이 크게 엇갈린 자리에서 '천천히 출발' 해에 갇힘(기전 일부 추정). 28 은 **가능한 증폭 요인** — 단정 못 함. 되돌리는 쪽 제안 | [`chk_ctrl_gap_f2pa2.txt`](../debug_log/2026-10-23/outputs/chk_ctrl_gap_f2pa2.txt) · [`chk_opt_traj_f2pa2.txt`](../debug_log/2026-10-23/outputs/chk_opt_traj_f2pa2.txt) · [`anal_mppi_stop_f2pa2.txt`](../debug_log/2026-10-23/outputs/anal_mppi_stop_f2pa2.txt) · [`anal_mppi_stop_cmp.txt`](../debug_log/2026-10-23/outputs/anal_mppi_stop_cmp.txt) · 그림 [`mppi_stop_f2pa2.png`](../debug_log/2026-10-23/figures/mppi_stop_f2pa2.png) |
| 10-23 §9 · §10 | 다음 선택 → PathAlign 14 복귀 + `vslam:=on` 시험(사용자 "14로 되돌리고 vslam on") | — | 하나씩 바꿈(원인 분리). cuVSLAM 쪽 판정은 [cuVSLAM 카드](cuvslam-velocity-fusion.md) | [`up_palign_1023_revert.txt`](../debug_log/2026-10-23/outputs/up_palign_1023_revert.txt) |
| 10-23 §10.1 · §11.1(상자 옆만) | f2von1 · f2von2(주 EKF = cuVSLAM) | 상자 옆 실제 **3.3 · 0.3 cm**, 경로 선보다 상자 쪽 6~8 · 5~9 cm. 172 s 기억 y 밀림 3.5~4.8 · **0.8~1.8 cm**(f2pr1 4~5) | 오도메트리는 좋아졌는데 근접은 그대로 → **근접의 주된 몫은 'MPPI 가 경로 선 남쪽을 달리는 것'**(f2pi1 · f2pa2 · f2von1 · 2 모두 5~12 cm, f2sm3 · f2pa1 만 1~5). vslam on 이 키웠는지는 미확인 | [`anal_contact_f2von1.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2von1.txt) · [`anal_contact_f2von2.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2von2.txt) · [`anal_plan_series_f2von2.txt`](../debug_log/2026-10-23/outputs/anal_plan_series_f2von2.txt) · [`anal_memory_shift_f2von2.txt`](../debug_log/2026-10-23/outputs/anal_memory_shift_f2von2.txt) |
| 10-23 §12 | f2von2 상자 옆 영상 | 들어올 때 최적 궤적 y ≈ 0.17~0.19 로 곧게 — 단면 비용(x 1.2) 로버 칸 85~91 · 경로 선 ≈ 70 · 통로 가운데 58~61 = **북쪽이 낮은데도** 안 올라감. 빠져나갈 때 t 200 s 부터 궤적 끝이 +13~17° 로 일찍 꺾여 t 202.0 s **0.5 cm**. GoalCritic 은 t 202.0 에야 켜짐 | ① 옆 10 cm 를 고치는 힘(경로 · 비용 크리틱)이 약함 ② 다음 꺾임 안쪽을 일찍 질러감 — 둘 다 '경로 곡선 안쪽에 상자' 모양(추정 포함) | `videos/f2von2_return_box.mp4`(git 제외) · [`fig_return_video2_f2von2.txt`](../debug_log/2026-10-23/outputs/fig_return_video2_f2von2.txt) · [`anal_cost_section_f2von2.txt`](../debug_log/2026-10-23/outputs/anal_cost_section_f2von2.txt) · [`anal_mppi_goal_f2von2.txt`](../debug_log/2026-10-23/outputs/anal_mppi_goal_f2von2.txt) |
| 10-23 §13 | 대책 추천 | 1 순위 ClearanceBandCritic 2 판(거리장), PathAlign ↑ 보류, 전역 감쇠 기각 쪽, 계획기 교체 '나중', CostCritic ↑ 기각 | — ⚠ **§14 에서 철회**(사용자) | SUMMARY §13 |
| 10-23 §14 | 사용자 판단 "planner 경로를 controller 가 추종 못하는 것, 장애물 인식이 아니다" → 경로마다 추종 오차 | 한 경로(2 s) 동안 상자 둘레 95 % **3.0~4.1 cm**(6 주행), 굽은 구간 95 % 8~9.6(14) 대 **5.0~5.3(28)**. 첫 판은 모든 주행 중앙 8.8 cm(인공물) | **기전: 2 s 마다 로버 자리에서 다시 그려 1~4 cm 치우침이 새 출발점이 되어 쌓임(톱니, 추정)**. 28 은 추종 자체는 개선. 손잡이 = 다시 그리기 | [`anal_track_err.txt`](../debug_log/2026-10-23/outputs/anal_track_err.txt) |
| 10-23 §15 | 사용자 "직사각 로버니 Smac Hybrid … NavFn 에 추가한 것 검토" | 계획기 단 7 개(전역 inflation 0.70/2.0 · SmoothPath · CopyPath · 패딩 0.01 · 러너 경로 끝 yaw · yaw 허용 0.35 · 재계획 정책) · 컨트롤러 단(PathAlign offset 3 · PathFollow 20 등). 09-15 Smac 되돌린 이유 = 출발 차체 충돌 'no valid path' 15 회 | 다시 바꿀 때 걸리는 점 목록 → 계획서 P1~P7 | SUMMARY §15 · [`SMAC_HYBRID_PLAN.md`](../06_planner/SMAC_HYBRID_PLAN.md) §3 |
| 10-23 §16 | `vslam:=on` 운용 기본(prep) | prep 해시 6bdd126a30 → 9a8a8e3361 | 같은 커밋에서 prep 재계획 주기를 환경 `REPLAN_HZ`(기본 0.5)로 | [`up_prep_patrol_1023.txt`](../debug_log/2026-10-23/outputs/up_prep_patrol_1023.txt) |
| 10-23 §17 · §17.1 | **f2rp1**: 주기 재계획 끔(`REPLAN_HZ=0.01` + 막힘 · 목표 변경 때만) | 상자 옆 로버 y 0.29~0.31 · 경로 선 0.28~0.30 → **치우침 0** · 실제 최소 **≈ 15.4 cm**(1 s 표본, §5 어긋남 1). 목표 3 첫 경로는 상자 기억 없이 관통(−9.4 cm) → PathBlockedAhead → 약 1 s 정지 → 새 경로 +13.3 cm. 주행 전체 추종 오차 95 % 11.4 cm(0.5 Hz 때 6.3~6.7) | §14 가설과 맞음(1 회). '눈앞 새 장애물' 은 막힘으로 약 1 s 정지 뒤 우회 | [`chk_rp_cfg_f2rp1.txt`](../debug_log/2026-10-23/outputs/chk_rp_cfg_f2rp1.txt) · [`run_f2rp1.txt`](../debug_log/2026-10-23/outputs/run_f2rp1.txt) · [`anal_track_dev_f2rp1.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2rp1.txt) · [`anal_track_err_f2rp1.txt`](../debug_log/2026-10-23/outputs/anal_track_err_f2rp1.txt) · [`nav_events_ms_f2rp1.txt`](../debug_log/2026-10-23/outputs/nav_events_ms_f2rp1.txt) |
| 10-23 §18 · §18.1 | **f2rp2** 반복 | 치우침 ≈ 0(경로 위), 그러나 막힘 뒤 새 경로 자체 여유 **+10.2 cm**(f2rp1 13.3) → 실제 **5.5 cm ✘** | 이번엔 추종이 아니라 계획 경로 여유 — 다시 그리는 출발 자리(막힘 순간 로버 위치)에 따라 10~13 cm. `REPLAN_HZ` 기본 변경 **보류**. ⚠ 57.57 s 사건을 'TF 외삽' 으로 적음 → §19 정정(MPPI 최적화 실패) | [`run_f2rp2.txt`](../debug_log/2026-10-23/outputs/run_f2rp2.txt) · [`anal_plan_series_f2rp2.txt`](../debug_log/2026-10-23/outputs/anal_plan_series_f2rp2.txt) · [`anal_contact_f2rp2.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2rp2.txt) · [`nav_events_ms_f2rp2.txt`](../debug_log/2026-10-23/outputs/nav_events_ms_f2rp2.txt) |
| 10-23 §19 | 사용자 "경로 위 장애물이 나오면 어떻게 고치나 + 영상" | 지금 구성의 순서(아래 §4.1) · f2rp2 실제 순서 · 영상 | 설명 · 영상(판정 아님) | `videos/f2rp2_replan.mp4`(git 제외) · [`fig_replan_video_f2rp2.txt`](../debug_log/2026-10-23/outputs/fig_replan_video_f2rp2.txt) |
| 10-23 §20 · §20.1 | **f2rp3**(no5, 좁은 통로 확인) | 8/8 · 접촉 0 · 최소 정확 여유 4.0 cm, 그러나 서쪽 통로 막힘 오판 → Wait 2 ✘ | → [PathBlockedAhead 카드](pathblocked-only-new.md) | [`run_f2rp3.txt`](../debug_log/2026-10-23/outputs/run_f2rp3.txt) · [`anal_band_run_f2rp3.txt`](../debug_log/2026-10-23/outputs/anal_band_run_f2rp3.txt) |
| 10-23 §20.2~§20.7 | 막힘 판정 99/100 · only_new · f2rp4 · 오프라인 재생 | f2rp4 8/8 · 막힘 0 · 최소 2.9 cm | → [PathBlockedAhead 카드](pathblocked-only-new.md) | — |
| 10-23 §20.8 · §20.9 | **f2rp5**(b910, B0 확정 주행) — 판정 ④ '> 2.7 cm' | 3/3 · 접촉 0 · 막힘 → 재계획 정상 · 새 경로 여유 **8.9 cm** · 굽은 곳 +9~10 cm 깎기 → 실제 **3.1 cm**(코스트맵 정확 4.4). 사용자 "상자에 너무 가까웠음" | 형식상 통과지만 **기준이 잘못 잡힘**(2.7 cm = 칸 판정 뒤집힘 하한, 안전 여유 아님 — 자인). '≥ 8 cm' 면 f2rp2 · f2rp5 불합격 | [`run_f2rp5.txt`](../debug_log/2026-10-23/outputs/run_f2rp5.txt) · [`prep_rp_1023_5.txt`](../debug_log/2026-10-23/outputs/prep_rp_1023_5.txt) · [`anal_contact_f2rp5.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2rp5.txt) · [`anal_track_dev_f2rp5.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2rp5.txt) · [`anal_band_run_f2rp5.txt`](../debug_log/2026-10-23/outputs/anal_band_run_f2rp5.txt) · 그림 [`f2rp5_return_box_frame.png`](../debug_log/2026-10-23/figures/f2rp5_return_box_frame.png) |
| 10-23 §21 | **B0 = NavFn '결함 기준선' 확정**(사용자) | 구성 · 수치 · 알려진 결함(아래 §4.2) | 태그 `navfn-baseline-20261023`(로컬), 다음 = 브랜치 `feature/smac-hybrid` · 계획 §3 → §4 → §5 | SUMMARY §21 |
| 10-23 §22.1 · §22.2 | **Phase P §4 오프라인 계획기 비교(첫 판)** — 실제 planner_server 를 도메인 42 에 | 재구성 칸 일치 6/6 1.0000(패딩 0.01). 상자 여유(차체): NavFn 13.3 · 8.0 · 9.1 · 9.0, Smac 기본형 나쁘거나 같음, B144 −1.0~+3.2. 해석 확장 0.5 · 1.0 m 변형은 대부분 실패 · 'vector::reserve'. 서쪽 통로 Smac 전부 실패(B144 북행만 201° 고리). 계획 0.001~0.04 s. 상자 북쪽 틈 0.70~0.90 m(가운데면 18~28 cm) | **판정 기준 미달 — Smac 으로 바꿀 근거 없음**. 꺾임 안쪽으로 짧게 도는 성질은 계획기와 무관 · 손잡이는 전역 비용장(k < 2, 미시험). ⚠ **10-26 §6.1: 한 서버에 Smac 변형 여럿 = 설정 공유 → Smac 변형 간 비교 무효**(NavFn 값은 유효) | [`prep_scenes.txt`](../debug_log/2026-10-23/outputs/plan_offline/prep_scenes.txt) · [`anal_plan_compare_2.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_plan_compare_2.txt)(표의 원천) · [`_1.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_plan_compare_1.txt) · [`_3.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_plan_compare_3.txt) · [`run_planoff_2.txt`](../debug_log/2026-10-23/outputs/plan_offline/run_planoff_2.txt) · [`anal_box_gap.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_box_gap.txt) · [`anal_fp_global_west_rp3_g4.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_fp_global_west_rp3_g4.txt) · [`chk_smac_ver.txt`](../debug_log/2026-10-23/outputs/plan_offline/chk_smac_ver.txt) |
| 10-23 §22.3 | 사용자 "현재 컨트롤러 문제는 없는지" — 재평가(보조 에이전트 계산, 원문 확인) | 굽은 구간 안쪽 치우침 비율 **69~91 %**(5 주행). 복귀 상자 옆 상자 쪽 최대 +7.1~+11.2 cm · 방향 +6~+15°, 갈 때 반대(중앙 −1.7~−4.7). 직선 옆 오차 중앙 3~5 · 95 % 9~11 cm. 실효 9.72~9.84 Hz, 0.2 s 넘는 틱 17~32, 실행 중 파라미터 = yaml(visualize 만 다름) | **컨트롤러 문제 있음** — 굽은 곳 안쪽 깎기(일관) + 작은 옆 오차를 잘 안 고침. 제어 주기 누락은 주원인 아님(추정). 근접 = 계획 경로 안쪽 치우침 + 컨트롤러 깎기의 합 | [`anal_ctrl_eval.txt`](../debug_log/2026-10-23/outputs/anal_ctrl_eval.txt) · [`anal_ctrl_rate.txt`](../debug_log/2026-10-23/outputs/anal_ctrl_rate.txt) · [`anal_track_err_f2rp1to5.txt`](../debug_log/2026-10-23/outputs/anal_track_err_f2rp1to5.txt) · [`mppi_params_snapshot.txt`](../debug_log/2026-10-23/outputs/mppi_params_snapshot.txt) |
| 10-23 §23 · §24 | 마무리 · 대화 정리 | 제자리 회전 가능(스키드스티어) → DUBIN 은 불필요한 제약, 차동용은 Lattice(diff). 오늘 주행 9 번(§20 · §20.4 · §20.8 의 '9 · 11 · 12 번째' 와 대화 '13 번' 은 잘못 셈). Dubins = 전진만 · RS = 전진 · 후진 · Lattice = 제자리 회전까지. D10(전진 · 후진 원호) · FG 방향 부호(이미 명령 부호로 보정 중) | 다음 = D5(전역 비용장 완만) · D1(Lattice) · 컨트롤러 깎기(MPPI 모의) | 정리 페이지 https://claude.ai/artifact/QqHgHLaFosoaqvAbwsBNu7 · 로컬 [`day_summary_1023.html`](../debug_log/2026-10-23/figures/day_summary_1023.html) · 계획서 §8 · §9 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 전역 감쇠(k)를 키우면 복귀 경로가 상자에서 ≥ 5 cm 멀어진다(사용자 §22) | 기록 지도로 k 2~5 흉내 경로(§1) | 0~5 cm(격자 1 칸), 기록 /plan 은 이미 +10~14 cm | **기각**(단독 대책) — 반대 방향(k < 2)은 10-26 §1 에서 '더 붙음' |
| 1.1 cm 는 계획기가 붙인 것 | 상자 앞에서 그린 경로를 고정한 벗어남(§2) · 출발 0.3 m 밖 경로 여유(§4) | 경로 +11~16 cm, 로버가 그 선보다 상자 쪽 8~16 cm | **기각** — 붙은 것은 로버 |
| PathAlign 이 상자 옆에서 꺼짐(점유율 > 0.05) | 컨트롤러 경로 0.26 m 구간 점의 로컬 칸 값(§3) | 19 시각 꺼짐 0 | **기각** |
| PathAlign 가중 28 이 질러가기를 막는다 | f2pa1 · f2pa2(§5 · §6) | 1~5 · 6~8 cm — 1/2. 굽은 구간 추종 95 % 는 5.0~5.3(14 는 8~9.6) | **부분 지지**(추종은 개선, 상자 옆 결과는 들어오는 길에 따라 갈림) |
| 28 이 5.5 s 정지를 만들었다 | 정지 서명 · 최적 궤적 · 크리틱 엇갈림(§6.2 · §7) | 28 주행 2 회 중 1 회 · 14 주행 같은 서명 0 회, 엇갈림 57° 는 14 주행(30~37°)보다 큼 | **미확인**(증폭 요인 후보) — 10-26 §10.6 모의 · §11~§14 Smac 주행 2 회엔 정지 없음(이후) |
| 상자 옆 근접은 기억 밀림(오도메트리) 탓 | vslam:=on(§10.1 · §11.1) | 밀림 0.8~1.8 cm 로 줄어도 실제 0.3 cm | **기각**(주된 몫 아님) |
| 0.5 Hz 재계획이 매번 로버 자리에서 다시 그려 치우침을 굳힌다(톱니) | 경로마다 추종 오차(§14) → 재계획 끔 f2rp1 · f2rp2 · f2rp5(§17~§20.9) | 한 경로 동안 3~5 cm · 고정 경로 대비 13~16 cm / 재계획 끔에서 치우침 0(f2rp1 · f2rp2) | **지지(측정 + 추론)** — 톱니 기전 자체는 경로별 치우침을 직접 누적해 본 것이 아니라 두 지표의 차이로 추론 |
| 재계획을 끄면 상자 옆 여유가 안정적으로 ≥ 8 cm | b910 3 회 | 15.4(15.2) · 5.5 · 3.1 cm | **기각** — 남은 몫 = 막힘 재계획 출발 자리에 따른 경로 여유(8.9~13.3) + 굽은 곳 깎기 |
| Smac Hybrid 가 상자 옆 경로 여유를 ≥ 5 cm 늘린다 | 오프라인 6 장면(§22.2) | 기준 미달 | 10-23 판정 **기각** → ⚠ 10-26 §6.1 에서 그 비교 자체 **무효**, 변형마다 따로 다시 잰 10-26 §6.3 도 기준 미달(RS 해석 1.0 m 평균 +3.1 · 나빠짐 0) |
| MPPI 는 굽은 곳 안쪽을 깎는다 | 틱마다 부호 있는 치우침(§22.3) | 안쪽 비율 69~91 % · 상자 쪽 최대 +7.1~+11.2 cm | **지지(측정)** — 기전(먼 경로점 당김 > 경로 크리틱)은 추정, 10-26 §10 모의로 이어짐 |

## 4. 조치와 효과
### 4.1 지금 구성에서 '경로 위에 장애물이 나오면'(10-23 §19 설명, BT 기준)
1. 목표를 받으면 RateController 첫 틱에 한 번 NavFn → SimpleSmoother(실패 시 CopyPath 원경로) → FollowPath(MPPI).
2. 주행 중 새 장애물은 MPPI 가 로컬 코스트맵으로 먼저 비켜 감 — 전역 경로는 그대로.
3. PathBlockedAhead(매 틱): 앞 0.30~1.5 m 경로점 중 전역 비용 ≥ 99 가 2 s 이어지면 FollowPath 를 끊고 → 복구(전역 3 m · 로컬 2.5 m 안을 지우지 않는 클리어) → 파이프라인 재시작 = **로버 자리에서 새 경로**.
4. 99 미만으로만 오르면 재계획 없음. 새 경로를 못 찾으면 ABORTED.
5. 그 밖의 재계획 계기: FollowPath 실패(TF 외삽 중단 · MPPI 최적화 실패) → 복구 차례(MonotoneEscape · Wait) → 새 경로.

### 4.2 B0(10-23 §21) — 고정한 것
- 구성: NavFn(GridBased) + SimpleSmoother/CopyPath + MPPI(PathAlign 14 · PathFollow 10 · PreferForward 15 · CostCritic) + 재계획 0.01 Hz(`REPLAN_HZ=0.01`, [`prep_rp_1023.sh`](../debug_log/2026-10-23/jobs/prep_rp_1023.sh)) + PathBlockedAhead(only_new) · vslam on · 깊이 프리셋 3 · nvblox 통합 2.0.
- 수치(상자 = 기록 위치, 실제 최소 여유):

  | 주행 | 코스 | 결과 | 막힘 뒤 경로 자체 여유 | 실제 최소 여유 | 비고 |
  |---|---|---|---|---|---|
  | f2rp1 | b910 | 3/3 | 13.3 cm | **15.2**(0.1 s · 10-26) / 15.4(1 s 표본 · 10-23) | 치우침 0 |
  | f2rp2 | b910 | 3/3 | 10.2 | **5.5** | 치우침 0, 경로가 가까움 |
  | f2rp5 | b910 | 3/3 | 8.9 | **3.1**(코스트맵 정확 4.4) | 굽은 곳 +9~10 cm 깎기, 차체 5° 기울어짐 |
  | f2rp3 | no5 | 8/8 | — | 정확 4.0(남서 목표 근처) | 막힘 오판 5 · Wait 2(only_new 전) |
  | f2rp4 | no5 | 8/8 | — | 정확 2.9(남서 돌아서기) | 막힘 0(only_new, 작동은 미확인) |

  원문 줄([`anal_contact_f2rp5.txt`](../debug_log/2026-10-23/outputs/anal_contact_f2rp5.txt)):
  ```
  17:23:03.11~17:23:13.85 (t 194.5~205.3 s) 최소 +0.031 m @ 17:23:07.64 t 199.1 · 로버 (1.21, 0.19, -173°) · 지령 v 0.080 ω -0.00 | 상자 영역 칸: 로컬 LETHAL 4 · 전역 LETHAL 4 · 조각 4
  ```
  10-26 비교 그림 출력([`fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt)) 1 행 `B0 f2rp1 15.2 cm · f2rp2 5.5 cm · f2rp5 3.1 cm`.
- 알려진 결함(§21 원문): 경로 여유 부족(NavFn 점 계획) + 굽은 곳 모서리 깎기 · 차체 방향 기울어짐(MPPI) + 막힘 재계획 출발 자리 의존.

### 4.3 판단에 쓴 핵심 줄 · 출력
- **톱니(§14)** — [`anal_track_err.py`](../debug_log/2026-10-23/jobs/anal_track_err.py) 5 · 47~49 행: 경로를 받은 뒤 0.5 s ~ 다음 경로까지 0.2 s 마다 로버 ↔ **그 경로** 수직 거리, 상자 둘레 = 지도 x 0.8~1.8 · y −0.3~0.5.
  ```python
  for t in np.arange(tp + 0.5, tn, 0.2):
      ...
      if 0.8 <= q[0] <= 1.8 and -0.3 <= q[1] <= 0.5: boxv.append(e)
  ```
  출력([`anal_track_err.txt`](../debug_log/2026-10-23/outputs/anal_track_err.txt)) — 상자 둘레 95 % 는 3~4 cm 인데 고정 경로 대비는 13~16 cm(§2):
  ```
  f2pi1 · 경로 103 개
     상자 둘레 중앙  0.8 · 95 %  3.2 · 최대  4.6 cm (n 125)
     굽은 구간 중앙  2.1 · 95 %  8.1 · 최대 13.0 cm (n 222)
  f2pa1 · 경로 103 개
     굽은 구간 중앙  1.7 · 95 %  5.3 · 최대 10.4 cm (n 241)
  ```
  [`anal_track_dev_f2pi1_freeze.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2pi1_freeze.txt)(열: t · 자세 · 실제 여유 · 고정 경로 여유 · 벗어남(+ 상자 쪽)):
  ```
  == f2pi1 경로 고정 t 198
    205.0 | ( 1.35,  0.20,  -178°) |   4.5 cm |  13.8 cm ·  +7.1 cm |  13.5 cm ·  +6.7 cm
    210.0 | ( 0.99,  0.14,  -173°) |   1.2 cm |  13.8 cm · +15.7 cm |  13.5 cm · +15.4 cm
  ```
- **PathAlign 꺼짐 기각(§3)** — [`anal_pathalign_occ.py`](../debug_log/2026-10-23/jobs/anal_pathalign_occ.py) 42 행(Humble `path_align_critic.cpp` 조건을 옮김):
  ```python
  on = not ((bad / rng > 0.05) and bad > 2); on2 = not (((bad + unk) / rng > 0.05) and bad + unk > 2)
  ```
  출력 끝 줄 `합: 19 시각 중 꺼짐 0`([`anal_pathalign_occ_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_pathalign_occ_f2pi1.txt)).
- **전역 감쇠(§1.1)** — [`anal_ginfl_path.py`](../debug_log/2026-10-23/jobs/anal_ginfl_path.py) 50 행(내접 0.175 · 반경 0.70 · NavFn 칸 비용 50 + 0.8 × c):
  ```python
  c = np.where(dist <= RINS, 253.0, np.where(dist <= R, 252.0 * np.exp(-k * (dist - RINS)), 0.0)); c[leth] = 254; cost = 50 + 0.8 * c; block = c >= 253
  ```
  출력([`anal_ginfl_path_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_ginfl_path_f2pi1.txt)):
  ```
   t 170.0 s(전역 코스트맵 t 169.5) · 로버 (2.46, -1.45, 140°) · 실제 상자 자리 치명 칸 5
     기록된 /plan(t 170.0): 실제 상자까지 0.294 m · 여유 +12.9 cm · 길이 3.76 m · 상자 0.4 m 안 0.73 m
     흉내 k 2.0 (현재): 실제 상자까지 0.285 m · 여유 +12.0 cm · 길이 3.86 m · 상자 0.4 m 안 0.70 m
     흉내 k 3.0      : 실제 상자까지 0.335 m · 여유 +17.0 cm · 길이 3.93 m · 상자 0.4 m 안 0.67 m
  ```
- **5.5 s 정지(§7)** — [`chk_opt_traj_f2pa2.txt`](../debug_log/2026-10-23/outputs/chk_opt_traj_f2pa2.txt)(최적 궤적 단계 속도):
  ```
  t  99.07 · 단계 속도(m/s) 앞 8: 0.077 0.071 0.069 0.065 0.071 0.071 0.071 0.077 · ...
  t 101.07 · 단계 속도(m/s) 앞 8: 0.002 0.006 0.012 0.027 0.054 0.060 0.066 0.077 · ...
  t 106.58 · 단계 속도(m/s) 앞 8: 0.076 0.068 0.065 0.061 0.068 0.068 0.068 0.076 · ...
  ```
  [`anal_mppi_stop_f2pa2.txt`](../debug_log/2026-10-23/outputs/anal_mppi_stop_f2pa2.txt)(열: t · v ω · 최적 궤적 · 경로 옆거리 · 경로 방향 · 목표 거리 · 방위):
  ```
   99.5 | +0.083 +0.02 | 0.221 m · +0.225/-0.020 ·  -11° | -0.061 m ·   -4° | 0.91 m ·  +15° ·  +43° (GoalCritic 켜짐)
  100.0 | +0.050 +0.09 | 0.227 m · +0.226/-0.003 ·   -6° | +0.014 m ·  -42° | 0.87 m ·  +15° ·  +42° (GoalCritic 켜짐)
  100.5 | +0.001 -0.07 | 0.214 m · +0.213/+0.001 ·   -7° | +0.014 m ·  -43° | 0.85 m ·  +14° ·  +41° (GoalCritic 켜짐)
  ```
- **컨트롤러 안쪽 깎기(§22.3)** — [`anal_ctrl_eval.txt`](../debug_log/2026-10-23/outputs/anal_ctrl_eval.txt) 114~115 · 435 행:
  ```
   굽음(≥30°): 안쪽(+) 부호 치우침 e_in cm 중앙  +1.9 · 95 %  +7.0 · 최대 +16.0 · 최소  -3.4 (n 256)
              안쪽 비율 91 % (e_in > 0) · 안쪽 2 cm 넘음 48 % · 바깥 2 cm 넘음 4 %
     지나감 17:22:55.8~17:23:16.5 (yaw 중앙 -163°, 틱 208): e_box 중앙 +8.1 · 최대 +11.2 · 최소 +0.2 cm · he_box 중앙 -1.3 · 최대 +15.3° · 차체↔상자 최소 0.032 m @ 17:23:08.3
  ```
  (첫 두 줄 = f2rp2, 마지막 = f2rp5 복귀.)
- **오프라인 비교(§22.2)** — [`anal_plan_compare_2.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_plan_compare_2.txt)(열: 점 · 길이 | 상자 여유 차체 · 중심 | 치명까지 | 최대 꺾임 | 계획 s):
  ```
  b910_rp2_replan  GridBased     |  121 ·  3.09 |    8.0 ·   10.2 |    7.9 |    90 | 0.001
  b910_rp2_replan  Smac_R10_C30_A05 | 실패
  b910_rp2_replan  Smac_R10_C30_A05_B144 |   46 ·  3.08 |    7.0 ·    8.3 |    7.3 |    26 | 0.003
  west_rp3_g5      Smac_R10_C30_A05_B144 |   46 ·  2.34 |  420.5 ·  434.6 |    3.1 |   201 | 0.030
  ```
  실패 원인 줄([`run_planoff_2.txt`](../debug_log/2026-10-23/outputs/plan_offline/run_planoff_2.txt) 58 행): `Smac_R10_C30_A05 plugin failed to plan calculation to (0.00, 0.00): "vector::reserve"`.

### 4.4 한계
- 주행마다 1 회씩 · 같은 날 · 같은 상자 배치. 'b910 3 회' 가 B0 수치의 전부.
- 실제 여유는 SLAM 지도 위 차체 사각형 ↔ 기록 상자 사각형(수 cm SLAM 오차 포함, 10-22 §16 의 '1.2 cm 는 오차 범위').
- 톱니 기전은 '한 경로 동안 3~5 cm' 와 '고정 경로 대비 13~16 cm' 의 차이에서 추론 — 재계획마다 치우침이 이어지는 모습을 직접 이어 그린 그림은 없음.

### 4.5 지금 코드 영향(11-03 확인)
- MPPI: [`nav2_params.yaml`](../../ros2_ws/src/rover_navigation/config/nav2_params.yaml) 281 행 `PathAlignCritic … cost_weight: 28.0`(278 행 주석 '2026-10-26 §11~§14 사용자 채택, Smac 구성'), 285 행 `PathFollowCritic … cost_weight: 5.0` — **B0 의 14 · 10 과 다름**. 10-23 은 28 을 '보류 → 14 복귀' 했고(§6.1 · §10), 10-26 에 PathFollow 5 와 짝지어 다시 들였다. `max_path_occupancy_ratio: 0.05`(281 행) 그대로.
- 재계획: BT [`nav_to_pose_no_spin.xml`](../../ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml) 66 행 `RateController hz="0.01"`(BT 원본), [`navigation.launch.py`](../../ros2_ws/src/rover_navigation/launch/navigation.launch.py) 112~114 행이 `replan_hz` 를 주면 그 줄을 바꾼 사본을 씀 · 201 행 기본 `''`(= 0.01) · 203 행 `planner` 기본 `navfn`. 순회 prep [`prep_patrol.sh`](../tools/prep_patrol.sh) 17 행 `replan_hz:=${REPLAN_HZ:-0.5}` → **표준 prep 은 아직 0.5 Hz**(§18.1 '기본값 변경 보류' 가 그대로). B0 · 10-26 ~ 28 Smac 주행은 `REPLAN_HZ=0.01`(+ `NAV_ADD="planner:=smac"`)을 따로 줬다(CLAUDE.md §6 11-03 정정과 일치).
- 태그 `navfn-baseline-20261023` → 커밋 `9ce20486`(annotated). 그 커밋의 `prep_patrol.sh` 도 기본 0.5 — B0 를 다시 띄우려면 `REPLAN_HZ=0.01` 을 줘야 한다(`prep_rp_1023.sh` 3 행).
- 막힘 판정 xml 108 행 `only_new="true"` — [PathBlockedAhead 카드](pathblocked-only-new.md).

## 5. 내 실수 · 기록 어긋남
1. **'최신 경로 대비 벗어남' 지표 오류**(10-23 §2 → §4) — 하려 한 것: 로버가 경로에서 얼마나 벗어났나 · 본 것: ±1~4 cm · 처음 추론: 잘 따라감 · 의심한 이유: 경로가 0.5 Hz 로 로버 자리에서 다시 그려짐 · 판별: 상자 앞 경로 고정(FREEZE) · 결론: 최신 경로 대비 지표는 늘 작게 나옴, 고정 경로 대비 +15.7 cm · 다음에 알아보는 법: 경로가 로버 자리에서 시작하면 그 경로 대비 오차는 0 에서 출발한다 — 경로 여유는 출발 0.3 m 밖 점으로, 벗어남은 고정 경로로 · 데이터: [`anal_track_dev_f2pi1.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2pi1.txt) → [`_freeze.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2pi1_freeze.txt). 같은 함정이 §2 의 '최신 경로 여유' 칸(209~210 s 에 0.0 cm)에도 있었다(§4 가 정정).
2. **`anal_track_err.py` 첫 판 인공물**(§14) — 출발 0.15 m 밖 구간만 써서 모든 주행이 중앙 8.8 cm 로 같게 나옴 → 전체 경로로 고침(도구 머리말 6 행). 다음에 알아보는 법: 주행마다 값이 거의 같으면 지표 인공물부터. 첫 판 출력은 원천 소실(덮어씀).
3. **§13 대책 추천을 장애물 쪽(ClearanceBandCritic)으로** — §4(경로는 11~16 cm) · §12(비용은 북쪽이 낮음) 가 이미 '추종' 을 가리켰는데 장애물 거리 크리틱을 1 순위로 올렸다. 사용자가 데이터로 반박(§14) → 철회.
4. **§18.1 '57.57 s TF 외삽 중단'** → §19 정정: 바로 앞 줄이 `Optimizer fail to compute path`(최근접 4.2 cm). 다음에 알아보는 법: `Aborting handle` 은 원인이 여럿 — 바로 앞 줄을 함께 본다.
5. **B0 확정 판정 ④ '> 2.7 cm'**(§20.8 → §20.9 자인) — 칸 판정 뒤집힘 하한(측정 잡음 수준)을 안전 기준으로 씀. §17 의 '≥ 8 cm' 를 쓰면 f2rp2 · f2rp5 불합격. 결과: B0 는 '합격 기준선' 이 아니라 '결함 기준선' 으로 이름 붙여 확정(사용자).
6. **오늘 주행 수를 잘못 셈**(§20 · §20.4 · §20.8 '9 · 11 · 12 번째', 대화 '13 번' → §23 정정: 9 번).
7. **(10-26 §6.1 이 찾은) 오프라인 비교 도구 결함** — 하려 한 것: Smac 변형 여럿을 한 planner_server 에 올려 한 번에 비교(10-23 §22.2) · 본 것(10-26): cp · 운동 모델을 바꿔도 같은 경로, 같은 설정이 함께 올린 변형에 따라 결과가 바뀜 · 판별: `node_hybrid.hpp:446` `static HybridMotionTable motion_table` 등 static 상태 · 결론: **10-23 §22.2 의 Smac 변형 간 비교는 무효**, NavFn 값은 유효 · 고친 도구 [`run_variants.sh`](../tools/plan_offline/run_variants.sh)(변형마다 프로세스 따로, 머리 주석 4~5 행이 '10-23 §22.2 무효' 를 적음) · 데이터 [10-26 SUMMARY §6.1](../debug_log/2026-10-26/SUMMARY.md). 10-23 의 'cost_penalty 효과 없음 · 해석 확장이 경로를 정함(추정)' 읽기도 함께 근거 없음으로 되돌려졌다.
8. **기록 어긋남**:
   1. **B0 f2rp1 '15.4 cm'**(10-23 SUMMARY §17.1 · §21, [`SMAC_HYBRID_PLAN.md`](../06_planner/SMAC_HYBRID_PLAN.md) §2 항목 1, 태그 커밋 메시지 `9ce20486`, [`prep_scenes.txt`](../debug_log/2026-10-23/outputs/plan_offline/prep_scenes.txt) 1 행) 은 [`anal_track_dev_f2rp1.txt`](../debug_log/2026-10-23/outputs/anal_track_dev_f2rp1.txt) 22 행 1 s 표본 값(`205.0 | ( 1.10, 0.30, -175°) | 15.4 cm`). 0.1 s 최소는 **15.2**([10-26 `fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt) 1 행), 틱 단위 [`anal_ctrl_eval.txt`](../debug_log/2026-10-23/outputs/anal_ctrl_eval.txt) 24 행은 0.153 m. 10-23 정리 페이지엔 11-03 에 정정 표시가 붙었지만 SUMMARY 본문 · 계획서 §2 에는 없다.
   2. **계획서 [`SMAC_HYBRID_PLAN.md`](../06_planner/SMAC_HYBRID_PLAN.md) §8(70 행)** 이 10-23 §22.2 수치('144 칸형 −1.0~+3.2 cm' · 'cost_penalty 효과 거의 없음' · '해석 확장 0.5 · 1.0 m 은 즉시 실패 · vector::reserve')를 무효 표시 없이 그대로 갖고 있다(10-26 §6.1 무효). §10(88 행~) 의 'cost_penalty · 회전 벌점 효과 없음(1.1.20)' 도 같은 도구로 잰 10-26 §3 결과라 §6.1 의 무효 범위에 걸릴 수 있다(미대조). 10-26 §6.3 의 다시 잰 판에선 설치판 RS + 해석 1.0 m 가 잘 계획됐다 — 10-23 의 'vector::reserve' 가 설정 공유 탓이었는지는 기록에 없음(미확인).
   3. **'B144' 변형의 정체**: SUMMARY §22.2 표는 'Smac B144(R 0.10 · cp 3 · 방향 144 칸)' 이라 적고 '해석 확장 0.5 · 1.0 m 로 줄인 변형은 장면 대부분에서 즉시 실패' 라고 하나, 설정 [`planner_offline_2.yaml`](../debug_log/2026-10-23/outputs/plan_offline/planner_offline_2.yaml) 171~173 행은 B144 도 `analytic_expansion_max_length: 0.5`(이름 `Smac_R10_C30_A05_B144`). 즉 '작동한 유일한 변형' 도 해석 0.5 m 판이었다. 그리고 SUMMARY 표 B144 값(16.5 · 7.0 · 11.8 · 12.2)은 패딩 0.01 판 `anal_plan_compare_2.txt`, 패딩 0 판 [`_3.txt`](../debug_log/2026-10-23/outputs/plan_offline/anal_plan_compare_3.txt) 은 15.9 · 11.1 · 10.9 · 11.9 — 표가 어느 판인지 SUMMARY 에 없다.
   4. **§22.3 '방향 오차 최대 +6~+15°'** 는 복귀 상자 지나감 구간(he_box 최대 9.4 · 10.4 · 6.2 · 9.3 · 15.3°)의 값이고, 상자 창 전체(갈 때 포함)의 최대는 10.4~19.9°([`anal_ctrl_eval.txt`](../debug_log/2026-10-23/outputs/anal_ctrl_eval.txt) 23 · 123 · 227 · 329 · 432 행). 적힌 범위 자체는 복귀 기준으로 맞음 — 구간 표시가 없을 뿐.
   5. 10-22 §16 '멈칫 B 는 velocity_smoother 0 감속' — 추정이라 적혀 있고 확인 수단(컨트롤러 출력 토픽 기록)은 그 뒤에도 없음.

## 6. 남은 것 (10-23 시점)
- 상자 옆 근접 = 계획 경로 안쪽 치우침(9~16 cm, 틈은 18~28 cm 가능) + MPPI 굽은 곳 깎기(+7~11 cm) + 막힘 재계획 출발 자리 의존. 어느 것도 고쳐지지 않음.
- f2pa2 5.5 s 정지(경로 · 목표 크리틱 57° 엇갈림)와 W3 앞 U 자 경로가 왜 생기나(NavFn 퍼텐셜 모양 추정) — 미확인.
- 재계획 0.01 Hz 의 대가: 주행 전체 추종 오차 95 % 11.4~11.6 cm(0.5 Hz 6.3~6.7). 표준 prep 은 0.5 Hz 그대로.
- 멈칫 A(TF 외삽) · B(제어 주기 늦음) — CPU 70~76 % 배경, 미해결(§23 목록).
- 출발 문 근처 스무더 충돌 12 회(f2pa2 §6.1) — 이유 미확인.
- §23 '다음': D5 전역 비용장 완만(오프라인) · D1 Lattice · 컨트롤러 깎기 모의.

## 7. 이후 (10-26 ~) — 포인터
- **10-26 §1** D5: 전역 감쇠를 완만하게(k 1.0 · 0.5) 하면 경로가 상자에 **더** 붙음 → '계획기 쪽 손잡이로는 +5 cm 못 얻음'. §6.1 오프라인 도구 결함(위 실수 7) · §6.3 변형마다 다시 잼(RS 해석 1.0 m 평균 +3.1 · 나빠짐 0, 기준 미달). §9~§10 MPPI 굽은 곳 깎기 오프라인 모의 → §11~§14 실주행 Smac + **PathAlign 28 · PathFollow 5 채택**(지금 yaml 281 · 285 행). §10.6 f2pa2 정지 장면 모의 · §11 판정 ③ '이유 없는 정지 0' — 그 2 회엔 정지 없음. 근거 [10-26 SUMMARY](../debug_log/2026-10-26/SUMMARY.md) · [10-26 `fig_box_compare.txt`](../debug_log/2026-10-26/outputs/compare/fig_box_compare.txt)(Smac f2sh1 18.4 · f2sh2 10.8 cm).
- **10-27** `planner:=smac`(Hybrid RS · cp 3.0 · 해석 1.0 · tolerance 0.35, 실패 시 NavFn) — 시험 인자(기본 navfn) → [전역 계획기 카드](global-planner-choice.md) '이후'. 그 시기 카드에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2pi1 · f2sm3(10-22) | 출발점 상자 b910 — 1.1 · 9.1 cm, 10-23 분석의 입력 | `2026-10-22/outputs/run_f2pi1.txt` · `run_f2sm3.txt` · bag `2026-10-22/bags/bag_f2pi1.tgz` · `bag_f2sm3.tgz` |
| f2pa1 · f2pa2 | PathAlign 28(Jetson 만) | `2026-10-23/outputs/run_f2pa*.txt` · bag `bags/bag_f2pa*.tgz` · nav2 `outputs/nav2_f2pa*.log` |
| f2von1 · f2von2 | vslam:=on — 상자 옆만 이 카드 | `outputs/run_f2von*.txt` · `anal_contact_f2von*.txt` |
| f2rp1 · f2rp2 · f2rp5 | b910 재계획 0.01 Hz(B0 수치) | `outputs/run_f2rp*.txt` · `chk_rp_cfg_f2rp*.txt` · `prep_rp_1023_*.txt` · bag `bags/bag_f2rp*.tgz` |
| f2rp3 · f2rp4 | no5 재계획 0.01 Hz | → [PathBlockedAhead 카드](pathblocked-only-new.md) |
| 오프라인 계획기 1~3 판 | 1 = 기본형 6 변형(패딩 0.01) · 2 = 해석 · 144 칸 변형(패딩 0.01) · 3 = 2 와 같은 변형 패딩 0 | `outputs/plan_offline/run_planoff_{1,2,3}.txt` · `anal_plan_compare_{1,2,3}.txt` · `result_{1,2,3}.npz` · `planner_offline_{1,2,3}.yaml` · 그림 `figures/plan_offline{,_2,_3}/` |
| `anal_ginfl_path.py` · `anal_track_dev.py` · `anal_pathalign_occ.py` · `anal_plan_series.py` · `anal_track_err.py` | 계획 경로 대 실제 길 | `2026-10-23/jobs/` |
| `chk_ctrl_gap.py` · `chk_opt_traj.py` · `anal_mppi_stop.py` · `chk_scan_window.py` · `fig_mppi_stop.py` | 5.5 s 정지 | 같은 곳 |
| `anal_cost_section.py` · `fig_return_video2.py` · `fig_replan_video.py` | 상자 옆 단면 · 영상 | 같은 곳 |
| `anal_ctrl_eval.py` · `anal_ctrl_rate.py` · `chk_mppi_params.py` | 컨트롤러 재평가 | 같은 곳 |
| `up_palign_1023.sh` · `prep_rp_1023.sh` · `chk_rp_cfg.sh` | 배포 · prep · 설정 확인 | 같은 곳 |
| `Docs/tools/plan_offline/` | 오프라인 계획기 비교(P7) | `prep_scenes.py` · `gen_yaml.py` · `up_bundle.sh` · `run_planner_offline.sh` · `query_planners.py` · `anal_plan_compare.py` · `anal_fp_global.py` · `kill_planoff.sh` · (10-26) `run_variants.sh` |
| (10-21 · 10-22) `anal_stops.py` · `anal_dip_events.py` · `anal_nav_ms.py` · `anal_contact.py` | 정지 · 멈칫 · 사건 · 실제 여유 | `2026-10-21/jobs/` · `2026-10-22/jobs/` |

## 9. 도구 해설
공통: 모두 PC(Git Bash · Python rosbags), 로버 안 움직임 — 단 `up_*` · `prep_*` · `chk_rp_cfg.sh` · `run_planner_offline.sh` · `query_planners.py` 는 Jetson(`run_jn.sh` 경유). 입력 bag 은 PC 로컬 `bags/bag_<이름>.tgz` 를 푼 것. 시각 인자 's' 는 bag 시작 기준 초.

### anal_ginfl_path.py — 전역 감쇠별 계획기 흉내 (10-23 §1)
- 부른 형태: `anal_ginfl_path.py bag 170,185,195,203 [2,3,4,5]`.
- 왜: 사용자 §22 제안의 계산 — 감쇠 k 를 바꾸면 복귀 경로가 실제 상자에서 얼마나 떨어지나.
- 하는 일: 그 시각 직전 `/global_costmap/costmap` 의 치명 칸(100)에서 거리 변환 → inflation 다시 계산(50 행, 위 §4.3) → 칸 비용 50 + 0.8 × c(NavFn COST_NEUTRAL · FACTOR), 내접 이상 통과 불가, 8 방향 Dijkstra(출발 = 그 시각 로버 map 자세, 도착 = (0, 0)). 상자 = 10-19 실측 사각형(16 행 `BOX = (1.151, 1.261, -0.20, -0.02)`). 같은 시각 기록 `/plan` 과 견줘 흉내 검증.
- 출력: 시각마다 기록 /plan · k 별 흉내의 '실제 상자까지 · 여유 · 길이 · 상자 0.4 m 안 길이' → `outputs/anal_ginfl_path_f2pi1.txt` · `_f2sm3.txt`.
- 쓰인 곳: §1.1 '선언 기준 미달'. 결함: NavFn 은 퍼텐셜 기울기를 따라 그리므로 Dijkstra 와 같지 않음 — 검증 차 0.5~7.7 cm(f2pi1 t 203 이 큼). 계보: 10-13 §5.2 B 흉내 → 이 판 → 10-23 §22 부터 실제 planner_server 를 부르는 `Docs/tools/plan_offline/`(P7 '흉내 기반 분석 도구 교체').

### anal_track_dev.py — 계획 경로 여유 대 실제 여유 (10-23 §2)
- 부른 형태: `anal_track_dev.py bag 시작s 끝s [간격 0.5]`, 환경 `FREEZE=198`(고정 경로).
- 하는 일: 시각마다 ① 실제 여유(차체 사각형 ↔ 상자) ② 그 시각 최신(또는 FREEZE 시각) `/plan_smoothed` 의 상자 옆 여유 ③ 로버 중심의 그 경로 수직 거리(+ = 상자 쪽) ④ `/transformed_global_plan` 기준 같은 값.
- 출력: `outputs/anal_track_dev_<run>.txt` · `_f2pi1_freeze.txt`. 쓰인 곳: §2 · §5 · §10.1 · §11.1 · §17.1 · §18.1 · §20.9 판정 1. 결함: 기본 판(최신 경로) 은 위 실수 1 의 지표 함정 — 머리말 5~6 행에 경고. 1 s 표본이라 최소값이 0.1 s 판보다 클 수 있음(어긋남 8.1).

### anal_pathalign_occ.py — PathAlign 이 꺼졌나 (10-23 §3)
- 부른 형태: `anal_pathalign_occ.py bag 196 214 [1.0] [0.26]`.
- 하는 일: 컨트롤러 경로에서 로버 최근접점 ~ 0.26 m(vx 0.08 × 3.2 s) 앞 구간 점의 로컬 칸 값을 세어, Humble 조건 `비율 > 0.05 이고 개수 > 2` 면 '꺼짐'(42 행). 미확인(−1)을 더한 판도 함께.
- 출력: 시각별 표 + `합: 19 시각 중 꺼짐 0`. 결함: '지평 끝 점' 을 거리로 근사(실제는 최적 궤적 끝이 닿은 경로점 index).

### anal_plan_series.py — 다시 그려진 경로마다 여유 (10-23 §4)
- 부른 형태: `anal_plan_series.py bag 시작s 끝s`.
- 하는 일: 구간의 `/plan` · `/plan_smoothed` 마다 출발 자리 · **출발에서 0.30 m 넘는 경로점만**(21 행 `far = … > 0.30`)으로 잰 실제 상자 여유(− 0.165)와 그 점 위치.
- 출력 예(`anal_plan_series_f2pi1.txt`): `204.3 /plan_smoothed  출발 ( 1.36,  0.19) · 여유 +10.9 cm @ (1.06, 0.24) [map]`. 쓰인 곳: §4 · §5 판정 1(출발점 y 대 경로점 y) · 그 뒤 모든 b910 판정. 결함: `/plan` 에는 러너 상주 조회기 경로도 섞임(같은 토픽) — 10-23 §20.6 이 영상 도구에서 `/plan_smoothed` 를 고른 이유.

### anal_track_err.py — 경로마다 추종 오차 (10-23 §14)
- 부른 형태: `anal_track_err.py bag…`(여러 bag).
- 하는 일: `/plan_smoothed` 하나가 쓰이는 동안(받은 뒤 0.5 s ~ 다음 경로) 0.2 s 마다 로버 중심 ↔ 그 경로 전체 수직 거리(방향 없음). 상자 둘레 · 굽은 구간(경로 0.5 m 안 방향 변화 > 30°, 20~21 행) · 경로 끝 시각으로 나눔.
- 출력: `outputs/anal_track_err.txt`(6 주행) · `_f2rp1.txt` · `_f2rp2.txt` · `_f2rp1to5.txt`. 결함: 방향 없는 거리 — 안쪽 · 바깥쪽 · 상자 쪽을 못 가름(→ `anal_ctrl_eval.py`). 재계획 0.01 Hz 주행에선 경로 하나가 오래 쓰여 '전체' 값이 커짐(같은 지표라도 뜻이 달라짐).

### chk_ctrl_gap.py · chk_opt_traj.py · anal_mppi_stop.py · chk_scan_window.py · fig_mppi_stop.py — 5.5 s 정지 (10-23 §6.2~§8)
- `chk_ctrl_gap.py bag 96 107`: `/trajectories` · `/transformed_global_plan` 수신 간격 · header 시각 → 컨트롤러가 새로 계산했나(110 개 ≈ 10 Hz). 출력 `chk_ctrl_gap_f2pa1.txt` · `_f2pa2.txt`.
- `chk_opt_traj.py bag 96.07,99.07,…`: 'Optimal Trajectory' 32 점의 점간 거리 / 0.1 s = 단계 속도(위 §4.3 발췌). 왜: 최적 궤적은 0.21 m 앞으로 가는데 명령이 0 인 이유 — '나중에 출발' 해인지.
- `anal_mppi_stop.py bag 93 106 5.50,-2.20,13 [0.5]`: 시각마다 명령 · 최적 궤적 길이 · 끝 변위 · 끝 방향 · 경로 옆거리 · 0.3 m 앞 경로 방향 · 목표 거리 · 방위, 크리틱 문턱(GoalCritic 1.0 m 등) 표시. 같은 도구를 목표 (0, 0) 으로 f2von2 상자 옆에도 씀(`anal_mppi_goal_f2von2.txt`, §12). 출력 `anal_mppi_stop_f2pa2.txt` · `_cmp.txt`(14 · 28 주행 같은 자리).
- `chk_scan_window.py bag 시작 끝`: 앞 ±60° 라이다 최소 거리 · 방위 · 1.2 m 안 점 수를 1 s 마다(라이다 yaw ≈ π 를 base_link 로 바꿈) — 사람이 지나갔나. 출력 `chk_scan_window_f2pa2.txt`.
- `fig_mppi_stop.py bag 출력.png 목표 시각들 그래프구간`: 정지 전 · 중 · 출발 3 장면 + 단계 속도 + 엇갈림 시간 그래프 → [`figures/mppi_stop_f2pa2.png`](../debug_log/2026-10-23/figures/mppi_stop_f2pa2.png). 새로 보인 것: U 자 경로.
- 결함 · 한계: 크리틱 비용 자체는 bag 에 없음(엇갈림 '각' 만 봄) — 국소 최소 기전은 추정. 이후 10-26 §10.6 오프라인 MPPI 모의가 같은 장면을 다시 봄.

### anal_cost_section.py · fig_return_video2.py — 상자 옆 단면 · 영상 (10-23 §12)
- `anal_cost_section.py bag 시각들 x값들 [y0,y1]`: 지도 x 고정 단면에서 로컬 코스트맵 값(odom → 그 순간 map→odom)을 y 따라, 차체 양옆 끝 칸 값도. 출력 `anal_cost_section_f2von2.txt` — '비용은 북쪽이 낮았다' 의 근거.
- `fig_return_video2.py`: 10-22 `fig_return_video.py`(상자 둘레 확대 · 깊이 영상 · 여유 그래프)에 MPPI 최적 궤적(단계 속도 색, 첫 단계 굵은 원)을 더한 판. 깊이가 bag 에 없으면 오른쪽 위 판을 비움. 출력 `videos/f2von2_return_box.mp4`(git 제외) · 줄 `fig_return_video2_f2von2.txt`. 계보 → 10-23 §20.6 `Docs/tools/fig_drive_video.py`(→ [주행 운영 카드](drive-ops-1019-1023.md)).

### fig_replan_video.py — 재계획 영상 (10-23 §19 · §20.1)
- 부른 형태: `fig_replan_video.py bag 출력.mp4 시작 끝 배속 nav_events.txt`.
- 하는 일: `Docs/tools/fig_run_video.py`(10-14) 사본 + PathBlockedAhead 가 보는 구간(앞 0.30~1.5 m)과 그 구간 전역 비용 ≥ 99 점(빨간 ×) + 최근 3 s nav2 사건 줄. 출력 `videos/f2rp2_replan.mp4` · `f2rp3_west_corridor.mp4`, 줄 `fig_replan_video_f2rp2.txt` · `_f2rp3.txt`.
- 결함: 경로를 `/plan`(39 · 52 행)으로 그림 — 이 토픽엔 러너 상주 조회기의 경로도 섞인다. §20.6 새 도구 `fig_drive_video.py` 가 `/plan_smoothed` 로 바꿨고, §20.7 에서 다시 'BT 가 고른 스무딩/원경로' 로 고쳤다(→ [주행 운영 카드](drive-ops-1019-1023.md)). 이 판은 고치지 않음.

### anal_ctrl_eval.py · anal_ctrl_rate.py · chk_mppi_params.py — 컨트롤러 재평가 (10-23 §22.3)
- `anal_ctrl_eval.py name=bag…`: 컨트롤러가 매 틱 낸 `/transformed_global_plan`(odom) 대비, 그 메시지 stamp 의 odom→base_link 로 부호 있는 옆 치우침 e · 방향 오차 · 0.5 m 앞 곡률(직선 < 15 · 중간 · 굽음 ≥ 30°). 굽음에선 e_in(+ = 안쪽), 1.0 m 안 치명 칸 있으면 e_obs, 상자 창(≤ 0.6 m)에서 e_box 와 차체 ↔ 상자. 병진 틱(|vx| ≥ 0.02)만. 출력 `anal_ctrl_eval.txt`(위 §4.3 발췌).
- `anal_ctrl_rate.py`: nav2 로그의 주기 놓침 · 최적화 실패 · TF 외삽(노드별) · Optimizer reset 수 + bag `/transformed_global_plan` 간격(컨트롤러 틱 대리, 실효 Hz) · `/cmd_vel` 간격(velocity_smoother 20 Hz 라 컨트롤러 주기를 직접 보여 주지 않음 — 도구가 주의를 적음). 출력 `anal_ctrl_rate.txt`(f2rp1 `실효 9.72 Hz` 등).
- `chk_mppi_params.py nav2_params.yaml name=bag…`: yaml controller_server 블록 원문 + bag `params.txt` 실행 중 값 + 차이. 출력 `mppi_params_snapshot.txt`(차이 = visualize 하나).
- 쓰인 곳: §22.3 '컨트롤러 문제 있음'. 계산은 보조 에이전트, 수치는 원문으로 확인했다고 SUMMARY 가 적음. 지금 다시 쓸 수 있음(10-26 이 같은 성질을 Smac 주행에서 다시 확인).

### Docs/tools/plan_offline/ — 오프라인 계획기 비교 (10-23 §22.1, P7)
- 순서: ① PC `prep_scenes.py 출력.npz 날짜폴더` — bag 에서 장면(그 시각 직전 전역 코스트맵 · 로버 map 자세 · 러너 출력의 '목표 N 출발' 자세) 6 개 → [`scenes_1023.npz`](../debug_log/2026-10-23/outputs/plan_offline/scenes_1023.npz) · `prep_scenes.txt` ② PC `gen_yaml.py 출력.yaml 패딩 변형…` — planner_server 설정(기록 지도의 치명 · 미지 칸만 static 층, inflation 0.70/2.0 · 풋프린트 재구성; 변형 이름 `Smac_R{R×100}_C{cp×10}[_A{해석×10}][_B{칸}]`) ③ PC `up_bundle.sh` — yaml · 스크립트 · npz 를 base64 로 담은 묶음(10-26: CR 제거 추가) ④ Jetson `run_planner_offline.sh 변형들` — `ROS_DOMAIN_ID=42` 에 planner_server + 수명 관리자 + map→base_link 고정 TF, `query_planners.py` 실행 뒤 정리 ⑤ Jetson `query_planners.py` — 장면마다 `/offline_map` 발행 → 재구성 코스트맵이 기록과 같은 크기 · 치명 칸 수가 될 때까지 대기 → 칸 일치율 → planner_id 마다 `ComputePathToPose(use_start)` ⑥ PC `anal_plan_compare.py` — 차체 ↔ 상자(경로 자세마다 차체 사각형, NavFn 은 접선 yaw) · 중심 여유 · 치명까지 · 길이 · 0.3 m 창 최대 꺾임 · 계획 시간 + 그림 ⑦ PC `anal_fp_global.py` — 차체(+ 패딩) 다각형이 전역 치명 칸에 걸리는지(출발 · 목표 · 실제 궤적) ⑧ `kill_planoff.sh` 잔재 정리.
- 출력: `outputs/plan_offline/` 전부(위 색인). 재구성 일치는 `run_planoff_*.txt` 장면 줄(패딩 0.01 판 1.0000 · 패딩 0 판 0.64).
- 쓰인 곳: §22.2 판정 · 계획서 §8.
- 계보 · 결함: **한 서버에 Smac 플러그인 여럿 = static 상태 공유 → 변형 간 비교 무효**(10-26 §6.1) → 10-26 `run_variants.sh`(변형마다 프로세스) · `gen_yaml.py` 에 `_NS` 등 추가 · 장면 json 입력(10-26 §20). 10-26 엔 CRLF 때문에 정리 단계가 안 돌아 planner_server 가 도메인 42 에 쌓인 일도 있었다(`up_bundle.sh` 주석). 지금 다시 쓸 수 있음 — 단 `run_variants.sh` 경유로.

### up_palign_1023.sh · prep_rp_1023.sh · chk_rp_cfg.sh — 배포 · prep · 확인 (Jetson, 로버 안 움직임)
- `up_palign_1023.sh [값=28.0]`: Jetson `~/ros2_ws/src` · `install` 의 `nav2_params.yaml` 에서 `PathAlignCritic … cost_weight:` 숫자만 정규식으로 바꿈, 실행 중 값은 안 바꿈(10-14 교훈 — 다음 prep 으로 적용). 출력 `up_palign_1023.txt` · `_revert.txt`(14.0). ⚠ 설치본이 src 링크가 아니면 두 파일을 따로 씀 — 출력에 `ls -l` 로 남김.
- `prep_rp_1023.sh`: `REPLAN_HZ=0.01 bash /tmp/prep_patrol.sh lite` + 주요 줄만 거름 + visual_preset · 주 EKF odom1 · rf2o 수 · `/tmp/nav_to_pose_active.xml` 의 RateController 확인. 출력 `prep_rp_1023_{1..5,5b}.txt` — 끝 줄이 끊겨 `chk_rp_cfg.sh`(확인 줄만)를 따로 만든 것(§17.1).

### (10-21 · 10-22 판) anal_stops.py · anal_dip_events.py · anal_nav_ms.py · anal_contact.py
- `anal_nav_ms.py nav2.log 시작 끝`: nav2 로그 사건을 0.01 s KST 시각 줄로(`Message Filter` · `tick rate` 줄 제외, 10-22 부터 'Control loop missed' 를 남김 — 10-21 §12.2 교훈) → `nav_events_ms_<run>.txt`.
- `anal_stops.py bag [사건파일]`(10-21): EKF |v| < 0.01 · |ω| < 0.05 가 `MIN_STOP`(기본 1.0, 10-22 · 23 출력은 0.5 s) 넘게 이어진 구간 + 그동안 명령 · 앞 ±30° 라이다 · stuck · nav2 사건. ⚠ 머리말은 '1 s 넘게', 출력 머리는 '0.5 s 넘게' — 환경 변수로 준 값(12 행).
- `anal_dip_events.py bag 사건파일`(10-21): 전진 명령이 < 0.01 로 떨어진 묶음마다 앞 2 s ~ 뒤 0.5 s 사건을 나란히 → '짧은 멈칫' 수와 A · B · C 분류의 원천.
- `anal_contact.py bag [D=0.10]`(10-22): map 기준 차체 사각형 ↔ 기록 상자 사각형 최소 거리가 D 안인 구간 + 그 순간 상자 영역 칸 수(로컬 · 전역 · 조각). B0 '실제 여유' 의 주 도구 — odom→base_link `/tf` 를 두 개에 하나씩(61 행 `OB[::2]`) 써서 거의 매 메시지. 문턱 D 밖이면 줄이 없다(f2rp1 은 0.12 m 문턱에 든 순간이 없어 `anal_contact_f2rp1.txt` 가 머리 줄뿐 → 15.4 는 `anal_track_dev` 1 s 표본에서 옴).

## 10. 용어
- **B0(결함 기준선)**: Phase P(계획기 교체) 전에 고정한 NavFn 구성과 그 성적. '합격한 기준선' 이 아니라 알려진 결함(상자 옆 3~15 cm)까지 함께 고정해, 바꾼 뒤의 성적을 같은 코스 · 같은 도구로 견주려는 것. 태그 `navfn-baseline-20261023`.
- **톱니 누적(재계획 고정)**: 전역 경로를 일정 주기로 **로버 자리에서** 다시 그리면, 매 주기 생긴 작은 옆 치우침이 새 경로의 출발점이 되어 원래 선으로 돌아가지 않고 쌓이는 것(10-23 §14 의 추정 기전).
- **굽은 곳 안쪽 깎기**: MPPI 가 굽은 경로의 안쪽으로 질러가는 성질. 복귀 길에선 상자가 꺾임 안쪽이라 상자 쪽 치우침이 됨(§22.3).
- **PathAlignCritic 점유율 조건**: Humble MPPI 는 컨트롤러 경로 구간의 '못 쓰는 점'(내접 · 치명) 비율이 `max_path_occupancy_ratio`(0.05)를 넘고 2 개 초과면 그 주기에 PathAlign 을 건너뜀(동적 물체가 경로를 막을 때 경로에 붙지 않게).
- **해석 확장(analytic expansion)**: Smac Hybrid 가 탐색 중 목표까지 Dubins/RS 곡선을 바로 그어 차체만 안 닿으면 붙이는 단축(1.1.20 기본 비율 3.5 · 최대 3 m, 비용은 안 봄 — 10-23 의 이해).
- **Dubins · Reeds-Shepp · State Lattice(diff)**: 전진만 · 최소 회전반경 원호 + 직선 / 전진 · 후진 / 미리 만든 운동 원형(차동구동은 제자리 회전 포함)으로 탐색 — 우리 스키드스티어엔 Lattice(diff)가 맞는 모델(10-23 §23).
- **GoalCritic 1.0 m**: MPPI 목표 크리틱이 켜지는 거리. 그 안에서 경로 방향과 목표 방위가 크게 엇갈리면 '천천히 출발' 해에 갇힐 수 있음(§7, 추정).
