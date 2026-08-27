# Jetson Phase 2 셋업 지시서 — Claude Code 작업 브리핑

> 이 문서는 **사용자 PC(Windows, 본 저장소)에서 실행되는 Claude Code에게 주는 작업 컨텍스트**다.
> Claude Code는 PC에서 **SSH로 Jetson에 원격 접속**하여 아래 "작업 단계"를 순서대로 수행한다.
> 각 단계는 반드시 검증 기준을 통과한 후 다음 단계로 넘어간다.

---

## 0. 원격 작업 방식 (필독)

- Jetson 접속 정보(호스트·계정·비밀번호)는 **사용자가 프롬프트로 전달**한다. 이 문서나 커밋되는 파일에 비밀번호를 기록하지 말 것.
- 접속은 이전 세션에서 검증된 **WSL + sshpass 패턴**을 사용한다 (`.claude/settings.local.json`의 allow 이력 참고):

```powershell
# 단발 명령
wsl -d Ubuntu -u root -- bash -c "sshpass -p '<PW>' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null <USER>@<HOST> '<명령>'"

# 여러 줄 작업: 로컬에 스크립트 작성 → scp 전송 → 원격 실행
wsl -d Ubuntu -u root -- bash -c "sshpass -p '<PW>' scp -o StrictHostKeyChecking=no /tmp/job.sh <USER>@<HOST>:/tmp/ && sshpass -p '<PW>' ssh -o StrictHostKeyChecking=no <USER>@<HOST> bash /tmp/job.sh"
```

- WSL에 `sshpass` 없으면 먼저 설치: `wsl -d Ubuntu -u root -- apt-get install -y sshpass`
- **장시간 실행 프로세스**(micro_ros_agent 등)는 SSH 세션에 매달지 말 것 — `docker run -d` 또는 `nohup ... &` + 로그 파일로 실행하고, 로그를 별도 명령으로 확인한다.
- **대화형 도구**(teleop_twist_keyboard 등)는 원격 비대화 셸에서 불가 — 사용자에게 직접 실행을 요청하거나, `ros2 topic pub -r`로 대체한다.
- Jetson 쪽 산출물은 `~/ros2_ws/`에, 전송용 스크립트는 `/tmp/`에만 생성한다.

---

## 1. 시스템 컨텍스트

- **하드웨어**: Jetson Orin Nano Super Developer Kit. USB-C 케이블로 로버 제어보드(ALOPS Jupiter R1.4, STM32F405)와 연결됨.
- **목표 OS/스택**: Ubuntu 22.04 + JetPack 6.x + **ROS2 Humble** (설치 여부 먼저 확인, 없으면 설치).
- **펌웨어 (이미 완료, 수정 금지)**: F405가 FreeRTOS + micro-ROS client로 동작. F0~F8 검증 완료.
- **모터**: 1:90 BLDC (무부하 45rpm) — 실측(2026-08-26) duty 98%에서 ≈0.115 m/s, 펌웨어 상한 `MAX_LINEAR_SPEED_MPS = 0.100`. 상위단 속도 파라미터는 **0.100 m/s**를 넘으면 안 되고, 수동 지령은 §3 한계(0.08) 준수.
- **상위 문서** (저장소 내): `PROJECT_OVERVIEW.md`, `Docs/FIRMWARE_DEV_PLAN.md`,
  `Docs/MOTOR_1TO90_MIGRATION_PLAN.md` §5 (Phase 2 계획), `Docs/INDEX.md`.

## 2. 통신 사양 (펌웨어 확정값 — 임의 변경 금지)

| 항목 | 값 | 근거 |
|---|---|---|
| 물리 연결 | F405 USART1 → CH340N → USB-C → Jetson | `microros_transport.c` |
| 시리얼 장치 | `/dev/rover` (udev 심볼릭 링크) | 기본적으로 CH340은 `ttyUSB*`로 잡히나, 설치된 드라이버에 따라 `ttyCH341USB*` 등 다른 이름일 수 있음. `lsusb`로 CH340(1a86:7523)을 찾아 실제 tty 장치명을 확인하고, 심볼릭 링크가 없으면 udev 규칙으로 `/dev/rover` 생성 (Step 0 참조). 이후 모든 단계는 `/dev/rover` 사용 |
| **Baud rate** | **2,000,000 bps** | `Core/Src/usart.c`: 921600을 런타임 override. agent에 `-b 2000000` 필수 |
| 프로토콜 | micro-ROS serial (XRCE-DDS), MTU 1024 | F8 최적화 확정값 |
| QoS | 고주기 토픽은 **BEST_EFFORT** | 구독 시 QoS 불일치하면 데이터 안 보임 |

