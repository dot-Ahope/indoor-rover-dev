# App Layer

미션·안전·제어 등 최상위 로직. MCU·드라이버·통신 구현과 무관해야 한다.

## 구성 (예정)
- `MotionController` — cmd_vel → 좌/우 휠 속도 변환
- `OdometryEstimator` — 엔코더 → pose (x, y, yaw) 적분
- `SafetyMonitor` — 스톨 감지, 통신 watchdog, E-stop
- `MissionState` — 상태 머신

## 원칙
STM32 HAL · AM2861 · micro-ROS API를 **직접 호출하지 않는다.**
HAL Layer 인터페이스(`hal/`)를 통해서만 하드웨어에 접근한다.
→ 양산기(G4/H7) 이식 시 이 레이어는 그대로 재사용.

참조: `docs/FIRMWARE_DEV_PLAN.md §3.1`
