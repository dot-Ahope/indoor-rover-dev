#!/usr/bin/env python3
"""stuck_monitor — rover-level 정체/접촉 감시 (2026-09-07).

왜 필요한가
  펌웨어 스톨 감지는 '휠이 안 도는' 구속만 잡는다(09-07 받침대 검증). 벽에 밀리거나 긁히며
  트랙이 헛도는 경우는 휠이 계속 돌아 펌웨어도, 휠 오도 기반 EKF 도 "이동 중"으로 본다
  (09-07 job54e MPPI 벽 접촉 사고에서 실증). 따라서 **휠과 무관한 관측**으로 실제 이동을 확인해야 한다.

방법 — 라이다 스캔 자체를 이동 관측으로 사용 (자이로도 병행)
  창(WINDOW s) 동안 지령 적산 ∫|v|dt, ∫|ω|dt 가 문턱 이상인데,
    회전: 창 전/후 스캔 프로파일(1° 빈)의 각도 상관 이동량, 자이로 y축 적분(D455f 프레임)
    병진: 회전 제거 후 정면/후면 ±20° 섹터의 range 중앙값 변화
  로 본 실제 이동이 지령의 RATIO 미만이면 '정체'. 연속 2회 판정 시 조치.
  조치(shadow_mode=false): Nav2 목표 취소 + /cmd_vel 0 + /rover/stuck 진단(level 2).
  shadow_mode=true(기본): 로그·진단(level 1)만 — 실주행 오탐 검증 후 해제.

한계
  - 정면·후면 3m 내 유효 반사가 없으면 병진 판정 불가 → 회전 판정만 사용, 그마저 없으면 판정 보류(오탐 방지).
  - 라이다 최소감지 0.2m: 정면 벽이 그보다 가까우면 정면 섹터 무효 → 후면 섹터로 대체.
"""
import math, time
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan, Imu
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from action_msgs.srv import CancelGoal

LIDAR_YAW = math.pi          # S2L 장착 yaw (rover.urdf) — 스캔각 + π = 로버 기준각
BINS = 360


def profile(msg):
    """스캔 → 로버 기준 1° 빈 최소 range 프로파일 (nan = 무효)."""
    r = np.asarray(msg.ranges, dtype=np.float32)
    a = msg.angle_min + msg.angle_increment * np.arange(len(r)) + LIDAR_YAW
    ok = np.isfinite(r) & (r > msg.range_min) & (r < min(msg.range_max, 12.0))
    prof = np.full(BINS, np.inf, dtype=np.float32)   # inf 로 시작해야 minimum.at 이 동작 (nan 은 전파됨)
    idx = (np.degrees(a[ok]) % 360).astype(int) % BINS
    np.minimum.at(prof, idx, r[ok])          # 같은 빈은 최소값
    prof[np.isinf(prof)] = np.nan
    return prof


def rot_shift_deg(A, B):
    """B 를 얼마나 돌리면 A 와 맞는가 (deg, 포물선 세밀화). 유효 겹침 부족 시 None."""
    best = None
    for d in range(-179, 180):
        Br = np.roll(B, d); m = np.isfinite(A) & np.isfinite(Br)
        if m.sum() < BINS * 0.3: continue
        c = float(np.median(np.abs(A[m] - Br[m])))
        if best is None or c < best[1]: best = (d, c)
    if best is None: return None
    d0 = best[0]
    def cost(dd):
        Br = np.roll(B, dd); m = np.isfinite(A) & np.isfinite(Br)
        return float(np.median(np.abs(A[m] - Br[m]))) if m.sum() > BINS * 0.3 else 1e9
    cm, c0, cp = cost(d0 - 1), best[1], cost(d0 + 1)
    den = cm - 2 * c0 + cp
    sub = 0.5 * (cm - cp) / den if abs(den) > 1e-9 else 0.0
    return d0 + max(-1.0, min(1.0, sub))


def sector_delta(A, B, center_deg, half=20, max_r=3.0):
    """center 섹터에서 median(A - B) (m). 앞으로 가면 정면 range 감소 → A-B > 0. 유효점 부족 시 None."""
    idx = [(center_deg + k) % 360 for k in range(-half, half + 1)]
    a, b = A[idx], B[idx]
    m = np.isfinite(a) & np.isfinite(b) & (a < max_r) & (b < max_r)
    if m.sum() < 8: return None
    return float(np.median(a[m] - b[m]))


