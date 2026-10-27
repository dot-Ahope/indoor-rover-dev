#!/usr/bin/env python3
"""gen_yaml — 오프라인 planner_server 설정(planner_offline.yaml) 생성 (2026-10-23 Phase P, PC).
  왜: Smac 변형(R · cost_penalty · 해석 확장 길이 · 방향 칸 수)과 코스트맵 패딩을 바꿔 가며 같은 장면을 비교하려고.
  변형 이름 규칙: Smac_R{R×100}_C{cp×10}[_A{해석 확장 최대 길이×10}][_B{방향 칸}] — 예 Smac_R10_C30_A05 = R 0.10 · cp 3.0 · 해석 확장 ≤ 0.5 m.
    해석 확장(analytic expansion) = 탐색 중 목표까지 Dubins 곡선을 바로 그어 보고, 차체가 치명에 안 닿으면 그대로 붙이는 단축(비용은 안 봄).
    1.1.20 기본은 비율 3.5 · 최대 3.0 m — 경로가 3 m 안이면 거의 처음부터 이 곡선이 붙어 cost_penalty 가 효과를 못 냄(첫 비교 결과, 2026-10-23 §22).
  _NS = smooth_path false(2026-10-26 §6: 탐색 경로를 다듬기 전 그대로 보려고)
  인자: 출력.yaml 패딩 변형이름...  (첫 비교 판 = 패딩 0.01, GridBased + Smac_R10_C12 … Smac_R15_C30, 해석 확장 기본)
  환경: SMAC_TOL = Hybrid tolerance(기본 0.25). SMAC_MAXT = Hybrid 계획 시간 상한(기본 5.0, 실주행 2.0). INFL_R · INFL_K = 전역 inflation 반경 · cost_scaling_factor(기본 0.70 · 2.0 = 실주행 값). 2026-10-26 D5 에서 추가."""
