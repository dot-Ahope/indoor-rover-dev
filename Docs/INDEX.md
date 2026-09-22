# Docs/ — 문서 색인 (2026-09-21 폴더 재구성)

폴더 번호는 **프로젝트 진행 순서**(펌웨어 → 하드웨어 → Jetson → 자율주행 → nvblox)다. 날짜별 실험 기록은 `debug_log/`에 그대로 두고 옮기지 않는다.

| 폴더 | 영역 | 대표 계획서 | 시기 |
|---|---|---|---|
| [`01_firmware/`](01_firmware/) | STM32F405 펌웨어 F0~F8, 빌드·플래시, micro-ROS | [FIRMWARE_DEV_PLAN.md](01_firmware/FIRMWARE_DEV_PLAN.md) | 2026-05~09 |
| [`02_hardware/`](02_hardware/) | 차체(WT-600)·모터(1:90)·URDF·배치도 | [WT600_UPDATE_BRIEF.md](02_hardware/WT600_UPDATE_BRIEF.md), [MOTOR_1TO90_MIGRATION_PLAN.md](02_hardware/MOTOR_1TO90_MIGRATION_PLAN.md) | 2026-08 |
| [`03_jetson/`](03_jetson/) | Jetson Orin Nano 설정, 센서 드라이버 | [JETSON_SETUP_BRIEF.md](03_jetson/JETSON_SETUP_BRIEF.md) | 2026-05·08 |
| [`04_navigation/`](04_navigation/) | SLAM·Nav2·코스·게이트·절차 | [NAV2_EXPLORATION_PLAN.md](04_navigation/NAV2_EXPLORATION_PLAN.md), [TEST_COURSE_AND_GATES.md](04_navigation/TEST_COURSE_AND_GATES.md) | 2026-09 |
| [`05_nvblox/`](05_nvblox/) | Isaac ROS nvblox 이전(Phase N) | [NVBLOX_MIGRATION_PLAN.md](05_nvblox/NVBLOX_MIGRATION_PLAN.md) | 2026-09~ |
| [`debug_log/`](debug_log/) | 날짜별 실험 기록 `<날짜>/{SUMMARY.md, jobs/, outputs/, bags/(로컬)}` — 기준선 [2026-09-21/BASELINE_STVL.md](debug_log/2026-09-21/BASELINE_STVL.md) | — | 2026-08~ |
| (루트) | [PROJECT_OVERVIEW.md](../PROJECT_OVERVIEW.md) 프로젝트 전반, [CLAUDE.md](../CLAUDE.md) 작업 지침 | | |

## 01_firmware — 펌웨어 개발 단계별 (F0 → F8)
| 단계 | 문서 | 핵심 산출물 |
|---|---|---|
| 계획 | [FIRMWARE_DEV_PLAN.md](01_firmware/FIRMWARE_DEV_PLAN.md) | 아키텍처(App/HAL/Driver), FreeRTOS 태스크, micro-ROS 토픽, F0~F8 |
| **F0** | [F0_CUBEMX_SETUP.md](01_firmware/F0_CUBEMX_SETUP.md) | CubeMX `.ioc` 체크리스트, 핀맵·클럭·FreeRTOS |
| **F1** | [F1_VERIFICATION.md](01_firmware/F1_VERIFICATION.md) | HAL/Driver 골격, 페리페럴 sanity |
| **F2** | [F2_VERIFICATION.md](01_firmware/F2_VERIFICATION.md) | 모터 개방루프 PWM, 매핑·방향 |
| **F3** | [F3_VERIFICATION.md](01_firmware/F3_VERIFICATION.md) | 엔코더 속도·EMA·누적 거리 |
| **F4** | [F4_VERIFICATION.md](01_firmware/F4_VERIFICATION.md) | 속도 PI 제어·데드밴드 |
| **F5a/b/c** | [F5a_MICROROS_LIB.md](01_firmware/F5a_MICROROS_LIB.md), [F5b_VERIFICATION.md](01_firmware/F5b_VERIFICATION.md), [F5c_VERIFICATION.md](01_firmware/F5c_VERIFICATION.md) | micro-ROS 라이브러리·세션·토픽 |
| **F6** | [F6_VERIFICATION.md](01_firmware/F6_VERIFICATION.md) | 오도메트리 발행 |
| **F7/7.5** | [F7_VERIFICATION.md](01_firmware/F7_VERIFICATION.md), [F7.5_VERIFICATION.md](01_firmware/F7.5_VERIFICATION.md) | IMU·자기계·스톨 보호 |
| **F8** | [F8_VERIFICATION.md](01_firmware/F8_VERIFICATION.md) | 통합 검증 |
| 공통 | [BUILD_AND_FLASH_GUIDE.md](01_firmware/BUILD_AND_FLASH_GUIDE.md), [F103_to_G474_pin_migration.md](01_firmware/F103_to_G474_pin_migration.md), [ICM-20948_magnetometer_SPI.md](01_firmware/ICM-20948_magnetometer_SPI.md), [STM32BD/](01_firmware/STM32BD/) 보드 자료 | |
| 폐기 | [legacy/ROVER_SERIAL_PROTOCOL_v1.0.md](01_firmware/legacy/ROVER_SERIAL_PROTOCOL_v1.0.md) — micro-ROS 채택으로 대체, 기록 보존 | |

