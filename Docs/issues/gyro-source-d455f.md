# 자이로 소스: 보드 ICM-20948 무반응 → D455f 카메라 IMU (커널 HID 모듈 · EKF 축 설정 · 컨디셔너)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(D455f 자이로로 대체 · 융합 동적 확인) · 보드 자이로 원인은 **미확인**으로 보류 | 08-26 ~ 08-27 (운용 결정 09-01, 이후 09-10 · 09-23 · 09-28 계속) | [08-26 판단·결정 3](../debug_log/2026-08-26/SUMMARY.md) | Jetson 커널 모듈 5 종(`/lib/modules/5.15.185-tegra/…/hid-sensor-*.ko`) + 패치 `uvcvideo.ko` · `/etc/udev/rules.d/99-realsense-libusb.rules` · `rover_bringup/config/ekf.yaml`(`imu0_config` 인덱스 10) · `rover_bringup/launch/ekf.launch.py`(`/imu/data_raw` → `/camera/camera/imu` 재매핑) · `rover_bringup/scripts/sensor_conditioner.py` | [보드 연결 · micro-ROS 세션](board-link-microros-session.md) · 회전 슬립 계수(W4, 카드 예정) · 정지 중 방향 드리프트 → [stationary-yaw-drift](stationary-yaw-drift.md)(10-28, 같은 컨디셔너 경로) |

**한 줄**: 보드 IMU(ICM-20948)는 정지 값(중력 · 노이즈)이 그럴듯해 처음엔 EKF 에 넣었지만, 손으로 로버를 돌린 녹화 2 회(88.6 s · 114.7 s)에서 자이로 z 가 |z| ≤ 0.041 rad/s 로 회전을 전혀 못 봤다. 그래서 RealSense D455f 내장 IMU 로 바꿨는데, Jetson 커널(5.15.185-tegra)에 HID 센서 모듈이 없어 커널 소스로 모듈을 직접 빌드(34 분 37 초)해 재부팅 없이 올렸다. EKF 는 설정이 맞아 보이는데 yaw 속도가 정확히 0 으로 나왔고(무음 실패), 원인은 robot_localization 이 `imu0_config` 를 **센서(광학) 프레임 축**으로 해석하는 것이었다 — 인덱스 11 → 10 으로 고쳐 정지 yaw 드리프트 0.10°/30 s, 손 회전 시 EKF 가 최대 2.12 rad/s 추종. 펌웨어가 covariance 0 을 보내고 카메라 IMU 는 펌웨어 경로 밖이라 Jetson `sensor_conditioner` 가 바이어스 · covariance 를 맡는다.

## 1. 증상
- 보드 IMU 를 넣은 EKF 의 정지 yaw 가 흐름: 컨디셔너 소스 주석 '정지 자이로 z 바이어스 −0.0072 rad/s → EKF yaw −0.23°/s 드리프트(2026-08-26 실측)', 보정 뒤에도 보드 IMU 구성 **4.4°/분**(08-27 결과 표 'EKF' 줄의 비교값). 출력 원문 없음 — 08-26 은 출력 저장 규약 전.
- 접지 회전 0.3 rad/s × 3 s 에서 휠은 36°, 실제는 15°(육안) — 그런데 자이로에는 그 15° 조차 없었다(08-26 판단 3).
- 손 회전 녹화: 1 ~ 3 rad/s 로 돌렸는데 |z| ≤ 0.041 rad/s(08-26 결과 표 '보드 자이로').

