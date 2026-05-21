/**
 * @file    icm20948_driver.h
 * @brief   ICM-20948 IMU 드라이버 (SPI2, CS=PB12).
 *
 * F7: PWR_MGMT wake + bank 2 accel/gyro 설정 + 14byte burst read.
 *
 * 측정 범위 (F7 기본):
 *   accel ±2g  → 16384 LSB/g  → 1 LSB ≈ 5.985e-4 m/s²
 *   gyro  ±250 dps → 131 LSB/dps → 1 LSB ≈ 1.331e-4 rad/s
 * DLPF: bandwidth ~111Hz (구성 가능, F7 에선 적당히 잡음)
 */
#ifndef APP_DRIVERS_ICM20948_DRIVER_H
#define APP_DRIVERS_ICM20948_DRIVER_H

#include "i_imu.h"

/* WHO_AM_I 기대값 (ICM-20948 datasheet §8). */
#define ICM20948_WHOAMI 0xEAu

/* 변환 스케일 — imu_processor.c 에서 raw → SI 변환에 사용. */
#define ICM20948_ACCEL_LSB_PER_G    16384.0f       /* ±2g */
#define ICM20948_GYRO_LSB_PER_DPS   131.0f         /* ±250 dps */

#endif
