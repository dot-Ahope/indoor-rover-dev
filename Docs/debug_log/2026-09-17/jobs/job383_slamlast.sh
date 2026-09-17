#!/bin/bash
source /opt/ros/humble/setup.bash
echo "ptrace_scope=$(cat /proc/sys/kernel/yama/ptrace_scope)  gdb=$(which gdb || echo 없음)  eu-stack=$(which eu-stack || echo 없음)"
python3 - <<'PY'
import rosbag2_py
from rclpy.serialization import deserialize_message
from tf2_msgs.msg import TFMessage
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/tmp/bag_mp7', storage_id='sqlite3'), rosbag2_py.ConverterOptions('', ''))
first = last = None; mo = []; maps = []; ob_last = None
while r.has_next():
    topic, data, ts = r.read_next(); t = ts * 1e-9
    if first is None: first = t
    last = t
    if topic == '/tf':
        for tr in deserialize_message(data, TFMessage).transforms:
            st = tr.header.stamp.sec + tr.header.stamp.nanosec * 1e-9
            if tr.header.frame_id == 'map': mo.append((t, st))
            if tr.child_frame_id == 'base_link': ob_last = (t, st)
    elif topic == '/map':
        maps.append(t)
G = 1789610470.807
print('bag %.2f ~ %.2f (goal 기준 %+.1f ~ %+.1f s)' % (first, last, first - G, last - G))
if mo:
    gaps = [(mo[i][0] - mo[i-1][0], mo[i-1][0] - G) for i in range(1, len(mo))]
    big = [g for g in gaps if g[0] > 0.5]
    print('map->odom 메시지 %d개, 마지막 수신 goal %+.2f s (stamp 지연 %.2f s), 0.5 s 넘는 간격: %s' % (len(mo), mo[-1][0] - G, mo[-1][0] - mo[-1][1], ' '.join('%.1fs@%+.1f' % g for g in big[:8])))
print('/map 메시지 %d개, 마지막 goal %+.1f s' % (len(maps), (maps[-1] - G) if maps else float('nan')))
print('odom->base 마지막 goal %+.1f s' % (ob_last[0] - G))
PY