## 2. 흐름 (시간순)
| 날짜 · 제목 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-26 Step 3 | robot_localization 설치, 휠 + 보드 IMU EKF 기동(임시 static TF `base_link→imu_link` (−0.01, 0.01, 0.08)), 누락 의존성 `diagnostic-updater` 설치 | `/odometry/filtered` 30.000 Hz | EKF 동작 | `jobs/job3a.sh` · `job3b.sh` · `job3c.sh`(출력 원문 없음) |
| 08-26 Step 3 | 정지 자이로 바이어스 · 30 s yaw 드리프트 · 구독 QoS | 바이어스 z −0.0072 rad/s(컨디셔너 주석) | 펌웨어 covariance 전부 0 → robot_localization 이 0 을 ε 로 바꿔 '완벽 측정' 취급 → **Jetson 컨디셔너로 보완**(펌웨어 수정 금지 규칙, 판단 4) | `job3d.sh` · `job3e.sh` |
| 08-26 Step 3 | 'IMU 실물인가' 정적 판정(중력 ≈ 9.8 · 샘플 간 변동) · 중복 실행 · `/imu/mag` 확인 | 정지 값은 실물처럼 보임. `/imu/mag` 무발행(`mag.valid` 항상 false) | 실물로 판단 — ⚠ 정적 값으로는 판별 불가였음(판단 3 이 사후에 명시) | `job3g.sh` · `job3h.sh` |
| 08-26 Step 3 | 컨디셔너 10 s 캘리브레이션 → 60 s 정적 드리프트 / 휠 단독 EKF → 45 s 정적 | 휠 단독 정적 드리프트 0(45 s) | — | `job3i.sh` · `job3j.sh` |
| 08-26 Step 3 | 주행 검증(회전 0.3 · 전후 0.05), 휠 단독 최종 | filtered 가 wheel_odom 추종, 발산 없음 | — | `job3m.sh` · `job3n.sh` |
| 08-26 Step 3 | 회전 슬립 보정(컨디셔너) 0.3 / 0.6 rad/s | 슬립 계수 0.42 @ 0.20 · 0.28 @ 0.57 rad/s(**육안 기준 2 점**) | 속도 의존 → 2 점 선형보간 — ⚠ **08-27 W4 에서 착시로 정정** | `job3o.sh` · `job3p.sh` · `job3q.sh` |
| 08-26 판단 3 | **손 회전 녹화**(사용자가 들고 돌림) 2 회 + 분석 | 88.6 s · 114.7 s 모두 |z| ≤ 0.041 rad/s | **보드 자이로 무반응 → 융합 제외, D455f 로 대체 예정**. 기각: '저속이라 노이즈에 묻힘'(0.087 rad/s 는 σ 의 14 배, 손 회전 1~3 rad/s 에도 무반응) · '트랙 슬립으로 안 돌았다'(실제 15° 돎) | `job3r.sh` · `job3r2.sh` · `job3s.sh` |
| 08-27 '한 일' | D455f 좌이미저 · IMU 오프셋을 Intel `_d455.urdf.xacro` 에서 추출 | bottom_screw→camera_link (+11.2, +47.5, +14.5) mm, imu (−16.0, −30.2, +7.4) mm | URDF 반영 | `job4b.sh` · `job4c.sh` |
| 08-27 '한 일' | Jetson RealSense 준비 상태 진단 | 커널 5.15.185-tegra, HID 모듈 · iio · udev 없음, 패키지 구버전 | — | `job4d.sh`(출력 원문 없음) |
| 08-27 판단 2 | 저리스크 준비 · JetsonHacks 조사 | librealsense2 2.58.3 / realsense2-camera 4.58.3, udev 2 종. JetsonHacks 프리빌트 HID 모듈은 5.15.148 전용 | **소스 빌드(A) 채택**(사용자 승인) — HID 5 종은 소스에 있고 config 만 꺼짐 → 모듈로 켜서 전체 빌드(vermagic · CRC 정합) | `job4e.sh` · `job4f.sh` |
| 08-27 '결과' | 커널 HID 모듈 빌드(10:23:44 시작, 백그라운드) | uvcvideo 패치 2 종 정상 적용, **34 분 37 초**, `BUILD DONE 11:00:54`, vermagic `5.15.185-tegra SMP preempt mod_unload modversions aarch64` | 성공. ⚠ 감시 중 '죽은 빌드' 오경보(§5.3) | [`outputs/job4g_diag.txt`](../debug_log/2026-08-27/outputs/job4g_diag.txt) · `job4g_progress30.txt` · `job4g_launch.txt` |
| 08-27 판단 7 | 모듈 라이브 로드 → uvcvideo 교체 + USB 재열거(`authorized 0→1`) | 모듈 5 종 vermagic 일치, `hid-sensor-hub` 바인딩, `iio:device0=accel_3d` / `iio:device1=gyro_3d` | **재부팅 불필요** | [`job4j_module_load.txt`](../debug_log/2026-08-27/outputs/job4j_module_load.txt) · [`job4k_rs_gate.txt`](../debug_log/2026-08-27/outputs/job4k_rs_gate.txt) |
| 08-27 '결과' D455f USB | 카메라 게이트(depth 640×480×30 + IMU 200) | `Device USB type: 2.1`(480M), depth **25.505 Hz**, IMU 199.625 Hz | USB 3 케이블 · 포트 필요(IMU 용도엔 무관) | `job4k_rs_gate.txt` |
| 08-27 '결과' D455f IMU | IMU 정밀 검증 45 s(accel + gyro, unite copy) · iio 권한 | `/camera/camera/imu` **199.637 Hz**, 정지 가속 y −9.767(광학 −Y = 중력), iio 파일 rwxrwxrwx | 정상 | [`job4l_imu_lidar.txt`](../debug_log/2026-08-27/outputs/job4l_imu_lidar.txt) |
| 08-27 판단 6 | D455f → 컨디셔너 → EKF 배포(카메라 IMU 만) | `/imu/data` 199.686 Hz, frame `camera_imu_optical_frame`, TF (0.066, 0.017, 0.251) / RPY (−90, 0, −90), **40 s 정적 yaw z=0.0 · w=1.0 그대로, vyaw 0.0** | 겉보기 정상 — 실제론 융합 안 됨(무음 실패) | `job4m.sh`(출력 소실, §8) · [`job4n_ekf_d455_verify.txt`](../debug_log/2026-08-27/outputs/job4n_ekf_d455_verify.txt) |
| 08-27 판단 6 | 융합 진단: stamp · 구독 QoS · 값 분포 | `/imu/data` 자이로 z 0.0003 ~ 0.0021(0 아님) vs filtered vyaw 10 개 전부 0.0. 구독 BEST_EFFORT 정합. `imu0_config` 인덱스 11 = True | 입력은 들어가는데 출력이 0 | [`job4o_ekf_imu_diag.txt`](../debug_log/2026-08-27/outputs/job4o_ekf_imu_diag.txt) |
| 08-27 판단 6 | **시각 가설**: 오래된 측정이라 무음 폐기? now − stamp 측정 | `/imu/data` +2.0 ms, `/wheel_odom` +13.8, `/wheel_odom/conditioned` +15.5 — IMU 가 더 신선. `sensor_timeout` 0.1 | **기각** | [`job4p_latency.txt`](../debug_log/2026-08-27/outputs/job4p_latency.txt) |
| 08-27 판단 6 | EKF `debug:=true` 15 s | 디버그 파일 710,900 줄. imu0 측정은 처리됨(`imu0_twist` 23,518 회). 원래 update 벡터 인덱스 11 → `After applying transform to base_link` 에서 **인덱스 9(vroll)** | robot_localization 은 `*_config` 를 **센서 프레임 기준**으로 해석해 TF 로 회전 → 광학 z(vyaw 자리)가 로봇 롤 속도가 되어 2D 모드에서 버려짐 | [`job4q_ekf_debug.txt`](../debug_log/2026-08-27/outputs/job4q_ekf_debug.txt) · [`job4q_updatevec.txt`](../debug_log/2026-08-27/outputs/job4q_updatevec.txt) |
| 08-27 판단 6 | `imu0_config` 인덱스 10(광학 y = 로봇 −yaw) 으로 수정 | filtered vyaw 0 아닌 작은 값(−0.0022 ~ +0.0021), 29.998 Hz. 30 s 정적 z 0.000633 → 0.001536 ⇒ **0.10°/30 s ≈ 0.2°/분** | 보드 IMU 4.4°/분 대비 22 배 개선 | [`job4r_axis_fix.txt`](../debug_log/2026-08-27/outputs/job4r_axis_fix.txt) |
| 08-27 '결과' 손 회전 | D455f 자이로(광학 y) + EKF vyaw 동시 녹화 → 분석 | 자이로 min −2.770 / max +2.997 rad/s(정지 구간 2 s 창 최대 0.01), EKF vyaw max 2.121 / min −0.627 | 자이로 실동작 · 융합 축 정합 확인. ⚠ EKF 음의 방향 최대가 −0.627 로 작은 비대칭은 기록에서 다루지 않음(**미확인**, §6) | `job4t_rec_start*.txt` · [`job4u_hand_rotation.txt`](../debug_log/2026-08-27/outputs/job4u_hand_rotation.txt) |
| 08-27 판단 8 | USB 대역폭: 카메라 풀스트림 + LiDAR + 로버 동시 vs 카메라 단독 | 카메라 Bus 02 **5000M**(USB 3.2), LiDAR 12M(외장 허브 하위), CH340 12M. 동시: scan 10.016 / depth 28.838 / color 13.264 / imu 199.592 / odom 49.994. 단독: depth 29.117 / color 14.551 / imu 199.641. dmesg USB 오류 0 | **간섭 없음**(SuperSpeed 와 USB2 신호 도메인 분리). color 소폭 미달은 단독에서도 같음 → 버스 아님. 컨디셔너(Python) CPU 41.2 % → C++ 또는 다운샘플 TODO | [`job4v_usb_bandwidth.txt`](../debug_log/2026-08-27/outputs/job4v_usb_bandwidth.txt) · [`job4w_usb_simul.txt`](../debug_log/2026-08-27/outputs/job4w_usb_simul.txt) |
| 08-27 '한 일' | 통합 `sensors.launch.py` 전환 + SLAM 스모크 | scan 9.990 / imu 199.568 / depth **29.999**(USB 3) / filtered 30.001 / odom 49.995. HID `set_power 1 failed` 경고 1 회 | 무해(사소 항목) | [`job4x_sensors_slam.txt`](../debug_log/2026-08-27/outputs/job4x_sensors_slam.txt) |
| 08-27 'W 트랙' | D455f 자이로를 기준으로 회전 슬립 재측정(W4, 사용자 `!` 실행) | 자이로/휠 적분비 L-slow 0.482 · L-fast 0.402 · R-slow 0.429 · R-fast 0.553 → 평균 0.47, ±0.06 | **속도 의존 없음 → 단일 상수 0.46**. 08-26 의 속도 의존은 '육안 + 구 게이지 + 이상치 착시'. 적용 뒤 정적 0.017°/30 s | [`job5b_w4_recalib.txt`](../debug_log/2026-08-27/outputs/job5b_w4_recalib.txt) · [`job5c_slip_apply.txt`](../debug_log/2026-08-27/outputs/job5c_slip_apply.txt) |
| 08-27 'W 트랙' 외부 검증 | 자이로 누적 방위 vs 사용자 육안 | 좌 2 번 뒤 자이로 +79°(육안 ≈ 70°), 우 2 번 뒤 −15°(육안 ≈ 10° 우). 원본 휠은 좌 2 번에 183° | **자이로 정확 · 원본 휠 ≈ 2.3 배 과대** 독립 확인 | [`job5d_w4_external_validation.txt`](../debug_log/2026-08-27/outputs/job5d_w4_external_validation.txt)(정리 메모, 스크립트 없음) |
| 08-28 '한 일' | Jetson 재부팅(08:51) 뒤 | `lsmod | grep -c hid_sensor` = 6, `iio:device0 iio:device1` 생존, `/camera/camera/imu` 200 Hz | **HID 모듈 재부팅 뒤 자동 로드** — 빌드 영구 적용 입증 | `2026-08-27/outputs/job6b_restart.txt`(08-28 실행분) |
| 08-28 'SLAM 첫 맵' | 360° 제자리 회전 맵핑 | 복귀 자세 x +0.2 cm · y +0.1 cm · yaw +1° | yaw(π) · EKF · 자이로 융합 · 슬립 보정 체인 정합 최종 증명(SUMMARY 표현) | 08-28 SUMMARY |
| 09-01 'CPU 최적화 + conditioner 결정' | 프로세스별 CPU | `sensor_conditioner` **44 %**(200 Hz IMU 처리) — 앞서 'deskew 45 %' 는 오인 | 최적화 안 함: 임시 shim · IMU 레이트 하향(200→100)은 cuVSLAM VIO 에 반확장적 · 펌웨어는 카메라 IMU 를 처리 못 함 | `2026-08-31/SUMMARY.md` 09-01 세션2 절 · `outputs/job17e_identify.txt` |
| **이후(09-04 ~)** | 다음 시기에서 채움 | 지시만: 09-10 정지 80 분 뒤 105°(09-28 SUMMARY 인용) · **09-23 ZUPT**(휠 정지 구간 바이어스 온라인 재추정) · 09-23 사용자 결정 'IMU 200 Hz 유지 · 다운샘플 금지' · **09-28 컨디셔너 C++ 이식 계획** · 10-28 정지 중 yaw 드리프트([카드](stationary-yaw-drift.md)) | — | — |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 보드 IMU 는 실물이다(값이 지어낸 것이 아니다) | 정지 중력 ≈ 9.8 · 샘플 간 변동(job3g) | 실물처럼 보임 | 정적 값으로는 **판별 불가**(08-26 판단 3) — 가속도는 실제여도 자이로는 별개 |
| 보드 자이로가 저속 회전을 노이즈에 묻는다 | 실회전 0.087 rad/s(15°/3 s) vs 노이즈 σ, 손 회전 1~3 rad/s | 0.087 은 σ 의 14 배, 손 회전에도 |z| ≤ 0.041 | **기각** |
| 트랙 슬립으로 차체가 실제로 안 돌았다 | 육안 실회전 | 15° 돎, 그마저 자이로에 없음 | **기각** |
| 보드 자이로 무반응의 원인(하드웨어 · 레지스터 설정 · `imu_processor` 가 비실측 값을 `valid=true` 로 발행) | — | 펌웨어 과제로만 기록(08-26 '펌웨어 과제 목록') | **미확인**(CLAUDE.md §4: '자이로 원인 규명 시 복귀 검토') |
| EKF 가 IMU 를 '오래된 측정' 으로 무음 폐기한다 | now − stamp(job4p) | IMU +2.0 ms 로 휠(+13.8)보다 신선 | **기각** |
| EKF 가 `imu0_config` 를 base_link 축으로 해석한다(처음 전제) | debug 로그의 update 벡터(job4q) | 인덱스 11 → 변환 뒤 9 | **기각** — 센서 프레임 축 해석이 **확인** |
| 카메라 · LiDAR · 로버가 USB 대역을 나눠 IMU 를 굶긴다 | 동시 vs 단독(job4v/4w) | IMU 199.59 vs 199.64 Hz, USB 오류 0 | **기각** |
| 회전 슬립은 속도 의존(0.42 @ 0.20 · 0.28 @ 0.57) | 자이로 기준 W4 4 회 | 느림 0.456 / 빠름 0.478 | **기각** → 단일 0.46 |

