# F1 — 페리페럴 검증 체크리스트

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-003 |
| 단계 | F1 (펌웨어 개발 2단계) |
| 대상 | STM32F405RGTx / ALOPS Jupiter R1.4 (수정본) |
| 목적 | F0 코드 생성 위에 드라이버 골격을 올리고, 모든 페리페럴이 init·통신까지 정상 동작함을 실측 확인 |
| 결과물 | UART5 콘솔 출력으로 `motor/enc/imu/mag/adc = OK` 확인 |

---

## 1. F1 단계에서 추가된 것

### 1.1 디렉토리 / 파일

```
firmware/rover_jupiter_fw/App/
├── hal/                          ← App Layer ↔ Driver 사이 인터페이스
│   ├── i_motor_driver.h
│   ├── i_encoder.h
│   ├── i_imu.h
│   └── i_magnetometer.h
├── drivers/                      ← HAL 인터페이스의 구체 구현
│   ├── am2861_driver.[ch]        TIM1+TIM3 PWM, sign-magnitude
│   ├── stm32_encoder_driver.[ch] TIM2+TIM5 엔코더 (32-bit)
│   ├── icm20948_driver.[ch]      SPI2, WHO_AM_I 확인
│   └── rm3100_driver.[ch]        I2C1, REVID 확인
└── app/
    └── f1_sanity_task.[ch]       모든 드라이버 init + 1Hz 라이브 dump
```

- `Makefile`: `App/{drivers,app}/*.c` 빌드 포함, `-IApp/{hal,drivers,app,microros}` 인클루드 경로 추가
- `Core/Src/freertos.c`: 기존 heartbeatTask → `f1SanityTask` 로 교체 (defaultTask = LED 블링크는 유지)

### 1.2 인터페이스 설계 — "linker-as-interface"

App Layer는 `motor_driver_*()`, `encoder_*()`, `imu_*()`, `mag_*()` 함수를 호출.
구현은 `App/drivers/*.c` 가 제공. 양산기 이식 시 driver .c 통째 교체로 끝남.
함수 포인터 struct 보다 단순하고, 본 프로젝트 요구사항(다중 인스턴스 불필요)에 부합.

---

## 2. 빌드 검증 (호스트)

```powershell
cd C:\Project\Rover\Rover\firmware\rover_jupiter_fw
make clean ; make
```

성공 시 `build/rover_jupiter_fw.elf|hex|bin` 생성. 현재 크기 기준:

| 영역 | 크기 | 비고 |
|---|---|---|
| text (Flash) | ~31.5 KB | 1 MB 중 ~3% |
| bss (RAM)   | ~72 KB    | FreeRTOS heap 32 KB 포함 / 128 KB 중 ~56% |

> RAM 여유 충분. F5 micro-ROS 통합 시 heap 48~64 KB 로 상향 예정.

---

## 3. 보드 검증 (사용자 실측)

### 3.1 준비
- ST-Link V3 → SWD 연결
- UART5 콘솔 (PC12=TX, PD2=RX) 115200 8N1
  - USB-UART 변환기 (CH340/CP2102 등)로 PC 연결
  - Tera Term / minicom / PuTTY 등 시리얼 터미널 띄우기
- 배터리 또는 외부 12V 전원 인가 (모터·드라이버 전원)

### 3.2 플래시 & 부팅
- [ ] `STM32_Programmer_CLI -c port=swd -d build/rover_jupiter_fw.bin 0x08000000 -rst`
      (또는 STM32CubeProgrammer GUI)
- [ ] UART5 콘솔에 부팅 배너 출력 확인
  ```
  =========================================
   Rover Jupiter F405 - F0 boot OK
   SYSCLK=168MHz  build=... ...
  =========================================
  ```

### 3.3 F1 sanity 초기화 결과
- [ ] 다음 형식의 한 줄이 콘솔에 출력될 것:
  ```
  [F1-init] motor=OK enc=OK imu=OK(whoami=0xEA) mag=OK(revid=0x22) adc=OK(raw=XXXX)
  ```
- 각 항목별 의미:

| 항목 | 통과 조건 | 실패 시 의심 지점 |
|---|---|---|
| `motor=OK` | TIM1+TIM3 PWM Start 성공 | CubeMX 타이머 init / PWM 채널 매핑 |
| `enc=OK`   | TIM2+TIM5 Encoder Start 성공 | TIM2(PA15/PB3), TIM5(PA0/PA1) AF·핀 |
| `imu=OK(whoami=0xEA)` | SPI2 통신 + ICM-20948 응답 | SPI Mode3, CS(PB12), 센서 전원, SPI mode 핀 |
| `mag=OK(revid=0x22)`  | I2C1 통신 + RM3100 응답 | I2C 풀업, 7-bit 주소 (0x20 기본), 센서 전원 |
| `adc=OK(raw=XXXX)`    | ADC1 IN8(PB0) 변환 성공 | VDDA 디커플링, 배터리 전압 |

