# 오프라인 MPPI 시뮬레이터 — job355 → job410 → job419 → job452 (→ job776 → anal_mppi_sim)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **도구 카드 · 계속 쓰는 중**(현재판 [`Docs/tools/anal_mppi_sim.py`](../tools/anal_mppi_sim.py), 10-13 고정 이름). 이 카드는 09-16 ~ 09-18 판을 코드 수준으로 풀고, 그 뒤 판은 '이후' 로 가리킨다 | 09-16 §1.14 ~ 09-18 §17.2 (이 카드), 이후 09-21 · 10-01 · 10-08 · 10-13 · 10-14 · 10-26 | [09-16 §1.14 '회피 로직과 추종 로직이 충돌하는가'](../debug_log/2026-09-16/SUMMARY.md) | 도구만(설정 파일 아님): `2026-09-16/jobs/job355_mppi_sim.py` → `2026-09-17/jobs/job355_mppi_sim.py`(같은 이름, 내용 다름) → `job410_mppi_sim_lag.py` → `job419_mppi_sim_humble.py` → `2026-09-18/jobs/job452_mppi_sim_cc.py` → `2026-10-01/jobs/job776_mppi_sim_ack.py` → `Docs/tools/anal_mppi_sim.py` | [조향 흔들림 · temperature](mppi-wobble-temperature.md) · [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md) · [컨트롤러 선택 RPP vs MPPI](controller-rpp-vs-mppi.md) |

**한 줄**: bag 의 한 순간(로컬 코스트맵 · 경로 · 로버 자세 · 마지막 명령)을 잘라 그 위에서 Nav2 Humble MPPI 의 '표본 1000 개 → 크리틱 → softmax 가중 평균' 을 파이썬으로 흉내 내고, 로버를 그 첫 명령으로 움직이며 6~20 s 를 굴려 파라미터 변형을 비교하는 도구. 첫 판(09-16)은 '기어감' 정체를 재현하는 데는 맞았지만, 09-17 에 temperature 예측이 실주행에서 크게 빗나간 뒤 설치본 1.1.20 소스와 대조해 **네 가지 동작 차이**(잡음 재사용 · 후보 clip · 스텝 0 속도 · SG 필터)를 고쳤고(job419 `humble=1`), 09-18 에 CostCritic 을 넣었다(job452). 그 뒤에도 '구동계 = 회전만 ×0.7' 모델이 틀렸다는 것(10-26, 실제는 바퀴 포화로 v · ω 함께 축소)과 '씨앗(잡음 한 벌)에 결과가 크게 흔들림'(ESS 10~20)이 드러났다. **결과의 방향(어느 손잡이가 정체를 푸는가)은 여러 번 실주행과 맞았고, 크기(cm · 회/m · %)는 맞지 않은 때가 많다** — 아래 §6 표.

## 1. 증상(왜 만들었나)
- 09-16 mp2~mp4: 상자 옆 입구에서 v 0.035 → 0.012 로 '기어가다' 정지. `/trajectories`(job345)로 후보 끝단 분포가 붕괴(앞 5 cm 이상 후보 78 → 2 %)함은 봤지만, **어떤 크리틱 가중을 바꾸면 풀리는지**는 실주행 한 번에 한 변수씩 시험하기엔 비쌌다(한 회 ≈ 수 분 + 배치 · 게이트). 사용자 질문 "회피 로직과 추종 로직이 충돌하는가, 과한 값인가"([09-16 §1.14](../debug_log/2026-09-16/SUMMARY.md)).
- 그래서 bag 장면 위에서 MPPI 최적화를 직접 돌려 '정지 장면에서 6 s 동안 얼마나 나아가나' 를 변형별로 비교한 것이 시작.