## 4. 조치와 효과
- **IMU 소스 교체**: `ekf.launch.py` 가 컨디셔너 입력 `/imu/data_raw` 를 `/camera/camera/imu`(D455f, 200 Hz, `unite_imu_method` 1 = copy)로 재매핑. 보드 `/imu/data_raw` · `/imu/mag` 는 미사용.
- **커널 모듈**: `CONFIG_HID_SENSOR_{HUB,IIO_COMMON,IIO_TRIGGER,ACCEL_3D,GYRO_3D}=m` 으로 `Image + modules` 전체 빌드 → 5 개 `.ko` 와 패치 `uvcvideo.ko`(원본 `.original` 백업) 설치 + `depmod`. 재부팅 없이 `modprobe` + 카메라 USB 재열거로 적용, 재부팅 뒤 자동 로드 확인(08-28).
- **EKF 축**(`ekf.yaml`, 09-02 커밋 판 주석 그대로 요지): `camera_imu_optical_frame` 은 x 우 / y 하 / z 전방 → 로봇 yaw(base z) = 광학 −y = `imu0_config` 인덱스 10(vpitch 자리). 자이로 1 축만, 가속도 융합 금지(이전 로버 EKF 2026-05-29 실측: 바이어스 이중적분 발산), `imu0_twist_rejection_threshold` 8.0, `two_d_mode` true.
- **컨디셔너**(`sensor_conditioner.py`, Python): 시작 2000 샘플(200 Hz × 10 s) 평균으로 자이로 바이어스, σ 최대 < 0.015 rad/s 일 때만 채택(아니면 '움직임' 경고 + 바이어스 0); 자이로 covariance 대각 0.02² = 0.0004, 가속 0.5², orientation_covariance[0] = −1(자세 미제공 표시); 휠 오도 twist covariance vx 0.02² · vy 0.01² · vyaw 0.1², vyaw × 슬립 계수. '자이로가 25 배 신뢰'(0.01 / 0.0004) 의 근거.
- 효과(측정): 정적 yaw 드리프트 보드 IMU 4.4°/분 → D455f 0.10°/30 s(0.2°/분) → 슬립 0.46 뒤 0.017°/30 s(job5c). 손 회전 자이로 ±3.0 rad/s 포착. 360° 회전 뒤 yaw +1°(08-28).
- 한계: 바이어스는 **시작 10 s 한 번** — 발열 등으로 바이어스가 움직이면 정지 중에도 샌다(이후 09-10 · 09-23 ZUPT · 10-28 카드). 컨디셔너 CPU 41~44 %. 카메라 IMU 는 USB 로 Jetson 에 붙어 보드와 시각 동기 이점이 없음.

## 5. 내 실수
### 5.1 보드 IMU 를 정적 값만 보고 EKF 에 넣음
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 휠 + 보드 자이로 EKF(job3b) 와 바이어스 보정(job3e · job3i) |
| 본 것 | 정지 중 중력 · 샘플 간 변동이 실물처럼 보임(job3g, 출력 원문 없음) |
| 처음 추론 | 실물 IMU → 자이로도 동작 |
| 의심한 이유 | 회전 0.3 rad/s 3 s 에서 실제 15° 가 돌았는데 자이로 · EKF 에 없음 |
| 판별 | 사용자 손 회전 녹화 2 회(job3r · job3r2 → job3s) |
| 결론 | 자이로 무반응. 가속도의 '실물스러움' 은 자이로의 생사를 말하지 않는다 |
| 다음에 알아보는 법 | 센서 생사는 **동적 시험**(알려진 큰 입력)으로. 정지 노이즈 · 중력은 판별력 없음 |
| 데이터 | `2026-08-26/jobs/job3g.sh` · `job3r.sh` · `job3r2.sh` · `job3s.sh`, 녹화 `/tmp/gyro_rec.txt` — **원천 소실**(Jetson `/tmp`, 출력 저장 규약 전) |

