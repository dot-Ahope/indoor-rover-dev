# Docs/tools — 계속 쓰는 도구 (2026-10-13~)

도구 규약(2026-10-12 결정): 이름은 용도로 짓고 앞머리로 종류를 구분한다. 날짜 폴더 `Docs/debug_log/<날짜>/jobs/` 에는 그날만 쓴 것만 둔다.
어떤 상황에 써서 어떤 값이 나왔는지는 날짜 폴더의 `TOOLS.md` 에 적는다.

| 앞머리 | 뜻 | 실행 위치 |
|---|---|---|
| `prep_` | 스택 기동 | Jetson |
| `chk_` | 상태 확인(로버 안 움직임) | Jetson |
| `run_` | 주행 | PC → Jetson |
| `anal_` | 주행 기록 분석 | PC (일부 Jetson) |
| `fig_` | 그림 | PC |
| `up_` | 파일 전송 | PC |

## 목록

| 도구 | 하는 일 | 옛 이름 |
|---|---|---|
| `prep_fast.sh` | 정리 → 센서 → SLAM(위치 추정) → Nav2 기동, 준비될 때까지 확인. 환경 변수로 구성을 받는다. 약 60~70 s | `job972_prep_fast.sh` |
| `prep_patrol.sh` | 순회 구성(그림자 EKF 끔 · 전역 nvblox · 재계획 0.5 Hz)으로 `prep_fast.sh` 를 부른다. 인자: 궤적 발행 `lite`/`true`/`off`, 후진 벌점 | `job973_prep_lite_fast.sh` 등 |
| `chk_prep.py` | prep 확인 노드 1 개: Nav2 상태 · 좌표 변환 · 보드/EKF 주기 · 전역 지도 · 실행 중 설정값 · 배터리. 마지막 줄 `PREP_OK`/`PREP_FAIL` | `job971_prepchk.py` |
| `chk_jetson_state.sh` | 재부팅 여부 · IP · /tmp 스크립트 · 캡처 권한 · 수신 버퍼 | `job947_state.sh` |
| `anal_tf_rate.py` | bag → 10 s 칸마다 /tf 수신 Hz(포화 판정 지표: 정상 50) | `tf_rate.py` |
| `anal_navlog.py` | Nav2 로그 → 사건 종류별 횟수 · 10 s 분포 · 원문 | `navlog_pc.py` |
| `anal_proc_cpu.py` | 전 프로세스 CPU 기록 → 구간별 비교 표 | `proc_cmp2.py` |
| `anal_top.py` | top 기록 → 구간의 CPU 여유 · 상위 프로세스 | `top_eval.py` |
| `anal_udp_drops.py` | `net_<이름>.log` → 포화 전후 초당 UDP 수신 · 손실, 프로세스별 소켓 손실 | `net_anal.py` |
| `anal_rtps_pcap.py` | 루프백 캡처 → DDS 패킷을 종류 · 쓰는 쪽(토픽) · 받는 프로세스별로 집계(평상 창 vs 포화 창) | (10-13 신규) |
| `anal_rtps_onset.py` | 포화 시작 몇 초를 0.2 s 칸으로 — 토픽(기본 `rt/tf`)의 DATA·HEARTBEAT·ACKNACK 보낸 곳 | (10-13 신규) |
| `anal_rtps_acklag.py` | 쓰는 쪽 HEARTBEAT(보관 번호)와 읽는 쪽 ACKNACK(받은 번호)을 맞춰 뒤처진 읽는 쪽 찾기 | (10-13 신규) |
| `anal_bag_rates.py` | bag 여러 개의 토픽별 수신 주기 · 크기 · kB/s 를 나란히 비교 | (10-13 신규) |
| `anal_recorder_cpu.py` | proc 로그에서 bag 기록기 CPU 를 시간순으로(전체 사용률 · 주요 노드와 함께, 주행 간 비교) | (10-13 신규) |
| `fig_bag_reception.py` | 토픽 × 시간 수신 부족률 그림 + `/tf` 최대 간격(주행 간 비교) | (10-13 신규) |
| `fig_stop_costmap.py` | 지정 시각의 로컬 코스트맵 + 차체 + 라이다 점, 정지 전 풋프린트 비용 · 여유 시간열 | (10-13 신규) |
| `anal_box_history.py` | 정지 때 차체 옆 치명 칸 덩어리가 로컬 · 전역 코스트맵에 언제부터 있었는지, 로버 · 전역 경로가 얼마나 가까이 갔는지 시간순 | (10-13 신규) |
| `anal_box_layers.py` | 그 칸을 어느 층이 채웠나 — nvblox 슬라이스 값 · 라이다 점 수 · 로컬 치명 · map→odom 보정 차를 시간순 | (10-13 신규) |
| `anal_box_pass.py` | 여러 주행이 같은 구역을 지날 때의 차체 ↔ 치명 칸 여유 · 정지 여부를 나란히 | (10-13 신규) |
| `anal_odom_drift.py` | 구간별로 EKF · 휠만 · rf2o 적분이 SLAM 이동과 얼마나 어긋났나(미끄러짐 인지 평가) | (10-13 신규) |
| `anal_plan_keepout.py` | 전역 지도에서 카메라(nvblox) 장애물 둘레를 통과 금지 띠로 두껍게 했을 때의 재계획 — 경로 없음 횟수 · 상자와의 거리 | (10-14 신규) |
| `anal_mppi_sim.py` | MPPI 오프라인 시뮬(bag 의 경로 · 로컬 코스트맵 재생, CostCritic, `fpchk=1` = Nav2 방식 칸 단위 둘레 검사 · 후보 전부 충돌 집계). Jetson 에서 실행 | `job776_mppi_sim_ack.py`(10-01) |
| `fig_box_approach_video.py` | 위 내용을 지도 좌표 영상으로(전역 코스트맵 · 로컬 치명 칸 · 경로 · 카메라 시야 · 차체) | (10-13 신규) |
| `anal_traj_size.py` | bag → MPPI 궤적 메시지 크기 · 기록 주기 | `traj_size.py` |
| `anal_reverse.py` | 러너 csv → 목표별 후진 거리 · 시간 | `rev_eval.py` |
| `up_tools.sh` | 위 Jetson 쪽 도구와 주행 보조 스크립트를 /tmp 로 전송 | `up950.sh` 등 |

주행 러너(`run_f0.sh` · `run_f2c.sh` · `job551_f0drive.sh` · `job550_f0run.py`)와 범용 러너 `run_jn.sh` 는 접속 정보가 들어 있어 작업 폴더에 두고, 가린 사본을 날짜 폴더 `jobs/` 에 남긴다(이름은 다음 정리 때 `run_` 로 맞춘다).
