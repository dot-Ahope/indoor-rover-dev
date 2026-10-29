#!/usr/bin/env python3
"""place_server — 장소 이름으로 이동 · 복귀 · 정지 (F2.5 S1, 2026-10-28 — 설계 Docs/07_language/F25_PLACE_LLM_DESIGN.md §3.2).

입력: /place/command (std_msgs/String) — '<요청id>|<명령>' 또는 '<명령>'. 명령:
  go_to <장소>   등록부(places.yaml)의 이름 · 별칭 중 하나로 이동
  return          home 장소(출발점)로 이동 — 09-30 §9 사용자: "돌아와 하면 출발 위치로 복귀"
  stop            진행 중 목표 취소(Nav2 모든 목표) — 언제든 받음
  list · where    등록 장소 목록 · 현재 map 자세
출력: /place/status (std_msgs/String, JSON 한 줄) — {"id", "state": accepted|rejected|moving|arrived|failed|canceled|info|checked(dry_run), "place", "detail"}

원칙(설계 §1 · §4):
  · 좌표는 등록부에서만 나온다. 모르는 이름 → 움직이지 않고 rejected.
  · 이동 중 새 go_to · return 은 거절('먼저 stop') — 10-28 기본값(설계 §8-4 결정 전).
  · 목표 여유 검사: 목표 자세 차체(반길이 0.26 · 반폭 0.175) ↔ 전역 코스트맵 치명 칸 ≥ min_clear(0.10 m) 아니면 rejected(job377 기준).
  · 목표 방향: yaw_mode p = 계획 경로 끝 0.3 m 방향, f = p 와 같되 xy 0.15 m 안이면 방향 맞춤 없이 끝(arrived_xy), 숫자 = 고정(도).
    경로 조회는 **별도 상주 프로세스**(path_end_yaw.py --serve) — 같은 노드에서 compute_path_to_pose 를 부르면 뒤이은
    navigate_to_pose 응답이 오지 않던 사고(09-28 §20) 때문. 조회 실패 시 직선 방향.
  · 시간 · 무진행 한도는 nav_guard(Nav2 와 독립, Jetson 안)가 맡는다.
  · 출발 전 위치 추정 검사(10-29 §2): 지금 라이다 한 판을 정적 /map 에 맞춰 점수(점유 칸 1 칸 안 점 비율)와 ±30° 훑은 최적 각을 본다.
    점수 < loc_min_score 이거나, 최적 각이 loc_max_yaw 를 넘고 그 각에서 점수가 loc_min_gain 이상 오르면 rejected — 오래 세워 둔 로버의
    방향 추정이 돌아간 채 출발하지 않게(10-28 §16.1: 0.140 · −32.5°, f2pl1 출발 직전 −7°). 고치지는 않는다(prep · 재위치는 사람).
파라미터: places_file(기본 = 이 패키지 share/config/places.yaml) · min_clear(0.10) · xy_done(0.15) · dry_run(False: True 면 목표를 보내지 않고 검사까지만)
          loc_check(True) · loc_min_score(0.40) · loc_max_yaw(4.0°) · loc_min_gain(0.03)
"""
import json, math, os, select, subprocess, time
import numpy as np
import yaml
import rclpy
import rclpy.executors
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from std_msgs.msg import String
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from rclpy.qos import qos_profile_sensor_data
from nav2_msgs.action import NavigateToPose
from action_msgs.srv import CancelGoal
import tf2_ros

HL, HW = 0.26, 0.175   # 목표 여유 검사 차체 반길이 · 반폭(job377 과 같음)