### 5.2 회전 슬립 '속도 의존' 을 육안 2 점으로 결정
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 휠 vyaw 과대(36° vs 15°)를 컨디셔너에서 보정(job3o~3q) |
| 본 것 | 0.42 @ 0.20 rad/s · 0.28 @ 0.57 rad/s |
| 처음 추론 | 속도 의존 → 2 점 선형보간 |
| 의심한 이유 | 기준이 육안 각도(자이로가 죽어 있었음) + 08-27 게이지 변경 |
| 판별 | D455f 자이로 적분을 기준으로 좌우 × 2 속도(job5b), 사용자 육안 교차(job5d) |
| 결론 | 속도 의존 없음(0.456 / 0.478) → 단일 0.46. 08-26 값은 '육안 + 구 게이지 + 이상치 착시'(08-27 W 트랙) |
| 다음에 알아보는 법 | 계수는 독립 기준 센서로, 조건마다 2 회 이상. 2 점만으로 '의존성' 을 말하지 않는다 |
| 데이터 | `2026-08-27/outputs/job5b_w4_recalib.txt` · `job5d_w4_external_validation.txt` · `jobs/job5b.sh` |

### 5.3 커널 빌드 감시 오경보('죽은 빌드')
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 백그라운드 빌드(job4g) 진행 감시 |
| 본 것 | 11:00:34 진행 확인 출력: `NO_IMAGE_YET` · `HID_KO_NOT_YET` · `objs: 0`, 로그 끝이 `== [5/6] build Image + modules (long)` 에서 멈춘 것처럼 보임 |
| 처음 추론 | 빌드가 죽었다 |
| 의심한 이유 | load average 4.82 로 CPU 는 일하고 있었음(같은 출력) |
| 판별 | `job4g_diag`(11:01:38): 전체 로그에 `real 34m36.984s` · `BUILD DONE 11:00:54` · `BUILD_SUCCESS`, `Module.symvers` 10:59:13 생성 |
| 결론 | 성공(오경보 20 s 뒤). job4g 의 `make … 2>&1 \| grep … \| tail -40` 이 make 가 끝날 때까지 아무것도 내보내지 않아 로그가 멈춘 것처럼 보였다. `objs: 0` 의 계산 방식은 스크립트가 남지 않아 **미확인** |
| 다음에 알아보는 법 | 장기 빌드는 원본 로그를 `tee` 로 따로 저장하고 진행 지표(.o 개수 · make 프로세스 · 최근 수정 파일)로 감시(08-27 판단 5) |
| 데이터 | `2026-08-27/outputs/job4g_progress30.txt`(생성 스크립트 원문 없음) · `job4g_diag.txt` · `job4g_procs.txt`(스크립트 원문 없음) · `jobs/job4g.sh` |

### 5.4 EKF 무음 실패를 처음에 시각 문제로 봄
| 칸 | 내용 |
|---|---|
| 하려 한 것 | D455f 자이로를 vyaw 로 융합(`imu0_config` 인덱스 11 = vyaw 에 True) |
| 본 것 | 40 s 정적 yaw 가 z = 0.0 · w = 1.0 **정확히** 그대로, filtered vyaw 0.0(job4n). 입력 `/imu/data` z 는 0 아닌 값(job4o) |
| 처음 추론 | 측정이 오래돼(stamp 지연) EKF 가 조용히 버린다 |
| 의심한 이유 | 경고 · 오류 로그 0(job4n 'EKF warnings' 빈칸), 구독 QoS 정합 |
| 판별 | now − stamp(job4p) → 기각. `debug:=true`(job4q) → update 벡터가 변환 뒤 인덱스 9 |
| 결론 | robot_localization 은 `*_config` 를 센서 프레임 축으로 보고 TF 로 회전시킨다. 광학 프레임에선 로봇 yaw = 광학 −y → 인덱스 10 |
| 다음에 알아보는 법 | 서명: 융합했다는 상태가 **정확히 0**(노이즈조차 없음) + 경고 없음 → 측정이 다른 축으로 들어가 2D 모드에서 버려지는 경우. 센서 frame_id 가 base 와 다르면 config 를 센서 축으로 적는다. 판별은 `debug` 로그의 `After applying transform to base_link, update vector is:` 줄 |
| 데이터 | `2026-08-27/outputs/job4n_ekf_d455_verify.txt` · `job4o_ekf_imu_diag.txt` · `job4p_latency.txt` · `job4q_ekf_debug.txt` · `job4q_updatevec.txt` · `job4r_axis_fix.txt` |

## 6. 남은 것 (이 시기 기준)
- 보드 ICM-20948 자이로 무반응의 원인 — 미확인(펌웨어 과제 3: `imu_processor` 가 비실측 자이로를 `valid=true` 로 발행). `/imu/mag` 무발행.
- 손 회전에서 EKF vyaw 음의 최대 −0.627 vs 자이로가 본 로봇 −3.0 rad/s(광학 +2.997) — 양의 방향(2.12 vs 2.77)보다 크게 덜 따라감. `imu0_twist_rejection_threshold` 8 거절 · 30 Hz 표본 · echo 누락 중 무엇인지 **미확인**(이후 판단에 쓰이지 않음).
- 컨디셔너 CPU 41~44 % — 09-01 '최적화 안 함' 결정. 이후 09-28 C++ 이식 계획.
- 시작 10 s 바이어스 1 회 — 이후 ZUPT(09-23) 로 이어짐.
- D455f 를 USB 2.1 로 붙였던 연결이 언제 3.2 로 바뀌었는지(job4k 480M → job4v 5000M) 기록 없음.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 손 회전 1 · 2(보드) | 88.6 s · 114.7 s, |z| ≤ 0.041 | 08-26 `job3r` · `job3r2` · `job3s` |
| HID 모듈 빌드 | 34 분 37 초, vermagic 일치 | 08-27 `job4g*` · `outputs/job4g_*` |
| RealSense 게이트 | USB 2.1 · depth 25.5 · IMU 199.6 | 08-27 `job4k` · `job4l` |
| EKF 무음 실패 판별 | job4m → 4n → 4o → 4p → 4q → 4r | 08-27 `outputs/job4n~4r` |
| 손 회전 3(D455f) | ±3.0 rad/s · EKF 2.12 | 08-27 `job4t` · `job4u` |
| USB 대역 | 동시 vs 단독 | 08-27 `job4v` · `job4w` |
| W4 | 슬립 0.46 · 외부 육안 | 08-27 `job4z` · `job5b` · `job5c` · `job5d` |

## 8. 도구 해설
도구 계보: (보드 자이로) `job3b → job3c → job3d → job3e → job3g · job3h → job3i → job3j → job3m → job3n → job3o → job3p → job3q → job3r → job3r2 → job3s` · (커널) `job4d → job4e → job4f → job4g(+ job4g_launch · job4g_diag) → job4i → job4j → job4k → job4l` · (EKF) `job4m → job4n → job4o → job4p → job4q → job4r` · (검증) `job4t → job4u`, `job4v → job4w → job4x` · (슬립) `job4z → job5b → job5c`. 공통 실행: PC → WSL `sshpass` → Jetson `/tmp/<job>.sh`, 패키지 소스는 `/tmp/rover_src/` 로 올린 뒤 `~/ros2_ws/src` 에 복사 · `colcon build --symlink-install`. sudo 는 `echo '<PW>' | sudo -S`(커밋본 가림). 모터를 움직이는 스크립트(job3m · 3n · 3p · 3q · job4z · job5b)는 사용자가 `!` 로 실행.

