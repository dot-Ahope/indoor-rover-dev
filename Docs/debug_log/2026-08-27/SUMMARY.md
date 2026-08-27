# 2026-08-27 — Step 4 사전 준비 (데크 분석 · 이전 프로젝트 조사 · D455f 커널 모듈 빌드)

> 진행 중 — 마감 시 갱신. 출력 캡처: `outputs/`, 스크립트: `jobs/`.

## 한 일
- 센서 데크 `lidar_deck_camera_FUSED_ROVER.stl` 파라메트릭 소스 분석 → URDF 오프셋 확정 (`JETSON_SETUP_BRIEF.md` §4-0).
- D455 좌이미저 오프셋을 Jetson의 Intel `realsense2_description` xacro에서 추출 (bottom_screw→camera_link = +11.2, +47.5, +14.5mm; imu = −16.0, −30.2, +7.4).
- 이전 handheld/rover 프로젝트(`Documents\Claude\Projects\Rover`) 조사 → 학습 반영, `JETSON_SETUP_BRIEF.md` Step 4 상세화 + §6 참조 자산.
- Jetson RealSense 준비 상태 진단 (`job4d`): 커널 5.15.185-tegra, HID 모듈·iio·udev 없음, 패키지 구버전.
- 저리스크 준비 (`job4e`): rplidar_ros 2.1.4 설치, librealsense2 2.58.3/realsense2-camera 4.58.3 업그레이드, udev `/dev/rplidar` + `99-realsense-libusb.rules`(v2.58.3).
- 커널 HID 센서 모듈 소스 빌드 시작 (`job4g`, 10:23:44, 백그라운드, 로그 `/tmp/hid_build.log`).
- 워크스페이스 초안: `lidar/camera/slam/foxglove.launch.py`, `slam.yaml`, `rover.urdf.xacro`(데크 인자화, 메시 포함), `description.launch.py`(xacro).
- 디버깅 로그 규약 채택 (`Docs/debug_log/README.md`).
- 센서 측 통합 `sensors.launch.py`(camera+lidar+EKF+foxglove, agent와 분리) + `full.launch.py`(base+sensors, systemd용) 배포·전환. slam_toolbox 스모크 테스트, Foxglove 개통. 장착 후용 스크립트 준비: `job4y`(LiDAR yaw 정렬), `job4z`(자이로 기준 슬립 캘리브레이션).

## 결과 (수치)
| 항목 | 값 |
|---|---|
| 커널 HID 모듈 빌드 | 성공, 34분 37초 (`Image + modules` 전체), vermagic `5.15.185-tegra SMP preempt mod_unload modversions aarch64` 일치, uvcvideo 패치 2종 정상 적용 |
| 재부팅 | **불필요** — 모듈 라이브 로드 + USB 재열거(`authorized 0→1`)로 `hid-sensor-hub` 바인딩, `iio:device0=accel_3d`/`iio:device1=gyro_3d` 생성 |
| D455f IMU | `/camera/camera/imu` **199.6Hz** 안정, 중력 -9.77(광학 -Y), 정지 자이로 바이어스 (-0.0008, -0.0002, -0.0002) rad/s, σ 0.0016~0.0026 |
| D455f USB | **2.1 (480M)** — depth 25.5Hz(30 미달). USB 3 케이블/포트 필요 (IMU 용도엔 무관) |
| RPLidar S2L | `/dev/rplidar`→ttyUSB0, `/scan` 10.015Hz, Standard 16kHz/16m, FW 1.02 HW 18, 1605점 |
| EKF(D455f 자이로 융합) | 30Hz, TF `base_link→camera_imu_optical_frame` (0.066, 0.017, 0.251 / RPY -90,0,-90) 해석, **정적 yaw 드리프트 0.10°/30s ≈ 0.2°/분** (보드 IMU 4.4°/분 대비 22배 개선) |
| 로버 | `/wheel_odom` 50Hz, `/rover_jupiter` 세션 (오늘 09:41 Jetson 재부팅 후 bringup 복구) |
| **USB 대역폭 (job4v/4w)** | 카메라 = Bus 02 USB 3.2 **5000M**(온보드 허브 2-1.3), LiDAR = Bus 01 USB 2 하위 외장 허브 **12M FS**(1-2.4.1), 로버 CH340 = 12M(1-2.1). 카메라 풀스트림(depth 640×480×30 + color 640×480×15 + IMU 200) + LiDAR + 로버 동시: scan 10.02 / depth 28.8 / color 13.3 / imu 199.6 / odom 50.0 Hz — 카메라 단독(depth 29.1 / color 14.6 / imu 199.6)과 동일, dmesg USB 오류 0 |
| **통합 launch + SLAM 스모크** | `sensors.launch.py`: scan 9.99 / imu 199.6 / **depth 30.0**(USB 3) / filtered 30.0 / odom 50.0. slam_toolbox: `/map` 0.5Hz(171×85 @5cm), `map→odom` TF 발행, 로그 경고 1건(min range 0<0.2, 무해). foxglove `ws://192.168.0.101:8765` |
| **손 회전 동적 검증** | D455f 자이로 피크 **±3.0 rad/s**(정지 구간 0.01), EKF vyaw 동일 시간창에 최대 2.12 rad/s 추종 — 자이로 실동작·EKF 융합 축 정합 확인 (보드 IMU는 같은 테스트에서 ≤0.04) |

