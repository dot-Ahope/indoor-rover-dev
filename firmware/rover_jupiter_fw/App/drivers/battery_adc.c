/**
 * @file battery_adc.c
 * @brief battery_adc.h 구현.
 */
#include "battery_adc.h"

#include "adc.h"
#include "cmsis_os.h"

/* F8.5 — 배터리 전압 변환. 실측 캘리브레이션 (2026-05-28, microros_task.c 에서 옮김):
 *   V_battery = 11.9 V, ADC raw = 3645 → divider ratio = 11.9 / (3645 × 3.3/4095) = 4.05
 *   회로도 의도값은 4:1 (R1≈30k, R2≈10k) — 저항 tol·VDDA 편차로 4.05 측정. */
#define VIN_DIVIDER_RATIO   4.05f
#define ADC_REF_VOLTS       3.3f
#define ADC_LSB_TO_VOLTS    (ADC_REF_VOLTS * VIN_DIVIDER_RATIO / 4095.0f)

static osMutexId_t s_mtx = NULL;

void battery_adc_init(void)
{
    if (s_mtx == NULL) s_mtx = osMutexNew(NULL);
}

bool battery_adc_read(float *v)
{
    if (s_mtx == NULL || osMutexAcquire(s_mtx, 20) != osOK) return false;
    bool ok = false;
    uint16_t raw = 0;
    if (HAL_ADC_Start(&hadc1) == HAL_OK && HAL_ADC_PollForConversion(&hadc1, 5) == HAL_OK) {
        raw = (uint16_t)HAL_ADC_GetValue(&hadc1);
        ok = true;
    }
    HAL_ADC_Stop(&hadc1);
    osMutexRelease(s_mtx);
    if (ok) *v = (float)raw * ADC_LSB_TO_VOLTS;
    return ok;
}
