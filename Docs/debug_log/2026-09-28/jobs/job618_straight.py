#!/usr/bin/env python3
"""직진 전·후진 시험 (2026-09-28 §23, A2·A3): 같은 거리를 앞으로 갔다가 뒤로 돌아오며
  ① 휠 거리 vs 실제 거리(bag 정지 스캔 정합으로 사후 측정) — 전진·후진의 슬립 비대칭
  ② 직진 중 방향 틀어짐(EKF=자이로) — 좌우 트랙 비대칭
  ③ 바퀴별 듀티·측정 속도(/rover/status L·R) — 모터/드라이버의 정·역 비대칭 후보
  를 기록한다.
  사용: python3 job618_straight.py NAME DIST VF VR REPS   (예: s_fb 0.6 0.07 0.06 2)
  동작: 회차마다 [정지 3 s → 전진 v=+VF, ω=0 → EKF 이동 DIST 에서 0 지령 → 정지 3 s → 후진 v=−VR → 이동 DIST → 정지 3 s].
  안전: 라이다 점 중 진행 방향 차체 앞(뒤)끝 너머 |by|<0.25 m 안의 최근접이 0.15 m 미만이면 즉시 정지·중단.
        낮은 상자처럼 라이다에 안 보이는 물체는 못 막는다(거리로 정한 이동량으로 제한).
  기록: /tmp/<NAME>.csv(10 Hz: t, 회차, 구간(F/R/S), odom x·y·yaw, 지령 v, L·R 목표·측정 mm/s·듀티 %·pps), 구간 요약."""
import sys, math, time, csv
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from diagnostic_msgs.msg import DiagnosticArray
import tf2_ros

NAME = sys.argv[1]; DIST = float(sys.argv[2]); VF = float(sys.argv[3]); VR = float(sys.argv[4]); REPS = int(sys.argv[5])
CLEAR = 0.15


def yaw_of(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


class St(Node):
    def __init__(self):
        super().__init__('straight618')
        self.buf = tf2_ros.Buffer(); self.tl = tf2_ros.TransformListener(self.buf, self)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10); self.tcmd = 0.0
        self.front = self.back = 9.0; self.l2b = None; self.wh = {'L': {}, 'R': {}}
        self.create_subscription(LaserScan, '/scan', self.cb_scan, qos_profile_sensor_data)
        self.create_subscription(DiagnosticArray, '/rover/status', self.cb_st, qos_profile_sensor_data)   # 09-28: 펌웨어 발행은 best effort — reliable 구독이면 못 받음(s_fb1)

    def cb_st(self, m):
        for s in m.status:
            for kv in s.values:
                if kv.key in ('L', 'R'):
                    self.wh[kv.key] = {a: int(b) for a, b in (p.split('=') for p in kv.value.split())}

    def cb_scan(self, m):
        if self.l2b is None:
            try:
                t = self.buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
                self.l2b = (t.translation.x, t.translation.y, yaw_of(t.rotation))
            except Exception:
                return
        tx, ty, th = self.l2b; f = b = 9.0
        for i, r in enumerate(m.ranges):
            if not math.isfinite(r) or r < 0.15: continue
            a = m.angle_min + i * m.angle_increment + th; x, y = tx + r * math.cos(a), ty + r * math.sin(a)
            if abs(y) < 0.25:
                if x > 0.25: f = min(f, x - 0.25)
                elif x < -0.25: b = min(b, -0.25 - x)
        self.front, self.back = f, b

    def tf(self):
        try:
            t = self.buf.lookup_transform('odom', 'base_link', rclpy.time.Time()).transform
            return (t.translation.x, t.translation.y, yaw_of(t.rotation))
        except Exception:
            return None

    def cmd(self, v):
        now = time.time()
        if now - self.tcmd < 0.05: return
        self.tcmd = now; m = Twist(); m.linear.x = float(v); self.pub.publish(m)


