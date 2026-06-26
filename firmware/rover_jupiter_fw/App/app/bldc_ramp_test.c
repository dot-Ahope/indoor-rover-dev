/**
 * @file    bldc_ramp_test.c
 * @brief   통합 BLDC 개방루프 duty 램프 테스트 (0단계 ①②④ 측정용).
 *
 * 받침대(공중) 전제. 한쪽 휠씩 0%→60% 를 5% 단계로, 정·역 각각 인가하며
 * UART5(115200) 로 duty/방향 로그 출력. 한 번에 측정 가능:
 *   ① duty 0%=정지 여부 / 최소 기동 duty(deadband)
 *   ② 방향 극성(어느 부호가 전진인지) / 회전 중 전환
 *   - L/R 매핑 (지령한 휠이 실제로 도는지)
 *   ④ 전류제한: 램프 중 휠을 손/지그로 구속해 전류계 관찰
 *
 * ⚠ control task(speed_controller) 와 동시에 켜면 100Hz PID 가 duty 0 으로
 *   덮어쓰므로, 본 테스트 활성 시 freertos.c 에서 controlTask 도 비활성할 것.
 *
 * 모터 타입과 무관하게 i_motor_driver 인터페이스로 동작 (통합 BLDC 검증 목적).
 */
#include "bldc_ramp_test.h"

#include <stdio.h>
#include "cmsis_os.h"
#include "i_motor_driver.h"

#define RAMP_STEP_PCT   5       /* duty 증가 폭 */
#define RAMP_MAX_PCT    60      /* 받침대 안전 상한 */
#define RAMP_DWELL_MS   3000    /* 단계당 인가 시간 */
#define RAMP_REST_MS    1000    /* 램프 종료 후 정지 시간 */

/* duty 를 정수 % 로 — newlib-nano printf 가 %f 미지원이라 회피. */
static int duty_pct(float d) { return (int)(d * 100.0f); }

/* 한 채널을 sign(+전진/-역방향) 으로 0→MAX 단계 램프. 각 단계 로그. */
static void ramp(MotorChannel ch, int sign)
{
    const char *who = (ch == MOTOR_LEFT) ? "LEFT " : "RIGHT";
    const char *dir = (sign >= 0) ? "fwd" : "rev";

    for (int pct = 0; pct <= RAMP_MAX_PCT; pct += RAMP_STEP_PCT) {
        const float duty = (float)(sign * pct) / 100.0f;
        printf("[BLDC-ramp] %s %s duty=%+d%%\r\n", who, dir, duty_pct(duty));
        motor_driver_set_duty(ch, duty);
        osDelay(RAMP_DWELL_MS);
    }
    motor_driver_stop_all();
    printf("[BLDC-ramp] %s %s done -> stop\r\n", who, dir);
    osDelay(RAMP_REST_MS);
}

void bldc_ramp_test_run(void *argument)
{
    (void)argument;

    printf("[BLDC-ramp] start in 3s — 휠 받침대/모터 전원 확인\r\n");
    osDelay(3000);

    ramp(MOTOR_LEFT,  +1);   /* 좌 전진: 최소 기동 duty / 매핑 / 0%=정지 */
    ramp(MOTOR_LEFT,  -1);   /* 좌 역방향: 방향 극성 */
    ramp(MOTOR_RIGHT, +1);   /* 우 전진 */
    ramp(MOTOR_RIGHT, -1);   /* 우 역방향 */

    motor_driver_stop_all();
    printf("[BLDC-ramp] sequence done — motors stopped (reset to re-run)\r\n");

    for (;;) {
        osDelay(1000);
    }
}
