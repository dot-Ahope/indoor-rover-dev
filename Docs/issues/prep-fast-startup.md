# 빠른 prep — 주행 전 기동 4 분 41 초~5 분 17 초 → 약 60 s (7 시기: 10-12 §10 · §13 ~ 10-15 §30)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결(단축)** — 10-12 첫 실행 Jetson 61 s(PC 70 s), 10-13 · 10-14 prep 9 회 Jetson **55~61 s** 모두 `PREP_OK`(측정, `outputs/prep_f2*.txt`). 옛 prep 4 분 41 초~5 분 17 초는 PC 시각 값(출력 파일에 경과 시각 없음 — **원천 소실**). 남은 것: 출발 게이트 60 s · 사용자 '시작' 대기(10-12 §10 의 4 · 6 번 — 7 기 미착수), prep 이 설치본 `nav2_params.yaml` 을 `sed -i` 로 고쳐 링크를 끊는 결함(10-15 §30 발견 → 배포 도구 쪽 **우회**, prep 은 지금도 `sed -i`) | 10-12 §10 · §11.1 · §13 · §13.1 · §14, 10-13 §0~§1(상시 도구로), 10-14 §24~§25(직전 기록 보관), 10-15 §30(링크 끊김), 이후 10-19 ~ 10-23 확장(8 기 — §2 '8 기' 줄들: `SENSORS_ADD` · cuVSLAM 고아 정리 · `fastdds shm clean` · `PREP_POSE` · `ODOM=vslam`, prep 63~79 s), 10-26 ~ 는 다음 시기 | [10-12 §10](../debug_log/2026-10-12/SUMMARY.md) — 사용자 'prep 과 prep → 출발 시간을 줄일 방법' | 10-12 [`job971_prepchk.py`](../debug_log/2026-10-12/jobs/job971_prepchk.py) · [`job972_prep_fast.sh`](../debug_log/2026-10-12/jobs/job972_prep_fast.sh) · [`job973_prep_lite_fast.sh`](../debug_log/2026-10-12/jobs/job973_prep_lite_fast.sh)(커밋 `1aa5d922`) → 10-13 [`Docs/tools/chk_prep.py`](../tools/chk_prep.py) · [`prep_fast.sh`](../tools/prep_fast.sh) · [`prep_patrol.sh`](../tools/prep_patrol.sh)(커밋 `03008a09`) → 10-14 `prep_fast.sh` 기록 보관(커밋 `abafbe2f`) | [DDS 공유메모리 사고](dds-shm-incident.md)(정리 단계 TERM → −9 · `fastdds shm clean` 의 근거, `job240_clean.sh` 제정) · [주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md)(출발 게이트 30 s) · [통신 포화 · MPPI 궤적 발행](network-saturation-mppi-viz.md)(같은 날 · `ros2` 조회의 탐색 폭주) · [보드 연결 · 세션](board-link-microros-session.md)(에이전트 없으면 빠른 prep 은 중단) · [실행 중 패딩 변경](pad-relief-runtime-padding.md)(`prep_patrol_pad.sh` · '패딩을 바꿨으면 prep 으로 재기동') · [낮은 상자 · 전역 기억](low-box-global-memory.md)(10-14 §24 '이상 경로' 를 못 본 이유 = nav2.log 덮어씀) · [상자 옆 정지 대책](box-side-stall-remedies.md)(10-15 §30 통합 거리 시험 때 링크 끊김 발견) · [F2 순회 · 위치 점프](f2-patrol-loc-jump.md)(옛 prep 계보 job726 · 731 · 780) · [주행 전 검사와 운용 사고](drive-ops-1019-1023.md)(8 기 — 출발 위치 검사 · prep 실패 유형) · [카메라 ↔ 컨테이너 공유메모리](camera-container-shm.md) (8 기) · [주행 전 검사 정리](drive-gate-consolidation.md) · [Smac Hybrid 채택](smac-hybrid-adoption.md) (9 기) |

**한 줄**: 10-12 하루에 주행 10 회를 하며 매번 prep 이 4 분 41 초~5 분 17 초(PC 시각) 걸렸다. 사용자 요청으로 시간을 쪼개 보니(스크립트 읽기 기준 **추정**) 고정 `sleep` 과 `ros2` CLI 조회 약 25 회(회당 3~15 s, 부를 때마다 DDS 참여자 탐색)가 대부분이었다(§10). 사용자가 단축안 6 개 중 '조회를 한 프로세스로' · '고정 대기를 될 때까지 폴링' 2 개를 골랐고(§11.1), 확인 노드 `job971_prepchk.py`(rclpy 참여자 1 개 — 수명 주기 · TF · 주기 · 전역 지도 · 실행 중 파라미터) + 기동 순서는 그대로 둔 `job972_prep_fast.sh` 로 첫 실행이 Jetson 61 s · `PREP_OK`(§13), 그 스택으로 f2l2 3/3 성공(§13.1). 10-13 에 `Docs/tools/prep_fast.sh` · `chk_prep.py` · `prep_patrol.sh`(운용 구성 래퍼)로 고정 이름이 됐고 10-13 · 10-14 9 회 모두 55~61 s. 10-14 에는 prep 이 앞 주행의 `nav2.log` 를 지워 이상 경로 원인을 못 본 일로 직전 기록을 `/tmp/logkeep` 에 8 벌 보관하게 했다(§25). 10-15 에는 prep 의 `sed -i`(PreferForward 값 덮기)가 colcon `--symlink-install` 링크를 일반 파일로 바꿔 src 수정이 설치본에 안 따라오는 것을 발견했다(§30).

