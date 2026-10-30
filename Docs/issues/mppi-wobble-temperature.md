# MPPI 조향 흔들림 — 'temperature 0.15 의 ESS 부족' 가설이 실주행 1 회로 깨지기까지

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **보류**(위치 영향 < 0.1 mm 로 우선순위 내림 — 원인 교란원 미확정). temperature 는 0.15 → 0.3 → **0.15 복귀**(현재 값 0.15, `nav2_params.yaml` 243 행) | 09-17 §11.1 ~ §14.7 (이 카드), 이후 10-07 · 10-26 에서 같은 '씨앗 잡음' 이 다시 언급됨 | [09-17 §11.1 '남은 문제 ①'](../debug_log/2026-09-17/SUMMARY.md) — 09-16 mp5 '직진 중 ω 부호반전 14 /m' 이 시작 | `ros2_ws/src/rover_navigation/config/nav2_params.yaml` `FollowPathMPPI.temperature`(09-17 §12.6 에서 0.3, §14 머리에서 0.15) | [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md)(이 카드의 도구 계열) · [ObstaclesCritic → CostCritic](obstacles-to-costcritic.md)(§13.4 여유 지표가 이어짐) · [컨트롤러 선택 RPP vs MPPI](controller-rpp-vs-mppi.md) · [센서 데크 yaw](sensor-deck-yaw.md)(§13.3 후보 ③ · §15.5 와 이어짐) |

**한 줄**: 상자 옆 통로에서 MPPI 명령 ω 가 0.4~0.67 s 간격으로 좌우로 뒤집혔다(통로 10.3~14.8 회/m). 오프라인 시뮬레이터로 'softmax temperature 0.15 에서 유효 표본 수(ESS)가 1000 개 중 ≈10 이라 평균 제어에 독립 잡음이 섞인다' 는 기제를 세우고 temperature 를 0.3 으로 올렸지만(§12.6), 첫 실주행 mp12 에서 흔들림이 줄지 않았고(8.8 회/m, 예측 0) 느려진다는 예측도 빗나갔다(§13.3). 사용자 결정으로 0.15 로 되돌리고 시뮬레이터를 설치본 1.1.20 소스와 대조하자 **네 가지가 달랐다**(잡음 재사용 · 후보 clip 없음 · 측정 속도 스텝 0 · Savitzky-Golay 필터, §14.1). 고친 시뮬로도 재계획 · SLAM 보정 · 코스트맵 깜빡임 · 정지 센서 잡음은 원인이 아니었고(§14.3~14.4), 흔들림의 위치 영향은 횡 0.1 mm 미만(§14.6, 단 아래 §5 의 한계)이라 우선순위를 내렸다. 주기마다 교란을 넣는 실제 원천은 **미확정**.

