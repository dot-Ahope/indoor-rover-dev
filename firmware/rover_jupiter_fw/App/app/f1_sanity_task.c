/**
 * @file    f1_sanity_task.c
 * @brief   F1 페리페럴 검증 구현.
 *
 * 출력 예 (UART5 115200):
 *   [F1-init] motor=OK enc=OK imu=OK(whoami=0xEA) mag=OK(revid=0x22) adc=OK(raw=2350)
 *   [F1   12] enc L=  +123 R=  -45  adc=2348  imu_whoami=0xEA  freeHeap=29800
 */
#include "f1_sanity_task.h"

#include <stdio.h>
#include <stdint.h>

#include "FreeRTOS.h"
#include "task.h"
#include "cmsis_os.h"

#include "main.h"
#include "adc.h"
#include "i2c.h"

#include "i_motor_driver.h"
#include "i_encoder.h"
#include "i_imu.h"
#include "i_magnetometer.h"
#include "icm20948_driver.h"
#include "rm3100_driver.h"

static struct {
    bool    motor_ok;
    bool    enc_ok;
    bool    imu_ok;
    uint8_t imu_whoami;
    bool    mag_ok;
    uint8_t mag_revid;
    uint32_t count;
} s_st;

/* 1회 ADC 변환. HAL_ADC_Start → PollForConversion → GetValue → Stop. */
static bool adc_read_once(uint16_t *raw)
{
    if (HAL_ADC_Start(&hadc1) != HAL_OK) return false;
    HAL_StatusTypeDef st = HAL_ADC_PollForConversion(&hadc1, 10);
    if (st == HAL_OK) {
        *raw = (uint16_t)HAL_ADC_GetValue(&hadc1);
    }
    HAL_ADC_Stop(&hadc1);
    return st == HAL_OK;
}

/* I2C 버스 스캔 — 발견된 7-bit 주소 출력 (없으면 "(none)"). */
static void i2c_scan(I2C_HandleTypeDef *hi2c, const char *label)
{
    printf("[F1-%s scan]", label);
    int found = 0;
    for (uint8_t a = 0x08; a < 0x78; a++) {
        if (HAL_I2C_IsDeviceReady(hi2c, (uint16_t)(a << 1), 1, 5) == HAL_OK) {
            printf(" 0x%02X", a);
            found++;
        }
    }
    if (!found) printf(" (none)");
    printf("\r\n");
}

void f1_sanity_init(void)
{
    s_st.motor_ok = motor_driver_init();
    s_st.enc_ok   = encoder_init();
    s_st.imu_ok   = imu_init();
    (void)imu_read_whoami(&s_st.imu_whoami);

    /* I2C 양쪽 버스 스캔 — 디버그 가시성용. 빈 줄 출력해도 정상 (외부 I2C 디바이스 없을 수 있음). */
    i2c_scan(&hi2c1, "i2c1");
    i2c_scan(&hi2c2, "i2c2");

#if F1_RM3100_PRESENT
    s_st.mag_ok = mag_init();
    (void)mag_read_revid(&s_st.mag_revid);
#else
    s_st.mag_ok    = false;
    s_st.mag_revid = 0;
#endif

    uint16_t adc_raw = 0;
    bool adc_ok = adc_read_once(&adc_raw);

#if F1_RM3100_PRESENT
    const char *mag_str = s_st.mag_ok ? "OK" : "FAIL";
#else
    const char *mag_str = "SKIP";   /* RM3100 미실장 — ICM-20948 내장 AK09916 사용 예정 (F7) */
#endif

    printf("[F1-init] motor=%s enc=%s imu=%s(whoami=0x%02X) mag=%s(revid=0x%02X) adc=%s(raw=%u)\r\n",
           s_st.motor_ok ? "OK" : "FAIL",
           s_st.enc_ok   ? "OK" : "FAIL",
           s_st.imu_ok   ? "OK" : "FAIL", s_st.imu_whoami,
           mag_str, s_st.mag_revid,
           adc_ok ? "OK" : "FAIL", (unsigned)adc_raw);
}

void f1_sanity_tick(void)
{
    s_st.count++;
    int32_t enc_l = encoder_read_count(ENC_LEFT);
    int32_t enc_r = encoder_read_count(ENC_RIGHT);

    uint16_t adc_raw = 0;
    (void)adc_read_once(&adc_raw);

    uint8_t whoami = 0;
    (void)imu_read_whoami(&whoami);

    printf("[F1 %4lu] enc L=%+ld R=%+ld  adc=%u  imu_whoami=0x%02X  freeHeap=%u\r\n",
           (unsigned long)s_st.count,
           (long)enc_l, (long)enc_r,
           (unsigned)adc_raw,
           whoami,
           (unsigned)xPortGetFreeHeapSize());
}
