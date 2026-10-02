import rosbag2_py, math, numpy as np
from rclpy.serialization import deserialize_message
from sensor_msgs.msg import LaserScan
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_rot1', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
t0 = None
while r.has_next():
    tp, d, ts = r.read_next()
    if t0 is None: t0 = ts
    if tp != '/scan': continue
    m = deserialize_message(d, LaserScan); rr = np.array(m.ranges); a = m.angle_min + m.angle_increment * np.arange(len(rr)) + math.pi - 0.04677; ok = np.isfinite(rr) & (rr > 0.2) & (rr < 3)
    x = 0.152 + rr[ok] * np.cos(a[ok]); y = rr[ok] * np.sin(a[ok])
    dx = np.where(x > 0, np.maximum(x - 0.262, 0), np.maximum(-x - 0.248, 0)); dy = np.maximum(np.abs(y) - 0.165, 0); g = np.hypot(dx, dy)
    k = np.argmin(g); n0 = (g < 0.08).sum()
    if g[k] < 0.15: print('%.2f s 최소 %.3f m 점 차체(%+.2f, %+.2f) 거리 %.2f | 0.08 안 점 %d' % ((ts - t0) * 1e-9, g[k], x[k], y[k], rr[ok][k], n0))
