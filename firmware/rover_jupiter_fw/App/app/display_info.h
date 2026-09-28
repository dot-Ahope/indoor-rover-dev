/**
 * @file display_info.h
 * @brief OLED 에 띄울 정보의 공유 상태 (2026-09-28) — 쓰는 쪽(microros_task)과 읽는 쪽(display_task)을 분리.
 *
 * Wi-Fi IP·SSID 는 보드가 모른다(무선은 Jetson 에 있음) → Jetson 노드 display_info_pub.py 가
 * micro-ROS 토픽 /rover/display_info (std_msgs/String, "IP=…;SSID=…") 로 보내고, microros_task 가 여기에 넣는다.
 * 짧은 복사만 하므로 크리티컬 섹션으로 보호한다.
 */
#ifndef DISPLAY_INFO_H
#define DISPLAY_INFO_H

#include <stdint.h>

typedef enum {
    UROS_WAITING = 0,   /* 에이전트 찾는 중(Jetson 스택 꺼짐·케이블 등) */
    UROS_CONNECTED,     /* 엔티티 생성 끝, 스핀 중 */
    UROS_ERROR          /* 초기화 실패로 idle */
} uros_state_t;

typedef struct {
    char ip[20];            /* "192.168.0.101" — 모르면 빈 문자열 */
    char ssid[24];
    uint32_t info_rx_ms;    /* 마지막 /rover/display_info 수신 시각(HAL_GetTick), 0 = 받은 적 없음 */
    uros_state_t uros;
} display_info_t;

/** "IP=…;SSID=…" 형식 문자열을 해석해 저장(모르는 키는 무시). now_ms 를 수신 시각으로. */
void display_info_set_text(const char *s, uint32_t len, uint32_t now_ms);
void display_info_set_uros(uros_state_t st);
/** 현재 상태 복사본. */
void display_info_get(display_info_t *out);

#endif /* DISPLAY_INFO_H */