## 2. 흐름 (판별 계보)
| 날짜 · § | 판 | 무엇을 더했나 | 쓰인 결과(수치) | 실주행과 맞았나 | 데이터 |
|---|---|---|---|---|---|
| 09-16 §1.14 | `job355_mppi_sim.py`(09-16 폴더) | 첫 판: 배치 1000 · 32 step · 0.1 s, 크리틱 7 종 근사, softmax, 정적 장면 | mp4 t=17: A(mp4 값) 4 s 7 cm · v 0.012(기어감 재현), B(배포값) 0.087, C(offset 20) 0.143, **F(PathFollow 10 · offset 20) 0.250 m · −26°**, E · L · I/J/K 는 F 와 같거나 미미 | **방향 맞음** — mp5 가 입구를 v 0.04~0.08 로 통과(09-16 §1.15) | [j355_ab.txt](../debug_log/2026-09-16/outputs/j355_ab.txt) · [j355_cdefgh.txt](../debug_log/2026-09-16/outputs/j355_cdefgh.txt) · [j355_ijkl.txt](../debug_log/2026-09-16/outputs/j355_ijkl.txt), 배치 `job356~358_variants*.sh`, bag `2026-09-16/bags/bag_mp4.tgz` |
| 09-16 §1.15 | 같은 판 | 목표 근처 크리틱(Goal · GoalAngle · 문턱) 변형 | mp5 t=29 복귀: M(현재) 0.23 m / 6 s(**실제는 정지**), N(문턱 0.2) 0.26, P(+goal_w 10) 0.31, O(GoalAngle 끔) 0.31 | **크기 틀림**(실제 정지를 진행으로 봄 — 정적 장면 · 1 Hz 재계획 없음, 표본 충돌률 35 % 경계) | [j366_mp5_return.txt](../debug_log/2026-09-16/outputs/j366_mp5_return.txt), `job366_mp5sim.sh` |
| 09-17 §7.2 | `job355_mppi_sim.py`(09-17 폴더) | 펌웨어 휠 처리(`eps` · `promote` · `db`) · `/transformed_global_plan` 이 없을 때 `/plan` 을 map→odom 으로 옮겨 1 m 가지치기(`prune`) · 흔들림 지표 | mp8 t=33, 12 s: S1(현재) 목표 거리 0.234(실측 0.243 재현) → S3(경로 크리틱 문턱 0.2) 0.144 → S5(+GoalCritic 10) **0.116** | **방향 맞음** — mp9~11 3/3 성공(09-17 §9~11) | [j396_goalsim8.txt](../debug_log/2026-09-17/outputs/j396_goalsim8.txt), `job396_goalsim8.sh`, bag `bag_mp8.tgz` |
| 09-17 §12.3 | `job410_mppi_sim_lag.py` | 구동계(smoother ω 가속 · 지연 큐 · v/ω 이득), ESS 기록, 목표 허용오차 첫 진입 시각, 명령/차체 흔들림 분리 | temperature 0.3 이면 통로 반전 0 · RMS 0.032~0.040 · 진행 −15~−23 % | **틀림** — mp12(T 0.3) 반전 8.8 /m · RMS 0.059 · 가장 빠름(09-17 §13.3) | [j413_wobblecause.txt](../debug_log/2026-09-17/outputs/j413_wobblecause.txt) · [j412_tempsim2.txt](../debug_log/2026-09-17/outputs/j412_tempsim2.txt) |
| 09-17 §14.1~14.5 | `job419_mppi_sim_humble.py` | `humble=1`: (a) 고정 잡음 (b) 후보 clip 없음 + ConstraintCritic (c) 스텝 0 = 측정 속도 (d) SG 필터 → 출력 [1]. `regen` · `dyn_path` · `dyn_cost` 재생 | 속도는 실측과 맞음(6 s 0.41~0.48 m, T 0.3 도 안 느려짐). 흔들림은 고정 잡음이면 과소, 새 잡음이면 실측 크기 | **속도 맞음, 흔들림 크기는 '교란' 가정 없이 못 맞춤** | [j420_humblesim.txt](../debug_log/2026-09-17/outputs/j420_humblesim.txt) · [j421b_dynsim.txt](../debug_log/2026-09-17/outputs/j421b_dynsim.txt) · [j423_regensim.txt](../debug_log/2026-09-17/outputs/j423_regensim.txt) |
| 09-18 §17.2 | `job452_mppi_sim_cc.py` | `obst=0/1/2`(Obstacles/Cost/둘 다), 두 크리틱의 `near_goal_distance`(`near_thr`), `t_abs`, 주기별 LETHAL 여유 | dy2 · dy4 · dy6 × 3 장면 × seed 2: CostCritic 이 입구 +1.5 · 복귀 회전 +0.9 · 모서리 −0.3 cm(차이 없음), 입구 진행 −4 %, 모서리 반전 · RMS 소폭 증가 | **방향 맞음, 크기 과소** — 09-21 cc1~3 여유 8.4~10.8 cm(dy 2.5~5.1), 반전은 오히려 줄어듦(2.0 · 1.05 · 5.2 /m) | [j452_sim_cc.txt](../debug_log/2026-09-18/outputs/j452_sim_cc.txt) · [j452_sim_cc_table.txt](../debug_log/2026-09-18/outputs/j452_sim_cc_table.txt), bag `2026-09-18/bags/bag_dy2 · dy4 · dy6.tgz` |
| 이후 10-01 §8.29 | `job776_mppi_sim_ack.py` | job452 + Ackermann 최소 회전 반경 \|ω\| ≤ \|v\|/r · 후진 거리 · 제자리 회전 시간 집계 | 서쪽 통로 입구 f2a10: ACK 절충(r 0.22) 15 s 회전 −31° · 제자리 0.4 s 등 | 이 카드 범위 밖 | [10-01 SUMMARY](../debug_log/2026-10-01/SUMMARY.md) |
| 이후 10-08 | job776(`job944_fwdsim.sh` · `job946_fwdseed.sh`) | PreferForward 평가 | — | 범위 밖 | [10-08 SUMMARY](../debug_log/2026-10-08/SUMMARY.md) |
| 이후 10-13 §7~§11 | `anal_mppi_sim.py`(job776 고정 이름) | `fpchk=1`(Nav2 식 칸 단위 풋프린트 검사 — 꼭짓점 4 개 Bresenham), '후보 전부 충돌' 주기를 실패로 셈, `pad` | 상자 옆 정지 재현 시도. **정정**(10-13 SUMMARY 328 행): '시뮬이 옛 ObstaclesCritic 기준이라 고쳐야 한다(반나절)' 는 확인 없이 한 말 — job452 · job776 이 이미 CostCritic | 범위 밖 | [10-13 SUMMARY](../debug_log/2026-10-13/SUMMARY.md) |
| 이후 10-14 | 같은 도구 `unstuck=1` | 갇혔을 때만 패딩 0 흉내 | — | 범위 밖 | [10-14 SUMMARY](../debug_log/2026-10-14/SUMMARY.md) |
| 이후 10-26 §10 | 같은 도구 `resample` · `wheel_max` · dev 기록 | **구동계 정정**: 옛 `w_gain 0.7`(회전만)은 곡률을 바꿔 깎기를 가렸다 → `wheel_max=0.085` 비례 축소. 재현 판 씨앗 1·2·3 안쪽 최대 9.7 · 9.6 · 20.2 cm(실제 15.7 이 범위 안). ESS 10~20 → 변형 비교는 씨앗 6 개씩 | 재현됨(범위로) | [10-26 SUMMARY §10](../debug_log/2026-10-26/SUMMARY.md) |

