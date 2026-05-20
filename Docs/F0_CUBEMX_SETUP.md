# F0 — STM32CubeMX 프로젝트 설정 체크리스트

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-002 |
| 단계 | F0 (펌웨어 개발 1단계) |
| 대상 | STM32F405RGTx / ALOPS Jupiter R1.4 (수정본) |
| 목적 | `FIRMWARE_DEV_PLAN.md §2.3` 핀맵대로 CubeMX `.ioc` 구성 후 코드 생성 |
| 결과물 | 완성된 `.ioc` + 생성 코드 (FreeRTOS 골격 포함) |

> CubeMX에서 아래 순서대로 설정하세요. 모든 페리페럴 핀을 한 번에 잡아두면
> 이후 F2~F8 단계는 코드만 작성하면 됩니다.

---

## 1. 프로젝트 생성

- [ ] CubeMX → **New Project** → 파트 검색 `STM32F405RGTx` 선택 (LQFP64)
- [ ] 빈 핀맵에서 시작

---

## 2. System Core

### 2.1 RCC (클럭 소스)
- [ ] **High Speed Clock (HSE)**: `Crystal/Ceramic Resonator` ← 8MHz 외장 크리스털 (PD0/PD1)
- [ ] **Low Speed Clock (LSE)**: `Disable` ← 32.768kHz 크리스털 없음

### 2.2 SYS
- [ ] **Debug**: `Serial Wire` ← SWD 전용 (ST-Link), JTAG 비활성 → PA15/PB3 해방
- [ ] **Timebase Source**: `TIM6` ← FreeRTOS 사용 시 SysTick 대신 별도 타이머 권장

### 2.3 GPIO / NVIC
- 페리페럴 설정 후 §8, §9에서 일괄 처리

---

## 3. Clock Configuration (탭)

- [ ] **HCLK** 입력란에 `168` (MHz) 입력 → Enter → CubeMX 자동 해결(Resolve Clock Issues)
- [ ] 결과 확인:
  - SYSCLK 168 MHz, HCLK 168 MHz
  - APB1 42 MHz / APB1 Timer clocks **84 MHz**
  - APB2 84 MHz / APB2 Timer clocks **168 MHz**
  - Flash latency 5 WS (자동)
- PLL 소스 = HSE(8MHz). USB는 미사용이라 PLLQ 무시 가능

---

## 4. FreeRTOS

- [ ] **Middleware → FREERTOS**
- [ ] Interface: `CMSIS_V2`
- [ ] 기본 Task(`defaultTask`) 유지 — F0 단계 골격용
- [ ] (태스크 구체 설계는 `FIRMWARE_DEV_PLAN.md §3.2` — F1 이후 코드에서)

---

## 5. 타이머 (모터 PWM · 엔코더 · 제어 루프)

### 5.1 TIM1 — M3 모터 PWM (어드밴스드 타이머, 168MHz)
- [ ] Channel1: `PWM Generation CH1` → 핀 **PA8** (기본 핀, 자동)
- [ ] Channel4: `PWM Generation CH4` → 핀 **PA11** (기본 핀, 자동)
- [ ] Counter: PWM 주파수 ~20kHz 목표 (Prescaler·Period는 F2에서 확정)

### 5.2 TIM3 — M1 모터 PWM (84MHz)
- [ ] Channel1: `PWM Generation CH1`
- [ ] Channel2: `PWM Generation CH2`
- [ ] ⚠ **핀 리맵 필요**: 기본은 PA6/PA7 → **PC6=TIM3_CH1, PC7=TIM3_CH2**로 변경
      (핀맵 뷰에서 PC6 클릭 → `TIM3_CH1`, PC7 클릭 → `TIM3_CH2`)

### 5.3 TIM2 — H1 엔코더
- [ ] Combined Channels: `Encoder Mode`
- [ ] ⚠ **핀 리맵 필요**: 기본은 PA0/PA1 → **PA15=TIM2_CH1, PB3=TIM2_CH2**로 변경
      (PA0/PA1은 TIM5가 사용하므로 반드시 리맵)
- [ ] **Counter Settings**:
  - Prescaler: `0`
  - **Counter Period (ARR): `4294967295`** ← 0xFFFFFFFF, TIM2는 32-bit.
    기본값 0으로 두면 엔코더 동작 안 함 — 반드시 입력
  - Counter Mode: `Up` (기본)
