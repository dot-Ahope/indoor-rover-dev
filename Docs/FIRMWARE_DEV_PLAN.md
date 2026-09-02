# Rover F405 펌웨어 개발 계획

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-001 |
| 버전 | 1.0 |
| 작성일 | 2026-05-14 |
| 대상 H/W | STM32F405RGT6 / ALOPS Jupiter R1.4 (하드웨어 수정본) |
| 상위 문서 | `PROJECT_OVERVIEW.md` |

---

## 1. 확정된 설계 결정

| 항목 | 결정 | 비고 |
|---|---|---|
| MCU | **STM32F405RGT6** | F103RCT6에서 교체. Cortex-M4F 168MHz, FPU, 1MB Flash, 192KB RAM(128KB + 64KB CCM) |
| 통신 | **micro-ROS** | F405가 직접 ROS2 노드. XRCE-DDS over UART |
| RTOS | **FreeRTOS** | micro-ROS 실행 및 태스크 구조화에 필수 |
| STM32 라이브러리 | STM32F4 HAL (CubeMX 생성) | 타이밍 핫패스만 LL 고려 |
| 툴체인 | STM32CubeMX + VS Code(PlatformIO) 또는 STM32CubeIDE | 핀 설정은 CubeMX |
| ROS2 / micro-ROS | Humble | Jetson과 버전 일치 |

### 1.1 micro-ROS 채택으로 달라진 점
- 기존 커스텀 시리얼 프로토콜(`ROVER_SERIAL_PROTOCOL_v1.0.md`)은 **F103의 RAM 부족 때문에** 설계된 것 → F405 채택으로 전제 소멸, **micro-ROS로 대체**
- Jetson 측 `rover_bridge` 변환 노드 **불필요** → `micro_ros_agent`만 실행
- F405가 직접 `/cmd_vel` 구독, `/wheel_odom`·`/imu` 발행

---

## 2. 하드웨어 수정 기록

F103RCT6 → F405RGT6 교체 시 LQFP-64 64핀 중 62핀은 동일하나, **Pin 31·Pin 47**이 F103에서는 VSS(GND), F405에서는 VCAP(내부 1.2V 레귤레이터 출력)임.

적용된 수정 (사용자 완료 · 동작 확인됨):
- 방식: **핸드 리워크** (보드 리비전 아님)
- Pin 31, Pin 47을 GND 연결에서 분리
- 각 핀 → GND 간 안정화 캐패시터 추가 (적정 용량)
- F405 부팅·동작 확인 완료

검증 권장 항목 (개발 진행하며):
- 8MHz HSE 크리스털 → F405 PLL 168MHz 설정에서 안정 동작
- VDD 디커플링 (168MHz 동작 기준)
- VDDA 노이즈 (F405 ADC 사용 시)

### 2.1 모터 드라이버 제어 방식 (확정)
AM2861 H-브리지는 **부호-크기(sign-magnitude) 방식**으로 구동:

| 동작 | IA | IB |
|---|---|---|
| 전진 | PWM | Low |
| 후진 | Low | PWM |
| 정지 | Low | Low |

→ **펌웨어 함의**: 모터당 IA·IB **둘 다 타이머 PWM 채널**에 연결되어야 함
(방향에 따라 한쪽이 PWM, 다른 쪽은 듀티 0). 2모터 → PWM 채널 4개 필요.

### 2.2 차체·모터 파라미터

> ⚠ **모터 변경 이력**: JGB37-520 30:1 (초기) → 통합 드라이버형 56:1 (2026-07-08)
> → **1:90 통합 드라이버형 (2026-08-26, 현재)**. 최신 확정값은 `App/app/rover_platform.h` 참조.

| 항목 | 값 | 출처 |
|---|---|---|
| 휠 유효 반경 | 0.0257 m (유효 Ø51, 트랙 포함 — 바닥 실주행 3.72m 합산 캘리브레이션 2026-08-26) | `rover_platform.h` |
| 트랙 베이스 폭 | 0.190 m | `wheel_separation` |
| 차체 질량 | 3.0 kg | `inertial` |
| 모터 | 12V 7W, 기어비 1:90, 무부하 45 rpm / 정격 37 rpm | 모터 사양표 |
| 피드백 | FG 펄스, 휠 1회전당 **541.5 → 542 (실측 2026-08-26)** | L/R 각 20턴 → ≈10830 카운트. 6 FG/모터회전 × 실기어비 90.25 |

