# Rover 자율주행 개발 프로젝트 개요

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-DOC-001 |
| 버전 | 1.0 |
| 작성일 | 2026-05-14 |
| 회사 | ALOPS Robotics (엘럽스로보틱스) |
| 목적 | Claude Code 작업 시 참조 문서, 프로젝트 전반 정의 |

---

## 0. Claude Code 작업 지침

### 0.1 컨벤션
- 모든 답변과 코드 주석은 한글 우선, 식별자(변수·함수명)는 영문
- 솔직하게, 사실 기반으로 답변
- 모든 설계 결정은 **양산 이식 가능성**을 최우선 가치로 검토
- 임시방편 코드 작성 시 반드시 `// TODO(production):` 주석 표기

### 0.2 관련 문서
- `CLAUDE.md` — 사용자 지침
- `PROJECT_OVERVIEW.md` — 본 문서, 프로젝트 전반
- `docs/FIRMWARE_DEV_PLAN.md` — **F405 펌웨어 개발 계획 (현행, 펌웨어 작업 시 우선 참조)**
- `ROVER_SERIAL_PROTOCOL_v1.0.md` — [대체됨] micro-ROS 채택으로 폐기, 기록 보존용
- `docs/F103_to_G474_pin_migration.md` — [철회됨] 핀호환 분석 오류 정정 기록
- `docs/rover_top_down_layout.svg` — dev 로버 조감도 (URDF 작성 참고)

### 0.3 작업 디렉토리 구조 (제안)
```
C:\Project\Rover\Rover\
├── CLAUDE.md
├── PROJECT_OVERVIEW.md             ← 본 문서
│
├── firmware/                       (펌웨어 컨테이너)
│   └── rover_jupiter_fw/           (STM32F405 CubeMX 프로젝트)
│       ├── rover_jupiter_fw.ioc    (CubeMX 설정)
│       ├── App/                    (우리 코드: app/ hal/ drivers/ microros/)
│       ├── Core/ Drivers/ Middlewares/   (CubeMX 생성)
│       └── Makefile                (빌드, CubeMX 생성)
│
├── ros2_ws/                        (Jetson ROS2 workspace)
│   └── src/
│       ├── rover_description/      (URDF)
│       ├── rover_msgs/             (custom messages, 필요 시)
│       ├── rover_bringup/          (launch 파일, micro_ros_agent 포함)
│       └── rover_navigation/       (Nav2 설정)
│
└── docs/
    ├── FIRMWARE_DEV_PLAN.md        ← F405 펌웨어 개발 계획
    ├── rover_top_down_layout.svg
    └── ...
```

---

## 1. 프로젝트 개요

### 1.1 제품 정의
- **품목**: 자율주행 농업용 로버
- **운영 환경**: 실내 → 실외 (단계적 확장)
- **양산 단가 목표**: 대당 500만원 이상
- **개발 형태**: 두 단계 분리 (소형 dev → 풀스케일 양산)

### 1.2 적용 시나리오 (양산기)
- 과일 따기 (매니퓰레이터)
- 작물 수분 작업
- 농약 발포 (분무)
- **현재 의사결정 필요**: 1차 양산 시 한 가지 작업 집중 권장 (작업기 모듈 교체식 설계는 별개 고려)

### 1.3 양산기 사양 (목표)
- **크기**: 약 2m (길이) × 1m (폭), 높이 미정
- **구동**: 4WD 또는 스키드스티어 4WD 전망
- **전원**: 48V 계열 (배터리 + 모터 드라이버 사양에 따름)
- **메인 컴퓨터**: Jetson Orin 계열 유지 가능성
- **FC 검토**: ArduRover + CUAV X7+ Pro 또는 동급 (실외 RTK GPS 필요 시)

---

## 2. 개발 전략 — 두 단계 분리

### 2.1 단계 구분

| Phase | 목표 | 기간 | 산출물 |
|---|---|---|---|
| Phase 1 | **소형 dev 플랫폼** — 소프트웨어 스택 검증 | 0~6개월 | ROS2 패키지, F405 펌웨어, 시뮬레이션 |
| Phase 2 | **풀스케일 mule** — 기구·구동·전원 검증 (병렬 시작) | 3~9개월 | 풀스케일 베이스 차량 (작업기 없음) |
| Phase 3 | **작업기 통합** — 매니퓰레이터/분무/수분 | 9~18개월 | 완성형 양산기 후보 |
| Phase 4 | **필드 시험** — 실농가 운용 | 15~24개월 | MTBF, 신뢰성 데이터 |