def yaw_of(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


class PlaceServer(Node):
    def __init__(self):
        super().__init__('place_server')
        try:
            from ament_index_python.packages import get_package_share_directory
            dflt = os.path.join(get_package_share_directory('rover_navigation'), 'config', 'places.yaml')
        except Exception:
            dflt = ''
        for k, v in (('places_file', dflt), ('min_clear', 0.10), ('xy_done', 0.15), ('dry_run', False), ('path_yaw_script', ''),
                     ('loc_check', True), ('loc_min_score', 0.40), ('loc_max_yaw', 4.0), ('loc_min_gain', 0.03)):
            self.declare_parameter(k, v)
        self.reg = self.load_places()
        self.buf = tf2_ros.Buffer(); self.tl = tf2_ros.TransformListener(self.buf, self)
        self.gcm = None
        self.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: setattr(self, 'gcm', m),
                                 QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
        self.scan, self.occ = None, None   # 위치 추정 검사용: 마지막 라이다 · 정적 지도 점유(1 칸 팽창)
        self.create_subscription(LaserScan, '/scan', lambda m: setattr(self, 'scan', m), qos_profile_sensor_data)
        self.create_subscription(OccupancyGrid, '/map', self.on_map,
                                 QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
        self.pub = self.create_publisher(String, '/place/status', 10)
        self.create_subscription(String, '/place/command', self.on_command, 10)
        self.ac = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.cancel_all = self.create_client(CancelGoal, '/navigate_to_pose/_action/cancel_goal')
        self.goal = None   # 진행 중: {'id','place','x','y','yaw','mode','handle','t0'}
        self.py = None
        self.start_path_yaw()
        self.create_timer(0.2, self.tick)
        self.get_logger().info('장소 %d 곳 적재(%s) · home=%s · dry_run=%s' % (len(self.reg['places']), self.reg.get('map', '?'), self.reg.get('home'), self.p('dry_run')))

    def p(self, k): return self.get_parameter(k).value

    # ---------- 등록부 ----------
    def load_places(self):
        with open(self.p('places_file'), encoding='utf-8') as f:
            d = yaml.safe_load(f)
        names = {}
        for pl in d['places']:
            for nm in [pl['name']] + list(pl.get('aliases') or []):
                key = self.norm(str(nm))
                if key in names and names[key] is not pl:
                    raise RuntimeError('이름 겹침: %s' % nm)   # 등록부 오류는 기동 단계에서 막는다
                names[key] = pl
        d['_names'] = names
        return d

    @staticmethod
    def norm(s): return ''.join(s.split()).lower()

    def resolve(self, name):
        return self.reg['_names'].get(self.norm(name))

    # ---------- 경로 끝 방향(별도 상주 프로세스) ----------
    def start_path_yaw(self):
        scr = self.p('path_yaw_script') or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'path_end_yaw.py')
        try:
            self.py = subprocess.Popen(['python3', '-u', scr, '--serve'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, bufsize=1)
            ok = bool(select.select([self.py.stdout], [], [], 15)[0]) and self.py.stdout.readline().strip() == 'READY'
            if not ok: self.py.kill(); self.py = None
        except Exception as e:
            self.get_logger().warn('경로 방향 조회기 기동 실패: %s' % e); self.py = None
        self.get_logger().info('경로 방향 조회기: %s' % ('준비됨' if self.py else '없음 — 직선 방향 사용'))

    def path_yaw(self, gx, gy, fb):
        if self.py is None or self.py.poll() is not None: return fb, '조회기 없음 → 직선 방향'
        try:
            self.py.stdin.write('%.4f %.4f %.6f\n' % (gx, gy, fb)); self.py.stdin.flush(); te = time.time() + 20
            while time.time() < te:
                if select.select([self.py.stdout], [], [], 0.2)[0]:
                    l = self.py.stdout.readline().strip()
                    if l.startswith('YAW'): return float(l.split()[1]), '경로 끝 방향(%s 점)' % l.split()[2]
                    if l.startswith('FAIL'): return fb, l + ' → 직선 방향'
            return fb, '조회 시간 초과 → 직선 방향'
        except Exception as e:
            return fb, '조회 오류 %s → 직선 방향' % e

    # ---------- 도우미 ----------
    def say(self, rid, state, place=None, detail=''):
        m = String(); m.data = json.dumps({'id': rid, 'state': state, 'place': place, 'detail': detail}, ensure_ascii=False)
        self.pub.publish(m); self.get_logger().info('[%s] %s %s %s' % (rid, state, place or '', detail))

    def pose(self):
        try:
            t = self.buf.lookup_transform('map', 'base_link', rclpy.time.Time()).transform
            return t.translation.x, t.translation.y, yaw_of(t.rotation)
        except Exception:
            return None

    def clearance(self, gx, gy, gth):
        g = self.gcm
        if g is None: return None
        d = np.array(g.data, dtype=np.int16).reshape(g.info.height, g.info.width); jj, ii = np.where(d >= 100)
        if not len(ii): return 9.9
        X = g.info.origin.position.x + (ii + .5) * g.info.resolution - gx; Y = g.info.origin.position.y + (jj + .5) * g.info.resolution - gy
        lx = X * math.cos(gth) + Y * math.sin(gth); ly = -X * math.sin(gth) + Y * math.cos(gth)
        return float(np.min(np.hypot(np.maximum(np.abs(lx) - HL, 0), np.maximum(np.abs(ly) - HW, 0))))

    # ---------- 출발 전 위치 추정 검사(10-29 §2) ----------
    def on_map(self, m):
        from scipy.ndimage import binary_dilation
        g = np.array(m.data, dtype=np.int16).reshape(m.info.height, m.info.width) >= 65
        self.occ = (binary_dilation(g, iterations=1), m.info)

    def loc_align(self):
        """(s0, sb, db°) 또는 (None, 이유). s0 = 지금 TF 점수, sb · db = ±30° 0.5° 훑은 최고 점수와 그 각.
        정의는 Docs/debug_log/2026-10-28/jobs/chk_scan_align.py · 2026-10-29/jobs/anal_scan_align_bag.py 와 같음(점 ≤ 6 m)."""
        sc, oc = self.scan, self.occ
        if sc is None or oc is None: return None, '라이다 또는 정적 지도 없음'
        if time.time() - (sc.header.stamp.sec + sc.header.stamp.nanosec * 1e-9) > 2.0: return None, '라이다 2 s 넘게 끊김'
        try: t = self.buf.lookup_transform('map', sc.header.frame_id, rclpy.time.Time()).transform
        except Exception: return None, 'TF(map→라이다) 없음'
        G, i = oc; lx, ly, la = t.translation.x, t.translation.y, yaw_of(t.rotation)
        r = np.array(sc.ranges, np.float32); a = sc.angle_min + sc.angle_increment * np.arange(len(r))
        ok = np.isfinite(r) & (r > sc.range_min) & (r < min(sc.range_max, 6.0)); r, a = r[ok], a[ok]
        if len(r) < 50: return None, '라이다 점 %d 개뿐' % len(r)
        def score(d):
            x = lx + r * np.cos(la + d + a); y = ly + r * np.sin(la + d + a)
            J = ((y - i.origin.position.y) / i.resolution).astype(int); I = ((x - i.origin.position.x) / i.resolution).astype(int)
            v = (J >= 0) & (J < G.shape[0]) & (I >= 0) & (I < G.shape[1]); return float(G[J[v], I[v]].mean()) if v.any() else 0.0
        D = np.arange(-30, 30.25, 0.5); S = np.array([score(math.radians(d)) for d in D]); k = int(np.argmax(S))
        return (S[len(D) // 2], float(S[k]), float(D[k])), ''

    def loc_ok(self):
        """(통과?, 설명). 문턱 근거 10-29 §2: 위치 추정이 맞던 5 주행 570 판 — 점수 최소 0.594 · 주행 중 최적 각 ≤ 3.0° ·
        출발점 prep 직후 0.92~0.93 / 틀린 상태: 10-28 16:15 0.140 · −32.5°, f2pl1 출발 직전 0.71 · −7°(최적 각에서 +0.10)."""
        if not self.p('loc_check'): return True, '위치 검사 끔'
        res, why = self.loc_align()
        if res is None: return False, '위치 검사 못 함: ' + why
        s0, sb, db = res; txt = '라이다↔지도 %.2f · 최적 각 %+.1f° (%.2f)' % (s0, db, sb)
        if s0 < self.p('loc_min_score'): return False, txt + ' — 점수 낮음, 위치 추정이 틀렸을 수 있음(prep 필요)'
        if abs(db) > self.p('loc_max_yaw') and sb - s0 >= self.p('loc_min_gain'):
            return False, txt + ' — 방향 추정 약 %.0f° 틀림(prep 필요)' % -db
        return True, txt

    # ---------- 명령 ----------
    def on_command(self, msg):
        s = msg.data.strip(); rid = ''
        if '|' in s: rid, s = s.split('|', 1)
        parts = s.split(None, 1); cmd = parts[0].lower() if parts else ''; arg = parts[1].strip() if len(parts) > 1 else ''
        if cmd == 'stop': return self.do_stop(rid)
        if cmd == 'list':
            return self.say(rid, 'info', None, ' · '.join('%s(%s)' % (p['name'], ', '.join(p.get('aliases') or [])) for p in self.reg['places']))
        if cmd == 'where':
            P = self.pose(); ok, lw = self.loc_ok()
            return self.say(rid, 'info', None, ('map (%.2f, %.2f, %.0f°)' % (P[0], P[1], math.degrees(P[2])) if P else 'TF 없음') + ' · ' + lw)
        if cmd == 'return': arg, cmd = self.reg.get('home', ''), 'go_to'
        if cmd != 'go_to': return self.say(rid, 'rejected', None, '모르는 명령: %s' % s)
        if self.goal is not None:
            return self.say(rid, 'rejected', arg, '이동 중(%s) — 먼저 stop' % self.goal['place'])
        pl = self.resolve(arg)
        if pl is None: return self.say(rid, 'rejected', arg, '등록되지 않은 장소')
        self.do_go(rid, pl)

    def do_go(self, rid, pl):
        P = self.pose()
        if P is None: return self.say(rid, 'rejected', pl['name'], 'TF(map→base_link) 없음')
        lok, lw = self.loc_ok()
        if not lok: return self.say(rid, 'rejected', pl['name'], lw)
        gx, gy = float(pl['x']), float(pl['y']); fb = math.atan2(gy - P[1], gx - P[0]); mode = str(pl.get('yaw_mode', 'p'))
        if math.hypot(gx - P[0], gy - P[1]) < self.p('xy_done'):
            return self.say(rid, 'arrived', pl['name'], '이미 그 자리(%.2f m)' % math.hypot(gx - P[0], gy - P[1]))
        if mode in ('p', 'f'): gth, why = self.path_yaw(gx, gy, fb)
        else: gth, why = math.radians(float(mode)), '고정 방향'
        c = self.clearance(gx, gy, gth)
        mc = float(pl['min_clear']) if 'min_clear' in pl else self.p('min_clear')   # 장소별 기준(등록부에 근거와 함께) — 10-28 §7 남서
        if c is None: return self.say(rid, 'rejected', pl['name'], '전역 코스트맵 없음')
        if c < mc and mode != 'f' and not mode.lstrip('-').replace('.', '').isdigit():
            # 10-28 §8: 경로 끝 방향이 좁은 곳에 비스듬히 들어가면(통로 북쪽 −51°) 그 자세 그대로는 차체가 옆 치명 칸에 겹친다.
            # no5 에서는 같은 목표(−55~−64°)를 Nav2 가 받아 로버가 통로 축 쪽(−74~−87°)으로 서서 끝냈음(f2tt2 등 4 회).
            # → 경로 끝 방향에서 가장 가까운, 여유 기준을 넘는 방향으로 고쳐 보낸다(±45° 안, 5° 간격). 못 찾으면 거절.
            # TODO(improve): ±45° · 5° 는 통로 북쪽 한 사례로 정한 값 — 다른 좁은 곳이 생기면 다시 본다
            for k in range(1, 10):
                cand = [(self.clearance(gx, gy, gth + s * math.radians(5 * k)), gth + s * math.radians(5 * k)) for s in (-1, 1)]
                cc, ct = max(cand)
                if cc >= mc:
                    why += ' → 여유 위해 %+.0f° 고침(원래 여유 %.3f)' % (math.degrees(ct - gth), c); c, gth = cc, math.atan2(math.sin(ct), math.cos(ct)); break
        if c < mc: return self.say(rid, 'rejected', pl['name'], '목표 여유 %.3f m < %.2f · 방향 %.0f° %s' % (c, mc, math.degrees(gth), why))   # 10-28 §8: 거절 때도 방향을 남김(f2pl1 은 방향 기록 없어 재현 필요했음)
        info = '목표 (%.2f, %.2f, %.0f°) %s · 여유 %.2f m · 거리 %.2f m · %s' % (gx, gy, math.degrees(gth), why, c, math.hypot(gx - P[0], gy - P[1]), lw)
        if self.p('dry_run'): return self.say(rid, 'checked', pl['name'], '[dry_run — 보내지 않음] ' + info)   # checked = 검사 통과 · 목표 안 보냄(끝 상태)
        if not self.ac.wait_for_server(timeout_sec=3): return self.say(rid, 'rejected', pl['name'], 'navigate_to_pose 서버 없음')
        g = NavigateToPose.Goal(); g.pose.header.frame_id = 'map'; g.pose.header.stamp = self.get_clock().now().to_msg()
        g.pose.pose.position.x, g.pose.pose.position.y = gx, gy; g.pose.pose.orientation.z, g.pose.pose.orientation.w = math.sin(gth / 2), math.cos(gth / 2)
        self.goal = {'id': rid, 'place': pl['name'], 'x': gx, 'y': gy, 'yaw': gth, 'mode': mode, 'handle': None, 't0': time.time()}
        f = self.ac.send_goal_async(g); f.add_done_callback(self.on_accept)
        self.say(rid, 'accepted', pl['name'], info)

    def on_accept(self, f):
        gh = f.result()
        if self.goal is None: return
        if gh is None or not gh.accepted:
            rid, nm = self.goal['id'], self.goal['place']; self.goal = None; return self.say(rid, 'failed', nm, 'Nav2 가 목표 거부')
        self.goal['handle'] = gh; self.say(self.goal['id'], 'moving', self.goal['place'])
        gh.get_result_async().add_done_callback(self.on_result)

    def on_result(self, f):
        if self.goal is None: return
        st = f.result().status; rid, nm, t0 = self.goal['id'], self.goal['place'], self.goal['t0']
        if self.goal.get('xy_done'): return   # f 모드에서 이미 arrived_xy 로 끝냄
        self.goal = None
        self.say(rid, {4: 'arrived', 5: 'canceled', 6: 'failed'}.get(st, 'failed'), nm, '상태 %d · %.1f s' % (st, time.time() - t0))

    def tick(self):
        g = self.goal
        if g is None or g['mode'] != 'f' or g['handle'] is None or g.get('xy_done'): return
        P = self.pose()
        if P and math.hypot(g['x'] - P[0], g['y'] - P[1]) < self.p('xy_done'):   # 위치만 목표: 방향 맞춤 없이 끝(10-07 §7)
            g['xy_done'] = True; g['handle'].cancel_goal_async()
            self.say(g['id'], 'arrived', g['place'], '위치 도착(xy %.2f m, 방향 맞춤 생략) · %.1f s' % (math.hypot(g['x'] - P[0], g['y'] - P[1]), time.time() - g['t0']))
            self.goal = None

    def do_stop(self, rid):
        nm = self.goal['place'] if self.goal else None
        if self.cancel_all.wait_for_service(timeout_sec=1.0):
            self.cancel_all.call_async(CancelGoal.Request())   # 빈 요청 = 모든 목표(nav_guard 와 같은 방식)
        if self.goal and self.goal.get('handle'): self.goal['handle'].cancel_goal_async()
        if self.goal:   # 진행 중이던 이동 명령에도 끝 상태를 알림(그 명령을 기다리는 쪽이 멈추지 않게)
            self.say(self.goal['id'], 'canceled', nm, 'stop 으로 취소 · %.1f s' % (time.time() - self.goal['t0']))
        self.goal = None
        self.say(rid, 'canceled', nm, '정지 요청 — Nav2 목표 전부 취소')


def main():
    rclpy.init(); n = PlaceServer()
    try: rclpy.spin(n)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException): pass
    finally:
        try:
            if n.py and n.py.poll() is None: n.py.stdin.close(); n.py.wait(timeout=3)
        except Exception: pass
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