계산값 (오도메트리 설계 기준):
- 휠 유효 둘레 = 3.720 m ÷ 12500카운트 × 542 = **0.1613 m** (일치하는 2개 런 합산, 상호 편차 0.15%)
- 최대 속도(이론): 정격 37 rpm → 0.099 m/s, 무부하 45 rpm → 0.121 m/s
  - 실측: duty 98%에서 ≈0.115 m/s — **duty-속도 곡선은 부하 무관** (받침대·바닥 동일,
    모터 내장 속도제어 추정). 곡선 비선형: 30mm/s→72%, 50→92%, 70→94%, 98%→115
  - `/cmd_vel` saturation = **0.100 m/s** (`MAX_LINEAR_SPEED_MPS`, 실측 기반)
- FG 카운트당 거리 = 0.1613 / 542 ≈ **0.298 mm** (실주행 캘리브레이션, 2.8m 검증 ±0.2%)
- 차동구동 역기구학: `v_left = v − ω·0.095`, `v_right = v + ω·0.095`
  (베이스 폭/2 = 0.095 m)

(구형 Ø50 휠 + 1320 CPR 쿼드러처 파라미터는 `rover_platform.h`의 AM2861 블록에 보존)

### 2.3 F405 핀 배정표 (확정)

회로도 `ROVER_MECURY_R10` page 2 기준. F103↔F405 62/64핀 동일하므로 그대로 적용.
사용하지 않는 신호는 펌웨어에서 미할당(아래 "미사용" 참조).

**전원·시스템**

| Pin | 포트 | 네트 | 비고 |
|---|---|---|---|
| 1 | VBAT | 3.3V | |
| 5 / 6 | PD0 / PD1 | XTAL_IN / OUT | 8 MHz HSE 크리스털 |
| 7 | NRST | /RESET | |
| 60 | BOOT0 | BOOT0 | |
| 12 / 13 | VSSA / VDDA | — | 아날로그 전원 |
| 18, 63 | VSS | GND | |
| 31, 47 | (F405 VCAP) | — | **핸드리워크 캡 적용** (F103에선 VSS) |
| 19, 32, 48, 64 | VDD | 3.3V | |

**디버그 — SWD (ST-Link 사용 중)**

| Pin | 포트 | 네트 |
|---|---|---|
| 46 | PA13 | SWDIO |
| 49 | PA14 | SWCLK |

→ SWD 전용. JTAG 비활성화 → PA15·PB3을 엔코더 입력으로 사용 가능.

**모터 PWM — M1, M3 (AM2861 sign-magnitude, IA·IB 각각 PWM)**

| Pin | 포트 | 네트 | 타이머 채널 |
|---|---|---|---|
| 37 | PC6 | M1A (IA) | TIM3_CH1 (또는 TIM8_CH1) |
| 38 | PC7 | M1B (IB) | TIM3_CH2 (또는 TIM8_CH2) |
| 41 | PA8 | M3B (IB) | TIM1_CH1 |
| 44 | PA11 | M3A (IA) | TIM1_CH4 |

**엔코더 — H1, H3 (직교, 타이머 엔코더 모드)**

| Pin | 포트 | 네트 | 타이머 |
|---|---|---|---|
| 50 | PA15 | H1A | TIM2_CH1 |
| 55 | PB3 | H1B | TIM2_CH2 |
| 14 | PA0 | H3A | TIM5_CH1 |
| 15 | PA1 | H3B | TIM5_CH2 |

> H3A=PA0: 회로도 page 2에 NC로 잘못 표기됐으나 **실제 연결됨** (사용자 확인).
> F405의 TIM2·TIM5는 32-bit 카운터 → 엔코더 오버플로 여유 큼.

**통신**

| Pin | 포트 | 네트 | 용도 |
|---|---|---|---|
| 42 | PA9 | TX1 | USART1_TX → Jetson (micro-ROS) |
| 43 | PA10 | RX1 | USART1_RX → Jetson |
| 53 | PC12 | TX5 | UART5_TX → 디버그 콘솔 |
| 54 | PD2 | RX5 | UART5_RX → 디버그 콘솔 |