## 1. 증상
- 10-12 prep 소요(PC 시각, SUMMARY 서술 — 출력 파일엔 경과 시각이 없어 **원천 소실**): §9.1 `job969_prep_j.sh` 14:53:44~14:58:32 = **4 분 48 초** · §11.1 15:16:48~15:21:29 = **4 분 41 초** · §12.1 `job970_prep_lite.sh` 15:35:00~15:40:17 = **5 분 17 초**(launch 배포 · 빌드 포함).
- 출발 게이트 60 s(§10: 15:01:51 → 15:02:51 — PC 시각 원문 없음). 같은 날 f2l2 러너 기록으로는 게이트 시작 15:53:27 → 주행 15:54:28 = **61 s**(측정, [`f0_f2l2_runner.log`](../debug_log/2026-10-12/outputs/f0_f2l2_runner.log) 1 · 10 행).
- 그 앞 파일 전송 · 기동 10~20 s, 내 선언 · 보고와 사용자 '시작' 대기(§10 서술).
- prep 출력 원문에는 '시간' 이 없고 결과 줄만 있다 — 예 [`j969_prep.txt`](../debug_log/2026-10-12/outputs/j969_prep.txt) 끝 줄 `정지 부하(20 s 뒤): 14.56 9.34 6.95 · 유휴 56.7 id`.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 09-11 §5.4 | 사용자 '설정을 깔끔하게 초기화하지 못해 재부팅했다' → 기동 절차 고정 | — | `job240_clean.sh` 제정(정리 → base → sensors → slam → nav2 → 설정 검증 → 비우기 → 재마킹 대기) | [DDS 카드 §2](dds-shm-incident.md) |
| 10-01 §5 · §7 · §8.1 · §8.33 | F2 순회 prep 을 래퍼로 쌓음: `job726_prep_map.sh`(지도 · 위치 추정 모드 → job240) → `job731_f2_prep.sh`(slamloc + `job697_restore_chk.py` + 배터리) → `job780_prep_navmap.sh`(+ 정적 지도 층 · `/map_nav` 확인) | — | 10-12 까지의 '옛 prep' 계보 | [`2026-10-01/jobs/`](../debug_log/2026-10-01/jobs/) |
| 10-12 §1.1 ~ §12.1 | 주행마다 옛 prep(구성별 래퍼 `job963` · `964` · `966` · `969` · `970` → `job780`) | 4 분 41 초~5 분 17 초(PC 시각, **원천 소실**). §4.1 `job963` 은 'Terminated' 한 줄만 남음(거르는 파이프가 정리 중 끊긴 것으로 **추정**) | — | [`j963_prep5.txt`](../debug_log/2026-10-12/outputs/j963_prep5.txt) · [`j969_prep.txt`](../debug_log/2026-10-12/outputs/j969_prep.txt) · [`j970_prep.txt`](../debug_log/2026-10-12/outputs/j970_prep.txt) |
| 10-12 §10 | 사용자 'prep 과 prep → 출발 시간을 줄일 방법' → 스크립트 읽기로 구성 추정 | 고정 대기 합 약 108 s(`job240`: 3 + 12 + 28 + 15 + 5 + 30 + 15) · `ros2` 조회 약 25 회(회당 3~15 s, 합 90~120 s) · 내 확인 단계 대기 35 s | 단축안 6 개(효과 큰 순): ① 구성 안 바뀌면 자세 초기화만(30~40 s 예상) ② 조회를 한 프로세스로(−60~90 s) ③ 고정 대기 → 폴링(−40~60 s) ④ prep 확인과 출발 게이트 합치기(30 s 규칙 재검토) ⑤ 다시 놓지 않기 ⑥ 묶음 사전 승인. 제안: 단계별 시각부터 찍고 2 · 3 먼저. ⚠ 108 s 는 이 경로에서 안 타는 분기(base 재기동 12 s · 매핑 5 s)를 넣은 값(§5.3) | SUMMARY §10 · [`2026-10-06/jobs/job240_clean.sh`](../debug_log/2026-10-06/jobs/job240_clean.sh)(저장된 마지막 판) |
| 10-12 §11.1 | 사용자 결정 'prep 단축은 앞 2 가지 적용하자' | — | §10 의 ② · ③ 을 f2k1 뒤에 작업 | SUMMARY §11.1 |
| 10-12 §13 | 확인 노드 · 빠른 prep · 운용 구성 래퍼 작성 → 첫 실행(로버 안 움직임) | **Jetson 61 s**(PC 15:51:03~15:52:13 = 70 s): 정리 10 s · 자이로 캘리브까지 19 s · slam · nav2 기동 1 s · 준비 대기 13.8 s · 비우기 + 재마킹 15 s · 나머지 약 2 s. `PREP_OK`, Nav2 5 개 active, `/wheel_odom 25.0 · /odometry/filtered 30.0 · /tf 49.7 Hz`, map→base (−0.006, −0.007) | 조회 묶기 + 폴링으로 충분. 결함 1 건: 'SHM 오류' 줄 수 계산이 빈 값(§5.1) → 고침. 남긴 대기: 재마킹 15 s(09-11 '클리어 직후 옛 데이터' 대책) · 자이로 캘리브 약 19 s | [`j973_prep_fast.txt`](../debug_log/2026-10-12/outputs/j973_prep_fast.txt) · `job971` · `job972` · `job973`(§9) |
| 10-12 §13.1 | 빠른 prep 스택으로 f2l2(lite 반복) | 3/3 성공(52.1 · 47.0 · 102.6 s), 포화 없음. prep 끝 15:52:13 → 게이트 15:53:27 → 출발 15:54:28 = **2 분 15 초**(파일 전송 + 게이트 61 s + 사용자 '시작' 대기) | 빠른 prep 으로 띄운 스택에서도 정상 | [`f0_f2l2_runner.log`](../debug_log/2026-10-12/outputs/f0_f2l2_runner.log) |
| 10-12 §14 | 마무리 — 다음 후보 ② '출발 게이트 60 s 줄이기(§10-4: 게이트를 확인 노드 1 개로, DDS 30 s 규칙 재검토)' | — | 7 기에는 미착수 | SUMMARY §14 |
| 10-13 §0 ~ §1.1 | 도구 규약 적용: `job972` → `Docs/tools/prep_fast.sh`, `job971` → `chk_prep.py`, `job973` 을 인자 받는 `prep_patrol.sh VIZ FWD` 로 | f2m1 prep `prep_patrol.sh true 15.0` PC 10:06:00~10:07:04 = 64 s, Jetson 출력 `⏱ +55 s prep 끝 — PREP_OK` | 상시 도구로 고정 | [`prep_f2m1.txt`](../debug_log/2026-10-13/outputs/prep_f2m1.txt) · 커밋 `03008a09` |
| 10-13 · 10-14 | 주행마다 새 스택(prep) | Jetson '+N s prep 끝' : f2m1 55 · f2n1 59 · f2o1 59 · f2p1 61 · f2q1 59 · f2r1 59 · f2r2 60 · f2s1 61 · f2t1 60 — 전부 `PREP_OK`(정리 5~10 s · 자이로 19~20 s · 확인 29~31 s) | 단축 유지(측정 9/9) | `2026-10-13/outputs/prep_f2{m,n,o,p,q}1.txt` · `2026-10-14/outputs/prep_f2{r1,r2,s1,t1}.txt` |
| 10-14 §24 | 이상 경로(B 16:30:06.6)의 계획기 · 코스트맵 경고를 보려 했으나 A2 전 prep 이 `/tmp/nav2.log` 를 새로 써 볼 수 없음 ✘ | — | 제안 ① 'prep 전에 nav2.log 를 보관' | [10-14 SUMMARY §24](../debug_log/2026-10-14/SUMMARY.md) · [낮은 상자 카드](low-box-global-memory.md) |
| 10-14 §25 | 사용자 '진행' → `prep_fast.sh` 에 직전 `nav2 · slam · sensors` 기록 보관(최근 8 벌) | Jetson `/tmp/prep_fast.sh` md5 = 저장소 판(602e2da9…) 확인 뒤 교체. 보관 부분만 실행: 3 개 보관 ✔(A2 의 nav2.log 118 kB). sensors.log 8 MB → 8 벌 ≈ 70 MB, /tmp 여유 149 GB | 다음 prep 부터 직전 기록 보관 | [`chk_prep_md5.sh`](../debug_log/2026-10-14/jobs/chk_prep_md5.sh) · [`chk_logkeep.sh`](../debug_log/2026-10-14/jobs/chk_logkeep.sh)(둘 다 출력 파일 없음 — SUMMARY 서술이 전부) · 커밋 `abafbe2f` |
| 10-15 §0 | 재부팅으로 Jetson `/tmp` 기동 스크립트 6 개 소실 → 저장소 판 5 개 재전송(러너가 스스로 올리는 job551 제외) | — | 운용 규칙(CLAUDE.md 네트워크 항목) | [10-15 SUMMARY](../debug_log/2026-10-15/SUMMARY.md) 11 · 15 행 |
| 10-15 §30 | nvblox 통합 거리 1.0 · ClearanceBandCritic 끔 배포 중 | 설치본 `nav2_params.yaml` 이 src 링크가 아니라 일반 파일 — 설치본이 `enabled: true` 로 남아 있었음 | **prep_fast 의 `sed -i` 가 링크를 끊는다**(측정). 배포 도구에 링크 복구. 그간 주행은 '빌드 → prep' 순서였거나 내용이 같아 영향 없었음(§29 빌드 16:59 · 17:2x → prep 17:01 · 17:31) | [`up_cfg_intdist.sh`](../debug_log/2026-10-15/jobs/up_cfg_intdist.sh) 7~10 행 |
| **8 기** 10-19 §16 | `prep_patrol.sh` 에 `SENSORS_ADD`(센서 launch 인자 추가 — 예 `emitter_flash:=true stereo_fps:=30` 프로젝터 번갈이) | f2y1 IR 기록 주행 prep 에 `SENSORS_ADD="emitter_flash:=true"`(§19) | 구성 실험을 prep 을 고치지 않고 인자로 | 커밋 `d1edc058` · 지금 [`prep_patrol.sh`](../tools/prep_patrol.sh) 15 · 17 행 |
| 10-20 §6 | 정리 단계 `PATS` 에 `cuvslam_up.sh vslam_twist`, 컨테이너 안 cuVSLAM 고아를 `docker exec … pkill -INT` → 3 s → `-9` 로 직접 정리, 끝 줄에 cuVSLAM · vslam_twist · ekf_vslam 수 | (고아가 실제로 남은 사례는 SUMMARY · TOOLS 에 없음 — 코드 주석 '래퍼가 -9 로 죽으면 컨테이너 안 cuVSLAM 이 고아로 남는다' 가 전부, **원문 없음**) | 그림자 cuVSLAM 구성의 재기동 대비 | 커밋 `1269e3e5` · 지금 [`prep_fast.sh`](../tools/prep_fast.sh) 24 · 37~39 · 73 행 |
| 10-20 §8.4 | 사용자 'prep 이 오래 걸리는 이유' → 지금 구성 1 회 측정 | 총 **60 s**: 정리 9 s(26 프로세스) · 센서 19 s(카메라 초기화 → EKF 8 s 타이머 → 자이로 2000 샘플 = 200 Hz × 10 s) · SLAM · Nav2 띄우기 0~1 s · 확인 30 s(폴링 ≈ 15 + 재마킹 고정 15) — `⏱ +9 s 정리 끝` · `+28 s 자이로 캘리브 끝` · `+59 s 확인 끝` · `+60 s prep 끝 — PREP_OK` | 7 기 61 s 와 같은 구성. 남은 단축 후보 = 재마킹 15 s · EKF 8 s 타이머(§10 '미해결', 8 기 미착수). 시간 재려고 prep 을 한 번 더 돌린 것이라 그 앞의 위치 추정 값은 무효(사용자 지적 — 다시 재서 0.48°) | [`chk_prep_timing.txt`](../debug_log/2026-10-20/outputs/chk_prep_timing.txt) |
| 10-20 §9.1 · §9.5 | 정리 뒤 **`fastdds shm clean`**(아무도 안 잡은 고아 세그먼트만 지움; `rm -f /dev/shm/fastrtps_*` 는 금지 — 살아 있는 참가자 파일까지 지움) · 남은 수 기록 | S3 재기동 10 회: 매 회 고아 1~2 세그먼트 정리, 남은 10~12 개 = 쓰는 중, 10/10 PREP_OK(카메라 · nvblox · cuVSLAM `-9` 섞어도 다음 prep 에서 복귀) | 카메라 ↔ cuVSLAM SHM 구성의 prep 쪽 대비 — 내용은 [카메라 컨테이너 SHM](camera-container-shm.md) · [DDS 공유메모리 사고](dds-shm-incident.md) | 커밋 `8e31e2b1` · [`run_shm_restart.txt`](../debug_log/2026-10-20/outputs/run_shm_restart.txt) · 지금 `prep_fast.sh` 41~43 행 |
| 10-21 §1 · §2 | `chk_prep.py` 에 **출발 위치 추정 검사 `PREP_POSE`**(기본 `0,0,0`, ±0.10 m · ±2° 밖이면 `PREP_FAIL`) | 통과 `위치 차 0.008 m · yaw 차 +0.8° → 통과` · 불합격 경로 `PREP_POSE=0,0,10` → `yaw 차 -9.2° → ★ 불합격` · `종료 코드 1`. 10-21 ~ 10-23 저장된 prep 26 회: 통과 23 · 실제 불합격 3(2.5° · 81° · 2.8°) | 10-20 출발 SLAM 21° · −41° 오류를 주행 전에 거름 → [주행 전 검사와 운용 사고](drive-ops-1019-1023.md) §3 · §8.1 | 커밋 `e43798c2` · [`prep_sm_1021_1.txt`](../debug_log/2026-10-21/outputs/prep_sm_1021_1.txt) · 지금 `chk_prep.py` 27~29 · 122~129 행 |
| 10-21 §5 | 주소 변경 뒤 prep 이 보드 토픽 0 Hz 로 실패 | 2 단계(base)는 에이전트 컨테이너 **수**와 컨테이너 전체 로그의 '세션 수립' 줄 수만 본다 → 옛 세션 1 건이 있으면 지나감, 판정은 6 단계 `/wheel_odom` 주기 | prep 은 에이전트를 재시작하지 않는다(설계 그대로) — 순서 = 에이전트 재시작 → 보드 RESET → prep | [`prep_sm_1021_2.txt`](../debug_log/2026-10-21/outputs/prep_sm_1021_2.txt) · 지금 `prep_fast.sh` 53~55 행 · [보드 세션 카드](board-link-microros-session.md) |
| 10-22 §5.3 | prep 3 회째 `PREP_FAIL` — 150 s 동안 Nav2 수명 주기 활성화 멈춤 | `controller=inactive planner=inactive bt_navigator=unconfigured behavior=inactive nav_map=active`, nav2.log `failed to send response to /…/get_state (timeout)` | 원인 미확인. `chk_prep` 의 조회 재시도에 백오프가 없다(코드 70~88 행 — 응답이 오면 0.1 s 뒤 다시) — 기여 여부 미확인 | [`chk_prep_fail_1022.txt`](../debug_log/2026-10-22/outputs/chk_prep_fail_1022.txt) · [운용 사고 카드 §3](drive-ops-1019-1023.md) |
| 10-22 · 10-23 | 8 기 prep 소요(Jetson `⏱ … prep 끝`, 저장된 출력 28 개) | 성공 · 위치 검사 불합격 prep **63~79 s**(10-21 63~73 · 10-22 63~79 · 10-23 63~68) — 7 기 55~61 s 보다 약 5~15 s 김(그림자 · on cuVSLAM · SHM 구성 기동분으로 **추정**, 단계별 비교 안 함). 준비 실패 prep 은 150 s 한도까지 기다려 185 · 187 s | 단축은 유지, 구성이 커진 만큼 늘어남 | `2026-10-21/outputs/prep_sm_1021_*.txt` · `2026-10-22/outputs/prep_*_1022_*.txt` · `2026-10-23/outputs/prep_op_1023_2.txt` |
| 10-23 §16 | `prep_patrol.sh` 기본 오도메트리 `ODOM=vslam`(`emitter_off:=true vslam:=on dds_shm:=true`), 옛 구성 `ODOM=rf2o`, `REPLAN_HZ` 환경(기본 0.5) | — | 사용자 결정 '`vslam on` 기본 채택' — 내용은 [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md) | 커밋 `dcfdb0b6` · 지금 `prep_patrol.sh` 10~14 · 17 행 |
| 이후(10-26 ~) | **다음 시기에서 채움** — 포인터: 10-26 `NAV_ADD` · 10-27 파라미터 조회를 `chk_prep.py` 로 통합 · 출발 게이트 한 노드 `chk_drive_gate.py`(`a813ac8a` — §10 의 ④) · 11-03 §3 PreferForward 편집을 `--follow-symlinks` · 값이 같으면 안 건드림(커밋 `ce1a0bee` — §5.2 의 `sed -i` 링크 끊김 대책) | — | — | `git log -- Docs/tools/prep_fast.sh Docs/tools/chk_prep.py Docs/tools/prep_patrol.sh` |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| prep 시간의 대부분은 고정 `sleep` 과 `ros2` CLI 조회 | 빠른 prep 의 단계별 시각(§13) | 조회 25 회 → 노드 1 개, 고정 대기 → 폴링으로 4 분 41 초~ → 61 s. 남은 것 = 정리 10 · 자이로 19 · 준비 13.8 · 재마킹 15 s | **지지**(전후 측정. 단 '전' 은 PC 시각 원천 소실) |
| 폴링으로 바꿔도 스택은 같은 상태로 뜬다 | f2l2 주행 · 이후 9 회 prep | f2l2 3/3 · 포화 없음, 이후 9/9 `PREP_OK` 와 주행 | **지지**(통과 폭 감사 job248 · 지도 복원 확인 job697 은 뺐으므로 그 확인은 없음) |
| 재마킹 15 s 는 줄일 수 있다 | (시험 안 함) | 09-11 '클리어 직후 옛 데이터' 사고 대책이라 유지 | **미시험** |
| prep 의 `sed -i` 는 무해 | 10-15 §30 설치본 확인 | 링크 → 일반 파일, 이후 src 수정이 설치본에 안 감 | **기각**(§5.2) |

