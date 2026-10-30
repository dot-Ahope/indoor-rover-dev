# 상자를 크게 도는 이유 · 여유 불합격 분해 → ObstaclesCritic 을 CostCritic 으로

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결(교체 채택)** — 09-21 cc1~3 판정 5 기준 합격 · 코스트맵 기준 여유 dy 2.5~5.1 → cc 8.4~10.8 cm. 넓게 도는 것 자체는 '코스 기하 + NavFn 골짜기' 로 설명되어 고치지 않음(설계상 정상) | 09-17 §15 · 09-18 §13.6 ~ §17.5 (이 카드), 이후 09-21 §1~§4 · BASELINE_STVL | [09-17 §15 사용자 질문 "상자를 지날 때 크게 돌아가는 이유"](../debug_log/2026-09-17/SUMMARY.md) · [09-18 §13.6 여유 불합격](../debug_log/2026-09-18/SUMMARY.md) | `ros2_ws/src/rover_navigation/config/nav2_params.yaml` `FollowPathMPPI.critics`(ObstaclesCritic → CostCritic) · `CostCritic: {…}` 한 줄(09-18 §17.5, md5 `2a91eb8a3f47`). 계측: `jobs/job125_avoid3.py`(러너 1안) · `job231_drive.sh` · `job451_paramsnap.py` · `job453_runmeta.sh`(09-18 §17.3~17.4) | [조향 흔들림 · temperature](mppi-wobble-temperature.md)(§13.4 여유 ≈2 cm 가 출발점) · [오프라인 MPPI 시뮬레이터](mppi-offline-simulator.md)(job452) · [센서 데크 yaw](sensor-deck-yaw.md)(09-17 §15.5 로컬 상자 드리프트의 진짜 원인) · [inflation · padding 역할](inflation-padding-roles.md) · [회피 주행 계측 결함](avoid-run-metrics.md)(러너 상자 모델) |

**한 줄**: '상자를 크게 돈다' 는 질문을 층별로 나누니 측면 간격 13~15 cm 는 코스트맵 상자 부풀림 2~7 cm + 내접 여유 ≈4 cm + NavFn 비용 골짜기 1~9 cm + MPPI 2~4 cm 가 쌓인 것이었고, 큰 S 자는 상자가 출발-목표 직선 한가운데 있는 코스 탓이었다(09-17 §15). inflation 을 줄여도 경로는 상자 쪽으로 오지 않았다(NavFn 근사 재팽창). 다음 날 데크 보정 뒤 6 회(dy1~6)에서 여유 ≥ 5 cm 기준이 1 회(dy4 4.1 cm) 불합격하자(09-18 §13.6), 여유가 줄어드는 곳을 원경로 → 스무딩 → 실제로 분해했다: 스무더는 영향 0, 여유는 **원경로의 옆 위치**가 정하고, 컨트롤러는 평균 1~2.5 cm 더 붙는다. 컨트롤러가 여유를 벌리지 못하는 이유는 1.1.20 **ObstaclesCritic 이 consider_footprint 에서 옆 여유 17.5 cm 안을 모두 같은 비용으로 보고**, 거리 역산 파라미터도 YAML 누락으로 기본 10/0.55 로 돌고 있었기 때문(§15.3). 얻고 잃는 것을 표로 정리하고(§16), 시뮬(job452)로 막을 신호가 없음을 본 뒤 배포(§17), 09-21 실주행 3 회로 채택.