### 8.1 08-26 EKF · 컨디셔너 기동 계열 (출력 원문 전부 없음)
| 도구 | 하는 일(코드 기준) | 대기 · 판정 | 결과가 쓰인 곳 · 계보 |
|---|---|---|---|
| `job3a.sh` | `dpkg -l` 로 robot-localization 유무, 없으면 `apt-get install`, `ros2 pkg executables robot_localization` | — | Step 3 시작 |
| `job3b.sh` | 소스 복사 · 빌드 → 임시 `static_transform_publisher` base_link→imu_link (x −0.01, y 0.01, z 0.08)(이미 있으면 생략) → 기존 ekf_node 종료 → `ekf.launch.py` → 노드 목록 · 로그 · `/odometry/filtered` hz · pose · `/wheel_odom` QoS | 12 s | → job3c(의존성 누락) |
| `job3c.sh` | `ros-humble-diagnostic-updater` 설치 → EKF 재기동 → 같은 확인 + EKF 구독 QoS | 12 s | Step 3 'EKF 30.000 Hz' |
| `job3d.sh` | `/wheel_odom` · `/imu/data_raw` 의 발행 · 구독 QoS, 정지 자이로 1 회, `date` 와 함께 yaw quaternion → **30 s** → 다시, filtered twist | 30 s 차이 = 정적 드리프트 | 컨디셔너 필요성(바이어스) |
| `job3e.sh` | 컨디셔너 첫 배포: rover_bringup 만 빌드 → ekf · conditioner · launch 종료 → `ekf.launch` → 로그에서 `bias|error|died|WARN` → `/imu/data` 자이로(보정 뒤) → yaw 30 s 차 | 15 s | → job3i(캘리브 10 s 로 확장) |
| `job3h.sh` | `pgrep` 으로 conditioner · ekf · static TF 중복, `/imu/data` 발행자 수, `/imu/mag` hz | — | 중복 실행 의심 해소 · mag 무발행 확인 |
| `job3i.sh` | 컨디셔너 10 s 캘리브판 배포 → 20 s 대기 → `bias` 로그 → yaw **60 s** 차 · 위치 | 20 s + 60 s | 보드 IMU 정적 드리프트(4.4°/분은 08-27 표 비교값, 이 출력과의 대응은 원문 없어 **미확인**) |
| `job3j.sh` | '휠 단독 EKF' 판 배포 → 오류 grep · hz → yaw **45 s** 차 · 위치 | 15 s + 45 s | '휠 단독 정적 드리프트 0(45 s)' |
| `job3m.sh` | 스냅샷(wheel_odom · filtered 의 pose x,y,z,w) → 회전 0.3 rad/s 3 s(중간에 filtered vyaw 와 `/imu/data` z 1 회씩) → 정지 → 전진 0.05 3 s(중간 vx) → 후진 3 s → 최종 twist | 지시서 §3 한계 내 | 주행 중 발산 없음 |
| `job3n.sh` | job3m 과 같은 절차, 자이로 비교 줄 없음(휠 단독 최종) | — | Step 3 주행 검증 |
| `job3o.sh` | 슬립 보정판 배포 → 오류 · hz · 정적 pose | 15 s | → job3p |
| `job3p.sh` | yaw quaternion 스냅샷(wheel · filtered) → 0.3 rad/s 3 s → 다시 | 기대: filtered Δyaw ≈ 15°, wheel ≈ 35° | 0.42 @ 0.20(육안 기준) |
| `job3q.sh` | 0.6 rad/s 3 s, 중간에 원본 wheel vyaw 와 보정 뒤 filtered vyaw | '계수 0.43 의 속도 의존성 확인' | 0.28 @ 0.57 → §5.2 에서 정정 |

지금 다시 쓸 수 있나: 전부 아니오(보드 IMU 경로 · `/tmp/rover_src` 배포 방식 · 옛 ekf 구성 전제). 개념(정적 N 초 yaw 차)은 이후 `Docs/tools/` 의 확인 도구로 계승.

### 8.2 `job3g.sh` — IMU 실물 여부(정적)
- 하는 일: `/imu/data_raw` 의 linear_acceleration 2 회, angular_velocity 2 회, `/imu/mag` 1 회를 `--once` 로 찍음.
- 판정 의도: |a| ≈ 9.8 이고 두 샘플이 조금 다르면(실센서 노이즈) 실물. 
- 결함: 자이로의 '살아 있음' 은 정지 2 샘플로 판별 못 함(§5.1). 출력 원문 없음. 재사용 안 함.

### 8.3 `job3r.sh` → `job3r2.sh` → `job3s.sh` — 손 회전 녹화 · 분석(보드 자이로)
- job3r: `setsid nohup` 백그라운드로 `timeout 90 ros2 topic echo /imu/data_raw --field angular_velocity.z > /tmp/gyro_rec.txt` 시작, 'RECORDING_STARTED (90s)' 만 찍고 바로 끝 → 그동안 사용자가 로버를 손으로 돌림.
- job3r2: 기존 녹화 `pkill`, 파일 삭제, `timeout 180` 으로 재녹화, **5 s 뒤 줄 수를 세서 녹화가 실제로 흐르는지 즉시 확인**(job3r 에 없던 점검) → `RECORDING_STARTED (180s) — first 5s lines: N`.
- job3s(파이썬, Jetson): `/tmp/gyro_rec.txt` 에서 `---` 를 뺀 숫자 줄 → n, `n/50` s(50 Hz 가정), min · max · mean · std, |z| > 0.1 · > 0.5 비율, 100 샘플(= 2 s) 창마다 최대 |z| 와 막대(`#` × peak×20, 최대 40).
- 판정: 손으로 1~3 rad/s 를 줬는데 |z| > 0.5 가 0 % 면 무반응. 결과 88.6 s · 114.7 s, |z| ≤ 0.041(SUMMARY).
- 결함: 시간 = 샘플 수 / 50 — echo 가 표본을 놓치면 시간이 짧게 나온다(180 s 녹화가 114.7 s 로 나온 것이 그 탓인지, 녹화를 일찍 분석한 탓인지 **미확인**). 출력 원문 없음, 녹화 파일 원천 소실.
- 계보: 08-27 `job4t` → `job4u` 로 그대로 확장(토픽 2 개 · 200/30 Hz).

### 8.4 `job4d.sh` — RealSense 준비 상태 진단
- 하는 일: `uname -r`, L4T 첫 줄, `lsmod` 에 hid_sensor · uvcvideo, `/lib/modules/$(uname -r)` 에서 `hid-sensor*` 파일 검색, `/sys/bus/iio/devices`, realsense · rplidar udev 규칙, librealsense 패키지 버전, Intel apt 저장소, DKMS, `/usr/local` 라이브러리, 그룹, JetsonHacks 클론 여부, 홈 디렉터리 단서.
- 기준: 이전 프로젝트의 `JETSON_REALSENSE_INSTALL.md` 게이트. 출력 원문 없음 → 결과는 08-27 '한 일'(HID 모듈 · iio · udev 없음).
- 재사용: 새 Jetson 점검용으로 그대로 쓸 수 있음.