## 4. 조치와 효과
- **확인 노드 1 개**(`job971_prepchk.py` → `Docs/tools/chk_prep.py`): `ros2 lifecycle get` · `param get` · `topic hz` · `tf2_echo` 약 25 회(회당 새 참여자 · 탐색)를 rclpy 노드 하나로. 효과: 조회 시간 + 탐색 폭주(10-12 §9.2) 감소.
- **폴링**: sensors 는 `gyro bias calibrated` 줄, slam 은 기동 로그 줄, Nav2 는 수명 주기 active 를 기다림. 효과: 61 s(첫 실행) · 55~61 s(9 회).
- **기동 순서 · 정리 방식은 그대로**(job240): base 유지 → sensors → slam(위치 추정) → nav2. 에이전트가 없으면 빠른 prep 은 base 를 띄우지 않고 중단(`exit 1`, job240 전체 절차 안내).
- **뺀 것**: 통과 폭 감사(job248) · 지도 복원 확인(job697) — 순회에 안 씀(§13).
- **직전 기록 보관**(10-14 §25): `/tmp/logkeep/<시각>_{nav2,slam,sensors}.log`, 최근 8 벌. 한계: `/tmp` 라 재부팅이면 사라짐.
- **지금 저장소(카드 작성 중 확인)**:
  - [`Docs/tools/prep_fast.sh`](../tools/prep_fast.sh) 12 행 `sed -i "s/\(PreferForwardCritic: {enabled: true, cost_power: 1, cost_weight: \)[0-9.]*/\1${FWD:-15.0}/" $Y` — **지금도 설치본을 `sed -i`**(링크 끊김 결함 남음, 링크 복구는 배포 도구 쪽 `up_cfg_intdist.sh` 9 행에만).
  - 14 행 스크립트 자신의 참여자도 `fastdds_udp_only.xml`, 25~29 행 TERM → 1 s 간격 최대 15 회 확인 → 남으면 −9 + 3 s, 36 행 `fastdds shm clean`(10-20), 39~42 행 기록 보관 8 벌, 48 행 에이전트 없으면 `exit 1`, 51 행 자이로 대기 최대 80 × 0.5 = 40 s, 55 행 slam 대기 최대 60 × 0.5 = 30 s, 59 행 `chk_prep.py $WAIT 150`.
  - [`Docs/tools/chk_prep.py`](../tools/chk_prep.py) 29 행 `POS_TOL, YAW_TOL = 0.10, 2.0`(10-21), 31~42 행 `PARAMS`(10-12 의 3 노드 → 지금 8 노드: controller 7 개 · global_costmap 3 · stuck_monitor · planner SmacHybrid 6 · camera 프리셋 · ekf `odom1` · slam `mode` · `transform_timeout` · bt `default_nav_to_pose_bt_xml`), 104~107 행 판정 문턱(그대로: 주기 < 20 Hz, 전역 지도 칸 수 ≤ 20000).
  - ⚠ (11-03, 8 기 채울 때 확인) 위 행 번호는 10-30 무렵 판 기준이다. 11-03 §3(커밋 `ce1a0bee`)에 PreferForward 편집이 바뀌어 지금 `prep_fast.sh` 는 12~19 행이 '링크가 아니면 경고 · 값이 다를 때만 `sed -i --follow-symlinks`' 이고, 이하 행이 7 줄씩 밀렸다(`fastdds shm clean` 43 · 기록 보관 46~49 · 에이전트 없으면 `exit 1` 55 · 자이로 대기 58 · slam 대기 62 · `chk_prep.py` 66 행). `chk_prep.py` 의 위치 검사는 122~129 행.
  - [`Docs/tools/prep_patrol.sh`](../tools/prep_patrol.sh) 10~14 행 `ODOM` 기본 `vslam`(`emitter_off:=true vslam:=on dds_shm:=true`), `rf2o` 이면 10-12 구성(`rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel`), 17 행 `global_camera:=nvblox replan_hz:=${REPLAN_HZ:-0.5}`.

