# 낮은 상자 기억 — 전역 코스트맵 카메라 층(obstacle → STVL 시험 → nvblox) · 주기 재계획

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **우회(10-08 시점)** — 계획기가 라이다 아래 낮은 상자를 '잊는' 원인을 전역 obstacle 층의 한 격자(라이다 2D 소거)로 좁혔고(설정 근거 + bag 정황, 소거 순간은 직접 못 봄), STVL 전역 층은 갱신(C2) 불합격으로 기각, **전역 nvblox 층(map 프레임) + 주기 재계획 0.5 Hz(B 구성)** 으로 f2e2 3/3 · 상자 미접촉 1 회. 기본값 전환은 그날 미결정(→ 이후 prep 기본으로, 10-12). 남은 것: 근접 정면 상자의 로컬 치명 → 내접 강등(f2e1), 상자 옆 여유 | 10-07 §2.6 · §7.1 ~ §7.2 · §8 ~ §8.5 · §10 ~ §10.1 · §16, 10-08 §1 ~ §3.8 · §7 (이 카드), 10-12 §1, 10-13 §4.6 · §5.1 · §6.2 · §13 · §14.1, 10-14 §1 · §6 · §24 · §25, 10-15 §18.3 (7 기 이어 채움 — 상자 옆 정지 쪽은 [기전 카드](box-side-stall-cause.md)), 이후 10-19 ~ | [10-07 §2.6](../debug_log/2026-10-07/SUMMARY.md)(사용자: "상자를 피해 경로를 세워 이동하다가 상자 쪽으로 다시 몸을 틀어…" · 주행 뒤 "상자를 밀면서 왔다") | `ros2_ws/src/rover_navigation/launch/navigation.launch.py`(`global_camera:=obstacle\|stvl\|nvblox` · `replan_hz` — 커밋 `de2a9a8e` · `b6e93383`(10-07) · `453813f1` · `eb27aba4`(10-08)) · prep `jobs/job922_prep.sh`(10-07) · `jobs/job934_prep.sh`(10-08) · 러너 래퍼 `2026-10-08/jobs/run_f2c.sh`(`b910`) | [Phase N 후반 · 유령 셀](nvblox-n6-global-ghosts.md)(09-22 전역 nvblox 첫 도입 — 같은 프레임 미지정) · [카메라 깊이 장애물](depth-obstacle-costmap.md)(STVL 절두체 · 근평면 이력) · [nvblox 층 round → floor](nvblox-layer-round-floor.md)(같은 층 · 프레임 변환 결함 10-27) · [전역 계획기 NavFn vs Smac](global-planner-choice.md) · [F2 순회 위치 점프](f2-patrol-loc-jump.md)(10-01 §8.24 전역 nvblox 제거 · §8.35 전역 카메라 점군 층) · [inflation · padding 역할](inflation-padding-roles.md) · [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md)(critical_cost) · [저장소 공개 운영](repo-public-ops.md) (6 기) · [빠른 prep](prep-fast-startup.md) · [BT 끝 방향 CopyPath](bt-copypath-end-yaw.md) (7 기) · [유령 칸 · 깊이 프리셋](ghost-cells-depth-preset.md) · [복귀 상자 칸](box-return-cells.md) · [경로 추종 · B0](path-tracking-replan-b0.md) (8 기) · [nvblox 층 TF 조회 실패 처리](nvblox-layer-tf-drop.md)(이 카드의 10-08 map 프레임 지정이 그 결함의 조건) · [PathBlockedAhead 99/100](pathblocked-only-new.md) (9 기) |

**한 줄**: 출발 방 통로의 **라이다(높이 0.185 m)보다 낮은 상자 ②** 를 로컬(nvblox)은 보는데 전역(계획기)은 거의 못 봐서, f2c2 는 상자를 밀고 지나갔고 f2d2 는 상자 앞에서 45 s 무진행 취소됐다(10-07 §2.6 · §7.1). 원인은 두 겹 — ① 전역 obstacle 층이 라이다와 카메라 점군을 **한 2D 격자**에 두어 라이다 소거가 카메라 표시를 지우는 것으로 **추정**(설정 + bag 에서 전역 상자 칸 거의 0), ② BT 가 목표당 1 회만 계획(재계획 0.01 Hz)이라 상자가 보인 뒤 33 s 동안 옛 경로 유지(**측정**, 10-07 §10.1). 전역 카메라를 STVL 로 떼면 가까이서 기억(C1)은 됐지만 치운 상자를 1 분 30 s 넘게 못 지워(C2) 기각(10-07 §8.5). 같은 녹화의 nvblox 슬라이스는 치운 칸 대부분을 수 초 안에 지웠고(10-08 §1.1), 순회 bag 재계산에서 카메라만 본 묶음은 사용자 확인으로 대부분 실제 물체였다(§2.2). 그래서 **전역 nvblox + 재계획 0.5 Hz** 를 주행했는데 f2e1 은 **전역 nvblox 층 프레임이 기본값 odom**(내 결함)이라 상자가 ≈ 0.3 m 밀려 찍혀 접촉, 고친 f2e2 는 3/3 · 미접촉(§3.3 ~ §3.8).

---

## 1. 증상
- **f2c2 복귀(10-07 §2.6)**: 사용자 "마지막에 상자를 피해 경로를 세워 이동하다가, 상자 쪽으로 다시 몸을 틀어 출발 위치로 돌아왔다" · 주행 뒤 "**상자를 밀면서 왔다**" → ③-a 접촉 0 불합격. 계산은 상자 묶음까지 최소 7.3 cm 였다([`f2c2_boxgap.txt`](../debug_log/2026-10-07/outputs/f2c2_boxgap.txt)) — 이 묶음은 뒤에 상자 ① 로 밝혀짐(실수 ①).
- **f2d2 목표 10(출발 복귀, 10-07 §7.1)**: 사용자 "작은 박스 앞에서 주행을 하지 못하고 멈췄다". 러너 로그 원문([`j921_f2d2_g10.txt`](../debug_log/2026-10-07/outputs/j921_f2d2_g10.txt)):
  ```
  +376.0 … PathBlockedAhead: 앞 경로 (1.45, 0.02) 비용 99 가 2.0 s 지속 → 주행 중단·재계획
  +383.0 … PathBlockedAhead: 앞 경로 (1.36, -0.30) 비용 99 — 2.0 s 지속되면 재계획
  +410.0 [ERROR] … [controller_server]: Failed to make progress
  +430.0 [ERROR] … nav_guard 개입 — 무진행: 45 s 동안 최대 0.24 m 이동 < 0.25 m → 모든 목표 취소·정지
  ```
