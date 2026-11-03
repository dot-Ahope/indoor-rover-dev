# 상자 옆 정지 — 시험한 대책들(전역 감쇠 · 패딩 · cost_weight · 금지 띠 · 지도 · nvblox 설정 · MonotoneEscape · ClearanceBandCritic)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **조사 중(10-15 시점)** — 10-13 ~ 10-15 에 대책 19 개를 시험 · 평가했다. **남은 것은 둘**: ① `MonotoneEscape`(교착 탈출 복구, BT 에 켬 — 실제 교착에서의 판정은 **0 회**, 재현 시도 2 번 모두 교착을 못 만듦) ② `ClearanceBandCritic`(칸 판정 경계 띠 회피 — 주행 2/2 에서 띠 진입 0 · 교착 0 이었지만 제어 주기 놓침 167 · 428 회로 **끔**, 코드 유지). 나머지(전역 감쇠 3.0 · BT 후진 · 패딩 0 · cost_weight 2 · 3 배 · 전역 금지 띠 · 목표 이동 · 지도 수정 · 카메라 칸 낮추기 2 가지 · nvblox site 1.0 · 통합 거리 2.0 · 1.0)는 효과 없음 · 부작용 · 사용자 기각 · 미주행으로 되돌렸다 | 10-13 §4.6 · §5 ~ §6 · §9 ~ §14, 10-14 §1 ~ §6 (· §27 기준선 코스), 10-15 §8 ~ §13 · §18 ~ §31 · §34 (이 카드), 이후 10-19 ~ | [10-13 §4.4 · §4.5](../debug_log/2026-10-13/SUMMARY.md)(f2o1 목표 3 이 출발점 앞 낮은 상자 옆에서 '후보 전부 충돌' 로 ABORTED, 사용자 "로버 정면 왼쪽에 상자가 있었고, 닿지는 않았다") | `ros2_ws/src/rover_navigation/config/nav2_params.yaml`(전역 `cost_scaling_factor` 3.0 → 2.0 되돌림 · `CostCritic.cost_weight` Jetson 에서만 11.43 → 3.81 · `ClearanceBandCritic` 블록 · `monotone_escape` 블록), `config/nvblox_local.yaml`(통합 거리 1.4 → 2.0 → 1.4 → 1.0 → 1.4, site 2.0 → 1.0 → 2.0), `config/nav_to_pose_no_spin.xml`(BackUp → `server_name="monotone_escape"`), `src/monotone_escape_behavior.cpp` · `src/clearance_band_critic.cpp` · `behavior_plugins.xml` · `mppi_critic_plugins.xml` · `CMakeLists.txt` · `package.xml` — 커밋 `0fca2dd4`(10-15 §26) · `9d71c40d` · `ffa806e7`(§29) · `d767368f` · `1ded74b3`(§30) | [상자 옆 정지 — 기전](box-side-stall-cause.md)(같은 줄기의 '왜 멈추나', 10-13 §4.6 · §6.2 · §8 · §10 · 10-15 §5 ~ §7 · §28) · ['갇혔을 때만 패딩 0' pad_relief](pad-relief-runtime-padding.md)(10-13 §14.2 · 10-14 §2 · §7 ~ §23) · [낮은 상자 기억 · 전역 nvblox](low-box-global-memory.md)(10-07 ~ 10-08 앞 줄기) · [F2 기준선 no5](f2-baseline-no5.md)(10-15 §2 ~ §21 기준선 3/6) · [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md)(`anal_mppi_sim.py` fpchk · pad) · [inflation · padding 역할](inflation-padding-roles.md) · [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md) · [prep_fast 기동](prep-fast-startup.md)(10-15 §30 `sed -i` 링크 끊김) · [Phase N 후반 · 유령 셀](nvblox-n6-global-ghosts.md)(통합 거리 1.4 의 출처) · [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(09-23 '여유 4.4 cm 에서 LETHAL') |

**한 줄**: 출발점 앞 낮은 시험 상자(라이다 아래, 카메라만 봄)와 서쪽 통로 상자 옆에서 로버가 가끔 '후보 전부 충돌' → 후진 실패 → 약 12 s 만에 Nav2 포기로 섰다. 실제로는 8~11 cm 비어 있었지만(사용자 줄자 10-13 §5.6 · 10-15 §18.2) 코스트맵에서는 2~5 cm 였다. 10-13 은 '경로를 더 멀리' 쪽(전역 감쇠 3.0 → f2p1 같은 자리 재정지, cost_weight 3 배 → f2q1 4.3 cm · 머뭇거림)과 '갇히는 문턱 낮추기'(패딩 0 — 시뮬에선 멈춤 1/10 → 0/10 이지만 사용자 기각 "상자를 돌아가야지 더 붙어서 가는 건 문제")를 시험해 모두 되돌렸다. 10-14 는 전역 카메라 금지 띠(0.30 m 까지 경로 유지, 0.35 m 면 그 통로 막힘 — 여유 한 칸)를 사용자가 기각했다. 10-15 는 '지도 쪽 cm 깎기'(목표를 통로 가운데로 · 저장 지도 벽 고침 · 깜빡이는 카메라 칸만 낮추기 · nvblox site 1.0 · 통합 거리 1.0)가 모두 효과 없음이거나 판정 불가였고, 방향을 바꿔 **'붙어도 서지 않게'**(ClearanceBandCritic — 띠 진입 0 이지만 계산 부담) 와 **'서면 여유가 줄지 않는 쪽으로만 빠져나오기'**(MonotoneEscape — 오프라인 5/5, 실제 교착 재현 실패) 를 만들었다. 이 시기 끝 구성: 통합 거리 1.4 · 크리틱 끔 · 탈출 켬(10-15 §31).

---

## 0. 대책 한눈 표
'선언' = 주행 · 계산 **전에** 적은 판정 기준. '지금' = 11-03 저장소 코드(§6 에 줄 번호).

| # | 대책 | 날짜 · § | 방법 | 선언한 기준 | 결과(측정) | 판정 | 지금 |
|---|---|---|---|---|---|---|---|
| 1 | 전역 inflation 감쇠 2.0 → 3.0 | 10-13 §5.2 · §5.3 · §5.6 · §6.1 | 오프라인 재계획(`anal_f2o1_options.py` B) → 주행 f2p1 | 효과 있음 = 경로 ↔ 상자 끝 ≥ 0.30 m **그리고** 차체 여유 ≥ 8 cm · 3 목표 성공 / 효과 없음 = < 0.28 m 또는 같은 자리 정지 | 오프라인 0.260 → 0.310 m(+5 cm). f2p1 경로 0.24~0.28 m, 목표 3 ABORTED (1.347, 0.263) — f2o1 정지 자리에서 약 10 cm | **효과 없음** → 2.0 되돌림(사용자 "1번 진행하라") | 2.0 |
| 2 | BT 에 짧은 직후진 | 10-13 §5.4 | 정지 자세 풋프린트 비용 탐색(`anal_f2o1_options.py` C) | (분석, 선언 없음) | 기하로는 직후진 · 오른쪽 회전이 99(치명 아님)인데 실제 후진 복구 3 회 모두 "Collision Ahead" | **안 함** — 같은 칸 단위 검사기에 걸림(추정) | — |
| 3 | 전역 지도가 상자를 오래 기억 | 10-13 §5.1 | — | — | — | **보류**(사용자: 동적 물체도 남아 전역 경로가 막힘) | — |
| 4 | footprint_padding 0.01 → 0(상시) | 10-13 §11 · §11.1 | MPPI 시뮬 `pad=0` | 효과 = 상자 두 장면 멈춘 씨앗 1/10 → 0/10 · 부작용 = 여유 < 0 씨앗 | 0/10 · 0/10, 여유 < 0 없음. 좁은 곳 최악 2.7 → 0.4 cm | 시뮬 합격 → **사용자 기각**("상자를 돌아가야지 더 붙어서 가는 건 문제") | 0.01 |
| 5 | CostCritic cost_weight 2 · 3 배(시뮬) | 10-13 §9 · §9.1 | `anal_mppi_sim.py fpchk=1` 장면 5 × 가중 3 × 씨앗 10 | 효과 = 상자 두 장면 중앙값 +3 cm **그리고** 최악 ≥ 5 cm / 부작용 = 통로 멈춤 증가 또는 전진 < 90 % | 2 배 중앙 +0.1 · −2.0 cm, 최악 3.3 · 4.3. 3 배 최악 7.3 · 8.1 이지만 중앙 +1.7, 전진 −18 · −19 · −44 % | **기준 미달** — 시뮬 근거로는 안 올림 | — |
| 6 | cost_weight 3 배(11.43) 주행 | 10-13 §12 · §12.1 | f2q1(Jetson yaml 만) | 효과 = 상자 구역 최소 ≥ 6 cm · 2 s 정지 없음 · 3 목표 / 효과 없음 = < 5 cm 또는 같은 자리 정지 | 최소 4.3 cm · 구역 체류 58.8 s(평소 27~29) · 목표 1 67.9 s(+17) · 목표 3 CANCELED 상자 앞 | **효과 없음 + 부작용** → 3.81(사용자 "이전 구성으로") | 3.81 |
| 7 | nvblox 통합 거리 1.4 → 2.0 | 10-13 §14.1 → 10-14 §5.4 · §6 | yaml 만(다음 prep) | (주행 확인 예정이었음) | 2.0 으로 한 번도 안 띄움 | 사용자 지시로 2.0 → 다음 날 사용자 지시로 **1.4**(멀리서 볼수록 불리 근거 2 건) | 2.0(10-22 다시 바꿈, 이후) |
| 8 | 갇혔을 때만 패딩 0(pad_relief) | 10-13 §14.2 · 10-14 §2 ~ §23 | 시뮬 → 노드 → 주행 | (그 카드) | 시뮬 5/5 탈출. 실행 중 패딩 토글 뒤 멈칫 증가(A/B) | **켜지 않음** — [pad_relief 카드](pad-relief-runtime-padding.md) | 끔(launch 기본) |
| 9 | 전역 카메라 장애물 금지 띠 D | 10-14 §1 · §4.1 | 오프라인 재계획 `anal_plan_keepout.py`(주행 3 · 계획 71) | **선언 없이 돌린 탐색**(§1 첫 줄에 명시) | D 0.30 경로 없음 0/71 · 상자 끝 +5~10 cm, D 0.35 10/71 '통로 막힘'(바로 그 상자 옆) | **사용자 기각**("다른 좁은 곳도 같은 식으로 막힐 수 있다") | — |
| 10 | 서쪽 통로 목표를 통로 가운데로 | 10-15 §9.1 | 오프라인 다익스트라 `anal_path_center.py`(출발 x 4 × 감쇠 3) | (사용자 결정 대책, 효과 확인) | 12 경우 모두 상자 옆 경로 x −1.765~−1.715 · 동쪽 여유 11.0 cm 같음 | **효과 없음**(길이 지도 단면으로 정해짐) | — |
| 11 | (가) 카메라만 본 칸 일괄 한 칸 낮추기 | 10-15 §9.2 · §9.3 | 카메라 면 vs 라이다 면 `anal_cam_vs_lidar.py` | 사용자 전제 "과대평가는 해도 과소평가는 못할 때 적절" | 과소 10.4 · 12.1 % · 누락 1.6 · 3.1 % — 그러나 라이다가 보는 물체라 (가)와 무관(§9.3 정정) | **위험 — 안 함**(근거는 §12 에서 다시 바뀜) | — |
| 12 | 저장 지도 서쪽 벽 바로잡기 | 10-15 §10 · §11 | 고친 사본으로 재계획 `anal_mapfix_replan.py` | (효과 확인) | 지날 수 있는 폭 0.30 → 0.40 m 인데 경로는 두 판 모두 x −1.765 · 상자 앞면 11.0 cm | **효과 없음** → 지도 그대로 | — |
| 13 | 후보 3: 깜빡이는 카메라 칸만 낮추기 | 10-15 §12 | `anal_flicker_filter.py` → odom 칸 고정 재계산 `anal_cell_ratio_odom.py` | ① 서쪽 통로: 과장 줄 낮춤 · 실제 면 유지 · 최근접 > 4.4 cm ② 시험 상자: 면 칸 남음 | 멈춘 칸이 시야 안 90~91 % 꾸준히 치명 — 깜빡이지 않음 | **① 불합격**, ② 안 함(§7 '30 % 깜빡임' 은 착시로 철회) | — |
| 14 | nvblox `esdf_integrator_max_site_distance_vox` 2.0 → 1.0 | 10-15 §13 · §22 · §22.1 · §22.2 · §23 | 정지 A/B(출발 테이프, 정면 약 0.9 m) `chk_box_face.py` · `chk_box_dump.py` | ① 1.0 의 면이 실제보다 0~5 cm 앞 ② 과장이 3 cm 이상 감소 | 면 1.144 vs 1.138(차 0.6 cm), 줄자 0.92 m 대비 둘 다 약 3.2 cm 앞 · 점군도 같은 차 | **② 불합격** → 2.0 유지 | 2.0 |
| 15 | MonotoneEscape(교착 탈출 복구) | 10-15 §25 · §25.1 · §26 · §27 ~ §27.5 | 오프라인 `anal_monotone_escape.py` → C++ behavior 플러그인 → 실제 시험 `run_escape_test.py` | 오프라인: 실패 5 건 중 ≥ 4 건에서 0.30 m 안 '줄지 않은 채 ≥ 5 cm' / 실제: 재현(후보 전부 충돌) 뒤 (a) 거리 3 mm 넘게 안 줄임 (b) 끝에 ≥ 5 cm (c) 접촉 없음 | 오프라인 **5/5**. 실제 1 차: 지도 8.6 cm(줄자 8.6) — 교착 아님, '이미 충분' 0.0 s 성공. 2 차: 지도 4.3 cm 까지 만들었으나 Nav2 가 그대로 22.8 s 도착 | 오프라인 합격 · **실제 판정 불가**(재현 2/2 실패) | **켬**(BT 복구) |
| 16 | ClearanceBandCritic 첫 판 | 10-15 §28 · §29 · §29.1 · §29.2 | MPPI 크리틱(띠 0.06 · 가중 20), 주행 f2w1(b910) | ① 두 코스 도착 ② 상자 옆 최소 ≥ 5 cm(또는 피할 수 없던 자리 설명) ③ 제어 주기 놓침 기준선 수준 ④ 서쪽 통로 통과 | 3/3 · 최소 4.8 cm · 2.7~4.4 cm 띠 0 프레임 · fp 100 0 · 놓침 **167**/206 s | ② 엄밀히 미달 · **③ 불합격** | — |
| 17 | ClearanceBandCritic 가볍게 고친 판 | 10-15 §29.3 · §29.6 · §34 | 치명 칸 목록 + 통, 주행 f2w2(no5) | 같은 ①~④ | 8/8 · 최소 4.9 cm(서쪽 통로 5.1~6.0) · 띠 0 · fp 100 0 · 놓침 **428**/430 s · 크리틱 최대 162 ms | 기능 ✔(①②④) · **③ 불합격** → §30 에서 **끔** | 끔(코드 유지) |
| 18 | 사용자 제시 nvblox 번짐 대책 3 가지 | 10-15 §29.7 | 검토만 | — | ① 복셀 0.025: 3D 8 배 · 코스트맵 칸 그대로 ② 통합 거리 제한: 가장 싸고 근거 맞음 → #19 ③ 팽창 하향: 우리 멈춤은 치명 칸 자체라 해당 안 됨 | ②만 시험으로 | — |
| 19 | nvblox 통합 거리 1.4 → 1.0 | 10-15 §30 · §30.1 | 주행 선언 → 배터리 부족으로 bag 근사 `anal_intdist_slice.py` | 과장 중앙 ≤ +3 cm 채택 / +3~+5 일부 / ≥ +5 효과 없음(**주행 기준**) | 시야 안 생성 중 과장 칸의 23~56 % 가 이미 ≤ 1.0 m 에서 생김 | **판정 없음**(선언은 주행 기준) · 근거 약함 → 1.4 되돌림 | 2.0(10-22, 이후) |

