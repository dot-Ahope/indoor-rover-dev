/**
 * @file display_task.h
 * @brief OLED 상태 표시 태스크 (2026-09-28) — 1 Hz 로 4 줄 갱신.
 *
 *   줄 1  IP 192.168.0.101        (Jetson 이 보낸 Wi-Fi IP. 15 s 넘게 안 오면 끝에 '?')
 *   줄 2  WEB_DEV_5G              (SSID)
 *   줄 3  BAT 12.05V  ROS OK      (전압 = 보드 ADC 직접, ROS = micro-ROS 상태 WAIT/OK/ERR)
 *   줄 4  RUN   UP 01:23:45       (안전 상태 RUN/CMD-TO/STALL/LATCH, 부팅 뒤 시간)
 * 모듈이 없거나 응답이 없으면 5 s 마다 다시 초기화를 시도하고, 그동안 아무것도 막지 않는다.
 */
#ifndef DISPLAY_TASK_H
#define DISPLAY_TASK_H

void display_task_run(void *argument);

#endif /* DISPLAY_TASK_H */
