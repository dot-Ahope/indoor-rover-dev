# MPPI 로 상자 옆 통로 지나기 — 입구 정체 · 복귀 정지 · 목표 옆 정지를 하나씩 풀어 3/3 (mp1 ~ mp11)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결(이 코스 기준, 3/3)** — 같은 구성 mp9 · mp10 · mp11 SUCCEEDED. 단 '상자 최근접 9.2~19.3 cm' 는 그날 저녁 코스트맵 기준 **1.4~2.2 cm** 로 정정(09-17 §13.4) — 여유 문제는 남음(이후 [상자 옆 정지](../debug_log/2026-10-13/SUMMARY.md)) | 09-15 ~ 09-17 | [09-15 §2 mp1](../debug_log/2026-09-15/SUMMARY.md) | `ros2_ws/src/rover_navigation/config/nav2_params.yaml`(FollowPathMPPI 블록 · `controller_frequency` · 전역 `inflation_radius` · STVL `filter`/`voxel_min_points`/`voxel_decay` · `bt_navigator.default_server_timeout`), `config/nav_to_pose_no_spin.xml`(planner_id · controller_id · SmoothPath · fallback), 펌웨어 정지 문턱(→ [기동 데드밴드](start-deadband.md)) — 커밋 `e63c872b` `3317bf17` `0d548855` `4b3512ff` `a6c25149` `ce2d8f9f` `a5853162` `964a350a` `7eaf0b09` `6facf928` `722e5c32` | 앞: [컨트롤러 선택 RPP vs MPPI](controller-rpp-vs-mppi.md) · [inflation · padding](inflation-padding-roles.md) · [통과 폭 판단 도구](passage-width-analysis.md) · [카메라 깊이 장애물](depth-obstacle-costmap.md) · [stuck_monitor](stuck-monitor.md). 같은 시기: [기동 데드밴드](start-deadband.md)(mp8 의 펌웨어 문턱) · `slam-dds-deadlock.md`(mp7 의 SLAM 정지, 다른 카드) · [CPU · 위치 추정 정지](cpu-load-stalls.md) |

**한 줄**: 09-14 에 RPP 가 상자 뒤 목표에서 '둘레 검사로 멈춤' 을 되풀이하자, 09-15 부터 같은 코스(상자 옆 창 ≈0.23 m 통로 → 상자 뒤 목표)를 MPPI 로 다시 달렸다. 11 번의 주행에서 문제는 네 겹이었다 — ① 계획기 Smac 이 좁은 띠에서 재계획을 거부(mp1) ② 통로 **입구**에서 MPPI 가 굳음(mp2 · mp3 · mp4) ③ 상자 **뒤 복귀 회전**에서 굳음(mp5 · mp6) ④ **목표 옆** 0.24 m 에서 굳음(mp6 · mp8). 입구 정체의 원인을 나는 세 번 잘못 짚었고(지평 0.13 m → '정지가 최저 비용인 구조' → 표본 붕괴), 오프라인 MPPI 재현(job354 · job355)으로 가린 진짜 원인은 **PathFollow 의 당근이 12.5 cm 로 너무 짧아 진행 보상이 거의 없는 것**이었다(→ weight 10 · offset 20). 복귀 · 목표 옆 정지는 목표 자리 기하(벽 · 상자 모서리 가까움)와 경로 크리틱이 목표 0.4~0.6 m 안에서 꺼지는 '크리틱 교대', 그리고 펌웨어가 3~10 mm/s 휠 지령을 버리는 결함이 겹친 것. 사이에 SLAM 정지(mp7)는 주행 로직이 아니라 시스템 문제였다. 같은 구성 3/3 은 얻었지만, 그 '상자 최근접' 수치는 러너의 상자 모델 오류로 부풀려져 있었다.

---

## 1. 증상
- 09-14 bk1(RPP, 상자 뒤 목표 1.8/0): 완주했지만 상자 옆에서 정지 2 회(충돌감지 6, BackUp 실패 1). 사용자 목표 "상자 뒤로 갈 때 머뭇거리지 않고 자연스럽게"(09-14 §2.27) → [09-15 머리말](../debug_log/2026-09-15/SUMMARY.md).
- mp2 사용자 관찰(09-16 §1.1): "상자를 피해서 이제 공간을 통과해야 하는 상황에, 오른쪽으로 꺾어야 하는데, 왼쪽으로 계속 방향을 튼다. 왼쪽에는 책상 다리 같은 장애물이 있기에 통과하지 못하는 모습."
- mp3: 같은 자리에서 굳은 뒤 "진동"(사용자), 그리고 기억 소실 뒤 상자 쪽으로 전진.
- mp4: 부드럽게 들어와 같은 입구에서 서서히 멈춤 — 사용자 질문 "회피 로직과 추종 로직이 충돌하는가, 과한 값인가"(09-16 §1.14).
- mp5 · mp6 · mp8: 통로는 통과하는데 상자 뒤 · 목표 앞에서 v 0.009~0.02 로 수십 초 기어감(정지).

## 2. 흐름 (시간순)
시각 기준이 셋이다: 'goal 후 t'(러너 CSV · `drive_*.txt`), 'bag t'(첫 odom 기준, job327 · job345 · job354 · job355), nav2.log 의 절대 시각. 같은 사건이 표마다 몇 초 어긋나 보이는 것은 이 때문이다(예: mp4 정지는 goal 후 12~18 s = bag t 17~22 s).

| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-15 §1 | Smac 스윕(R 0.10/0.15 × cost 1.2/2.0/3.0, 정지) | 어느 조합도 상자 뒤 복귀를 상자 뒤로 미루지 못함 | 계획기로는 안 풀림 → BT 컨트롤러 RPP → MPPI(커밋 `e63c872b`) | `2026-09-15/jobs/run_ab_bk.sh`(→ 09-14 `job317_plan_ab2.py`), 출력 원문 없음 |
| 09-15 §2 **mp1** | Smac Hybrid + MPPI(20 Hz · 32 step · 0.05 s), 패딩 0.01, 목표 (1.8, 0) | 진입 t 2~20 v 0.04~0.05 · 부호반전 0 · 실여유 최소 **0.20 m**(RPP 주행 0.03~0.10). (0.79, +0.40) 에서 정지, nav2.log `SmacHybrid: failed to create plan` ×15 → 복구 → BackUp 2 → **ABORTED 48 s**. `BT tick rate exceeded` ×3 | 원인 = 계획기: MPPI 가 좌로 치우쳐(+0.40, 기하 중앙 +0.33) 패딩 풋프린트 좌변 +0.575 가 좌측 가구 LETHAL(+0.55) 에 닿아 **Smac 이 시작 자세를 거부**(NavFn 은 시작 셀만 본다 — **추정**, 로그 문구는 '경로 없음' 뿐). MPPI 자체는 '자연스러운 이동' 의 모양 | `2026-09-15/outputs/mp1.csv`(실여유 최소 0.200 @ t 14.9, 횡 최대 +0.405 확인). nav2.log 원문 **원천 소실** |
| 09-15 §3 | BT planner_id → GridBased(NavFn), MPPI 유지(커밋 `3317bf17`). mp2 1 차 시도 | 게이트 통과 직후 Jetson 네트워크 소실(AP deauth) | 주행 여부 미확인 → 러너를 원격 nohup + 로그 폴링으로(`run_drive_nohup.sh`) | [Jetson Wi-Fi](jetson-wifi-link.md) |
| 09-16 §1.2 **mp2** | NavFn + MPPI(32 step) 상자 뒤 (1.80, 0.01), 통과폭 0.235 | bag t 5~17 정상 추종(경로 대비 횡편차 ≤ 2 cm). **t 18~20 경로는 −0.5~−14°(우) 요구, 로버는 제자리 좌회전 +39.5 → +48.5°**. t 27~72 (0.72, +0.42) yaw 44~59° 정체, 진행 실패 2 회 → **TIMEOUT 90 s, 1.23 m**, 접촉 없음 | §1.3 '검증 5 / 추론' 으로 분리: 원인(추론) = 지평 32 × 0.05 s × 0.08 m/s = **0.128 m** 라 PathAlign(offset 20) 이 한 번도 안 켜지고 PathFollow(5) 만 남아 장애물 기울기에 졌다 → **이후 mp3 로 반증**(§5 실수 ①) | `outputs/job327_mp2why.txt` · `job329_plancorner.txt` · `mp2.csv`, `bags/bag_mp2.tgz`(git 제외). 러너 화면 원문(`drive_mp2.txt`) 없음 |
| 09-16 §1.5 | mp3 용 3 손잡이: `time_steps` 32 → **56**, PathAlign `offset_from_furthest` 20 → **3**, PathAngle `max_angle_to_furthest` 1.0 → **0.5 rad** | — | 사전 규칙: "mp3 가 다시 정체하면 RPP 복귀" | 커밋 `0d548855` |
| 09-16 §1.7 | mp3 준비 게이트가 두 번 거부 | 상자 셀 최대 y 0.169 ↔ **0.218**(창 0.235 ↔ 0.187). job331 6/6 0.169 → 곧 3/3 0.218 | 깊이 가장자리 +0.14 인데 코스트맵이 0.20~0.25 셀을 간헐 표시 | `outputs/job331_boxflicker.txt` · `gate_mp3_refused.txt`, `prep_mp3.txt` |
| 09-16 §1.8 | 원인 계측(job312 30 s × 2, job333 40 s + 180 s) | 좌측 띠 점 y +0.18 은 실물(66~72 % 프레임). y ≥ 0.20 점은 **180 s 중 9/2694 프레임(0.3 %)**, 각 1~2 점, 같은 복셀 최대 2 점 — 릴레이 필터(카메라 복셀 ≥ 3 점)는 못 거름. 한 점이 찍히면 decay 60 s 동안 셀이 켜짐 | **STVL `filter: voxel` · `voxel_min_points: 3`**(odom 정렬 0.05 m 복셀). 검증 24 회/160 s **0.164~0.168, 0.22 셀 0 회** | `outputs/j312.txt` · `j333.txt` · `j333b.txt` · `job331_after_voxelfilter.txt`, 커밋 `4b3512ff` |
| 09-16 §1.9 **mp3** | NavFn + MPPI(56 step, offset 3, angle 0.5) + 복셀 필터 | goal 후 26 s (0.70, +0.27) → 29~71 s **(0.741, 0.301) yaw 43~47° 정지 42 s**(mp2 와 같은 자리 · 모양). 루프 20 Hz 미달 **306 건**, load 7.7 → 11.8, EKF 위반 32 → 91. ~71 s 로컬 상자 기억 소멸 → 우회전 전진 → 러너 ① **0.0 cm @ 84.8 s**, ② 계획 여유 **−3.7 cm** → TIMEOUT 90 s | 지평 · 크리틱 변경은 **효과 없음** + CPU 과부하 → 사전 규칙대로 **RPP 복귀**, time_steps 56 → 32(offset 3 · angle 0.5 는 유지). '접촉' 은 러너 상자 모델 값(상자 미관측 79.6 s 외삽) — 사용자 확인 기록 없음(**미확인**) | `outputs/drive_mp3.txt` · `mp3.csv` · `job327_mp3.txt`(job334 집계 포함), `bags/bag_mp3.tgz`, 커밋 `4b3512ff` |
| 09-16 §1.10 | 사용자 지시 "재정의 · 재분석 · 다각도 해결책" | [`PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md`](../04_navigation/PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md) — 문제는 '컨트롤러 A vs B' 가 아니라 **입구 기동 설계(격자 경로가 상자 앞 0.25 m 에 35~50° 꺾임을 남김) + 기억 지속 60 s** | 해결책 A(계획) · B(제어) · C(기억) · D(시스템) · E(실험) 다섯 갈래. 1 순위 권장은 **RPP + A + C**(§5) | 아래 §3.3 |
| 09-16 §1.11 | **사용자 결정: MPPI 유지 · A 진행 · C 검토 · D 위임** | MPPI: `controller_frequency` 20 → **10 Hz**, `model_dt` 0.05 → **0.1**, 32 step → 지평 3.2 s ≈ **0.26 m**(연산량 mp2 의 절반), `visualize: true`, BT → FollowPathMPPI. C: job338 로 bag 3 개 검토 → 왼쪽 통로를 막는 깊이 전용 셀 0 → decay 로컬 **120** · 전역 **180** s. D: 릴레이 `data` setter 병목 수정 CPU 53~60 → 13~20 %, `max_range 4.0` | 권장(RPP)과 다른 결정 — 근거는 MPPI 가 mp1 에서 보인 '정지 없는 부드러운 이동'(문서 §6) | `outputs/j338.txt` · `j338b.txt`, 커밋 `a6c25149` |
| 09-16 §1.12 | A 정지 A/B(job340, 주행 없음) | 0.1 m 창 최대 꺾임: navfn 78.0° · +smooth 76.7° · @inflation 0.70 50.8° · **@0.70 + smooth 16.6°**. 상자셀 최소 0.269 → 0.260(−0.9 cm) | **전역 inflation 0.55 → 0.70 + BT SmoothPath** 채택(둘 다 바꾼 이유: 목표 지표는 결합에서만 나옴) | `outputs/job340_planab.txt`, 커밋 `ce2d8f9f` · [inflation 카드](inflation-padding-roles.md) |
| 09-16 §1.13 **mp4** | NavFn + inflation 0.70 + SmoothPath + MPPI(10 Hz · 32 · decay 120) | goal 후 0~12 s ω 최대 0.15 · 부호반전 0 · 루프 미달 0 로 부드러운 차선 변경. 12~18 s (0.70~0.72, +0.30~0.36) 에서 v 0.038 → 0.006 → **18.0 s stuck_monitor 취소**(지령 1.3 cm/14° vs 관측 0.3 cm/1.4°), 접촉 없음 최근접 17 cm | `/trajectories`(job345): '앞 > 5 cm' 후보 78 → 55 → 32 → 13 → 6 → 2 %, 끝단 거리 중앙 0.105 → 0.011 m → **기제 = 저속 표본 붕괴**(§5 실수 ③) → `vx_std` 0.05 → 0.08, `wz_std` 0.3 → 0.4, `iteration_count` 1 → 2, `temperature` 0.3 → 0.15. BT `{path}` 이중 기록(매초 `Aborting handle`) → `{raw_path}` 분리. stuck_monitor 는 `stuck_shadow:=true` | `outputs/drive_mp4.txt` · `mp4.csv` · `j345_mp4.txt` · `job327_mp4.txt`, 커밋 `a5853162` · [stuck_monitor 카드](stuck-monitor.md) |
| 09-16 §1.14 | 사용자 질문에 답: 크리틱 비용 재구성(job354) + 오프라인 MPPI(job355, bag_mp4 bag t 17 s) | 재현 A(mp4 값) 4 s 전진 0.072 m · 최종 v 0.012(실제의 '기어감'). B(배포한 탐색 4 손잡이) 0.087 m — **부족**. C(follow offset 20) 0.143 · E(align 6) 0.137 · **F(follow w 10 · offset 20) 6 s 0.250 m, yaw 32 → 7°** · L(F + align 6 + rep 0.5) 0.258 | 충돌의 실체 = **'당근이 짧은 추종'**: offset 5 점 × 점간격 0.025 = 12.5 cm 라 진행해도 PathFollow 가 거의 안 줄고, PathAlign · Obstacles 만 이동에 비례해 커져 v ≈ 0.02 평형. 회피 · 정렬 가중은 과하지 않음 → `PathFollowCritic` **5/5 → 10/20** | `outputs/j354_mp4.txt` · `j355_ab.txt` · `j355_cdefgh.txt` · `j355_ijkl.txt`, 커밋 `964a350a` |
| 09-16 §1.15 **mp5** | PathFollow 10/20 | goal 후 0~12 s 입구 (0.77, +0.27) 를 **v 0.04~0.08 로 통과(정지 0)**, 12~24 s 통로 실여유 0.11~0.15. 29~90 s (1.49, +0.26) 상자 뒤에서 정지(v ±0.02), 뒤우 모서리 ↔ 상자 뒤 모서리 **0.07 m** → TIMEOUT 90 s, 2.54 m, 최근접 10.5 cm. 직진 중 ω 부호반전 **36 회(14.16 /m)**(mp4 0) | 입구 해결. 복귀 정지 = **목표 자리 기하**(상자 뒤 0.3 m 중심선) + **크리틱 교대**(목표 0.4 m: PathFollow(문턱 0.6) · PathAlign(0.4) 꺼지고 Goal · GoalAngle 만 — GoalAngle 은 좌회전 요구, 좌회전은 LETHAL). 시뮬(t 29 s, 6 s): 현재 M 0.227 · 문턱 0.2(N) 0.260 · +GoalAngle 끔(O) 0.310 · +goal_w 10(P) 0.305 m | `outputs/drive_mp5.txt` · `mp5.csv` · `job327_mp5.txt` · `j366_mp5_return.txt` |
| 09-17 §1 | (이 카드 범위 밖 — [회피 주행 계측](avoid-run-metrics.md)) 감사 · 러너의 상자 검출이 y 군집에 바닥 잡음을 섞어 전면 1.345 를 0.957 로 | 내 안내로 로버를 12 cm 잘못 옮김 → mp6 은 어제보다 17 cm 뒤 배치, 창 0.287 | 검출을 x 정렬 10 cm 간격 분할로 | `2026-09-17/outputs/j369_370.txt` · `j371.txt` |
| 09-17 §2 **mp6** | 목표만 (2.2, 0) 으로(한 변수, 회전 지점을 상자 뒤에서 멀리) | bag t 27~33 통로 통과(여유 ≈16 cm). 33~39 상자 뒤 모서리에서 우회전 시작 → smoother "Smoothed path leads to a collision" 3 연속 → BT 가 **3 s 묵은 경로** 유지. 40 s 차체 ↔ 상자 뒤-왼쪽 모서리 내 계산 ≈3.6 cm / 러너 0.0 cm. 54~90 s (2.079, +0.219) 에서 **v 0.009 정체**, 목표까지 0.24 m → TIMEOUT 90 s, 2.64 m | 목표 앞 정체 = **목표가 벽 · 문틀 LETHAL 0.367 m 앞**(풋프린트 여유 0.098 m) — **목표 선택 오류(내 실수, SUMMARY 자인)**. 사용자 확인: 접촉 없음(§4) | `outputs/drive_mp6.txt` · `drive_mp6_runner.txt` · `mp6.csv` · `j374_mp6.txt` · `j376_mp6.txt`, `snap_mp6_start.jpg` |
| 09-17 §3 | 조치 3 | BT `Fallback(SmoothPath raw → path, TruncatePath raw → path distance 0)` · 목표 여유 게이트 job377(풋프린트 ↔ 전역 LETHAL ≥ 0.20 m) · 상자 검출 x 분할 | TruncatePath 가 끝 방향을 0 으로 덮는 TODO(improve) 남김(→ 10-14 `CopyPath` 로 해소) | 커밋 `7eaf0b09` |
| 09-17 §5 **mp7** | 목표 (2.0, 0)(게이트: (2.2, 0) 0.145 거부 · **(2.0, 0) 0.249** 통과) | goal 후 11.4 s 루프 미달 → `compute_path` ack 타임아웃(20 ms) ×4 → 클리어 → BackUp(입구에서) … 27.1 s **ABORTED**, 1.72 m, 최근접 8 cm. bag: map→odom 이 +6.8 s 에 5.1 s 공백 등. 주행 뒤 slam_toolbox 가 그래프에서 사라짐 | **주행 로직이 아니라 SLAM 가용성 · 계산 자원**. 조치: `default_server_timeout` 20 → 100 ms, `visualize` → false(bag 에서 `/trajectories` 제외), 주행 중 top 기록, SLAM 생존 게이트 job386. 원인 추적(gdb → Fast DDS 데드락)은 `slam-dds-deadlock.md`(다른 카드) | `outputs/drive_mp7.txt` · `j379_mp7_events.txt` · `j380_health.txt` · `j381_slam.txt` · `j382.txt` · `mp7_*.log`, 커밋 `6facf928` |
| 09-17 §7 **mp8** | 오늘 조치 전부(visualize off · timeout 100 ms · fallback · Fast DDS 2.6.12 · 15W) | **처음으로 BT 타임아웃 0 · 루프 미달 0 · SmoothPath 실패 0 · SLAM 생존**. 기하 최근접 2.6 cm(26.5 s). 38~90 s **(1.960, +0.241) 정지, 목표까지 0.243 m**. `/cmd_vel` 0.009 m/s(20 Hz) 인데 휠 tgt 0 · duty 0 · wheel_odom 0(51 s) | 원인 1 = **펌웨어 문턱 불일치**(승격 0.008 < 정지 문턱 0.010 → 휠 지령 3~10 mm/s 를 버림, [기동 데드밴드](start-deadband.md)). 원인 2 = **크리틱 교대**: 시뮬(펌웨어 모델 포함) S1 0.234(실측 0.243 재현) · S2 펌웨어만 0.232 · S3 문턱 0.2 0.144 · S4 S3+펌웨어 0.140 · **S5 S4+GoalCritic 10 0.116 m** → 경로 크리틱 `threshold_to_consider` **0.2**, `GoalCritic` **5 → 10** | `outputs/drive_mp8.txt` · `j379_mp8_events.txt` · `j394_mp8.txt` · `j395_mp8.txt` · `j396_goalsim8.txt` · `mp8.csv`, 커밋 `722e5c32`(설정) · `de596551`(펌웨어 정지 문턱 10 → 5 mm/s) |
| 09-17 §9 **mp9** | 새 펌웨어 + 문턱 0.2 · GoalCritic 10 | **SUCCEEDED 33.7 s, 2.19 m**, 목표 오차 0.124 m(시뮬 S5 예측 0.116), 러너 최근접 10.3 cm. 25.45~26.0 s `extrapolation into the future` 3 회 → 1~2 s 정지. 휠 tgt 8~9 mm/s 12 샘플(옛 펌웨어면 0) | 상자 뒤 목표 첫 MPPI 성공. 펌웨어 수정의 기여는 분리 못 함(반사실 없음) | `outputs/drive_mp9.txt` · `j379_mp9.txt` · `j404_mp9.txt` · `mp9.csv`, `prep_mp9*.txt` |
| 09-17 §10 **mp10** | 같은 구성 반복 #2 | **SUCCEEDED 33.1 s, 2.21 m**, 오차 0.140 m. 18.6 s `Optimizer fail` 1 회(즉시 재시작). 부호반전 **15.69 /m** | 2/2. 흔들림이 mp9 의 2~4 배 → 탐색 잡음 탓으로 **추정** | `outputs/drive_mp10.txt` · `j379_mp10.txt` · `mp10.csv` |
| 09-17 §11 **mp11** | 반복 #3(재기동 직후 게이트가 사람 자취 셀 7 로 거부 → 재측정 0) | **SUCCEEDED 33.6 s, 2.22 m**, 오차 0.117 m, nav2 로그 두 줄뿐(중단 · 복구 0) | **같은 구성 3/3** | `outputs/drive_mp11.txt` · `j379_mp11.txt` · `mp11.csv` · `snap_mp11_start.jpg` |
| 09-17 §13.4(범위 밖, 정정) | 새 지표 job416(로컬 코스트맵 LETHAL ↔ 차체 외곽) | 상자 최소 여유 mp9 **1.4** · mp10 **2.2** · mp11 **2.2** cm | §11.1 의 '상자 최근접(기하) 9.2~19.3 cm' 는 러너 상자 모델(재고정 · 외삽) 값이라 대표성 없음 — §5 실수 ⑥ | `2026-09-17/outputs/j416_mp12_boxclear.txt` |