## 3. 가설과 판별(도구의 충실도에 관한 것)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 정적 장면 + 근사 크리틱이어도 '크기 순서' 는 믿을 수 있다(09-16 §1.14) | A 변형이 mp4 의 기어감(v 0.035 → 0.012, 4 s 7 cm)을 재현 | 09-16 F → mp5 통과, 09-17 S5 → mp9~11 성공 | **지지**(정체를 푸는 방향) |
| 같은 모델로 흔들림 · 속도의 크기도 예측할 수 있다(09-17 §12) | mp12 실주행 | 반전 · RMS · 속도 모두 빗나감 | **기각** |
| 실제 1.1.20 과 동작이 같다 | 설치 헤더 grep(job418) + 같은 태그 소스 | 4 가지 차이(§4.3) | **기각 → job419 로 수정** |
| 고친 모델(job419)은 흔들림 크기를 재현한다 | job420 · job423 | 고정 잡음(실제 기본)이면 과소, 매 반복 새 잡음이면 맞음 | **부분**(시뮬에 없는 주기마다 교란이 있다고 가정해야 맞음 — 교란원 미확인) |
| 재계획 · map→odom · 코스트맵 변화를 재생하면 달라진다 | `dyn_path=1/2` · `dyn_cost=1`(job421b) | 체계적 차이 없음, 코스트맵 재생은 소수점까지 같음 | 이 장면에선 **영향 없음**(bag 코스트맵 2 Hz 한계) |
| '회전만 ×0.7' 구동계가 실제 손실을 대표한다 | 10-26 §10.1 명령 대 움직임 | 실제는 바깥 바퀴 0.085 포화로 v · ω 함께 축소(곡률 유지) | **기각**(10-26) — 09-17 · 09-18 결과에 이 결함이 들어 있음 |
| 씨앗 2~3 개로 변형을 비교할 수 있다 | 10-26 §10.2 | ESS 10~20 이라 씨앗 간 안쪽 최대 9.6 vs 20.2 cm | **기각**(10-26) — 09-18 job452 의 seed 2 비교는 이 잡음 안에 있을 수 있음 |

