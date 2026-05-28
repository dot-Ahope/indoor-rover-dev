/**
 * @file    imu_processor.c
 * @brief   F7  IMU raw → SI 변환 + F7.5 Mag raw → Tesla + F8.5 gyro bias auto-cal.
 */
#include "imu_processor.h"

#include <string.h>
#include <stdio.h>
#include "stm32f4xx_hal.h"

#include "i_imu.h"
#include "i_magnetometer.h"
#include "icm20948_driver.h"
#include "ak09916_driver.h"

#define GRAV_MPS2          9.80665f
#define DEG_TO_RAD         0.01745329252f

/* LSB → SI 변환 상수. F7 default range: ±2g, ±250dps. */
#define ACCEL_LSB_TO_MPS2  (GRAV_MPS2 / ICM20948_ACCEL_LSB_PER_G)
#define GYRO_LSB_TO_RADPS  (DEG_TO_RAD / ICM20948_GYRO_LSB_PER_DPS)

/* Temp: ICM-20948 datasheet § 8.31 (TEMP_OUT) — RoomTemp_Offset 약 0, sensitivity 333.87 LSB/°C, 21°C nominal. */
#define TEMP_SENS_LSB_PER_C  333.87f
#define TEMP_ROOM_OFFSET     21.0f

static ImuSi   s_si;
static MagSi   s_mag;
static bool    s_imu_present;   /* imu_init 성공 */
static bool    s_mag_present;   /* mag_init 성공 */
static uint8_t s_imu_whoami;    /* WHOAMI 캐시 */

/* F8.5 — Gyro bias auto-calibration. 부팅 시 N 샘플 평균을 bias 로 저장.
 * icm20948_gyro_z_bias 메모리: z 축 chip-specific bias 약 +0.66 rad/s 알려진 값.
 * 차감 후 publish 하면 Jetson EKF/Madgwick 가 빠르게 수렴. */
#define GYRO_CAL_SAMPLES      200
#define GYRO_CAL_INTERVAL_MS  10
static float s_gyro_bias[3] = {0.0f, 0.0f, 0.0f};

static void imu_calibrate_gyro_bias(void)
{
    int32_t accum[3] = {0, 0, 0};
    int n_ok = 0;
    for (int i = 0; i < GYRO_CAL_SAMPLES; i++) {
        ImuSample raw;
        if (imu_read(&raw)) {
            accum[0] += raw.gyro_raw[0];
            accum[1] += raw.gyro_raw[1];
            accum[2] += raw.gyro_raw[2];
            n_ok++;
        }
        HAL_Delay(GYRO_CAL_INTERVAL_MS);
    }
    if (n_ok < GYRO_CAL_SAMPLES / 2) {
        printf("[imu_cal] gyro cal FAIL — only %d/%d samples\r\n",
               n_ok, GYRO_CAL_SAMPLES);
        return;
    }
    s_gyro_bias[0] = ((float)accum[0] / (float)n_ok) * GYRO_LSB_TO_RADPS;
    s_gyro_bias[1] = ((float)accum[1] / (float)n_ok) * GYRO_LSB_TO_RADPS;
    s_gyro_bias[2] = ((float)accum[2] / (float)n_ok) * GYRO_LSB_TO_RADPS;
    /* mrad/s 출력 (nano-printf float 미지원 회피). */
    printf("[imu_cal] gyro bias (mrad/s): x=%+d y=%+d z=%+d (N=%d)\r\n",
           (int)(s_gyro_bias[0] * 1000.0f),
           (int)(s_gyro_bias[1] * 1000.0f),
           (int)(s_gyro_bias[2] * 1000.0f),
           n_ok);
}

void imu_processor_init(void)
{
    memset(&s_si,  0, sizeof(s_si));
    memset(&s_mag, 0, sizeof(s_mag));

    /* ICM-20948 + AK09916 HW init — control task 단독 점유 (SPI race 차단).
     * imu_init: DEVICE_RESET → wake → PWR_MGMT_2 → bank2 config.
     * 그 후 ICM 가 안정된 상태에서 mag_init 진행 (I2C master, AK09916 setup). */
    s_imu_present = imu_init();
    if (s_imu_present) {
        (void)imu_read_whoami(&s_imu_whoami);
        s_mag_present = mag_init();
        /* F8.5 — gyro bias 캘. ~2초 소요 (200 samples × 10ms). 부팅 시 정지 가정.
         * 실패해도 진행 — bias=0 으로 raw 그대로. */
        imu_calibrate_gyro_bias();
    } else {
        s_imu_whoami  = 0;
        s_mag_present = false;
    }
}

bool imu_processor_imu_ready(void)   { return s_imu_present; }
uint8_t imu_processor_get_whoami(void) { return s_imu_whoami; }
bool imu_processor_mag_ready(void)   { return s_mag_present; }

void imu_processor_update(void)
{
    if (!s_imu_present) { s_si.valid = false; return; }

    ImuSample raw;
    if (imu_read(&raw)) {
        /* Direct axis mapping — ICM 칩 축 그대로 (보드 mount 보정은 F7 검증 후). */
        s_si.ax = (float)raw.accel_raw[0] * ACCEL_LSB_TO_MPS2;
        s_si.ay = (float)raw.accel_raw[1] * ACCEL_LSB_TO_MPS2;
        s_si.az = (float)raw.accel_raw[2] * ACCEL_LSB_TO_MPS2;
        /* F8.5 — gyro bias 차감 (부팅 시 평균). EKF/Madgwick 빠른 수렴. */
        s_si.gx = (float)raw.gyro_raw[0]  * GYRO_LSB_TO_RADPS - s_gyro_bias[0];
        s_si.gy = (float)raw.gyro_raw[1]  * GYRO_LSB_TO_RADPS - s_gyro_bias[1];
        s_si.gz = (float)raw.gyro_raw[2]  * GYRO_LSB_TO_RADPS - s_gyro_bias[2];
        s_si.temp_c = ((float)raw.temp_raw / TEMP_SENS_LSB_PER_C) + TEMP_ROOM_OFFSET;
        s_si.ts_ms  = raw.ts_ms;
        s_si.valid  = true;
    } else {
        s_si.valid = false;
    }

    /* Mag — AK09916 측정 50Hz 라 100Hz 호출 중 절반은 같은 샘플 (게이팅 X).
     * mag_init 실패 시 SPI 낭비 방지로 read skip. */
    if (s_mag_present) {
        MagSample mraw;
        if (mag_read(&mraw)) {
            s_mag.mx = (float)mraw.mag_raw[0] * AK09916_LSB_TO_TESLA;
            s_mag.my = (float)mraw.mag_raw[1] * AK09916_LSB_TO_TESLA;
            s_mag.mz = (float)mraw.mag_raw[2] * AK09916_LSB_TO_TESLA;
            s_mag.ts_ms = mraw.ts_ms;
            s_mag.valid = true;
        } else {
            s_mag.valid = false;
        }
    }
}

void imu_processor_get(ImuSi *out)
{
    if (!out) return;
    *out = s_si;
}

void imu_processor_get_mag(MagSi *out)
{
    if (!out) return;
    *out = s_mag;
}