- **사용자 확인(10-07 §7.1)**: "출발 위치 앞, 그 위치에 상자 하나가 원래 있었다 — 라이다에 안 잡히는 높이라 카메라만 볼 수 있다." 현장 상자 둘: ① 통로 남쪽 map (1.3~1.6, −0.3~−0.45) ② 통로 가운데 (1.1~1.3, −0.1~+0.1).
- **f2e1 복귀(10-08 §3.5)**: 사용자 "f2e1 복귀 때 상자에 닿았다. 왜 닿았나" — 전역 nvblox · 재계획을 넣은 첫 주행.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 앞 시기 10-01 §8.24 · §8.35 | 전역에서 nvblox 층 제거(통로 입구 카메라 유령 93 칸) + 재계획 1.0 → 0.01 Hz, 그 뒤 f2a11 에서 전역이 상자를 몰라 경로가 관통 → 전역 obstacle_layer 에 **camera 소스**(점군, 높이 0.06~0.40, 표시 ≤ 1.2 m) | (5 기) | 낮은 물체는 로컬만 본다는 위험을 그때 적어 둠(§8.24) — 10-07 이 그 위험이 실현된 것 | [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md) · [F2 순회 카드](f2-patrol-loc-jump.md) |
| 10-07 §2.6 | f2c2 복귀를 bag 으로(`job912_extract.py` → `f2c2_boxgap.py`, 그림 `render_f2c2_box2.py`) | 로컬 치명 칸 중 라이다 점에서 7.5 cm 넘게 떨어진 묶음 map x 1.3~1.7 · y −0.25~−0.5, +106 s 상자 쪽으로 12° 더 틀며 최소 **7.3 cm** | '상자 쪽으로 다시 틂' = MPPI 가 상자 칸에서 약 10 cm 떨어져 지나는 계획 경로로 복귀(측정). 실제 밀었으니 '카메라 칸이 앞면을 늦게 · 덜 표시' (추정) — ❌ 민 것은 이 묶음(상자 ①)이 아니라 상자 ②(§7.1, 실수 ①) | [`f2c2_boxgap.txt`](../debug_log/2026-10-07/outputs/f2c2_boxgap.txt) · [`2026-10-07_f2c2_return_box.png`](../04_navigation/figures/2026-10-07_f2c2_return_box.png) |
| 10-07 §7.1 | f2d2 상자 앞 정지 — 로그(`job921_run.sh`) + 그림(`render_f2d2_box2.py`) | 카메라만 본 치명 칸 **두 묶음**: ① (1.3~1.6, −0.30~−0.45) ② 통로 가운데 (1.10~1.30, −0.10~+0.10). 같은 범위 카메라 칸 y 상위 5 % 는 f2c2 −0.12 · f2d2 −0.00. 두 묶음 사이 ≈ 0.2 m < 차체 폭 0.33 | ② 는 실제 낮은 상자(사용자). f2c2 의 '밀며 옴' 은 ② 를 민 것으로 다시 읽음(측정 + 추정) | [`j921_f2d2_g10.txt`](../debug_log/2026-10-07/outputs/j921_f2d2_g10.txt) · [`2026-10-07_f2d2_box_stop.png`](../04_navigation/figures/2026-10-07_f2d2_box_stop.png) · 'y 상위 5 %' 원문 없음(SUMMARY 수치만) |
| 10-07 §7.2 | 재계획 때 전역 단면(x 1.0~1.6) | +380 s ② 가 y −0.15~+0.15 를 99 로 막음 · 남쪽 y −0.35~−0.25(80~88) · 북쪽 +0.30~+0.40(70~80) 남음 → 계획기는 남쪽. **+399 s ② 가 전역에서 사라짐** | '멀리선 보이고 가까이선 잊힘'(추정) | 단면 원문 없음(SUMMARY 수치만) |
| 10-07 §8.1 | 설정 확인 + `box_vis.py`(전역 상자 ② 칸 vs 카메라 표시 조건) | 전역 상자 ② 치명 칸: **f2c2 내내 0**, f2d2 +76.6 s 에 3 칸뿐, 0.41 m 앞에 선 동안 0 | 전역의 잊음은 '라이다 2D 소거' 가능성이 가장 큼 — **설정 근거 + bag 정황, 소거 순간 직접 관측 아님** | [`box_vis.txt`](../debug_log/2026-10-07/outputs/box_vis.txt) |
| 10-07 §8.2 | `global_camera:=stvl` 구현: 전역 plugins static · stvl · obstacle(scan 만) · inflation, voxel_decay 600(선형), 절두체 근평면 min_z 0.8, 가속 100 | — | 사용자 조건 '화각 밖은 기억, 카메라가 볼 땐 갱신' 에 맞는 층으로 판단(계산 2.4 s 소거는 추정 식) | 커밋 `de2a9a8e` |
| 10-07 §8.3 | 시험 선언(주행 아님) C1 기억 · C2 갱신 ≤ 5 s · C3 재표시 ≤ 3 s · C4 유령 | — | `box_step.py` 단계 실행 + 녹화 `job923_rec.sh` | 10-07 §8.3 |
| 10-07 §8.4 | 첫 시도 | 단계 1 에서 상자 ② 0 칸, **전역 출발 방 대부분 −1(미지)** | ❌ 내 설정 결함: 재사용한 STVL 블록 `track_unknown_space: true`(실수 ②) → false, 재 prep | [`j922_prep.txt`](../debug_log/2026-10-07/outputs/j922_prep.txt) · `job925` · `job926` 출력 원천 소실, 커밋 `b6e93383` |
| 10-07 §8.5 | 재 prep 뒤 단계 1~4, 녹화 `bag_box1`(1.6 GB) | 상자 ② **25**(창 최대값) — 0.35 m 앞 30 s 도 25, 후진 22~25. 치운 뒤(카메라 상자 높이 점 98 → 218(사람) → **0**, 14:10:15 → :17 → :19) 전역 칸 **24~25 가 14:11:51 까지** | **C1 통과 · C2 불합격 → STVL 전역 채택 불가.** 소거 실패 원인 미확정 | [`j924_box_steps.txt`](../debug_log/2026-10-07/outputs/j924_box_steps.txt) · [`j929_box_points.txt`](../debug_log/2026-10-07/outputs/j929_box_points.txt) · bag `2026-10-07/bags/bag_box1.tgz`(로컬) |
| 10-07 §10.1 | `plan_vs_box.py`(f2d2 13:17~13:19) | 경로 발행 13:16:44 다음은 **13:17:58** 뿐. 로컬은 13:17:25 부터 상자 근처 치명 4 → 60 칸, 남은 경로는 13:17:39 부터 그 칸에서 **0.01~0.02 m**. 재계획 경로는 전역 **< 99 인 7 칸**(x 1.29~1.45 · y −0.41~−0.31)에서 0.02 m | **계획기와 MPPI 가 다른 지도** + **주기 재계획 없음**(측정) | [`plan_vs_box.txt`](../debug_log/2026-10-07/outputs/plan_vs_box.txt) |
| 10-07 §16 | 사용자 "nvblox 를 쓰고 있으면 STVL 을 빼도 되지 않나" | 기본 구성엔 STVL 이 이미 없음(로컬 nvblox · 전역 obstacle). `job933_nvslice.py` 는 사용자 지시로 중단 | 실제 쟁점 = 전역 기억을 nvblox 로 풀 수 있나 → 내일 | 출력 없음(중단) |
| 10-08 §1 · §1.1 | Jetson 무응답 → PC 에서 rosbags 로 `bag_box1` 슬라이스(`nvslice_pc.py`) | 상자 ② 자리 48 점 중 장애물: 정지 9 · 접근 17~21 · 후진 뒤 14~15 → 8 · 치운 뒤 14:10:17 **12**(사람) → :19 **3** → :21 **2** → :35 1 → 14:11:20 **0** | C1 통과(단 30 s 는 감쇠 수명 81 s 안). C2 선언 기준(5 s 안 0)으론 불합격 — 1~2 칸이 64 s. **'카메라가 볼 때 갱신' 은 nvblox 쪽이 실제 동작** | [`nvslice_box1.txt`](../debug_log/2026-10-08/outputs/nvslice_box1.txt) |
| 10-08 §2 · §2.1 | '전역에 nvblox 를 넣었다면' — f2c2 · f2d2 재계산(`nv_global_whatif.py`, 첫 판은 /map 을 슬라이스로 잘못 읽어 멈춤) | 카메라만 본 묶음 f2c2 **35** · f2d2 **41**, 큰 것 (−0.09, −4.79) 122 칸 · 198 s 등. 상자 ② 첫 표시 f2c2 11:14:22 · f2d2 13:17:33 — 둘 다 그 목표 첫 경로(11:13:27 · 13:16:44) **뒤** | 전역 nvblox 만으론 부족 → **보이는 순간 재계획** 이 함께 필요. '전역 inflation 0.70 이 통로를 닫는다' ❌(§2.2 정정, 실수 ④) | [`whatif_f2c2_f2d2.txt`](../debug_log/2026-10-08/outputs/whatif_f2c2_f2d2.txt) · [`2026-10-08_nvblox_global_whatif.png`](../04_navigation/figures/2026-10-08_nvblox_global_whatif.png) |
| 10-08 §2.2 | 사용자 확인 | "대부분 실제 물체였다. f2d2 (0.1, −5.8) 근처는 바닥의 에어캡 — 꽤 투명한 물체도 인식하고 피해 갔다" | 유령 위험 규칙(§2 선언)에 걸리지 않음 → A/B 주행 후보 | 10-08 §2.2 |
| 10-08 §3 · §3.1 · §3.2 | B 구성 선언 · prep: `global_camera:=nvblox replan_hz:=0.5 mppi_viz:=true`, 코스는 사용자 선택 목표 1 · 9 · 10(B → W3 동쪽 → 출발) | prep: 전역 plugins static · nvblox_layer · obstacle(scan) · inflation, BT RateController 0.5 Hz | 0.5 Hz = MPPI 지평 3.2 s 안에 새 경로(추정 근거) | [`j934_prep.txt`](../debug_log/2026-10-08/outputs/j934_prep.txt), 커밋 `453813f1` |
| 10-08 §3.3 | f2e1 | 3/3 성공(53.8 · 48.3 · 122.7 s). 13:36:01 부터 경로 ↔ 상자 칸 0.01~0.02 m. 같은 자리 로컬 99~100 · 전역 73~84, 전역 99 는 y +0.3 줄 | ❌ 내 결함: 전역 nvblox 층 `nav2_costmap_global_frame` 미지정 → 기본 odom(실행 중 값, `job937_src.sh`) → map→odom 만큼 밀림(실수 ③) | [`f2e1_box_replan.txt`](../debug_log/2026-10-08/outputs/f2e1_box_replan.txt) · [`f2e1_costmaps.txt`](../debug_log/2026-10-08/outputs/f2e1_costmaps.txt) · `job937` 출력 원천 소실, 커밋 `eb27aba4` |
| 10-08 §3.5 | 접촉 원인(`contact_eval.py`) | 다가갈수록 로컬 상자 치명 12~18 → 2 칸, 통과 때 차체 안 내접 6~12 · 치명 0 | 두 겹: ① 프레임 결함 ② 근접 **치명 → 내접 강등** + CostCritic 은 치명만 충돌(강등 기전은 추정) | [`f2e1_contact.txt`](../debug_log/2026-10-08/outputs/f2e1_contact.txt) |
| 10-08 §3.6 · §3.7 · §3.8 | 프레임만 고친 B 로 f2e2 | 3/3(52.1 · 49.1 · 108.5 s), 상자 ② 중심 로컬 · 전역 차 ≤ 0.04 m, 경로 ↔ 상자 0.19~0.31 m, 차체 ↔ 상자 최소 0.06 m, 경로 발행 105 회 · 0.3 m 넘는 변화 2 회 · 계획기 CPU 10.9 % | ③-a · ③-b · ③-c 통과, **사용자: 닿지 않음** | [`j934b_prep.txt`](../debug_log/2026-10-08/outputs/j934b_prep.txt) · [`f2e2_box_align.txt`](../debug_log/2026-10-08/outputs/f2e2_box_align.txt) · [`f0_f2e2_runner.log`](../debug_log/2026-10-08/outputs/f0_f2e2_runner.log) · bag `2026-10-08/bags/bag_f2e2.tgz`(로컬) |
| 10-08 §7 | 마무리 | — | B 구성 기본값 전환 · STVL 정리 미결정, 근접 정면 상자 강등 대책은 다음 | 10-08 §7 |
| 10-12 §1 · §1.1 | B 구성을 그대로 순회에 씀(f2f1 부터, PreferForward 15 만 바꿈) | prep 출력 `전역 plugins: … ['static_layer', 'nvblox_layer', 'obstacle_layer', 'inflation_layer']` · `RateController hz="0.5"` · `전역 nvblox 프레임 String value is: map` | 10-08 미결이던 기본값 전환이 사실상 이날부터(→ 10-12 운용 확정, CLAUDE.md §6). f2f1 복귀 상자 ② 옆 멈칫은 CPU 포화 탓(§2) | [`j934c_prep.txt`](../debug_log/2026-10-12/outputs/j934c_prep.txt) 29 · 31 · 34 행 · [상자 옆 정지 기전](box-side-stall-cause.md) |
| 10-13 §4.6 | f2o1 목표 3 — 전역이 상자 끝을 언제 알았나(`Docs/tools/anal_box_history.py`) | 로버가 3.3~4.7 m 떨어져 있던 13:31:43~13:32:55 전역 상자 끝 **0/4** → 목표 3 첫 경로가 약 50 s 동안 상자 끝을 지나감(0.00~0.02 m). 13:33:02(1.41 m) 3/4 와 함께 경로가 0.26 m 로 비킴 | 전역은 멀어지면 잊고 1.4~1.7 m 에서 다시 안다. 재계획 0.5 Hz 덕에 다시 본 뒤 2 s 안에 경로가 바뀜(측정). 그러나 정지의 원인은 '잊음' 이 아니라 다시 그린 경로가 0.22~0.29 m 로 가까운 것 → [기전 카드](box-side-stall-cause.md) | [`f2o1_box_history.txt`](../debug_log/2026-10-13/outputs/f2o1_box_history.txt) 52~73 행 |
| 10-13 §5.1 | 전역이 상자를 오래 기억하게 하는 안 | — | **보류(사용자)**: 지나간 사람 같은 동적 물체도 남아 경로가 막힘. 지금 구조엔 정적 · 동적을 가를 수단 없음(사람 마스크는 JetPack 7.2 Phase) | 10-13 §5.1 |
| 10-13 §6.2 · §13 | 잊는 까닭 · 다시 보는 거리 확인(`Docs/tools/anal_box_layers.py` + 설정) | nvblox 슬라이스 좌표계 odom, 상자 끝 첫 값 1.51 m. f2o1 전역 0/4 가 된 13:31:43 에 로버 ↔ 상자 3.25 m | 멀리서 잊는 원인은 감쇠(0.99, 약 81 s)가 아니라 **`map_clearing_radius_m: 3.0`**, 다시 보는 1.5 m 는 **통합 거리 1.4**(설정 근거). '다시 보면 갱신' 은 이미 됨 — 사용자 질문 "기억 말고 다시 봤을 때 갱신" 의 답 | [`f2o1_box_layers.txt`](../debug_log/2026-10-13/outputs/f2o1_box_layers.txt) 2 행 `nvblox 슬라이스: 좌표계 odom, 칸 0.050 m …` · `config/nvblox_local.yaml` 42 행(지금도 같음) |
| 10-13 §14.1 → 10-14 §6 | 통합 거리 1.4 → 2.0(사용자 "2.0 으로 복구") → 다음 날 1.4(사용자 "1.4 로 되돌려라") | 2.0 으로는 한 번도 안 띄움(재부팅 뒤 prep 전 되돌림) | 되돌린 근거: 멀리서 처음 볼 때 한 줄 두껍게(10-14 §5.1) · 각 오차가 거리에 비례(§4.2). 이후 10-22 에 다시 2.0 | `config/nvblox_local.yaml` 50~57 행 이력 주석 |
| 10-14 §1 · §4.1 | 전역에서 카메라 칸 둘레만 통과 금지 띠 D(`Docs/tools/anal_plan_keepout.py`, 3 주행 71 계획) | D 0.30 까지 경로 없음 0/71 · 상자 끝 +5~10 cm, D 0.35 에서 10/71 이 그 상자 옆 '통로 막힘' | 여유 한 칸 → 사용자 기각("여러 부분에서 문제"). 설정 안 바꿈 | [`keepout_all.txt`](../debug_log/2026-10-14/outputs/keepout_all.txt) |
| 10-14 §24 · §25 | 계획기 경로가 낮은 상자를 가로지른 한 번(f2u2 16:30:06.6) · 사용자 결정 | /plan 이 전역 253 칸 20/55 점 — 같은 지도의 NavFn 흉내는 내접을 피함. 출발점 상자 = **라이다 아래 물체 감지 시험용으로 일부러 둔 물체**(사용자) | 전역 nvblox 가 상자를 알아도 이상 경로 1 회(원인 미확인). 이 자리 여유 · 정지는 낮은 물체 회피 성능의 측정값으로 읽음 | [`anal_navfn_replay_f2u.txt`](../debug_log/2026-10-14/outputs/anal_navfn_replay_f2u.txt) · 10-14 §25 |
| 10-15 §18.3 | f2v3 멈춘 뒤 9 분 서 있다가 복귀(서쪽 통로 상자) | 출발 순간 최근접 17.5 cm(라이다 종이백), 상자 모서리 카메라 칸 **사라짐** | 라이다 아래 물체는 시야 밖 감쇠 뒤 로컬 · 전역에서 없어짐 — 오래 서 있으면 실제 상자가 지도에 없다(측정). '대기 늘리기' 대책이 위험한 근거 | [`anal_motion_probe_f2v3r.txt`](../debug_log/2026-10-15/outputs/anal_motion_probe_f2v3r.txt) |
| 이후 8 기(10-19 ~ 10-23) | 다음 시기에서 채움(포인터는 §7 끝) | — | — | — |
| 이후 9 기 10-27 §14(다른 묶음 — 요약) | f2st1 복귀 막힘 칸 원자료 대조 | 로버가 상자에서 약 2.4 m 멀어진 11:19:48~52 에 전역 P 값 99 → 80 → 39 · nvblox ≤ 0 칸 3 → 0(**4 s**). 11:23:41.7 복귀 경로를 상자 없는 지도로 계획(P 41) → 11:24:32 2.1 m 에서 다시 봄 → 막힘 판정 → Wait · 재계획(복귀 16.3 cm) | '멀어지면 잊는 전역 지도' 가 막힘의 원인, 막힘 노드는 맞게 동작. 2.4 m · 4 s 로 사라진 기전은 **미확인**(감쇠 0.99 면 점진적이어야 함 — 아래 §7 어긋남) | [`anal_block_cell_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/anal_block_cell_f2st1.txt) · 도구 [`anal_block_cell.py`](../debug_log/2026-10-27/jobs/anal_block_cell.py) |
| 10-27 §15 ~ §17 | 전역 nvblox 층(map 프레임)의 TF 조회 실패 처리 결함 · 수정 | 실패 순간 슬라이스를 단위 변환으로 적어 카메라 장애물이 0.55 m · 7.5° 틀어진 전역 장(f2st1 3 장) → catch 에 return | 이 카드 10-08 §3.3 의 프레임 지정(`navigation.launch.py` 97 행)부터 조회 경로를 타게 된 결함 → [TF 카드](nvblox-layer-tf-drop.md) | `2026-10-27/outputs/block_cell/` · `outputs/tffix/` |
| 10-27 §19 ~ §21 | f2tf1 복귀 접촉 · 사용자 결정 | 늦어도 15:02:14(로버 4.1 m)부터 P (1.13, 0.14) 0.4 m 안 전역 치명 없음 → 복귀 경로가 상자 북쪽 끝 바로 위 → 카메라 시야 밖으로만 지나 **접촉 · 밀림**(사용자 확인). 사용자: "상자 잊기는 기능, 시야는 센서 한계" | 전역이 화각 밖에서 오래 기억하게 하는 안은 다시 **하지 않음**(10-13 §5.1 보류와 같은 방향) — 본체 [복귀 상자 카드](box-return-cells.md) §7 | [`anal_block_cell_f2tf1.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/box/anal_block_cell_f2tf1.txt) 271 행 · [`chk_cam_fov_f2tf1_return.txt`](../debug_log/2026-10-27/outputs/drives/f2tf1/box/chk_cam_fov_f2tf1_return.txt) |
| 10-27 §25 · 10-28 §4 | f2tt1 · f2tt2 복귀 | 둘 다 '잊었다 다시 봄' → 막힘 (1.24, 0.07) · (1.50, 0.06) → 중단 · 재계획 · MonotoneEscape, 복귀 14.4 · 14.0 cm | §14 와 같은 기전이 반복 — 다시 보면 막힘으로 비켜 감 | [`nav_events_ms_f2tt1.txt`](../debug_log/2026-10-27/outputs/drives/f2tt1/nav_events_ms_f2tt1.txt) · [`nav_events_ms_f2tt2.txt`](../debug_log/2026-10-28/outputs/drives/f2tt2/nav_events_ms_f2tt2.txt) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 전역 obstacle 층의 한 2D 격자에서 **라이다 소거가 카메라 표시를 지운다** | 설정(`scan.clearing: true` · 같은 격자) + `box_vis.py` 의 전역 상자 ② 칸 시계열 | f2c2 내내 0, f2d2 3 칸 1 회(4 s 간격 표본) | **지지(정황)** — 소거 순간을 직접 본 것은 아님. 같은 소스의 카메라 자체 소거(`camera.clearing: true`, raytrace 1.5 m)와 근거리 0.45 m 컷도 0 을 만들 수 있어 따로 가르지 않음(미확인) |
| 계획기가 상자를 알아도 **재계획이 늦어** 옛 경로로 간다 | `plan_vs_box.py`: 경로 발행 시각 vs 로컬 상자 칸 | 13:17:25 상자 표시 → 다음 발행 13:17:58(33 s) | **지지(측정)** |
| STVL 전역 층이 '기억 + 볼 때 갱신' 을 한다 | `box_step.py` C1 · C2 | C1 25 유지 · C2 치운 뒤 95 s 넘게 24~25 | **기각(갱신)** — 원인(감쇠 모델 · 가속 식 · 절두체 프레임) 미확정, 이 시기엔 더 안 팜 |
| nvblox 슬라이스는 볼 때 갱신한다 | 같은 bag, `nvslice_pc.py` | 치운 뒤 8 → 3 → 2(2 s 표본 두 번), 1 칸은 64 s 뒤 0 | **지지(대부분)** — 남은 1~2 칸이 관측 소거인지 감쇠(81 s)인지 못 가름 |
| 전역 nvblox 를 넣으면 유령이 통로를 닫는다(10-01 §8.24 재발) | `nv_global_whatif.py` 묶음 목록 → 사용자 확인 | 묶음 f2c2 35 · f2d2 41, 사용자 "대부분 실제 물체" | **기각(이 코스 · 이 날)** — 어느 묶음이 실제가 아니었는지는 기록 없음 |
| 전역 nvblox 가 있으면 계획기가 상자를 미리 안다 | 같은 도구, 상자 ② 첫 표시 vs 목표 첫 경로 | 둘 다 첫 경로 뒤(nvblox 반경 3 m · 통합 1.4 m) | **기각** → 주기 재계획 필요 |
| f2e1 접촉 = 전역 층 프레임 밀림 | 실행 중 파라미터(`job937`) + 같은 시각 전역 · 로컬 단면(`f2e_gcm.py`) + 고친 뒤 f2e2 위치 비교 | odom(원천 소실) · 전역 99 가 ≈ 0.3 m 북쪽 · f2e2 차 ≤ 0.04 m | **지지(측정)** |
| 근접 정면 상자의 로컬 치명 칸이 내접으로 강등돼 MPPI 가 밀고 지나감 | `contact_eval.py` | 치명 12~18 → 2, 차체 안 내접 6~12 · 치명 0 | 현상 **측정**, 기전(카메라 근거리 한계 + nvblox 거리값 약화)은 **추정 · 미검증** |
| (10-13) 전역이 멀리서 상자를 잊는 것은 감쇠(81 s) 탓 | f2o1 전역 상자 끝이 0/4 가 된 시각의 로버 ↔ 상자 거리 + `nvblox_local.yaml` | 13:31:43 에 3.25 m(관측 끊긴 지 81 s 안) | **기각** → `map_clearing_radius_m: 3.0`(3 m 밖 지움)이 원인(설정 + 시각 일치, 10-13 §13) |
| 09-22 N6-1 전역 nvblox 도 같은 프레임 결함이었다 | (이번 확인) 커밋 `384c1eb6` ~ `1d50bd00^` 의 `navigation.launch.py` · `nav2_params.yaml` 에 `nav2_costmap_global_frame` 줄 없음 | 설정 없음 = 기본값으로 돌았음(코드) | **설정은 지지(코드)** · 그 결함이 10-01 §8.24 유령에 얼마나 섞였는지는 **미확인**(10-08 §3.3 도 추정으로 적음) |

