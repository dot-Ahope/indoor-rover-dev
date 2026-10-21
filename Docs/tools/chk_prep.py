#!/usr/bin/env python3
"""prep 확인을 한 프로세스(DDS 참여자 1 개)로 (2026-10-12 §13).
  왜: 기존 prep 은 `ros2 topic hz/param get/lifecycle get` 을 약 25 번 따로 불렀다 — 회당 3~15 s + 부를 때마다 참여자 탐색 폭주(§9.2).
      또 고정 대기(30 s 등) 대신 '준비될 때까지' 기다린다.
  동작: 아래 조건이 모두 될 때까지 폴링(기본 한도 150 s) → 코스트맵 비우기 → 재마킹 대기(WAIT s) → 요약 출력. 마지막 줄 PREP_OK / PREP_FAIL.
    필수: Nav2 수명 주기 active(controller·planner·bt_navigator·behavior·nav_map_server), map→base_link TF, /wheel_odom ≥ 20 Hz,
          /odometry/filtered ≥ 20 Hz, 전역 코스트맵에 저장 지도(크기 > 100×100).
    기록: 실행 중 파라미터(PreferForward·visualize·궤적 간격·전역 plugins·nvblox 프레임·obstacle 소스·stuck shadow), 배터리, /tf 주기.
  인자: [WAIT=15] [한도=150]
  10-21: 출발 위치 추정 검사 — 준비 뒤 map→base 가 기대 자세(환경 PREP_POSE, 기본 '0,0,0' = 출발 테이프)에서 위치 ±0.10 m · yaw ±2° 밖이면 PREP_FAIL.
    근거: 10-20 에 prep 직후 SLAM 이 출발 위치를 21° · −41° 틀린 적 2 회(정상일 땐 yaw 0.0~1.0°, 위치 3 cm 안 — 그날 prep 15 회).
    출발 테이프가 아닌 곳에서 prep 하면 PREP_POSE=any(검사 끔) 또는 PREP_POSE='x,y,yaw°'."""
import sys, time, math, os
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, qos_profile_sensor_data
from lifecycle_msgs.srv import GetState
from rcl_interfaces.srv import GetParameters
from nav_msgs.msg import OccupancyGrid, Odometry
from sensor_msgs.msg import BatteryState
from tf2_msgs.msg import TFMessage
from nav2_msgs.srv import ClearEntireCostmap
import tf2_ros

WAIT = float(sys.argv[1]) if len(sys.argv) > 1 else 15.0
LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 150.0
PP = os.environ.get('PREP_POSE', '0,0,0').strip()
POSE = None if PP == 'any' else tuple(float(v) for v in PP.split(','))
POS_TOL, YAW_TOL = 0.10, 2.0
LC = ['controller_server', 'planner_server', 'bt_navigator', 'behavior_server', 'nav_map_server']
PARAMS = {'/controller_server': ['FollowPathMPPI.PreferForwardCritic.cost_weight', 'FollowPathMPPI.vx_min', 'FollowPathMPPI.visualize',
                                 'FollowPathMPPI.TrajectoryVisualizer.trajectory_step', 'FollowPathMPPI.TrajectoryVisualizer.time_step'],
          '/global_costmap/global_costmap': ['plugins', 'nvblox_layer.nav2_costmap_global_frame', 'obstacle_layer.observation_sources'],
          '/stuck_monitor': ['shadow_mode']}


def pval(v):
    return {1: v.bool_value, 2: v.integer_value, 3: v.double_value, 4: v.string_value, 9: list(v.string_array_value)}.get(v.type, '(없음)')


