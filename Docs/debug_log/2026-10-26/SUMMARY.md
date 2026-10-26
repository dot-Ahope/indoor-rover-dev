# 2026-10-26 SUMMARY — 상자 옆 여유: 전역 비용장(D5) · Smac Lattice(D1) · 반전 부호 오차(D10 전제)

## §0 하루 시작 (사용자: "재부팅했다. 진행하라. 푸시도 하라.")
- push: personal `feature/nvblox-migration` · `feature/smac-hybrid` f106840c → a10a315a, 공개 dev 1cef72c → e1c1104(점검 0 · 0 · 0).
- Jetson 재부팅(가동 2 시간) → `/tmp` prep 3 개를 저장소 판으로 재전송(`jobs/up_prep_1026.sh` 머리 + 스크래치패드 base64 묶음): prep_fast 034f2179c7 · prep_patrol 9a8a8e3361 · chk_prep 6a3fa16e08 = 저장소와 같음. 스택 꺼짐(카메라 · nav2 · slam 0), micro-ROS 에이전트 컨테이너 살아 있음(`outputs/setup/up_prep_1026.txt`). 주행 전 prep 필요.
- 오늘 순서(10-23 §24 · SMAC_HYBRID_PLAN §9): ① D5 전역 비용장(오프라인) → ③ 반전 순간 휠 부호 오차(bag) → ② D1 Smac Lattice(오프라인) → ④ ①이 통과하면 b910 주행 2 회. ①~③ 로버 안 움직임.

## §1 D5 선언 — 전역 inflation 을 더 완만하게 하면 NavFn 경로가 상자 옆 틈 가운데로 가나 (결과 보기 전)
- 왜: 상자 북쪽 틈 0.70~0.90 m(가운데면 양옆 18~28 cm)인데 NavFn · Smac 모두 9~16 cm — 꺾임 안쪽으로 짧게 돎(10-23 §22.2). 비용이 거리에 따라 천천히 줄수록(cost_scaling_factor ↓) 상자 가까운 칸의 상대 비용이 커져 경로를 가운데로 밀 것(추정). 10-23 §1 은 반대 방향(2 → 5)만 시험.
- 방법: 오프라인 도구(`Docs/tools/plan_offline/`)에서 전역 inflation 만 바꿔 같은 장면 6 개(10-23 `outputs/plan_offline/scenes_1023.npz`)로 NavFn(GridBased) 경로. 변형 (반경 m, k) = (0.70, 2.0 · 기준 B0), (0.70, 1.0), (0.70, 0.5), (1.0, 1.0), (1.0, 0.5). 지도 재구성은 기록 치명 칸 + 그 inflation(기준 판은 기록과 일치 확인).
- 판정: ① 상자 장면 4 개에서 차체 ↔ 상자 여유가 기준보다 평균 ≥ +5 cm, 어느 장면도 기준보다 나빠지지 않음 ② 서쪽 통로 2 장면 계획 성공 · 치명까지 차체 거리 기준보다 나빠지지 않음 ③ 경로 길이 증가 ≤ 10 %. 통과한 변형 중 가장 완만하지 않은(변경이 작은) 것을 주행 후보로.
- 한계(미리 적음): 비용장을 바꾸면 MPPI 가 보는 로컬은 그대로(이번엔 전역만) — 컨트롤러 안쪽 깎기(+7~11 cm)는 남음. 전역 비용이 넓게 높아지면 좁은 통로에서 NavFn 이 먼 길로 돌 수 있음(③으로 봄).

### §1.1 D5 결과 — **반대로 나옴**: 비용을 완만하게 하면 경로가 상자에 더 붙음(판정 ① ✘) · 내 도구 실수 1 건
- 원문 `outputs/planner_offline/d5/run_*.txt` · `result_*.npz` · 지표 `anal_*.txt` · 표 `d5_table.txt`, 그림 `figures/planner_offline/d5_*/`. 기준 판(0.70/2.0) 재구성 일치 1.0000 · 경로 10-23 과 같음(재현 ✔).
- NavFn 차체 ↔ 상자 여유(cm): 기준 13.3 · 8.0 · 9.1 · 9.0 → k 1.0 · 0.5(반경 0.70 · 1.0 모두) **0.0 · 0.0 · 0.0 · 0.0**, 경로 길이 −6~−15 %(짧아짐). 서쪽 통로는 성공(치명까지 0.0~2.2 — 기준과 비슷). Smac 144 칸도 16.5 · 7.0 · 11.8 · 12.2 → 0.0~8.2.
- 왜(단면 `outputs/planner_offline/d5/` 의 x 1.2 비용, 상자 위 y 0.10 → 0.30): k 2.0 은 92 → 64(차 28), k 1.0 은 95 → 79(차 16), k 0.5 는 96 → 88(차 8) — 완만할수록 '상자 곁' 과 '틈 가운데' 의 비용 차가 줄어 경로 길이가 이김 → 안쪽으로 더 짧게. 처음 추론(완만 → 가까운 칸 상대 비용 ↑)은 틀림: 상대 차는 가파를수록 큼.
- **도구 실수**(같은 자리에서 고침): 하려 한 것 = inflation 5 변형 오프라인 → 본 것 = 5 판 모두 재구성 일치 1.0000 · NavFn '실패(상태 0)' 다수 · 'more than one action server' 경고 → 처음 추론 없음(숫자가 말이 안 됨) → 판별 = 실행 원문에 `$'\r': command not found` → 결론: 주말 사이 git(core.autocrlf=true) 체크아웃으로 `Docs/tools/plan_offline/*.sh` 가 CRLF → Jetson bash 가 깨져 정리 단계가 안 돌고 planner_server 가 매 판 쌓임(정리 전 20 개 프로세스) → 고침: `up_bundle.sh` 가 CR 을 빼고 담음, `run_planner_offline.sh` 가 시작 전 잔재 있으면 중단, `kill_planoff.sh` 추가. 무효 결과는 `outputs/planner_offline/d5/invalid_crlf/` 에 보존. 다음에 알아보는 법: 변형을 바꿨는데 검증 지표(재구성 일치)가 같으면 변형이 실제로 적용됐는지부터.

### §1.2 D5b 선언 — 전역 풋프린트 패딩을 키우면(계획기가 못 들어가는 띠를 넓힘) (결과 보기 전)
- 왜: 비용 기울기로는 길이를 못 이김(§1.1). 패딩은 내접 반경(= NavFn 이 장애물로 보는 띠, Smac 차체 다각형)을 직접 넓혀 '상자에서 최소 몇 cm' 를 보장. 대가: 좁은 통로 통과 불가 위험(서쪽 통로는 이미 경계).
- 변형: 전역 footprint_padding 0.01(기준) · 0.03 · 0.05, inflation 0.70/2.0 그대로, NavFn + Smac 144 칸.
- 판정: §1 과 같음(상자 4 장면 평균 ≥ +5 cm · 나빠지는 장면 0 · 서쪽 통로 성공 · 길이 +10 % 이하). 서쪽 통로 실패면 '패딩 상향 + 통로용 대체(패딩 원래 값으로 재계획)' 가 필요하다는 뜻으로 기록.

### §1.3 D5b 결과 — 패딩은 적용됐으나 경로가 안 바뀜(판정 ① ✘): 계획 경로는 이미 그 띠 밖
- 원문 `outputs/planner_offline/d5/run_pad0.03.txt` · `run_pad0.05.txt`, 지표 `anal_pad0.03.txt` · `anal_pad0.05.txt`, 그림 `figures/planner_offline/d5_pad*/`.
- 적용 확인: 내접(99) 칸 17 981(0.01) → 19 218(0.03) → 22 680(0.05), 상자 북쪽 단면도 99 띠가 1 칸 넓어짐.
- NavFn 차체 ↔ 상자: 13.3 · 8.0 · 9.1 · 9.0 → 0.05 에서 13.4 · 9.4 · 9.1 · 9.1 cm(+0~1.4). Smac 144 칸 16.5 · 7.0 · 11.8 · 12.2 → 16.8 · 8.5 · 12.8 · 15.2. 서쪽 통로 NavFn 성공, Smac 실패 그대로.
- 읽기: 패딩은 '최소 여유 바닥' 만 정함 — 계획 경로는 이미 상자에서 8~13 cm(차체)라 0.05 띠(5 cm) 밖. 경로를 가운데로 밀려면 패딩 ≥ 0.10~0.15 수준이 필요한데 그러면 서쪽 통로(이미 경계)가 막힘(추정, 시험 안 함).
- §1 · §1.1 · §1.3 종합: **전역 비용장 · 패딩으로는 계획 경로를 틈 가운데로 옮기기 어려움**(완만 = 더 붙음, 가파름 = 0~5 cm, 패딩 = 바닥만). 계획 여유 8~13 cm 를 실제 3~15 cm 로 줄인 것은 재계획 출발 자리 · 컨트롤러 안쪽 깎기(+6~11 cm, 10-23 §22.3). → 다음 손잡이는 컨트롤러 쪽이 더 큼(판단, 미검증). 주행 시험(오늘 ④)은 근거 없음 — 하지 않음.

