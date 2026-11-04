# 세워 둔 로버의 방향 추정 드리프트 → 틀린 자세로 출발 · 경로 없음 (9 기: 10-28 §13.1 · §16 ~ 10-29 §5)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **조사 중** · 증상 차단 구현(미배포) — 원인(무엇이 정지 중 odom yaw 를 돌리나)은 미확인. 정지만으로는 재현 안 됨(d1 30 분 0.07°), '주행 뒤 정지' 시험 d2 는 선언만 하고 미실행(10-29 §4 · §5). 증상 차단(출발 전 라이다 ↔ 지도 검사 ⓐ)은 저장소 소스에만 있고 Jetson 배포 · 실동작 확인 없음(§4.2) | 10-28 ~ (11-04 까지 진전 없음 — 11-02 SUMMARY '다음 후보' 에 'ⓐ 배포 · d2' 로만 남음) | [10-28 §13.1](../debug_log/2026-10-28/SUMMARY.md)(그때는 원인 오판) · [§16.1](../debug_log/2026-10-28/SUMMARY.md) | `ros2_ws/src/rover_navigation/scripts/place_server.py`(출발 전 위치 추정 검사, 10-29 커밋 `b359fbc7`) | [SLAM 시각 정체](slam-stamp-freeze.md)(SLAM 이 언제 스캔을 처리하나) · [SLAM 포크 — 회전 중 스캔 처리](slam-fork-rotation.md)(위치 추정 모드 회전 문턱 0.15 rad — §3 의 모순) · [센서 컨디셔너 · ZUPT](sensor-conditioner.md)(09-10 ZUPT 도입 — 없을 때 80 분 정지 ≈ 105°) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) · [주행 전 검사 · 운용(8 기)](drive-ops-1019-1023.md) (8 기) · [F2.5 장소 이름 이동](f25-place-navigation.md)(ⓐ 가 들어간 서버 · 휴대폰 명령 — 9 기) · [주행 전 검사 한 노드](drive-gate-consolidation.md)(prep 의 출발 위치 검사와 구분 — 9 기) |

**한 줄**: 주행한 뒤 세워 둔 로버는 odom 방향 추정이 분당 0.04~0.39° 돌고, SLAM 위치 추정은 로버가 움직이지 않으면 스캔을 처리하지 않아 고치지 않는다. 그래서 실제 벽이 돌아간 자리에 칠해져 출구가 막히거나(경로 없음), 틀린 방향으로 출발한다(f2pl1, 7°). prep 직후 정지에서는 생기지 않는다(30 분 0.07°). 원인은 아직 모른다.

> 보충(11-04 카드 작성 중 원문 · 코드 대조): ① '정지 중 SLAM 이 안 고친다' 의 추정 기전(최소 이동 조건)은 지금 설정과 **맞지 않는 데가 있다** — 위치 추정 모드 포크는 odom 자세의 회전이 0.12 rad(6.9°)를 넘으면 스캔을 처리하는데, f2pl5 뒤 odom yaw 는 16.6° 돌았고 map→odom 은 그대로였다(§3 · §6). ② 10-28 §16.1 의 원천 후보 'cuVSLAM 속도' 는 EKF 설정상 yaw 에 직접 들어가지 않는다(§3). ③ f2pl1 은 '출발 37 s 뒤' 가 아니라 **움직인 첫 판(2 s 안)**에 이미 맞춰졌다(§6).

## 1. 증상
- 10-28 15:18 dry_run: 출발점에서 모든 목표 경로 조회 실패, 비워도 5 s 안에 치명 띠가 되살아남. [10-28 §13.1](../debug_log/2026-10-28/SUMMARY.md)
- 10-28 16:10 같은 증상. 로버에서 닿는 칸 1.3 m², 출발 방 출구에 정적 지도에 없는 치명 칸 185 개(실제 벽을 로버 둘레로 돌린 모양). [§16.1](../debug_log/2026-10-28/SUMMARY.md) · `2026-10-28/outputs/gcm_reach_1610.png` · `gcm_vs_static_1610.txt`
  - 문자 격자 발췌([`gcm_vs_static_1610.txt`](../debug_log/2026-10-28/outputs/gcm_vs_static_1610.txt) — `#` 치명이고 정적 지도도 점유 · `N` 치명인데 정적 지도는 빈 칸 · `+` 내접 99 · `~` 로버에서 닿는 칸 · `@` 로버):
    ```
    x -0.60..2.60 (칸 5 cm) · 로버 (-0.01, 0.08)
      +0.55 NN++NNN++++++~~~~~~~~~~~~~+++~++++N+++++++.......................
      +0.10 ~~~~~~~~~~~~@~~~~~~~~~+++++++~~~~~~~+++NN++++...................+
      -0.10 ~~~~~~~~~~~~++++++++++~~~~~~~~~~+++++NNN++++++..................+
      -0.60 #################+################################+++..........++
    창 안 치명 · 정적 지도엔 빈 칸(N) 185 칸
    ```
    읽기: 남쪽 y −0.60 띠는 `#`(정적 벽), 동쪽 x ≈ 1.2~1.4 를 세로로 막은 것은 `N`(돌아간 벽) — 닿는 칸 `~` 가 그 안에 갇힘.
