# [대체됨] Rover ↔ Jetson 시리얼 통신 프로토콜 명세서

> ⚠ **이 문서는 폐기되었습니다 (2026-05-14).**
>
> 이 커스텀 바이너리 프로토콜은 **STM32F103RCT6의 RAM 48KB로는 micro-ROS가
> 불가능**했기 때문에 설계되었습니다. 이후 MCU를 **STM32F405RGT6**(192KB RAM)으로
> 교체하면서 그 전제가 사라졌고, 통신 방식을 **micro-ROS**로 결정했습니다.
>
> **현행 통신 설계는 다음을 참조하세요:**
> - `docs/FIRMWARE_DEV_PLAN.md §3~§5` — micro-ROS 통합, 토픽 계약, 대역폭
> - `PROJECT_OVERVIEW.md §6` — 통신 개요
>
> 아래 내용은 기록 보존용으로만 남겨둡니다. 단, 다음은 micro-ROS 설계에서도
> 여전히 유효합니다: 좌표·단위 규약(REP-103), 안전 메커니즘(watchdog, 스톨 보호),
> 메시지가 담는 데이터 항목(→ 표준 ROS2 메시지로 매핑).

---

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-PROTO-001 |
| 버전 | 1.0 (폐기) |
| 작성일 | 2026-05-14 |
| 상태 | **대체됨 — micro-ROS 채택** |
| 대상 H/W | ALOPS Jupiter R1.4 (STM32F103RCT6) ↔ Jetson Orin Nano Super Dev Kit |

---

## 1. 개요와 설계 원칙

### 1.1 목적
STM32F103과 Jetson 간 양방향 실시간 통신을 정의한다. 이 프로토콜은 다음을 만족한다.

- 1kHz 모터 제어 루프의 안정적 명령 수신
- 200Hz IMU 및 100Hz 오도메트리 텔레메트리 전송
- 통신 단절·노이즈 시 안전 동작 보장
- 양산기 단계에서 micro-ROS로의 매끄러운 마이그레이션

### 1.2 설계 원칙
1. **바이너리 프로토콜** — 텍스트 대비 5~10배 효율, 파싱 단순
2. **고정 SOF + CRC** — 노이즈 환경에서도 프레임 동기 회복 가능
3. **시퀀스 번호** — 패킷 손실 검출
4. **Watchdog/Heartbeat** — 통신 단절 시 자동 안전 모드
5. **양산 호환 구조** — 메시지 의미·필드가 ROS2 표준 메시지와 1:1 대응

---

## 2. 물리 계층

| 항목 | 값 |
|---|---|
| F103 측 | USART1 (PA9=TX, PA10=RX) → CH340N → USB-C |
| Jetson 측 | `/dev/ttyUSB0` (CH340 드라이버 자동 인식) |
| Baudrate | **921600 bps** (1차), 460800 bps (대안) |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |
| 인코딩 | Binary, **little-endian** |

---

## 3. 프레임 구조

```
+------+------+------+------+------+------------+------+------+
| SOF1 | SOF2 | TYPE | SEQ  | LEN  | PAYLOAD    | CRCH | CRCL |
| 0xAA | 0x55 | 1B   | 1B   | 1B   | 0~255 B    | 1B   | 1B   |
+------+------+------+------+------+------------+------+------+
```

총 길이: **7 + LEN 바이트** (최소 7, 최대 262)

| 필드 | 크기 | 설명 |
|---|---|---|
| SOF1, SOF2 | 2 B | 시작 동기 (고정값 0xAA 0x55) |
| TYPE | 1 B | 메시지 타입 (0x01~0x7F=명령, 0x80~0xFF=텔레메트리) |
| SEQ | 1 B | 시퀀스 번호 (0~255 순환) |
| LEN | 1 B | PAYLOAD 길이 (0~255) |
| PAYLOAD | LEN B | 메시지별 데이터 (little-endian) |
| CRCH, CRCL | 2 B | CRC-16, [TYPE..PAYLOAD] 구간, big-endian 전송 |

---

## 4. CRC-16/CCITT-FALSE