class StuckMonitor(Node):
    def __init__(self):
        super().__init__('stuck_monitor')
        p = self.declare_parameters('', [
            ('window', 2.0), ('v_thr', 0.015), ('w_thr', 0.10), ('ratio', 0.25),
            ('confirm', 2), ('cooldown', 5.0), ('shadow_mode', True), ('rate', 5.0)])
        g = lambda k: self.get_parameter(k).value
        self.W, self.v_thr, self.w_thr = g('window'), g('v_thr'), g('w_thr')
        self.ratio, self.confirm, self.cooldown = g('ratio'), int(g('confirm')), g('cooldown')
        self.shadow = bool(g('shadow_mode'))
        self.cmds, self.scans = [], []      # (t,v,w) / (t,profile)
        self.gyro = []                      # (t, wz_robot)
        self.hits, self.last_action = 0, 0.0
        self.create_subscription(Twist, '/cmd_vel', self.cb_cmd, 10)
        self.create_subscription(LaserScan, '/scan', self.cb_scan, qos_profile_sensor_data)
        self.create_subscription(Imu, '/imu/data', self.cb_imu, qos_profile_sensor_data)
        self.diag_pub = self.create_publisher(DiagnosticArray, '/rover/stuck', 5)
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.cancel = self.create_client(CancelGoal, '/navigate_to_pose/_action/cancel_goal')
        self.create_timer(1.0 / g('rate'), self.tick)
        self.get_logger().info(f"stuck_monitor 시작 (window {self.W}s, ratio {self.ratio}, "
                               f"{'SHADOW(로그만)' if self.shadow else 'ACTIVE(취소+정지)'})")

    def cb_cmd(self, m): self.cmds.append((time.time(), m.linear.x, m.angular.z))
    def cb_scan(self, m): self.scans.append((time.time(), profile(m)))
    def cb_imu(self, m): self.gyro.append((time.time(), -m.angular_velocity.y))   # D455f y축(부호 반대) = 로버 yaw율

    def _prune(self, now):
        keep = now - self.W - 0.5
        self.cmds = [c for c in self.cmds if c[0] >= keep]
        self.scans = [s for s in self.scans if s[0] >= keep]
        self.gyro = [q for q in self.gyro if q[0] >= keep]

    def _integrate(self, seq, now, idx):
        """창 내 |값| 적산 (사다리꼴 근사)."""
        pts = [x for x in seq if x[0] >= now - self.W]
        if len(pts) < 2: return 0.0
        return sum(abs(pts[i][idx]) * (pts[i][0] - pts[i-1][0]) for i in range(1, len(pts)))

    def tick(self):
        now = time.time(); self._prune(now)
        dist_cmd = self._integrate(self.cmds, now, 1)
        ang_cmd = self._integrate(self.cmds, now, 2)
        want_move = dist_cmd >= self.v_thr * self.W or ang_cmd >= self.w_thr * self.W
        if not want_move or len(self.scans) < 2:
            self.hits = 0; return
        old = [s for s in self.scans if s[0] <= now - self.W]
        if not old: return
        A, B = old[-1][1], self.scans[-1][1]

        # 회전 관측: 스캔 상관 + 자이로 적분 중 큰 쪽(어느 하나라도 움직임을 보이면 움직인 것)
        rot_scan = rot_shift_deg(A, B)
        rot_gyro = math.degrees(self._integrate(self.gyro, now, 1))
        rot_obs = max(abs(rot_scan) if rot_scan is not None else 0.0, rot_gyro)

        # 병진 관측: 회전 제거 후 정면/후면 섹터 range 변화
        Br = np.roll(B, int(round(rot_scan))) if rot_scan is not None else B
        f, b = sector_delta(A, Br, 0), sector_delta(A, Br, 180)
        trans_obs = max(abs(f) if f is not None else 0.0, abs(b) if b is not None else 0.0)
        trans_valid = f is not None or b is not None

        # 판정: 지령이 요구한 이동 중 관측된 비율
        ratios = []
        if dist_cmd >= self.v_thr * self.W and trans_valid: ratios.append(trans_obs / dist_cmd)
        if ang_cmd >= self.w_thr * self.W: ratios.append(rot_obs / math.degrees(ang_cmd))
        if not ratios: self.hits = 0; return      # 판정 근거 없음 → 보류
        r = max(ratios)
        self.hits = self.hits + 1 if r < self.ratio else 0
        if self.hits >= self.confirm and now - self.last_action > self.cooldown:
            self.last_action = now; self.hits = 0
            self.on_stuck(dist_cmd, ang_cmd, trans_obs, rot_obs, r)

    def on_stuck(self, dist_cmd, ang_cmd, trans_obs, rot_obs, r):
        msg = (f"STUCK: 지령 {dist_cmd*100:.1f}cm/{math.degrees(ang_cmd):.0f}° 인데 "
               f"관측 {trans_obs*100:.1f}cm/{rot_obs:.1f}° (비율 {r:.2f})")
        self.get_logger().warn(msg + (" [shadow — 조치 없음]" if self.shadow else " → 목표 취소·정지"))
        da = DiagnosticArray(); da.header.stamp = self.get_clock().now().to_msg()
        st = DiagnosticStatus(level=DiagnosticStatus.WARN if self.shadow else DiagnosticStatus.ERROR,
                              name='stuck_monitor', message=msg, hardware_id='rover')
        st.values = [KeyValue(key='ratio', value=f"{r:.3f}"), KeyValue(key='shadow', value=str(self.shadow))]
        da.status.append(st); self.diag_pub.publish(da)
        if self.shadow: return
        if self.cancel.service_is_ready():
            self.cancel.call_async(CancelGoal.Request())
        for _ in range(10): self.cmd_pub.publish(Twist())


def selftest():
    """이동 없이 검증: 합성 프로파일로 회전/병진 추정기 점검."""
    rng = np.random.default_rng(0)
    A = 1.0 + 0.5 * np.sin(np.radians(np.arange(BINS)) * 3) + rng.normal(0, 0.01, BINS)
    B = np.roll(A, -15)                                   # 15° 회전
    print("회전 추정(기대 15):", rot_shift_deg(A, B))
    C = A.copy(); C[[i % 360 for i in range(-20, 21)]] -= 0.05   # 정면 5cm 접근
    print("병진 추정(기대 0.05):", sector_delta(A, C, 0))


def main():
    import sys
    if '--selftest' in sys.argv: selftest(); return
    from rclpy.executors import ExternalShutdownException
    rclpy.init(); n = StuckMonitor()
    try: rclpy.spin(n)
    except (KeyboardInterrupt, ExternalShutdownException): pass
    finally:
        try: n.destroy_node(); rclpy.try_shutdown()
        except Exception: pass


if __name__ == '__main__':
    main()