### 2.2 두 단계 분리의 의미
- 소형: **소프트웨어 검증용**으로 한정
- 풀스케일: 기구·구동·전원·작업기 검증 (소프트웨어는 소형에서 이식)
- 풀스케일 시작 시점을 너무 늦추면 안 됨 (Phase 1 중반 시작 권장)

### 2.3 스케일이 안 되는 영역 (소형 → 풀스케일 비선형)
- 모터 토크/관성/제동 거리
- 서스펜션
- 전원 시스템 (12V → 48V)
- 매니퓰레이터 reach·payload·강성
- SLAM 센서 위치·시야각 (캐노피 회피)

---

## 3. 현재 dev 플랫폼 하드웨어

### 3.1 차체
- **형식**: 차동구동 탱크형 트랙 (스키드스티어)
- **크기**: 24cm(폭) × 29cm(길이) × 20cm(높이)
- **트랙**: 좌/우 각 1
- **트랙 휠 반경**: 0.025 m (Ø50 mm, 실측 2026-05-21) — `Docs/rover.urdf` 확인
- **트랙 베이스 폭** (좌/우 트랙 중심 간 거리): 0.190 m — `Docs/rover.urdf` 확인
- **차체 질량**: 약 3.0 kg (URDF 추정값)

### 3.2 메인 컨트롤 보드: ALOPS Jupiter R1.4 (하드웨어 수정본)
- **회로도**: `ROVER_MECURY_R10.20260106.pdf` (Rev 1.0)
- **MCU**: **STM32F405RGT6** (F103RCT6에서 교체)
  - Cortex-M4F @ 168MHz, FPU 내장
  - 1 MB Flash, 192 KB RAM (128 KB 메인 + 64 KB CCM)
  - **HW 수정**: F103↔F405 핀 차이(Pin 31·47 = VCAP) 대응 — VCAP 안정화 캐패시터 추가 (상세는 `docs/FIRMWARE_DEV_PLAN.md §2`)
  - 이 사양 덕분에 micro-ROS · FreeRTOS 운용 가능
- **모터 드라이버**: AM2861 × 2 (M1, M3 채널, 인코더 입력 포함)
- **추가 PWM**: M2, M4, M5 (피드백 없음)
- **IMU**: ICM-20948 (9축, SPI)
- **마그네토미터**: RM3100 (별도 고정밀, I2C)
- **통신 인터페이스**:
  - USB-UART: CH340N (디버깅·통신용)
  - CAN: SN65HVD230 (향후 확장)
  - RS485 × 2: MAX13488 (센서 확장용)
  - UART1/2/3/5 다수
- **부가 기능**: OLED 헤더, RGB LED, 부저, KEY, DIP, 릴레이, ST-Link V3 SPI

### 3.3 모터: JGB37-520
| 항목 | 값 |
|---|---|
| 정격 전압 | DC 12V |
| 정격 속도 | 250 RPM (무부하 330 RPM) |
| 정격 전류 | 1.0 A |
| **스톨 전류** | **2.3 A** |
| 정격 토크 | 3.5 kg·cm |
| 최대 토크 | 5.0 kg·cm |
| 엔코더 | 1320 CPR (출력축 기준) |
| 엔코더 전압 | 3~5 V |
| 추정 기어비 | 약 30:1 |
| 무게 | 150 g |
| 길이 × 직경 | 58 mm × 37 mm |

**계산값** (휠 반경 0.025 m / Ø50 mm 실측 — `Docs/rover.urdf`)
- 휠 둘레: 0.1571 m
- 최대 선속도: 약 0.864 m/s (무부하), 0.654 m/s (정격)
- 카운트당 거리: 0.119 mm (오도메트리 분해능 매우 우수)
- 권장 운용 속도: 실내 SLAM 0.2~0.3 m/s, Nav2 0.3~0.5 m/s