## 4. 도구 해설 — 판별로 코드 수준
### 4.1 job355_mppi_sim.py (09-16 판, 177 행)
- **실행 위치**: Jetson(`rosbag2_py` · `rclpy.serialization` 필요). PC 의 WSL 에서 `run_j356.sh` 가 `scp` 로 `/tmp/job355_mppi_sim.py` 와 배치 스크립트를 올리고 `ssh` 로 바로 실행(timeout 1500 s, nohup 아님).
- **부른 형태**: `python3 job355_mppi_sim.py /tmp/bag_mp4 17 label=F vx_std=0.08 wz_std=0.4 temperature=0.15 iters=2 follow_w=10 follow_off=20 cycles=60 seed=1`. 첫 인자 = 압축 푼 bag 폴더(sqlite3), 둘째 = bag 첫 `odom→base_link` stamp 로부터의 초(T0 + t), 나머지 `key=val` 은 아래 기본값 사전 `P` 를 덮어씀.
- **기본값 `P`**(= 09-16 mp4 당시 YAML 근사): `vx_std 0.05 · wz_std 0.3 · temperature 0.3 · gamma 0.015 · iters 1 · batch 1000 · steps 32 · dt 0.1 · vx_max 0.08 · vx_min −0.06 · wz_max 0.38 · align_w 14 · align_off 3 · align_step 3 · follow_w 5 · follow_off 5 · angle_w 2 · angle_off 4 · angle_max 0.5 · rep_w 1.5 · crit_w 20 · margin 0.05 · coll_cost 10000 · fwd_w 5 · infl_r 0.40 · scale 2.5 · r_in 0.175 · goal_w 5 · goal_thr 1.0 · ga_w 3 · ga_thr 0.4 · follow_thr 0.6 · align_thr 0.4 · angle_thr 0.4 · goal_yaw 0 · cycles 40 · seed 1`. 차체 반길이 0.25 · 반폭 0.165 · 패딩 0.01.
- **입력(bag 에서 읽는 것)**: `/tf` 의 `odom→base_link`(자세, header stamp 기준), `/local_costmap/costmap`(OccupancyGrid), `/transformed_global_plan`(컨트롤러가 받은 odom 경로 — `visualize: true` 일 때만 발행), `/cmd_vel`(초기 평균 제어). 각각 t 이전 마지막 메시지 하나만 씀 → **정적 장면**.
- **코스트맵 환산**: 발행값 0~100 → costmap_2d 비용 `1 + (o−1)·251/97`(1~98), 99 → 253(내접), 100 → 254(LETHAL), −1 → 255(미지).
- **한 주기의 계산**(`cycles` 번, 각 주기 안에서 `iters` 번 반복):
  1. 잡음 `nv ~ N(0, vx_std)`, `nw ~ N(0, wz_std)` 를 (1000, 32) 로 **매 반복 새로** 뽑고, 후보 = 평균열 + 잡음을 `[vx_min, vx_max]` · `[−wz_max, wz_max]` 로 **clip**.
  2. 롤아웃(DiffDrive): θ = θ₀ + cumsum(ω)·dt, x · y 는 스텝 시작 heading 으로 cumsum(v cos θ · dt).
  3. 크리틱(배치 전체 벡터 연산):
     - **Obstacles**(1.1.x obstacles_critic 근사): 중심 칸 비용 c 가 `POSS_INSCR = 253·exp(−2.5·(hypot(0.26, 0.175) − 0.175))`(외접 반경의 비용) 이상이면 차체 둘레 72 점(긴 변 21 점 × 2, 짧은 변 15 점 × 2)의 최대 비용으로 교체. 충돌 = 254 이상 또는 (253 이고 둘레 모드 아님). 거리 역산 d = (2.5·0.175 − ln c + ln 253)/2.5(둘레 모드가 아니면 d − 0.175). d < margin 이면 crit += margin − d, 아니면 rep += infl_r − d. 비용 = 충돌이면 10000, 아니면 20·Σcrit + 1.5·Σrep/32.
     - **배치 furthest**: 후보마다 끝점에 가장 가까운 경로 index, 그 최댓값 하나를 모든 크리틱이 공유(1.1.x `furthest_reached_path_point`).
     - **PathAlign**: furthest ≥ align_off 이고 목표까지 ≥ align_thr 일 때, 3 스텝마다의 점 ↔ 경로 최근접 거리 평균 × 14(점유율 검사 `max_path_occupancy_ratio` 등 정규화 세부는 생략).
     - **PathFollow**: 목표까지 ≥ follow_thr 일 때 끝점 ↔ `path[furthest + follow_off]` 거리 × follow_w.
     - **PathAngle**: 현재 자세에서 `path[furthest + angle_off]` 방향 오차 > angle_max 일 때만, 끝점 heading 오차 × angle_w.
     - **Goal** · **GoalAngle**: 목표까지 < goal_thr(1.0) 이면 끝점 ↔ 목표 × goal_w, < ga_thr(0.4) 이면 |끝 yaw − goal_yaw| × ga_w.
     - **PreferForward 근사**: fwd_w · Σmax(−v, 0)·dt.
  4. 제어 비용(1.1.x `updateControlSequence`): cost += γ/σ_v² · Σ(평균_v · (후보_v − 평균_v)) + γ/σ_ω² · Σ(평균_ω · (후보_ω − 평균_ω)), γ = 0.015.
  5. **softmax**: w = exp(−(cost − min)/temperature), 정규화 → 새 평균열 = Σ w·후보.
  6. 로버 이동: 평균열 [0] 을 dt 동안 적용(완전 추종, 구동계 없음) → 평균열을 한 칸 당기고 끝을 복사.
- **출력**: 2 주기마다 `cyc | 명령 v w | 로버 x y yaw | furthest | 후보 충돌 % | 끝단 전방 중앙/최대 | 평균 비용(전체 · obst · align · follow · angle+goal) | 최저 후보 v w | 평균열 최대 둘레비용/첫 충돌 스텝` 와 마지막 '→ N 주기 후 전진 · 횡 · 회전 · 최종 v w'. 원문은 `2026-09-16/outputs/j355_*.txt` · `j366_mp5_return.txt`.
- **알려진 결함**(이후 판에서 발견): §4.3 의 4 가지, 정적 장면, 재계획 없음, 구동계 없음, PathAlign 정규화 생략, near_goal 처리 없음(ObstaclesCritic 반발이 목표 근처에서도 켜짐 — job452 에서 추가).
- **지금 다시 쓸 수 있나**: bag(`2026-09-16/bags/bag_mp4.tgz` 등)과 Jetson ROS 환경만 있으면 같은 seed 로 같은 결과(numpy `default_rng(seed)` 고정). 다만 새 질문에는 현재판을 쓴다.