## §2 반전 순간 휠 부호 오차 (10-23 §24 '먼저 잴 것', 로버 안 움직임)
- 도구 `jobs/anal_rev_sign.py`(바퀴별: 휠 = /wheel_odom v · ω 를 펌웨어 식 B 0.443 으로, 지령 = /cmd_vel, 기준 = /vslam/odom vx + /imu/data 각속도를 /tf_static 으로 base_link 에 돌린 z, 교차상관으로 지연 맞춤 vslam −20~+20 ms · 자이로 −40~−20 ms). 입력 `2026-10-23/bags/bag_f2pa1 … f2rp5.tgz`. 원문 `outputs/rev_sign/anal_rev_sign.txt`, 합계 `anal_rev_sign_summary.txt`.
- 결과(9 주행, 바퀴 반전 159 번): **부호 어긋남 거리 중앙 0.0 · 95 % 1.2 · 최대 3.1 mm**, 어긋남 시간 최대 0.11 s. 반전 창의 휠−기준 순 차 중앙 3.8 · 95 % 18.6 mm(반전 없는 창 2.5~3.8) — 이 차는 부호가 맞는 동안 생긴 것(회전 중 미끄러짐 · 축척 추정)이라 부호 오류 탓 아님.
- 결론: 지금 주행의 반전(지령 바퀴 속도 중앙 0.019 · 최대 0.091 m/s — 느린 반전)에선 FG 부호 오류는 mm 이하 → 펌웨어 '멈춘 뒤 방향 바꾸기' 는 지금 근거 없음. 단 D10(전진 · 후진 원호)은 더 빠른 반전이 잦을 것 → 그 시험에서 같은 도구로 다시 잼.
- **도구 실수 2 개**(같은 자리에서 고침, 무효 판 보존): v1 = /imu/data z 를 그대로 씀 → 카메라 IMU 좌표라 수직축 아님(지연이 탐색 끝 +480~500 ms 에 붙고 평소 창 차 13~20 mm) `outputs/rev_sign/anal_rev_sign_v1_imuaxis.txt`; v2 = /odometry/filtered 각속도 → EKF 가 휠 vyaw 도 융합(ekf.yaml odom0_config)해 휠과 독립 아님 `anal_rev_sign_v2_ekfyaw.txt`. 다음에 알아보는 법: 상관 지연이 탐색 범위 끝에 붙으면 축 · 부호 · 좌표부터 의심, 기준 신호가 비교 대상을 융합했는지 설정에서 확인.

## §3 D1 선언 — Smac Lattice(차동구동 원형) 오프라인 (결과 보기 전)
- 왜: 우리 차체(직사각 · 스키드스티어 = 제자리 회전 가능)에 맞는 Smac 은 Lattice(10-23 SMAC_HYBRID_PLAN §8 · §9 D1). Hybrid(DUBIN)는 서쪽 통로 실패 · 상자 여유 개선 없음(10-23 §22.2).
- 설정: 설치판 원형 `sample_primitives/5cm_resolution/0.5m_turning_radius/diff/output.json`, 그 밖은 Hybrid 와 같은 값 + rotation_penalty. 변형: cost_penalty {2.0, 5.0} × rotation_penalty {5, 20}, 후진 허용판 2(cp 2.0 · 5.0, 회전 5). 지도 = 실주행 inflation 0.70/2.0 · 패딩 0.01. NavFn 함께(대조).
- 판정(계획 §4 · D9 그대로): ① 상자 4 장면 차체 여유 NavFn 대비 평균 ≥ +5 cm · 나빠지는 장면 0 ② 서쪽 통로 2 장면 성공(고리 없음 = 0.3 m 창 최대 꺾임 ≤ 180°, 제자리 회전 구간은 따로 셈) ③ 계획 시간 ≤ 0.5 s. 기록: 경로 안의 제자리 회전 수 · 총 회전각(미끄러짐 대가).

### §3.1 D1 결과 — Lattice 도 기준 미달 · 변형끼리 경로가 같음(해석 확장 추정)
- 원문 `outputs/planner_offline/d1/run_d1.txt` · 결과 `result_d1.npz` · 지표 `anal_d1.txt`, 그림 `figures/planner_offline/d1/`. 재구성 일치 6 장면 1.0000.
- 6 변형(cp 2 · 5 × 회전 벌점 5 · 20, 후진 허용 2) 모두 **장면마다 같은 경로**. 차체 ↔ 상자: NavFn 13.3 · 8.0 · 9.1 · 9.0 → Lattice 14.0 · 10.6 · 8.9 · 8.1 cm(평균 +0.55, 기준 +5 ✘). 서쪽 통로 남행 **실패**(6 변형 모두, 4.6 s), 북행 성공 — 출발 −99° → 목표 82° 를 제자리 회전 198°(22 구간)로 돌고 감. 복귀 전체 경로도 제자리 회전 126°. 계획 0.002~0.032 s.
- 읽기: 회전 벌점 · cost_penalty 가 경로를 안 바꿈 → Hybrid 때처럼 해석 확장(최대 3 m)이 경로를 정하는 것으로 추정. 확인: 해석 확장 최대 길이 0.5 · 1.0 m 판을 한 번 돌림(Hybrid 는 예외가 났음).

### §3.2 Lattice + 해석 확장 제한(0.5 · 1.0 m) — 작동은 함(Hybrid 와 달리 예외 없음), 그래도 기준 미달
- 원문 `outputs/planner_offline/d1/run_d1a.txt` · 지표 `anal_d1a.txt` · 그림 `figures/planner_offline/d1a/`.
- 0.5 m: 차체 ↔ 상자 18.3 · 3.8 · 16.6 · 10.5 cm(NavFn 13.3 · 8.0 · 9.1 · 9.0 대비 +5.0 · **−4.2** · +7.5 · +1.5, 평균 +2.5) — 한 장면이 나빠져 ① ✘. 1.0 m: 14.0 · 8.2 · 10.2 · 14.1. 서쪽 통로 남행 여전히 실패, 북행 성공(제자리 회전 포함).
- cost_penalty 2 → 5, 회전 벌점 5 → 20 은 해석 확장을 줄여도 **경로 그대로** — 이 판(1.1.20)에서 이 두 손잡이가 우리 장면에 효과를 못 냄(기전 미확인).
- §1~§3 종합(오늘 오프라인 4 갈래): 전역 비용 완만화 ✘(더 붙음) · 패딩 ✘(바닥만) · Smac Hybrid ✘(10-23) · Smac Lattice ✘. **계획기 쪽 손잡이로는 상자 옆 여유를 안정적으로 +5 cm 못 얻음**, 서쪽 통로 남행은 차체 계획기 전부 실패(전역 지도상 경계 통로). → Phase P(계획기 교체)는 '근거 없음' 으로 멈추고 B0(NavFn) 유지 제안. 남은 큰 손잡이 = 컨트롤러 추종(굽은 곳 안쪽 +7~11 cm, 10-23 §22.3).

## §4 Smac Hybrid 계속 (사용자: "Smac Hybrid는 진행하고 싶다.") — 오프라인으로 막힌 자리부터
- 설치판 1.1.20 이 아는 파라미터(`outputs/setup/chk_smac_params.txt`): 해석 확장을 비용에 묶는 `analytic_expansion_max_cost`(새 Nav2 판에 있다고 알고 있음 — 일반 지식, 미확인) **없음**.
- §4.1 선언(결과 보기 전): REEDS_SHEPP(전진 · 후진, 사용자 D10 제안과 같은 동작) Hybrid 가 서쪽 통로(10-23 DUBIN 은 남행 실패 · 북행 목표 충돌)를 푸는가. 변형 R 0.10 · cp 3.0 · 72 칸, 같은 + 144 칸 · 해석 확장 0.5 m, R 0.15, 해석 확장 1.0 m. 판정: 서쪽 통로 2 장면 성공 · 상자 4 장면 NavFn 대비 나빠지지 않음 · 후진 구간 수 기록.

### §4.2 REEDS_SHEPP 결과 — 서쪽 통로는 여전히 실패, 상자는 'RS + 해석 확장 1.0 m' 가 지금까지 가장 나음(평균 +3.1, 나빠짐 0) · 도구 실수 1
- 원문 `outputs/planner_offline/hyb/run_rs.txt` · `anal_rs.txt` · `run_rs_pad0.txt` · `anal_rs_pad0.txt`, 그림 `figures/planner_offline/hyb_rs*/`.
- 차체 ↔ 상자(cm, NavFn 13.3 · 8.0 · 9.1 · 9.0): `Smac_R10_C30_A10_RS` **13.6 · 14.4 · 12.3 · 11.4**(+0.3 · +6.4 · +3.2 · +2.4, 평균 +3.1 — 기준 +5 미달이나 나빠진 장면 0, 후진 0~1 구간). 해석 확장 기본(3 m) RS 는 3.4 · 3.0 cm 로 나빠짐, 144 칸 + 0.5 m RS 는 후진 13 구간 · 11 m 길이의 엉뚱한 경로. 해석 확장 1.0 m 는 RS 에서 예외 없음.
- 서쪽 통로: RS 4 변형 모두 남 · 북 실패(북은 0.05 s — 목표 차체 충돌로 바로 거부). 패딩 0 으로도 실패, 그 판에선 상자 장면 rp2 가 2.1 cm 로 급락 — 작은 설정 차이에 경로가 크게 바뀜(장면 민감).
- **도구 실수**: 첫 RS 실행은 조회표 계산으로 planner_server 기동이 30 s 를 넘어 질의 쪽이 '계획 서버 없음' 으로 끝났는데, 결과 파일을 앞 실행(Lattice) 것으로 읽어 표가 잘못 나옴 → `query_planners.py` 대기 180 s, 무효 판 `outputs/planner_offline/hyb/invalid_wait30/`. 다음에 알아보는 법: 결과 표의 계획기 이름이 요청한 것과 같은지 먼저 봄.
- 읽기: Hybrid 를 쓰려면 ① 서쪽 통로 같은 경계 통로 · 목표 충돌 → **실패 시 NavFn 대체(D3) + 목표 자세 검사(D4)** 가 필수 ② 상자 여유 개선은 작고(+3 cm) 장면에 민감 — 1.1.20 엔 해석 확장을 비용에 묶는 설정이 없음(§4). 새 판 소스 빌드(D6)가 근본 손잡이일 수 있음(미확인).

