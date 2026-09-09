/**
 * @file    microros_transport.c
 * @brief   F5b — micro-ROS UART + DMA custom transport (USART1).
 *
 * Adapted from micro_ros_stm32cubemx_utils/extra_sources/microros_transports/dma_transport.c
 * 수정 사항:
 *   - cubemx_transport_write 시그니처 const 추가 (Humble write_custom_func 호환).
 *   - 주석 한글화.
 *
 * 사전 조건 (CubeMX 설정 — F0 단계에서 완료):
 *   - USART1: 921600 8N1, TX=PA9, RX=PA10
 *   - USART1_RX DMA: Circular mode
 *   - USART1_TX DMA: Normal mode
 *
 * 전송 흐름 (2026-09-09 재작성):
 *   - write: TX 링 버퍼에 복사 후 즉시 반환(논블로킹). DMA 는 완료 IRQ 에서
 *            남은 데이터를 이어서 자동으로 다시 건다 → 바이트가 끊김 없이 나감.
 *   - read:  DMA RX ring buffer 에서 head/tail 비교, timeout 까지 polling
 *
 * 왜 바꿨나 (2026-09-09 실측):
 *   micro-XRCE 프레이밍은 전송 계층을 **최대 42 B 씩** 호출한다(실측 wl=42).
 *   /wheel_odom 은 732 B 프레임이라 한 메시지가 18 회의 개별 DMA 트랜잭션이 되고,
 *   이전 구현은 매 호출마다 완료 세마포어를 기다렸다 → 청크 사이에 태스크 스케줄링
 *   지연이 끼어 프레임 하나가 수십 ms 에 걸쳐 도착. agent 의 프레임 수신 타임아웃을
 *   넘겨 **미완성 프레임이 버려졌다.**
 *   실측 증거: 보드는 25 회/s 발행 성공(rcl rc=0, 전송 실패 카운터 0)인데
 *   agent 수신은 그 7% 뿐. 작은 메시지(1~8 청크)는 100% 도달, odom 만 탈락 —
 *   크기가 아니라 **청크 수(=전송 소요 시간)** 에 의존하는 손실이었다.
 *   링 버퍼로 바꾸면 732 B 가 한 번의 연속 DMA(2 Mbps 에서 3.7 ms)로 나간다.
 */
#include <uxr/client/transport.h>
#include <rmw_microxrcedds_c/config.h>

#include "main.h"
#include "cmsis_os.h"
#include "FreeRTOS.h"
#include "semphr.h"

#include <stdio.h>
#include <string.h>
#include <stdbool.h>

#ifdef RMW_UXRCE_TRANSPORT_CUSTOM

#define UART_DMA_BUFFER_SIZE 2048

static uint8_t s_dma_buffer[UART_DMA_BUFFER_SIZE];
static size_t  s_dma_head = 0;
static size_t  s_dma_tail = 0;


/* 2026-09-09 계측 — best-effort 스트림은 전송 실패를 rcl 로 올리지 않아
 * '발행 성공(rc=0) 인데 수신 0Hz' 가 발생한다. 어느 경로로 버려지는지 센다.
 * UART5 콘솔 미배선이라 /rover/status 로 실어 보낸다. */
volatile uint32_t g_tx_call = 0;   /* write 호출 수 */
volatile uint32_t g_tx_busy = 0;   /* gState != READY 로 즉시 버림 */
volatile uint32_t g_tx_hal  = 0;   /* HAL_UART_Transmit_DMA != HAL_OK */
volatile uint32_t g_tx_max  = 0;   /* 관측된 최대 len */
volatile uint32_t g_tx_full = 0;   /* 링 가득 차 버린 바이트 수 */
volatile uint32_t g_tx_hw   = 0;   /* 링 최대 점유 (high-water) */

/* TX 링 — 프레임을 끊김 없이 흘려보내기 위한 버퍼.
 * 50Hz × 약 1.6 kB/cycle 을 감당하려면 여유가 필요해 8 kB. */
#define TX_RING_SIZE 8192u
static uint8_t  s_tx_ring[TX_RING_SIZE];
static volatile uint32_t s_tx_head = 0;   /* 다음 쓰기 위치 */
static volatile uint32_t s_tx_tail = 0;   /* 다음 송신 위치 */
static volatile uint32_t s_tx_busy_len = 0; /* 현재 DMA 중인 길이 */

static inline uint32_t tx_used(void)
{
    const uint32_t h = s_tx_head, t = s_tx_tail;
    return (h >= t) ? (h - t) : (TX_RING_SIZE - t + h);
}

/* 링에 대기 중인 데이터가 있으면 다음 연속 구간을 DMA 로 건다.
 * 호출 조건: 인터럽트 차단 구간 또는 ISR 문맥. */