### 8.5 `job4e.sh` — 저리스크 준비(설치 · udev)
- 하는 일: `apt-get update` → `ros-humble-rplidar-ros` 설치 → realsense 4 패키지 `--only-upgrade` → `/etc/udev/rules.d/99-rplidar.rules`(CP210x 10c4:ea60 → `/dev/rplidar`) → `99-realsense-libusb.rules` 를 deb 동봉본에서, 없으면 설치 버전 태그(`v2.58.3`)의 GitHub 원본에서 받아 설치 → `udevadm` 재로드 · trigger → 디스크 여유.
- 왜 realsense udev: 없으면 iio 권한 오류가 전 스트림을 죽인다(이전 프로젝트 C25, `JETSON_SETUP_BRIEF.md`). 출력 원문 없음.

### 8.6 `job4f.sh` — JetsonHacks 저장소 조사
- 하는 일: `jetson-orin-kernel-builder` · `jetson-orin-librealsense` 클론 → 빌드 스크립트 원문(`get_kernel_sources.sh` · `make_kernel_modules.sh` · `patch-for-realsense.sh` · README) 출력 → 프리빌트 tar 의 `install-realsense-modules.sh` 원문 → `/proc/config.gz` 의 `CONFIG_HID_SENSOR` · `USB_VIDEO_CLASS` · `IIO` · `LOCALVERSION`.
- 결과: 프리빌트는 5.15.148 전용 → 소스 빌드 결정(08-27 판단 2). 출력 원문 없음.

### 8.7 `job4g.sh` (+ `job4g_launch.sh` · `job4g_diag.sh`) — HID 센서 모듈 소스 빌드
- 실행: Jetson, root. `job4g_launch.sh` 가 `/tmp/hid_build.log` 를 지우고 `sudo setsid nohup bash /tmp/job4g.sh` 로 띄운 뒤 5 s 후 로그 3 줄(`job4g_launch.txt`).
- job4g 단계: 모든 출력을 `tee -a /tmp/hid_build.log`.
  1. 빌드 의존성(build-essential · bc · flex · bison · libssl-dev · libelf-dev · kmod · wget).
  2. 커널 소스 `/usr/src/kernel/kernel-jammy-src` 가 없으면 `get_kernel_sources.sh --force-replace`(L4T 자동 감지) → VERSION · `CONFIG_LOCALVERSION="-tegra"` 확인.
  3. uvc 패치 2 종(`patch-for-realsense.sh`) — 실패해도 HID 만 진행(`PATCH_OK` 플래그).
  4. `scripts/config --module` 로 HID 5 종을 m → `make olddefconfig` → 결과 줄 grep(+ `CONFIG_MODVERSIONS`).
  5. `make -j$(nproc−1) Image modules` 를 `time` 으로, 출력은 error · hid · uvcvideo 줄만 grep 후 `tail -40` → 5 개 `.ko` 존재 확인(없으면 `FAIL:missing`) → `modinfo` vermagic.
  6. `/lib/modules/$KVER/kernel/...` 에 설치, 패치가 됐으면 기존 `uvcvideo.ko` 를 `.original` 로 백업 후 교체 → `depmod -a` → `BUILD_SUCCESS`.
- 왜 Image 까지 전체 빌드: 모듈만 빌드하면 `Module.symvers`(심볼 CRC)가 실행 중 커널과 어긋날 수 있어서(판단 2 'vermagic · CRC 정합').
- 출력: `job4g_diag.txt` 안의 `FULL_LOG`(시작 10:23:44 → 소스 준비 10:26:04 → 패치 OK → config → `real 34m36.984s` → 설치 → `BUILD DONE 11:00:54`).
- job4g_diag: make · gcc 프로세스, `top`, `free`, dmesg OOM · kill, 전체 로그, 트리 상태(`.config` · `autoconf.h` · `fixdep` · `Module.symvers` · `modules.order` 시각), 컴파일러 경로, 최근 수정 파일. → 오경보 해소(§5.3).
- 결함: 5 단계 `| grep | tail -40` 이 진행을 숨김(§5.3). 같은 폴더의 `job4g_check1.txt`(`/tmp/job4g.sh` 없음 — 업로드 전 확인으로 보임) · `job4g_progress30.txt` · `job4g_procs.txt` 를 만든 스크립트는 남아 있지 않음.
- 재사용: 커널이 바뀌면(JetPack 업그레이드) 다시 필요. 커널 버전이 같으면 이미 설치된 모듈로 충분(08-28 재부팅 뒤 자동 로드).

### 8.8 `job4i.sh` · `job4j.sh` · `job4k.sh` — 로드 · 바인딩 · 카메라 게이트
- job4i: uptime, `modinfo hid_sensor_hub`(색인됐나), `modprobe` 3 종, `lsmod`, dmesg(taint 등), iio 목록, `/dev/rover` · `/dev/rplidar`, 그리고 bringup 복구(base · ekf). 출력 원문 없음.
- job4j: 모듈 5 종 `modinfo -F vermagic` 표, `modprobe` 3 종, `lsmod`, **카메라가 연결돼 있으면 uvcvideo 교체 보류**(`lsusb | grep 8086`), dmesg, agent · 노드 생존. 출력 `job4j_module_load.txt`: vermagic 5 줄 일치 · 카메라 연결됨 → 교체 보류 · `AGENT_DOWN`.
- job4k: [1] 카메라 노드 종료 → `modprobe -r uvcvideo` → `modprobe uvcvideo`(패치판) → sysfs 에서 8086:0b5c 찾아 속도 출력 → `authorized` 0 → 2 s → 1(USB 재열거) → iio 장치 이름, hid 드라이버 바인딩, dmesg, `lsusb -t` / [2] 45 s 게이트: `realsense2_camera_node` depth 640×480×30 + gyro · accel 200, `unite_imu_method` 1, `initial_reset` true → 22 s 뒤 depth hz(7 s) · IMU hz(8 s) · 샘플 1 개 · 로그 grep(USB type · 오류 · IMU) / [3] bringup 복구.
- 출력 `job4k_rs_gate.txt`: speed 480 Mbps, `iio:device0: accel_3d` · `iio:device1: gyro_3d`, `-> hid-sensor-hub`, depth 25.505, IMU 199.625, `Device USB type: 2.1`, 경고 `IMU Calibration is not available` · `HID set_power 1 failed` · `Motion Module failure`(그래도 IMU 는 199.6 Hz — 영향 없음으로 판단, 08-27 '사소').
- 재사용: job4k [1] 의 재열거 절차는 카메라 재인식이 필요할 때 유효.

### 8.9 `job4l.sh` — IMU 정밀 검증 + LiDAR + 로버 토픽
- [A] iio `buffer/enable` · `scan_elements` 권한과 사용자 그룹(video · plugdev) [B] 카메라 IMU 만 45 s(`initial_reset` false) → 15 s hz, 샘플 전체(각속도 · 가속), accel · gyro · imu 토픽 목록, 로그 경고 집계 [C] LiDAR 게이트(`/dev/rplidar`, `/scan` hz, frame · 각도 · 거리 메타, 유한 거리 n/min/max/median) [D] `/wheel_odom` · `/odometry/filtered` hz.
- 출력 `job4l_imu_lidar.txt`: IMU 199.637 Hz, 가속 (1.049, −9.767, 0.118), `accel/sample` · `gyro/sample` 원시 토픽도 발행(판단 4 의 '실측: unite=1 에서도 원시 토픽 함께'), `/scan` 10.015 Hz · 1605 점, `/wheel_odom` 50.002, filtered 26.613.

