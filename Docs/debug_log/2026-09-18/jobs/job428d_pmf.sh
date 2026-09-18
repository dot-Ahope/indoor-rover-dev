#!/bin/bash
echo "-- station dump (AP 항목)"; iw dev wlP1p1s0 station dump 2>&1 | grep -aE 'Station|MFP|authorized|authenticated|associated|connected time|inactive time|signal:|tx retries|tx failed|beacon loss|rx drop' | head -14
echo "-- wpa_cli status (권한 있으면)"; wpa_cli -i wlP1p1s0 status 2>&1 | grep -avE 'passphrase|psk' | head -20
echo "-- wpa_supplicant 설정 파일/소켓 권한"; ls -la /run/wpa_supplicant/ 2>&1 | head -4
echo "-- NM 프로파일 WEB_DEV_5G 보안(비밀 제외)"; nmcli -f 802-11-wireless-security.key-mgmt,802-11-wireless-security.pmf,802-11-wireless.powersave,connection.autoconnect-priority con show WEB_DEV_5G 2>&1
echo "-- 드라이버 모듈 파라미터 목록"; ls /sys/module/rtl88x2ce/parameters/ 2>&1 | tr '\n' ' ' | cut -c1-600; echo
for p in rtw_power_mgnt rtw_ips_mode rtw_lps_level rtw_wmm_enable rtw_ht_enable rtw_vht_enable rtw_country_code rtw_channel_plan rtw_dfs_region_domain rtw_80211d; do [ -f /sys/module/rtl88x2ce/parameters/$p ] && echo "   $p=$(cat /sys/module/rtl88x2ce/parameters/$p)"; done
modinfo rtl88x2ce 2>/dev/null | grep -aE '^(version|vermagic|description)' | head -3
