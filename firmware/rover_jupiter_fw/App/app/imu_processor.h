/**
 * @file    imu_processor.h
 * @brief   F7 — ICM-20948 raw → SI 변환 + 최신 샘플 캐시.
 *          F7.5 — AK09916 자기계 raw → Tesla 변환 추가.
 *
 *   100Hz 호출 (control task) — imu_processor_update() 가 SPI burst read 후
 *   raw → m/s², rad/s 변환 + 내부 캐시 저장. 동일 cycle 에 mag 도 폴링.
 *   micro-ROS task 가 imu_processor_get() / _get_mag() 로 스냅샷 읽어 publish.
 *
 * Axis 매핑: 일단 ICM-20948 자체 축 그대로 (X, Y, Z).
 * 차체 좌표계 (ROS REP-103: X 전방, Y 좌측, Z 위방향) 와 정합은
 * 보드 위 IMU 칩 방향에 따라 보정 필요 — F7 검증 시 중력 벡터로 확인.
 *
 * AK09916 축은 ICM accel/gyro 축과 다를 수 있음 (datasheet §5). F7.5
 * 검증 시 자기 북쪽 회전 실험으로 매핑 확인.
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

typedef struct {
    float    mx, my, mz;   /* Tesla */
    uint32_t ts_ms;
    bool     valid;        /* false 면 mag_init 실패 또는 read 실패 */
} MagSi;

/** **모든 ICM-20948 SPI 하드웨어 init** 을 단독 점유 (imu_init + mag_init).
 *  f1_sanity 가 SPI 만지면 race 발생 (DEVICE_RESET 도중 mag_init writes 가
 *  default 로 되돌아감). 이 init 은 control task (AboveNormal) 에서 호출 —
 *  HAL_Delay 동안 f1_sanity 는 I2C scan 만 수행해 SPI race 차단. */
void imu_processor_init(void);

/** 주기적 호출 (100Hz). SPI 읽기 + SI 변환 + 캐시 갱신 (IMU + Mag).
 *  imu_init/mag_init 실패 시 해당 read 호출 자체를 skip. */
void imu_processor_update(void);

/** 최신 IMU SI 스냅샷. */
void imu_processor_get(ImuSi *out);

/** 최신 Mag SI 스냅샷. */
void imu_processor_get_mag(MagSi *out);

/** imu_init 성공 여부 + WHOAMI (f1_sanity status 표시용). */
bool    imu_processor_imu_ready(void);
uint8_t imu_processor_get_whoami(void);

/** mag_init 성공 여부 (f1_sanity status 표시용). */
bool imu_processor_mag_ready(void);

#ifdef __cplusplus
}
#endif

#endif
