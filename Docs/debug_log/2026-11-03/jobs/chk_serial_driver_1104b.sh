#!/bin/bash
# 11-04 §11 보충: 커널 패키지가 ch341.ko 를 갖고 있나 · 시계 · 설치 흔적(읽기만, sudo 없음, 로버 안 움직임)
echo "== 시각 · 부팅"; date '+%F %T %Z'; uptime -p; timedatectl 2>/dev/null | grep -E 'synchronized|RTC time'
echo "== 커널 패키지가 가진 usb/serial 모듈"
P=$(dpkg -S /lib/modules/$(uname -r)/kernel/drivers/usb/serial/cp210x.ko 2>/dev/null | cut -d: -f1); echo "cp210x 소유 패키지: ${P:-없음}"
[ -n "$P" ] && dpkg -L $P | grep -E 'usb/serial/' | sed 's#.*/##' | tr '\n' ' '; echo
echo "== usb/serial 폴더 파일 시각"; ls -l --time-style=+%F_%T /lib/modules/$(uname -r)/kernel/drivers/usb/serial/ | head -20
echo "== 커널 패키지 설치 시각"; [ -n "$P" ] && grep -E " (install|upgrade) $P" /var/log/dpkg.log* 2>/dev/null | tail -3
echo "== 홈의 드라이버 소스 흔적"; ls -d ~/*ch34* ~/*CH34* ~/Downloads/*ch34* ~/Downloads/*CH34* 2>/dev/null || echo "(없음)"
