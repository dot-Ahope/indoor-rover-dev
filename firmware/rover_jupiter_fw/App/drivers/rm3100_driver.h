/**
 * @file    rm3100_driver.h
 * @brief   RM3100 자기계 드라이버 (I2C1).
 *
 * F1 단계: REVID (0x22) 검증만. 측정 cycle·연속 읽기는 F7.
 *
 * I2C 7-bit 주소: SA1·SA0 핀에 따라 0x20~0x23 중 하나.
 * 보드 기본은 0x20 (HAL 8-bit = 0x40). 회로도 미확정 시 스캔으로 탐색.
 */
#ifndef APP_DRIVERS_RM3100_DRIVER_H
#define APP_DRIVERS_RM3100_DRIVER_H

#include "i_magnetometer.h"

#define RM3100_I2C_ADDR_7BIT  0x20u
#define RM3100_REVID_EXPECTED 0x22u

#endif
