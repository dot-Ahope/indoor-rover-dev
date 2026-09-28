#!/usr/bin/env python3
"""제자리 180° 회전 시험 (2026-09-28, 09-23 §20.3): 스키드스티어 제자리 회전 중 차체 중심이 옆으로 밀리는 양을 잰다.
  사용: python3 job562_spin.py NAME W_rad_s DIR REPS
    DIR: -1 = 시계(오른쪽, f0a2 와 같은 방향) / +1 = 반시계 / 0 = 교대(시계부터) — ⚠ 09-28 §5.1: 교대는 바닥 기준 같은 쪽으로 누적된다(쓰지 말 것). 같은 방향 반복이 짝수 회에서 상쇄
  동작: 회전마다 [정지 3 s → 시작 자세 기록 → /cmd_vel (v=0, ω=DIR·W) 20 Hz → EKF(자이로) 누적 회전이 180° − 관성 여유에
        이르면 0 지령 → 정지 4 s(SLAM 반영) → 끝 자세 기록]. Nav2 는 목표가 없으면 /cmd_vel 을 내지 않는다.
  안전: 라이다 점을 차체 좌표로 바꿔 **차체 중심 기준** 최근접을 본다(모서리 회전 반경 0.30 m).
        회전 전 < 0.50 m 이면 그 회전을 건너뛰고 중단, 회전 중 < 0.42 m(모서리 여유 0.12 m) 이면 즉시 0 지령·중단.
        (09-28: 사용자 판단으로 오른쪽 0.60 m 상태에서 진행 — 처음 값 0.60/0.40(라이다 거리)에서 변경)
        낮은 상자 등 라이다에 안 보이는 물체는 못 막는다.
        한도 = π/W × 2 + 5 s. 펌웨어 워치독(500 ms)도 있음.
  기록: /tmp/<NAME>.csv(10 Hz), 회전별 요약 — 시작 차체 기준 중심 이동(앞+/왼+)을 SLAM(map)·EKF(odom) 로 각각, 회전량 map/EKF/휠.
  한계: SLAM 값은 줄자 블록 측정으로 검증한다(§ 판정 M1)."""
import sys, math, time, csv
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan
import tf2_ros

NAME = sys.argv[1]; W = float(sys.argv[2]); DIR = int(sys.argv[3]); REPS = int(sys.argv[4])
COAST = W * 0.25            # 관성 회전 여유(rad) — 0 지령 뒤 더 도는 양 추정, 결과에 실제값이 남는다
PRE_MIN, RUN_MIN = 0.45, 0.42   # 09-28 §5.1: 회전 전 0.50→0.45(다음 밀림이 가까운 물체 반대쪽일 때 불필요한 중단 방지), 회전 중은 유지


