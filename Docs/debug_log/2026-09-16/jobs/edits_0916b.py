import sys
root = 'F:/6_Indoor_Rover/Rover/'
def edit(path, pairs):
    s = open(path, encoding='utf-8').read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, old[:50], s.count(old))
        s = s.replace(old, new)
    open(path, 'w', encoding='utf-8', newline='\n').write(s); print('edited', path)
edit(root + 'ros2_ws/src/rover_navigation/config/nav2_params.yaml', [
    ("        inflation_radius: 0.55\n",
     "        # ★ 2026-09-16 A 계획 정지 A/B(job340, 상자 1.085/-0.008, 목표 1.8/0): 0.55 → 0.70. NavFn 사선의 최대 진행방향 +64° → +37°,\n"
     "        #   0.1 m 창 최대 꺾임 78° → 51°(+SmoothPath 16.6°), 차선변경 0.43→0.92 에서 0.40→0.86, 상자셀 최소거리 0.269 → 0.265 (유지),\n"
     "        #   통로 계획횡 +0.412 → +0.390. 입구 접선각(x=BX-0.45)은 31° → 28° 로 기하 한계(0.40 m 횡이동/0.64 m) 안에서 소폭.\n"
     "        inflation_radius: 0.70\n"),
])
edit(root + 'ros2_ws/src/rover_navigation/config/nav_to_pose_no_spin.xml', [
    ('            <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>\n',
     '            <!-- 2026-09-16 A 계획: SmoothPath(simple_smoother) 연결. 정지 A/B(job340)에서 inflation 0.70 과 함께 0.1 m 창 최대 꺾임 78° → 16.6°.\n'
     '                 실패(충돌 검사 등) 시 ForceSuccess 로 원 경로를 그대로 쓴다 — RecoveryNode 의 클리어를 유발하지 않기 위해. -->\n'
     '            <Sequence name="PlanAndSmooth">\n'
     '              <ComputePathToPose goal="{goal}" path="{path}" planner_id="GridBased"/>\n'
     '              <ForceSuccess>\n'
     '                <SmoothPath unsmoothed_path="{path}" smoothed_path="{path}" smoother_id="simple_smoother" max_smoothing_duration="1.0" check_for_collisions="true"/>\n'
     '              </ForceSuccess>\n'
     '            </Sequence>\n'),
])