## §5 Smac 포크 — Jazzy 의 해석 확장 비용 상한(analytic_expansion_max_cost)을 Humble 1.1.20 에 이식 (사용자: "2로 가자")
- 근거(소스 비교, PC 스크래치패드 sparse clone: navigation2 1.1.20 a097086 · jazzy 426682f): Jazzy `analytic_expansion.cpp` getAnalyticPath 는 곡선 위 칸 비용을 모아 **max_cost(기본 200) 를 넘는 칸에 들어갔다 다시 나오면 곡선을 버림**(목표가 높은 비용 안이라 끝에서만 들어가는 것은 허용, override 면 목표 가까이 허용). 1.1.20 엔 이 검사 · 파라미터가 없음 → 해석 확장이 비용을 무시하고 경로를 정해 cost_penalty 가 효과 없던 것(§3.1 · §4 추정)과 맞음. Jazzy 는 `d < √2`(한 칸 안) 도 건너뜀.
- 패치 `Docs/06_planner/smac_fork/nav2_smac_planner_rover_maxcost.patch`(4 파일 +59/−4): types.hpp SearchInfo 2 필드 · hybrid/lattice 파라미터 선언(Jazzy 와 같은 이름 · 기본값) · analytic_expansion.cpp 검사 이식. Jazzy 와 다른 점 1: override 거리 판정에 `goal->motion_table.min_turning_radius`(1.1.20 Lattice 표에 없음) 대신 `_search_info.minimum_turning_radius`(칸 단위).
- 빌드: Jetson `~/smac_ws`(1.1.20 태그 + 패치, Release, 2 분 44 초), .so 에 파라미터 이름 있음(`jobs/up_smac_fork_1026.sh` → `outputs/setup/up_smac_fork_1026.txt`). 주행 스택은 /opt/ros 판 그대로(오버레이는 오프라인 · planner:=smac 때만).
- §5.1 선언(결과 보기 전): 같은 6 장면, 오버레이로. 변형 Hybrid RS(해석 확장 1.0 m · 기본 3 m) × max_cost {200, 100, 60}, cost_penalty 1.2 판, DUBIN 판, Lattice 판. 판정: §1 과 같음(상자 4 장면 NavFn 대비 평균 ≥ +5 cm · 나빠짐 0, 서쪽 통로 결과 기록, 계획 ≤ 0.5 s) + **cost_penalty · max_cost 를 바꾸면 경로가 바뀌는가**(이식이 작동하는지).

### §5.1 · §5.2 포크 결과 — 이식은 실제로 실리고 결과도 재현되나, 상자 여유는 나아지지 않음
- 원문 `outputs/planner_offline/fork/run_fork.txt` · `anal_fork.txt`(7 변형), 확인 판 `run_chk_{stock1,stock2,fork1,fork2}.txt` · `anal_chk_*.txt`, 그림 `figures/planner_offline/fork*/`.
- 적재 확인(§5.2, 질의 뒤 측정): 포크 판 planner_server 의 /proc/maps = `~/smac_ws/.../libnav2_smac_planner.so`, `analytic_expansion_max_cost` = 200.0 / 설치판은 /opt/ros .so · 'Parameter not set'. 같은 판 두 번 실행 결과 장면마다 **완전히 같음**(결정적). (§5.1 의 '포크 파라미터 선언 수 0' 은 기동 전 조회라 의미 없었음 — 도구 쪽에서 질의 뒤로 옮김.)
- 포크 vs 설치판(같은 설정): `RS + 해석 1.0 m` 은 rp2 만 14.4 → **4.3 cm**(나빠짐), 나머지 같음. `RS + 해석 3 m + max_cost 60` 은 설치판과 **모든 장면 같음**(13.5 · 6.8 · 3.4 · 3.0) — 비용 상한이 이 장면들에선 경로를 거의 안 바꿈. 7 변형 판: max_cost 60 · 100 · 200, cost_penalty 1.2 · 3.0 사이도 대부분 같은 경로. Lattice + max_cost 100: 16.5 · 7.5 · **0.1** · 11.2. 서쪽 통로는 Lattice 북행만 성공, 나머지 실패 그대로.
- 판정 ✘(평균 +5 · 나빠짐 0 둘 다 미달). 이식 자체는 작동(rp2 경로가 바뀜)하나, **cost_penalty 가 경로를 거의 못 바꾸는 원인은 해석 확장만이 아님**(미확인 — 탐색 비용식 · 휴리스틱 쪽 의심, 계측 필요).

## §6 cost_penalty 가 왜 경로를 못 바꾸나 — 원인 찾기 (사용자: "1번으로 진행하라")
- 소스(1.1.20 `node_hybrid.cpp:304`): 탐색 비용 = 이동 거리 × (0.985 + cost_penalty × 칸 비용/252) — 상자 곁(≈ 200)에서 cp 3 이면 ×3.4, cp 1.2 면 ×1.9 → 탐색 자체는 비용을 봐야 함. 휴리스틱(`getObstacleHeuristic`, 521 행)도 같은 꼴.
- §6.1 가설 1(결과 보기 전): **후처리 smoother**(`smooth_path: true` — 비용을 안 보고 매끄럽게 · 짧게 당김, 추정)가 탐색 경로 차이를 지움. 시험: 같은 변형을 smooth_path false 로(`_NS`), cp 1.2 · 3.0 · 6.0. 판별: smoother 끄면 cp 마다 경로가 달라지고(상자 여유가 cp 따라 증가) smoother 켜면 같아지면 가설 맞음.

### §6.1 가설 1(smoother) 기각 + **내 도구 결함 발견 — 한 서버에 Smac 변형 여럿을 올린 비교는 무효**
- smoother 끔(`outputs/planner_offline/cause/run_ns.txt` · `anal_ns.txt`): cp 1.2 · 3.0 · 6.0 이 끈 판에서도 장면마다 같은 경로 → smoother 탓 아님.
- 단서: 같은 설정(`Smac_R10_C30_A10_RS`, 설치판)이 f2rp2 에서 앞 판 14.4 cm(§4.2) · 이번 판 8.6 cm — 차이는 '같이 올린 다른 변형' 뿐.
- **내 실수 · 정정**

| 칸 | 내용 |
|---|---|
| 하려 한 것 | 오프라인 도구(`Docs/tools/plan_offline/`)로 Smac 변형 여럿을 한 planner_server 에 플러그인으로 올려 한 번에 비교(10-23 §22.2 · 10-26 §3 · §3.2 · §4.2 · §5.1 · §6.1) |
| 본 것 | cp · max_cost · 회전 벌점 · 운동 모델을 바꿔도 경로가 같고, 같은 설정이 함께 올린 변형에 따라 결과가 달라짐 |
| 처음 추론 | 해석 확장이 비용을 무시(§3.1 · §4), 다음엔 smoother(§6.1) — 둘 다 1.1.20 의 동작 문제로 봄 |
| 의심한 이유 | 같은 설정 · 같은 장면에서 결과가 달라짐(결정적 재실행에선 같았으므로 무작위 아님) |
| 판별 | 소스: `node_hybrid.hpp:446` `static HybridMotionTable motion_table`(cost_penalty · 회전반경 · 운동 모델), 휴리스틱 표 · sampled_costmap 도 static(445~455 행), Lattice 도 `node_lattice.hpp:417` static. 초기화는 `a_star.cpp:115` — 지도 크기가 바뀔 때만 → 한 프로세스의 Smac 인스턴스들이 한 설정을 공유 |
| 결론 | 여러 Smac 변형을 한 서버에서 비교한 결과는 **무효**(변형 차이가 실제로 적용 안 됨). 유효: NavFn 전부, Smac 변형 하나만 올린 판(10-26 §1 D5 의 144 칸, §1.3, §5.2 확인 판의 '설치판 vs 포크' 는 같은 두 변형 구성이라 두 판끼리 비교는 유효하나 변형 간 차이는 무효). 'cp 가 효과 없음 · 해석 확장 탓' 이라는 §3.1 · §4 · §5 의 읽기는 근거 없음으로 되돌림 |
| 다음에 알아보는 법 | 같은 프로세스에 같은 플러그인을 여럿 올리는 비교는 static 상태 공유부터 의심. 변형마다 프로세스를 따로(도구 `run_variants.sh`). 실주행(Smac 하나)은 해당 없음 |

### §6.2 다시 재기 선언 — 변형마다 프로세스 따로(설치판), 결과 보기 전
- 변형: Hybrid DUBIN R 0.10 × cp {1.2, 3.0, 6.0}(해석 확장 기본 3 m), R 0.15 cp 3.0, REEDS_SHEPP cp 3.0(3 m · 1.0 m), Lattice cp {2.0, 5.0} 회전 5. 판정은 §1 · §3 과 같음(상자 4 장면 NavFn 대비 평균 ≥ +5 cm · 나빠짐 0, 서쪽 통로 성공, ≤ 0.5 s) + cp 를 올리면 상자 여유가 느는가.

### §6.3 다시 잰 결과(변형마다 프로세스 따로) — cp 는 경로를 바꾸지만 상자 여유를 꾸준히 올리진 않음 · 가장 나은 것은 설치판 REEDS_SHEPP + 해석 1.0 m
- 원문 `outputs/planner_offline/sep/` · `outputs/planner_offline/sep_fork/`(각 `run_<변형>.txt` · `anal_<변형>.txt` · 합친 `anal_all.txt`), 도구 `Docs/tools/plan_offline/run_variants.sh`. 재구성 일치 모든 판 6/6, 적재 .so 확인(설치판 /opt/ros · 포크 smac_ws).
- 차체 ↔ 상자(cm; 장면 rp1 · rp2 · rp5 재계획 · rp5 전체), NavFn 13.3 · 8.0 · 9.1 · 9.0:

| 변형(설치판) | rp1 | rp2 | rp5 | rp5 전체 | 평균 차 | 나빠진 장면 |
|---|---|---|---|---|---|---|
| DUBIN R0.10 cp 1.2 | 9.0 | 5.4 | 10.8 | 6.4 | −1.95 | 3 |
| DUBIN R0.10 cp 3.0 | 13.5 | 6.3 | 9.4 | 1.3 | −2.2 | 2 |
| DUBIN R0.10 cp 6.0 | 7.3 | 7.5 | 3.6 | 4.4 | −4.15 | 4 |
| DUBIN R0.15 cp 3.0 | 9.8 | 4.0 | 9.6 | 6.4 | −2.4 | 3 |
| RS cp 3.0(해석 3 m) | 13.5 | 6.8 | 3.4 | 3.0 | −3.2 | 3 |
| **RS cp 3.0 해석 1.0 m** | **13.6** | **14.4** | **12.3** | **11.4** | **+3.1** | **0** |
| Lattice cp 2 회전 5 | 14.0 | 8.2 | 16.0 | 8.1 | +1.7 | 1 |
| Lattice cp 5 회전 5 | 15.5 | 6.3 | 9.2 | 11.2 | +0.7 | 2 |