- 위험(10-28 §16.1 '안전 의미'): 오차가 작으면 경로가 나오고 틀린 자세로 출발한다 — f2pl1 이 실제로 7° 틀린 채 출발했다(10-29 §2, bag 재분석).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 10-28 §13.1 | 출발점 갇힘 원인 칸 | 남쪽 y −0.57 띠 · f2pl4 끝 격자엔 없음 · 비워도 되살아남 | '13:44 이후 생긴 nvblox 기억'(**틀림**, §16.2) | `2026-10-28/outputs/costmap_robot_1519*.txt` |
| 10-28 §16.1 | 전역 코스트맵 전체 · 정적 지도 대조 · 라이다 yaw 맞춤 · TF 이력 | 치명 185 칸 = 돌린 벽 · 맞춤 지금 0.140 / −32.5° 에서 0.295 · odom yaw **+16.6° / 43 분** · map→odom 불변 | 정지 중 odom yaw 가 돌고 SLAM 은 안 고침 | `2026-10-28/outputs/{gcm_vs_static_1610,scan_align_1615,odom_yaw_end_f2pl5}.txt` |
| 10-28 §16.3 | 대책 후보(사용자 결정) | ⓐ 출발 전 스캔 ↔ 정적 지도 점수 검사 · ⓑ 정지 판정 중 yaw 고정(EKF/컨디셔너) · ⓒ 출발 전 제자리 소회전으로 SLAM 이 다시 맞추게 | 추천 ⓐ(어떤 원인이든 잡음 · 코드 작음), ⓑ 는 원인 쪽 | [10-28 §16.3](../debug_log/2026-10-28/SUMMARY.md) |
| 10-29 §0 | 밤새 측정하려 했으나 | Jetson 밤사이 재부팅 | 원천 소실. 어제 sensors.log: 출발 전 ZUPT 20 s 마다 정상, **주행 뒤 정지 구간 로그 없음** | `2026-10-29/outputs/zupt_f2pl5_sensors.txt` |
| 10-29 §2 | prep 직후 원천별 yaw rate 1 분 | 원시 자이로 +2.14 °/min · 조건 IMU +0.02 · EKF +0.02 | ZUPT 가 바이어스를 지움 | 대화 기록(§2 표) · `jobs/chk_yaw_drift.py` |
| 10-29 §2 | 어제 bag 5 개 2 s 마다 라이다↔지도 맞춤 | 맞던 상태 점수 ≥ 0.594 · 주행 중 각 ≤ 3.0°. **f2pl1 출발 직전 −7°**(→ 출발 37 s 뒤 SLAM 이 고침 — §6 ③: 실제로는 움직인 첫 판) · f2pl4 직전 +2.5° · prep 직후 0~0.5° | **어제 f2pl1 은 7° 틀린 채 출발**. 드리프트는 주행 뒤 정지에서만 | `2026-10-29/outputs/scan_align/*` |
| 10-29 §2 | 검사 ⓐ 구현(`place_server.py`) | 문턱 0.40 · 4° · 0.03(근거 570 판) | 증상 차단, 미배포 | 커밋 `b359fbc7` |
| 10-29 §3 | d1: prep 뒤 30 분 정지 기록 | EKF **+0.07°**(원시 적분 +73°) · ZUPT 30 분 내내 · map→odom 0 | 정지만으로는 재현 안 됨 | `2026-10-29/outputs/anal_drift_d1.txt` · `bags/bag_d1.tgz` |
| 10-29 §4 | d2 선언: 주행 뒤 40 분 정지 + 검사 실동작 | (미실행) | | `2026-10-29/jobs/run_d2_1029.sh` |
| 10-29 §5 | 하루 마무리 | d2 실행 안 함, ⓐ 저장소 소스만 | 다음 = d2. '다음 세션은 가동 시간과 관계없이 prep 부터' | [10-29 §5](../debug_log/2026-10-29/SUMMARY.md) |
| 10-29 §6 ~ §9 · 11-02 ~ 11-04 | 문제 대장 작업으로 넘어감(주행 없음) | 11-02 '다음 후보: 드리프트 — 위치 확인 ⓐ 배포 · d2', 11-04 §1 Jetson src 비교 8 파일에 `place_server.py` 없음 | **진전 없음** — ⓐ 의 Jetson 판은 확인된 적 없음 | [11-02 SUMMARY](../debug_log/2026-11-02/SUMMARY.md) 71 행 · [11-04 §1](../debug_log/2026-11-04/SUMMARY.md) · [`chk_src_md5_1104.txt`](../debug_log/2026-11-04/outputs/chk_src_md5_1104.txt) |

**앞선 관측(10-30 문제 대장 3 시기를 읽으며 추가 — 이 카드의 판정은 바꾸지 않음)**
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-15 §0.5 | 사용자 우려 '시간이 지나 세션에 오차가 쌓였나' → 정지 30 s 점검(Jetson 가동 3 h 19 min, 충전 뒤 재부팅 · 그날 첫 주행 mp1 **전**, 그 전엔 정지 상태의 Smac 스윕만) | 휠 odom 위치 0.0000 m · yaw 0.00 °/min · **EKF 위치 0.0000 m · yaw +0.05 °/min**(09-10 1.31 → ZUPT 뒤 0.02~0.05) · map→odom 변화 0 / 0 / 0.000° · odom→base yaw 변동 0.052° / 30 s · `/wheel_odom` 25.1 Hz · EKF 27.6 Hz · 카운터: EKF 위반 0 · nav2 ERROR 0 · slam 폐기 27 · 에이전트 세션 1 | '기반 계층에 누적 오차 없음, 손 배치로 낡은 것은 SLAM 자세뿐 → 재기동' | SUMMARY 표만(**출력 원문 없음**) · 도구 [`2026-09-15/jobs/job321_drift.py`](../debug_log/2026-09-15/jobs/job321_drift.py) · 러너 [`run_j321.sh`](../debug_log/2026-09-15/jobs/run_j321.sh) |
- 이 카드와의 관계: 'prep(기동) 뒤 오래 켜 둔 정지' 조건이라 10-29 d1(30 분 +0.07°)과 같은 쪽이고, '주행 **뒤** 정지' 는 아니다 → 09-15 의 정상 판정은 H1 · H2 를 지지도 기각도 하지 않는다. 또 **창 30 s 가 너무 짧다**: +0.05 °/min 은 30 s 동안 0.025° 로 같은 창의 odom→base 잡음 변동(0.052°)보다 작아, 10-28 의 0.04~0.39 °/min 하단은 이 방법으로 구별되지 않는다(계산). map→odom 변화 0 은 '정지 중 SLAM 이 고치지 않음' 의 가장 이른 기록이다(그때는 정상 동작으로 해석 — 그 해석 자체는 맞다).
- `job321_drift.py`(Jetson, `run_j321.sh` 가 올려 실행 — 그 러너는 앞에 Jetson uptime · 에이전트 컨테이너 상태 · `/tmp/sensors.log` 의 'violat' 줄 수 · slam.log 'dropping' · nav2.log 'ERROR' · 에이전트 'session established' 개수를 찍고, 뒤에 load · 릴레이 ms/프레임을 찍는다): `/wheel_odom` · `/odometry/filtered` · `/scan` · `/camera/depth/points_filtered` 를 센서 QoS 로 30 s 구독해 수신률과 stamp 지연(now − header.stamp)의 중앙 · 최대, 두 odom 의 처음 · 끝 위치 차와 yaw 차(°, ×2 = °/min), 2 s 마다 TF `map→odom` · `odom→base_link` 의 stamp 지연과 정지 중 x · y · yaw 범위(최대 − 최소). 판정 문턱은 코드에 없다(사람이 읽음). 결함: yaw 차를 `P[-1] − P[0]` 로 바로 빼 ±180° 넘김을 처리하지 않음(정지라 무해) · 처음 · 끝 두 점만 써 잡음에 민감. 계보 → 10-29 `chk_yaw_drift.py`(원천별 yaw rate, 1 분 창). 지금 다시: 쓸 수 있으나 창을 수 분 이상으로 늘려야 이 카드의 율을 본다.
- 더 앞(09-10, [센서 컨디셔너 카드](sensor-conditioner.md)): ZUPT 도입 전 80 분 정지에 약 105°(1.31 °/min) — 그때 원인은 부팅 캘리브 뒤 발열로 바이어스가 움직인 것, 대책이 ZUPT. 이 카드의 드리프트는 ZUPT 가 있는데도 생긴 것이라 같은 문제의 재발인지 다른 원천인지가 핵심 질문이다(§3 H1).

