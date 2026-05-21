/**
 * @file    imu_processor.c
 * @brief   F7 IMU raw → SI 변환 구현.
 */
#include "imu_processor.h"

#include <string.h>
#include "stm32f4xx_hal.h"

#include "i_imu.h"
#include "icm20948_driver.h"

#define GRAV_MPS2          9.80665f
#define DEG_TO_RAD         0.01745329252f

/* LSB → SI 변환 상수. F7 default range: ±2g, ±250dps. */
#define ACCEL_LSB_TO_MPS2  (GRAV_MPS2 / ICM20948_ACCEL_LSB_PER_G)
#define GYRO_LSB_TO_RADPS  (DEG_TO_RAD / ICM20948_GYRO_LSB_PER_DPS)

/* Temp: ICM-20948 datasheet § 8.31 (TEMP_OUT) — RoomTemp_Offset 약 0, sensitivity 333.87 LSB/°C, 21°C nominal. */
#define TEMP_SENS_LSB_PER_C  333.87f
#define TEMP_ROOM_OFFSET     21.0f

static ImuSi s_si;

void imu_processor_init(void)
{
    memset(&s_si, 0, sizeof(s_si));
}

void imu_processor_update(void)
{
    ImuSample raw;
    if (!imu_read(&raw)) {
        s_si.valid = false;
        return;
    }

    /* Direct axis mapping — ICM 칩 축 그대로 (보드 mount 보정은 F7 검증 후). */
    s_si.ax = (float)raw.accel_raw[0] * ACCEL_LSB_TO_MPS2;
    s_si.ay = (float)raw.accel_raw[1] * ACCEL_LSB_TO_MPS2;
    s_si.az = (float)raw.accel_raw[2] * ACCEL_LSB_TO_MPS2;
    s_si.gx = (float)raw.gyro_raw[0]  * GYRO_LSB_TO_RADPS;
    s_si.gy = (float)raw.gyro_raw[1]  * GYRO_LSB_TO_RADPS;
    s_si.gz = (float)raw.gyro_raw[2]  * GYRO_LSB_TO_RADPS;
    s_si.temp_c = ((float)raw.temp_raw / TEMP_SENS_LSB_PER_C) + TEMP_ROOM_OFFSET;
    s_si.ts_ms  = raw.ts_ms;
    s_si.valid  = true;
}

void imu_processor_get(ImuSi *out)
{
    if (!out) return;
    *out = s_si;
}