## 5. 내 실수 · 어긋남
### 5.1 'SHM 오류' 줄 수 계산 결함(10-12 §13 첫 실행)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | prep 끝에 세 로그의 SHM 오류 줄 수를 DDS 조회 없이 찍기 |
| 본 것 | 첫 실행 출력 `navmap_ensure: active (1) · no map 경고 0 · SHM 오류 `(빈 값) |
| 처음 추론 | (출력 형식 오류 — 여러 파일 grep 출력이 `파일:수` 줄 여러 개라 한 값이 안 됨, SUMMARY §13 '여러 파일 grep 출력 형식') |
| 의심한 이유 | 빈 칸 |
| 판별 시험 | 코드 읽기 |
| 결론 | 세 파일을 `cat … \| grep -ac` 로 합쳐 한 수로. 확인 항목 자체에는 영향 없음. 저장된 `job972` 는 고친 판이다(그래서 저장된 스크립트와 `j973` 출력이 맞지 않는다) |
| 다음에 알아보는 법 | 여러 파일에 `grep -c` 를 쓰면 파일마다 한 줄이 나온다 — 합계가 필요하면 `cat` 으로 묶거나 `awk` 로 더한다 |
| 스크립트 핵심 | 고친 판 `SHM 오류 $(cat /tmp/nav2.log /tmp/sensors.log /tmp/slam.log \| grep -ac 'RTPS_TRANSPORT_SHM\|init_port')`([`job972_prep_fast.sh`](../debug_log/2026-10-12/jobs/job972_prep_fast.sh) 51 행 · 지금 `prep_fast.sh` 63 행). 고치기 전 판은 원문 없음 |
| 나온 결과 | `j973` `  navmap_ensure: active (1) · no map 경고 0 · SHM 오류 ` → 10-14 f2t1 `  navmap_ensure: active (1) · no map 경고 0 · SHM 오류 0` |
| 데이터 | [`j973_prep_fast.txt`](../debug_log/2026-10-12/outputs/j973_prep_fast.txt) · [`prep_f2t1.txt`](../debug_log/2026-10-14/outputs/prep_f2t1.txt) |