### 4.2 job355_mppi_sim.py (09-17 판, 207 행) — 같은 이름, 다른 내용
- 09-16 판과의 차이(diff): ① `db · promote · eps · track_b 0.443` — **펌웨어 휠 처리 흉내**: 평균열 [0] 을 바퀴 속도 v ∓ ω·B/2 로 나눈 뒤 바퀴마다 |v| < eps(0.003) → 0, < promote → ±promote 로 올림, < db(정지 문턱) → 0, 다시 v · ω 로 합침. ② `/transformed_global_plan` 이 없으면(09-17 mp7 부터 `visualize: false`) **`/plan`(map) 을 그 시각 `map→odom` 으로 odom 에 옮기고 로버 최근접점부터 `prune`(1.0 m)만 남김**. ③ 매 주기 적용 ω 기록 → '흔들림: |ω|>0.05 반전 회/m · 고주파 RMS(ω − 10 점 이동평균)' 와 목표까지 거리 출력.
- 왜: 09-17 §7 mp8 '목표 0.24 m 옆에서 정지' 의 원인 1(펌웨어 정지 문턱 0.010 vs 승격 0.008 불일치)과 원인 2(목표 근처 크리틱 교대)를 함께 재현하려고(`job396_goalsim8.sh`: `FWNOW eps 0.003 promote 0.008 db 0.010` vs `FWFIX promote 0.012`).
- 그 뒤 job408(흔들림 첫 배치)도 이 판으로 돌았다(`db=0.005` = §8 펌웨어 수정 뒤 값).
- 주의: ② 의 `/plan` 은 NavFn **원경로**다. 실제 컨트롤러는 BT 의 SmoothPath 결과를 받았는데 그것은 bag 에 없었다(09-18 §17.3 에서 `/plan_smoothed` · `/unsmoothed_plan` 기록 추가). 09-18 §15.1 측정으로 스무더가 옆 위치를 ≤ 0.5 cm 만 바꾼다고 나왔으므로 위치 영향은 작지만, **점 간격**(경로 크리틱 offset 이 점 개수)이 다르면 당근 거리가 달라진다 — 10-26 에 `resample` 을 넣은 것과 같은 문제이며 09-17 판에서의 영향은 **미확인**(출력 머리의 '경로 41점(간격 0.047)' 은 첫 두 점의 간격만 찍은 것이라 이것으로 판단 못 함).

### 4.3 job410_mppi_sim_lag.py (09-17, 225 행)
- 09-17 판 job355 + 다음:
  - `lag_steps`(지연 큐, 주기 단위) · `w_gain` · `v_gain` · `w_acc`(velocity_smoother ω 가속 제한 rad/s²). 적용 순서(저장본): 평균열 [0] → **ω 가속 제한**(직전 ω 에서 ±w_acc·dt 안으로) → 기록(=bag `/cmd_vel` 에 해당) → 지연 큐 → ×이득 → 펌웨어 처리 → 로버 이동. MPPI 내부 롤아웃은 이 구동계를 모른다(실제와 같음).
  - **ESS** = 1/Σw²(각 주기 마지막 반복)의 중앙 · 10/90 % 와 `wz_std/√ESS`.
  - 흔들림을 명령(가속 제한 뒤) · 차체(이득 · 펌웨어 뒤) 둘로.
  - 목표 xy 0.15 첫 진입 주기(goal checker 대용).
- 쓰인 곳: job411(옛 판, 폐기) · job412 · job413 → [흔들림 카드](mppi-wobble-temperature.md) §12.3~12.6.
- 알려진 결함: 09-16 판의 4 가지 그대로 + 구동계가 '회전만 상수 이득'(10-26 에 기각) + 상수 지연.

### 4.4 job419_mppi_sim_humble.py (09-17 §14, 303 행) — `humble=1` 의 네 가지
설치본 `ros-humble-nav2-mppi-controller 1.1.20` 헤더(`job418_mppisrc.sh` → [j418_mppisrc.txt](../debug_log/2026-09-17/outputs/j418_mppisrc.txt) · [j418b_sgfilter.txt](../debug_log/2026-09-17/outputs/j418b_sgfilter.txt) · [j418c_motion.txt](../debug_log/2026-09-17/outputs/j418c_motion.txt))와 같은 태그 github 소스(`optimizer.cpp` · `noise_generator.cpp` · `critics/constraint_critic.cpp` — PC 사본 없음)로 확인한 동작(메모리의 '1.1.20 동작 4 가지'):
| | 실제 1.1.20 | job355 · job410 | job419 `humble=1` 의 코드 |
|---|---|---|---|
| (a) 잡음 | `regenerate_noises` 기본 false → 초기화 · `reset()` 때만 생성, 모든 주기 · 반복에 재사용. reset 은 주행당 mp9 1 · mp10 3 · mp11 1 · mp12 3 회 | 매 반복 새로 | 시작 때 `NVF · NWF` 한 번 생성. `regen=1` 이면 매 반복 새로(A/B 용) |
| (b) 후보 한계 | 후보 clip 없음(`setNoisedControls` = 평균 + 잡음). vx 초과는 ConstraintCritic(가중 4 · Σ초과 · dt), **wz 는 벌점 없음**. 갱신된 평균열만 clip | 후보 clip | 후보 = 평균 + 고정 잡음(clip 없음), 비용 += 4 · Σ(max(v − vx_max, 0) + max(vx_min − v, 0))·dt, 갱신 뒤 평균열만 clip |
| (c) 롤아웃 속도 | 스텝 0 = 측정 속도(`/odometry/filtered` twist), 스텝 k = 제어 k−1(`DiffDrive::predict`) | 스텝 k = 제어 k | `Vs = [MEAS, V[:, :-1]]`. MEAS 는 직전 주기에 차체에 실제로 걸린 (v, ω)(지연 · 이득 · 펌웨어 반영) |
| (d) 출력 | 최적화 뒤 **Savitzky-Golay 9 점 필터**(적용 이력 4 개, 소스상 index 27 은 건너뜀) → 주기 = model_dt 라 `shift_control_sequence` ON → **제어열 [1]** 출력 → 이력 갱신 → roll −1 | 필터 없음, [0] | `sg_filter()` 가 1.1.20 `utils::savitskyGolayFilter` 를 그대로: 계수 (−21, 14, 39, 54, 59, 54, 39, 14, −21)/231, 앞 4 점은 이력 4 개로 채움, `while i != n−4` 루프가 27 에서 멈추고 `i += 1` 로 28 부터 끝 4 점을 끝값 반복으로 — 결과적으로 27 번은 갱신되지 않음. 출력 [1], 이력에 [1] 추가 |
- 추가 인자: `cons_w`(4.0) · `regen` · `dyn_path`(1 = 같은 `/plan` 을 매 주기 로버 기준 재가지치기 — Humble `transformGlobalPlan` 흉내, 2 = + bag 의 `/plan` · `map→odom` 을 시각대로 재생) · `dyn_cost`(1 = bag 로컬 코스트맵을 시각대로 교체 — bag 은 2 Hz, 실제 갱신 5 Hz).
- 결과가 바꾼 것: 옛 모델의 'T 0.3 이면 −15~−23 % 느려진다' 가 clip 착시였음(clip 이 없으면 vx_max 초과 후보가 평균을 한계로 끌어올림 → v 0.08 포화 유지, mp12 실측과 일치). 09-16 §1.14 · 09-17 §7 · §12 의 정량 예측은 신뢰도를 낮춰 본다(09-17 §14.1).
- 출력 · 쓰인 곳: [흔들림 카드](mppi-wobble-temperature.md) §14.2~14.5. 지금 다시 쓸 수 있음(이후 판이 상위 호환).

