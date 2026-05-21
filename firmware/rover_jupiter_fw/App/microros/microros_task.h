/**
 * @file    microros_task.h
 * @brief   F5b — micro-ROS FreeRTOS task. Node + executor + heartbeat publisher.
 *
 * UART1 + DMA serial transport (CH340N → Jetson 또는 PC).
 * Agent: `micro_ros_agent serial --dev /dev/ttyACM0 -b 921600` (예시)
 *
 * F5b 검증용 publisher: `/rover/f5b_heartbeat` (std_msgs/Int32, 1Hz)
 * F5c 에서 /cmd_vel subscriber 추가 → speed_controller_set_target 연결.
 */
#ifndef APP_MICROROS_MICROROS_TASK_H
#define APP_MICROROS_MICROROS_TASK_H

#ifdef __cplusplus
extern "C" {
#endif

/** FreeRTOS task entry. RTOS 시작 후 호출됨. */
void microros_task_run(void *arg);

#ifdef __cplusplus
}
#endif

#endif