- [ ] **Encoder settings**:
  - Encoder Mode: `TI1 and TI2` (×4 체배)
  - IC1/IC2 Polarity: `Rising` (기본 — F3에서 방향 반대면 한쪽만 Falling)
  - IC1/IC2 Filter: `0` (기본 OK — 노이즈 시 F3에서 ~10)
- [ ] NVIC: **인터럽트 불필요** (CNT 레지스터 직접 읽음, 32-bit라 오버플로 무시 가능)

### 5.4 TIM5 — H3 엔코더
- [ ] Combined Channels: `Encoder Mode`
- [ ] 핀: **PA0=TIM5_CH1, PA1=TIM5_CH2** (기본 핀, 리맵 불필요)
- [ ] Counter / Encoder settings: **§5.3 TIM2와 동일**
  (ARR `4294967295`, Prescaler `0`, `TI1 and TI2` ×4, NVIC 불필요)

### 5.5 TIM7 — 1kHz 제어 루프 틱
- [ ] `Activated` 체크
- [ ] Prescaler `8399`, Counter Period `9999` → 84MHz/8400/10000 = **1000 Hz**
- [ ] NVIC: `TIM7 global interrupt` Enable (§9에서)

---

## 6. 통신

### 6.1 USART1 — Jetson 통신 (micro-ROS)
- [ ] Mode: `Asynchronous`
- [ ] 핀: **PA9=TX, PA10=RX** (기본)
- [ ] Baud Rate: `921600`, 8N1
- [ ] NVIC: `USART1 global interrupt` Enable
- [ ] DMA 추가 (micro-ROS DMA 트랜스포트용):
  - `USART1_RX` — **Mode: `Circular`** ← 기본 `Normal`에서 반드시 변경
  - `USART1_TX` — Mode: `Normal` (기본 그대로)
  - 스트림 자동할당 / Byte·Byte / Mem 증가 / Direct 모드 / Priority Low → 모두 기본값 OK

### 6.2 UART5 — 디버그 콘솔
- [ ] Mode: `Asynchronous`
- [ ] 핀: **PC12=TX, PD2=RX** (기본)
- [ ] Baud Rate: `115200`, 8N1
- [ ] `printf` 리타게팅 대상 (F0 검증용)

### 6.3 SPI2 — ICM-20948 IMU
- [ ] Mode: `Full-Duplex Master`
- [ ] Hardware NSS: `Disable` ← CS는 GPIO(PB12)로 수동 제어
- [ ] 핀: **PB13=SCK, PB14=MISO, PB15=MOSI** (기본)
- [ ] Clock: Prescaler로 ≤ 7 MHz 맞춤 (APB1 42MHz → `/8` ≈ 5.25 MHz)
- [ ] CPOL=`High`, CPHA=`2 Edge` (ICM-20948 SPI Mode 3)

### 6.4 I2C1 — RM3100 자기계
- [ ] Mode: `I2C`
- [ ] 핀: **PB6=SCL, PB7=SDA** (기본)
- [ ] Speed: `Fast Mode` (400 kHz) — RM3100 사양 내

### 6.5 I2C2 — 보조 (OLED 등, 옵션)
- [ ] Mode: `I2C`
- [ ] 핀: **PB10=SCL, PB11=SDA** (기본)
- [ ] Speed: `Standard`/`Fast` (OLED에 맞춤)

---

## 7. ADC — 배터리 전압

### ADC1
- [ ] `IN8` 체크 → 핀 **PB0** 자동 할당
- [ ] 단일 변환, 소프트웨어 트리거 (F8에서 주기 샘플링으로 확정)

---

## 8. GPIO 설정

핀맵 뷰에서 각 핀 클릭 → 모드 지정.

| 핀 | 모드 | 용도 | User Label (권장) |
|---|---|---|---|
| PC13 | `GPIO_Output` | 상태 LED | `LED_STATUS` |
| PA12 | `GPIO_Output` | LED 제어 | `SW_LED` |
| PB1 | `GPIO_Output` | 능동 부저 (on/off) | `BUZZER` |
| PB12 | `GPIO_Output` | ICM-20948 SPI CS | `IMU_CS` |
| PC4 | `GPIO_Input` (Pull-up) | KEY1 버튼 | `KEY1` |
| PC5 | `GPIO_EXTI5` | IMU INT1 (데이터레디) | `IMU_INT1` |