### 4.5 job452_mppi_sim_cc.py (09-18 §17.2, 311 행)
- 왜: ObstaclesCritic → CostCritic 교체 전 '정체 · 입구 지연 · 셀 계단 흔들림' 위험을 미리 보려고(09-18 §16 의 '잃음: 시뮬 사전 검증 불가' 를 해소).
- job419 + 다음:
  - `obst=0`(ObstaclesCritic, 위 §4.1 식) / `obst=1` **CostCritic**(1.1.20 `cost_critic.cpp` — 사본 `2026-09-18/refs/mppi_1.1.20_cost_critic.cpp`): 충돌은 Obstacles 와 같은 둘레 검사(중심 비용 ≥ 외접 비용일 때만 둘레 최대), 점수는 **중심 칸 비용**: c0 < 1 → 0, c0 ≥ 253 → `crit_cost`(300), 그 밖 c0. 궤적 비용 = (`cost_w`/254) · Σ/32(실제 소스: `weight_ /= 254`, `weight_ * repulsive_cost / traj_len`, 거듭제곱 1). / `obst=2` 둘 다.
  - `near_thr`(0.5): 로버 ↔ 경로 끝 < 0.5 m 이면 Obstacles 의 반발 항 · CostCritic 의 '중심 비용 선호' 항을 끔(소스의 `withinPositionGoalTolerance(near_goal_distance_, …)`). 09-17 판엔 없던 것.
  - `t_abs`(bag 절대 epoch 로 시각 지정), 주기별 **LETHAL 여유**(`lethal_clear`: 1 m 안 254 칸 중심 ↔ 패딩 없는 차체 외곽 − 반셀, job416 정의) → 최소(시각) · 평균 · 끝.
- 배치 `job452_run.sh`: dy4 · dy6 · dy2 × {goal + 8 s(입구 차선변경) · + 16.5 s(복귀 회전 시작) · + 20 s(상자 뒤 모서리)} × seed 1 · 2 × obst 0 · 1, 공통 = job421b 의 실측 구동계 + `temperature=0.15 near_thr=0.5 dyn_path=2 dyn_cost=1 cycles=60`. 36 판, 표는 손으로 정리(`j452_sim_cc_table.txt`, 감싸개 `run_j452.sh` · `run_j452chk.sh` · `run_j452get.sh`).
- 실제 소스와 남은 차이(이 카드 작성 중 `refs/` 대조): 충돌 궤적의 비용이 실제는 `collision_cost`(1e6)에도 가중 3.81/254/32 가 곱해지지만(≈ 469) 시뮬은 1e6 그대로 — 두 경우 모두 softmax 가중이 사실상 0 이라 결과 차이 없음. ObstaclesCritic 충돌 비용도 실제는 `critical_weight` 20 이 곱해짐(시뮬 10000) — 같은 이유로 무해.
- 결과 · 신뢰도: 위 §2 표. 09-21 실주행이 여유를 더 크게(8.4~10.8 cm vs 시뮬 +0.9~1.5 cm) 보여 '시뮬은 재계획 없음 · 6 s 창이라 과소'(09-21 §4).

### 4.6 배치 스크립트 · 감싸개 (09-16 ~ 09-18)
- `job356_variants.sh`(A · B) · `job357_variants2.sh`(6 판) · `job358_variants3.sh`(7 판): 09-16 §1.14 변형표. `run()` 이 `T=${T:-17}` 로 장면 시각을 받음.
- `job366_mp5sim.sh`: job345(후보 분포) · job354(크리틱 재구성) · job355 M/N/O/P.
- `job396_goalsim8.sh`(09-17 §7.2), `job408 · 411 · 412 · 413 · 420 · 421 · 421b · 423`(09-17 §12 · §14 — [흔들림 카드 §9](mppi-wobble-temperature.md)), `job452_run.sh`(09-18).
- 감싸개 `run_j3xx.sh` · `run_j4xx.sh`: PC WSL → `sshpass -p <PW> scp` → Jetson `/tmp`, `setsid nohup` 로 실행 → `run_waitsim.sh` 가 '######## 끝' 대기. 감싸개 안의 스크래치패드 경로는 소실(09-28) — 지금은 저장소 `jobs/` 판을 직접 올려야 함.
- bag 은 PC `Docs/debug_log/2026-09-16|17|18/bags/*.tgz`(git 제외)에 남아 있다 → **원천 보존**.

