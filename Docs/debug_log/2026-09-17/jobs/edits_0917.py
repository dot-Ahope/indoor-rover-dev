import sys
sp = sys.argv[1]; root = 'F:/6_Indoor_Rover/Rover/'
def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:60], s.count(old))
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8', newline='\n').write(s); print('edited', path.split('/')[-1])
y = root + 'ros2_ws/src/rover_navigation/config/nav2_params.yaml'
s = open(y, encoding='utf-8').read()
vis_line = [l for l in s.splitlines() if l.strip().startswith('visualize: true')][0]
edit(y, [
    ("    default_server_timeout: 20\n",
     "    # ★ 2026-09-17 mp7: 20 ms 안에 planner 가 목표 요청을 수락하지 못해(\"Timed out while waiting for action server to acknowledge\")\n"
     "    #   BT 가 실패로 보고 복구(클리어·BackUp 0.15 m)를 돌렸다 — SLAM map->odom 이 5.1 s 끊겨 map 프레임 서버가 막힌 순간. 100 ms 로 여유.\n"
     "    default_server_timeout: 100\n"),
    (vis_line + "\n",
     "      # ★ 2026-09-17 mp7: 끔. 주기마다 후보 궤적 MarkerArray(≈2232 점)를 발행·bag 기록(≈5 MB/s)하는 비용이 15W 모드 CPU 를 압박.\n"
     "      #   mp4~mp6 분석용 기록은 확보됨. 진단 주행에만 true 로 켠다.\n"
     "      visualize: false\n"),
])
d = sp + '/job231_drive.sh'
edit(d, [
    ('TOPICS="/tf /tf_static /map /scan /plan /local_plan /trajectories /transformed_global_plan \\n',
     'TOPICS="/tf /tf_static /map /scan /plan /local_plan /transformed_global_plan \\n'),
    ('setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &\n',
     'setsid nohup ros2 bag record -o $BAG $TOPICS > /tmp/bag_$NAME.log 2>&1 &\n'
     '# 09-17 mp7: 주행 중 CPU 굶주림(SLAM map->odom 5 s 끊김)의 범인을 가리기 위해 2 s 마다 프로세스별 CPU 기록\n'
     'setsid nohup top -b -d 2 -w 180 -o %CPU > /tmp/top_$NAME.log 2>&1 &\n'),
    ('pkill -INT -f "ros2 bag record" 2>/dev/null\n',
     'pkill -INT -f "ros2 bag record" 2>/dev/null\npkill -f "top -b -d 2 -w 180" 2>/dev/null\n'),
])
