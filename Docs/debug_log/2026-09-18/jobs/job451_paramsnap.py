#!/usr/bin/env python3
"""주행 재현용 파라미터 스냅샷 (2026-09-18 §17). 노드 하나로 여러 노드의 list/get_parameters 서비스를 직접 불러
   `ros2 param dump`(노드마다 7~8 s) 대신 한 번의 디스커버리로 끝낸다. 출력: YAML 비슷한 텍스트(노드별 정렬).
   인자: [node ...]  기본 = Nav2·SLAM·EKF·stuck_monitor. 응답 없는 노드는 '(없음)' 으로 남긴다.
"""
import sys, time
import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import ListParameters, GetParameters
from rcl_interfaces.msg import ParameterType as PT
DEFAULT = ['/controller_server', '/local_costmap/local_costmap', '/global_costmap/global_costmap', '/planner_server', '/smoother_server',
           '/bt_navigator', '/behavior_server', '/velocity_smoother', '/slam_toolbox', '/ekf_filter_node', '/stuck_monitor', '/depth_relay']


def val(p):
    t = p.type
    return {PT.PARAMETER_BOOL: p.bool_value, PT.PARAMETER_INTEGER: p.integer_value, PT.PARAMETER_DOUBLE: p.double_value,
            PT.PARAMETER_STRING: p.string_value, PT.PARAMETER_BYTE_ARRAY: list(p.byte_array_value), PT.PARAMETER_BOOL_ARRAY: list(p.bool_array_value),
            PT.PARAMETER_INTEGER_ARRAY: list(p.integer_array_value), PT.PARAMETER_DOUBLE_ARRAY: list(p.double_array_value),
            PT.PARAMETER_STRING_ARRAY: list(p.string_array_value)}.get(t, None)


def call(n, cli, req, sec):
    if not cli.wait_for_service(timeout_sec=sec):
        return None
    f = cli.call_async(req); t0 = time.time()
    while rclpy.ok() and not f.done() and time.time() - t0 < sec:
        rclpy.spin_once(n, timeout_sec=0.1)
    return f.result() if f.done() else None


rclpy.init(); n = Node('paramsnap451')
nodes = sys.argv[1:] or DEFAULT
print('# paramsnap %s' % time.strftime('%Y-%m-%d %H:%M:%S'))
for nd in nodes:
    lc = n.create_client(ListParameters, nd + '/list_parameters'); gc = n.create_client(GetParameters, nd + '/get_parameters')
    lr = call(n, lc, ListParameters.Request(depth=0), 4.0)
    if lr is None:
        print('%s: (없음)' % nd); continue
    names = sorted(lr.result.names)
    out = {}
    for k in range(0, len(names), 60):        # 한 번에 너무 많이 물으면 응답이 커서 나눠서
        gr = call(n, gc, GetParameters.Request(names=names[k:k + 60]), 6.0)
        if gr is None:
            continue
        for nm, pv in zip(names[k:k + 60], gr.values):
            out[nm] = val(pv)
    print('%s:  # %d 개' % (nd, len(out)))
    for nm in names:
        if nm in out and not nm.startswith('qos_overrides'):
            print('  %s: %r' % (nm, out[nm]))
n.destroy_node(); rclpy.shutdown()
