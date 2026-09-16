# 2026-09-16 일괄 편집: 릴레이 CPU 수정·max_range, decay 120/180, 컨트롤러 10 Hz·MPPI model_dt·visualize, BT MPPI 유지, bag 토픽
import sys
sp = sys.argv[1]
root = 'F:/6_Indoor_Rover/Rover/'

def edit(path, pairs, must=True):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        n = s.count(old)
        if n != 1:
            if must:
                raise SystemExit('패턴 %d회: %s :: %s' % (n, path, old[:60]))
            continue
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8', newline='\n').write(s)
    print('edited', path)

# 1) depth_relay.py
p = root + 'ros2_ws/src/rover_bringup/scripts/depth_relay.py'
s = open(p, encoding='utf-8').read()
if 'import array' not in s:
    edit(p, [
        ('import numpy as np', 'import array\nimport numpy as np'),
        ("        self.declare_parameter('min_range', 0.45)",
         "        self.declare_parameter('max_range', 4.0)              # [m] D455 원거리 잡음(6~7 m 군집, 09-16 job338) 제거 + 점 수 절감\n        self.declare_parameter('min_range', 0.45)"),
        ("        self.min_range = float(self.get_parameter('min_range').value)",
         "        self.min_range = float(self.get_parameter('min_range').value)\n        self.max_range = float(self.get_parameter('max_range').value)"),
        ("        keep = finite & (r2 >= self.min_range * self.min_range)",
         "        keep = finite & (r2 >= self.min_range * self.min_range) & (r2 <= self.max_range * self.max_range)"),
        ("        out.data = buf[idx].tobytes()",
         "        # ★ 2026-09-16 (job339 cProfile): bytes 를 넣으면 생성 메시지의 setter 가 바이트마다 isinstance 검사를 해\n        #   콜백 시간의 95 %(12 s 중 10.5 s)를 먹었다(프레임당 14k점×16B). array('B') 는 검사 없이 통과한다.\n        out.data = array.array('B', buf[idx].tobytes())"),
    ])
# launch
edit(root + 'ros2_ws/src/rover_bringup/launch/camera.launch.py', [
    ("parameters=[{'min_range': 0.45, 'voxel': 0.05,", "parameters=[{'min_range': 0.45, 'max_range': 4.0, 'voxel': 0.05,"),
], must=False)
# 2) yaml
edit(root + 'ros2_ws/src/rover_navigation/config/nav2_params.yaml', [
    ("        voxel_decay: 60.0             # 선형 감쇠 수명(초)",
     "        # ★ 2026-09-16 §C: 60 → 120. 입구 머뭇거림 중 기억 소실(mp3 접촉)을 막는다. 누적 잡음 검토(job338, mp2/mp3/bk1 bag):\n"
     "        #   깊이 전용 셀 중 로버 궤적 0.25 m 이내 0개, 통로 띠 안은 상자 앞 오른쪽 '바닥 점' 1~2개뿐(왼쪽 통로 밖), 나머지는\n"
     "        #   y>1.0 의 낮은 가구·6~7 m 원거리 군집. 120 s 상한 시뮬레이션에서도 통로 띠 최대 2개 → 통로를 막지 않는다.\n"
     "        #   남는 위험: 사람이 지나간 자취가 2 배 오래 남는다(관찰자 시야 밖 규칙 유지).\n"
     "        voxel_decay: 120.0            # 선형 감쇠 수명(초)"),
    ("        voxel_decay: 90.0             # 선형 감쇠 수명(초)",
     "        voxel_decay: 180.0            # 선형 감쇠 수명(초) — 2026-09-16 §C: 90 → 180 (로컬과 같은 근거, 전역 통로 띠 유령 0개)"),
    ("    controller_frequency: 20.0\n",
     "    # ★ 2026-09-16: 20 → 10 Hz. MPPI 를 Orin Nano CPU 예산 안에서 쓰기 위해: 56 step@20 Hz 는 루프 미달 306 건/90 s(mp3).\n"
     "    #   10 Hz + model_dt 0.1 + 32 step 이면 지평 3.2 s(0.26 m, RPP lookahead 급)를 mp2(32 step@20 Hz)의 절반 연산으로 얻는다.\n"
     "    #   0.08 m/s 로봇은 한 주기 0.8 cm 이동이라 10 Hz 로 충분. MPPI 는 Humble 에서 CPU(xtensor) 전용 — GPU 를 쓰지 않는다.\n"
     "    controller_frequency: 10.0\n"),
    ("      model_dt: 0.05\n", "      model_dt: 0.1             # 2026-09-16: = 1/controller_frequency(10 Hz). 32 step → 지평 3.2 s\n"),
    ("      visualize: false\n", "      visualize: true           # 2026-09-16: 후보 궤적(/trajectories)·변환 경로를 bag 에 남겨 정체 원인을 본다 (진단 기간만)\n"),
])
# 3) BT: MPPI 유지
edit(root + 'ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml', [
    ('<FollowPath path="{path}" controller_id="FollowPath"/>',
     '<!-- 2026-09-16 사용자 결정: Orin Nano 에서 MPPI 유지. CPU 는 10 Hz·model_dt 0.1·32 step 으로 맞춘다 (분석 문서 §4 B3). -->\n          <FollowPath path="{path}" controller_id="FollowPathMPPI"/>'),
])
# 4) bag 토픽 (스크래치패드 러너)
edit(sp + '/job231_drive.sh', [
    ('TOPICS="/tf /tf_static /map /scan /plan /local_plan ', 'TOPICS="/tf /tf_static /map /scan /plan /local_plan /trajectories /transformed_global_plan '),
], must=False)
print('all edits done')
