#!/usr/bin/env python3
"""nav_guard — Nav2 목표의 온보드 시간·무진행 한도 (2026-09-29, Docs/debug_log/2026-09-29/SUMMARY.md §13).

왜 필요한가
  목표 시간 한도가 PC 러너(job550)에만 있어 Wi-Fi 가 끊기면 사라진다. Nav2 자체에는 전체 시간 한도가 없고
  (BT 가 복구를 반복하며 오래 끌 수 있음), 진행 검사기(0.25 m / 25 s)는 Nav2 가 건강할 때만 작동한다.
  → Jetson 에서 Nav2 와 독립으로 돌며, 한도를 넘으면 모든 목표를 취소하고 정지 지령을 낸다.

판정 (NavigateToPose 피드백 기준, 목표마다)
  - 시간 한도: 시작 뒤 d0_window(10 s) 안의 남은 거리 최대값 d0 로 한도 = d0 / v_nominal × time_factor + time_margin
    (PC 러너와 같은 식: 0.07 m/s, ×2, +30 s). `time_limit_override` > 0 이면 그 값(시험용).
  - 무진행 한도: 로버 위치(피드백 current_pose)가 no_progress_s 동안 no_progress_m 넘게 움직이지 않음.
    Nav2 진행 검사기(0.25 m / 25 s)보다 느슨하게(0.25 m / 45 s) 두어 Nav2 가 건강하면 Nav2 가 먼저 처리한다.
조치: `/navigate_to_pose/_action/cancel_goal`(빈 요청 = 모든 목표) + `/cmd_vel` 0 을 20 Hz 로 1 s + `/rover/guard` 진단(ERROR).
파라미터는 매 틱 다시 읽는다 → `ros2 param set /nav_guard ...` 로 실행 중 바꿀 수 있다(시험 G1·G2).
"""
import math, time
import rclpy
import rclpy.executors
from rclpy.node import Node
from geometry_msgs.msg import Twist
from action_msgs.msg import GoalStatusArray
from action_msgs.srv import CancelGoal
from nav2_msgs.action import NavigateToPose
from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue

ACTIVE = (1, 2, 3)   # ACCEPTED, EXECUTING, CANCELING


