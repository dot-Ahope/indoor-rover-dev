# 2026-10-06 — rf2o R3: 게이트 정식 노드·ekf.launch 인자

전날 기록: `Docs/debug_log/2026-10-02/SUMMARY.md` §13~§19(rf2o R0~R2, 다음 시험 설계 §17).

## §1 R3 코드 (사용자: 1 번 진행)
- `rover_bringup/scripts/rf2o_gate.py`(R2 원형 `r2_gate.py` 정식화): 방향 보정 R(π−0.04677), G1 자이로 일치(0.1 s 평균·바닥 0.12), G2 정지 검사, σ 회전 0.03 / 직진 vx 0.10·vy 0.03 → `/odom_rf2o/gated`. 그림자 EKF 용 휠 중계 `/wheel_odom/plain`(relay_plain). TODO(improve): 200 Hz 자이로를 Python 으로 받음.
- `rover_bringup/config/rf2o.yaml`(rf2o 노드, publish_tf false, init_pose_from_topic "" — 명령줄로 빈 문자열을 못 넘겨 파일로).
- `rover_bringup/launch/ekf.launch.py` 인자: `rf2o:=true|false`(**기본 false — 지금 구성 그대로**) → rf2o·게이트 노드 + EKF odom1 + 컨디셔너 B3(rot_cov) 켬·순수 회전 중 휠 병진 σ 0.3. `shadow:=true` → 그림자 EKF A(`/odometry/ekf_a`, TF 없음, rf2o 이전 구성)를 같이 — 단계별 실측(10-02 §17)에서 A·B 동시 비교용. `use_sim_time`·`gate_csv` 인자. conditioner:=py 와 rf2o 동시 사용은 거부(B3 가 C++ 판에만).
- prep `job240_clean.sh`: `~/rf2o_ws` 있으면 source, 정리 목록에 rf2o_laser_odometry·rf2o_gate.py·ekf_shadow_a. 설치: CMakeLists `install(PROGRAMS … rf2o_gate.py)`.

## §2 R3 재생 검증 — 정식 launch 가 R2 오프라인 결과를 재현하나 (도메인 42, 로버 안 움직임)
- 방법(`jobs/r3_replay.sh`·`r3_rec.py`·`r3_eval.py`): `ekf.launch.py rf2o:=true shadow:=true use_sim_time:=true` 를 띄우고 bag 의 /scan·/tf_static·/imu/data·/wheel_odom 재생. 컨디셔너는 원시 IMU 가 없어 /imu/data 를 내지 않고(bag 것 사용) 휠 B3 공분산만 냄. 지도·SLAM 기준은 bag 기록값.
- **회전 시험 bag(rot2·rot3)은 Jetson 재부팅으로 /tmp 와 함께 소실**(PC 로 옮겨 두지 않은 내 실수) → 줄자 대조(R2-a) 재현은 다음 실측 시험(10-02 §17)에서. 앞으로 시험 bag 은 끝나는 즉시 PC 로 회수.
- 첫 시도 무효: WSL 에서 F: 경로가 안 보여 배포 파일이 안 올라감(전에도 겪음) → scratchpad 경유로 다시.
- 결과(`outputs/r3_eval.txt`, `j850_r3_replay.txt`):
| | R2 5 차(오프라인 원형) | **R3 정식 launch** |
|---|---|---|
| f2b4 직진 축척 B/SLAM (A) | 0.998 (1.000) | **0.998** (0.999) |
| f2b3 구석 벽 안쪽 면 범위 A / B / SLAM | 0.198 / 0.099 / 0.084 m | 0.196 / **0.096** / 0.084 m |
| f2b3 기동 뒤 남은 차 A−SLAM / B−SLAM | −15.2 / −4.9 cm | −15.1 / **−4.7 cm** |
| 게이트 판정(f2b3) | — | 통과 1290 · G1 1 · G2 2 |
- 판단: 정식 노드·launch 가 오프라인 원형과 **같은 결과**(차 0.2~0.3 cm). 그림자 EKF A 도 라이브 기록과 일치.
- 확인할 것: 게이트 CPU 누적 85 s / f2b3 재생 297 s ≈ **코어 하나의 29 %**(Python 200 Hz 자이로 + csv 기록 포함, 재생 100 Hz 클록 부담도 섞임) — 라이브에서 csv 끄고 다시 잼, 크면 C++ 이식(TODO(improve)).
- 다음: prep(`SENSORS_ARGS="rf2o:=true shadow:=true"`) → 정지 기동 확인(게이트 통과율·EKF·CPU) → 90° 단계별 실측 시험(10-02 §17).

## §3 R3 정지 기동 확인 (사용자: 로버를 출발 테이프 **45 cm 앞**에 둠 — 후방 공간 확보) — `outputs/j851_r3prep.txt`
- prep(`EXTRA_SENSORS="rf2o:=true shadow:=true"`, `jobs/job852_prep_rf2o.sh`): 시작 map (+0.444, −0.008, −0.9°) — 사용자가 놓은 자리와 일치, 흔들림 0. 배터리 12.12 V.
- 발행: /odom_rf2o 10.0 · /odom_rf2o/gated 10.0 · EKF B 30.0 · 그림자 EKF A 29.1 · /wheel_odom/plain 25.1 Hz. B3 켜짐(rot_vx_var 0.09), EKF odom1 = /odom_rf2o/gated. 게이트 통과 1957 · G1 3 · G2 7(정지).
- CPU(10 s): rf2o 4 % · **게이트 39 %**(csv 끔 — Python 200 Hz 자이로 구독 부담 추정) · 그림자 EKF A 11 %. load 10~12(기동 직후). 대책 후보: 자이로 대신 EKF 회전 속도(30 Hz, B 의 회전은 자이로만이라 같은 값)로 — 단계별 시험 뒤.