| 파라미터 | 값 |
|---|---|
| 다항식 | 0x1021 |
| 초기값 | 0xFFFF |
| Reflect In/Out | false |
| XorOut | 0x0000 |

```c
uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= ((uint16_t)data[i]) << 8;
        for (int j = 0; j < 8; j++) {
            crc = (crc & 0x8000) ? (crc << 1) ^ 0x1021 : (crc << 1);
        }
    }
    return crc;
}
```

CRC 검증 범위: TYPE, SEQ, LEN, PAYLOAD (SOF 제외)

---

## 5. 좌표·단위 규약 (ROS REP-103 준수)

### 5.1 차체 좌표계 (base_link)
- **X축**: 전방 (forward, +)
- **Y축**: 좌측 (left, +)
- **Z축**: 상방 (up, +)
- 우손법, yaw 양수 = 좌회전 (반시계, 위에서 볼 때)

### 5.2 단위

| 물리량 | 단위 |
|---|---|
| 위치 | m |
| 선속도 | m/s |
| 각속도 | rad/s |
| 선가속도 | m/s² |
| 각도 | rad |
| 자기장 | μT |
| 시간 | μs (uint32, MCU uptime) |
| 전압 | V |
| 전류 | A |

### 5.3 부동소수 표현
모든 float 필드는 IEEE 754 single precision (4 byte).

---

## 6. 메시지 카탈로그

### 6.1 명령 (Jetson → F103)

#### `0x01 CMD_VEL` — 속도 명령
- 주기: **50 Hz 권장**, 최소 10 Hz
- 페이로드: 8 byte

```c
typedef struct __attribute__((packed)) {
    float linear_x;     // m/s, [-1.0, +1.0]
    float angular_z;    // rad/s, [-3.14, +3.14]
} cmd_vel_t;
```

#### `0x02 CMD_MODE` — 모드 제어
- 주기: 이벤트 기반
- 페이로드: 4 byte

```c
typedef struct __attribute__((packed)) {
    uint8_t enable;       // 0=모터 비활성, 1=활성
    uint8_t estop;        // 1=비상정지
    uint8_t reset_odom;   // 1=오도메트리 0으로 리셋
    uint8_t reserved;
} cmd_mode_t;
```

#### `0x03 CMD_PID` — PID 게인 업데이트 (디버깅용)
- 주기: 이벤트 기반
- 페이로드: 16 byte

```c
typedef struct __attribute__((packed)) {
    uint8_t channel;      // 0=좌, 1=우
    uint8_t reserved[3];
    float kp;
    float ki;
    float kd;
} cmd_pid_t;
```

#### `0x04 CMD_HEARTBEAT` — Keepalive
- 주기: **10 Hz** (CMD_VEL 없을 때만 의무, 보통 CMD_VEL이 대신함)
- 페이로드: 4 byte

```c
typedef struct __attribute__((packed)) {
    uint32_t timestamp_ms;
} cmd_heartbeat_t;
```

#### `0x05 CMD_LED` — LED/부저 제어
- 주기: 이벤트 기반
- 페이로드: 4 byte

```c
typedef struct __attribute__((packed)) {
    uint8_t led_r;        // 0~255
    uint8_t led_g;
    uint8_t led_b;
    uint8_t buzzer;       // 0=off, 1=beep
} cmd_led_t;
```

### 6.2 텔레메트리 (F103 → Jetson)

#### `0x81 TLM_STATUS` — 시스템 상태
- 주기: 10 Hz
- 페이로드: 8 byte

```c
typedef struct __attribute__((packed)) {
    uint8_t  mode;           // 0=DISABLED, 1=ENABLED, 2=ESTOP, 3=FAULT
    uint8_t  fault_flags;    // bit별 플래그 (아래)
    uint16_t cpu_load_pct;   // 0~10000 (×0.01%)
    uint32_t uptime_ms;
} tlm_status_t;

// fault_flags 비트 정의
#define FAULT_STALL_L       (1<<0)
#define FAULT_STALL_R       (1<<1)
#define FAULT_LOW_BATTERY   (1<<2)
#define FAULT_IMU_ERROR     (1<<3)
#define FAULT_OVERCURRENT   (1<<4)
#define FAULT_COMM_TIMEOUT  (1<<5)
```

