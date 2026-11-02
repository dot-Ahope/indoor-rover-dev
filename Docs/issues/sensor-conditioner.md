# 센서 컨디셔너 sensor_conditioner — 무엇을 하고, 왜 뺄 수 없나 (역할 카드: 08-26 시작 · 09-23 역할 점검)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **작동(필수 구성)** — 09-23 §15 사용자 질의 '빼도 되는가' 에 '그냥 빼면 안 된다' 로 답함(근거 3 개, 수치는 출력 원문 없이 SUMMARY 문장뿐). 같은 날 사용자 결정: IMU 200 Hz 유지 · 로직만 C++ 로. 09-28 대체 패키지 안 씀(사용자) · C++ 이식(첫 누락 전 비트 동일, CPU 42.2 → 7.1 %) · B2/B3 추가 | 08-26 ~ (이 카드는 기원 요약 + 09-23 + 09-28 §10 · §11 을 채움) | [08-26 '판단 · 결정' 4](../debug_log/2026-08-26/SUMMARY.md) "펌웨어 covariance=0 → Jetson 측 컨디셔너로 보완" | 지금 코드: [`scripts/sensor_conditioner.py`](../../ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py)(Python 판, `conditioner:=py` 로만) · [`src/sensor_conditioner.cpp`](../../ros2_ws/src/rover_bringup/src/sensor_conditioner.cpp) + [`include/rover_bringup/conditioner_core.hpp`](../../ros2_ws/src/rover_bringup/include/rover_bringup/conditioner_core.hpp)(C++ 판, 기본) · [`launch/ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py) · [`config/ekf.yaml`](../../ros2_ws/src/rover_bringup/config/ekf.yaml). 09-23 에는 파일 변경 없음 | [자이로 소스: 보드 IMU → D455f](gyro-source-d455f.md) · [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md)(`VX_SCALE` · `SLIP_PTS` 의 역사) · ['후진하고 멈췄다' — CPU](cpu-load-stalls.md)(컨디셔너가 최대 CPU 소비원) · [Foxglove 4 초 스냅](foxglove-snap-cpu.md)(08-29 '큰 python3 = 컨디셔너') · [제자리 회전 중 옆 밀림](f0-rotation-side-slip.md)(고정 공분산 → 가변 σ 결정) · [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md) · [rf2o 게이트 · 사람 시험](rf2o-gates-people.md) · [회전 방식 · 트랙 비율](rotation-method-track-ratio.md) (6 기) |

**한 줄**: EKF(robot_localization)에 들어가는 두 입력 — 카메라 IMU 200 Hz 와 보드 휠 오도 25 Hz — 는 둘 다 이 노드를 거친다. 하는 일은 ① 자이로 **바이어스 제거**(부팅 10 s 정지 평균 + 휠이 정지를 보고하는 동안 천천히 다시 재는 **ZUPT**) ② 펌웨어가 0 으로 보내는 **공분산 채우기**(robot_localization 은 0 을 '완벽한 측정' 으로 다룸) ③ (지금은 1.0 이라 무동작인) 휠 스케일 · 회전 슬립 계수. 09-23 사용자가 '빼도 되나' 를 물었고, 나는 **안 된다**고 답했다 — 바이어스 · ZUPT 가 없으면 정지 중 yaw 가 분당 수 도 새고(09-10: 80 분 정지에 ≈ 105°), 휠 공분산 0 이 그대로 EKF 로 가며, 원본 자이로 공분산 0.01 은 휠 yaw 와 같은 믿음이라 '자이로를 25 배 믿는' 구성이 사라진다. 대신 Python 판의 CPU(41.8 %)를 줄이려 **C++ 로 같은 로직을 옮기자**고 제안했고, 사용자는 '200 Hz 그대로(다운샘플 금지)' 를 조건으로 붙였다.

> 읽는 법: 09-23 §15 의 수치(바이어스 −0.00073 → −0.00106 rad/s, ZUPT 잔차 0.00003, 원본 공분산 0.01, 휠 공분산 전부 0, CPU 41.8 %)는 `job549_cond.sh` 를 돌린 결과지만 **출력 원문이 저장되지 않았다**(`outputs/` 에 j549 없음) — SUMMARY 문장이 유일한 출처. 아래 §0 알고리즘은 **지금(10-30) 저장소 코드** 기준이다.

## 0. 하는 일 — 지금 코드 기준
입력 · 출력(두 판 같음, QoS = SensorData: best effort · depth 5):
| 방향 | 토픽 | 비고 |
|---|---|---|
| 입력 | `/imu/data_raw` → launch 에서 **`/camera/camera/imu`** 로 remap | D455f 내장 IMU, `unite_imu_method 1` 이라 자이로 속도 200 Hz. 보드 `/imu/data_raw`(ICM-20948)는 자이로 무반응이라 안 씀 |
| 입력 | `/wheel_odom` | 보드 micro-ROS, 25 Hz, **공분산 전부 0**(펌웨어 `microros_task.c` 287 행 '0 그대로' — 지금 코드 확인) |
| 출력 | `/imu/data` | EKF `imu0` — 쓰는 것은 `imu0_config` 인덱스 10(광학 프레임 −y = 로봇 yaw rate) 하나 |
| 출력 | `/wheel_odom/conditioned` | EKF `odom0` — vx · vy · vyaw |

**IMU 경로(200 Hz, 콜백마다)**
1. **부팅 캘리브레이션**: 처음 2,000 개(200 Hz × 10 s) 원시 자이로(x, y, z)를 모아 축별 평균 · 모표준편차. 세 축 중 최대 σ < **0.015 rad/s** 면 평균을 바이어스로(`gyro bias calibrated: …` 로그), 아니면 바이어스 0 으로 두고 경고 `startup not stationary`. 끝날 때까지(끝나게 한 표본 포함) **발행하지 않는다** → EKF 는 기동 뒤 ≈ 10 s 동안 IMU 가 없다. 그래서 '자이로 바이어스 10 s 동안 정지 필수' 가 운용 규칙이 됐다(→ [보드 연결](board-link-microros-session.md) 도구 해설).
2. **ZUPT(Zero-velocity UPdaTe)**: 휠 콜백이 `|vx| < 0.005 m/s` **그리고** `|wz| < 0.005 rad/s`(보정 전 원시 휠 값)면 '정지' 플래그. 정지인 동안 원시 자이로를 400 개(2 s) 모아 평균 · σ → 최대 σ ≥ **0.010** 이면 버림('휠은 0 인데 흔들림 = 손으로 옮기는 중') → 아니면 축마다 `step = (관측 평균 − 바이어스) × 0.10` 을 **±0.0005 rad/s 로 자른 뒤** 바이어스에 더함(지수 이동 평균 + 한 번 갱신량 상한). 움직이면 모으던 표본은 버린다. 20 s 마다 `ZUPT #n: bias y … → … (관측 …), 잔차 yaw rate … = … °/분` 로그(잔차 = 로봇 yaw 축 −(관측 − 새 바이어스)).
   - 계산(이 카드): 정지 2 s 마다 차이의 10 % 를 줄이므로 시간 상수 ≈ 20 s, 그러나 한 번 0.0005 rad/s 상한 → 큰 차이는 2 s 당 0.0005 씩(≈ 1.7 °/분 의 바이어스를 지우는 데 최소 2 s × 2 = 4 s 이상).
   - IMU 단독 정지 판정을 쓰지 않는 이유(코드 주석 · 09-28 §10): 느린 고른 회전을 바이어스로 흡수하므로.