### 3.4 메인 컴퓨터: Jetson Orin Nano Super Developer Kit
- **OS**: Ubuntu 22.04 + JetPack 6.x
- **ROS2**: Humble Hawksbill
- **전원**: ALOPS 보드의 12V_ORIN 라인에서 공급 (⚠ 12V는 정격 9~19V의 하한선)

### 3.5 센서
- **LiDAR**: RPLidar (정확한 모델 미확인, A1 또는 A2로 보임)
- **카메라**: Intel RealSense (D435i 또는 D455로 보임, IMU 내장)
  - VIO(Visual-Inertial Odometry) 가능
  - 내장 IMU는 보드 IMU와 별개로 사용 (VIO 전용)

### 3.6 배터리
- 48V 12셀 → 외부 DC-DC로 12V 강하 후 ALOPS 보드 입력
- 정확한 셀 화학(Li-ion / LiFePO4), 용량 미확인

---

## 4. 하드웨어 이슈와 변경 계획

### 4.1 🔴 Critical — 즉시 대응 필요

**(1) AM2861 스톨 전류 초과**
- AM2861 피크 한계 ≈ 1.8 A, 모터 스톨 2.3 A
- 트랙 걸림 시 드라이버 손상 가능
- **대응 (필수)**:
  - 펌웨어 스톨 감지 (지령 vs 엔코더 변화) → 200ms 내 PWM 차단
  - PWM 최대값 80% 제한
  - 적분 와인드업 클램프
- **중기 대응**: 외장 드라이버(BTS7960, MDD10A 등)로 교체 검토

**(2) VM 라인 전압 실측**
- AM2861 정격 ≤ 11V, 보드 VM 라인이 12V로 보임 → 정격 초과 가능
- 실측 후 11V 초과 시 별도 강압 필요

### 4.2 🟡 Moderate — 개발 중 보완 권장

**(3) IMU 등급**
- ICM-20948 자이로 드리프트 큼
- 양산기에서 BMI088 또는 산업급(VN-100)으로 교체

**(4) Jetson 전원 12V**
- Orin Nano 정격 9~19V, 12V는 하한선
- GPU 부하 피크 시 voltage droop 위험
- 별도 19V DC-DC 또는 USB-C PD 검토

**(5) MCU — F405RGT6으로 교체 완료**
- F103RCT6 → **STM32F405RGT6** 교체 (LQFP-64, 62/64핀 동일, VCAP 2핀만 HW 수정)
- F4 채택으로 FPU·168MHz·192KB RAM 확보 → micro-ROS·FreeRTOS 운용 가능
- 양산기 MCU(G4/H7 등)는 신규 PCB 설계 시 별도 결정
- 상세는 `docs/FIRMWARE_DEV_PLAN.md` 참조

### 4.3 ✅ 그대로 사용
- CAN/RS485 인프라
- 전원 보호 회로 (소프트스타트, 셀프락, TVS)
- RM3100 마그네토미터
- OLED/RGB LED/부저 디버깅 보조

---

## 5. 소프트웨어 아키텍처

### 5.1 시스템 다이어그램
```
┌─────────────────────────────────────────────────┐
│  Jetson Orin Nano (Ubuntu 22.04 + ROS2 Humble)  │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ micro_ros_agent                         │    │
│  │ (XRCE-DDS ↔ ROS2 DDS 브리지)           │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ robot_localization (EKF)                │    │
│  │ wheel_odom + imu → /odometry/filtered  │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────┐  │
│  │ rplidar_ros  │  │ realsense2   │  │ slam  │  │
│  │              │  │ _camera      │  │_toolbox│  │
│  └──────────────┘  └──────────────┘  └───────┘  │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ nav2 (planner, controller, behavior)    │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
            ▲                       │
            │ micro-ROS (XRCE-DDS)  │
            │ serial 921600 / CH340N▼
┌─────────────────────────────────────────────────┐
│  STM32F405 (FreeRTOS + micro-ROS, ALOPS R1.4)   │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │ micro-ROS client                        │    │
│  │ sub /cmd_vel, pub /wheel_odom /imu ...   │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌───────────────┐  ┌───────────────────┐       │
│  │ Motor Control │  │ Sensor Sampling   │       │
│  │ PID @ 1kHz    │  │ IMU @ 200Hz       │       │
│  │ Stall Protect │  │ Encoder @ 1kHz    │       │
│  └───────────────┘  │ Mag @ 50Hz        │       │
│                     └───────────────────┘       │
│  ┌─────────────────────────────────────────┐    │
│  │ Odometry, Safety, Watchdog              │    │
│  └─────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
```
F405가 직접 ROS2 노드로 동작 → Jetson 측 변환 노드(rover_bridge) 불필요.

