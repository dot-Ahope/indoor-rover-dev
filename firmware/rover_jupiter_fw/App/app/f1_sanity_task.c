/**
 * @file    f1_sanity_task.c
 * @brief   F1 페리페럴 검증 구현.
 *
 * 출력 예 (UART5 115200):
 *   [F1-init] motor=OK enc=OK imu=READY(whoami=0xEA) mag=READY adc=OK(raw=2350)
 *   [F1   12] enc L=  +123 R=  -45  adc=2348  freeHeap=29800
 *
 * ICM-20948 SPI HW init (imu_init + mag_init) 은 모두 control task 의
 * imu_processor_init() 책임 — SPI race 회피. 본 태스크는 status query 만.
 * f1_sanity 가 액세스하는 페리: 모터·엔코더·I2C·ADC (전부 SPI/ICM 무관).
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
#include "imu_processor.h"
#include "speed_controller.h"
#include "safety_monitor.h"

static struct {
    bool    motor_ok;
    bool    enc_ok;
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

    /* I2C 양쪽 버스 스캔 — 디버그 가시성용. AK09916 은 ICM 내장 (AUX bus)
     * 이라 본 스캔에는 안 잡힘. RM3100 자리 비어있어 외부 디바이스 없으면
     * (none) 출력이 정상. */
    i2c_scan(&hi2c1, "i2c1");
    i2c_scan(&hi2c2, "i2c2");

    uint16_t adc_raw = 0;
    bool adc_ok = adc_read_once(&adc_raw);

    /* IMU/Mag status — control task 의 imu_processor_init() 이 끝났는지 query.
     * i2c_scan 두 번 (~1.1초) 동안 control task 가 imu_init+mag_init 끝낼 시간 충분. */
    const bool    imu_ready  = imu_processor_imu_ready();
    const uint8_t imu_whoami = imu_processor_get_whoami();
    const bool    mag_ready  = imu_processor_mag_ready();

    printf("[F1-init] motor=%s enc=%s imu=%s(whoami=0x%02X) mag=%s adc=%s(raw=%u)\r\n",
           s_st.motor_ok ? "OK" : "FAIL",
           s_st.enc_ok   ? "OK" : "FAIL",
           imu_ready     ? "READY" : "FAIL", imu_whoami,
           mag_ready     ? "READY" : "FAIL",
           adc_ok        ? "OK" : "FAIL", (unsigned)adc_raw);
}

void f1_sanity_tick(void)
{
    s_st.count++;

    /* F3: 속도·거리 (mm/s, mm 정수 — nano-printf float 미지원 회피). */
    int v_l = (int)(encoder_read_velocity_mps(ENC_LEFT)  * 1000.0f);
    int v_r = (int)(encoder_read_velocity_mps(ENC_RIGHT) * 1000.0f);
    int d_l = (int)(encoder_read_distance_m(ENC_LEFT)    * 1000.0f);
    int d_r = (int)(encoder_read_distance_m(ENC_RIGHT)   * 1000.0f);

    /* F4: PID 상태 (target, duty, stall). */
    int t_l    = (int)(speed_controller_get_target(MOTOR_LEFT)  * 1000.0f);
    int t_r    = (int)(speed_controller_get_target(MOTOR_RIGHT) * 1000.0f);
    int duty_l = (int)(speed_controller_get_duty(MOTOR_LEFT)    * 100.0f);
    int duty_r = (int)(speed_controller_get_duty(MOTOR_RIGHT)   * 100.0f);
    const char *flags;
    if (safety_monitor_has_fault())             flags = " [FAULT]";
    else if (safety_monitor_cmdvel_timeout())   flags = " [CMDVEL_TO]";
    else                                        flags = "";

    printf("[F1 %4lu] tgt L=%+d R=%+d  v L=%+d R=%+d (mm/s)  duty L=%+d%% R=%+d%%  dist L=%+d R=%+d (mm)  heap=%u%s\r\n",
           (unsigned long)s_st.count,
           t_l, t_r, v_l, v_r, duty_l, duty_r, d_l, d_r,
           (unsigned)xPortGetFreeHeapSize(),
           flags);
}
