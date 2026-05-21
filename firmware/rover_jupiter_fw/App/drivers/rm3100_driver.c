/**
 * @file    rm3100_driver.c
 * @brief   RM3100 I2C 드라이버 (F1: REVID 검증 수준).
 */
#include "rm3100_driver.h"
#include "main.h"
#include "i2c.h"

#define RM3100_HAL_ADDR  (RM3100_I2C_ADDR_7BIT << 1)
#define RM3100_REG_REVID 0x36

bool mag_init(void)
{
    uint8_t revid = 0;
    if (!mag_read_revid(&revid)) return false;
    return revid == RM3100_REVID_EXPECTED;
    /* TODO(F7): CMM(continuous measurement) 모드 활성, TMRC, CCR 설정 */
}

bool mag_read_revid(uint8_t *out)
{
    return HAL_I2C_Mem_Read(&hi2c1, RM3100_HAL_ADDR, RM3100_REG_REVID,
                            I2C_MEMADD_SIZE_8BIT, out, 1, 100) == HAL_OK;
}

bool mag_read(MagSample *out)
{
    /* TODO(F7): MX/MY/MZ 24-bit raw 9바이트 burst read + sign-extend */
    (void)out;
    return false;
}