## 1. 증상
- 사용자(09-17 §15): "상자를 지날 때 크게 돌아가는 이유". 상자는 18 × 14 × 11 cm, 출발점 정면 ≈1.15 m, 목표 (2.0, 0) 은 상자 바로 뒤 0.7 m(BASELINE_STVL §1 코스 서술).
- 09-17 §13.4: 컨트롤러가 보는 여유(로컬 코스트맵 LETHAL ↔ 차체 외곽)는 mp9~12 에서 **1.4~2.6 cm** — 동시에 '물리 측면 간격' 은 13~15 cm(§15.4). 크게 도는 듯 보이면서 코스트맵 기준으로는 붙어 있는 두 모습.
- 09-18 §13.6: 데크 yaw 보정 뒤 dy1~dy6 복귀 회전 자리(x 1.10~1.25) 로컬 코스트맵 여유 6.5~7.8 · 7.2~8.7 · 5.9~7.7 · **4.1~4.6** · 7.1~8.5 · 8.7~10.2 cm → '매 회 ≥ 5 cm' **불합격**. 최소 여유는 상자 뒤 모서리(t 22~25 s)에서 2.5~5.1 cm.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-17 §15.1 | `/plan` vs 실제 궤적 횡 위치(map)(`job425_detour.py` A) | 상자 옆 x 1.2: mp12 경로 +0.33(t=10.5 +0.31) · 궤적 +0.35, mp11 +0.39(+0.35) · +0.37, mp9 +0.41(+0.35) · +0.38. 경로는 x 0.4~0.6 부터 옮김, 로버는 x 0.4 에서 경로보다 6~12 cm 왼쪽(최대 yaw mp12 +40°, mp9/11 +25~28°) | **경로가 먼저 넓고** 로버는 더 일찍 꺾고 상자 옆에서 2~4 cm 더 왼쪽 | [j425_detour.txt](../debug_log/2026-09-17/outputs/j425_detour.txt), bag `2026-09-17/bags/bag_mp9 · mp11 · mp12.tgz` `/plan` · `/tf` |
| 09-17 §15.2 | 전역 코스트맵 단면(B, mp12 t=10) | x 0.3 에서 y 0 도 115(복도 양 벽 inflation 0.70 겹침), x 1.2: +0.25 236 · +0.30 216 · **+0.35 195** · +0.40 198 · +0.45 216 · +0.50 231 · +0.55 247, 오른쪽은 −0.35/−0.40 에 234~236 한 칸뿐 | 골짜기 최저 = 상자 내접선(+0.20)과 왼쪽 벽 내접선(+0.60)의 가운데. NavFn(50 + 0.8·c 적분 최소)은 그 중앙을 탄다 | 같은 파일 |
| 09-17 §15.3 | NavFn 근사(C, 8-이웃 Dijkstra) · 재팽창(D) | 근사가 실제 /plan 상자 옆을 −2~−5 cm 로 재현(mp12 +0.308 vs +0.326 등). R/k 0.70/2.0 → +0.31, 0.55/2.0 +0.31, 0.40 · 0.30 · 0.70/4.0 · 0.55/4.0 · 0.40/4.0 · 0.70/8.0 모두 **+0.36**, 차선변경 시작 x 0.6~0.7 | **inflation 수치는 '크게 도는' 주원인이 아니다** — 통과 가능한 가장 가까운 자리(d 0.20~0.30)의 비용이 k ≤ 4 에서 150~240 으로 자유 공간의 3~5 배 | 같은 파일 |
| 09-17 §15.4 | 횡 위치 예산(물리 상자 끝 → 궤적) | 물리 좌끝 +0.038/+0.069/+0.086, 전역 LETHAL 좌끝 +0.08/+0.09/+0.16, 통과 최소 중심선 +0.25/+0.26/+0.34, 전역 경로 +0.31/+0.35/+0.35, 궤적 +0.35/+0.37/+0.38 → **물리 측면 간격 14.7/13.6/12.9 cm**(mp12/mp11/mp9) | 13~15 cm = 부풀림 2~7 + 내접 ≈4 + 골짜기 1~9 + MPPI 2~4. S 자는 코스 | 같은 파일(물리 끝은 '게이트 깊이 중심 + 실측 폭/2' 추정) |
| 09-17 §15.5 | 로컬(odom) vs 전역(map) 상자(`job426_boxframes.py`) | 통과 중 map→odom dy +0.03 → +0.08 m, 로컬 상자 좌끝(map 환산) − 전역: mp12 +3.5~+7.1 · mp11 +7.3~+8.3 · mp9 +0.7~+3.2 cm | 로컬 상자가 로버 쪽으로 2~8 cm. 원인을 'odom 이 차선변경 중 횡이동을 덜 셈 — 스키드스티어 옆미끄럼 추정' 으로 봄 — **틀림**(09-18 §9: 데크 yaw −2.68° 장착 오차) | [j426_boxframes.txt](../debug_log/2026-09-17/outputs/j426_boxframes.txt) → [센서 데크 yaw 카드](sensor-deck-yaw.md) |
| 09-17 §15.6 | 결론 · 손잡이 후보(오늘은 안 바꿈) | (a) 코스 배치 (b) 로컬 상자 드리프트 — decay 단축은 기각, 옆미끄럼 · 로컬 map 프레임화 검토 (c) PathFollow offset 축소 — 09-16 입구 정지 위험 (d) SmacHybrid — 각도만 | — | — |
| 09-18 §9~§13 | 데크 yaw 보정 → dy1~dy6 | 로컬−전역 상자 좌끝 차 dy4 +0.000~+0.010 m(§13.5) — 드리프트 해소. 그러나 여유 불합격(dy4 4.1 cm), dy4 로버 odom y 0.260(dy5 0.30, dy6 0.32~0.34) | '드리프트가 아니라 지나간 선' — 컨트롤러가 더 붙는 선을 골랐다 | [센서 데크 yaw 카드](sensor-deck-yaw.md), `2026-09-18/outputs/j435_dy4_verify.txt` |
| 09-18 §14 | 사용자 결정: 러너 상자 모델 1안(재고정은 출발 yaw ±5° 안에서만), 순서는 여유 불합격 대응 먼저 | 라이다는 상자를 못 봄(dy6 출발 전 스캔 20 장에서 상자 자리 ±5 cm 점 0, 같은 방향 빔 2.73 m 벽; 라이다 면 지면 위 ≈0.21 m) | 2안(점군 직선 맞춤) 기각 — 보이는 면 1~2 개 · 점 수 적음 | [j445_lidarbox.txt](../debug_log/2026-09-18/outputs/j445_lidarbox.txt) |
| 09-18 §15.1 | 여유 분해 원경로 → 스무딩 → 실제(`job446_pathdecomp.py`, dy1~6) | 복귀 회전 x 1.10~1.25(L=3 s, 24 표본): **9.4 → 9.2 → 8.0** cm(스무딩 Δ −0.1, 컨트롤러 Δ −1.2). 상자 뒤 모서리 x 1.35~1.55(18 표본): **9.5 → 9.4 → 6.9**(Δ −0.1, **−2.5**). 회차별 원경로 여유(복귀 회전) dy4 **4.8~7.1** · dy6 12~15 | 스무더는 영향 없음(≤ 0.5 cm) — 앞선 곡률 어림 '3~4 cm 당긴다' **틀림**. dy4 는 원경로 자체가 붙었다 | [j446_pathdecomp.txt](../debug_log/2026-09-18/outputs/j446_pathdecomp.txt), bag `2026-09-18/bags/bag_dy1~6.tgz` |
| 09-18 §15.2 | 원경로 옆 위치가 회차마다 다른 이유(`job448_leftwall.py`) | 통로(상자 좌끝 ↔ 왼쪽 LETHAL) 0.55~0.60 m, 원경로는 6 회 중 5 회 통로 중앙보다 상자 쪽 **2.4~5.6 cm**(dy6 만 −1.7). 비용 단면 골은 얕음(0~100 척도 중앙 71~77, ±5 cm 80~84) | dy4 = 가장 좁은 통로 0.55 + 가장 큰 치우침 5.6 cm | [j448_leftwall.txt](../debug_log/2026-09-18/outputs/j448_leftwall.txt) |
| 09-18 §15.3 | 1.1.20 소스 · README 대조 + 정적 비용 곡선(`job449_criticcurve.py`) + 실행 중 값(`job451_paramsnap.py`) | ① consider_footprint 에서 중심 비용 ≥ 외접 비용(≈178, 중심↔장애물 0.313 m 안)이면 둘레 최대 비용 → 둘레가 장애물 0.175 m 안이면 늘 253 → 거리 0.175 고정 ② `cost_scaling_factor` · `inflation_radius` 를 크리틱 자기 파라미터에서 읽는데 YAML 누락 → 실행 중 **10.0 / 0.55**(코스트맵은 2.5/0.40) ③ 옆 여유 1~25 cm 에서 Obstacles 비용 0.56(현재) · 0.34(값 맞춤 · margin 0.10) **일정** ④ CostCritic w 3.81: W 0.55 에서 5 cm 3.42 → 11 cm 2.94(기울기 ≈0.08 /cm) vs 경로 크리틱 ≈0.24 /cm → 정적으로는 경로 여유를 그대로 따름(가중 12 에서야 중앙으로) | 여유를 정하는 것은 **전역 원경로의 옆 위치**. 고칠 1 순위 = 계획, 크리틱 교체 = 2 순위(정확성 수정 · 모서리 안쪽 붙음). **09-17 메모 'inflation = 여유 선호' 는 MPPI 컨트롤러엔 해당 안 됨**(전역 계획엔 해당) | [j447_mppi_ver.txt](../debug_log/2026-09-18/outputs/j447_mppi_ver.txt) · [j449_criticcurve.txt](../debug_log/2026-09-18/outputs/j449_criticcurve.txt) · [j451_paramsnap_test.txt](../debug_log/2026-09-18/outputs/j451_paramsnap_test.txt), 소스 사본 `2026-09-18/refs/mppi_1.1.20_obstacles_critic.cpp` · `mppi_1.1.20_cost_critic.cpp` |
| 09-18 §16 | 교체 근거 표(얻음 · 잃음 · 위험 · 변화 없음) + 설정 · 판정 기준 선언 | 설정 `{cost_weight 3.81, critical_cost 300, consider_footprint true, collision_cost 1e6, near_goal_distance 0.5}` — 0.5 유지 이유: README 예시 1.0 이면 상자 뒤 모서리(목표 0.65~0.75 m 안)에서 기울기가 꺼짐. 기준: 중단 0 · 1 s 정지 0 / 모서리 Δ > −2.5 cm / 복귀 회전 여유 기록(≥ 5 목표) / 복귀 회전 도달 ≤ dy 범위 + 1 s / 직진 부호반전 ≤ 9 /m / 루프 미달 ≤ 1 | '잃음: 기준선 연속성' — **과장**(§17.1 정정, 사용자 지적) | 09-18 SUMMARY 표 |
| 09-18 §17.1 | 사용자 지적 처리 | S5 기준선은 아직 측정 전 → 어차피 3 회 새로 → 추가 비용 0. 남는 손실은 통계 누적뿐 | 정정 기록 | — |
| 09-18 §17.2 | 시뮬 사전 검증(`job452_mppi_sim_cc.py`, dy2 · dy4 · dy6 × 3 장면 × seed 2) | 입구 g8: 전진 −4 %, LETHAL 여유 최소 4.1 → **5.6**(+1.5), 반전 12.5 → 10.5. 복귀 회전 g16.5: 4.6 → **5.5**(+0.9), 반전 3.5 → 6.6. 모서리 g20: 5.7 → 5.3(−0.3, 셀 양자화 안), 반전 2.4 → 4.1 · RMS 0.034 → 0.050 | 정체 없음 · 막을 신호 없음. 위험 (a) 입구 지연 −4 %, (b) 셀 계단 흔들림 소폭 — 기준 ≤ 9 /m 안 | [j452_sim_cc.txt](../debug_log/2026-09-18/outputs/j452_sim_cc.txt) · [j452_sim_cc_table.txt](../debug_log/2026-09-18/outputs/j452_sim_cc_table.txt) → [시뮬 카드 §4.5](mppi-offline-simulator.md) |
| 09-18 §17.3 | bag 재현성 — 토픽 `/plan_smoothed` · `/unsmoothed_plan` 기본 추가 + `BAG_EXTRA`, 실행 파라미터 스냅샷 `params.txt`(job451, 12 노드 5.6 s), 주행 메타 `run_meta.txt`(job453) | 시험: 메타 9.1 s, 12 노드 전부 응답, 파일 해시 10 개. heredoc `\\n` 사고 → Edit 로 고치고 확장 결과 검증 | '유동적이지 않고 재현 정보 부족' → 적용 | [j453_metatest.txt](../debug_log/2026-09-18/outputs/j453_metatest.txt), `jobs/job231_drive.sh` · `run_drive_nohup.sh` · `job254_s4run.sh` · `run_post3.sh` |
| 09-18 §17.4 | 러너 1안(`job125_avoid3.py`, 백업 `.bak_0918b`) | 재고정은 \|yaw − 출발 yaw\| ≤ 5° 일 때만, `/tmp/<이름>_refix.csv` 기록 | 첫 실주행에서 ① vs job416 일치 확인 예정 | — |
| 09-18 §17.5 | 배포(`run_deploy_cc.sh`) | 주석 제외 diff = critics 목록 1 줄 + CostCritic 1 줄, md5 `2a91eb8a3f47`(src · install · 전송본 같음), 이전본 `~/ros2_ws/.bak_20260918/install_nav2_params_before_cc.yaml` | 실행 중 controller 는 옛 목록 — 다음 prep 반영 | [j454_deploy_cc.txt](../debug_log/2026-09-18/outputs/j454_deploy_cc.txt) |
| 이후 09-21 §1~§4 | cc1~cc3(STAGE=cc) | 3/3 성공, 중단 · 1 s 정지 0, 모서리 Δ +2.8~+3.0 · +1.8~+1.9 · −1.8~+2.5, 복귀 회전 여유 9.3~10.0 · 8.4~8.5 · 10.7~10.8 cm, 도달 15.5 · 16.6 · 17.1 s, 직진 부호반전 5.2 · 2.0 · 1.05 /m, 루프 미달 **18** · 0 · 0(cc1 = 주행 직전 메타 스냅샷의 DDS 부하 — 스냅샷을 bag 종료 뒤로 옮겨 해소) | **CostCritic 채택**. ObstaclesCritic 블록은 YAML 에 남기고 목록에서 제외. 시뮬 예측(+0.9~1.5, 모서리 0)보다 실측이 큼 | [09-21 SUMMARY](../debug_log/2026-09-21/SUMMARY.md) |
| 이후 09-21 BASELINE | cc2~cc5 기준선 | 4/4 성공 31.5 s, 코스트맵(로컬) 상자 최소 여유 8.4~12.9 cm, 복귀 회전 ≥ 8.1, 직진 부호반전 1~5.6 | Phase S 기준선 | [BASELINE_STVL.md](../debug_log/2026-09-21/BASELINE_STVL.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| inflation 이 커서 크게 돈다 | NavFn 근사로 같은 LETHAL 칸을 R · k 8 조합으로 재팽창(job425 D) | 상자 옆 횡 +0.31~+0.36, 차선변경 x 0.6~0.7 — 줄여도 안 붙음 | **기각**(근사 오차 2~5 cm 안). 근거식: 252·exp(−k(d − 0.175)) 가 d 0.20~0.30 에서 150~240 |
| 크게 도는 주원인은 코스 기하 + NavFn 골짜기 | 횡 위치 예산(§15.4) · 단면(§15.2) | 층별 합이 13~15 cm 를 설명 | **지지** |
| 로컬 상자가 2~8 cm 다가온 것은 스키드스티어 옆미끄럼 | 09-18 §9 bag 재분석 · 정지 측정 | 옆미끄럼 기각, 데크 yaw −2.68° | **기각**(09-18) → [데크 카드](sensor-deck-yaw.md) |
| 스무더가 경로를 상자 쪽으로 3~4 cm 당긴다(곡률 어림) | SimpleSmoother 이식으로 원경로에 적용(job446) | Δ ≤ 0.5 cm | **기각**(측정) |
| 여유 불합격은 원경로가 회차마다 상자 쪽으로 치우친 탓 | job446 회차별 원경로 여유 · job448 통로 중앙 대비 | dy4 원경로 4.8~7.1, 중앙 대비 +5.6 cm(최대) · 통로 0.55(최소) | **지지** |
| 컨트롤러가 여유를 못 벌리는 것은 ObstaclesCritic 이 17.5 cm 안 거리를 구분 못 하기 때문 | 1.1.20 소스 · 정적 비용 곡선(job449) · 실행 중 파라미터(job451) | 1~25 cm 에서 비용 일정, 파라미터 10/0.55 | **지지**(소스 · 계산). 실주행 효과는 09-21 cc 로 확인 |
| CostCritic 기본 가중만으로 여유 불합격이 풀린다 | job449 정적: 기울기 0.08 /cm < 경로 0.24 /cm → 경로를 따름. job452: +0.9~1.5 cm | 정적 · 시뮬은 '못 푼다' 쪽 | 09-21 실측은 복귀 회전 3/3 ≥ 8.4 cm 로 **기대보다 큼**(원인 분리 안 됨 — cc 날 원경로 위치 · 상자 배치 차이와 섞임, §5) |
| CostCritic 이 입구 차선 변경을 늦춘다(§16 위험 a) | job452 입구 −4 % · 09-21 도달 시각 | cc 15.5~17.1 s ≤ 19.9 | **기각**(실주행) |
| 5 cm 셀 계단이 점수에 들어와 부호반전이 는다(§16 위험 b) | job452 모서리 반전 2.4 → 4.1 · 09-21 직진 부호반전 | cc 1.05~5.2 /m(dy 5~6) | **기각**(실주행, 시뮬 예측과 반대) |

## 4. 조치와 효과
| 시점 | 바꾼 것 | 전 | 후 |
|---|---|---|---|
| 09-18 §17.5 → 09-21 첫 기동 | `critics` 의 ObstaclesCritic → **CostCritic**, `CostCritic: {enabled: true, cost_power: 1, cost_weight: 3.81, critical_cost: 300.0, consider_footprint: true, collision_cost: 1000000.0, near_goal_distance: 0.5}` | dy1~6: 코스트맵 최소 여유 2.5~5.1 cm, 복귀 회전 4.1~10.2, 모서리 Δ −2.5(평균) | cc1~3: 8.4~10.8, 9.3~10.8, Δ −1.8~+3.0 |
| 09-18 §17.3 | bag 토픽 · `params.txt` · `run_meta.txt`(재현 정보) | 실행 중 파라미터 · 스무더 결과 미기록 | 09-21 부터 모든 주행 폴더에 남음(CLAUDE.md '주행 재현 규칙') |
| 09-18 §17.4 | 러너 재고정 yaw ±5° | mp12 · dy3 러너 ① 0.0 cm(모델 오류) | 09-21 재고정 채택 1 · 건너뜀 44~48(사실상 출발 때 사각형 유지) |
- 한계: cc 3 회의 여유 증가가 전부 크리틱 덕인지는 분리되지 않았다(같은 날 상자 배치 1.154~1.164 / −0.050~−0.097, cc2 는 원경로가 더 붙었는데도 컨트롤러가 밖으로 +1~2 cm 벌려 8.4 cm — 09-21 §2). n = 3.

## 5. 한계 · 모순 기록(원문 대조)
- **09-18 §15.1 의 '컨트롤러 Δ −2.5'(상자 뒤 모서리)는 L = 3 s 기준값만**이다. 같은 출력의 L = 2 s 줄은 원경로 8.4 → 실제 6.9, Δ **−1.3**([j446_pathdecomp.txt](../debug_log/2026-09-18/outputs/j446_pathdecomp.txt) 마지막 줄). §16 판정 기준 'Δ 가 −2.5 cm 보다 작아질 것' 은 L 선택에 민감한 값을 기준으로 삼았다. 09-21 cc 값은 −1.8~+3.0 이라 어느 L 로도 합격.
- **09-17 §15.5 의 원인 서술(옆미끄럼)** 은 다음 날 뒤집혔다 — 09-17 SUMMARY 본문은 고쳐지지 않았으니 이 칸과 [데크 카드](sensor-deck-yaw.md)를 같이 볼 것. 09-18 §11.2 에는 그 분석 도구(job431 · job431b)의 버그 정정도 있다(데크 카드 범위).
- §15.3 ④ 와 §16 의 '경로 크리틱 ≈0.24 /cm' 는 당시 PathAlign 14 + PathFollow 10 = 24 /m 의 선형 근사(job449 docstring). **현재 설정은 PathAlign 28 · PathFollow 5**(`nav2_params.yaml` 280 · 284 행, 10-26) → 같은 근사로 33 /m = 0.33 /cm. CostCritic 3.81 의 상대적 '중앙 끌림' 은 당시보다 더 약하다(계산상 — 실주행 영향은 이 카드 범위 밖).
- **현재 YAML 의 ObstaclesCritic 블록**(265 행)은 'A/B 복귀용' 으로 남아 있지만 여전히 `cost_scaling_factor` · `inflation_radius` 가 없다. 목록에 다시 넣으면 09-18 이전과 같이 기본 10.0 / 0.55 로 돈다(1.1.20 README 'Humble only'). 현재 동작에는 영향 없음(목록에 없음).
- 09-18 §16 '잃음: 시뮬 사전 검증 불가' 는 같은 날 §17.2 에서 job452 로 해소(모순 아님, 순서 기록).
- 09-21 §4: 시뮬(job452)이 예측한 '모서리에서 반전 · RMS 소폭 증가' 와 달리 실주행 직진 부호반전은 줄었다 — 시뮬의 흔들림 크기는 믿지 않는다는 [시뮬 카드 §6](mppi-offline-simulator.md) 규칙과 같은 사례.
- job446 의 '중심 비용' 환산은 `round(v·252/98)` 로 costmap_2d 의 `1 + (v−1)·251/97` 과 1 단위 안팎 다르다(스무더 중단 조건 > 252 판정에는 99/100 → 253/254 가 따로 처리돼 영향 없음).
- job425 의 NavFn 근사는 출발 (0, 0) · 목표 (2.0, 0) 를 코드에 고정했다(이 코스 전용).

## 6. 내 실수
### M1. '스무더가 3~4 cm 안쪽으로 당긴다' (09-18 §15.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 여유가 어디서 줄어드는지 단계별로 나누기 |
| 본 것 | (분해 전) 원경로와 실제 궤적 차이, 경로 곡률 |
| 처음 추론 | 곡률로 어림해 SimpleSmoother 가 S 자 안쪽(상자 쪽)으로 3~4 cm 당긴다 |
| 의심한 이유 | bag 에 스무딩 결과가 없어 어림만 있었고, 측정이 아니었다 |
| 판별 시험 | `job446_pathdecomp.py` 에 nav2_smoother SimpleSmoother(Humble) `smoothImpl` 을 이식(w_data 0.2 · w_smooth 0.3 · tol 1e-10 · max_its 1000 · 정밀화 4 회 · 점 비용 > 252 면 직전 경로로 중단)해 원경로에 적용, 같은 전역 코스트맵으로 세 단계 여유 |
| 결론 | 스무딩 Δ −0.1~−0.2 cm(≤ 0.5). 어림은 틀렸다 |
| 다음에 알아보는 법 | 중간 단계 산출물이 bag 에 없으면 어림 대신 그 단계를 소스 그대로 재현해 측정하거나, 다음 주행부터 그 토픽을 기록한다(→ §17.3 에서 `/plan_smoothed` 추가) |
| 데이터 | [j446_pathdecomp.txt](../debug_log/2026-09-18/outputs/j446_pathdecomp.txt), `jobs/job446_pathdecomp.py`, bag `bag_dy1~6.tgz` `/plan` · `/global_costmap/costmap` · `/tf` |

### M2. 'inflation = 여유 선호' 를 MPPI 에도 적용 (09-17 메모 → 09-18 §15.3)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 컨트롤러가 왜 원경로보다 여유를 더 벌리지 않는지 설명 |
| 본 것 | job446: 컨트롤러 Δ 평균 −1.2~−2.5 cm(밖으로 안 벌림) |
| 처음 추론 | 09-08 에 정리한 원리(inflation 은 연성 비용 = 여유 선호)가 컨트롤러에도 작동한다고 전제(메모 'inflation = 여유 선호') |
| 의심한 이유 | 그 전제라면 통로 가운데로 끌리는 힘이 있어야 하는데 컨트롤러는 경로를 거의 그대로 따랐다 |
| 판별 시험 | 1.1.20 `obstacles_critic.cpp` 를 읽고 그 식 그대로 정적 비용 곡선(job449) + 실행 중 파라미터(job451) |
| 결론 | consider_footprint 에서 옆 여유 17.5 cm 안은 비용 일정 + 파라미터 누락. 원리는 전역 계획(NavFn)에는 맞고 이 컨트롤러 크리틱에는 안 맞았다 |
| 다음에 알아보는 법 | '비용이 여유를 선호하게 한다' 는 원리는 **그 비용을 읽는 쪽(계획기 · 각 크리틱)이 거리 기울기를 실제로 보는지** 소스로 확인한 뒤 적용한다. README 의 'Humble only' 같은 버전 주석을 찾는다 |
| 데이터 | [j449_criticcurve.txt](../debug_log/2026-09-18/outputs/j449_criticcurve.txt) · [j451_paramsnap_test.txt](../debug_log/2026-09-18/outputs/j451_paramsnap_test.txt) · `refs/mppi_1.1.20_obstacles_critic.cpp`, 원리 출처 [inflation 카드](inflation-padding-roles.md) |

### M3. '기준선 연속성 손실' 을 잃는 것으로 셈 (09-18 §16 → §17.1)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 교체의 얻음 · 잃음을 빠짐없이 적기 |
| 본 것 | mp9~12 · dy1~6(16 회)이 ObstaclesCritic 구성 |
| 처음 추론 | 교체하면 그 16 회와 비교가 끊기므로 '잃음(확인)' |
| 의심한 이유 | 사용자 지적 — 배치가 회차마다 ≈2 cm 다르고 지표는 원래 Δ · 코스트맵 여유 · 중단 횟수로 잡았으며, S5 기준선은 아직 측정한 적이 없다 |
| 판별 시험 | (논리 확인) S5 기준선은 어차피 새로 3 회 |
| 결론 | 추가 비용 0, 남는 손실은 통계 누적('보정 후 중단 1/6' 같은 집계)뿐 — 정정 기록 |
| 다음에 알아보는 법 | '잃음' 을 쓸 때 그 비교가 실제로 계획에 있었는지(이미 측정된 기준인지, 앞으로 잴 것인지)를 먼저 묻는다 |
| 데이터 | [09-18 SUMMARY §16 · §17.1](../debug_log/2026-09-18/SUMMARY.md) |

### M4. 로컬 상자 2~8 cm 를 옆미끄럼으로 추정 (09-17 §15.5 → 09-18 §9)
- 칸 형식 기록은 [센서 데크 yaw 카드](sensor-deck-yaw.md)(다른 카드). 요지: map→odom dy 가 통과 중 3~8 cm 자라는 것을 '차선변경 중 odom 이 횡이동을 덜 센다' 로 봤으나, 다음 날 bag 재분석으로 옆미끄럼을 기각하고 벽에 붙인 정지 측정으로 데크 −2.68° 를 찾음. 데이터 [j426_boxframes.txt](../debug_log/2026-09-17/outputs/j426_boxframes.txt).

### M5. heredoc 안 `\\n` 이 리터럴로 들어감 (09-18 §17.3, 도구 사고)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | `job231_drive.sh` 토픽 목록 수정 |
| 본 것 | 토픽 줄이 한 줄로 합쳐질 뻔함, `bash -n` 은 통과 |
| 판별 · 결론 | Edit 도구로 고치고 **확장 결과**(토픽 18 개 전부 `/` 로 시작)로 검증 |
| 다음에 알아보는 법 | 문법 검사 통과가 내용 검증이 아니다 — 생성된 값을 펼쳐 본다. 메모리 'tool-heredoc-backslash' |
| 데이터 | `2026-09-18/jobs/job231_drive.sh`, SUMMARY §17.3 |

## 7. 남은 것
- '넓게 도는 것' 자체는 고치지 않았다 — 코스(상자가 직선 위, 목표가 바로 뒤)가 원인이고 대표 코스 확장은 이후 F0~F2 로.
- 원경로가 통로 중앙보다 상자 쪽으로 2~6 cm 치우치는 것(§15.2, 얕은 골 · S 자 안쪽이 짧음) — 09-18 §15.3 결론 '고칠 1 순위 = 계획' 은 이 시기에 손대지 않음. 10-27 Smac Hybrid 채택(CLAUDE.md §6)이 같은 질문의 후속인지는 그 시기 카드에서.
- CostCritic 의 여유 증가 중 크리틱 몫 분리(§4 한계).
- ObstaclesCritic 블록의 누락 파라미터(§5) — 다시 켤 일이 있으면 먼저 채울 것.

## 8. 실험 · 도구 색인
- 주행: 09-17 mp9 · mp11 · mp12(분석만), 09-18 dy1~dy6(분석만), 09-21 cc1~cc3(검증) · cc2~cc5(기준선).
- 도구: 09-17 `job425_detour.py` · `job426_boxframes.py`(감싸개 `run_j425.sh` · `run_j426.sh`), 09-18 `job445_lidarbox.py` · `job446_pathdecomp.py` · `job448_leftwall.py` · `job449_criticcurve.py` · `job451_paramsnap.py` · `job452_mppi_sim_cc.py` + `job452_run.sh` · `job453_runmeta.sh` · `run_deploy_cc.sh`(출력 이름 j454), 버전 확인 `run_j447.sh` → `j447_mppi_ver.txt`.

## 9. 도구 해설
공통: Jetson 에서 실행(`rosbag2_py`), PC WSL 의 `run_j4xx.sh` 가 `sshpass -p <PW> scp` 로 `/tmp` 에 올려 돌리고 출력을 받아 `outputs/` 에 둔다. bag 은 PC `Docs/debug_log/2026-09-17|18/bags/*.tgz` 에 남아 있어 **다시 돌릴 수 있다**. 감싸개 안 스크래치패드 경로는 소실 — 저장소 `jobs/` 판을 직접 올린다. 좌표 상수(상자 영역 map x 0.9~1.6, y −0.35~+0.2 등)는 이 코스 전용.

### job425_detour.py — 넓게 도는 이유 4 단(A~D)
- 부른 형태: `python3 job425_detour.py BAG GOAL_EPOCH [1]`(마지막 `1` 이면 D 재팽창 변형까지 — mp12 에만 줌).
- 하는 일: A. `/plan`(t ≥ 0 첫 번째 · t≈10 에 가장 가까운 것)과 실제 궤적(`odom→base_link` 를 그 시각 `map→odom` 으로 map 에) 을 x 0.0~2.0 · 0.1 간격에서 최근접 점(±0.06 m 안)의 y 로 비교, 최대 진행각(4 점 이동평균). B. t≈10 전역 코스트맵을 costmap_2d 비용으로 환산해 x 0.3/0.6/0.9/1.2/1.5/1.8 에서 y −0.50~+0.90(5 cm) 단면, `#` LETHAL · `o` 253 · `?` 미지, 최저 칸. C. NavFn 근사: 비용 칸 → 50 + 0.8·c(253 이상 통과 불가, 미지 253), 8-이웃 Dijkstra(간선 = 두 칸 평균 × 이동 길이), 출발 (0, 0) → 목표 (2.0, 0). D. LETHAL(100) 칸만 남겨 거리장을 다시 만들고 cost = 253(d ≤ 0.175) · floor(252·exp(−k(d − 0.175)))(d ≤ R) · 0 으로 재팽창 → C 로 다시 계획, 상자 옆 횡 · 차선변경 시작 x.
- 출력: [j425_detour.txt](../debug_log/2026-09-17/outputs/j425_detour.txt). §15.1~15.4.
- 결함: 격자 Dijkstra 는 실제 NavFn 퍼텐셜 전파 · 기울기 하강과 달라 횡 2~5 cm 차, 격자 계단. 재팽창 거리장은 LETHAL 칸마다 사각 창을 도는 단순 구현(느림).

### job426_boxframes.py — 로컬 vs 전역 상자
- 하는 일: 로컬 코스트맵 LETHAL 상자 칸(odom x 0.9~1.6, y −0.35~+0.25)을 그 시각 `map→odom` 으로 map 에 옮겨, 가장 가까운 시각 전역 코스트맵 상자 칸과 y 범위 · 중심 · 좌끝 차 비교, map→odom dx · dy · dyaw 와 로버 자세를 함께. 3 s 마다 한 줄.
- 출력: [j426_boxframes.txt](../debug_log/2026-09-17/outputs/j426_boxframes.txt). §15.5 → 다음 날 데크 분석의 출발점.
- 계보: 09-18 `j435_dy*_verify.txt`(C 절)가 같은 비교를 보정 뒤에 반복(데크 카드).

### job445_lidarbox.py — 라이다가 상자를 보나 (§14)
- dy6 출발 전 2 s 스캔 20 장에서 상자 자리 ±5 cm 안 점 수와 같은 방향 빔 거리. 결과 점 0 · 벽 2.73 m. [j445_lidarbox.txt](../debug_log/2026-09-18/outputs/j445_lidarbox.txt). 러너 1안의 '점군은 카메라만' 근거.

### job446_pathdecomp.py — 원경로 → 스무딩 → 실제
- 부른 형태: `python3 job446_pathdecomp.py NAME BAG GOAL_EPOCH [NAME BAG GOAL_EPOCH …]`(dy1~dy6).
- 하는 일: 로버(map)가 X* ∈ {1.10, 1.15, 1.20, 1.25, 1.35, 1.45, 1.55} 에 처음 닿은 시각 t_arr. 그 시각 최신 전역 코스트맵의 상자 LETHAL 칸으로 여유 = 차체 외곽(0.25 × 0.165) ↔ 칸 중심 − 반셀(job416 정의). 원경로 = t_arr − L(3 · 2 s) 직전 `/plan` 을 X* 에서 선형 보간(y)하고 ±2 점으로 접선 방향 → 그 자세로 차체를 놓아 여유. 스무딩 = SimpleSmoother `smoothImpl` 이식(위 M1 칸의 값) 결과로 같은 계산. 실제 = 로버 자세. map→odom 은 같은 stamp 두 번 발행 시 마지막 값(CLAUDE.md 분석 규칙).
- 출력: 주행 · X* · L 마다 한 줄 + '통합' 4 줄. [j446_pathdecomp.txt](../debug_log/2026-09-18/outputs/j446_pathdecomp.txt). §15.1, §16 기준, 09-21 cc 판정 · BASELINE_STVL '컨트롤러 − 원경로 여유 Δ(job446)'.
- 결함: 방향 전환 구간 분할 생략(이 코스는 전진만), 스무더 서버의 풋프린트 충돌 검사는 여유 계산으로 대신, L 에 따라 Δ 가 다름(§5). 지금 다시 쓸 수 있음(이 코스 · 이 토픽).

### job448_leftwall.py — 통로 폭과 원경로 치우침
- 하는 일: 로버가 map x 1.20 에 닿기 3 s 전 `/plan` 과 그 시각 전역 코스트맵에서 상자 LETHAL 좌끝 y(x 1.0~1.4, y < 0.2) · 왼쪽 LETHAL 최근접 y(y > 0.2) → 통로 폭 · 중앙, 원경로 y(x 1.20), 중앙 − 경로, 비용(0~100) 단면 y 0.10~0.60.
- 출력: [j448_leftwall.txt](../debug_log/2026-09-18/outputs/j448_leftwall.txt). §15.2.

### job449_criticcurve.py — 크리틱 비용 곡선(정적)
- 실행: 어디서나(순수 파이썬, bag 안 씀).
- 하는 일: 궤적 32 점이 모두 같은 옆 여유 c 로 상자(오른쪽)와 왼쪽 장애물(통로 폭 W 0.55 · 0.60) 사이를 지난다고 가정. 층 비용 = InflationLayer 식(254 · 253 · 252·exp(−2.5(d − 0.175)) · 0, R 0.40), 외접 0.3134 → POSS. 중심 비용 = max(층(0.165 + c), 층(0.165 + c_left)), 둘레 비용 = max(층(c), 층(c_left)). ObstaclesCritic(1.1.20 식): 중심 ≥ POSS 면 둘레 비용 · 둘레 모드, 거리 역산 (s·0.175 − ln cost + ln 253)/s(둘레 모드 아니면 −0.175), margin 미만이면 crit, 아니면 rep → 20·crit + 1.5·rep/32. 세 설정: 현재(s 10, R 0.55, m 0.05) · 값 맞춤(2.5 · 0.40 · 0.05) · +m 0.10. CostCritic: 중심 ≥ 253 이면 300, 그 밖 중심 비용, × w/254(3.81 · 8 · 12). 경로 크리틱은 |c − c_plan| × 24 /m 로 근사하고 c_plan 3 · 5 · 7 · 10 cm 에서 합이 최소인 c.
- 출력: [j449_criticcurve.txt](../debug_log/2026-09-18/outputs/j449_criticcurve.txt). §15.3 ③ ④, §16.
- 결함: 셀 양자화 무시, 차체 기울기 무시(옆면이 늘 가장 가까움), 경로 크리틱 선형 근사(현재 가중과 다름 — §5).

### job451_paramsnap.py — 실행 중 파라미터 스냅샷
- 실행: Jetson, 인자 없으면 12 노드(`/controller_server` · 두 코스트맵 · planner · smoother · bt_navigator · behavior · velocity_smoother · slam_toolbox · ekf · stuck_monitor · depth_relay). 노드 하나로 각 노드의 `list_parameters` · `get_parameters` 서비스를 직접 불러 `ros2 param dump`(노드당 7.8 s) 대신 한 번의 디스커버리(5.6 s). 응답 없는 노드는 '(없음)'.
- 출력: `params.txt`(bag 폴더 안) · 시험 [j451_paramsnap_test.txt](../debug_log/2026-09-18/outputs/j451_paramsnap_test.txt) — 여기서 `ObstaclesCritic.cost_scaling_factor 10.0 / inflation_radius 0.55` 를 직접 확인.
- ⚠ 이후: 09-21 cc1 에서 **주행 직전**에 돌린 이 스냅샷(+ topic list · echo = DDS 참여자 3 개 생성 · 소멸)이 루프 미달 18 · CPU 상승의 원인으로 판정 → bag 종료 뒤로 옮김. '주행 30 s 전 DDS 참여자 생성 금지' 규칙의 출처(09-21 §2).

### job453_runmeta.sh — 주행 메타
- 인자 `NAME [주행 인자 …]`, 환경 `TOPICS BAG_EXTRA STAGE NOTE GIT_HEAD`. `run_meta.txt` 에 이름 · 날짜 · 주행 인자 · 상자 힌트 · STAGE · NOTE · PC git HEAD · 기록 토픽 · nvpmodel · load · 패키지 버전(nav2-mppi · costmap-2d · slam-toolbox) · 배포 파일 sha256 앞 12 자(nav2_params · BT · URDF · stuck_monitor · camera.launch · fastdds xml · depth_relay · 러너 3 종) · 펌웨어 status 한 줄 · 라이브 토픽 목록, 이어 job451 → `params.txt`.
- 출력: [j453_metatest.txt](../debug_log/2026-09-18/outputs/j453_metatest.txt)(9.1 s, run_meta 25 줄 · params 598 줄 · 무응답 0). CLAUDE.md '주행 재현 규칙'(09-18) 의 구현.

### run_deploy_cc.sh — 배포
- PC 스크래치패드 `nav2_params_0918cc.yaml` 을 CR 제거 → `"CostCritic"` 문자열 확인(옛 파일 방지) → Jetson `/tmp` → `yaml.safe_load` 로 critics · CostCritic 사전 출력 → 설치본과 주석 제외 diff → 설치본 백업 → src · install 에 복사 → md5 셋 비교. 재기동은 하지 않음.
- 출력: [j454_deploy_cc.txt](../debug_log/2026-09-18/outputs/j454_deploy_cc.txt).
- 주의(메모리 'prep 이 설치본 링크 끊음'): 이 방식은 install 의 파일을 덮어 쓰므로 install 이 심볼릭 링크였다면 일반 파일이 된다 — 이 배포에서 링크 상태를 확인한 기록은 없음.

### job452_mppi_sim_cc.py — [시뮬 카드 §4.5](mppi-offline-simulator.md)

## 10. 용어
- **ObstaclesCritic**(Nav2 MPPI 1.1.20): 궤적 각 점의 코스트맵 비용에서 '장애물까지 거리' 를 역산해(역산식에 크리틱 자기 `cost_scaling_factor` · `inflation_radius` 사용 — Humble 만), 거리 < `collision_margin_distance` 면 강한 벌점, 아니면 (inflation_radius − 거리) 반발을 더한다. `consider_footprint: true` 에서 중심 비용이 외접 비용 이상이면 차체 둘레 최대 비용을 쓰는데, 둘레가 장애물 내접 반경 안이면 그 값은 늘 253 이라 거리가 0.175 로 고정된다 → 옆 여유 17.5 cm 안을 구분 못 함.
- **CostCritic**: 충돌은 같은 둘레 검사로 판정하되, 점수는 **중심 칸 비용**을 그대로 더한다(≥ 253 이면 `critical_cost` 300). 중심 비용은 inflation 감쇠를 그대로 담고 있어 거리 기울기가 있다. 가중은 내부에서 /254(비용 단위 정규화).
- **near_goal_distance**: 로버 ↔ 경로 끝이 이 거리 안이면 '멀리 있기 선호' 항을 끈다(목표가 장애물 옆일 수 있으므로). 이 코스에서는 0.5 m — 1.0 이면 상자 뒤 모서리에서 기울기가 꺼짐.
- **외접 비용(possibly inscribed cost)**: 차체 외접 반경(여기 0.313 m) 거리의 inflation 비용(≈178). 중심 비용이 이보다 낮으면 차체 어디도 내접 안에 있을 수 없으니 둘레 검사를 건너뛴다(계산 절약).
- **NavFn 비용 골짜기**: NavFn 은 칸 비용(50 + 0.8·c)의 적분을 최소화하므로, 양쪽 inflation 이 겹친 통로에서는 비용 최저선(대개 두 내접선의 가운데)을 탄다.
- **원경로 · 스무딩 · 실제**: NavFn `/plan` · BT SmoothPath(SimpleSmoother) 결과 · MPPI 가 실제로 지나간 궤적.
- **L(선행 시간)**: job446 에서 로버가 그 x 에 닿기 몇 초 전의 계획을 쓰는가(NavFn 은 매 계획을 로버 현재 자리에서 시작하므로 L = 0 은 무의미).
- MPPI · temperature · ESS · 크리틱 가중은 [흔들림 카드 §10](mppi-wobble-temperature.md).
