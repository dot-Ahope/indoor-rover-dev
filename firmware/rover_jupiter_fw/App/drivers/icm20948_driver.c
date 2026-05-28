/**
 * @file    icm20948_driver.c
 * @brief   ICM-20948 SPI 드라이버.
 *
 *   F7   — base init + 14-byte burst read (accel/gyro/temp)
 *   F7.5 — AUX I2C master 헬퍼 (AK09916 액세스용)
 *
 * 핵심 설계 (작동 확인된 sandbox 기준):
 *   - **Cold-boot recovery**: CS strobe + MISO pull-up + dummy read → SPI lock 확보
 *   - **Bank 캐시**: 같은 bank 재선택 SPI 트래픽 절약. DEVICE_RESET 후 무효화 필수.
 *   - **SLV0 one-shot 후 disable**: 다음 reconfigure 전에 ICM 가 같은 transaction
 *     반복하지 않도록 CTRL=0 으로 끄기.
 *   - **모든 HW init 은 main.c 의 scheduler 시작 전에 수행** — task race 차단.
 */
#include "icm20948_driver.h"
#include "main.h"
#include "spi.h"
#include <stdio.h>

/* Bank selector — 모든 bank 공통 위치. */
#define ICM_REG_BANK_SEL    0x7F

/* Bank 0 레지스터 */
#define ICM_REG_WHOAMI            0x00
#define ICM_REG_USER_CTRL         0x03   /* I2C_MST_EN bit5, I2C_IF_DIS bit4 */
#define ICM_REG_LP_CONFIG         0x05
#define ICM_REG_PWR_MGMT_1        0x06   /* DEVICE_RESET bit7, SLEEP bit6, CLKSEL[2:0] */
#define ICM_REG_PWR_MGMT_2        0x07
#define ICM_REG_INT_PIN_CFG       0x0F
#define ICM_REG_INT_ENABLE_1      0x11
#define ICM_REG_I2C_MST_STATUS    0x17
#define ICM_REG_ACCEL_XOUT_H      0x2D   /* 14-byte burst: accel 6 + gyro 6 + temp 2 */
#define ICM_REG_EXT_SLV_SENS_00   0x3B   /* AUX slave read 결과 (최대 24바이트) */

/* Bank 2 레지스터 */
#define ICM_REG_GYRO_CFG_1   0x01
#define ICM_REG_ACCEL_CFG    0x14

/* Bank 3 레지스터 (I2C master) */
#define ICM_REG_I2C_MST_CTRL    0x01
#define ICM_REG_I2C_SLV0_ADDR   0x03   /* RNW bit7 | 7-bit addr */
#define ICM_REG_I2C_SLV0_REG    0x04
#define ICM_REG_I2C_SLV0_CTRL   0x05   /* EN bit7, BYTE_SW bit6, REG_DIS bit5, GRP bit4, LEN[3:0] */
#define ICM_REG_I2C_SLV0_DO     0x06

/* USER_CTRL bits */
#define USER_CTRL_I2C_MST_EN  (1u << 5)
#define USER_CTRL_I2C_IF_DIS  (1u << 4)

/* AUX I2C transaction 완료 대기 — ICM ODR 1 cycle 이면 충분. */
#define AUX_DELAY_MS    10

#define CS_LOW()   HAL_GPIO_WritePin(IMU_CS_GPIO_Port, IMU_CS_Pin, GPIO_PIN_RESET)
#define CS_HIGH()  HAL_GPIO_WritePin(IMU_CS_GPIO_Port, IMU_CS_Pin, GPIO_PIN_SET)

/* Bank 캐시 — 같은 bank 반복 선택 회피. 0xFF = 알 수 없음 (다음 액세스 시 강제 write). */
static uint8_t s_current_bank = 0xFF;

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

static bool spi_read_burst(uint8_t reg, uint8_t *buf, size_t len)
{
    if (len == 0 || len > 32) return false;
    uint8_t tx[33] = { (uint8_t)(reg | 0x80u) };
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
    if (bank == s_current_bank) return true;
    if (!spi_write_reg(ICM_REG_BANK_SEL, (uint8_t)((bank & 0x03u) << 4))) return false;
    s_current_bank = bank;
    return true;
}

