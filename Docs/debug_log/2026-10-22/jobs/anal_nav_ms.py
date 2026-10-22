#!/usr/bin/env python3
"""anal_nav_ms — nav2.log(PC 사본) 사건을 0.01 s 시각(KST)으로 — 10-21 chk_nav_ms.sh 의 PC 판(2026-10-22 §4).
  인자: nav2.log 시작HH:MM:SS 끝HH:MM:SS   출력 줄: 'HH:MM:SS.cc 노드 메시지'"""
import sys, re, datetime
NODES = ('controller_server', 'planner_server', 'bt_navigator', 'behavior_server', 'smoother_server', 'velocity_smoother', 'bt_navigator_navigate_to_pose_rclcpp_node')
KST = datetime.timezone(datetime.timedelta(hours=9))
for l in open(sys.argv[1], encoding='utf8', errors='replace'):
    if 'Message Filter' in l or 'tick rate' in l: continue
    m = re.search(r'\[(\d{10}\.\d+)\] \[([a-z_]+)\]: (.*)', l)
    if not m or m.group(2) not in NODES: continue
    t = float(m.group(1)); s = datetime.datetime.fromtimestamp(t, KST).strftime('%H:%M:%S')
    if not (sys.argv[2] <= s <= sys.argv[3]): continue
    print(('%s.%02d %s %s' % (s, int((t % 1) * 100), m.group(2), m.group(3)))[:200])