- 포크(변형 단독): RS 해석 1.0 m 는 rp2 만 14.4 → 4.3(나빠짐), max_cost 100 판들은 설치판 같은 설정과 같은 결과 → **포크는 이 장면들에 이득 없음**.
- 서쪽 통로: 모든 Hybrid 남 · 북 실패, Lattice 는 북만 성공.
- 비용 골(`run_variants` 결과의 재구성 지도, 상자 북쪽 x 1.15~1.30 단면 최소 비용 위치): 그 선을 따르면 차체 ↔ 상자 약 **18 cm**(rp5 x 1.30 은 13). 계획기들은 8~14 cm — 비용 골까지 4~10 cm 남음.
- 판정 ✘(+5 · 나빠짐 0 동시 만족 없음). 가장 가까운 후보 = 설치판 `Smac_R10_C30_A10_RS`(나빠짐 0, 평균 +3.1). cp 를 올려도 여유가 늘지 않는 이유는 미확인(탐색 각도 칸 · 원형 길이 대 0.85 m 틈 폭 추정).

## §7 Smac Hybrid 주행 준비 (사용자: "A진행") — 브랜치 `feature/smac-hybrid`
- 구현(로버 안 움직임):
  - `navigation.launch.py` 인자 `planner:=navfn|smac`(기본 navfn = B0 그대로). smac 이면 BT 사본(/tmp/nav_to_pose_active.xml)의 PlanAndSmooth 를 `Fallback(PlanSmacOrNavFn)` = [SmacHybrid → CopyPath step 0.03] 실패 시 [기존 NavFn → SimpleSmoother/CopyPath] 로 바꿈. 미리보기 `outputs/setup/bt_smac_preview.xml`(XML 검사 통과).
  - `CopyPath` 에 `step` 포트: 호 길이 간격으로 다시 찍음(끝 점은 그대로) — Smac 점 간격 ≈ 0.07 m 를 NavFn 판 0.026~0.047 에 맞춰 MPPI 경로 크리틱 offset(점 개수) 의미 유지.
  - `nav2_params.yaml` SmacHybrid: REEDS_SHEPP · cp 3.0 · 해석 확장 1.0 m · 캐시 끔 · max_planning_time 2.0(대체로 넘어가는 시간 상한). R 0.10 · 72 칸 그대로. = 오프라인 최선 판(§6.3) + 시간 상한.
  - `Docs/tools/prep_patrol.sh` `NAV_ADD` 환경. prep `jobs/prep_smac_1026.sh`(BT 사본 · Smac 매개변수 확인 포함).
  - 배포 `jobs/up_smac_nav_1026.sh` → `outputs/setup/up_smac_nav_1026.txt`(첫 판 launch 문법 오류 — 파이썬 heredoc 의 '\n' 이 실제 줄바꿈으로 깨짐, 메모리에 적어 둔 함정 그대로. 스택이 꺼진 동안이라 쓰인 적 없음, Edit 로 고쳐 재배포 `up_smac_nav_1026_b.txt`, CopyPath .so 재빌드 확인 `chk_copypath_so.txt`). 설치본 링크 유지.
- §7.1 주행 선언(결과 보기 전): f2sh1 · f2sh2 = b910, f2sh3 = no5. 판정: ① 전부 도착 · ABORT 0 · 접촉 0 · nav_guard 취소 0 ② **상자 옆 실제 최소 여유 ≥ 8 cm(b910 두 번 모두)** — B0 15.4 · 5.5 · 3.1 ③ Smac 이 실제로 쓰였나(nav2 로그의 계획 · 대체 횟수, BT 경로 중 Smac 비율) · 경로 후진 구간 · 실제 후진(cmd_vel < 0) 기록 ④ no5 서쪽 통로 통과(대체 작동) · 복구 Wait ≤ 1 ⑤ 짧은 멈칫 · CPU ≤ B0(f2rp4 · f2rp5) + 20 %. 실패 시 planner:=navfn 으로 되돌림(같은 코드).

### §7.2 prep 첫 시도 실패 — 아침에 보낸 prep 스크립트가 CRLF 였음(내 실수)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | f2sh1 prep(`jobs/prep_smac_1026.sh`) |
| 본 것 | prep_patrol 첫 줄 뒤 아무 노드도 안 뜸(`outputs/setup/prep_smac_1026_1.txt`), 전체 출력 `/tmp/prep_fast.sh: line 7: set: +: invalid option · line 68: syntax error`(`prep_smac_1026_2.txt`) |
| 판별 | §0 의 재전송 묶음(`jobs/up_prep_1026.sh`)이 작업 사본(주말 체크아웃 뒤 CRLF)을 그대로 base64 로 보냄. §0 의 '저장소와 같음' 해시도 CRLF 사본끼리 비교 — 저장소(git blob, LF) 해시는 prep_fast c636f4060d · chk_prep d06751ab73 로 다름 |
| 결론 | CR 을 빼고 재전송(`up_prep_1026b.txt`: 세 파일 CR 0, 해시 = git HEAD blob). prep 재시도 PREP_OK(`prep_smac_1026_3.txt`: 0.003 m · 12.22 V, BT 사본 PlanSmacOrNavFn 1 · step 1, SmacHybrid REEDS_SHEPP · cp 3.0 · 해석 1.0 · 2.0 s) |
| 다음에 알아보는 법 | Jetson 으로 보내는 텍스트는 항상 `tr -d '\r'`, 해시 비교는 `git show HEAD:<경로>` 기준 |

### §7.3 f2sh1(b910, planner:=smac) 결과 — 3/3 · **상자 옆 실제 최소 여유 18.4 cm**(B0 15.4 · 5.5 · 3.1)
- 러너 `outputs/drives/f2sh1/run_f2sh1.txt`: 3/3 · 51.4 · 47.9 · 104.6 s(총 205.8 s; f2rp5 202.8). bag `bags/bag_f2sh1.tgz`, 로그 `bags/logs_f2sh1/` → `outputs/drives/f2sh1/nav2_f2sh1.log` · `nav_events_ms_f2sh1.txt`.
- Smac 사용: nav2 로그에 SimpleSmoother 호출('Received a path to smooth') **0** = BT 경로 전부 Smac(NavFn 대체 0). 막힘 중단 1(상자 (1.36, −0.11), 경로 받고 새로 99) → Smac 재계획.
- 상자 옆(`outputs/drives/f2sh1/anal_contact_f2sh1_d30.txt` · `anal_plan_series_f2sh1.txt` · `anal_track_dev_f2sh1.txt` · `anal_band_run_f2sh1.txt`, 상자 = 기록 위치):
  - 막힘 뒤 다시 그린 Smac 경로 상자 여유 **18.5 cm**(NavFn 판 8.9~13.3). 갈 때 경로 13.5 · 17.7.
  - 실제 최소 여유: 갈 때 **18.9 cm**(12:47:33.6), 복귀 **18.4 cm**(12:50:26.4, 로버 (1.06, 0.32, −172°)). 상자 옆 구간 경로 이탈 −1.3~+1.1 cm(경로 위). 굽은 곳 진입(t 181~186)은 경로보다 상자 쪽 +8~11 cm 로 여전히 안쪽 깎기 — 그러나 경로가 상자에서 멀어 여유가 남음. 로컬 코스트맵 정확 여유 최소 8.1 cm(벽 쪽 포함 전체, < 6 cm 0 프레임).
  - 후진 지령(< −0.01 m/s) 38 개 · 1.9 s · 최소 −0.05.
- 판정(§7.1): ① ✔ ② ✔(18.4 ≥ 8, 1 회째) ③ 기록 ✔ ⑤ 아래 수치 비교는 3 회 뒤. 재현 확인 = f2sh2.

### §7.4 f2sh2(b910 반복) 결과 — 3/3 · 상자 옆 실제 최소 여유 **10.8 cm**(판정 ② 2 회 모두 ≥ 8 ✔) · 굽은 곳 안쪽 깎기가 남은 손실
- 러너 `outputs/drives/f2sh2/run_f2sh2.txt`: 3/3 · 52.0 · 48.4 · 101.1 s(총 201.7 s). prep `outputs/setup/prep_smac_1026_4.txt`(0.006 m · 12.19 V). bag `bags/bag_f2sh2.tgz`, 로그 → `outputs/drives/f2sh2/nav2_f2sh2.log` · `nav_events_ms_f2sh2.txt`.
- Smac: SimpleSmoother 호출 0(NavFn 대체 0). 막힘 중단 0. 복귀 재계획 1 회 = 13:18:09 TF 외삽으로 컨트롤러 중단 → 로버 (2.39, −1.23) 에서 Smac 재계획, 그 경로 상자 여유 **17.1 cm**(`outputs/drives/f2sh2/anal_plan_series_f2sh2.txt`).
- 실제 여유(`outputs/drives/f2sh2/anal_contact_f2sh2_d30.txt` · `anal_track_dev_f2sh2.txt`): 갈 때 19.0 cm, 복귀 **10.8 cm**(13:18:32.9, 로버 (1.63, 0.09, 152°) = 상자 동쪽 끝에 비스듬히 다가가는 굽은 곳). 그때 로버는 경로보다 상자 쪽 **+13~15.6 cm**(t 183~188) — MPPI 굽은 곳 안쪽 깎기(10-23 §22.3). 상자 옆 직선(t 194~197)은 +0.7~2.6 cm 로 경로 위. 로컬 코스트맵 정확 여유 최소 14.2 cm(< 6 cm 0 프레임).
- b910 두 번 종합(Smac): 18.4 · 10.8 cm(B0 NavFn 15.4 · 5.5 · 3.1). 계획 경로 여유 17.1~18.5 cm(NavFn 8.9~13.3). 남은 손실은 컨트롤러 굽은 곳 깎기(f2sh2 에서 −6 cm).

## §8 시각화 (사용자: "서쪽 통로는 지금 사람들이 있어서 나중으로 미루자. 우선 이전 2번의 주행 시각화해달라.") — f2sh3(no5) 미룸
- 비교 그림 `figures/compare/box_compare_b0_smac.png`(도구 `jobs/fig_box_compare.py` → `outputs/compare/fig_box_compare.txt`; 입력 10-23 `bag_f2rp1 · f2rp2 · f2rp5`, 10-26 `bag_f2sh1 · f2sh2`): 왼쪽 B0(NavFn) · 오른쪽 Smac, 실선 = 지나간 길, 점선 = 가장 가까운 순간에 따르던 BT 경로, 칠한 차체 = 최소 여유 순간. 최소 여유 B0 15.2 · 5.5 · 3.1 / Smac 18.4 · 10.8 cm.
  - 읽기: B0 경로(점선)는 상자 북쪽 y ≈ 0.25~0.30 로 지나고 로버(실선)는 그보다 상자 쪽(y 0.15~0.23)으로 달림. Smac 경로는 y ≈ 0.31~0.36 로 더 북쪽 · 더 큰 호. f2sh2 의 10.8 cm 는 상자 옆이 아니라 상자 동쪽으로 꺾어 들어오는 대각선(x ≈ 1.6)에서 경로 안쪽으로 깎은 자리.
  - 도구 첫 판 실수: 점선을 '복귀 구간 시작 직전 경로' 로 그려 B0 는 막힘 전 상자 관통 경로가 나옴 → '최소 여유 순간에 쓰이던 경로' 로 고침.