- [ ] 출력 핀: 초기 레벨 `Low`, Push-Pull, Low speed
- [ ] PC4: 외부 풀업 있으면 `No pull`, 없으면 `Pull-up`
- [ ] PC5 EXTI: ICM-20948 INT 설정에 맞춰 `Rising` 또는 `Falling` (보통 Rising)

---

## 9. NVIC (인터럽트)

활성화할 인터럽트:
- [ ] `TIM7 global interrupt` — 제어 루프 틱
- [ ] `USART1 global interrupt` — micro-ROS
- [ ] `EXTI line[9:5] interrupt` — PC5 (IMU INT1)
- [ ] DMA 인터럽트 (USART1 RX/TX) — DMA 추가 시 자동

### 9.1 우선순위 규칙 (FreeRTOS 필수)

Cortex-M은 **우선순위 숫자가 작을수록 더 긴급**. CubeMX+FreeRTOS 기본값에서
기준선 `configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY` = **5**.

| 우선순위 숫자 | FreeRTOS `...FromISR()` 호출 |
|---|---|
| 0 ~ 4 | ❌ 금지 (기준선보다 긴급 → 커널 보호 불가 → HardFault) |
| 5 ~ 15 | ✅ 허용 |

→ FreeRTOS API를 호출하는 ISR은 **Preemption Priority 숫자 ≥ 5**.
   호출하지 않는 ISR은 0~4도 가능하나, 헷갈리면 전부 5 이상으로 두면 안전.

권장 설정 (NVIC 탭, Preemption Priority):

| 인터럽트 | Preemption Priority |
|---|---|
| TIM7 (제어 루프) | 5 |
| USART1 / DMA | 6 |
| EXTI (IMU INT1) | 6 |

- [ ] 위 표대로 Preemption Priority 설정
- SysTick / PendSV / SVC 는 FreeRTOS용 — CubeMX 자동 설정, **수정 금지**

> 참고: 모터 제어를 TIM7 ISR 안에서 직접 수행하고 FreeRTOS 함수를 호출하지
> 않으면 우선순위 제약이 없어진다(`FIRMWARE_DEV_PLAN.md §3.2` 방식). 그래도
> 단순화를 위해 TIM7 = 5 로 두는 것을 권장.

---

## 10. Project Manager

- [ ] **Project Name**: `rover_jupiter_fw`
- [ ] **Project Location**: `C:\Project\Rover\Rover\firmware\`
      → CubeMX가 `firmware\rover_jupiter_fw\` 폴더를 생성
- [ ] **Toolchain/IDE**: `Makefile` (VS Code + Claude Code + `make`,
      micro_ros_stm32cubemx_utils 빌드 지원)
- [ ] **Code Generator**:
  - `Generate peripheral initialization as a pair of .c/.h files` 체크
  - `Keep User Code when re-generating` 체크
- [ ] **GENERATE CODE**

---

## 11. 코드 생성 후 — F0 검증 작업

CubeMX 코드 생성 후 VS Code에서:

- [ ] `make` 빌드 성공 확인
- [ ] ST-Link로 플래시
- [ ] **PC13 LED blink** (FreeRTOS defaultTask에서 토글)
- [ ] **UART5 디버그 콘솔** — `printf` → 115200으로 메시지 출력 확인
- [ ] **PB1 부저** 짧게 on/off 테스트
- [ ] FreeRTOS 태스크 스케줄링 동작 확인 (2개 태스크로 확인)

→ 여기까지 되면 **F0 완료**, F1(드라이버 골격) 진행.

---

## 12. 핀 충돌 점검 결과 (사전 검증 완료)

| 자원 | 사용 | 충돌 |
|---|---|---|
| TIM1 / TIM3 / TIM2 / TIM5 / TIM6 / TIM7 | 모터·엔코더·timebase·제어틱 | 없음 |
| PA15 / PB3 (JTAG 핀) | H1 엔코더 | SWD 전용 설정으로 해소 |
| PA0 / PA1 | H3 엔코더 (TIM5) | 없음 (TIM2는 PA15/PB3로 리맵) |
| SPI2 / I2C1 / I2C2 / USART1 / UART5 / ADC1 | 통신·센서 | 없음 |

---

## 13. micro-ROS 관련 (참고 — F5에서 진행)

F0에서는 USART1 핀·DMA만 잡아두고, micro-ROS 본 통합은 F5 단계:
- `micro_ros_stm32cubemx_utils` 추가
- USART1을 micro-ROS serial transport에 연결
- 상세는 `FIRMWARE_DEV_PLAN.md §3.3, §5`

---

*문서 끝.*
