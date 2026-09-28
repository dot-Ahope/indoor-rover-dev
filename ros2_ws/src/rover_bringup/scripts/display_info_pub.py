#!/usr/bin/env python3
# 보드 OLED 표시용 정보 발행 (2026-09-28) — Jetson 의 Wi-Fi IP·SSID 를 보드로 보낸다.
# 왜: 무선은 Jetson 에 있어 보드(F405)는 IP 를 모른다. 보드 OLED(J8, SSD1306 128×32)가 줄 1·2 에 표시한다.
# 형식: std_msgs/String "IP=192.168.0.101;SSID=WEB_DEV_5G" 를 /rover/display_info 로 3 s 마다(펌웨어는 15 s 넘게 안 오면 '?' 표시).
# IP = 기본 경로가 쓰는 출발 주소(`ip -4 route get 1.1.1.1` 의 src) — 인터페이스가 바뀌어도(WEB_DEV ↔ ALOPS) 실제로 쓰는 주소를 보인다.
# SSID = 그 경로 장치의 연결 이름(nmcli). 유선이면 장치 이름을 대신 보낸다.
import subprocess

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=2).stdout
    except Exception:
        return ''


def current_ip_ssid():
    out = _run(['ip', '-4', 'route', 'get', '1.1.1.1']).split()
    ip = out[out.index('src') + 1] if 'src' in out else ''
    dev = out[out.index('dev') + 1] if 'dev' in out else ''
    ssid = ''
    for line in _run(['nmcli', '-t', '-f', 'DEVICE,TYPE,CONNECTION', 'device']).splitlines():
        f = line.split(':')
        if len(f) >= 3 and f[0] == dev:
            ssid = f[2] if f[1] == 'wifi' else dev
    return ip, ssid


class DisplayInfoPub(Node):
    def __init__(self):
        super().__init__('display_info_pub')
        self.pub = self.create_publisher(String, 'rover/display_info', 1)
        self.create_timer(3.0, self.tick)
        self.tick()

    def tick(self):
        ip, ssid = current_ip_ssid()
        m = String(); m.data = 'IP=%s;SSID=%s' % (ip, ssid[:23])   # 펌웨어 버퍼: IP 19·SSID 23 글자
        self.pub.publish(m)


def main():
    rclpy.init()
    rclpy.spin(DisplayInfoPub())


if __name__ == '__main__':
    main()