## 4. 조치와 효과
### 4.1 `global_camera:=stvl`(10-07, 기각)
- `navigation.launch.py` 의 활성 파라미터 생성 함수가 전역 plugins 를 static · stvl · obstacle · inflation 으로 바꾸고 obstacle 소스를 scan 하나로, STVL 은 `voxel_decay 600` · `decay_model 0` · `track_unknown_space False`(§8.4 정정) · `depth_clear.min_z 0.8` · `decay_acceleration 100`(커밋 `de2a9a8e` · `b6e93383`). 실효값은 prep 출력으로 확인:
  ```
  전역 plugins: String values are: ['static_layer', 'stvl_layer', 'obstacle_layer', 'inflation_layer'] · …
  stvl_layer.voxel_decay Double value is: 600.0
  stvl_layer.depth_clear.min_z Double value is: 0.8
  stvl_layer.depth_clear.decay_acceleration Double value is: 100.0
  ```
  (`2026-10-07/outputs/j922_prep.txt` 48~52 행)
- 효과: C1 기억은 됨, C2 갱신이 안 돼 사용자 조건(동적 물체를 오래 기억하면 갈 수 있는데 못 감) 위반 → **채택 안 함**. 옵션은 코드에 남음(지금 `navigation.launch.py` 79~87 행).