### 5.2 prep 의 `sed -i` 가 설치본 링크를 끊음(10-12 부터, 10-15 §30 발견)
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 주행마다 PreferForward 값을 prep 인자(`FWD`)로 확실히 맞추기 — 10-12 §4 · §5 의 5 / 15 비교에서 시작해 `job963` · `964` · `969` · `970` · `job972` 모두 설치본 yaml 에 `sed -i` |
| 본 것 | 10-15 §30: src 를 고쳐도 설치본에 `ClearanceBandCritic: {enabled: true` 가 남아 있었음 |
| 처음 추론 | (그때까지) 설치본은 `--symlink-install` 로 src 를 가리키므로 고쳐도 같은 파일 |
| 의심한 이유 | 배포 뒤 확인 줄이 src 와 다른 값 |
| 판별 시험 | 설치본이 링크인지(`[ -L $I ]`) |
| 결론 | `sed -i` 는 임시 파일을 만들어 원래 경로로 옮기므로 **링크가 일반 파일로 바뀐다**(측정 — 링크 아님 확인). 그 뒤 src 수정은 다음 빌드나 링크 복구 전까지 설치본에 안 간다. 그간 주행은 '빌드 → prep' 순서였거나 내용이 같아 영향 없었음(10-15 §30 대조) |
| 다음에 알아보는 법 | 설치본을 고치는 줄이 있으면 배포 뒤 `readlink` · `diff src install` 을 같이 찍는다. 값을 바꾸려면 설치본 대신 launch 인자 · 파라미터 덮기로 |
| 스크립트 핵심 | `sed -i "s/\(PreferForwardCritic: …cost_weight: \)[0-9.]*/\1${FWD:-15.0}/" $Y`(`prep_fast.sh` 12 행 — 지금도 있음) · 복구 `[ -L $I ] \|\| { rm -f $I && ln -s $D/nav2_params.yaml $I && echo "설치본 nav2_params 링크 복구"; }`([`up_cfg_intdist.sh`](../debug_log/2026-10-15/jobs/up_cfg_intdist.sh) 9 행) |
| 나온 결과 | 10-15 §30 서술 '이번에 설치본이 enabled: true 로 남아 있었음'(배포 출력 파일 없음 — 서술이 전부) |
| 데이터 | [10-15 SUMMARY §30](../debug_log/2026-10-15/SUMMARY.md) |