**IMU — ICM-20948 (SPI2)**

| Pin | 포트 | 네트 | 기능 |
|---|---|---|---|
| 33 | PB12 | NSS | SPI2_NSS |
| 34 | PB13 | SCLK | SPI2_SCK |
| 35 | PB14 | SDO | SPI2_MISO |
| 36 | PB15 | SDI | SPI2_MOSI |
| 25 | PC5 | INT1 | EXTI — 데이터레디 인터럽트 |

**자기계 — RM3100 (I2C1)**

| Pin | 포트 | 네트 | 기능 |
|---|---|---|---|
| 58 | PB6 | (I2C1_SCL) | RM3100 |
| 59 | PB7 | (I2C1_SDA) | RM3100 |

**보조 I/O**

| Pin | 포트 | 네트 | 기능 |
|---|---|---|---|
| 29 / 30 | PB10 / PB11 | SCL / SDA | I2C2 — OLED 등 보조 |
| 2 | PC13 | LED | GPIO 출력 — 상태 LED |
| 45 | PA12 | SW_LED | GPIO 출력 — LED 제어 |
| 27 | PB1 | Buzzer | GPIO 출력 — **능동 부저 (on/off)** |
| 26 | PB0 | BAT | ADC1_IN8 — 배터리 전압 |
| 24 | PC4 | KEY1 | GPIO 입력 — 버튼 |

**미사용 (펌웨어 미할당)**

M2A(PC8), M4A(PB2), M5A(PC9), S1~S4(PC3/PC2/PC1/PC0),
UART2(PA2/PA3), UART3(PC10/PC11), CAN, RS485(D/R/485_en),
GPS I2C(PB8/PB9), RELAY_OUT, PC14·PC15(32kHz 크리스털 없음 → 미사용).

**타이머 배정 요약**

| 타이머 | 용도 | 비고 |
|---|---|---|
| TIM1 | M3 PWM | 어드밴스드 타이머 |
| TIM3 (또는 TIM8) | M1 PWM | TIM8 쓰면 TIM3 해방 |
| TIM2 | H1 엔코더 | 32-bit |
| TIM5 | H3 엔코더 | 32-bit |
| TIM6 / TIM7 | 제어 루프 틱 (1kHz) 후보 | 베이직 타이머 |

---

## 3. 펌웨어 아키텍처

### 3.1 계층 구조 (하드웨어 교체 대비)
```
┌──────────────────────────────────────────────┐
│ App Layer                                    │
│  - MotionController (cmd_vel → 휠 속도)       │
│  - OdometryEstimator (엔코더 → pose)          │
│  - SafetyMonitor (스톨·watchdog·E-stop)       │
│  - MissionState (상태머신)                    │
└──────────────────────────────────────────────┘
                    ↕
┌──────────────────────────────────────────────┐
│ HAL Layer (인터페이스)                        │
│  IMotorDriver / IEncoder / IImu /             │
│  IMagnetometer                                │
└──────────────────────────────────────────────┘
                    ↕
┌────────────────────────┬─────────────────────┐
│ Driver Layer           │ Comm Layer           │
│  AM2861Driver          │  micro-ROS client    │
│  STM32F4 TIM 엔코더    │  (XRCE-DDS / UART)   │
│  ICM20948Driver        │                      │
│  RM3100Driver          │                      │
│  STM32F4 HAL           │                      │
└────────────────────────┴─────────────────────┘
```
**원칙**: App Layer는 STM32F4 HAL·AM2861·micro-ROS API를 직접 호출하지 않음.
MCU·모터드라이버가 바뀌어도 **Driver/Comm Layer만 교체**하면 됨 — 설계 역량을 드러내고 재작업을 줄이는 목적.

### 3.2 FreeRTOS 태스크 구성