- 영상 `videos/f2sh1_return_box.mp4`(12:49:45~12:50:42) · `videos/f2sh2_return_box.mp4`(13:18:00~13:18:55), 1.5 배속(git 제외, `outputs/fig_video/fig_drive_video_f2sh*.txt`). 장면 `figures/compare/f2sh2_return_box_frame.png`(13:18:32.8 최소 여유 순간). 영상 도구 `Docs/tools/fig_drive_video.py` 수정: Smac 주행은 스무더 사건이 없어 BT 경로를 못 골랐음 → /plan 중 점 간격 > 0.04 m 를 Smac BT 경로로(각 4 개).

## §9 f2sh2 굽은 곳 이탈은 컨트롤러 탓인가 (사용자: "전역 경로가 상자를 인식하고 수정되었을 때, 로버가 그 수정된 경로보다 상자쪽으로 꺾어 움직이려고 한 움직임이 컨트롤러 부분 문제라는 것인가?")
- 전제 정정: f2sh2 의 복귀 재계획은 상자 막힘이 아니라 **13:18:09 TF 외삽으로 컨트롤러 중단 → 재계획**(그때 상자는 이미 지도에 있어 새 Smac 경로가 처음부터 17.1 cm). 막힘 판정으로 경로가 바뀐 것은 f2sh1.
- 판별(`jobs/chk_dev_frame_f2sh2.py` → `outputs/drives/f2sh2/chk_dev_frame_f2sh2.txt`, 입력 `bags/bag_f2sh2.tgz` /tf · /transformed_global_plan): 컨트롤러 자기 좌표(odom)에서 로버 ↔ 받은 경로 옆 거리 13:18:25 +9.3 → 13:18:30.5 **+15.7 cm**(상자 쪽) → 13:18:37.5 +5.2. 같은 창 map→odom 변화 2~5 cm.
- 결론: 상자 쪽으로 꺾어 든 것은 **MPPI 가 받은 경로 안쪽을 깎은 것**(위치 보정 탓 아님, 그 몫은 ≤ 5 cm). 10-23 §22.3 의 굽은 곳 안쪽 69~91 % 와 같은 성질 — Smac 은 경로를 멀리 둬서 여유를 남겼을 뿐 깎는 양은 비슷. 기전(지평 3.2 s 의 먼 경로점 당김 > PathAlign · PathFollow)은 추정, MPPI 오프라인 모의로 확인할 과제.

## §10 MPPI 굽은 곳 안쪽 깎기 — 오프라인 시뮬 (사용자: "MPPI 굽은 곳 깎기 오프라인 분석 진행하라")
- 도구 `Docs/tools/anal_mppi_sim.py`(1.1.20 MPPI 흉내, bag 경로 · 로컬 코스트맵 재생, 10-01 job776 계열) + 오늘 추가: `resample`(BT CopyPath 0.03 과 같게 — 경로 크리틱 offset 이 점 개수라 필수) · 매 주기 '굽은 곳 안쪽 +' 경로 이탈 · 1 s 넘는 정지 시간.
- 설정 대조(yaml): PathFollow 가중 10 · offset 20 점(0.03 m 간격이면 ≈ 0.6 m 앞 점으로 궤적 끝을 당김 — 굽은 곳에선 그 점으로 가는 지름길이 안쪽), PathAlign 14 · offset 3, PathAngle 2, Goal 10, PreferForward 15, temperature 0.15, 지평 32 × 0.1 s.
- §10.1 선언(결과 보기 전): 장면 f2sh2 복귀 13:18:22 부터 16 s(실제 이탈 최대 +15.7 cm). ① 재현 판정: base(실주행 값)의 안쪽 최대가 실제의 ±5 cm 안(10.7~20.7)이면 시뮬을 비교에 씀, 아니면 시뮬 한계로 기록 ② 변형(PathFollow offset 10 · 5, 가중 5 · 0, PathAlign 28, 28 + offset 10, PathAngle 0)에서 안쪽 최대가 base 대비 ≥ 5 cm 줄고 1 s 넘는 정지 · 후보 전부 충돌이 늘지 않는 것을 후보로. 실행 `jobs/run_sim_corner_1026.sh`.

### §10.1 · §10.2 첫 시뮬은 재현 실패 → 원인은 시뮬 구동계 · 실제는 **바깥 바퀴 포화**
- 첫 판(`outputs/mppi_sim/sim_corner_1026.txt`): 9 변형 모두 시작 이탈 9.6 cm 에서 줄어듦(중앙 0.7~2.5 cm) — 실제는 9.3 → 15.7 로 커짐 → 재현 ✘(판정 ①). 변형 차이 작음.
- 실제 명령 대 움직임(`jobs/chk_cmd_vs_motion_f2sh2.py` → `outputs/drives/f2sh2/chk_cmd_vs_motion_f2sh2.txt`, 입력 bag_f2sh2 /cmd_vel · /wheel_odom · /odometry/filtered · /vslam/odom · /imu/data(tf_static 으로 base_link)): 굽은 곳 13:18:24~28 명령 v 0.080 · ω +0.17~0.20, 실제(휠 · 자이로 · cuVSLAM 일치) v 0.055~0.061 · ω +0.10~0.13(비 0.45~0.68). 바깥 바퀴 = 0.058 + 0.125 × 0.2215 ≈ **0.086 m/s = 펌웨어 바퀴 한계 0.085**.
- 펌웨어(`firmware/rover_jupiter_fw/App/microros/microros_task.c` cmdvel_callback): 한쪽 바퀴가 0.085 를 넘으면 두 바퀴를 같은 비율로 줄임(곡률 유지, 속도만 줄어듦). 계산 (0.08, 0.19) → 바깥 0.122 → ×0.70 → (0.056, 0.132) = 실측과 맞음.
- 시뮬 구동계 정정: 예전 `w_gain 0.7`(회전만 70 %)은 곡률을 바꿔(덜 돌아 바깥으로) 깎기를 가렸음 → `wheel_max=0.085`(펌웨어와 같은 비례 축소) 추가. 재현 판(`outputs/mppi_sim/sim_corner_1026b.txt`): 씨앗 1 · 2 · 3 안쪽 최대 9.7 · 9.6 · **20.2**, 중앙 4.9 · 1.9 · 17.5 cm — 실제 15.7 이 이 범위 안. ESS 10~20(표본 1000 중 실효 10~20)이라 결과가 씨앗에 크게 흔들림 → 변형 비교는 씨앗 6 개씩.
- §10.3 선언(결과 보기 전): 바퀴 포화 구동계, 씨앗 1~6. 변형 base · PathFollow offset 10 · 5 · PathFollow 가중 5 · PathAlign 28 · vx_max 0.06(포화 줄임) · temperature 0.3. 판정: 안쪽 최대의 씨앗 평균이 base 보다 ≥ 5 cm 작고, 최악 씨앗도 base 최악보다 작고, 1 s 넘는 정지 · 후보 전부 충돌이 늘지 않을 것.

### §10.3 결과 — 기준 미달: 어느 변형도 안쪽 깎기를 크게 줄이지 못함 · 시뮬은 '씨앗 잡음' 이 변형 효과보다 큼
- 원문 `outputs/mppi_sim/sim_corner_1026c.txt`(42 판), 요약 `outputs/mppi_sim/sim_corner_1026c_summary.txt`, 도구 `jobs/run_sim_corner_1026c.sh`.

| 변형(씨앗 6) | 안쪽 최대 평균 | 최악 | 안쪽 중앙 평균 | 정지 · 실패 | 평균 속도 |
|---|---|---|---|---|---|
| base(실주행) | 11.4 | 20.2 | 6.1 | 0 · 0 | 0.080 |
| PathFollow offset 10 | 11.1 | 18.8 | 4.8 | 0 · 0 | 0.080 |
| PathFollow offset 5 | 10.9 | 17.6 | 4.6 | 0 · 0 | 0.080 |
| PathFollow 가중 5 | 10.7 | 16.3 | 4.9 | 0 · 0 | 0.079 |
| PathAlign 28 | 10.6 | 16.0 | 3.9 | 0 · 0 | 0.080 |
| vx_max 0.06 | 11.7 | 21.8 | 5.9 | 0 · 0 | 0.060 |
| temperature 0.3 | 10.7 | 16.3 | 5.5 | 0 · 0 | 0.080 |

- 판정(§10.3) ✘: 평균 감소 최대 0.8 cm(기준 5). 최악은 PathAlign 28 · PathFollow 가중 5 · temperature 0.3 이 4 cm 남짓 줄였으나 씨앗 6 개로는 잡음 범위(같은 base 가 씨앗에 따라 9.6~20.2).
- 읽기: ① '안쪽 최대' 는 시작 이탈 9.6 cm 가 바닥이라 대부분 씨앗에서 그보다 안 커짐 — 실제(15.7)는 나쁜 꼬리 쪽. ② **속도를 낮춰 포화를 줄여도(vx_max 0.06) 깎기가 안 줄어듦** → 포화는 '속도가 계획보다 느려지는' 원인이지 깎기의 주원인은 아님(시뮬 기준, 추정). ③ ESS 10~20 — MPPI 해가 매 주기 표본 잡음에 크게 흔들림이 공통 배경일 수 있음(미확인).
- 시뮬 한계(미리 적음): 장면 시작이 이미 9.3 cm 벗어난 뒤(13:18:22) — 깎기는 재계획 직후(13:18:10~22)부터 시작됐을 수 있음. 다음엔 시작을 13:18:10 으로, 지표를 '시작보다 더 벗어난 양' 으로.