### 8.10 `job4m.sh` → `job4n.sh` — D455f 를 EKF 에 연결
- job4m: rover_bringup 빌드 → `camera.launch.py enable_depth:=false enable_color:=false`(IMU 만, USB2 대역 절약) → IMU hz → ekf · conditioner 재시작(20 s) → 컨디셔너 로그(`bias|stationary`) · `/imu/data` hz · frame_id · filtered hz · `tf2_echo base_link camera_imu_optical_frame` · EKF 경고 → 40 s 정적 yaw.
- 결함: 출력 파일 `job4m_ekf_d455.txt` 내용이 `Binary file (standard input) matches` 한 줄뿐 — 로그에 제어 문자가 섞여 `grep` 이 이진 파일로 판단하고 내용을 버렸다(추정: ros2 로그의 색 코드 등). **원천 소실**.
- job4n('텍스트 안전'): 같은 검증부를 `grep -a` 와 `cut -c` 로 다시. 출력 `job4n_ekf_d455_verify.txt`: 바이어스 (−0.00106, −0.00007, −0.00031) · σ (0.0022, 0.0026, 0.0015), `/imu/data` 199.686 Hz, TF (0.066, 0.017, 0.251) / RPY (−90, 0, −90), **정적 z 0.0 / w 1.0 두 번 다 · vyaw 0.0** — 무음 실패의 첫 증거.
- 이후 이 날 모든 grep 에 `-a` 가 붙는다(계보상의 수정).

### 8.11 `job4o.sh` — 융합 여부 진단
- 하는 일: 현재 시각, 네 토픽(`/imu/data` · `/camera/camera/imu` · `/wheel_odom/conditioned` · `/odometry/filtered`)의 header.stamp 1 개씩, `/imu/data` 발행 · 구독자 QoS(Reliability · Durability), 보정 자이로 z 10 개, filtered vyaw 10 개, 카메라 `global_time_enabled`, EKF `imu0` · `imu0_config`.
- 결함: stamp 를 `echo --once` 로 차례로 받아 각 줄 사이 시간이 흘러 '지연' 비교에는 못 씀(그래서 job4p). `/imu/data` z 는 광학 z(로봇 전방축) 성분이라 정지 노이즈일 뿐 — 그래도 '0 이 아님' 의 증거로는 충분.
- 출력 `job4o_ekf_imu_diag.txt`: vyaw 10 개 모두 0.0, `imu0_config` 12 번째(인덱스 11) True.

### 8.12 `job4p.sh` — 토픽별 수신 지연(시각 가설 판별)
- 파이썬 노드 `latency_probe`: 다섯 토픽을 `qos_profile_sensor_data` 로 구독, 콜백마다 (노드 시계 now − header.stamp) × 1000 ms 저장, 4 s 동안 → 토픽별 n · 평균 · 최소 · 최대. 이어서 EKF `smooth_lagged_data` · `history_length` · `sensor_timeout` · `transform_time_offset`.
- 판정: IMU 가 휠보다 덜 신선하면 '오래된 측정 폐기' 가능 → 결과는 반대(IMU +2.0 ms vs 휠 +13.8 ms) → 기각.
- 출력 `job4p_latency.txt`. 재사용: 개념은 09-01 `job16f_latency.sh`(콜백 내 지연)로 다시 쓰임.

### 8.13 `job4q.sh` — EKF debug 모드(결정적 판별)
- 하는 일: launch 의 EKF 종료 → 같은 `ekf.yaml` 로 `ros2 run robot_localization ekf_node … -p debug:=true -p debug_out_file:=/tmp/ekf_debug.txt` 15 s → 파일 크기 · 토픽 언급 횟수(`imu0_*` · `odom0_*`) · 변환 · 무시 · 드롭 줄 집계 · 첫 imu0 콜백 앞뒤 12 줄 · stdout 경고 → launch 로 EKF 복구.
- 출력 `job4q_ekf_debug.txt`: 710,900 줄 / 77.7 MB, `imu0_twist` 23,518 회 → 측정은 처리됨, `camera_imu_optical_frame->base_link transform` 2,354 회, 원래 update 벡터 `(… false true false …)`(인덱스 11). `job4q_updatevec.txt`(같은 디버그 파일에서 뽑은 추가 grep — 그 명령 원문은 없음): 변환 뒤 `(false … true(인덱스 9) …)`, 측정 Rotational 이 축이 바뀐 값.
- 주의: debug 파일이 15 s 에 77 MB — 오래 켜 두면 디스크를 채운다.

### 8.14 `job4r.sh` — 축 수정 배포 · 확인
- 하는 일: 고친 `ekf.yaml` 만 복사 → 빌드 → 설치본에서 `imu0_config` 마지막 두 줄 출력 → EKF 재시작 20 s → 바이어스 로그 → filtered vyaw 8 개('이제 작은 0 아닌 값이어야') → hz → 30 s 정적 yaw.
- 출력 `job4r_axis_fix.txt`: vyaw −0.0022 ~ +0.0021, 29.998 Hz, z 0.000633 → 0.001536(Δyaw = 2·(asin 차) ≈ 0.10°). 재사용: 정적 N 초 yaw 차 패턴.

### 8.15 `job4t.sh` → `job4u.sh` — 손 회전 동적 검증(D455f)
- job4t: 기존 녹화 정리 → 백그라운드 두 개: `timeout 180 ros2 topic echo /imu/data --field angular_velocity.y`(광학 y = 로봇 −yaw) → `/tmp/gyro_rec.txt`, `/odometry/filtered --field twist.twist.angular.z` → `/tmp/yaw_rec.txt` → 4 s 뒤 줄 수. 주석은 150 s, 코드는 180 s — 출력 `job4t_rec_start.txt`('(150s)', gyro 834 줄) 와 `job4t_rec_start2.txt`('(180s)', 694 줄)로 보아 두 번 녹화했고 남은 파일은 두 번째 판.
- job4u: 두 파일을 읽어 samples · n/hz(200 · 30 가정) · min · max · std · |v| > 0.3 · > 1.0 개수 · 2 s 창 최대 줄.
- 출력 `job4u_hand_rotation.txt`: 자이로 7323 샘플(36.6 s 환산), EKF 1102(36.7 s). 2 s 창 최대 자이로 `0.01 … 1.40 3.00 2.64 1.46 1.97 1.81 0.42 0.01 …`, EKF `0.00 … 0.96 2.12 0.85 0.69 1.72 0.46 0.41 0.00 …`.
- 결함: 180 s 녹화인데 두 파일 모두 ≈ 37 s 분량 — 녹화 도중(시작 ≈ 40 s 뒤) 분석했거나 echo 누락(**미확인**). 시간축이 '샘플 수 / 명목 Hz' 라 두 줄의 창이 실제 시각으로 맞춰졌다는 보장 없음. §6 의 비대칭도 이 결함과 엮여 있을 수 있음.

### 8.16 `job4v.sh` → `job4w.sh` — USB 대역폭
- job4v: [0] `lsusb -t` + 8086:0b5c · 10c4:ea60 · 1a86:7523 의 sysfs 속도 · 제품명 [1] 카메라 풀스트림(depth 640×480×30 + color 640×480×15 + IMU) 확보, `dmesg -C` [A] LiDAR 확보 후 scan · depth · color · imu · odom 다섯을 **병렬로** `ros2 topic hz --window 100` 15 s → 표 + 그 동안 USB 오류(error · fail · reset · bandwidth · babble · overflow · no space) + 카메라 로그 드롭 [B] LiDAR 끄고 카메라 단독 [C] LiDAR 재시작 + `top` 상위 6.
- 결함: [A] 의 scan 칸이 빈 줄 — LiDAR 가 아직 발행 전이었음 → job4w 가 '발행 확인 후' 같은 동시 측정을 다시 함.
- job4w: scan · depth 사전 hz → 다섯 동시 15 s → dmesg USB 오류(부팅 뒤 전체) → LiDAR 로그.
- 출력: `job4v_usb_bandwidth.txt`(토폴로지 · B · CPU: python3 41.2 % · realsense 17.6 % · rplidar 11.8 % · ekf 5.9 %) · `job4w_usb_simul.txt`(동시 표). 'python3 = sensor_conditioner' 는 SUMMARY 의 해석(top 은 이름만 보임).