def yaw_of(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


class Spin(Node):
    def __init__(self):
        super().__init__('spin562')
        self.buf = tf2_ros.Buffer(); self.tl = tf2_ros.TransformListener(self.buf, self)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.wyaw = None; self.rmin = 9.0; self.tcmd = 0.0; self.l2b = None   # l2b = 라이다→차체 (tx, ty, yaw)
        self.create_subscription(Odometry, '/wheel_odom', lambda m: setattr(self, 'wyaw', yaw_of(m.pose.pose.orientation)), qos_profile_sensor_data)
        self.create_subscription(LaserScan, '/scan', self.cb_scan, qos_profile_sensor_data)

    def cb_scan(self, m):
        if self.l2b is None:
            try:
                t = self.buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
                self.l2b = (t.translation.x, t.translation.y, yaw_of(t.rotation))
            except Exception:
                return
        tx, ty, th = self.l2b; best = 9.0
        for i, r in enumerate(m.ranges):
            if not math.isfinite(r) or r < 0.15: continue
            a = m.angle_min + i * m.angle_increment + th
            d = math.hypot(tx + r * math.cos(a), ty + r * math.sin(a))
            if d < best: best = d
        self.rmin = best

    def tf(self, a, b):
        try:
            t = self.buf.lookup_transform(a, b, rclpy.time.Time()).transform
            return (t.translation.x, t.translation.y, yaw_of(t.rotation))
        except Exception:
            return None

    def cmd(self, w):
        # 20 Hz 로 제한 — spin_once 는 메시지마다 돌아오므로 그대로 내면 수백 Hz 가 되어 micro-ROS 시리얼(460800)을 압박한다
        now = time.time()
        if now - self.tcmd < 0.05: return
        self.tcmd = now
        m = Twist(); m.angular.z = float(w); self.pub.publish(m)

    def spin_for(self, sec, w=None):
        t0 = time.time()
        while time.time() - t0 < sec:
            if w is not None: self.cmd(w)
            rclpy.spin_once(self, timeout_sec=0.05)


def rel(p0, p1):
    """p0 차체 기준 p1 중심 이동 (앞+, 왼+)."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; c, s = math.cos(p0[2]), math.sin(p0[2])
    return c * dx + s * dy, -s * dx + c * dy


def main():
    rclpy.init(); n = Spin()
    t0 = time.time()
    while time.time() - t0 < 15 and (n.tf('map', 'base_link') is None or n.tf('odom', 'base_link') is None or n.wyaw is None or n.l2b is None):
        rclpy.spin_once(n, timeout_sec=0.1)
    if n.tf('map', 'base_link') is None:
        print('TF 없음 — 중단'); return 2
    print('회전 시험 %s: ω %.2f rad/s, 방향 %s, %d 회 | 중심 기준 최근접 %.2f m' % (NAME, W, {-1: '시계', 1: '반시계', 0: '교대(시계부터)'}[DIR], REPS, n.rmin), flush=True)
    rows = []; res = []; tstart = time.time()
    M00 = n.tf('map', 'base_link'); O00 = n.tf('odom', 'base_link')
    for k in range(REPS):
        n.spin_for(3.0, 0.0)
        if n.rmin < PRE_MIN:
            print('  ★ 회전 %d 전 중심 기준 최근접 %.2f m < %.2f — 중단' % (k + 1, n.rmin, PRE_MIN)); break
        d = DIR if DIR != 0 else (-1 if k % 2 == 0 else 1)
        M0 = n.tf('map', 'base_link'); O0 = n.tf('odom', 'base_link'); W0 = n.wyaw
        acc = 0.0; lastyaw = O0[2]; wacc = 0.0; lw = W0; tr = time.time(); lim = math.pi / W * 2 + 5; stop = ''
        while True:
            n.cmd(d * W); rclpy.spin_once(n, timeout_sec=0.05)
            O = n.tf('odom', 'base_link'); M = n.tf('map', 'base_link')
            if O: acc += uw(O[2] - lastyaw); lastyaw = O[2]
            if n.wyaw is not None: wacc += uw(n.wyaw - lw); lw = n.wyaw
            if M and O and (not rows or time.time() - tstart - rows[-1][0] >= 0.1):
                rows.append((round(time.time() - tstart, 2), k + 1, M[0], M[1], math.degrees(M[2]), O[0], O[1], math.degrees(O[2]), round(n.rmin, 3)))
            if abs(acc) >= math.pi - COAST: break
            if n.rmin < RUN_MIN: stop = '라이다 %.2f m' % n.rmin; break
            if time.time() - tr > lim: stop = '한도 초과'; break
        tturn = time.time() - tr
        n.spin_for(1.0, 0.0); n.spin_for(3.0, 0.0)
        # 정지 뒤 누적(관성 포함)
        O = n.tf('odom', 'base_link'); acc += uw(O[2] - lastyaw)
        M1 = n.tf('map', 'base_link'); O1 = n.tf('odom', 'base_link')
        sx, sy = rel(M0, M1); ex, ey = rel(O0, O1)
        r = dict(k=k + 1, t=tturn, slam=(sx, sy), ekf=(ex, ey), rot_map=math.degrees(uw(M1[2] - M0[2])), rot_ekf=math.degrees(acc), rot_wheel=math.degrees(wacc), stop=stop)
        res.append(r)
        print('  회전 %d: %.1f s | 중심 이동(시작 차체 기준 앞+/왼+) SLAM (%+.3f, %+.3f) = %.3f m | EKF (%+.3f, %+.3f) | 회전 map %+.1f° EKF %+.1f° 휠 %+.1f° %s'
              % (k + 1, tturn, sx, sy, math.hypot(sx, sy), ex, ey, r['rot_map'], r['rot_ekf'], r['rot_wheel'], ('★ ' + stop) if stop else ''), flush=True)
        if stop: break
    n.spin_for(0.5, 0.0)
    with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 'rep', 'map_x', 'map_y', 'map_yaw', 'odom_x', 'odom_y', 'odom_yaw', 'scan_min']); w.writerows(rows)
    M1 = n.tf('map', 'base_link'); O1 = n.tf('odom', 'base_link')
    if res:
        sx, sy = rel(M00, M1); ex, ey = rel(O00, O1)
        lat = [abs(r['slam'][1]) for r in res]; tot = [math.hypot(*r['slam']) for r in res]
        print('\n블록 요약 %s: 회전 %d 회 | 회전당 SLAM 중심 이동 크기 평균 %.3f m (최소 %.3f, 최대 %.3f), 옆(|왼|) 평균 %.3f m'
              % (NAME, len(res), sum(tot) / len(tot), min(tot), max(tot), sum(lat) / len(lat)))
        print('  블록 누적(첫 시작 차체 기준 앞+/왼+): SLAM (%+.3f, %+.3f) m | EKF (%+.3f, %+.3f) m ← 줄자 측정과 대조' % (sx, sy, ex, ey))
        print('  누적 방향 %.1f°(map, 첫 시작 대비)' % math.degrees(uw(M1[2] - M00[2])))
    rclpy.shutdown(); return 0


if __name__ == '__main__':
    sys.exit(main())