static void tx_kick(UART_HandleTypeDef *uart)
{
    if (s_tx_busy_len != 0u) return;              /* 이미 송신 중 */
    const uint32_t h = s_tx_head, t = s_tx_tail;
    if (h == t) return;                            /* 보낼 것 없음 */
    /* 링 끝을 넘지 않는 연속 구간만 한 번에 보낸다. */
    const uint32_t run = (h > t) ? (h - t) : (TX_RING_SIZE - t);
    if (HAL_UART_Transmit_DMA(uart, &s_tx_ring[t], (uint16_t)run) == HAL_OK) {
        s_tx_busy_len = run;
    } else {
        g_tx_hal++;
    }
}

static UART_HandleTypeDef *s_tx_uart = NULL;   /* ISR 에서 재기동용 */

bool cubemx_transport_open(struct uxrCustomTransport *transport)
{
    UART_HandleTypeDef *uart = (UART_HandleTypeDef *)transport->args;
    s_tx_uart = uart;
    s_tx_head = s_tx_tail = 0;
    s_tx_busy_len = 0;
    HAL_UART_Receive_DMA(uart, s_dma_buffer, UART_DMA_BUFFER_SIZE);
    return true;
}

bool cubemx_transport_close(struct uxrCustomTransport *transport)
{
    UART_HandleTypeDef *uart = (UART_HandleTypeDef *)transport->args;
    HAL_UART_DMAStop(uart);
    return true;
}

size_t cubemx_transport_write(struct uxrCustomTransport *transport,
                              const uint8_t *buf, size_t len, uint8_t *err)
{
    (void)err;
    UART_HandleTypeDef *uart = (UART_HandleTypeDef *)transport->args;
    s_tx_uart = uart;

    g_tx_call++;
    if (len > g_tx_max) g_tx_max = (uint32_t)len;
    if (len == 0u) return 0;

    /* 링에 자리가 날 때까지 짧게 대기 (프레임 중간을 잘라 버리면 agent 가
     * 그 프레임 전체를 버리므로, 버리는 것보다 잠깐 기다리는 편이 낫다). */
    int waited = 0;
    while (TX_RING_SIZE - 1u - tx_used() < (uint32_t)len) {
        if (++waited > 50) {          /* 50ms 초과 — agent 다운 등 비정상 */
            g_tx_full += (uint32_t)len;
            return 0;
        }
        osDelay(1);
    }

    /* 복사 — DMA 는 우리 링을 읽으므로 호출자 버퍼 수명과 무관해진다.
     * (이전 구현은 호출자 버퍼를 직접 DMA 소스로 썼다.) */
    uint32_t h = s_tx_head;
    for (size_t i = 0; i < len; i++) {
        s_tx_ring[h] = buf[i];
        h = (h + 1u) % TX_RING_SIZE;
    }

    __disable_irq();
    s_tx_head = h;
    const uint32_t used = tx_used();
    if (used > g_tx_hw) g_tx_hw = used;
    tx_kick(uart);
    __enable_irq();

    return len;   /* 논블로킹 — 완료를 기다리지 않는다 */
}

/* HAL UART TX complete callback — DMA2_Stream7 IRQ → HAL → 여기.
 * USART1 만 micro-ROS 용. 다른 UART 가 DMA TX 사용하면 case 추가. */
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance != USART1) return;
    /* 방금 보낸 만큼 tail 전진 후 곧바로 다음 구간을 건다 →
     * 링에 데이터가 있는 한 UART 가 쉬지 않는다(프레임 내 공백 제거). */
    s_tx_tail = (s_tx_tail + s_tx_busy_len) % TX_RING_SIZE;
    s_tx_busy_len = 0u;
    if (s_tx_uart != NULL) tx_kick(s_tx_uart);
}

size_t cubemx_transport_read(struct uxrCustomTransport *transport,
                             uint8_t *buf, size_t len, int timeout, uint8_t *err)
{
    (void)err;
    UART_HandleTypeDef *uart = (UART_HandleTypeDef *)transport->args;

    int ms_used = 0;
    do {
        /* DMA Circular: NDTR 카운터로 현재 tail 위치 산출.
         * portENTER_CRITICAL 대신 __disable_irq — DMA·UART IRQ 만 잠시 차단. */
        __disable_irq();
        s_dma_tail = UART_DMA_BUFFER_SIZE - __HAL_DMA_GET_COUNTER(uart->hdmarx);
        __enable_irq();
        ms_used++;
        osDelay(1);
    } while (s_dma_head == s_dma_tail && ms_used < timeout);

    size_t wrote = 0;
    while ((s_dma_head != s_dma_tail) && (wrote < len)) {
        buf[wrote] = s_dma_buffer[s_dma_head];
        s_dma_head = (s_dma_head + 1) % UART_DMA_BUFFER_SIZE;
        wrote++;
    }
    return wrote;
}

#endif /* RMW_UXRCE_TRANSPORT_CUSTOM */