| 태스크 | 우선순위 | 주기 | 역할 |
|---|---|---|---|
| `tMotorCtrl` | 최고 | 1 kHz | 속도 PID (정밀 타이밍 필요 → TIM ISR 활용 권장) |
| `tSensor` | 높음 | 200 Hz | ICM-20948 / RM3100 샘플링 |
| `tSafety` | 높음 | 100 Hz | Watchdog, 스톨 감시, E-stop |
| `tMicroRos` | 중간 | — | micro-ROS executor spin (pub/sub 처리) |
| `tDiag` | 낮음 | 10 Hz | RGB LED, 부저, OLED |

- 태스크 간 데이터 공유: FreeRTOS 큐 / 뮤텍스 또는 더블버퍼
- 모터 제어는 타이밍 결정성을 위해 **타이머 ISR**에서 수행하고, 태스크는 게인·지령만 전달하는 구조 권장
- micro-ROS executor는 별도 태스크에서 spin

### 3.3 micro-ROS 통합
- **통합 도구**: `micro_ros_stm32cubemx_utils` (CubeMX 프로젝트용 공식 유틸)
- **Transport**: serial (USART1 → CH340N → USB)
- **Jetson/PC 측**: `micro_ros_agent` 실행
- **빌드**: micro-ROS 정적 라이브러리를 F405용으로 빌드 후 CubeMX 프로젝트에 링크
- **메모리**: micro-ROS 미들웨어 + executor + pub/sub → 수십 KB 수준, F405 128KB 메인 SRAM으로 충분. 스택·고속 데이터는 64KB CCM RAM 활용 가능

---

## 4. micro-ROS 토픽 계약

F405가 직접 발행/구독하는 ROS2 토픽:

| 방향 | 토픽 | 타입 | 주기 | frame_id |
|---|---|---|---|---|
| 구독 | `/cmd_vel` | `geometry_msgs/Twist` | 이벤트 | — |
| 발행 | `/wheel_odom` | `nav_msgs/Odometry` | 50 Hz | `odom` → `base_link` |
| 발행 | `/imu/data_raw` | `sensor_msgs/Imu` | 50 Hz | `imu_link` |
| 발행 | `/imu/mag` | `sensor_msgs/MagneticField` | 25 Hz | `imu_link` |
| 발행 | `/rover/status` | `diagnostic_msgs/DiagnosticArray` | 5 Hz | — |
| 발행 | `/battery` | `sensor_msgs/BatteryState` | 1 Hz | — |

- QoS: 텔레메트리는 **best-effort**, `/cmd_vel`은 reliable 권장
- 좌표·단위: ROS REP-103 (m, m/s, rad, rad/s, X 전방/Y 좌측/Z 상방)
- 시간: micro-ROS time sync 사용 (agent와 동기)

---

## 5. micro-ROS 대역폭 고려 ⚠

표준 ROS2 메시지는 커스텀 바이너리보다 직렬화 크기가 훨씬 큼.

| 메시지 | 대략 직렬화 크기 | 주기 | 대역 |
|---|---|---|---|
| `sensor_msgs/Imu` | ~320 B (공분산 배열 포함) | 50 Hz | ~16 KB/s |
| `nav_msgs/Odometry` | ~720 B (pose+twist 공분산) | 50 Hz | ~36 KB/s |
| `sensor_msgs/MagneticField` | ~100 B | 25 Hz | ~2.5 KB/s |
| 기타 | — | — | ~3 KB/s |
| **합계** | | | **~57 KB/s + XRCE 오버헤드** |

**대응:**
- **921600 bps 필수** (가용 ~92 KB/s, 사용률 약 65~75%)
- 발행률은 위 표 수준으로 보수적 설정, 필요 시 조정
- 초기 단계에서 발행률을 낮게 시작해 안정성 확인 후 상향
- best-effort QoS로 과부하 시 자연 드롭 허용
- 대역 부족 시 검토: CH340N 더 높은 baud(최대 ~2Mbps) 또는 F405 네이티브 USB CDC 전환(보드 배선 확인 필요)

---

## 6. 개발 단계