class NavGuard(Node):
    def __init__(self):
        super().__init__('nav_guard')
        for k, v in (('enable', True), ('v_nominal', 0.07), ('time_factor', 2.0), ('time_margin', 30.0),
                     ('time_limit_override', 0.0), ('no_progress_s', 45.0), ('no_progress_m', 0.25), ('rate', 5.0),
                     ('d0_window', 10.0)):
            self.declare_parameter(k, v)
        self.goals = {}          # goal_id(bytes) → {'t0', 'd0', 'limit', 'hist': [(t, x, y)]}
        self.tripped = set()     # 개입한 목표 — 취소 뒤 늦게 온 피드백으로 다시 등록되지 않게(09-29 G1 에서 관찰)
        self.create_subscription(NavigateToPose.Impl.FeedbackMessage, '/navigate_to_pose/_action/feedback', self.cb_fb, 10)
        self.create_subscription(GoalStatusArray, '/navigate_to_pose/_action/status', self.cb_status, 10)
        self.cancel = self.create_client(CancelGoal, '/navigate_to_pose/_action/cancel_goal')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.diag_pub = self.create_publisher(DiagnosticArray, '/rover/guard', 5)
        self.stop_until = 0.0
        self.create_timer(1.0 / self.p('rate'), self.tick)
        self.create_timer(0.05, self.hold_stop)
        self.get_logger().info('nav_guard 시작 (시간 = d0/%.2f×%.1f+%.0f s, 무진행 %.2f m/%.0f s)'
                               % (self.p('v_nominal'), self.p('time_factor'), self.p('time_margin'), self.p('no_progress_m'), self.p('no_progress_s')))

    def p(self, k): return self.get_parameter(k).value

    def cb_fb(self, m):
        gid = bytes(m.goal_id.uuid); f = m.feedback; now = time.time()
        if gid in self.tripped: return
        pos = f.current_pose.pose.position
        g = self.goals.get(gid)
        if g is None:
            g = self.goals[gid] = {'t0': now, 'd0': None, 'limit': None, 'hist': []}
        # 2026-10-01 §8.13: d0 = 목표 시작 뒤 d0_window(10 s) 안에 본 남은 거리의 **최대값**.
        #   첫 피드백 하나로 잡으면 새 경로가 오기 전 bt_navigator 가 직전 목표의 경로로 계산한 값(B 도착 직후 0.14~0.15 m)이
        #   들어와, C(3.87 m) 목표 한도가 34 s 로 잡혀 정상 주행 중에 취소했다(f2a4·f2a5).
        if f.distance_remaining > 0.0 and now - g['t0'] <= self.p('d0_window') and (g['d0'] is None or f.distance_remaining > g['d0'] + 0.05):
            g['d0'] = f.distance_remaining
            g['limit'] = g['d0'] / self.p('v_nominal') * self.p('time_factor') + self.p('time_margin')
            self.get_logger().info('목표 %s: 남은 거리 %.2f m → 시간 한도 %.0f s (시작 뒤 %.1f s)' % (gid.hex()[:8], g['d0'], g['limit'], now - g['t0']))
        g['hist'].append((now, pos.x, pos.y))
        keep = now - self.p('no_progress_s') - 2.0
        g['hist'] = [h for h in g['hist'] if h[0] >= keep]

    def cb_status(self, m):
        live = {bytes(s.goal_info.goal_id.uuid) for s in m.status_list if s.status in ACTIVE}
        for gid in list(self.goals):
            if gid not in live: del self.goals[gid]

    def tick(self):
        if not self.p('enable'): return
        now = time.time()
        for gid, g in list(self.goals.items()):
            elapsed = now - g['t0']
            ov = self.p('time_limit_override')
            limit = ov if ov > 0 else g['limit']
            if limit is not None and elapsed > limit:
                self.trip('시간 한도 초과: %.0f s > %.0f s (남은 거리 시작 %.2f m)' % (elapsed, limit, g['d0'] or -1), gid); return
            ns = self.p('no_progress_s')
            if elapsed > ns and g['hist']:
                old = [h for h in g['hist'] if h[0] <= now - ns]
                if old:
                    a = old[-1]; b = g['hist'][-1]
                    moved = max(math.hypot(h[1] - a[1], h[2] - a[2]) for h in g['hist'] if h[0] >= a[0])
                    if moved < self.p('no_progress_m'):
                        self.trip('무진행: %.0f s 동안 최대 %.2f m 이동 < %.2f m' % (ns, moved, self.p('no_progress_m')), gid); return

    def trip(self, why, gid):
        self.get_logger().error('nav_guard 개입 — ' + why + ' → 모든 목표 취소·정지')
        da = DiagnosticArray(); da.header.stamp = self.get_clock().now().to_msg()
        st = DiagnosticStatus(level=DiagnosticStatus.ERROR, name='nav_guard', message=why, hardware_id='rover')
        st.values = [KeyValue(key='goal', value=gid.hex()[:8])]
        da.status.append(st); self.diag_pub.publish(da)
        if self.cancel.service_is_ready():
            self.cancel.call_async(CancelGoal.Request())      # 빈 요청 = 모든 목표 취소
        else:
            self.get_logger().error('cancel_goal 서비스 없음 — 정지 지령만 보냄')
        self.stop_until = time.time() + 1.0
        self.tripped.update(self.goals.keys()); self.goals.clear()

    def hold_stop(self):
        if time.time() < self.stop_until: self.cmd_pub.publish(Twist())


def main():
    rclpy.init(); n = NavGuard()
    try:
        rclpy.spin(n)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass   # launch 종료(SIGINT)·timeout(SIGTERM) 때 정상 종료
    finally:
        n.destroy_node()
        if rclpy.ok(): rclpy.shutdown()


if __name__ == '__main__':
    main()
