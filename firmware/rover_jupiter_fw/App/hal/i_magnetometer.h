/**
 * @file    i_magnetometer.h
 * @brief   HAL — 자기계 인터페이스
 *
 * 구현체: App/drivers/rm3100_driver.c (I2C1)
 * 양산기 이식 시 동급/상위 자기계로 교체 가능.
 *
 * Raw 24-bit signed (RM3100 측정값). 단위는 LSB/μT — App Layer에서 변환.
 */
#ifndef APP_HAL_I_MAGNETOMETER_H
#define APP_HAL_I_MAGNETOMETER_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int32_t  mag_raw[3];   /* X/Y/Z, 24-bit sign-extended */
    uint32_t ts_ms;
} MagSample;

bool mag_init(void);
bool mag_read(MagSample *out);

/** REVID 1바이트 (RM3100 = 0x22). F1 단계 sanity 검증용. */
bool mag_read_revid(uint8_t *out);

#ifdef __cplusplus
}
#endif

#endif /* APP_HAL_I_MAGNETOMETER_H */