| 단계 | 내용 | 기간 | 검증 방법 |
|---|---|---|---|
| **F0** | CubeMX F405 프로젝트(168MHz, FreeRTOS), ST-Link, blink+UART 콘솔, 태스크 골격 — 상세 체크리스트 `F0_CUBEMX_SETUP.md` | 3~5일 | LED·UART 동작 |
| **F1** | F405 핀 배정 확정, 클럭/페리페럴 init, 타이머·AF 할당 | 3~5일 | 페리페럴 초기화 OK |
| **F2** | 모터 개방루프 PWM (AM2861), 스톨 보호 PWM 클램프(80%) | 1주 | 모터 정·역회전 |
| **F3** | 엔코더 (타이머 엔코더 모드), 속도 산출 (float/FPU) | 3~5일 | 카운트·방향 일치 |
| **F4** | 폐루프 속도 PID + 스톨 감지 | 1~2주 | 지령 속도 추종 |
| **F5** | **micro-ROS 통합** — 라이브러리 빌드/링크, serial transport, `/cmd_vel` 구독 → 모터 구동 | 1.5~2주 | PC에서 `ros2 topic pub /cmd_vel` → 모터 회전 |
| **F6** | 차동구동 + 오도메트리 → `/wheel_odom` 발행 | 1주 | RViz에서 odom 확인 |
| **F7** | ICM-20948 + RM3100 드라이버 → `/imu/data_raw`, `/imu/mag` 발행 | 1~2주 | raw 데이터 검증 |
| **F8** | 통합·안전 — Watchdog(cmd_vel 타임아웃), 안전 상태머신, 전체 토픽 스트리밍 | 1주 | end-to-end 동작 |

**총 8~10주.** F8 완료 시 Jetson 없이도 PC + `micro_ros_agent`만으로
"`/cmd_vel` 발행 → 모터 구동 → `/wheel_odom`·`/imu` 수신 → RViz 확인"이 검증됨.
이후 Jetson 단계(SLAM, Nav2)로 진행.

### 6.1 하드웨어 교체 대비 원칙 (전 단계 공통)
- App Layer를 STM32F4 HAL·AM2861·micro-ROS API에 직접 의존시키지 않음
- HAL 인터페이스(`IMotorDriver` 등)로 격리
- micro-ROS 토픽 구조·메시지 의미는 하드웨어가 바뀌어도 동일 유지

---

## 7. 안전 메커니즘 (F103 계획에서 계승)

- **통신 Watchdog**: `/cmd_vel` 500 ms 미수신 → 모터 즉시 정지, FAULT 진입
- **스톨 감지**: 지령 vs 엔코더 변화 200 ms 윈도우 비교 → PWM 차단
- **PWM 최대 80% 제한** (AM2861 스톨 전류 2.3A > 드라이버 한계 대응)
- **적분 와인드업 클램프**
- 모든 안전 로직은 F405 펌웨어에서 처리 (Jetson 응답성 신뢰하지 않음)

---

## 8. 미해결 / 확인 필요

### 8.1 해결됨 (개발 착수 가능)
- [x] 하드웨어 수정 상세 — 핸드 리워크, VCAP 캡 추가, 동작 확인 (§2)
- [x] AM2861 제어 방식 — sign-magnitude (§2.1)
- [x] 휠 반경·베이스 폭 — `Docs/rover.urdf` 확인 (§2.2)
- [x] **F405 핀 배정표** — 회로도 page 2 기준 확정 (§2.3)
- [x] H3A = PA0 — 회로도 누락이었으나 실제 연결 확인
- [x] RM3100 = I2C1 (PB6/PB7), 32kHz 크리스털 없음
- [x] 디버그 = SWD 전용 (ST-Link)
- [x] ALOPS 제공 예제 펌웨어 — 없음

### 8.2 개발 진행하며 확인
- [ ] AM2861 데이터시트 (정확한 정격)
- [ ] VDDA 노이즈 / 디커플링 (168MHz 동작, ADC 사용 시)
- [x] 부저 = 능동형 → PB1 GPIO on/off

---

## 9. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|---|---|---|
| 1.0 | 2026-05-14 | 초기 작성. F405RGT6 + micro-ROS + FreeRTOS 결정 반영, F0~F8 단계 정의 |
| 1.1 | 2026-05-14 | HW수정·AM2861 제어·차체 파라미터 확정 반영(§2.1·2.2). **F405 핀 배정표 §2.3 확정** (회로도 page 2 기준). §8 블로커 해소. |

---

*문서 끝.*