3. 바이어스 빼기 → `angular_velocity_covariance` 대각 **0.02² = 0.0004**, `linear_acceleration_covariance` 대각 0.5² = 0.25, `orientation_covariance[0] = −1`(REP-145 '자세 없음' 표식 — EKF 가 자세를 쓰지 않게) → `/imu/data` 발행.
4. (C++ 만) B2 판정용으로 바이어스 뺀 로봇 yaw rate(`gyro_yaw_sign −1 × 축 1`)와 시각을 보관.

**휠 경로(25 Hz)**
1. 정지 플래그 갱신(위 2).
2. `vx *= VX_SCALE`(**1.0**) · `wz *= yaw_slip_factor(|wz|)`(두 점 (0.15, 1.0) · (0.60, 1.0) 선형 보간 = **1.0**). 둘 다 09-07 펌웨어 교정(휠 둘레 0.12533 · 유효 게이지 `WHEEL_BASE_M`) 뒤 무동작 — 펌웨어를 옛 상수로 되돌릴 때만 같이 되돌리는 '한 쌍' 값([휠 오도 스케일 카드](wheel-odom-scale-slip.md)).
3. (C++ 만, 기본 꺼짐) **B2 ICR**: '순수 회전'(휠 `|vx| < 0.02` 그리고 `|ω| > 0.10`, ω 는 0.1 s 안 자이로가 있으면 자이로, 없으면 휠)이면 회전축 p(시계 (−0.029, +0.052) · 반시계 (−0.029, −0.095) m)로 도는 차체의 속도 (ω·py, −ω·px)를 vx · vy 에 더함.
4. 공분산: `twist.covariance[0]` vx **0.02² = 0.0004** · `[7]` vy **0.01² = 0.0001**(차동 구동의 '옆 속도 = 0' 을 측정으로 주장) · `[35]` vyaw **0.1² = 0.01**. (C++ 만) **B3**: 순수 회전이면 vx · vy 분산을 `rot_vx_var` · `rot_vy_var` 로(헤더 기본 0.03², 그러나 launch 가 바꿈 — 아래).
5. 발행.

**지금 기동 구성(코드 확인, 10-30)**: `ekf.launch.py` 기본 `conditioner:=cpp`. `rf2o:=true` 이거나 `vslam:=shadow|on` 이면 **B3 를 자동으로 켜고 σ 0.3**(`rot_vx_var = rot_vy_var = 0.3²`, 39~40 행). prep 기본(`Docs/tools/prep_patrol.sh`, `ODOM=vslam` → `vslam:=on`)이므로 **지금 기본 스택에서 B3 는 켜져 있다**. B2(`icr`)는 기본 꺼짐. ⚠ CLAUDE.md §6 의 '컨디셔너 B2 · B3 는 코드만 있고 기본 끔' 은 `ekf.launch` 의 `rot_cov:=` 인자 기본값 이야기이고, 실제 기본 구성(vslam on)에서는 B3 가 켜진다.

**EKF 에서의 의미**: yaw rate 는 휠 vyaw(분산 0.01)와 자이로(분산 0.0004) 둘이 들어오고, 분산 비 0.01 / 0.0004 = **25** → 자이로를 25 배 믿는다. 09-23 §12.1 n62b 끝 좌회전 헛돎에서 휠은 22.8° 를 보고했지만 EKF 는 8.7°(라이다 8.5°)로 따라간 것이 이 비율 덕분이다([제자리 회전 카드](f0-rotation-side-slip.md) 도구 해설 `job545` · `job546`). 반대로 vy 0.0001 은 '옆으로 1 cm/s 도 안 움직였다' 를 강하게 주장해 회전 중 실제 옆 밀림을 EKF 가 부정하게 만든다(09-23 §20.5) — B3 가 그것을 푸는 장치.