## 3. 가설과 판별
### 3.1 mp1 — 왜 ABORTED 인가
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| MPPI 가 상자를 못 피함 | mp1.csv | 실여유 최소 0.200 m, 부호반전 0, 충돌감지 0 | **기각** |
| Smac 이 시작 풋프린트가 LETHAL 에 닿아 재계획 거부 | nav2.log `failed to create plan, no valid path found` ×15, 정지 자세의 좌변 +0.575 vs 가구 셀 +0.55 | 로그 · 기하 일치 | **지지(추정)** — 로그 문구는 '경로 없음' 이고 '시작 충돌' 을 직접 말하지 않는다. Smac 소스로 확인한 기록 없음 |
| BT tick 초과 = MPPI 1000 × 32 @ 20 Hz CPU 부하 | — | 경고 3 회만 | **미확인**(계측 없음). mp3 에서 56 step 이 실제 과부하를 냄 |

### 3.2 입구 정체(mp2 · mp3 · mp4) — 원인을 세 번 바꿈
| 가설(제기한 곳) | 판별 | 결과 | 판정 |
|---|---|---|---|
| SLAM · 오도 오차로 경로를 놓침(§1.4) | 정체 전 경로 대비 횡편차 | ≤ 3.5 cm | **기각** |
| 상자 기억 소실(§1.4) | 정체 시작 t 27 vs 상자 셀 소멸 t 70 | 정체가 먼저 | **기각**(mp3 의 접촉에는 관여) |
| 모든 샘플 충돌(§1.4) | `Optimizer fail` 없음, job327 ±40° 0.15 m 전진에 LETHAL 없음 | — | **기각** |
| 계획기가 잘못된 통로 선택(§1.4) | 경로 y +0.44 = 창 중앙, 좌우 전환 0 | — | **기각** |
| A. 지평 0.13 m 라 경로 크리틱(PathAlign offset 20)이 안 켜짐(§1.3) | 3 손잡이(56 step · offset 3 · angle 0.5)로 mp3 | **같은 자리 · 자세 · 시간에 정체**(0.741, 0.301) yaw 43~47° 42 s | **기각(이 정체의 원인으로서는)** — §1.3 의 '추론' 칸이 그대로 반증됨. offset 3 은 지금도 남아 있다 |
| B. '정지 빼면 모든 출구가 내접 셀 → 정지가 최저 비용' 인 구조(PASSAGE §2.4 (iii)) | job355 G(D + repulsion 0.5) · L(F + align 6 + rep 0.5) | 반발을 1/3 로 줄여도 F 와 같은 결과(0.250 vs 0.258) | **기각** — 반발이 원인이면 줄일 때 풀려야 한다. 또 job354 표에서 '정지' 는 **정상 주행 중(bag t 10 · 14 s)에도 최저**였다(0.59 · 0.66) — 정체 시점을 가리는 지표가 아니다 |
| C. 저속 표본 붕괴(§1.13) | job355 A → B(네 손잡이) | 4 s 전진 0.072 → 0.087 m, 6 s 0.079 m(bag t 20) | **원인 아님(결과로 봄)** — 붕괴는 평균이 0 근처로 내려간 결과이며, 탐색만 넓혀서는 안 풀림. 네 손잡이는 지금도 설정에 남아 있다(§4) |
| D. PathFollow 당근이 짧아 가속기가 약함(§1.14) | job355 C(offset 20) 0.143 · F(w 10 · offset 20) **0.250** · K(offset 30) 0.245 · H(A 값 + offset 20) 0.094 | F 에서 6 s 0.25 m · 경로 정렬, 같은 F 가 bag t 12 · 20 에서도 0.273 · 0.237 | **지지(시뮬)** → mp5 실주행에서 입구 정지 0 으로 **확인** |
| PathAngle 이 큰 오차를 회전으로 풀 것(§1.5) | job355 I(angle_max 0.3) · J(+ w 4) | F 와 소수점까지 같음 — 목표점이 0.1~0.25 m 앞이라 각이 문턱 미만, 비활성 | **기각** |

### 3.3 PASSAGE 문서(09-16)의 해결책 갈래와 실제로 한 것
| # | 방안 | 실행 | 결과 |
|---|---|---|---|
| A1 · A2 | SmoothPath 연결 · 전역 inflation 0.70 | job340 정지 A/B → 둘 다 | 꺾임 78 → 16.6°, mp4 에서 입구까지 부드러움. 입구 정체 자체는 그대로(mp4) |
| A3 · A4 · A5 | Smac + 복구 · Theta* · 재계획 0.2 Hz | 안 함(Theta* 는 설치 확인 `job337_pkgs2.sh` 만) | 이후 10-12 `replan_hz:=0.5`, 10-26 Smac + NavFn fallback(CLAUDE.md §6) |
| B1 | RPP 유지 + 경로 수정 | **사용자 결정으로 안 함(MPPI 유지)** | — |
| B3 | MPPI 재도전 조건(CPU 벤치 · 반발 완화 · PathAngle ↑ · 재계획 억제) | 10 Hz · model_dt 0.1 로 CPU 해결. 나머지는 job354/355 로 기각 · 대체 | — |
| C1 | decay 60/90 → 120/180 | job338 검토 뒤 적용 | 이후 nvblox 로 교체(Phase N) |
| C3 | 라이다 높이를 0.13 m 이하로 | 안 함 | 출발점 낮은 상자는 이후 '라이다 아래 물체' 시험 물체로 유지 |
| D1 | 릴레이 CPU | `data` setter 수정 53~60 → 13~20 % | — |
| E1 · E2 | 지표 고정 · n = 3 | mp9~mp11 에서 n = 3 | 지표 '상자 최근접' 은 이후 정정(§5 실수 ⑥) |
| E4 | 회전 지점을 장애물에서 ≥ 0.3~0.4 m | mp6 목표 (2.2, 0) | 회전은 여전히 모서리 옆 — 경로가 목표 쪽으로 상자 뒷면 바로 뒤에서 꺾임 |

