#!/usr/bin/env python3
"""트랙 속도 비율 통제 시험 (2026-10-08 §5): 회전 방식(느린/빠른 트랙 비 r)에 따라 회전 미끄러짐이 어떻게 달라지는지 잰다.
  사용: python3 job940_ratio.py NAME PLAN [REPS] [ANG_deg]
    PLAN = "r:dir:fwd,r:dir:fwd,..."  r ∈ [−1, 0] (−1 = 제자리, 0 = 피벗), dir −1 = 시계 / +1 = 반시계, fwd +1 = 앞으로 / −1 = 뒤로
    REPS = 블록당 회전 수(기본 4 → 같은 방향 4 × 90° = 한 바퀴라 반피벗도 대략 제자리로 돌아옴), ANG 기본 90°
  지령: 빠른 트랙을 F = 0.08 m/s 로 고정(모든 r 에서 같은 트랙 속도 — 상한 ≈0.085 아래), 펌웨어 분배 반게이지 b = 0.2215:
        |ω| = F·(1−r)/(2b),  |v| = F·(1+r)/2   (v_l = v − ω·b, v_r = v + ω·b 를 r = 느린/빠른, 빠른 = F 로 푼 것)
        r −1: ω 0.361, v 0 · −0.6: 0.289, 0.016 · −0.4: 0.253, 0.024 · −0.2: 0.217, 0.032 · 0: 0.181, 0.040
        → 회전 속도가 r 마다 다르다(교란 요인). 09-28 제자리 시험에서 0.20 vs 0.38 rad/s 차이가 없었으므로 트랙 속도를 같게 두는 쪽을 택함.
  동작: 회전마다 [정지 3 s → /cmd_vel (v, ω) 20 Hz → EKF(자이로) 누적 회전이 ANG − 관성 여유(ω·0.25 rad)면 0 지령 → 정지 4 s].
        측정은 오프라인: bag 의 정지 스캔끼리 직접 정합(실제 이동) − 휠 추측항법(/rover/status 측정 트랙 속도). 러너 값은 참고.
  안전: 라이다 점의 차체 중심 기준 최근접. 블록 시작 전 < PRE_MIN(0.85 m)이면 전체 중단 — 피벗(r 0)은 한 바퀴 동안 중심이 시작점에서
        최대 ≈0.44 m 벗어나고 모서리 반경 0.30 m 를 더하면 0.74 m. 회전 중 < RUN_MIN(0.40 m)이면 즉시 0 지령·전체 중단.
        회전 한도 = ANG/ω × 2 + 5 s. 펌웨어 워치독 500 ms. 라이다 높이(≈18.5 cm)보다 낮은 물체는 못 막는다 → 사용자가 주변을 비움.
  기록: /tmp/<NAME>.csv (10 Hz: 블록·회전·지령·map·odom·최근접), 회전별 한 줄 요약."""
import sys, math, time, csv
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
import tf2_ros

NAME = sys.argv[1]; PLAN = [tuple(float(x) for x in p.split(':')) for p in sys.argv[2].split(',')]
REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 4; ANG = math.radians(float(sys.argv[4]) if len(sys.argv) > 4 else 90.0)
F, B = 0.08, 0.2215
PRE_MIN, RUN_MIN = 0.85, 0.40


def yaw_of(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


class Ratio(Node):
    def __init__(self):
        super().__init__('ratio940')
        self.buf = tf2_ros.Buffer(); self.tl = tf2_ros.TransformListener(self.buf, self)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.rmin = 9.0; self.tcmd = 0.0; self.l2b = None
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

    def cmd(self, v, w):
        now = time.time()   # 20 Hz 제한(micro-ROS 시리얼 보호, 09-28)
        if now - self.tcmd < 0.05: return
        self.tcmd = now; m = Twist(); m.linear.x = float(v); m.angular.z = float(w); self.pub.publish(m)

    def hold(self, sec):
        t0 = time.time()
        while time.time() - t0 < sec:
            self.cmd(0.0, 0.0); rclpy.spin_once(self, timeout_sec=0.05)


def rel(p0, p1):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]; c, s = math.cos(p0[2]), math.sin(p0[2])
    return c * dx + s * dy, -s * dx + c * dy