### 2.1 판정별 발췌 (README §2.3 — 스크립트 핵심 + 실제 출력)
**(가) 10-28 §16.1 — 정지 중 어느 TF 가 돌았나**
- 도구: f2pl5 bag 끝 TF 는 '인라인 rosbags'(10-28 TOOLS 42 행) — **스크립트 원문 없음, 출력만**. 지금 상태는 `chk_scan_align.py`(아래 §9.1) 머리 두 줄.
- 출력 [`odom_yaw_end_f2pl5.txt`](../debug_log/2026-10-28/outputs/odom_yaw_end_f2pl5.txt)(CP949 저장 — 읽을 때 `iconv -f cp949`) · [`scan_align_1615.txt`](../debug_log/2026-10-28/outputs/scan_align_1615.txt)(첫 줄은 WSL 잡음):
  ```
  bag 끝(정지 뒤) TF
    map→odom 15:32:20 (0.019, 0.041, -2.1°)
    odom→base_link 15:32:20 (0.085, 0.019, -161.4°)
  끝 8 s /odometry/filtered ω 평균 0.00318 rad/s (10.95 °/min) · n 241
  ---- (16:15, scan_align_1615.txt)
  map→odom: (0.019, 0.041, -2.1°)
  odom→base_link: (-0.030, 0.037, -144.8°)
  라이다 점 1699 · 지금 TF(0°) 점수 0.140
    yaw -32.5° → 0.295
  ```
  읽기: odom→base_link yaw −161.4 → −144.8° = **+16.6°**, map→odom 은 소수 셋째 자리까지 같음 → 돈 것은 odom(EKF) 쪽, SLAM 은 그 사이 한 번도 고치지 않았다(측정). odom→base_link 위치도 (0.085, 0.019) → (−0.030, 0.037)로 0.12 m 바뀌었다 — yaw 가 돌면서 EKF 위치도 움직인 것인지는 SUMMARY 에 언급 없음(**미확인**). 셋째 줄 '끝 8 s ω 평균 10.95 °/min' 은 SUMMARY 가 쓰지 않은 값 — 도착 직후 끝 회전이 섞였는지 정지 중 율인지 가르지 않았다(43 분 평균 0.39 °/min 의 28 배라 정지 중 율로 이어졌다고 보긴 어려움, 계산).

**(나) 10-29 §2 — 출발 직전 방향이 맞았나(라이다 ↔ 정적 지도)**
- 핵심 줄([`anal_scan_align_bag.py`](../debug_log/2026-10-29/jobs/anal_scan_align_bag.py)):
  ```python
  G = binary_dilation(np.array(MAP.data, np.int16).reshape(i.height, i.width) >= 65, iterations=1)
  def score(d):   # 라이다 점(≤ 6 m)을 각 d 만큼 더 돌려 정적 점유 칸(1 칸 팽창) 안에 드는 비율
      ...; return float(G[J[v], I[v]].mean())
  S = np.array([score(d) for d in D]); k = int(np.argmax(S))      # D = −30 ~ +30°, 0.5° 간격
  print(name, ts, x, y, yaw, v, S[len(D)//2], S[k], degrees(D[k]))  # s0 = 지금 TF · sb · db
  ```
- 출력 [`scan_align/f2pl1.txt`](../debug_log/2026-10-29/outputs/scan_align/f2pl1.txt)(열: 이름 t x y yaw v s0 sb db):
  ```
  f2pl1 1793160712.3 -0.10 +0.03   +5.0 0.000 0.711 0.814  -7.0
  f2pl1 1793160741.0 -0.10 +0.03   +5.0 0.000 0.707 0.806  -6.5
  f2pl1 1793160743.0 +0.05 -0.00  +11.8 0.055 0.911 0.912  +0.5
  f2pl1 1793160747.2 +0.28 +0.09  +31.4 0.071 0.914 0.923  -1.5
  ```
  분포 [`scan_align/summary.txt`](../debug_log/2026-10-29/outputs/scan_align/summary.txt):
  ```
  판 570 · 정지(v<0.02) 83
  정지 s0 최소 0.594 · 5% 0.629 · 중앙 0.809 | |db| 중앙 1.0 · 95% 7.0 · 최대 7.5 | sb-s0 95% 0.110 최대 0.113
  주행 s0 최소 0.596 · 5% 0.634 · 중앙 0.818 | |db| 중앙 0.5 · 95% 1.5 · 최대 3.0 | sb-s0 95% 0.020 최대 0.059
  ```
  읽기: 정지 중 −7° 쪽으로 돌리면 점수가 0.71 → 0.81 로 오른다 = 방향 추정이 약 7° 틀림(측정). 정지 판의 |db| 95 % 7.0 은 거의 f2pl1 출발 직전 판들이 만든 값 — '맞던 상태' 의 문턱 근거로는 주행 판(최대 3.0° · sb − s0 95 % 0.020)을 썼다(10-29 §2).

**(다) 10-29 §3 — d1 정지 30 분**
- 핵심 줄([`anal_drift_bag.py`](../debug_log/2026-10-29/jobs/anal_drift_bag.py)):
  ```python
  def dyaw(X, a, b): u = np.unwrap(X[i:j + 1, 1]); return degrees(u[-1] - u[0])      # TF yaw 변화
  def integ(X, a, b):                                                                # 각속도 적분
      dt = np.minimum(np.diff(s[:, 0]), 0.2)   # 빠진 구간은 0.2 s 까지만 이어 붙임
      return degrees(sum(s[:-1, 1] * dt)), degrees(s[:, 1].mean()) * 60
  # 조건 IMU · 원시 IMU 는 광학 −y(= 로봇 yaw), 휠 · EKF 는 twist.angular.z
  ```
