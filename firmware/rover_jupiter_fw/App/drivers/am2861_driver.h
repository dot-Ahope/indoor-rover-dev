/**
 * @file    am2861_driver.h
 * @brief   AM2861 H-브리지 드라이버 (sign-magnitude PWM).
 *
 * 핀 매핑 (F2 실측 확정 — FIRMWARE_DEV_PLAN §2.3 표기와 실제 배선 결과):
 *   MOTOR_LEFT  ← M3 (TIM1): CH1=PA8, CH4=PA11   (물리적 좌측 휠)
 *   MOTOR_RIGHT ← M1 (TIM3): CH1=PC6, CH2=PC7    (물리적 우측 휠)
 *
 * LEFT 모터: +duty 시 차량 전진 — CH1=PWM, CH4=Low. (회로도 IA/IB 라벨과
 *   실배선 종합 결과 CubeMX 핀 표기상의 IB 채널이 forward.)
 * RIGHT 모터: 방향 검증은 RIGHT 휠 회전 가능해진 시점에 추가.
 *
 * TODO(production): 외장 드라이버 채택 시 본 파일 통째 교체.
 */
#ifndef APP_DRIVERS_AM2861_DRIVER_H
#define APP_DRIVERS_AM2861_DRIVER_H

#include "i_motor_driver.h"

#endif