#### `0x82 TLM_ODOM` — 휠 오도메트리
- 주기: 100 Hz
- 페이로드: 24 byte

```c
typedef struct __attribute__((packed)) {
    uint32_t timestamp_us;
    float x;                 // m, 시작점 기준
    float y;                 // m
    float yaw;               // rad
    float vx;                // m/s (전방 선속도)
    float vyaw;              // rad/s (각속도)
} tlm_odom_t;
```

#### `0x83 TLM_IMU` — IMU (자이로+가속도)
- 주기: 200 Hz
- 페이로드: 28 byte

```c
typedef struct __attribute__((packed)) {
    uint32_t timestamp_us;
    float ax, ay, az;        // m/s²
    float gx, gy, gz;        // rad/s
} tlm_imu_t;
```

#### `0x84 TLM_MAG` — 자기계 (RM3100 권장)
- 주기: 50 Hz
- 페이로드: 16 byte

```c
typedef struct __attribute__((packed)) {
    uint32_t timestamp_us;
    float mx, my, mz;        // μT
} tlm_mag_t;
```

#### `0x85 TLM_ENCODER` — 엔코더 원시값
- 주기: 100 Hz
- 페이로드: 20 byte

```c
typedef struct __attribute__((packed)) {
    uint32_t timestamp_us;
    int32_t  left_count;     // 누적 카운트
    int32_t  right_count;
    float    left_speed_rps; // 출력축 rev/sec
    float    right_speed_rps;
} tlm_encoder_t;
```

#### `0x86 TLM_BATTERY` — 배터리
- 주기: 1 Hz
- 페이로드: 12 byte

```c
typedef struct __attribute__((packed)) {
    float    voltage;        // V
    float    current;        // A (측정 가능 시, 없으면 NaN)
    uint8_t  percentage;     // 0~100
    uint8_t  reserved[3];
} tlm_battery_t;
```

#### `0x87 TLM_ACK` — 명령 응답
- 주기: 이벤트 (명령 수신 시 즉시)
- 페이로드: 4 byte

```c
typedef struct __attribute__((packed)) {
    uint8_t  cmd_type;       // 응답 대상 명령 TYPE
    uint8_t  result;         // 0=OK, 1=INVALID, 2=ERROR, 3=DISABLED
    uint8_t  seq;            // 응답 대상 SEQ
    uint8_t  reserved;
} tlm_ack_t;
```

---

## 7. 신뢰성·안전 메커니즘

### 7.1 통신 Watchdog

**F103 측 (모터 안전):**
- CMD_VEL 또는 CMD_HEARTBEAT를 **500 ms** 이상 미수신 시:
  1. 모터 PWM = 0 즉시 적용
  2. `mode = FAULT`, `fault_flags |= FAULT_COMM_TIMEOUT`
  3. 5초 후 자동 복구 시도, 통신 정상화되면 ENABLED 복귀
- CMD_VEL 수신 후 **200 ms** 내 새 명령 없으면 → 속도 지령 ramp-down (0으로 감속)

**Jetson 측 (장치 감시):**
- TLM_STATUS 1초 이상 미수신 → `/rover/status`에 단절 표시, 알람 발행
- TLM_ODOM 500ms 이상 미수신 → 오도메트리 stale 플래그

### 7.2 스톨 보호 (F103 측)
- 조건: `|cmd_speed| > min_threshold` AND 엔코더 카운트 변화 < 임계 (200 ms 윈도우)
- 동작:
  1. `fault_flags |= FAULT_STALL_L` 또는 `STALL_R`
  2. 해당 채널 PWM 차단
  3. 1초 후 재시도, 3회 연속 stall 시 ENABLED 해제 (사용자 개입 필요)

### 7.3 시퀀스 번호
- 송신 측: 0~255 순환 증가, 메시지 타입별로 별도 카운터
- 수신 측: gap 검출 시 손실 통계 누적 (로깅용)
- **재전송 없음** (실시간 제어 특성)

### 7.4 프레임 무결성
- CRC 불일치 → 프레임 폐기, 파서는 SOF 재탐색 상태로 복귀
- LEN > 255 또는 알 수 없는 TYPE → 폐기 + 통계 카운트

