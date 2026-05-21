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
#include "f2_motor_test.h"
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
/* F2 검증: 모터 개방루프 PWM 시퀀스 (휠 받침대 전제). */
osThreadId_t f2MotorTaskHandle;
const osThreadAttr_t f2MotorTask_attributes = {
  .name = "f2Motor",
  .stack_size = 256 * 4,
  .priority = (osPriority_t) osPriorityBelowNormal,
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
  f2MotorTaskHandle  = osThreadNew(f2_motor_test_run, NULL, &f2MotorTask_attributes);
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
/* USER CODE END Application */

