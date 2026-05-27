#!/usr/bin/env python3
"""rover_teleop_kb — 키보드 teleop, 조이스틱처럼 hold-to-move 동작.

동작 원리
---------
- publisher 를 한 번만 만들어 20Hz 로 cmd_vel 지속 발행 (`ros2 topic pub
  --once` 의 1초 startup 비용을 1회로 줄임).
- 키 입력시마다 active 벨로시티 갱신 + auto-stop 타이머 reset.
- AUTO_STOP_S 동안 새 입력 없으면 zero 발행 (키를 놨다고 간주).
- 키를 누르고 있으면 OS 키 리피트가 AUTO_STOP_S 내에 계속 입력을 보내므로
  hold-to-move 처럼 느껴짐.

키 매핑
-------
  W / S       : 전진 / 후진 (tap, auto-stop)
  A / D       : 좌회전 / 우회전 (tap, auto-stop)
  Q / E       : 전진 + 좌 / 전진 + 우 (대각)
  Z / C       : 후진 + 좌 / 후진 + 우
  G           : cruise 토글 — 전진 latch (auto-stop 무시, 다시 G 또는
                SPACE / W·S·Q·E·Z·C 로 해제). cruise 중에도 A/D 로 조향 가능.
  SPACE       : 즉시 정지 (cruise 도 해제)
  ↑ / ↓       : 선속도 ±0.05 m/s
  ← / →       : 각속도 ±0.20 rad/s
  o           : 속도 기본값 reset
  ESC         : 종료 (zero 발행 후 exit)
  Ctrl+C      : 강제 종료

OS 키 리피트 안내
----------------
- Linux 기본: 첫 리피트 지연 ~500ms, 이후 ~30Hz.
- AUTO_STOP_S 가 OS 첫 리피트 지연보다 짧으면 hold 직후 잠시 blip 발생 가능.
- X11 환경에서 `xset r rate 50 30` 로 단축 가능.
- SSH 환경에서는 SSH client (PuTTY/터미널) 의 키 리피트 설정이 적용됨.

안전
----
- 종료시 zero twist 를 3회 발행하여 도달 보장.
- 비정상 종료시에도 F405 watchdog (500ms cmd_vel timeout) 가 motor 정지.
- 운영 한계 외 속도 입력 차단 (LIN_MAX, ANG_MAX).

사용
----
  python3 tools/rover_teleop_kb.py
  # micro_ros_agent 가 떠 있어야 함. 받침대 위에서 시작 권장.
"""
import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist


PUBLISH_HZ    = 20
AUTO_STOP_S   = 0.40          # 마지막 키 후 이 시간 지나면 zero 발행
LIN_DEFAULT   = 0.20          # m/s
ANG_DEFAULT   = 1.00          # rad/s
LIN_STEP      = 0.05
ANG_STEP      = 0.20
LIN_MAX       = 0.60          # CLAUDE.md MAX_LINEAR_SPEED_MPS (0.654) 보다 보수적
ANG_MAX       = 3.00

# 키 → (lin_sign, ang_sign).  대각키는 두 성분 모두 사용.
KEYBINDS = {
    'w': ( 1,  0), 'W': ( 1,  0),
    's': (-1,  0), 'S': (-1,  0),
    'a': ( 0,  1), 'A': ( 0,  1),
    'd': ( 0, -1), 'D': ( 0, -1),
    'q': ( 1,  1), 'Q': ( 1,  1),
    'e': ( 1, -1), 'E': ( 1, -1),
    'z': (-1,  1), 'Z': (-1,  1),
    'c': (-1, -1), 'C': (-1, -1),
}

HEADER = """\
======================================================
  rover_teleop_kb — 키보드 teleop (조이스틱 모드)
======================================================
  W / S      전진 / 후진
  A / D      좌회전 / 우회전
  Q E Z C    대각 (전·후 + 좌·우)
  G          cruise 토글 — 전진 latch (A/D 로 조향 가능)
  SPACE      즉시 정지 (cruise 해제)
  ↑↓         선속도 ±0.05 m/s
  ←→         각속도 ±0.20 rad/s
  o          속도 기본값 reset
  ESC        종료
======================================================
"""


