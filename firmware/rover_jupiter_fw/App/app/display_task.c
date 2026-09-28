/**
 * @file display_task.c
 * @brief display_task.h 구현.
 */
#include "display_task.h"

#include <stdio.h>
#include <string.h>

#include "battery_adc.h"
#include "cmsis_os.h"
#include "display_info.h"
#include "i2c.h"
#include "safety_monitor.h"
#include "ssd1306_driver.h"

#define OLED_ADDR          0x3C     /* 0.91" 128×32 SSD1306 모듈 기본 주소 */
#define OLED_HEIGHT        32
#define REFRESH_MS         1000u
#define RETRY_MS           5000u
#define INFO_STALE_MS      15000u   /* Jetson 이 3 s 마다 보냄 → 5 번 놓치면 오래된 값 표시 */

/* nano-printf 는 float 미지원 → 전압을 정수 두 자리로 */
static void fmt_volts(char *dst, size_t n, float v)
{
    const int cv = (int)(v * 100.0f + 0.5f);
    snprintf(dst, n, "%d.%02dV", cv / 100, cv % 100);
}

static void draw(void)
{
    display_info_t in;
    display_info_get(&in);
    const uint32_t now = HAL_GetTick();
    char l[4][48];   /* 화면은 21 글자 — 넘는 부분은 ssd1306_text 가 자른다(버퍼를 넉넉히 둬 snprintf 잘림 경고를 없앰) */

    const bool have = in.info_rx_ms != 0;
    const bool stale = have && (now - in.info_rx_ms > INFO_STALE_MS);
    if (have && in.ip[0]) snprintf(l[0], sizeof(l[0]), "IP %s%s", in.ip, stale ? "?" : "");
    else snprintf(l[0], sizeof(l[0]), "IP (no Jetson info)");
    snprintf(l[1], sizeof(l[1]), "%s", (have && in.ssid[0]) ? in.ssid : "-");

    float v = 0.0f;
    char vs[16];
    if (battery_adc_read(&v)) fmt_volts(vs, sizeof(vs), v); else snprintf(vs, sizeof(vs), "--.--V");
    const char *ros = (in.uros == UROS_CONNECTED) ? "OK" : (in.uros == UROS_ERROR) ? "ERR" : "WAIT";
    snprintf(l[2], sizeof(l[2]), "BAT %s ROS %s", vs, ros);

    const char *st;
    if (safety_monitor_is_latched())           st = "LATCH";
    else if (safety_monitor_has_fault())       st = "STALL";
    else if (safety_monitor_cmdvel_timeout())  st = "CMD-TO";
    else                                       st = "RUN";
    const uint32_t s = now / 1000u;
    snprintf(l[3], sizeof(l[3]), "%-6s UP %02lu:%02lu:%02lu", st, (unsigned long)(s / 3600u), (unsigned long)(s / 60u % 60u), (unsigned long)(s % 60u));

    ssd1306_clear();
    for (uint8_t i = 0; i < 4; i++) ssd1306_text(i, 0, l[i]);
    (void)ssd1306_flush();
}

void display_task_run(void *argument)
{
    (void)argument;
    osDelay(500);   /* f1_sanity 의 부팅 I2C 스캔(I2C2 포함)과 겹치지 않게 */
    battery_adc_init();
    uint32_t last_try = 0;
    for (;;) {
        if (!ssd1306_ok()) {
            const uint32_t now = HAL_GetTick();
            if (last_try == 0 || now - last_try >= RETRY_MS) {
                last_try = now;
                if (ssd1306_init(&hi2c2, OLED_ADDR, OLED_HEIGHT)) printf("[OLED] SSD1306 128x%d @0x%02X OK\r\n", OLED_HEIGHT, OLED_ADDR);
            }
        }
        if (ssd1306_ok()) draw();
        osDelay(REFRESH_MS);
    }
}
