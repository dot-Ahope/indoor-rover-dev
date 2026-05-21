/**
 * @file    i_imu.h
 * @brief   HAL — IMU (6축) 인터페이스
 *
 * 구현체: App/drivers/icm20948_driver.c (SPI2)
 * 양산기 이식 시 산업급 IMU(예: BMI088) 로 교체 가능.
 *
 * 단위 변환·캘리브레이션은 App Layer 책임. 본 인터페이스는 raw int16.
 * (ROS REP-103 단위 변환은 micro-ROS 발행 시점에 수행)
 */
#ifndef APP_HAL_I_IMU_H
#define APP_HAL_I_IMU_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/** Raw 6축 + 온도. 채널 차원 X/Y/Z. */
typedef struct {
    int16_t  accel_raw[3];
    int16_t  gyro_raw[3];
    int16_t  temp_raw;
    uint32_t ts_ms;   /* HAL_GetTick() 시각 — 동기 검증용 */
} ImuSample;

/** IMU 초기화 (CS GPIO + SPI 설정 + WHO_AM_I 확인 + 센서 활성). */
bool imu_init(void);

/** 동기식 raw 읽기. SPI burst read. */
bool imu_read(ImuSample *out);

/** WHO_AM_I 1바이트. F1 단계 sanity 검증용. */
bool imu_read_whoami(uint8_t *out);

#ifdef __cplusplus
}
#endif

#endif /* APP_HAL_I_IMU_H */