def main():
    rclpy.init(); n = St(); t0 = time.time()
    while time.time() - t0 < 15 and (n.tf() is None or n.l2b is None): rclpy.spin_once(n, timeout_sec=0.1)
    if n.tf() is None: print('TF 없음 — 중단'); return 2
    print('직진 시험 %s: 거리 %.2f m, 전진 %.3f / 후진 %.3f m/s, %d 회 | 앞 여유 %.2f m, 뒤 여유 %.2f m' % (NAME, DIST, VF, VR, REPS, n.front, n.back), flush=True)
    rows = []; ts = time.time(); stop = ''

    def log(k, ph, v):
        p = n.tf()
        if p and (not rows or time.time() - ts - rows[-1][0] >= 0.1):
            L, R = n.wh['L'], n.wh['R']
            rows.append((round(time.time() - ts, 2), k, ph, p[0], p[1], math.degrees(p[2]), v,
                         L.get('tgt'), L.get('v'), L.get('d'), L.get('pps'), R.get('tgt'), R.get('v'), R.get('d'), R.get('pps')))

    def hold(k, sec):
        te = time.time()
        while time.time() - te < sec: n.cmd(0.0); rclpy.spin_once(n, timeout_sec=0.02); log(k, 'S', 0.0)

    def move(k, ph, v):
        p0 = n.tf(); tl = time.time()
        while True:
            n.cmd(v); rclpy.spin_once(n, timeout_sec=0.02); log(k, ph, v); p = n.tf()
            if math.hypot(p[0] - p0[0], p[1] - p0[1]) >= DIST: return ''
            if (v > 0 and n.front < CLEAR) or (v < 0 and n.back < CLEAR): return '라이다 %s %.2f m' % ('앞' if v > 0 else '뒤', n.front if v > 0 else n.back)
            if time.time() - tl > DIST / abs(v) * 2 + 5: return '한도 초과'

    for k in range(1, REPS + 1):
        hold(k, 3.0)
        stop = move(k, 'F', VF)
        if stop: break
        hold(k, 3.0)
        stop = move(k, 'R', -VR)
        if stop: break
        hold(k, 3.0)
        print('  회 %d 완료' % k, flush=True)
    hold(0, 1.0)
    if stop: print('  ★ 중단: %s' % stop)
    with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 'rep', 'phase', 'odom_x', 'odom_y', 'odom_yaw', 'v_cmd', 'L_tgt', 'L_v', 'L_duty', 'L_pps', 'R_tgt', 'R_v', 'R_duty', 'R_pps']); w.writerows(rows)
    # 구간 요약: 방향 틀어짐(EKF), 바퀴별 듀티·측정 속도 평균(정상 구간 = 구간 시작 1 s 뒤부터)
    for k in range(1, REPS + 1):
        for ph in ('F', 'R'):
            seg = [r for r in rows if r[1] == k and r[2] == ph]
            if len(seg) < 12: continue
            st = [r for r in seg if r[0] - seg[0][0] > 1.0 and r[9] is not None]
            dyaw = uw(math.radians(seg[-1][5] - seg[0][5]))
            dist = math.hypot(seg[-1][3] - seg[0][3], seg[-1][4] - seg[0][4])
            avg = lambda i: sum(r[i] for r in st) / len(st) if st else float('nan')
            print('  회 %d %s: EKF 이동 %.3f m, 방향 변화 %+.2f° | L 목표 %.0f 측정 %.0f mm/s 듀티 %.1f %% | R 목표 %.0f 측정 %.0f mm/s 듀티 %.1f %% (표본 %d)'
                  % (k, '전진' if ph == 'F' else '후진', dist, math.degrees(dyaw), avg(7), avg(8), avg(9), avg(11), avg(12), avg(13), len(st)), flush=True)
    rclpy.shutdown(); return 0


if __name__ == '__main__':
    sys.exit(main())