- 출력 [`anal_drift_d1.txt`](../debug_log/2026-10-29/outputs/anal_drift_d1.txt):
  ```
  구간 t s      | EKF Δ°  | map→odom Δ° | ∫조건IMU° | ∫원시IMU° | ∫휠° | ∫EKF wz° | 뺀 바이어스 °/min
      0–  300 |  +0.056 |  +0.000 |   +0.041 |  +11.274 | +0.00 |  -0.063 | +2.254
   1500– 1798 |  -0.064 |  +0.000 |   -0.066 |  +12.649 | +0.00 |  +0.053 | +2.561
  전체 1798 s: EKF Δ +0.072° (+0.002 °/min) · map→odom Δ +0.000° · ∫조건IMU +0.051° · ∫원시IMU +73.097° · ∫휠 +0.000° · ∫EKF wz +0.016°
  판정 ① |EKF Δ| 0.07° (≥3 재현 · <1 안 됨) · ② ∫조건IMU/EKF Δ = 70 % · ④ |map→odom Δ| 0.00° (<0.5 = 안 고침)
  ```
  읽기: 도구가 ② 를 '70 %' 로 찍은 것은 EKF Δ 가 0.05° 문턱을 겨우 넘어서다 — SUMMARY 는 'Δ 가 너무 작아 의미 없음' 으로 읽었다(맞는 읽기). 원시 자이로는 30 분에 73° 돌 만큼 치우쳐 있고, 컨디셔너가 구간마다 2.25~2.56 °/min 을 빼 0.07° 로 묶었다(측정). 뺀 양이 30 분 동안 0.3 °/min 늘었다 = 정지 중에도 바이어스가 천천히 움직였고 ZUPT 가 따라갔다(계산).
- ZUPT 로그([`zupt_d1.txt`](../debug_log/2026-10-29/outputs/zupt_d1.txt) 94 줄, 첫 · 끝):
  ```
  ZUPT #1: bias y -0.000658 → -0.000649 (관측 -0.000572), 잔차 yaw rate -0.000078 rad/s = -0.27 °/분
  ZUPT #931: bias y -0.000701 → -0.000711 (관측 -0.000803), 잔차 yaw rate +0.000091 rad/s = +0.31 °/분
  ```

**(라) 10-29 §0 — 어제 주행 앞뒤의 ZUPT**
- 출력 [`zupt_f2pl5_sensors.txt`](../debug_log/2026-10-29/outputs/zupt_f2pl5_sensors.txt)(12 줄, 원본 `2026-10-28/outputs/drives/f2pl5/sensors.log`):
  ```
  gyro bias calibrated: (-0.00743, -0.00070, -0.00182) rad/s, std=(0.0027, 0.0022, 0.0018)
  ZUPT #1: bias y -0.000696 → -0.000722 (관측 -0.000951), 잔차 yaw rate +0.000229 rad/s = +0.79 °/분
  ZUPT #91: bias y -0.000798 → -0.000802 (관측 -0.000838), 잔차 yaw rate +0.000036 rad/s = +0.12 °/분
  ZUPT #98: bias y -0.000772 → -0.000788 (관측 -0.000938), 잔차 yaw rate +0.000150 rad/s = +0.51 °/분
  ```
  읽기: #91 → #98 사이 로그 시각 206 s(주행 15:29:05~15:32:20 = 195 s 와 비슷) — #98 은 복귀 직후 첫 정지 갱신으로 보인다(추정, 로그 시각은 Jetson 시계라 벽시계와 직접 대조 안 함). 그 뒤 43 분은 로그 사본이 15:32 에 끝나 **원천 소실**. 즉 'ZUPT 가 주행 뒤 멈췄나(H1)' 를 가를 줄은 남아 있지 않다.

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| nvblox 기억이 띠를 만듦 | 정적 지도와 겹쳐 N/# 로 나눔 | 남쪽 띠는 정적 벽, 막은 것은 돌린 벽 | **기각**(§16.2) |
| 정지만 해도 자이로 잔차로 돎 | d1(prep 뒤 30 분) | 0.07° | **기각**(10-29 §3) |
| (H1) 주행 뒤 ZUPT 가 멈추고 데워진 자이로 바이어스가 변함 | d2 의 ZUPT 로그 · ∫조건 IMU vs EKF Δ | — | 미확인 |
| (H2) 주행 뒤 휠 · 그 밖 입력이 0 아닌 yaw 를 줌 | d2 의 ∫휠 · 입력별 적분 | — | 미확인 |
| SLAM 이 정지 중 고치지 않음 | map→odom 변화 | 10-28 · d1 모두 0 | **확인**(기전은 slam_toolbox 최소 이동 조건으로 추정) |
| (카드 작성 중 추가) 그 기전 = 최소 이동 조건 | 지금 설정 대조: `slam.launch.py` 75~77 행 위치 추정 `minimum_travel_heading 0.15` · 포크 조건 `dheading < 0.8 × min_heading` 이면 버림([SLAM_FORK_ROTATION.md](../04_navigation/SLAM_FORK_ROTATION.md) 24 행) → odom 자세가 **0.12 rad(6.9°)** 넘게 돌면 처리 대상 | d1(0.07°)과 f2pl4 앞(2.5°)은 문턱 아래라 맞음. f2pl1 앞 7° 는 문턱 언저리. **f2pl5 뒤 16.6° 는 문턱의 2.4 배인데 map→odom 불변** | **어긋남 — 미확인**. 가능성(전부 추정): 드리프트가 고르지 않아 대부분이 마지막 몇 분에 생겼다 · 처리했지만 정합 결과를 버렸다(위치 추정 정합이 이전 자세 근처만 찾음) · `scan_ctr < 5` 같은 다른 조건. 다음에 볼 것 = d2 기록의 slam.log 처리 · 정합 줄과 map→odom 이력 |
| (카드 작성 중 추가) 원천이 cuVSLAM 속도(10-28 §16.1 미확인 ①) | EKF 설정: `ekf.launch.py` 30~31 행 `odom1_config` = vx · vy 만, `ekf.yaml` 18~23 · 35~40 행 yaw rate 는 휠 `odom0` vyaw · 자이로 `imu0` 만 | cuVSLAM 은 yaw · yaw rate 를 직접 주지 않음 | **약화**(설정 근거 — 공분산을 통한 간접 영향은 0 이라고 확인한 것은 아님) |
| (카드 작성 중 추가) f2pl5 의 스캔 맞춤 30° 와 odom 변화 16.6° 차 | `scan_align_1615.txt` 상위 5 각 −26~−33.5°, 점수 0.29(맞던 상태 0.59 미만) | 복귀 도착 때 이미 틀렸는지 · 맞춤이 거친 값인지 못 가름 | 미확인(10-28 §16.1 미확인 ② 그대로) |