### 4.7 도구 계보(한 줄씩)
- job355(09-16) → job355(09-17): + 펌웨어 휠 처리 · `/plan` 대체 경로 · 흔들림 지표.
- job355(09-17) → job410: + 구동계(가속 · 지연 · 이득) · ESS · 목표 진입.
- job410 → job419: + `humble=1` 네 가지 · `regen` · `dyn_path` · `dyn_cost`.
- job419 → job452: + CostCritic · near_goal · t_abs · LETHAL 여유.
- job452 → job776(10-01): + Ackermann 최소 반경 · 후진 · 제자리 회전 집계.
- job776 → `Docs/tools/anal_mppi_sim.py`(10-13 고정 이름): + `fpchk`(Nav2 칸 단위 풋프린트) · 실패 주기 · `pad` · `unstuck`(10-14) · `resample` · `wheel_max` · 경로 이탈(10-26).

## 5. 조치와 효과(이 도구가 바꾼 설정)
| 날짜 | 시뮬이 고른 손잡이 | 실주행 확인 | 지금 |
|---|---|---|---|
| 09-16 §1.14 | PathFollow `cost_weight 5 → 10` · `offset_from_furthest 5 → 20` | mp5 입구 통과(09-16 §1.15) | PathFollow 가중은 10-26 에 5 로(굽은 곳 깎기), offset 20 유지(`nav2_params.yaml` 284 행) |
| 09-17 §7.2 | 경로 크리틱 `threshold_to_consider` 0.6/0.4/0.4 → 0.2, GoalCritic 5 → 10 | mp9~11 3/3 | 유지(PathAlign 280 행 0.20) |
| 09-17 §12.6 | temperature 0.15 → 0.3 | mp12 불합격 → 0.15 복귀 | 0.15 |
| 09-18 §17.2 | (교체를 막을 신호 없음 확인) ObstaclesCritic → CostCritic | 09-21 cc1~3 채택 | CostCritic(254 · 268 행) |

## 6. 결과를 얼마나 믿나 — 요약 규칙
- **믿어도 되는 것**: 정체 장면에서 '어느 크리틱 변경이 정체를 푸는가' 의 방향(09-16 F, 09-17 S5, 09-18 CostCritic — 셋 다 실주행과 같은 방향).
- **믿으면 안 되는 것**: 흔들림 · 속도 · 여유의 **크기**. 원인: 정적 또는 2 Hz 재생 장면 · 재계획 없음 · 6 s 창 · 근사 크리틱 · 구동계 형태(10-26 전) · 씨앗 2~3 개(ESS 10~20 에서 씨앗 편차가 변형 효과보다 클 수 있음, 10-26 §10.3).
- 09-17 이전 판(job355 · job410)의 수치는 §4.4 의 4 가지 차이를 가진다. 인용할 때 판 이름을 같이 적는다.
- 09-17 · 09-18 의 '실측 구동계'(`w_gain 0.7`)는 10-26 이후 기준으로는 틀린 형태다 — 곡률이 실제보다 덜 꺾이는 쪽.

## 7. 내 실수
### M1. 근사 시뮬의 정량 예측으로 판정 기준까지 정함 (09-17 §12 → §13.3 → §14.1)
- 칸 형식 전문은 [흔들림 카드 §6 M1](mppi-wobble-temperature.md). 요지: 하려 한 것 = temperature 로 흔들림 줄이기(job410) → 본 것 = 반전 0 예측 vs mp12 8.8 /m, 속도 저하 예측 vs 가장 빠름 → 의심 = 두 지표가 동시에 빗나감 → 판별 = 설치 헤더 · 같은 태그 소스 대조(job418) → 결론 = 4 가지 동작 차이, job419 → 다음에 알아보는 법 = **시뮬 결과로 손잡이를 정하기 전에 잡음 생성 시점 · 한계 처리 위치 · 초기 상태 · 출력 필터를 설치본 소스와 줄 단위로 대조한다**. 데이터 [j418_mppisrc.txt](../debug_log/2026-09-17/outputs/j418_mppisrc.txt).

