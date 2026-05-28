# ICM-20948 — SPI로 지자계(AK09916) 읽기 가이드

## 개요

ICM-20948은 두 개의 Die로 구성된 MCM(Multi-Chip Module)이다.

```
MCU  ←──SPI──→  ICM-20948 (Die 1: Gyro + Accel + DMP)
                     │
                내부 I2C (보조 I2C Master)
                     │
                AK09916 (Die 2: 지자계)
```

MCU는 SPI로 ICM-20948과만 통신하며, AK09916은 ICM-20948이 내부 I2C Master로 대신 폴링한다.  
초기화가 완료되면 MCU는 `EXT_SLV_SENS_DATA` 레지스터를 SPI로 읽어 지자계 값을 취득한다.

---

## 레지스터 Bank 구조

ICM-20948은 레지스터가 **Bank 0~3**으로 나뉜다.  
`REG_BANK_SEL (0x7F)` 레지스터로 Bank를 전환한 뒤 접근해야 한다.

| 작업 | Bank |
|------|------|
| 초기화 (I2C_SLV 설정) | Bank 3 |
| 데이터 읽기 (EXT_SLV_SENS_DATA) | Bank 0 |
| USER_CTRL, I2C_MST_DELAY_CTRL | Bank 0 |

```c
// Bank 전환 방법
#define REG_BANK_SEL  0x7F

void select_bank(uint8_t bank) {
    spi_write(REG_BANK_SEL, bank << 4);
}
```

---

## 주요 레지스터 정의

```c
/* ICM-20948 레지스터 — Bank 0 */
#define REG_USER_CTRL           0x03
#define REG_I2C_MST_DELAY_CTRL  0x02  // 실제로는 Bank 0 0x02
#define REG_EXT_SLV_SENS_DATA_00 0x3B  // ~ 0x43 (DATA_00 ~ DATA_08)

/* ICM-20948 레지스터 — Bank 3 */
#define REG_I2C_MST_CTRL        0x01
#define REG_I2C_SLV0_ADDR       0x03
#define REG_I2C_SLV0_REG        0x04
#define REG_I2C_SLV0_CTRL       0x05
#define REG_I2C_SLV0_DO         0x06

/* AK09916 */
#define AK09916_I2C_ADDR        0x0C
#define AK09916_REG_CNTL2       0x31  // 동작 모드 설정
#define AK09916_REG_ST1         0x10  // 데이터 준비 상태
#define AK09916_REG_HXL         0x11  // X축 데이터 시작

/* AK09916 CNTL2 모드 값 */
#define AK09916_MODE_10HZ       0x02
#define AK09916_MODE_20HZ       0x04
#define AK09916_MODE_50HZ       0x06
#define AK09916_MODE_100HZ      0x08  // 권장

/* 플래그 */
#define READ_FLAG               0x80  // SPI 읽기 시 MSB=1
#define I2C_READ_FLAG           0x80  // I2C_SLV0_ADDR 읽기 모드
#define I2C_MST_EN              0x20  // USER_CTRL 비트
```

---

## 초기화 시퀀스

### 전체 흐름

```
① ICM-20948 초기화 (리셋, 클럭 선택)
② I2C Master 활성화
③ I2C Master 클럭 설정
④ AK09916에 동작 모드 쓰기 (Write 경로)
⑤ AK09916 자동 읽기 설정 (Read 경로, ST1부터 9바이트)
⑥ 루프: EXT_SLV_SENS_DATA 읽기
```

### 단계별 코드

```c
void icm20948_mag_init(void) {

    /* ── ① ICM-20948 기본 초기화 ── */
    select_bank(0);
    spi_write(0x06, 0x01);   // PWR_MGMT_1: 클럭 자동 선택, 슬립 해제
    delay_ms(10);

    /* ── ② I2C Master 활성화 (Bank 0) ── */
    select_bank(0);
    spi_write(REG_USER_CTRL, I2C_MST_EN);  // 0x03 ← 0x20

    /* ── ③ I2C Master 클럭 400 kHz 설정 (Bank 3) ── */
    select_bank(3);
    // [3:0] = 0x07 → 400 kHz, bit[4] = 1 → stop between reads
    spi_write(REG_I2C_MST_CTRL, 0x17);    // 0x01 ← 0x17

    /* ── ④ AK09916에 CNTL2 쓰기 (연속 측정 100 Hz 설정) ── */
    // SLV0를 Write 모드로 설정
    spi_write(REG_I2C_SLV0_ADDR, AK09916_I2C_ADDR);        // 0x03 ← 0x0C (Write)
    spi_write(REG_I2C_SLV0_REG,  AK09916_REG_CNTL2);       // 0x04 ← 0x31
    spi_write(REG_I2C_SLV0_DO,   AK09916_MODE_100HZ);       // 0x06 ← 0x08
    spi_write(REG_I2C_SLV0_CTRL, 0x81);  // SLV0_EN | 1바이트
    delay_ms(10);

    /* ── ⑤ AK09916 자동 읽기 설정: ST1부터 9바이트 ── */
    // SLV0를 Read 모드로 전환
    spi_write(REG_I2C_SLV0_ADDR, AK09916_I2C_ADDR | I2C_READ_FLAG);  // 0x03 ← 0x8C
    spi_write(REG_I2C_SLV0_REG,  AK09916_REG_ST1);                    // 0x04 ← 0x10
    // SLV0_EN | 9바이트 (ST1 + HXL HXH HYL HYH HZL HZH dummy ST2)
    spi_write(REG_I2C_SLV0_CTRL, 0x89);                               // 0x05 ← 0x89

    /* ── SLV0 딜레이 ODR 동기화 활성화 (Bank 0) ── */
    select_bank(0);
    spi_write(REG_I2C_MST_DELAY_CTRL, 0x01);  // SLV0 딜레이 활성화
}
```

