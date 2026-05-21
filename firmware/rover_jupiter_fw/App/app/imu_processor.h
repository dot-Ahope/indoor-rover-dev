/**
 * @file    imu_processor.h
 * @brief   F7 — ICM-20948 raw → SI 변환 + 최신 샘플 캐시.
 *
 *   100Hz 호출 (control task) — imu_processor_update() 가 SPI burst read 후
 *   raw → m/s², rad/s 변환 + 내부 캐시 저장.
 *   micro-ROS task 가 imu_processor_get() 으로 스냅샷 읽어 publish.
 *
 * Axis 매핑: 일단 ICM-20948 자체 축 그대로 (X, Y, Z).
 * 차체 좌표계 (ROS REP-103: X 전방, Y 좌측, Z 위방향) 와 정합은
 * 보드 위 IMU 칩 방향에 따라 보정 필요 — F7 검증 시 중력 벡터로 확인.
 */
#ifndef APP_APP_IMU_PROCESSOR_H
#define APP_APP_IMU_PROCESSOR_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float    ax, ay, az;   /* m/s² */
    float    gx, gy, gz;   /* rad/s */
    float    temp_c;       /* °C */
    uint32_t ts_ms;        /* HAL_GetTick */
    bool     valid;        /* false 면 init 실패 / 못 읽음 */
} ImuSi;

void imu_processor_init(void);

/** 주기적 호출 (100Hz). SPI 읽기 + SI 변환 + 캐시 갱신. */
void imu_processor_update(void);

/** 최신 SI 샘플 스냅샷. */
void imu_processor_get(ImuSi *out);

#ifdef __cplusplus
}
#endif

#endif