### 3.4 복귀 정지 · 목표 옆 정지(mp5 · mp6 · mp8)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 목표 자리 기하(상자 뒤 0.3 m · 벽 0.367 m 앞) | mp6 목표 이동, job376 · job377 | mp5 의 '상자 뒤 즉시 정지' 사라짐, mp6 은 벽 앞 정체 | **지지** → 목표 여유 게이트 |
| 목표 근처 크리틱 교대 | job366(mp5 t 29) · job396(mp8 t 33) 시뮬 | 문턱 0.2 로 진행 0.227 → 0.260 m(mp5), 거리 0.234 → 0.144 m(mp8) | **지지(시뮬)** → mp9~11 실주행 3/3 |
| 펌웨어가 저속 휠 지령을 버림 | bag `/rover/status`(job395), 코드 | 0.009 m/s 명령에 양 휠 tgt 0 · duty 0 · 51 s | **확정**(코드 · 실측 일치). 시뮬 S2(펌웨어만 수정)는 0.232 m 로 단독 효과 거의 없음 — **보조 원인**(멈춘 상태를 영원히 만든 것) |
| 스무딩 실패 때 묵은 경로를 따름(mp6) | nav2.log 3 연속 + 위치 | 3 s 묵은 경로 | **지지** → fallback(새 원경로). mp9 에서 같은 실패 3 회가 났지만 묵은 경로는 따르지 않음 |

### 3.5 mp9 · mp10 의 짧은 중단
| 가설 | 판별 | 판정 |
|---|---|---|
| mp9 TF `extrapolation into the future` — 경로 헤더 stamp 와 map→odom 시각 차 | 스무딩 실패 3 회 직후라는 시간 일치만 | **미확인**(이후 10-07 에 MPPI `transform_tolerance` 0.2 → 0.5 로 같은 계열을 다룸 — 현재 `nav2_params.yaml` 주석) |
| mp10 `Optimizer fail` | 로그 1 줄 | **미확인**(09-17 §13.4 '여유가 한 셀 수준이라 가장자리 셀이 나타나면 전 후보 충돌' 은 가능성 — 미검증) |

## 4. 조치와 효과
### 4.1 파라미터 · 구성 이력(이 카드 기간)
| 시점 · 커밋 | 바꾼 것 | 전 → 후 | 근거 | 효과(측정) |
|---|---|---|---|---|
| 09-15 `e63c872b` | BT controller | FollowPath(RPP) → **FollowPathMPPI** | bk1 정지 · Smac 스윕 실패 | mp1 부드러움 · 여유 0.20 m |
| 09-15 `3317bf17` | BT planner_id | SmacHybrid → **GridBased(NavFn)** | mp1 재계획 거부 | mp2 부터 계획 실패 없음 |
| 09-16 `0d548855` → `4b3512ff` | `time_steps` | 32 → 56 → **32** | 지평 → CPU 초과 | 정체 불변 · 루프 미달 306 |
| 09-16 `0d548855` | PathAlign `offset_from_furthest` | 20 → **3** | 지평 0.22 m / 점간격 0.04 | 단독 효과 미확인(지금도 3) |
| 09-16 `0d548855` | PathAngle `max_angle_to_furthest` | 1.0 → **0.5 rad** | 29° 부터 회전 유도 | job355 I · J 로 효과 없음 확인(지금도 0.5) |
| 09-16 `4b3512ff` | STVL 로컬 · 전역 `filter` / `voxel_min_points` | passthrough / 0 → **voxel / 3** | 가장자리 셀 깜빡임 | 160 s 0 회 |
| 09-16 `4b3512ff` → `a6c25149` | BT controller | MPPI → RPP → **MPPI** | mp3 사전 규칙 → 사용자 결정 | — |
| 09-16 `a6c25149` | `controller_frequency` · `model_dt` | 20 Hz · 0.05 → **10 Hz · 0.1** | CPU 안에서 지평 0.26 m | mp4 루프 미달 0 |
| 09-16 `a6c25149` | STVL `voxel_decay` | 로컬 60 → **120**, 전역 90 → **180** | 기억 > 머뭇거림(job338) | mp4~ 기억 소실 0(러너 ③ 99) |
| 09-16 `ce2d8f9f` | 전역 `inflation_radius` · BT | 0.55 → **0.70**, **SmoothPath** 연결 | job340 | 꺾임 78 → 16.6° |
| 09-16 `a5853162` | `vx_std` · `wz_std` · `iteration_count` · `temperature` | 0.05 · 0.3 · 1 · 0.3 → **0.08 · 0.4 · 2 · 0.15** | 표본 붕괴(§5 실수 ③) | 시뮬 B: 단독으로는 부족. mp5 부호반전 0 → 14 /m 의 원인 후보(**추정**) |
| 09-16 `a5853162` | BT | `{path}` 이중 기록 → `{raw_path}` → SmoothPath → `{path}` | `Aborting handle` 매초 | mp4 로그 17 건 → 고침(뒤 주행의 건수는 기록 없음) |
| 09-16 `964a350a` | PathFollow `cost_weight` · `offset_from_furthest` | 5 · 5 → **10 · 20** | job355 F | mp5 입구 정지 0 |
| 09-17 `7eaf0b09` | BT SmoothPath 실패 처리 | ForceSuccess(직전 경로 유지) → **Fallback(TruncatePath 로 새 원경로 복사)** | mp6 묵은 경로 | mp9 실패 3 회에도 새 경로 |
| 09-17 `6facf928` | `bt_navigator.default_server_timeout` · `visualize` | 20 ms · true → **100 ms · false** | mp7 ack 타임아웃 · CPU | mp8 BT 타임아웃 0 |
| 09-17 `722e5c32` | 경로 크리틱 `threshold_to_consider`(Follow · Align · Angle) · `GoalCritic.cost_weight` | 0.6 · 0.4 · 0.4 · 5 → **0.2 · 0.2 · 0.2 · 10** | job396 S5 | mp9~11 목표 오차 0.117~0.140 |
| 09-17 `de596551` | 펌웨어 정지 · 스톨 문턱 | 10 → **5 mm/s**(EPS 3 < STOP 5 ≤ MIN 8 `#error` 검사) | mp8 | mp9 휠 tgt 8~9 mm/s 12 샘플 실행 |
| 게이트(러너) | 목표 여유 job377 ≥ 0.20 m · SLAM 생존 job386 · 상자 x 분할 | — | mp6 · mp7 · 09-17 §1 | mp7 목표 (2.2, 0) 거부 |

### 4.2 3/3 성공 구성과 지금(2026-10-30 저장소)의 비교
| 항목 | mp9~mp11(09-17) | 지금 `nav2_params.yaml` · BT | 바뀐 곳 |
|---|---|---|---|
| 컨트롤러 · 주기 | MPPI 10 Hz, 32 × 0.1 s, batch 1000, iteration 2 | 같음 | — |
| 탐색 | vx_std 0.08 · wz_std 0.4 · temperature 0.15 | 같음 | temperature 는 09-17 §12 에서 0.3 → §14 에서 0.15 로 되돌림 |
| 장애물 크리틱 | ObstaclesCritic(rep 1.5 · crit 20, consider_footprint) | **CostCritic**(09-21 채택) | 09-18 §16 — ObstaclesCritic 이 거리 역산 파라미터를 기본 10/0.55 로 쓰고 있었음 |
| PathAlign | 14, offset 3, 문턱 0.2 | **28**, offset 3, 문턱 0.2 | 10-26 |
| PathFollow | 10, offset 20, 문턱 0.2 | **5**, offset 20, 문턱 0.2 | 10-26 |
| PathAngle | 2, max_angle 0.5, 문턱 0.2 | 같음 | — |
| GoalCritic / GoalAngle | 10 / 3 (0.4) | 같음 | — |
| PreferForward | 5 | **15** | 10-08 · 10-12 |
| 전역 inflation | 0.70 / 2.0 | 같음 | 10-13 3.0 시도 뒤 2.0 복귀 |
| 깊이 층 | STVL voxel 필터 · decay 120/180 | nvblox(Phase N, STVL 블록은 대조군으로 보존) | 09-21~23 |
| BT 스무딩 fallback | TruncatePath | 우리 노드 **CopyPath** | 10-14 |
| `default_server_timeout` | 100 ms | 같음 | — |
| 계획기 | NavFn | NavFn 기본, `planner:=smac` 이면 Smac → 실패 시 NavFn | 10-26 · 10-27(mp1 의 'Smac 거부' 를 fallback 으로 받는 구조) |

## 5. 내 실수
### 실수 ① mp2 정체를 '지평 0.13 m 라 경로 크리틱이 안 켜짐' 으로 단정하고 로버로 바로 시험 (09-16 §1.3 · §1.5 → §1.9)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | mp2 입구 정체의 원인을 찾아 mp3 에서 고치기 |
| 본 것 | job327: bag t 18~20 경로는 오른쪽, 로버는 제자리 좌회전. 코스트맵 기울기는 왼쪽(앞-좌 89/96, 앞-우 99). `Optimizer fail` 없음. 재계획된 직진 경로에서도 안 돎 |
| 처음 추론 | Humble 소스 의미론으로: 지평 1.6 s × 0.08 = 0.128 m → furthest index ≤ 5 → PathAlign(offset 20) 이 **한 번도 안 켜짐**, PathAngle(57°) 간헐 → 남은 힘은 PathFollow(5) 뿐이라 장애물 기울기에 짐. SUMMARY 는 이것을 '추론' 칸에 적었지만 조치는 이 가설 하나의 세 손잡이(56 step · offset 3 · angle 0.5)였다 |
| 의심한 이유 | mp3 가 **같은 자리 · 자세 · 시간**에 정체(§1.9) |
| 판별 | job354 · job355 로 bag 장면에서 크리틱을 재구성 · 재현: 56 step 이 아니어도 PathAlign 은 offset 3 이면 켜지고, 켜져도 '브레이크' 로 작동했다. 진행을 바꾼 것은 PathFollow 의 당근 거리(F) |
| 결론 | '경로 크리틱이 안 켜짐' 은 정체의 원인이 아니었다. 대가: mp3 한 번(CPU 과부하 · 기억 소실 · 러너 ① 0 cm). offset 3 · angle 0.5 는 근거가 무너진 채 지금 설정에 남아 있다(angle 0.5 는 job355 I · J 에서 효과 없음, offset 3 의 단독 효과는 미확인) |
| 다음에 알아보는 법 | 내부값을 못 본(`visualize: false`) 상태에서 소스 의미론으로 세운 원인은 **로버로 고치기 전에 오프라인 재현으로 판별**한다 — 이 카드에서 그 도구가 job355 였다. '추론' 칸에 둔 것으로 조치를 정하면, 다음 주행은 원인 판별이 아니라 손잡이 시험이 된다 |
| 데이터 | `2026-09-16/outputs/job327_mp2why.txt` · `job327_mp3.txt` · `drive_mp3.txt` · `j355_*.txt`, 도구 `jobs/job327_mp2why.py` · `job355_mppi_sim.py` |

### 실수 ② '정지가 최저 비용인 구조라 지평을 늘려도 같다(mp3 로 확인)' (PASSAGE §2.4 (iii) · §0)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 사용자 지시로 문제 재정의(PASSAGE 문서) |
| 본 것 | mp2 · mp3 정체 자세에서 job327 실현가능성: ±40° 어느 쪽으로 0.15 m 가도 내접(99) 셀을 스침 |
| 처음 추론 | ObstaclesCritic 은 내접 셀을 지나는 모든 궤적에 최대 반발 → 정지가 최저 → MPPI 는 구조적으로 정지. '지평을 늘려도 같다' 를 mp3 로 확인했다고 적음 |
| 의심한 이유 | mp3 가 바꾼 것은 지평 · PathAlign · PathAngle 이지 반발이 아니다 — mp3 는 반발 구조를 시험하지 않았다. 사용자 질문 "과한 값인가" |
| 판별 | job355 G · L: 반발 1.5 → 0.5 로 결과 거의 불변(F 0.250 vs L 0.258). job354 표: '정지' 는 정체가 없던 bag t 10 · 14 s 에도 최저(0.59 · 0.66) |
| 결론 | 반발은 정체의 원인이 아니었다(문서 §7 에서 '가중은 과하지 않다' 로 바뀜). 문서 §0 · §2.4 의 문장은 고치지 않은 채 남아 있다. 또 재구성은 ObstaclesCritic 의 거리 역산을 로컬 코스트맵 값 2.5/0.40 로 했는데, 실제 컨트롤러는 크리틱 자기 파라미터 **기본 10/0.55** 로 돌고 있었다(09-18 §16, job451 실행 중 값) — 반발 크기의 절대값은 재구성과 달랐다. '반발이 원인 아님' 은 반발을 1/3 로 줄인 상대 비교라 그대로 성립한다고 본다(**추정**) |
| 다음에 알아보는 법 | '최저 비용 후보' 가 정체 시점과 정상 시점에서 같다면 그 지표로 정체를 설명할 수 없다 — 정상 구간을 대조군으로 같은 표에 넣는다. 재구성에 쓰는 상수는 **실행 중 파라미터 스냅샷**에서 읽는다(코스트맵 값이 아니라 크리틱이 실제 읽는 값) |
| 데이터 | [`PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md`](../04_navigation/PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md) §0 · §2.4 · §7, `2026-09-16/outputs/j354_mp4.txt` · `j355_cdefgh.txt` · `j355_ijkl.txt`, [09-18 §16](../debug_log/2026-09-18/SUMMARY.md) |

### 실수 ③ mp4 의 '표본 붕괴' 를 정체 기제로 보고 탐색 손잡이 넷을 한 번에 배포 (09-16 §1.13)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | mp4 입구 정체를 `/trajectories` 로 직접 보고 고치기 |
| 본 것 | job345: 명령 평균이 0 으로 내려가자 '앞 > 5 cm' 후보 78 % → 2 %, 끝단 거리 중앙 0.105 → 0.011 m. 잡음이 스텝마다 독립이라 끝단 산포 ≈ std/√32 × 3.2 s ≈ 3 cm |
| 처음 추론 | 정체의 기제 = 저속 탐색 부족 → `vx_std` 0.08 · `wz_std` 0.4 · `iteration_count` 2 · `temperature` 0.15('가설 하나의 네 손잡이') |
| 의심한 이유 | 같은 날 저녁 사용자 질문 → 크리틱별로 나눠 보니 후보 분포는 평균을 따라 줄어든 것일 뿐, 평균이 왜 0 으로 가는지는 설명하지 않는다 |
| 판별 | job355 A(mp4 값) vs B(네 손잡이): 4 s 전진 0.072 → 0.087 m — '탐색 확대만으론 부족'. 진행을 바꾼 것은 F(PathFollow) |
| 결론 | 표본 붕괴는 정체의 결과(평균 제어가 0 근처면 분포도 0 근처)였다. 네 손잡이는 되돌리지 않고 mp5 에 함께 들어갔고, mp5 의 직진 중 부호반전 0 → 36 회(14 /m)의 원인 후보가 됐다(SUMMARY §1.15 · §2-3). temperature 0.15 는 09-17 §12 에서 흔들림 원인으로 지목돼 0.3 으로 갔다가 실주행에서 차이가 없어 §14 에서 0.15 로 복귀 — `nav2_params.yaml` 주석이 '단독 효과는 검증되지 않았다' 고 적고 있다. 네 값은 **지금도 그대로**다 |
| 다음에 알아보는 법 | '분포가 줄었다' 는 원인과 결과 어느 쪽에도 맞는다. 손잡이를 넣기 전에 **평균을 움직이는 항**(크리틱별 비용 차)을 먼저 나눈다. 한 가설에 손잡이를 여럿 넣으면, 그 가설이 틀렸을 때 남은 손잡이가 다른 증상의 원인으로 남는다 |
| 데이터 | `2026-09-16/outputs/j345_mp4.txt` · `j355_ab.txt` · `drive_mp5.txt`, 커밋 `a5853162`, `nav2_params.yaml` `temperature` 주석 |

