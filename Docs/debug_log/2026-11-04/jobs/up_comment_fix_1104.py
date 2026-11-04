# up_comment_fix_1104 — 11-04 §3: 8 기 문제 대장이 찾은 낡은 주석 정정(동작 변경 없음 · 정확한 문자열 치환 · 한 번씩). PC, 로버 안 움직임. 인자 없음, 출력 'ok'.
R = 'F:/6_Indoor_Rover/Rover/'
def sub(p, o, n):
    s = open(R + p, encoding='utf-8', newline='').read()
    assert s.count(o) == 1, (p, o[:60], s.count(o))
    open(R + p, 'w', encoding='utf-8', newline='').write(s.replace(o, n))
Y = 'ros2_ws/src/rover_navigation/config/nvblox_local.yaml'
sub(Y, '# (10-22 전: 1.4) 09-22 N6-1: 2.0 → 1.6 → 1.4 — 1.5~2.2 m 의 바닥·테이프 깊이 잡음이 전역 코스트맵 유령 셀로(SUMMARY §5.2). 상자(≤1.3 m)·STVL 지평선(1.2)보다 여유. 원거리는 라이다·SLAM 지도가 맡음',
       '# 지금 2.0(위 ★ 10-22). 이력: 09-22 N6-1 2.0 → 1.6 → 1.4(1.5~2.2 m 바닥·테이프 깊이 잡음이 전역 유령 셀로, 09-22 §5.2) — 11-04 정정: 꼬리의 1.4 근거는 옛 값의 것')
sub(Y, '      esdf_integrator_min_weight: 0.1\n',
       '      esdf_integrator_min_weight: 0.1   # 10-22 §9 재생 A/B: 1 · 2 는 유령 ≤ 30 % · 상자 칸 ≥ 80 % 기준 미달 → 0.1 유지(11-04 주석 추가)\n')
sub(Y, '      # 2026-10-15 §22~§23: 1.0(라이브러리 기본값)을 정지 A/B 로 시험',
       '      # (아래 3 줄은 다음 줄 esdf_integrator_max_site_distance_vox 설명 — 11-04 위치 표시)\n      # 2026-10-15 §22~§23: 1.0(라이브러리 기본값)을 정지 A/B 로 시험')
sub(Y, '#   실패 때 6~7 cm 과장(§13 · §18.2)은 이 값이 아니라 비스듬한 먼 첫 관측 쪽으로 추정.',
       '#   실패 때 6~7 cm 과장(§13 · §18.2)은 이 값이 아니라 비스듬한 먼 첫 관측 쪽으로 추정 → 10-19 §14 정정: 관측 오차 3~5 + odom 기억 밀림 + 칸 반올림(문제 대장 box-exaggeration-source).')
C = 'ros2_ws/src/rover_bringup/launch/camera.launch.py'
sub(C, '# (10-19 §25) emitter_off:=true — 프로젝터 상시 끔 + IR 좌우 켬(같은 15 fps). cuVSLAM 오프라인 확인용 기록 주행.',
       '# (10-19 §25) emitter_off:=true — 프로젝터 상시 끔 + IR 좌우 켬(같은 15 fps). 처음엔 cuVSLAM 오프라인 확인용 기록 주행이었으나 10-21 §20 결정 뒤 운용 기본(prep_patrol.sh ODOM=vslam — launch 기본값은 false 그대로, 11-04 정정).')
sub(C, "기억 · 시험으로 확인 중)이라", "기억 — 미확인)이라")
sub(C, '#   상자 모서리에서 상자 · 배경 깊이가 섞인 점이 면 밖에 찍히는지(10-20 §8.1 북 면 +6 cm) 정지 A/B 로 본다. 1 = 데시메이션 끔(640×480).',
       '#   상자 모서리에서 상자 · 배경 깊이가 섞인 점이 면 밖에 찍히는지(10-20 §8.1 북 면 +6 cm) 정지 A/B 로 봤다 → 10-20 §8.3: ×2 · 끔 모두 상자 칸 번짐 차이 < 1 cm, 대책 아님(4 유지, 11-04 정정). 1 = 데시메이션 끔(640×480).')
sub('ros2_ws/src/rover_bringup/config/fastdds_udp_only.xml', '→ **원인 제거**: SHM 전송을 아예 쓰지 않는다.',
       '→ **원인 제거**: SHM 전송을 아예 쓰지 않는다.\n  (10-20 §7.2 정정: 확인된 것은 비정상 종료 · 잔재 강제 삭제 때의 문제까지 — SHM 자체가 원인이라는 것은 과한 일반화. 10-21~ 카메라 ↔ cuVSLAM 만\n   fastdds_shm_udp.xml 로 SHM+UDP 를 쓴다(dds_shm:=true, 문제 대장 camera-container-shm). 나머지는 이 파일 그대로, 11-04 주석 추가)')
sub('ros2_ws/src/rover_navigation/src/path_blocked_ahead_condition.cpp', '막힘 5 회 · 탈출 · 대기 2 회, 목표 5 에 52 s(f2v2 31.6 s).',
       '막힘 5 회 · 탈출 · 대기 2 회(§20.7 정정: 서쪽 통로 막힘 4 번은 목표 4(34.6 s) 구간, 목표 5 의 52.1 s 는 다른 막힘 1 번 + 최적화 실패 — 11-04 주석 정정).')
for p in ('Docs/debug_log/2026-11-03/jobs/job551_f0drive.sh',):
    sub(p, '# 10-19 §16 · §17: BAG_IR=1(BAG_DEPTH 포함) — prep 에 SENSORS_ADD="emitter_flash:=true" 필요.',
           '# 10-19 §16 · §17: BAG_IR=1(BAG_DEPTH 포함) — prep 에 SENSORS_ADD="emitter_flash:=true" 또는 emitter_off:=true(지금 prep 기본, 10-19 f2z1 이 이 조합 — 11-04 정정) 필요.')
print('ok')
