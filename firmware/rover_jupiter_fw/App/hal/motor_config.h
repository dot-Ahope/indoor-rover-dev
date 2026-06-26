/**
 * @file    motor_config.h
 * @brief   모터 드라이버 타입 선택 (컴파일 타임).
 *
 * 양산/플랫폼 전환 시 아래 MOTOR_TYPE 한 줄만 변경하면
 * App 계층(speed_controller 등) 수정 없이 드라이버 구현이 교체됩니다.
 * (Makefile 에서 -DMOTOR_TYPE=... 로 override 도 가능)
 *
 * 각 드라이버 .c 는 본 매크로로 자기 구현을 #if 가드하므로,
 * 선택되지 않은 드라이버는 심볼을 만들지 않습니다(중복 정의 방지).
 *
 * 참조: docs/FIRMWARE_DEV_PLAN.md §3.1 (계층 구조), CLAUDE.md §1 (양산 이식성)
 */
#ifndef APP_HAL_MOTOR_CONFIG_H
#define APP_HAL_MOTOR_CONFIG_H

/* 지원 드라이버 타입 */
#define MOTOR_TYPE_AM2861           0  /* dev 보드 내장 AM2861 H-브리지 (PWM 2채널 sign-magnitude) */
#define MOTOR_TYPE_INTEGRATED_BLDC  1  /* 통합 드라이버형 모터 (50Hz PWM duty + 방향선 + FG) */

/* ── 모터 드라이버 타입 선택 ──────────────────────────────── */
#ifndef MOTOR_TYPE
#define MOTOR_TYPE  MOTOR_TYPE_INTEGRATED_BLDC
#endif

#endif /* APP_HAL_MOTOR_CONFIG_H */