### 실수 ④ mp6 목표를 벽 0.367 m 앞에 둠 (09-17 §2, SUMMARY 자인)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 회전 지점을 상자에서 멀리 두려고 목표만 (2.2, 0) 으로(한 변수) |
| 본 것 | 54~90 s 목표 0.24 m 앞에서 v 0.009 정체. job376: 목표 ↔ 최근접 LETHAL 0.367 m(벽 · 문틀 x ≈ 2.55), 목표 풋프린트 여유 0.098 m(job377) |
| 처음 추론 | (주행 전) 게이트가 통로 창 · 상자 위치를 통과시켰으니 목표도 괜찮다 |
| 의심한 이유 | 목표 앞 정체의 자리가 상자와 무관한 벽 앞 |
| 판별 | 전역 코스트맵에서 목표 자세 풋프린트 ↔ LETHAL 거리 |
| 결론 | 게이트가 통로만 보고 목표 자리를 안 봤다 → job377 게이트(≥ 0.20 m). 단 mp6 정체에는 펌웨어 문턱(0.009 m/s 무시)도 겹쳐 있었다(09-17 §7.1 'mp6 의 0.009 m/s 정지도 같은 기제') — '목표 선택 오류' 하나로만 설명한 §2 의 결론은 절반이다 |
| 다음에 알아보는 법 | 목표를 옮길 때마다 목표 자리 여유를 같은 게이트로 잰다(지금은 `place_server` 의 '목표 여유 검사', CLAUDE.md §6 F2.5) |
| 데이터 | `2026-09-17/outputs/j376_mp6.txt` · `drive_mp6.txt`, 도구 `jobs/job377_goalclear.py` |

### 실수 ⑤ mp5 복귀 정지 크리틱 재구성에 mp4 상수를 그대로 씀 (09-16 §1.15, 이 카드 작성 중 발견)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | mp5 상자 뒤 정지(bag t 29 s)의 크리틱 구조를 job354 로 보기 |
| 본 것 | `j366_mp5_return.txt` 의 job354 표: 정지 0.96 최저, 좌회전 · 제자리 우회전 −0.38 LETHAL, 전진 · 완만한 우호 1.46~1.91(Align 0.42~0.94, Follow 0.72~0.89) |
| 처음 추론 | SUMMARY: "목표까지 0.40 m 라 PathFollow(문턱 0.6) · PathAlign(0.4) 은 꺼지고 GoalCritic · GoalAngle 만 남는 교대 구간" |
| 의심한 이유 | 같은 표에 Align · Follow 가 0 이 아닌 값으로 찍혀 있다 — '꺼졌다' 와 모순 |
| 판별 | `job354_critics.py` 상수: `FOLLOW_W, FOLLOW_OFF = 5.0, 5`(mp4 값, mp5 배포값은 10/20), 문턱 · Goal · GoalAngle 처리 **없음**(인자로 바꿀 수 없음) |
| 결론 | §1.15 의 재구성 표는 mp5 의 실제 크리틱이 아니다(당근 · 문턱 · 목표 크리틱이 다름). '좌회전 LETHAL · 제자리 우회전 25 스텝 LETHAL' 같은 **충돌 판정은 크리틱 가중과 무관해 유효**하고, 크리틱 교대 결론은 job355(문턱 · 목표 크리틱 구현, `follow_w=10 follow_off=20`) 시뮬로 따로 뒷받침된다. 표의 비용 크기 비교만 무효 |
| 다음에 알아보는 법 | 재구성 · 시뮬 도구의 상수는 **주행마다 실행 중 파라미터에서** 읽거나 인자로 받게 하고, 출력 머리에 쓴 값을 찍는다(job355 는 머리 줄에 찍지만 job354 는 안 찍는다) |
| 데이터 | `2026-09-16/outputs/j366_mp5_return.txt`, 도구 `jobs/job354_critics.py` L24~33 · `job366_mp5sim.sh` |

### 실수 ⑥ '상자 최근접(기하)' 로 여유를 보고 (09-17 §2 · §9~§11 → §13.4 정정)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 각 주행의 상자 여유를 러너 ①(`clear_geo`)로 기록 · 비교 |
| 본 것 | mp6 0.0 cm, mp8 2.6, mp9 10.3, mp10 19.3, mp11 9.2 cm. mp6 은 내 풋프린트 계산 ≈3.6 cm 와 달랐다 |
| 처음 추론 | §2: "러너(패딩 포함 다각형) 0.0 cm" — 패딩 차이로 설명. §11.1: 3/3 '최소 9.2 cm' |
| 의심한 이유 | (09-17 §13 mp12) 러너 ① 0.0 cm 인데 같은 시각 코스트맵 상자 셀은 그보다 멀리 있었다 |
| 판별 | job416: bag 로컬 코스트맵 LETHAL 셀 ↔ 차체 외곽(0.25 × 0.165) − 반셀 → mp9 1.4 · mp10 2.2 · mp11 2.2 cm. 러너 코드: `clear_geo` 는 **패딩 제외**(HL 0.25 · HW 0.165)이고, 상자 사각형은 0.5 s 마다 깊이 검출로 **재고정**, 안 보이면 마지막 모델을 외삽(⑥ 상자 미관측 최대 31~86 s) |
| 결론 | §2 의 '패딩 포함 다각형' 설명은 코드와 다르다(패딩 제외). 러너 ① 은 상자 모델에 따라 0 으로도, 19 cm 로도 나오는 값이라 주행 간 비교 지표가 못 된다. 컨트롤러 기준 여유는 3/3 모두 한 셀 수준(1.4~2.2 cm) — '여유 9.2 cm' 로 정리한 PASSAGE §9 와 §11.1 은 과장이었다 |
| 다음에 알아보는 법 | 여유는 **컨트롤러가 보는 격자**(그 격자의 `header.frame_id` 기준)로 잰다. 러너 표가 실측 계산과 다르면 설명을 쓰기 전에 그 지표의 코드를 연다 |
| 데이터 | `2026-09-17/outputs/drive_mp6.txt` ~ `drive_mp11.txt` · `j416_mp12_boxclear.txt`, 도구 `2026-09-17/jobs/job125_avoid3.py` L28 · L212~219 · `job416_boxclear.py`, [09-17 §13.4](../debug_log/2026-09-17/SUMMARY.md) |

### 참고: 같은 기간 다른 카드의 실수
- 09-16 §1.6 정지 요청에 전체 종료 스크립트 실행 — 다른 카드에서 다룸.
- 09-17 §1 상자 위치 오측정으로 로버를 잘못 옮김 → [회피 주행 계측](avoid-run-metrics.md).
- 09-17 §6.2 전력 모드 25W 판단 오류 → `slam-dds-deadlock.md`(다른 카드).
- mp4 stuck_monitor 의 '갇힘' 오판(데드밴드 아래 떨림 명령) → [stuck_monitor](stuck-monitor.md).

## 6. SUMMARY ↔ 원문 대조에서 드러난 것 (이 카드 작성 중)
- **09-15 §2 mp1 '계획 여유'**: SUMMARY 는 실여유 0.20 m 만 적었지만 `mp1.csv` 의 `plan_clear`(러너 ②)는 482 행 중 **248 행이 음수**(t 10.4 s ~ 끝, 최소 −5.3 cm @ 28.5 s). 러너 상자 모델(재고정 · 외삽, 그 시각 `box_age` 19.5 s) 기준이라 실제 계획이 상자를 지났다는 뜻은 아닐 수 있다(실수 ⑥ 과 같은 모델) — **미확인**.
- **09-16 §1.3 점간격 '0.026~0.047 m'** 은 mp2 의 NavFn `/plan`(job329 머리 줄: 0.047 · 0.049 · 0.026 · 0.035), §1.14 의 '0.025 m' 는 mp4 의 `/transformed_global_plan`(job355 머리 줄 '간격 0.025'). §1.5 의 'offset 3 → 0.1 m 만 나아가도 켜진다' 는 0.04 기준이고, 컨트롤러가 실제로 본 경로(0.025)로는 7.5 cm.
- **09-16 §1.9 '제어 루프 20 Hz 미달 … goal 후 6~95 s 사이 306 건'**: `job334_rate.sh` 의 기준 시각 `LOGT=1789525870` 은 bag T0(1789525870.37)이지 goal 이 아니다(출력 줄의 '(goal 후 …)' 라벨이 잘못). 같은 출력의 진행 실패 53.4 · 78.4 s 를 SUMMARY 는 47.3 · 72.3 s(goal 기준)로 옮겨 적었다 — 둘의 차 6.1 s 가 목표 수신 시각.
- **09-16 §1.7 job331**: 출력 앞 6 줄(0.169 × 6, 11:03:36~11:04:12)은 맞지만, 뒤의 '상자 주변 셀 값 표' 는 heredoc 안 `'\x'` 때문에 **SyntaxError 로 실행되지 않았다**(`job331_boxflicker.txt`). SUMMARY 는 이 실패를 적지 않았다 — 셀 값 표 대신 job312 · job333 으로 판별했다.
- **창 공식의 0.195**: 게이트(`run_inf1.sh` · `run_drive_nohup.sh` · `run_gate.sh`)의 창 = 좌측 경계 − (상자 셀 최대 y + **0.195**). 0.195 는 09-14 §2.16 당시 패딩 0.03 의 내접반경이고, 09-14 §2.23 에서 패딩 0.01(내접 0.175)로 바뀐 뒤에도 그대로다 → 이 카드의 '창 0.23 m' 들은 상자 쪽에서 **2 cm 보수적**(코드 기준 계산, 의도였는지 기록 없음 — **미확인**). 통로 폭 도구 계보는 [통과 폭 카드](passage-width-analysis.md).
- **09-16 §1.12 표 '최대 진행방향 +64°(사선) / −119°(복귀)'**: `job340` 이 찍는 '최대 진행방향' 은 절댓값 최대 하나(−118.6°)뿐이고, +64° · +37° 는 같은 출력의 '헤딩 프로파일' 줄에서 읽은 값이다(내용은 일치).
- **09-16 §1.14 시뮬 표** 는 `j355_*.txt` 와 일치. 표에 없는 변형: D(follow offset 20 + align 6) 0.135 m, G(D + rep 0.5) 0.178 m, H(mp4 값 + follow offset 20) 0.094 m. G 는 D 보다 4 cm 더 갔다 — '반으로 줄여도 결과 동일' 은 F 계열(F vs L)에만 해당.
- **09-16 §1.15 크리틱 재구성** 은 mp4 상수로 계산됨(§5 실수 ⑤).
- **09-17 §2 mp6 '조향 부호반전 14 회(5.6/m; mp5 14/m)'**: mp5 는 36 회 = 14.16 /m(`drive_mp5.txt`). 횟수와 /m 를 섞어 비교한 문장. mp6 의 /m 는 목표 부근 461 샘플을 뺀 주행 구간 2.52 m 기준.
- **09-17 §2 '러너(패딩 포함 다각형)'** — 코드는 패딩 제외(실수 ⑥).
- **09-17 §5 '5 s 동안 map→odom 최대 간격 < 0.5 s · stamp 지연 < 0.5 s'**: `job386_slamalive.py` 의 판정은 간격 < 0.5 s · **지연 < 1.0 s**(코드 주석: job393 에서 정상 지연이 −0.08~+0.55 s 로 흔들려 1.0 으로 올림, §6). §10 의 '지연 1.12 s FAIL' 은 코드 문턱과 맞다.
- **09-17 §7.2 'S1 0.234 m (1.961, 0.191) — 실측 0.243 (1.960, 0.241) 재현'**: 시뮬 좌표는 odom, 실측은 러너의 출발 프레임 — y 가 5 cm 다르고 일치한 것은 목표까지 거리다. 또 시뮬은 09-17 §14.1 에서 실제 Humble 1.1.20 과 네 가지(고정 잡음 · 후보 clip · 롤아웃 첫 속도 · SG 필터 출력)가 달랐다고 확인됨 — §1.14 · §7.2 의 정량 예측은 신뢰도를 낮춰 본다(SUMMARY 자인). 채택값은 실주행(mp5 · mp9~11)으로 따로 확인됐다.
- **09-17 §2 의 job375**(`job375_goalsim.sh`, mp6 bag t 52 s 에서 G1~G4: 현재 · 문턱 0.2 · goal_w 10 · 둘 다)는 커밋에 있지만 **출력이 없고 SUMMARY 에도 결과가 없다** — mp8 의 job396(S1~S5)이 같은 질문을 다시 했다(원천 소실).
- **PASSAGE §1 mp3 '0 cm(접촉 추정, 사용자 확인 대기)'** vs 09-16 §1.9 제목 '상자 접촉(기하 0 cm)': 사용자 확인 기록은 어디에도 없다(mp6 은 09-17 §4 에서 '접촉 없음' 확인).
- **PASSAGE §9 '상자 최근접 최소 9.2 cm'** 는 09-17 §13.4 정정 전 값(실수 ⑥).