## 4. 조치와 효과
### 4.1 운용 규칙
- 운용 규칙(10-28): 정지가 길었으면 출발 전 prep. CLAUDE.md §6 F2.5 줄('대책 결정 전까지 정지가 길었으면 출발 전 prep').
- 10-29 §5 강화: '다음 세션에서는 가동 시간과 관계없이 prep 부터'. prep 은 SLAM 을 출발 테이프 자세 (0, 0, 0°)로 다시 띄우므로 로버를 테이프에 다시 놓아야 한다(10-28 §13.1 '복구 방법').

### 4.2 출발 전 위치 추정 검사 ⓐ(10-29) — 증상 차단
- **출발 전 위치 추정 검사(ⓐ, 10-29)** `place_server.py`: 라이다 한 판 ↔ 정적 지도 점수 < 0.40 이거나, 최적 각 > 4° 이면서 그 각에서 점수가 +0.03 이상 오르면 go_to 거절('prep 필요'). 문턱 근거 = 맞던 570 판 vs 틀린 두 사례(§2). **Jetson 배포 · 실동작 미확인.**
- 핵심 줄([`place_server.py`](../../ros2_ws/src/rover_navigation/scripts/place_server.py) 170~181 행):
  ```python
  def loc_ok(self):
      if not self.p('loc_check'): return True, '위치 검사 끔'
      res, why = self.loc_align()
      if res is None: return False, '위치 검사 못 함: ' + why
      s0, sb, db = res; txt = '라이다↔지도 %.2f · 최적 각 %+.1f° (%.2f)' % (s0, db, sb)
      if s0 < self.p('loc_min_score'): return False, txt + ' — 점수 낮음, 위치 추정이 틀렸을 수 있음(prep 필요)'
      if abs(db) > self.p('loc_max_yaw') and sb - s0 >= self.p('loc_min_gain'):
          return False, txt + ' — 방향 추정 약 %.0f° 틀림(prep 필요)' % -db
      return True, txt
  ```
- 문턱을 오늘 본 판에 대 보면(계산, 10-29 §2): 10-28 16:15(s0 0.140 < 0.40) 거절 · f2pl1 출발 직전(|db| 7.0 > 4, sb − s0 0.10 ≥ 0.03) 거절 · f2pl4 출발 직전(|db| 2.0~2.5) 통과 · prep 직후 통과.
- 기각한 대안(10-29 §2): 자동 재위치(찾은 각으로 `/initialpose`) — 잡동사니에서 거짓 최적이 나올 수 있어 사람 확인(prep) 쪽으로.
- 원인 쪽 대책(10-28 §16.3 ⓑ yaw 고정 · ⓒ 소회전)은 d2 결과 뒤로 미룸 — 결정 없음.

### 4.3 지금 코드 영향 (11-04 저장소 기준)
| 무엇 | 지금 | 근거 |
|---|---|---|
| ⓐ 코드 위치 | `place_server.py` 23 행(파라미터 설명) · 57 행 기본 `loc_check True · loc_min_score 0.40 · loc_max_yaw 4.0 · loc_min_gain 0.03` · 64~65 행 `/scan` 구독 · 146~149 행 `/map` 점유 1 칸 팽창 · 151~168 행 `loc_align`(±30° · 0.5° · 점 ≤ 6 m · 라이다 2 s 넘게 끊기면 검사 못 함) · 170~181 행 `loc_ok` · 190~192 행 `where` 응답에 결과 · 204~205 행 `do_go`(go_to · return — return 은 go_to 홈으로 바뀜) 거절 | 저장소 파일 |
| 배포 | **확인된 적 없음**. 10-29 §5 '저장소 소스만', 커밋 `b359fbc7` 이후 이 파일 변경 없음(`git log`). 11-04 §1 Jetson src 비교 8 파일에 `place_server.py` 가 들어 있지 않아 Jetson `~/ros2_ws/src` 판이 ⓐ 판인지 모름 | [`chk_src_md5_1104.sh`](../debug_log/2026-11-04/jobs/chk_src_md5_1104.sh) 파일 목록 |
| 실주행 영향 | **없음** — `place_server` 는 어떤 launch 에도 없고(CLAUDE.md F2.5 · 11-03 §7 ③) job 스크립트가 따로 띄운다. 표준 순회(`job125_avoid3.py` 러너 · `prep_patrol.sh`)는 place_server 를 거치지 않으므로 ⓐ 가 켜져도 그 경로에는 검사가 없다 | `ros2_ws/src/*/launch/` 검색 0 · `CMakeLists.txt` 47 행 설치 목록에만 |
| 기록의 TODO | 10-29 §2 '`TODO(improve)`: 문턱은 5 주행 한 사무실 자료 — 사람이 많을 때 점수 하한 다시 볼 것' 은 **코드에 없다**(파일의 `TODO(improve)` 는 218 행 통로 방향 ±45° 하나) — §6 ④ | grep |
| 드리프트 원천 쪽 | 컨디셔너 ZUPT 문턱 그대로(`conditioner_core.hpp` 32~37 행: 휠 `|vx|` · `|wz|` < 0.005, 창 400 개 = 2 s, σ < 0.010, α 0.10, 한 번 ±0.0005 rad/s). EKF yaw 입력 = 휠 vyaw + 자이로(`ekf.yaml`) | 저장소 |
| SLAM 정지 중 처리 | 위치 추정 모드 0.30 m · 0.15 rad(`slam.launch.py` 75~77 행) — §3 의 어긋남 | 저장소 |

