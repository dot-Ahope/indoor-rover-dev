#!/bin/bash
# A안 설치 (2026-09-18, 사용자 승인): wifi-mon 서비스 + rsyslog 규칙. 네트워크 설정은 바꾸지 않는다. SPW 환경변수로 sudo.
S() { echo "$SPW" | sudo -S -p '' "$@"; }
set -e
S true
S install -d -o syslog -g adm -m 2750 /var/log/wifi_mon
S install -o root -g root -m 0755 /tmp/wifi_mon.sh /usr/local/sbin/wifi_mon.sh
cat > /tmp/25-wifi-mon.conf <<'CONF'
# 2026-09-18 Wi-Fi 계측(A안): wpa_supplicant DEBUG(severity 7) 줄만 별도 파일로 보내고 syslog 에는 넣지 않는다.
# INFO 이상(CTRL-EVENT-* 등)은 지금처럼 /var/log/syslog 에 남는다. 되돌리기: 이 파일 삭제 후 systemctl restart rsyslog
if ($programname == "wpa_supplicant" and $syslogseverity == 7) then {
    action(type="omfile" file="/var/log/wifi_mon/wpa_debug.log")
    stop
}
CONF
S install -o root -g root -m 0644 /tmp/25-wifi-mon.conf /etc/rsyslog.d/25-wifi-mon.conf
cat > /tmp/wifi-mon.service <<'UNIT'
[Unit]
Description=Wi-Fi monitor (2026-09-18 plan A: WEB_DEV_5G disconnect cause, read-only)
After=wpa_supplicant.service NetworkManager.service rsyslog.service

[Service]
Type=simple
ExecStart=/usr/local/sbin/wifi_mon.sh
Restart=always
RestartSec=10
Nice=10

[Install]
WantedBy=multi-user.target
UNIT
S install -o root -g root -m 0644 /tmp/wifi-mon.service /etc/systemd/system/wifi-mon.service
echo "== rsyslog 설정 검사"; S rsyslogd -N1 2>&1 | tail -3
S systemctl restart rsyslog
S systemctl daemon-reload
S systemctl enable --now wifi-mon.service 2>&1 | tail -2
set +e
sleep 75
echo "== 상태"; systemctl is-active wifi-mon rsyslog | tr '\n' ' '; systemctl is-enabled wifi-mon; echo
echo "== wpa 로그 수준: $(S wpa_cli log_level 2>&1 | awk -F': ' '/Current level/{print $2}')"
echo "== mon.log"; S tail -n 12 /var/log/wifi_mon/mon.log | cut -c1-230
echo "== wpa_debug.log: $(S wc -l < /var/log/wifi_mon/wpa_debug.log 2>/dev/null) 줄"; S tail -n 3 /var/log/wifi_mon/wpa_debug.log 2>/dev/null | cut -c1-150
echo "== syslog 에 DEBUG 줄이 새지 않는지(최근 2 분 wpa_supplicant 줄)"; grep -a 'wpa_supplicant' /var/log/syslog | tail -n 5 | cut -c1-150
ls -la /var/log/wifi_mon/