---

## 데이터 읽기

### EXT_SLV_SENS_DATA 레지스터 맵

ICM-20948이 샘플링마다 AK09916을 자동으로 읽어 아래 레지스터에 채워준다.

| 레지스터 | 주소 | 내용 |
|----------|------|------|
| `EXT_SLV_SENS_DATA_00` | 0x3B | ST1 (DRDY 비트 포함) |
| `EXT_SLV_SENS_DATA_01` | 0x3C | HXL — X축 하위 바이트 |
| `EXT_SLV_SENS_DATA_02` | 0x3D | HXH — X축 상위 바이트 |
| `EXT_SLV_SENS_DATA_03` | 0x3E | HYL — Y축 하위 바이트 |
| `EXT_SLV_SENS_DATA_04` | 0x3F | HYH — Y축 상위 바이트 |
| `EXT_SLV_SENS_DATA_05` | 0x40 | HZL — Z축 하위 바이트 |
| `EXT_SLV_SENS_DATA_06` | 0x41 | HZH — Z축 상위 바이트 |
| `EXT_SLV_SENS_DATA_07` | 0x42 | dummy (읽기 전용) |
| `EXT_SLV_SENS_DATA_08` | 0x43 | **ST2 — 반드시 읽어야 다음 샘플 갱신** |

### 읽기 코드

```c
typedef struct {
    int16_t x;
    int16_t y;
    int16_t z;
} mag_data_t;

bool icm20948_mag_read(mag_data_t *mag) {
    select_bank(0);

    uint8_t buf[9];
    spi_read_burst(REG_EXT_SLV_SENS_DATA_00, buf, 9);

    uint8_t st1 = buf[0];
    uint8_t st2 = buf[8];

    /* DRDY 비트 확인 (ST1[0]) */
    if (!(st1 & 0x01)) {
        return false;  // 데이터 미준비
    }

    /* Overflow 확인 (ST2[3]) */
    if (st2 & 0x08) {
        return false;  // 자기 센서 오버플로우
    }

    /* Little-endian 조합 */
    mag->x = (int16_t)((buf[2] << 8) | buf[1]);  // HXH | HXL
    mag->y = (int16_t)((buf[4] << 8) | buf[3]);  // HYH | HYL
    mag->z = (int16_t)((buf[6] << 8) | buf[5]);  // HZH | HZL

    // ST2를 읽었으므로 AK09916이 다음 샘플 갱신 가능
    return true;
}
```

### 단위 변환

```c
/* 감도: 0.15 µT/LSB */
float mag_x_uT = mag.x * 0.15f;
float mag_y_uT = mag.y * 0.15f;
float mag_z_uT = mag.z * 0.15f;
```

---

## 주의사항

### ① ST2는 반드시 읽어야 한다

ST2(0x43)를 읽어야 AK09916이 다음 측정 데이터를 갱신한다.  
ST2를 읽지 않으면 레지스터 값이 갱신되지 않고 고정된다.

```c
// 올바른 읽기: ST1(0x3B)부터 ST2(0x43)까지 9바이트 일괄 읽기
spi_read_burst(0x3B, buf, 9);  // ✅ ST2까지 포함

// 잘못된 읽기: HX~HZ만 읽고 ST2 미읽기
spi_read_burst(0x3C, buf, 6);  // ❌ 데이터 갱신 안 됨
```

### ② Bank 전환을 잊지 말 것

초기화(SLV 레지스터 설정)는 Bank 3, 데이터 읽기는 Bank 0이다.  
Bank 전환 없이 접근하면 엉뚱한 레지스터를 읽게 된다.

### ③ AK09916 좌표계와 ICM-20948 좌표계가 다르다

AK09916은 ICM-20948의 가속도계·자이로와 좌표 방향이 다르다.  
센서 퓨전 시 데이터시트의 좌표 변환 행렬을 적용해야 한다.

```c
// AK09916 → ICM-20948 좌표 정렬 예시 (보드 실장 방향에 따라 다를 수 있음)
int16_t mx =  mag_raw.x;
int16_t my =  mag_raw.y;
int16_t mz = -mag_raw.z;
```

### ④ SPI 속도 제한

ICM-20948 SPI는 최대 7 MHz이나, 안정적인 동작을 위해 초기화 시 **2.5 MHz 이하** 사용을 권장한다.

---

## 참고

| 항목 | 값 |
|------|----|
| AK09916 I2C 주소 | `0x0C` |
| 측정 범위 | ±4900 µT |
| 감도 | 0.15 µT/LSB |
| 최대 ODR | 100 Hz |
| 데이터 형식 | 16-bit signed, Little-endian |

- ICM-20948 Datasheet: DS-000189 v1.6 (TDK InvenSense, 2024-03-12)
- AK09916 Datasheet (Asahi Kasei Microdevices)