> `mag=FAIL` 인 경우 자동으로 `[F1-i2c1 scan] 0xNN ...` 로 발견된 I2C 주소 목록을 출력.
> 표시된 주소가 있으면 `rm3100_driver.h` 의 `RM3100_I2C_ADDR_7BIT` 를 그 값으로 수정.

### 3.4 1Hz 라이브 dump
- [ ] 1초마다 한 줄씩 다음 형식 출력:
  ```
  [F1   12] enc L=  +0 R=  +0  adc=2350  imu_whoami=0xEA  freeHeap=29800
  ```
- [ ] LED (PC13) 0.5초 주기 토글 — defaultTask 동작 확인
- [ ] **엔코더 수동 검증**: 전원 인가 상태에서 좌·우 휠을 손으로 천천히 돌리면
      `enc L=` / `enc R=` 값이 변해야 함.
      - 시계방향 회전 시 부호: 모터 ↔ 엔코더 페어링·극성에 따라 달라짐. F3 단계에서 확정.
      - 한쪽만 변하면 다른 쪽 엔코더 배선·H1/H3 매핑 확인.

### 3.5 모터 PWM 출력 확인 (선택, 오실로스코프 있을 때)
F1에선 듀티 0% 유지가 정상. 다음 핀의 정적 레벨이 Low 인지 확인:
- [ ] PC6 / PC7 (M1): Low
- [ ] PA8 / PA11 (M3): Low

> TIM1 (어드밴스드)는 MOE 가 set 안 되면 출력 비활성. `HAL_TIM_PWM_Start` 가 내부에서 set 함.
> F2 단계에서 듀티를 올리며 본격 검증.

---

## 4. 디버깅 가이드

| 증상 | 추정 원인 | 확인 방법 |
|---|---|---|
| 콘솔에 아무 출력 없음 | UART5 핀 / baud / 변환기 | `Core/Src/main.c` 의 부팅 배너가 RTOS 시작 전에 나오므로 그 단계부터 안 보이면 UART5 자체 문제 |
| `motor=FAIL` | TIM1 BDTR/MOE, TIM3 클럭 | tim.c init 함수, MspInit AF |
| `enc=FAIL` | TIM2 ARR 미설정(0이면 즉시 trigger 안 됨) | tim.c `htim2.Init.Period = 4294967295` 확인 — 현재는 OK |
| `imu=FAIL`, whoami=0x00 또는 0xFF | SPI 미통신 또는 CS 항상 Low | CS=PB12 초기값(현재 RESET → driver 가 SET 으로 올림), SPI prescaler(<7MHz) |
| `imu` whoami=0x00 만 | MISO 미수신, MOSI 만 동작 | PB14(MISO) AF·결선 |
| `mag=FAIL` + 스캔에서 발견 주소 있음 | 7-bit 주소 차이 | `RM3100_I2C_ADDR_7BIT` 수정 |
| `mag=FAIL` + 스캔 비어있음 | I2C 풀업 / 센서 전원 / SCL·SDA 결선 | PB6/PB7 외부 풀업 (보통 4.7k~10k 필요) |
| `adc` raw 가 0 또는 4095 고정 | VDDA 미연결 / PB0 결선 | 보드 회로도 |

---

## 5. F1 완료 기준 (Definition of Done)

- [x] `App/{hal,drivers,app}/` 골격 작성 + 빌드 통과
- [ ] `[F1-init] motor=OK enc=OK imu=OK mag=OK adc=OK` 콘솔에서 확인
- [ ] 휠 수동 회전 시 엔코더 카운트 변동 확인 (양·음방향 둘 다)
- [ ] 1Hz dump 가 끊김 없이 ≥ 1분 출력 지속
- [ ] LED 0.5초 토글 유지 (FreeRTOS 정상 동작)

→ 모두 통과하면 **F1 완료**, F2(모터 개방루프 PWM) 진행.

---

## 6. 알려진 한계 / 의도된 미구현

- **PWM 주파수**: 현재 TIM1=~2.5kHz, TIM3=~1.3kHz (가청대). F2 에서 ~20kHz 로 재튜닝.
- **ICM-20948 본 init**: PWR_MGMT/accel-gyro 설정·INT 활성·DMA burst read 는 F7.
- **RM3100 측정**: CMM 모드 활성·9바이트 burst read·24-bit 부호확장 은 F7.
- **모터 안전 클램프**: PWM ≤ 80% 만 적용. 스톨 감지·watchdog 은 F4, F8.
- **MOTOR_LEFT/RIGHT ↔ M1/M3 매핑**: 잠정 (M1=LEFT, M3=RIGHT). F2~F3 에서 실제 회전 방향 확인 후 확정.

---

*문서 끝.*