## 7. 남은 것 · 이후
- **상자 옆 여유가 한 셀 수준**(1.4~2.6 cm, 09-17 §13.4) — 이후 [09-18 §15~16](../debug_log/2026-09-18/SUMMARY.md) 데크 yaw 보정 · ObstaclesCritic → CostCritic, [09-21 §4](../debug_log/2026-09-21/SUMMARY.md) CostCritic 3/3(여유 8~11 cm), 10-13 · 10-15 '상자 옆 정지'(칸 판정 뒤집힘 · 기억 밀림)로 이어짐.
- **조향 흔들림**(부호반전 4~16 /m): 09-17 §12~§14 에서 temperature · 시뮬레이터 충실도 · 위치 영향(< 0.1 mm)으로 정리 — 다음 시기 카드.
- **간헐 중단**: mp9 TF 외삽(→ 10-07 MPPI `transform_tolerance` 0.5), mp10 · mp12 `Optimizer fail` — 원인 미확정.
- **offset 3 · max_angle 0.5 · 탐색 네 손잡이** 는 반증되거나 단독 효과가 확인되지 않은 채 남아 있다(§5 실수 ① · ③). 되돌릴지 판단한 기록 없음.
- 펌웨어 수정의 성공 기여도는 분리 못 함(반사실 없음, 09-17 §9).
- Smac 의 '시작 자세 거부' 는 소스로 확인하지 않았다(**추정**). 10-26 · 10-27 에 Smac 을 NavFn fallback 과 함께 다시 들였다(CLAUDE.md §6).
- 크기 n = 3 은 한 코스 · 한 상자 배치(창 0.23 m)다. 대표 코스(창 ≥ 0.30) · 자유 이동 확장은 이후 F0~F2.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| mp1 | Smac + MPPI, ABORTED 48 s | 09-15 §2, `2026-09-15/outputs/mp1.csv` |
| mp2 | NavFn + MPPI(32), 입구 60 s 정체 | 09-16 §1.2, `outputs/mp2.csv` · `job327_mp2why.txt` · `job329_plancorner.txt` |
| mp3 | 56 step · offset 3 · angle 0.5 + 복셀 필터, 정체 + CPU + 기억 소실 | 09-16 §1.9, `outputs/drive_mp3.txt` · `mp3.csv` · `job327_mp3.txt` |
| mp4 | 10 Hz · inflation 0.70 · SmoothPath, 18 s stuck 취소 | 09-16 §1.13, `outputs/drive_mp4.txt` · `mp4.csv` · `j345_mp4.txt` · `j354_mp4.txt` · `j355_*.txt` |
| mp5 | PathFollow 10/20, 입구 통과 · 복귀 정지 | 09-16 §1.15, `outputs/drive_mp5.txt` · `mp5.csv` · `j366_mp5_return.txt` |
| mp6 | 목표 (2.2, 0), 목표 앞 정체 | 09-17 §2, `2026-09-17/outputs/drive_mp6*.txt` · `j374_mp6.txt` · `j376_mp6.txt` |
| mp7 | SLAM 정지로 ABORTED | 09-17 §5, `outputs/drive_mp7*.txt` · `j379_mp7_events.txt` · `mp7_*.log` |
| mp8 | 목표 0.24 m 옆 정지 | 09-17 §7, `outputs/drive_mp8*.txt` · `j394_mp8.txt` · `j395_mp8.txt` · `j396_goalsim8.txt` |
| mp9 · mp10 · mp11 | 같은 구성 3/3 | 09-17 §9~§11, `outputs/drive_mp9~11*.txt` · `j379_mp9~11.txt` · `j404_mp9.txt` |
| bag | `bag_mp2` ~ `bag_mp11` | 날짜 폴더 `bags/*.tgz`(git 제외, 로컬 보관) |
| 원본 없는 도구 | 09-15 `job317_plan_ab2.py` 는 09-14 판만, `job314_relay_orphan.sh` · `job207_return.py` · `run_j.sh`(09-16) 는 저장소에 없음 | 원천 소실 |

---

## 9. 도구 해설
### 9.0 이 시기 공통 사항
- **실행 경로**: PC 스크래치패드(`82ce61d4…/scratchpad`, 09-28 자동 소실 — 저장소 `jobs/` 가 남은 사본)의 스크립트를 WSL + `sshpass -p <PW>` 로 Jetson `/tmp/` 에 올려 실행. Jetson 주소는 `JETSON_HOST` 기본 192.168.0.101(09-15 오후 · 09-17 mp9 무렵엔 172.30.1.8 — `run_j_alt.sh` · `run_mp9prep.sh`).
- **bag 분석 도구의 공통 골격**(job327 · 329 · 338 · 345 · 354 · 355 · 383 · 394 · 395 · 404): `rosbag2_py.SequentialReader` 로 sqlite3 bag 을 처음부터 끝까지 읽고, `/tf` 의 map→odom · odom→base_link 를 **header stamp** 로, 나머지(경로 · 코스트맵 · 명령)는 **bag 수신 시각**으로 줄 세운 뒤 `bisect` 로 '그 시각 직전 값' 을 쓴다. 시각 0 = 첫 odom→base_link stamp(T0) 또는 goal 시각(인자 G). 두 시계를 섞으므로 수십 ms 어긋날 수 있다(코드 기준 추정).
- **DDS 프로파일**: 09-16 저녁부터 잡 스크립트 첫 줄에 `export FASTRTPS_DEFAULT_PROFILES_FILE=…fastdds_udp_only.xml`(IP 변경 뒤 CLI 노드가 SHM 으로 뜨는 문제). 09-17 아침 `$HOME` 이 WSL 쪽에서 먼저 풀려 `/root/...` 가 되는 결함 → 절대경로로(09-17 §0).
- **출력 보존**: 09-16 · 09-17 은 대부분 `outputs/` 에 남았다. 원문이 없는 것은 각 항목에 적었다.

**도구 계보**
- 러너: 09-11 `job254_s4run.sh` + `job231_drive.sh` + `job125_avoid3.py` → 09-15 `run_inf1.sh`(PC 쪽 게이트, ssh 한 번에 주행까지 — 끊기면 주행 여부 모름) → 09-16 `run_drive_nohup.sh` v2(원격 nohup + 로그 폴링) → 09-17 판(목표 여유 · SLAM 생존 게이트, 주행 중 top) → 09-18 `run_meta.txt` · `params.txt` 기록 → 09-23 `job550_f0run.py` → 10 월 `Docs/tools/run_*`.
- 정체 해부: `job327_mp2why.py`(자세 · 경로 · 실현가능성 · ASCII) → `job345_traj.py`(MPPI 후보 분포, `/trajectories` 필요) → `job354_critics.py`(대표 후보 16 개의 크리틱 비용) → `job355_mppi_sim.py`(배치 · softmax 재현, 09-17 펌웨어 모델 · `/plan` 대체 추가) → 09-17 `job410` · `job419_mppi_sim_humble.py`(Humble 1.1.20 충실화) → 이후 `job452` 등.
- 게이트: `job248_audit.py`(상자 · 통로 폭) + `job315_boxcells.py`(상자 셀 최대 y) → 창 공식(09-14) → 3 표본 중앙값 · 좌측 경계 필터(09-16) → `job377_goalclear.py` · `job386_slamalive.py`(09-17) → 09-21 이후 게이트 표 A~N → 10-27 `Docs/tools/chk_drive_gate.py`.

### 9.1 `run_inf1.sh` — 09-15 mp1 게이트 + 주행 (PC)
- 위치 · 형태: PC(WSL), `run_inf1.sh NAME D BX BY TOL GL`(기본 inf1 · 2.0 · 1.15 · −0.04 · 0.06 · 0). 이름은 09-14 inflation 시험(inf1) 때 만든 것을 mp1 에도 썼다. [원본](../debug_log/2026-09-15/jobs/run_inf1.sh)
- 왜: 상자 위치 · 창 · 유령 셀을 확인하고 나서만 주행(09-14 §2.16 · §2.20 의 교훈).
- 하는 일: job254 · 231 · 125 · 248 전송 → ① `job248_audit.py`(BOX_HINT) 출력에서 '로컬[' 다음 줄의 셀 좌표 중 **통로 띠 x 0.3~1.6 · y −0.10~+0.50**(09-15 에 오른쪽 유리 칸막이 셀을 빼려고 좁힘) 안 '센서 근거 없는 셀' 수 ≤ 1 ② 기준1 표 x 0.9~1.4 행 최소폭 ③ `job315_boxcells.py` 로 상자 셀 최대 y(nan 이면 3 회 재시도) ④ 창 = 기준1 좌측 경계(x 1.0~1.3 최소) − (상자 셀 최대 y + 0.195) ≥ 0.20 ⑤ 통과하면 `GOAL_LAT=GL bash job254_s4run.sh …` 를 **같은 ssh 안에서** `| tail -70`.
- 출력: 화면만 — mp1 은 `outputs/mp1.csv` 만 남음(러너 화면 · nav2.log **원천 소실**).
- 결함: ⑤ 가 ssh 하나에 묶여 끊기면 주행 여부를 모른다(09-15 §3 의 mp2 1 차 시도 — 그래서 v2). 0.195 상수(§6). 좌측 경계가 x 1.00 행의 오른쪽 구간을 섞을 수 있음(09-16 mp3 게이트에서 −0.365 오판 → v2 에서 고침).
- 계보 · 다시 쓰기: → `run_drive_nohup.sh`. 안 씀.

### 9.2 `run_drive_nohup.sh` — 주행 러너 v2 (09-16 · 09-17 판, PC)
- 위치 · 형태: PC(WSL), `run_drive_nohup.sh NAME D BX BY TOL GL`. [09-16 판](../debug_log/2026-09-16/jobs/run_drive_nohup.sh) · [09-17 판](../debug_log/2026-09-17/jobs/run_drive_nohup.sh)
- 왜: 09-15 Wi-Fi 소실로 주행 여부를 잃은 교훈 — 원격에서 nohup 으로 띄우고 PC 는 로그만 읽는다.
- 하는 일: ① 스크립트 5 개 전송 ② `job248_audit.py`(출력에 '최소폭' 줄이 없으면 1 회 재시도 — 09-16 `run_gate` 에서 출력이 잘린 일) ③ 상자 셀 최대 y **3 표본 중앙값**(09-16 mp3 게이트: 1 표본이 0.219 로 튐) ④ 좌측 경계 = x 1.10~1.30 행의 기준1 구간 중 **하한 > 상자 셀 최대 y** 인 것만 ⑤ 근거 없는 셀 ≤ 1 · 창 ≥ 0.20 ⑥ (09-17 판) **`job377_goalclear.py D GL` ≥ 0.20 m** ⑦ `nohup bash job254_s4run.sh … > /tmp/drive_NAME.log` ⑧ 5 s 마다 ssh 로 로그를 읽어 새 줄만 출력(최대 8 분, ssh 실패는 재시도), '결과 ' · '게이트 실패' 줄에서 끝.
- 출력: `outputs/drive_mpN.txt`(PC 화면 = 게이트 + 러너 요약), `drive_mpN_runner.txt`(09-17, Jetson 로그 원문).
- 결함: 게이트 수치는 문자열 grep 으로 파싱 — job248 출력 형식이 바뀌면 조용히 nan(그래서 nan 검사). 0.195 상수. 주행 중 PC 가 끊겨도 주행은 계속되므로 **현장 정지 수단**이 따로 필요(09-15 §3 교훈, 이후 F0 '온보드 정지 수단').
- 다시 쓰기: 안 씀(10 월 `Docs/tools/` 러너 · `chk_drive_gate.py` 가 대신).

### 9.3 `job254_s4run.sh` · `job231_drive.sh` — Jetson 쪽 주행 절차
- `job254_s4run.sh NAME D BX BY TOL`(09-11 판 해설은 [컨트롤러 카드 §9.9](controller-rpp-vs-mppi.md)). 09-17 판에서 더한 것: DDS 프로파일 export, 프로세스 · 보드 검사 뒤 **`job386_slamalive.py` 가 OK 가 아니면 중단**. [09-17 판](../debug_log/2026-09-17/jobs/job254_s4run.sh)
- `job231_drive.sh NAME D TMO`: bag 기록(`/tf /tf_static /map /scan /plan /local_plan /trajectories /transformed_global_plan` 두 코스트맵 · `/odometry/filtered /wheel_odom /cmd_vel /rover/status /battery /rover/stuck`) → 4 s 뒤 `job125_avoid3.py D TMO NAME` → bag 종료(SIGINT, 10 s 대기) → nav2.log 신규분에서 'detected collision' · 'clear except' · 'clear entirely' · 'backup failed' · 'Goal succeeded' · 'aborted' 건수, EKF 위반(`Failed to meet update rate`) · SLAM 폐기(`Message Filter dropping`) 누적 · load. 09-17 판: `/trajectories` 제외(mp7 CPU), 주행 동안 `top -b -d 2` 를 `/tmp/top_NAME.log` 로. [09-16 판](../debug_log/2026-09-16/jobs/job231_drive.sh) · [09-17 판](../debug_log/2026-09-17/jobs/job231_drive.sh)
- 결함: EKF 위반 · SLAM 폐기는 **로그 누적 수**라 주행분이 아니다(SUMMARY 의 '32 → 91' 처럼 앞뒤 차로 읽어야 함). '`Goal succeeded`' 패턴은 Nav2 로그 문구('Reached the goal!' 등)와 달라 0 이 나올 수 있다(코드 기준, 확인 안 함). 다시 쓰기: 안 씀.

### 9.4 `job125_avoid3.py` — 주행 러너 지표 (09-17 판)
- 위치 · 형태: Jetson, `python3 job125_avoid3.py D TMO NAME`, `GOAL_LAT` 환경변수. [09-17 판](../debug_log/2026-09-17/jobs/job125_avoid3.py)
- 이 카드에 관련된 출력 줄: `결과 · 소요 · 주행` / ① **실제 최근접(차체 ↔ 상자 기하)** = `clear_geo`: 상자 사각형(사용자 실측 0.18 × 0.11, 깊이 검출로 0.5 s 마다 재고정 · 허용 0.30 m)의 둘레 84 점 ↔ 차체 외곽(**패딩 제외** 0.25 × 0.165) / ② **계획의 최소 여유** = 그 순간 `/plan` 점 ↔ 상자 둘레 최소 − 0.165 / ③ 상자 자리의 로컬 · 전역 코스트맵 비용(0 이면 기억 소실) / ⑥ 상자 미관측 최대 시간(이 구간의 ① 은 외삽) / 조향 = 목표 0.30 m 밖 주행 구간의 \|v\| > 0.03 샘플 ω 부호반전(문턱 0.01). CSV 열 `t, fwd, lat, clear_geo, plan_clear, plan_lat_at_box, lc_box, gc_box, v, w, box_pts, box_age`.
- 09-17 변경: 상자 검출을 x 정렬 10 cm 간격으로 나눠 가장 큰 조각만(바닥 잡음이 전면을 끌어당기던 결함, 09-17 §1).
- 알려진 결함: ① · ② 는 상자 **모델** 기준이라 재고정 · 외삽 오류를 그대로 받는다(실수 ⑥, 09-17 §13.4). 조향 문턱 0.01 은 09-11 에 과소 판정됐는데 코드는 그대로. 전체 해설(상자 기하 · 09-10 클러스터링 결함)은 [회피 주행 계측](avoid-run-metrics.md).
- 다시 쓰기: 안 씀 → 09-23 `job550_f0run.py`. 여유는 job416 · 이후 코스트맵 기준 도구로.