## 5. 내 실수
- [10-28 §16.2](../debug_log/2026-10-28/SUMMARY.md): 범위가 다른 두 격자(±0.5 m vs ±1.2 m)를 비교해 정적 벽을 '새로 생긴 칸' 으로 봄. 다음에 알아보는 법: 같은 창 크기 · 치명 칸은 먼저 정적 지도와 겹쳐 나눔 · 정지 중 생긴 치명이면 TF yaw 이력과 스캔-지도 맞춤부터.
- (카드 작성 중) 10-28 §16.1 의 미확인 ① 에 'cuVSLAM 속도' 를 원천 후보로 올렸으나, EKF 설정상 cuVSLAM 은 yaw 축에 들어가지 않는다 — 후보를 적기 전에 그 입력이 그 상태 변수에 융합되는지(`*_config`) 먼저 본다(§3).
- (카드 작성 중) SLAM 기전 '최소 이동 조건' 을 지금 위치 추정 문턱(0.15 rad)과 대조하지 않고 적었다 — 16.6° 면 문턱을 넘는다(§3). 다음에 알아보는 법: '처리 안 함' 을 기전으로 쓸 때 그 순간의 odom 변화량을 처리 문턱과 나란히 적는다.

## 6. 기록 어긋남 (원문 대조, 카드 작성 중)
| # | 기록 | 원문 · 코드 | 처리 |
|---|---|---|---|
| ① | 10-28 §16.1 · 10-29 §2 'SLAM 은 로버가 움직이지 않으면 스캔을 처리하지 않아' (기전 = 최소 이동 조건 추정) | 포크는 odom 회전 0.12 rad 이상이면 처리(§3). f2pl5 뒤 16.6° 에 map→odom 불변 | 이 카드 §3 에 '어긋남 — 미확인' 행 |
| ② | 10-28 §16.1 미확인 ① '카메라 IMU 자이로 잔여 바이어스인지 cuVSLAM 속도인지' | `ekf.launch.py` 30~31 행 cuVSLAM = vx · vy 만 | §3 '약화' |
| ③ | 10-29 §2 'f2pl1 … 출발 37 s 뒤 −1.5°' | [`scan_align/f2pl1.txt`](../debug_log/2026-10-29/outputs/scan_align/f2pl1.txt): 정지 마지막 판 t 741.0 db −6.5° → 움직인 첫 판 t 743.0(v 0.055) db **+0.5°** → 747.2 −1.5°. 37 s 는 bag 시작(712.3)부터 잰 값에 가깝다(747.2 − 712.3 = 34.9 s) | 결론('움직이자 SLAM 이 고쳤다')은 같고 더 빠르다(≤ 2 s) |
| ④ | 10-29 §2 '`TODO(improve)`: 문턱은 5 주행 한 사무실 자료 …' | `place_server.py` 에 해당 TODO 없음 | CLAUDE.md '임시방편 코드는 `// TODO(improve):`' 와 어긋남 — 배포 때 코드에 넣을 것(남은 것) |
| ⑤ | 10-29 §3 'ZUPT … 바이어스 y −0.00070~−0.00077 rad/s 를 오감' | `zupt_d1.txt` 94 줄의 갱신 뒤 값 범위 **−0.000577 ~ −0.000781**(앞 24 줄이 −0.00058~−0.00066) | 결론 무관(뒤 70 줄은 −0.00066~−0.00078) |
| ⑥ | 10-28 TOOLS 42 행 'f2pl5 bag 끝 TF = 인라인 rosbags' | 스크립트 파일 없음 · 출력 [`odom_yaw_end_f2pl5.txt`](../debug_log/2026-10-28/outputs/odom_yaw_end_f2pl5.txt) 는 CP949 로 저장(다른 출력은 UTF-8) · '끝 8 s ω 10.95 °/min' 줄은 SUMMARY 에 안 쓰임 | 원문 없음 표시 · §2.1 (가) |

## 7. 남은 것
- d2(주행 뒤 정지) — 선언 [10-29 §4](../debug_log/2026-10-29/SUMMARY.md). 판정 표(주행 ①② · 정지 ①②③ · ⓐ 거절)는 그대로 유효. 추가로 볼 것(이 카드 §3): 정지 중 slam.log 처리 · 정합 줄, odom yaw 가 6.9° 를 넘는 시각과 map→odom 변화.
- 검사 ⓐ 배포 · 실동작(정상 상태 수락, 틀린 상태 거절). 배포 때 §6 ④ 의 TODO 를 코드에 넣고, Jetson src 비교 목록(11-04 `chk_src_md5_1104.sh`)에 `place_server.py` 를 더한다.
- 드리프트 율이 0.04~0.39 °/min 로 들쭉날쭉한 이유.
- 원인 쪽 대책 ⓑ(정지 판정 중 yaw 고정) · ⓒ(출발 전 소회전) 결정.
- 표준 순회 러너 경로에는 ⓐ 같은 출발 전 방향 검사가 없다 — prep 의 PREP_POSE 는 기동 직후 한 번(8 기 [운용 카드](drive-ops-1019-1023.md)).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2pl1 · f2pl4 · f2pl5 | 주행 뒤 정지에서 드리프트가 보인 주행 | 10-28 §8 · §11 · §14.1, 재분석 10-29 §2 |
| f2pl2 · f2tt2 | 맞던 상태 분포에 들어간 주행(출발 직전 −1.0° · 0~+0.5°) | 10-28 §9 · §4, `2026-10-29/outputs/scan_align/` |
| d1 | prep 뒤 30 분 정지 | 10-29 §3 |
| d2 · d2s | 주행 뒤 40 분 정지 + ⓐ dry_run(미실행) | 10-29 §4 · `jobs/run_d2_1029.sh` |
| `chk_scan_align.py` | 실시간 라이다↔지도 yaw 맞춤 | `2026-10-28/jobs/` |
| `anal_scan_align_bag.py` · `anal_scan_align_sum.py` | bag 판마다 맞춤 · 분포 | `2026-10-29/jobs/` |
| `chk_yaw_drift.py` · `anal_drift_bag.py` | 원천별 yaw rate(실시간 · bag) | `2026-10-29/jobs/` |
| `chk_drift_rec_1029.sh` · `up_drift_rec_1029.sh` · `up_fetch_drift.sh` | 정지 기록 · 전송 · 회수 | `2026-10-29/jobs/` |
| `chk_day_start_1029.sh` | 하루 시작 점검(재부팅 발견) | `2026-10-29/jobs/` |
| `chk_costmap_dump.py` · `fig_gcm_reach.py` · `anal_gcm_vs_static.py` | 닿는 영역 · 정적 대조 | `2026-10-28/jobs/` |
| (인라인 rosbags) | f2pl5 bag 끝 TF | 원문 없음 → `2026-10-28/outputs/odom_yaw_end_f2pl5.txt` |

