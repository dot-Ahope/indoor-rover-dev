/**
 * @file    i_magnetometer.h
 * @brief   HAL — 자기계 인터페이스
 *
 * 구현체 (현 dev 보드): App/drivers/ak09916_driver.c
 *   ICM-20948 패키지 내장 AK09916 — STM32 SPI2 → ICM I2C master → AK09916.
 *   (외장 RM3100 미실장 — 양산기에서 산업급 자기계로 교체 검토)
 *
 * Raw: 16-bit signed (AK09916 LE) 또는 24-bit signed (RM3100 BE 등).
 * 다양한 구현 폭을 수용하기 위해 int32_t 로 sign-extend 해 적재.
 * SI 변환 (Tesla) 은 App Layer (imu_processor) 책임.
 */
#ifndef APP_HAL_I_MAGNETOMETER_H
#define APP_HAL_I_MAGNETOMETER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int32_t  mag_raw[3];   /* X/Y/Z, sign-extended (LSB 의미는 구현체별) */
    uint32_t ts_ms;
} MagSample;

bool mag_init(void);
bool mag_read(MagSample *out);

/** 식별 레지스터 1바이트 — F1 sanity 검증용.
 *  AK09916 구현: WIA1 (=0x48). 기존 RM3100 구현: REVID (=0x22). */
bool mag_read_revid(uint8_t *out);

#ifdef __cplusplus
}
#endif

#endif /* APP_HAL_I_MAGNETOMETER_H */