### 9.5 `job248_audit.py` · `job315_boxcells.py` — 상자 · 통로 감사, 상자 셀 최대 y
- `job248_audit.py`(Jetson, `BOX_HINT='BX BY'`): 깊이 점군으로 상자 검출(09-17 판에서 x 분할 추가) + 로컬 · 전역 코스트맵의 x 행별 통과 구간(기준1: 중심 셀 < 99 / 기준2 RPP / 기준3) · 최소폭 · 센서 근거 없는 셀 목록. 상세는 [통과 폭 카드](passage-width-analysis.md). [09-17 판](../debug_log/2026-09-17/jobs/job248_audit.py)
- `job315_boxcells.py BX BY`(09-14, [원본](../debug_log/2026-09-14/jobs/job315_boxcells.py)): 로컬 코스트맵(TRANSIENT_LOCAL 1 장) LETHAL(≥ 100) 셀 중심을 base_link 로 옮겨, 전진 BX−0.15 ~ BX+0.45 · 횡 BY ± 0.40 창 안 셀의 **횡 최대**를 한 줄로. 셀 **중심**값이라 0.175 셀이 0.169 처럼 찍힌다(로버 yaw · 원점 정렬 차). 창 안에 상자 아닌 셀이 들어오면 그대로 최대가 된다.
- 다시 쓰기: 안 씀(Phase N 뒤 코스트맵이 nvblox 로 바뀜).

### 9.6 `run_gate.sh` · `run_gate2.sh` · `run_prep.sh` · `run_prep_alt.sh` · `run_mp7prep.sh` · `run_mp8prep.sh` · `run_mp9prep.sh` — 준비 · 게이트 묶음 (PC)
| 도구 | 하는 일 | 쓰인 곳 |
|---|---|---|
| [`run_prep.sh`](../debug_log/2026-09-16/jobs/run_prep.sh) BXH BYH | `job240_clean.sh 15`(재기동) → `job314_relay_orphan.sh`(릴레이 고아 정리, **원본 없음**) → readback(time_steps · offset · max_angle · 패딩) → 감사 · 게이트(1 표본) | mp3 준비 `outputs/prep_mp3.txt` |
| `run_prep_alt.sh` | 같은 것을 172.30.1.8 로 | — |
| [`run_gate.sh`](../debug_log/2026-09-16/jobs/run_gate.sh) BXH BYH | 재기동 없이 감사 + 3 표본 중앙값 + 좌측 경계 필터 + 창 | mp4 게이트(1 회 출력 잘림 → 러너 재시도 추가) |
| [`run_gate2.sh`](../debug_log/2026-09-17/jobs/run_gate2.sh) | 재부팅 뒤 /tmp 소실 대비: 감사 도구 전송 → 릴레이 고아 → `job348_readback2.sh` → 프로세스 · 부하 → `run_gate.sh` | 09-17 prep |
| `run_mp7prep.sh` · `run_mp8prep.sh` · `run_mp9prep.sh` | `job240_clean.sh` → `run_gate2.sh` → (7 · 8) `job378_goalcands.sh` 목표 후보 / (8 · 9) `job386` SLAM 생존 · (9) `job403_critics_rb.sh` | `outputs/prep_mp7~9*.txt` |
- 결함: 모두 grep 파싱 · 0.195 상수. 다시 쓰기: 안 씀(→ `Docs/tools/prep_patrol.sh` · `chk_prep.py`).

### 9.7 `job327_mp2why.py` — 정체 해부(자세 · 경로 · 실현가능성 · 코스트맵 ASCII) (09-16)
- 위치 · 형태: Jetson, `python3 job327_mp2why.py BAG [sx sy yaw_deg] [t1,t2,…]`. PC 감싸개 [`run_j327.sh`](../debug_log/2026-09-16/jobs/run_j327.sh)(+ `job328_navlog.sh`) · [`run_j327b.sh`](../debug_log/2026-09-16/jobs/run_j327b.sh)(+ `job334_rate.sh`). [원본](../debug_log/2026-09-16/jobs/job327_mp2why.py)
- 왜: 사용자 관찰 "오른쪽으로 꺾어야 하는데 왼쪽으로 튼다" 를 '경로가 그랬나 / 컨트롤러가 그랬나 / 그 자리에서 다른 선택지가 있었나' 로 가르려고.
- 하는 일(1 s 간격, bag 첫 odom 기준 92 s 까지): ① map 자세 = map→odom ∘ odom→base_link, 출발 자세 기준 (전진, 횡, yaw) ② 그 시각 `/cmd_vel` ③ 최신 `/plan` 에서 로버 최근접 점 i: **경로 접선**(i−1 → i+5 방향, 로버 yaw 대비), **carrot**(경로를 따라 0.25 m 앞 점의 방위 — RPP lookahead 와 같은 거리), 경로 대비 횡편차(+ = 경로 왼쪽) ④ 로컬 코스트맵(odom): 풋프린트 둘레(반길이 0.25 · 반폭 0.165 + 패딩 0.01, 변마다 21 · 15 점) **최대 비용**, LETHAL 셀을 로버 좌 · 우로 나눠 4 모서리까지 최소 거리 · 셀 수 ⑤ **실현가능성**: dθ = −50 ~ +50°(10° 간격)마다 '제자리 회전 스윕 최대 비용' · '회전 후 0.025~0.15 m 전진 최대 비용'(`#` ≥ 100 LETHAL, `o` = 99 내접) ⑥ 지정 시각마다 로컬 코스트맵 ASCII(odom 축, `R` 풋프린트 · `>` 앞 · `p` 경로 · `G` 목표, `#` · `o` · `+` 50~98 · `.` 1~49).
- 출력: `outputs/job327_mp2why.txt` · `job327_mp3.txt` · `job327_mp4.txt` · `job327_mp5.txt`, 09-17 `j374_mp6.txt`(job374) · `j376_mp6.txt`(job376).
- 쓰인 곳: 09-16 §1.2 타임라인 · §1.3 '검증' 1~5 · PASSAGE §2.1 · §3 표, 09-17 §2.
- 알려진 결함: ① 실현가능성은 **둘레 최대 비용 하나**라 내접(99) 셀을 '스침' 과 '깊이 들어감' 을 구분 못 함. ② carrot 0.25 m 는 RPP 개념 — MPPI 의 당근(furthest + offset)과 다르다(그래서 job354 가 생김). ③ 풋프린트가 대칭(0.25) — 09-30 실측 비대칭(0.262/0.248) 이전. ④ 경로는 bag 수신 시각, TF 는 stamp 기준.
- 계보: 09-14 `job3xx` 상자 진단 → 이것 → job345 · job354. 다시 쓰기: 개념 유효(실현가능성 표), 파일은 안 씀.

### 9.8 `job329_plancorner.py` · `job328_navlog.sh` · `job334_rate.sh` — 경로 헤딩 · nav2.log 추출 (09-16)
| 도구 | 형태 | 하는 일 | 출력 · 결함 |
|---|---|---|---|
| [`job329_plancorner.py`](../debug_log/2026-09-16/jobs/job329_plancorner.py) | `BAG t1,t2,…`(감싸개 `run_j329.sh`, 기본 5,24,48,75) | 그 시각 최신 `/plan` 의 점 수 · 첫 점간격, 로버 최근접 점부터 0.05 m 마다 (x, y, 진행방향 = k → k+3, 로버 yaw 대비 상대각), 0.85 m 까지 | `outputs/job329_plancorner.txt`. 점간격을 첫 두 점으로만 잼(§6 의 0.026~0.049) |
| [`job328_navlog.sh`](../debug_log/2026-09-16/jobs/job328_navlog.sh) | `LOGT` | `/tmp/nav2.log` 에서 LOGT 이후 controller · progress · abort · recover · clear · MPPI · fail · goal 등 키워드 줄 80 개 + `drive_mp2.log` 앞 45 줄 + 설치 YAML md5 · BT 의 controller_id · planner_id | job327 출력 머리(`job327_mp2why.txt`). nav2.log 원문은 소실 |
| [`job334_rate.sh`](../debug_log/2026-09-16/jobs/job334_rate.sh) | `LOGT` | 'missed its desired rate' 수 · 10 s 구간별 분포, 'Failed to make progress' 시각, Optimizer · collision · Aborting 줄, load · 릴레이 CPU | `job327_mp3.txt` 머리. 라벨 '(goal 후)' 가 실제로는 LOGT(= bag T0) 기준(§6) |

### 9.9 `job331_boxflicker.sh` · `job312_box_edge.py` · `job333_voxstat.py` — 상자 가장자리 셀 깜빡임 (09-16 §1.7~1.8)
- `job331_boxflicker.sh BX BY N`(Jetson, [원본](../debug_log/2026-09-16/jobs/job331_boxflicker.sh)): `job315_boxcells.py` 를 4 s 간격 N 회 → 이어서 로컬 코스트맵 상자 주변(y 0.30 → 0.10, x 1.05~1.35) 셀 값 표를 찍으려 했으나 heredoc 안 `'\x'` 로 **SyntaxError — 표는 한 번도 안 나옴**. 출력 `outputs/job331_boxflicker.txt`(6 회 0.169), `job331_after_voxelfilter.txt`(필터 뒤 24 회, 같은 앞부분만 반복 실행).
- `job312_box_edge.py BX BY [DUR]`(09-14 작성, 09-16 재사용, [원본](../debug_log/2026-09-14/jobs/job312_box_edge.py), 감싸개 [`run_j312.sh`](../debug_log/2026-09-16/jobs/run_j312.sh) 가 원시 `/camera/camera/depth/color/points` 와 필터 `/camera/depth/points_filtered` 를 연달아): 상자 핵심 · 좌측 연장 띠 · 뒤쪽 연장 띠 세 상자 영역(z ≥ 0.06)에서 점 있는 프레임 비율 · 프레임당 점 수 · z 분포 · **고립 비율**(같은 프레임 5 cm 안 이웃 ≤ 2) · **혼합 화소 광선 여부**(카메라 → 상자 가장자리 방위 ±1° 안이면서 상자보다 먼 점) + 같은 시각 코스트맵 상자 LETHAL 범위. 출력 `outputs/j312.txt`. 결론 '좌측 띠 y +0.18 점은 실물(옆면)'.
- `job333_voxstat.py X0 X1 Y0 Y1 [DUR] [TOPIC]`(Jetson, [원본](../debug_log/2026-09-16/jobs/job333_voxstat.py), 감싸개 `run_j333.sh` · `run_j333b.sh`): 필터 점군을 odom 으로 옮겨 **STVL 과 같은 월드 복셀**(0.05 m, 원점 정렬, z 0.06~0.40 = STVL min/max 높이)로 프레임마다 점 수를 셈 → 2D 셀마다 '점 ≥ 1 프레임 %' · '한 z-복셀에 ≥ 2 / ≥ 3 점 프레임 %' · 프레임당 최대 복셀 점수 · z 범위. `EVENT_Y` 를 주면 y ≥ EVENT_Y 점이 있는 프레임을 사건으로 기록(점 수 · 같은 복셀 최대 점 수 · 좌표). 출력 `outputs/j333.txt`(40 s) · `j333b.txt`(180 s raw · filtered 동시, 사건 9/2694). 결과가 `voxel_min_points: 3` 을 고른 근거(2 는 사건 3/9 통과, 3 은 9/9 차단 · 진짜 가장자리 셀 91 % 유지).
- 결함: TF 를 첫 프레임에서 한 번만 조회(로버 정지 전제). `any1` 을 z-복셀마다 더한 뒤 프레임 수로 클램프 — 한 2D 셀에 z-복셀이 둘이면 비율이 과대(코드 주석 자인).
- 계보 · 다시 쓰기: 깊이 장애물 줄기([카메라 깊이 장애물](depth-obstacle-costmap.md)). STVL 이 nvblox 로 바뀌어 지금은 안 씀(같은 생각 — 월드 복셀 단위 잡음 통계 — 은 Phase N 유령 칸 분석으로 이어짐).

### 9.10 `job338_ghost_decay.py` — decay 연장이 통로를 막는가 (09-16 §1.11 C)
- 위치 · 형태: Jetson, `python3 job338_ghost_decay.py BAG BX BY [D1L=60 D2L=120 D1G=90 D2G=180]`, 감싸개 `run_j338.sh`(mp2 · mp3) · `run_j338b.sh`(mp2 + bk1 업로드). [원본](../debug_log/2026-09-16/jobs/job338_ghost_decay.py)
- 왜: 사용자 결정 'C 검토' — decay 를 늘리면 잡음 · 사람 자취가 쌓여 통로를 막지 않는가를 **실데이터로**.
- 하는 일: 로컬(odom) · 전역(map) 코스트맵 프레임마다 LETHAL 셀을 셋으로 분류 — **lidar**(최근 10 s `/scan` 점을 그 프레임으로 옮겨 0.12 m 안: 2D 층 담당) · **box**(BX−0.05~BX+0.35, BY ± 0.30) · **other**(깊이 전용 = 유령 후보). other 셀마다 생존 구간(첫 ~ 마지막 LETHAL) → 5 s 간격 개수표, 통로 띠(x 0.3~1.6, y −0.10~+0.50) 안 셀 목록, 로버 궤적과 최소 거리 분포, **상한 시뮬**: 모든 소멸을 decay 소멸로 보고 생존을 (D2 − D1) 만큼 늘렸을 때 동시 생존 최대 · 통로 띠 최대.
- 출력: `outputs/j338.txt`(mp2 bk1 없음, mp3) · `j338b.txt`(mp2 · bk1). SUMMARY §1.11 C 표와 일치(mp2 로컬 334 개 · 띠 3 → 4, mp3 191 · 1 → 2, bk1 364 · 띠 23 = 상자 셀 오분류, 전역 띠 0 · 0 · 7).
- 결함: '소멸 = decay 소멸' 이라 상한(SUMMARY 자인). bk1 은 BX 입력 1.19 가 실제 전면 1.05~1.12 와 달라 상자 셀을 other 로 셈. 95 s 넘는 주행 데이터 없음.
- 다시 쓰기: 안 씀(STVL 전용).

### 9.11 `job339_relay_prof.sh` · `job341_relay_cpu.sh` · `job337_pkgs2.sh` — 시스템 · 설치 확인 (09-16 §1.11 D)
| 도구 | 하는 일 | 결과 |
|---|---|---|
| [`job339_relay_prof.sh`](../debug_log/2026-09-16/jobs/job339_relay_prof.sh) | 상위 CPU 프로세스 → `depth_relay.py` **두 번째 인스턴스**를 `cProfile` 로 14 s(다른 노드 이름 · 출력 토픽, 원 릴레이 그대로) → tottime 상위 14 | 12 s 중 10.5 s 가 PointCloud2 `data` setter(bytes 를 바이트마다 isinstance 검사) — 출력 원문 없음(SUMMARY 인용) |
| [`job341_relay_cpu.sh`](../debug_log/2026-09-16/jobs/job341_relay_cpu.sh) | 새 코드(`array.array('B', …)`) 인스턴스를 20 s 띄우고 top 으로 새 · 기존(PID 8443 고정) %CPU 4 표본, 출력 hz | 53~60 → 13~20 %, 15.1 Hz — 원문 없음. PID 하드코딩 |
| [`job337_pkgs2.sh`](../debug_log/2026-09-16/jobs/job337_pkgs2.sh) | navfn · theta_star · smoother · constrained_smoother · rotation_shim · dwb · mppi · smac 패키지 설치 여부 + apt 후보 | PASSAGE A4 'Theta* 설치됨(1.1.20)' 의 근거 |

