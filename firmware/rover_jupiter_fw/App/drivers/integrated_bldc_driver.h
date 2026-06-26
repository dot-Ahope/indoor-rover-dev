/**
 * @file    integrated_bldc_driver.h
 * @brief   통합 드라이버형 모터 드라이버 (50Hz PWM duty + 방향 GPIO + FG).
 *
 * 대상 모터: 컨트롤러 내장형. 배선:
 *   적색=모터+, 흑색=모터-, 청색=PWM 속도지령(50Hz duty),
 *   백색=방향선(레벨 방식), 황색=FG 펄스(속도 피드백, 방향정보 없음)
 *
 * 핀 매핑 (사용자 배선 확정):
 *   MOTOR_RIGHT ← M1 : M1A=PC6(TIM3_CH1)=PWM,  M1B=PC7=방향GPIO,  H1A=PA15=FG
 *   MOTOR_LEFT  ← M3 : M3A=PA8(TIM1_CH1)=PWM,  M3B=PA11=방향GPIO, H3A=PA0 =FG
 *
 * 본 드라이버는 i_motor_driver.h 인터페이스를 구현 (set_duty 부호=방향선, 크기=PWM).
 * .ioc 는 AM2861 기준 그대로 두고, init 시 PC7/PA11(AF)을 GPIO 출력으로,
 * TIM1/TIM3 를 50Hz 로 런타임 재설정한다.
 *
 * NOTE: FG 기반 속도/odometry 는 별도 드라이버(step 5)에서 처리. 본 파일은 구동만 담당.
 * TODO(production): 외장 컨트롤러 사양 확정 시 극성/전류제한/방향전환 시퀀스 보강.
 */
#ifndef APP_DRIVERS_INTEGRATED_BLDC_DRIVER_H
#define APP_DRIVERS_INTEGRATED_BLDC_DRIVER_H

#include "i_motor_driver.h"

#endif /* APP_DRIVERS_INTEGRATED_BLDC_DRIVER_H */
