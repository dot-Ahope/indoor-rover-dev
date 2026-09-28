/**
 * @file display_info.c
 * @brief display_info.h 구현.
 */
#include "display_info.h"

#include <string.h>
#include "cmsis_os.h"

static display_info_t s_info;   /* 0 초기화: ip·ssid 빈 문자열, 수신 없음, UROS_WAITING */

/* s[0..len) 에서 "KEY=" 뒤 값을 ';' 또는 끝까지 dst 로(최대 cap−1). 없으면 dst 그대로. */
static void take(const char *s, uint32_t len, const char *key, char *dst, uint32_t cap)
{
    const uint32_t kl = (uint32_t)strlen(key);
    for (uint32_t i = 0; i + kl <= len; i++) {
        if ((i == 0 || s[i - 1] == ';') && memcmp(&s[i], key, kl) == 0) {
            uint32_t j = i + kl, n = 0;
            while (j < len && s[j] != ';' && s[j] != '\0' && n + 1 < cap) dst[n++] = s[j++];
            dst[n] = '\0';
            return;
        }
    }
}

void display_info_set_text(const char *s, uint32_t len, uint32_t now_ms)
{
    char ip[sizeof(s_info.ip)], ssid[sizeof(s_info.ssid)];
    ip[0] = '\0'; ssid[0] = '\0';
    take(s, len, "IP=", ip, sizeof(ip));
    take(s, len, "SSID=", ssid, sizeof(ssid));
    taskENTER_CRITICAL();
    memcpy(s_info.ip, ip, sizeof(ip));
    memcpy(s_info.ssid, ssid, sizeof(ssid));
    s_info.info_rx_ms = (now_ms == 0) ? 1 : now_ms;
    taskEXIT_CRITICAL();
}

void display_info_set_uros(uros_state_t st)
{
    taskENTER_CRITICAL();
    s_info.uros = st;
    taskEXIT_CRITICAL();
}

void display_info_get(display_info_t *out)
{
    taskENTER_CRITICAL();
    *out = s_info;
    taskEXIT_CRITICAL();
}