## 1. 증상
- 09-16 mp5(PathFollow 10/20 적용 첫 주행): '조향 품질은 나빠졌다: 직진 중 ω 부호반전 36 회(14/m; mp4 는 0)' — 탐색 폭(vx_std 0.08 · wz_std 0.4) · 낮은 temperature 의 대가로 보고 'wz_std 0.3 비교' 를 다음 과제로([09-16 §1.15](../debug_log/2026-09-16/SUMMARY.md)).
- 09-17 mp9 · mp10 · mp11(같은 구성 3/3 성공) 러너의 '직진 중 ω 부호반전' **4.1 · 15.7 · 10.2 /m** — 편차가 커서 '남은 문제 ①' 로 올림([09-17 §11.1](../debug_log/2026-09-17/SUMMARY.md)). 이 러너 수치는 직진 구간 전체 · 다른 샘플링이라 §12 의 표와 직접 비교하지 않는다(§12.1 마지막 줄).
- 로버는 이 카드의 분석(§12 · §14) 동안 움직이지 않았다. 실주행은 mp12 한 번(§13).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-16 §1.13 | mp4 정체(표본 붕괴) 대책으로 네 손잡이 동시 변경 | `vx_std` 0.05 → 0.08, `wz_std` 0.3 → 0.4, `iteration_count` 1 → 2, **`temperature` 0.3 → 0.15** | '표본 붕괴' 가설 하나의 네 손잡이 — temperature 단독 효과는 검증 안 됨(§12.6 근거 ②) | [09-16 SUMMARY](../debug_log/2026-09-16/SUMMARY.md) |
| 09-17 §12.1 | bag 으로 흔들림이 어디서 · 차체까지 가는지(`job407_wobble.py`) | 통로(odom x 0.6~1.45) 명령 반전 mp9 10.3 · mp10 13.7 · mp11 14.8 /m, 실제 yaw 반전 12.6 · 15.9 · 21.7 /m, 고주파 RMS 명령/실제 0.058/0.061 · 0.076/0.066 · 0.061/0.060 rad/s, 반전 간격 중앙 0.67 · 0.60 · 0.40 s. 접근(<0.6) 1.5~6.3 /m. `/plan` 수신 일치 50~60 % vs 우연 57 %, map→odom 점프 58/33/20 % vs 우연 33/34/34 % | 흔들림은 통로에 몰리고 **차체 yaw rate 에도 같은 크기**. 재계획 · SLAM 점프와는 무관(mp9 만 높아 일관성 없음) | [j407_wobble.txt](../debug_log/2026-09-17/outputs/j407_wobble.txt), bag `2026-09-17/bags/bag_mp9~11.tgz` `/cmd_vel` · `/odometry/filtered` · `/tf` · `/plan` |
| 09-17 §12.2 | 구동계 지연 · 이득(`job409_lag.py`, 상호상관) | 명령 ω → EKF ω: 0.10 s · 상관 0.94~0.95 · **이득 0.68~0.75**. 명령 ω → 휠 오도 ω: 0.12 s · 0.98~0.99 · **0.60~0.62** | 지연 = MPPI 1 주기. 이득 0.6~0.75 는 '스키드스티어 트랙 미끄럼으로 추정, 미검증' — **이 표 자체와 맞지 않음**(§3 · §7 M6) | [j409_lag.txt](../debug_log/2026-09-17/outputs/j409_lag.txt) |
| 09-17 §12.3 | 시뮬레이터에 구동계(smoother ω 가속 1.2 · 지연 1 주기 · ω 이득 0.7 · 펌웨어 휠 처리)와 ESS 기록 추가 → `job410_mppi_sim_lag.py` | 선행 배치 `job408`(구동계 없음, mp11 t=10): 반전 39~72 /m, wz_std 0.3/0.2 는 27~72 로 일정치 않음, T 0.3 은 7~14 /m. `job411` 은 순서 오류로 폐기 | — | [j408_wobblesim.txt](../debug_log/2026-09-17/outputs/j408_wobblesim.txt), [j411_tempsim.txt](../debug_log/2026-09-17/outputs/j411_tempsim.txt)(쓰지 않음) |
| 09-17 §12.4 | 기제 분리(`job413_wobblecause.sh`, mp11 t=19 통로 (0.77, 0.31) yaw +18°, 6 s, seed 1~3) | 실측 구동계 · T 0.15: ESS 10.2~11.3/1000, 명령 반전 5.9~12.9 /m · RMS 0.065~0.071(bag 10.3~14.8 · 0.058~0.076 과 같은 크기). T 0.3: ESS 80.8~88.7, 반전 **0**, RMS 0.032~0.040, 6 s 전진 0.26(0.15 는 0.30~0.34) | '원천 = 평균 제어의 표본 잡음 wz_std/√ESS ≈ 0.12~0.14 rad/s, 지연은 원인 아님, smoother 가 절반을 거름' — **실측으로 확인 안 됨**(§13.3 에서 가설로 강등, §14.1 에서 모델 자체가 실제와 4 가지 다름) | [j413_wobblecause.txt](../debug_log/2026-09-17/outputs/j413_wobblecause.txt) |
| 09-17 §12.5 | 부작용(`job412_tempsim2.sh`): 통로 · 입구(mp4 t=17) · 목표 근처(mp8 t=33) | T 0.3: 통로 6 s 0.26 m/−15~−17°(0.15 는 0.30~0.34/−20~−24°), 입구 0.24~0.25 · 최종 v 0.04~0.05 · 반전 0, 목표 허용오차 첫 진입 12.3~12.4 s(0.15 는 7.2~7.5 s). wz_std 0.3: 반전 5.7/6.4/11.9 vs 0.15 현재 11.5/12.9/5.9 | '정지 없이 진행, 대가는 진행 −15~−23 %' — **속도 저하 예측은 후보 clip 이 만든 착시**(§14.2) | [j412_tempsim2.txt](../debug_log/2026-09-17/outputs/j412_tempsim2.txt) |
| 09-17 §12.6 | **결정: temperature 0.15 → 0.3**, 주행 전 판정 기준 선언 | 기준: 성공 3/3 · 통로 반전 ≤ 5 /m · RMS ≤ 0.045 · 1 s 정지 0 · 상자 최근접 ≥ 9 cm · 시간 ≤ 45 s. 예비안 T 0.22 | 기각: wz_std 축소 · TwirlingCritic · smoother 가속 강화 · iteration 추가(시뮬은 wz_std 만 함) | `nav2_params.yaml` 주석 |
| 09-17 §13.1~13.2 | mp12(T 0.3) 첫 실주행. 상자가 약 19 cm 옮겨져 있어 로버를 9 cm 뒤로(사용자) | **SUCCEEDED 31.9 s, 2.19 m**, 19.16 s 'Optimizer fail to compute path' → 클리어 → 재시작(≈0.5 s), 24.18 s SmoothPath 충돌 판정 1 회, load 평균 11.6(원인 미확인) | — | [drive_mp12.txt](../debug_log/2026-09-17/outputs/drive_mp12.txt) · [drive_mp12_runner.txt](../debug_log/2026-09-17/outputs/drive_mp12_runner.txt) · [j379_mp12.txt](../debug_log/2026-09-17/outputs/j379_mp12.txt) · [mp12.csv](../debug_log/2026-09-17/outputs/mp12.csv) · [j415_sectors.txt](../debug_log/2026-09-17/outputs/j415_sectors.txt), bag `bag_mp12.tgz` |
| 09-17 §13.3 | 같은 방식 비교(`job417_compare.sh` = job407 + job416) | mp12 통로 반전 **8.8 /m** · RMS **0.059** · 실제 반전 11.0 · 복귀 11.5 · 전체 7.9, 31.9 s(가장 빠름) | **불합격**(기준 ≤ 5 · ≤ 0.045). '실제 controller 에서는 temperature 가 출력에 거의 영향을 주지 않는다(n=1)', §12 의 ESS 기제는 **가설로 강등**. 차이 후보 ① 비용 스케일 ② 상자 가장자리 셀 깜빡임 ③ map→odom 1 cm 미만 보정 | [j417_compare.txt](../debug_log/2026-09-17/outputs/j417_compare.txt) |
| 09-17 §13.4 | 상자 여유 지표 재점검(`job416_boxclear.py`) | 러너 ① mp12 '0.0 cm' 는 t≈8 s(yaw +40°) 마지막 재고정에서 상자 모델이 왼쪽으로 ≈13 cm 밀린 탓. 코스트맵 LETHAL ↔ 차체 외곽 − 반셀: mp9 **1.4** · mp10 2.2 · mp11 2.2 · mp12 2.6 cm | **정정**: §11.1 '상자 최근접 9.2~19.3 cm' 는 대표값 아님. 통로 여유 자체가 셀 한 칸 수준 → [CostCritic 카드](obstacles-to-costcritic.md) 로 이어짐 | j417 안 job416 부분, [j416_mp12_boxclear.txt](../debug_log/2026-09-17/outputs/j416_mp12_boxclear.txt) |
| 09-17 §13.5 · §14 머리 | 사용자 결정: (b) 기준 구성으로 복귀 + 오프라인 | 설치본 temperature **0.15** 복귀(diff 한 줄) | — | `nav2_params.yaml` |
| 09-17 §14.1 | 시뮬 충실도 점검: 설치 헤더(`job418_mppisrc.sh`) + 같은 태그 소스 | (a) `regenerate_noises` 기본 false → 잡음은 초기화 · reset 때만(주행당 reset mp9 1 · mp10 3 · mp11 1 · mp12 3) (b) 후보 clip 없음, vx 초과는 ConstraintCritic, wz 벌점 없음 (c) 롤아웃 스텝 0 = 측정 속도 (d) SG 9 점 필터 → 제어열[1] 출력 | **§12 · 09-16 §1.14 · 09-17 §7 의 시뮬 정량 예측은 신뢰도 낮춤**(실주행으로 따로 확인된 PathFollow 10/20 등은 유지) → `job419_mppi_sim_humble.py` | [j418_mppisrc.txt](../debug_log/2026-09-17/outputs/j418_mppisrc.txt) · [j418b_sgfilter.txt](../debug_log/2026-09-17/outputs/j418b_sgfilter.txt) · [j418c_motion.txt](../debug_log/2026-09-17/outputs/j418c_motion.txt) |
| 09-17 §14.2 | Humble 모드 검증(`job420_humblesim.sh`, mp11 · mp12 t=17/19) | 6 s 전진 0.41~0.48 m, v 0.08 포화 유지, T 0.3 에서도 안 느려짐(mp12 실측과 일치). T 0.15 RMS 0.012~0.079 · 반전 0~12.7 /m — seed 에 크게 좌우. ESS T 0.15 ≈ 6~14, T 0.3 ≈ 45~58 | 옛 '−15~−23 %' 는 clip 착시 | [j420_humblesim.txt](../debug_log/2026-09-17/outputs/j420_humblesim.txt) |
| 09-17 §14.3 | 입력 변화 재생(재가지치기 R / + /plan · map→odom D / + 코스트맵 C) | `job421` 은 무효 실행(D · C 가 temperature=19). `job421b`: 예 mp12 seed2 T 0.15 R · D · C 모두 8.5 /m · 0.056. 코스트맵 재생 = 재생 없음과 소수점까지 같음 | §13.3 후보 ② ③ **기각** | [j421_dynsim.txt](../debug_log/2026-09-17/outputs/j421_dynsim.txt)(R 행만 유효) · [j421b_dynsim.txt](../debug_log/2026-09-17/outputs/j421b_dynsim.txt) |
| 09-17 §14.4 | EKF 상태 잡음(`job422_sensnoise.py`) | 정지: ω std 0.0010~0.0012 rad/s, yaw std 0.007~0.013°. 주행 통로: ω 0.1 s 차분 RMS 0.061~0.077 | 정지 잡음 무시 가능. 주행 중엔 운동과 잡음을 못 나눔 | [j422_sensnoise.txt](../debug_log/2026-09-17/outputs/j422_sensnoise.txt) |
| 09-17 §14.5 | 고정 잡음 vs 매 반복 새 잡음(`job423_regensim.sh`, mp11 seed 1~6 · mp12 seed 1~3) | 고정 T 0.15: mp11 9.4 0 0 0 0 4.3 /m · 평균 RMS 0.041, mp12 9.4 8.5 0 · 0.049. 새 잡음 T 0.15: 15.7 6.9 17.9 11.5 9.0 15.4 · 0.085 / 21.0 9.2 13.6 · 0.083. 새 잡음 T 0.3 RMS 0.065(mp12 실측 0.059) | 실측은 '새 잡음' 모델과 크기가 맞음 → 실제 기본값(고정)과 다르므로 **시뮬에 없는 주기마다의 교란**이 같은 효과를 낸다고 봄(추정). T 0.3 기대 효과 RMS −23 %, §12.6 기준(≤ 0.045)은 과대 기대 | [j423_regensim.txt](../debug_log/2026-09-17/outputs/j423_regensim.txt) |
| 09-17 §14.6 | 위치 영향(`job424_latwobble.py`) | 통로 odom 궤적 − 1 s 창 2 차식: 횡 잔차 RMS 0.017~0.021 mm(최대 0.047~0.063), yaw 잔차 RMS 0.156~0.187°(최대 0.483~0.639°). 해석식 횡 진폭 ≈ 0.04 mm | **'위치 영향 실질 없음'** — 단 odom 에 옆미끄럼이 없는 구조라 횡 잔차는 정의상 heading 적분분만 잡힘(§5) | [j424_latwobble.txt](../debug_log/2026-09-17/outputs/j424_latwobble.txt) |
| 09-17 §14.7 · §16 | 정리 | 확정: 충실도 결함 4 가지 수정, 재계획 · SLAM · 코스트맵 · 정지 센서 잡음 원인 아님. 미확정: 교란원. 확정하려면 `/cmd_vel_nav` · IMU 원자료 기록 | 흔들림 우선순위 내림 → 여유 ≈2 cm · 간헐 중단 먼저 | — |
| 이후 09-18 §13.7 | dy1~6(데크 보정 후) | 직진 부호반전 dy3 · dy4 만 16~17 /m, 나머지 5~6 | 원인 미조사 | [09-18 SUMMARY](../debug_log/2026-09-18/SUMMARY.md) |
| 이후 09-21 | CostCritic 채택 cc1~3 · 기준선 cc2~5 | 직진 부호반전 1~5.6 /m(BASELINE_STVL) | 흔들림 자체를 다시 다루진 않음 | [BASELINE_STVL.md](../debug_log/2026-09-21/BASELINE_STVL.md) |
| 이후 10-07 | 저속 떨림 원인 미확정 | 후보 ② 'MPPI 표본 분포가 저속에 머문 상태(09-17 §12 의 ESS 기제와 관련 가능)' | 오프라인 재현으로만 가를 수 있음 | [10-07 SUMMARY](../debug_log/2026-10-07/SUMMARY.md) |
| 이후 10-26 §10.1~10.2 | 같은 계열 시뮬(`anal_mppi_sim.py`)로 굽은 곳 깎기 재현 | 실제 명령 대 움직임 비 0.45~0.68 = **펌웨어 바퀴 포화**(한쪽 바퀴 0.085 초과 시 두 바퀴 비례 축소). 옛 `w_gain 0.7`(회전만) 모델이 곡률을 바꿔 깎기를 가렸다 → `wheel_max` 추가. ESS 10~20 이라 결과가 씨앗에 크게 흔들림 | 09-17 §12.2 의 '이득 0.6~0.75' 도 같은 기전일 가능성(§3, 추정) | [10-26 SUMMARY §10](../debug_log/2026-10-26/SUMMARY.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 1 Hz 재계획(`/plan` 수신)이 흔들림을 만든다 | job407 반전 ±0.3 s 안 일치율 vs 무작위 | 50~60 % vs 57 % | **기각**(§12.1), job421b 재생으로도 기각(§14.3) |
| SLAM map→odom 점프가 흔들림을 만든다 | 같은 방식(>1 cm 또는 >0.5° 점프) · job421b 재생 | 58/33/20 % vs 33/34/34 %(mp9 만 높음), 재생해도 반전 · RMS 체계적 변화 없음 | **기각**(1 cm 미만 보정은 job407 이 안 봤지만 job421b 의 map→odom 시간 재생에는 들어감) |
| 구동계 지연(0.1 s)의 과보정 발진 | job413 '지연 · 이득만' 변형 | 명령 RMS 0.107~0.113 으로 이상 구동계(0.109~0.121)와 같음 | **기각**(시뮬 안에서) — 단 그 시뮬은 §14.1 의 4 가지가 다른 모델 |
| temperature 0.15 → ESS ≈ 10 → 평균 제어에 독립 잡음 | job413(옛 모델) → mp12 실주행(T 0.3) | 옛 모델 예측 반전 0 · RMS 0.032~0.040 ↔ 실측 8.8 /m · 0.059 | **실측으로 확인 안 됨**(§13.3). 고친 모델(§14.5)에서는 고정 잡음이면 과소 예측, 새 잡음이면 실측과 맞음 → 'ESS 만' 으로는 설명 못 함 |
| 상자 가장자리 셀이 갱신마다 나타났다 사라져 크리틱 비용을 흔든다(§13.3 ②) | job421b 코스트맵 시간 재생 | 재생 없음과 소수점까지 같음(이 구간 상자 셀 불변 — bag 2 Hz 라 5 Hz 갱신 사이 변화는 못 봄) | **기각**(bag 해상도 한계 안에서) |
| 정지 센서 잡음이 측정 속도(스텝 0)를 흔든다 | job422 정지 구간 | ω std 0.001 rad/s | **기각**(정지 잡음). 주행 중 잡음은 분리 불가 → **미확인** |
| 주기마다의 교란(센서 · 트랙 미끄럼 · 제어 주기 떨림)이 고정 잡음 표본 선택을 바꾼다 | job423 의 '새 잡음' 모델이 실측과 맞는다는 간접 근거만 | — | **미확인**(추정). 판별하려면 `/cmd_vel_nav` · IMU 원자료 기록(§14.7) |
| 이득 0.6~0.75 = 스키드스티어 트랙 미끄럼(§12.2) | 같은 j409 표의 휠 오도 이득 vs EKF 이득 | 휠 오도 ω 이득 0.60~0.62 < EKF(자이로) 0.68~0.75. 트랙 미끄럼이 주원인이면 바퀴(휠 오도)는 명령을 다 따르고 자이로만 작아야 한다 | **표와 맞지 않음**(이 카드 작성 중 판단). 10-26 §10.1 의 펌웨어 바퀴 포화(`microros_task.c` cmdvel_callback 비례 축소 — 코드는 05-21 부터, 한계 0.085 는 09-07 부터, 따라서 09-17 주행에도 적용)가 더 그럴듯함 — 09-17 bag 으로 바퀴별 명령을 재계산하지 않았으므로 **미확인** |
| 흔들림이 경로 정확도 · 상자 여유를 해친다 | job424 잔차 | 횡 < 0.1 mm, yaw 0.16~0.19° RMS(모서리 ≈3 mm) | **기각**(odom 기준). SLAM 기준 실제 옆 흔들림은 안 잼(§5) |

## 4. 조치와 효과
| 시점 | temperature | 근거 | 결과 |
|---|---|---|---|
| 09-16 mp4 뒤 | 0.3 → 0.15 | 표본 붕괴 가설(네 손잡이 동시) | mp5 입구 통과(당근 10/20 의 효과로 판단), 부호반전 0 → 14 /m |
| 09-17 §12.6 | 0.15 → **0.3** | 옛 시뮬(job410)의 ESS 기제 | mp12: 성공 31.9 s · 반전 8.8 /m · RMS 0.059 → 기준 불합격, 느려지지도 않음 |
| 09-17 §14 머리 | 0.3 → **0.15** | 사용자 결정(기준 구성 3/3 으로 복귀) | 현재까지 유지(BASELINE_STVL 09-21, 현재 YAML 243 행) |
- 바꾼 것은 이 한 줄뿐이고, 흔들림은 해결되지 않았다. 남긴 것은 '위치 영향이 없다' 는 측정(§14.6)과 '시뮬레이터 4 가지 결함 수정'(job419 → [시뮬 카드](mppi-offline-simulator.md)).

## 5. 한계 · 모순 기록(원문 대조)
- **§12.2 '트랙 미끄럼으로 추정'** — 같은 표의 휠 오도 이득(0.60~0.62)이 자이로 융합 EKF 이득(0.68~0.75)보다 작다. 휠 오도 ω 는 펌웨어가 B_eff 0.443(`rover_platform.h` 73 행)으로 환산하므로 '바퀴가 명령한 바퀴 속도 차를 못 냈다' 가 먼저다. 10-26 §10.1 에서 확인한 바퀴 포화 계산(v 0.08 · ω 0.19 → 바깥 바퀴 0.122 → ×0.70)과 같은 방향. 09-17 의 시뮬은 이 손실을 '회전만 ×0.7' 로 넣어(v 는 그대로) 곡률이 실제와 다르다 — 10-26 §10.2 의 정정과 같은 결함.
- **§14.6 '위치 영향 < 0.1 mm'** — 쓴 궤적이 odom(`odom→base_link`)이다. 같은 날 job422 출력의 '차체 횡방향 이동/주기 RMS 0.0000 m'(4 주행 모두)가 보여주듯 odom 에는 차체 옆방향 운동이 없다(EKF 가 전진 속도 + yaw rate 만 적분). 그래서 횡 잔차는 정의상 'heading 흔들림 × v 적분' 만 잡고, 해석식(0.04 mm)과 맞는 것은 당연하다. 실제 옆미끄럼이 흔들림을 따라 생겼는지는 이 방법으로 볼 수 없다(**미확인**). yaw 잔차(자이로 기반)는 실측이다.
- **§12.4 '시뮬레이터 타당성 — 현재 흔들림을 재현한다'** — §13.3 에서 '우연 일치였을 수 있다' 로, §14.1 에서 모델이 실제와 4 가지 달랐다로 뒤집힘. 수치(5.9~12.9 /m)는 원문에 그대로 남아 있으니 인용할 때 주의.
- **현재 YAML 주석**(`nav2_params.yaml` 234~242 행): '0.15 → 0.3 … ESS 기제 … 진행 −15~−23 %' 문장이 남아 있고 §13 의 '확인되지 않았다' 는 덧붙였지만 §14.2(속도 저하 예측 = clip 착시) · §14.5(T 0.3 기대 효과 −23 %) 는 반영되지 않았다. 동작에는 영향 없음(값은 0.15).
- `job411` 출력(`j411_tempsim.txt`)은 지금 저장된 `job410_mppi_sim_lag.py` 로 다시 만들 수 없다: 출력 줄 형식(ESS 없음, 반전 한 종류)이 지금 판과 다르고, SUMMARY 는 '가속 제한을 지연 · 이득 뒤에 둔 순서 오류' 라 적었는데 저장본은 가속 제한이 지연 큐 앞에 있다(고친 뒤의 판). 옛 판 코드는 **원천 소실**.
- §14.3 'R · D · C 가 체계적으로 달라지지 않음' — 같은 값만 나온 것은 아니다: mp12 seed1 T 0.15 는 R 9.4 /m · 0.049 vs D · C 4.7 · 0.043, mp11 seed1 은 R 9.4 · 0.054 vs D · C 9.6 · 0.040. 방향이 일정하지 않아 '원인 아님' 판정은 유지.
- 재현 경로: bag 은 PC `Docs/debug_log/2026-09-17/bags/bag_mp*.tgz`(git 제외)에 남아 있다. 모든 시뮬은 Jetson `/tmp` 에서 돌았고 로그는 `outputs/` 로 옮겨졌다.

## 6. 내 실수
### M1. temperature 가설로 설정을 바꿨는데 실주행에서 효과 없음 (09-17 §12 → §13.3 → §14)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 통로 조향 흔들림의 원인을 찾아 한 손잡이로 줄이기. `job410_mppi_sim_lag.py`(job355 + 구동계 + ESS), 배치 `job413_wobblecause.sh` · `job412_tempsim2.sh` |
| 본 것 | j413: 실측 구동계 T 0.15 ESS 10.2~11.3, 반전 5.9~12.9 /m(bag 10.3~14.8 과 같은 크기), T 0.3 ESS 80.8~88.7 · 반전 0. j412: 정지 없음 |
| 처음 추론 | 원천 = softmax ESS 부족 → wz_std/√ESS ≈ 0.12~0.14 rad/s 독립 잡음. T 0.3 이면 사라진다. 시뮬이 bag 크기를 재현하므로 모델은 타당 |
| 의심한 이유 | mp12(T 0.3) 실측 반전 8.8 /m · RMS 0.059 — 예측(0 · 0.032~0.040)과 크기가 전혀 안 맞고, **같은 창의 다른 지표**(진행 속도)도 예측(−15~−23 %)과 반대(가장 빠름 31.9 s). 두 예측이 동시에 빗나가면 모델 쪽 문제 |
| 판별 시험 | 설치 헤더 grep(`job418_mppisrc.sh`) + 같은 태그 소스 대조 → 4 가지 차이 발견 → `job419` humble=1 로 재실행(`job420`): T 0.3 에서도 안 느려짐(mp12 와 일치), 흔들림은 seed 의존 |
| 결론 | ESS 기제는 '실측으로 확인되지 않은 가설'. 옛 모델의 속도 저하는 후보 clip 착시. 실측 크기는 고정 잡음 모델로는 과소, 매 반복 새 잡음 모델로 맞음 → 시뮬에 없는 주기마다의 교란이 있다(미확인) |
| 다음에 알아보는 법 | **시뮬로 정한 손잡이는 시뮬이 설치본 소스와 같은지 먼저 대조한다**(잡음 생성 시점 · clip 위치 · 초기 상태 · 출력 필터). '크기가 맞다' 한 지표로 타당성을 주장하지 말고 두 지표 이상(흔들림 + 속도)을 같이 맞춘다. 판정 기준을 시뮬 예측값에서 바로 가져오지 않는다(§12.6 RMS ≤ 0.045 는 과대 기대였음, §14.5) |
| 데이터 | [j413_wobblecause.txt](../debug_log/2026-09-17/outputs/j413_wobblecause.txt) · [j412_tempsim2.txt](../debug_log/2026-09-17/outputs/j412_tempsim2.txt) · [j417_compare.txt](../debug_log/2026-09-17/outputs/j417_compare.txt) · [j418_mppisrc.txt](../debug_log/2026-09-17/outputs/j418_mppisrc.txt) · [j420_humblesim.txt](../debug_log/2026-09-17/outputs/j420_humblesim.txt), 도구 `jobs/job410` · `job419`, bag `bag_mp11.tgz` · `bag_mp12.tgz`(t=19), 소스 github ros-navigation/navigation2 태그 `1.1.20`(PC 에 사본 없음 — 09-18 refs/ 에는 obstacles · cost critic 두 파일만) |

### M2. job411 — 구동계 순서 오류 · 차체 ω 만 셈 (09-17 §12.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 실측 구동계를 넣은 온도 A/B(`job411_tempsim.sh` → job410) |
| 본 것 | j411: 반전 11.4 /m(T 0.15) · 0 /m(T 0.3) 같은 줄, ESS 줄 없음 |
| 처음 추론 | (그대로 쓰려 함) |
| 의심한 이유 | 코드 검토에서 smoother 가속 제한(상류, bag `/cmd_vel` 에 해당)을 지연 · 이득 **뒤**에 둔 것과 반전을 차체 ω 로만 센 것을 발견(SUMMARY 기록). bag 지표는 명령(smoother 출력) 기준이라 비교 대상이 다름 |
| 판별 시험 | 순서를 가속 제한 → 지연 → 이득으로 고치고 명령 · 차체 둘 다 세서 `job412` 재실행 |
| 결론 | j411 수치는 쓰지 않는다 |
| 다음에 알아보는 법 | 시뮬 지표는 bag 지표가 잰 **그 지점**(여기선 smoother 출력)에서 센다. 신호 사슬 순서(controller → smoother → 지연 → 펌웨어)를 주석으로 먼저 적고 코드를 맞춘다 |
| 데이터 | [j411_tempsim.txt](../debug_log/2026-09-17/outputs/j411_tempsim.txt)(옛 판 출력 — 그 판 코드는 원천 소실), [j412_tempsim2.txt](../debug_log/2026-09-17/outputs/j412_tempsim2.txt) |

### M3. job421 — 셸 함수가 전역 변수 T 를 덮어씀 (09-17 §14.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 재가지치기(R) · 경로 재생(D) · +코스트맵 재생(C) 를 T 0.15/0.3 로 비교(`job421_dynsim.sh`) |
| 본 것 | j421: D · C 줄의 라벨이 `..._T19`, RMS 0.005~0.014(다른 변형의 1/5) |
| 처음 추론 | (없음 — 라벨에서 바로 드러남) |
| 의심한 이유 | 라벨 `T19` · 지나치게 작은 RMS |
| 판별 시험 | 스크립트 확인: `run() { B=$1; T=$2; ...}` 가 바깥 `for T in 0.15 0.3` 의 T 를 장면 시각 19 로 덮어씀 → 첫 변형(R)만 정상. `local` 로 고친 `job421b` 재실행 |
| 결론 | j421 은 R 행만 유효, D · C 는 j421b |
| 다음에 알아보는 법 | bash 함수 안 변수는 `local`. 출력 라벨에 실제로 쓴 파라미터 값을 찍게 하고, 결과 표를 만들기 전에 라벨부터 훑는다 |
| 데이터 | [j421_dynsim.txt](../debug_log/2026-09-17/outputs/j421_dynsim.txt) · [j421b_dynsim.txt](../debug_log/2026-09-17/outputs/j421b_dynsim.txt), `jobs/job421_dynsim.sh` · `job421b_dynsim.sh` |

### M4. '상자 최근접 9.2~19.3 cm' 를 대표값으로 씀 (09-17 §11.1 → §13.4)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 반복 3 회의 여유를 러너 ① 로 요약, §12.6 판정 기준(≥ 9 cm)에도 씀 |
| 본 것 | mp12 러너 ① **0.0 cm**, 그러나 접촉 보고 없음 |
| 처음 추론 | — (바로 의심) |
| 의심한 이유 | 같은 시각 코스트맵 상자 셀은 y ≤ +0.075 에 있었는데 러너 모델은 그보다 왼쪽까지 |
| 판별 시험 | `job416_boxclear.py`: bag 로컬 코스트맵 LETHAL ↔ 차체 외곽. 러너 모델은 t≈8 s(yaw +40°) 마지막 재고정에서 ≈13 cm 밀림(상자 미관측 23.8 s 동안 외삽) |
| 결론 | 컨트롤러가 보는 여유는 네 주행 모두 1.4~2.6 cm. §11.1 수치는 재고정 모델 의존이라 대표값 아님 |
| 다음에 알아보는 법 | 러너 계측 모델(재고정 · 외삽)에 의존하는 값은 코스트맵 기준(컨트롤러가 실제 보는 것)과 같이 낸다. 이 러너 결함은 09-18 §13.4 · §14 에서 '재고정은 출발 yaw ±5° 안에서만'(1안)으로 고침 — [회피 주행 계측 결함 카드](avoid-run-metrics.md) · [CostCritic 카드 §17.4](obstacles-to-costcritic.md) |
| 데이터 | [j417_compare.txt](../debug_log/2026-09-17/outputs/j417_compare.txt)(job416 부분) · [j416_mp12_boxclear.txt](../debug_log/2026-09-17/outputs/j416_mp12_boxclear.txt) · [mp12.csv](../debug_log/2026-09-17/outputs/mp12.csv), 도구 `jobs/job416_boxclear.py` · `job125_avoid3.py`, bag `bag_mp9~12.tgz` `/local_costmap/costmap` · `/tf` |

### M5. 이득 0.6~0.75 를 '트랙 미끄럼' 으로 추정 (09-17 §12.2 — 이 카드 작성 중 다시 봄)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 구동계 지연 · 이득을 재서 시뮬에 넣기(`job409_lag.py`) |
| 본 것 | 명령 → EKF ω 이득 0.68~0.75, 명령 → 휠 오도 ω 이득 0.60~0.62 |
| 처음 추론 | '스키드스티어 트랙 미끄럼으로 추정, 미검증' → 시뮬에 'ω 만 ×0.7' |
| 의심한 이유 | 미끄럼이면 바퀴는 명령을 따르고(휠 오도 이득 ≈1) 자이로만 작아야 하는데, 휠 오도 이득이 더 작다. 10-26 §10.1 에서 펌웨어가 한쪽 바퀴 0.085 초과 시 두 바퀴를 비례 축소함을 실측으로 확인 |
| 판별 시험 | 09-17 bag 에서는 하지 않음. 할 수 있는 것: `/cmd_vel` 로 바퀴별 목표(v ± ω·0.2215)를 계산해 0.085 넘는 표본 비율과 축소 비율을 구하고 이득과 비교 |
| 결론 | **미확인**(유력 후보 = 바퀴 포화). 확인되면 09-17 · 09-18 시뮬의 '실측 구동계' 는 회전만 줄인 잘못된 형태(10-26 §10.2 와 같은 결함) |
| 다음에 알아보는 법 | 이득을 잴 때 **두 센서(바퀴 · 자이로) 중 어느 쪽에서 손실이 생기는지** 먼저 본다. 명령 사슬에 포화 · 클램프가 있는지 펌웨어 코드를 확인한다(`microros_task.c` 170~182 행) |
| 데이터 | [j409_lag.txt](../debug_log/2026-09-17/outputs/j409_lag.txt), `jobs/job409_lag.py`, bag `bag_mp9~11.tgz` `/cmd_vel` · `/odometry/filtered` · `/wheel_odom`, [10-26 §10.1](../debug_log/2026-10-26/SUMMARY.md) `outputs/drives/f2sh2/chk_cmd_vs_motion_f2sh2.txt` |

## 7. 남은 것
- 주기마다 교란의 원천(미확정). 판별하려면 `/cmd_vel_nav`(smoother 전 controller 원출력) · IMU 원자료를 bag 에 넣고 주행(§14.7). 09-18 §17.3 에서 bag 토픽에 `BAG_EXTRA` 를 넣었지만 이 두 토픽을 기록했는지는 이 시기 기록에서 확인 못 함.
- 09-17 이득 0.6~0.75 가 바퀴 포화인지(§6 M5). 맞으면 이 시기의 '실측 구동계' 시뮬 결과는 다시 볼 대상.
- 실제 옆 흔들림(SLAM 또는 외부 기준) — odom 으로는 원리상 못 봄(§5).
- YAML 주석 정리(§5) — 동작 무관.

## 8. 실험 · 도구 색인
- 주행: mp9 · mp10 · mp11(T 0.15) · mp12(T 0.3) — `2026-09-17/outputs/drive_mp*.txt` · `mp*.csv` · `j379_mp*.txt`, bag `2026-09-17/bags/`. 시뮬 장면 bag: mp4(09-16, 입구 t=17), mp8(목표 근처 t=33), mp11 · mp12(통로 t=17 · 19), mp11 t=10(job408).
- 도구: `job407_wobble.py` · `job409_lag.py` · `job408_wobblesim.sh` · `job410_mppi_sim_lag.py` · `job411_tempsim.sh` · `job412_tempsim2.sh` · `job413_wobblecause.sh` · `job415_sectors.py` · `job416_boxclear.py` · `job417_compare.sh` · `job418_mppisrc.sh` · `job419_mppi_sim_humble.py` · `job420_humblesim.sh` · `job421(b)_dynsim.sh` · `job422_sensnoise.py` · `job423_regensim.sh` · `job424_latwobble.py`, 실행 감싸개 `run_j4xx.sh` · `run_waitsim.sh` (모두 `Docs/debug_log/2026-09-17/jobs/`).

## 9. 도구 해설
**공통 실행 방식(이 시기)**: PC 의 WSL 에서 `run_j4xx.sh` 가 스크래치패드의 스크립트를 CR 제거(`tr -d '\r'`) 후 `sshpass -p <PW> scp` 로 Jetson `/tmp` 에 올리고, `setsid nohup bash /tmp/jobNNN.sh > /tmp/<이름>.log` 로 띄운 뒤 `run_waitsim.sh <로그> <최대 s>` 가 30 s 마다 '######## 끝' 줄을 찾아 기다렸다가 로그를 cat 한다(그 출력이 `outputs/jNNN_*.txt`). Jetson 쪽은 `source /opt/ros/humble/setup.bash` 뒤 `rosbag2_py` 로 `/tmp/bag_<이름>`(tgz 를 풀어 둔 것)을 읽는다. 감싸개 안의 스크래치패드 경로(`82ce61d4-…`)는 09-28 자동 소실되었으므로 **지금 다시 돌리려면 저장소 `jobs/` 판을 직접 올려야 한다**. bag 타임스탬프 기준점 `GOAL_EPOCH`(예 mp9 1789621954.078)은 `job417_compare.sh` 안에 적혀 있다.

### job407_wobble.py — 흔들림 위치 · 전달 · 원인 일치
- 실행: Jetson. 부른 형태 `python3 job407_wobble.py BAG GOAL_EPOCH [BAG GOAL_EPOCH …]`(job417 안에서 mp9~12).
- 왜: '흔들림이 어디서 나고 차체까지 가는가, 재계획 · SLAM 점프와 맞물리는가'(§12.1).
- 하는 일: `/cmd_vel`(smoother 출력) · `/odometry/filtered` twist 를 목표 시각 기준 0~(|v|>0.02 마지막 명령) 구간에서 **20 Hz 격자로 0 차 보간**. `odom→base_link` x 로 구간 분할(접근 < 0.6 · 통로 0.6~1.45 · 복귀 ≥ 1.45). 반전 = |ω| > 문턱(0.01/0.05/0.10)이고 |v| > 0.03 인 표본끼리 부호가 바뀐 횟수 ÷ 그 구간 이동 거리. 고주파 = ω − 1 s(20 표본) 이동평균의 RMS. 반전 간격 = 0.05 문턱 반전 시각 차의 중앙값. 원인 일치 = 0.05 반전 시각 ±0.3 s 안에 `/plan` 수신 또는 map→odom 점프(연속 메시지 간 > 1 cm 또는 > 0.5°)가 있는 비율, 무작위 기준 = 같은 수의 시각을 균일 분포로 200 번 뽑아 같은 비율의 평균(seed 0).
- 출력: 구간별 한 줄(반전 /m 세 문턱 × 명령/실제, RMS, 간격, 거리) + '원인 일치' 줄. [j407_wobble.txt](../debug_log/2026-09-17/outputs/j407_wobble.txt) · [j417_compare.txt](../debug_log/2026-09-17/outputs/j417_compare.txt).
- 쓰인 곳: §12.1 표, §13.3 판정(mp12).
- 알려진 결함: 0 차 보간이라 20 Hz 보다 성긴 토픽은 계단이 됨(`/cmd_vel` 20 Hz 라 영향 작음). map→odom 1 cm 미만 보정은 안 봄(§13.3 ③ — job421b 가 대신 봄). 구간이 odom x 기준이라 SLAM 보정분만큼 map 기준 구간과 어긋남.
- 계보: 이후 같은 지표를 러너 · 기준선이 '직진 조향 부호반전' 으로 따로 계산(09-21 BASELINE_STVL — 같은 함수인지는 이 시기 기록으로 확인 못 함). 지금 다시 쓸 수 있음(bag 이 남아 있고 토픽 이름 동일).

### job409_lag.py — 명령 ω → 실제 ω 지연 · 이득
- 실행: Jetson, `python3 job409_lag.py BAG GOAL_EPOCH …`(`run_j409.sh`).
- 왜: 흔들림이 구동계 지연의 되먹임 발진인지 가리려면 지연 · 이득이 필요(§12.2).
- 하는 일: `/cmd_vel` · `/odometry/filtered` · `/wheel_odom` 을 1.0 s ~ 끝, **20 ms 격자로 선형 보간**(np.interp). |v_cmd| > 0.03 표본만. 지연 L = 0~25 칸(0~0.50 s) 중 (명령 ω − 평균) 과 L 칸 당긴 실제 ω 의 상관계수가 최대인 L. 이득 = 그 L 에서 원점 통과 최소제곱 기울기 Σab/Σa².
- 출력: 주행마다 한 줄. [j409_lag.txt](../debug_log/2026-09-17/outputs/j409_lag.txt).
- 쓰인 곳: §12.2 → job410 의 `lag_steps=1 · w_gain=0.7`.
- 알려진 결함: 이득을 '선형 상수' 로 요약 — 실제 손실이 바퀴 포화처럼 명령 크기에 따라 달라지면(§6 M5) 상수 하나가 맞지 않는다. `np.roll` 이 끝을 앞으로 감아 붙이므로 마지막 L 칸을 마스크로 지우는데, 지운 것은 맞다.
- 지금 다시 쓸 수 있음. 바퀴 포화 판별용으로는 바퀴별 목표 재계산을 추가해야 함.

### job408_wobblesim.sh · job411_tempsim.sh · job412_tempsim2.sh · job413_wobblecause.sh — 시뮬 배치
- 실행: Jetson, `run_j408.sh` 등이 올리고 nohup. 각 `run()` 은 `python3 /tmp/<시뮬>.py /tmp/bag_<B> <t> key=val …` 의 출력에서 라벨 · '→' · '흔들림' · '유효 표본' 줄만 grep.
- 공통 인자: `vx_std=0.08 follow_w=10 follow_off=20 goal_w=10 follow_thr=0.2 align_thr=0.2 angle_thr=0.2 eps=0.003 promote=0.008 db=0.005 iters=2`(09-17 당시 실주행 구성 + 새 펌웨어 정지 문턱). 실측 구동계 = `lag_steps=1 w_gain=0.7 w_acc=1.2`.
- job408(job355 09-17 판, 구동계 없음): 통로 mp11 **t=10**(SUMMARY 표기 '접근 · 차선변경 구간') seed 1~3 × {wz_std 0.4 현재 · 0.3 · 0.2 · T 0.3}, 입구 mp4 t=17 × wz_std 3 종, 목표 mp8 t=33 120 주기 × 2 종. → [j408_wobblesim.txt](../debug_log/2026-09-17/outputs/j408_wobblesim.txt).
- job411(job410 **옛 판**): T 0.15/0.22/0.3 × 통로 mp11 t=19 · 입구 · 목표 → 폐기(M2). [j411_tempsim.txt](../debug_log/2026-09-17/outputs/j411_tempsim.txt).
- job412(job410): 통로 seed 1~3 × {이상 구동계 T 0.15 · 실측 T 0.15 · 실측 wz_std 0.3 · 실측 T 0.22 · 실측 T 0.3}, 입구 seed 1·2 × T 3 종, 목표 200 주기 × seed 2 × T 3 종 → §12.5. [j412_tempsim2.txt](../debug_log/2026-09-17/outputs/j412_tempsim2.txt).
- job413(job410): 통로 seed 1~3 × 7 변형(이상 T 0.15 · 가속 제한만 · 지연 · 이득만 · 이상 T 0.3 · 실측 T 0.15/0.22/0.3) → §12.4. [j413_wobblecause.txt](../debug_log/2026-09-17/outputs/j413_wobblecause.txt).
- 결함: 모두 §14.1 의 4 가지 차이를 가진 모델 위의 결과. 지금 다시 돌리면 같은 숫자가 나오는지(난수 seed 고정 — numpy `default_rng(seed)`)는 job408 · 412 · 413 은 가능, job411 은 불가(M2).

### job410_mppi_sim_lag.py · job419_mppi_sim_humble.py — 시뮬레이터 본체
- 코드 수준 해설은 [오프라인 MPPI 시뮬레이터 카드](mppi-offline-simulator.md). 이 카드에서 중요한 것: job410 은 '매 반복 새 잡음 · 후보 clip · 출력 [0]', job419 `humble=1` 은 '고정 잡음 · clip 없음 + ConstraintCritic · 스텝 0 측정 속도 · SG 필터 + [1] 출력'.

### job418_mppisrc.sh — 설치 헤더 grep (읽기 전용)
- 실행: Jetson, `run_j418.sh`(b · c 는 SG 필터 · 운동 모델 헤더 본문 확인용 `run_j418b.sh` · `run_j418c.sh`).
- 하는 일: `/opt/ros/humble/include/nav2_mppi_controller` 아래 `.hpp` 에서 `regenerate` · `generateNoisedControls` · `savitsky` · `control_history` · `temperature|gamma|softmax|exp(` · `updateInitialStateVelocities|propagateStateVelocities` · `shift` 를 grep 해 줄을 200 자로 자름.
- 출력: [j418_mppisrc.txt](../debug_log/2026-09-17/outputs/j418_mppisrc.txt) · [j418b_sgfilter.txt](../debug_log/2026-09-17/outputs/j418b_sgfilter.txt) · [j418c_motion.txt](../debug_log/2026-09-17/outputs/j418c_motion.txt). `.cpp` 본문(optimizer · noise_generator · constraint_critic)은 github 태그 1.1.20 에서 봤다고 SUMMARY 에 적혀 있고 PC 사본은 없음(**원천 소실** — 다시 받을 수는 있음).
- 쓰인 곳: §14.1 표 (a)~(d).

### job420 · job421 · job421b · job423 — Humble 모드 배치
- 공통: job419 `humble=1` + 위 공통 인자 + 실측 구동계, `cycles=60`(6 s).
- job420: mp11 t=19 seed 1~3 · mp12 t=17/19 seed 1~2 × T 0.15/0.3 → §14.2.
- job421: mp11 · mp12 t=19 × seed 1~2 × T × {`dyn_path=1` R · `dyn_path=2` D · `dyn_path=2 dyn_cost=1` C}. **무효**(M3). job421b: D · C 만 `local` 로 재실행 → §14.3.
- job423: `dyn_path=1` 고정, mp11 seed 1~6 · mp12 seed 1~3 × T 0.15/0.3 × `regen=0/1` → §14.5.

### job415_sectors.py — 출발 자리 비교(§13.1)
- 실행: Jetson. 현재 스캔과 mp10 · mp11 출발 스캔의 전/후 복도 최근접을 비교해 로버가 10.5 cm 뒤에 있음을 계산(요 같다고 가정). [j415_sectors.txt](../debug_log/2026-09-17/outputs/j415_sectors.txt). ICP(job370)는 Jetson 에서 10 분 넘게 안 끝나 중단(`outputs/j414_startpose.txt`). 이 카드에서는 mp12 준비 맥락으로만 쓰임.

### job416_boxclear.py — 코스트맵 기준 상자 여유
- 실행: Jetson, `python3 job416_boxclear.py BAG GOAL_EPOCH`.
- 왜: 러너 ① '0.0 cm' 가 사실인지(§13.4).
- 하는 일: bag `/local_costmap/costmap`(t −2~40 s)마다 header stamp 에 가장 가까운 `odom→base_link` 로 LETHAL(=100) 셀 중심을 차체 좌표로 옮기고 거리 = hypot(max(|x|−0.25, 0), max(|y|−0.165, 0)) − 0.025(반셀). 상자 영역 = odom x 0.9~1.6, y −0.3~+0.2. 12~30 s 는 줄마다 출력.
- 출력: 시각별 줄 + '상자 LETHAL ↔ 차체 최소'. j417 안, [j416_mp12_boxclear.txt](../debug_log/2026-09-17/outputs/j416_mp12_boxclear.txt).
- 결함: 셀 양자화로 물리 여유보다 최대 ≈3.5 cm 작게 나올 수 있음(보수적). 상자 영역이 odom 고정 사각형 — 상자 배치가 바뀌면 고쳐야 함. 패딩 없는 외곽 기준(컨트롤러 둘레 검사는 패딩 0.01 포함).
- 계보: 09-18 job446 · job452 의 'LETHAL 여유' 가 같은 정의, 09-21 기준선 '코스트맵(로컬) 상자 최소 여유(job416)'. 지금도 쓸 수 있음(코스 좌표 조건부).

### job417_compare.sh — mp9~12 같은 지표 묶음
- job407 을 네 bag 에, job416 을 각각 돌리고 상자 최소 줄 · 14~29 s 줄만 grep. [j417_compare.txt](../debug_log/2026-09-17/outputs/j417_compare.txt). → §13.3 · §13.4.

### job422_sensnoise.py — EKF 상태 잡음
- 실행: Jetson, `BAG GOAL_EPOCH …`.
- 하는 일: (1) 정지 = 목표 시각 −6 ~ −0.5 s 의 `/odometry/filtered` ω · v std, `odom→base_link` yaw(unwrap) · x · y std. (2) 통로 = 10 Hz 격자 선형 보간, odom x 0.6~1.45 에서 yaw 2 차 차분 RMS, ω 0.1 s 차분 RMS, 차체 횡방향 이동/주기 RMS(−dx sin ψ + dy cos ψ).
- 출력: [j422_sensnoise.txt](../debug_log/2026-09-17/outputs/j422_sensnoise.txt). §14.4. 부수 관찰 '횡방향 0.0000 m' 는 §5 의 근거.

### job424_latwobble.py — 위치 영향
- 하는 일: 20 Hz 격자, 통로 표본마다 ±10 표본(±0.5 s) 창에 x · y · yaw 각각 2 차 다항식 맞춤, 중심 시각의 잔차를 진행 방향 수직(횡)과 yaw 로. RMS · 최대.
- 출력: [j424_latwobble.txt](../debug_log/2026-09-17/outputs/j424_latwobble.txt). §14.6.
- 결함: odom 은 옆미끄럼이 없어 횡 잔차는 구조적으로 작다(§5). 창 1 s 안에 반전 주기 0.4~0.67 s 가 1.5~2.5 번 들어가 2 차식이 흔들림 일부를 흡수할 수 있음(영향 크기 미확인).

## 10. 용어
- **MPPI**(Model Predictive Path Integral): 매 주기 평균 제어열(32 스텝 × 0.1 s)에 잡음을 더한 후보 1000 개를 굴려 크리틱 비용을 매기고, 비용으로 가중 평균해 새 평균 제어열을 만드는 표본 기반 예측 제어. 출력은 그 평균열의 첫 원소(Humble 1.1.20 은 SG 필터 뒤 [1]).
- **softmax temperature**: 가중 wᵢ = exp(−(cᵢ − c_min)/T) / Σ. T 가 작을수록 최저 비용 몇 개에 가중이 몰린다(날카로운 선택). 비용 차 Δc 는 T 로 나뉘므로 T 를 절반으로 하면 지수 안 차이가 두 배.
- **유효 표본 수 ESS**: 1/Σwᵢ². 가중이 고르면 1000, 한 표본에 몰리면 1. 평균 제어의 표본 잡음은 대략 std/√ESS 로 커진다(독립 표본 평균의 표준오차 근사).
- **크리틱 가중(cost_weight)**: 각 크리틱 비용에 곱하는 계수. 크리틱 간 균형이 행동을 정한다(예: PathAlign 14 · PathFollow 10 · CostCritic 3.81 — 이 시기 값).
- **regenerate_noises**: 1.1.20 기본 false — 잡음 표본을 초기화 · reset 때만 만들고 이후 주기 · 반복에서 재사용.
- **Savitzky-Golay 필터**: 이웃 9 점에 2 차 다항식을 맞춘 것과 같은 고정 계수(−21, 14, 39, 54, 59, 54, 39, 14, −21)/231 의 평활. 1.1.20 은 최적화 뒤 제어열에 적용.
- **상호상관 지연(cross-correlation lag)**: 두 신호를 L 만큼 밀어 상관계수가 최대가 되는 L. 여기선 명령 ω 와 실제 ω 의 시간 어긋남.
- **바퀴 포화(비례 축소)**: 펌웨어가 v ± ω·(B_eff/2) 중 한쪽 바퀴가 0.085 m/s 를 넘으면 두 바퀴를 같은 비율로 줄인다 — 곡률은 유지, 속도(v · ω 둘 다)는 줄어든다(10-26 §10.1).
- ObstaclesCritic · CostCritic 은 [CostCritic 카드 §10](obstacles-to-costcritic.md).