## §4 단계별 회전 실측 — 선언(10-02 §17 사용자 제안)
- 방법(`jobs/step_rot.py`): 한 번 = 제자리 90°(ω 0.38, 외곽 0.08 m 안이면 중단) → 정지 → 네 추정(EKF B·그림자 EKF A·rf2o 중심 환산·SLAM)으로 **오른쪽 앞끝(+0.262, −0.165)** 의 시작 대비 위치·예측 대각 거리 → 사용자 줄자(시작 표시 ↔ 오른쪽 앞끝). 순서 +90, −90 × 3 = 6 단계. bag `/tmp/bag_step1`(/imu/data 포함, 끝나면 즉시 PC 회수).
- 판정: 단계별 |예측 − 줄자| — **EKF B 평균 ≤ 3 cm, 단계가 지나도 쌓이지 않음(6 단계 ≤ 5 cm)**. A·SLAM·rf2o 는 기록(A 는 쌓일 것으로 예상). 방향이 원위치인 짝수 단계는 순수 미끄러짐만 남음.

### §4.1 결과 — **EKF B 통과**: 줄자 대비 |오차| 평균 1.5 cm, 방향 원위치 단계(2·4·6)는 0.0 / +0.1 / +0.7 cm
- `outputs/step_tape.csv`(사용자 줄자), `outputs/step_state_1.json`(단계별 네 추정 자세), 그림 `Docs/04_navigation/figures/2026-10-06_step_rot1.png`(`jobs/render_step1.py`), bag `bags/bag_step1.tgz`(PC 회수 완료, git 제외).
| 단계 | 방향 | 줄자 | EKF B | EKF A(지금) | SLAM |
|---|---|---|---|---|---|
| 1 | +90 | 44.8 | 41.9 (−2.9) | 45.1 (+0.3) | 45.6 (+0.8) |
| 2 | −90 (원위치) | 10.8 뒤·오른 | **10.8 (0.0)** | 0.8 (−10.0) | 6.0 (−4.8) |
| 3 | +90 | 43.3 | 40.5 (−2.8) | 45.4 (+2.1) | 43.3 (0.0) |
| 4 | −90 (원위치) | 16.1 뒤·오른 | **16.2 (+0.1)** | 0.6 (−15.5) | 14.9 (−1.2) |
| 5 | +90 | 43.5 | 41.2 (−2.3) | 45.4 (+1.9) | 45.3 (+1.8) |
| 6 | −90 (원위치) | 17.6 | **18.3 (+0.7)** | 0.6 (−17.0) | 11.4 (−6.2) |
| \|오차\| 평균 | | | **1.5** | 7.8 | 2.5 |
- 판정(§4 선언): EKF B 평균 ≤ 3 cm **통과(1.5)**, 6 단계 ≤ 5 cm **통과(0.7)**, 쌓이지 않음 ✔. 방향(뒤·오른쪽)도 사용자 관찰과 일치(B 단계 2 (−0.088, −0.063)).
- A 는 미끄러짐을 거의 0 으로 봐 원위치 단계 오차가 10 → 15.5 → 17 cm 로 쌓임(예상대로). SLAM 은 맞을 때도 있으나(단계 3·4) 6 cm 까지 틀림 — 회전 중 SLAM 은 기준으로 부족(10-02 §19 주의와 같음).
- 관찰: B 는 **+90° 단계(1·3·5)마다 −2.3~−2.9 cm** 로 같은 쪽 치우침, 원위치 단계엔 0~0.7. 이 단계는 회전 중간이라 모서리 위치가 각도에 민감(1° = 모서리 약 0.5 cm)하고, EKF 각도는 +93~94° 로 나옴(지령 90° 판정은 EKF 각 기준) — 줄자 측정점(모서리) 잡기 차이도 있을 수 있음. 원인 미분리, 판정엔 영향 없음.
- rf2o 단독 누적 자세는 단계 3 부터 각도 59°(실제 94°) 등으로 무너져 비교에서 뺌 — EKF B 는 rf2o **속도만** 쓰고 각도는 자이로라 영향 없음. 원인(초기 자세·각도 누적)은 bag 으로 따로.
- 진행 중 사고: 스크립트 오류 2 회(DDS 발견 지연, 유효 점 없는 스캔) — 둘 다 회전 전 멈춤, 고쳐 재실행. Wi-Fi 일시 끊김 2 회(단계 4·6 명령 미전달, 로버 안 움직임 확인 뒤 재실행).
- 다음: 게이트 CPU 39 % 줄이기(자이로 대신 EKF 회전 속도) → 사람 시험 T1~T3 → rf2o 기본값 켜기 결정 → 피벗 회전 시험.
