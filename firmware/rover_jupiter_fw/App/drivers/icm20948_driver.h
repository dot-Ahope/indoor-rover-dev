/**
 * @file    icm20948_driver.h
 * @brief   ICM-20948 IMU 드라이버 (SPI2, CS=PB12).
 *
 * F1 단계: WHO_AM_I (0xEA) 검증만. 본 init·연속 읽기는 F7.
 */
#ifndef APP_DRIVERS_ICM20948_DRIVER_H
#define APP_DRIVERS_ICM20948_DRIVER_H

#include "i_imu.h"

/* WHO_AM_I 기대값 (ICM-20948 datasheet §8). */
#define ICM20948_WHOAMI 0xEAu

#endif