### 4.2 `global_camera:=nvblox` + 프레임 고침(10-08)
- 전역 plugins static · nvblox_layer · obstacle(scan 만) · inflation. f2e1 뒤 한 줄 추가(커밋 `eb27aba4`, 지금 `navigation.launch.py` 97 행):
  ```python
  gp.setdefault('nvblox_layer', {})['nav2_costmap_global_frame'] = gp.get('global_frame', 'map')
  ```
  확인 출력(`2026-10-08/outputs/j934b_prep.txt` 48 · 53 행): `전역 plugins: … ['static_layer', 'nvblox_layer', 'obstacle_layer', 'inflation_layer']` · `전역 nvblox 프레임 String value is: map`.
- 효과(f2e1 → f2e2): 전역 상자 ② 위치 ≈ 0.3 m 밀림 → 로컬과 차 ≤ 0.04 m, 경로 ↔ 상자 0.01~0.02 → 0.19~0.31 m, 접촉 1 → 0(사용자). **한 번의 주행**이고 상자 옆 차체 여유는 0.06 m 로 작았다.

### 4.3 `replan_hz:=0.5`(10-08)
- BT 원본의 `<RateController hz="0.01">` 한 줄을 바꾼 사본 `/tmp/nav_to_pose_active.xml` 을 쓴다(지금 `navigation.launch.py` 112~114 행: 그 줄이 정확히 1 개가 아니면 assert 로 기동 실패).
- 효과: 상자 ② 가 보인 표본(14:39:28)부터 경로가 0.21 m 이상 비켜 감(③-b). 대가: 경로 발행 f2e1 114 회 · f2e2 105 회, 0.3 m 넘는 경로 변화 5 회 · 2 회(③-c 기준 '목표당 > 5' 이내), 계획기 CPU 10.9 %(A f2c2 10.2 %).

### 4.4 지금 저장소 코드(11-02 확인, 고치지 않음)
| 항목 | 지금 | 위치 |
|---|---|---|
| `global_camera` 선택지 · 기본 | obstacle \| stvl \| nvblox, **기본 obstacle**(launch). 순회 기본은 prep 이 `global_camera:=nvblox replan_hz:=${REPLAN_HZ:-0.5}` 를 붙여서 정함 | `navigation.launch.py` 78 · 207 행, `Docs/tools/prep_patrol.sh` 17 행 |
| 전역 nvblox 층 프레임 | `nav2_costmap_global_frame` = 전역 `global_frame`(map) — nvblox 일 때만 | `navigation.launch.py` 97 행(로컬은 68 행에서 `local_frame`) |
| `replan_hz` | 기본 '' = 원본 0.01, 주면 RateController 사본 | `navigation.launch.py` 101 · 112~114 · 201 행, BT 원본 `config/nav_to_pose_no_spin.xml` 66 행 `hz="0.01"` |
| 원본 YAML 전역 plugins | `static · stvl · obstacle · inflation`(원본 · 대조군 값, launch 가 `_GLOBAL_PLUGINS[layer]` 로 덮음 — nvblox 모드 기본은 static · obstacle · inflation) | `config/nav2_params.yaml` 561 행, `navigation.launch.py` 39~44 · 57 행 |
| 원본 YAML 전역 obstacle 소스 | `scan camera`(10-01 §8.35) — `global_camera:=nvblox\|stvl` 이면 `scan` 으로 덮음 | `config/nav2_params.yaml` 669 · 686~695 행 |
| 전역 nvblox_layer 블록 | 이진 코스트맵, `max_obstacle_distance 0.40` · `inflation_distance 0.175`, **프레임 줄 없음**(launch 가 넣음) | `config/nav2_params.yaml` 565~572 행 |
| ⚠ 낡은 주석 | "슬라이스는 odom 프레임, 전역은 map 프레임 → 플러그인이 TF 로 변환(09-21 §10.4 코드)" — 실제로는 `nav2_costmap_global_frame` 을 지정해야 map 으로 변환되며, 지정 안 하면 odom 기본이라 10-08 f2e1 처럼 밀린다 | `config/nav2_params.yaml` 563 행 |
| 층 TF 조회 실패 처리 | 조회 실패 시 슬라이스를 버림(이후 10-27 패치 — 이 시기엔 없음. 이 시기 B 구성은 실패 순간 단위 변환으로 적었을 것 — 10-08 f2e1 · f2e2 nav2 로그의 층 경고 수는 안 셈) → [TF 카드](nvblox-layer-tf-drop.md) | `Docs/05_nvblox/nvblox_nav2_rover.patch` 5~10 행(hunk 전체, 9 행이 `return;` 줄) |
| nvblox 지우기 반경 · 통합 거리(11-03 확인) | `map_clearing_radius_m: 3.0`(전역이 멀리서 잊는 원인, 10-13 §13) · `projective_integrator_max_integration_distance_m: 2.0`(이 시기 끝 1.4 → 10-22 에 2.0) | `config/nvblox_local.yaml` 42 · 57 행 |
| CostCritic | `critical_cost: 300.0` · `collision_cost: 1000000.0` · `consider_footprint: true`(지금 값; 10-08 §3.5 '치명만 충돌' 설명의 근거 설정) | `config/nav2_params.yaml` 269 행 |

## 5. 내 실수
### 실수 ① 상자가 둘인 줄 모르고 상자 ① 묶음까지 거리로 '상자 접촉' 을 읽음 (10-07 §2.6 → §7.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2c2 복귀에서 로버가 상자 쪽으로 다시 튼 이유와 접촉 여부(`jobs/f2c2_boxgap.py`) |
| 본 것 | '라이다 점에서 7.5 cm 넘게 떨어진 로컬 치명 칸 묶음' map x 1.3~1.7 · y −0.25~−0.5 까지 최소 0.073 m(+106 s) |
| 처음 추론 | 계획 경로가 상자에서 약 10 cm 로 지나 MPPI 가 상자 쪽으로 복귀 · 실제로 밀었으니 카메라 칸이 앞면을 늦게 · 덜 표시(추정) |
| 의심한 이유 | f2d2 에서 같은 범위에 **카메라 칸 묶음이 둘** 나옴(§7.1), 사용자 "그 위치에 상자 하나가 원래 있었다" |
| 판별 시험 | f2c2 · f2d2 의 같은 범위 카메라 칸 y 상위 5 % 비교(−0.12 vs −0.00), 사용자 현장 확인 |
| 결론 | 민 것은 통로 가운데 **상자 ②**(f2c2 에선 카메라 칸이 거의 안 보임), 7.3 cm 는 상자 ① 까지 거리. '앞면을 늦게 표시' 는 상자 ① 에 대한 말이 아니라 상자 ② 가 전역 · 로컬에서 빠진 문제였다 |
| 다음에 알아보는 법 | 상자 근접 판정 전에 현장 물체 수 · 위치를 사용자에게 먼저 확인. 거리 계산 창(`box = (X > 1.2) & (X < 1.8) & (Y > -0.6) & (Y < -0.15)`)이 고정 범위면 그 밖 물체는 0 으로 빠진다 |
| 스크립트 핵심 | `2026-10-07/jobs/f2c2_boxgap.py` 10 행 `box = (X > 1.2) & (X < 1.8) & (Y > -0.6) & (Y < -0.15)` |
| 나온 결과 | `+106.0 s 자세 (1.55,0.03,-171°) \| 상자 칸  41, 외곽까지 최소 0.073 m \| 계획(+91 s) 대비 옆 -0.001 m(+ = 왼쪽), 방향  +12°` (`2026-10-07/outputs/f2c2_boxgap.txt`) |
| 데이터 | 결과 `2026-10-07/outputs/f2c2_boxgap.txt`, 도구 `2026-10-07/jobs/f2c2_boxgap.py` · `job912_extract.py`, 입력 bag `2026-10-07/bags/bag_f2c2.tgz` → 중간 `x912_f2c2.npz`(스크래치패드, 원천 소실 — bag 에서 재생성 가능), 그림 `Docs/04_navigation/figures/2026-10-07_f2c2_return_box.png` |

### 실수 ② STVL 블록을 그대로 재사용해 `track_unknown_space: true` 로 전역 빈 공간을 미지로 덮음 (10-07 §8.4)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `global_camera:=stvl` 첫 시험(`jobs/job922_prep.sh` → `box_step.py mark 20`) |
| 본 것 | 단계 1 에서 상자 ② 칸 0, 전역 코스트맵 출발 방 대부분 −1 |
| 처음 추론 | (점군이 안 오는지 의심) `job925_chk.sh` 로 점군 · 로컬 확인 → 점군 16 Hz 정상, 로컬은 앞을 봄 |
| 의심한 이유 | 점군 · 로컬은 정상인데 전역만 −1 — 층 결합 문제 |
| 판별 시험 | `job926_gc.py` 로 전역 상자 근처 값 표 |
| 결론 | Phase S STVL 블록의 `track_unknown_space: true` 가 카메라가 못 본 곳을 미지로 표시하고 최대값 결합으로 정적 지도의 빈 공간까지 가림 → false 로 고침(커밋 `b6e93383`) |
| 다음에 알아보는 법 | 다른 용도 블록을 재사용할 땐 `track_unknown_space` · `combination_method` 같은 결합 설정을 새 용도로 다시 읽는다. 서명 = 정적 지도는 정상인데 전역이 넓게 −1 |
| 스크립트 핵심 | `navigation.launch.py`(커밋 `b6e93383`) `sv['track_unknown_space'] = False` |
| 나온 결과 | 원천 소실(`job925` · `job926` 출력은 저장 안 됨 — SUMMARY 서술만) |
| 데이터 | prep 출력 `2026-10-07/outputs/j922_prep.txt`(새 설정 반영 확인), 도구 `2026-10-07/jobs/job925_chk.sh` · `job926_gc.py` |