### 5.3 기타 어긋남(원문 대조)
1. **§10 '고정 대기 합계 약 108 s(3 + 12 + 28 + 15 + 5 + 30 + 15)'**: 저장된 마지막 `job240_clean.sh`(10-06 판)에서 12 s 는 '에이전트 없음 → base 기동' 분기(59 행), 5 s 는 `MAPPING=1` 분기(127 행)라 F2 순회 prep 에선 안 탄다. 3 s 는 `ros2 bag record` 가 있을 때만(30 행). 실제 이 경로의 고정 대기는 28 + 15 + 30 + WAIT 15 = **88 s**(+ 3) — 코드 읽기, 10-12 Jetson `/tmp` 판이 10-06 판과 같다는 것은 **추정**. 여기에 래퍼 `job969` 의 `sleep 15` · `sleep 20`(= §10 '내 확인 단계 대기 35 s')이 더해진다.
2. **`chk_prep.py` 독스트링 '전역 코스트맵에 저장 지도(크기 > 100×100)'** vs 코드 `n.gcm[0] * n.gcm[1] <= 20000` 이면 기다림 — 100×100 = 10 000 이 아니라 20 000 칸이 문턱(`job971` 부터 같음). 실제 지도 333×242 = 80 586 칸이라 판정엔 영향 없음.
3. **PC 70 s vs Jetson 61 s · 64 s vs 55 s**: SUMMARY · 정리 페이지의 '70 s' · '64 s' 는 PC 쪽 시각(전송 · ssh 포함), 출력의 `⏱` 은 Jetson `date` 기준. 둘 다 맞지만 다른 것을 잰다. 정리 페이지 `2026-10-12_report.html` 은 'PC 기준 70 s · 옛 prep 4 분 41 초~5 분 17 초: 원천 소실' 로 이미 표시.
4. **`prep_fast.sh` 주석 '10-14 §24'**(39 행 위) vs 결정 §25: §24 는 제안, §25 가 사용자 결정 · 구현 — 둘 다 맞는 참조.
5. **`chk_logkeep.sh` · `chk_prep_md5.sh` 출력 없음**: '3 개 보관 ✔ · md5 602e2da9…' 는 SUMMARY 서술뿐(**원천 소실**, README §2.3 의 `| tee` 규칙 전).

## 6. 남은 것
- (8 기) 재마킹 15 s · EKF 8 s 타이머 단축 — 10-20 §8.4 · §10 에 후보로 다시 적혔지만 8 기 미착수. 구성이 커져 prep 이 63~79 s 로 늘었다.
- (8 기) `chk_prep.py` 의 수명 주기 · 파라미터 조회 재시도에 백오프 없음 — 10-22 §5.3 활성화 멈춤과의 관계 미확인. 준비 실패 때는 출발 위치 검사 줄이 안 나옴.
- 출발 게이트 60 s · 'DDS 참여자 생성 뒤 30 s' 규칙(10-12 §10 ④) — 7 기 미착수. 10-27 `chk_drive_gate.py` 로 이어짐(그 시기 카드).
- §10 ① 자세 초기화만 하는 가벼운 prep · ⑤ 다시 놓지 않기 · ⑥ 사전 승인 — 7 기 미시험.
- 재마킹 15 s · 자이로 캘리브 19 s — 그대로.
- `sed -i` 링크 끊김 — prep 쪽은 그대로(§4 지금 저장소).
- 빠른 prep 에서 뺀 통과 폭 감사 · 지도 복원 확인 — 필요할 때 따로.
- 직전 기록 보관은 `/tmp` — 재부팅이면 사라짐. 주행 이름이 아니라 보관 시각으로 저장되므로 어느 주행의 기록인지는 시각으로 맞춰야 함.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| 옛 prep(10-12) | `job963_prep5` · `job964_prep15` · `job966_prep_lean` · `job969_prep_j` · `job970_prep_lite` → `job780` → `job731` → `job726` → `job240` | [`2026-10-12/jobs/`](../debug_log/2026-10-12/jobs/) · [`2026-10-01/jobs/`](../debug_log/2026-10-01/jobs/) · [`2026-10-06/jobs/job240_clean.sh`](../debug_log/2026-10-06/jobs/job240_clean.sh) → `j963` · `j964` · `j966` · `j966b` · `j969` · `j969b` · `j970` |
| 빠른 prep 첫 판 | `job971_prepchk.py` · `job972_prep_fast.sh` · `job973_prep_lite_fast.sh` · 전송 `up972.sh` | `2026-10-12/jobs/` → [`j973_prep_fast.txt`](../debug_log/2026-10-12/outputs/j973_prep_fast.txt) |
| f2l2 | 빠른 prep 스택 첫 주행(3/3) | [`f0_f2l2_runner.log`](../debug_log/2026-10-12/outputs/f0_f2l2_runner.log) · `bags/bag_f2l2.tgz`(PC 로컬) |
| 상시 판 | `prep_fast.sh` · `chk_prep.py` · `prep_patrol.sh` | [`Docs/tools/`](../tools/) |
| 10-13 · 10-14 prep 9 회 | 55~61 s | `2026-10-13/outputs/prep_f2m1 · n1 · o1 · p1 · q1.txt` · `2026-10-14/outputs/prep_f2r1 · r2 · s1 · t1.txt` |
| 기록 보관 | `chk_prep_md5.sh` · `chk_logkeep.sh` | [`2026-10-14/jobs/`](../debug_log/2026-10-14/jobs/)(출력 없음) |
| 그림 | W3 후진 · prep 시간(PC 기준 288 · 281 · 317 s → 70 s, 값은 `fig_1012.py` 75 행에 손으로 적음) | [`2026-10-12_reverse_prep.png`](../04_navigation/figures/2026-10-12_reverse_prep.png) |
| 링크 복구 | `up_cfg_intdist.sh` | [`2026-10-15/jobs/up_cfg_intdist.sh`](../debug_log/2026-10-15/jobs/up_cfg_intdist.sh) |

## 8. 도구 해설
**공통**: 전부 Jetson 에서 실행(PC WSL → 러너 · `run_jn.sh`, 실행 투명성 규약은 README §4). 스크립트는 저장소에서 Jetson `/tmp` 로 올려 부른다 — 재부팅이면 사라져 다시 올림.