### §10.4 선언(사용자: "A진행해봐라.") — 시작을 재계획 직후로, 해 잡음 줄이는 설정 포함, 씨앗 10 (결과 보기 전)
- 장면: f2sh2 13:18:10.0(Smac 재계획 13:18:09.9 직후 — 경로가 로버 자리에서 시작하므로 이탈 ≈ 0 에서 출발)부터 26 s(260 주기, 상자 옆 지나감까지). 바퀴 포화 구동계(wheel_max 0.085) · 재표본 0.03.
- 변형: base · PathAlign 28 · PathFollow 가중 5 · PathAlign 28 + PathFollow 5 · batch 2000 · wz_std 0.3 · iteration 3. 씨앗 1~10.
- 지표: 굽은 곳 안쪽 이탈 최대 · 95 % · 중앙(시작 ≈ 0 이라 최대 = 더 벗어난 양), 1 s 넘는 정지, 후보 전부 충돌, 평균 속도. 시뮬 base 의 최대 분포가 실제 15.7 cm 를 품는지(재현) 먼저 봄.
- 판정: 안쪽 최대 씨앗 평균이 base 보다 ≥ 5 cm 작고 · 최악도 작고 · 정지 · 실패 늘지 않음. 차이가 씨앗 표준편차보다 작으면 '구분 불가' 로 기록.

### §10.5 결과 — 판정 ✘(평균 감소 ≥ 5 cm 없음) · PathAlign 28 + PathFollow 5 가 꼬리를 줄이는 경향(구분 불가 수준)
- 원문 `outputs/mppi_sim/sim_corner_1026d.txt`(70 판, 4 병렬), 요약 `outputs/mppi_sim/sim_corner_1026d_summary.txt`(도구 `jobs/anal_sim_corner_summary.py` — 첫 요약은 병렬 출력이 한 줄에 섞인 판 1 개를 놓쳐 base n 9 였음, 경계로 나눠 고침).

| 변형(씨앗 10) | 안쪽 최대 평균 ± 표준편차 | 최악 | 95 % 평균 | 중앙 평균 | base 대비 차 / 표준오차 |
|---|---|---|---|---|---|
| base | 7.9 ± 5.2 | 19.8 | 6.9 | 3.7 | — |
| PathAlign 28 | 6.1 ± 3.9 | 15.7 | 5.0 | 2.3 | −1.8 / 2.1 |
| PathFollow 가중 5 | 7.9 ± 4.3 | 16.2 | 7.1 | 3.8 | 0.0 / 2.1 |
| **PathAlign 28 + PathFollow 5** | **5.5 ± 2.1** | **11.2** | 4.6 | 1.9 | −2.4 / 1.8 |
| batch 2000 | 9.4 ± 2.2 | 12.4 | 8.9 | 5.6 | +1.6 / 1.8 |
| wz_std 0.3 | 9.1 ± 6.6 | 21.1 | 8.2 | 4.5 | +1.2 / 2.7 |
| iteration 3 | 7.1 ± 5.1 | 20.1 | 6.0 | 3.2 | −0.8 / 2.3 |

- 모든 판 정지 0 · 후보 전부 충돌 0 · 평균 속도 0.079~0.080.
- 재현: base 씨앗별 최대 3.5~19.8 cm — 실제 15.7 은 위쪽 꼬리(10 개 중 2 개가 ≥ 12).
- 읽기(추정): ① 평균 차는 모두 표준오차의 1.3 배 이하 → **구분 불가**(선언 규칙). ② PathAlign 28 + PathFollow 5 는 최악 19.8 → 11.2 · 표준편차 반으로 — '가끔 크게 깎는' 꼬리를 줄이는 쪽으로 보임. ③ batch 2000 은 흔들림(표준편차)을 줄이지만 깎기 평균은 그대로 → 깎기는 표본 잡음이 아니라 **비용 구조가 고르는 해**(경로를 따르는 힘 < 앞쪽 점 당김 · 진행). ④ 10-23 실주행에서 PathAlign 28 은 5.5 s 정지(§6~§7)가 있었음 — 이 장면 시뮬엔 정지 없음(그 정지는 목표 방향 · 경로 방향 57° 어긋남 장면, 10-23 §7).

### §10.6 선언(사용자: "A 진행하라") — PathAlign 28 + PathFollow 5 를 10-23 f2pa2 5.5 s 정지 장면에서 (결과 보기 전)
- 장면: 10-23 f2pa2(B0 NavFn, 실주행 PathAlign 28) bag t 94 s 부터 16 s — 실제 정지 t 100.6~105.6 s(경로 방향 −43° 대 목표 방위 +14°, 10-23 §7). 경로 = /plan_smoothed(`path_topic=smoothed` 추가 — NavFn 판 BT 경로), 재표본 없음, 바퀴 포화 0.085. 입력 `2026-10-23/bags/bag_f2pa2.tgz` → Jetson /tmp.
- 변형: A14(B0 값) · A28(그때 실주행 값) · A28Fw5. 씨앗 1~10.
- 재현 판정: A28 에서 1 s 넘는 정지가 씨앗 일부라도 나오면 시뮬이 그 정지를 재현. 후보 판정: A28Fw5 의 정지 합 ≤ A14 의 정지 합 + 1 s 이고 정지 씨앗 수가 A28 보다 적을 것. 재현 안 되면 '이 장면 시뮬로는 안전 판단 불가' 로 기록하고 주행 판단은 사용자에게.

### §10.7 결과 — 시뮬이 f2pa2 정지를 재현하지 못함 → 이 장면 시뮬로는 PathAlign 28 의 안전 판단 불가
- 원문 `outputs/mppi_sim/sim_stall_1026.txt`(30 판), 요약 `outputs/mppi_sim/sim_stall_1026_summary.txt`, 시작 장면 확인 `outputs/mppi_sim/chk_sim_head_f2pa2.txt`(t 94 s 로버 (4.51, −1.80) −28°, /plan_smoothed 42 점 간격 0.025 — W3 접근 맞음).
- A14 · A28 · A28Fw5 모두 1 s 넘는 정지 **0**(씨앗 10 × 3), 평균 속도 0.076~0.078, 16 s 전진 0.96~0.97 m. 실제(A28)는 t 100.6~105.6 s 5.5 s 정지.
- 판정(선언 규칙): 재현 ✘ → 'PathAlign 28 이 정지를 부르는가' 는 시뮬로 판단 불가. 시뮬과 실제의 차이 후보(미확인): 목표 크리틱의 목표 자세(시뮬은 경로 끝 · goal_yaw 0), 실제 MPPI 의 직전 해 이어 쓰기(warm start)와 정지 상태 되먹임 세부, 경로 전환 시각.
- 정리(§10): 굽은 곳 깎기 줄이기 후보 = PathAlign 28 + PathFollow 5(꼬리 19.8 → 11.2 cm, 평균 차 구분 불가). 정지 위험은 10-23 실주행 1 회(f2pa2)가 유일한 증거이고 시뮬로는 확인 못 함 → 실주행 시험 여부는 사용자 결정.

## §11 실주행 A/B 선언 — Smac + PathAlign 28 · PathFollow 5 (사용자: "진행하자." — §10.7 의 1 번) — 결과 보기 전
- 구성: §7 Smac 구성 그대로 + MPPI PathAlign 14 → **28**, PathFollow 10 → **5**(Jetson yaml 만, `jobs/up_mppi_path_1026.sh 28 5`, 시험 뒤 `14 10` 으로 되돌림). 주행 f2sa1 · f2sa2 = b910.
- 비교 대상: f2sh1 · f2sh2(같은 Smac, 14 · 10): 상자 옆 실제 최소 18.4 · 10.8 cm, 복귀 굽은 곳 안쪽 이탈 최대(odom, §9 방식) f2sh2 +15.7.
- 판정: ① 전부 도착 · 접촉 0 · ABORT 0 ② 상자 옆 실제 최소 ≥ 8 cm(2 회) ③ **1 s 넘는 '이유 없는' 정지 0**(10-23 f2pa2 형 — W3 근처 포함), 있으면 즉시 기록 · 되돌림 ④ 복귀 굽은 곳 안쪽 이탈 최대(odom) 기록 — f2sh2 +15.7 대비 ⑤ 목표 시간 · 짧은 멈칫 기록.

### §11.1 f2sa1(Smac + PathAlign 28 · PathFollow 5) 결과 — 3/3 · 정지 0 · 상자 옆 14.6 cm · **굽은 곳 안쪽 이탈 +4.6 cm**(같은 Smac 14 · 10 판 10.7 · 15.7)
- 러너 `outputs/drives/f2sa1/run_f2sa1.txt`: 3/3 · 51.8 · 47.0 · 106.9 s(총 205.8 s), stuck 진단 0. prep `outputs/setup/prep_smac_1026_5.txt`(0.005 m · 12.17 V, 실행 중 PathAlign 28.0 · PathFollow 5.0 확인). bag `bags/bag_f2sa1.tgz`, 로그 → `outputs/drives/f2sa1/nav2_f2sa1.log` · `nav_events_ms_f2sa1.txt`.
- 판정 ③ ✔: 1 s 넘는 정지 **0**(`outputs/drives/f2sa1/anal_stops_f2sa1.txt`), W3 근처 포함.
- 상자 옆 실제 최소(`outputs/drives/f2sa1/anal_contact_f2sa1_d30.txt`): 갈 때 17.6 · 복귀 **14.6 cm**(15:14:53.1, 로버 (1.05, 0.30, −181°)) ② ✔.
- 굽은 곳 안쪽 이탈(odom, 컨트롤러 자기 좌표 · '안쪽 +'; 도구 `jobs/anal_bend_dev_odom.py` → `outputs/drives/f2sa1/anal_bend_dev_odom_sa1.txt`): f2sh1 +10.7 · f2sh2 +15.7 → **f2sa1 +4.6 cm**(95 % +4.3, 중앙 +0.9). 같은 창 map→odom 변화 5~7 cm(비교 판들과 같은 크기).
- 계획: 복귀 출발(15:13:19) Smac 'no valid path'(목표 (0, 0)) → NavFn 대체(설계대로 작동, 스무딩 충돌 → 원경로). 그 경로는 아직 모르는 상자를 관통(−15.5) → 15:15 전 로버 (2.44, −1.43) 에서 재계획 Smac 성공(17.0 cm, 계기 미확인 — 막힘 로그 0). Smac 실패 원인(목표 자세 차체 충돌 추정 — D4)은 미확인. NavFn 도 한 번 'failed with tolerance 0.25'.
- 1 회라 판단 보류 — f2sa2 로 재현 확인.