### 5.2 펌웨어 추상화 (양산 이식 대비)
```
┌─────────────────────────────────────────┐
│ App Layer                               │
│  - MissionStateMachine                  │
│  - SafetyMonitor                        │
│  - MotionController                     │
│  - OdometryEstimator                    │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│ HAL Layer (인터페이스)                  │
│  - IMotorDriver                         │
│  - IEncoder                             │
│  - IIMU, IMagnetometer                  │
└─────────────────────────────────────────┘
                  ↕
┌────────────────────────┬────────────────┐
│ Driver Layer           │ Comm Layer      │
│  - AM2861Driver        │  - micro-ROS    │
│  - STM32F4 TIM 엔코더  │    client       │
│  - ICM20948Driver      │  - XRCE-DDS     │
│  - RM3100Driver        │    over UART    │
│  - STM32F4 HAL         │                 │
└────────────────────────┴────────────────┘
```

**원칙**: 양산 시 Driver/Comm Layer만 교체, App Layer는 그대로.
펌웨어 상세 구조·FreeRTOS 태스크 구성은 `docs/FIRMWARE_DEV_PLAN.md §3` 참조.

### 5.3 ROS2 토픽 구조

| 토픽 | 타입 | 발행 노드 | 주기 |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/Twist` | 외부 (nav2/teleop) | 이벤트 |
| `/wheel_odom` | `nav_msgs/Odometry` | **F405 (micro-ROS)** | 50Hz |
| `/imu/data_raw` | `sensor_msgs/Imu` | **F405 (micro-ROS)** | 50Hz |
| `/imu/mag` | `sensor_msgs/MagneticField` | **F405 (micro-ROS)** | 25Hz |
| `/rover/status` | `diagnostic_msgs/DiagnosticArray` | **F405 (micro-ROS)** | 5Hz |
| `/battery` | `sensor_msgs/BatteryState` | **F405 (micro-ROS)** | 1Hz |
| `/odometry/filtered` | `nav_msgs/Odometry` | robot_localization | 30Hz |
| `/scan` | `sensor_msgs/LaserScan` | rplidar_ros | 10Hz |
| `/camera/*` | (RealSense topics) | realsense2_camera | 30Hz |
| `/map` | `nav_msgs/OccupancyGrid` | slam_toolbox | 이벤트 |

발행률은 micro-ROS 대역폭을 고려한 값 — 근거는 `docs/FIRMWARE_DEV_PLAN.md §5`.

### 5.4 IMU 전략 — 3개 IMU의 역할 분담
| IMU | 용도 | 비고 |
|---|---|---|
| ICM-20948 (보드) | **메인** — wheel odom과 EKF 융합 | 모터 제어와 동기, 시간 동기화 최적 |
| RM3100 (보드) | 보조 컴퍼스 | ICM-20948 자기계 노이즈 보완 |
| RealSense 내장 | VIO 전용 | librealsense + VIO 알고리즘 내부 |

별도 USB IMU는 현재 단계에서 불필요.

---

## 6. 통신 — micro-ROS

F405 채택으로 통신 방식을 **micro-ROS**로 결정. F405가 직접 ROS2 노드로
동작하며, 별도 변환 노드·커스텀 프로토콜이 불필요하다.
(이전 커스텀 시리얼 프로토콜 `ROVER_SERIAL_PROTOCOL_v1.0.md`는 폐기.)

### 6.1 물리 계층
- F405 USART1 → CH340N → USB-C → Jetson `/dev/ttyUSB0`
- **921600 bps** (micro-ROS 메시지 대역폭상 필수)
- micro-ROS serial transport (XRCE-DDS)

### 6.2 구조
- F405: FreeRTOS + micro-ROS client (`micro_ros_stm32cubemx_utils`)
- Jetson/PC: `micro_ros_agent`
- F405가 직접 `/cmd_vel` 구독, `/wheel_odom`·`/imu`·`/imu/mag`·
  `/rover/status`·`/battery` 발행 (토픽 목록은 §5.3)

### 6.3 대역폭 주의
- 표준 ROS2 메시지는 직렬화 크기가 큼 (`sensor_msgs/Imu` ~320B 등)
- 921600 bps 사용률 약 65~75% → 발행률 보수적 설정 필요
- 상세는 `docs/FIRMWARE_DEV_PLAN.md §5`

### 6.4 안전 메커니즘
- F405: `/cmd_vel` 500ms 미수신 시 모터 정지
- F405: 스톨 감지 (200ms 윈도우) → PWM 차단
- F405: PWM 최대 80% 제한, 적분 와인드업 클램프

---

## 7. 핵심 설계 결정 (FAQ)

### 7.1 왜 PX4/ArduPilot을 안 쓰는가?
- PX4는 드론 중심, 로버 지원 약함. ArduRover가 차라리 적합
- 농업 작업기 제어는 ROS2 영역 → FC 도입 시너지 작음
- 실내 SLAM은 PX4의 GPS 가정과 충돌
- **양산기 단계에서 ArduRover + CUAV X7+ Pro 재검토 예정**

### 7.2 통신 — micro-ROS 채택 (F103 시절 결정에서 변경)
- 초기엔 F103 RAM 48KB 한계로 커스텀 바이너리 프로토콜을 설계했음
- **F405RGT6 교체로 192KB RAM 확보 → micro-ROS 운용 가능**
- micro-ROS 채택: F405가 직접 ROS2 노드, 변환 노드 불필요, 양산 아키텍처와 일치
- 트레이드오프: 대역폭 비용 증가 (§6.3) — 921600 bps + 보수적 발행률로 대응

### 7.3 왜 보드 IMU를 메인으로 쓰는가?
- USB IMU는 Linux USB 스택 지터(1~10ms)로 타임 동기 부정확
- 보드 IMU는 엔코더와 같은 MCU에서 동기 샘플링 → EKF 성능 최적

### 7.4 양산 이식 시 ROS2 코드 변경?
- 거의 없음. 토픽 이름·메시지 타입 유지가 핵심 설계 가치
- 변경되는 것: 펌웨어 Driver Layer, MCU, 모터 드라이버, 차체 치수

---

## 8. 개발 로드맵 (체크리스트)

### Phase 0 — 보드 검증 (2~3주)
- [ ] ALOPS 보드 전원 인가, RGB/부저/OLED 동작 확인
- [ ] ST-Link V3 SPI로 펌웨어 업로드 환경 구축
- [ ] M1 채널 1축 폐루프 PID 동작 (단순 PWM 응답 → PID 튜닝)
- [ ] ICM-20948, RM3100 raw 데이터 출력 확인
- [ ] VM 라인 실측 전압 확인 (AM2861 정격 검증)
- [ ] Jetson Orin Nano: JetPack 6 설치, Ubuntu 22.04, ROS2 Humble
- [ ] Jetson ↔ ALOPS UART echo 테스트 (115200 → 921600 단계)

### Phase 1 — F405 펌웨어 (8~10주)
상세 단계(F0~F8)는 **`docs/FIRMWARE_DEV_PLAN.md`** 참조. 요약:
- [ ] F0: CubeMX F405 프로젝트(168MHz, FreeRTOS), 툴체인, blink
- [ ] F1: 핀 배정 확정, 페리페럴 init
- [ ] F2~F4: 모터 개방루프 → 엔코더 → 폐루프 PID + 스톨 보호
- [ ] F5: micro-ROS 통합 (`/cmd_vel` 구독 → 모터 구동)
- [ ] F6: 차동구동 + 오도메트리 → `/wheel_odom` 발행
- [ ] F7: ICM-20948/RM3100 → `/imu/data_raw`·`/imu/mag` 발행
- [ ] F8: Watchdog·안전 상태머신·전체 토픽 스트리밍

### Phase 2 — Jetson ROS2 스택 (4~5주)
- [ ] ROS2 workspace 셋업, colcon 빌드 환경
- [ ] `micro_ros_agent` 설치·실행 (F405 토픽 브리지)
- [ ] `rover_description` 패키지 (URDF/xacro)
- [ ] `robot_localization` EKF 설정
- [ ] `rplidar_ros` 드라이버 통합
- [ ] `realsense2_camera` 드라이버 통합
- [ ] `slam_toolbox` 매핑 launch
- [ ] `rover_bringup` 통합 launch 파일
- [ ] systemd 서비스 등록 (부팅 시 자동 실행)

### Phase 3 — Nav2 자율주행 (3~4주)
- [ ] Nav2 패키지 통합
- [ ] 글로벌 플래너 (NavFn/Smac) 설정
- [ ] 로컬 플래너 (DWB/MPPI) 설정
- [ ] 코스트맵 파라미터 튜닝
- [ ] 목표점 자율 이동 데모
- [ ] 동적 장애물 회피 테스트
- [ ] Behavior Tree 커스터마이즈

### Phase 4 — 인지 (지속)
- [ ] YOLOv8 모델 학습 (농업 객체 — 과일, 작물 등)
- [ ] TensorRT 변환 및 최적화
- [ ] ROS2 인지 노드 통합
- [ ] 인지 기반 미션 시퀀스

### Phase 5 — 양산기 준비 (병렬)
- [ ] 풀스케일 BOM
- [ ] 풀스케일 기구 설계
- [ ] HAL 레이어 STM32G4/H7 포팅 PoC
- [ ] Gazebo 시뮬레이션 환경 (풀스케일 모델)
- [ ] 작업기 우선순위 결정 및 단일 작업 PoC

---

## 9. 양산 이식 전략

### 9.1 dev 보드와 양산기는 별개 설계 (확정)
dev 플랫폼은 ALOPS Jupiter R1.4 보드를 사용하되, MCU를 **F405RGT6으로 교체**
(F4는 F103과 LQFP-64 62/64핀 동일, VCAP 2핀만 HW 수정 — `FIRMWARE_DEV_PLAN.md §2`).

양산기는 차체·전원·모터·드라이버가 모두 바뀌므로 어차피 **완전한 신규 PCB
설계** — 이때 MCU도 함께 결정. (참고: F103↔G4/H7는 VDD/VSS 핀 위치가 달라
drop-in 불가. F4만이 F103과 거의 핀호환이었음.)

### 9.2 양산 이식 변경표

| 영역 | dev (현재) | 양산기 (계획) | 변경 영향 |
|---|---|---|---|
| **PCB** | ALOPS Jupiter R1.4 (수정본) | 신규 설계 | 완전 재설계 |
| **MCU** | STM32F405RGT6 | TBD (G4/H7 등, 신규 PCB에서 결정) | 펌웨어 Driver Layer 교체 |
| **모터 드라이버** | AM2861 (내장, 1.8A) | 외장 고출력 드라이버 | 드라이버 클래스 교체 |
| **통신** | micro-ROS over UART | micro-ROS over UART/CAN | 트랜스포트만 교체 |
| **ROS2 토픽** | §5.3 정의 | **동일 유지** | **변경 없음 ← 핵심 가치** |
| **RTOS** | FreeRTOS | FreeRTOS (동일) | 변경 없음 |
| **IMU** | ICM-20948 + RM3100 | 산업급 검토 (BMI088, VN-100 등) | HAL 교체 |
| **차체** | 24×29×20 cm 트랙 | 2m×1m 4WD (TBD) | URDF 치수 수정 |
| **단가** | (계산 불필요) | 500만원+/대 | — |

### 9.3 이식성을 지키는 방법
PCB·MCU·드라이버가 바뀌어도 다음은 **유지**된다.
- App Layer 펌웨어 로직 (PID, 오도메트리, 상태머신, 안전로직)
- HAL 추상화 인터페이스 (`IMotorDriver`, `IEncoder` 등)
- micro-ROS 토픽 구조·메시지 의미
- FreeRTOS 태스크 구조

→ **HAL 추상화 레이어를 처음부터 잘 설계하는 것이 양산 이식의 핵심.**
F405 펌웨어를 짤 때부터 App Layer가 STM32F4 HAL·AM2861·micro-ROS API에
직접 의존하지 않도록 인터페이스로 분리한다.

---

## 10. 미해결 사항 (TBD)

### 10.1 즉시 실측·확인 필요
- [x] 트랙 휠 반경 0.025 m (Ø50 mm 실측 2026-05-21), 베이스 폭 0.190 m — `Docs/rover.urdf` 확인
- [x] F405 핀 배정표 — 회로도 page 2 기준 확정 (`FIRMWARE_DEV_PLAN.md §2.3`)
- [ ] VM 라인 실측 전압
- [ ] 12V_ORIN 라인 실측 전압·전류 용량
- [ ] 외부 48V→12V DC-DC 컨버터 모델·용량
- [ ] RPLidar 모델 (A1? A2? A3?)
- [ ] RealSense 모델 (D435i? D455?)
- [ ] 배터리 셀 화학·용량

### 10.2 설계 결정 필요
- [ ] 1차 양산기 작업 우선순위 (과일따기 vs 수분 vs 방제)
- [ ] 풀스케일 mule 시작 시점 (Phase 1 어느 시점?)
- [ ] 양산기 FC 도입 여부 (ArduRover + CUAV X7+ Pro)
- [x] 펌웨어 OS — FreeRTOS 확정

---

## 11. 개발 도구·환경

### 11.1 펌웨어 (F405)
- **MCU**: STM32F405RGT6 (Cortex-M4F)
- **초기 설정**: STM32CubeMX (핀맵·클럭·FreeRTOS 생성)
- **IDE**: VS Code + PlatformIO 또는 STM32CubeIDE
- **컴파일러**: arm-none-eabi-gcc
- **디버거**: ST-Link V3
- **OS**: FreeRTOS
- **통신**: micro-ROS (`micro_ros_stm32cubemx_utils`)

### 11.2 ROS2 (Jetson)
- **OS**: Ubuntu 22.04
- **JetPack**: 6.x
- **ROS2**: Humble Hawksbill
- **빌드**: colcon
- **언어**: C++ (성능 노드), Python (launch, 유틸)
- **micro-ROS**: `micro_ros_agent` (F405 토픽 브리지)
- **IDE**: VS Code + Claude Code

### 11.3 시뮬레이션
- **Gazebo**: Garden 또는 Harmonic (ROS2 Humble 호환)
- **RViz2**: 시각화

### 11.4 GCS (지상국, 향후)
- **현재**: 불필요
- **양산기**: QGroundControl (ArduRover 도입 시) 또는 자체 웹 UI

---

## 12. 참고 자료

### 12.1 표준·문서
- ROS REP-103 (좌표·단위): https://www.ros.org/reps/rep-0103.html
- ROS2 Humble: https://docs.ros.org/en/humble/
- Nav2: https://navigation.ros.org/
- micro-ROS: https://micro.ros.org/
- ArduRover: https://ardupilot.org/rover/

### 12.2 데이터시트 (필수)
- STM32F405RGT6 (DS8626): ST.com
- ICM-20948: TDK InvenSense
- RM3100: PNI Sensor
- AM2861: 데이터시트 확보 필요 (정확한 사양 검증용)
- JGB37-520: 쿠팡 판매처 또는 알리바바

### 12.3 라이브러리
- FreeRTOS: https://www.freertos.org/
- STM32 HAL/LL: STM32Cube
- robot_localization: http://docs.ros.org/en/melodic/api/robot_localization/

---

## 13. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|---|---|---|
| 1.0 | 2026-05-14 | 초기 작성 (Phase 0~5 정의, HW 분석, 프로토콜 요약) |
| 1.1 | 2026-05-14 | §9 양산기 MCU를 STM32G474RET6으로 명시 (※v1.2에서 정정됨) |
| 1.2 | 2026-05-14 | **정정**: F103↔G474 drop-in 핀호환 불가 확인. §9를 "dev 보드 유지 + 양산기 신규 PCB" 전략으로 재작성. §4.2 MCU 항목 정정. F103_to_G474 문서 철회. |
| 1.3 | 2026-05-14 | **MCU를 STM32F405RGT6으로 교체** (F4는 F103과 62/64핀 동일, VCAP 2핀만 HW 수정). 통신을 micro-ROS로, RTOS를 FreeRTOS로 결정. §3·§5·§6·§7·§8 갱신. 커스텀 시리얼 프로토콜 폐기. `docs/FIRMWARE_DEV_PLAN.md` 신설. |

---

*문서 끝.*