### ROS2 토픽 계약 (F8 확정)

| 방향(F405 기준) | 토픽 | 타입 | 주기 |
|---|---|---|---|
| 구독 | `/cmd_vel` | `geometry_msgs/Twist` | event |
| 발행 | `/wheel_odom` | `nav_msgs/Odometry` | 50 Hz |
| 발행 | `/imu/data_raw` | `sensor_msgs/Imu` | 50 Hz ⚠ 값은 나오나 **실기동 검증(2026-08-26)에서 자이로가 실제 회전에 무반응** — 융합 사용 금지. D455f IMU로 대체 예정 |
| 발행 | `/imu/mag` | `sensor_msgs/MagneticField` | ⚠ **무발행** (`mag.valid` 항상 false — 보드 측 자기계 읽기 실패) |
| 발행 | `/battery` | `sensor_msgs/BatteryState` | 1 Hz |
| 발행 | `/rover/status` | `diagnostic_msgs/DiagnosticArray` | 5 Hz |
| 발행 | `/rover/f5b_heartbeat` | `std_msgs/Int32` | 1 Hz |

## 3. 안전 규칙 (Claude Code가 반드시 지킬 것)

1. `/cmd_vel` 발행 테스트는 **바퀴가 지면에서 뜬 상태**를 사용자에게 확인받은 후 수행.
2. 속도 지령은 linear.x ≤ 0.08 m/s, angular.z ≤ 0.8 rad/s 이내.
3. 펌웨어 watchdog: `/cmd_vel` 500ms 미수신 시 자동 정지 — teleop 종료로 정지 가능함을 활용.
4. 펌웨어·보드 쪽 설정은 변경하지 않는다. 문제 의심 시 사용자에게 보고만.
5. `sudo` 필요 작업은 실행 전에 무엇을 왜 하는지 한 줄로 알리고 진행.

## 4. 작업 단계

### Step 0 — 환경 점검
```bash
cat /etc/os-release            # Ubuntu 22.04 확인
dpkg -l | grep nvidia-jetpack  # JetPack 확인
ls /opt/ros/                   # humble 있는지
lsusb | grep 1a86              # CH340(1a86:7523) 보드 연결 확인
ls -l /dev/ttyUSB* /dev/ttyCH341USB* /dev/rover   # tty 장치명 확인 (드라이버에 따라 다름)
groups                         # dialout 포함 여부
```
- ROS2 Humble 미설치 시: 공식 데비안 패키지로 `ros-humble-ros-base` + `ros-dev-tools` 설치.
- `dialout` 그룹에 없으면 `sudo usermod -aG dialout $USER` 후 재로그인 필요(사용자에게 알림).
- CH340의 tty 장치명은 드라이버에 따라 다르다 (기본 커널 ch341 → `ttyUSB*`, WCH 벤더 드라이버 → `ttyCH341USB*`). 장치명을 하드코딩하지 말 것.
- `/dev/rover` 심볼릭 링크가 없으면 udev 규칙으로 생성 후 리로드:
  `/etc/udev/rules.d/99-rover.rules` → `SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="rover", GROUP="dialout", MODE="0660"`
  이후 모든 단계는 `/dev/rover`만 참조한다.

### Step 1 — micro_ros_agent 설치·통신 검증 ★ 최우선 마일스톤
설치는 다음 중 가용한 방법 선택 (우선순위 순):
1. `sudo apt install ros-humble-micro-ros-agent` (패키지 존재 시)
2. Docker: `docker run -it --rm --net host --device $(readlink -f /dev/rover):/dev/rover microros/micro-ros-agent:humble serial --dev /dev/rover -b 2000000` (심볼릭 링크는 실장치로 resolve해서 전달)
3. 소스 빌드 (micro_ros_setup)