class Chk(Node):
    def __init__(self):
        super().__init__('prepchk971')
        self.buf = tf2_ros.Buffer(); self.tl = tf2_ros.TransformListener(self.buf, self)
        self.t = {'wheel': [], 'ekf': [], 'tf': []}; self.gcm = None; self.batt = None
        self.create_subscription(Odometry, '/wheel_odom', lambda m: self.t['wheel'].append(time.time()), qos_profile_sensor_data)
        self.create_subscription(Odometry, '/odometry/filtered', lambda m: self.t['ekf'].append(time.time()), 10)
        self.create_subscription(TFMessage, '/tf', lambda m: self.t['tf'].append(time.time()), 100)
        self.create_subscription(BatteryState, '/battery', lambda m: setattr(self, 'batt', m.voltage), qos_profile_sensor_data)
        self.create_subscription(OccupancyGrid, '/global_costmap/costmap', self.cb_gcm,
                                 QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
        self.lc = {n: self.create_client(GetState, '/%s/get_state' % n) for n in LC}; self.state = {n: '?' for n in LC}; self.pend = {}
        self.pc = {n: self.create_client(GetParameters, n + '/get_parameters') for n in PARAMS}; self.pv = {}; self.ppend = {}

    def cb_gcm(self, m):
        self.gcm = (m.info.width, m.info.height, sum(1 for v in m.data if v >= 99))

    def hz(self, k, win=3.0):
        now = time.time(); self.t[k] = [x for x in self.t[k] if now - x <= win]
        return len(self.t[k]) / win

    def poll(self):
        for n, c in self.lc.items():
            if self.state[n] == 'active': continue
            f = self.pend.get(n)
            if f is None:
                if c.service_is_ready(): self.pend[n] = (c.call_async(GetState.Request()), time.time())
            elif f[0].done():
                r = f[0].result(); self.state[n] = r.current_state.label if r else '?'; self.pend[n] = None
            elif time.time() - f[1] > 4.0: self.pend[n] = None
        for n, c in self.pc.items():
            if n in self.pv: continue
            f = self.ppend.get(n)
            if f is None:
                if c.service_is_ready(): self.ppend[n] = (c.call_async(GetParameters.Request(names=PARAMS[n])), time.time())
            elif f[0].done():
                r = f[0].result()
                if r and len(r.values) == len(PARAMS[n]): self.pv[n] = [pval(v) for v in r.values]
                self.ppend[n] = None
            elif time.time() - f[1] > 4.0: self.ppend[n] = None

    def tfm(self):
        try:
            t = self.buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
            q = t.rotation; return (t.translation.x, t.translation.y, math.degrees(math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))))
        except Exception:
            return None


def main():
    rclpy.init(); n = Chk(); t0 = time.time(); last = ''; ok = False
    while time.time() - t0 < LIMIT:
        rclpy.spin_once(n, timeout_sec=0.1); n.poll()
        if time.time() - t0 < 4.0: continue
        need = [k for k, v in n.state.items() if v != 'active']
        if n.tfm() is None: need.append('map→base TF')
        if n.hz('wheel') < 20: need.append('/wheel_odom')
        if n.hz('ekf') < 20: need.append('/odometry/filtered')
        if n.gcm is None or n.gcm[0] * n.gcm[1] <= 20000: need.append('전역 지도')
        s = ' '.join(need)
        if s != last: print('  [%5.1f s] 기다리는 것: %s' % (time.time() - t0, s or '없음'), flush=True); last = s
        if not need: ok = True; break
    tready = time.time() - t0
    if ok:   # 코스트맵 비우기 + 재마킹 대기
        for nm in ('/local_costmap/clear_entirely_local_costmap', '/global_costmap/clear_entirely_global_costmap'):
            c = n.create_client(ClearEntireCostmap, nm)
            if c.wait_for_service(timeout_sec=5.0):
                f = c.call_async(ClearEntireCostmap.Request()); te = time.time()
                while not f.done() and time.time() - te < 8.0: rclpy.spin_once(n, timeout_sec=0.1)
                print('  %s: %s' % (nm.split('/')[-1], '완료' if f.done() else '응답 없음'), flush=True)
        te = time.time(); n.gcm = None
        while time.time() - te < WAIT: rclpy.spin_once(n, timeout_sec=0.1); n.poll()
    p = n.tfm()
    if ok and POSE is not None:   # 10-21: 출발 위치 추정 검사
        if p is None:
            ok = False; print('  ★ 위치 추정 검사: map→base 없음', flush=True)
        else:
            dp = math.hypot(p[0] - POSE[0], p[1] - POSE[1]); dy = (p[2] - POSE[2] + 180) % 360 - 180
            good = dp <= POS_TOL and abs(dy) <= YAW_TOL
            print('  위치 추정 검사(기대 %s): 위치 차 %.3f m · yaw 차 %+.1f° → %s' % (PP, dp, dy, '통과' if good else '★ 불합격 — SLAM 이 출발 위치를 틀림, prep 다시'), flush=True)
            ok = ok and good
    print('  준비까지 %.1f s | Nav2 %s' % (tready, ' '.join('%s=%s' % (k.replace('_server', ''), v) for k, v in n.state.items())))
    print('  /wheel_odom %.1f Hz · /odometry/filtered %.1f Hz · /tf %.1f Hz · 배터리 %s V' % (n.hz('wheel'), n.hz('ekf'), n.hz('tf'), ('%.2f' % n.batt) if n.batt else '?'))
    print('  map→base: %s' % (('(%.3f, %.3f) yaw %.1f°' % p) if p else '없음'))
    print('  전역 코스트맵: %s' % (('%d×%d · 치명/내접 %d 칸' % n.gcm) if n.gcm else '비운 뒤 아직 수신 없음'))
    for nd, names in PARAMS.items():
        v = n.pv.get(nd); print('  %s: %s' % (nd, ' · '.join('%s=%s' % (a.split('.')[-1] if 'Critic' not in a else 'PreferForward', b) for a, b in zip(names, v)) if v else '조회 실패'))
    print('PREP_OK' if ok else 'PREP_FAIL'); rclpy.shutdown(); return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