## 1. 증상 · 질문 (09-23 §15)
- 사용자 질의: sensor_conditioner 는 빼도 되는가(정지 CPU 41.8 % — 스택에서 가장 큰 단일 프로세스 중 하나).

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-26 Step 3 | EKF 를 세우며 컨디셔너 신설(covariance 주입 · 자이로 바이어스 캘리브레이션 · 회전 슬립 보정) | 펌웨어 covariance 전부 0. 당시 보드 ICM-20948 정지 자이로 z 바이어스 −0.0072 rad/s → EKF yaw −0.23°/s(Python 머리 주석). 회전 슬립 2 점 0.42 @ 0.20 rad/s · 0.28 @ 0.57 | 'robot_localization 은 0 을 ε 로 치환해 완벽 측정 취급 → 필수'. 펌웨어 수정 금지 규칙이라 Jetson 쪽에서. 주석에 'TODO(production): 펌웨어가 캘리브 + 실측 covariance 를 주면 본 노드 제거' | [08-26 SUMMARY](../debug_log/2026-08-26/SUMMARY.md)(출력 원문 없음 — 그날은 규약 전) |
| 08-27 | 보드 자이로 무반응 → IMU 소스를 D455f 로(EKF `imu0` 인덱스 10 = 광학 −y) | — | 컨디셔너 입력을 `/camera/camera/imu` 로 remap | [자이로 소스 카드](gyro-source-d455f.md) |
| 08-29 · 09-02 | CPU 조사 | 큰 python3 = 컨디셔너 44.1 %(08-29) · 47 %(09-02) | '펌웨어가 대체할 임시 shim · 카메라 IMU 는 Jetson USB 라 펌웨어가 못 맡음' 으로 최적화 안 함 | [Foxglove 카드](foxglove-snap-cpu.md) |
| 09-01 · 09-07 | `VX_SCALE` 0.783 → 1.0, `SLIP_PTS` → 1.0(펌웨어 교정으로 이관) | 직진 0.06 % | 노드의 보정 계수는 무동작으로 | [휠 오도 스케일 카드](wheel-odom-scale-slip.md) |
| 09-09 §8.16 | 자이로 200 → 100 Hz 로 부하 반 시도 | D455 자이로 100 Hz 미지원 → 200 복귀 | '컨디셔너에서 다운샘플하거나 C++ 로'(S6) | [CPU 카드](cpu-load-stalls.md) |
| 09-10 | **ZUPT 추가**(커밋 `ebc5885`) | `job213`(정지 30 s): 원본 광학 wy −0.001126, 시작 캘리브 y −0.00075, 잔차 −0.000376 → EKF yaw rate +0.000380 rad/s = **1.31 °/분**(EKF 드리프트 실측과 같음, 설명 비율 100 %). 그날 80 분 정지 뒤 **약 105°**. ZUPT 뒤 0.02 °/분(65 배) | 부팅 캘리브는 '차가운 카메라' 를 잰다 — 발열로 바이어스 이동. 정지 중엔 SLAM 이 스캔을 처리하지 않아 오차가 map 자세에 쌓임. 기각 대안: 웜업 뒤 캘리브(기동마다 수 분) · EKF 바이어스 상태(robot_localization 미지원) · 휠 vyaw 신뢰 상향(스크럽 산포 7 %) | [09-10 SUMMARY](../debug_log/2026-09-10/SUMMARY.md) 머리 4 · Python 판 주석 · [`2026-09-10/jobs/job213_axis.py`](../debug_log/2026-09-10/jobs/job213_axis.py) |
| 09-21 | Phase S 기준선 | 컨디셔너 ≈ 43 %(python3 108~110 % 의 내역) | — | [CPU 카드](cpu-load-stalls.md) 이후 칸 |
| **09-23 §15** | 역할 점검(`job549_cond.sh`, 12:5x, 정지) | 자이로 yaw 바이어스 부팅 −0.00073 → 지금 **−0.00106 rad/s**(발열 이동) → 보정 없으면 **3.6 °/분**, ZUPT 잔차 ≈ 0.00003 rad/s(**0.1 °/분**). 카메라 원본 자이로 covariance **0.01**, 펌웨어 휠 오도 covariance **전부 0**. CPU **41.8 %** | **그냥 빼면 안 된다**: (a) 정지 중 yaw 분당 수 도(09-10 80 분 105°) (b) 휠 covariance 0 이 EKF 로 (c) 원본 0.01 = 휠 yaw 0.01 과 같은 믿음 → '자이로 25 배' 소실. 불필요한 부분은 vx · slip 계수(1.0)와 orientation covariance(원본이 이미 −1)뿐 | `jobs/job549_cond.sh`(**출력 원문 없음**) · `/tmp/sensors.log`(ZUPT 줄, 원천 소실) |
| 09-23 §15 대체 | 같은 기능의 기성 패키지 | robot_localization 바이어스 추정 미지원, imu_tools 미설치, imu_complementary_filter 정지 바이어스 추정은 후보(미검증) | '설치된 스택에 같은 기능 없음' — **부분 정정**(09-28 §10, §5 실수 1) | 같은 도구의 `ros2 pkg list` 줄 |
| 09-23 §15 제안 | — | — | ① C++ 노드로 이식(파이썬 200 Hz 역직렬화가 비용 대부분으로 **추정**, 기대 41 → 수 % — 미측정) ② 발행 100 Hz 다운샘플 ③ 휠 covariance 는 **펌웨어가 직접 채우면** 이 경로를 없앨 수 있음. 검증 = 정지 10 분 yaw 드리프트 · ZUPT 잔차 · 미끄러짐 재현 시 EKF 추종이 Python 판과 같을 것 | — |
| **09-23 §16** | 사용자 결정 | — | **IMU 발행 200 Hz 유지**('카메라 기본 200 Hz 에 맞춘 균일한 환경이 더 중요') → 제안 ② 삭제. 로직만 이식 | (메모리 'IMU 200 Hz 유지') |
| 09-23 §20.5 | 공분산 점검(Python 11~15 행) | 전부 고정 상수(자이로 σ 0.02 · vx 0.02 · **vy 0.01** · vyaw 0.1), EKF 과정 잡음 기본값 | 휠 vy 가 회전 중 옆 밀림을 적극 부정 → D 도입 때 |ω| 에 따른 **가변 공분산**(수치 근거 없음, 회전 시험으로) | [제자리 회전 카드](f0-rotation-side-slip.md) §20.5 줄 |
| 09-23 §20.6 | 사실 확인 · 순서 | C++ 이식 **미착수**(저장소엔 Python 판뿐) | 순서 2 번 = 이식, '처음부터 가변 공분산을 넣을 수 있는 구조로, 첫 단계는 고정값 그대로 동일성(같은 입력 bag → 두 출력 비교) · CPU' | — |
| 09-28 §7.3 | 순서 재확정(사용자) | — | 이식 = 순서 4(B1 SLAM 포크 · A1 · A2/A3 다음, **B2 피팅 전**). '출력이 같으면 다른 단계에 영향 없음' 이라 A 단계와 독립(§11 머리) | [09-28 SUMMARY](../debug_log/2026-09-28/SUMMARY.md) §7.3 |
| **09-28 §10** | 대체 패키지 기능별 재검토(설치 상태 · 소스 직접 확인) | Python 판 CPU **42 %**(그날 10 s 실측, 누적 평균 41.0 %). realsense2_camera 4.58.3 `angular_velocity_cov` 있음 · `enable_motion_correction` + `rs-imu-calibration` = 정적 보정 · imu_complementary_filter humble 2.1.5(미설치) `do_bias_estimation` 의 정지 판정 = IMU 만 · 휠 공분산 · ICR · 가변 σ 는 대체 없음 | '전체를 대신하는 조합은 없다' 로 09-23 문장 정정(§5 실수 1). **사용자 결정: 대체 패키지 안 씀**, 자체 노드를 C++ 로, 공분산 로직은 한 곳(§7.2). 'CPU 42 % 는 rclpy 200 Hz 수신 · 재발행 비용' 은 **추정**(이식 뒤 측정으로 확인하기로) | 같은 § 표(출력 원문 없음 — 소스 행 번호만) |
| **09-28 §11 구현** | C++ 이식(`conditioner_core.hpp` · `sensor_conditioner.cpp` · `test/test_conditioner_core.cpp` · `ekf.launch.py conditioner:=cpp\|py`) | gtest 5 개, Jetson `colcon test` **6 tests 0 failures**(5 개 + 1 = gtest 실행 파일 단위 결과로 **추정** — 아래 모순 7). 배포는 바뀐 6 파일, CRLF 제거 뒤 md5 로 Jetson 소스 = 저장소 HEAD | — | §0 코드 · 아래 §9 해설 |
| **09-28 §11 V1** | 정지 원시 입력 183 s 녹화(`job595 rec`, `bag_condraw`) → 도메인 42 재생으로 두 판 동시 대조(`job595 ab` → `job594`) 2 회, 그다음 결정적 대조(`job598`) | 재생 대조: IMU 짝 34,407 · 34,412 개, **각속도만** 최대 4.26e-5 · 4.03e-5 rad/s, 그 밖 필드(가속 · 자세 · 세 공분산) 차 0, 휠 4,557 짝 전 필드 차 0. Python 판 수신 34,409 · 34,414(기대 34,585 → **171~176 개 누락**), C++ 34,580(5 개 누락). 각속도 y 가 완전히 같은 짝은 1.2 %뿐 — 첫 차이 전에 Python 쪽에만 빠진 IMU 2 개. 결정적 대조: Python 판을 DDS 없이 콜백 직접 호출(누락 0) → C++ 첫 누락(캘리브 뒤 index 4,969) **이전 4,969 개 100 % 비트 동일(차 0)**, 전체 최대 4.43e-5, 휠 4,557 개 100 % | **논리 동일 — 통과**. 차이의 기전 = ZUPT 창이 '표본 400 개' 로 세어지므로(시간이 아님) 입력 한 개가 빠지면 그 뒤 창 경계가 밀려 평균이 달라짐(코드 `zuptUpdate` 기준 — 이 카드의 해석). 최대 차 4.4e-5 rad/s = 0.15 °/분 | [`j596_cond_v1_static.txt`](../debug_log/2026-09-28/outputs/j596_cond_v1_static.txt) · [`j597_cond_v1_static2.txt`](../debug_log/2026-09-28/outputs/j597_cond_v1_static2.txt) · [`j598_cond_det.txt`](../debug_log/2026-09-28/outputs/j598_cond_det.txt) · bag `/tmp/bag_condraw`(Jetson, **원천 소실** — 09-29 §0 재부팅으로 `/tmp` 지워짐, 로컬 사본 여부 미확인) |
| **09-28 §11 V2** | 라이브 정지 상태에서 Python 판 → C++ 판을 그 자리에서 교체, 각 30 s | 컨디셔너 CPU **42.20 → 7.10 %**, 전체 CPU 합 202 → 166 %, `/imu/data` 196.528 → 199.134 Hz, `/odometry/filtered` 30.232 → 30.001 Hz, EKF 주기 위반 로그 누적 32 → 32. C++ 부팅 캘리브 (−0.00907, −0.00108, −0.00192) rad/s, std (0.0026, 0.0022, 0.0018) | **통과**(83 % 절감, 기대 '수 %' 보다는 큼). 기본을 **cpp** 로(되돌리기 `conditioner:=py`). 수동 `ros2 run` 교체라 프로세스 수 2(래퍼 포함) — 다음 prep 부터 launch 로. V3(주행 중 EKF 거동)는 '입력이 비트 동일이니 같을 것' 으로 **예상**만, 다음 주행 게이트로 확인하기로 | [`j599_cond_v2_cpu.txt`](../debug_log/2026-09-28/outputs/j599_cond_v2_cpu.txt)(도구 원본 없음 — `jobs/` 에 측정 스크립트가 없다) |
| 09-28 §26~§27 | B2 · B3 자리를 `CovariancePolicy`(실제 이름 `wheelTwistCov`) · `icrTwistAdd` 로 채움, 기본 꺼짐 | 꺼져 있으면 출력은 §11 과 같음(더하는 값 0, 분산 고정) | 이 줄기는 별도 카드 | [회전축 치우침 B2 · 회전 구간 분산 B3](icr-b2-b3.md) |

