/**
 * @file    ak09916_driver.c
 * @brief   AK09916 (ICM-20948 내장) 자기계 드라이버 — i_magnetometer 구현.
 *
 * 초기화 — sandbox (c:\Workspace\Code\sandbox\icm20948) 검증 절차:
 *   1) ICM I2C master 활성 (USER_CTRL | I2C_MST_EN, I2C_MST_CTRL=0x07)
 *   2) AK09916 soft reset: CNTL3=0x01, 100ms 대기
 *   3) WIA2 (=0x09) 검증 — 칩 식별
 *   4) CNTL2=0x08 (continuous mode 4, 100 Hz)
 *   5) SLV0 streaming arm: HXL 부터 8바이트 자동 read 매 ODR cycle
 *      → EXT_SLV_SENS_DATA_00..07 적재: HXL HXH HYL HYH HZL HZH dummy ST2
 *      ST2 까지 읽어야 AK09916 가 다음 측정 갱신 (datasheet §6)
 *
 * 데이터 형식: 16-bit signed, **little-endian** (ICM 의 big-endian 과 반대).
 */
#include "ak09916_driver.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

#include "main.h"
#include "icm20948_driver.h"

#define AK_REG_WIA2   0x01   /* Device ID — 0x09 */
#define AK_REG_HXL    0x11   /* streaming read 시작점 */
#define AK_REG_CNTL2  0x31   /* operation mode */
#define AK_REG_CNTL3  0x32   /* soft reset bit0 */

#define AK_WIA2_EXPECTED     0x09
#define AK_CNTL2_CONT_100HZ  0x08   /* continuous mode 4 */
#define AK_STREAM_LEN        8      /* HXL HXH HYL HYH HZL HZH dummy ST2 */

bool mag_init(void)
{
    if (!icm20948_i2c_master_enable()) {
        printf("[ak09916] master_enable FAIL\r\n");
        return false;
    }

    /* AK09916 soft reset. */
    if (!icm20948_aux_slv0_write_byte(AK09916_I2C_ADDR_7BIT, AK_REG_CNTL3, 0x01)) {
        printf("[ak09916] CNTL3 reset FAIL\r\n");
        return false;
    }
    HAL_Delay(100);

    /* WIA2 검증 — 칩 식별. WIA1 (=0x48, Asahi Kasei) 보다 WIA2 (=0x09, AK09916)
     * 가 칩별 식별에 더 의미 있음. */
    uint8_t wia2 = 0;
    if (!icm20948_aux_slv0_read_byte(AK09916_I2C_ADDR_7BIT, AK_REG_WIA2, &wia2)) {
        printf("[ak09916] WIA2 read FAIL\r\n");
        return false;
    }
    if (wia2 != AK_WIA2_EXPECTED) {
        printf("[ak09916] WIA2=0x%02X (expected 0x09)\r\n", wia2);
        return false;
    }
    printf("[ak09916] WIA2=0x%02X OK\r\n", wia2);

    /* Continuous mode 4 (100 Hz). */
    if (!icm20948_aux_slv0_write_byte(AK09916_I2C_ADDR_7BIT, AK_REG_CNTL2, AK_CNTL2_CONT_100HZ)) {
        printf("[ak09916] CNTL2 write FAIL\r\n");
        return false;
    }
    HAL_Delay(10);

    /* SLV0 streaming arm: HXL 부터 8바이트 — ST2 포함이라 다음 측정 자동 unlock. */
    if (!icm20948_aux_setup_slave0_read(AK09916_I2C_ADDR_7BIT, AK_REG_HXL, AK_STREAM_LEN)) {
        printf("[ak09916] SLV0 stream setup FAIL\r\n");
        return false;
    }

    HAL_Delay(20);   /* 첫 ICM read cycle 대기 */
    printf("[ak09916] init OK\r\n");
    return true;
}

bool mag_read_revid(uint8_t *out)
{
    /* HAL 호환용 stub — WIA2 single-shot read. */
    if (!out) return false;
    return icm20948_aux_slv0_read_byte(AK09916_I2C_ADDR_7BIT, AK_REG_WIA2, out);
}

bool mag_read(MagSample *out)
{
    if (!out) return false;

    uint8_t buf[AK_STREAM_LEN];
    if (!icm20948_aux_read_ext_sens(buf, AK_STREAM_LEN)) return false;

    /* AK09916 little-endian (LSB 먼저). buf[0]=HXL buf[1]=HXH ... buf[7]=ST2 */
    const int16_t hx = (int16_t)((uint16_t)buf[0] | ((uint16_t)buf[1] << 8));
    const int16_t hy = (int16_t)((uint16_t)buf[2] | ((uint16_t)buf[3] << 8));
    const int16_t hz = (int16_t)((uint16_t)buf[4] | ((uint16_t)buf[5] << 8));

    out->mag_raw[0] = (int32_t)hx;
    out->mag_raw[1] = (int32_t)hy;
    out->mag_raw[2] = (int32_t)hz;
    out->ts_ms      = HAL_GetTick();
    return true;
}