---

## 8. 파서 상태 머신

```
       +-------------------+
       | S0: WAIT_SOF1     |<------+
       +-------------------+       |
              | 0xAA              | (timeout 100ms / CRC fail / 비정상)
              v                    |
       +-------------------+       |
       | S1: WAIT_SOF2     |-other-+
       +-------------------+
              | 0x55
              v
       +-------------------+
       | S2: READ_TYPE     |
       +-------------------+
              |
              v
       +-------------------+
       | S3: READ_SEQ      |
       +-------------------+
              |
              v
       +-------------------+
       | S4: READ_LEN      |
       +-------------------+
              | (LEN ≤ 255?)
              v
       +-------------------+
       | S5: READ_PAYLOAD  |  N=LEN bytes
       +-------------------+
              |
              v
       +-------------------+
       | S6: READ_CRC_HI   |
       +-------------------+
              |
              v
       +-------------------+
       | S7: READ_CRC_LO   |
       +-------------------+
              | CRC OK?
              v
       +-------------------+
       | DISPATCH HANDLER  |---> back to S0
       +-------------------+
```

상태 사이 타임아웃: **100 ms** (한 프레임 내에서 다음 바이트가 안 오면 폐기)

---

## 9. 대역폭 분석

baudrate = 921600 bps, 10 bit/byte (start + 8 data + stop)
→ 유효 대역 = **92,160 B/s**

| 메시지 | 프레임 크기 | 주기 | 대역 (B/s) |
|---|---|---|---|
| TLM_STATUS | 8+7 = 15 | 10 | 150 |
| TLM_ODOM | 24+7 = 31 | 100 | 3,100 |
| TLM_IMU | 28+7 = 35 | 200 | 7,000 |
| TLM_MAG | 16+7 = 23 | 50 | 1,150 |
| TLM_ENCODER | 20+7 = 27 | 100 | 2,700 |
| TLM_BATTERY | 12+7 = 19 | 1 | 19 |
| **상향 합계** | | | **~14,120 (15.3%)** |
| CMD_VEL | 8+7 = 15 | 50 | 750 |
| CMD_HEARTBEAT | 4+7 = 11 | 10 | 110 |
| **하향 합계** | | | **~860 (0.9%)** |

전체 사용률 약 **16%**. 충분한 헤드룸.

---

## 10. ROS2 토픽 매핑 (Jetson 측 `rover_bridge_node`)

| 시리얼 메시지 | ROS2 토픽 | 메시지 타입 |
|---|---|---|
| TLM_ODOM | `/wheel_odom` | `nav_msgs/Odometry` |
| TLM_IMU | `/imu/data_raw` | `sensor_msgs/Imu` |
| TLM_MAG | `/imu/mag` | `sensor_msgs/MagneticField` |
| TLM_ENCODER | `/encoder/raw` | `rover_msgs/EncoderState` (custom) |
| TLM_BATTERY | `/battery` | `sensor_msgs/BatteryState` |
| TLM_STATUS | `/rover/status` + `/diagnostics` | `rover_msgs/RoverStatus` |
| **구독 `/cmd_vel`** | CMD_VEL 송신 | `geometry_msgs/Twist` |
| **구독 `/rover/mode`** | CMD_MODE 송신 | `rover_msgs/RoverMode` |

**EKF (robot_localization)**:
- 입력: `/wheel_odom` + `/imu/data_raw`
- 출력: `/odometry/filtered` (TF: odom → base_link)

---

## 11. 구현 체크리스트

### 11.1 F103 펌웨어 (STM32CubeIDE 또는 PlatformIO)
- [ ] USART1 DMA TX/RX 셋업 @ 921600 bps
- [ ] RX 링버퍼 (≥ 1KB), TX 링버퍼 (≥ 2KB)
- [ ] `crc16_ccitt()` 구현 (테이블 방식 권장, 256B ROM)
- [ ] 파서 상태 머신 (인터럽트 컨텍스트에서 byte-by-byte 처리)
- [ ] 메시지 디스패처 (TYPE → handler 함수 포인터 테이블)
- [ ] CMD_VEL → 차동구동 변환 → 좌/우 PID 입력
  - `v_left = linear_x - angular_z * track_width / 2`
  - `v_right = linear_x + angular_z * track_width / 2`
