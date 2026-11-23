# 펌웨어 — STM32F405 + FreeRTOS + micro-ROS

[← 첫 페이지](../../README.md)

<p align="center"><img src="../media/2026-11-23_firmware.png" width="85%"/><br/><sub>Nav2 속도 지령(<code>/cmd_vel</code>)과 휠 엔코더로 잰 속도(<code>/wheel_odom</code>) — 실주행 첫 60 초(위 병진 v, 아래 회전 ω)</sub></p>

## 하는 일
- 보드(STM32F405)가 직접 ROS 2 노드가 된다 — micro-ROS 로 `/cmd_vel` 을 받고 `/wheel_odom` · `/rover/status` · `/battery` 를 낸다. Jetson 쪽은 에이전트만 띄운다(변환 노드 없음).
- 바퀴 속도 제어(엔코더 FG 펄스 → 100 Hz PID, 적분 클램프), 스톨 보호(무이동 감지 → 자동 복구 → 반복 시 래치), `/cmd_vel` 이 끊기면 모터 정지(워치독).
- 코드는 App / HAL / Driver 계층으로 나눔 — MCU · 모터 · 통신을 바꿔도 App 층과 토픽 구조는 그대로.

## 왜 이렇게 했나
- **안전 로직은 전부 보드에서.** 모터 드라이버의 과전류 보호 사양을 확인할 수 없어(출처 없는 수치는 지움) 보드 감지를 1 차 보호로 둔다. Jetson · Wi-Fi 응답은 믿지 않는다.
- **커스텀 시리얼 프로토콜 대신 micro-ROS.** 첫 MCU(F103)의 RAM 한계로 직접 프로토콜을 설계했다가, F405 로 바꾸면서 표준 메시지를 그대로 쓰는 쪽으로 버림.

## 겪은 문제
- 모터를 바꿀 때 PWM 주파수가 옛 모터 값(50 Hz)으로 12 일 동안 남아 있었다 — 그 기간 측정치는 전부 다시 잴 대상으로 표시 → [모터 PWM 50 Hz 오적용](../issues/motor-pwm-50hz.md)
- 작은 지령을 올려 주는 데드밴드 보상이 스톨 판정 문턱 바로 위라, 접촉 없이 로버 전체가 잠김 → [스톨 래치 × 데드밴드](../issues/stall-latch.md)
- 설계 통신 속도(2 Mbps)에서 `/wheel_odom` 이 사라짐 — 지금은 460 800 bps 로 우회, 원인 미확정 → [micro-ROS 보드율 회귀](../issues/microros-baud-regression.md)
- 보드 IMU 자이로가 회전에 반응하지 않음(손회전 녹화 2 회) → EKF 자이로는 카메라 IMU 로 → [자이로 소스](../issues/gyro-source-d455f.md)

## 더 보기
- 지금 값(통신 속도 · 스톨 문턱 · 워치독): [CURRENT_STACK §2.5](../04_navigation/CURRENT_STACK.md)
- 단계별 계획 · 검증: [FIRMWARE_DEV_PLAN.md](../01_firmware/FIRMWARE_DEV_PLAN.md) · [`Docs/01_firmware/`](../01_firmware/)