## 9. 도구 해설
### 9.1 `chk_scan_align.py` (10-28 §16.1, Jetson, 로버 안 움직임)
- 부른 형태: 인자 없음. 왜: 출구를 막은 'N' 칸이 정적 벽을 돌린 모양이라 '로버 방향 추정이 틀렸나' 를 직접 재려고.
- 하는 일: `/scan`(센서 QoS) · `/map`(transient local) 한 판씩 + TF `map→라이다` · `map→odom` · `odom→base_link` 를 최대 20 s 기다려 받음 → 정적 점유(≥ 65)를 1 칸 팽창 → 라이다 점(range_min ~ min(range_max, 6 m))을 지금 TF 로 map 에 놓고 −40 ~ +40° 를 0.5° 간격으로 더 돌려 가며 '팽창 점유 칸 안 점 비율' 을 점수로 → 지금(0°) 점수와 상위 5 각.
- 출력: 화면 — `map→odom` · `odom→base_link` 한 줄씩 · '라이다 점 N · 지금 TF(0°) 점수' · 상위 5 각. 남은 곳 `2026-10-28/outputs/scan_align_1615.txt`, 10-29 §2 실시간 값(0.925 · +0.5°)은 대화 기록뿐(**원문 없음**).
- 판정 문턱: 코드에 없음(사람이 읽음). 결함: 회전만 훑고 위치는 고정 · 점수는 점 비율이라 잡동사니 · 대칭 구조에서 거짓 최적 가능 · 정적 지도에 없는 물체(사람 · 상자)는 점수를 깎는다.
- 계보 → `anal_scan_align_bag.py`(bag 판마다, ±30°) → `place_server.loc_align`(같은 정의, ±30°). 지금 다시 쓸 수 있음.

### 9.2 `anal_scan_align_bag.py` · `anal_scan_align_sum.py` (10-29 §2, PC)
- 부른 형태: `anal_scan_align_bag.py 이름 bag폴더 [STEP=2.0] > outputs/scan_align/이름.txt`(입력 = `2026-10-28/bags/bag_*.tgz` 를 푼 폴더), 이어 저장소 루트에서 `python anal_scan_align_sum.py`(→ `summary.txt`, 상대 경로 `outputs/scan_align/*.txt` 를 읽으므로 그날 폴더에서 실행).
- 왜: ⓐ 문턱을 '맞던 상태' 분포로 정하려고, 그리고 f2pl1 · f2pl4 출발 직전이 틀렸는지 확인하려고.
- 하는 일: bag 의 `/tf` 에서 map→odom · odom→base_link, `/tf_static` 에서 라이다 사슬, `/map` 첫 판(위치 추정 모드라 안 바뀜). `/scan` 을 STEP 초마다 한 판 → 그 시각의 마지막 TF 로 map ← 라이다 행렬 → ±30° · 0.5° 점수(§2.1 (나)). 속도 v = 1 s 전 base_link 와의 거리(정지 판정 v < 0.02 m/s 는 sum 쪽).
- 출력: 판마다 `이름 t x y yaw v s0 sb db`. sum: 전체 · 정지 · 주행별 s0 최소 · 5 % · 중앙, |db| 중앙 · 95 % · 최대, sb − s0 95 % · 최대, 낮은 s0 8 판 · 큰 |db| 8 판.
- 결함: map→odom 은 같은 stamp 두 번 발행(CLAUDE.md §6) 중 '그 시각 이전 마지막 수신값' 을 써서 보정 순간 판 하나는 옛 값일 수 있다 · 정지 판정이 1 s 거리라 제자리 회전은 '정지' 로 셈 · `.err` 파일 5 개는 비어 있음.
- 결과가 쓰인 곳: ⓐ 문턱(0.40 · 4° · 0.03), f2pl1 7° 판정. 지금 다시 쓸 수 있음(d2 bag 에도).

### 9.3 `chk_yaw_drift.py` (10-29 §2, Jetson, 로버 안 움직임)
- 부른 형태: `chk_yaw_drift.py [창 s=60]`. 왜: d1 기록이 도는 동안 원천별로 지금 율을 바로 보려고.
- 하는 일: `/camera/camera/imu`(원시, 광학 −y) · `/imu/data`(조건, 광학 −y, best effort) · `/wheel_odom/conditioned` wz · `/vslam/odom` wz · vx · `/odometry/filtered` wz · vx 구독 → 3 s 버리고 창 동안 모음, 창 처음 · 끝에 TF odom→base_link · map→odom yaw → 변화(°, atan2 로 감기 처리) · °/min, 원천마다 개수 · 평균(rad/s · °/min) · 표준편차.
- 출력: 화면만 — 10-29 §2 표가 대화 기록에서 옮긴 것(**원문 파일 없음**, 표가 전부).
- 결함: TF 처음 · 끝 두 점 · 1 분 창이라 0.02 °/min 은 잡음 수준과 구별이 약함(09-15 job321 과 같은 한계, 창이 2 배 길 뿐).
- 계보: 09-15 `job321_drift.py` → 이것(원천별) → `anal_drift_bag.py`(bag, 구간별 적분).

### 9.4 `chk_drift_rec_1029.sh` · `up_drift_rec_1029.sh` · `up_fetch_drift.sh` (10-29 §1 · §3)
- `up_drift_rec_1029.sh 이름 길이s`(PC · WSL): Jetson 에 기록 스크립트를 CR 빼고 올린 뒤 `run_jn.sh` 로 `chk_drift_rec_1029.sh 이름 길이` 실행(`JX_WHY` = '정지 기록 … (로버 안 움직임)'). 비밀번호는 러너 파일에서 읽고 출력하지 않음.
- `chk_drift_rec_1029.sh`(Jetson): `setsid nohup` 으로 자기 자신을 독립 실행(PC 연결이 끊겨도 길이만큼 기록) → `/tf` best effort QoS 재정의 파일 → 부팅 캘리브 줄 출력 → `ros2 bag record /tf /tf_static /map /scan /odometry/filtered /wheel_odom /wheel_odom/conditioned /imu/data /camera/camera/imu /vslam/odom /cmd_vel` → 길이만큼 sleep → SIGINT → sensors · slam 로그 사본 · ZUPT 줄 수. 출력 `/tmp/drift_<이름>.log` → [`drift_d1.log`](../debug_log/2026-10-29/outputs/drift_d1.log)('bag 699M · ZUPT 줄 94').
- `up_fetch_drift.sh 이름`(PC · WSL): Jetson 에서 tgz 로 묶어 스크래치패드 `drift_<이름>/` 로 가져와 풂 → 저장소 `bags/bag_d1.tgz`(git 제외) · `outputs/sensors_d1.log` · `slam_d1.log`.
- 결함: 세 스크립트 모두 스크래치패드 절대 경로 · Jetson IP 고정. 기록이 `/tmp` 라 재부팅 전에 회수해야 함(10-29 §0 의 교훈).

