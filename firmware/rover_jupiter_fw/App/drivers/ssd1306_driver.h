/**
 * @file ssd1306_driver.h
 * @brief SSD1306 OLED 드라이버 (I2C, 128×32 기본) — 텍스트 전용 (2026-09-28).
 *
 * 보드: ALOPS Jupiter R1.4 J8 "OLED Display" 헤더 (1 SDA, 2 SCL, 3 5V, 4 GND) → I2C2 (PB10 SCL / PB11 SDA).
 * 모듈: 0.91" 128×32 SSD1306 (사용자 확인 2026-09-28). 높이 64 모듈도 init 인자로 지원.
 * 글꼴: 5×7 ASCII(0x20~0x7E), 셀 6×8 → 128×32 에서 21 글자 × 4 줄.
 * 전송: HAL 블로킹 I2C. 512 B 프레임 + 제어 바이트 ≈ 50 ms @100 kHz — 낮은 우선순위 태스크에서만 호출할 것.
 *
 * Driver 계층 — HAL 핸들(I2C_HandleTypeDef)만 알고, 무엇을 표시할지는 App(display_task)이 정한다.
 */
#ifndef SSD1306_DRIVER_H
#define SSD1306_DRIVER_H

#include <stdbool.h>
#include <stdint.h>
#include "i2c.h"

#define SSD1306_WIDTH        128
#define SSD1306_MAX_HEIGHT    64
#define SSD1306_COLS         (SSD1306_WIDTH / 6)   /* 21 글자 */

/** 초기화. addr7 = 7-bit 주소(보통 0x3C), height = 32 또는 64. 장치가 응답하지 않으면 false. */
bool ssd1306_init(I2C_HandleTypeDef *hi2c, uint8_t addr7, uint8_t height);
/** 장치 응답 여부(초기화 성공 뒤 전송 실패가 나면 false 로 바뀜). */
bool ssd1306_ok(void);
/** 프레임 버퍼 지우기(전송은 flush). */
void ssd1306_clear(void);
/** line(0~height/8−1) 의 col(0~20) 글자 칸부터 문자열을 쓴다. 넘치는 글자는 잘린다. 표시 못 하는 문자는 '?'. */
void ssd1306_text(uint8_t line, uint8_t col, const char *s);
/** 프레임 버퍼를 화면으로 전송. 실패하면 false. */
bool ssd1306_flush(void);

#endif /* SSD1306_DRIVER_H */