### §11.2 f2sa2 결과 · A/B 정리 — PathAlign 28 · PathFollow 5 가 굽은 곳 깎기를 줄임(2/2), 정지 없음
- 러너 `outputs/drives/f2sa2/run_f2sa2.txt`: 3/3 · 52.0 · 45.7 · 101.2 s(총 199.1 s), stuck 진단 2(관찰 모드). prep `outputs/setup/prep_smac_1026_6.txt`(0.006 m · 12.12 V, PathAlign 28 · PathFollow 5 확인). bag `bags/bag_f2sa2.tgz`, 로그 → `outputs/drives/f2sa2/nav2_f2sa2.log` · `nav_events_ms_f2sa2.txt`.
- BT 경로 전부 Smac(스무더 0). 1 s 넘는 정지 0(`outputs/drives/f2sa2/anal_stops_f2sa2.txt`). 막힘 감지 1(상자 (1.24, 0.07)) → 재계획 경로 15.7 cm(`outputs/drives/f2sa2/anal_plan_series_f2sa2.txt`).
- 상자 옆 실제 최소(`outputs/drives/f2sa2/anal_contact_f2sa2_d30.txt`): 갈 때 18.8 · 복귀 **14.9 cm**. 굽은 곳 안쪽 이탈(odom, `outputs/drives/f2sa2/anal_bend_dev_odom_sa2.txt`) **+1.6 cm**(95 % +0.9).

| 주행 | MPPI PathAlign · PathFollow | 상자 옆 실제 최소(복귀) | 굽은 곳 안쪽 이탈 최대(odom) | 1 s 넘는 정지 | 총 시간 |
|---|---|---|---|---|---|
| f2sh1 | 14 · 10 | 18.4 | +10.7 | 0 | 205.8 |
| f2sh2 | 14 · 10 | 10.8 | +15.7 | 0 | 201.7 |
| f2sa1 | **28 · 5** | 14.6 | **+4.6** | 0 | 205.8 |
| f2sa2 | **28 · 5** | 14.9 | **+1.6** | 0 | 199.1 |

- 판정(§11): ① ✔ ② ✔(14.6 · 14.9) ③ ✔ 정지 0(2 회) ④ 안쪽 이탈 10.7 · 15.7 → 4.6 · 1.6 cm ⑤ 시간 같은 수준.
- 읽기: 굽은 곳 깎기가 줄고 상자 옆 여유가 두 번 다 ~15 cm 로 고름(14 · 10 판은 18.4 · 10.8 로 흩어짐). 10-23 f2pa2 형 정지는 이 2 회에선 안 나옴(그때는 NavFn 경로 + W3 앞 경로 꺾임 장면 — Smac 경로에선 그 모양이 덜 생길 수 있음, 추정). 각 2 회라 표본이 작음.
- 상태: Jetson yaml 은 아직 28 · 5(저장소 기본 14 · 10). 채택(저장소 반영) 여부는 사용자 결정.

## §12 시각화 (사용자: "영상으로 시각화해달라.")
- 영상(1.5 배속, git 제외): `videos/f2sa1_return_box.mp4`(15:14:15~15:15:05) · `videos/f2sa2_return_box.mp4`(15:36:20~15:37:10), 비교 `videos/cmp_f2sh2_vs_f2sa2.mp4`(위 f2sh2 = MPPI 14 · 10, 아래 f2sa2 = 28 · 5, ffmpeg 세로 붙임). 생성 기록 `outputs/fig_video/fig_drive_video_f2sa*.txt`. 장면 `figures/compare/f2sa2_return_box_frame.png`.
- 비교 그림 `figures/compare/box_compare_b0_smac_mppi.png`(`jobs/fig_box_compare.py` → `outputs/compare/fig_box_compare_mppi.txt`): 오른쪽 판에 Smac 4 주행 — f2sh2(파랑)는 상자 동쪽 대각선에서 경로 안쪽으로 깎아 10.8 cm, f2sa1 · f2sa2 는 점선(경로) 바깥 호를 따라 14.6 · 14.9 cm.
- 영상 도구 수정: 스무더 사건이 하나라도 있으면 Smac 경로 규칙(점 간격 > 0.04 m)을 건너뛰어, NavFn 대체가 한 번 있던 f2sa1 첫 영상에 Smac 경로가 빠졌음 → 두 규칙을 항상 합침(f2sa1 다시 렌더: BT 경로 1 + Smac 3).

## §13 28 · 5 에서 '경로와 어긋나 멈췄다 다시 움직임' 이 있었나 (사용자: "MPPI 28/5에서, 중간중간 전역경로와의 괴리로, 멈췄다가 다시 움직이는 경우가 있었는가?")
- 도구: `2026-10-21/jobs/anal_dip_events.py`(전진 명령 < 0.01 묶음 + 앞 2 s ~ 뒤 0.5 s nav2 사건) → `outputs/compare/anal_dip_events_f2{sh1,sh2,sa1,sa2}.txt`, W3 출발 회전 확인 `jobs/chk_w3_turn.py` → `outputs/compare/chk_w3_turn.txt`.
- 멈칫 수: f2sh1 5 · f2sh2 4 · **f2sa1 6 · f2sa2 7**. 종류별:
  - **목표 바뀜(W3 도착 → 복귀 출발)에서 전진 0 근처 0.9~2.35 s**: 네 주행 모두(f2sh1 1.55 · f2sh2 1.35 · f2sa1 0.9 + 1.05 · f2sa2 2.35 s). 그 동안 회전 명령 −0.21~−0.37 rad/s · 실제 −0.10~−0.35 → **제자리에서 돌아서는 중**(멈춘 것 아님). f2sa1 은 그 사이 Smac 실패 → NavFn 대체 계획.
  - **TF 외삽으로 컨트롤러 중단 0.15~0.35 s**: f2sh1 2 · f2sh2 2 · f2sa1 2 · f2sa2 2(그중 f2sa2 15:36:33 은 막힘 감지 1.27 s 뒤 TF 중단).
  - 사건 없는 0.05 s 이하: 명령이 0 을 스치는 것.
- 결론: 28 · 5 두 주행에 10-23 f2pa2 같은 '경로 · 목표 어긋남으로 1 s 넘게 서 있는' 정지는 **없음**. 멈칫 수가 1~3 개 많은 것은 W3 돌아서기 구간을 둘로 나눠 센 것(f2sa1)과 사건 없는 0.05 s 스침 — 성격은 14 · 10 판과 같음.

## §14 MPPI 28 · 5 채택 · 서쪽 통로 주행 준비 (사용자: "28/5 채택하고 서쪽 통로 주행 준비하라")
- 저장소 `ros2_ws/src/rover_navigation/config/nav2_params.yaml`(브랜치 `feature/smac-hybrid`): PathAlign 14 → 28, PathFollow 10 → 5(근거 주석 포함). NavFn 판(planner:=navfn)도 같은 MPPI 값을 쓰게 됨 — B0 기준선은 태그 `navfn-baseline-20261023` 에 14 · 10 그대로. Jetson 배포 `jobs/up_params_1026.sh` → `outputs/setup/up_params_1026.txt`(저장소 판 sha 7bce0cb94734).
- §14.1 주행 선언 f2sa3 = no5(8 목표: B → C → 서쪽 통로 → 남서(위치만) → 서쪽 통로 → 위 복도 → W3 → 출발), 구성 = Smac(RS · 해석 1.0 m) → 실패 시 NavFn · MPPI 28 · 5 · 재계획 0.01 + PathBlockedAhead(only_new) · vslam on. 비교: 10-23 f2rp4(B0, no5 8/8 · 서쪽 통로 여유 3.7~4.8 · 최소 2.9 cm) · f2rp3.
- 판정: ① 8/8(남서는 위치만) · ABORT 0 · nav_guard 취소 0 · 접촉 0 ② **서쪽 통로 통과** — Smac 실패 시 NavFn 대체가 작동했는지(대체 횟수 · 자리 기록) ③ 복구 Wait ≤ 1 · 1 s 넘는 정지는 돌아서기 · TF 중단 외 0 ④ 서쪽 통로 · 출발 상자 최소 정확 여유 기록(f2rp4 대비) ⑤ 목표별 시간 기록(f2rp4 51.7 · 54.1 · 28.5 · 26.2 · 32.6 · 24.4 · 98.6 · 101.3 s).
- 사람이 통로에 없을 때 시작(사용자, 10-26 §8).

## §15 f2sa3(no5) 결과 — 8/8 · 서쪽 통로 통과(NavFn 대체 5 회 작동), 그러나 통로 최소 여유 **0.8 cm** · 정지 5 회(15.3 s) · Wait 2 → 판정 ③ ✘
- 러너 `outputs/drives/f2sa3/run_f2sa3.txt`: 8/8 — 52.3 · 55.4 · 26.4 · **39.7**(위치만) · **49.8** · 22.9 · 96.7 · 104.4 s(총 448.0; B0 f2rp4 417.9, 목표 4 · 5 는 26.2 · 32.6). prep `outputs/setup/prep_smac_1026_7.txt`(0.014 m · 12.11 V). bag `bags/bag_f2sa3.tgz`, 로그 → `outputs/drives/f2sa3/nav2_f2sa3.log` · `nav_events_ms_f2sa3.txt`.
- 계획: 서쪽 통로 계획 5 번 모두 **Smac 'no valid path' → NavFn 대체**(목표 4 · 5, 재계획 포함), 스무딩은 5 번 모두 충돌로 실패 → NavFn 원경로. 그 밖 구간은 Smac.
- 통로(목표 4 남행): 16:12:14~15.8 MPPI 최적화 실패 4 · MonotoneEscape · **Wait 7.1 s**, 로컬 정확 여유 최소 **0.8 cm**(16:12:15.7, (−1.44, −4.67, −57°)), < 2.7 cm 7 프레임(`outputs/drives/f2sa3/anal_band_run_f2sa3.txt`). 목표 5 북행: 최적화 실패 2, 막힘 → MonotoneEscape, 최소 2.8 cm. 1 s 넘는 정지 5 번 합 15.3 s(`outputs/drives/f2sa3/anal_stops_f2sa3.txt`) — 4 번이 통로, 1 번은 복귀 상자 막힘 뒤 Wait 4.8 s.
- 출발 상자: 복귀 실제 최소 13.2 cm(`outputs/drives/f2sa3/anal_contact_f2sa3_d30.txt`), 막힘 감지 → Wait(복구 차례가 Wait) → 재계획.
- 통로 추종 비교(`jobs/anal_corridor_track.py` → `outputs/drives/f2sa3/anal_corridor_track.txt`, 입력 10-23 bag_f2rp4 · bag_f2sa3): 컨트롤러 경로와의 |이탈| 중앙 **4.1 → 1.0 cm**(95 % 13.9 → 10.4), 로버 중심 로컬 비용 분포는 같음(중앙 71 · 95 % 80).
- 읽기(추정 — 각 1 회, 날짜 · 지도 다름): 통로에선 Smac 이 실패해 **NavFn 원경로**(벽 쪽으로 붙는 점 계획 경로)를 따름 → PathAlign 28 이 그 경로를 더 바짝 따라가 MPPI 가 통로 가운데로 비켜 갈 여지가 줄어든 것으로 보임(B0 14 · 10 은 경로에서 중앙 4 cm 벗어나며 지나감). 상자 구간(Smac 경로)에선 바짝 따름이 이득, 통로(NavFn 경로)에선 손해 — **경로 품질에 따라 같은 가중치가 반대로 작용**.