### 실수 ③ 전역 nvblox 층 프레임을 지정하지 않음 — 로컬에만 지정 (10-08 §3.3, 뿌리는 09-22)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | B 구성 `global_camera:=nvblox`(커밋 `453813f1`) 로 f2e1 |
| 본 것 | 13:36:01 부터 경로가 상자 칸에서 0.01~0.02 m, 같은 map 좌표에서 로컬 99~100 · 전역 73~84, 전역 99 는 y +0.3 줄 |
| 처음 추론 | (주행 결과만 볼 땐 3/3 성공) 사용자 접촉 보고 뒤 원인 조사 |
| 의심한 이유 | 같은 시각 같은 map 좌표에서 두 지도가 다름 — 전역 상자가 한 방향으로 통째로 밀림 |
| 판별 시험 | `job937_src.sh` 로 실행 중 `nvblox_layer.nav2_costmap_global_frame`(전역 · 로컬) → 전역 odom. 고친 뒤 f2e2 에서 두 지도 상자 중심 비교 |
| 결론 | 전역 격자는 map 인데 층이 odom 기준으로 그려 map→odom 보정(f2e1 끝 Δy 0.31 m)만큼 밀림. 고친 뒤 차 ≤ 0.04 m. 이번 확인: 09-22 N6-1 전역 nvblox(커밋 `384c1eb6`)부터 10-01 제거 전(`1d50bd00^`)까지도 프레임 줄이 없었다 — 그때 영향 크기는 미확인 |
| 다음에 알아보는 법 | 서명 = 같은 시각 · 같은 map 좌표에서 전역 · 로컬 칸이 한 방향으로 일정량 어긋나고 그 양이 map→odom 보정과 비슷함. 층을 다른 코스트맵에 옮길 때 프레임 파라미터를 실행 중 값으로 확인(prep 에 `ros2 param get … nav2_costmap_global_frame` 줄 — `job934_prep.sh` 10 행) |
| 스크립트 핵심 | `2026-10-08/jobs/f2e_gcm.py` 24~27 행 — odom 격자면 map → odom 으로 바꿔 같은 map 좌표의 칸을 읽음: `if m.header.frame_id == 'odom': … X, Y = c_ * dx + s_ * dy, -s_ * dx + c_ * dy` |
| 나온 결과 | `13:36:06 /global_costmap/costmap (map 프레임)` 의 `y +0.3   83   90   99   99   99   96` · `y -0.0   73   80   84   84   80   73`, 같은 때 로컬 `y -0.0   99   99  100   99   99   80` (`2026-10-08/outputs/f2e1_costmaps.txt`) |
| 데이터 | 결과 `2026-10-08/outputs/f2e1_costmaps.txt` · `f2e1_box_replan.txt` · `f2e2_box_align.txt`, 도구 `2026-10-08/jobs/f2e_gcm.py` · `f2e_eval.py` · `box_align.py` · `job937_src.sh`(출력 원천 소실), bag `2026-10-08/bags/bag_f2e1.tgz` · `bag_f2e2.tgz`, 영상 `2026-10-08/videos/f2e1_global_debug.mp4`(git 제외) |

### 실수 ④ '전역 inflation 0.70 이 통로를 닫는다' 는 설명 (10-08 §2.1 → §2.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 전역 nvblox 의 위험을 설명 |
| 본 것 | (수치 아님) 로컬 inflation 0.40 · 전역 0.70 |
| 처음 추론 | 전역 inflation 이 넓어 같은 칸이 통로를 더 쉽게 '닫힌' 것으로 만든다 — 10-01 §8.24 와 같은 기제 |
| 의심한 이유 | inflation 은 내접(0.175) 밖에선 비용만 올림 — [inflation · padding 카드](inflation-padding-roles.md) 의 원리와 모순 |
| 판별 시험 | 원리 대조(측정 없음) |
| 결론 | 통로 닫힘은 유령 칸(치명) 자체 때문. inflation 은 그대로 둠(§2.2 정정) |
| 다음에 알아보는 법 | '닫힘' 을 말하기 전에 그 칸이 치명 · 내접(≥ 99)인지, 비싼 길(< 99)인지 값으로 확인 |
| 스크립트 핵심 · 나온 결과 | 해당 없음(설명 정정) |
| 데이터 | 10-08 §2.1 · §2.2 |

### 작은 실수 — `nv_global_whatif.py` 첫 판이 /map 을 슬라이스로 처리 (10-08 §2.1)
위치 추정 모드가 10 s 마다 다시 발행한 `/map` 을 슬라이스 분기로 넘겨 f2d2 에서 멈춤 → 첫 /map 만 쓰도록 고침(`2026-10-08/jobs/nv_global_whatif.py` 27 행 주석). 첫 판 출력은 원천 소실.

## 6. SUMMARY · 정리 페이지 ↔ 원문 어긋남 (이번 확인)
| # | 기록 | 원문 | 판정 |
|---|---|---|---|
| 1 | 10-07 §8.5 "'출발 방 그 밖 고비용' 칸도 49 → 86" | `j924_box_steps.txt`: 단계 1~3 은 **65~76**, 단계 4 재관찰 첫 줄들 **125 · 184 · 181 · 110 · 107** | SUMMARY 수치가 원문에 없음 — 원문 기준 65~76 → 107~184 |
| 2 | 10-08 §1.1 제목 "치운 뒤 2~3 s 에 대부분 지움" · 같은 § "8 칸 중 6 칸(75 %)은 3 s 안에" · 10-08 정리 페이지 "치운 뒤 2~5 s 3 → 2" · "75 % 를 3 s 안에" | `nvslice_box1.txt`: 14:10:15 8 · :17 12 · **:19 3**(5/8 = 62.5 % 지움) · **:21 2**(6/8 = 75 %). 치운 시각을 14:10:16 으로 두면 3 s · 5 s | 75 % 는 **5 s** 표본. 기준 시각도 둘로 갈림 — 10-08 페이지는 '14:10:16 무렵', 10-07 페이지는 '14:10:17~19'(`j929_box_points.txt`: :15 상자 높이 점 98 · :17 218(사람) · :19 0). 카메라 점이 0 이 된 첫 표본(14:10:19) 기준이면 nvblox 는 같은 표본에 3, 2 s 뒤 2 |
| 3 | 10-08 §1.1 표 "STVL 전역 25" 를 nvblox 9 와 나란히 | STVL 수는 전역 코스트맵 **≥ 99**(내접 포함) 칸을 **5 × 5 = 25 칸 창**(`box_step.py` `count(1.1, 1.3, -0.1, 0.1)`)에서 센 값 — 25 는 창 최대값(포화). nvblox 수는 슬라이스 거리 ≤ 0.05 m 칸을 48 점 격자에서 센 값(팽창 없음) | 두 열은 다른 척도. 'STVL 25 그대로' 는 창 안에 치명 칸이 몇 개만 남아도 내접 띠로 거의 다 찬다는 점을 함께 읽어야 함(이번 코드 확인) |
| 4 | 10-08 §2.2 사용자 "f2d2 (0.1, −5.8) 근처 에어캡" | `whatif_f2c2_f2d2.txt` f2d2 목록에 그 중심의 묶음 없음 — 가까운 것 (−0.96, −5.92) 9 칸 · 0 s, (1.03, −5.90) 4 칸 · 52 s | 사용자가 그림(칸 색)에서 본 자리로 추정 — 묶음 대응은 미확인 |
| 5 | 10-08 §3.3 "전역은 73~84 이고 대신 y +0.3 줄에 99" | `f2e1_costmaps.txt`: 13:36:06 · :15 · :26 은 맞음, **13:35:55 전역 y +0.3 줄은 58~69** | 13:35:55 는 전역에 상자 ② 가 아직 안 찍힌 때 — '같은 시각' 은 13:36:06 이후로 읽어야 맞음 |
| 6 | 10-08 §3.5 "13:36:05~14(0.3~0.7 m): 상자 자리 치명 12~18 칸" | `f2e1_contact.txt`: 13:36:08.7 **7** · 09.2 **6** 포함 6~18 | 범위 하한이 원문과 다름(결론엔 영향 작음) |
| 7 | 10-08 §3.3 "경로 발행: 0.5 Hz 로 목표 3(복귀) 동안 수십 회" · "같은 목표 안 0.3 m 넘는 경로 변화 5 회(13:34~13:36)" | `f2e1_box_replan.txt`: 주행 전체 `경로 발행 114 회`, 첫 변화 13:34:10 → 13:34:12 는 목표 2 구간(러너: 목표 1 · 2 가 53.8 + 48.3 s, 13:33:00 출발) | 5 회는 주행 전체 · 목표 2 · 3 합계 |
| 8 | 10-07 §8.1 "카메라 조건을 만족한 순간에도 대부분 0" | `box_vis.txt` 는 4 s 간격 표본 — 조건 '예' 는 f2c2 1 표본 · f2d2 2 표본 | '대부분' 의 표본이 3 개 |
| 9 | `nav2_params.yaml` 563 행 주석 "플러그인이 TF 로 변환" | 10-08 §3.3 측정 · `eb27aba4` 수정 | 주석이 낡음(§4.4) — 코드는 고치지 않음 |

## 7. 남은 것 (10-08 시점) · 이후
- B 구성(전역 nvblox + 0.5 Hz)의 근거는 f2e2 **1 회**(목표 3 개, 상자 ② 한 자리). 기본값 전환은 그날 미결정(10-08 §7 ⑤).
- **근접 정면 상자의 로컬 치명 → 내접 강등**(f2e1 §3.5) 대책 없음 — 후보(층 치명 거리 넓히기 · MPPI 가 내접을 충돌로)는 좁은 통로 통과와 맞바꿈(10-08 §7 ④).
- f2e2 차체 ↔ 상자 최소 0.06 m — 옆으로 지나갈 때 여유가 작다.
- STVL 전역 소거 실패 원인 미확정(10-07 §15 다음 ① 이었으나 nvblox 로 방향이 바뀌어 미실행). `global_camera:=stvl` 옵션은 코드에 남음.
- 라이다 2D 소거 가설은 정황뿐 — 카메라 소스 자체 소거 · 근거리 컷과 가르지 않음.
- §2 선언 규칙('실제 물체가 아닌 묶음이 통로에 10 s 넘게 남으면 보류')의 적용이 "대부분 실제" 라는 사용자 답에 기댐 — 실제가 아닌 묶음의 목록은 없음.
- 전역 nvblox 는 반경 3 m · 감쇠 81 s 기억이라 '화각 밖에서 오래 기억' 은 못 함(10-08 §1.1 한계).
- **10-12 ~ 10-15 에서 더해진 것**(7 기, 흐름 표 10-12 ~ 10-15 줄):
  - B 구성(전역 nvblox map 프레임 + 재계획 0.5 Hz)이 10-12 부터 순회 운용 기본(`global_camera:=nvblox replan_hz:=0.5 mppi_viz:=lite`, CLAUDE.md §6 · `Docs/tools/prep_patrol.sh` 17 행). 이 시기에 B 구성의 상자 접촉은 기록상 없음 — 대신 같은 상자 옆에서 **닿지 않고 멈추는** 문제가 주가 됨 → [상자 옆 정지 기전](box-side-stall-cause.md) · [대책](box-side-stall-remedies.md).
  - 전역은 여전히 **3 m 밖에서 잊는다**(`map_clearing_radius_m: 3.0`, 10-13 §13). 다시 보면 2 s 안 경로가 바뀌므로 '다시 봤을 때 갱신' 은 되고, 오래 기억하게 하는 안은 동적 물체 때문에 보류(사용자, 10-13 §5.1).
  - 화각 밖 기억은 서 있으면 약 80 s 뒤 사라져 실제 상자가 지도에서 없어진다(10-15 §18.3) — 이 카드 §7 의 '화각 밖에서 오래 기억은 못 함' 이 정지 상황에서도 확인됨.
  - 전역 카메라 칸 금지 띠(10-14 §1)는 0.35 m 에서 통로가 막혀 기각. 계획기 경로가 낮은 상자를 가로지른 이상 1 회(10-14 §24)는 원인 미확인.
  - 남은 것 '근접 정면 상자의 치명 → 내접 강등'(10-08 §3.5)은 이 시기에 다시 재지 않음.
