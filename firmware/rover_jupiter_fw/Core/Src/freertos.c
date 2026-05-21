/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * File Name          : freertos.c
  * Description        : Code for freertos applications
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2026 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */

/* Includes ------------------------------------------------------------------*/
#include "FreeRTOS.h"
#include "task.h"
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>
#include "f1_sanity_task.h"
#include "f4_pid_test.h"
#include "i_encoder.h"
#include "speed_controller.h"
#include "safety_monitor.h"
#include "microros_task.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
/* USER CODE BEGIN Variables */
/* F1 검증: 페리페럴 sanity 태스크. heap·tick 정보도 함께 dump. */
osThreadId_t f1SanityTaskHandle;
const osThreadAttr_t f1SanityTask_attributes = {
  .name = "f1Sanity",
  .stack_size = 512 * 4,   /* SPI/I2C HAL + printf 여유 */
  .priority = (osPriority_t) osPriorityBelowNormal,
};
/* F4 검증: 폐루프 PID + 스톨 시퀀스 (F2 는 비활성 — 매핑/방향 검증 완료). */
osThreadId_t f4PidTaskHandle;
const osThreadAttr_t f4PidTask_attributes = {
  .name = "f4Pid",
  .stack_size = 256 * 4,
  .priority = (osPriority_t) osPriorityBelowNormal,
};
/* F3/F4 통합: 100 Hz 제어 루프 — encoder_update_velocity →
   speed_controller_update → safety_monitor_update 를 단일 task 에서 sequencing.
   다른 진단/UI 태스크보다 살짝 높은 우선순위로 dt jitter 최소화. */
osThreadId_t controlTaskHandle;
const osThreadAttr_t controlTask_attributes = {
  .name = "control",
  .stack_size = 256 * 4,   /* PID·monitor 호출 여유 */
  .priority = (osPriority_t) osPriorityAboveNormal,
};
/* F5b: micro-ROS executor + publisher. rclc·rmw 호출 깊이 큼.
 * 권장 12 KB 였으나 F405 RAM 제약 → 6 KB 로 시작. stack overflow 검출(option 2)
 * 활성이라 오버 시 hook 에서 잡힘. 부족하면 8 KB 로 상향. */
osThreadId_t microrosTaskHandle;
const osThreadAttr_t microrosTask_attributes = {
  .name = "uros",
  .stack_size = 1536 * 4,   /* 6 KB */
  .priority = (osPriority_t) osPriorityNormal,
};
/* USER CODE END Variables */
/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};

/* Private function prototypes -----------------------------------------------*/
/* USER CODE BEGIN FunctionPrototypes */
void StartF1SanityTask(void *argument);
void StartControlTask(void *argument);
/* USER CODE END FunctionPrototypes */

void StartDefaultTask(void *argument);

void MX_FREERTOS_Init(void); /* (MISRA C 2004 rule 8.1) */

/* Hook prototypes */
void vApplicationStackOverflowHook(xTaskHandle xTask, signed char *pcTaskName);

/* USER CODE BEGIN 4 */
void vApplicationStackOverflowHook(xTaskHandle xTask, signed char *pcTaskName)
{
   /* Run time stack overflow checking is performed if
   configCHECK_FOR_STACK_OVERFLOW is defined to 1 or 2. This hook function is
   called if a stack overflow is detected. */
}
/* USER CODE END 4 */

/**
  * @brief  FreeRTOS initialization
  * @param  None
  * @retval None
  */
void MX_FREERTOS_Init(void) {
  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  f1SanityTaskHandle = osThreadNew(StartF1SanityTask, NULL, &f1SanityTask_attributes);
  controlTaskHandle  = osThreadNew(StartControlTask,  NULL, &controlTask_attributes);
  /* F5c: F4 자동 시퀀스 비활성 — /cmd_vel 콜백이 speed_controller 의 target 설정.
   * 회귀 필요 시 아래 한 줄 다시 활성. */
  /* f4PidTaskHandle = osThreadNew(f4_pid_test_run, NULL, &f4PidTask_attributes); */
  microrosTaskHandle = osThreadNew(microros_task_run, NULL, &microrosTask_attributes);
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

}

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN StartDefaultTask */
  /* F0 검증: PC13 상태 LED 1Hz 토글 (defaultTask 동작 신호) */
  for(;;)
  {
    HAL_GPIO_TogglePin(LED_STATUS_GPIO_Port, LED_STATUS_Pin);
    HAL_GPIO_TogglePin(BUZZER_GPIO_Port, BUZZER_Pin);
    osDelay(500);
  }
  /* USER CODE END StartDefaultTask */
}

/* Private application code --------------------------------------------------*/
/* USER CODE BEGIN Application */
/**
 * @brief F1 검증 태스크.
 *        시작 시 모든 드라이버 init 호출 → 결과 dump.
 *        이후 1Hz 로 엔코더 카운트·ADC·IMU WHO_AM_I 라이브 출력.
 */
void StartF1SanityTask(void *argument)
{
  /* 스케줄러가 충분히 안정된 후 시작 */
  osDelay(100);
  f1_sanity_init();
  for(;;)
  {
    f1_sanity_tick();
    osDelay(1000);
  }
}

/**
 * @brief F3/F4 통합 제어 루프 — 100 Hz.
 *        순서: encoder 속도 업데이트 → PID → safety monitor.
 *        같은 dt 내에 sequencing 함으로써 PID 가 항상 최신 actual 사용.
 */
void StartControlTask(void *argument)
{
  (void)argument;
  /* f1_sanity_init() 이 encoder_init() · motor_driver_init() 마치길 대기. */
  osDelay(200);
  speed_controller_init();
  safety_monitor_init();

  uint32_t next = osKernelGetTickCount();
  const uint32_t period_ticks = 10u;  /* 10 ms = 100 Hz */
  for(;;)
  {
    encoder_update_velocity();
    speed_controller_update();
    safety_monitor_update();
    next += period_ticks;
    osDelayUntil(next);
  }
}
/* USER CODE END Application */