def read_key(settings, timeout=0.02):
    """raw 모드로 한 키 (또는 escape 시퀀스) 읽기. 없으면 빈 문자열.

    arrow key 는 `\\x1b[A/B/C/D` 3바이트로 들어옴 — 추가 read 로 묶음.
    """
    tty.setraw(sys.stdin.fileno())
    try:
        rlist, _, _ = select.select([sys.stdin], [], [], timeout)
        if not rlist:
            return ''
        ch = sys.stdin.read(1)
        if ch != '\x1b':
            return ch
        # ESC 또는 arrow key — 즉시 추가 바이트 시도. bare ESC 이면 추가 없음.
        rlist, _, _ = select.select([sys.stdin], [], [], 0.002)
        if not rlist:
            return '\x1b'
        seq = sys.stdin.read(2)
        return '\x1b' + seq
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


def main():
    rclpy.init()
    node = rclpy.create_node('rover_teleop_kb')
    pub = node.create_publisher(Twist, '/cmd_vel', 10)

    settings = termios.tcgetattr(sys.stdin)

    lin = LIN_DEFAULT
    ang = ANG_DEFAULT
    sign_lin = 0
    sign_ang = 0
    last_key_t = 0.0
    cruise = False                # G 로 토글되는 전진 latch

    print(HEADER)
    print(f"  현재 step: linear={lin:.2f} m/s   angular={ang:.2f} rad/s")
    print(f"  publish: {PUBLISH_HZ} Hz   auto-stop: {AUTO_STOP_S*1000:.0f} ms")
    print("  discovery 정착 대기 중... (약 0.8s)\n")

    # DDS discovery 정착 — 첫 publish 까지 ~1s 소비됨, 한 번만 지불.
    time.sleep(0.8)

    period = 1.0 / PUBLISH_HZ
    next_pub = time.monotonic()
    last_status_print = ''

    try:
        while True:
            key = read_key(settings)
            now = time.monotonic()

            if key:
                if key in ('\x03', '\x1b'):    # Ctrl+C / ESC — 종료
                    break

                if key == ' ':
                    sign_lin, sign_ang = 0, 0
                    cruise = False
                    last_key_t = 0.0          # 즉시 정지 (auto-stop 즉발)
                elif key in ('g', 'G'):
                    cruise = not cruise       # cruise 토글 — last_key_t 안 건드림
                elif key in KEYBINDS:
                    sl, sa = KEYBINDS[key]
                    sign_lin, sign_ang = sl, sa
                    last_key_t = now
                    if sl != 0:               # 수동 lin 입력은 cruise 해제 (A/D 만 cruise 보존)
                        cruise = False
                elif key == '\x1b[A':         # ↑
                    lin = min(LIN_MAX, lin + LIN_STEP)
                elif key == '\x1b[B':         # ↓
                    lin = max(0.0, lin - LIN_STEP)
                elif key == '\x1b[D':         # ←  (각속도 ↑)
                    ang = min(ANG_MAX, ang + ANG_STEP)
                elif key == '\x1b[C':         # →  (각속도 ↓)
                    ang = max(0.0, ang - ANG_STEP)
                elif key in ('o', 'O'):
                    lin, ang = LIN_DEFAULT, ANG_DEFAULT

            # auto-stop — 마지막 키 후 AUTO_STOP_S 경과시 정지.
            if now - last_key_t > AUTO_STOP_S:
                sign_lin, sign_ang = 0, 0

            # cruise 가 켜져 있으면 lin 만 강제로 +1 (auto-stop 무력화).
            if cruise:
                sign_lin = 1

            # 고정 주기 발행.
            if now >= next_pub:
                msg = Twist()
                msg.linear.x  = float(sign_lin) * lin
                msg.angular.z = float(sign_ang) * ang
                pub.publish(msg)
                next_pub = now + period

                tag = "[CRUISE]" if cruise else "        "
                status = (
                    f"\r cmd: lin={msg.linear.x:+5.2f} m/s "
                    f"ang={msg.angular.z:+5.2f} rad/s {tag}  "
                    f"|  step: lin={lin:.2f} ang={ang:.2f}     "
                )
                if status != last_status_print:
                    sys.stdout.write(status)
                    sys.stdout.flush()
                    last_status_print = status

    except KeyboardInterrupt:
        pass
    finally:
        # zero twist 안전 종료 — 여러번 발행하여 도달 보장.
        for _ in range(3):
            pub.publish(Twist())
            time.sleep(0.05)
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        node.destroy_node()
        rclpy.shutdown()
        print("\n\nstopped. (F405 watchdog 도 500ms 내 motor 정지 보장)")


if __name__ == '__main__':
    main()