## 3. 가설과 판별 — '빼면 무엇이 깨지나'
| 기능 | 빼면 | 판별 근거 | 판정 |
|---|---|---|---|
| 부팅 바이어스 | 바이어스 −0.00106 rad/s 가 그대로 → 3.6 °/분 | 09-23 실측(원문 없음) · 09-10 job213 | **필요** |
| ZUPT | 발열 이동분(부팅 −0.00073 → −0.00106)이 남음 → 09-10 1.31 °/분 · 80 분 105° | 09-10 실측 · 09-23 잔차 0.1 °/분 | **필요** |
| 휠 twist 공분산 | 펌웨어 0 → robot_localization 이 ε 로 = '완벽' | 08-26 판단 · 09-23 원본 확인 · 지금 펌웨어 287 행 | **필요**(펌웨어가 채우면 대체 가능 — 이후 철회, 아래) |
| 자이로 공분산 0.0004 | 원본 0.01 = 휠 vyaw 0.01 → 1:1 | 09-23 원본 확인 · 09-23 §12.1 n62b(EKF 가 자이로를 따라 맞음) | **필요**(이후 09-28: realsense `angular_velocity_cov` 로는 대체 가능) |
| orientation −1 | 원본도 −1 | 09-23(원문 없음) | 불필요(무해) |
| `VX_SCALE` · `SLIP_PTS` | 1.0 → 무동작 | 코드 | 불필요(펌웨어와 한 쌍으로 보존) |

## 4. 조치와 효과
- 09-23: 변경 없음. 결정 = 200 Hz 유지 · C++ 이식 · 가변 공분산 구조.
- 09-28 §10: 대체 패키지 안 씀(사용자). §11: C++ 판 도입 · 기본 `conditioner:=cpp`. 효과(측정): 컨디셔너 CPU 42.2 → 7.1 %(−35 %p), 스택 정지 합 202 → 166 %, `/imu/data` 누락 0.4~0.5 % → 거의 0(199.1 Hz). 출력은 Python 판과 논리 동일(첫 누락 전 비트 동일).
  - 한계: 비트 동일은 **정지 입력 183 s** 로만 확인 — 휠 정지 · ZUPT 경로는 검증됐지만 '움직이는 휠' 경로(슬립 계수 · 회전 중)는 V1 입력에 없다. 다만 그 경로의 계수가 모두 1.0 이라 곱셈만 남는다(코드). 주행 중 EKF 동등성(V3)은 '예상' 으로 남겼고 이 카드 범위(09-28 ~ 09-29)에서 따로 판정한 기록은 없다 — 다음 날 B2 오프라인 A/B(09-29 §1.1 V0: 꺼짐 재생 EKF = 라이브 EKF 차 중앙값 0.00 cm)가 간접 근거이나 그 재생은 이미 조정된 `/imu/data` 를 입력으로 넣었다([B2 · B3 카드](icr-b2-b3.md) 모순 칸).
  - SLAM 포크(B1)의 회전 중 추가 CPU(40~50 %p, 회전하는 동안만)를 상시 절감 35 %p 가 상당 부분 상쇄(§11 문장 — 두 수치의 측정 조건이 달라 단순 비교는 **추정**).

## 5. 내 실수 · 정정
**실수 1 — '대체 패키지 없음'(09-23 §15 → 09-28 §10 정정)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 컨디셔너를 기성 패키지로 대신할 수 있는지(§15) |
| 본 것 | `ros2 pkg list` 에 imu_complementary_filter · madgwick · imu_tools 없음, robot_localization 은 바이어스 상태 없음 |
| 처음 추론 | 설치된 스택에 같은 기능 없음. complementary_filter 는 '미검증 후보' |
| 의심한 이유 | 09-28 이식 전 기능별로 다시 보다가 — '설치돼 있나' 와 '기능이 맞나' 는 다른 질문 |
| 판별 | 09-28 §10: realsense2_camera 4.58.3 에 `angular_velocity_cov` 존재 확인, complementary_filter humble 2.1.5 소스(`complementary_filter.cpp` 255~271)의 정지 판정이 **IMU 만**(\|a\|−g < 0.1, 샘플 간 Δω < 0.01, \|ω−bias\| < 0.2 rad/s) |
| 결론 | 'IMU 공분산은 드라이버 파라미터로 대체 가능, 바이어스는 정적 보정만, ZUPT 대체안은 0.2 rad/s 미만 고른 회전을 바이어스로 흡수 → 위험'. 전체를 대신하는 조합은 없다는 결론은 유지. 사용자 결정: 대체 패키지 안 씀 |
| 다음에 알아보는 법 | '없다' 를 말하기 전에 기능별(공분산 · 정적 바이어스 · 온라인 바이어스 · 휠 공분산)로 쪼개고, 후보는 **소스의 판정 조건**을 이 로버 운동(느린 회전)과 대조 |
| 데이터 | `Docs/debug_log/2026-09-28/SUMMARY.md` §10 |