### M2. '회전만 ×0.7' 구동계 (09-17 §12.3 → 10-26 §10.2)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 실측 이득(job409)을 시뮬에 넣어 '실측 구동계' 를 만들기(`w_gain=0.7`) |
| 본 것 | 09-17: 명령 → EKF ω 이득 0.68~0.75, 휠 오도 0.60~0.62. 10-26: 굽은 곳 명령 v 0.080 · ω 0.17~0.20 에 실제 v 0.055~0.061 · ω 0.10~0.13 |
| 처음 추론 | 09-17: 트랙 미끄럼으로 회전만 덜 됨 → ω 에만 상수 이득 |
| 의심한 이유 | 10-26: 이 모델로는 실제 '굽은 곳 안쪽 깎기'(9.3 → 15.7 cm)가 재현되지 않음(9 변형 모두 줄어듦). v 도 함께 줄어 있었음 |
| 판별 시험 | 10-26 `chk_cmd_vs_motion_f2sh2.py`: 바깥 바퀴 = 0.058 + 0.125 × 0.2215 ≈ 0.086 = 펌웨어 한계 0.085. 펌웨어 `cmdvel_callback` 의 비례 축소 계산 (0.08, 0.19) → ×0.70 → (0.056, 0.132) = 실측. `wheel_max=0.085` 로 바꾼 재현 판에서 실제 15.7 이 씨앗 범위(9.6~20.2) 안 |
| 결론 | 손실은 회전만이 아니라 **v · ω 같은 비율**(곡률 유지). 09-17 · 09-18 시뮬의 '실측 구동계' 는 곡률을 바꾸는 잘못된 형태. 09-17 의 이득 0.6~0.75 도 같은 기전일 가능성(미확인 — [흔들림 카드 M5](mppi-wobble-temperature.md)) |
| 다음에 알아보는 법 | 구동계 손실을 시뮬에 넣기 전 펌웨어 명령 경로(클램프 · 포화 · 데드밴드)를 코드로 확인하고, v 와 ω 손실을 따로 재서 같은 비율인지 본다 |
| 데이터 | [j409_lag.txt](../debug_log/2026-09-17/outputs/j409_lag.txt), [10-26 SUMMARY §10.1~10.2](../debug_log/2026-10-26/SUMMARY.md) `outputs/mppi_sim/sim_corner_1026.txt` · `sim_corner_1026b.txt` · `outputs/drives/f2sh2/chk_cmd_vs_motion_f2sh2.txt`, 펌웨어 `firmware/rover_jupiter_fw/App/microros/microros_task.c` 170~182 행 · `App/app/rover_platform.h` 73 · 82 행 |

### M3. job421 의 셸 변수 덮어쓰기 · job411 순서 오류
- [흔들림 카드 §6 M2 · M3](mppi-wobble-temperature.md).

### M4. '시뮬이 옛 ObstaclesCritic 기준이라 고쳐야 한다(반나절)' (10-13 — 이후 시기, 기록만)
- 10-13 SUMMARY 272 · 328 행: 확인 없이 job419 만 떠올리고 말함 → 같은 날 정정, job452 · job776 이 이미 CostCritic 판. **다음에 알아보는 법**: 도구 계보를 이 카드(또는 [도구 사전](index/JOBS.md))에서 먼저 찾는다.

## 8. 남은 것
- 시뮬에 없는 '주기마다 교란'(흔들림 크기를 맞추려면 필요, 원천 미확인).
- 재계획(1 Hz)을 bag `/plan` 재생 말고 실제 계획기와 함께 도는 형태는 없다.
- 코스트맵 2 Hz 재생 한계(실제 5 Hz 갱신 사이 셀 변화는 못 봄).
- 09-18 job452 결론(입구 · 복귀 +1~2 cm)이 씨앗 2 개라 10-26 기준(씨앗 6)으로는 잡음 안일 수 있음 — 09-21 실주행이 방향을 확인했으므로 다시 돌릴 필요는 낮음.

## 9. 실험 · 도구 색인
- 장면 bag: 09-16 `bag_mp4`(t=17 입구) · `bag_mp5`(t=24 · 29 복귀), 09-17 `bag_mp8`(t=33 목표 근처) · `bag_mp11`(t=10 · 19) · `bag_mp12`(t=17 · 19), 09-18 `bag_dy2` · `dy4` · `dy6`(goal + 8 · 16.5 · 20 s).
- 출력: 09-16 `j355_ab · j355_cdefgh · j355_ijkl · j366_mp5_return`, 09-17 `j396_goalsim8 · j408 · j411 · j412 · j413 · j420 · j421 · j421b · j423`, 09-18 `j452_sim_cc · j452_sim_cc_table`.
- 소스 대조: 09-17 `j418_mppisrc · j418b_sgfilter · j418c_motion`, 09-18 `refs/mppi_1.1.20_cost_critic.cpp` · `refs/mppi_1.1.20_obstacles_critic.cpp`, `outputs/j447_mppi_ver.txt`(설치 버전 1.1.20-1jammy.20260219).

## 10. 용어
- **MPPI · softmax temperature · ESS · Savitzky-Golay · regenerate_noises**: [흔들림 카드 §10](mppi-wobble-temperature.md).
- **정적 장면**: bag 의 한 시각 코스트맵 · 경로를 고정하고 시뮬 로버만 움직이는 방식. 실제는 코스트맵 5 Hz · 재계획 1 Hz 로 바뀐다.
- **배치 furthest**: 1000 후보 각각의 끝점에 가장 가까운 경로 점 index 중 최댓값. 경로 크리틱(PathAlign 의 켜짐 조건, PathFollow · PathAngle 의 목표점)이 공유하는 '얼마나 멀리 갈 수 있는 표본이 있나' 의 척도.
- **ConstraintCritic**: 1.1.20 에서 후보를 자르지 않는 대신 속도 한계 초과분을 비용으로 벌하는 크리틱(가중 4, vx 만 — wz 는 벌점 없음).
- **씨앗(seed)**: 잡음 한 벌을 정하는 난수 시작값. 고정 잡음 모드에서는 씨앗 하나가 주행 전체의 표본 집합을 정한다.
- **ObstaclesCritic · CostCritic**: [CostCritic 카드 §10](obstacles-to-costcritic.md).