## 판단·결정 (근거)
1. **LiDAR = S2L 확정**(사용자). 드라이버 1,000,000 baud/Standard/angle_compensate; `lidar_yaw` 기본 π(이전 프로젝트 C8), 실측 확정 필요.
2. **JetsonHacks 프리빌트 HID 모듈 사용 불가** (5.15.148 전용, 현재 5.15.185) → 소스 빌드(A) 채택(사용자 승인). HID 5종은 커널 소스에 있고 config만 꺼짐 → 모듈로 켜서 전체 빌드(vermagic·CRC 정합).
3. uvcvideo 패치 2종은 선택(메타데이터) — 적용 실패 시 스크립트가 자동 되돌리고 HID만 진행.
4. `unite_imu_method`: 결론 "1(copy) 사용"은 이전 팀 자체 실측이 아니라 realsense-ros #2221(VIO 사용자 보고) 인용. 원인은 가속도계 저율 샘플의 보간(가짜 대역폭·불안정 주기). **로버 EKF(자이로 1축만)에는 무관** — 어느 방법이든 자이로 원신호 보존. VIO용은 accel_fps를 자이로와 같은 200Hz 네이티브로 맞추면 보간 자체가 불필요(실측으로 확인 예정). 실측: unite=1에서도 `accel/sample`·`gyro/sample` 원시 토픽이 함께 발행됨.
5. **오경보 교훈**: 빌드 감시 시 `make ... | grep | tail -40` 필터가 완료 전 출력을 묶어 "죽은 빌드"로 오판(실제로는 20초 뒤 성공). 장기 빌드는 원본 로그를 별도 파일로 tee하고 진행 지표(.o 개수·make 프로세스)로 감시할 것.
6. **EKF 무음 실패 → debug 로그로 확정**: filtered vyaw가 정확히 0 → 타임스탬프 가설(기각: IMU +2ms, 휠 +14ms로 IMU가 더 신선) → `debug: true` 로그에서 update 벡터가 인덱스 9(vroll)로 회전됨을 확인 → **robot_localization은 `*_config`를 센서 프레임 기준으로 해석**. 광학 프레임 IMU는 로봇 yaw = 광학 -y → `imu0_config` 인덱스 10(vpitch 자리) 사용. 수정 후 vyaw에 자이로 반영 확인.
8. **USB 대역폭 간섭 없음**: 카메라(SuperSpeed 5Gbps 레인)와 LiDAR·로버(USB2 HS/FS)는 같은 xHCI 컨트롤러를 쓰지만 신호 도메인이 분리돼 있어 대역폭을 공유하지 않는다. 부하도 카메라 ~30MB/s(USB3 실효 ~400MB/s의 8%), LiDAR ~100kB/s로 미미. color 13.3Hz(목표 15)·depth 28.8(목표 30)의 소폭 미달은 단독 조건에서도 같아 버스가 아닌 카메라/드라이버·CPU 측 특성. 참고: `sensor_conditioner`(Python)가 200Hz IMU 처리로 CPU 41% — 양산 전 C++ 이식 또는 IMU 다운샘플 TODO.
7. 재부팅 회피: HID 모듈은 핫플러그 로드, uvcvideo는 카메라 미사용 시 교체 가능 → bringup·보드 리셋 절차 없이 적용. (카메라가 이미 연결돼 있어 USB 재열거로 재바인딩)

## 미해결·다음
- ~~USB 3 케이블/포트~~ → 사용자가 직결로 해결(5000M, depth 30Hz 확인).
- 카메라 `initial_reset: true` 기동 시 accel `buffer/enable` set_power 경고 1회(udev 권한 적용 타이밍) — 자이로·EKF 무영향, 재현 시 `initial_reset:=false` 검토.
- 데크 장착 후 실측 3종(H, D_x, D_y) + LiDAR yaw(h_axis_check 절차) → xacro 인자 확정 → bringup 재시작(보드 리셋 1회).
- 슬립 계수 재캘리브레이션(이제 자이로 기준 가능) → SLAM 맵핑.
- Step 5: base.launch에 camera/lidar/ekf 통합, systemd.