### 9.12 `job340_smooth_ab.py` — 계획 정지 A/B (09-16 §1.12) ⚠ 실행 중 전역 inflation 을 바꿨다 되돌림
- 위치 · 형태: Jetson, `python3 job340_smooth_ab.py GOAL_X GOAL_Y BX BY [INFL=0.70] [SMOOTHER=simple_smoother]`, 감싸개 `run_j340.sh`. 로버가 출발점(map 원점)에 있어야 함. [원본](../debug_log/2026-09-16/jobs/job340_smooth_ab.py)
- 왜: PASSAGE A1(SmoothPath) · A2(inflation 0.70) 중 무엇이 입구 꺾임을 줄이는지 주행 없이 고르려고.
- 하는 일: ① `/compute_path_to_pose`(GridBased, `use_start` (0, 0, 0)) ② 같은 경로를 `/smooth_path`(simple_smoother, `check_for_collisions` true, 2 s) ③ 전역 코스트맵 `set_parameters` 로 `inflation_layer.inflation_radius` = INFL → 3 s 대기 → ① · ② 반복 → 원래 값으로 복원. 각 경로의 지표: 입구 접선(x = BX − 0.45 에 가장 가까운 점의 진행방향), 절댓값 최대 진행방향, **0.1 m 창 최대 꺾임**(점 i 와 호 길이 +0.10 m 점의 진행방향 차), 차선변경 시작 x(횡 > 0.10) · 끝 x(횡 > 통로값의 90 %), 통로 계획횡(x 1.0~1.4 중앙값), 상자 셀(전역 LETHAL, BX−0.10~+0.40 · BY ± 0.30) · 좌측 셀 최소 거리, 헤딩 프로파일 12 점.
- 출력: `outputs/job340_planab.txt`(SUMMARY 표와 일치, 끝에 CPU 상위 · load).
- 결함: ① 입구 접선은 x 로 가장 가까운 점이라 경로가 같은 x 를 두 번 지나면(복귀) 엉뚱한 점을 잡을 수 있다. ② 상자 · 좌측 셀은 **처음 받은 전역 코스트맵 한 장**(LETHAL 은 inflation 과 무관해 결과엔 영향 없음). ③ 실행 중 파라미터 변경(10-14 이후 '바꿨으면 재기동' 규칙). ④ 한 배치 · 한 목표에서 한 번.
- 계보: 09-14 `job317_plan_ab2.py`(NavFn vs Smac) → 이것 → 10-13 `anal_f2o1_options.py`(기록된 코스트맵에서 inflation 재계산 · 격자 최단 비용 경로 — 실행 중 노드를 건드리지 않음). 다시 쓰기: 안 씀.

### 9.13 `job345_traj.py` — MPPI 후보 궤적 분포 (09-16 §1.13) — `visualize: true` 일 때만
- 위치 · 형태: Jetson, `python3 job345_traj.py BAG t1,t2,…`(bag 첫 odom 기준 초). mp4 는 `run_alt3.sh`(syslog Wi-Fi 와 함께), mp5 는 `job365` · `job366`, mp6 은 `job374`. [원본](../debug_log/2026-09-16/jobs/job345_traj.py)
- 왜: 정체 순간 최적화기가 '어디로 가는 후보' 를 보고 있었는지.
- 하는 일: `/trajectories`(MarkerArray — Humble TrajectoryVisualizer 가 배치를 `trajectory_step` 마다, 시간축을 `time_step` 마다 뽑아 점마다 SPHERE marker, scale 이 시간에 따라 커짐)의 점을 로버 좌표로 → **scale 상위 20 % 를 '끝단'** 으로 보고 '앞 > 5 cm' · '뒤 < −3 cm' · '우 < −3 cm' · '좌 > 3 cm' 비율, 끝단 거리 중앙 · 최대, 전방 · 횡 중앙값. `/transformed_global_plan`(컨트롤러가 보는 잘린 경로)의 첫 점 거리 · 0.3 m 앞 방위.
- 출력: `outputs/j345_mp4.txt`(메시지당 2,232 점 = 시각화용 표본, 배치 1,000 전체가 아님), `j366_mp5_return.txt` · 09-17 `j374_mp6.txt` 안.
- 결함: '끝단 = scale 상위 20 %' 는 marker 크기 규칙에 기댄 근사(이 bag 에서 scale 종류 2). 시각화 표본이라 배치 전체 분포가 아니다. 원인과 결과를 못 가름(실수 ③).
- 다시 쓰기: 시각화가 무거워(≈5 MB/s, 이후 10-12 `mppi_viz:=true` 206 kB × 10 Hz 로 UDP 포화) 진단 주행에만. 파일은 안 씀.

### 9.14 `job354_critics.py` — 크리틱 비용 재구성 (09-16 §1.14)
- 위치 · 형태: Jetson, `python3 job354_critics.py BAG t1,t2,…`, 감싸개 `run_j354.sh`. [원본](../debug_log/2026-09-16/jobs/job354_critics.py)
- 왜: 사용자 질문 "회피 로직과 추종 로직이 무엇이 충돌하는가, 과한 값인가" 에 크리틱별 숫자로 답하려고.
- 하는 일: 그 시각 로컬 코스트맵 · `/transformed_global_plan` · odom 자세에서 대표 후보 16 개(정지 · 직진 0.08/0.04 · 우호 3 종 · 완만 우호 2 · 제자리 우 −0.38/−0.20 · 우회전 1 s → 직진 · 좌호 · 제자리 좌 · 후진 · 후진 + 우 · **실제 명령 유지**)를 DiffDrive 로 32 × 0.1 s 굴려 Humble 크리틱 식으로 계산(머리 주석): **Obstacles** = 둘레 최대 비용 c → 거리 d = r_in − (ln c − ln 253)/scale, LETHAL 이면 10,000, d < 0.05 면 20 × (0.05 − d), 아니면 1.5 × mean(0.40 − d) / **PathAlign** = furthest ≥ 3 일 때만 3 점마다 경로 최근접 거리 평균 × 14 / **PathFollow** = 끝단 ↔ path[furthest + 5] × 5 / **PathAngle** = 현재 → path[furthest + 4] 각 > 0.5 rad 일 때 끝단 heading 오차 × 2 / **PreferForward** 후진량 × 5 / **Constraint** 한계 초과 × 4. 각 후보의 합계 · 끝단 (dx, dy, dθ) · furthest · 충돌 index, 최저 후보.
- 출력: `outputs/j354_mp4.txt`(bag t 10 · 14 · 17 · 18 · 19 · 20 · 22), `j366_mp5_return.txt`(t 29 · 32).
- 쓰인 곳: §1.14 '무엇이 충돌하는가' 표(브레이크 둘 · 약한 가속기 하나).
- 알려진 결함: ① 상수가 **코드에 고정**(mp4 값: Follow 5/5, 문턱 · Goal · GoalAngle 없음) — mp5 에 그대로 써서 실수 ⑤. ② Obstacles 거리 역산을 로컬 코스트맵 2.5/0.40 로 했으나 실제 크리틱은 기본 10/0.55(09-18 §16). ③ 소스 의미론 근사(경로 창 · 정규화 세부 생략, 주석 자인). ④ 16 개 대표 후보의 최저는 MPPI 의 softmax 평균과 다르다 — '정지 최저' 가 정상 주행 중에도 나온다(실수 ②).
- 계보: → job355(배치 전체 · softmax). 다시 쓰기: 안 씀(ObstaclesCritic 미사용).

### 9.15 `job355_mppi_sim.py` — 오프라인 MPPI 시뮬레이터 (09-16 판 · 09-17 판)
- 위치 · 형태: Jetson, `python3 job355_mppi_sim.py BAG t key=val …`(키: vx_std · wz_std · temperature · gamma · iters · batch · steps · dt · align_w/off/thr · follow_w/off/thr · angle_w/off/max/thr · rep_w · crit_w · margin · coll_cost · fwd_w · goal_w/thr · ga_w/thr · goal_yaw · cycles · seed · label, 09-17 판 + db · promote · eps · track_b · prune). 변형 일괄 실행 [`job356_variants.sh`](../debug_log/2026-09-16/jobs/job356_variants.sh)(A · B) · [`job357_variants2.sh`](../debug_log/2026-09-16/jobs/job357_variants2.sh)(C~H) · [`job358_variants3.sh`](../debug_log/2026-09-16/jobs/job358_variants3.sh)(I~L, F_t12 · F_t20 · B_t20) · [`job366_mp5sim.sh`](../debug_log/2026-09-16/jobs/job366_mp5sim.sh)(mp5 t 29: M · N · O · P, t 24) · 09-17 [`job375_goalsim.sh`](../debug_log/2026-09-17/jobs/job375_goalsim.sh)(mp6 t 52: G1~G4, **출력 없음**) · [`job396_goalsim8.sh`](../debug_log/2026-09-17/jobs/job396_goalsim8.sh)(mp8 t 33: S1~S5, 120 주기). [09-16 판](../debug_log/2026-09-16/jobs/job355_mppi_sim.py) · [09-17 판](../debug_log/2026-09-17/jobs/job355_mppi_sim.py)
- 왜: 실주행 한 번(배터리 · 배치 · 15 분)을 쓰기 전에 손잡이 후보를 **정체 장면 그대로** 비교하려고.
- 하는 일: bag 의 그 시각 로컬 코스트맵 · 변환 경로 · 자세를 고정(정적 장면). 한 주기: 배치 1,000 × 32 스텝 잡음(스텝마다 독립 N(0, std)) + 평균열 → 한계로 clip → DiffDrive 롤아웃 → 크리틱(job354 와 같은 식, 단 **furthest 는 배치 전체 최대** — 모든 크리틱이 공유, 경로 · 목표 크리틱의 `threshold_to_consider`, GoalCritic · GoalAngle 포함) → 비용 += γ/σ² Σ 평균 · 잡음 → w = softmax(−(c − min)/temperature) → 평균열 = Σ w · 제어 → iters 회 → 첫 제어를 dt 동안 적용해 로버를 움직이고 한 스텝 shift. 주기 표: 명령 · 자세 · furthest · 충돌 % · 끝단 전방 · 크리틱별 평균 비용 · 최저 후보. 끝: '전진 · 횡 · 회전 · 최종 명령'. 09-17 판 추가: **펌웨어 휠 속도 모델**(휠 v = v ± ω·0.443/2 → \|v\| < eps 0.003 이면 0, < promote 면 promote 로, < db 면 0 → 다시 v · ω), `/transformed_global_plan` 이 없으면 `/plan`(map)을 odom 으로 옮겨 prune 1.0 m 만, 흔들림 지표(\|ω\| > 0.05 반전 /m · 고주파 RMS) · 목표까지 거리.
- 출력: `outputs/j355_ab.txt` · `j355_cdefgh.txt` · `j355_ijkl.txt` · `j366_mp5_return.txt`(09-16), `j396_goalsim8.txt`(09-17).
- 쓰인 곳: PathFollow 10/20(§1.14), 경로 크리틱 문턱 0.2 · GoalCritic 10(§7.2). 두 채택은 실주행(mp5 · mp9~11)으로 따로 확인.
- 알려진 결함: ① **Humble 1.1.20 과 네 가지 다름**(09-17 §14.1: 실제는 잡음을 reset 때만 생성해 재사용 · 후보 clip 없음 · 롤아웃 첫 스텝이 측정 속도 · Savitzky-Golay 필터 뒤 제어열[1] 출력) — 정량 예측(전진 m · 목표 거리)은 신뢰도 낮음. ② Obstacles 거리 역산 상수 2.5/0.40(실제 10/0.55). ③ 정적 장면 · 1 Hz 재계획 없음 — mp5 M 은 6 s 0.23 m 진행을 예측했지만 실제는 정지(표본 충돌률 35 % 경계, SUMMARY 자인). ④ seed 1 고정(seed 간 산포는 09-17 §14 에서야 봄).
- 계보: → 09-17 `job410_mppi_sim_lag.py`(구동계 지연 · 이득) → `job419_mppi_sim_humble.py`(`humble=1` 로 ①을 고침) → 09-18 `job452`(CostCritic) → 10 월 시뮬(job944/946 PreferForward, 10-26 PathAlign 28). 다시 쓰기: 이 판은 안 씀(job419 이후 판으로).

### 9.16 `job364_mp5state.sh` · `job365_mp5ana.sh` · readback 묶음 (09-16)
| 도구 | 하는 일 |
|---|---|
| [`job364_mp5state.sh`](../debug_log/2026-09-16/jobs/job364_mp5state.sh) | 주행 직후: `/cmd_vel` hz(정지 확인) · map 자세 · nav2.log 이벤트(1789547850 이후) · 루프 미달 · STUCK(shadow) 수 · 드라이브 로그 후반 · bag tgz |
| [`job365_mp5ana.sh`](../debug_log/2026-09-16/jobs/job365_mp5ana.sh) | job327(t 30 ASCII) · job345 · job354(t 28 · 32) — job366 으로 대체돼 출력 없음 |
| [`job342_readback.sh`](../debug_log/2026-09-16/jobs/job342_readback.sh) · [`job348_readback2.sh`](../debug_log/2026-09-16/jobs/job348_readback2.sh) | 실행 중 값 확인: controller_frequency · model_dt · time_steps · visualize · decay · relay max_range · BT controller_id(342), + temperature · iteration · std · BT raw_path · SmoothPath · stuck_monitor 파라미터(348, 컨트롤러가 뜰 때까지 12 회 재시도) |
| [`job343_chk.sh`](../debug_log/2026-09-16/jobs/job343_chk.sh) | BT 의 SmoothPath · ForceSuccess · controller_id, bt_navigator 오류 수, job248 감사 |
| [`job346_mp4state.sh`](../debug_log/2026-09-16/jobs/job346_mp4state.sh) | mp4 직후 상태 · nav2.log · syslog 15:56~59 Wi-Fi · bag 토픽 수 |
| `job323_state.sh` · `job349_health.sh` · `job351_now.sh` | 프로세스 · 토픽 · 자세 한 장 |
| `job347_cancel.sh` · [`job353_stop2.sh`](../debug_log/2026-09-16/jobs/job353_stop2.sh) | 목표 취소 / 전체 정지(타임아웃 있는 판 — `ros2 topic pub -1` 대기를 안 씀, §1.13 교훈) |
| `edits_0916.py` · `b` · `c` · `d` | 저장소 · 스크래치패드 파일을 '정확히 1 번 나오는 문자열' 치환(assert)으로 일괄 편집: (무) 릴레이 · decay · 10 Hz · model_dt · visualize · BT · bag 토픽, (b) BT SmoothPath, (c) 러너 감사 재시도 · 좌측 경계, (d) DDS 루프백 화이트리스트 · 러너 export · stuck_shadow |
- 이것들은 결과보다 '그때 설치본이 무엇이었나' 의 증거다. 다시 쓰기: 안 씀(→ `chk_prep.py` · `params.txt` 스냅샷).