실행:
```bash
ros2 run micro_ros_agent micro_ros_agent serial --dev /dev/rover -b 2000000
```
보드 리셋(RESET 버튼) 후 세션 수립 로그 확인.

**검증 기준**:
```bash
ros2 topic list                            # §2 토픽 전부 보여야 함
ros2 topic hz /wheel_odom                  # ≈50 Hz (Humble의 hz verb는 --qos-reliability 플래그 없음, QoS 자동 적응)
ros2 topic hz /imu/data_raw                # ≈50 Hz
ros2 topic echo /battery --once            # 전압값 정상 (≈12V 계열)
```

### Step 2 — ros2_ws 골격 + teleop 주행 확인
```
~/ros2_ws/src/
  rover_description/   # 저장소 Docs/rover.urdf 기반 (휠 유효반경 0.02567m=Ø51 — 펌웨어 rover_platform.h 실측과 일치 확인. 구 Ø40 스프로킷 기준값은 기각됨)
  rover_bringup/       # launch: micro_ros_agent + (이후 추가 노드들)
```
- colcon 빌드 환경 구성, `rover_bringup/launch/base.launch.py` 작성.
- `teleop_twist_keyboard`로 저속 주행 테스트 (안전 규칙 §3 준수, 속도 스케일 0.05부터).

### Step 3 — robot_localization EKF
- `ekf_node`: `/wheel_odom` → `/odometry/filtered` (30Hz). **휠 단독 융합** — 보드 IMU는 자이로 무반응 판명(2026-08-26)으로 제외, D455f IMU 도입 시 `imu0` 복원.
- 펌웨어 covariance=0(unknown) 보완: `sensor_conditioner` 노드가 `/wheel_odom/conditioned`로 covariance 주입.
- **회전 슬립 보정 (속도 의존)**: 실측(2026-08-26) 트랙 스크럽 슬립이 속도에 따라 증가 —
  |vyaw|≈0.20 rad/s에서 계수 0.42 (휠 36.2°/실 15°), ≈0.57 rad/s에서 0.28 (휠 106.4°/실 30°).
  컨디셔너에서 2점 선형보간 적용. **맵핑·주행 시 각속도 ≤0.4 rad/s 권장** (캘리브레이션 신뢰 구간).
  LiDAR 확보 후 스캔매칭 기준 다점 정밀 재캘리브레이션 필요.
- two_d_mode: true. 프레임: odom → base_link.
- 검증: 제자리 회전·직진 시 `/odometry/filtered` 발산 없음.

### Step 4 — LiDAR + D455f + SLAM (2026-08-26 상세화 — 이전 handheld 프로젝트 학습 반영)

