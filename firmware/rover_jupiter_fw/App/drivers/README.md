# Driver Layer — 저수준 드라이버

HAL 인터페이스의 구체 구현. F405·보드 의존 코드는 모두 여기에 격리한다.

## 구성 (예정)
- `AM2861Driver` — 모터 드라이버 (sign-magnitude PWM: 전진 IA=PWM/IB=Low, 후진 반대)
- `Stm32EncoderDriver` — STM32 TIM 엔코더 모드 (TIM2=H1, TIM5=H3)
- `Icm20948Driver` — IMU, SPI2
- `Rm3100Driver` — 자기계, I2C1

## 핀 배정
`docs/FIRMWARE_DEV_PLAN.md §2.3` 핀 배정표 참조.

## 원칙
하드웨어(MCU·모터드라이버) 교체 시 바뀌는 레이어. App Layer는 영향받지 않는다.
