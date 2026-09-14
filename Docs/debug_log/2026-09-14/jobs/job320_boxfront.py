#!/usr/bin/env python3
"""상자 앞 0.03~0.35 m, 상자 y 폭 안, z 0.06~0.25 의 깊이점 — '상자 앞 유령 셀' 출처 (2026-09-14). 정지, 주행 없음.
   프레임별 점 수·x 분포·z 분포. 상자 앞면 무늬 없음(스테레오 오정합)이면 상자 y 폭 안에서 앞면보다 가까운 x 에 간헐적으로 찍힌다.
   인자: BX BY [DUR=60] ; 환경 TOPIC (기본 필터 토픽)"""
import sys, os, math, time, numpy as np, rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2 as pc2
import tf2_ros
BX, BY = float(sys.argv[1]), float(sys.argv[2]); DUR = float(sys.argv[3]) if len(sys.argv) > 3 else 60.0
TOPIC = os.environ.get('TOPIC', '/camera/depth/points_filtered')
rclpy.init(); n = Node('boxfront320'); buf = tf2_ros.Buffer(); tl = tf2_ros.TransformListener(buf, n)
S = dict(R=None, T=None, f=0, hits=[], per=[], face=[])
def cb(m):
    if S['R'] is None:
        try: tr = buf.lookup_transform('base_link', m.header.frame_id, rclpy.time.Time()).transform
        except Exception: return
        q = tr.rotation
        S['R'] = np.array([[1-2*(q.y*q.y+q.z*q.z), 2*(q.x*q.y-q.z*q.w), 2*(q.x*q.z+q.y*q.w)],[2*(q.x*q.y+q.z*q.w), 1-2*(q.x*q.x+q.z*q.z), 2*(q.y*q.z-q.x*q.w)],[2*(q.x*q.z-q.y*q.w), 2*(q.y*q.z+q.x*q.w), 1-2*(q.x*q.x+q.y*q.y)]])
        S['T'] = np.array([tr.translation.x, tr.translation.y, tr.translation.z])
    P = pc2.read_points_numpy(m, field_names=('x','y','z'), skip_nans=True) @ S['R'].T + S['T']
    x, y, z = P[:,0], P[:,1], P[:,2]
    front = (x > BX - 0.35) & (x < BX - 0.03) & (np.abs(y - BY) < 0.15) & (z >= 0.06) & (z < 0.25)
    face = (x >= BX - 0.03) & (x < BX + 0.12) & (np.abs(y - BY) < 0.15) & (z >= 0.06) & (z < 0.25)
    S['f'] += 1; S['per'].append(int(front.sum())); S['face'].append(int(face.sum()))
    if front.any(): S['hits'].extend(P[front].tolist())
n.create_subscription(PointCloud2, TOPIC, cb, qos_profile_sensor_data)
t0 = time.time()
while time.time() - t0 < DUR: rclpy.spin_once(n, timeout_sec=0.05)
per = np.array(S['per']); face = np.array(S['face'])
print('%s: %d 프레임 / %.0f s. 상자 앞면 점 %d/프레임(중앙). 상자 앞 띠(x %.2f~%.2f, |y-BY|<0.15, z 0.06~0.25): 점 있는 프레임 %d (%.1f%%), 프레임당 최대 %d, 합 %d'
      % (TOPIC, S['f'], DUR, int(np.median(face)) if len(face) else 0, BX-0.35, BX-0.03, int((per>0).sum()), 100*(per>0).mean() if len(per) else 0, per.max() if len(per) else 0, per.sum()))
if S['hits']:
    H = np.array(S['hits'])
    print('  x 5~50~95%%: %.2f %.2f %.2f | y: %+.2f~%+.2f | z 5~50~95%%: %.3f %.3f %.3f' % (np.percentile(H[:,0],5), np.percentile(H[:,0],50), np.percentile(H[:,0],95), H[:,1].min(), H[:,1].max(), np.percentile(H[:,2],5), np.percentile(H[:,2],50), np.percentile(H[:,2],95)))
    from collections import Counter
    cc = Counter((round(p[0]/0.05)*0.05, round(p[1]/0.05)*0.05) for p in S['hits'])
    print('  5 cm 셀 상위: ' + ', '.join('(%.2f,%+.2f)x%d' % (a,b,c) for (a,b),c in cc.most_common(6)))
    # 버스트 구조: 연속 프레임에 몰리는가
    idx = np.where(per > 0)[0]
    if len(idx) > 1:
        gaps = np.diff(idx); print('  점 있는 프레임 간격: 중앙 %d, 최대 %d 프레임 (연속=1) → %s' % (int(np.median(gaps)), int(gaps.max()), '버스트' if np.median(gaps) <= 2 else '산발'))
