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
 * 전송 흐름:
 *   - write: HAL_UART_Transmit_DMA → 완료 대기 (busy-wait osDelay(1))
 *   - read:  DMA RX ring buffer 에서 head/tail 비교, timeout 까지 polling
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

/* F6+ 최적화: DMA TX 완료를 polling 대신 binary semaphore 로 대기.
 * HAL_UART_TxCpltCallback (DMA2_Stream7 IRQ, priority 6 = FreeRTOS 안전) 에서 give. */
static SemaphoreHandle_t s_tx_done = NULL;

bool cubemx_transport_open(struct uxrCustomTransport *transport)
{
    UART_HandleTypeDef *uart = (UART_HandleTypeDef *)transport->args;
    if (s_tx_done == NULL) {
        s_tx_done = xSemaphoreCreateBinary();
    }
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

    if (uart->gState != HAL_UART_STATE_READY) return 0;

    /* HAL_UART_Transmit_DMA 가 첫 인자 uint8_t* 라서 const 제거 캐스트.
     * DMA 컨트롤러는 메모리를 읽기만 함 → 안전. */
    HAL_StatusTypeDef ret = HAL_UART_Transmit_DMA(uart, (uint8_t *)buf, len);
    if (ret != HAL_OK) return 0;

    /* F6+ 최적화: TX complete IRQ semaphore 대기 (polling osDelay(1) 제거).
     * Timeout 100ms — 비정상 lock-up 방지 safety. */
    if (s_tx_done != NULL) {
        if (xSemaphoreTake(s_tx_done, pdMS_TO_TICKS(100)) != pdTRUE) {
            return 0;   /* TX timeout — agent down 등 */
        }
    } else {
        /* Fallback: semaphore 없으면 옛 polling. (init 전 호출 등) */
        while (uart->gState != HAL_UART_STATE_READY) osDelay(1);
    }
    return len;
}

/* HAL UART TX complete callback — DMA2_Stream7 IRQ → HAL → 여기.
 * USART1 만 micro-ROS 용. 다른 UART 가 DMA TX 사용하면 case 추가. */
void HAL_UART_TxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART1 && s_tx_done != NULL) {
        BaseType_t hpw = pdFALSE;
        xSemaphoreGiveFromISR(s_tx_done, &hpw);
        portYIELD_FROM_ISR(hpw);
    }
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
