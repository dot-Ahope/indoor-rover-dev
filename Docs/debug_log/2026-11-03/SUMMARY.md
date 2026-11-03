# 2026-11-03 SUMMARY

## §0 문제 대장 7 기(10-12 ~ 10-15) 착수 (사용자: "7기 진행.")
- 묶음 6 개, 카드마다 담당 하나. 각 묶음은 11-02 §12 에서 발췌를 붙인 그날 정리 페이지(10-12 · 10-13 · 10-14 · 10-15)를 길잡이로 쓰고 SUMMARY · 원문으로 다시 확인.
  - A 통신 포화(MPPI 궤적 발행 · /tf HEARTBEAT · 기록기 best effort) 새 카드 + W3 떨림 · TF 지연 이어 채움
  - B DDS 공유메모리 · 제로카피 질의(이어 채움) · 빠른 prep 새 카드 · 회전 방식 카드에 PreferForward 15 검증
  - C 상자 옆 정지 — 원인 새 카드 + 낮은 상자 기억 이어 채움
  - D 갇힘 해제 pad_relief · 실행 중 패딩 변경 멈칫 새 카드
  - E 상자 옆 정지 — 그 밖의 대책(전역 감쇠 · cost_weight · 통합 거리 · MonotoneEscape · ClearanceBand) 새 카드
  - F BT 끝 방향(TruncatePath → CopyPath) 새 카드 · F2 기준선 no5 새 카드 · 남서 정체 · Jetson Wi-Fi 이어 채움

## §1 7 기 완료 — 새 카드 7 · 이어 채움 6
- 새: `network-saturation-mppi-viz` · `prep-fast-startup` · `box-side-stall-cause` · `box-side-stall-remedies` · `pad-relief-runtime-padding` · `bt-copypath-end-yaw` · `f2-baseline-no5`. 이어 채움: tf-lag-w3-wobble · dds-shm-incident · rotation-method-track-ratio · low-box-global-memory · southwest-orient-stall · jetson-wifi-link. 묶음 보고의 링크를 머리 표 '관련 문제' 칸에 덧붙임(카드 18 장). ISSUES.md 7 기 표 · 색인 다시 생성. 카드 73 장(ISSUES.md 제외).
- F 묶음이 bag 을 PC 에서 다시 분석해 10-14 '원천 소실' 이던 끝 방향 출력을 되찾음 → `outputs/anal_path_endyaw_s1g3.txt` · `anal_path_endyaw_t1g3.txt` · `anal_path_endyaw_t1g5.txt`(스크립트 `2026-10-14/jobs/anal_path_endyaw.py`, 스크래치패드 결과를 옮김). 남서 목표: TruncatePath 시절 컨트롤러 끝 방향 0.0° · 계획기 −101.3° 직접 확인.
- 내 대조(직접 확인): 러너 `2026-10-27/jobs/job551_f0drive.sh` 46~67 행 — `/tf` best effort 재정의(54 행)가 `BAG_BE_TRAJ` 조건 안 · `prep_fast.sh` 12 행 `sed -i` 남음 · `pad_relief.py` 35 행 mode 기본 'on'(launch 기본 off, 표준 prep 은 안 띄움) · `nav2_params.yaml` 255 · 276 ClearanceBandCritic 목록에 있고 enabled false · `monotone_escape_behavior.cpp` 58~60 · `nav2_params.yaml` 804~806 풋프린트 손 입력값 · BT 108 PathBlockedAhead min_cost 99.
- **바로 고친 것 1 건(보안)**: PC 스크래치패드 실행본 `run_f0.sh` 4 행 기본 주소가 옛 `192.168.0.101`(10-14 다른 서버가 가져간 주소) — 직접 부르면 그 주소로 비밀번호를 보낼 수 있어 `192.168.0.110` 으로 바꿈(저장소 밖 파일, 되돌리기 쉬움). 저장소의 날짜 사본(2026-10-14 · 10-21 · 10-27 jobs)은 기록이라 그대로.
- 지금 코드 · 문서에 걸린 것(결정 대기, 바꾸지 않음):
  - 러너 `/tf` 재정의를 `BAG_BE_TRAJ` 조건 밖으로 · `prep_fast.sh` `sed -i` 링크 끊김 · `pad_relief.py` 기본 'on' · `chk_padding_dynamic.py` 에 '돌린 뒤 prep 재기동' 경고 없음 · MonotoneEscape 풋프린트를 코스트맵에서 읽게(데크 · 차체 상수 목록에 추가).
  - 낡은 주석: `navigation.launch.py` 229~230(pad_relief off 이유) · 133~134('4/4' → 6/6) · BT 74 행 · 러너의 기각된 '재전송 씨앗' 근거.
  - CLAUDE.md: 'prep 기본 shadow'(지금 안 띄움) · '4~5 cm 밀림'(출발점 상자만) · TEST_COURSE 'v2.2'(파일은 v2.3) · 'A/B 확정' 범위.
  - 남서 목표 `p` 재시험(BT 결함은 해소, 고친 뒤 3 회 모두 f) · F2 기준선 문서 `BASELINE_F2.md` · 태그 없음 · ClearanceBand 를 목록에서 뺄지.