**실수 2 — '휠 covariance 는 펌웨어가 직접 채우면 된다'(09-23 §15 → 09-28 §7.2 철회)**: 저비용 이관안으로 냈지만, 같은 날 §20.5 의 가변 공분산(회전 중 σ 를 키움)과 B2 ICR 모델이 들어오면 공분산 로직이 펌웨어 · 컨디셔너로 갈라진다 → 09-28 §7.2 '펌웨어 이관안 철회 — 컨디셔너(C++) 한 곳'. **다음에 알아보는 법**: 같은 날 다른 결정(§20.5)과 충돌하는지 제안끼리 대조한다. 데이터: 09-28 SUMMARY §7.2 표 '§15 "휠 공분산 펌웨어 이관" ↔ B2 · B3'.

**실수 3 — 비교 스크립트가 reliable 로 구독해 best effort 출력을 0 개 받음(09-28 §11)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | V1 재생 대조 — `job594_condab.py` 가 `/py/...` · `/cpp/...` 출력을 받아 짝지음 |
| 본 것 | 첫 실행에서 수신 0 개(SUMMARY 문장. 그 실행의 출력 원문은 없음 — j596 은 고친 뒤) |
| 처음 추론 | (SUMMARY 에 기록 없음) |
| 의심한 이유 | 두 판 다 `SensorDataQoS`(best effort) 로 발행 — reliable 구독은 호환되지 않아 연결 자체가 안 됨 |
| 판별 | 구독 QoS 를 `BEST_EFFORT` depth 200 으로 바꿔 재실행 → 34,409 · 34,580 개 수신(j596) |
| 결론 | 도구 결함(측정 대상 문제 아님). 같은 날 §24 직진 러너(`job618`)의 `/rover/status` 구독도 같은 실수(표본 0 · nan) → [B2 · B3 카드](icr-b2-b3.md) 실수 2. 10-02 §14.1 rf2o 게이트의 `/wheel_odom` reliable 구독(휠 입력 0)도 같은 서명 |
| 다음에 알아보는 법 | 서명 = '수신 0 · 표본 0 · nan' 인데 발행은 살아 있음. 센서 · 컨디셔너 · micro-ROS 토픽은 best effort 가 기본 — 새 구독기는 `qos_profile_sensor_data` 로 시작하고, 0 이 나오면 `ros2 topic info -v` 로 QoS 부터 본다 |
| 데이터 | `Docs/debug_log/2026-09-28/SUMMARY.md` §11 마지막 괄호 · [`job594_condab.py`](../debug_log/2026-09-28/jobs/job594_condab.py) 9~10 행 주석 |

**추정의 검증 — 'CPU 는 rclpy 200 Hz 비용, 기대 41 → 수 %'(§15)**: 09-28 §11 V2 실측 **42.2 → 7.1 %**. 방향은 맞았고 크기는 과소(수 % 가 아니라 7 %). Python 판은 200 Hz 입력의 0.4~0.5 % 를 놓치고 있었다(196.5 Hz 발행) — §15 당시엔 몰랐던 사실.

**기록 사이 모순 · 지금 코드의 낡은 주석(10-30 확인)**
1. `job549` 출력 원문 없음 — §15 의 여섯 수치 모두 다시 볼 수 없다.
2. Python 판 머리 주석은 여전히 '근거: ICM-20948 정지 자이로 z 바이어스 −0.0072 rad/s' · 'TODO(production): 펌웨어가 … 제공하면 본 노드 제거' — 지금 IMU 는 Jetson USB 의 D455f 라 펌웨어가 바이어스를 처리할 수 없다(CLAUDE.md §4). 주석이 현재 근거와 다르다.
3. Python 판 `SLIP_PTS` 주석의 'B_eff 0.409 를 펌웨어 `WHEEL_BASE_M` 에' — 펌웨어 지금 값은 **0.443**(`rover_platform.h` 73 행, 09-07 2 차 실측).
4. `camera.launch.py` 4 행 주석 'EKF 는 자이로 z 만 사용' — 실제 EKF 는 광학 −y(인덱스 10, `ekf.yaml` 32~34 행 주석이 맞음).
5. CLAUDE.md §6 'B2 · B3 기본 끔' vs 실제 기본 구성(vslam on)에서 B3 켜짐 σ 0.3(§0).
6. 09-23 §15 는 '휠 오도 25 Hz' 라 썼다 — 08-26 기록은 `/wheel_odom` 50 Hz(당시 펌웨어). 25 Hz 로 바뀐 시점은 이 카드 범위에서 확인 안 함(09-28 §28 재확인 25.000 Hz).
7. (09-28 §11 · §27) gtest 는 §11 에 5 개, §27 에 3 개 추가 → 지금 파일의 `TEST(` 는 **8 개**(`test_conditioner_core.cpp` 12 · 25 · 34 · 51 · 63 · 73 · 89 · 104 행). colcon 은 '6 tests' · '9 tests' 라 했다 — 둘 다 TEST 수 + 1. CMake 의 gtest 대상은 `ament_add_gtest(test_conditioner_core …)` 하나(`CMakeLists.txt` 33 행)이므로 +1 은 실행 파일 단위 결과로 **추정**(colcon 출력 원문 없음).
8. (09-28 §11) 'Python 판이 IMU 입력 약 120~176 개(0.4~0.5 %)' — 원문은 재생 대조 171 · 176 개(j596 · j597), 결정적 대조 때 함께 돈 재생에서 122 개(j598 의 Python 수신 34,463). 122 / 34,585 = 0.35 % 라 '0.4~0.5 %' 는 j596 · j597 두 번만의 범위다.
9. (09-28 §11) j596 출력에는 '각속도 y 차 = 0 인 짝' · '첫 차이 시점까지 Python 쪽에만 빠진 IMU' 줄이 없고 j597 에는 있다 — 두 실행 사이에 `job594` 가 고쳐졌다(저장소에 남은 것은 마지막 판). 즉 j596 을 지금 `job594` 로 재현하면 줄이 더 나온다.

## 6. 남은 것 (09-23 시점)
- C++ 이식 · 동일성 검증 — 미착수.
- 가변 공분산 수치 — 회전 시험 대기.
- 펌웨어 공분산 0 — 그대로(지금도 `microros_task.c` 287 행).

