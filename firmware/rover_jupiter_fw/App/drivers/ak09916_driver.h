/**
 * @file    ak09916_driver.h
 * @brief   AK09916 자기계 드라이버 — ICM-20948 패키지 내장 (AUX I2C 경유).
 *
 * 액세스 경로: STM32 SPI2 → ICM-20948 I2C master → AK09916 (AUX 0x0C).
 * 본 드라이버는 icm20948_driver 의 aux 헬퍼만 사용 — STM32 I2C 페리 미점유.
 *
 * 측정 사양:
 *   ±4912 µT, 16-bit signed, **little-endian**
 *   sensitivity = 0.15 µT/LSB
 *   continuous mode 4 (100 Hz) 사용 — sandbox 검증
 */
#ifndef APP_DRIVERS_AK09916_DRIVER_H
#define APP_DRIVERS_AK09916_DRIVER_H

#include "i_magnetometer.h"

#define AK09916_I2C_ADDR_7BIT  0x0Cu

/* LSB → Tesla 변환 — imu_processor.c 에서 사용. */
#define AK09916_LSB_TO_TESLA   1.5e-7f   /* 0.15 µT/LSB */

#endif
