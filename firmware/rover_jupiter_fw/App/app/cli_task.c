/**
 * @file    cli_task.c
 * @brief   UART5 시리얼 CLI — 명령 입력으로 모터 속도 수동 제어 (테스트용).
 *
 * 명령 (개행으로 실행):
 *   r <mm/s>   우측 목표속도 (예: r 200,  r -150)
 *   l <mm/s>   좌측 목표속도
 *   b <mm/s>   양쪽
 *   s          정지 (양쪽 0)
 *   c          fault 해제 (스톨 latch clear)
 *   ? / h      도움말
 *
 * 속도 목표는 speed_controller 로 전달 → control task 의 PID 가 구동.
 * cmd_vel watchdog 은 agent 미접속 시 비활성이라, 지령은 정지 명령 전까지 유지됨.
 *
 * 수신: UART5 RXNE 인터럽트 → 링버퍼. (F4 UART 는 RX FIFO 없어 폴링 시
 * 붙여넣기 등 연속 바이트가 overrun 으로 유실됨 → 인터럽트로 매 바이트 즉시 포착.)
 * TX(printf, HAL_UART_Transmit) 와 RX IT 는 독립 경로라 충돌 없음.
 */
#include "cli_task.h"

#include <stdio.h>
#include <stdlib.h>
#include "cmsis_os.h"

#include "main.h"
#include "usart.h"
#include "speed_controller.h"
#include "safety_monitor.h"
#include "i_encoder.h"       /* FG 카운트 읽기·리셋 (기어비 캘리브레이션용) */

#define CLI_LINE_MAX  32

/* RX 링버퍼 (크기는 2의 거듭제곱). ISR push / task pop. */
#define RX_BUF_SZ     64u
static volatile char     s_rx[RX_BUF_SZ];
static volatile uint16_t s_rx_head = 0;   /* ISR 기록 */
static volatile uint16_t s_rx_tail = 0;   /* task 소비 */

/* UART5 RX 인터럽트 처리 — DR 즉시 읽어 링버퍼에. (stm32f4xx_it.c 에서 호출) */
void cli_uart5_rx_isr(void)
{
    /* overrun 먼저 정리 (RXNEIE 시 ORE 도 같은 인터럽트 유발) */
    if (__HAL_UART_GET_FLAG(&huart5, UART_FLAG_ORE)) {
        __HAL_UART_CLEAR_OREFLAG(&huart5);
    }
    if (__HAL_UART_GET_FLAG(&huart5, UART_FLAG_RXNE)) {
        const char c = (char)(huart5.Instance->DR & 0xFFu);   /* 읽으면 RXNE clear */
        const uint16_t nh = (uint16_t)((s_rx_head + 1u) & (RX_BUF_SZ - 1u));
        if (nh != s_rx_tail) {              /* 가득 차면 drop */
            s_rx[s_rx_head] = c;
            s_rx_head = nh;
        }
    }
}

static int rx_pop(char *c)
{
    if (s_rx_tail == s_rx_head) return 0;
    *c = s_rx[s_rx_tail];
    s_rx_tail = (uint16_t)((s_rx_tail + 1u) & (RX_BUF_SZ - 1u));
    return 1;
}

static void print_help(void)
{
    printf("\r\n[cli] 명령: r/l/b <mm/s>, s(정지), c(fault해제), e(FG카운트), z(카운트리셋), ?(도움말)\r\n");
    printf("[cli] 예: 'r 200'  'r -150'  'b 100'  's'\r\n");
    printf("[cli] 기어비 캘리: z(리셋) → 휠 N턴 손으로 회전 → e(카운트). count/N = FG펄스/회전\r\n");
}

/* 한 줄 파싱·실행. */
static void exec_line(char *line)
{
    /* 앞 공백 skip */
    while (*line == ' ' || *line == '\t') line++;
    const char cmd = *line;
    const int  mmps = atoi(line + 1);          /* 뒤 정수 (없으면 0) */
    const float mps = (float)mmps / 1000.0f;

    switch (cmd) {
        case 'r': case 'R':
            speed_controller_set_target(MOTOR_RIGHT, mps);
            printf("[cli] R tgt = %+d mm/s\r\n", mmps);
            break;
        case 'l': case 'L':
            speed_controller_set_target(MOTOR_LEFT, mps);
            printf("[cli] L tgt = %+d mm/s\r\n", mmps);
            break;
        case 'b': case 'B':
            speed_controller_set_target(MOTOR_LEFT,  mps);
            speed_controller_set_target(MOTOR_RIGHT, mps);
            printf("[cli] BOTH tgt = %+d mm/s\r\n", mmps);
            break;
        case 's': case 'S':
            speed_controller_set_target(MOTOR_LEFT,  0.0f);
            speed_controller_set_target(MOTOR_RIGHT, 0.0f);
            printf("[cli] STOP\r\n");
            break;
        case 'c': case 'C':
            safety_monitor_clear();
            printf("[cli] fault cleared\r\n");
            break;
        case 'e': case 'E':
            /* FG 누적 카운트 출력 — 기어비 캘리브레이션용.
             * 휠 N턴 돌린 뒤 count/N 이 FG_PULSES_PER_REV(현재 336) 확인값. */
            printf("[cli] FG count  L=%ld  R=%ld\r\n",
                   (long)encoder_read_count(ENC_LEFT),
                   (long)encoder_read_count(ENC_RIGHT));
            break;
        case 'z': case 'Z':
            encoder_reset(ENC_LEFT);
            encoder_reset(ENC_RIGHT);
            printf("[cli] FG count reset (L=0 R=0)\r\n");
            break;
        case '?': case 'h': case 'H':
            print_help();
            break;
        case '\0':
            break;                             /* 빈 줄 무시 */
        default:
            printf("[cli] ? unknown '%c' — '?' 로 도움말\r\n", cmd);
            break;
    }
}

void cli_task_run(void *argument)
{
    (void)argument;

    static char line[CLI_LINE_MAX];
    uint32_t idx = 0;

    osDelay(500);   /* 부팅 로그 이후 */

    /* UART5 RX 인터럽트 활성 (ISR 은 FreeRTOS API 미사용 → 우선순위 자유). */
    __HAL_UART_ENABLE_IT(&huart5, UART_IT_RXNE);
    HAL_NVIC_SetPriority(UART5_IRQn, 6, 0);
    HAL_NVIC_EnableIRQ(UART5_IRQn);

    printf("\r\n[cli] 시리얼 모터 제어 준비 (우측만 장착).\r\n");
    print_help();

    for (;;) {
        char c;
        /* 링버퍼(ISR 채움) 소비 */
        while (rx_pop(&c)) {
            if (c == '\r' || c == '\n') {
                if (idx > 0) {
                    line[idx] = '\0';
                    printf("\r\n");            /* 입력 개행 에코 */
                    exec_line(line);
                    idx = 0;
                }
            } else if (c == 0x08 || c == 0x7F) {   /* backspace/DEL */
                if (idx > 0) { idx--; printf("\b \b"); }
            } else if (idx < (CLI_LINE_MAX - 1)) {
                line[idx++] = c;
                printf("%c", c);               /* 에코 */
            }
        }
        osDelay(10);   /* 100Hz 폴링 */
    }
}
