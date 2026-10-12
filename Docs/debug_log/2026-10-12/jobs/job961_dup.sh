#!/bin/bash
# 10-12 §3.4: 중복·잔류 프로세스 확인(사용자 요청). 로버 안 움직임
echo "== ROS 관련 프로세스(실행 파일별 개수 · 시작 시각 · pid)"
ps -eo pid,ppid,lstart,etimes,args --no-headers | grep -aE "/opt/ros|ros2 |ros2_ws|slam_ws|rf2o_ws|micro_ros|nvblox|foxglove|rosbag|launch" | grep -av "grep\|job961" | python3 -c "
import sys,re,collections
g=collections.defaultdict(list)
for l in sys.stdin:
    f=l.split(None,8)
    if len(f)<9: continue
    pid,ppid=f[0],f[1]; start=f[5]; et=int(f[7]); a=f[8]
    m=re.search(r'__node:=(\S+)',a); exe=a.split()[0].split('/')[-1]
    if exe.startswith('python3') or exe=='bash' or exe=='timeout':
        t=[x for x in a.split()[1:4] if not x.startswith('-')]; exe=exe+' '+(t[0].split('/')[-1] if t else '')+(' '+' '.join(t[1:3]) if t and t[0].endswith('ros2') else '')
    g[(exe,m.group(1) if m else '')].append((start,pid,ppid,et))
for (exe,node),v in sorted(g.items(),key=lambda kv:(-len(kv[1]),kv[0])):
    print('  %s%-34s %-24s %s'%('★ ' if len(v)>1 else '  ',exe[:34],node[:24],' | '.join('%s pid %s(부모 %s)'%(s,p,pp) for s,p,pp,_ in v)))
"
echo "== 컨테이너 안 nvblox: $(docker exec isaac_ros_dev-aarch64-container bash -c "pgrep -fa nvblox_node | grep -v pgrep | wc -l" 2>/dev/null) 개 · 컨테이너 목록: $(docker ps --format '{{.Names}}({{.Status}})' | tr '\n' ' ')"
echo "== ROS 그래프 노드 이름 중복"
timeout 20 ros2 node list 2>/dev/null | sort | uniq -c | awk '$1>1{print "  ★ "$0}' ; echo "  노드 총 $(timeout 20 ros2 node list 2>/dev/null | wc -l) 개"
echo "== /tf 발행자·구독자"
timeout 12 ros2 topic info -v /tf 2>/dev/null | grep -aE "Node name|Endpoint type" | paste - - | awk '{print $3, $6}' | sort | uniq -c | sort -k3,3 -k1,1nr | sed 's/^/  /'
echo "== /cmd_vel 발행자: $(timeout 10 ros2 topic info -v /cmd_vel 2>/dev/null | grep -aB1 'PUBLISHER' | grep -a 'Node name' | awk '{print $3}' | sort | uniq -c | tr '\n' ' ')"
echo "== 부하: $(cut -d' ' -f1-3 /proc/loadavg) · 가동 $(uptime -p)"