### 8.17 `job4x.sh` — 통합 `sensors.launch.py` + SLAM 스모크
- 하는 일: 빌드 → 개별 launch · 노드(camera · lidar · ekf · realsense · rplidar · conditioner · foxglove) 종료 → `sensors.launch.py` 35 s → 노드 · 바이어스 로그 · 오류 → 다섯 토픽 hz → `slam.launch.py` 15 s → `/map` hz · `map→odom` · `map→lidar_link` · map info · slam 경고 → foxglove 포트 8765.
- 출력 `job4x_sensors_slam.txt`(위 흐름 표). 이 파일의 `/wheel_odom` 49.995 Hz 가 CLAUDE.md 의 '2 Mbps 에서도 08-27 에는 안정' 근거로 인용됨(→ 보드 연결 카드).

### 8.18 슬립 · 기타 (간단 표)
| 도구 | 하는 일 | 출력 | 비고 |
|---|---|---|---|
| `job4a.sh` | Step 4 apt 후보 버전(rplidar · sllidar · slam_toolbox · realsense · foxglove · laser_filters)과 설치분, USB 장치 | 원문 없음 | 사전 조사 |
| `job4b.sh` · `job4c.sh` | Intel `_d455.urdf.xacro` 의 `d455_cam_*` · `bottom_screw_frame` · imu 원점 · `d455_imu_p[xyz]` 와 joint 체인(55~75 행) 출력 | 원문 없음 | IMU 오프셋 (−16.0, −30.2, +7.4) mm 의 출처 |
| `job4s.sh` | **빈 파일**(0 줄) | — | 내용 없음 |
| `job4z.sh` | 인자 `W`(기본 0.3) `T`(기본 4): 정지 1.5 s → `/cmd_vel` 회전 T s → 정지 2 s 동안 `/imu/data` 의 **−angular_velocity.y**(광학 −y = 로봇 yaw)와 `/wheel_odom` vyaw 를 stamp 기준 사다리꼴 적분 → 비 = 자이로/휠 | 원문 없음 | 08-27 장착 후용 준비. → job5b |
| `job5b.sh` | job4z 의 4 연속판(L-slow +0.3×4 · L-fast +0.5×3 · R-slow −0.3×4 · R-fast −0.5×3) + 정지 확인 | `job5b_w4_recalib.txt` | 사용자 `!` |
| `job5c.sh` | `SLIP_PTS` 0.46 판 배포 → sensors 재시작 35 s → 바이어스 · hz → 30 s 정적 yaw | `job5c_slip_apply.txt`(0.017°/30 s) | — |
| `job5d_*.txt` | (스크립트 없음) 자이로 누적 방위 재구성과 사용자 육안 대조 정리 | `job5d_w4_external_validation.txt` | W4 외부 검증 |

제외(같은 날이지만 다른 줄기): `job4h`(URDF xacro 배포) · `job4y`(LiDAR yaw 정렬) · `job5a`(URDF bringup — 세션 측면은 [보드 연결 카드](board-link-microros-session.md)).

## 9. 용어
- **ICM-20948 / RM3100**: 보드에 실린 9 축 IMU(가속 · 자이로 · 자기) / 자기계. 이 시기 자이로 무반응 · 자기 무발행으로 둘 다 미사용.
- **바이어스(자이로)**: 정지해도 0 이 아닌 일정한 출력. 그대로 적분하면 yaw 가 일정 속도로 샌다(−0.0072 rad/s ≈ −0.41°/s 원시값).
- **covariance(공분산)**: 측정이 얼마나 불확실한지의 숫자(분산 = σ²). EKF 는 이것으로 센서별 신뢰를 나눈다. 0 이면 robot_localization 이 아주 작은 값으로 바꿔 '완벽한 측정' 처럼 쓴다 → 펌웨어의 0 은 위험.
- **REP-145 orientation_covariance[0] = −1**: IMU 메시지에서 '자세(orientation)를 주지 않음' 을 뜻하는 약속.
- **robot_localization `*_config`**: 센서마다 15 개 true/false(x y z · roll pitch yaw · vx vy vz · vroll vpitch vyaw · ax ay az)로 '이 측정의 어느 성분을 쓸지' 고른다. **센서 메시지의 frame_id 축 기준**이며 EKF 가 TF 로 base_link 축으로 돌린다.
- **two_d_mode**: 평면 로봇 가정 — z · roll · pitch 와 그 속도를 0 으로 고정. 다른 축으로 잘못 들어간 yaw 속도가 여기서 조용히 사라졌다.
- **광학 프레임(optical frame)**: 카메라 관례 축 — x 오른쪽, y 아래, z 앞. 로봇 관례(x 앞, y 왼쪽, z 위)와 다르다. 그래서 로봇 yaw 속도 = 광학 −y 성분.
- **HID 센서 허브 · iio**: D455f 의 IMU 는 USB HID 센서 장치로 붙고, 리눅스 `hid-sensor-hub` 드라이버가 이를 iio(Industrial I/O) 장치(`iio:device0=accel_3d`, `iio:device1=gyro_3d`)로 노출한다. 이 모듈이 커널에 없으면 IMU 스트림이 안 나온다.
- **vermagic · modversions(CRC)**: 커널 모듈에 새겨진 '어느 커널용인가' 문자열과 심볼 시그니처. 실행 중 커널과 다르면 로드가 거부된다 — 그래서 같은 소스 · config 로 `Image` 까지 빌드했다.
- **uvcvideo 패치**: RealSense 의 추가 영상 형식 · 메타데이터를 UVC 드라이버가 알게 하는 패치. IMU 에는 필요 없고 선택 사항이었다.
- **USB 재열거(`authorized 0→1`)**: sysfs 에서 장치를 잠깐 끊었다 다시 붙여 드라이버 바인딩을 새로 하게 하는 방법 — 재부팅 대신 썼다.
- **USB 2.1(480M) vs 3.2(5000M)**: 같은 카메라라도 케이블 · 포트에 따라 고속(480 Mbps) 또는 SuperSpeed(5 Gbps)로 붙는다. SuperSpeed 레인과 USB2 레인은 신호가 분리돼 서로 대역을 나눠 쓰지 않는다.
- **`unite_imu_method`**: realsense-ros 가 따로 오는 가속 · 자이로를 한 `Imu` 메시지로 합치는 방식(1 = copy, 2 = 보간). 로버 EKF 는 자이로 1 축만 쓰므로 무관(08-27 판단 4).
- **sensor_conditioner**: Jetson 쪽 Python 노드. IMU 바이어스 제거 · covariance 주입, 휠 오도 covariance · 계수 보정 후 `/imu/data` · `/wheel_odom/conditioned` 로 다시 발행. 임시 shim(`TODO(production)` 라벨).
- **회전 슬립 계수**: 스키드스티어 트랙은 제자리 회전 때 미끄러져 휠이 말하는 각도보다 덜 돈다. 실회전/휠 비(이 시기 0.46).
- **EKF debug 모드**: robot_localization 이 측정 수신 · 변환 · 갱신 과정을 파일로 자세히 남기는 모드. 무음 실패를 직접 보는 유일한 창이었다.