> 근거 자료: `C:\Users\magma\Documents\Claude\Projects\Rover\` (이전 handheld/rover 프로젝트, §6 참조 자산).
> 센서 확정: **RPLidar S2L** (사용자 확인) + **Intel RealSense D455f**. 센서 데크 = `tools/handheld/rig_mount_v1/stand/stl/lidar_deck_camera_FUSED_ROVER.stl`.

#### 4-0. 데크 형상 → URDF (데크 원점 = LiDAR 마운트 중심·데크 하면, ROS 축)
| 프레임 | 데크 원점 기준 (mm) | 근거 |
|---|---|---|
| `lidar_link` | (0, 0, +25.8) | 데크 5 + S2L 스캔면 20.8 (CAD) |
| `camera_link` (D455 좌이미저) | (+82.2 ±2, +47.5, −16.5) | 벽 58 + 몸체중심 13 + Intel xacro 11.2 / py 0.0475 / M4축 높이 |
| IMU·광학 프레임 | 드라이버 자동 발행 (`camera_link` 하위, imu = (−16.0, −30.2, +7.4)) | realsense2_description |

**장착 후 실측 필요 (데크 원점 ↔ `base_link`)**: ① H = 지면→LiDAR 하면 높이 (스캔면 = H+20.8) ② D_x = LiDAR 중심의 트랙 길이 중점 기준 전후 오프셋 ③ D_y = 좌우 오프셋 ④ 수평 잔류 기울기(3.5° 보상 설계 검증) ⑤ 스캔면보다 높은 로버 부속 유무(음영 필터).

#### 4-1. LiDAR (S2L)
- 패키지: `ros-humble-rplidar-ros` 2.1.4 (apt, S2 지원). udev: CP210x `10c4:ea60` → `/dev/rplidar`.
- 파라미터(이전 프로젝트 실측 확정): `serial_baudrate 1000000`, `scan_mode Standard`(16m, 10Hz), `angle_compensate true`, `inverted false`, `frame_id lidar_link`.
- **yaw 정렬 필수**: rplidar_ros 출력은 오른손계이나 **x축이 하드웨어 후방**(케이블측 0° 관례) → 이전 리그에서 `lidar_yaw = π` 확정(케이스북 C8). 데크는 케이블 슬롯이 +Y라 방향이 다를 수 있음 → `h_axis_check.sh` 방식(카메라 정면 0.3m 손 → 최근접 섹터 → 90° 격자 스냅)으로 실측해 URDF에 기입.
- 게이트: `/scan` 10Hz, Foxglove에서 벽이 차체 기준 올바른 방향.

#### 4-2. D455f — 설치 (현 Jetson은 RealSense 전제조건 전무 상태, 2026-08-26 진단)
| 진단 항목 | 현재 상태 | 조치 |
|---|---|---|
| 커널 | **5.15.185-tegra** (L4T R36.5.0) | ⚠ JetsonHacks 프리빌트 HID 모듈은 5.15.148 전용(vermagic 불일치) → **소스 빌드 필요** (`jetson-orin-kernel-builder` + `build/patch-for-realsense.sh`, HID_SENSOR_HUB/ACCEL_3D/GYRO_3D 모듈 6종 → depmod → 재부팅) |
| HID 모듈·iio 장치 | 없음 | 위 빌드 전까지 **IMU 불가** (`No HID info`) |
| udev 규칙 | 없음 | `99-realsense-libusb.rules` 설치 필수 — 없으면 iio 권한 오류가 **전 스트림을 죽임**(C25). deb 동봉본 우선(`dpkg -L ros-humble-librealsense2`), 없으면 설치 버전 태그에서 다운로드 |
| 패키지 | librealsense2 2.56.4 / realsense2-camera 4.56.4 | apt 업그레이드 → 2.58.x / 4.58.3 (버전 짝 확인: 로그 `Built with` = `Running with`) |
| apt 잔재·dkms·/usr/local | 깨끗함 | 유지. **금지 경로**: Intel apt 리포+dkms(Tegra 커널 파괴), RSUSB 소스빌드(멀티스트림 30→7Hz 드랍, C12), apt+소스빌드 혼용 |
- 실행 파라미터: `camera_name camera`(→ 프레임 `camera_link`, URDF와 일치하므로 별도 static TF 불필요), `enable_gyro/accel true`, `gyro_fps/accel_fps 200`, `unite_imu_method 1`(copy), `initial_reset true`, `publish_tf true`. 4.55+ 파라미터명 `depth_module.depth_profile/infra_profile`, `rgb_camera.color_profile` (구명칭은 **조용히 무시됨**, C16). USB는 **3.x 포트** 필수(로그 `Device USB type: 3.2`).
- `unite_imu_method` 판단(2026-08-27 분석): 이전 팀의 "2(보간) 부적합" 결론은 자체 실측이 아니라 realsense-ros #2221(D455 VIO 사용자 보고: 보간 IMU의 주기 불안정·프레임 누락으로 VSLAM 추적 열화) 인용. 원인은 가속도계 네이티브 샘플률이 자이로보다 낮을 때 드라이버가 자이로 타임스탬프에 맞춰 accel을 **선형보간(가짜 대역폭)** 하고, 보간에 다음 샘플이 필요해 지연·주기 흔들림이 생기는 구조. **로버 EKF(자이로 z만 융합)에는 무관** — 1/2 어느 쪽도 자이로 원신호를 바꾸지 않음. 더 깔끔한 대안은 `unite_imu_method 0` + `/camera/camera/gyro/sample` 직접 구독. VIO 용도로는 `accel_fps`를 자이로와 동일한 네이티브 200Hz로 맞추면 보간 자체가 사라짐(D455 accel 100/200Hz 지원) — 실장 후 `/camera/camera/accel/sample` hz·dt 통계로 확인 예정.
- 게이트: depth 30Hz + IMU 200Hz 동시, 로그에 `Permission denied`/`No HID` 없음. 반복 재기동 시 스트림 열화(C23) → 재부팅 후 첫 기동 원칙, `jetson_clocks` 적용.
- **USB 배치 (2026-08-27 실측)**: 카메라는 Type-A 직결 → 온보드 허브 USB 3 측(Bus 02, 5000M, `Device USB type: 3.2`). LiDAR(CP2102N 12M)·로버(CH340 12M)는 USB 2 측(Bus 01) — 외장 허브 경유 가능. **대역폭 간섭 없음** (풀스트림 동시 측정: scan 10.0 / depth 28.8 / color 13.3 / imu 199.6 / odom 50.0 Hz, USB 오류 0). 카메라를 USB 2로 잡히게 하면 depth 25Hz로 저하되므로 케이블·포트는 USB 3 유지.
- **IMU 미확보 시 대안**: 카메라는 IMU off로 depth/color만 운용(V4L2 apt 경로는 HID 무관), EKF는 휠 단독 유지, SLAM 스캔매칭이 회전 보정. IMU는 커널 모듈 빌드 완료 후 활성.

#### 4-3. D455f IMU → EKF 복원
- `sensor_conditioner`의 IMU 경로를 `/camera/camera/imu`로 리맵 → 부팅 정지 판정·바이어스 제거·covariance 주입 → `ekf.yaml` `imu0` 주석 해제(**자이로 z만**).
- **가속도 융합 금지**: 이전 로버 EKF(2026-05-29)에서 accel 바이어스 이중적분으로 정지 중 위치 t² 발산 실측. 이전 handheld EKF(C9)는 자이로 바이어스 −5.2°/min 적분으로 yaw 34°/5분 드리프트 → IMU 제외했으나, 로버는 휠 vyaw=0 구속 + 부팅 바이어스 캘리브레이션이 있어 조건이 다름 (보드 IMU에서 4.4°/분으로 검증됨).
- IMU frame_id는 `camera_imu_optical_frame`(광학 축) — EKF가 TF로 변환하므로 드라이버 `publish_tf`가 켜져 있어야 함.
- **⚠ `imu0_config` 축 함정 (2026-08-27 디버그로 확정)**: robot_localization은 `*_config`를 **센서 프레임 기준**으로 해석해 측정값과 함께 TF로 회전시킨다. 광학 프레임(x우/y하/z전방)에서 로봇 yaw = 광학 **-y** → config의 **vpitch 자리(인덱스 10)** 를 켜야 한다. 'vyaw' 자리(광학 z)를 켜면 로봇 롤 속도로 매핑돼 2D 모드에서 무시됨(증상: filtered vyaw가 정확히 0). 검증법: `debug: true` 로그의 "After applying transform to base_link, update vector" 줄.
- 검증(2026-08-27 완료): 손 회전 녹화에서 자이로 ±3.0 rad/s, EKF vyaw 최대 2.12 rad/s 추종 확인. 정적 드리프트 0.2°/분. → 데크 장착 후 회전 슬립 계수를 자이로 기준으로 재캘리브레이션.

#### 4-4. SLAM (slam_toolbox 2.6.10 설치됨)
- 이전 프로젝트 `rover_bringup/param/slam.yaml`(보수적 표준값)을 베이스로: `base_frame base_link`(현 EKF 출력과 일치), `minimum_travel_distance 0.05~0.1`·`minimum_travel_heading 0.05~0.1`(저속 로버), `max_laser_range 12`, `resolution 0.05`, 루프클로저 기본값.
- 주행 속도 0.05~0.08 m/s, **각속도 ≤0.4 rad/s**(슬립 캘리브레이션 신뢰 구간).
- 시각화: `foxglove_bridge`(설치됨, `:8765`) + PC Foxglove Studio.
- 게이트: 폐루프 복귀 시 맵 어긋남 없음, map→odom TF 안정. 맵 저장 `map_saver_cli`.

#### 4-4b. launch 구성 (2026-08-27 배포)
- `base.launch.py` = Docker agent + RSP(xacro) — **재시작 시 보드 RESET 필요**
- `sensors.launch.py` = camera + lidar + foxglove + (8s 후) EKF — 센서/EKF 재시작은 이것만 (agent 무관)
- `slam.launch.py` = slam_toolbox(online async) · `full.launch.py` = base + sensors (Step 5 systemd용)
- 시각화: PC Foxglove Studio → `ws://192.168.0.101:8765`

