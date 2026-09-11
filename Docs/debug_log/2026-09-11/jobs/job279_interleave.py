#!/usr/bin/env python3
import rosbag2_py
from rclpy.serialization import deserialize_message
from geometry_msgs.msg import Twist
r=rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_s4r2',storage_id='sqlite3'),rosbag2_py.ConverterOptions('',''))
msgs=[]
while r.has_next():
    t,d,ts=r.read_next()
    if t=='/cmd_vel': m=deserialize_message(d,Twist); msgs.append((ts*1e-9,m.linear.x,m.angular.z))
t0=msgs[0][0]; msgs=[(t-t0,v,w) for t,v,w in msgs]
for a,b in ((9.2,11.2),(22.2,24.2),(13.8,14.6)):
    win=[m for m in msgs if a<=m[0]<=b]
    print(f"=== t {a}~{b}s: {len(win)}개 ===")
    line=[]
    for t,v,w in win:
        line.append(f"{t:5.2f}:{v:+.2f}")
    for i in range(0,len(line),8): print("  "+"  ".join(line[i:i+8]))
    # 100ms 당 메시지 수 (2 이면 두 스트림 맞물림)
    import collections
    c=collections.Counter(int(t*10) for t,_,_ in win)
    print("  100ms 창당 메시지 수 분포:", dict(sorted(collections.Counter(c.values()).items())))