**09-28 시점(§10 · §11 뒤)**
- C++ 이식 · V1 · V2 — 완료(§2 표). 남은 V3(주행 중 EKF 동등성) — '예상' 만, 따로 판정한 기록 없음.
- 대체 패키지 — 사용자 결정으로 닫힘. realsense `angular_velocity_cov` 로 자이로 공분산을 옮기는 것은 가능하지만 하지 않았다(공분산 로직 한 곳 원칙, §7.2).
- Python 판(`scripts/sensor_conditioner.py`) — 되돌리기용으로 남김(`conditioner:=py`). B2 · B3 · rf2o · vslam 구성은 C++ 판에서만(`ekf.launch.py` 47~48 행이 py + rf2o 를 거부. 단 py + `vslam:=on` 은 거부하지 않는다 — 그때 B3 는 Python 판에 없어 조용히 빠진다, 코드 확인 11-02).
- 가변 공분산 수치 — 09-28 §26 · §27 에서 B3 0.03 으로 구현(→ [B2 · B3 카드](icr-b2-b3.md)).

## 7. 이후 — 포인터
- 09-28 §10 · §11 은 위 §2 · §4 · §5(실수 3) · §9 로 채움.
- 09-28 §26~§27 B2(ICR) · B3(회전 구간 분산) 구현, 기본 꺼짐 → 09-29 §1 · §3 · §4 · §5 시험 뒤 B2 끔 유지: [회전축 치우침 B2 · 회전 구간 분산 B3](icr-b2-b3.md).
- 10-02 · 10-06 rf2o: 순수 회전 중 휠 병진 σ 0.3(0.03 이면 25 Hz 휠이 10 Hz rf2o 를 눌러 미끄러짐을 지움) → `rf2o:=true` 면 B3 자동(σ 0.3). 10-20 · 10-23 cuVSLAM 도 같은 조건(`ekf.launch.py` 37~40 행 주석).
- 10-28 · 10-29 정지 중 yaw 드리프트: 주행 **뒤** 정지에서만 odom yaw 가 0.39 °/분 돎(43 분 +16.6°), prep 직후 정지 30 분은 0.07°(보정 없으면 73°) — 'ZUPT 정상' 은 prep 직후 조건에서만 확인. 주행 뒤에 ZUPT 가 돌았는지 · 원인(잔여 바이어스 vs cuVSLAM)은 **미확인**: [세워 둔 로버의 방향 드리프트](stationary-yaw-drift.md).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job549_cond.sh` | 09-23 역할 점검(원본 공분산 · Hz · CPU · 대안 패키지 · ZUPT 로그) | [`2026-09-23/jobs/`](../debug_log/2026-09-23/jobs/job549_cond.sh) — 출력 원문 없음 |
| `job213_axis.py` | 09-10 ZUPT 의 근거 측정(정지 30 s 자이로 축 · 잔차) | [`2026-09-10/jobs/`](../debug_log/2026-09-10/jobs/job213_axis.py) — 해설은 2 기 시기 카드 몫(이 카드는 수치만 인용) |
| `job595_condab.sh` | 09-28 V1 래퍼 — `rec SEC` 원시 입력 녹화 · `ab BAG` 두 판 동시 기동 + `job594` | [`2026-09-28/jobs/`](../debug_log/2026-09-28/jobs/job595_condab.sh) |
| `job594_condab.py` | 09-28 V1 재생 대조(DDS, 1 배속) | [`2026-09-28/jobs/`](../debug_log/2026-09-28/jobs/job594_condab.py) → [`j596`](../debug_log/2026-09-28/outputs/j596_cond_v1_static.txt) · [`j597`](../debug_log/2026-09-28/outputs/j597_cond_v1_static2.txt) |
| `job598_conddet.py` | 09-28 V1 결정적 대조(Python 판 콜백 직접 호출) | [`2026-09-28/jobs/`](../debug_log/2026-09-28/jobs/job598_conddet.py) → [`j598`](../debug_log/2026-09-28/outputs/j598_cond_det.txt) |
| (이름 없음) V2 CPU 측정 | 09-28 V2 — 30 s CPU · 발행률 · EKF 위반 로그 | 도구 원본 없음 → [`j599`](../debug_log/2026-09-28/outputs/j599_cond_v2_cpu.txt) |
| `test_conditioner_core.cpp` | gtest — 09-28 §11 5 개 + §27 3 개 | [`ros2_ws/src/rover_bringup/test/`](../../ros2_ws/src/rover_bringup/test/test_conditioner_core.cpp) |
| `bag_condraw` | 정지 원시 입력 183.2 s(IMU 36,585 · 휠 4,557) | Jetson `/tmp`(원천 소실) |

도구 계보: 09-23 `job549_cond.sh`(역할 점검, 원문 없음) → 09-28 `job595 rec` 녹화 → `job595 ab` + `job594`(DDS 재생 대조, 누락 때문에 '논리 동일' 을 못 가림) → `job598`(Python 판을 DDS 없이 돌려 누락 변수 제거) → 09-29 `job627` · `job628`(같은 '도메인 42 재생' 틀로 컨디셔너 + EKF 를 함께 재생 — B2 · B3 A/B, [B2 · B3 카드](icr-b2-b3.md)) → 10-06 R3 재생(`r3_replay.sh`, rf2o 까지). 상시 도구로 올라간 것은 없다(`Docs/tools/` 에 컨디셔너 대조 도구 없음).

## 9. 도구 해설
### job549_cond.sh — 컨디셔너 역할 점검 (09-23 12:5x, Jetson, 읽기 전용)
- 부른 형태: `run_jx.sh job549_cond.sh`(인자 없음). UDP 전용 DDS 프로파일 · humble 환경.
- 왜: 사용자 질의 '빼도 되는가' — 빼면 EKF 가 받을 입력(원본)이 실제로 어떤지를 보려고.
- 하는 일: ① `ros2 topic echo --once /camera/camera/imu` 에서 `covariance:` 다음 줄들 8 줄(원본 자이로 · 가속 · 자세 공분산) ② `/wheel_odom` 한 메시지의 `twist:` 이후 공분산 36 개 중 0 이 아닌 값 개수(`^- [1-9]` 또는 `^- 0.0*[1-9]` 에 맞는 줄 수) ③ `/camera/camera/imu` 와 `/imu/data` 각 6 s hz ④ `top -b -n2 -d5` 의 둘째 화면에서 COMMAND 가 python3 인 pid 중 `ps -o args` 에 sensor_conditioner 가 든 것의 %CPU ⑤ `ros2 pkg list` 에서 imu_complementary · imu_filter_madgwick · imu_tools ⑥ `/tmp/sensors.log` 의 'ZUPT' · 'gyro bias' 마지막 3 줄.
- 출력: **원문 없음**(대화에만). SUMMARY 에 옮긴 것: 원본 공분산 0.01 · 휠 0 · CPU 41.8 % · 바이어스 부팅 −0.00073 / 지금 −0.00106 · ZUPT 잔차 0.00003.
- 결과가 쓰인 곳: §15 판정 (a)~(c) · 대체 가능성 · C++ 제안.
- 알려진 결함: ② 의 정규식은 `1e-05` 같은 지수 표기나 음수를 못 센다(그 메시지는 0 뿐이었다니 결과엔 영향 없음, 추정). ④ 는 pid 하나만 — launch 래퍼가 있으면 두 줄 나올 수 있음. ⑥ 은 그 순간 로그 파일에 의존(prep 이 덮어씀). 바이어스 '부팅 값' 과 '지금 값' 은 각각 calibrated 줄과 마지막 ZUPT 줄에서 읽은 것으로 보인다(어느 줄인지 출력이 없어 **미확인**).
- 계보: 08-29 `job17e`(pid → cmdline 으로 컨디셔너 식별) → 09-09 · 09-10 CPU 도구들 → 이 도구 → 09-28 V1(`job596` · `job597` 재생 대조, `job598` 결정적 대조) · V2(`j599` CPU).
- 지금 다시: 형태는 쓸 수 있으나 ④ 는 C++ 판에서 COMMAND 가 `sensor_conditioner_node` 라 python3 필터를 바꿔야 한다.

### job595_condab.sh — V1 래퍼 (09-28 §11, Jetson)
- 부른 형태: `bash /tmp/job595_condab.sh rec SEC`(라이브 도메인 0, 로버 정지. SEC 값은 기록 없음 — 녹화 길이 183.2 s 와 'SEC + 5 s 뒤 timeout' 으로 보아 ≈ 180 **추정**) → `bash /tmp/job595_condab.sh ab /tmp/bag_condraw`. UDP 전용 DDS 프로파일.
- 왜: 같은 입력을 두 판에 넣어 출력을 비교하려면 원시 입력(컨디셔너 앞)이 있어야 한다 — 평소 bag 에는 이미 조정된 `/imu/data` 만 있다.
- 하는 일: `rec` = `ros2 bag record /camera/camera/imu /wheel_odom` 를 SEC + 5 s 동안, 끝나면 `ros2 bag info` 의 길이 · 토픽 줄. `ab` = `ROS_DOMAIN_ID=42`(라이브와 분리) 에서 Python 판(`__node:=cond_ab_py`)과 C++ 판(`cond_ab_cpp`)을 **출력 토픽만 `/py/…` · `/cpp/…` 로 remap** 해 띄우고(입력은 둘 다 `/camera/camera/imu` · `/wheel_odom`), 4 s 뒤 `job594` 실행 → 두 로그의 calibrated · ZUPT 마지막 4 줄 → 노드 종료 · 남은 노드 수.
- 출력: j596 · j597 아래쪽 '== 로그(캘리브·ZUPT)' 블록. 쓰인 곳: §11 V1.
- 결함: 두 노드가 같은 DDS 입력을 각자 받으므로 **어느 한쪽 누락이 결과를 흔든다**(그래서 job598 이 필요했다). 노드 이름 `pkill -f "cond_ab_(py|cpp)"` 로 정리 — 같은 이름 다른 프로세스가 있으면 같이 죽는다.
- 지금 다시: `rec` 은 그대로 쓸 수 있다(원시 IMU 토픽 이름 같음). `ab` 는 Python 판이 남아 있어 실행은 되나, C++ 판 B3 가 launch 에서만 켜지는 지금 구성(파라미터 없이 `ros2 run`)과는 다른 기본값으로 돈다.

### job594_condab.py — V1 재생 대조 (09-28 §11, Jetson 도메인 42)
- 부른 형태: `python3 /tmp/job594_condab.py BAG`(job595 가 부름).
- 하는 일: ① `rosbag2_py` 로 bag 전체를 메모리에 읽음(IMU · 휠) ② 같은 노드에서 `/camera/camera/imu` · `/wheel_odom` 를 `qos_profile_sensor_data` 로 발행, 출력 4 토픽을 **BEST_EFFORT depth 200** 으로 구독(첫 판은 reliable 이라 0 개 — §5 실수 3) ③ bag 시각 간격대로 1 배속 재생(`spin_once` 로 기다림) ④ 출력 메시지를 `header.stamp`(ns 정수)로 짝지어 필드별 최대 절대차: IMU 각속도 · 가속 · 자세 · 세 공분산, 휠 twist(vx · vy · wz) · pose · twist 공분산 ⑤ 한쪽에만 있는 IMU 수 ⑥ 바이어스 추이 = 원시 y − 출력 y(처음 · 끝) ⑦ 각속도 y 차 = 0 인 짝 비율, 첫 차이 전 Python 쪽에만 빠진 IMU 수('0 이면 논리 차이 의심') ⑧ C++ 출력을 `/tmp/cond_cpp_out.pkl` 로 저장(job598 입력).
- 출력: j596(⑦ 줄 없음 — 앞판) · j597(⑦ 있음). 핵심 줄: '수신: Python IMU 34409 / C++ IMU 34580' · 'angular_velocity 4.26e-05 … 나머지 0'.
- 판정에 준 영향: '각속도만 다르고 나머지 0' + '첫 차이 전에 Python 누락 2 개' → 차이가 누락에서 온다는 가설. 하지만 누락이 있는 한 비트 동일은 못 보임 → job598.
- 결함: 짝짓기 키가 stamp 라 같은 stamp 가 두 번 오면 마지막 것만 남는다(이 bag 에선 영향 없음으로 보임 — 휠 4,557 = 입력 수). 재생기 자신도 DDS 발행이라 누락 원인이 '수신 노드' 인지 '재생기' 인지는 가르지 않음.
- 지금 다시: 형태 재사용 가능(컨디셔너를 바꿨을 때 회귀 검사용). 상시 도구로는 안 올라감.

### job598_conddet.py — V1 결정적 대조 (09-28 §11, Jetson)
- 부른 형태: `python3 /tmp/job598_conddet.py /tmp/bag_condraw`(job594 가 pkl 을 남긴 뒤).
- 왜: 재생 대조에서는 Python 판이 0.5 % 를 놓쳐 ZUPT 창이 어긋난다 — '누락 없는 Python 판' 을 기준으로 삼아야 논리 동일을 가린다.
- 하는 일: ① 저장소 Python 판(`~/ros2_ws/src/rover_bringup/scripts/sensor_conditioner.py`)을 `importlib` 로 모듈째 불러 노드 객체 생성 ② 그 노드의 `imu_pub.publish` · `odom_pub.publish` 를 **가로채는 람다로 바꿔** 출력을 사전에 저장(DDS 를 안 거침) ③ bag 메시지를 순서대로 `imu_cb` · `odom_cb` 에 직접 넣음(누락 0) ④ C++ 재생 출력(pkl)과 stamp 로 짝지음 ⑤ 캘리브 2,000 개 뒤 입력 중 C++ 에 없는 것 = C++ 누락, 첫 누락 index ⑥ 첫 누락 **이전** 짝의 각속도 최대 차 · 완전 동일 비율, 전체 최대 차, 휠 완전 동일 비율.
- 출력: [`j598_cond_det.txt`](../debug_log/2026-09-28/outputs/j598_cond_det.txt) — 'C++ 누락 입력 6 개(캘리브 이후), 첫 누락 index 4969 / 34585' · '이전 4969 개 → 0 … 100.0 %' · '휠 … 100.0 %'.
- 판정에 준 영향: §11 '논리 동일 — 통과' 의 유일한 비트 동일 근거. 비교 구간은 캘리브 뒤 ≈ 24.8 s(4,969 / 200 Hz, 계산)이고 그 안에 ZUPT 2 s 창이 ≈ 12 번 닫힌다(계산 — 정지 bag 이라 창이 계속 돎) → ZUPT 갱신 · 상한 자르기 경로까지 비트 동일로 확인된 셈.
- 결함: C++ 쪽은 여전히 DDS 재생 출력이라 '누락 이후' 구간은 비교가 안 된다(그래서 전체 4.43e-5 는 기대된 차). Jetson 저장소 경로를 코드에 박음.
- 지금 다시: 쓸 수 있다(Python 판 · pkl 형식 그대로라면). C++ 판도 같은 식(콜백 직접 호출)으로 돌리는 짝 도구는 없다 — 만들면 두 판 모두 누락 0 으로 전 구간 대조가 된다(제안, 미구현).

### (도구 원본 없음) V2 CPU 측정 (09-28 §11, Jetson 라이브)
- 하는 일(출력 줄로 역추적): 각 판 pid 의 30 s CPU %, `top` 전체 합, `ros2 topic hz /imu/data` · `/odometry/filtered` 평균, `sensors.log` 의 EKF 주기 위반 줄 수(교체 전 · 후), 컨디셔너 프로세스 수. 측정 스크립트는 `jobs/` 에 없다 — 인라인 명령으로 **추정**.
- 출력: [`j599_cond_v2_cpu.txt`](../debug_log/2026-09-28/outputs/j599_cond_v2_cpu.txt). 쓰인 곳: §11 V2 표 · 기본 cpp 결정.
- 결함: 두 판을 **순차로**(같은 정지 상태, 다른 30 s) 쟀다 — 동시 비교 아님. 30 s 한 번씩.

### test/test_conditioner_core.cpp — gtest (09-28 §11 · §27, Jetson `colcon test`)
- 하는 일(TEST 8 개): `GyroBias.CalibratesMeanWhenStationary` · `ZeroBiasWhenNotStationary`(캘리브 문턱) · `ZuptStepIsClampedAndNeedsStationary`(±0.0005 자르기 · 정지 플래그) · `ZuptRejectsShaking`(σ ≥ 0.010 버림) · `Wheel.StationaryAndSlipFactor` — 여기까지 §11. `Icr.OffByDefaultAndGated` · `Icr.HalfTurnIntegratesToTwiceOffset` · `RotCov.OnlyWhenEnabledAndRotating` — §27([B2 · B3 카드](icr-b2-b3.md) §0).
- 왜 ROS 비의존 헤더로 뺐나: 위 계산을 노드 없이 검증하려고(`conditioner_core.hpp` 머리 주석 6 행).
- 한계: Python 판과의 수치 동일은 gtest 가 아니라 V1(bag)로만 확인. 출력 원문 없음(SUMMARY 의 '6 tests' · '9 tests' 문장뿐).

### job547_cpuidle.sh — (참고) 정지 CPU 합 (09-23, Jetson)
- 하는 일: 60 s 대기 → `top -b -n2 -d10` 둘째 화면에서 %CPU > 0 합과 8 % 넘는 프로세스 이름=값. 출력 원문 없음. §15 의 'CPU 41.8 %(정지)' 와 같은 시간대의 정지 부하 확인용으로 보이나 SUMMARY 에 인용 줄이 없어 **어디에 쓰였는지 미확인**.

### (지금 코드) sensor_conditioner_node · sensor_conditioner.py
- 실행 위치: Jetson, `sensors.launch.py` → `ekf.launch.py` 가 띄움(이름 `sensor_conditioner`).
- 부른 형태: `ros2 launch rover_bringup ekf.launch.py [conditioner:=cpp|py] [icr:=…] [rot_cov:=…] [rf2o:=…] [vslam:=off|shadow|on]` — 보통 prep 이 부른다.
- 하는 일: §0. C++ 판은 상수를 ROS 파라미터로 노출(`gyro_var` · `vy_var` · `zupt_*` · `icr_*` · `rot_*` …, 기본값 = Python 상수), 파라미터는 시작 때 한 번만 읽음.
- 로그: `gyro bias calibrated: (x, y, z) rad/s, std=(…)` / `startup not stationary (max std=…) — bias=0 유지` / `ZUPT #n: bias y A → B (관측 C), 잔차 yaw rate ±D rad/s = ±E °/분`(20 s 마다) — prep 로그(`/tmp/sensors.log` 류)에 남는다.
- 알려진 한계: 부팅 10 s 동안 로버가 움직이면 바이어스 0(경고만). ZUPT 는 휠이 정확히 정지를 보고해야 돈다(|vx| · |wz| < 0.005) — 휠 펄스가 남는 상태면 안 돎. 자이로 x · z 바이어스도 갱신하지만 EKF 는 y(로봇 yaw)만 씀.
- 지금 다시: 상시 사용 중.

