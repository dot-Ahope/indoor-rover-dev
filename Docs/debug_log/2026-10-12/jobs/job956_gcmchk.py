# 10-12 §3.2 게이트 후보: 전역 코스트맵에 정적 지도가 들어왔는가 — /global_costmap/costmap 한 장의 치명(≥99) 칸 수와 크기
import rclpy, time
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid
rclpy.init(); n = Node('gcmchk956'); got = []
n.create_subscription(OccupancyGrid, '/global_costmap/costmap', lambda m: got.append(m), QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL, reliability=ReliabilityPolicy.RELIABLE))
t0 = time.time()
while time.time() - t0 < 15 and not got: rclpy.spin_once(n, timeout_sec=0.2)
if not got: print('  전역 코스트맵: 수신 없음 ★')
else:
    m = got[-1]; d = m.data; leth = sum(1 for v in d if v >= 99); print('  전역 코스트맵 %d×%d · 치명/내접 칸 %d (%.1f %%) → %s' % (m.info.width, m.info.height, leth, 100.0 * leth / len(d), 'OK' if (leth > 500 and m.info.width * m.info.height > 20000) else '★ 지도 없음 의심(기본 크기 100×100 이면 정적 층이 지도를 못 받은 것)'))
rclpy.shutdown()
