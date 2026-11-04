# 상자 옆 정지 — 기전(라이다 아래 낮은 상자 옆에서 '서 있는 자세부터 닿음' 이 되는 까닭)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **조사 중(10-15 시점) — 정지 기전은 측정으로 확인, 과장의 근원은 미확정.** 정지 = MPPI 가 카메라만 본 치명 칸 옆으로 서서히 붙다가(경로가 상자 끝에서 0.22~0.29 m) 정확 여유 **2.7~4.4 cm** 띠 안에서 Nav2 칸 검사의 꼭짓점 내림 위치가 바뀌는 순간 서 있는 자세가 99 → 100 으로 뒤집혀 모든 후보 · 후진이 거부되는 것(10-15 §28, 실패 3 건 + 10-13 §8 시뮬 재현). 그 칸이 실제 면보다 로버 쪽으로 나와 있는 양은 주행 중 **+5~10 cm**(기록 상자 대비 4 주행, 10-15 §29.4), 정지 관측은 0~3 cm(§22 · §24). 과장의 내역(기억 밀림 · 각도 · 격자 계단 · 먼 첫 관측 · 깊이)은 몇 cm 씩 겹친다는 데까지(추정) | 10-12 §2, 10-13 §4.4 ~ §13, 10-14 §1 · §4 ~ §5 · §20 · §22 ~ §22.2 · §24 ~ §25, 10-15 §3 ~ §13 · §18 ~ §21 · §22 ~ §24.1 · §28 ~ §28.1 · §29.4 ~ §29.5 · §32 ~ §34 (이 카드), 이후 10-19 ~ | [10-13 §4.4](../debug_log/2026-10-13/SUMMARY.md)(f2o1 목표 3 이 출발점 앞 상자 옆에서 ABORTED — 사용자 "정면 왼쪽에 상자, 닿지는 않았다") · 앞 모양 10-12 §2(f2f1 복귀 상자 ② 옆 멈칫) | 기전 분석만 — 설정 변경은 대책 카드 몫. 이 카드에서 남긴 도구: `Docs/tools/anal_box_history.py` · `fig_stop_costmap.py` · `fig_box_approach_video.py` · `anal_box_layers.py` · `anal_box_pass.py` · `anal_mppi_sim.py`(`fpchk`) · `anal_plan_keepout.py` | [상자 옆 정지 대책](box-side-stall-remedies.md)(감쇠 · cost_weight · 패딩 0 · 통합 거리 · MonotoneEscape · ClearanceBandCritic · site 거리) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(앞 시기, 같은 상자) · [실행 중 패딩 변경 · pad_relief](pad-relief-runtime-padding.md) · [남서 구석 방향 맞춤 정체](southwest-orient-stall.md) · [CopyPath · 끝 방향](bt-copypath-end-yaw.md) · [F2 기준선 no5](f2-baseline-no5.md) · [포화 · mppi_viz](network-saturation-mppi-viz.md)(10-12 §2 의 CPU · TF 끊김) · [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md) · [회전 중 장애물 번짐](rotation-obstacle-smear.md)(odom 기억 번짐의 앞 모양) · [inflation · padding 역할](inflation-padding-roles.md) · [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md) · [F0 회전 옆 밀림](f0-rotation-side-slip.md)(09-23 f0a1 '4.4 cm 에서 LETHAL') · [카메라 상자 칸 과장의 근원](box-exaggeration-source.md)(8 기) · [복귀 길 상자 칸](box-return-cells.md)(8 기) · [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md) · [경로 추종 · B0](path-tracking-replan-b0.md) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) (8 기) · [nvblox 층 TF 조회 실패 처리](nvblox-layer-tf-drop.md)(전역만 — 이 기전과 무관, 9 기) · [MPPI 굽은 곳 · PathAlign 28/5](mppi-corner-cut-pathalign.md) (9 기) |

**한 줄**: 출발점 동쪽의 **라이다(0.185 m)보다 낮은 시험 상자**(사용자가 일부러 둔 물체, 10-14 §25)와 서쪽 통로의 낮은 상자 옆에서 로버가 실제로는 8~11 cm 떨어져 있는데(사용자 줄자 10-13 §5.6 · 10-15 §18.2) Nav2 가 '후보 전부 충돌 → 후진 0.0 s 실패 → 대기 × 2 → 포기' 로 멈춘다. 10-13 에는 **경로 근접 0.22~0.29 m + 기억된 상자의 오도메트리 밀림 4~5 cm + 칸 단위 검사 약 5 cm** 로 설명했고(§12.2, 밀림 크기는 SLAM 보정 변화로 잰 값), 10-14 는 그 밀림을 각도 몫 약 2 cm · 격자 계단 평균 3.5 cm · 먼 첫 관측 한 줄로 쪼갰으며(§4.2 · §5), 10-15 는 판정이 뒤집히는 순간을 프레임 단위로 잡아 **뒤집힘 띠 2.7~4.4 cm** 를 측정하고(§28), 카메라 칸이 주행 중 실제 면보다 **+5~10 cm** 나와 있음을 기록 상자와 견줘 쟀다(§29.4). '지도가 갑자기 바뀌어서' 도 '미끄러져서' 도 아니다(§28 (가) · (나) 기각).

---

