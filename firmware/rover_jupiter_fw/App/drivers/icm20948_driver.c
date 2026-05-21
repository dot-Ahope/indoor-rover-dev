/**
 * @file    icm20948_driver.c
 * @brief   ICM-20948 SPI 드라이버 (F7: 본 init + 14-byte burst read).
 */
#include "icm20948_driver.h"
#include "main.h"
#include "spi.h"

/* Bank selector — 모든 bank 공통 위치. */
#define ICM_REG_BANK_SEL    0x7F

/* Bank 0 레지스터 */
#define ICM_REG_WHOAMI      0x00
#define ICM_REG_PWR_MGMT_1  0x06   /* CLKSEL[2:0]=1 auto, SLEEP bit5 */
#define ICM_REG_PWR_MGMT_2  0x07   /* DISABLE_ACCEL[5:3], DISABLE_GYRO[2:0] */
#define ICM_REG_ACCEL_XOUT_H 0x2D  /* burst start: 14 bytes (accel 6 + temp 2 + gyro 6) */

/* Bank 2 레지스터 (gyro·accel config) */
#define ICM_REG_GYRO_CFG_1   0x01  /* FS_SEL[2:1]=00 (±250dps), DLPFCFG[5:3]=0, GYRO_FCHOICE bit0 */
#define ICM_REG_ACCEL_CFG    0x14  /* FS_SEL[2:1]=00 (±2g), DLPFCFG[5:3]=0, ACCEL_FCHOICE bit0 */

#define CS_LOW()   HAL_GPIO_WritePin(IMU_CS_GPIO_Port, IMU_CS_Pin, GPIO_PIN_RESET)
#define CS_HIGH()  HAL_GPIO_WritePin(IMU_CS_GPIO_Port, IMU_CS_Pin, GPIO_PIN_SET)

static bool spi_read_reg(uint8_t reg, uint8_t *val)
{
    uint8_t tx[2] = { (uint8_t)(reg | 0x80u), 0x00 };
    uint8_t rx[2] = { 0 };
    CS_LOW();
    HAL_StatusTypeDef st = HAL_SPI_TransmitReceive(&hspi2, tx, rx, 2, 100);
    CS_HIGH();
    if (st != HAL_OK) return false;
    *val = rx[1];
    return true;
}

static bool spi_write_reg(uint8_t reg, uint8_t val)
{
    uint8_t tx[2] = { (uint8_t)(reg & 0x7Fu), val };
    CS_LOW();
    HAL_StatusTypeDef st = HAL_SPI_Transmit(&hspi2, tx, 2, 100);
    CS_HIGH();
    return st == HAL_OK;
}

/* 연속 read: reg 부터 len 바이트. tx 첫바이트 = reg|0x80, 이후 dummy. */
static bool spi_read_burst(uint8_t reg, uint8_t *buf, size_t len)
{
    if (len == 0 || len > 32) return false;
    uint8_t tx[33] = { (uint8_t)(reg | 0x80u) };  /* 나머지 0 dummy */
    uint8_t rx[33] = { 0 };
    CS_LOW();
    HAL_StatusTypeDef st = HAL_SPI_TransmitReceive(&hspi2, tx, rx, len + 1, 100);
    CS_HIGH();
    if (st != HAL_OK) return false;
    for (size_t i = 0; i < len; i++) buf[i] = rx[i + 1];
    return true;
}

static bool select_bank(uint8_t bank)
{
    /* USER_BANK[5:4] — bank 값을 4-bit shift. bank 0~3. */
    return spi_write_reg(ICM_REG_BANK_SEL, (uint8_t)((bank & 0x03u) << 4));
}

bool imu_init(void)
{
    /* CS idle High (SPI Mode 3). */
    CS_HIGH();
    HAL_Delay(10);

    /* Bank 0. */
    if (!select_bank(0)) return false;

    /* WHO_AM_I 확인. */
    uint8_t whoami = 0;
    if (!spi_read_reg(ICM_REG_WHOAMI, &whoami)) return false;
    if (whoami != ICM20948_WHOAMI) return false;

    /* PWR_MGMT_1: SLEEP=0 (wake), CLKSEL=1 (auto best clock). */
    if (!spi_write_reg(ICM_REG_PWR_MGMT_1, 0x01)) return false;
    HAL_Delay(20);   /* wake stabilization */

    /* PWR_MGMT_2: 0x00 → accel·gyro 모두 enable (3축 each). */
    if (!spi_write_reg(ICM_REG_PWR_MGMT_2, 0x00)) return false;

    /* Bank 2 — config. */
    if (!select_bank(2)) return false;
    /* GYRO_CONFIG_1: DLPFCFG=0 (~196Hz BW), FS_SEL=00 (±250dps), GYRO_FCHOICE=1 (DLPF enable). */
    if (!spi_write_reg(ICM_REG_GYRO_CFG_1, 0x01)) return false;
    /* ACCEL_CONFIG: DLPFCFG=0 (~246Hz BW), FS_SEL=00 (±2g), ACCEL_FCHOICE=1 (DLPF enable). */
    if (!spi_write_reg(ICM_REG_ACCEL_CFG, 0x01)) return false;

    /* Bank 0 으로 복귀 — burst read 가 ACCEL_XOUT_H 부터. */
    if (!select_bank(0)) return false;

    return true;
}

bool imu_read_whoami(uint8_t *out)
{
    CS_HIGH();
    return spi_read_reg(ICM_REG_WHOAMI, out);
}

bool imu_read(ImuSample *out)
{
    if (!out) return false;
    uint8_t buf[14];
    if (!spi_read_burst(ICM_REG_ACCEL_XOUT_H, buf, 14)) return false;

    /* Big-endian int16 → host int16. */
    out->accel_raw[0] = (int16_t)((buf[0]  << 8) | buf[1]);
    out->accel_raw[1] = (int16_t)((buf[2]  << 8) | buf[3]);
    out->accel_raw[2] = (int16_t)((buf[4]  << 8) | buf[5]);
    out->temp_raw     = (int16_t)((buf[6]  << 8) | buf[7]);
    out->gyro_raw[0]  = (int16_t)((buf[8]  << 8) | buf[9]);
    out->gyro_raw[1]  = (int16_t)((buf[10] << 8) | buf[11]);
    out->gyro_raw[2]  = (int16_t)((buf[12] << 8) | buf[13]);
    out->ts_ms        = HAL_GetTick();
    return true;
}