### 8.1 옛 prep — `job240_clean.sh` 와 래퍼 (Jetson, bash)
- `job240_clean.sh`(10-06 판): 정리(PATS TERM → 15 s → −9) → base(에이전트 · 보드 송수신이 정상이면 생략, 아니면 기동 + 12 s, 보드 무발행이면 `exit 1`) → sensors + **`sleep 28`** → `/odometry/filtered` hz → slam + **`sleep 15`** → `tf2_echo map odom` → nav2 + **`sleep 30`** → `lifecycle get` 4 회 → 설정 검증(`param get` · BT 파일 grep) → 코스트맵 비우기 2 회(`ros2 service call`) + **`sleep $WAIT`(15)** → `tf2_echo map base_link` · 로그 집계 → 통과 폭 감사(job248).
- `job726`(지도 · 위치 추정 모드 인자로 job240) → `job731`(+ `job697_restore_chk.py` · 배터리 `topic echo`) → `job780`(+ `param get static_layer.map_topic` · `/map_nav` 확인) → 10-12 래퍼(`job969` 등: 설치본 `sed -i` PreferForward → `job780` → `sleep 15` → `lifecycle get` 4 개 × 최대 3 회 · `job956_gcmchk.py` · `param get` 3 개 × 최대 3 회 · `tf2_echo` → `sleep 20` → 정지 부하 `top`).
- 출력: 결과 줄만, 경과 시각 없음(예 `j969_prep.txt` `  /wheel_odom  average rate: 24.999` · `  map->odom: - Translation: [-0.011, 0.000, 0.000]`).
- 결함: `ros2` CLI 한 번 = 참여자 하나 생성 · 탐색 · 종료 → 회당 수 초 + 탐색 통신 급증. `timeout 15 … | tail -1` 을 최대 3 회 되풀이해 실패 때 45 s 까지. 시간 기록 없음.
- 지금: 쓰지 않음. 대체 = `prep_fast.sh`.

### 8.2 `job971_prepchk.py` → `Docs/tools/chk_prep.py` — 확인 노드 1 개 (Jetson, rclpy) ★
- 부른 형태: `python3 -u /tmp/chk_prep.py $WAIT 150`(prep_fast 59 행). 인자 [WAIT = 재마킹 대기 15 s] [한도 = 150 s].
- 왜(독스트링): '기존 prep 은 `ros2 topic hz/param get/lifecycle get` 을 약 25 번 따로 불렀다 — 회당 3~15 s + 부를 때마다 참여자 탐색 폭주. 또 고정 대기 대신 준비될 때까지 기다린다.'
- 하는 일(코드 기준, 10-12 판):
  - 구독: `/wheel_odom`(sensor_data) · `/odometry/filtered`(10) · `/tf`(100) · `/battery` · `/global_costmap/costmap`(TRANSIENT_LOCAL · RELIABLE, 칸 값 ≥ 99 수 셈). TF 버퍼로 map→base_link.
  - 서비스 클라이언트: 5 노드 `get_state`(controller · planner · bt_navigator · behavior · nav_map_server), 3 노드 `get_parameters`(PARAMS). 응답이 4 s 안에 안 오면 다시 보냄.
  - 루프(0.1 s spin): 시작 4 s 뒤부터 '기다리는 것' = active 아닌 수명 주기 · map→base TF 없음 · `/wheel_odom` 3 s 창 < 20 Hz · `/odometry/filtered` < 20 Hz · 전역 지도 없음 또는 칸 수 ≤ 20000. 목록이 바뀔 때만 한 줄 출력. 비면 `ok`.
  - `ok` 면 로컬 · 전역 `clear_entirely_*`(서비스 대기 5 s · 응답 8 s) → WAIT 초 동안 spin(재마킹 대기 — 마킹이 실제로 됐는지는 판정 안 함) → 요약 → 마지막 줄 `PREP_OK` / `PREP_FAIL`(한도 150 s 초과), 종료 코드 0 / 1.
- 출력(10-12 첫 실행 발췌, [`j973_prep_fast.txt`](../debug_log/2026-10-12/outputs/j973_prep_fast.txt)):
```
  [  4.0 s] 기다리는 것: controller_server planner_server bt_navigator behavior_server nav_map_server /wheel_odom /odometry/filtered 전역 지도
  [ 13.3 s] 기다리는 것: bt_navigator
  [ 13.8 s] 기다리는 것: 없음
  준비까지 13.8 s | Nav2 controller=active planner=active bt_navigator=active behavior=active nav_map=active
  /wheel_odom 25.0 Hz · /odometry/filtered 30.0 Hz · /tf 49.7 Hz · 배터리 12.07 V
  /controller_server: PreferForward=15.0 · vx_min=-0.06 · visualize=True · trajectory_step=100 · time_step=4
PREP_OK
```
- 계보: 10-12 `job971`(PARAMS 3 노드) → 10-13 `chk_prep.py`(같은 코드, 이름만) → 10-21 출발 위치 검사 `PREP_POSE`(±0.10 m · ±2°, 근거 10-20 prep 직후 SLAM 21° · −41° 오류 2 회) → 10-27 PARAMS 확장(경로 크리틱 · SmacHybrid · 카메라 프리셋 · ekf · slam · bt — 래퍼의 `param get` 11 회를 흡수). 이후는 다음 시기 카드.
- 알려진 결함: ① 독스트링 문턱 '100×100' 과 코드 20000 불일치(§5.3-2) ② `/tf` Hz 는 메시지 수(변환 수 아님) ③ 재마킹 대기 뒤 전역 지도를 다시 받았는지 판정에 안 씀('비운 뒤 아직 수신 없음' 도 `PREP_OK`) ④ 파라미터 조회 실패는 '조회 실패' 표시만 — 불합격 아님. 다시 쓸 수 있음(지금 운용 도구).

