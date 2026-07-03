/**
 * @file    cli_task.h
 * @brief   UART5 시리얼 CLI — 사용자가 명령 입력으로 모터 속도 지령 (수동 테스트).
 *
 * control task 와 함께 활성 (CLI 는 target 설정, control 이 PID 구동).
 * freertos.c 에서 osThreadNew 로 생성 (평소 비활성).
 */
#ifndef APP_APP_CLI_TASK_H
#define APP_APP_CLI_TASK_H

#ifdef __cplusplus
extern "C" {
#endif

void cli_task_run(void *argument);

/** UART5 RX 인터럽트에서 호출 (stm32f4xx_it.c). RXNE/ORE 처리 + 링버퍼 push. */
void cli_uart5_rx_isr(void);

#ifdef __cplusplus
}
#endif

#endif /* APP_APP_CLI_TASK_H */