def main():
    rclpy.init(); n = Ratio(); t0 = time.time()
    while time.time() - t0 < 15 and (n.tf('map', 'base_link') is None or n.tf('odom', 'base_link') is None or n.l2b is None):
        rclpy.spin_once(n, timeout_sec=0.1)
    if n.tf('odom', 'base_link') is None or n.l2b is None:
        print('TF/스캔 없음 — 중단'); return 2
    print('비율 시험 %s: 블록 %d × %d 회 × %.0f° | 중심 기준 최근접 %.2f m (블록 전 ≥ %.2f 필요)' % (NAME, len(PLAN), REPS, math.degrees(ANG), n.rmin, PRE_MIN), flush=True)
    rows = []; ts = time.time(); abort = ''
    for bi, (r, d, fw) in enumerate(PLAN, 1):
        w = d * F * (1 - r) / (2 * B); v = fw * F * (1 + r) / 2
        n.hold(3.0)
        if n.rmin < PRE_MIN:
            abort = '블록 %d 전 최근접 %.2f m < %.2f' % (bi, n.rmin, PRE_MIN); break
        print('블록 %d: r %+.1f %s %s → 지령 v %+.3f ω %+.3f (트랙 목표 L %+.3f R %+.3f)' % (bi, r, '시계' if d < 0 else '반시계', '앞' if fw > 0 else '뒤', v, w, v - w * B, v + w * B), flush=True)
        for k in range(1, REPS + 1):
            n.hold(3.0 if k > 1 else 0.5)
            O0 = n.tf('odom', 'base_link'); M0 = n.tf('map', 'base_link'); acc = 0.0; last = O0[2]
            tr = time.time(); lim = ANG / abs(w) * 2 + 5; coast = abs(w) * 0.25; stop = ''
            while True:
                n.cmd(v, w); rclpy.spin_once(n, timeout_sec=0.05)
                O = n.tf('odom', 'base_link')
                if O: acc += uw(O[2] - last); last = O[2]
                if not rows or time.time() - ts - rows[-1][0] >= 0.1:
                    M = n.tf('map', 'base_link') or (math.nan,) * 3
                    rows.append((round(time.time() - ts, 2), bi, k, r, d, fw, v, w, M[0], M[1], math.degrees(M[2]), O[0], O[1], math.degrees(O[2]), round(n.rmin, 3)))
                if abs(acc) >= ANG - coast: break
                if n.rmin < RUN_MIN: stop = '회전 중 최근접 %.2f m' % n.rmin; break
                if time.time() - tr > lim: stop = '한도 초과'; break
            tt = time.time() - tr; n.hold(4.0)
            O1 = n.tf('odom', 'base_link'); acc += uw(O1[2] - last); M1 = n.tf('map', 'base_link')
            ex, ey = rel(O0, O1); mx, my = rel(M0, M1) if (M0 and M1) else (math.nan, math.nan)
            print('  회전 %d-%d: %.1f s | 회전 EKF %+.1f° | 중심 이동(시작 차체 기준 앞+/왼+) EKF (%+.3f, %+.3f) · map (%+.3f, %+.3f) | 최근접 %.2f m %s'
                  % (bi, k, tt, math.degrees(acc), ex, ey, mx, my, n.rmin, ('★ ' + stop) if stop else ''), flush=True)
            if stop: abort = stop; break
        if abort: break
    n.hold(0.5)
    with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
        c = csv.writer(f); c.writerow(['t', 'block', 'rep', 'r', 'dir', 'fwd', 'v', 'w', 'map_x', 'map_y', 'map_yaw', 'odom_x', 'odom_y', 'odom_yaw', 'scan_min']); c.writerows(rows)
    print('★ 중단: ' + abort if abort else '완료 — 블록 %d 개' % len(PLAN), flush=True)
    rclpy.shutdown(); return 1 if abort else 0


if __name__ == '__main__':
    sys.exit(main())