## 1. 증상
- **f2f1 복귀(10-12 §2)** — 상자 ② 옆 구간(map x 2.6 → 0.4)이 f2e2 44 s → **67 s**, 느린 시간 1 → 11 s, 후진 0 → 4 s. 차체 ↔ 치명 칸 최소 0.06 m 는 두 주행이 같았다([`f2f1_box_smooth.txt`](../debug_log/2026-10-12/outputs/f2f1_box_smooth.txt) 요약 줄 "평균 v 0.062 m/s · 느린 시간(v<0.04) 11 s · 후진 포함 4 s … 치명까지 최소 0.06 m" / f2e2 "평균 v 0.078 · 1 s · 0 s … 0.06 m"). 직접 원인은 CPU 포화로 Nav2 가 끊긴 것(→ [포화 카드](network-saturation-mppi-viz.md)), 상자 자리 자체의 문제는 이 시기 뒤에 드러남.
- **f2o1 목표 3(10-13 §4.4)** — 출발점 1.45 m 앞 map (1.437, 0.218, 161.8°)에서 ABORTED 98.7 s. Nav2 원문([`navlog_f2o1.txt`](../debug_log/2026-10-13/outputs/navlog_f2o1.txt) 요지, SUMMARY §4.4 인용): 13:33:24 smoother "collision at x 1.51, y 0.19" → 13:33:25 "Optimizer fail to compute path" 14 회 → 후진 3 회 "Collision Ahead" → Goal failed. 충돌 좌표가 로버 자기 자리.
- **사용자 실측** — f2p1 정지 "옆 트랙과 상자 사이 **11 cm**"(10-13 §5.6), f2v3 정지 "왼쪽 앞끝 ↔ 상자 대각선 **8~9 cm**"(10-15 §18.2). 같은 순간 코스트맵은 5.4 cm(차체 ↔ 칸 중심) · 2.7 cm(패딩 차체 ↔ 칸 중심).
- **같은 자리 반복** — 출발점 상자: f2o1 · f2p1 · f2q1(10-13), f2r1 실패 2 회 · f2u2(10-14), f2v4(10-15). 서쪽 통로 상자: f2t1(10-14), f2v1 · f2v3(10-15). 10-15 기준선 6 회 중 실패 3 회가 모두 이 기전(§21).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 앞 시기 10-08 §3.5 | f2e1 접촉 원인 | 근접 정면 상자 치명 → 내접 강등 | 낮은 상자 옆 여유 0.06 m 를 '남은 것' 으로 둠 | [낮은 상자 카드](low-box-global-memory.md) |
| 10-12 §2 | f2f1 복귀 상자 ② 구간 비교(`box_smooth.py` · `top_eval.py` · `gap_eval.py`) | 위 §1. CPU 69 → 92 %, odom→base_link TF 0.5 s 넘는 끊김 30 군데(그중 22 이 구간), 10:35:09 `PathBlockedAhead`(앞 경로 (1.18, 0.24) 비용 99 가 2 s) | 멈칫의 직접 원인 = 연산 부하로 Nav2 중단 · 재시작 반복(측정). 서 있으면 앞 경로 99 가 2 s 이어져 PathBlockedAhead 가 또 끊는 '멈춤이 멈춤을 부르는 고리'(추정). 상자 옆 여유 자체는 f2e2 와 같다고 봄 | [`f2f1_box_smooth.txt`](../debug_log/2026-10-12/outputs/f2f1_box_smooth.txt) · [`f2f1_cpu.txt`](../debug_log/2026-10-12/outputs/f2f1_cpu.txt) · [`f2f1_gaps.txt`](../debug_log/2026-10-12/outputs/f2f1_gaps.txt) · [`f2f1_navlog.txt`](../debug_log/2026-10-12/outputs/f2f1_navlog.txt) · 그림 [`2026-10-12_f2f1_box_stall.png`](../04_navigation/figures/2026-10-12_f2f1_box_stall.png) |
| 10-13 §4.4 | f2o1(러너 수정 검증) | 목표 3 ABORTED(§1). 통신 징후 없음(소켓 손실 0, `/tf` 49~51 Hz). 목표 3 구간 휠 231.7° 대 EKF 166.7° | 통신 아닌 주행 문제. 실제 물체 · 유령 · 위치 밀림 중 무엇인지 미구분 | [`run_f2o1.txt`](../debug_log/2026-10-13/outputs/run_f2o1.txt) · [`navlog_f2o1.txt`](../debug_log/2026-10-13/outputs/navlog_f2o1.txt) · [`f2o1.csv`](../debug_log/2026-10-13/outputs/f2o1.csv) |
| 10-13 §4.5 | 정지 순간 코스트맵 vs 라이다(`fig_stop_costmap.py`) | 치명 칸 중심까지 차체 여유 21.2 → 11.6 → **5.1 → 4.8 cm**(13:33:19 → 26), 둘레 최대 비용 96 → **99**, 그 자리 라이다 점 없음(라이다 최소 여유 26.5 cm 는 다른 물체) | 유령 아닌 **실제 상자**(사용자 위치와 일치), 카메라 층만 봄. 풋프린트 둘레가 99 에 들어가 후보 전부 충돌 · 후진 거부(추정). 09-23 f0a1 과 같은 모양 | [`f2o1_stop.txt`](../debug_log/2026-10-13/outputs/f2o1_stop.txt) · [`2026-10-13_f2o1_stop_costmap.png`](../04_navigation/figures/2026-10-13_f2o1_stop_costmap.png) |
| 10-13 §4.6 | '붙어 갔나, 늦게 떴나'(`anal_box_history.py` · 영상 `fig_box_approach_video.py`) | 상자 끝 = 정지 때 차체 최근접 치명 덩어리 4 칸 (1.23, 0.03). 전역 0/4(13:31:43~13:32:55, 3.3~4.7 m) → 첫 경로가 상자 끝을 지나감(0.00~0.02 m, 13:32:17 · 19 만 0.16~0.19) → 13:33:02(1.41 m) 3/4 · 경로 0.26 m 로 비킴 → 이후 경로 **0.22~0.29 m** | ① 전역은 잊었다가 1.4~1.7 m 에서 다시 봄 — 늦었지만 1 m · 20 s 여유 ② **경로 자체가 가까웠고 MPPI 가 넓히지 않음 = 직접 원인** ③ 북쪽은 0.4 m 이상 비어 있음 | [`f2o1_box_history.txt`](../debug_log/2026-10-13/outputs/f2o1_box_history.txt) · [`2026-10-13_f2o1_plan_through_box.png`](../04_navigation/figures/2026-10-13_f2o1_plan_through_box.png) · [`2026-10-13_f2o1_stop_at_box.png`](../04_navigation/figures/2026-10-13_f2o1_stop_at_box.png) · 영상 `2026-10-13/videos/f2o1_box_approach.mp4`(git 제외) |
| 10-13 §5.4 | 정지 자세에서 움직여 본 풋프린트 비용(`anal_f2o1_options.py` C) | 직후진 0~30 cm · 직전진 · 오른쪽 회전 5~40° 모두 **99**, 왼쪽 회전 10° 이상 100 | 기하로는 직후진 · 오른쪽 회전이 충돌 아님 → Nav2 꼭짓점 칸 반올림 + 칸 단위 직선의 '계단' 이 약 5 cm 를 먹는다(추정, 소스 대조 안 함). BT 후진 추가는 효과 없음 | [`f2o1_options.txt`](../debug_log/2026-10-13/outputs/f2o1_options.txt) 38~44 행 |
| 10-13 §5.6 | f2p1(전역 감쇠 3.0 시험 — 대책은 E 카드) | 같은 자리 재정지 (1.347, 0.263). 상자 끝 4 칸 (1.29, 0.02)이 0.34 m 옆까지 **1/4** → 정지 5 s 전 4/4. 실측 11 cm 대 코스트맵 5.4 cm(칸 가장자리 2.9) | '이번엔 늦게 떴다' ❌(§6.2 정정, 실수 ①). 코스트맵 상자 끝이 실제보다 6~8 cm 로버 쪽, 11 − 6 − 5 ≈ 0 → Nav2 는 '이미 충돌' | [`f2p1_box_history.txt`](../debug_log/2026-10-13/outputs/f2p1_box_history.txt) · [`run_f2p1.txt`](../debug_log/2026-10-13/outputs/run_f2p1.txt) · [`2026-10-13_f2p1_stop_at_box.png`](../04_navigation/figures/2026-10-13_f2p1_stop_at_box.png) |
| 10-13 §6.2 | 상자 끝 칸을 어느 층이 언제 채웠나(`anal_box_layers.py`) | 라이다 점 두 주행 모두 **0**. nvblox 값이 처음 생긴 때 1.51 m(f2o1 13:33:01 · f2p1 14:14:23~24). 슬라이스 header = **odom**. 정지까지 map→odom 변화 f2p1 y +5.0 · f2o1 y +4.1 cm. f2p1 의 1/4 → 4/4 순간(14:14:35 · 44 · 48)은 보정 값이 바뀐 순간과 일치 | 상자는 1.5 m 에서 관측돼 odom 에 기억 → 시야(±43°) 밖으로 나간 뒤 다시 안 보임 → 오도메트리가 4~6 cm 어긋난 만큼 실제와 어긋난 자리에 남음(추정, SLAM 보정이 참이라는 가정). 여유 손실 = 밀림 ~5 + 칸 검사 ~5 cm | [`f2o1_box_layers.txt`](../debug_log/2026-10-13/outputs/f2o1_box_layers.txt) · [`f2p1_box_layers.txt`](../debug_log/2026-10-13/outputs/f2p1_box_layers.txt) |
| 10-13 §7 · §7.1 | MPPI 오프라인 시뮬(job776 판, 점 표본 둘레 검사)로 재현 | 최소 여유(차체 ↔ 칸 중심 − 반 칸): f2o1 실제 2.3 · 씨앗 7.4 · 9.2 · **1.8**, f2p1 실제 2.9 · 10.0 · 10.5 · **1.6**. 멈춤 0/6 | 선언 기준 **재현 안 됨**. 씨앗 3 은 실제만큼 붙고도 지나감 → 차이는 Nav2 칸 단위 검사(추정) | [`sim_repro.txt`](../debug_log/2026-10-13/outputs/sim_repro.txt) · `jobs/run_sim_box.sh` |
| 10-13 §8 · §8.1 | 시뮬에 Nav2 방식 둘레 검사(`anal_mppi_sim.py fpchk=1`) | 씨앗 3: f2o1 최소 **2.8 cm** · +24.1 s(= 13:33:23)부터 실패 59 주기 · 끝 3 s 이동 0 / f2p1 **2.7 cm** · +24.6 s(= 14:14:47) 104 주기. 나머지 9 씨앗 5.1~11.1 cm, 실패 0 | **'칸 가장자리까지 3 cm 안팎이면 현재 자세부터 충돌' 시뮬로 재현(추정 지지).** 그만큼 붙는 비율 10 % vs 실제 2/5 → 시뮬이 낙관적일 수 있음 | [`sim_repro_fp.txt`](../debug_log/2026-10-13/outputs/sim_repro_fp.txt) · [`sim_repro_fp2.txt`](../debug_log/2026-10-13/outputs/sim_repro_fp2.txt) |
| 10-13 §10 | '포화가 있던 주행은 피해 갔나'(`anal_box_pass.py`, 상자 구역 복귀 방향 11 주행) | 통과 6 회 최소 여유 **2.8~4.7 cm**, 정지 2 회 2.2 · 1.8 cm. 포화 주행 4 회 중 3 회는 상자 전에 중단 | 포화가 도움 됐다는 근거 없음. **이 상자 옆은 원래 아슬아슬, 통과/정지는 1~2 cm 로 갈림**. 시뮬은 이 자리에서 실제보다 약 5 cm 넉넉 | [`box_pass.txt`](../debug_log/2026-10-13/outputs/box_pass.txt) |
| 10-13 §12.2 | 그날 시도 정리(대책은 [E 카드](box-side-stall-remedies.md)) | 감쇠 3.0 · BT 후진 · 패딩 0 · cost_weight 3 배 · 전역 기억 — 모두 기각 · 보류 | 남은 사실: 9 회 모두 코스트맵 여유 2~5 cm, 원인 ① 경로 0.22~0.29 m ② 기억 밀림 4~5 cm ③ 칸 검사 약 5 cm | 10-13 §12.2 |
| 10-13 §13 | 사용자 "기억 말고 다시 봤을 때 갱신" | 다시 보면 갱신은 이미 됨(1.51 m 재관측 → 2 s 안 경로 비킴). 멀리서 잊는 원인 = `map_clearing_radius_m: 3.0`(f2o1 0/4 된 13:31:43 에 로버 3.25 m). 재관측 1.5 m = 통합 거리 1.4 | 일찍 갱신해도 이 정지는 안 풀림(추정): 밀림은 상자가 시야 밖으로 나간 **뒤** 생김 | `config/nvblox_local.yaml`(그날 판) · 10-13 §13 |
| 10-14 §1 | 전역 카메라 칸 둘레 금지 띠 D 오프라인 재계획(`anal_plan_keepout.py`, 3 주행 71 계획) | D 0.30 까지 경로 없음 0/71 · 상자 끝 거리 +5~10 cm, **D 0.35 에서 10/71 막힘 — 모두 그 상자 옆 '통로 막힘'** | 코스트맵상 통로 폭 약 0.7 m(차체 빼면 양쪽 37 cm), 그 37 cm 를 상자 쪽 5 · 반대 30 cm 로 씀. 여유 한 칸 → 사용자 기각(§4.1) | [`keepout_all.txt`](../debug_log/2026-10-14/outputs/keepout_all.txt) |
| 10-14 §4.2 | 사용자 '각도 문제도' → 밀림을 위치 몫 · 각도 몫으로(`anal_box_shift_angle.py`) | f2o1 1.48 m · −0.86° → 전체 4.1 = 위치 3.1 + 각도 **2.2 cm**, f2p1 6.2 = 4.5 + **1.8 cm** | 1° 미만 각 차이가 1.5 m 에서 2 cm. 통합 거리 2.0 은 이를 키울 수 있음 | [`box_shift_angle.txt`](../debug_log/2026-10-14/outputs/box_shift_angle.txt) |
| 10-14 §5 | 사용자가 말한 '각도' = ① 비스듬한 번짐 ② 격자 계단(`anal_box_edge_growth.py`) | ① odom 고정 7 × 7 창: 처음 한꺼번에 찍힐 때(1.47 m · 1.43 m) 로버 쪽 한 줄 더(2 칸), 0.68~0.69 m 에서 지워짐, 정지 때는 없음 ② 18 × 11 cm 상자를 5 cm 격자에: 0° 평균 2.6 · 최대 5.0, 5° 3.5 · 5.4, 45° 5.4 · 7.1 cm | 실측 11 vs 코스트맵 2.9 cm 차 약 8 cm ≈ 계단 3.5 + 각도 2 + 위치 3~4.5(합 8.5~10, 방향이 모두 로버 쪽이라는 가정). 멀리서 볼수록 불리 → 통합 거리 1.4 로 되돌림(§6, 사용자) | [`box_edge_growth.txt`](../debug_log/2026-10-14/outputs/box_edge_growth.txt) |
| 10-14 §20 | f2t1 남서 통로에서 상자 쪽으로 머리를 돌림(`anal_sw_turn.py` · `anal_sw_yawsweep.py`) | 선 채로 14 s(v ≈ 0, ω +0.02~+0.07) −75 → −66°, 경로 −86° 그대로, 가까운 쪽(왼쪽 여유 5.6~8.8 cm)으로. 컨트롤러 실패 0, 앞 경로 칸 62~77 → '갈 수 없어서' 아님. −51° 부터 충돌 | MPPI 소스: CostCritic 은 중심 칸 비용만(제자리 회전엔 거의 그대로), PathAngle 은 28.6° 안이면 꺼짐, PathAlign 은 위치만 → 서 있으면 방향 구속 없음(추론). '이유 없이 선 것' 은 pad_relief 토글 멈칫(§21) | [`anal_sw_turn_f2t1.txt`](../debug_log/2026-10-14/outputs/anal_sw_turn_f2t1.txt) · [`anal_sw_turn_f2s2.txt`](../debug_log/2026-10-14/outputs/anal_sw_turn_f2s2.txt) · [`anal_sw_yawsweep_f2t1.txt`](../debug_log/2026-10-14/outputs/anal_sw_yawsweep_f2t1.txt) · [pad_relief 카드](pad-relief-runtime-padding.md) |
| 10-14 §22 · §22.1 | f2u2(B) 복귀 상자 끝 사건(`anal_sw_turn.py` 변형 · `anal_box_edge_map.py` · `anal_blob_src.py`) | 여유 4.7~5.5 cm 진행 중 16:30:06.6 새 경로가 상자 끝을 감아 돔(−136°) → 후보 전부 충돌 2 회 → 후진 즉시 실패 → 대기 → 15 cm 더 나아간 자리의 새 경로 −170° 로 통과. 상자 끝 앞 구역 치명 A 1~2 · **B 6~7 개**, 라이다 0 | B 는 지도상 3 cm 바깥인데 여유는 2 cm 작음 → 코스트맵 쪽 장애물이 더 나와 있었음. map→odom yaw 차(0.7°)로는 15 cm 덩어리 차를 설명 못 함. 빠져나온 이유 = 다시 짠 경로가 곧았음(측정) | [`anal_box_f2u2.txt`](../debug_log/2026-10-14/outputs/anal_box_f2u2.txt) · [`anal_box_f2u1.txt`](../debug_log/2026-10-14/outputs/anal_box_f2u1.txt) · [`anal_box_edge_map_f2u.txt`](../debug_log/2026-10-14/outputs/anal_box_edge_map_f2u.txt) |
| 10-14 §22.2 | A2(f2u3) 같은 자리 | 여유 **4.2 cm** 에서 상자 반대쪽으로 꺾어(ω −0.16~−0.24) 통과, 실패 0. 경로 +171 ~ −177°(곧음) | 지나느냐는 **그 순간 계획기가 상자 끝을 감아 도는 경로를 내느냐**에 크게 달림(추론) | [`anal_box_f2u3.txt`](../debug_log/2026-10-14/outputs/anal_box_f2u3.txt) |
| 10-14 §24 | 계획기 경로가 언제 상자를 가로지르나(`anal_navfn_replay.py` · `anal_slice_blob.py` · `fig_box_end_plans.py`) | 정상 6 장(내접 0 점, 재현과 방향 차 ≤ 6°). **B 16:30:06.6 만** /plan 이 253 칸 20/55 점을 지남(재현 경로는 +180°). 전역 지도 15 장 어디서도 그 경로는 20 점 내접, 슬라이스 덩어리 끊김 없음, 16:30:05.7 전역 발행 하나 빠짐 | NavFn(253 이상 장애물)로는 나올 수 없는 경로 — 원인 모름 ？. 실패 두 종류: **이상 경로형**(1 회) · **좁은 여유형**(f2r1 11:26:39). nav2.log 가 덮여 경고 확인 불가 → prep 에 기록 보관(§25) | [`anal_navfn_replay_f2u.txt`](../debug_log/2026-10-14/outputs/anal_navfn_replay_f2u.txt) · [`anal_slice_blob_f2u2.txt`](../debug_log/2026-10-14/outputs/anal_slice_blob_f2u2.txt) · [`box_end_plans_f2u.png`](../debug_log/2026-10-14/figures/box_end_plans_f2u.png) |
| 10-14 §25 | 사용자 결정 | 출발점 작은 상자 = **라이다 아래 물체 감지 시험용**(치우지 않음). 좁은 여유형은 지금 시스템으로 어느 정도 됨 → 이 자리는 지금 안 바꿈 | 이 자리의 여유 · 정지는 낮은 물체 감지 · 회피 성능의 측정값으로 읽음 | 10-14 §25 |
| 10-15 §3 · §5 · §6 | f2v1 서쪽 통로 남쪽 정지(`anal_ahead_cells.py` · `anal_motion_probe.py` · `anal_near_cells_src.py` · `fig_stall_cells.py`) | 멈춘 순간 왼쪽 치명 칸 **3.6 cm**, 회전 ±15~30° 이상 · 전진+회전 모두 닿음, 직진 · 후진만 겨우. 8 cm 안 칸 7 개 모두 **라이다 0**, 라이다 벽보다 5~8 cm 통로 안쪽. 9 분 뒤 복귀 출발엔 0 개(최근접 10.1 cm) | 라이다 높이 아래 무언가를 카메라가 찍었고, 차체 옆으로 오자 시야 밖이라 기억으로 남았다가 감쇠로 사라짐(추정). Nav2 는 12 s 만에 포기, 칸 감쇠는 약 80 s | [`anal_motion_probe.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe.txt) · [`anal_near_cells_src.txt`](../debug_log/2026-10-15/outputs/anal_near_cells_src.txt) · [`stall_cells_westpass.png`](../debug_log/2026-10-15/figures/stall_cells_westpass.png) · [`navlog_f2v1.txt`](../debug_log/2026-10-15/outputs/navlog_f2v1.txt) |
| 10-15 §7 | 사용자 '카메라 가장자리 왜곡?'(`anal_cell_first_seen.py`) | 카메라 칸 15 개 모두 처음 찍힌 방위 **+21~+27°** · 거리 **1.27~1.30 m**(통합 한도 1.4 안). 찍힌 뒤 약 16 s 시야 안 | 가장자리 왜곡 아님(측정). '바깥 줄 30 % 깜빡임' ❌(§12 정정, 실수 ③) | [`anal_cell_first_seen_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_first_seen_f2v1.txt) |
| 10-15 §8 | 사용자 현장 확인 | "라이다보다 낮은 상자 위에 종이백, 종이백은 상자보다 약 5 cm 들어감" → 라이다 선 = 종이백 앞면, 안쪽 카메라 줄 = 상자 앞면 | 로버를 멈춘 칸 = 과장 칸(실제 면까지 약 8~9 cm, 추정). 로버가 통로 가운데보다 13 cm 상자 쪽 | 10-15 §8 |
| 10-15 §9 ~ §11 | 목표를 가운데로 · 카메라가 과소평가하나 · 저장 지도 서쪽 벽(`anal_path_center.py` · `anal_cam_vs_lidar.py` · `anal_map_vs_lidar.py` · `anal_mapfix_replan.py`) | 목표 이동 12 경우 모두 경로 x −1.765~−1.715 · 동쪽 여유 11.0 cm. 라이다 면 대비 카메라: 앞 61~65 % · 같음 22~24 % · **뒤 10~12 %** · 누락 1.6~3.1 %. 저장 지도 서쪽 벽 약 10 cm 두꺼움(3 순간 −12.4~−12.8 cm, 동쪽 −3.2~−3.6), 고친 사본도 경로 그대로 | 길은 지도 단면이 정함. '과소 → (가) 부적절' ❌(§9.3 정정, 실수 ④). '서쪽도 카메라 과장' ❌ → 저장 지도(실수 ⑤) | [`anal_path_center.txt`](../debug_log/2026-10-15/outputs/anal_path_center.txt) · [`anal_cam_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar.txt) · [`anal_cam_vs_lidar_breakdown.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar_breakdown.txt) · [`anal_map_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_map_vs_lidar.txt) · [`anal_mapfix_replan.txt`](../debug_log/2026-10-15/outputs/anal_mapfix_replan.txt) |
| 10-15 §12 | 깜빡이는 칸만 낮추기 오프라인(`anal_flicker_filter.py` · `anal_cell_ratio_odom.py` · `anal_grid_phase.py` · `anal_lidar_strip.py`) | odom 칸 고정: 안쪽 줄 치명 67~93 % · **바깥 줄(멈춘 칸 포함) 90~91 %** · 더 바깥 3~6 %. 슬라이스 ↔ 코스트맵 원점 위상차 0 | 불합격. 카메라는 그 상자를 **꾸준히 약 한 칸 두껍게** 찍음 | [`anal_cell_ratio_odom_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_ratio_odom_f2v1.txt) · [`anal_flicker_westbox_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_flicker_westbox_f2v1.txt) · [`anal_grid_phase_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_grid_phase_f2v1.txt) · [`anal_lidar_strip_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_lidar_strip_f2v1.txt) |
| 10-15 §13 | 사용자 줄자: 상자 앞면 = 종이백 + 5.8~6.0 cm | 실제 면 x ≈ −1.43 → 바깥 줄(−1.455~−1.505)은 전부 빈 공간인데 90~100 % 점유 | 라이다 아래 이 상자를 카메라는 **실제 면보다 약 7 cm(1.4 칸) 앞까지** 찍음. site 거리 2.0(예제값, 검토 안 함)이 후보 | 10-15 §13 · `jobs/chk_nvblox_site.sh` |
| 10-15 §18 · §18.2 · §20 | f2v3(서쪽 통로) · f2v4(출발점 상자) 정지 | f2v3 앞 왼쪽 모서리 ↔ 칸 2.7 cm(사용자 8~9 cm, 카메라만 · 상자 북쪽 모서리), f2v4 4.3 cm(차체 왼쪽, 칸 2 개 라이다 0). 둘 다 후진 0.0 s 실패 · 약 12 s 포기 | 세 실패 모두 같은 기전: 카메라 과장 약 6~7 cm + 칸 검사(§21) | [`anal_motion_probe_f2v3.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v3.txt) · [`anal_near_cells_src_f2v3.txt`](../debug_log/2026-10-15/outputs/anal_near_cells_src_f2v3.txt) · [`anal_motion_probe_f2v4.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v4.txt) · [`anal_near_cells_src_f2v4.txt`](../debug_log/2026-10-15/outputs/anal_near_cells_src_f2v4.txt) · [`box_end_f2v4.png`](../debug_log/2026-10-15/figures/box_end_f2v4.png) |
| 10-15 §18.3 · §19 | 9 분 뒤 복귀 f2v3r | 출발 순간 최근접 17.5 cm(라이다 종이백), 상자 모서리 카메라 칸 사라짐. 경로는 처음부터 북쪽(+85~+107°), 회전 중 카메라가 다시 봐 칸 2 → 12 | 복귀 성공 = 시야 밖 칸 감쇠 덕. ⚠ 그때 지도엔 실제 상자가 없음 → '대기 늘리기' 류가 위험한 근거. 사용자 '상자 쪽 경로를 고쳤다' 는 아님 | [`anal_motion_probe_f2v3r.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v3r.txt) · [`anal_replan_trace_f2v3r.txt`](../debug_log/2026-10-15/outputs/anal_replan_trace_f2v3r.txt) |
| 10-15 §22 ~ §23 | 정면 0.9 m 정지 관측(site 거리 A/B — 대책은 E 카드) | 두 값 모두 상자 앞면이 실제보다 약 3 cm 앞, **원시 점군부터 −2.3~−3.4 cm** | 정면 · 가까이 · 계속 보이면 거의 정확 → 과장은 비스듬한 먼 관측 쪽(추정) | [`box_face_A.txt`](../debug_log/2026-10-15/outputs/box_face_A.txt) · [`box_face_B.txt`](../debug_log/2026-10-15/outputs/box_face_B.txt) · [`box_site_AB.png`](../debug_log/2026-10-15/figures/box_site_AB.png) |
| 10-15 §24 · §24.1 | 옆면을 앞 측면에서 정지 관측(P1 1.0 m · P2 0.4 m, `chk_box_dump.py` · `anal_memory_shift.py`) | 옆면: 지도 · 코스트맵이 실제보다 **1.6~1.7 cm 안쪽**(덜 찍힘), 점군은 P2 에서 2.2 cm 로버 쪽. 기억 밀림 f2v1 2.1 cm(길이 방향, 옆 0.1~0.2) · f2v3 2.3 cm(로버에서 멀어지는 쪽) | **③ 가설 기각**(정지해서 옆면을 봐도 과장 없음). 기억 밀림도 6~7 cm 를 설명 못 함 → 몇 cm 짜리가 겹침(추정) | `outputs/boxdump/box_dump_P{1,2}.npz` · [`anal_memory_shift_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_memory_shift_f2v1.txt) · [`anal_memory_shift_f2v3.txt`](../debug_log/2026-10-15/outputs/anal_memory_shift_f2v3.txt) |
| 10-15 §28 · §28.1 | 멈춤에 '들어가는' 경로(`anal_stall_entry.py`, 실패 3 건 첫 실패 전 10 s) | 다가간 과정 5.9 → 3.6 · 14.6 → 2.7 · 23.1 → 3.2 cm. 99 → 100 넘어간 정확 여유 3.6 · **3.1** · 4.3 cm, 직전 99 였던 최소 4.4 · **2.7** · 3.2. fp_prev 도 100(지도 변화 아님), 옆 예측 오차 ≤ 0.3 cm. 최적 궤적에 칸 검사 치명 점이 0.6~6 s 전부터 | **멈춤 = MPPI 가 2.7~4.4 cm 띠 안까지 서서히 붙고, 띠 안에서 칸 내림 위상이 바뀌는 순간 서 있는 자세가 충돌로 뒤집힘**(측정). (가) 지도 변화 · (나) 미끄러짐 기각. 밟힌 칸은 카메라 치명 칸 자체(99 띠 아님) | [`anal_stall_entry.txt`](../debug_log/2026-10-15/outputs/anal_stall_entry.txt) |
| 10-15 §29.4 · §29.5 | 기록 상자 위치 vs 센서 상자(`anal_box_true_vs_map.py`, b910 4 주행) | 찍힌 북쪽 면 − 기록 북쪽 면 **+8.2 · +9.6 · +6.1 · +5.3 cm**, 실제 여유 최소 9.5 · 12.3 · 6.6 · 5.6 cm 대 지도 4.8 · 5.9 · 3.3 · 3.2. 남동쪽 덩어리 = 창문틀 · 드론(사용자, 실물) | **주행 중에는 로버 쪽으로 5~10 cm 과장**(정지 0~3 cm 보다 큼) — 움직이며 비스듬히 · 멀리서 찍을 때 생김(추정). 배치 오차 1~2 cm 못 가름. 여유 층 정리(과장 · 패딩 · 띠 · 칸 검사 · 팽창) | [`anal_box_true_vs_map.txt`](../debug_log/2026-10-15/outputs/anal_box_true_vs_map.txt) 47 · 93 · 142 · 213 행 · [`box_true_vs_map.png`](../debug_log/2026-10-15/figures/box_true_vs_map.png) |
| 10-15 §32 ~ §34 | f2w2 서쪽 통로 몸 틀기 · 안 멈춘 이유(`anal_cmd_timeline.py` · `fig_passage_f2w2.py`) | 상자 쪽 회전 두 자리(입구 ω +0.34 · 상자 끝 +0.27)가 크리틱 없던 f2v2 에도 같은 자리 · 같은 크기. f2w2 서 있는 자세 fp 100 **727 프레임 중 0**, 뒤집힘 띠 0 프레임(최소 4.9 · 통로 5.1 cm) | 몸 틀기는 연산 부담 탓 아님(통로 축이 꺾이는 경로를 따름, 경로 모양 미확인). 안 멈춘 직접 이유 = 띠에 안 들어감. f2v2 도 띠 안 12 프레임을 위상 운으로 통과 → '크리틱 때문' 은 1 회로 단정 못 함 | [`anal_cmd_timeline_f2w2.txt`](../debug_log/2026-10-15/outputs/anal_cmd_timeline_f2w2.txt) · [`anal_cmd_timeline_f2v2.txt`](../debug_log/2026-10-15/outputs/anal_cmd_timeline_f2v2.txt) · [`anal_band_run_no5.txt`](../debug_log/2026-10-15/outputs/anal_band_run_no5.txt) · [`passage_f2w2_south.png`](../debug_log/2026-10-15/figures/passage_f2w2_south.png) · [`missed_sec_f2w2.txt`](../debug_log/2026-10-15/outputs/missed_sec_f2w2.txt) |
| 이후 8 기 10-19 §4 · §6 · §13 | 과장 +5~10 cm 를 nvblox 조각으로 다시 재고, 깊이 bag(f2x1)을 컨테이너 nvblox 에 재생해 설정 A/B(→ [과장 근원 카드](box-exaggeration-source.md)) | 실시간 조각에서 이미 북 +5.3~+9.5 cm(코스트맵 판과 같음). 재생 R0 ✔, 통합 1.0 · site 1.0 · 가장자리 거르기 · 회전 프레임 빼기 모두 +5.3 · 범위까지 같음, 복셀 0.025 +6.7~6.9, map 좌표 기억 +7.0 | 과장은 **nvblox 출력에서**(측정). 설정 · 깊이 필터로 안 줄음 — 단 면 지표가 5 cm 계단이라 2~7 cm 차이는 못 가름(§13) | [`anal_slice_box_baseline.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_baseline.txt) · [`anal_slice_box_f2x1_ab.txt`](../debug_log/2026-10-19/outputs/anal_slice_box_f2x1_ab.txt) |
| 이후 8 기 10-19 §10 · §11 · §14 | 원시 깊이 점 → 지도 · 관측 → 통과 기억 밀림 분해(f2x1) | 출발 정면 관측 북 +1.7 cm(기록 위치 맞음). 복귀 길 상자 옆은 시야 밖 — 지도의 상자 = 남동쪽 회전 중 관측의 기억, 그 기억이 통과 순간까지 북(로버 쪽) **+2.7~+6.1 cm** 밀림 | 통과 순간 상자 = 관측 오차(남동 3~5) + **기억 밀림** + **칸 반올림(최대 +5)** = +5.3 과 맞음 → 이 카드 표 '기억 밀림' 가설의 크기 · 방향을 f2x1 에서 측정으로 지지(1 주행). '먼 비스듬한 첫 관측' 몫은 이 주행에선 작음 | [`anal_box_decomp_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_decomp_f2x1.txt) · [`anal_box_memory_f2x1.txt`](../debug_log/2026-10-19/outputs/anal_box_memory_f2x1.txt) |
| 이후 8 기 10-20 §8 ~ §8.3 | 깊이 해상도(데시메이션 ×4 · ×2 · ×1) 정지 A/B | nvblox 북 · 서 면 +2.3 · +3.1 / +2.2 · +2.4 / +2.0 · +2.9 — 차 ≤ 0.7 cm, 세션 사이 ±3 cm 흔들림이 더 큼 | 해상도는 대책 아님(정지 기준) · ×4 유지 | [`anal_decim_static.txt`](../debug_log/2026-10-20/outputs/anal_decim_static.txt) · [`anal_decim_points.txt`](../debug_log/2026-10-20/outputs/anal_decim_points.txt) |
| 이후 8 기 10-19 §21 ~ §22 · 10-22 §11 ~ §13.1 · §17 | 복귀 길 상자 칸(→ [복귀 길 상자 칸 카드](box-return-cells.md)) | f2y1 상자 안 8 → 1 칸(map→odom +41.7 cm), f2pr1 상자 밖 칸 = 172 s 기억 +4.2~+5.0 cm 밀림 · 그 자리 깊이 0 이라 안 지워짐, f2lp1 세 지도 0 칸인 채 **접촉**, f2pi1(통합 2.0) 실제 여유 1.1 cm · 지도 5.6 cm | 상자 옆 정지와 같은 뿌리(odom 기억 · 칸 반올림)가 이번엔 '멈춤' 이 아니라 '붙음 · 접촉' 으로. 통합 거리 2.0 은 이 접촉에서 나온 결정(10-22 §15) | [`anal_box_cells_in.txt`](../debug_log/2026-10-19/outputs/anal_box_cells_in.txt) · [`anal_contact_f2lp1.txt`](../debug_log/2026-10-22/outputs/anal_contact_f2lp1.txt) · [`fig_return_video.txt`](../debug_log/2026-10-22/outputs/fig_return_video.txt) |
| 이후 8 기 10-23 §4 · §10.1 · §11.1(다른 묶음) | vslam:=on(cuVSLAM 병진 속도 융합) 주행 · 경로 대 로버 자리 | f2von1 · f2von2 상자 옆 실제 여유 **3.3 · 0.3 cm**, 172 s 기억 밀림 y +1.8~+4.7 · +0.8~+1.8 cm, 로버가 경로 선보다 상자 쪽 5~9 cm, 다시 그린 경로는 상자에서 11~16 cm | 상자 옆 근접의 주원인이 기억 밀림보다 **'MPPI 가 경로 선 안쪽을 달리는 것'** 으로 옮겨 감(10-23 §11.1 읽기) → [경로 추종 · 재계획 · B0](path-tracking-replan-b0.md) | `2026-10-23/outputs/anal_contact_f2von{1,2}.txt` · `anal_memory_shift_f2von{1,2}.txt` · `anal_plan_series_f2pi1.txt` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 정지 칸은 유령(실물 없음) | 정지 그림 칸 위치 vs 사용자가 본 상자(10-13 §4.5), 라이다 점 | 칸 = 상자 앞 왼쪽, 라이다 0 | **기각** — 실제 낮은 상자(카메라만). 단 칸 하나하나는 실제 면보다 앞(10-15 §13) |
| 상자 칸이 늦게 나타나 갑자기 막힘 | `anal_box_history` 전역 · 로컬 시간열 → `anal_box_layers` 층별(odom 기준) | 전역은 3 m 밖에서 잊고 1.4~1.7 m 에서 다시 봄, 로컬은 1.17 m 전부터 4/4(f2o1). f2p1 의 '1/4' 는 지도 좌표 고정 착시 | 전역 잊음은 **지지**(원인 `map_clearing_radius_m 3.0`, 10-13 §13), 정지의 원인으로는 **기각** — 다시 본 뒤 1 m · 20 s 여유 |
| 경로가 상자에 가깝게 그려지고 MPPI 가 넓히지 않음 | 경로 ↔ 상자 끝 거리, 로버 중심 ↔ 경로(영상) | 0.22~0.29 m(차체 반폭 0.165 → 옆 6~12 cm), 정지 때 중심은 경로 위 | **지지(측정)** — 10-13 §4.6 의 '직접 원인'. 왜 그 거리인지는 inflation 감쇠 · 통로 폭 0.7 m(10-14 §1) |
| Nav2 칸 단위 풋프린트 검사가 여유 수 cm 를 먹어 현재 자세부터 충돌 | ① 정지 자세 둘레 비용 탐색(10-13 §5.4) ② 시뮬 fpchk 0 ↔ 1(§7 · §8) ③ 실주행 프레임별 fp 와 정확 여유(10-15 §28) | ① 기하로 안 닿는 움직임도 99 ② 같은 씨앗이 fpchk=1 에서만 실제와 같은 시각에 멈춤 ③ 99 → 100 이 정확 여유 2.7~4.4 cm 에서 위상 따라 갈림, fp_prev 도 100 | **지지(측정 + 시뮬)**. 크기는 '약 5 cm'(10-13 추정) → **뒤집힘 띠 2.7~4.4 cm**(10-15 측정). 시뮬 칸 검사는 소스와 한 줄씩 대조하지 않은 흉내 |
| 지도가 로버 밑에서 바뀌어 막힘 (가) | fp_prev(같은 자세를 앞 프레임 지도에) · new8 | 세 건 모두 fp_prev 100, 새 8 cm 안 칸 0 | **기각(측정)** 10-15 §28 |
| 실제 움직임이 예측과 어긋남(미끄러짐) (나) | 0.5 s 전 최적 궤적 예측 vs 실제 | 옆 ≤ 0.3 cm | **기각(측정)** 10-15 §28 |
| 기억된 상자가 오도메트리 어긋남만큼 로버 쪽으로 밀림 | map→odom 변화(10-13 §6.2) → 위치 · 각도 몫(10-14 §4.2) → 처음 찍힌 순간 → 멈춘 순간 칸별(10-15 §24.1) | 출발점 상자 f2o1 4.1 · f2p1 6.2 cm(방향 +y = 로버 쪽), 서쪽 통로 f2v1 2.1 · f2v3 2.3 cm(옆 0.1~0.2 · 멀어지는 쪽) | **부분 지지** — 출발점 상자에선 크기 · 방향이 맞고, 서쪽 통로에선 6~7 cm 를 설명 못 함. SLAM 보정이 참이라는 가정 위의 값 |
| 비스듬히 · 멀리서 처음 찍을 때 한 줄 두껍게 | odom 고정 창(10-14 §5.1), 처음 찍힌 방위 · 거리(10-15 §7), 정지 정면(§22 ~ §23) · 옆면(§24) 관측, 주행 중 기록 상자 비교(§29.4) | 처음 찍힐 때 한 줄 더 · 0.7 m 에서 지워짐 / 정지 0~3 cm / 주행 +5~10 cm / bag 근사로 과장 칸의 1/4~1/2 은 1.0 m 안에서 생김(§30.1) | **미확인** — '주행 중에만 크다' 는 측정, 원인을 '먼 첫 관측' 하나로 돌리기엔 근사 근거가 약함 |
| 상자 변이 5 cm 격자와 나란하지 않아 계단 | 계산(10-14 §5.2) | 평균 3.5 · 최대 5.4 cm(5°) | **계산상 가능** — 'nvblox 가 겹치면 장애물' 가정, 칸 중심 규칙이면 절반. 측정으로 가르지 않음 |
| 카메라 가장자리(±43°) 왜곡 | 처음 찍힌 방위(10-15 §7) | +21~+27° | **기각(측정)** |
| 정지해서 옆면을 봐도 지도가 두껍다(③) | P1 · P2 정지(10-15 §24) | 지도가 1.6~1.7 cm 안쪽 | **기각(측정)** |
| 깜빡이는 바깥 칸이 과장의 정체 | 지도 좌표 3 cm 맞춤(§7) → odom 칸 고정(§12) | 30 % 깜빡 → 90~91 % 꾸준 | **기각** — 앞 판이 착시(실수 ③) |
| 저장 지도 서쪽 벽 두께가 경로를 상자 쪽으로 밈 | 라이다 vs 저장 지도(§10), 고친 사본 재계산(§11) | 벽 약 10 cm 두꺼움(측정), 경로는 그대로 x −1.765 | **벽 두께는 지지 · 경로 영향은 기각(재계산)** |
| 상자 쪽 몸 틀기 = 연산 부담 탓(f2w2) | f2v2(크리틱 없음) 같은 자리 비교(10-15 §32) | 같은 자리 · 같은 크기 | **기각(1 회 비교)** |
| f2u2 의 상자 가로지르는 경로 = 그 순간 지도가 달랐음 | 전역 지도 15 장 재현 · 슬라이스(10-14 §24) | 어느 지도에서도 20 점 내접, 덩어리 그대로 | **기각** — NavFn 정상 동작으로 설명 안 됨, 원인 미확인 ？ |

## 4. 조치와 효과
이 카드는 기전 카드라 조치는 대책 카드가 맡는다. 이 시기 시도의 한 줄 요약 — 전역 감쇠 3.0(f2p1 재정지 → 되돌림) · BT 후진(같은 검사에 걸려 안 함) · 패딩 0(시뮬 1/10 → 0/10, 사용자 기각) · CostCritic 3 배(f2q1 4.3 cm · 머뭇 → 되돌림) · 전역 기억 연장(동적 물체 문제로 보류) · 전역 카메라 금지 띠(0.35 에서 통로 막힘, 사용자 기각) · 통합 거리 2.0 → 1.4 · 1.0 근사 · site 거리 1.0(효과 없음) · MonotoneEscape(켬, 자연 교착 미검증) · ClearanceBandCritic(띠 진입 0 · 놓침 428 → 끔) → **[상자 옆 정지 대책](box-side-stall-remedies.md)**.

기전 쪽에서 나온 운용 결정:
- 출발점 상자는 치우지 않는 시험 물체(10-14 §25 ②), 좁은 여유형은 지금 그대로(③).
- prep 이 직전 nav2 · slam · sensors 기록을 `/tmp/logkeep` 에 보관(10-14 §25 ①, 이상 경로를 다음에 보려고) — [prep 카드](prep-fast-startup.md).

### 4.1 지금 저장소 코드(11-03 확인, 고치지 않음)
| 항목 | 지금 | 이 시기 끝(10-15) | 위치 |
|---|---|---|---|
| nvblox 통합 거리 | **2.0 m**(10-22 사용자 결정, 프리셋 3 과 함께) | 1.4 | `ros2_ws/src/rover_navigation/config/nvblox_local.yaml` 57 행(이력 주석 50~56 행) |
| 슬라이스 높이 | min 0.06 · max 0.30 · slice 0.10 | 같음 | 같은 파일 67~69 행 |
| 복셀 · 감쇠 · 지우기 반경 | voxel 0.05 · tsdf_decay_factor 0.99 · `map_clearing_radius_m 3.0` | 같음 | 17 · 70 · 42 행 |
| site 거리 | `esdf_integrator_max_site_distance_vox 2.0`(10-15 §22~§23 주석) | 같음 | 65 행(주석 61~64 행) |
| 풋프린트 · 패딩(로컬 · 전역) | `[[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]` · padding 0.01, 해상도 0.05 | 같음 | `config/nav2_params.yaml` 303 · 321 · 301 행(로컬), 538 · 556 · 536 행(전역) |
| 로컬 nvblox 층 | 이진(`convert_to_binary_costmap: true` — 거리 ≤ 0 → LETHAL), `inflation_distance 0.175` | 같음 | 336~338 행 |
| 전역 nvblox 층 | 이진 · `max_obstacle_distance 0.40` · `inflation_distance 0.175` — 10-14 §1 금지 띠는 적용 안 됨 | 같음 | 569~571 행, 프레임은 `navigation.launch.py` 97 행 |
| inflation | 로컬 0.40 / 2.5, 전역 0.70 / 2.0(10-13 §5 시험 주석) | 같음 | 525~526 · 720~721 행(주석 713~719) |
| CostCritic | `cost_weight 3.81` · `critical_cost 300` · `consider_footprint true` · `collision_cost 1e6` · `near_goal_distance 0.5` | 같음 | 269 행 |
| ClearanceBandCritic | critics 목록에 있으나 **`enabled: false`**(band 0.06 · weight 20) | 같음(§30.1 끔) | 255 · 276 행, `src/clearance_band_critic.cpp` |
| PathAngleCritic | `max_angle_to_furthest 0.5`(10-14 §20 의 '28.6° 안이면 꺼짐') | 같음 | 288 행 |
| BT PathBlockedAhead | `lookahead 1.5 · skip_near 0.30 · hold_time 2.0 · min_cost 99 · only_new true` — 10-12 §2 후보 (c)(정지 중 판정 안 함 · 문턱 100)는 적용 안 됨 | 같음 | `config/nav_to_pose_no_spin.xml` 108 행 |
| 복구의 후진 자리 | `BackUp … server_name="monotone_escape"`(Nav2 BackUp 대신 우리 플러그인) → Wait 5 | 같음(10-15 §26) | 같은 BT 122~127 행, `src/monotone_escape_behavior.cpp` |
| 계획기 | 이 시기 NavFn → **10-27 부터 Smac Hybrid 우선 · 실패 시 NavFn**(10-14 §24 이상 경로 · 0.22~0.29 m 근접은 NavFn 에서 잰 값) | NavFn | CLAUDE.md §6 · [전역 계획기 카드](global-planner-choice.md) |

## 5. 내 실수
### 실수 ① 칸을 지도 좌표에 고정해 놓고 '늦게 떴다' 고 읽음 (10-13 §5.6 → §6.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2p1(전역 감쇠 3.0) 결과 판정 — 상자 끝 칸이 언제부터 있었나 |
| 본 것 | 상자 끝 4 칸이 0.34 m 옆까지 로컬 · 전역 모두 1/4, 정지 5 s 전 4/4 |
| 처음 추론 | "이번에는 늦게 떴다가 주된 이유" — 감쇠 비교가 불공정 |
| 의심한 이유 | 사용자 "2번 수행하라"(층별 추적) — 1/4 → 4/4 가 계단식이고 새 관측 계기가 없음 |
| 판별 시험 | `anal_box_layers.py` 로 칸마다 nvblox 슬라이스 값 · 라이다 점 · map→odom 변화를 1 s 간격 |
| 결론 | nvblox 는 1.51 m 에서 이미 봤고 계속 가짐. 1/4 → 4/4 순간(14:14:35 · 44 · 48)이 보정 값이 바뀐 순간과 일치 — odom 에 고정된 칸이 지도 위에서 미끄러져 고정한 칸 위로 옮겨 온 것. §4.6 · §5.6 시간열의 '차체 여유' 에도 ±5 cm 섞임(정지 순간 값은 유효) |
| 다음에 알아보는 법 | odom 에 쌓이는 층(nvblox · 로컬 코스트맵)의 칸을 시간에 걸쳐 셀 때는 **odom 칸 번호로 고정**한다. 서명 = 칸 수가 관측 없이 계단식으로 바뀌고 그 시각이 map→odom 변화와 겹침 |
| 스크립트 핵심 | `Docs/tools/anal_box_history.py` `count()`: `P = (Tin @ BOX.T).T` — BOX 는 정지 순간 지도 좌표, 로컬은 `Tin = inv(Mmo)` 로 그때그때 odom 으로 옮김(= 지도 고정). `anal_box_layers.py` 76 행 `dM = np.linalg.inv(MmoS) @ Mmo; sh = (dM @ …)[:2] - BOX.mean(0)` 로 보정 차를 함께 출력 |
| 나온 결과 | `f2p1_box_layers.txt` 34~35 행: `14:14:47  0.38 m  +54°  -0.00  0.05 -0.00  0.05 … #+#+  -4.4, -1.5 cm` → `14:14:48 … -0.00 -0.00 -0.00 -0.00 … ####  -1.4, -1.1 cm` |
| 데이터 | [`f2p1_box_history.txt`](../debug_log/2026-10-13/outputs/f2p1_box_history.txt) · [`f2p1_box_layers.txt`](../debug_log/2026-10-13/outputs/f2p1_box_layers.txt), bag `2026-10-13/bags/bag_f2p1.tgz`(로컬, git 제외) |

### 실수 ② 칸 크기 오차의 크기를 확인 없이 '약 5 cm' 로 두 번 더함 (10-13 §5.6 · §6.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 실측 11 cm 와 코스트맵 2.9~5.4 cm 의 차이 설명 |
| 본 것 | 실측 11 · 코스트맵(칸 중심) 5.4 · (칸 가장자리) 2.9 cm |
| 처음 추론 | "실제 11 − 번짐 약 6 − 칸 단위 검사 약 5 ≈ 0" (§5.6), "밀림 약 5 + 칸 검사 약 5"(§6.2) |
| 의심한 이유 | 칸 검사 5 cm 는 §5.4 에서도 '추정 · 소스 대조 안 함' 이었는데 결론 식에 수치로 들어감 |
| 판별 시험 | 10-15 §28 `anal_stall_entry.py` 로 실주행 프레임마다 Nav2 식 fp 와 정확 여유를 같이 계산 |
| 결론 | 뒤집힘은 정확 여유(패딩 차체 ↔ 칸 중심) **2.7~4.4 cm** 띠에서 위상 따라 일어남 — '5 cm 를 늘 먹는다' 가 아니라 '이 띠 안이면 될 수도 안 될 수도'. 결론 방향(실제 여유가 남아도 Nav2 는 충돌로 봄)은 유지 |
| 다음에 알아보는 법 | 추정 값을 덧셈 식에 넣을 땐 '추정' 표시를 식에 남기고, 측정 가능한 항(이번엔 fp)은 먼저 잰다 |
| 스크립트 핵심 | `2026-10-15/jobs/anal_stall_entry.py` `fp_cost`: `mx = int(math.floor((wx - info[0]) / info[2]))` 로 꼭짓점 내림 → `bresenham(*cells[i], *cells[(i + 1) % 4])` 변마다 최대 |
| 나온 결과 | `anal_stall_entry.txt`: `13:24:06.1 | … |   2.7 (+0.210, +0.202) |   99     99     99` · `13:24:07.3 | … |   3.1 (+0.299, +0.190) |  100    100     99` |
| 데이터 | [`anal_stall_entry.txt`](../debug_log/2026-10-15/outputs/anal_stall_entry.txt) |

### 실수 ③ 실수 ① 과 같은 착시를 이틀 뒤 다시 — '바깥 줄 30 % 깜빡임' (10-15 §7 → §12)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 질문 '카메라 가장자리 왜곡?' 판별 + 칸별 관측 통계 |
| 본 것 | 바깥 줄(x −1.47~−1.48) 칸은 시야 안 프레임의 약 30 % 에서 치명 아님 |
| 처음 추론 | 바깥 줄 = '깜빡이는 과장 칸', 안쪽 줄 = 실제 면 → §8 대응 · §9.3 '30 % 의 시간엔 바깥 칸이 실제 면' · 후보 3(깜빡이는 칸만 낮추기) 제안 |
| 의심한 이유 | 후보 3 검증(§12)에서 원본 슬라이스는 그 칸을 98 % 점유로 봄 — 코스트맵만 빠짐 |
| 판별 시험 | `anal_grid_phase.py`(슬라이스 ↔ 코스트맵 원점 위상차 0) → `anal_cell_ratio_odom.py`(odom 칸 `floor(x/0.05)` 로 고정해 다시 셈) |
| 결론 | 바깥 줄 90~91 %, 꾸준히 찍힘. '30 %' 는 칸을 지도 좌표 3 cm 안으로 맞춘 착시(그 사이 map→odom 회전 0.2° · 이동 약 2 cm). §8 · §9.3 의 기댄 결론 철회, 후보 3 불합격 |
| 다음에 알아보는 법 | 실수 ① 의 규칙을 도구에 넣는다 — 칸 대응은 **odom 격자 번호**로. '지도 좌표 N cm 안' 맞춤은 기억 층에 쓰지 않는다. 이 실수는 같은 날 기록에 실수 ① 이 있었는데도 되풀이됐다 |
| 스크립트 핵심 | 앞 판 `anal_cell_first_seen.py` 51 행 `on = (np.hypot(CC[:, 0] - p[0], CC[:, 1] - p[1]) < 0.03).any()`(지도 좌표 3 cm) → 뒤 판 `anal_cell_ratio_odom.py` 40 행 `(int(math.floor(xo / 0.05)), int(math.floor(yo / 0.05)))` |
| 나온 결과 | 앞: `anal_cell_first_seen_f2v1.txt` `(-1.481, -4.254) 카메라 … 찍힌 뒤: 시야 안 28 프레임 …, 그중 치명 아님 9` / 뒤: `anal_cell_ratio_odom_f2v1.txt` `(-1.481, -4.254)  30  27 ( 90 %)  27 ( 90 %)` |
| 데이터 | [`anal_cell_first_seen_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_first_seen_f2v1.txt) · [`anal_cell_ratio_odom_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_ratio_odom_f2v1.txt) · [`anal_grid_phase_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_grid_phase_f2v1.txt) |

### 실수 ④ 라이다로 잰 '과소' 를 라이다에 안 보이는 물체의 안전성 근거로 씀 (10-15 §9.2 → §9.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 조건 '(가) 는 카메라가 과대평가는 해도 과소평가는 못할 때 적절' 검증 |
| 본 것 | 라이다 면 대비 카메라 뒤 10~12 % · 누락 1.6~3.1 % |
| 처음 추론 | 전제 불성립 → (가) 부적절 |
| 의심한 이유 | 사용자 "과소 문제일 경우 라이다로 해결 가능한 부분 아닌가?" |
| 판별 시험 | 기준 점이 라이다 점이므로 표본은 전부 라이다가 보는 물체 — 그런 물체는 라이다 층이 막음(논리 확인) |
| 결론 | 결론의 근거가 질문과 어긋남 ✘. (가) 에 필요한 것은 '라이다 아래 물체에서 가장 바깥 카메라 칸이 늘 실제 면보다 앞인가' — 그 뒤 §12 에서 다시 봄 |
| 다음에 알아보는 법 | 판별 표본을 고른 기준(여기선 라이다 점)이 가설의 적용 대상(라이다에 안 보이는 것)과 겹치는지 먼저 확인 |
| 스크립트 핵심 | `2026-10-15/jobs/anal_cam_vs_lidar.py` 머리말: "카메라 → 점 방향으로 1 cm 씩 나가며 조각 거리 ≤ 0(점유)인 첫 지점 s … ≤ −2.5 cm = 앞(과대) · ±2.5 cm = 같음 · > +2.5 cm = 뒤(과소)" — 기준 = 시야 안 라이다 점 |
| 나온 결과 | 원문 [`anal_cam_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar.txt)(SUMMARY §9.2 표: f2v1 4109 점 · 뒤 10.4 % · 누락 1.6 %) |
| 데이터 | 같은 파일 · [`anal_cam_vs_lidar_breakdown.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar_breakdown.txt) |

### 실수 ⑤ 서쪽 통로 서쪽 두께를 '카메라 과장' 으로 말함 (10-15 §8 · 대화 → §9.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 서쪽 통로의 지날 수 있는 폭 설명 |
| 본 것 | 정지 그림에서 서쪽 벽 라이다 선 바깥 주황 띠(§6) |
| 처음 추론 | 서쪽도 카메라가 두껍게 찍음 |
| 의심한 이유 | §9.1 전역 지도 단면을 출처별로 가르니 서쪽 점유는 정적 층 |
| 판별 시험 | `anal_path_center.py` 단면 → `anal_map_vs_lidar.py`(3 순간, 서쪽 −12.4~−12.8 · 동쪽 −3.2~−3.6 cm) |
| 결론 | 출처 = 저장 지도 office_v3 의 벽(약 10 cm 두꺼움, 지도 만든 날 번짐으로 추정). 고친 사본으로도 경로는 그대로(§11) |
| 다음에 알아보는 법 | 전역 칸을 말할 땐 층 출처(정적 · 라이다 · 카메라)를 먼저 가른다 |
| 스크립트 핵심 | `2026-10-15/jobs/anal_map_vs_lidar.py` 머리말: "양쪽 면이 같은 방향으로 밀렸으면 위치 어긋남, 한쪽만이면 지도 번짐" |
| 나온 결과 | [`anal_map_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_map_vs_lidar.txt) |
| 데이터 | 같은 파일 · [`anal_mapfix_replan.txt`](../debug_log/2026-10-15/outputs/anal_mapfix_replan.txt) |

### 작은 실수 (각 날 SUMMARY 에 정정 기록 있음)
- 10-13 §4.6 고칠 곳 후보 1 '감쇠를 완만하게' — 방향이 반대(§5.2: 1.0 이면 더 붙음).
- 10-13 §5.5 '시뮬은 옛 ObstaclesCritic 기준이라 반나절' — 확인 없이 한 말, job452 · job776 이 이미 있었음(§7 정정).
- 10-13 §9 선언 'f2a10 은 그 구간을 지나갔다' — 10-01 기록상 못 지남(선언 정정). 같은 묶음의 out_f2p1 30 회는 시작 시각이 첫 경로보다 일러 무효(§9.1).
- 10-13 §8.1 첫 실행 라벨에 `=` → 인자 해석 오류로 전부 실패.
- 10-14 §20 옆 여유를 ≥ 99 로 재서 음수 → 100 만 셈. 10-14 §22 뒤집힌 라이다(roll 180°)를 yaw 만으로 변환해 거울상 → 쿼터니언 전체.
- 10-14 §24 A2 전 prep 이 `/tmp/nav2.log` 를 덮어 B 의 계획기 경고를 못 봄 — 기록 손실(→ §25 보관).
- 10-15 §22.1 'B 에서 행 y 0.00 빠짐' → §23 에서 A · B 모두 없음, 측정 때마다의 차(정정).
- 10-15 §28 대책 ① '풋프린트 99 에 벌점' — 99 는 치명 칸 중심 17.5 cm 안이면 늘 나옴(§29 정정, 소스 + f2v4 17.4 cm 에서 99).
- 10-15 §30.1 1 차 근사(`anal_intdist_proxy.py`)는 로컬 창 진입이 섞여 무효.

## 6. SUMMARY · 정리 페이지 ↔ 원문 어긋남 (이번 확인)
| # | 기록 | 원문 | 판정 |
|---|---|---|---|
| 1 | 10-13 §4.6 표 "13:32:12~13:32:50 전역 경로 ↔ 상자 끝 0.00~0.01 m" | `f2o1_box_history.txt` 52~68 행: 13:32:17 **0.19** · :19 **0.16**, :33 · :36 0.02, 나머지 0.00~0.01 | 대부분 맞음, 17~19 s 두 표본은 경로가 잠깐 비켜 있었음 |
| 2 | **'여유' 정의가 도구마다 셋** — 10-13 §4.5 · §4.6 · §5.6(`fig_stop_costmap` · `anal_box_history`, 몸체 ↔ 칸 중심), §7 · §10 · 시뮬(`anal_box_pass` · `anal_mppi_sim`, 몸체 ↔ 칸 중심 − 2.5 cm = 칸 가장자리 근사), 10-15 §28 · §29 · §34(`anal_stall_entry` · `anal_band_run` · `anal_box_true_vs_map` '지도 여유', **패딩 차체** ↔ 칸 중심) | 코드: `anal_box_history.py` FP 반폭 0.165(패딩 없음) · `anal_box_pass.py` `… - res / 2` · `anal_stall_entry.py` `XF, XR, HW = 0.272, -0.258, 0.175` | 같은 자리라도 셋이 다름: 패딩 차체 ↔ 중심 = 몸체 ↔ 중심 − 1.0 = 몸체 ↔ 가장자리 + 1.5 cm. 10-13 §10 의 '통과 2.8~4.7 · 정지 1.8~2.2 cm' 와 10-15 §28 의 '띠 2.7~4.4 cm' 는 **다른 척도** — 10-13 값을 10-15 척도로 바꾸면 +1.5 cm(정지 3.3~3.7 · 통과 4.3~6.2) |
| 3 | 10-13 §6.2 "nvblox 값이 처음 생긴 것은 1.51 m … 상자는 설계상 1.5 m 안에서만 보인다" | `box_edge_growth.txt`(10-14, odom 고정 7 × 7 창): `13:32:58  1.68 m  +10°  2` 칸 · `13:33:01  1.47 m  +25°  8` | 4 칸 창(§6.2)과 7 × 7 창(10-14)의 차. 상자 일부는 1.68 m(로버 중심 기준)에서 먼저 찍힘 — 카메라는 중심보다 앞이라 통합 한도 1.4 와 모순은 아님. '한꺼번에' 는 1.47 m |
| 4 | CLAUDE.md §6 "nvblox 가 odom 좌표라 기억된 상자가 4~5 cm 밀림" | 10-14 §4.2 출발점 상자 4.1 · 6.2 cm(맞음), 10-15 §24.1 서쪽 통로 2.1 · 2.3 cm(옆 방향 0.1~0.2, 멀어지는 쪽) | 출발점 상자에서만 맞는 수치. 10-15 기준 과장 +5~10 cm 의 일부일 뿐 — 문구 갱신은 사용자 판단(이 카드에서 안 고침) |
| 5 | 10-14 §1 "D 0.35 에서 막히는 곳: f2o1 13:33:11 · 19, f2p1 14:14:29~45, f2n1 10:55:04~20" | `keepout_all.txt`: f2p1 은 **14:11:49 · 14:11:57**(목표 1 가는 길, 같은 상자 옆)도 '통로 막힘' | 막히는 자리가 상자 옆이라는 결론은 같음, 시각 목록이 빠짐 |
| 6 | 10-15 §28 표 f2v3 "넘어간 순간 3.1 cm · 직전 99 최소 2.7" | `anal_stall_entry.txt`: 13:24:06.1 2.7(99) → 07.3 3.1(100) → 07.9 2.7(100, ◀ 기준) | 맞음 — 같은 2.7 cm 가 06.1 엔 99, 07.9 엔 100(위상 차). 띠 하한 2.7 은 이 한 표본 |
| 7 | 10-15 §28 '경계 띠 2.7~4.4 cm(오늘 3 건 + 09-23 4.4 cm)' | 09-23 f0a1 '여유 4.4 cm' 의 정의(패딩 포함 · 칸 중심 여부)는 이번에 확인 안 함 | 같은 척도인지 미확인 — 상한 4.4 는 오늘 f2v1(10:15:46.9 · 47.5 4.4 cm 에서 99)로도 나옴 |
| 8 | 10-15 정리 페이지 `figures/stall_trace_1015.html` 기각 표 "'30 % 깜빡임'은 … 착시 §9.3 · §12" | SUMMARY: 착시 정정은 §12, §9.3 은 '30 %' 를 근거로 쓴 곳 | 근거 § 표기만 엇갈림 |

## 7. 남은 것 (10-15 시점) · 이후
- **과장 +5~10 cm 의 원인 미확정** — 정지 정면 · 옆면은 0~3 cm, 주행 중만 큼. 후보(먼 비스듬한 첫 관측 · 기억 밀림 · 격자 계단 · 깊이 / 장착 2~3 cm)는 몇 cm 씩이고 측정으로 다 가르지 못함. 진짜 비교는 깊이 영상 · camera_info · tf 가 든 bag 을 컨테이너 nvblox 에 재생하는 오프라인 A/B(10-15 §30.1 · §31 다음 ①).
- **'후보 전부 충돌' 인데 쓸고 갈 영역에 치명 칸 0**(f2v1 10:15:45~10:16:06, `anal_ahead_cells.py`, 10-15 §3) — §28 의 '서 있는 자세 fp 100' 이 설명하지만, 제자리 회전 모서리 검사 범위는 따로 안 봄.
- **최적 궤적에 칸 검사 치명 점이 멈추기 0.6~6 s 전부터**(§28 (다)) — Humble MPPI 가 최적 궤적을 검사하는지 소스 미확인.
- **f2u2 이상 경로**(253 칸 20 점을 지나는 NavFn 경로, 10-14 §24) 원인 미확인 — 지금은 Smac 우선(10-27)이라 재현 조건이 달라짐.
- 서 있을 때 방향 구속 크리틱 없음(10-14 §20) — PathAngle 0.5 → 0.35 후보는 시뮬 전.
- 출발점 상자의 시야 밖 기억은 서 있으면 약 80 s 뒤 사라져 실제 상자가 지도에서 없어짐(10-15 §18.3) — 대기를 늘리는 대책 금지 근거.
- 통합 거리가 10-22 에 2.0 으로 바뀌어 '멀리서 처음 본 면이 두껍게' 위험이 다시 커짐(nvblox_local.yaml 56 행 주석이 스스로 적음) — 이후 시기 카드에서 확인.
- **이후 8 기(10-19 ~ 10-23) — 채움(11-03)**:
  - '과장 +5~10 cm 의 원인 미확정' → **f2x1 1 주행에서 분해**: 관측 오차(남동 3~5 cm, (b) 외부 보정 / 그 순간 자세 오차 미분리) + odom 기억 밀림(로버 쪽 +2.7~+6.1 cm) + 칸 반올림(최대 +5 cm). nvblox 설정 · 깊이 필터 · map 기억 · 깊이 해상도는 대책 아님 — [과장 근원 카드](box-exaggeration-source.md). 서쪽 통로 상자는 이 분해를 안 함.
  - '진짜 비교 = 깊이 bag 재생 오프라인 A/B' → 10-19 §2 · §6 에서 경로 완성(R0 ✔, `run_nvblox_replay.sh`). 10-22 §9 · §11.3 · §14.2 에서도 씀.
  - 통합 거리 2.0(10-22) — 근거는 복귀 상자를 **못 봐서 접촉**(f2lp1). 바뀐 뒤 f2pi1 상자 옆 실제 여유 1.1 cm(지도 5.6 cm, 기억이 로버 반대쪽 약 3 cm) — '멀리서 처음 본 면이 두껍게' 의 효과를 따로 잰 기록은 없음 — [복귀 길 상자 칸](box-return-cells.md).
  - 10-23(다른 묶음): vslam:=on 으로 기억 밀림이 한 주행은 그대로(y 1.8~4.7 cm) · 한 주행은 줄었으나(0.8~1.8 cm) 여유 3.3 · 0.3 cm — 근접의 주원인은 경로 추종 쪽으로 → [경로 추종 · 재계획 · B0](path-tracking-replan-b0.md).
  - 그 뒤 포인터만(9 기 이후): 10-26 PathAlign 28 · PathFollow 5 · 10-27 Smac Hybrid · nvblox 층 TF 실패 시 슬라이스 버림.
- **이후 9 기(10-26 ~ 10-28) — 이 카드 쪽만 채움(11-04)**:
  - 10-27 §15 ~ §17 nvblox 층 결함(TF 조회 실패 순간 슬라이스를 단위 변환으로 적음)은 **전역 층만** 해당 — 로컬 층은 슬라이스와 같은 odom 이라 조회를 안 한다(층 소스 조건 `nav2_costmap_global_frame_ != slice_frame`, [TF 카드](nvblox-layer-tf-drop.md) §3.1). 이 카드의 정지 기전(MPPI · 로컬 코스트맵 칸 검사)과 '주행 중 과장 +5~10 cm'(로컬 · nvblox 조각에서 잰 값)은 그 결함으로 설명되지 않는다(코드 조건 추론). 단 10-08 ~ 10-27 전역 계획 · PathBlockedAhead 는 틀어진 전역 장을 봤을 수 있다(f2st1 3 장 · 가짜 막힘 2 번, 그 전 주행은 미측정).
  - 같은 상자의 9 기 복귀(f2st1 · f2tf1 · f2tt1 · f2tt2)는 '닿지 않고 멈춤' 이 아니라 **잊었다 다시 봄 → PathBlockedAhead → 재계획**(3 회 14.0~16.3 cm) 또는 **못 보고 접촉**(f2tf1) — [복귀 상자 카드](box-return-cells.md) §7. 이 묶음(10-27 §15 ~ §26 · 10-28 §1 ~ §4)에는 '후보 전부 충돌' 정지를 이 카드 기전으로 다시 분석한 기록이 없다.
  - 포인터(다른 묶음): 10-28 §5 통로 남쪽 좁은 곳 막힘 칸 — 회전 중 벽 · 물체 가장자리가 한 칸(5 cm) 더 찍혀 경로 점이 96 → 99(SUMMARY 가 '10-15 칸 판정 뒤집힘과 같은 꼴' 로 적음) · 10-26 MPPI 굽은 곳 깎기(→ [PathAlign 카드](mppi-corner-cut-pathalign.md)) · 10-27 Smac(→ [Smac 카드](smac-hybrid-adoption.md)).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2f1 | 10-12 PreferForward 15 검증, 복귀 상자 ② 옆 멈칫 | 10-12 §1 ~ §2, `outputs/f0_f2f1_runner.log` · `f2f1_box_smooth.txt` · `f2f1_cpu.txt` · `f2f1_gaps.txt` · `f2f1_navlog.txt`, bag `2026-10-12/bags/bag_f2f1.tgz`(로컬), 영상 `videos/f2f1_box_debug.mp4`(git 제외) |
| f2o1 · f2p1 | 10-13 출발점 상자 옆 정지 2 회(f2p1 = 전역 감쇠 3.0) | 10-13 §4.4 ~ §6, `run_f2o1.txt` · `run_f2p1.txt` · `navlog_f2o1.txt` · `f2o1_stop.txt` · `f2o1_box_history.txt` · `f2p1_box_history.txt` · `f2o1_box_layers.txt` · `f2p1_box_layers.txt` · `f2o1_options.txt`, bag `2026-10-13/bags/bag_f2o1.tgz` · `bag_f2p1.tgz`(로컬) |
| f2q1 | cost_weight 3 배 실주행(대책 카드) | 10-13 §12, `run_f2q1.txt`, bag `bag_f2q1.tgz` |
| 시뮬 재현 | f2o1 · f2p1 장면 × 씨앗(fpchk 0 · 1) | 10-13 §7 ~ §8.1, `sim_repro.txt` · `sim_repro_fp.txt` · `sim_repro_fp2.txt`, `jobs/run_sim_box{,2,3}.sh` |
| box_pass | 11 주행 상자 구역 최소 여유 | 10-13 §10 · §12.1, `box_pass.txt` |
| keepout | 전역 금지 띠 D 재계획(f2o1 · f2p1 · f2n1) | 10-14 §1, `keepout_all.txt` |
| f2t1 · f2s2 | 남서 통로 머리 돌림 · 대조 | 10-14 §20, `anal_sw_turn_f2t1.txt` · `anal_sw_turn_f2s2.txt` · `anal_sw_yawsweep_f2t1.txt`, bag `2026-10-14/bags/bag_f2t1.tgz` · `bag_f2s2.tgz`(로컬) |
| f2r1 · f2u1 · f2u2 · f2u3 | 출발점 상자 끝 실패 · 통과(A · B · A2) | 10-14 §9 · §21 ~ §24, `anal_box_f2u{1,2,3}.txt` · `anal_box_edge_map_f2u.txt` · `anal_navfn_replay_f2u.txt` · `anal_slice_blob_f2u2.txt`, bag f2r1 로컬 · **f2u1~3 bag 은 PC 로컬에 없음**(11-03 확인) |
| f2v1 · f2v1r · f2v2 · f2v3 · f2v3r · f2v4 | 10-15 기준선 · 복귀 | 10-15 §3 ~ §21, `run_f2v*.txt` · `navlog_f2v*.txt` · `anal_motion_probe*.txt` · `anal_near_cells_src*.txt` · `anal_stall_entry.txt`, **bag 은 PC 로컬에 없음**(11-03 확인) |
| box_face · boxdump | 정지 정면 · 옆면 관측 | 10-15 §22 ~ §24.1, `box_face_{A,B}.txt` · `outputs/boxdump/*.npz` |
| f2w1 · f2w2 | ClearanceBandCritic 주행(대책 카드) — 기록 상자 비교 · 안 멈춘 이유 | 10-15 §29 ~ §34, `anal_box_true_vs_map.txt` · `anal_band_run_{b910,no5}.txt` · `anal_cmd_timeline_f2w2.txt` |
| 도구(상시, Docs/tools) | `anal_box_history.py` · `fig_stop_costmap.py` · `fig_box_approach_video.py` · `anal_box_layers.py` · `anal_box_pass.py` · `anal_mppi_sim.py` · `anal_plan_keepout.py` | §9.1 ~ §9.6 |
| 도구(그날만) | 10-12 `box_smooth.py` · `fig_f2f1.py` / 10-13 `anal_f2o1_options.py` · `run_sim_box*.sh` / 10-14 `anal_box_shift_angle.py` · `anal_box_edge_growth.py` · `anal_sw_turn.py` · `anal_sw_yawsweep.py` · `anal_box_edge_map.py` · `anal_blob_src.py` · `anal_navfn_replay.py` · `anal_slice_blob.py` · `fig_box_end_plans.py` · `chk_nav2_window.sh` / 10-15 `anal_ahead_cells.py` · `anal_motion_probe.py` · `anal_near_cells_src.py` · `fig_stall_view.py` · `fig_stall_cells.py` · `anal_cell_first_seen.py` · `anal_path_center.py` · `anal_cam_vs_lidar.py` · `anal_map_vs_lidar.py` · `anal_mapfix_replan.py` · `anal_flicker_filter.py` · `anal_cell_ratio_odom.py` · `anal_lidar_strip.py` · `anal_grid_phase.py` · `chk_box_face.py` · `chk_box_dump.py` · `fig_box_dump.py` · `anal_memory_shift.py` · `anal_replan_trace.py` · `anal_stall_entry.py` · `anal_box_true_vs_map.py` · `anal_cmd_timeline.py` · `fig_passage_f2w2.py` | §9.7 ~ §9.9 |

## 9. 도구 해설
공통: 10-13 부터 bag 분석은 PC 에서 `rosbags`(AnyReader, Humble 타입)로 직접 읽는다. `nvblox_msgs/DistanceMapSlice` 는 정의를 손으로 등록(10-08 `nvslice_pc.py` 와 같음). 좌표: 로컬 코스트맵 · nvblox 슬라이스 = **odom**, 전역 = map — 도구는 `/tf` 의 map→odom 으로 옮긴다(이 시기 실수 ① · ③ 이 바로 이 변환을 지도 고정으로 쓴 데서 나옴). OccupancyGrid 값 100 = 치명(254) · 99 = 내접(253). '여유' 정의가 도구마다 다르다(§6 #2). 시뮬만 Jetson(`rosbag2_py`). `Docs/tools` 의 7 개는 `anal_mppi_sim.py` 말고는 그날 커밋 판 그대로다(`git log` 확인); `anal_mppi_sim.py` 는 10-26 에 바뀌어 아래는 10-13 판(`dbbf206e` · `2887e666`) 기준.

### 9.1 `Docs/tools/anal_box_history.py` — 상자 칸이 언제부터 · 로버 · 경로가 어떻게 (10-13 §4.6 · §5.6) ★ '직접 원인 = 경로 근접' 을 낸 도구
- **형태**: PC `python Docs/tools/anal_box_history.py bag 정지HH:MM:SS [시작HH:MM:SS]`.
- **왜**: f2o1 정지 — MPPI 가 붙었나, 칸이 늦게 떴나.
- **하는 일**: 정지 시각의 로컬 코스트맵에서 치명 칸(≥ 100)을 몸체 좌표로 옮겨 차체 직사각형(FP 앞 0.262 · 뒤 0.248 · 반폭 0.165, **패딩 없음**)과의 거리를 구하고, 최근접 칸이 속한 8-연결 덩어리(`ndimage.label`)를 '상자' 로 정해 **지도 좌표로 고정**. 그 뒤 ~2 s 간격으로 로컬 · 전역의 그 자리 치명/내접 칸 수, 로버 ↔ 상자 중심, 차체 여유(몸체 ↔ 칸 중심), 방위, 최신 `/plan` 의 상자 칸까지 최소 거리.
- **출력**: 첫 줄 `상자(정지 13:33:27 때 로컬 코스트맵 기준): 치명 칸 4 개, 지도 좌표 중심 (1.23, 0.03), 폭 x 0.10 · y 0.10 m`, 표 `13:33:26   0.28 m   4.8 cm  +61°  4 /  4  4 /  4  0.22 m`. 남은 곳 [`f2o1_box_history.txt`](../debug_log/2026-10-13/outputs/f2o1_box_history.txt) · [`f2p1_box_history.txt`](../debug_log/2026-10-13/outputs/f2p1_box_history.txt).
- **결함**: 상자 자리가 지도 고정이라 odom 기억 층의 칸 수 · 여유가 보정 변화만큼 틀어짐(실수 ①, 머리말 '한계' 에 스스로 적혀 있음). 영상 `fig_box_approach_video.py` 도 같은 정의(검은 십자).
- **계보 · 지금**: `anal_box_pass.py` 가 이 모듈의 `load` · `near` · `grid` 를 가져다 씀. 지금도 쓸 수 있으나 기억 층 시간열엔 odom 고정 도구(`anal_box_edge_growth` · `anal_cell_ratio_odom` 방식)를 쓸 것.

### 9.2 `Docs/tools/fig_stop_costmap.py` · `fig_box_approach_video.py` — 정지 장면 · 접근 영상 (10-13 §4.5 · §4.6)
- **형태**: `fig_stop_costmap.py bag 출력.png HH:MM:SS [앞으로 볼 초=25]` · `fig_box_approach_video.py bag 출력.mp4 시작 정지 [배속=2.5]`.
- **하는 일**: 앞 것은 지정 시각 로컬 코스트맵 + 풋프린트 + 라이다 점 그림과, 그 전 구간 0.6 s 마다 '둘레 최대 비용 · 라이다 최소 여유 · 치명 칸 중심까지 차체 여유' 표. 뒤 것은 전역 코스트맵 바탕에 로컬 치명 칸(빨간 테), 라이다, 차체 궤적, `/plan`, 카메라 시야 부채꼴(±43°, 1.4 m), 상자 칸 십자.
- **출력**: [`f2o1_stop.txt`](../debug_log/2026-10-13/outputs/f2o1_stop.txt)(`13:33:02.0  77  0.272 (0.44, 0.37)  0.271 (0.43, 0.38)` …), 그림 [`2026-10-13_f2o1_stop_costmap.png`](../04_navigation/figures/2026-10-13_f2o1_stop_costmap.png), 영상 `2026-10-13/videos/f2o1_box_approach.mp4` · `f2p1_box_approach.mp4`(git 제외), 정지 장면 2 장(§2 표).
- **쓰인 곳**: '유령 아닌 실제 상자 · 카메라만' 판정, '로버 중심은 경로 위' (영상 판독 — 수치 근거 없음).
- **지금**: 영상 상시 도구는 이후 `fig_drive_video.py`(10-23).

### 9.3 `Docs/tools/anal_box_layers.py` — 어느 층이 언제 채웠나 (10-13 §6.2) ★ odom 기억 · 보정 밀림을 낸 도구
- **형태**: `anal_box_layers.py bag 정지HH:MM:SS 시작HH:MM:SS [간격 s=1.0]`.
- **하는 일**: 상자 끝 칸(위 9.1 과 같은 정의, 지도 고정)마다 1 s 간격으로 ① `/nvblox_node/static_map_slice` 그 자리 값(≤ 0 = 장애물, `?` = 미관측; 슬라이스 header 프레임이 odom 이면 map→odom 역변환으로 옮겨 `floor` 색인) ② `/scan` 점(정적 tf 사슬로 지도 좌표) 중 칸 ±2.5 cm 안 개수 ③ 로컬 치명(#) · 내접(+) ④ 정지 때 대비 map→odom 차(`dM = inv(MmoS) @ Mmo` 로 상자 중심이 옮겨지는 양 cm · °).
- **출력**: `nvblox 슬라이스: 좌표계 odom, 칸 0.050 m, 미관측 값 1000.0, 351 장` · `13:33:01  1.51 m  +26°  -0.00 -0.00 -0.00 -0.00  0  0  0  0  +#+#  +0.2, -4.1 cm · +0.9°`. 남은 곳 [`f2o1_box_layers.txt`](../debug_log/2026-10-13/outputs/f2o1_box_layers.txt) · [`f2p1_box_layers.txt`](../debug_log/2026-10-13/outputs/f2p1_box_layers.txt).
- **읽는 법**: 마지막 열은 '그 시각 − 정지 때' 라 SUMMARY 의 '정지 때까지 변화' 와 부호가 반대(f2o1 출력 −4.1 = SUMMARY y +4.1).
- **결함**: 칸 대응이 지도 고정이라 nvblox 값 열도 보정 변화에 따라 이웃 칸을 읽음 — 이 도구가 바로 그 사실(실수 ①)을 드러냈다. SLAM 보정이 참이라는 가정.

### 9.4 `Docs/tools/anal_box_pass.py` — 같은 구역을 지날 때 여유 비교 (10-13 §10 · §12.1)
- **형태**: `anal_box_pass.py x0,x1,y0,y1 이름=bag …`(이날 `0.6,2.2,-0.5,0.8`).
- **하는 일**: 로버 중심이 구역 안 · |yaw| > 100°(복귀 = 서쪽)인 로컬 코스트맵마다 몸체(앞 0.262 · 뒤 0.248 · 반폭 0.165) ↔ 치명 칸 중심 거리 **− res/2**(칸 가장자리 근사, 시뮬 'LETHAL 여유' 와 같은 정의). 최소 · 그때 위치, 5 cm 미만 시간, 0.5 cm 미만 이동이 2 s 넘게 이어진 '구역 안 정지'.
- **출력**: [`box_pass.txt`](../debug_log/2026-10-13/outputs/box_pass.txt) — `f2o1  34.2 s  2.2 cm  (1.48, 0.20) 13:33:24  21.0 s  18.6 s` 등 11 줄.
- **쓰인 곳**: '통과와 정지는 1~2 cm', '시뮬은 이 자리에서 약 5 cm 넉넉' (§10), f2q1 판정(§12.1).
- **결함 · 지금**: 10-15 도구들과 척도가 다름(§6 #2). 이후 `anal_band_run.py`(10-15, 패딩 차체 ↔ 중심, 구간별 프레임 수)가 같은 질문을 다른 척도로.

### 9.5 `Docs/tools/anal_mppi_sim.py fpchk=1` — Nav2 방식 둘레 검사 시뮬 (10-13 §8 · §9 · §11) ★
- **형태**: Jetson, `run_sim_box2.sh` · `run_sim_box3.sh`(장면 f2o1 13:32:59 · 300 주기, f2p1 14:14:22 · 350 주기, 씨앗 1~10). 공통 인자는 10-08 `job944_fwdsim.sh` 의 것(실측 구동계 · `obst=1` CostCritic · `dyn_path=2 dyn_cost=1`) + `fwd_w=15 vx_min=-0.06 cost_w=3.81`.
- **하는 일(10-13 추가분)**: `fpchk=1` 이면 패딩 풋프린트 `FPV`(앞 0.272 · 뒤 0.258 · 반폭 0.175)의 꼭짓점을 `np.floor((vx - OX) / RES)` 로 칸에 내리고 변을 정수 직선(`floor(… + 0.5)` 반올림 보간 — Bresenham 과 동률 처리에서 한 칸 다를 수 있음)으로 그어 최대 비용, 254 면 충돌. 후보 전부 충돌인 주기는 실패로 세고 그 주기 명령 0. `pad` 인자(10-13 §11, `2887e666`). 출력 끝 `후보 전부 충돌(실패) 주기 59 회 — 처음 24.1 s …` · `LETHAL 여유(차체 외곽↔1 m 안 LETHAL 셀, 반셀 뺌): 최소 0.028 @23.7 s`.
- **출력**: [`sim_repro_fp.txt`](../debug_log/2026-10-13/outputs/sim_repro_fp.txt) 36 · 39 행(씨앗 3 f2o1) · [`sim_repro_fp2.txt`](../debug_log/2026-10-13/outputs/sim_repro_fp2.txt).
- **결함**: Nav2 소스와 한 줄씩 대조 안 한 흉내. 이 자리에서 실제보다 약 5 cm 넉넉(10-13 §10 · §12.1 f2q1 로 확인) → 절대값으로 설정을 정하면 안 됨.
- **계보**: job419 → job452 → job776 → 이 도구(10-13 고정 이름) → 10-26 굽은 곳 판. 본체 해설은 [오프라인 MPPI 시뮬레이터 카드](mppi-offline-simulator.md).

### 9.6 `Docs/tools/anal_plan_keepout.py` — 전역 카메라 칸 금지 띠 재계획 (10-14 §1)
- **형태**: PC `anal_plan_keepout.py bag [--step 8] [--box 정지HH:MM:SS] [--at HH:MM:SS …]`.
- **하는 일**: 8 s 마다 전역 코스트맵 치명 칸 중 nvblox 슬라이스가 ≤ 0 인 자리(±1 칸)를 '카메라 칸' 으로 가르고, inflation 을 반경 0.70 · 감쇠 2.0 · 내접 0.175 로 다시 계산한 뒤 카메라 칸 둘레 D 안을 통과 불가로 덧씌움 → 그때 로버 → 그때 `/plan` 끝점까지 8 방향 다익스트라(칸 비용 50 + 0.8 × 비용, 10-13 §5.2 의 NavFn 흉내). D = 0.175 · 0.25 · 0.30 · 0.35 · 0.40.
- **출력**: [`keepout_all.txt`](../debug_log/2026-10-14/outputs/keepout_all.txt) — `0.350 m  3 / 23  1  +0.00 · +0.08 m  10:55:04(통로 막힘) …`, `계획 14:14:28 — 경로 ↔ 상자 끝: D 0.175 → 0.26 m … D 0.300 → 0.31 m`.
- **판정에 준 영향**: 판정 기준 선언 없이 돌린 탐색 — 채택 판정 아님(SUMMARY 가 명시). 사용자가 '다른 좁은 곳도 막힘' 으로 기각.
- **지금**: 다시 쓸 수 있음(계획기가 Smac 으로 바뀐 뒤엔 NavFn 흉내라는 점이 한계).

### 9.7 10-12 · 10-13 그날 도구
| 도구 | 실행 · 인자 | 하는 일(핵심) | 출력 · 쓰인 곳 |
|---|---|---|---|
| `2026-10-12/jobs/box_smooth.py` | PC, `이름=npz …`(Jetson 추출 npz — 원천 소실, bag 에서 재생성 가능) | 복귀 상자 구간(마지막 목표 시작 뒤 x 2.6 → 0.4) 1 s 표: 지령 v · w, 차체(HL 0.25 · HW 0.165) ↔ 로컬 치명 최소, 차체 안 내접 칸 수, 새 경로 수 · 옆 이동. 요약 = 평균 v · v < 0.04 시간 · 후진 시간 · |w| > 0.1 부호 반전 | [`f2f1_box_smooth.txt`](../debug_log/2026-10-12/outputs/f2f1_box_smooth.txt) 70 · 117 행 → 10-12 §2 표. `top_eval.py` · `gap_eval.py` 는 [포화 카드](network-saturation-mppi-viz.md) |
| `2026-10-13/jobs/anal_f2o1_options.py` | PC | A 스무더 전후 경로 거리, B inflation 재계산 + NavFn 흉내(전역 대책 → E 카드), **C 정지 자세에서 직후진 · 직전진 · 회전한 자세의 풋프린트 둘레 최대 비용**(1 cm 간격 표본) | [`f2o1_options.txt`](../debug_log/2026-10-13/outputs/f2o1_options.txt) 38~44 행 `직후진 거리(cm): 0→99 … 제자리 회전(°, +왼쪽): … +10→100` → 10-13 §5.4 |
| `run_sim_box.sh` · `run_sim_box2.sh` · `run_sim_box3.sh` | Jetson | 9.5 의 묶음 실행(첫 판 fpchk 0, 둘째 · 셋째 fpchk 1 씨앗 1~3 · 4~10) | §2 표 |

### 9.8 10-14 그날 도구
| 도구 | 실행 · 인자 | 하는 일(핵심 문턱) | 출력 · 쓰인 곳 |
|---|---|---|---|
| `anal_box_shift_angle.py` | `bag 관측 정지 상자x 상자y` | map→odom 변화로 상자가 지도에서 움직인 양을 '관측 자리 이동(위치 몫)' 과 '각 변화 × 관측 거리(각도 몫)' 로, 시선 수직 성분도 | [`box_shift_angle.txt`](../debug_log/2026-10-14/outputs/box_shift_angle.txt) `· 각도 몫(각 변화 × 1.48 m) (+1.6, +1.5) cm = 2.2 cm [검산: 0.86° × 1.48 m = 2.2 cm]` → §4.2 |
| `anal_box_edge_growth.py` | `bag 정지 시작` | ① 정지 때 차체 최근접 nvblox 장애물 칸을 가운데로 **odom 고정 7 × 7 창**, 1 s 마다 장애물(거리 ≤ 0) 칸 · 새로 생김 · 사라짐 · 로버 쪽 1 · 2 줄 칸 수 ② 18 × 11 cm 상자를 5 cm 격자에 각도 6 가지 × 어긋남 400 가지로 찍어 면 밖으로 나간 거리 | [`box_edge_growth.txt`](../debug_log/2026-10-14/outputs/box_edge_growth.txt) `13:33:01  1.47 m  +25°  8  6  1 | 2 · 0`, `격자와  5° 어긋남: 3.5 / 5.4` → §5.1 · §5.2 |
| `anal_sw_turn.py` | `bag 시작 끝 [간격 0.5] [치명 문턱 100]` | 0.5 s 마다 로버 방향, `/transformed_global_plan` 0.3 m 앞 방향 · 경로 오차 · 옆 거리, 명령 v · ω, 최적 궤적 끝 방향, 차체 좌 · 우 옆 여유(치명 칸까지). '상자 쪽 틀기' = ω 가 여유 작은 쪽으로 | [`anal_sw_turn_f2t1.txt`](../debug_log/2026-10-14/outputs/anal_sw_turn_f2t1.txt) · `anal_box_f2u{1,2,3}.txt` 도 같은 도구 → §20 · §22 · §22.2. 첫 판 문턱 99 로 음수 여유(정정) |
| `anal_sw_yawsweep.py` | `bag HH:MM:SS …` | 같은 자리에서 방향만 바꿔 차체(패딩) 안 최대 비용 · 둘레 15 cm 띠 비용 합 · 최근접 치명 칸과 그 모서리 | [`anal_sw_yawsweep_f2t1.txt`](../debug_log/2026-10-14/outputs/anal_sw_yawsweep_f2t1.txt) → '−51° 부터 충돌 · 모든 방향 99' |
| `anal_box_edge_map.py` | `이름=bag@HH:MM:SS …` | 상자 구역(x 0.9~1.7, y −0.6~0.25) 로컬 · 전역 치명 칸의 x 열별 북쪽 가장자리 y + map→odom | [`anal_box_edge_map_f2u.txt`](../debug_log/2026-10-14/outputs/anal_box_edge_map_f2u.txt) → §22 'A −0.18 → B +0.09' |
| `anal_blob_src.py` | `bag 시작 끝 [x0 x1 y0 y1]` | 지도 구역의 로컬 치명 칸 수 · 라이다 점 수 2 s 마다(라이다는 쿼터니언 전체 변환 — 첫 판 yaw 만이라 거울상) | 원문 출력 파일 없음(SUMMARY §22 수치만 — **원천 소실**) |
| `anal_navfn_replay.py` | `bag HH:MM:SS.f 목표x 목표y` | OccupancyGrid → 원가 역변환(1~98 → 1 + (v − 1) × 251 / 97, 99 → 253, 100 → 254), NavFn 변환(253 이상 장애물, 50 + 0.8 × 원가) 8-연결 다익스트라 vs bag `/plan` 의 253 이상 점 수 · 0.3 m 앞 방향 | [`anal_navfn_replay_f2u.txt`](../debug_log/2026-10-14/outputs/anal_navfn_replay_f2u.txt) `bag /plan 길이 1.41 m · 0.3 m 앞 방향 -146° · … 253 이상 점 20/55` → §24 |
| `anal_slice_blob.py` | `bag 시작 끝 [구역]` | 슬라이스마다 구역 칸 수 · 아는 칸 · 최소 거리 · ≤ 0.05 m 칸 | [`anal_slice_blob_f2u2.txt`](../debug_log/2026-10-14/outputs/anal_slice_blob_f2u2.txt) → '덩어리 26 칸 끊김 없음' |
| `fig_box_end_plans.py` · `chk_nav2_window.sh` | PC 그림 · Jetson `/tmp/nav2.log` 시각 구간 출력 | 전역 코스트맵 + 로컬 치명 + 라이다 + `/plan` 나란히 | [`box_end_plans_f2u.png`](../debug_log/2026-10-14/figures/box_end_plans_f2u.png). nav2.log 는 덮여 B 구간 **원천 소실** |

### 9.9 10-15 그날 도구 (모두 PC · rosbags, `chk_box_face.py` · `chk_box_dump.py` 만 Jetson · 로버 정지)
| 도구 | 하는 일(핵심 문턱) | 출력 · 쓰인 곳 |
|---|---|---|
| `anal_ahead_cells.py` · `fig_stall_view.py` | 차체 좌표 x −0.30~+0.60 · |y| ≤ 0.20 안 치명 · 미지 칸 수 / f2v1 · f2t1 정지 장면 | [`anal_ahead_cells_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_ahead_cells_f2v1.txt) · [`figures_stall_f2v1.png`](../debug_log/2026-10-15/figures/figures_stall_f2v1.png) → §3 '0 · 0' |
| `anal_motion_probe.py` | 패딩 차체(0.272 · −0.258 · 0.175)를 전진 0.10~0.26 · 후진 0.05~0.10 · 회전 ±15~±150° · 전진+회전으로 옮겨 **넓이 전체**로 치명 칸 닿음 검사(Nav2 둘레 검사보다 엄격) · 최근접 거리 | [`anal_motion_probe.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe.txt) · `_f2v3` · `_f2v3r` · `_f2v4` → §5 · §18 · §20 |
| `anal_near_cells_src.py` | 기준 순간 차체 R 안 치명 칸마다 라이다 점 3.5 cm 안 여부 · 다른 순간 존재 여부 | [`anal_near_cells_src.txt`](../debug_log/2026-10-15/outputs/anal_near_cells_src.txt) 등 → '모두 카메라만' |
| `fig_stall_cells.py` | 라이다 확인(파랑) · 카메라만(주황) 칸, 최근접 시간열, 4.4 cm 선 | [`stall_cells_westpass.png`](../debug_log/2026-10-15/figures/stall_cells_westpass.png) → §6 |
| `anal_cell_first_seen.py` | 칸(지도 좌표 **3 cm 안** 맞춤)이 처음 치명이 된 프레임의 카메라 방위 · 거리(시야 |방위| ≤ 43° · ≤ 1.4 m), 그 뒤 시야 안 · 치명 아님 프레임 | [`anal_cell_first_seen_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_first_seen_f2v1.txt) → §7. 뒤 열(깜빡임)은 실수 ③ 의 근원 |
| `anal_path_center.py` · `anal_mapfix_replan.py` | 전역 한 장에서 inflation 재계산(0.70 · 감쇠 2.0/3.0/5.0 · 내접 0.175) + NavFn 변환 다익스트라, 출발 x 바꾸기 / 저장 지도 서쪽 벽 36 칸 비운 사본 | [`anal_path_center.txt`](../debug_log/2026-10-15/outputs/anal_path_center.txt) · [`anal_mapfix_replan.txt`](../debug_log/2026-10-15/outputs/anal_mapfix_replan.txt) → §9.1 · §11. 첫 판 칸 중심 정확값 선택으로 0 칸(원점이 0.05 배수 아님, 정정) |
| `anal_cam_vs_lidar.py` | 1 s 마다 시야 |방위| ≤ 40° · 0.3~1.3 m 라이다 점에 대해 카메라 → 점 1 cm 씩 진행, 슬라이스 첫 점유 지점과의 차(±2.5 cm 기준 앞 · 같음 · 뒤 · 누락) | [`anal_cam_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar.txt) → §9.2(실수 ④) |
| `anal_map_vs_lidar.py` | y 5 cm 띠마다 라이다 서 · 동 면 vs 저장 지도 점유 경계 | [`anal_map_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_map_vs_lidar.txt) → §10 |
| `anal_flicker_filter.py` · `anal_cell_ratio_odom.py` · `anal_grid_phase.py` · `anal_lidar_strip.py` | odom 칸별 시야(방위 ≤ 43° · 0.15~1.4 m · 가림 없음) · 점유 누적 / **odom 칸 `floor(x/0.05)` 고정** 시야 안 치명 · 점유 비율 / 두 격자 원점 mod 0.05 위상차 / 지도 띠 안 라이다 점 시각 · 방위 | [`anal_flicker_westbox_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_flicker_westbox_f2v1.txt) · [`anal_cell_ratio_odom_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_ratio_odom_f2v1.txt) · [`anal_grid_phase_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_grid_phase_f2v1.txt) · [`anal_lidar_strip_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_lidar_strip_f2v1.txt) → §12 |
| `chk_box_face.py` · `chk_box_dump.py` · `fig_box_dump.py` | Jetson 정지 — 로컬 치명 칸의 상자 서쪽 면 x 프레임마다 / 깊이 점군 · 슬라이스 · 코스트맵을 tf2 로 저장(npz, §24 부터 `base_link` 기준 인자) / 세 층 + 실제 상자 그림 | [`box_face_A.txt`](../debug_log/2026-10-15/outputs/box_face_A.txt) · [`box_face_B.txt`](../debug_log/2026-10-15/outputs/box_face_B.txt) · `outputs/boxdump/` · [`box_site_AB.png`](../debug_log/2026-10-15/figures/box_site_AB.png) → §22 ~ §24 |
| `anal_memory_shift.py` | 칸의 나중 지도 좌표 → 나중 map→odom 으로 odom → 처음 map→odom 으로 지도: 두 지도 좌표 차 = 기억 밀림(처음 순간 map 이 참이라는 가정) | [`anal_memory_shift_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_memory_shift_f2v1.txt) `밀림 Δx -0.1 cm · Δy -2.1 cm · 크기 2.1 cm` → §24.1 |
| `anal_replan_trace.py` | `/plan` 마다 처음 0.6 m 방향 · 상자 구역 최소 거리, 구역 카메라 칸 수, 로버 자세 | [`anal_replan_trace_f2v3r.txt`](../debug_log/2026-10-15/outputs/anal_replan_trace_f2v3r.txt) → §19 |
| `anal_stall_entry.py` ★ | 로컬 코스트맵 프레임마다(odom) `fp_now`(꼭짓점 `floor` 내림 + 변 Bresenham 최대 — FootprintCollisionChecker 식) · `fp_prev`(같은 자세 앞 프레임 지도) · `fp_was` · `new8` · `opt`(직전 최적 궤적 32 점의 최대 fp · 첫 치명 점) · `dev`(0.5 s 전 예측 대비) · `exact`(패딩 차체 ↔ 치명 칸 중심) | [`anal_stall_entry.txt`](../debug_log/2026-10-15/outputs/anal_stall_entry.txt) → §28 결론 전부 |
| `anal_box_true_vs_map.py` ★ | 기록 상자(x 1.151~1.261 · y −0.20~−0.02)와 상자 구역 치명 칸(칸 가장자리 기준 북 · 남 · 서 · 동 면), 실제 여유(패딩 · 몸체 ↔ 기록 직사각형) · 지도 여유(패딩 ↔ 칸 중심) | [`anal_box_true_vs_map.txt`](../debug_log/2026-10-15/outputs/anal_box_true_vs_map.txt) 47 행 `요약: 실제 여유(패딩 포함) 최소 9.5 cm · 지도 여유 최소 4.8 cm · … 북쪽 면 중앙 +0.062(실제보다 +8.2 cm 로버 쪽)` → §29.4. 출발 자세 테이프 오차 1~2 cm 섞임(머리말) |
| `anal_cmd_timeline.py` · `fig_passage_f2w2.py` | 0.5 s 칸 자세 · Δyaw · v · ω · 명령 수 · 최대 간격 · 지도 여유 / 통로 남행 한 장(라이다 · 카메라 칸 누적, A · B 확대, 여유 · ω · 놓침) | [`anal_cmd_timeline_f2w2.txt`](../debug_log/2026-10-15/outputs/anal_cmd_timeline_f2w2.txt) · [`passage_f2w2_south.png`](../debug_log/2026-10-15/figures/passage_f2w2_south.png) → §32 · §33 |
- 계보 · 지금: 10-15 도구는 모두 '오늘만'. 상시화된 것은 없다. `anal_stall_entry.py` 의 fp 식과 `anal_box_true_vs_map.py` 는 이 문제를 다시 볼 때 첫 도구로 쓸 만하다(bag 에 로컬 코스트맵 · `/trajectories` · tf 가 있으면 됨).

## 10. 용어
- **카메라만 본 칸(라이다 0)**: 로컬 코스트맵 치명 칸 중 같은 순간 라이다 점이 3.5 cm(도구마다 2.5~4 cm) 안에 없는 칸 — 라이다(0.185 m)보다 낮은 물체 또는 카메라 과장 · 유령.
- **odom 기억**: nvblox 슬라이스와 로컬 코스트맵은 odom 좌표에 쌓인다. 시야 밖으로 나간 칸은 감쇠(0.99, 약 81 s)나 지우기 반경(3 m) 전까지 odom 자리에 남고, 그 사이 SLAM 이 map→odom 을 고치면 지도(실제) 위에서 그만큼 옮겨 보인다.
- **지도 고정 착시**: 칸을 지도 좌표로 고정해 시간에 걸쳐 세면, odom 칸이 보정 변화만큼 미끄러져 이웃 칸과 번갈아 잡혀 '깜빡임 · 늦게 뜸' 처럼 보이는 것(실수 ① · ③).
- **풋프린트 칸 검사(fp)**: Nav2 FootprintCollisionChecker — 풋프린트 꼭짓점을 칸 번호로 내리고(floor) 변을 칸 단위 직선으로 그어 지나는 칸의 최대 비용. 차체 윤곽이 칸 바깥에 있어도 내린 윤곽이 칸을 지나면 '닿음'.
- **뒤집힘 띠(경계 띠)**: 패딩 차체 ↔ 치명 칸 중심 정확 거리 약 2.7~4.4 cm — 이 구간에선 칸 내림 위상에 따라 fp 가 99(내접, 충돌 아님) ↔ 100(치명, 충돌)으로 갈린다(10-15 §28). 칸이 아니라 거리 구간.
- **99(내접 253)**: 차체 윤곽이 치명 칸 중심 17.5 cm(내접 반지름 = 반폭 0.165 + 패딩 0.01) 안이면 늘 나오는 값. 충돌이 아니고 CostCritic 에선 중심 비용만 벌점.
- **서 있는 자세부터 닿음**: 현재 자세의 fp 가 100 이면 MPPI 의 모든 후보가 첫 점에서 충돌, BackUp 도 같은 검사로 0.0 s 실패 → 대기 5 s × 2 → 약 12 s 뒤 Goal failed.
- **이상 경로형 · 좁은 여유형**(10-14 §24): 계획기 경로가 낮은 물체를 가로질러 MPPI 가 머리를 돌리다 막히는 것 · 경로는 정상인데 여유 4~5 cm 라 순간 막히는 것.
- **과장(주행 중 · 정지)**: 카메라 칸의 로버 쪽 면 − 실제 면. 기록 상자 대비 주행 중 +5~10 cm(4 주행), 정지 정면 · 옆면 0~3 cm(점군부터 2~3 cm).
- **격자 계단**: 상자 변이 5 cm 격자와 나란하지 않을 때 '조금이라도 겹치는 칸' 이 장애물이 되어 면 밖으로 나가는 거리(5° 에서 평균 3.5 · 최대 5.4 cm, 계산).
