# up_launch_defaults_1104 — 11-04 §17: launch 기본값을 표준 prep(prep_patrol.sh) 구성과 같게 + 헷갈리는 설정 · 주석 정리. PC, 로버 안 움직임, 인자 없음, 출력 'ok'.
#   바꾸는 것(동작 변경 — launch 만 띄웠을 때): navigation global_camera obstacle→nvblox · mppi_viz false→lite · replan_hz ''→0.5 · stuck_shadow false→true,
#   ⚠ 이 스크립트는 첫 실행에서 ekf vslam 줄(원문 불일치)에서 멈춰 앞 5 건만 적용됐다 — 나머지는 같은 날 대화 안에서 줄 단위로 적용(SUMMARY §17). 다시 돌리면 assert 로 멈춤.
#   ekf vslam off→on · dds_shm false→true, camera emitter_off false→true · dds_shm false→true. prep 은 같은 값을 명시해 넘기므로 표준 주행은 그대로.
R = 'F:/6_Indoor_Rover/Rover/'
def sub(p, o, n):
    s = open(R + p, encoding='utf-8', newline='').read()
    assert s.count(o) == 1, (p, o[:70], s.count(o))
    open(R + p, 'w', encoding='utf-8', newline='').write(s.replace(o, n))
NL = 'ros2_ws/src/rover_navigation/launch/navigation.launch.py'
sub(NL, "DeclareLaunchArgument('replan_hz', default_value='',\n                              description='BT 주기 재계획 Hz(비우면 원본 0.01 = 목표당 1 회). 10-08 §3 A/B'),",
        "DeclareLaunchArgument('replan_hz', default_value='0.5',\n                              description='BT 주기 재계획 Hz — 기본 0.5(표준 prep 과 같음, 11-04). 비우면 BT 원본 0.01 = 목표당 1 회(B0 · Smac 시험). 10-08 §3 A/B'),")
sub(NL, "DeclareLaunchArgument('mppi_viz', default_value='false',\n                              description='장기 주행 기록용 MPPI 후보·최적 궤적 발행(10-07 §11, 기본 끔)'),",
        "DeclareLaunchArgument('mppi_viz', default_value='lite',\n                              description='MPPI 궤적 발행: lite(기본 — 표준 prep 과 같음, 11-04) | false | true(206 kB × 10 Hz — 쓰지 않음, 10-12 통신 포화)'),")
sub(NL, "DeclareLaunchArgument('global_camera', default_value='obstacle',",
        "DeclareLaunchArgument('global_camera', default_value='nvblox',   # 11-04: 표준 prep 과 같게(옛 기본 obstacle)")
sub(NL, "        # 2026-09-08 활성(기본 false): 실주행 오탐 0 (09-07 46s + 09-08 6회 주행) · 정탐 3/3 (job57) 검증 완료.\n        # 관찰만 하려면 stuck_shadow:=true.\n        DeclareLaunchArgument('stuck_shadow', default_value='false',",
        "        # 2026-09-08 활성(기본 false): 실주행 오탐 0 (09-07 46s + 09-08 6회 주행) · 정탐 3/3 (job57) 검증 완료.\n"
        "        # → 11-04 기본 true(관찰만): 10-01 §8.11 f2a4 실주행 오판 취소(use_gyro 꺼진 채 문틀 회전 과대) → §8.12 사용자 'F2 순회 동안 그림자',\n"
        "        #   10-29 §9 사용자 '자이로 우선은 켜지 마라' — 표준 prep 은 10-01 부터 true. 작동시키려면 stuck_shadow:=false.\n"
        "        DeclareLaunchArgument('stuck_shadow', default_value='true',")
EL = 'ros2_ws/src/rover_bringup/launch/ekf.launch.py'
sub(EL, "DeclareLaunchArgument('dds_shm', default_value='false', description='10-20 §7.4 cuVSLAM 컨테이너를 SHM+UDP 로(camera.launch dds_shm 과 같이)'),",
        "DeclareLaunchArgument('dds_shm', default_value='true', description='10-20 §7.4 cuVSLAM 컨테이너를 SHM+UDP 로(camera.launch dds_shm 과 같이) — 기본 true(표준 prep, 11-04)'),")
sub(EL, "DeclareLaunchArgument('vslam', default_value='off',\n                              description='2026-10-20 §6 cuVSLAM 병진 속도: off | shadow(그림자 EKF /odometry/ekf_vslam) | on(주 EKF 가 rf2o 대신) — emitter_off:=true 필요'),",
        "DeclareLaunchArgument('vslam', default_value='on',\n                              description='2026-10-20 §6 cuVSLAM 병진 속도: on(기본 — 10-23 §16 채택, 표준 prep 과 같음, 11-04) | shadow(그림자 EKF /odometry/ekf_vslam) | off — on · shadow 는 emitter_off:=true 필요. rf2o:=true 를 주인으로 쓰려면 vslam:=off 도 같이(53 행)'),")
CL = 'ros2_ws/src/rover_bringup/launch/camera.launch.py'
sub(CL, "DeclareLaunchArgument('emitter_off', default_value='false'),",
        "DeclareLaunchArgument('emitter_off', default_value='true'),   # 11-04: 프로젝터 상시 끔이 기본(10-21 §20 사용자 결정 · 표준 prep 과 같음). 켜려면 emitter_off:=false")
sub(CL, "DeclareLaunchArgument('dds_shm', default_value='false',",
        "DeclareLaunchArgument('dds_shm', default_value='true',   # 11-04: 표준 prep 과 같게")
PP = 'Docs/tools/prep_patrol.sh'
sub(PP, '  rf2o)  S="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel";;',
        '  rf2o)  S="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel vslam:=off emitter_off:=false dds_shm:=false";;   # 11-04: launch 기본이 vslam on · 프로젝터 끔 · SHM 이 돼 옛 구성 값을 명시')
NP = 'ros2_ws/src/rover_navigation/config/nav2_params.yaml'
sub(NP, 'controller_plugins: ["FollowPath", "FollowPathMPPI"]   # ★현재 FollowPath=RPP (09-03 벤치마크 A/B). MPPI 대기',
        'controller_plugins: ["FollowPath", "FollowPathMPPI"]   # BT 는 FollowPathMPPI 를 쓴다(09-15 부터). FollowPath = RPP 는 대조군으로 남김(11-04 주석 정정)')
sub(NP, '"PreferForwardCritic", "ClearanceBandCritic"]', '"PreferForwardCritic"]   # 11-04: ClearanceBandCritic 은 enabled false 라 목록에서 뺌(10-15 계산 부담으로 끔, 블록은 아래에 보존)')
print('ok')