## 10. 용어
- **자이로 바이어스(gyro bias)**: 가만히 있어도 자이로가 내는 0 이 아닌 값. 적분하면 각도가 계속 샌다(−0.00106 rad/s × 60 s ≈ 3.6°/분). MEMS 자이로는 온도에 따라 바이어스가 바뀐다 — D455f 는 켜 두면 데워진다.
- **ZUPT(Zero-velocity Update)**: '지금 안 움직인다' 는 걸 다른 근거(여기선 휠 정지)로 알 때, 그 동안의 센서 출력을 0 이 되게 바이어스를 다시 맞추는 표준 기법.
- **공분산(covariance) · 분산 · σ**: 측정을 얼마나 믿을지 숫자로. 분산 = σ². EKF 는 분산이 작은 입력을 더 믿는다. robot_localization 은 0 을 아주 작은 값(ε)으로 바꿔 '완벽' 으로 취급하므로, 모르는 값은 0 이 아니라 적당히 큰 값을 넣어야 한다.
- **REP-145 · orientation_covariance[0] = −1**: ROS IMU 메시지 규약에서 '이 메시지는 자세(orientation)를 제공하지 않는다' 는 표식.
- **광학 프레임(optical frame)**: 카메라 좌표 관례(x 오른쪽 · y 아래 · z 앞). 로버의 yaw(위축 회전)는 이 프레임의 −y 축 회전이다 — 그래서 EKF `imu0_config` 인덱스 10(vpitch 자리)을 켜고, 컨디셔너 로그의 잔차도 '−y'.
- **B2 · B3(09-28 명칭)**: B2 = 제자리 회전을 '차체의 한 점 p 를 축으로 도는 운동' 으로 보고 휠 속도에 그 축 이동 속도를 더하는 모형(ICR, Instantaneous Center of Rotation). B3 = 순수 회전 중 휠의 vx · vy 공분산을 키워 다른 센서(rf2o · cuVSLAM)가 옆 속도를 정하게 하는 가변 공분산.