#### 4-5. 순서
1. (프린트 대기 중) rplidar_ros 설치, udev 2종, librealsense apt 업그레이드, **커널 HID 모듈 소스 빌드(sudo+재부팅, 사용자 승인)**, launch/URDF 초안
2. (장착 후) 실측 3종 → URDF 확정 → bringup 재시작(보드 리셋 1회) → LiDAR yaw 정렬 → 카메라 게이트 → IMU 복원·검증 → 슬립 재캘리브레이션 → 맵핑

### Step 5 — 통합 bringup + 자동 실행
- `rover_bringup`에 전체 launch 통합.
- systemd 서비스 등록은 **사용자 확인 후** 진행.

## 5. 진행 방식

- 각 Step 완료 시 검증 결과(명령 출력 요약)를 보고하고 다음 Step 진행 여부를 확인받는다.
- 실패·불확실 지점은 추측으로 넘어가지 말고 질문한다 (특히 LiDAR/RealSense 모델, 바퀴 공중 여부).
- 펌웨어 소스·문서는 PC의 현재 저장소에서 직접 읽는다 (Jetson에 clone 불필요).
- Jetson에 생성하는 파일은 `~/ros2_ws/` 아래에만 (전송용 임시 스크립트는 `/tmp/`).
- `Docs/전자회로기초/`, `Docs_Beginner/`는 사용자 학습 자료 — 읽거나 참조하지 않는다.

