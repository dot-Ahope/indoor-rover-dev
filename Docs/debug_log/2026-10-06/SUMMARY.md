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