- **이후 9 기(10-26 ~ 10-28) — 채움(11-04)**:
  - 이 카드의 B 구성(전역 nvblox map 프레임)은 9 기에도 표준(`prep_patrol.sh` 17 행 `global_camera:=nvblox`). 같은 상자는 **멀어지면 여전히 잊는다**(f2st1 · f2tf1 · f2tt1 · f2tt2 네 번 모두), 복귀 계획은 잊은 지도로 세워지고, 다시 보면 PathBlockedAhead 가 막힘으로 비켜 간다(3 회) · 못 보면 닿는다(f2tf1 1 회). 사용자 결정(10-27 §21): 잊기는 기능, 시야는 센서 한계 — 대책 대상 아님.
  - 이 카드 10-08 §3.3 의 '프레임을 map 으로' 는 옳았지만, 그 순간부터 층이 TF 를 조회하게 되어 **상위 층의 조회 실패 처리 결함**이 드러날 조건이 됐다(10-08 ~ 10-27 매 주행 층 경고 17~54 번 — 저장소 nav2 로그 grep, [TF 카드](nvblox-layer-tf-drop.md) §5.3). 10-27 수정 뒤 실패 순간엔 직전 슬라이스를 쓴다.
  - ⚠ 기록 어긋남(11-04 확인): 10-13 §13 은 '전역은 3 m 밖에서 잊는다(`map_clearing_radius_m: 3.0`)' 였는데 10-27 §14 f2st1 은 로버 ↔ P **약 2.4 m** 에서 4 s 안에 사라졌다([`anal_block_cell_f2st1.txt`](../debug_log/2026-10-27/outputs/block_cell/anal_block_cell_f2st1.txt), SUMMARY §14.1 표 '11:19:48→11:19:52 (로버 2.3→2.5 m)'). P 는 상자 북쪽 16 cm 점이라 상자 중심까지는 조금 더 멀고, 지우기 반경이 어느 점(카메라 · base_link) 기준인지 기록에 없다 — 두 설명이 맞는지 **미확인**(§14.2 미확인 ① 그대로).
- **이후(10-19 ~ 10-23, 8 기): 다음 시기에서 채움** — 알려진 포인터만: 10-22 깊이 프리셋 3 + 통합 거리 2.0(f2lp1 복귀에서 1.4 m 안 낮은 상자를 못 보고 접촉 → 2.0 재생에서 상자 칸 회복, `config/nvblox_local.yaml` 54~57 행 주석) · 10-27 층 TF 조회 실패 시 슬라이스 버림 패치([nvblox 층 카드 §7](nvblox-layer-round-floor.md)) · 10-27 Smac Hybrid 계획기.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2c2 · f2d2 | 10-07 순회(rf2o · G4 켬) — 복귀 상자 ② 밀기 · 상자 앞 정지 | 10-07 §2.4 ~ §2.6 · §7 · §7.1, `outputs/f0_f2c2_runner.log` · `f0_f2d2_runner.log`, bag `2026-10-07/bags/bag_f2c2.tgz` · `bag_f2d2.tgz`(로컬) |
| box1 | 전역 STVL 상자 시험 단계 1~4(주행 아님, 0.5 m 전후진) | 10-07 §8.3 ~ §8.5, `j922_prep.txt` · `j924_box_steps.txt` · `j929_box_points.txt`, bag `2026-10-07/bags/bag_box1.tgz`(로컬, 820 MB 압축) · 10-08 §1 재계산 `nvslice_box1.txt` |
| whatif | 전역 nvblox 가정 재계산(f2c2 · f2d2) | 10-08 §2.1, `whatif_f2c2_f2d2.txt` · 그림 `2026-10-08_nvblox_global_whatif.png` |
| f2e1 · f2e2 | B 구성 주행(목표 1 · 9 · 10) | 10-08 §3.2 ~ §3.8, `j934_prep.txt` · `j934b_prep.txt` · `f0_f2e{1,2}_runner.log` · `f2e1_box_replan.txt` · `f2e1_costmaps.txt` · `f2e1_contact.txt` · `f2e2_box_align.txt`, bag `2026-10-08/bags/bag_f2e{1,2}.tgz`(로컬), 영상 `2026-10-08/videos/f2e{1,2}_global_debug.mp4`(git 제외) |
| 도구(10-07) | `job912_extract.py` · `f2c2_boxgap.py` · `render_f2c2_box2.py` · `job921_run.sh` · `render_f2d2_box2.py` · `box_vis.py` · `job922_prep.sh` · `box_step.py` · `job923_rec.sh` · `job925_chk.sh` · `job926_gc.py` · `job929_bagpts.py` · `job930_extract.py` · `job931_run.sh` · `plan_vs_box.py` · `job933_nvslice.py` | §9.1 ~ §9.8 |
| 도구(10-08) | `nvslice_pc.py` · `nv_global_whatif.py` · `render_whatif.py` · `job934_prep.sh` · `job936_chk.sh` · `job937_src.sh` · `f2e_eval.py` · `f2e_gcm.py` · `extract_pc.py` · `contact_eval.py` · `box_align.py` · `run_f2c.sh`(b910) | §9.9 ~ §9.15 |
| 코드(저장소) | `navigation.launch.py`(`global_camera` · `replan_hz`) | §4 |

## 9. 도구 해설
공통: 10-07 의 bag 분석은 Jetson 에서 `rosbag2_py` 로 추출해 npz(스크래치패드 · Jetson `/tmp`, **원천 소실** — bag 에서 재생성 가능)를 만들고 PC 에서 numpy 로 읽었다. 10-08 은 Jetson 무응답으로 PC 에서 `rosbags`(AnyReader) 로 bag 을 직접 읽었고, `nvblox_msgs/DistanceMapSlice` 정의(header · resolution · width · height · origin · unknown_value · data)를 손으로 등록했다. 좌표: 로컬 코스트맵 · nvblox 슬라이스는 odom, 전역은 map — 도구는 `/tf` 의 map→odom(`mo`)으로 옮긴다. 상자 ② 창은 도구마다 조금씩 다르다(아래 각 항목). 이날 도구는 전부 그날 커밋 판 그대로다(뒤에 바뀐 판 없음, `git log` 확인).

### 9.1 `job912_extract.py` · `job930_extract.py` · `job931_run.sh` — bag 추출 (10-07)
- **형태**: Jetson `python3 /tmp/job912_extract.py BAG TA TB OUT`(epoch 구간). `job921_run.sh` 가 f2d2 를 `x921_f2d2.npz` 로, `job931_run.sh` 가 `job930_extract.py`(스캔 0.2 s · 로컬 0.5 s 간격 변형)로 `fz_f2d2.npz` 를 만든다.
- **하는 일**: 첫 `/map` 1 장, 구간 안 `/tf` 의 map→odom · odom→base_link, `/odometry/ekf_a`(그림자 A), `/cmd_vel`, `/plan` 전부, 전역 코스트맵 2 s 간격, 로컬 1 s 간격, 스캔 1 s.
- **출력**: npz(원천 소실). **쓰인 곳**: §2.6 · §7.1 · §8.1 · §10.1 의 모든 수치.
- **계보 · 지금**: 10-08 PC 판 `extract_pc.py`(MPPI `/trajectories` 추가). 상시 도구로는 옮겨지지 않음.

### 9.2 `f2c2_boxgap.py` · `render_f2c2_box2.py` · `render_f2d2_box2.py` — 복귀 상자 근접 (10-07 §2.6 · §7.1)
- **형태**: PC `python f2c2_boxgap.py`(인자 없음, `x912_f2c2.npz` 고정).
- **하는 일**: 목표 10 시작(+307.8 s) 뒤 +78 ~ +112 s 의 로컬 코스트맵 2 s 마다 — 치명(≥ 100) 칸을 map 으로 옮겨 창 `X 1.2~1.8 · Y −0.6~−0.15` 를 상자로 보고, 차체 직사각(앞 0.262 · 뒤 −0.248 · 반폭 0.165) 외곽까지 최소 거리. 계획 경로 대비 옆 거리 · 방향 차(경로 3 점 앞 접선).
- **출력**: [`f2c2_boxgap.txt`](../debug_log/2026-10-07/outputs/f2c2_boxgap.txt) — 예 `+106.0 s … 상자 칸  41, 외곽까지 최소 0.073 m`. 그림 두 장(`Docs/04_navigation/figures/2026-10-07_f2c2_return_box.png` · `2026-10-07_f2d2_box_stop.png`).
- **알려진 결함**: 창이 상자 ① 자리라 상자 ② 를 못 봄(실수 ①). 칸 중심 기준이라 ±2.5 cm.
- **지금**: 안 씀. 같은 질문의 상시 도구는 이후 `Docs/tools/anal_box_pass.py` · `anal_box_history.py`(10-13).

### 9.3 `box_vis.py` — 전역 상자 ② 칸 vs 카메라 표시 조건 (10-07 §8.1)
- **형태**: PC, 인자 없음(`x912_f2c2.npz` · `x921_f2d2.npz`).
- **하는 일**: 목표 10 시작 뒤 30 s 부터 **4 s 마다** 전역 코스트맵 창 x 1.1~1.3 · y −0.1~+0.1 의 ≥ 100 칸 수, 로버 → (1.2, 0) 거리 d · 방위. 카메라 표시 조건 = `abs(bear) < 43 and 0.45 < d - 0.26 < 1.2`(D455 수평 ±43° · depth_relay 근거리 0.45 · 전역 카메라 표시 1.2 m, 0.26 은 카메라 앞 위치 근사).
- **출력**: [`box_vis.txt`](../debug_log/2026-10-07/outputs/box_vis.txt) — `+76.6 s 상자② 치명 칸  3 | … 상자까지 0.87 m · 방위  +22° | 카메라 표시 조건 예`.
- **쓰인 곳**: §8.1 '전역은 상자를 모름' 근거. **결함**: 표본 간격 4 s · 조건은 상자 중심 한 점 기준.

### 9.4 `job922_prep.sh` — 전역 STVL prep (10-07 §8.2 ~ §8.5)
- **형태**: Jetson `bash /tmp/job922_prep.sh`. `EXTRA_SENSORS="rf2o:=true shadow:=true gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=stvl"` 를 내보내고 `job780_prep_navmap.sh` 를 부른 뒤, 전역 obstacle 소스 · STVL 3 값(`voxel_decay` · `depth_clear.min_z` · `decay_acceleration`)을 `ros2 param get` 으로, 활성 yaml 첫 줄을 출력. `job726_prep_map.sh` 10 행이 `EXTRA_NAV` 를 nav 인자에 덧붙임.
- **출력**: [`j922_prep.txt`](../debug_log/2026-10-07/outputs/j922_prep.txt)(§4.1 발췌). 재 prep 출력은 따로 없음.
- **계보**: 10-08 `job934_prep.sh`(같은 꼴, nvblox) → 이후 `Docs/tools/prep_patrol.sh`.