### 9.5 `anal_drift_bag.py` (10-29 §3, PC) ★ 원천 가르기
- 부른 형태: `anal_drift_bag.py bag폴더 [BIN=300]`. 왜: §1 판정 ①~④ 를 숫자로.
- 하는 일(§2.1 (다) 발췌): TF 두 개의 yaw 를 `np.unwrap` 해 구간 처음 · 끝 차, 각속도 네 원천을 표본 간격(최대 0.2 s)으로 적분, '원시 평균 − 조건 평균' = 그 구간에 컨디셔너가 뺀 바이어스. 끝에 판정 문장(① ≥ 3° 재현 · < 1° 안 됨, ② 비율은 |EKF Δ| > 0.05° 일 때만, ④ < 0.5° = 안 고침).
- 출력: [`anal_drift_d1.txt`](../debug_log/2026-10-29/outputs/anal_drift_d1.txt).
- 결함: 시작 · 끝을 `ob` · `imu` 의 겹침으로만 잡음(휠 · EKF 가 늦게 시작해도 모름) · ③(ZUPT 이력)은 로그 grep 으로 따로. 지금 다시: d2 bag 에 그대로 쓸 수 있음.

### 9.6 `chk_costmap_dump.py` · `fig_gcm_reach.py` · `anal_gcm_vs_static.py` (10-28 §16.1)
- `chk_costmap_dump.py`(Jetson): `/global_costmap/costmap` · `/map`(transient local) 한 판 + `map→base_link` → `/tmp/gcm_dump.npz`(격자 · 원점 · 해상도 · 로버 자세).
- `fig_gcm_reach.py npz 출력.png [이름:x:y …]`(PC): 로버 칸에서 값 ≤ 98(미지 −1 포함)인 칸을 4 방향 넓이 우선으로 칠함(NavFn 이 99 · 100 을 못 지난다고 보는 근사) → 닿는 칸 넓이 · 장소마다 '닿음' 여부 · 그림(연초록 닿음 · 빨강 100 · 주황 99 · 정적 점유 검은 점). 출력 `gcm_reach_1610.png` · `.txt`(1.3 m²).
- `anal_gcm_vs_static.py npz x0 x1 y0 y1`(PC): 창 안 칸을 문자로(§1 발췌) — 치명을 정적 점유와 겹쳐 `#` · `N` 으로 나누고 N 개수.
- 결함: 넓이 우선은 차체 크기 · 방향을 안 봄(내접 99 를 벽으로만 봄) — '닿음' 은 근사. 다시 쓸 수 있음(10-28 §16.2 의 교훈: 같은 창 크기로).

### 9.7 `run_d2_1029.sh` (10-29 §4, 미실행)
- 내용: `up_place_s1_1028.sh d2 w3`(10-28 S1 러너 — where · go_to W3 · return, 새 place_server 배포 포함) → `up_drift_rec_1029.sh d2s 2400`. 로버는 앞 단계에서만 움직임. 두 하위 스크립트가 스크래치패드에 있어야 함 — 10-22 처럼 스크래치패드가 지워졌으면 저장소 사본(`2026-10-28/jobs/up_place_s1_1028.sh` 등)에서 복구 필요(이 카드에서 실행 가능 여부 확인 안 함).

## 10. 용어
- **odom yaw 드리프트**: EKF(odom→base_link)의 방향이 로버가 서 있는데도 천천히 변하는 것. 전역(map) 방향 = map→odom + odom→base_link 이므로, SLAM 이 map→odom 을 고치지 않으면 그대로 전역 방향 오차가 된다.
- **ZUPT(정지 중 바이어스 재추정)**: 휠이 정지를 보고하는 2 s 동안 원시 자이로 평균을 '0 이어야 할 값' 으로 보고 바이어스를 조금씩(α 0.10, 한 번 ±0.0005 rad/s) 그쪽으로 옮김. 흔들림 σ ≥ 0.010 rad/s 면 그 창은 버림. 상세는 [센서 컨디셔너 카드](sensor-conditioner.md).
- **잔차 yaw rate(ZUPT 로그)**: 갱신 직후 '관측 평균 − 새 바이어스' 의 로봇 yaw 성분(광학 −y). 0 근처면 그 창 동안 바이어스가 맞았다는 뜻.
- **광학 −y**: 카메라 IMU 는 광학 좌표(x 오른쪽 · y 아래 · z 앞)라 로봇 yaw 축(위) = −y. 도구들이 `-m.angular_velocity.y` 를 쓰는 이유.
- **라이다 ↔ 정적 지도 맞춤 점수(s0 · sb · db)**: 라이다 점 중 저장 지도의 점유 칸(1 칸 팽창) 안에 드는 비율. s0 = 지금 TF 그대로, sb = ±30° 를 훑은 최고, db = 그 각. db 가 크고 sb 가 s0 보다 확실히 크면 방향 추정이 db 만큼 틀린 것.
- **위치 추정 모드 처리 문턱**: slam_toolbox 가 새 스캔을 정합에 쓰는 조건 — odom 기준 이동이 0.8 × 0.30 m 이상 또는 회전이 0.8 × 0.15 rad(포크) 이상. 처리하지 않으면 map→odom 은 마지막 값 그대로 발행된다.
- **증상 차단 vs 원인 대책**: ⓐ 는 원인을 몰라도 '틀린 상태로 출발' 만 막는다(고치지 않음). ⓑ · ⓒ 는 원인 쪽.
- **dry_run(place_server)**: 목표를 Nav2 에 보내지 않고 검사 · 응답까지만 하는 모드 — 로버가 움직이지 않는다.