## 02_hardware
- [WT600_UPDATE_BRIEF.md](02_hardware/WT600_UPDATE_BRIEF.md) — WT-600 섀시 실측·URDF 개정(2026-08-27)
- [MOTOR_1TO90_MIGRATION_PLAN.md](02_hardware/MOTOR_1TO90_MIGRATION_PLAN.md) — 1:90 모터 교체 계획(2026-08-26; 09-21 부터 리포 추적)
- [rover.urdf](02_hardware/rover.urdf), [rover.urdf.xacro](02_hardware/rover.urdf.xacro) — **기록 사본**. 배포 원본은 `ros2_ws/src/rover_description/urdf/`. 데크 yaw −2.68° 보정(2026-09-18) 반영본
- [rover_top_down_layout.svg](02_hardware/rover_top_down_layout.svg) — 배치도(2026-05)

## 03_jetson
- [JETSON_SETUP_BRIEF.md](03_jetson/JETSON_SETUP_BRIEF.md) — Jetson·ROS 2·센서 드라이버 설치 요약
- [Jetson/](03_jetson/Jetson/) — 설치 자료

## 04_navigation
- [TEST_COURSE_AND_GATES.md](04_navigation/TEST_COURSE_AND_GATES.md) — **코스 배치·게이트 표·주행 절차·운영 규칙의 단일 출처**(Phase S v1.0). Phase 전환 시 절 단위 재검토
- [NAV2_EXPLORATION_PLAN.md](04_navigation/NAV2_EXPLORATION_PLAN.md) — Nav2 도입 계획(2026-09-08)
- [PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md](04_navigation/PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md) — 통로 정체 분석(계획·컨트롤러·지도 3 계층)
- 기준선: [debug_log/2026-09-21/BASELINE_STVL.md](debug_log/2026-09-21/BASELINE_STVL.md)

## 05_nvblox
- [NVBLOX_MIGRATION_PLAN.md](05_nvblox/NVBLOX_MIGRATION_PLAN.md) — Phase S/N 종료 조건·git 전략·N0~N5
- [PHASE_N_RESULTS.md](05_nvblox/PHASE_N_RESULTS.md) — **N0~N5 결과 요약·결정(09-22: 로컬 층 nvblox 채택)·그림 색인·남은 항목**
- [figures/](05_nvblox/figures/) — 자체 완결 HTML 그림 4 장(09-21 코스트맵 비교 v1/v2, 09-22 절단 A/B, N4 궤적 5 회). 원자료·스크립트는 `debug_log/2026-09-2{1,2}/`
- 채택 설정: [`ros2_ws/src/rover_navigation/config/nvblox_local.yaml`](../ros2_ws/src/rover_navigation/config/nvblox_local.yaml)

## 옛 경로 → 새 경로 (2026-09-21 이전 문서·`debug_log/` 기록의 링크 해석용)
| 옛 경로 | 새 경로 |
|---|---|
| `Docs/FIRMWARE_DEV_PLAN.md`, `Docs/F*_VERIFICATION.md`, `Docs/F5a_MICROROS_LIB.md`, `Docs/F0_CUBEMX_SETUP.md`, `Docs/BUILD_AND_FLASH_GUIDE.md`, `Docs/F103_to_G474_pin_migration.md`, `Docs/ICM-20948_magnetometer_SPI.md`, `Docs/STM32BD/` | `Docs/01_firmware/…` |
| `ROVER_SERIAL_PROTOCOL_v1.0.md` (루트) | `Docs/01_firmware/legacy/ROVER_SERIAL_PROTOCOL_v1.0.md` |
| `Docs/WT600_UPDATE_BRIEF.md`, `Docs/MOTOR_1TO90_MIGRATION_PLAN.md`, `Docs/rover.urdf`, `Docs/rover.urdf.xacro`, `Docs/rover_top_down_layout.svg` | `Docs/02_hardware/…` |
| `Docs/JETSON_SETUP_BRIEF.md`, `Docs/Jetson/` | `Docs/03_jetson/…` |
| `Docs/NAV2_EXPLORATION_PLAN.md`, `Docs/PASSAGE_PROBLEM_ANALYSIS_2026-09-16.md`, `Docs/TEST_COURSE_AND_GATES.md` | `Docs/04_navigation/…` |
| `Docs/NVBLOX_MIGRATION_PLAN.md` | `Docs/05_nvblox/NVBLOX_MIGRATION_PLAN.md` |
| `Docs/debug_log/…` | 변경 없음 |
