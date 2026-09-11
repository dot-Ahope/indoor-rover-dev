#!/usr/bin/env python3
"""velocity_smoother.velocity_timeout A/B 검증 (2026-09-11).

  bag_s4r2 에서 BackUp 첫 1.0 s 동안 smoother 의 0(20 Hz)과 behavior_server 의 -0.05(10 Hz)가
  맞물렸다(100 ms 창당 3개). 원인: 컨트롤러 마지막 명령 뒤 smoother 가 velocity_timeout 동안 0 을
  계속 내보낸다. 실제 충돌을 기다리지 않고 같은 메커니즘을 재현한다:
    (1) 컨트롤러처럼 /cmd_vel_nav 에 +0.05 를 20 Hz 로 2.0 s → 끊는다 (FollowPath 중단 흉내)
    (2) 0.4 s 뒤(BT 전환 실측 0.45 s) BackUp 액션 호출 (0.15 m, 0.05 m/s)
    (3) /cmd_vel 을 수신 시각으로 기록 → 후진 첫 1.0 s 의 100 ms 창당 메시지 수, 0 메시지 수
  A: velocity_timeout 현재값(0.3)   B: 1.0 으로 바꿔 같은 절차   → 끝나면 0.3 복원
  판정: A 는 창당 1개·0 없음, B 는 창당 3개·0 섞임이면 원인·수정 모두 확정.
"""
import sys, time, math, subprocess
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Twist, Point
from nav2_msgs.action import BackUp, DriveOnHeading
from builtin_interfaces.msg import Duration

rclpy.init()
n = Node('ab282')
pub_nav = n.create_publisher(Twist, '/cmd_vel_nav', 10)
REC = []
n.create_subscription(Twist, '/cmd_vel', lambda m: REC.append((time.time(), m.linear.x)), 20)
MODE = sys.argv[1] if len(sys.argv) > 1 else 'backup'
if MODE == 'drive':
    ac = ActionClient(n, DriveOnHeading, '/drive_on_heading'); SIGN = +1
else:
    ac = ActionClient(n, BackUp, '/backup'); SIGN = -1
if not ac.wait_for_server(timeout_sec=10.0):
    print('액션 서버 없음'); sys.exit(1)


def param_get():
    out = subprocess.run("source /opt/ros/humble/setup.bash; timeout 6 ros2 param get /velocity_smoother velocity_timeout",
                         shell=True, capture_output=True, text=True, executable='/bin/bash').stdout
    return out.strip().split('is:')[-1].strip()


def param_set(v):
    subprocess.run("source /opt/ros/humble/setup.bash; timeout 8 ros2 param set /velocity_smoother velocity_timeout %s" % v,
                   shell=True, capture_output=True, text=True, executable='/bin/bash')
    return param_get()


def trial(label):
    REC.clear()
    t0 = time.time()
    cmd = Twist(); cmd.linear.x = 0.05
    # (1) 컨트롤러 흉내: 20 Hz 2.0 s
    while time.time() - t0 < 2.0:
        pub_nav.publish(cmd); rclpy.spin_once(n, timeout_sec=0.0); time.sleep(0.05)
    t_stop = time.time()
    fwd = [v for t, v in REC if v > 0.005]
    print('  전진 단계: /cmd_vel 메시지 %d개, 그중 +: %d개 (최대 %.3f)' % (len(REC), len(fwd), max(fwd) if fwd else 0))
    # (2) 0.4 s 뒤 BackUp
    while time.time() - t_stop < 0.4:
        rclpy.spin_once(n, timeout_sec=0.02)
    if MODE == 'drive':
        g = DriveOnHeading.Goal(); g.target = Point(x=0.15, y=0.0, z=0.0); g.speed = 0.05
    else:
        g = BackUp.Goal(); g.target = Point(x=0.15, y=0.0, z=0.0); g.speed = 0.05
    g.time_allowance = Duration(sec=15)
    fut = ac.send_goal_async(g)
    while not fut.done():
        rclpy.spin_once(n, timeout_sec=0.02)
    gh = fut.result()
    if gh is None or not gh.accepted:
        print('  BackUp 거부'); return None
    rf = gh.get_result_async()
    t_goal = time.time()
    while not rf.done() and time.time() - t_goal < 15:
        rclpy.spin_once(n, timeout_sec=0.02)
    t_end = time.time()
    st = {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}
    code = rf.result().status if rf.done() else -1
    print('  액션 결과: %s (%.1f s)' % (st.get(code, code), t_end - t_goal))
    while time.time() - t_end < 1.0:
        rclpy.spin_once(n, timeout_sec=0.02)
    # (3) 분석
    rec = [(t - t_stop, v) for t, v in REC]
    backs = [t for t, v in rec if (v * SIGN) > 0.005 and t > 0.3]
    if not backs:
        print('  행동 명령 관측 없음 (중단 후 /cmd_vel %d개)' % sum(1 for t, v in rec if t > 0)); return None
    tb = backs[0]
    win = [(t, v) for t, v in rec if tb <= t < tb + 1.0]
    zeros = sum(1 for t, v in win if abs(v) < 0.005)
    negs = sum(1 for t, v in win if (v * SIGN) > 0.005)
    import collections
    per = collections.Counter(int((t - tb) * 10) for t, v in win)
    mx = max(per.values()) if per else 0
    # smoother 의 마지막 0 시각(중단 후)
    zeros_after_stop = [t for t, v in rec if t > 0 and abs(v) < 0.005 and t < tb]
    last0 = max(zeros_after_stop) if zeros_after_stop else float('nan')
    print('  [%s] 중단→첫 행동명령 %.2f s | 중단 후 smoother 0 마지막 %.2f s | 후진 첫 1 s: 메시지 %d (0: %d, 후진: %d), 100ms 창당 최대 %d'
          % (label, tb, last0, len(win), zeros, negs, mx))
    seq = ' '.join('%.2f:%+.2f' % (t - tb, v) for t, v in win[:14])
    print('    처음 14개: ' + seq)
    return dict(tb=tb, last0=last0, zeros=zeros, negs=negs, mx=mx)


print('현재 velocity_timeout =', param_get())
ra = trial('A timeout=%s' % param_get())
time.sleep(1.0)
vb = param_set(1.0); print('B 로 변경 →', vb)
rb = trial('B timeout=%s' % vb)
vr = param_set(0.3); print('복원 →', vr)
print()
print('=== 판정 ===')
if ra and rb:
    print('  A(0.3): 후진 첫 1 s 에 0 메시지 %d개, 창당 최대 %d   |   B(1.0): 0 메시지 %d개, 창당 최대 %d'
          % (ra['zeros'], ra['mx'], rb['zeros'], rb['mx']))
    ok = ra['zeros'] == 0 and ra['mx'] == 1 and rb['zeros'] > 0 and rb['mx'] >= 2
    print('  → ' + ('원인·수정 확정: 0.3 에서 맞물림 사라짐, 1.0 에서 재현' if ok else '판정 보류 — 위 수치로 다시 본다'))
