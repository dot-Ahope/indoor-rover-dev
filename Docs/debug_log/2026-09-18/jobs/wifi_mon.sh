#!/bin/bash
# Wi-Fi 계측 (2026-09-18 A안: WEB_DEV_5G 가 끊고 재인증을 거부하는 원인 — DFS(160 MHz) vs PMF/드라이버).
# 설정은 바꾸지 않는다: 읽기·스캔·wpa_supplicant 로그 수준(DEBUG) 유지만. systemd wifi-mon.service 로 root 실행.
#   /var/log/wifi_mon/mon.log        15 s 링크 줄(LINK), 60 s AP 비콘 줄(BEACON), 사건 줄(EVENT)
#   /var/log/wifi_mon/event_*.txt    BSSID 변화·끊김 순간의 스냅샷(전체 스캔, wpa 상태, 직전 debug 400 줄)
#   /var/log/wifi_mon/wpa_debug.log  wpa_supplicant DEBUG 줄(rsyslog 25-wifi-mon.conf 가 기록)
# 되돌리기: systemctl disable --now wifi-mon; rm /etc/rsyslog.d/25-wifi-mon.conf; systemctl restart rsyslog; wpa_cli log_level INFO
IF=wlP1p1s0
AP=b0:38:6c:37:1b:4c          # WEB_DEV_5G (ipTIME AX3000R, 5 GHz ch36 160 MHz)
APFREQ=5180
D=/var/log/wifi_mon; M=$D/mon.log
mkdir -p $D

log() { echo "$(date '+%F %T') $*" >> $M; }

rot() {   # 크기 제한 회전: rot 파일 최대바이트 [hup]
  local f=$1 max=$2
  if [ -f "$f" ] && [ "$(stat -c %s "$f")" -gt "$max" ]; then
    mv -f "$f" "$f.1"; [ "$3" = hup ] && pkill -HUP rsyslogd
    log "ROTATE $f"
  fi
}

scan_ap() {   # scan_ap <freq|all> → AP 블록을 한 줄로
  local out rc   # 09-18: 첫 스캔이 다른 스캔과 겹쳐 98 s 막힘 → timeout(단일 10 s, 전체 20 s)
  if [ "$1" = all ]; then out=$(timeout 20 iw dev $IF scan 2>&1); else out=$(timeout 10 iw dev $IF scan freq "$1" 2>&1); fi
  rc=$?
  if [ $rc -ne 0 ]; then sleep 2; if [ "$1" = all ]; then out=$(timeout 20 iw dev $IF scan 2>&1); else out=$(timeout 10 iw dev $IF scan freq "$1" 2>&1); fi; rc=$?; fi
  if [ $rc -ne 0 ]; then echo "scan_err=$(echo "$out" | tail -1 | tr ' ' '_')"; return; fi
  echo "$out" | awk -v ap="$AP" '
    /^BSS / { p = (index($0, ap) > 0); next }
    p && /signal:/ { sig = $2 }
    p && /freq:/ { fr = $2 }
    p && /secondary channel offset/ { ht2 = $NF }
    p && /\* channel width:/ { vw = $4 }
    p && /center freq segment 1/ { s1 = $NF }
    p && /center freq segment 2/ { s2 = $NF }
    p && /[Cc]hannel [Ss]witch/ && !/Extended/ { csa = 1 }
    p && /Quiet/ { q = 1 }
    END { if (fr == "") print "ap=absent"; else printf "ap_freq=%s ap_sig=%s vht_w=%s seg1=%s seg2=%s ht2=%s csa=%d quiet=%d\n", fr, sig, vw, s1, s2, ht2, csa, q }'
}

snapshot() {   # 사건 스냅샷
  local f=$D/event_$(date +%Y%m%d_%H%M%S).txt
  {
    echo "### $(date '+%F %T.%3N') $*"
    echo "--- iw link"; iw dev $IF link
    echo "--- wpa_cli status"; wpa_cli -i $IF status 2>&1 | grep -avE 'passphrase|psk|pmk'
    echo "--- ip"; ip -4 -o addr show $IF
    echo "--- nmcli dev"; nmcli -f GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS dev show $IF 2>&1
    echo "--- 전체 스캔(AP 블록)"; timeout 20 iw dev $IF scan 2>&1 | awk -v ap="$AP" '/^BSS /{p=(index($0,ap)>0)} p' | head -80
    echo "--- wpa_debug.log 직전 400 줄"; tail -n 400 $D/wpa_debug.log 2>/dev/null | grep -avE 'passphrase|psk=|PMK -|PTK -'
    echo "--- syslog wpa_supplicant/NM 직전 80 줄"; grep -aE 'wpa_supplicant|NetworkManager.*wlP1p1s0' /var/log/syslog | tail -n 80
  } > "$f" 2>&1
  log "SNAPSHOT $f"
}

log "START pid $$"
last_bssid="__init__"; n=0
while true; do
  # wpa_supplicant 로그 수준 DEBUG 유지(재시작·재부팅 뒤엔 INFO 로 돌아간다)
  if ! wpa_cli log_level 2>/dev/null | grep -q 'Current level: DEBUG'; then
    wpa_cli log_level DEBUG >/dev/null 2>&1 && log "LOGLEVEL DEBUG"
  fi
  L=$(iw dev $IF link 2>/dev/null)
  bssid=$(echo "$L" | awk '/Connected to/{print $3}')
  ssid=$(echo "$L" | awk -F': ' '/SSID:/{print $2}')
  freq=$(echo "$L" | awk '/freq:/{print $2}')
  sig=$(echo "$L" | awk '/signal:/{print $2}')
  rx=$(echo "$L" | awk -F': ' '/rx bitrate/{print $2}' | tr ' ' '_')
  tx=$(echo "$L" | awk -F': ' '/tx bitrate/{print $2}' | tr ' ' '_')
  ip4=$(ip -4 -o addr show $IF | awk '{print $4}')
  st=$(wpa_cli -i $IF status 2>/dev/null | awk -F= '/^(wpa_state|pmf|key_mgmt)=/{printf "%s=%s ", $1, $2}')
  log "LINK bssid=${bssid:-none} ssid=${ssid:-} freq=${freq:-} sig=${sig:-} rx=${rx:-} tx=${tx:-} ip=${ip4:-} $st"

  if [ "$last_bssid" != "__init__" ] && [ "$bssid" != "$last_bssid" ]; then
    log "EVENT bssid ${last_bssid:-none} -> ${bssid:-none}"
    snapshot "bssid ${last_bssid:-none} -> ${bssid:-none}"
  fi
  if [ "$bssid" = "$AP" ] && [ $((n % 4)) -eq 0 ]; then
    log "BEACON $(scan_ap $APFREQ)"               # 60 s 마다, 연결 채널 1 개(≈140 ms)
  elif [ "$bssid" != "$AP" ] && [ $((n % 40)) -eq 0 ]; then
    log "BEACON_ALL $(scan_ap all)"               # WEB_DEV 가 아닐 때 10 분마다 전체 스캔
  fi

  last_bssid=$bssid; n=$((n + 1))
  if [ $((n % 240)) -eq 0 ]; then rot $M 50000000; rot $D/wpa_debug.log 300000000 hup; fi
  sleep 15
done