### 9.5 `box_step.py` · `job923_rec.sh` — 상자 단계 시험 (10-07 §8.3 ~ §8.5) ★ C1 · C2 를 낸 도구 · **로버가 움직임**
- **형태**: Jetson `python3 /tmp/box_step.py mark|fwd|back|watch N`(한 번 = 한 단계). 녹화는 `bash /tmp/job923_rec.sh start|stop` — `/camera/depth/points_filtered /scan /tf /tf_static /global_costmap/costmap /local_costmap/costmap /odometry/filtered /cmd_vel /nvblox_node/static_map_slice /map_nav` 를 `/tmp/bag_box1` 로(멈추면 tgz).
- **하는 일**: 처음 3 s spin. `fwd`/`back` 은 `/cmd_vel` ±0.05 m/s 를 EKF 위치 변화가 D m 에 이를 때까지(한도 D/0.05 + 8 s), 그 뒤 정지 10 회. 0.5 s 마다 전역 코스트맵(TRANSIENT_LOCAL)에서 세 창의 **≥ 99** 칸 수:
  ```python
  b2, b1 = count(1.1, 1.3, -0.1, 0.1), count(1.3, 1.6, -0.45, -0.3); allc = count(0.3, 2.0, -0.3, 0.4)
  ```
  '출발 방 고비용' = `allc − b2`(상자 ① 창 일부 포함). 화면엔 값이 바뀔 때만 한 줄, CSV `/tmp/box_step.csv` 에 매 표본.
- **출력**: 화면 → [`j924_box_steps.txt`](../debug_log/2026-10-07/outputs/j924_box_steps.txt):
  ```
  fwd 0.50 m 끝(이동 0.510 m, 10.9 s)
   13.2 s 로버 (0.50,-0.00,-0°) | 상자② 25 · 상자① 10 · 출발 방 고비용 74
  ```
  CSV 는 원천 소실. 단계 4 두 번째 관찰의 화면 줄은 첫 몇 줄과 96.9 s 한 줄뿐이라 치운 뒤 시계열은 `job929` 쪽이 근거.
- **알려진 결함**: 상자 ② 창은 5 × 5 = 25 칸이라 25 = 포화 — 내접(99) 띠를 함께 세므로 치명 칸이 일부만 남아도 25 근처(§6-3). 출력 파일에 WSL 경고 줄이 섞여 깨진 글자가 있음. 주행 스택이 MPPI 로 움직이지 않는지 확인하는 장치는 없음(Nav2 목표가 없는 상태 가정).
- **지금**: 상시 도구로는 안 옮김.

### 9.6 `job925_chk.sh` · `job926_gc.py` — 첫 시도 진단 (10-07 §8.4)
| 도구 | 하는 일 | 출력 |
|---|---|---|
| `job925_chk.sh` | `points_filtered` · 원본 점군 `ros2 topic hz`, 구독자 수, 상자 근처 점 수 · 로컬 코스트맵(파이썬 노드) | **원천 소실**(SUMMARY "점군 16 Hz 정상, 로컬은 앞을 봄") |
| `job926_gc.py` | 전역 코스트맵 12 s 구독(TRANSIENT_LOCAL depth 5) → 받은 수 · stamp, 마지막 판의 x 0.6~1.7 × y −0.55~+0.40 값 표 | **원천 소실**(SUMMARY "출발 방 대부분 −1") |

### 9.7 `job929_bagpts.py` — 치운 시각 판정 (10-07 §8.5) ★
- **형태**: Jetson `python3 /tmp/job929_bagpts.py`(인자 없음, `/tmp/bag_box1`). 로버가 단계 4 동안 같은 자리라 **지금 TF**(map ← camera_depth_optical_frame)로 점군을 옮김.
- **하는 일**: 2 s 마다 점군에서 창 map x 1.05~1.35 · y −0.30~+0.10 안 점을 높이로 나눠 셈 — 상자 높이 `0.06 < z < 0.40` · 바닥 `z ≤ 0.06`. 같은 때 전역 코스트맵 상자 ② 창(1.1~1.3 × −0.1~0.1, ≥ 99) 칸 수. 14:03:00 이후만 출력.
- **출력**: [`j929_box_points.txt`](../debug_log/2026-10-07/outputs/j929_box_points.txt):
  ```
  14:10:15 상자 높이 점   98 · 바닥 점  283 · 전역 상자② 칸 24
  14:10:17 상자 높이 점  218 · 바닥 점  116 · 전역 상자② 칸 24
  14:10:19 상자 높이 점    0 · 바닥 점  152 · 전역 상자② 칸 25
  14:11:51 상자 높이 점    0 · 바닥 점  140 · 전역 상자② 칸 24
  ```
- **쓰인 곳**: C2 판정, 10-08 §1 치운 시각 기준. **결함**: '지금 TF' 고정 변환(로버가 움직인 구간엔 틀림). 창 범위가 `box_step` 과 다름(점 창이 더 넓음).

### 9.8 `plan_vs_box.py` — 계획기 지도 vs MPPI 지도 (10-07 §10.1) ★ '다른 지도' 를 측정한 도구
- **형태**: PC, 인자 없음(`fz_f2d2.npz`).
- **하는 일**: 13:17:07 ~ 13:18:57 의 로컬 코스트맵 4 장마다 1 장(≈ 2 s) — 치명(≥ 100) 칸을 map 으로 옮겨 창 x 1.0~1.8 · y −0.6~+0.25(상자 ① · ②), 로버 앞 남은 경로(가장 가까운 점부터)와 그 칸 최소 거리, 같은 칸의 전역 값을 치명 · 내접(99) · < 99 로 셈. 끝에 재계획 직후(E0 + 384 s) 로컬 치명인데 전역 < 99 인 칸의 위치와 새 경로까지 거리.
  ```python
  print('%s 로버 (%.2f,%.2f) | 로컬 상자 근처 치명 %3d | 남은 경로 ↔ 그 칸 최소 %.2f m … | 같은 칸 전역 값: 치명 %d · 내접 %d · <99 %d | 계획 %s' % …)
  ```
- **출력**: [`plan_vs_box.txt`](../debug_log/2026-10-07/outputs/plan_vs_box.txt) — `13:17:39 … 로컬 상자 근처 치명  60 | 남은 경로 ↔ 그 칸 최소 0.01 m … | 같은 칸 전역 값: 치명 11 · 내접 36 · <99 13 | 계획 13:16:44`, `전역 < 99(계획기는 통과 가능) 7 칸: x 1.29~1.45 · y -0.41~-0.31 | 새 경로(13:17:58)까지 최소 0.02 m`.
- **결함**: 시각 변환이 10-07 고정 기준(E0 · K0)이라 다른 날 bag 엔 못 씀(10-08 §3.4 렌더러에서 같은 결함 발견 · 수정). 상자 ① · ② 를 한 창으로 셈.
- **지금**: 같은 질문의 상시 도구는 이후 `anal_box_history.py`(10-13).

### 9.8a `job933_nvslice.py` — nvblox 슬라이스로 C1 · C2 (10-07 §16, 중단)
- Jetson `rosbag2_py` 판. 창 · 판정은 §9.9 와 같음(아래). 사용자 지시로 중단 → **출력 없음**. 다음 날 PC 판 `nvslice_pc.py` 로 대신.

### 9.9 `nvslice_pc.py` — nvblox 는 볼 때 갱신하나 (10-08 §1) ★
- **형태**: PC `python nvslice_pc.py <bag_box1 디렉터리>`.
- **하는 일**: `/tf` 에서 map→odom · odom→base_link 최신값, `/nvblox_node/static_map_slice` 를 2 s 마다 — 상자 ② 자리 **칸 중심 48 개**(x 1.075~1.325 × y −0.275~+0.075, 0.05 간격)를 map → odom 으로 옮겨 슬라이스 픽셀을 읽고, 미지(`unknown_value`)는 따로, 나머지는 **거리 ≤ 0.05 m** 면 장애물. data 길이 ≠ width × height 면 버리고 셈.
  ```python
  if v == m.unknown_value: unk += 1
  else: n += int(v <= 0.05); dmin = min(dmin, v)
  ```
- **출력**: [`nvslice_box1.txt`](../debug_log/2026-10-08/outputs/nvslice_box1.txt) — 끝줄 `길이 불일치 메시지 0`, 발췌는 §2 · §6-2.
- **결함**: 슬라이스 `header.frame_id` 를 보지 않고 odom 으로 가정. 픽셀 인덱스는 `int()`(내림) — 층 수정(floor)과 같은 규약. 전역 STVL 열과 척도가 다름(§6-3).

### 9.10 `nv_global_whatif.py` · `render_whatif.py` — '전역에 nvblox 를 넣었다면' (10-08 §2)
- **형태**: PC `python nv_global_whatif.py <bag> [출력 npz]`(f2c2 · f2d2 각각), 그림 `python render_whatif.py`(`wi_f2c2.npz` · `wi_f2d2.npz`).
- **하는 일**: 첫 `/map` 으로 빈 칸(0 ≤ 값 < 50) 거리 변환 `WALLD`. 1 s 마다 슬라이스 거리 ≤ 0.05 m 칸을 map 으로 옮기고, 같은 때 `/scan` 을 차체 기준(라이다 x 0.152, yaw π − 0.04677)으로 map 점으로 바꿔 KD 트리 거리. **카메라만 본 칸** = `(wd > 0.15) & (dl > 0.10)` — 저장 지도 벽 0.15 m 밖 · 라이다 점 0.10 m 밖. 0.1 m 칸으로 묶어 첫 · 끝 시각 · 관측 횟수, 8 이웃 연결로 묶음, '지속 > 10 s 또는 칸 ≥ 4' 만 출력(칸 × 지속 큰 순). 상자 ② 창(1.05~1.35 × −0.30~+0.10) 첫 · 끝 표시와 마지막 경로 6 개 시각.
- **출력**: [`whatif_f2c2_f2d2.txt`](../debug_log/2026-10-08/outputs/whatif_f2c2_f2d2.txt):
  ```
  중심 map (-0.09, -4.79) · 칸 122 · 지속   198 s(관측 프레임 최대 169) · 벽까지 0.15 m ← 통로(반폭 ≤ 0.5) · 처음 11:08:19
  == 상자 ② 자리 nvblox 칸 첫 표시(복귀 구간) · 경로 발행 시각
    11:14:22 로버 (2.42, -1.45) 상자 ② 칸 2
    경로 발행: 11:13:27 11:13:27 11:14:16 11:14:32 11:14:44 11:14:53
  ```
  그림 [`2026-10-08_nvblox_global_whatif.png`](../04_navigation/figures/2026-10-08_nvblox_global_whatif.png)(번호 = 칸 × 지속 큰 순 15 개).