/* MISO 에 pull-up — 슬레이브 silent (line floats 0xFF) 와 chip 이 실제로 0x00
 * 구동하는 상황을 구분 가능하게. ICM SPI 첫 통신 안정성 향상.
 * PB14 = SPI2_MISO (AF5). */
static void miso_pullup(void)
{
    GPIO_InitTypeDef cfg = {
        .Pin       = GPIO_PIN_14,
        .Mode      = GPIO_MODE_AF_PP,
        .Pull      = GPIO_PULLUP,
        .Speed     = GPIO_SPEED_FREQ_VERY_HIGH,
        .Alternate = GPIO_AF5_SPI2,
    };
    HAL_GPIO_Init(GPIOB, &cfg);
}

bool imu_init(void)
{
    /* === Cold-boot recovery ===
     * STM32 만 reflash 되거나 power-on 직후 ICM SPI 가 lock 안 된 경우가 있음.
     * 100ms VDD settle → MISO pull-up → CS strobe → dummy read 로 SPI 강제 lock. */
    CS_HIGH();
    HAL_Delay(100);

    miso_pullup();

    /* CS strobe: cold-boot 시 SPI 모드 lock 용. */
    CS_LOW();
    HAL_Delay(1);
    CS_HIGH();
    HAL_Delay(1);

    /* Bank 캐시 무효화 → 다음 select_bank 가 강제로 write. */
    s_current_bank = 0xFF;

    /* 첫 SPI 바이트는 cold-boot 시 garbage 가능 → discard. */
    uint8_t dummy = 0;
    (void)spi_read_reg(ICM_REG_WHOAMI, &dummy);

    /* === DEVICE_RESET === */
    if (!select_bank(0)) return false;
    if (!spi_write_reg(ICM_REG_PWR_MGMT_1, 0x80)) return false;   /* DEVICE_RESET */
    HAL_Delay(100);
    /* Reset 으로 bank latch 도 0 으로 돌아감 — 캐시 무효화. */
    s_current_bank = 0xFF;

    /* === Wake (CLKSEL=auto) === */
    if (!select_bank(0)) return false;
    if (!spi_write_reg(ICM_REG_PWR_MGMT_1, 0x01)) return false;
    HAL_Delay(35);   /* clock stabilization */

    /* I2C 인터페이스 disable (SPI 전용). I2C_MST_EN 은 mag_init 단계에서 OR. */
    if (!spi_write_reg(ICM_REG_USER_CTRL, USER_CTRL_I2C_IF_DIS)) return false;

    /* === WHO_AM_I 검증 === */
    uint8_t whoami = 0;
    if (!spi_read_reg(ICM_REG_WHOAMI, &whoami)) return false;
    if (whoami != ICM20948_WHOAMI) {
        printf("[icm] WHO_AM_I=0x%02X (expected 0x%02X)\r\n", whoami, ICM20948_WHOAMI);
        return false;
    }
    printf("[icm] WHO_AM_I=0x%02X OK\r\n", whoami);

    /* PWR_MGMT_2: accel·gyro 모두 enable. */
    if (!spi_write_reg(ICM_REG_PWR_MGMT_2, 0x00)) return false;

    /* INT pin / source 비활성 — F8 에서 cmd_vel watchdog 등 사용 시 별도 enable. */
    if (!spi_write_reg(ICM_REG_INT_PIN_CFG, 0x00)) return false;
    if (!spi_write_reg(ICM_REG_INT_ENABLE_1, 0x00)) return false;

    /* === Bank 2: gyro/accel range·DLPF === */
    if (!select_bank(2)) return false;
    /* GYRO_CONFIG_1: DLPFCFG=0 (~196Hz BW), FS_SEL=00 (±250dps), FCHOICE=1. */
    if (!spi_write_reg(ICM_REG_GYRO_CFG_1, 0x01)) return false;
    /* ACCEL_CONFIG: DLPFCFG=0 (~246Hz BW), FS_SEL=00 (±2g), FCHOICE=1. */
    if (!spi_write_reg(ICM_REG_ACCEL_CFG, 0x01)) return false;

    if (!select_bank(0)) return false;
    return true;
}

bool imu_read_whoami(uint8_t *out)
{
    CS_HIGH();
    if (!select_bank(0)) return false;
    return spi_read_reg(ICM_REG_WHOAMI, out);
}

