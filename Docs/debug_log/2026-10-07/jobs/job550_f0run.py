#!/usr/bin/env python3
"""F0 코스 확장 러너 (2026-09-23): 상자 코스와 무관한 연속 목표 주행 + 왕복 복귀 오차 계측.
  사용: python3 job550_f0run.py NAME "x1,y1,yaw1_deg;x2,y2,yaw2_deg;..." [SPEED=0.07]
    목표는 **출발 자세 기준**(출발 base_link: +x 앞, +y 왼쪽, yaw 도) — 러너가 시작 시 map 자세를 읽어 map 좌표로 바꾼다.
    예) 5 m 가서 돌아 출발점에 뒤돌아 서기: "5.0,0,180;0,0,180"
    yaw 자리에 a = 자동(09-28 §12, A1): 직전 지점 → 목표의 진행 방향을 목표 자세로 준다 = 도착 뒤 자세 맞춤 제자리 회전을 요구하지 않음.
    yaw 자리에 p = 경로 자동(09-28 §16, A1 개선): 목표를 보내기 직전 planner(compute_path_to_pose)로 경로를 받아
      **경로 끝 0.3 m 의 진행 방향**을 목표 자세로 준다 — a 는 상자 우회처럼 경로가 휘면 실제 접근 방향과 15~40° 어긋났다(f0a3 §14·§15).
      경로를 못 받으면 a 방식으로 떨어진다.
    yaw 자리에 f = 위치만(10-07 §7, 사용자: '방향을 크게 바꾸라는 명령 제거'): p 처럼 경로 끝 방향으로 보내되, map 위치가 목표 XY_DONE(0.15 m,
      = xy_goal_tolerance) 안에 들어오면 러너가 목표를 취소하고 SUCCEEDED_XY 로 친다 — 도착 뒤 방향 맞춤 제자리 회전을 하지 않음
      (남서 구석에서 방향 맞추다 정체 3/3: 10-02 f2b3·10-07 f2c1·f2d1).
      예) "2.3,0,a;0,0,a" — 목표 1 은 앞을 본 채 도착, 목표 2 는 복귀 방향을 본 채 도착(방향 전환은 목표 2 경로를 따라가며 MPPI 가 한다).
  동작: 목표를 하나씩 NavigateToPose 로 보냄(이전 목표 SUCCEEDED 뒤 다음), 목표별 한도 = 경로 길이/SPEED × 2 + 30 s(초과 시 취소·중단).
  기록(/tmp/<NAME>.csv, 10 Hz): t, 목표 번호, map x·y·yaw, odom x·y·yaw(EKF), 휠 yaw(/wheel_odom), 지령 v·ω, map→odom x·y·yaw, stuck 여부
  요약: 목표별 결과·소요, **복귀 오차**(마지막 목표 대비 map 위치·yaw, 출발 대비), map→odom 누적 보정량(= 오도메트리 드리프트의 SLAM 추정),
        휠 오도 vs EKF 누적 yaw 차(미끄러짐 흔적), stuck 진단 수.
  한계: map 좌표 복귀 오차는 SLAM 자체 오차를 포함 — 물리 복귀 오차는 사용자가 출발 테이프 기준으로 줄자로 잰다(정답).
"""
import sys, math, time, csv
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.qos import qos_profile_sensor_data
from nav2_msgs.action import NavigateToPose, ComputePathToPose
from geometry_msgs.msg import PoseStamped, Twist
from nav_msgs.msg import Odometry
from diagnostic_msgs.msg import DiagnosticArray
import tf2_ros

NAME = sys.argv[1]
GOALS = [tuple(float(v) if (j < 2 or v.strip() not in ('a', 'p', 'f')) else v.strip() for j, v in enumerate(g.split(','))) for g in sys.argv[2].split(';') if g.strip()]   # yaw 'a' = 직선 자동, 'p' = 경로 끝 자동
SPEED = float(sys.argv[3]) if len(sys.argv) > 3 else 0.07
XY_DONE = 0.15   # 'f' 목표의 위치 도달 판정(m) = nav2 xy_goal_tolerance
PAUSE = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0   # 목표 사이 정지 시간(s)


