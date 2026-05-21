/**
 * @file    icm20948_driver.c
 * @brief   ICM-20948 SPI 드라이버 (F1: WHO_AM_I 검증 수준).
 */
#include "icm20948_driver.h"
#include "main.h"
#include "spi.h"

/* ICM-20948 레지스터. 모든 bank 공통(Bank 0~3에서 모두 동일 위치).
 * REG_BANK_SEL=0x7F, WHO_AM_I=0x00 (Bank 0). */
#define ICM_REG_BANK_SEL  0x7F
#define ICM_REG_WHOAMI    0x00

#define CS_LOW()   HAL_GPIO_WritePin(IMU_CS_GPIO_Port, IMU_CS_Pin, GPIO_PIN_RESET)
#define CS_HIGH()  HAL_GPIO_WritePin(IMU_CS_GPIO_Port, IMU_CS_Pin, GPIO_PIN_SET)

/* SPI read 1 byte: 첫 바이트 = (reg | 0x80). */
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

bool imu_init(void)
{
    /* CS idle High (SPI Mode 3). CubeMX는 PB12 초기 Low로 설정 → 여기서 High 로. */
    CS_HIGH();
    HAL_Delay(10);

    /* Bank 0 선택 (POR 기본값이지만 명시). */
    if (!spi_write_reg(ICM_REG_BANK_SEL, 0x00)) return false;

    /* F1 sanity: WHO_AM_I 검증. */
    uint8_t whoami = 0;
    if (!spi_read_reg(ICM_REG_WHOAMI, &whoami)) return false;
    return whoami == ICM20948_WHOAMI;
    /* TODO(F7): PWR_MGMT_1 wakeup, accel/gyro 설정, INT 활성, DMA burst read */
}

bool imu_read_whoami(uint8_t *out)
{
    CS_HIGH();
    /* Bank 0 가정. (외부에서 bank 변경했다면 호출자 책임) */
    return spi_read_reg(ICM_REG_WHOAMI, out);
}

bool imu_read(ImuSample *out)
{
    /* TODO(F7): ACCEL_XOUT_H 부터 14바이트 burst read */
    (void)out;
    return false;
}
