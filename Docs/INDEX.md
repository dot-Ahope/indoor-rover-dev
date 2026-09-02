# Docs/ — 문서 색인

| 문서 ID | 제목 | 단계 / 영역 |
|---|---|---|
| — | [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) | 프로젝트 전반 (하드웨어·로드맵·결정 근거) |
| — | [CLAUDE.md](../CLAUDE.md) | 작업 지침 · 핵심 설계 원칙 |

## 펌웨어 개발 단계별 (F0 → F8)

| 단계 | 문서 | 핵심 산출물 |
|---|---|---|
| **F0** | [F0_CUBEMX_SETUP.md](F0_CUBEMX_SETUP.md) | STM32CubeMX `.ioc` 설정 체크리스트, 핀맵·클럭·FreeRTOS |
| **F1** | [F1_VERIFICATION.md](F1_VERIFICATION.md) | HAL/Driver 골격 (`App/{hal,drivers,app}/`), 페리페럴 sanity (PWM/Encoder/SPI/I2C/ADC) |
| **F2** | [F2_VERIFICATION.md](F2_VERIFICATION.md) | 모터 개방루프 PWM (20kHz), 매핑·방향 확정 |
| **F3** | [F3_VERIFICATION.md](F3_VERIFICATION.md) | 엔코더 속도 산출 + EMA 필터 + 누적 거리 (CPR 1320 실측 검증) |
| **F4** | [F4_VERIFICATION.md](F4_VERIFICATION.md) | 폐루프 속도 PID + dead-zone feedforward + 스톨 감지 |
| **F5a** | [F5a_MICROROS_LIB.md](F5a_MICROROS_LIB.md) | micro-ROS 정적 라이브러리 빌드 (WSL Ubuntu-22.04 + ROS2 Humble) |
| **F5b** | [F5b_VERIFICATION.md](F5b_VERIFICATION.md) | UART1 transport + executor + heartbeat publisher (`/rover/f5b_heartbeat`) |
| **F5c** | [F5c_VERIFICATION.md](F5c_VERIFICATION.md) | `/cmd_vel` subscriber + 차동구동 역기구학 |
| **F6** | [F6_VERIFICATION.md](F6_VERIFICATION.md) | 휠 오도메트리 + `/wheel_odom` 발행 + TX IRQ 최적화 |
| **F7** | [F7_VERIFICATION.md](F7_VERIFICATION.md) | ICM-20948 본 init + `/imu/data_raw` 발행 |
| **F7.5** | [F7.5_VERIFICATION.md](F7.5_VERIFICATION.md) | AK09916 (ICM 내장) 자기계 + `/imu/mag` 발행 |
| **F8** | [F8_VERIFICATION.md](F8_VERIFICATION.md) | cmd_vel watchdog + `/battery` + `/rover/status` + time sync |

## 기타 자료

| 문서 | 내용 |
|---|---|
| [BUILD_AND_FLASH_GUIDE.md](BUILD_AND_FLASH_GUIDE.md) | **저장소 clone → 빌드 → ST-Link 플래시 → UART5 검증** 전체 절차 (Windows/Linux/Mac, 트러블슈팅 포함) |
| [MOTOR_1TO90_MIGRATION_PLAN.md](MOTOR_1TO90_MIGRATION_PLAN.md) | **신규 1:90 (45rpm) BLDC 교체** — 배선·펌웨어 변경·T0~T6 테스트·자율주행 계획 (2026-08-18) |
| [FIRMWARE_DEV_PLAN.md](FIRMWARE_DEV_PLAN.md) | F0~F8 단계 정의 + 아키텍처 + 핀 배정표 (전체 마스터 플랜) |
| [F103_to_G474_pin_migration.md](F103_to_G474_pin_migration.md) | [철회됨] MCU 교체 검토 이력 (참고용) |
| [rover.urdf](rover.urdf) | 차체 URDF (휠 반경·트랙 폭) |
| [rover_top_down_layout.svg](rover_top_down_layout.svg) | 차체 평면도 |
| [Jetson/](Jetson/) | Jetson Orin Nano 관련 자료 |
| [STM32BD/](STM32BD/) | ALOPS Jupiter R1.4 보드 자료 (회로도 등) |

## ROS2 토픽 계약 (F8 시점 확정)

| 방향 | 토픽 | 타입 | 주기 |
|---|---|---|---|
| 구독 | `/cmd_vel` | `geometry_msgs/Twist` | event |
| 발행 | `/wheel_odom` | `nav_msgs/Odometry` | **50 Hz** |
| 발행 | `/imu/data_raw` | `sensor_msgs/Imu` | **50 Hz** |
| 발행 | `/imu/mag` | `sensor_msgs/MagneticField` | **50 Hz** (F7.5) |
| 발행 | `/battery` | `sensor_msgs/BatteryState` | 1 Hz |
| 발행 | `/rover/status` | `diagnostic_msgs/DiagnosticArray` | 5 Hz |
| 발행 | `/rover/f5b_heartbeat` | `std_msgs/Int32` | 1 Hz |

> 발행률 최적화: F7.5 직후 9.4 Hz → A/B/C 단계 (BEST_EFFORT QoS, UART 2Mbps, MTU 1024) 거쳐 50 Hz 달성. 상세는 메모리 `microros_publish_optimization`.

## 향후 작업

- ~~**F8.5**: voltage divider ratio 측정, IMU gyro.z auto-calibration, header.stamp wall time 변환~~ → **완료 (2026-05-28)**. 메모리 `board_voltage_divider`, `icm20948_gyro_z_bias`, `f405_header_stamp_fix` 참조.
- **Jetson Phase 2**: `rover_description` (URDF), `rover_bringup` (launch + micro_ros_agent), `robot_localization` EKF (wheel_odom + IMU fusion)
- **하드웨어 교체 시**: G4/H7 + 외장 모터 드라이버 + 상위 IMU 로 바꿔도 App Layer 재사용, Driver Layer 만 교체

---

*문서 끝.*
