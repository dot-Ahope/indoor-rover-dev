#!/usr/bin/env python3
"""pad_relief — 컨트롤러가 '후보 궤적 전부 충돌'로 갇혔을 때만 로컬 코스트맵 footprint_padding 을 잠깐 0 으로 내렸다가 되돌린다.
(2026-10-14, Docs/debug_log/2026-10-14/SUMMARY.md §8. 근거 10-13 §5.4·§8·§14.2, 10-14 §2·§7)

왜 필요한가
  Nav2 의 풋프린트 충돌 검사는 칸(5 cm) 단위라, 코스트맵상 여유가 한 칸 안으로 줄면 '현재 자세부터 충돌'로 본다.
  그러면 MPPI 의 후보가 전부 충돌이 되어 명령이 0 이 되고, 후진 복구도 같은 검사에 걸려 거부된다 — 실제로는 11 cm 가 남아 있어도
  빠져나올 수단이 없다(10-13 f2o1·f2p1). 패딩 1 cm 를 잠깐 내주면 검사 기준이 1 cm 물러나 다시 움직일 수 있다
  (시뮬: 실제 정지 자세 2 곳 × 5 씨앗 모두 통과, 0.15 m 뒤 되돌려도 다시 갇히지 않음).
  평소 주행은 패딩 0.01 그대로다 — '늘 더 붙어서 가는 것'이 아니라 갇힌 뒤의 탈출 수단이다(사용자 방침 10-13).

판정·조치
  켜기: controller_server 의 로그(/rosout)에 "fail to compute path" 가 trig_win(3 s) 안에 trig_n(3)회 → 로컬 코스트맵 footprint_padding = relief(0.0).
  끄기: 켠 뒤 로버가 restore_dist(0.15 m) 움직였거나(/odometry/filtered) max_hold(15 s)가 지나면 원래 값으로.
        되돌린 뒤 cooldown(3 s) 동안은 다시 켜지 않는다. 60 s 안에 max_per_min(4)회를 넘으면 더 켜지 않는다(장애물 쪽으로 조금씩 파고드는 것 방지).
  종료할 때(Ctrl-C·SIGTERM)도 원래 값으로 되돌린다.
  mode: on = 실제로 바꿈 | shadow = 판정과 로그만(값은 안 바꿈).
기록: 로그 + /rover/pad_relief 진단(WARN = 내린 상태) + log_path(기본 /tmp/pad_relief.log)에 한 줄씩.

// TODO(improve): 켜는 신호를 로그 문자열에서 읽는다(Nav2 Humble 의 문구에 묶임). FollowPath 액션 결과나 컨트롤러 진단 토픽이 있으면 그쪽으로.
// TODO(improve): 전역 코스트맵 패딩은 건드리지 않는다(계획기·스무더는 그대로) — 필요가 확인되면 추가.
"""
import math, time, signal
import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import Log, Parameter, ParameterValue, ParameterType
from rcl_interfaces.srv import SetParameters, GetParameters
from nav_msgs.msg import Odometry
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue


