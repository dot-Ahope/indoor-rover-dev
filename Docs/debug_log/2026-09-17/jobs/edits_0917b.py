import sys
p = sys.argv[1]; BS = chr(92); NL = chr(10)
s = open(p, encoding='utf-8').read()
pairs = [
    ('/local_plan /trajectories /transformed_global_plan ' + BS + NL, '/local_plan /transformed_global_plan ' + BS + NL),
    ('setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &' + NL,
     'setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &' + NL +
     '# 09-17 mp7: 주행 중 CPU 굶주림(SLAM map->odom 5 s 끊김)의 범인을 가리기 위해 2 s 마다 프로세스별 CPU 기록' + NL +
     'setsid nohup top -b -d 2 -w 180 -o %CPU > /tmp/top_$NAME.log 2>&1 &' + NL),
    ('pkill -INT -f "ros2 bag record" 2>/dev/null' + NL,
     'pkill -INT -f "ros2 bag record" 2>/dev/null' + NL + 'pkill -f "top -b -d 2 -w 180" 2>/dev/null' + NL),
]
for old, new in pairs:
    c = s.count(old); assert c == 1, (old[:50], c)
    s = s.replace(old, new)
open(p, 'w', encoding='utf-8', newline=NL).write(s); print('job231 patched')