## 6. 참조 자산 — 이전 handheld/rover 프로젝트 (2026-08-26 조사)

경로: `C:\Users\magma\Documents\Claude\Projects\Rover\` (본 저장소와 별개, 읽기 전용 참조)

| 자산 | 경로 | 활용 |
|---|---|---|
| RealSense Jetson 설치 가이드 (금지 경로·4단계·진단표) | `docs/handheld/JETSON_REALSENSE_INSTALL.md` | Step 4-2 절차 원본 |
| 디버깅 케이스북 (C1~C24) | `docs/handheld/DEBUG_CASEBOOK.md` | C8 LiDAR yaw, C9 IMU 바이어스, C12 RSUSB 역전, C16 파라미터 개명, C23 스트림 열화, C25 udev |
| IMU 융합 실패·재도전 조건 | `docs/handheld/IMU_FUSION_RETRY.md` | VIO(cuVSLAM) 트랙 참고 — 로버 EKF와는 조건 다름 |
| 자동화 스크립트 | `tools/handheld/h104_diag.sh`(진단) · `h104_fix.sh`(udev) · `h_kernel_hid.sh`(5.15.148 전용) · `h_axis_check.sh`(LiDAR yaw) · `h_imu_sanity.sh` · `h_cam_reset.sh` | 원격 실행 패턴 그대로 재사용 (NOPASSWD 전제 → 본 프로젝트는 `echo pw \| sudo -S`로 대체) |
| 이전 세대 rover_bringup | `ros2_ws/src/rover_bringup/{launch,param,udev}` | `rplidar.launch.py`·`slam.yaml`·`ekf.yaml`(rejection threshold)·`99-rplidar.rules`·`twist_mux`/`teleop`(Step 5) |
| `cov_relay.py` | `ros2_ws/src/rover_bringup/rover_bringup/` | 본 프로젝트 `sensor_conditioner.py`가 상위호환(covariance + 바이어스 + 슬립) |
| rover_navigation (Nav2 params) | `ros2_ws/src/rover_navigation` | Step 5+ 이식 후보 |
| 데크 설계 소스 | `tools/handheld/rig_mount_v1/stand/gen_rover_deck.py`, `gen_deck_bracket_fused.py` | URDF 치수 원본 (§Step 4-0) |
| Jetson 실행 계획 (J0~J7) | `docs/planning/JETSON_PLAN.md` | micro_ros_agent 소스빌드 대안(`~/uros_ws`), Nav2 속도 한계 산정 방식 |
