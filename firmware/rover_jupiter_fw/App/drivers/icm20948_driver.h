/**
 * @file    icm20948_driver.h
 * @brief   ICM-20948 IMU 드라이버 (SPI2, CS=PB12) + AUX I2C master.
 *
 * 핵심 설계:
 *   - **HW init 은 main.c 의 scheduler 시작 전에 호출** — task race 차단.
 *     imu_init() 안에 cold-boot recovery (CS strobe + MISO pull-up + dummy read)
 *     포함.
 *   - SLV0 single-shot 후 disable 패턴 — sandbox 검증 (Docs/ICM-20948_magnetometer_SPI.md).
 *
 * 측정 범위 (F7 기본):
 *   accel ±2g  → 16384 LSB/g  → 1 LSB ≈ 5.985e-4 m/s²
 *   gyro  ±250 dps → 131 LSB/dps → 1 LSB ≈ 1.331e-4 rad/s
 */
#ifndef APP_DRIVERS_ICM20948_DRIVER_H
#define APP_DRIVERS_ICM20948_DRIVER_H

#include "i_imu.h"

/* WHO_AM_I 기대값. */
#define ICM20948_WHOAMI 0xEAu

/* 변환 스케일 — imu_processor.c 에서 raw → SI 변환에 사용. */
#define ICM20948_ACCEL_LSB_PER_G    16384.0f       /* ±2g */
#define ICM20948_GYRO_LSB_PER_DPS   131.0f         /* ±250 dps */

/* ─── AUX I2C master 헬퍼 (AK09916 자기계용) ──────────────────────────
 *
 * 호스트(STM32)는 SPI2 만 사용. AUX 디바이스 액세스는 ICM 내장 I2C master
 * 가 대행. **SLV4 미사용** — SLV0 만으로 단순화 (sandbox 검증).
 */

/** I2C master 활성: USER_CTRL bit5/4 + I2C_MST_CTRL CLK=400kHz. */
bool icm20948_i2c_master_enable(void);

/** SLV0 one-shot write — ICM 가 다음 ODR cycle 에 AUX write 실행 후 disable.
 *  다음 reconfigure 전 transient 안전. */
bool icm20948_aux_slv0_write_byte(uint8_t aux_addr, uint8_t aux_reg, uint8_t val);

/** SLV0 one-shot read — 결과를 *val 에 반환 후 SLV0 disable. */
bool icm20948_aux_slv0_read_byte(uint8_t aux_addr, uint8_t aux_reg, uint8_t *val);

/** SLV0 를 주기 read (streaming) 으로 arm — ICM ODR 마다 EXT_SLV_SENS 적재.
 *  len ∈ [1,15]. */
bool icm20948_aux_setup_slave0_read(uint8_t aux_addr, uint8_t aux_reg, uint8_t len);

/** EXT_SLV_SENS_DATA_00 (Bank 0, 0x3B) 부터 len 바이트 burst read. */
bool icm20948_aux_read_ext_sens(uint8_t *buf, uint8_t len);

/** 임의 bank/reg 1바이트 read — 브링업 진단 전용. */
bool icm20948_debug_read(uint8_t bank, uint8_t reg, uint8_t *val);

#endif