bool imu_read(ImuSample *out)
{
    if (!out) return false;
    if (!select_bank(0)) return false;
    uint8_t buf[14];
    if (!spi_read_burst(ICM_REG_ACCEL_XOUT_H, buf, 14)) return false;

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

/* ─── F7.5 AUX I2C master 헬퍼 구현 ─────────────────────────────────── */

bool icm20948_i2c_master_enable(void)
{
    /* USER_CTRL = I2C_IF_DIS | I2C_MST_EN. (IF_DIS 는 imu_init 에서 이미 set,
     * 여기선 명시적으로 두 비트 다 set 해 안전.) */
    if (!select_bank(0)) return false;
    if (!spi_write_reg(ICM_REG_USER_CTRL, USER_CTRL_I2C_IF_DIS | USER_CTRL_I2C_MST_EN)) return false;

    /* I2C_MST_CTRL = 0x07 (400 kHz, NSR=0). sandbox 검증 값. */
    if (!select_bank(3)) return false;
    if (!spi_write_reg(ICM_REG_I2C_MST_CTRL, 0x07)) return false;

    if (!select_bank(0)) return false;
    HAL_Delay(10);
    return true;
}

bool icm20948_aux_slv0_write_byte(uint8_t aux_addr, uint8_t aux_reg, uint8_t val)
{
    if (!select_bank(3)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_ADDR, (uint8_t)(aux_addr & 0x7Fu))) return false;  /* RNW=0 */
    if (!spi_write_reg(ICM_REG_I2C_SLV0_REG,  aux_reg)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_DO,   val)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_CTRL, 0x80u | 1u)) return false;  /* EN | LEN=1 */
    HAL_Delay(AUX_DELAY_MS);
    /* **SLV0 disable 필수** — 안 그러면 ICM 이 매 ODR 마다 같은 write 반복.
     * 다음 reconfigure 시 transient 상태에서 잘못된 transaction 실행 위험. */
    if (!spi_write_reg(ICM_REG_I2C_SLV0_CTRL, 0x00)) return false;
    return select_bank(0);
}

bool icm20948_aux_slv0_read_byte(uint8_t aux_addr, uint8_t aux_reg, uint8_t *val)
{
    if (!val) return false;
    if (!select_bank(3)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_ADDR, (uint8_t)(0x80u | aux_addr))) return false; /* RNW=1 */
    if (!spi_write_reg(ICM_REG_I2C_SLV0_REG,  aux_reg)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_CTRL, 0x80u | 1u)) return false;
    HAL_Delay(AUX_DELAY_MS);
    /* 결과는 EXT_SLV_SENS_DATA_00 (Bank 0) 에 적재. */
    if (!select_bank(0)) return false;
    if (!spi_read_reg(ICM_REG_EXT_SLV_SENS_00, val)) return false;
    /* SLV0 disable. */
    if (!select_bank(3)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_CTRL, 0x00)) return false;
    return select_bank(0);
}

bool icm20948_aux_setup_slave0_read(uint8_t aux_addr, uint8_t aux_reg, uint8_t len)
{
    if (len == 0 || len > 15) return false;
    if (!select_bank(3)) return false;
    if (!spi_write_reg(ICM_REG_I2C_SLV0_ADDR, (uint8_t)(0x80u | aux_addr))) return false; /* RNW=1 */
    if (!spi_write_reg(ICM_REG_I2C_SLV0_REG,  aux_reg)) return false;
    /* EN | LEN — EN 유지로 streaming. */
    if (!spi_write_reg(ICM_REG_I2C_SLV0_CTRL, (uint8_t)(0x80u | (len & 0x0Fu)))) return false;
    return select_bank(0);
}

bool icm20948_aux_read_ext_sens(uint8_t *buf, uint8_t len)
{
    if (!buf || len == 0 || len > 24) return false;
    if (!select_bank(0)) return false;
    return spi_read_burst(ICM_REG_EXT_SLV_SENS_00, buf, len);
}

bool icm20948_debug_read(uint8_t bank, uint8_t reg, uint8_t *val)
{
    if (!val) return false;
    if (!select_bank(bank)) return false;
    bool ok = spi_read_reg(reg, val);
    (void)select_bank(0);
    return ok;
}