class PadRelief(Node):
    def __init__(self):
        super().__init__('pad_relief')
        for k, v in (('mode', 'on'), ('costmap_node', '/local_costmap/local_costmap'), ('relief', 0.0), ('trig_n', 3), ('trig_win', 3.0),
                     ('restore_dist', 0.15), ('max_hold', 15.0), ('cooldown', 3.0), ('max_per_min', 4),
                     ('fail_text', 'fail to compute path'), ('fail_node', 'controller_server'), ('log_path', '/tmp/pad_relief.log')):
            self.declare_parameter(k, v)
        g = lambda k: self.get_parameter(k).value
        self.mode = str(g('mode')); self.relief = float(g('relief')); self.trig_n = int(g('trig_n')); self.trig_win = float(g('trig_win'))
        self.restore_dist = float(g('restore_dist')); self.max_hold = float(g('max_hold')); self.cooldown = float(g('cooldown')); self.max_per_min = int(g('max_per_min'))
        self.fail_text = str(g('fail_text')); self.fail_node = str(g('fail_node')); self.log_path = str(g('log_path'))
        cm = str(g('costmap_node'))
        self.set_cli = self.create_client(SetParameters, cm + '/set_parameters'); self.get_cli = self.create_client(GetParameters, cm + '/get_parameters')
        self.nominal = None          # 원래 패딩(기동 때 읽음) — 읽기 전에는 아무것도 하지 않는다
        self.active = False; self.t_on = 0.0; self.p_on = None; self.t_off = 0.0; self.fails = []; self.events = []; self.pose = None; self.n_on = 0
        self.create_subscription(Log, '/rosout', self.cb_log, 100)
        self.create_subscription(Odometry, '/odometry/filtered', self.cb_odom, 10)
        self.diag = self.create_publisher(DiagnosticArray, '/rover/pad_relief', 5)
        self.create_timer(0.2, self.tick); self.create_timer(1.0, self.read_nominal)
        self.note('시작 mode=%s · 켜기 %d 회/%.0f s · 끄기 %.2f m 또는 %.0f s · 분당 최대 %d 회' % (self.mode, self.trig_n, self.trig_win, self.restore_dist, self.max_hold, self.max_per_min))

    def note(self, s):
        self.get_logger().info(s)
        try:
            with open(self.log_path, 'a') as f: f.write('%.2f %s %s\n' % (time.time(), time.strftime('%H:%M:%S'), s))
        except OSError:
            pass

    def read_nominal(self):
        if self.nominal is not None or not self.get_cli.service_is_ready(): return
        fut = self.get_cli.call_async(GetParameters.Request(names=['footprint_padding']))
        def done(f):
            r = f.result()
            if r is None or not r.values or self.nominal is not None: return
            v = r.values[0].double_value
            if abs(v - self.relief) < 1e-9:   # 이전 실행이 내린 채 죽었을 가능성 — 원래 값을 알 수 없으므로 켜지 않고 알린다
                self.note('⚠ 기동 때 패딩이 이미 %.3f(내린 값) — 원래 값을 모름, 동작 안 함. 스택을 다시 띄울 것' % v); self.mode = 'off'; self.nominal = v; return
            self.nominal = v; self.note('원래 패딩 %.3f 확인' % v)
        fut.add_done_callback(done)

    def cb_odom(self, m): self.pose = (m.pose.pose.position.x, m.pose.pose.position.y)

    def cb_log(self, m):
        if self.fail_node in m.name and self.fail_text in m.msg: self.fails.append(time.time())

    def set_padding(self, v, why):
        if self.mode != 'on': self.note('[%s] 패딩 %.3f 로 바꿀 상황(%s) — 값은 안 바꿈' % (self.mode, v, why)); return
        fut = self.set_cli.call_async(SetParameters.Request(parameters=[Parameter(name='footprint_padding', value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=float(v)))]))
        def done(f):
            r = f.result(); ok = r is not None and r.results and r.results[0].successful
            self.note('패딩 → %.3f (%s) %s' % (v, why, '적용' if ok else '실패: ' + (r.results[0].reason if r is not None and r.results else '응답 없음')))
        fut.add_done_callback(done)

    def tick(self):
        now = time.time(); self.fails = [t for t in self.fails if now - t <= self.trig_win]; self.events = [t for t in self.events if now - t <= 60.0]
        if self.nominal is None or self.mode == 'off': return
        if not self.active:
            if len(self.fails) >= self.trig_n and now - self.t_off >= self.cooldown:
                if len(self.events) >= self.max_per_min:
                    if not getattr(self, '_capped', False): self.note('⚠ 60 s 안에 %d 회 — 더 내리지 않음(장애물 쪽으로 파고드는 것 방지)' % len(self.events)); self._capped = True
                else:
                    self._capped = False; self.active = True; self.t_on = now; self.p_on = self.pose; self.events.append(now); self.n_on += 1; self.fails = []
                    self.set_padding(self.relief, '후보 전부 충돌 %d 회/%.0f s, %d 번째' % (self.trig_n, self.trig_win, self.n_on))
        else:
            moved = math.hypot(self.pose[0] - self.p_on[0], self.pose[1] - self.p_on[1]) if (self.pose and self.p_on) else 0.0
            if moved >= self.restore_dist or now - self.t_on >= self.max_hold:
                self.active = False; self.t_off = now; self.fails = []
                self.set_padding(self.nominal, '%.2f m 이동' % moved if moved >= self.restore_dist else '시간 한도 %.0f s(이동 %.2f m)' % (self.max_hold, moved))
        st = DiagnosticStatus(level=DiagnosticStatus.WARN if self.active else DiagnosticStatus.OK, name='pad_relief', message='패딩 내림' if self.active else '평상',
                              values=[KeyValue(key='mode', value=self.mode), KeyValue(key='count', value=str(self.n_on)), KeyValue(key='recent_fails', value=str(len(self.fails)))])
        msg = DiagnosticArray(); msg.header.stamp = self.get_clock().now().to_msg(); msg.status = [st]; self.diag.publish(msg)

    def restore_now(self):
        """종료 때: 내린 상태면 되돌리고 응답을 잠깐 기다린다."""
        if not (self.active and self.mode == 'on' and self.nominal is not None): return
        fut = self.set_cli.call_async(SetParameters.Request(parameters=[Parameter(name='footprint_padding', value=ParameterValue(type=ParameterType.PARAMETER_DOUBLE, double_value=float(self.nominal)))]))
        t = time.time()
        while not fut.done() and time.time() - t < 2.0: rclpy.spin_once(self, timeout_sec=0.05)
        self.active = False; self.note('종료 — 패딩 %.3f 로 되돌림(%s)' % (self.nominal, '적용' if fut.done() else '응답 없음'))


def main():
    rclpy.init(); n = PadRelief(); stop = {'f': False}
    for sg in (signal.SIGTERM, signal.SIGHUP):   # SIGHUP: 원격 접속이 끊겨 죽을 때도 패딩을 되돌린다(10-14 Wi-Fi 불안정 중 추가)
        signal.signal(sg, lambda *_: stop.update(f=True))
    try:
        while rclpy.ok() and not stop['f']: rclpy.spin_once(n, timeout_sec=0.1)
    except KeyboardInterrupt:
        pass
    finally:
        n.restore_now(); n.destroy_node()
        if rclpy.ok(): rclpy.shutdown()


if __name__ == '__main__':
    main()
