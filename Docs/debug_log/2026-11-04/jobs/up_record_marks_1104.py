# up_record_marks_1104 — 11-04 §3: 8 기 문제 대장이 찾은 기록 어긋남에 정정 표시를 줄 끝에 덧붙임(원문은 지우지 않음, README §2.1). PC, 로버 안 움직임. 출력 'ok'.
R = 'F:/6_Indoor_Rover/Rover/'
def mark(p, key, note):
    L = open(R + p, encoding='utf-8', newline='').read().split('\n')
    hit = [i for i, l in enumerate(L) if key in l]
    assert len(hit) == 1, (p, key, len(hit))
    i = hit[0]; cr = L[i].endswith('\r'); base = L[i].rstrip('\r')
    assert '2026-11-04 §3' not in base, (p, key)
    L[i] = base + ' → 2026-11-04 §3 정정: ' + note + ('\r' if cr else '')
    open(R + p, 'w', encoding='utf-8', newline='').write('\n'.join(L))
D = 'Docs/debug_log/'
mark(D+'2026-10-19/SUMMARY.md', '이 실내 조명(LED — 근적외선이 거의 없음, 추정)', '직접 원인은 같은 날 §24.1 · §24.2 — 자동 노출이 켠 프레임에 맞춰져 끈 IR 이 어두움(같은 자세 번갈이 17.7 · 상시 끔 44). 조명 가설은 확인 안 됨(문제 대장 projector-ir-alternation)')
mark(D+'2026-10-19/SUMMARY.md', 'box_points_f2y1.csv', "'남쪽 15.7 cm' 은 north_off 중앙 −15.66 = 남동에서 안 보이는 북 면 값. §14 방식(남 · 동 면)으로는 f2y1 남 +2.7 · 동 +2.2 cm 라 'f2x1 보다 훨씬 나쁨' 은 지지 안 됨(11-03 재계산, 결과 파일 없음 — 문제 대장 box-return-cells)")
mark(D+'2026-10-19/SUMMARY.md', 'jobs/fig_ir_extract.py', "mp4 'git 제외' 아님 — figures/f2y1_ir_drive.mp4 는 git 추적 중(커밋 d788c132, .gitignore 는 videos/ 만)")
mark(D+'2026-10-21/SUMMARY.md', 'mp4 는 git 제외)', "아님 — figures/f2sm2_people_block.mp4 는 git 추적 중(커밋 30581757)")
mark(D+'2026-10-20/SUMMARY.md', '게이트 B \'보드 무발행\': `/dev/ttyUSB0`', "/dev/ttyUSB0 은 라이다(cp210x, /dev/rplidar), 보드는 ttyCH341USB0(11-03 §11 · §11.1) — 다시 생긴 것은 라이다 장치라 '보드 USB 끊김' 근거 아님")
mark(D+'2026-10-20/SUMMARY.md', '| -9 포함 | 전체 -9 4 · 발행만 -9 재기동 4 | 7 · 8 |', '원문 outputs/run_shm_test.txt 는 A = KILL 4 · 발행 -9 3, B = KILL 7 · 발행 -9 7(문제 대장 camera-container-shm)')
mark(D+'2026-10-22/SUMMARY.md', '검증 f2pi1 · f2sm3 모두 3/3', '복귀 상자 칸 · 유령 A 지표를 잰 출력은 f2pi1 뿐(f2sm3 은 3/3 · 그림자 · 멈칫 · CPU 만) — 두 번째 검증으로 셀 수 없음. f2pi1 유령 A 4 칸도 벽 옆 열이라 10-21 §21.2 정의로는 0(문제 대장 ghost-cells-depth-preset)')
mark(D+'2026-10-23/SUMMARY.md', '| 상자 옆 실제 최소 여유 | 1.1 | 6.7 | 3.3 | 0.3 | **≈ 15.4 cm** |', '15.4 는 1 s 간격 표본(anal_track_dev_f2rp1.txt), 0.1 s 간격 최소 15.2(2026-10-26/outputs/compare/fig_box_compare.txt)')
mark(D+'2026-10-23/SUMMARY.md', '- 같은 구성 b910 3 회: 상자 옆 실제 여유 15.4 · 5.5 · 3.1 cm', 'f2rp1 15.4 는 1 s 표본, 0.1 s 최소 15.2(위 §17.1 표시)')
mark(D+'2026-10-23/SUMMARY.md', '- 기준 수치(b910 3 회, 상자 = 기록 위치 기준 실제 여유): f2rp1 15.4', 'f2rp1 15.4 는 1 s 표본, 0.1 s 최소 15.2')
mark(D+'2026-10-23/SUMMARY.md', '### §22.2 결과(', '이 비교는 10-26 §6.1 에서 무효 — 한 planner_server 에 Smac 변형 여러 개를 올리면 정적 동작 표를 공유해 변형 차이가 적용되지 않았다(plan_offline/run_variants.sh 4~5 행). 표 값은 2 차 실행(anal_plan_compare_2.txt, 패딩 0.01)')
mark('Docs/06_planner/SMAC_HYBRID_PLAN.md', '1. **B0 = NavFn 기준선 고정', 'f2rp1 15.4 는 1 s 표본, 0.1 s 최소 15.2')
mark('Docs/06_planner/SMAC_HYBRID_PLAN.md', '## 8. 2026-10-23 오프라인 비교 첫 판 결과', '10-26 §6.1 에서 이 비교 무효(Smac 변형이 동작 표를 공유) — 10-26 이후 판정이 대신함')
print('ok')