### 8.3 `job972_prep_fast.sh` → `Docs/tools/prep_fast.sh` — 빠른 prep (Jetson, bash) ★
- 부른 형태: 환경 `MAP`(기본 office_v3) · `EXTRA_SENSORS` · `EXTRA_NAV` · `STUCK_SHADOW`(기본 true) · `FWD`(기본 15.0) · `WAIT`(기본 15) 로 `bash /tmp/prep_fast.sh`. 보통 `prep_patrol.sh` 가 부름.
- 하는 일(10-12 판 기준, 단계마다 `⏱ +N s` 출력):
  1. 지도 파일 확인 → 설치본 yaml `sed -i` 로 PreferForward = FWD(§5.2) → `FASTRTPS_DEFAULT_PROFILES_FILE=fastdds_udp_only.xml`(스크립트 자신이 만드는 참여자도 UDP 전용).
  2. 정리: `ros2 bag record` 먼저 SIGINT + 3 s(09-30 bag 메타데이터) → PATS(10-12 판 31 개 이름) TERM → 1 s 간격 최대 15 회 개수 확인(`pgrep -fc | head -1` 로 두 줄 문제 회피) → 남으면 −9 + 3 s → `/dev/shm` fastrtps 잔재 수 표시 → 세 로그 비우기.
  3. base: 에이전트 컨테이너 수 · 세션 수립 기록 수 · robot_state_publisher 수. 에이전트 ≠ 1 이면 `exit 1`.
  4. sensors 기동 → `gyro bias calibrated` 줄을 0.5 s 간격 최대 80 회(40 s) 기다림.
  5. slam(위치 추정) 기동 → `Registering sensor|Load From File|위치 추정` 줄 최대 30 s → nav2 기동(기다리지 않음).
  6. `chk_prep.py $WAIT 150`.
  7. DDS 조회 없이 로그 · 프로세스 집계: 설치본 PreferForward · BT 재계획 Hz · `navmap_ensure` · no map 경고 · SHM 오류 · EKF 위반 · slam 폐기 · load · 프로세스 15 개 수 · nvblox(컨테이너) 수.
- 10-13 이후 바뀐 것(지금 판): 10-14 기록 보관(39~42 행) · 10-20 PATS 에 `cuvslam_up.sh vslam_twist` · 컨테이너 cuVSLAM 고아 정리(30~32 행) · `fastdds shm clean`(36 행) · 끝 줄에 cuVSLAM · vslam_twist · ekf_vslam 수(66 행). 확인 노드 이름 `job971_prepchk.py` → `chk_prep.py`(10-13).
- 출력: §2 의 `⏱` 줄과 §8.2 발췌. 원문 [`j973_prep_fast.txt`](../debug_log/2026-10-12/outputs/j973_prep_fast.txt) · 10-13 · 10-14 `prep_f2*.txt`.
- 알려진 결함: ① `sed -i` 링크 끊김(§5.2, 지금도) ② 자이로 줄 40 s · slam 줄 30 s 를 못 찾아도 **멈추지 않고** 다음 단계로(불합격 판정은 `chk_prep` 가 주기 · TF 로만) ③ `PREP_FAIL` 이어도 스크립트 종료 코드는 마지막 `st` 의 0 — 판정은 마지막 줄 문자열로 ④ 기록 보관은 보관 시각 이름(주행 이름 아님) ⑤ `pgrep -fc "$p"` 패턴(예 `amcl` · `map_server`)은 그 낱말이 명령줄에 든 다른 프로세스도 센다(코드 읽기, 사례 미관찰).
- 지금: 운용 도구.

### 8.4 `job973_prep_lite_fast.sh` → `Docs/tools/prep_patrol.sh` — 운용 구성 래퍼 (Jetson, bash)
- `job973`: `EXTRA_SENSORS="rf2o:=true shadow:=false gate_v:=on gate_vref:=wheel" EXTRA_NAV="global_camera:=nvblox replan_hz:=0.5 mppi_viz:=lite" STUCK_SHADOW=true FWD=15.0` 고정 → `job972`.
- `prep_patrol.sh VIZ FWD`(10-13): 같은 구성에서 궤적 발행만 인자(`lite|true|off`). 10-19 `SENSORS_ADD` · 10-23 `ODOM`(기본 vslam) · `REPLAN_HZ` · 10-26 `NAV_ADD` 가 붙음(지금 19 행).
- 10-14 `prep_patrol_pad.sh`(날짜 폴더 `2026-10-14/jobs/`)는 `pad_relief` 를 얹은 변형 — [실행 중 패딩 변경 카드](pad-relief-runtime-padding.md).

### 8.5 `chk_prep_md5.sh` · `chk_logkeep.sh` (10-14 §25, Jetson, bash)
- `chk_prep_md5.sh`: `md5sum /tmp/prep_fast.sh /tmp/prep_patrol.sh /tmp/prep_patrol_pad.sh` — Jetson 판이 저장소 판과 같은지(덮어쓰기 전 확인).
- `chk_logkeep.sh`: prep_fast 의 보관 부분(39~42 행과 같은 코드)만 실행 → `ls -la /tmp/logkeep | tail -5` · `df -h /tmp`. 기록을 비우지 않음.
- 출력: 없음(SUMMARY 서술 '3 개 보관 ✔', '602e2da9…' 가 전부 — **원천 소실**).

### 8.6 `up_cfg_intdist.sh` 의 링크 복구 (10-15 §30, Jetson, bash)
- 7~10 행: 주석 '⚠ prep_fast 의 sed -i 가 설치본 nav2_params.yaml 링크를 일반 파일로 바꿔 놓아(그 뒤 src 수정이 안 따라옴) — src 로 다시 링크' → `[ -L $I ] || { rm -f $I && ln -s $D/nav2_params.yaml $I … }` → `readlink` 로 재확인.
- 한계: 이 배포 스크립트를 쓸 때만 복구. prep 이 다시 `sed -i` 하면 또 끊김.

## 9. 용어
- **prep**: 주행 전 스택 정리 · 기동 · 확인 절차(로버는 안 움직임). 끝 줄 `PREP_OK` 면 주행 게이트로.
- **폴링(polling)**: 정해진 시간 기다리는 대신 조건이 될 때까지 짧은 간격으로 확인하는 것.
- **수명 주기(lifecycle) active**: Nav2 서버가 configure → activate 를 마쳐 일을 받는 상태. `get_state` 서비스로 확인.
- **DDS 참여자 · 탐색(discovery)**: `ros2` CLI 명령 하나도 실행 동안 참여자가 되어 다른 참여자를 찾는 통신을 일으킨다 — 짧은 명령을 여러 번 부르면 그때마다 탐색 급증([주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md)).
- **재마킹 대기**: 코스트맵을 비운 뒤 센서가 장애물을 다시 칠할 시간(15 s). 09-11 '클리어 직후 옛 데이터로 주행' 사고 대책.
- **`--symlink-install`**: colcon 이 설치본에 src 파일 복사본 대신 링크를 두는 방식 — src 를 고치면 빌드 없이 반영. 설치본을 `sed -i` 로 고치면 링크가 일반 파일로 바뀌어 이 연결이 끊긴다.
- **`/tmp/logkeep`**: prep 이 지우기 전에 직전 `nav2 · slam · sensors` 기록을 옮겨 두는 곳(최근 8 벌, 재부팅이면 사라짐).