## §16 실제 촬영 영상 분석 · 시각화와 붙이기 (사용자: "오늘자 video 폴더에 20261026_160944.mp4 ... 실제 주행에서 무슨 일이 있었는지 분석하고, 이번 주행 시각화와 붙여서 보고 싶다 ... 토큰 문제 검증 후")
- 원본 `videos/20261026_160944.mp4`(사용자 촬영, git 제외): HEVC 3840×2160 · 120 fps · 445.06 s · 2.7 GB. 시각 맞춤: 파일 이름 16:09:44(시작) + 445 s = 생성 시각 16:17:11(끝) 와 맞음 → 시작 16:09:44 로 놓음(±1 s 추정, 프레임 대조로 더 맞추진 않음). 주행 시작 16:09:41.
- 토큰: 영상 자체는 ffmpeg(PC)로만 다룸 — 토큰을 쓰는 것은 들여다본 정지 그림뿐(640×360 장면 6 장을 1 장으로 묶어 4 장 + 확인 1 장).
- 작업본(git 제외): `videos/real/f2sa3_real_corridor_161145.mp4`(16:11:45~16:13:35) · `f2sa3_real_box_161615.mp4`(16:16:15~16:17:09), 1280×720 · 30 fps. 장면 묶음 `figures/real_video/corridor_a.png` · `corridor_b.png` · `corridor_c_box_a.png`(도구 `jobs/fig_real_tiles.py`).
- 본 것(촬영, 내 판독 — 추정 섞임 표시):
  - 서쪽 통로 남행 좁은 자리 = 왼쪽 검은 둥근 물체(의자 받침으로 보임) · **빨간 쇼핑백/카트**, 오른쪽 프린터와 **뚜껑 날개가 열린 상자(병 들어 있음)**. 16:12:17 로버가 그 사이에 비스듬히 끼어 있고 오른쪽 앞에 상자 날개가 바짝. 16:12:12~13 카메라가 그 상자 안을 비춤(사용자가 닿았는지 본 것으로 추정). 16:12:23 통과.
  - 남서 돌아서기 · 북행(16:12:45~16:13:09): 열린 상자 옆에서 방향 바꾸기 → 16:12:58(2.8 cm) 옆면이 상자에 가까움 → 16:13:09 탈출 동작.
  - 복귀 상자 = 낮은 골판지 받침. 16:16:57 상자 옆을 눈에 보이는 틈을 두고 지나감(기록 13.2 cm 와 어긋나지 않음).
- 배치가 10-23 과 같은가(`jobs/anal_corridor_gap.py` → `outputs/drives/f2sa3/anal_corridor_gap.txt`, 남행 직전 전역 코스트맵): 가장 좁은 곳(y −4.7~−4.8) 치명 칸 사이 **0.50 m — 두 날 같음**(차체 + 패딩 0.35 m → 양옆 최대 7.5 cm). 지도상 통로 폭은 같아 f2rp4 와의 비교는 유효(물건 세부 차이는 미확인).
- 붙인 영상(git 제외, 위 = 실제 촬영 · 아래 = 시각화, 같은 시각 1 배속): `videos/cmp_f2sa3_corridor.mp4`(110 s) · `videos/cmp_f2sa3_box.mp4`(54 s). 확인 장면 `figures/real_video/cmp_corridor_161217.png`(16:12:17 — 실제 로버가 비스듬히 끼인 순간, 시각화도 로버 −61° · 경로 −100° 로 비스듬, 복구 MonotoneEscape 표시). 시각화 생성 기록 `outputs/fig_video/fig_drive_video_f2sa3_corridor.txt` · `_box.txt`.
- 큰 원본(2.7 GB)은 지우지 않음 — 사용자 확인 뒤(큰 파일 규칙).

## §17 실제 촬영 + RViz 스타일 시각화 합본 (사용자: "닿지 않았다. 실촬영 영상과 시각화 데이터 합쳐달라. 시각화 영상은 rviz스타일로 해달라.")
- 사용자 확인: 16:12:13~17 통로에서 로버는 상자 날개에 **닿지 않음**(기록 최소 0.8 cm 와 어긋나지 않음 — 칸 단위 · 기억 오차를 생각하면 실제 틈은 그 근처, 미측정).
- 새 도구 `Docs/tools/fig_rviz_video.py`(720×720, 로버 따라가는 3 m 창): 어두운 바탕(#303030) · 1 m 격자, 전역 코스트맵 RViz 'costmap' 색표 흉내(파랑 → 빨강 비용 · 하늘색 내접 99 · 자홍 치명 100 · 회청 미지, 낮은 비용은 더 투명), 노란 칸 = 로컬 치명, 빨간 점 = /scan, 초록 = BT 경로 · 차체, 빨강 / 초록 = base_link x / y 축, 시각 · 명령 · 로버 자세 · 최근 사건(Smac 실패 → NavFn · 최적화 실패 · 복구 · 막힘). BT 경로 고르기는 fig_drive_video 와 같은 규칙.
- 합본(git 제외, 왼쪽 실제 촬영 1280×720 · 오른쪽 RViz 스타일 720×720, 1 배속): `videos/f2sa3_real_rviz_corridor.mp4`(16:11:45~16:13:35) · `videos/f2sa3_real_rviz_box.mp4`(16:16:15~16:17:09). 생성 기록 `outputs/fig_video/fig_rviz_video_f2sa3_*.txt`, 확인 장면 `figures/real_video/real_rviz_corridor_161217.png`.

### §17.1 고화질 · 2 배속 판 (사용자: "실제 영상 구간 잘라놓은 것이, 해상도가 좋지 못해 보기 안좋다. 그리고 조금 배속을 걸어달라.")
- 실제 촬영: 4K 원본에서 1920×1080(lanczos) · 2 배속 · crf 19 로 다시 자름 `videos/real/f2sa3_real_{corridor,box}_hd_x2.mp4`. RViz 스타일: 1080×1080 · 2 배속(도구에 한 변 px 인자 추가) `videos/real/f2sa3_rviz_{corridor,box}_1080_x2.mp4`(`outputs/fig_video/fig_rviz_video_f2sa3_*_x2.txt`).
- 합본(git 제외, 3000×1080): `videos/f2sa3_real_rviz_corridor_hd_x2.mp4`(55 s = 16:11:45~16:13:35) · `videos/f2sa3_real_rviz_box_hd_x2.mp4`(27 s = 16:16:15~16:17:09). 확인 장면 `figures/real_video/real_rviz_corridor_hd_x2.png`(16:12:17) · `_end.png`(16:13:33 — 두 쪽 모두 로버 북행).
- 내 실수: 첫 통로 판은 `-t 110` 을 입력 뒤에 둬 출력 길이로 걸려 원본 220 s 를 2 배속으로 잘랐고(3300 장), 합칠 때 `-shortest` 가 필터 그래프에 안 먹어 시각화 끝 장면이 55 s 동안 멈춰 있었음 → `-t` 를 입력 앞으로, hstack `shortest=1`. 다음에 알아보는 법: 자른 뒤 ffprobe 로 길이 · 장 수를 기대값과 대조.

## §18 폴더 정리 (사용자: "2026-10-26 폴더 구조가 너무 난잡하다. 분석 후 정리해달라.")
- 전: `outputs/` 맨 위에 파일 86 개 + 폴더 12 개(주행 · 시뮬 · 전송 · 영상 기록이 이름 순으로 섞임), `figures/` 맨 위에 변형 폴더 18 개 + 그림 4 장, `TOOLS.md` 없음(10-12 도구 규약 위반).
- 후(파일 이름 그대로, 위치만 — `git mv` 로 이력 유지): `outputs/` = `setup/` · `planner_offline/` · `rev_sign/` · `drives/<주행>/` · `mppi_sim/` · `compare/` · `fig_video/`, `figures/` = `planner_offline/` · `compare/` · `real_video/`(옛 `real/`). `jobs/` · `videos/` · `bags/` 는 그대로(용도 앞머리로 이미 구분 · git 제외). 폴더 지도와 도구 색인은 `TOOLS.md`.
- §0~§17 의 경로는 같은 규칙으로 자리에서 고침(스크립트 치환 54 줄, 고친 뒤 SUMMARY 의 모든 경로가 실제로 있는지 확인 — 없다고 나온 것은 글롭 패턴과 10-23 경로뿐). 다른 날짜 폴더 · `Docs/tools` 에서 10-26 산출물을 가리키는 곳은 없었음(grep).
- §16 의 원본 촬영 `videos/20261026_160944.mp4`(2.7 GB)는 **사용자가 지움**(10-26 저녁). 남은 것 = 잘라 둔 구간 `videos/real/f2sa3_real_{corridor_161145,box_161615}.mp4`(1280×720) · `f2sa3_real_{corridor,box}_hd_x2.mp4`(1920×1080 · 2 배속). 이 두 구간 밖 장면이나 4K 로 다시 자르는 것은 **원천 소실**.
