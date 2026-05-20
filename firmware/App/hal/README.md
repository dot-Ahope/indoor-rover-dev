# HAL Layer — 하드웨어 추상화 인터페이스

App Layer가 의존하는 인터페이스 정의. 구체 구현은 없다 (Driver Layer에 있음).

## 인터페이스 (예정)
- `IMotorDriver` — 모터 속도/PWM 지령
- `IEncoder` — 엔코더 카운트·속도 읽기
- `IIMU` — 가속도·자이로 읽기
- `IMagnetometer` — 자기장 읽기

## 원칙
양산기(G4/H7 + 외장 드라이버)로 이식할 때 **이 인터페이스는 유지**하고
Driver Layer 구현만 교체한다. 이것이 양산 이식성의 핵심.

참조: `docs/FIRMWARE_DEV_PLAN.md §3.1`
