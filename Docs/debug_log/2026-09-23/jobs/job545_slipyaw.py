#!/usr/bin/env python3
"""목표 도착 뒤 제자리 회전 중 트랙 미끄러짐 검증 (09-23 n62b, 사용자 관찰): bag 에서 1 s 구간별로
   지령 ω(cmd_vel), 휠 오도 yaw 변화(/wheel_odom 자세), EKF yaw 변화(/odometry/filtered), SLAM(map) yaw 변화(map→odom ∘ odom→base_link),
   /rover/stuck 진단을 나란히 본다. 휠이 돌았는데 몸체가 안 돌았다면: 휠 yaw 는 변하고 SLAM yaw 는 거의 안 변한다. EKF 는 휠·자이로 융합값.
   인자: BAG [START_S=주행 끝 12 s 전]"""
import sys, math, bisect
import rosbag2_py
from rclpy.serialization import deserialize_message
from rosidl_runtime_py.utilities import get_message
BAG = sys.argv[1]
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri=BAG, storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
types = {t.name: t.type for t in r.get_all_topics_and_types()}
want = ['/cmd_vel', '/wheel_odom', '/odometry/filtered', '/tf', '/rover/stuck']
def yaw(q): return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))
cmd, wo, ek, mo, ob, st = [], [], [], [], [], []
while r.has_next():
    tp, data, ts = r.read_next()
    if tp not in want: continue
    m = deserialize_message(data, get_message(types[tp])); t = ts * 1e-9
    if tp == '/cmd_vel': cmd.append((t, m.linear.x, m.angular.z))
    elif tp == '/wheel_odom': wo.append((t, yaw(m.pose.pose.orientation), m.twist.twist.angular.z))
    elif tp == '/odometry/filtered': ek.append((t, yaw(m.pose.pose.orientation), m.twist.twist.angular.z))
    elif tp == '/rover/stuck': st.append((t, str(m)[:160]))
    elif tp == '/tf':
        for tr in m.transforms:
            if tr.header.frame_id == 'map' and tr.child_frame_id == 'odom': mo.append((t, yaw(tr.transform.rotation)))
            if tr.header.frame_id == 'odom' and tr.child_frame_id == 'base_link': ob.append((t, yaw(tr.transform.rotation)))
T1 = cmd[-1][0]; T0 = T1 - (float(sys.argv[2]) if len(sys.argv) > 2 else 14.0)
def at(arr, t, i=1):
    k = bisect.bisect_left([a[0] for a in arr], t); k = min(max(k, 0), len(arr) - 1); return arr[k][i]
def uw(a): return (a + math.pi) % (2 * math.pi) - math.pi
print('구간 %.1f s (주행 끝 %.1f s 전부터), map→odom %d 개, odom→base %d 개' % (T1 - T0, T1 - T0, len(mo), len(ob)))
print('  t(끝 기준) | 지령 v ω | 휠 yaw Δ(°) | EKF yaw Δ | SLAM(map) yaw Δ | 휠 ωz  EKF ωz')
t = T0; tot = [0, 0, 0]
while t < T1:
    t2 = min(t + 1.0, T1)
    dw = math.degrees(uw(at(wo, t2) - at(wo, t)))
    de = math.degrees(uw(at(ek, t2) - at(ek, t)))
    dm = math.degrees(uw((at(mo, t2) + at(ob, t2)) - (at(mo, t) + at(ob, t))))
    tot[0] += dw; tot[1] += de; tot[2] += dm
    print('  %5.1f | %+.2f %+.2f | %+6.1f | %+6.1f | %+6.1f | %+.2f %+.2f' % (t - T1, at(cmd, t, 1), at(cmd, t, 2), dw, de, dm, at(wo, t, 2), at(ek, t, 2)))
    t = t2
print('합계: 휠 %+.1f° / EKF %+.1f° / SLAM(map) %+.1f°' % tuple(tot))
print('map→odom yaw 보정 변화(구간): %+.1f°' % math.degrees(uw(at(mo, T1) - at(mo, T0))))
print('/rover/stuck 메시지(구간): %d' % sum(1 for s in st if T0 <= s[0] <= T1)); [print('  ', round(s[0] - T1, 1), s[1]) for s in st if T0 - 1 <= s[0] <= T1 + 1][:5]