import sys, re, os
out, pad, names = sys.argv[1], float(sys.argv[2]), sys.argv[3:]
IR, IK = float(os.environ.get('INFL_R', '0.70')), float(os.environ.get('INFL_K', '2.0'))
MAXT = float(os.environ.get('SMAC_MAXT', '5.0'))
TOL = float(os.environ.get('SMAC_TOL', '0.25'))   # Smac Hybrid tolerance(m) — 2026-10-27 §5: 목표 수락 허용 시험   # Smac Hybrid max_planning_time — 2026-10-26 §20: 실주행 값 2.0 으로 재현할 때
blocks = []
LAT = '/opt/ros/humble/share/nav2_smac_planner/sample_primitives/5cm_resolution/0.5m_turning_radius/diff/output.json'
for n in names:
    # Lattice_C{cp×10}_P{회전 벌점}[_REV] — 2026-10-26 D1: 설치판 diff 원형(5 cm · R 0.5 m, 제자리 회전 원형 포함). _REV = 후진 확장 허용
    m = re.match(r'Lattice_C(\d+)_P(\d+)(_REV)?(?:_A(\d+))?(?:_M(\d+))?(_NS)?$', n)   # _M = 해석 확장 비용 상한(포크 전용, 2026-10-26 §5)
    if m:
        CP, RP, REV = int(m.group(1)) / 10, float(m.group(2)), 'true' if m.group(3) else 'false'
        AL = int(m.group(4)) / 10 if m.group(4) else 3.0   # _A = 해석 확장 최대 길이 ×10
        MC = float(m.group(5)) if m.group(5) else 200.0
        blocks.append(f'''    {n}:
      plugin: "nav2_smac_planner/SmacPlannerLattice"
      allow_unknown: true
      tolerance: 0.25
      max_iterations: 1000000
      max_on_approach_iterations: 1000
      max_planning_time: 5.0
      analytic_expansion_ratio: 3.5
      analytic_expansion_max_length: {AL}
      reverse_penalty: 2.0
      change_penalty: 0.05
      non_straight_penalty: 1.05
      cost_penalty: {CP}
      rotation_penalty: {RP}
      retrospective_penalty: 0.015
      lattice_filepath: "{LAT}"
      analytic_expansion_max_cost: {MC}
      lookup_table_size: 20.0
      cache_obstacle_heuristic: false
      allow_reverse_expansion: {REV}
      smooth_path: {'false' if m.group(6) else 'true'}
      smoother:
        max_iterations: 1000
        w_smooth: 0.3
        w_data: 0.2
        tolerance: 1.0e-10
        do_refinement: true
        refinement_num: 2
''')
        continue
    m = re.match(r'Smac_R(\d+)_C(\d+)(?:_A(\d+))?(?:_B(\d+))?(_RS)?(?:_M(\d+))?(_NS)?$', n)   # _RS = REEDS_SHEPP(전진 · 후진, 2026-10-26)
    if not m: raise SystemExit('이름 형식: ' + n)
    R, CP = int(m.group(1)) / 100, int(m.group(2)) / 10; AL = int(m.group(3)) / 10 if m.group(3) else 3.0; B = int(m.group(4)) if m.group(4) else 72
    blocks.append(f'''    {n}:
      plugin: "nav2_smac_planner/SmacPlannerHybrid"
      tolerance: {TOL}
      downsample_costmap: false
      downsampling_factor: 1
      allow_unknown: true
      max_iterations: 1000000
      max_on_approach_iterations: 1000
      max_planning_time: {MAXT}
      motion_model_for_search: "{'REEDS_SHEPP' if m.group(5) else 'DUBIN'}"
      angle_quantization_bins: {B}
      analytic_expansion_ratio: 3.5
      analytic_expansion_max_length: {AL}
      analytic_expansion_max_cost: {float(m.group(6)) if m.group(6) else 200.0}
      minimum_turning_radius: {R}
      reverse_penalty: 2.0
      change_penalty: 0.0
      non_straight_penalty: 1.05
      cost_penalty: {CP}
      retrospective_penalty: 0.015
      lookup_table_size: 20.0
      cache_obstacle_heuristic: false
      smooth_path: {'false' if m.group(7) else 'true'}
      smoother:
        max_iterations: 1000
        w_smooth: 0.3
        w_data: 0.2
        tolerance: 1.0e-10
        do_refinement: true
        refinement_num: 2
''')
y = f'''# planner_offline — 계획기 오프라인 비교(Phase P §4 · P7) 전용 planner_server 설정. gen_yaml.py 로 생성(패딩 {pad}, inflation {IR}/{IK}, 변형 {len(names)} 개). Jetson ROS_DOMAIN_ID 42 에서만.
# 전역 코스트맵 = 기록된 /global_costmap/costmap 의 치명 칸(100) · 미지(−1)만 static_layer 로 받고(/offline_map), 실제와 같은 inflation(0.70/2.0) · 풋프린트로 다시 부풀림
#   → 실제 계획기가 본 지도를 재구성(일치율은 query_planners.py 가 확인; 2026-10-23 첫 판 6 장면 모두 1.0000).
#   99(내접)를 직접 넣지 않는 이유: StaticLayer 비삼진 변환은 99 → 251 이 되어 내접(253) 의미를 잃음(NavFn 은 ≥ 253 을 장애물로 봄).
# GridBased = B0 NavFn 과 같은 값. cache_obstacle_heuristic false — 장면마다 지도가 바뀌는데 목표가 같으면 묵은 휴리스틱을 씀(실주행 설정은 true, P6 에서 검토).
planner_server:
  ros__parameters:
    expected_planner_frequency: 1.0
    use_sim_time: false
    planner_plugins: ["GridBased", {", ".join('"%s"' % n for n in names)}]
    GridBased:
      plugin: "nav2_navfn_planner/NavfnPlanner"
      tolerance: 0.25
      use_astar: false
      allow_unknown: true
{"".join(blocks)}
global_costmap:
  global_costmap:
    ros__parameters:
      update_frequency: 2.0
      publish_frequency: 2.0
      global_frame: map
      robot_base_frame: base_link
      resolution: 0.05
      track_unknown_space: true
      trinary_costmap: true          # StaticLayer 가 읽는 코스트맵 단위 값: 100 → 치명, −1 → 미지, 나머지 → 빈 칸
      lethal_cost_threshold: 100
      footprint: "[[0.262, 0.165], [0.262, -0.165], [-0.248, -0.165], [-0.248, 0.165]]"
      footprint_padding: {pad}
      plugins: ["static_layer", "inflation_layer"]
      static_layer:
        plugin: "nav2_costmap_2d::StaticLayer"
        map_topic: /offline_map
        map_subscribe_transient_local: true
      inflation_layer:
        plugin: "nav2_costmap_2d::InflationLayer"
        inflation_radius: {IR}
        cost_scaling_factor: {IK}
      always_send_full_costmap: true

lifecycle_manager_offline:
  ros__parameters:
    autostart: true
    node_names: ["planner_server"]
    bond_timeout: 0.0
'''
open(out, 'w', encoding='utf-8').write(y); print('작성', out, '변형', names)