## 1. 증상
- **f2o1 · f2p1(10-13 §4.4 · §5.6)**: 복귀 길 출발점 앞 낮은 상자 끝 옆에서 '후보 전부 충돌' 14 회 → 후진 3 회 "Collision Ahead" → Goal failed. 코스트맵 차체 여유 4.8 · 5.4 cm(칸 중심), **사용자 줄자 11 cm**(f2p1). 같은 상자 옆을 다른 6 주행은 2.8~4.7 cm 로 통과했다(10-13 §10 [`box_pass.txt`](../debug_log/2026-10-13/outputs/box_pass.txt)) — '통과와 정지가 1~2 cm 로 갈리는 자리'.
- **f2v1 · f2v3 · f2v4(10-15 §3 · §18 · §20.1)**: 서쪽 통로 상자(라이다 아래 상자 + 그 위 종이백) 옆 · 입구, 출발점 시험 상자 옆에서 같은 모양 — 지도 3.6 · 2.7 · 4.3 cm, f2v3 사용자 줄자 **8~9 cm**(§18.2). 기준선 6 회 중 3 회 불합격의 원인 전부(§21).
- 왜 멈추는지(기전)는 [상자 옆 정지 — 기전](box-side-stall-cause.md): 경로 근접 · odom 좌표 기억 밀림 · 카메라 과장 · Nav2 칸 단위 판정이 2.7~4.4 cm 에서 위상에 따라 뒤집힘(10-15 §28). 이 카드는 **그 위에서 무엇을 해 봤나**를 다룬다.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 앞 시기 10-07 ~ 10-08 | 전역 nvblox + 재계획 0.5 Hz | f2e2 차체 ↔ 상자 최소 0.06 m | 상자 옆 여유가 작다는 것만 남김 | [낮은 상자 기억 카드](low-box-global-memory.md) |
| 10-13 §4.6 | 정지 원인 가림 → 고칠 곳 후보 4 개 | 경로 ↔ 상자 끝 0.22~0.29 m | 후보 1 '전역 inflation 감쇠를 완만하게' ❌ 방향 틀림(§5.2 정정, 실수 ①) | [`f2o1_box_history.txt`](../debug_log/2026-10-13/outputs/f2o1_box_history.txt) |
| 10-13 §5.1 | 사용자 결정: 1 번 진행 · 2 번(오래 기억) 보류 · 3 · 4 번 영향 평가부터 | — | 기억 시간은 정적 물체 vs 동적 물체 맞바꿈 | 10-13 §5.1 |
| 10-13 §5.2 | 스무더 탓? · inflation 변경 재계획 | 스무더 차 0.2~0.6 cm. 감쇠 2.0 → 0.260 · 3.0 · 5.0 → 0.310 · 1.0 → 0.210 m, 반경 · 패딩 무영향, 패딩 0.15 경로 없음 | 3.0 으로(효과 5 cm = 격자 한 칸) | [`f2o1_options.txt`](../debug_log/2026-10-13/outputs/f2o1_options.txt) A · B |
| 10-13 §5.4 | 4 번(탈출 수단) 평가 | 직후진 0~30 cm · 직전진 · 오른쪽 회전 5~40° 모두 99, 왼쪽 10° 이상 100 | 기하로는 탈출 가능, Nav2 는 칸 단위 검사로 전부 충돌(추정) → BT 후진 추가는 효과 없음 | 같은 파일 C |
| 10-13 §5.6 | f2p1(전역 감쇠 3.0) | 실행 중 3.0 · 0.7 확인. 목표 3 ABORTED, 경로 0.24~0.28 m, 사용자 줄자 11 cm | **효과 없음**. '이번엔 늦게 떴다' ❌(§6.2 정정 — 지도 좌표 고정 칸의 착시, [기전 카드](box-side-stall-cause.md)) | [`prep_f2p1.txt`](../debug_log/2026-10-13/outputs/prep_f2p1.txt) · [`run_f2p1.txt`](../debug_log/2026-10-13/outputs/run_f2p1.txt) · [`f2p1_box_history.txt`](../debug_log/2026-10-13/outputs/f2p1_box_history.txt) · bag `2026-10-13/bags/bag_f2p1.tgz`(로컬) |
| 10-13 §6.1 | 되돌림 | Jetson yaml 2 곳 2.0, 실행 중 Nav2 는 다음 prep 까지 3.0 | — | `jobs/up_ginfl_only.sh` |
| 10-13 §9 | cost_weight 영향 시뮬 선언 | 장면 5(상자 2 · 통로 1 · 실제 통과 2) | 선언 정정(실행 전): f2a10 은 '실제로 지나간' 장면이 아님(실수 ②) | 10-13 §9 |
| 10-13 §9.1 | 150 회 시뮬 | 표 §0 #5. out_f2p1 30 회 무효(시작 시각이 첫 경로보다 이름, 실수 ③) | **기준 미달** — 시뮬 근거로는 안 올림 | [`sim_sweep_summary.txt`](../debug_log/2026-10-13/outputs/sim_sweep_summary.txt) |
| 10-13 §10 | 기존 bag 11 주행의 상자 옆 여유 | 통과 6 회 2.8~4.7 cm, 정지 2 회 2.2 · 1.8 cm. 실제 8 회 모두 < 5 cm 인데 시뮬은 10 씨앗 중 9 개 5~11 cm | **시뮬은 이 자리에서 실제보다 약 5 cm 넉넉** → 시뮬 절대값으로 설정을 정하지 않음 | [`box_pass.txt`](../debug_log/2026-10-13/outputs/box_pass.txt) |
| 10-13 §11 · §11.1 | 패딩 0 시뮬 | 멈춘 씨앗 1/10 → 0/10(두 장면), 통로 최악 2.7 → 0.4 · 실제 통과 구간 3.2 → 0.7 cm | 시뮬 합격 → **사용자 기각**: 대책 방향을 '갇히는 문턱 낮추기' 가 아니라 '더 멀리 돌기' 로 고정 | [`sim_pad0_summary.txt`](../debug_log/2026-10-13/outputs/sim_pad0_summary.txt) |
| 10-13 §12 · §12.1 | f2q1(cost_weight 11.43) | prep 확인은 이름 틀려 "Parameter not set"(실수 ④) → `chk_costw.sh` 로 11.43. 최소 4.3 cm · 구역 58.8 s · 목표 3 CANCELED(1.571, 0.246). 사용자 "너무 돌아가려 하니, 좁은 곳을 통과하기 어려워한다" | **효과 없음 + 부작용**, 시뮬 3 배 최악 7.3~8.1 cm 와 어긋남 → 3.81 | [`prep_f2q1.txt`](../debug_log/2026-10-13/outputs/prep_f2q1.txt) · [`run_f2q1.txt`](../debug_log/2026-10-13/outputs/run_f2q1.txt) · 상자 구역 수치 원천 소실 · bag `2026-10-13/bags/bag_f2q1.tgz`(로컬) |
| 10-13 §12.2 | 오늘 대책 정리 | 감쇠 · BT 후진 · 패딩 0 · 가중 3 배 · 기억 — 모두 기각 · 되돌림 · 보류 | 원인 셋(경로 근접 · 기억 밀림 4~5 cm · 칸 검사 약 5 cm) 중 어느 것도 못 줄임 | 10-13 §12.2 |
| 10-13 §13 | 사용자 "다시 봤을 때 갱신되게는?" | 다시 보면 이미 갱신됨. 멀리서 잊는 것은 `map_clearing_radius_m: 3.0`, 다시 보이는 거리 1.5 m 는 통합 거리 1.4 | 더 일찍 갱신해도 이 정지는 안 풀림(추정 — 밀림은 시야 밖 옆을 지날 때 생김) | `config/nvblox_local.yaml`(그날 판) |
| 10-13 §14.1 | 사용자 "2.0 으로 복구" | yaml 만, 재기동 없음 | 다음 주행에서 유령 칸 · 재관측 거리 확인 예정 | `jobs/up_nvblox_integ.sh` |
| 10-13 §14.2 | 갇혔을 때만 패딩 0 — 시뮬 | 정지 자세 2 곳 0/5 → 5/5 탈출 | → [pad_relief 카드](pad-relief-runtime-padding.md) | [`sim_unstuck_summary.txt`](../debug_log/2026-10-13/outputs/sim_unstuck_summary.txt) |
| 10-14 §1 | 전역 카메라 금지 띠 탐색(선언 없음) | 표 §0 #9 | 0.30 은 통과 · 0.35 는 막힘 — 여유 한 칸, 갇힘이 '경로 없음' 으로 바뀔 위험 | [`keepout_all.txt`](../debug_log/2026-10-14/outputs/keepout_all.txt) |
| 10-14 §4.1 | 사용자 "1번은 진행하면 여러 부분에서 문제가 생길 것 같다" | — | 금지 띠 **안 함** | 10-14 §4.1 |
| 10-14 §5.4 · §6 | 멀리서 볼수록 불리(처음 볼 때 한 줄 두껍게 · 각 오차 × 거리) → 사용자 "1.4로 되돌려라" | 2.0 으로 실행된 적 없음 | 통합 거리 1.4 | [`box_edge_growth.txt`](../debug_log/2026-10-14/outputs/box_edge_growth.txt) · [`box_shift_angle.txt`](../debug_log/2026-10-14/outputs/box_shift_angle.txt) · 커밋 `0c05555a` |
| 10-14 §24 · §25 | 복귀 길 정지 두 종류(이상 경로형 · 좁은 여유형) → 사용자 "좁은 여유형은 지금 시스템으로 어느 정도 된다", 출발점 상자 = 일부러 둔 시험 물체 | 그날 이 자리 지난 주행 전부 접촉 없이 도착, 멈춤 2 번(사람 개입 없이 복구) | **이 자리는 지금 바꾸지 않음**(10-14 시점 결정) | 10-14 §24 · §25, [`anal_navfn_replay_f2u.txt`](../debug_log/2026-10-14/outputs/anal_navfn_replay_f2u.txt) |
| 10-15 §3 ~ §8 | 기준선 f2v1 서쪽 통로 정지 → 현장 확인(상자 + 종이백) | 지도 3.6 cm, 로버가 통로 가운데보다 상자 쪽 13 cm | 대책 후보 1(목표 가운데로) · 2(복구 변경 — 위험) · 3(복셀 — 비권고) | [기전 카드](box-side-stall-cause.md) · [`anal_motion_probe.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe.txt) |
| 10-15 §9.1 | 대책 1 오프라인 | 12 경우 같은 경로 · 11.0 cm | **효과 없음**. '서쪽도 카메라 과장' ❌ → 저장 지도 벽(실수 ⑤) | [`anal_path_center.txt`](../debug_log/2026-10-15/outputs/anal_path_center.txt) |
| 10-15 §9.2 · §9.3 | (가) 전제 검증 | 과소 10~12 % · 누락 2~3 % | '전제 불성립 → (가) 부적절' ❌ 근거가 라이다 물체(§9.3 정정, 실수 ⑥). 결론은 '여전히 위험' 으로 유지(근거 교체) | [`anal_cam_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar.txt) · [`anal_cam_vs_lidar_breakdown.txt`](../debug_log/2026-10-15/outputs/anal_cam_vs_lidar_breakdown.txt) |
| 10-15 §10 · §11 | 저장 지도 서쪽 벽(라이다 대비 약 10 cm 두꺼움) 고친 사본 | 폭 0.30 → 0.40 m · 경로 그대로 x −1.765. 첫 계산은 칸 중심 정확값으로 골라 0 칸 ✘ → 범위로 | **효과 없음**, 지도 그대로 | [`anal_map_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_map_vs_lidar.txt) · [`anal_mapfix_replan.txt`](../debug_log/2026-10-15/outputs/anal_mapfix_replan.txt) |
| 10-15 §12 | 후보 3(깜빡이는 칸) 오프라인 | odom 칸 고정: 바깥 줄(멈춘 칸 포함) 치명 90~91 % · 조각 90~100 %, 더 바깥 줄 3~6 % | **① 불합격**. §7 '30 % 깜빡임' ❌ 지도 좌표 맞춤 착시(실수 ⑦) | [`anal_flicker_westbox_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_flicker_westbox_f2v1.txt) · [`anal_cell_ratio_odom_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_cell_ratio_odom_f2v1.txt) · [`anal_grid_phase_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_grid_phase_f2v1.txt) |
| 10-15 §13 | 사용자 줄자: 상자 앞면이 종이백보다 5.8~6.0 cm 앞 → 과장 약 7 cm · site 거리 확인 | 라이브러리 기본 1.0, 벤더 예제 2.0, 우리 2.0(예제 그대로, 검토한 적 없음) | site 1.0 후보(판정식은 컴파일 코드라 미확인) | `jobs/chk_nvblox_site.sh`(출력 원천 소실) |
| 10-15 §21 | 기준선 3/6 · 개선 후보 ① site 1.0 ② 서쪽 통로 목표 방향 고정 | — | 같은 코스 전후 비교 계획 | [F2 기준선 카드](f2-baseline-no5.md) |
| 10-15 §22 · §22.1 · §22.2 | site 2.0 vs 1.0 정지 A/B | 면 1.144 vs 1.138, 줄자 0.92 m(지도 0.888 · 0.887) | **② 불합격** — 정면 0.9 m 관측은 거의 정확 | [`box_face_A.txt`](../debug_log/2026-10-15/outputs/box_face_A.txt) · [`box_face_B.txt`](../debug_log/2026-10-15/outputs/box_face_B.txt) |
| 10-15 §23 | 세 층(점군 · 거리 지도 · 코스트맵) 원자료 | 두 조건 같음, 점군부터 실측보다 −2.3~−3.4 cm. §22.1 'B 에서 행 y 0.00 빠짐' 은 측정마다 차(정정) | **2.0 유지**(저장소도 되돌림) | `outputs/boxdump/box_dump_{A_site2,B_site1}.npz` · [`box_site_AB.png`](../debug_log/2026-10-15/figures/box_site_AB.png) · 커밋 `89661faf` |
| 10-15 §24 · §24.1 | 옆면을 앞 측면에서 정지 관측(가설 ③ '스치듯 볼 때 두껍게') | 거리 지도 · 코스트맵이 실제보다 1.6~1.7 cm **안쪽**. 기억 밀림 2.1 · 2.3 cm(로버 쪽 아님) | 가설 기각 → 대책 방향 전환: cm 깎기 대신 '붙어 서지 않게' | `outputs/boxdump/box_dump_P{1,2}.npz` · [`anal_memory_shift_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_memory_shift_f2v1.txt) · [`anal_memory_shift_f2v3.txt`](../debug_log/2026-10-15/outputs/anal_memory_shift_f2v3.txt) |
| 10-15 §25 · §25.1 | 사용자 "경유점을 늘리는 식보다는 … 가끔씩 발생하는 문제를 해결하고 싶다" → '여유가 줄지 않는 곧은 이동' 오프라인 | 실패 5 건 모두 빠져나갈 방향 있음 | **5/5 합격** → 구현 제안 | [`anal_monotone_escape.txt`](../debug_log/2026-10-15/outputs/anal_monotone_escape.txt) |
| 10-15 §26 | MonotoneEscape 구현 · 배포 | 1 차 빌드 실패(package.xml 중복 의존) · 1 차 기동 실패(플러그인 xml `name` 누락) → 적재 확인 | 회전 문제 답: 중간 목표는 위치만 + 탈출에 작은 회전 포함 | 커밋 `0fca2dd4` · `jobs/up_escape.sh` · `up_escape2.sh` · `up_escape_xml.sh` · `chk_escape_loaded.sh`(출력 원천 소실) |
| 10-15 §27 · §27.1 · §27.2 | 실제 시험 1 차(평소 출발에서 왼쪽 25 cm) | gap 예상 8.9 cm · 지도 최근접 8.6 cm(줄자 8.6). creep 2 회 '라이다 4 cm 안' 즉시 정지 → 판정을 앞 절반 점만으로 | 교착 재현 안 됨 · 탈출 '이미 충분' 0.0 s 성공(설계대로) → **판정 불가** | `jobs/run_escape_test.py` · `chk_scan_near.py` · 탈출 로그 원천 소실 · bag `/tmp/bag_esc3`(Jetson, 원천 소실) |
| 10-15 §27.3 · §27.4 · §27.5 | 2 차: 선언을 두 번 바꿈(사용자 제안) → 기본 출발에서 Nav2 로 지나다 일부러 회전 | 가는 길 발동 안 함. 복귀 길 첫 호출 출력 없음(원인 미확인) → 다시: 발동 여유 8.9 cm → 왼쪽 12.5° 회전 → 지도 4.3 cm(앞 모서리) → 같은 목표 다시 **22.8 s 성공**, 탈출 줄 없음. 사용자 "닿지 않았다" | **재현 실패 → 판정 없음**. 회전으로는 '옆면 한가운데 4 cm' 를 만들기 어렵다(추정) — 실제 시험은 순회 중 자연 발생으로 | 10-15 §27.5 · `jobs/chk_esc_log.sh`(출력 원천 소실) |
| 10-15 §28 · §28.1 | 멈춤에 들어가는 경로(실패 3 건) | 지도 변화 아님 · 예측 오차 ≤ 0.3 cm · 칸 판정이 2.7~4.4 cm 에서 위상에 따라 99 ↔ 100 | 대책 ① '풋프린트 99 에 벌점' ❌(§29 정정, 실수 ⑧) | [`anal_stall_entry.txt`](../debug_log/2026-10-15/outputs/anal_stall_entry.txt) · [기전 카드](box-side-stall-cause.md) |
| 10-15 §29 · §29.1 · §29.2 | ClearanceBandCritic 첫 판 → f2w1(b910) | 3/3 · 최소 4.8 cm · 띠 0 · 놓침 167(같은 날 크리틱 없는 스택 16) | ③ 불합격 → 계산 줄임 | [`anal_band_run_b910.txt`](../debug_log/2026-10-15/outputs/anal_band_run_b910.txt) · [`run_f2w1.txt`](../debug_log/2026-10-15/outputs/run_f2w1.txt) · 놓침 수 원천 소실 · 커밋 `9d71c40d` |
| 10-15 §29.3 | 치명 칸 목록 + 통, 시간 기록 | 결과 값은 첫 판과 같음 | 다음 주행에서 ③ 재확인 | 커밋 `ffa806e7` |
| 10-15 §29.4 · §29.5 | 기록 상자 vs 찍힌 상자(사용자 "여유 상당히 많았고, 그리고도 또 더 회피") | f2w1 실제 여유 9.5 cm · 지도 4.8 cm, 북쪽 면 +8.2 cm 로버 쪽(네 주행 +5.3~+9.6). 남동쪽 덩어리 = 창문틀 · 드론(사용자) | '이중 여유' = 의도 안 한 과장 ① 위에 의도한 띠 ③. §29.4 '좁은 곳 통과를 막을 수 있어' 는 지나친 표현(§29.5 정정) | [`anal_box_true_vs_map.txt`](../debug_log/2026-10-15/outputs/anal_box_true_vs_map.txt) · [`box_true_vs_map.png`](../debug_log/2026-10-15/figures/box_true_vs_map.png) |
| 10-15 §29.6 | f2w2(no5, 가벼운 판) | 8/8 · 최소 4.9 · 서쪽 통로 5.1~6.0 · 띠 0 · 탈출 1 회(PathBlockedAhead 복구에서, 6.3 cm 라 움직임 없이 성공) · 놓침 428 · 크리틱 중앙 7.8 · 최대 162 ms | 기능 2/2 · **③ 불합격, 운용 불가** | [`anal_band_run_no5.txt`](../debug_log/2026-10-15/outputs/anal_band_run_no5.txt) · [`run_f2w2.txt`](../debug_log/2026-10-15/outputs/run_f2w2.txt) · [`missed_sec_f2w2.txt`](../debug_log/2026-10-15/outputs/missed_sec_f2w2.txt)(80 s 창만) |
| 10-15 §29.7 | 사용자 자료 3 가지 검토 | 표 §0 #18 | 통합 거리 제한이 첫 시험 | 10-15 §29.7 |
| 10-15 §30 | 통합 거리 1.0 · 크리틱 끔 선언 | prep `sed -i` 가 설치본 nav2_params 링크를 일반 파일로 바꿔 놓아 `enabled: true` 가 남아 있었음 → 배포 도구에 링크 복구 | — | `jobs/up_cfg_intdist.sh` · 커밋 `d767368f` · [prep_fast 카드](prep-fast-startup.md) |
| 10-15 §30.1 | 배터리 부족 → bag 근사 | 1 차(로컬 코스트맵) 무효 ✘ · 2 차(nvblox 조각) 과장 칸 23~56 % 가 ≤ 1.0 m 에서 생성 | **판정 없음** · 근거 약함 → 1.4 되돌림, 크리틱 끔 유지 | [`anal_intdist_proxy.txt`](../debug_log/2026-10-15/outputs/anal_intdist_proxy.txt) · [`anal_intdist_slice.txt`](../debug_log/2026-10-15/outputs/anal_intdist_slice.txt) · 커밋 `1ded74b3` |
| 10-15 §31 | 하루 정리 | 끝 상태: 통합 거리 1.4 · 크리틱 끔 · 탈출 켬 | 다음 ① 깊이 bag → nvblox 오프라인 A/B ② 크리틱 거리장 방식 ③ 탈출은 자연 교착에서 검증 | [`stall_trace_1015.html`](../debug_log/2026-10-15/figures/stall_trace_1015.html) |
| 10-15 §32 · §34 | f2w2 서쪽 통로 — 몸 튼 것 · 안 멈춘 이유 | 크리틱 없는 f2v2 도 같은 자리 같은 크기로 틂. f2w2 fp 100 0/727, 띠 0 프레임 · f2v2 는 띠 안 12 프레임을 위상 운으로 통과 | 몸 틀기는 연산 탓 아님. 크리틱이 띠 밖에 두었다 — '크리틱 덕에 통과' 는 1 회라 단정 못 함 | [`anal_cmd_timeline_f2w2.txt`](../debug_log/2026-10-15/outputs/anal_cmd_timeline_f2w2.txt) · [`anal_cmd_timeline_f2v2.txt`](../debug_log/2026-10-15/outputs/anal_cmd_timeline_f2v2.txt) · [`passage_f2w2_south.png`](../debug_log/2026-10-15/figures/passage_f2w2_south.png) |
| 이후(10-19 ~) | 다음 시기에서 채움 | — | — | — |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 전역 감쇠를 가파르게 하면 경로가 상자에서 멀어져 정지가 풀린다 | 오프라인 재계획(10-13 §5.2) + f2p1 | 오프라인 +5 cm, 실제 0.24~0.28 m · 같은 자리 정지 | **기각(1 회)** — 그 주행은 계획 시각 전역 상자 칸이 1/4 라 공정 비교 아님(그래도 효과 근거 없음) |
| MPPI 옆 여유 가중을 올리면 넓게 돈다 | 시뮬 150 회 + f2q1 | 시뮬 3 배 최악 7~8 cm, 실제 4.3 cm · 머뭇거림 | **기각** — 경로 추종이 이김 · 진행만 느려짐. 시뮬은 이 자리에서 약 5 cm 낙관(측정) |
| 갇히는 문턱을 낮추면(패딩 0) 정지가 없어진다 | 시뮬 | 1/10 → 0/10, 대신 1 cm 더 붙음 | 시뮬 **지지** — 그러나 방향이 사용자 요구와 반대(기각) |
| 카메라 장애물만 두껍게 하면(금지 띠) 더 멀리 돈다 | 오프라인 재계획 | 0.30 m 까지 +5~10 cm, 0.35 m 에서 그 통로 막힘 | **지지(오프라인)** · 여유 한 칸이라 기각(사용자) |
| 경로가 상자 쪽으로 붙는 건 목표 좌표 때문이다(서쪽 통로) | 출발 x 4 개 재계획 | 12 경우 같은 길 | **기각** — 지도 단면이 길을 정함 |
| 저장 지도의 두꺼운 서쪽 벽이 경로를 상자 쪽으로 민다 | 고친 사본 재계획 | 폭은 늘었으나 경로 같음 | **기각(재계산 기준)** — 실제 NavFn(퍼텐셜)과 다를 수 있음 |
| 과장 칸은 깜빡이므로(시야 안 30 % 빠짐) 걸러낼 수 있다 | odom 칸 고정 재계산 | 멈춘 칸 90~91 % 꾸준 | **기각** — 30 % 는 내 분석의 착시 |
| site 거리 2.0 이 면 앞 한 칸을 만든다 | 정지 A/B · 세 층 원자료 | 정면 0.9 m 에서 두 값 같음, 점군부터 −3 cm | **기각(정면 · 정지 조건)** — 주행 중 +5~10 cm 과장의 원인은 아님 |
| 정지해서 옆면을 스치듯 봐도 두껍게 찍힌다 | P1 · P2 몸체 좌표 관측 | 지도가 오히려 1.6~1.7 cm 안쪽 | **기각** |
| 멀리서 처음 찍힌 칸이 과장된다 → 통합 거리 1.0 이면 줄어든다 | bag 의 nvblox 조각 생성 순간 거리 | 과장 칸 23~56 % 가 이미 ≤ 1.0 m | **약함(근사)** — 깊이 영상 없는 bag 이라 재현 불가, 주행 판정 없음 |
| 여유가 줄지 않는 직진 · 회전만으로 교착에서 빠져나올 수 있다 | 실패 순간 코스트맵 고정 모의 5 건 | 5/5(직진 0.02~0.30 m) | **지지(오프라인)** · 실제 교착에서 미검증 |
| 정확 거리 6 cm 띠 벌점이면 칸 판정 경계(2.7~4.4 cm)에 안 들어간다 | f2w1 · f2w2 | 띠 프레임 0 · 0, fp 100 0 · 0 | **지지(2 회)** · 계산 부담 불합격, 크리틱 없는 주행도 위상 운으로 통과한 적 있어 인과는 1 회 비교 |

## 4. 조치와 효과
### 4.1 전역 감쇠 3.0 (10-13, 되돌림)
- 배포: `jobs/prep_deploy_ginfl.sh 3.0` — Jetson 소스 · 설치본 yaml 의 `inflation_radius: 0.70` 바로 다음 `cost_scaling_factor` 를 정규식으로 바꾸고 prep, 실행 중 값 확인:
  ```
  s2 = re.sub(r'(inflation_radius: 0\.70\n\s+cost_scaling_factor: )[0-9.]+', r'\g<1>' + v, s)
  ```
  결과 `실행 중 전역 inflation: Double value is: 3.0 · Double value is: 0.7` (`2026-10-13/outputs/prep_f2p1.txt` 45 행).
- 효과: `목표 3 ABORTED 102.6 s | 도착 map (1.347, 0.263, 167.9°)` (`2026-10-13/outputs/run_f2p1.txt` 21 행). 판정 기준(≥ 0.30 m)에 못 미침 → `jobs/up_ginfl_only.sh 2.0`. 저장소 yaml 에 시험 결과 주석(지금 `nav2_params.yaml` 713~719 행).

### 4.2 cost_weight 3 배 (10-13, 되돌림)
- 배포 `jobs/prep_deploy_costw.sh 11.43`(yaml 2 곳 + prep). 결과 `CostCritic cost_weight 1 곳 → 11.43 (바뀜)` · 실행 중 확인 줄은 `CostCritic cost_weight Parameter not set`(`2026-10-13/outputs/prep_f2q1.txt` 2 · 47 행 — 이름 오류, 실수 ④). 올바른 이름으로 본 `chk_costw.sh` 의 11.43 · 크리틱 8 개는 출력 원천 소실.
- 효과: `목표 1 SUCCEEDED 67.9 s` · `목표 3 CANCELED 125.3 s | 도착 map (1.571, 0.246, -152.1°)` (`2026-10-13/outputs/run_f2q1.txt` 15 · 21 행). 되돌림 `jobs/up_costw_only.sh 3.81` — yaml 2 곳 + `ros2 param set /controller_server FollowPathMPPI.CostCritic.cost_weight 3.81`(재기동 없음). **저장소 yaml 은 바꾼 적 없음**(3.81).

### 4.3 통합 거리 2.0 → 1.4 (10-13 → 10-14, 사용자 결정 두 번)
- `jobs/up_nvblox_integ.sh <값>`: `sed -i -E "s/^(\s+projective_integrator_max_integration_distance_m: )[0-9.]+/\1$V/"`(링크인 설치본은 건너뜀, 재기동 없음). 10-13 §14.1 에 2.0, 10-14 §6 에 1.4 — **2.0 으로 실행된 적 없음**(10-14 §6). 근거 주석은 지금 `nvblox_local.yaml` 50~53 행.
- 실행 중 동적 조절(§14.2)은 [pad_relief 카드](pad-relief-runtime-padding.md).

### 4.4 nvblox site 1.0 (10-15, 되돌림)
- `jobs/up_nvyaml.sh`(Jetson src yaml 백업 뒤 교체, 설치본은 링크) → 적용 확인 `[nvblox_node]: static_mapper.esdf_integrator_max_site_distance_vox: 1` (`2026-10-15/outputs/box_face_B.txt` 끝 줄). 되돌림 `jobs/up_nvyaml_restore.sh`(1.0 판은 `nvblox_local.yaml.site1_<시각>` 로 보관).
- 효과: `[A_site2.0] … 상자 서쪽 면 x … 중앙 1.144` 대 `[B_site1.0] … 중앙 1.138 · … 칸 수 중앙 8` (`box_face_A.txt` · `box_face_B.txt` 2 행). 저장소 2.0 + 시험 주석(지금 `nvblox_local.yaml` 61~65 행).

### 4.5 MonotoneEscape (10-15, 켬 · 실검증 없음)
- 설계(`src/monotone_escape_behavior.cpp`, 커밋 `0fca2dd4` — 그 뒤 바뀌지 않음): `nav2_behaviors::TimedBehavior<nav2_msgs::action::BackUp>` 상속. 시작 때 `local_costmap/costmap_raw` 의 254 칸 중심(로버 1 m 안)을 모아 앞 · 뒤(1 cm 걸음 ≤ 0.30 m) · 좌 · 우 회전(1° 걸음 ≤ 0.52 rad)을 모의, 한 걸음이라도 거리가 줄면 그 움직임은 버림:
  ```cpp
  if (c < prev - 2e-4) {break;}  // 모의에선 한 걸음도 줄면 안 됨
  if (c >= target_clearance_) {reached = a; break;}
  ```
  (91 · 93 행) 닿는 것 중 `reached / limit` 가 가장 작은 것을 고르고, 실행 중 매 주기 거리가 `decrease_tolerance` 0.003 m 넘게 줄면 정지 · 실패(126~128 행). 이미 ≥ 0.05 면 움직이지 않고 성공(106 행), 닿는 움직임이 없으면 움직이지 않고 실패(107 행) → BT 의 Wait.
- 연결: BT `nav_to_pose_no_spin.xml` 복구 RoundRobin 의 `<BackUp backup_dist="0.30" backup_speed="0.03" time_allowance="20.0" server_name="monotone_escape"/>`(지금 126 행), `nav2_params.yaml` `behavior_plugins` 에 `monotone_escape`(788 행)와 파라미터 블록(796~808 행).
- 효과: 실제 교착에서 불린 기록 **0 회**(이 시기). 불린 기록 2 회는 모두 여유 충분(§27.1 8.6 cm · §29.6 6.3 cm)이라 움직이지 않고 성공. §27.1 로그 원문(SUMMARY 에 인용): `[monotone_escape] 시작 최근접 8.6 cm · 목표 5.0 cm · 모의 결과(닿는 양 m/rad): 앞:0.010 뒤:0.010 좌회전:0.018 우회전:없음(끝 8.6 cm)` — 파일은 원천 소실.

### 4.6 ClearanceBandCritic (10-15, 끔 · 코드 유지)
- 설계(`src/clearance_band_critic.cpp`, 첫 판 `9d71c40d` → 계산 줄인 판 `ffa806e7`, 그 뒤 바뀌지 않음): 궤적 점(2 점 간격)마다 중심 칸이 FREE 면 건너뛰고, 아니면 차체 직사각형(패딩 포함, `getRobotFootprint`) ↔ 치명 칸 중심 정확 거리 d 의 최소를 구해
  ```cpp
  if (dmin < band_) {acc += (band_ - dmin) / band_;}
  ...
  if (acc > 0.0f) {data.costs(i) += std::pow(weight_ * acc / npts, power_);}
  ```
  (117 · 119 행). 치명 칸 목록은 주기마다 한 번 만들고 한 변 reach(외접 + 띠 ≈ 0.38 m) 통에 담아 이웃 3×3 통만 본다(60~88 행). 100 주기마다 `ClearanceBandCritic 시간: 평균 · 최대 ms` 기록(122~130 행).
- 효과: 기능은 2/2(띠 프레임 0), 계산은 2/2 불합격. 저장된 80 s 창(17:36:00~17:37:20)의 기록 최대는 `ClearanceBandCritic 시간: 평균 66.91 ms · 최대 141.82 ms · 치명 칸 최대 89 · 평가 점 최대 16000 (100 주기)` (`2026-10-15/outputs/missed_sec_f2w2.txt` 90 행), 그 창의 놓침 합 232 회 / 62 초 칸(이번 집계, `awk` 로 '놓침' 줄 합).
- 끔: `ClearanceBandCritic: {enabled: false, …}`(지금 `nav2_params.yaml` 276 행). 크리틱 목록에는 이름이 남아 있어 플러그인은 적재되고 `score()` 첫 줄 `if (!enabled_) {return;}`(41 행)에서 빠진다.

### 4.7 되돌림 · 끔이 실제로 적용됐는지
- 10-15 §30: prep_fast 의 `sed -i`(PreferForward 값) 때문에 설치본 nav2_params 가 링크가 아닌 일반 파일이 되어 src 의 `enabled: false` 가 안 따라오고 있었다(측정 — 설치본 `enabled: true`). `up_cfg_intdist.sh` 에 링크 복구:
  ```bash
  [ -L $I ] || { rm -f $I && ln -s $D/nav2_params.yaml $I && echo "설치본 nav2_params 링크 복구"; }
  ```
  그 전 주행(§29 빌드 → prep 순서)은 영향 없었다고 SUMMARY 가 적음(빌드가 링크를 다시 만듦 — 추정). 상세는 [prep_fast 카드](prep-fast-startup.md).

## 5. 내 실수
### 실수 ① '전역 감쇠를 완만하게' 후보 — 방향이 반대 (10-13 §4.6 → §5.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 경로가 상자 끝에서 0.22~0.29 m 로 도는 것을 넓힐 후보 적기 |
| 본 것 | (수치 없이 쓴 후보) |
| 처음 추론 | 감쇠를 완만하게 하면 비용이 멀리까지 퍼져 경로가 더 멀리 돈다 |
| 의심한 이유 | 값을 정하기 전 재계획 평가(사용자 '1번 진행') |
| 판별 시험 | `anal_f2o1_options.py` B — 감쇠 1.0 · 2.0 · 3.0 · 5.0 |
| 결론 | 완만(1.0)이면 0.210 m 로 **더 붙음**, 가파른 3.0 · 5.0 이 0.310 m. 감쇠가 가파를수록 장애물 바로 옆과 조금 떨어진 곳의 비용 차가 커져 모서리를 넓게 돈다 |
| 다음에 알아보는 법 | inflation 손잡이의 방향은 말로 정하지 말고 재계획 한 번으로 확인. 반경은 내접 밖 여유에 거의 안 듣는다(09-16 0.269 → 0.265 와 같음) |
| 스크립트 핵심 | `2026-10-13/jobs/anal_f2o1_options.py` 42 행 `c = np.where(dist <= RINS, 253.0, np.where(dist <= r, 252.0 * np.exp(-k * (dist - RINS)), 0.0)); … cost = 50 + 0.8 * c; block = c >= 253` |
| 나온 결과 | `패딩 0.01 \| 0.70 · 1.0             0.210 m                  4.5 cm` · `패딩 0.01 \| 0.70 · 3.0             0.310 m                 14.5 cm` (`2026-10-13/outputs/f2o1_options.txt`) |
| 데이터 | 결과 `2026-10-13/outputs/f2o1_options.txt`, 도구 `2026-10-13/jobs/anal_f2o1_options.py`, 입력 bag `2026-10-13/bags/bag_f2o1.tgz` |

### 실수 ② 통로 장면 f2a10 을 '실제로 지나간 기준' 으로 선언 (10-13 §9, 실행 전 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | cost_weight 시뮬(`run_sim_sweep.sh`)에 시뮬 자체 점검 기준 넣기 |
| 본 것 | 선언문 "fpchk=1 이 그 장면에서 현재 값으로도 멈춘다고 나오면 — 실제 f2a10 은 그 구간을 지나갔으므로 — 지나치게 비관적" |
| 처음 추론 | f2a10 은 서쪽 통로 입구를 지났다 |
| 의심한 이유 | 실행 전 10-01 기록 재확인 |
| 판별 시험 | 10-01 §8.27 ~ §8.32 읽기 |
| 결론 | f2a10 은 통로를 **못 지났다**(목표 2 취소). 통로 장면은 상대 비교용으로만, 대신 실제 통과 구간 out_f2o1 · out_f2p1 을 점검 장면으로 추가 |
| 다음에 알아보는 법 | '실제 결과' 를 기준으로 쓸 땐 러너 결과 줄(SUCCEEDED/ABORTED)을 같은 선언에 붙인다 |
| 스크립트 핵심 · 나온 결과 | 해당 없음(선언 정정) |
| 데이터 | 10-13 §9 '선언 정정', [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md) |

### 실수 ③ out_f2p1 30 회의 시작 시각이 첫 경로보다 이름 (10-13 §9.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 실제 통과 구간 f2p1 14:11:47 부터 28 s 를 시뮬 점검 장면으로 |
| 본 것 | 요약 단계 '해석 실패 30 개' |
| 처음 추론 | (연결 끊김으로 요약이 안 넘어와 Jetson 결과를 다시 집계하다 발견) |
| 의심한 이유 | 한 장면만 30 개 전부 실패 |
| 판별 시험 | 오류 원문 확인 |
| 결론 | 시작 시각에 `/plan` 이 아직 없어 `gp[1]` 이 None — 장면 무효, 실제 통과 장면은 out_f2o1 하나로 판정 |
| 다음에 알아보는 법 | 시뮬 시작 시각은 bag 의 첫 경로 발행 뒤인지 먼저 확인 |
| 스크립트 핵심 | `2026-10-13/jobs/run_sim_sweep.sh` 장면 목록 `"out_f2p1 bag_f2p1 $(date -d 14:11:47 +%s) 280"` |
| 나온 결과 | `/tmp/sweep/out_f2p1_11.43_1.txt :: … line 94, in <module> \|     G_ = np.array([[q.pose.position.x, q.pose.position.y] for q in gp[1].poses]) \| TypeError: 'NoneType' object is not subscriptable` (`2026-10-13/outputs/sim_sweep_summary.txt`) |
| 데이터 | 결과 `2026-10-13/outputs/sim_sweep_summary.txt`, 도구 `run_sim_sweep.sh` · `anal_sweep_summary.py` · `Docs/tools/anal_mppi_sim.py`(커밋 `2887e666` 판 무렵) |

### 실수 ④ 실행 중 cost_weight 확인에 틀린 파라미터 이름 (10-13 §12.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2q1 전에 11.43 이 실제로 실행 중인지 확인(`prep_deploy_costw.sh` 끝 줄) |
| 본 것 | `실행 중: CostCritic cost_weight Parameter not set · critics Parameter not set` |
| 처음 추론 | (값이 안 읽힘 — 적용 실패인지 이름 문제인지) |
| 의심한 이유 | yaml 2 곳은 바뀜으로 나옴 |
| 판별 시험 | `chk_costw.sh` — `ros2 param list /controller_server` 에서 `CostCritic.cost_weight` 를 grep 해 그 이름으로 get |
| 결론 | 이름은 `FollowPathMPPI.CostCritic.cost_weight`(컨트롤러 플러그인 이름 접두). 실행 중 11.43 · 크리틱 8 개 확인 뒤 주행 |
| 다음에 알아보는 법 | 실행 중 값 확인은 이름을 추측하지 말고 `param list` 로 찾은 이름을 쓴다. 'not set' 은 값 문제가 아니라 이름 문제의 서명 |
| 스크립트 핵심 | `2026-10-13/jobs/chk_costw.sh` 5 행 `for p in $(timeout 20 ros2 param list /controller_server 2>/dev/null \| grep -i "CostCritic.cost_weight\|\.critics$"); do …` |
| 나온 결과 | 틀린 이름의 줄은 `2026-10-13/outputs/prep_f2q1.txt` 47 행. `chk_costw.sh` 출력은 원천 소실 |
| 데이터 | 위 두 파일, 도구 `prep_deploy_costw.sh` · `chk_costw.sh` |

### 실수 ⑤ '서쪽도 카메라 과장' (10-15 §8 · 대화 → §9.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 서쪽 통로 계획기 폭을 좁힌 원인 설명 |
| 본 것 | 전역 지도 단면 서쪽 끝 x −2.10, 오늘 라이다 벽 −2.23 |
| 처음 추론 | 서쪽도 카메라가 과장한 것 |
| 의심한 이유 | `anal_path_center.py` 단면에서 그 칸의 출처를 가름 |
| 판별 시험 | 단면의 층 출처 + `anal_map_vs_lidar.py`(라이다 − 저장 지도, 이틀 세 순간) |
| 결론 | 출처는 **저장 지도 office_v3**(서쪽 −12.4~−12.8 · 동쪽 −3.2~−3.6 cm). 카메라가 아님 |
| 다음에 알아보는 법 | 치명 칸 출처는 층별(정적 · 라이다 · 카메라)로 갈라 본 뒤 말한다 |
| 스크립트 핵심 | `2026-10-15/jobs/anal_path_center.py` 방법 주석 "NavFn 비용 변환(253 이상 장애물, 50 + 0.8 × 원가) 8-연결 다익스트라" |
| 나온 결과 | `-1.65   기록값(2.0) -1.765 ~ -1.715                11.0 cm                     29.0 cm        -1.565` (`2026-10-15/outputs/anal_path_center.txt`) |
| 데이터 | `2026-10-15/outputs/anal_path_center.txt` · `anal_map_vs_lidar.txt`, 도구 같은 이름 `jobs/*.py` |

### 실수 ⑥ (가) 의 근거로 라이다가 보는 물체의 과소를 씀 (10-15 §9.2 → §9.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 전제 '카메라는 과소평가하지 못한다' 검증(`anal_cam_vs_lidar.py`) |
| 본 것 | 과소 10.4 · 12.1 %, 누락 1.6 · 3.1 %, 특정 장소에 몰림 |
| 처음 추론 | 전제 불성립 → (가) 부적절 |
| 의심한 이유 | 사용자 "과소 문제일 경우 라이다로 해결 가능한 부분 아닌가?" |
| 판별 시험 | 원리 대조 — 기준 면이 라이다 점이므로 잰 물체는 전부 라이다가 막는다 |
| 결론 | 근거가 결론과 무관. (가)에 중요한 건 '라이다에 안 보이는 물체에서 바깥 카메라 칸이 늘 실제 면보다 앞인가'. 그 대체 근거(§7 의 30 %)도 §12 에서 착시로 철회 → (가)는 근거 없이 '위험' 판단만 남음 |
| 다음에 알아보는 법 | 검증 대상(카메라만 본 물체)과 기준 자료(라이다 점)의 범위가 겹치는지 먼저 확인 |
| 스크립트 핵심 | `2026-10-15/jobs/anal_cam_vs_lidar.py` — 카메라 시야 \|방위\| ≤ 40° · 0.3~1.3 m 의 라이다 점을 기준 면으로, 카메라→점 선 위 nvblox 첫 점유와의 차 |
| 나온 결과 | 표 §2 행(`2026-10-15/outputs/anal_cam_vs_lidar.txt` · `anal_cam_vs_lidar_breakdown.txt`) |
| 데이터 | 위 두 파일 |

### 실수 ⑦ 칸을 지도 좌표로 맞춰 세어 '깜빡임 30 %' 를 만듦 (10-15 §7 → §12)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 서쪽 통로 상자 바깥 줄 칸이 시야 안에서 얼마나 빠지나(`anal_cell_first_seen.py`) |
| 본 것 | 바깥 줄 약 30 % 치명 아님 → 후보 3 의 근거 |
| 처음 추론 | 과장 칸은 깜빡인다 → 깜빡이는 칸만 낮추면 실제 면은 남는다 |
| 의심한 이유 | 후보 3 검증에서 칸을 odom 격자로 고정하자 비율이 달라짐 |
| 판별 시험 | `anal_grid_phase.py`(조각 · 코스트맵 odom 위상차 0) → `anal_cell_ratio_odom.py` |
| 결론 | 그 사이 map→odom 이 0.2° · 약 2 cm 바뀌어 같은 odom 칸이 지도에서 2~3 cm 움직이며 이웃 칸과 번갈아 잡힘. 바깥 줄은 90~91 % 꾸준 → §8 · §9.3 의 '깜빡이는 과장 칸' 철회 |
| 다음에 알아보는 법 | nvblox · 로컬 코스트맵 칸은 **odom 칸 번호**로 센다(10-13 §6.2 와 같은 함정의 재발) |
| 스크립트 핵심 | `2026-10-15/jobs/anal_cell_ratio_odom.py` 머리 주석 "조각과 코스트맵은 odom 에서 원점 위상이 같다(anal_grid_phase) → odom 칸 번호 floor(x/0.05) 로 바로 맞출 수 있다" |
| 나온 결과 | `(-1.481, -4.254)                                30                 27 ( 90 %)    27 ( 90 %)` · `(-1.527, -4.152)                                33                  1 (  3 %)     5 ( 15 %)` (`2026-10-15/outputs/anal_cell_ratio_odom_f2v1.txt`) |
| 데이터 | `anal_cell_first_seen_f2v1.txt` · `anal_grid_phase_f2v1.txt` · `anal_cell_ratio_odom_f2v1.txt`, 도구 같은 이름 |

### 실수 ⑧ '풋프린트 비용 99 에 벌점' 설계 (10-15 §28 대책 ① → §29)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 칸 판정 경계 띠로 붙지 않게 하는 MPPI 벌점 설계 |
| 본 것 | 멈춤 직전 서 있는 자세 fp 99 |
| 처음 추론 | 99 = 치명 한 칸 옆이니 99 인 궤적 점을 벌하면 된다 |
| 의심한 이유 | `cost_critic.cpp` 1.1.20 주석 "footprintCostAtPose will always return INSCRIBED if footprint is over it" 와 §28 표(f2v4 정확 여유 17.4 cm 에서 이미 99) |
| 판별 시험 | 소스 읽기 + 측정 표 대조 |
| 결론 | 99 는 치명 칸 중심 17.5 cm(내접) 안이면 늘 나옴 → 상자 17 cm 안 전체를 벌해 좁은 곳을 못 지남. 정확 거리 띠(6 cm)로 바꿈 |
| 다음에 알아보는 법 | Nav2 비용 값(253/99)을 '거리' 로 읽기 전에 그 값이 나오는 거리 범위를 계산 |
| 스크립트 핵심 | 해당 없음(설계 정정) — 정정 판 `src/clearance_band_critic.cpp` 4~7 행 주석 |
| 나온 결과 | `anal_stall_entry.txt`(§28 표의 원문) |
| 데이터 | `2026-10-15/outputs/anal_stall_entry.txt`, 10-15 §29 |

### 작은 실수 · 시행착오 (한 줄씩, 원문 경로)
- 10-15 §11 저장 지도 칸을 칸 중심 정확값(−2.15 · −2.10)으로 골라 0 칸(전역 지도 원점이 0.05 배수 아님) → 범위로(`jobs/anal_mapfix_replan.py`).
- 10-15 §26 1 차 빌드 실패 — `package.xml` 에 nav2_behaviors · nav2_costmap_2d 가 이미 exec_depend 로 있어 중복(`jobs/up_escape2.sh`), 1 차 기동 PREP_FAIL — `behavior_plugins.xml` 에 `name="rover_navigation/MonotoneEscape"` 누락(`jobs/up_escape_xml.sh`).
- 10-15 §27.1 `chk_scan_near.py` 첫 판의 '원거리' 열은 필터 뒤 색인이 어긋남(몸체 좌표 · 여유는 맞음) → 고친 판으로 교체. creep 안전 판정이 차체 왼쪽 뒤 1~2 cm 의 라이다 점(자체 부착물인지 미확인)에 걸려 앞 절반 점만으로 바꿈(`run_escape_test.py` 주석 §27.1).
- 10-15 §27.5 복귀 길 첫 navturn 호출이 출력 없이 끝남(원인 미확인, nav2.log 에 follow_path Aborting 1 줄).
- 10-15 §30.1 `anal_intdist_proxy.py` 1 차는 로컬 코스트맵(로버 따라 움직이는 창)이라 '창에 들어옴' 이 섞여 1.4 m 넘는 '처음 찍힘' 이 나옴 → 무효, `anal_intdist_slice.py` 로.
- 10-15 §22.1 'B 에서 행 y 0.00 빠짐' → §23 저장에선 A · B 모두 없음, 측정 때마다의 차(정정).
- 10-15 §29.4 '이중 여유가 좁은 곳 통과를 막을 수 있어' → §29.5 '막지는 않고 느려지거나 반대편 벽 쪽으로 밀릴 수 있음' 으로 정정(벌점만, 치명 칸 안 늘림).

## 6. 지금 저장소 코드(11-03 확인, 고치지 않음)
| 항목 | 지금 | 위치 |
|---|---|---|
| MPPI 크리틱 목록 | `… "PreferForwardCritic", "ClearanceBandCritic"]` — 이름은 목록에 있음 | `ros2_ws/src/rover_navigation/config/nav2_params.yaml` 255 행 |
| ClearanceBandCritic | `{enabled: false, cost_power: 1, cost_weight: 20.0, band: 0.06, trajectory_point_step: 2}` + §30 끔 사유 주석 | 같은 파일 270~276 행, 소스 `src/clearance_band_critic.cpp`(147 행, `enabled_` 검사 41 행), 등록 `mppi_critic_plugins.xml`(`mppi::critics::ClearanceBandCritic`), `CMakeLists.txt` 36~38 행 |
| CostCritic | `cost_weight: 3.81`(저장소는 10-13 내내 3.81), `critical_cost: 300.0` · `consider_footprint: true` | `nav2_params.yaml` 269 행 |
| 전역 inflation | `inflation_radius: 0.70` · `cost_scaling_factor: 2.0` + 10-13 §5 시험 주석 | 같은 파일 713~721 행 |
| footprint_padding | 로컬 · 전역 0.01 | 같은 파일 321 · 556 행 |
| behavior_server | `behavior_plugins: ["spin", "backup", "drive_on_heading", "wait", "monotone_escape"]`, `monotone_escape` 블록(max_travel 0.30 · max_rotation 0.52 · target_clearance 0.05 · 0.03 m/s · 0.15 rad/s · decrease_tolerance 0.003 · 풋프린트 0.272 / −0.258 / 0.175 · `local_costmap/costmap_raw`) | 같은 파일 788 · 796~808 행 |
| BT 복구 | RoundRobin: Clear(로컬 · 전역) → `<BackUp backup_dist="0.30" backup_speed="0.03" time_allowance="20.0" server_name="monotone_escape"/>` → `<Wait wait_duration="5"/>` | `config/nav_to_pose_no_spin.xml` 118~127 행(`default_nav_to_pose_bt_xml` = 이 파일, `nav2_params.yaml` 23 행). 옛 `nav_to_pose_mppi.xml` 37 행은 Nav2 BackUp 0.15 그대로 |
| MonotoneEscape 소스 | 195 행, 커밋 `0fca2dd4` 이후 변경 없음 | `src/monotone_escape_behavior.cpp`, 등록 `behavior_plugins.xml`, `CMakeLists.txt` 31~33 행 |
| ⚠ MonotoneEscape 풋프린트 | 파라미터 기본 · yaml 모두 손으로 적은 0.272 / −0.258 / 0.175(= 풋프린트 0.262 / −0.248 / 0.165 + 패딩 0.01). 코스트맵 풋프린트 · 패딩을 바꿔도 따라가지 않음(ClearanceBandCritic 은 `getRobotFootprint()` 로 따라감) | `monotone_escape_behavior.cpp` 58~60 행, `nav2_params.yaml` 804~806 행 |
| nvblox 통합 거리 | **2.0**(10-22 §14 ~ §15 사용자 결정 — 이 시기 끝은 1.4) | `config/nvblox_local.yaml` 57 행(이력 주석 49~56 행) |
| nvblox site 거리 | 2.0 + 10-15 §22 ~ §23 시험 주석 | 같은 파일 61~65 행 |
| nvblox 복셀 · 지우기 반경 | `voxel_size: 0.05` · `map_clearing_radius_m: 3.0` | 같은 파일 17 · 42 행 |

## 7. SUMMARY · 정리 페이지 ↔ 원문 어긋남 (이번 확인)
| # | 기록 | 원문 | 판정 |
|---|---|---|---|
| 1 | 10-13 §12.1 f2q1 상자 구역 '체류 58.8 s · 최소 4.3 cm · 5 cm 미만 18.6 s · 구역 안 정지 6.0 s' | `box_pass.txt` 는 f2f1 ~ f2p1 11 주행만, f2q1 행 없음 | **원천 소실**(10-13 정리 페이지에도 같은 표시) |
| 2 | 10-13 §12.1 '실행 중 11.43 · 활성 크리틱 8 개(CostCritic 포함, ObstaclesCritic 없음)' | `prep_f2q1.txt` 47 행은 `Parameter not set`, `chk_costw.sh` 출력 파일 없음 | 원천 소실 — 확인했다는 서술만 |
| 3 | 10-15 §25.1 'f2u2 4.6 → 앞 0.28 / 뒤 0.30 m 에 5.2' | `anal_monotone_escape.txt`: 앞 0.28 m **5.2** · 뒤 0.30 m **5.1** | 뒤 값이 0.1 cm 다름(판정 영향 없음) |
| 4 | 10-15 §29.2 · §29.6 놓침 167 · 428 · 16 회, 크리틱 중앙 7.8 · 최대 162 ms | 주행 전체 nav2.log 는 Jetson `/tmp`. 저장된 것은 `missed_sec_f2w2.txt`(17:36:00 ~ 17:37:20) — 놓침 합 232 회 / 62 칸, 크리틱 최대 141.82 ms | 전체 수치는 **원천 소실**(정리 페이지 표시와 같음). 저장 창 안의 값은 SUMMARY 와 모순 없음 |
| 5 | 10-15 §27.1 · §27.5 탈출 로그 인용 | `chk_esc_log.sh` 출력 파일 없음, bag `/tmp/bag_esc3` 저장 안 됨 | 원천 소실 |
| 6 | 10-15 §26 적재 확인(`Creating/Configuring/Activating monotone_escape` · 액션 서버 · target_clearance 0.05) | `chk_escape_loaded.sh` 출력 파일 없음 | 원천 소실 |
| 7 | 10-15 §13 site 기본값(라이브러리 1.0 · 예제 2.0) | `chk_nvblox_site.sh` 출력 파일 없음 | 원천 소실(값은 컨테이너 헤더 · 예제에서 다시 볼 수 있음) |
| 8 | 10-15 주행 bag(f2v1 ~ f2v4 · f2w1 · f2w2) | 날짜 폴더에 `bags/` 없음 | 이 카드의 10-15 분석 출력은 남았으나 입력 bag 위치는 미확인 |
| 9 | 10-14 §1 '경로 없음 D 0.35 10/71 · D 0.40 23/71' | `keepout_all.txt`: f2o1 2 + f2p1 5 + f2n1 3 = 10, 9 + 7 + 7 = 23 | 맞음 |
| 10 | 10-13 §9.1 표 | `sim_sweep_summary.txt` 12 줄 | 맞음 |

## 8. 남은 것 (10-15 시점) · 이후
- **MonotoneEscape 실제 효과 미검증** — 이 시기 실제 교착에서 한 번도 불리지 않았다. 순회 중 자연 발생을 기다려 nav2.log `[monotone_escape]` 줄로 판정(§27.2 (나)). 남은 위험: 빠져나온 뒤 Nav2 가 같은 자리로 다시 들어감(반복 제한 없음, §25.1 한계) · 목표 5 cm 가 뒤집힘 상한 4.4 cm 에 바짝 붙음 · 풋프린트 손 입력(§6 ⚠).
- **ClearanceBandCritic 계산 부담** — 다음 판 후보는 주기마다 1 cm 거리장(EDT)을 만들고 점마다 차체 둘레 표본만 조회(§29.6). '크리틱 덕에 통과' 는 f2w2 1 회 비교.
- **과장의 근본(주행 중 옆면 +5~10 cm)** 원인 미확정 — 정지 관측(정면 · 옆면)은 0~3 cm 라 '움직이며 · 비스듬히 · 멀리서' 쪽으로 좁혀졌을 뿐. 깊이 영상이 든 bag 이 없어 nvblox 설정(통합 거리 · 복셀)을 같은 입력으로 A/B 못 함(§30.1 다음).
- 경로 근접(0.22~0.29 m) · 서쪽 통로 지도 단면은 그대로. 서쪽 통로 목표 방향 고정은 [F2 기준선 카드](f2-baseline-no5.md) · [CopyPath 카드](bt-copypath-end-yaw.md) 쪽.
- 10-14 §25 '출발점 상자 자리는 지금 바꾸지 않는다' 결정 뒤 10-15 에 그 자리에서 f2v4 가 같은 기전으로 Nav2 중단(서쪽 통로 f2v1 · f2v3 도 같은 기전) — 결정 근거('어느 정도 된다')와 10-15 결과의 관계는 기록에 정리되지 않았다.
- **이후(10-19 ~): 다음 시기에서 채움** — 알려진 포인터만: 10-19 §0 크리틱 '보류(코드 유지 · 꺼 둠)' 판단 · 깊이 bag 기록 준비(커밋 `aff3a47b` '과장은 nvblox 조각에서 이미 +5~10 cm') · 10-21 §12.2 C 행 MonotoneEscape '최근접 4.6 cm' → 앞 0.28 m 탈출 기록 · 10-22 §14 ~ §15 통합 거리 1.4 → 2.0(깊이 프리셋 3 과 함께) · 10-23 PathBlockedAhead `only_new`(커밋 `0a6e5f73`).

## 9. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2p1 | 전역 감쇠 3.0 주행(b910) | 10-13 §5.6, `prep_f2p1.txt` · `run_f2p1.txt` · `f2p1_box_history.txt`, bag `2026-10-13/bags/bag_f2p1.tgz`(로컬) |
| sweep | cost_weight 시뮬 150 회 | 10-13 §9 · §9.1, `sim_sweep_summary.txt` |
| pad0 | 패딩 0 시뮬 40 회 | 10-13 §11 · §11.1, `sim_pad0_summary.txt` |
| f2q1 | cost_weight 11.43 주행(b910) | 10-13 §12 · §12.1, `prep_f2q1.txt` · `run_f2q1.txt` · `f2q1.csv`, bag `2026-10-13/bags/bag_f2q1.tgz`(로컬) |
| keepout | 전역 카메라 금지 띠 재계획(f2o1 · f2p1 · f2n1) | 10-14 §1, `keepout_all.txt` |
| 목표 이동 · 지도 수정 | 서쪽 통로 재계획 | 10-15 §9.1 · §11, `anal_path_center.txt` · `anal_mapfix_replan.txt` |
| 후보 3 | 깜빡임 거르기 | 10-15 §12, `anal_flicker_westbox_f2v1.txt` · `anal_cell_ratio_odom_f2v1.txt` · `anal_lidar_strip_f2v1.txt` · `anal_grid_phase_f2v1.txt` |
| site A/B · P1/P2 | 정지 관측 | 10-15 §22 ~ §24, `box_face_A.txt` · `box_face_B.txt` · `outputs/boxdump/*.npz` · `figures/box_site_AB.png` |
| escape | MonotoneEscape 오프라인 · 실제 시험 2 회 | 10-15 §25 ~ §27.5, `anal_monotone_escape.txt`, bag `/tmp/bag_esc3`(원천 소실) |
| f2w1 · f2w2 | ClearanceBandCritic 주행(b910 · no5) | 10-15 §29.2 · §29.6, `run_f2w1.txt` · `run_f2w2.txt` · `anal_band_run_b910.txt` · `anal_band_run_no5.txt` · `missed_sec_f2w2.txt` · `anal_box_true_vs_map.txt` |
| intdist | 통합 거리 1.0 bag 근사 | 10-15 §30.1, `anal_intdist_proxy.txt` · `anal_intdist_slice.txt` |
| 도구(10-13) | `anal_f2o1_options.py` · `prep_deploy_ginfl.sh` · `up_ginfl_only.sh` · `run_sim_sweep.sh` · `anal_sweep_summary.py` · `run_sim_pad0.sh` · `anal_pad0_summary.py` · `prep_deploy_costw.sh` · `chk_costw.sh` · `up_costw_only.sh` · `up_nvblox_integ.sh` · `Docs/tools/anal_box_pass.py` · `Docs/tools/anal_mppi_sim.py` | §10.1 ~ §10.4 |
| 도구(10-14) | `Docs/tools/anal_plan_keepout.py` | §10.5 |
| 도구(10-15) | `anal_path_center.py` · `anal_map_vs_lidar.py` · `anal_mapfix_replan.py` · `anal_cam_vs_lidar.py` · `anal_flicker_filter.py` · `anal_grid_phase.py` · `anal_lidar_strip.py` · `anal_cell_ratio_odom.py` · `chk_nvblox_site.sh` · `up_nvyaml.sh` · `up_nvyaml_restore.sh` · `chk_box_face.py` · `chk_box_dump.py` · `fig_box_dump.py` · `anal_memory_shift.py` · `anal_monotone_escape.py` · `up_escape.sh` · `up_escape2.sh` · `up_escape_xml.sh` · `chk_escape_loaded.sh` · `run_escape_test.py` · `chk_scan_near.py` · `chk_esc_log.sh` · `up_band_critic.sh` · `anal_band_run.py` · `chk_missed_hist.sh` · `chk_logkeep_missed.sh` · `chk_band_time.sh` · `chk_esc_context.sh` · `chk_missed_sec.sh` · `anal_box_true_vs_map.py` · `up_cfg_intdist.sh` · `anal_intdist_proxy.py` · `anal_intdist_slice.py` | §10.6 ~ §10.13 |
| 기전 쪽 도구 | `anal_box_history.py` · `anal_box_layers.py` · `anal_motion_probe.py` · `anal_near_cells_src.py` · `anal_cell_first_seen.py` · `anal_stall_entry.py` | [기전 카드](box-side-stall-cause.md) |

## 10. 도구 해설
공통: 10-13 · 10-15 의 Jetson 도구는 `/tmp` 에 올려 `run_jn.sh` 로 부르고(출력은 `| tee` 로 `outputs/`), PC 분석 도구는 날짜 폴더 `jobs/` 판이 그날 커밋 그대로다(이 카드의 도구 중 뒤에 바뀐 판 없음 — `git log` 확인, `run_escape_test.py` · `chk_box_dump.py` 는 같은 날 여러 커밋). 로컬 코스트맵 · nvblox 조각은 odom, 전역은 map — 지도 좌표로 비교하는 도구는 그 시각 map→odom 을 곱한다(그 함정은 실수 ⑦). 'fp' = Nav2 FootprintCollisionChecker 흉내(꼭짓점 칸 내림 + 변 Bresenham, 최대 비용), '정확 여유' = 차체 직사각형 ↔ 치명 칸 중심 기하 거리.

### 10.1 `anal_f2o1_options.py` — 대책 1 · 4 사전 평가 (10-13 §5.2 · §5.4, PC)
- **형태**: PC `python anal_f2o1_options.py`(f2o1 bag 고정).
- **왜**: '전역 경로가 상자 끝에 가깝다' 를 스무더 · inflation 값 · 탈출 동작 중 어디서 푸나.
- **하는 일**: A — `/plan` 과 바로 뒤 `/plan_smoothed` 의 상자 끝 최소 거리. B — 13:33:06 전역 코스트맵의 치명 칸에서 거리장 → `252·exp(−k(d − 내접))` 로 inflation 재계산(반경 r · 감쇠 k · 패딩 12 조합), 8 방향 다익스트라(칸 비용 50 + 0.8 × 비용, ≥ 253 통과 불가). 현재 값 재현 0.260 m 대 기록 0.271 m 로 흉내 검증. C — 정지 자세에서 직후진 · 직전진 · 회전 자세의 풋프린트 둘레 최대 비용(1 cm 표본).
- **출력**: [`f2o1_options.txt`](../debug_log/2026-10-13/outputs/f2o1_options.txt)(실수 ① 발췌). **쓰인 곳**: 대책 #1 값 3.0, #2 '안 함'.
- **결함 · 지금**: NavFn 퍼텐셜이 아닌 다익스트라(한 칸 오차). 같은 흉내가 10-14 `anal_plan_keepout.py` · 10-15 `anal_path_center.py` · `anal_mapfix_replan.py` 로 이어짐.

### 10.2 배포 · 되돌림 셸(10-13) — `prep_deploy_ginfl.sh` · `up_ginfl_only.sh` · `prep_deploy_costw.sh` · `chk_costw.sh` · `up_costw_only.sh` · `up_nvblox_integ.sh`
| 도구 | 하는 일(코드 기준) | 출력 |
|---|---|---|
| `prep_deploy_ginfl.sh [값]` | `find ~/ros2_ws/src ~/ros2_ws/install -name nav2_params.yaml` 중 링크 아닌 것에 정규식 치환(§4.1) → `prep_patrol.sh lite 15.0` → `ros2 param get` 로 실행 중 감쇠 · 반경 | [`prep_f2p1.txt`](../debug_log/2026-10-13/outputs/prep_f2p1.txt) |
| `up_ginfl_only.sh 2.0` | yaml 만, 재기동 없음 | 원천 소실(SUMMARY §6.1) |
| `prep_deploy_costw.sh 11.43` | `CostCritic: {enabled: true, cost_power: 1, cost_weight: ` 뒤 숫자 치환 + prep + 실행 중 확인(이름 틀림, 실수 ④) | [`prep_f2q1.txt`](../debug_log/2026-10-13/outputs/prep_f2q1.txt) |
| `chk_costw.sh` | `ros2 param list /controller_server` 에서 이름을 찾아 get | 원천 소실 |
| `up_costw_only.sh 3.81` | yaml 2 곳 + `ros2 param set … FollowPathMPPI.CostCritic.cost_weight` | 원천 소실(SUMMARY §12.1 '확인됨') |
| `up_nvblox_integ.sh 값` | `sed -i -E` 로 통합 거리, 링크는 건너뜀, nvblox 로그의 실행 중 값 출력 | 원천 소실 |
- **결함**: `prep_deploy_*` 는 링크 판정 뒤 '이미 같은 값' 만 알려 줘 설치본이 일반 파일이 된 경우(10-15 §30 발견)를 따로 알리지 않는다.

### 10.3 `Docs/tools/anal_mppi_sim.py` · `run_sim_sweep.sh` · `anal_sweep_summary.py` — cost_weight · 패딩 시뮬 (10-13 §9 · §11, Jetson)
- **형태**: Jetson `python3 /tmp/anal_mppi_sim.py /tmp/bag 0 label=… t_abs=<epoch> cycles=<N> seed=<s> cost_w=<w> …` — `run_sim_sweep.sh` 가 공통 인자 `… humble=1 temperature=0.15 … obst=1 vx_min=-0.06 fwd_w=15 fpchk=1` 로 150 개를 `xargs -P 3`.
- **하는 일**: 기록된 경로 · 로컬 코스트맵을 시간대로 재생(`dyn_path=2 dyn_cost=1`)하며 MPPI(Humble 1.1.20 동작)를 돌림. CostCritic 흉내는 `obst = obst + np.where(traj_coll, P['cc_coll'], P['cost_w'] / 254.0 * per.sum(axis=1) / T)`(235 행). `fpchk=1` = Nav2 칸 단위 둘레 검사(10-13 §8 추가), `pad` = 패딩(§11 추가). 요약: 'LETHAL 여유' 최소, 실패 주기 ≥ 10 이면 '멈춘 씨앗', 전진 거리.
- **출력**: [`sim_sweep_summary.txt`](../debug_log/2026-10-13/outputs/sim_sweep_summary.txt)(첫 줄 `box_f2o1      3.81      7.2 ·   2.8 · …   1 / 10 (씨앗 3)   1.90`) · [`sim_pad0_summary.txt`](../debug_log/2026-10-13/outputs/sim_pad0_summary.txt). PC 연결이 끊겨 Jetson 결과를 `anal_sweep_summary.py` · `anal_pad0_summary.py` 로 다시 집계.
- **알려진 결함**: 이 자리에서 실제보다 약 5 cm 넉넉(§10 측정) — 절대값 금지, 설정 간 차이만. 씨앗 사이 흔들림 ±3 cm 가 설정 효과와 같은 크기. 패딩 0 은 inflation 을 0.01 기준 그대로 둔 채 충돌 판정만 바꿈.
- **계보**: [오프라인 MPPI 시뮬레이터 카드](mppi-offline-simulator.md)(job355 → … → job776 → 이 이름).

### 10.4 `Docs/tools/anal_box_pass.py` — 같은 구역을 지날 때 여유 (10-13 §10 · §12.1, PC)
- **하는 일**: 로버 중심이 구역(map x 0.6~2.2, y −0.5~0.8)에 있고 복귀(서쪽) 방향일 때만 로컬 코스트맵마다 차체 외곽 ↔ 1 m 안 치명 칸 가장자리 거리. 주행마다 체류 · 최소 · 5 cm 미만 시간 · 2 s 넘는 정지.
- **출력**: [`box_pass.txt`](../debug_log/2026-10-13/outputs/box_pass.txt)(11 주행). f2q1 줄은 원천 소실(§7 #1).
- **지금**: 상시 도구, 커밋 `4a205e20` 이후 변경 없음. 10-15 의 `anal_band_run.py` 는 칸 중심 정확 거리 + fp 판정이라 값의 정의가 다르다(칸 가장자리 vs 칸 중심 — 약 2.5 cm 차).

### 10.5 `Docs/tools/anal_plan_keepout.py` — 전역 카메라 금지 띠 (10-14 §1, PC)
- **형태**: `anal_plan_keepout.py bag [--step 8] [--box HH:MM:SS] [--at HH:MM:SS …]`.
- **하는 일**: 8 s 마다 전역 코스트맵 치명 칸 중 nvblox 슬라이스가 장애물이라 한 자리(±1 칸)를 '카메라 칸' 으로 가르고, inflation 재계산(0.70 · 2.0 · 내접 0.175) 뒤 카메라 칸에서 D 안을 253 으로:
  ```python
  if cam.any() and D > RINS: c[(ndimage.distance_transform_edt(~cam) * res <= D) & (c < 253)] = 253.0
  ```
  (57 행) 로버 → 그때 `/plan` 끝점 다익스트라. D = 0.175 · 0.25 · 0.30 · 0.35 · 0.40.
- **출력**: [`keepout_all.txt`](../debug_log/2026-10-14/outputs/keepout_all.txt) — `0.350 m                  2 / 24               4                       +0.00 · +0.17 m                    13:33:11(통로 막힘) 13:33:19(통로 막힘)`.
- **결함**: 선언 없는 탐색. 실제 구현(전역 nvblox 층 비이진 + `inflation_distance`)과 같은지 · '비용만 올리는' 변형은 안 봄.

### 10.6 서쪽 통로 재계획 · 지도 대조 — `anal_path_center.py` · `anal_map_vs_lidar.py` · `anal_mapfix_replan.py` (10-15 §9.1 · §10 · §11, PC)
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `anal_path_center.py` | 10:15:45 전역 코스트맵(원가 역변환) — 치명 유지, inflation 재계산(반경 0.70 · 감쇠 바꿔 가며), 출발 (x0, −3.70) → (−1.60, −5.50) 다익스트라. y −3.90~−4.40 의 경로 x 와 차체(반폭 0.175) ↔ 상자 앞면 x −1.43 · 서쪽 벽 −2.23 여유 | [`anal_path_center.txt`](../debug_log/2026-10-15/outputs/anal_path_center.txt) |
| `anal_map_vs_lidar.py` | 그 순간 라이다 점을 지도로 옮겨 y 띠마다 저장 지도 점유 경계와 차(중앙값), 세 순간 | [`anal_map_vs_lidar.txt`](../debug_log/2026-10-15/outputs/anal_map_vs_lidar.txt) |
| `anal_mapfix_replan.py` | 저장 지도에만 있는 서쪽 두께 36 칸을 비운 판 vs 그대로, 같은 재계획 | [`anal_mapfix_replan.txt`](../debug_log/2026-10-15/outputs/anal_mapfix_replan.txt) |
- **결함**: NavFn(퍼텐셜 + 기울기 따라가기)과 같지 않다(경향만) — 둘 다 '경로가 안 움직인다' 의 근거가 이 흉내.

### 10.7 카메라 칸 걸러내기 검증 — `anal_cam_vs_lidar.py` · `anal_flicker_filter.py` · `anal_grid_phase.py` · `anal_lidar_strip.py` · `anal_cell_ratio_odom.py` (10-15 §9.2 · §12, PC)
- **`anal_flicker_filter.py bag 시작 기준 구역 [M=8]`**: `/nvblox_node/static_map_slice` 프레임마다 odom 0.05 격자 칸이 '시야 안'(카메라 \|방위\| ≤ 43° · 0.15~1.4 m · 미지 아님 · 카메라→칸 선 위 가림 없음)이면 시야 +1, 그때 거리 ≤ 0 이면 점유 +1. 라이다 확인 칸(3.5 cm 안 점 한 번이라도) 제외, 깜빡임 = 시야 ≥ M 이고 비율 < θ(0.8 · 0.9). 출력 [`anal_flicker_westbox_f2v1.txt`](../debug_log/2026-10-15/outputs/anal_flicker_westbox_f2v1.txt). ⚠ 이 판의 '라이다 확인' 은 멀리서 비스듬한 몇 점 때문에 넓게 잡혔다(§12 중간 발견).
- **`anal_cell_ratio_odom.py`**: 칸을 odom 칸 번호로 고정해 시야 안(\|방위\| ≤ 43° · ≤ 1.4 m, 가림 안 봄) 프레임마다 코스트맵 치명 · 조각 점유를 셈 — §12 판정의 근거(실수 ⑦ 발췌).
- **`anal_grid_phase.py`** · **`anal_lidar_strip.py`**: 조각 · 코스트맵 odom 원점 위상차(0) · 바깥 줄 근처 라이다 점의 시각 · 위치. 출력 `anal_grid_phase_f2v1.txt` · `anal_lidar_strip_f2v1.txt`.
- **`anal_cam_vs_lidar.py`**: §9.2 표(실수 ⑥).

### 10.8 nvblox site 정지 A/B — `chk_nvblox_site.sh` · `up_nvyaml.sh` · `up_nvyaml_restore.sh` · `chk_box_face.py` · `chk_box_dump.py` · `fig_box_dump.py` (10-15 §13 · §22 ~ §24, Jetson · PC)
- **`chk_box_face.py [초=20] [라벨]`**(Jetson, 로버 안 움직임): `/local_costmap/costmap` 치명(≥ 100) 칸을 map→odom 으로 지도로, 구역 x 0.6~1.6 · y −0.30~0.25 에서 행(5 cm)마다 가장 서쪽 칸의 서쪽 가장자리 x, 프레임마다 전체 최소 · 칸 수. 출력 `box_face_A.txt` · `box_face_B.txt`(앞 판에 yaml 링크 · md5 · nvblox 로그 확인 줄 포함).
- **`chk_box_dump.py 라벨 [초=12] [기준 프레임=map]`**: 점군(`/camera/camera/depth/color/points`) · 조각 · 로컬 코스트맵을 tf2 로 같은 좌표에 npz(`outputs/boxdump/`). §24 에서 `base_link` 기준 추가(손으로 옮겨 지도 위치가 틀어져도 몸체 기하 유지). `fig_box_dump.py` 가 [`box_site_AB.png`](../debug_log/2026-10-15/figures/box_site_AB.png).
- **배포**: `up_nvyaml.sh`(src 백업 `nvblox_local.yaml.bak_<시각>` 뒤 교체, 설치본은 링크) · `up_nvyaml_restore.sh`(가장 최근 백업으로). `chk_nvblox_site.sh` 는 컨테이너 안 헤더 · 예제 grep(출력 원천 소실).
- **결함**: 실제 면 기준이 '차체 앞끝 = base + 0.262' 가정 · 테이프 배치 오차를 안고 있어 2~3 cm 를 깊이 · 장착 · 기준점 중 무엇으로 가르지 못함(§23).

### 10.9 `anal_monotone_escape.py` — 탈출 오프라인 (10-15 §25, PC) ★ MonotoneEscape 를 낸 도구
- **형태**: `python anal_monotone_escape.py 이름=bag@HH:MM:SS.f …`(실패 5 건).
- **하는 일**: 그 순간 로컬 코스트맵 치명 칸 중심을 고정 장애물로, 차체(`XF, XR, HW = 0.272, -0.258, 0.175` · 15 행)를 지금 방향 그대로 1 cm 씩 ±0.30 m. 걸음마다 최근접(차체 다각형 → 칸 중심, 안이면 0). '줄지 않음' 허용 `TOL = 0.0002`, 목표 `TARGET = 0.05`.
- **출력**: [`anal_monotone_escape.txt`](../debug_log/2026-10-15/outputs/anal_monotone_escape.txt) — `f2v3(통로 입구)             2.7 cm(앞왼)   0.01 m 에서 거리 줄어 멈춤(2.7 → 2.1 cm, 앞왼)           ★ 0.03 m 에서 최근접 5.2 cm 도달(줄지 않음)` · `빠져나갈 방향이 있는 사례 5 / 5`.
- **결함**: 칸 고정(움직이며 새로 찍히는 칸 없음) · 회전은 안 봄(플러그인에는 회전 포함, 근거는 §18.1 탐색 한 건) · 빠져나온 뒤 재진입 미평가.

### 10.10 MonotoneEscape 플러그인 · 배포 · 실제 시험 — `monotone_escape_behavior.cpp` · `up_escape*.sh` · `chk_escape_loaded.sh` · `run_escape_test.py` · `chk_scan_near.py` · `chk_esc_log.sh` · `chk_esc_context.sh` (10-15 §26 ~ §27.5 · §29.6)
- **플러그인**: §4.5. 회전 걸음 0.0175 rad(1°), 실행 중 감소 허용 0.003 m, 시간 한도는 BT 의 `time_allowance` 20 s 만 씀(`backup_dist/speed` 무시).
- **배포**: `up_escape.sh`(`/tmp/esc.tar` 를 src 에 풀고 바뀌는 원본은 날짜 백업, colcon) → `up_escape2.sh`(package.xml) → `up_escape_xml.sh`(`name` 속성). `chk_escape_loaded.sh` 는 nav2.log 에서 `monotone_escape\|MonotoneEscape\|Failed to create\|PluginlibFactory\|error` grep(출력 원천 소실).
- **`run_escape_test.py <단계>`**(Jetson, **로버가 움직임** — goto · creep · turn · navturn · escape · backup): `gap` = 점군(높이 0.06~0.30)으로 상자 옆면 · 앞면과 예상 간격, `creep` = Nav2 없이 0.05 m/s 직진(라이다 점이 패딩 없는 차체에서 4 cm 안이면 정지 — §27.1 에 앞 절반 점만으로), `navturn gx gy gyaw trig stop max` = Nav2 목표를 보내고 출발 0.5 m 뒤 치명 칸이 차체 옆(몸체 x −0.20~+0.25, \|y\| ≥ 0.17)에 와 여유 ≤ trig 면 취소 · 그 칸 쪽으로 0.08 rad/s 회전(157 행 조건). 출력은 사람이 읽는 줄 — **파일로 남지 않음**(SUMMARY §27 인용만).
- **`chk_esc_log.sh` · `chk_esc_context.sh`**: nav2.log 의 탈출 · 복구 · 실패 줄 / 첫 `Running monotone_escape` 앞뒤 문맥(출력 원천 소실).

### 10.11 ClearanceBandCritic · 측정 — `clearance_band_critic.cpp` · `up_band_critic.sh` · `anal_band_run.py` · `chk_missed_hist.sh` · `chk_logkeep_missed.sh` · `chk_band_time.sh` · `chk_missed_sec.sh` (10-15 §29 ~ §29.6 · §32)
- **크리틱**: §4.6.
- **`anal_band_run.py 이름=bag …`**(PC): 로컬 코스트맵 프레임마다 정확 여유와 fp(`fp_cost` 29 행 — 꼭짓점 `floor` + `bresenham`), 구간 `bins = [(0, 0.027), (0.027, 0.044), (0.044, 0.06), (0.06, 99)]`(69 행). 출력 [`anal_band_run_b910.txt`](../debug_log/2026-10-15/outputs/anal_band_run_b910.txt) — `최소 정확 여유 4.8 cm · 17:12:50.8 …` · `여유 구간 프레임: < 2.7 cm 0 · 2.7~4.4 0 · 4.4~6 14 · ≥ 6 343` · `fp 100(서 있는 자세 닿음) 프레임 0`, [`anal_band_run_no5.txt`](../debug_log/2026-10-15/outputs/anal_band_run_no5.txt).
- **놓침 · 시간 셸**(Jetson, nav2.log grep): `chk_missed_hist.sh`(10 s 분포) · `chk_logkeep_missed.sh`(`/tmp/logkeep/*_nav2.log` 마다 `Control loop missed` 수) · `chk_band_time.sh`(크리틱 시간 줄의 평균 중앙값 · 최대) — 셋 다 출력 원천 소실. `chk_missed_sec.sh`(17:36:00~17:37:20 초별 놓침 + 사건)만 [`missed_sec_f2w2.txt`](../debug_log/2026-10-15/outputs/missed_sec_f2w2.txt) 로 남음(커밋 `5e8a3bb1` 판).
- **결함**: 놓침이 크리틱 탓이라는 것은 시각 일치 + 시간 기록(추정 아닌 측정은 f2w2 의 시간 줄), 크리틱 없는 같은 날 스택(16 회)은 목표 2 개짜리라 길이가 다름.

### 10.12 `anal_box_true_vs_map.py` — 기록 상자 vs 찍힌 상자 (10-15 §29.4, PC)
- **하는 일**: 기록 상자(x 1.151~1.261, y −0.20~−0.02, 출발 자세 = 원점)와 로컬 코스트맵 치명 칸(지도 좌표)의 북 · 남 · 서 · 동 면, 실제 여유(차체 ↔ 기록 상자 직사각형) · 지도 여유(차체 ↔ 칸 중심). 로버가 상자 옆(x 0.9~1.7, \|y\| < 0.6)인 프레임만.
- **출력**: [`anal_box_true_vs_map.txt`](../debug_log/2026-10-15/outputs/anal_box_true_vs_map.txt) — `요약: 실제 여유(패딩 포함) 최소 9.5 cm · 지도 여유 최소 4.8 cm · 같은 프레임 (실제 − 지도) 중앙 3.4 cm(범위 -2.7~8.0) · 북쪽 면 중앙 +0.062(실제보다 +8.2 cm 로버 쪽)`.
- **결함**: 테이프 배치 오차 1~2 cm · 1° 가 그대로 섞임(머리 주석 ⚠).

### 10.13 통합 거리 1.0 근사 — `up_cfg_intdist.sh` · `anal_intdist_proxy.py` · `anal_intdist_slice.py` (10-15 §30 · §30.1)
- **`up_cfg_intdist.sh`**(Jetson): `/tmp` 의 두 yaml 을 src 로(백업 `.bak_<시각>`), 설치본 값 확인, 설치본 nav2_params 가 링크가 아니면 다시 링크(§4.7).
- **`anal_intdist_slice.py 이름=bag …`**(PC): 조각에서 상자 구역 칸이 표면(거리 ≤ 0)이 되는 순간의 카메라 거리 · 방위. 상자 칸 = 기록 상자 안 또는 2.5 cm 안, 과장 = 그 밖(`BOX = (1.151, 1.261, -0.20, -0.02); REG = (1.0, 1.45, -0.25, 0.20)` 13 행). 통합으로 생길 수 있는 것만 `F = (B <= 45) & (D <= 1.45)`(56 행). 출력 [`anal_intdist_slice.txt`](../debug_log/2026-10-15/outputs/anal_intdist_slice.txt) — f2v4 `과장(상자 밖 7.5 cm 넘음) … 시야 안 · 1.45 m 안 생성 12: ≤ 1.0 m 1 (8 %)`.
- **`anal_intdist_proxy.py`**: 로컬 코스트맵 판 — 무효(작은 실수).
- **결함**: 깊이 영상 없는 bag 이라 '1.0 이면 나중에 가까이서 찍히는가' 는 알 수 없음. 칸 키 2.5 cm 반올림 · map→odom 보정 · ESDF 재계산이 '생성' 에 섞임.

## 11. 용어
- **칸 판정 경계 띠(2.7~4.4 cm)**: 차체 ↔ 치명 칸 중심 정확 거리가 이 구간이면 Nav2 의 칸 단위 풋프린트 검사(꼭짓점 칸 내림 + Bresenham)가 칸 위상에 따라 '닿음(100)' / '안 닿음(99)' 으로 갈린다(10-15 §28 측정 3 건 + 09-23 4.4 cm). 서 있는 자세가 100 이 되면 MPPI 후보 · BackUp 이 첫 점부터 버려진다.
- **이중 여유**: 의도 안 한 카메라 과장(주행 중 +5~10 cm) 위에 의도한 띠(ClearanceBandCritic 6 cm)가 더해져 넓은 곳에선 실제 10~15 cm 로 지나는 상태(10-15 §29.5).
- **MonotoneEscape**: '모든 치명 칸까지 정확 거리가 한 걸음도 줄지 않는' 직진 · 제자리 회전만으로 여유 5 cm 까지 천천히 빠져나오는 behavior_server 플러그인. 지도가 맞든 틀리든 지금보다 어떤 물체에도 가까워지지 않는 것이 설계 원칙.
- **ClearanceBandCritic**: 궤적 점마다 차체 ↔ 치명 칸 정확 거리 d < band(0.06 m)면 (band − d)/band 를 벌점으로 더하는 MPPI 크리틱. 치명 칸을 막지 않고 벌점만 준다.
- **site 거리(`esdf_integrator_max_site_distance_vox`)**: nvblox ESDF 가 표면에서 이 복셀 수 안의 칸을 '표면(site)' 으로 보는 거리(라이브러리 기본 1.0, 우리 2.0).
- **통합 거리(`projective_integrator_max_integration_distance_m`)**: 깊이를 TSDF 에 넣는 최대 거리. 짧으면 멀리 유령이 줄고 물체를 늦게 본다.
- **금지 띠(keepout) D**: 전역 지도에서 카메라 칸 둘레 D 안을 계획기 통과 불가(253)로 덧씌우는 가정(10-14 §1 오프라인).
- **'후보 전부 충돌'**: MPPI 로그 "Optimizer fail to compute path" — 표본 궤적이 모두 충돌 판정.