### 9.17 09-17 mp6 · mp7 분석 도구
| 도구 | 형태 · 하는 일 | 출력 |
|---|---|---|
| [`job373_mp6post.sh`](../debug_log/2026-09-17/jobs/job373_mp6post.sh) | nav2.log 마지막 'Begin navigating'(> 1789607900) 이후 이벤트(상대 초) + 드라이브 로그 요약 줄 + bag tgz | SUMMARY §2 표의 원천(원문 화면은 `drive_mp6.txt` 에 일부) |
| [`job374_mp6ana.sh`](../debug_log/2026-09-17/jobs/job374_mp6ana.sh) | job327(t 26~60, ASCII t 34) + job345(t 30~55) | `outputs/j374_mp6.txt` |
| [`job376_goalview.sh`](../debug_log/2026-09-17/jobs/job376_goalview.sh) | job327 ASCII t 54 + bag 의 **마지막** 전역 코스트맵에서 목표 (2.20, 0.01) 셀 비용 · 주변 비용표(y +0.30 → −0.40, x 1.90 → 2.50) · 목표 근처(x 1.8~2.8, y −0.8~+0.6) LETHAL 범위와 최근접 거리 | `outputs/j376_mp6.txt`(0.367 m) |
| [`job377_goalclear.py`](../debug_log/2026-09-17/jobs/job377_goalclear.py) `D LAT [YAW]` | **목표 여유 게이트**: 현재 map 자세 기준 (D, LAT) 를 map 으로 → 전역 코스트맵 LETHAL 셀을 목표 자세 좌표로 옮겨 직사각형(반길이 0.26 · 반폭 0.175 = 0.165 + 패딩 0.01)까지 거리 최소, 마지막 줄 여유(m). 러너는 ≥ 0.20 | prep 출력 · 러너. (D, LAT) 는 **지금 자세** 기준이라 로버가 출발점에 있을 때만 러너 목표와 같은 자리(머리 주석의 'map 원점 · yaw ≈ 0' 전제). 전역 격자 0.05 m 셀 **중심** 기준. 다시 쓰기: 개념 유효(→ `place_server` 목표 여유 검사, F2.5) |
| [`job378_goalcands.sh`](../debug_log/2026-09-17/jobs/job378_goalcands.sh) | BT 에 TruncatePath 로드 · bt_navigator 오류 수 + 후보 7 곳(2.2/0 · 2.0/0 · 1.9/0 · 2.0/0.2 · 2.1/0.3 · 2.2/0.3 · 2.0/−0.2)의 job377 | `prep_mp7.txt` · `prep_mp8.txt` |
| [`job379_navevents.sh`](../debug_log/2026-09-17/jobs/job379_navevents.sh) `NAME` | 마지막 'Begin navigating' 이후 nav2.log(경로 전달 · smoother 수신 · 정적층 크기 줄 제외) + 드라이브 표 1 s + bag tgz + 주행 후 SLAM 생존(job386) + map 자세 + `top_NAME.log` 의 프로세스별 CPU 평균 · 최대 | `j379_mp7_events.txt` ~ `j379_mp12.txt` |
| `job380_health.sh` · `job381_slam.sh` · `job382_slamgraph.sh` · `job383_slamlast.sh` · `job384_power.sh` · `job385_pmhist.sh` | mp7 뒤 상태(프로세스 · hz · TF 지연 · CPU), slam_toolbox 스레드 · `/map` hz · map→odom, 그래프 존재 · 스레드 상태 · wchan · utime, bag 의 map→odom 간격(goal 기준 0.5 s 넘는 공백 목록), 전력 모드 · CPU 주파수 · nvpmodel 이력 | `j380_health.txt` · `j381_slam.txt` · `j382.txt`, 383 · 384 · 385 는 SUMMARY 인용만. 해설은 `slam-dds-deadlock.md`(다른 카드) |
| [`job386_slamalive.py`](../debug_log/2026-09-17/jobs/job386_slamalive.py) | **SLAM 생존 게이트**: 5 s 동안 `/tf` 의 map→odom 수신 간격 최대 · (수신 시각 − stamp) 최대 → 간격 < 0.5 s **그리고** 지연 < 1.0 s 면 OK. `job254_s4run.sh` · prep · `job405_recheck.sh`(3 회) 에서 사용 | 이후 10-21 §9 · 10-27 §24 에서 다시 쓰임(색인 `JOBS.md`) — 계보 끝은 `Docs/tools/chk_drive_gate.py` |
| `edits_0917.py` · `b` · `c` · `d` | BT fallback · 목표 게이트 훅, bag 토픽에서 `/trajectories` 빼고 top 기록, job254 에 SLAM 생존 검사, nav2_params 의 크리틱 문턱 · GoalCritic(정규식 1 회 치환 assert) | 커밋 `7eaf0b09` · `6facf928` · `722e5c32` |

### 9.18 09-17 mp8 · mp9 · mp11 분석 도구
| 도구 | 형태 · 하는 일 | 출력 |
|---|---|---|
| [`job394_cmdtrace.py`](../debug_log/2026-09-17/jobs/job394_cmdtrace.py) `BAG G` | 구간(25~35 · 35~40 · 40~50 · 60~62 · 80~90 s)별 `/cmd_vel` 수 · 최대 간격 · 값 상위 4, `/wheel_odom` v · ω 평균, `/rover/status` 마지막 메시지 | `j394_mp8.txt`(35 s 이후 명령 0.009 · wheel 0) |
| [`job395_status.py`](../debug_log/2026-09-17/jobs/job395_status.py) `BAG G` | `/rover/status` 키-값(uptime · 카운터 제외)이 **바뀔 때만** 한 줄 + 같은 시각 cmd · wheel 속도 | `j395_mp8.txt`(37.3 s L tgt 10 · R 0, 38.1 s 부터 양쪽 0) — 펌웨어 문턱 결함의 실측 근거 |
| `edits_sim_db.py` | job355 에 펌웨어 휠 속도 모델 인자(db · promote · eps · track_b · prune) 삽입 | job355 09-17 판 |
| [`job404_lowtgt.py`](../debug_log/2026-09-17/jobs/job404_lowtgt.py) `BAG G` | `/rover/status` 의 L · R 문자열에서 tgt · v 를 정규식으로 → 0 < \|tgt\| < 10 mm/s 인 샘플(옛 펌웨어라면 버려졌을 것), 비영 `/cmd_vel` 중 가장 작은 명령 · 안쪽 휠 속도(반궤간 0.2215) | `j404_mp9.txt`(210 중 12, 최소 v 0.005) |
| [`job403_critics_rb.sh`](../debug_log/2026-09-17/jobs/job403_critics_rb.sh) | GoalCritic · 세 문턱 · PathFollow 가중 · offset · visualize · `default_server_timeout` readback + SLAM 생존 + 목표 (2.0, 0) 여유 + 배터리 | `prep_mp9*.txt` |
| [`job405_recheck.sh`](../debug_log/2026-09-17/jobs/job405_recheck.sh) | SLAM 생존 3 회(2 s 간격) + 두 파라미터 + load | mp10 준비(첫 1.12 s FAIL → 3 회 OK) |
| [`job406_bandcells.sh`](../debug_log/2026-09-17/jobs/job406_bandcells.sh) | 감사의 '근거 없는 셀' 좌표 + 필터 점군 4 s 를 base_link 로 → 통로 띠(x 0.3~1.6, y −0.1~0.5, z 0.05~0.3) 점을 상자(x 1.1~1.35, y < 0.12) · 그 외로 | mp11 준비(띠 점은 상자 130 뿐 → 셀 7 은 사람 자취로 **추정**). 출력 원문 없음 |

### 9.19 기동 · 정지 (참고)
- `job240_clean.sh`(09-11 제정 '깨끗한 기동', [09-16 판](../debug_log/2026-09-16/jobs/job240_clean.sh)): base → sensors → slam → nav2 순 기동 · 검증 · 클리어 · 재마킹 대기. 해설은 [컨트롤러 카드 §9.9](controller-rpp-vs-mppi.md).
- `job249_nav2only.sh`([09-16 판](../debug_log/2026-09-16/jobs/job249_nav2only.sh)): YAML 검증 뒤 Nav2 만 재기동. 09-16 에 '충돌 지평 == 1.5' 낡은 assert 를 제거(09-14 의 0.75 가 배포를 막음) — 검증 스크립트가 설정을 굳히는 위험의 예.
- `job156_stop.sh`(전체 종료 — `ros2 topic pub -1` 에서 무한 대기, 09-16 §1.13) → `job353_stop2.sh`.

## 10. 용어
- **MPPI(Model Predictive Path Integral)**: 매 주기 제어열(평균) 주변에 잡음을 더한 후보 batch 개를 time_steps 만큼 굴려 보고, 크리틱 비용으로 softmax 가중평균해 평균열을 갱신하는 샘플링 컨트롤러. 첫(Humble 1.1.20 에서는 필터 뒤 [1]) 제어를 낸다.
- **time_steps · model_dt · 지평**: 후보 한 개의 길이 = time_steps × model_dt 초. 거리로는 × 속도 — 0.08 m/s 에서 32 × 0.05 = 1.6 s = **0.128 m**, 56 × 0.05 = 2.8 s = 0.22 m, 32 × 0.1 = 3.2 s = **0.26 m**. model_dt 는 1/controller_frequency 와 맞춰야 주기마다 제어열을 한 칸 밀어 재사용하는 shift 가 맞는다(09-16 §1.5 기각 대안).
- **batch_size · iteration_count**: 후보 수(1,000)와 한 주기 안 최적화 반복 수. 연산량 ∝ batch × time_steps × iteration × 주기.
- **vx_std · wz_std**: 후보 잡음의 표준편차(선속도 · 각속도). 크면 넓게 탐색하지만 평균이 흔들린다.
- **temperature**: softmax 의 날카로움. 작으면 최저 비용 몇 개만 반영(유효 표본 수 ↓, 평균이 표본 잡음을 많이 탐), 크면 평균에 가깝다. **gamma**: 평균열에서 벗어난 잡음에 주는 비용(제어 부드러움 항)의 크기.
- **furthest(`furthest_reached_path_point`)**: 후보들의 끝단이 닿은 경로 점 index 중 **배치 전체 최대**. 경로 계열 크리틱이 이것을 공유한다 — 후보가 짧게 모이면(저속 · 표본 붕괴) furthest 가 작아진다.
- **offset_from_furthest**: 크리틱이 furthest 에서 몇 점 앞을 기준으로 삼는가. **경로 점간격에 곱해 거리로 읽어야 한다**(0.025 m 간격에서 5 점 = 12.5 cm, 20 점 = 0.5 m). Nav2 기본값은 0.5 m/s · 1.4 m 지평 로봇을 가정.
- **PathFollowCritic**: 끝단 ↔ path[furthest + offset] 거리에 가중 — '당근' 으로 앞으로 당기는 **가속기**. 당근이 짧으면 진행해도 비용이 거의 안 준다(09-16 §1.14).
- **PathAlignCritic**: furthest ≥ offset 일 때만, 후보 점(trajectory_point_step 마다)이 경로에서 떨어진 거리 평균에 가중 — 경로 위에 있기. 이동할수록 잡음 편차가 커져 **브레이크** 처럼 작동할 수 있다. `max_path_occupancy_ratio`: 경로가 장애물에 많이 덮이면 끔.
- **PathAngleCritic**: 현재 자세 → path[furthest + offset] 방향과의 각이 `max_angle_to_furthest` 보다 클 때만 끝단 heading 오차에 가중 — 큰 방향 오차를 회전으로 풀게 함. 목표점이 가까우면 각이 문턱을 못 넘어 비활성(job355 I · J).
- **threshold_to_consider**: 경로 계열 크리틱은 목표까지 이 거리 **안에서 꺼지고**, Goal · GoalAngle 크리틱은 이 거리 안에서만 켜진다. 둘 사이가 '크리틱 교대 구간'(09-16: Follow 0.6 · Align 0.4 · Angle 0.4 ↔ Goal 1.0 · GoalAngle 0.4 → 09-17 경로 0.2).
- **GoalCritic · GoalAngleCritic**: 끝단 ↔ 목표 위치 거리 · 목표 방향 오차에 가중. GoalAngle 은 목표 yaw 를 요구하므로 회전이 막힌 자리에서는 반대쪽으로 끌 수 있다(mp5).
- **ObstaclesCritic(09-17 까지)**: `consider_footprint` 면 둘레 최대 비용에서 거리를 역산(크리틱 자기 `cost_scaling_factor` · `inflation_radius`, 우리 YAML 에 없어 기본 10/0.55), LETHAL 이면 collision_cost, `collision_margin_distance` 안이면 critical_weight × 부족분, 아니면 repulsion_weight × (반경 − 거리). 09-21 부터 **CostCritic**(중심 칸 비용, 충돌은 둘레 검사)으로 교체.
- **PreferForwardCritic · ConstraintCritic**: 후진량에 벌점 · 속도 한계 초과분에 벌점.
- **표본 붕괴**: 평균 제어가 0 근처로 내려가면 후보 끝단이 로버 주변 수 cm 안에 모여(끝단 산포 ≈ std/√steps × 지평) 내접 띠 너머 출구를 보는 후보가 없어지는 상태(09-16 §1.13). 이 카드에서는 원인이 아니라 결과로 정리(실수 ③).
- **변환 경로(`/transformed_global_plan`)**: 컨트롤러가 전역 경로를 odom 으로 옮기고 로버 주변 `prune_distance`(1.0 m)만 잘라 쓰는 경로. `visualize: true` 일 때만 발행.
- **SmoothPath(simple_smoother)**: 격자 경로의 꺾임을 반복 평활(w_smooth 0.3 · w_data 0.2)하는 Nav2 smoother 서버 액션. `check_for_collisions` 면 평활 결과가 충돌이면 실패를 낸다 — 모서리를 깎다가 실패하는 일이 상자 뒤에서 반복(mp6 · mp9).
- **목표 여유 게이트 · SLAM 생존 게이트**: job377 · job386(§9.17).
- **창(통로 창)**: 로버 **중심**이 지날 수 있는 횡 폭 = 좌측 통과 구간 경계 − (상자 셀 최대 y + 0.195). 0.195 의 함정은 §6.
- **STVL `voxel_min_points`(필터 voxel)**: 깊이 점을 월드 정렬 복셀(0.05 m)로 묶어 복셀당 이 수 미만이면 마킹하지 않음. `voxel_decay`: 마킹된 복셀의 선형 감쇠 수명(초).
- **승격 · 정지 문턱**: [기동 데드밴드 카드](start-deadband.md).