- [ ] 100 Hz 타이머: TLM_ODOM, TLM_ENCODER 송신
- [ ] 200 Hz 타이머: TLM_IMU 송신
- [ ] 50 Hz 타이머: TLM_MAG 송신
- [ ] 10 Hz 타이머: TLM_STATUS 송신
- [ ] 1 Hz 타이머: TLM_BATTERY 송신
- [ ] Watchdog: 500 ms CMD_VEL 미수신 → 모터 정지
- [ ] 스톨 감지 로직 (지령 vs 엔코더 비교)
- [ ] PID 와인드업 클램프, PWM 최대 80% 제한

### 11.2 Jetson 측 ROS2 노드 `rover_bridge`
- [ ] 패키지 구조: `rover_bridge` (C++ 권장, Python 가능)
- [ ] `serial` 라이브러리 (C++ asio 또는 Python pyserial)
- [ ] 동일 프로토콜 파서 구현 (헤더 단위 공유 가능)
- [ ] `/cmd_vel` 구독 → CMD_VEL 송신 (50 Hz 또는 이벤트)
- [ ] 텔레메트리 수신 → 각 ROS2 토픽 발행
- [ ] TF 발행: `odom → base_link` (또는 EKF에 위임)
- [ ] `/diagnostics` 발행 (통신 통계, fault flags)
- [ ] ros2 launch 파일 (parameter: device, baudrate)
- [ ] systemd service 또는 launch on boot 설정

### 11.3 공용 헤더 (양쪽 공유)
- [ ] `protocol.h` — 메시지 타입 enum, 구조체 정의
- [ ] 빌드 시 정적 어서션으로 sizeof 검증
  ```c
  _Static_assert(sizeof(cmd_vel_t) == 8, "cmd_vel_t size mismatch");
  ```

---

## 12. 버전 관리 및 확장

- 프로토콜 메이저 버전: **1.0**
- 호환성 깨는 변경 시 메이저 증가, 후방 호환 추가는 마이너
- 예약 영역:
  - `0x06~0x7F`: 향후 명령 메시지
  - `0x88~0xFE`: 향후 텔레메트리 메시지
  - `0xFF`: 확장 헤더용 예약 (긴 페이로드 등)

### 향후 추가 후보
- `0x06 CMD_GPIO` — 범용 GPIO 제어 (작업기 트리거 등)
- `0x07 CMD_SERVO` — 시리얼 서보 위치 지령
- `0x88 TLM_GPIO` — 입력 GPIO 상태
- `0x89 TLM_TEMP` — 모터 드라이버, MCU 온도

---

## 13. 양산기 이식 시 변경 고려

이 프로토콜은 양산기(STM32G4/H7 + micro-ROS)로 갈 때 매끄러운 전환을 위해 다음을 미리 준비한다.

| 현재 (dev) | 양산기 | 변경점 |
|---|---|---|
| UART 921600 | CAN 1Mbps 또는 micro-ROS over UART | 물리 계층만 교체 |
| 자체 바이너리 | micro-ROS DDS-XRCE | 메시지 의미 유지, 인코딩만 변경 |
| F103 펌웨어 | G4/H7 펌웨어 + FreeRTOS + micro-ROS | HAL 추상화 덕분에 App 레이어 그대로 |
| `/wheel_odom`, `/imu/data_raw` 발행 | 동일 | **ROS2 토픽 변경 없음 ← 핵심 가치** |

→ Jetson 측 노드는 양산기 이행 시에도 **거의 무수정**.

---

## 14. 참고 자료

- ROS REP-103 (좌표·단위): https://www.ros.org/reps/rep-0103.html
- MAVLink v2 프레임 구조 (영감): https://mavlink.io/en/guide/serialization.html
- CRC-16/CCITT-FALSE 사양: https://reveng.sourceforge.io/crc-catalogue/16.htm
- micro-ROS supported boards: https://micro.ros.org/docs/overview/hardware/

---

*문서 끝.*
