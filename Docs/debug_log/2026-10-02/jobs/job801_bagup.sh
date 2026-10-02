#!/bin/bash
# 10-02 §1: f2a12 bag 을 재부팅에 안전한 ~/bags 로 풀고 정보 확인
cd ~/bags && tar -xzf /tmp/bag_f2a12.tgz && rm /tmp/bag_f2a12.tgz && source /opt/ros/humble/setup.bash
ros2 bag info ~/bags/bag_f2a12 | grep -aE "Duration|Start|End|Topic:" | cut -c1-140
python3 - <<'PY'
import rosbag2_py
r = rosbag2_py.SequentialReader(); r.open(rosbag2_py.StorageOptions(uri='/home/jetson/bags/bag_f2a12', storage_id='sqlite3'), rosbag2_py.ConverterOptions('cdr', 'cdr'))
tp, d, ts = r.read_next(); print('첫 메시지 epoch %.3f' % (ts * 1e-9))
PY