- **결함**: '벽' 거리는 점유뿐 아니라 **미지 칸까지** 거리(빈 칸만 0 이 아닌 거리 변환). 묶음 중심의 '벽까지' 는 칸마다의 0.15 m 조건과 별개라 0.00 도 나옴. 유령과 실제 물체를 가르지 못함(사용자 확인에 의존). 전역 inflation · 프레임 문제는 모형에 없음. 첫 판은 /map 오처리(§5 작은 실수).

### 9.11 `job934_prep.sh` · `job936_chk.sh` — B 구성 prep · 확인 (10-08 §3.2 · §3.6)
- `job934_prep.sh`: `EXTRA_NAV="global_camera:=nvblox replan_hz:=0.5 mppi_viz:=true"` 로 `job780_prep_navmap.sh`, 뒤에 전역 obstacle 소스 · BT 경로와 `RateController hz` 문자열(`grep -o` 로 활성 BT 사본) · MPPI visualize · 활성 yaml 첫 줄 · **전역 nvblox 프레임**(10 행, f2e1 뒤 추가). 출력 [`j934_prep.txt`](../debug_log/2026-10-08/outputs/j934_prep.txt)(f2e1 전) · [`j934b_prep.txt`](../debug_log/2026-10-08/outputs/j934b_prep.txt)(f2e2 전).
- `job936_chk.sh`(읽기만): MPPI visualize · controller/planner/bt 의 lifecycle 상태 · `/trajectories` 등 토픽 존재. 출력 원천 소실(SUMMARY "controller '?' 는 조회 시간 초과 — 재확인 active").
- **계보**: → `Docs/tools/prep_patrol.sh`(10-12 ~ 순회 기본).

### 9.12 `job937_src.sh` — 층 프레임 파라미터 (10-08 §3.3) ★ 결함을 확정한 도구
- **형태**: Jetson, 인자 없음, 읽기만.
- **하는 일**: `~/ros2_ws/src` 에서 `nav2_costmap_global_frame` 이 나오는 파일 3 개까지 찾아 `nav2_costmap_global_frame\|lookupTransform\|global_frame_` 줄, 그다음 실행 중 `/global_costmap/global_costmap` · `/local_costmap/local_costmap` 의 `nvblox_layer.nav2_costmap_global_frame`.
- **출력**: **원천 소실**(대화에만 — SUMMARY "global_costmap nvblox_layer.nav2_costmap_global_frame = odom"). 층 소스(호스트 `nvblox_nav2` 포크)는 저장소에 없고 변경분만 `Docs/05_nvblox/nvblox_nav2_rover.patch` 에 있다.

### 9.13 `f2e_eval.py` · `f2e_gcm.py` — f2e1 상자 · 재계획 (10-08 §3.3)
- **`f2e_eval.py`**(PC `python f2e_eval.py <bag>`): 슬라이스 0.5 s 마다 거리 ≤ 0.05 m 칸을 map 으로, 창 x 1.0~1.45 · y −0.25~+0.20 을 상자 ② 로. 상자 첫 표시(칸 ≥ 2) 20 s 전부터 경로마다 로버 앞 남은 경로 ↔ 그 시각 최신 상자 칸 최소 거리 · x 0.9~1.6 에서 경로 y. 경로 옆 변화 = 연속 경로 끝점이 0.2 m 안(같은 목표)일 때 새 경로 점마다 옛 경로까지 최소 거리의 최대값 > 0.3 m 횟수.
  - 출력 [`f2e1_box_replan.txt`](../debug_log/2026-10-08/outputs/f2e1_box_replan.txt): `13:36:01 (+177.3 s) 로버 (2.22,-0.59) | 경로 ↔ 상자 ② 칸 최소 0.01 m (칸 28) | 경로가 x 0.9~1.6 에서 지나는 y -0.04~0.10`.
  - 결함: 거리는 슬라이스(제자리) 기준이라 '계획기가 본 상자' 가 아니라 '실제 상자 근사' 와의 거리. 옆 변화는 목표를 끝점으로만 구분.
- **`f2e_gcm.py`**(PC): 13:35:55 · 13:36:05 · :15 · :25 첫 메시지의 전역 · 로컬 코스트맵을 **같은 map 좌표** x 1.0~1.5 × y +0.3 ~ −0.3(0.1 간격)으로 표(§5 실수 ③ 발췌). 출력 [`f2e1_costmaps.txt`](../debug_log/2026-10-08/outputs/f2e1_costmaps.txt).

### 9.14 `contact_eval.py` · `box_align.py` — 접촉 · 정렬 (10-08 §3.5 · §3.7)
- **`contact_eval.py`**(PC, `fz_f2e1.npz` — `extract_pc.py` 산출, 원천 소실): 13:36:05 ~ 13:36:40 로컬 코스트맵마다 99 · 100 칸을 map 으로, 창 x 0.95~1.45 · y −0.30~+0.20 의 치명 · 내접 수, 차체 직사각 **안**의 치명 · 내접 수, 치명 칸 ↔ 외곽 최소 거리, 가장 가까운 `/cmd_vel`.
  - 출력 [`f2e1_contact.txt`](../debug_log/2026-10-08/outputs/f2e1_contact.txt): `13:36:23.7 로버 (1.47,-0.01,+160°) v +0.080 w -0.08 | 상자 자리 치명  2 · 내접 48 | 차체 안 치명 0 · 내접 6 | 상자 치명 칸까지 0.053 m`.
  - 결함: 헤더의 'MPPI 최적 궤적이 상자 칸과 겹치나' 는 코드에 없음(설명만). 창에 상자 ① 북쪽 가장자리가 들어올 수 있음.
- **`box_align.py`**(PC `python box_align.py <npz> 시작 끝`): 2 s 마다 로컬(odom → map) · 전역(map) 치명 칸 중 창 x 0.95~1.45 · y −0.15~+0.25(상자 ① 은 y < −0.25 라 뺌)의 중심 · 수, 남은 경로 ↔ 로컬 상자, 차체 ↔ 로컬 상자.
  - 출력 [`f2e2_box_align.txt`](../debug_log/2026-10-08/outputs/f2e2_box_align.txt): `14:39:56 로버 (1.43,0.23) | 상자 ② 치명 칸: 로컬 12 중심(1.20,-0.04) · 전역 12 중심(1.22,-0.03) | 경로↔로컬 상자 0.23 m | 차체↔로컬 상자 0.06 m`.
  - 결함: 전역 칸 0 인 빈 프레임(14:39:40)을 그대로 씀.
- **지금**: 둘 다 안 씀 — 같은 질문은 이후 `anal_box_pass.py` · `anal_box_layers.py`(10-13).

### 9.15 `extract_pc.py` · `render_rviz.py` · `run_f2c.sh` — 영상 · 러너 래퍼 (10-08 §3.1 · §3.4)
| 도구 | 하는 일 | 지금 |
|---|---|---|
| `extract_pc.py` | PC rosbags 판 추출(`/tf` · `/cmd_vel` · `/plan` · 전역 · 로컬 · `/scan` · `/map` · `/trajectories`) → npz | 원천 소실(npz) |
| `render_rviz.py` | RViz 풍 영상 + 전역 주황 테두리 + MPPI 후보 · 최적 선. 10-08 에 '10-07 고정 시각 기준' 결함을 bag 날짜로 고침 | 이후 `Docs/tools/fig_drive_video.py`(10-23) |
| `run_f2c.sh` | 러너 `run_f0.sh` 래퍼 — 목표 문자열 `B910="2.25,-1.6,p;5.5,-2.2,p;0,0,p"` · `FULLF` 등, `STAGE` · `NOTE` · `GIT_HEAD`, bag 프로필 nvblox | 스크래치패드 경로 의존 |

### 9.16 이 시기에 부른 앞 시기 도구 (본체 해설은 다른 카드)
| 도구 | 이 시기에 한 일 | 해설 |
|---|---|---|
| `job780_prep_navmap.sh` · `job726_prep_map.sh` | prep 본체(`EXTRA_NAV` 덧붙임) | [F2 순회 카드](f2-patrol-loc-jump.md) |
| `job550_f0run.py` | 러너(목표 · yaw 모드 p · f, nav_guard 연동) | 같은 카드 |

## 10. 용어
- **한 격자(obstacle_layer 의 여러 소스)**: Nav2 ObstacleLayer 는 소스들의 표시 · 지우기를 같은 2D 칸에 한다. 라이다 빔이 낮은 상자 위를 지나가면 그 칸을 빈 곳으로 갱신해, 같은 칸에 찍힌 카메라 표시가 지워질 수 있다(높이를 안 봄).
- **C1 · C2 · C3 · C4**: 10-07 §8.3 에서 선언한 낮은 물체 기억 시험 기준 — 가까이 가서 화각 밖이어도 기억(C1), 카메라가 볼 때 치우면 5 s 안 지움(C2), 다시 놓으면 3 s 안 표시(C3), 출발 방 유령 증가 없음(C4).
- **STVL 절두체 소거 · 가속 감쇠**: STVL 은 깊이 카메라 시야(근평면 `min_z` ~ 원평면 `max_z` 의 사각뿔) 안 복셀의 남은 수명을 `decay_acceleration` 으로 빨리 줄여 '보이는데 없는 것' 을 지운다. 시야 밖 복셀은 `voxel_decay` 동안 남는다.
- **`track_unknown_space`**: 층이 '아직 못 본 칸' 을 미지(−1)로 낼지. 최대값 결합(`combination_method: 1`)이면 다른 층의 빈 칸 위에 미지를 덮는다.
- **`nav2_costmap_global_frame`(nvblox 층)**: nvblox 슬라이스를 이 프레임으로 변환해 코스트맵에 그린다. 코스트맵 자신의 `global_frame` 과 같아야 하며, 지정 안 하면 기본 odom.
- **주기 재계획(`replan_hz`)**: BT `RateController` 가 경로 계획 가지를 몇 Hz 로 다시 틱할지. 0.01 = 사실상 목표당 1 회(막힘 · 실패 때만 다시), 0.5 = 2 s 마다.
- **치명 → 내접 강등**: 로컬 코스트맵에서 상자 칸 값이 100(치명)에서 99(내접)로 내려가는 것. CostCritic 은 치명(과 `critical_cost` 넘는 비용)을 충돌로 막고 내접은 벌점만 주므로, 강등되면 MPPI 가 그 칸을 지나는 궤적을 고를 수 있다.
- **카메라만 본 칸(whatif)**: nvblox 장애물 칸 중 저장 지도 벽 0.15 m 밖 · 같은 시각 라이다 점 0.10 m 밖인 칸 — 낮은 실제 물체 또는 유령.
- **B 구성**: 10-08 §3 의 시험 구성 — 전역 nvblox 층(라이다는 별도 obstacle 층) + 재계획 0.5 Hz (+ 그날은 `mppi_viz:=true`). A = 10-07 f2c2 · f2d2 구성.