def yaw_of(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi


class F0(Node):
    def __init__(self):
        super().__init__('f0run550')
        self.buf = tf2_ros.Buffer(); self.tl = tf2_ros.TransformListener(self.buf, self)
        self.ac = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.pc = ActionClient(self, ComputePathToPose, 'compute_path_to_pose')
        self.cmd = (0.0, 0.0); self.wyaw = None; self.stuck = 0; self.stuck_now = 0
        self.create_subscription(Twist, '/cmd_vel', lambda m: setattr(self, 'cmd', (m.linear.x, m.angular.z)), 10)
        self.create_subscription(Odometry, '/wheel_odom', lambda m: setattr(self, 'wyaw', yaw_of(m.pose.pose.orientation)), qos_profile_sensor_data)
        self.create_subscription(DiagnosticArray, '/rover/stuck', self.cb_stuck, 10)

    def cb_stuck(self, m):
        lv = max((ord(s.level) if isinstance(s.level, (bytes, bytearray)) else int(s.level)) for s in m.status) if m.status else 0
        self.stuck_now = lv
        if lv >= 1: self.stuck += 1

    def tf(self, a, b):
        try:
            t = self.buf.lookup_transform(a, b, rclpy.time.Time()).transform
            return (t.translation.x, t.translation.y, yaw_of(t.rotation))
        except Exception:
            return None


def path_end_yaw(n, gx, gy, fallback):
    """경로 끝 0.3 m 의 진행 방향. 09-28 §20: 같은 노드에서 compute_path_to_pose 를 부르면 뒤이은 navigate_to_pose 응답이
    오지 않아 러너가 멈췄다(f0a5 1 차, 로버 정지 상태) → **별도 프로세스(job613)** 로 조회. 실패하면 fallback."""
    import subprocess
    try:
        r = subprocess.run(['python3', '/tmp/job613_pathyaw.py', '%.4f' % gx, '%.4f' % gy, '%.6f' % fallback], capture_output=True, text=True, timeout=20)
        last = [l for l in r.stdout.splitlines() if l.startswith(('YAW', 'FAIL'))][-1]
    except Exception as e:
        last = 'FAIL %s' % e
    if last.startswith('YAW'):
        _, yaw, npts, seg = last.split(); yaw = float(yaw)
        print('  경로 자동 yaw: 경로 %s 점, 끝 %s m 구간 방향 %.1f° (직선 방향 %.1f°, 차 %.1f°)' % (npts, seg, math.degrees(yaw), math.degrees(fallback), math.degrees(uw(yaw - fallback))), flush=True)
        return yaw
    print('  경로 자동 yaw: %s → 직선 방향 사용' % last, flush=True)
    return fallback


def main():
    rclpy.init(); n = F0()
    t0 = time.time()
    while time.time() - t0 < 15 and (n.tf('map', 'base_link') is None or n.tf('odom', 'base_link') is None or n.wyaw is None):
        rclpy.spin_once(n, timeout_sec=0.1)
    S = n.tf('map', 'base_link'); O0 = n.tf('odom', 'base_link'); MO0 = n.tf('map', 'odom'); W0 = n.wyaw
    if S is None or O0 is None:
        print('TF 없음 — 중단'); return 2
    if not n.ac.wait_for_server(timeout_sec=10):
        print('navigate_to_pose 서버 없음 — 중단'); return 2
    # 10-01 §8.19: GOAL_FRAME=map 이면 목표를 지도 절대 좌표로(기본 = 출발 자세 기준). 출발 테이프(원점·방향 0)에서 출발하면 둘이 같지만,
    #   다른 자리에서 이어 달릴 때 기본값이면 목표가 출발 자세만큼 돌고 옮겨진다(f2a7: D (1.6, −5.55) → 지도 (0.55, 3.33) 로 감).
    import os
    absf = os.environ.get('GOAL_FRAME', 'start') == 'map'
    B = (0.0, 0.0, 0.0) if absf else S
    c, s = math.cos(B[2]), math.sin(B[2])
    mgoals = []; px, py = S[0], S[1]
    for gx, gy, gyaw in GOALS:
        mx, my = B[0] + gx * c - gy * s, B[1] + gx * s + gy * c
        th = math.atan2(my - py, mx - px) if isinstance(gyaw, str) else uw(B[2] + math.radians(gyaw))   # 'a'·'p' 의 초기값 = 직선 진행 방향('p' 는 보내기 직전 경로로 교체)
        mgoals.append((mx, my, th, gyaw in ('p', 'f'), gyaw == 'f')); px, py = mx, my
    print('출발 map (%.3f, %.3f, %.1f°) | 목표 %d 개(%s 기준, a = 직선 자동, p = 경로 끝 자동): %s → map yaw(초기) %s' % (S[0], S[1], math.degrees(S[2]), len(GOALS), '지도 절대' if absf else '출발', GOALS, ['%.0f°' % math.degrees(g[2]) for g in mgoals]), flush=True)
    rows = []; res = []; prev = (S[0], S[1]); wacc = 0.0; eacc = 0.0; lw = W0; le = O0[2]
    tstart = time.time()
    for i, (gx, gy, gyaw, from_path, free) in enumerate(mgoals):
        dist = math.hypot(gx - prev[0], gy - prev[1]); lim = dist / SPEED * 2 + 30
        if from_path:
            gyaw = path_end_yaw(n, gx, gy, gyaw)
        g = NavigateToPose.Goal(); g.pose = PoseStamped(); g.pose.header.frame_id = 'map'; g.pose.header.stamp = n.get_clock().now().to_msg()
        g.pose.pose.position.x, g.pose.pose.position.y = gx, gy
        g.pose.pose.orientation.z, g.pose.pose.orientation.w = math.sin(gyaw / 2), math.cos(gyaw / 2)
        gh = None
        for attempt in range(2):   # 09-28 §20: 응답 대기에 시간 제한(무한 대기 사고) — 10 s 안에 응답 없으면 한 번 더 보낸다
            fut = n.ac.send_goal_async(g); tw = time.time()
            while not fut.done() and time.time() - tw < 10: rclpy.spin_once(n, timeout_sec=0.05)
            if fut.done(): gh = fut.result(); break
            print('  ★ 목표 %d 전송 응답 없음(10 s) — 재전송 %d' % (i + 1, attempt + 1), flush=True)
        if gh is None or not gh.accepted:
            print('목표 %d 거부 — 중단' % (i + 1)); res.append((i + 1, 'REJECTED', 0.0)); break
        rf = gh.get_result_async(); tg = time.time(); nxt = tg; xy_done = False
        print('목표 %d 출발: map (%.2f, %.2f, %.0f°), 거리 %.2f m, 한도 %.0f s' % (i + 1, gx, gy, math.degrees(gyaw), dist, lim), flush=True)
        while not rf.done():
            rclpy.spin_once(n, timeout_sec=0.02)
            now = time.time()
            if now - tg > lim:
                gh.cancel_goal_async(); print('  ★ 목표 %d 한도 초과 — 취소' % (i + 1)); break
            if now >= nxt:
                nxt += 0.1
                M = n.tf('map', 'base_link'); OB = n.tf('odom', 'base_link'); MO = n.tf('map', 'odom')
                if M and OB and MO and n.wyaw is not None:
                    wacc += uw(n.wyaw - lw); eacc += uw(OB[2] - le); lw = n.wyaw; le = OB[2]
                    if free and math.hypot(M[0] - gx, M[1] - gy) <= XY_DONE:
                        gh.cancel_goal_async(); xy_done = True; print('  목표 %d 위치 도달(%.3f m ≤ %.2f) — 방향 맞춤 없이 끝냄' % (i + 1, math.hypot(M[0] - gx, M[1] - gy), XY_DONE), flush=True); break
                    rows.append((round(now - tstart, 2), i + 1, M[0], M[1], math.degrees(M[2]), OB[0], OB[1], math.degrees(OB[2]), math.degrees(n.wyaw), n.cmd[0], n.cmd[1], MO[0], MO[1], math.degrees(MO[2]), n.stuck_now))
        st = rf.result().status if rf.done() else 5
        name = 'SUCCEEDED_XY' if xy_done else {4: 'SUCCEEDED', 5: 'CANCELED', 6: 'ABORTED'}.get(st, str(st))
        res.append((i + 1, name, time.time() - tg)); prev = (gx, gy)
        M = n.tf('map', 'base_link')
        if M: print('  목표 %d %s %.1f s | 도착 map (%.3f, %.3f, %.1f°) 목표 대비 %.3f m, %.1f°' % (i + 1, name, time.time() - tg, M[0], M[1], math.degrees(M[2]), math.hypot(M[0] - gx, M[1] - gy), math.degrees(uw(M[2] - gyaw))), flush=True)
        if xy_done:   # 취소 응답을 받아 두어야 다음 목표가 깔끔히 시작됨
            tw = time.time()
            while not rf.done() and time.time() - tw < 5: rclpy.spin_once(n, timeout_sec=0.05)
        if not name.startswith('SUCCEEDED'): break
        if i + 1 < len(mgoals) and PAUSE > 0:   # 09-23 사용자 제안: 도착 자세로 멈춘 뒤 복귀(SLAM·지도 안정 시간)
            tp = time.time()
            while time.time() - tp < PAUSE: rclpy.spin_once(n, timeout_sec=0.05)
            print('  정지 %.1f s 뒤 다음 목표' % PAUSE, flush=True)
    with open('/tmp/%s.csv' % NAME, 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['t', 'goal', 'map_x', 'map_y', 'map_yaw', 'odom_x', 'odom_y', 'odom_yaw', 'wheel_yaw', 'v', 'w', 'mo_x', 'mo_y', 'mo_yaw', 'stuck']); w.writerows(rows)
    M = n.tf('map', 'base_link'); MO = n.tf('map', 'odom')
    print('\n결과: %s | 총 %.1f s' % (' / '.join('%d %s %.1fs' % r for r in res), time.time() - tstart))
    if M:
        print('  출발 대비 최종 map: Δ(%.3f, %.3f) m = %.3f m, Δyaw %.1f° | 마지막 목표 대비 %.3f m' % (M[0] - S[0], M[1] - S[1], math.hypot(M[0] - S[0], M[1] - S[1]), math.degrees(uw(M[2] - S[2])), math.hypot(M[0] - mgoals[-1][0], M[1] - mgoals[-1][1])))
    if MO and MO0:
        print('  map→odom 누적 보정(SLAM 이 본 오도메트리 드리프트): Δ(%.3f, %.3f) m, Δyaw %.2f°' % (MO[0] - MO0[0], MO[1] - MO0[1], math.degrees(uw(MO[2] - MO0[2]))))
    print('  누적 회전: 휠 %.1f° vs EKF %.1f° (차 %.1f° = 미끄러짐·스크럽 흔적) | stuck 진단 %d 회' % (math.degrees(wacc), math.degrees(eacc), math.degrees(wacc - eacc), n.stuck))
    print('  물리 복귀 오차는 줄자로: 출발 테이프 기준 앞·뒤·좌우 편차(마지막 목표 yaw 180° 면 **뒤끝**이 테이프 선에 와야 함)')
    rclpy.shutdown(); return 0


if __name__ == '__main__':
    sys.exit(main())
