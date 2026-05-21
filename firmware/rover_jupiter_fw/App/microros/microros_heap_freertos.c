/**
 * @file    microros_heap_freertos.c
 * @brief   F5b — micro-ROS 가 FreeRTOS heap_4 를 그대로 쓰도록 하는 어댑터.
 *
 * 대안: micro_ros_stm32cubemx_utils/extra_sources/custom_memory_manager.c
 * 위 파일은 별도 ucHeap[configTOTAL_HEAP_SIZE] 를 또 잡아 RAM 2배 소비.
 * F405 128 KB SRAM 에선 부담스럽고, 별 이득 없음 (단일 힙 모니터링이 더 단순).
 *
 * 본 어댑터는 pvPortMallocMicroROS()/vPortFreeMicroROS() 등을 FreeRTOS heap_4
 * 의 pvPortMalloc/vPortFree 로 직접 매핑한다.
 *
 * 단점: micro-ROS 와 FreeRTOS 가 같은 heap 공유 → 한쪽 누수가 다른 쪽 영향.
 *       configTOTAL_HEAP_SIZE 모니터링으로 충분히 관찰 가능.
 */
#include <stddef.h>
#include <string.h>

#include "FreeRTOS.h"
#include "task.h"

void *pvPortMallocMicroROS(size_t xWantedSize)
{
    return pvPortMalloc(xWantedSize);
}

void vPortFreeMicroROS(void *pv)
{
    vPortFree(pv);
}

void *pvPortReallocMicroROS(void *pv, size_t xWantedSize)
{
    /* heap_4 에 realloc 없음 — malloc 후 copy. 이전 크기를 모르므로
     * 새 크기만큼 copy (truncate 가능). micro-ROS 호출자가 grow only 가정. */
    void *newmem = pvPortMalloc(xWantedSize);
    if (newmem != NULL && pv != NULL) {
        memcpy(newmem, pv, xWantedSize);
        vPortFree(pv);
    }
    return newmem;
}

void *pvPortCallocMicroROS(size_t num, size_t xWantedSize)
{
    size_t total = num * xWantedSize;
    void *mem = pvPortMalloc(total);
    if (mem) memset(mem, 0, total);
    return mem;
}

/* microros_allocators.c 의 usedMemory 추적용 — 실제 사이즈 모르므로 0.
 * 추적값은 부정확해지지만 동작에는 영향 없음. */
size_t getBlockSize(void *pv)
{
    (void)pv;
    return 0;
}
