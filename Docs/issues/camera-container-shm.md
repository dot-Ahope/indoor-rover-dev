# 카메라 ↔ 컨테이너 공유메모리(N-SHM) — IR 빠짐 원인 UDP 수신 버퍼, SHM 재검토 (8 기: 10-20 §7 ~ §7.5 · §9 ~ §9.5 · §11, 10-21 ~ 10-23 운용)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **해결(카메라 ↔ cuVSLAM 경로)** — 원인 측정(소켓 수신 버퍼 넘침, 크기별 재현) + 조치(그 두 프로세스만 SHM+UDP) + 재발 0 확인(정지 A/B 13 → 15.0 Hz, 실제 스택 재기동 10/10, 주행 f2sm1 `/vslam/odom` 15.0 Hz, 10-22 · 23 주행 13 회 로그 SHM 오류 0). ⚠ '영상이 SHM 으로 갔다' 의 직접 근거로 정한 소켓 버림 감소(§9.2 기준 2)는 내 측정 결함으로 **판정 불가**(조용한 창 39 → 0/s 는 보조 근거). 수신 버퍼(`rmem_max`) 상향은 안 함 — 다른 프로세스 쌍의 큰 UDP 메시지는 같은 한계 그대로 | 10-19 §16.1(첫 관찰) · 10-20 §6.4 → §7 ~ §7.5 · §9 ~ §9.5 · §11 · 10-21 §7(주행 확인) · §18.2 · 10-23 §16(prep 기본) | [10-19 §16.1](../debug_log/2026-10-19/SUMMARY.md) — 번갈이 시험에서 원시 IR 이 분리 노드에 30 Hz 중 21~22 Hz 만 도착. 직접 계기는 [10-20 §6.4](../debug_log/2026-10-20/SUMMARY.md) f2v1 그림자 주행의 `/vslam/odom` 주행 중 9.5 Hz | `ros2_ws/src/rover_bringup/config/fastdds_shm_udp.xml`(신규) · `camera.launch.py dds_shm:=` · `ekf.launch.py dds_shm:=` → `scripts/cuvslam_up.sh` 3 번째 인자 · `Docs/tools/prep_fast.sh` 정리 단계 `fastdds shm clean`(커밋 `8e31e2b1`, 10-20 §9.1) · `Docs/tools/prep_patrol.sh` 기본 `dds_shm:=true`(커밋 `dcfdb0b6`, 10-23 §16) | [DDS 공유메모리 사고](dds-shm-incident.md)(09-09 에 SHM 을 끈 이유 — 이 카드가 그 판정을 다시 봄) · [cuVSLAM 속도 융합](cuvslam-velocity-fusion.md)(이 경로의 소비자 — f2v1 · f2sm1 효과는 그쪽) · [프로젝터 · IR 번갈이](projector-ir-alternation.md)(10-19 IR 전달 손실 첫 관찰) · [통신 포화 · MPPI 궤적 발행](network-saturation-mppi-viz.md)(같은 208 kB 수신 버퍼, 10-12 SHM 검토) · [주행 직전 DDS 참여자 금지](pre-drive-dds-participants.md)(§11.2 측정 오염과 같은 현상) · [빠른 prep](prep-fast-startup.md)(정리 단계) · [주행 운용 10-19 ~ 23](drive-ops-1019-1023.md)(SHM 구성 게이트 P 65 % · 게이트 B 12 s) · [SLAM stamp 정체](slam-stamp-freeze.md)(10-27 §22 '공유메모리로는 안 풀림') |

**한 줄**: 10-20 f2v1 그림자 주행에서 cuVSLAM 입력(IR 좌우 640×480)이 정지 13 Hz · 주행 ≈ 10 Hz 로 빠졌다. 재 보니 Jetson 의 UDP 소켓 수신 버퍼가 리눅스 기본 **212 992 B** 인데 IR 한 장이 **307 kB** 로 더 컸고, cuVSLAM 을 SIGSTOP 하면 버림이 39 → 432 /s 로 뛰었다(§7.1). 같은 경로에서 크기만 바꾸면 38 kB(지금 깊이)는 15.0 Hz, 307 kB × 2 는 12.8~14.8 Hz 로 빠짐이 재현됐다(§7.5) — nvblox 깊이가 안 빠진 이유는 데시메이션 ×4 로 38 kB 이기 때문. 수신 버퍼를 키우는 길(sudo)은 두고, 09-09 에 끈 FastDDS 공유메모리(SHM)를 다시 볼 수 있는지 먼저 재기동 시험을 했다: 정리 없이 −9 를 섞어 15/15, `fastdds shm clean` 뒤 30/30, SHM 오류 0(§7.3a) — 09-09 의 'SHM 자체가 원인' 은 과한 일반화로 정정([DDS 사고 카드](dds-shm-incident.md) §5.4). 이어 카메라 프로세스와 cuVSLAM 컨테이너 **둘만** SHM+UDP 로 바꿔(나머지는 UDP 전용 그대로) 정지 A/B 에서 cuVSLAM 13.1 → **15.0 Hz** · 프레임 간격 경고 101 → **1** · CPU 변화 없음(§9.3), 실제 스택 −9 섞은 재기동 **10/10**(§9.5). 10-21 f2sm1 주행에서도 15.0 Hz · 버림 0, 10-23 부터 `prep_patrol.sh` 기본. 측정 실수 두 건(SHM 전용 시험의 발견 실패, 측정 노드가 버림 카운터를 오염)은 10-20 §11 칸 형식 기록의 원본이다.

## 1. 증상
- 10-19 §16.1(번갈이 S2 정지 시험, [프로젝터 카드](projector-ir-alternation.md) 몫): '② 만으로도 원시 IR 이 분리 노드에 30 Hz 중 21~22 Hz 만 도착(S1 스택 없을 때는 60 중 57~59) — **스택 부하 아래서 호스트 안 DDS(UDP)로 307 kB 영상을 나르는 길에서 잃는다**'. 대책 후보 4 번이 이미 'UDP 수신 버퍼(net.core.rmem_max) 키우기는 sudo — 사용자 결정 항목'. 원문 `2026-10-19/outputs/chk_flash_s2_*.txt`.
- 10-20 §6.4 f2v1(프로젝터 상시 끔 + cuVSLAM 그림자, UDP): `/vslam/odom` 정지 13 Hz → **주행 9.5 Hz**, 0.5 s 넘는 끊김 38(최대 3.8 s), `vslam_twist` 가 차분 간격 > 0.3 s 로 10 % 버림 — [`run_f2v1.txt`](../debug_log/2026-10-20/outputs/run_f2v1.txt) · [`chk_f2v1_logs.txt`](../debug_log/2026-10-20/outputs/chk_f2v1_logs.txt) · [10-20 TOOLS](../debug_log/2026-10-20/TOOLS.md) §6.4 줄. 그때 원인은 '호스트 → 컨테이너 IR 두 줄 DDS 전달 누락' **추정 · 미확인**.
- 같은 날 nvblox(같은 호스트 → 컨테이너 UDP, best effort)는 깊이를 15.1~15.2 Hz 로 빠짐 없이 받았다 — 둘 다 best effort 인데 cuVSLAM 만 빠지는 이유가 §7.4 에서 '미확인' 으로 남았고 §7.5 에서 풀렸다.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 10-19 §16.1 | 번갈이 30 fps 정지 시험(S2) | 원시 IR 30 Hz 중 21~22 Hz 도착, 기록 IR 7.7~8.7 Hz | 호스트 안 DDS(UDP) 전달에서 잃음(측정) → 대책 = 한 프로세스 합성(§17), rmem 은 사용자 결정 | `2026-10-19/outputs/chk_flash_s2_*.txt` — 해설은 [프로젝터 카드](projector-ir-alternation.md) |
| 10-20 §6.4 | f2v1 그림자 주행 | `/vslam/odom` 9.5 Hz · 끊김 38 | 입력 빠짐이 융합 효과를 깎았다(추정) → 다음 후보 (a) IR 전달 경로 개선 | [`run_f2v1.txt`](../debug_log/2026-10-20/outputs/run_f2v1.txt) — 효과 수치는 [cuVSLAM 카드](cuvslam-velocity-fusion.md) |
| 10-20 §7.1 | 커널 UDP 설정 · 카운터, cuVSLAM SIGSTOP 대조 | `rmem_max = rmem_default = 212 992`, 부팅 뒤 누적 `RcvbufErrors` 3 716 712, 정지 20 s **39/s**, cuVSLAM SIGSTOP 20 s **432/s** | 빠짐 = 소켓 수신 버퍼 넘침(측정). '432/s ≈ IR 데이터그램, 정지 때도 ≈ 9 % 버림' 은 계산 — §3 의 단서 | 도구 [`chk_udp.sh`](../debug_log/2026-10-20/jobs/chk_udp.sh) · [`chk_udp_rate.sh`](../debug_log/2026-10-20/jobs/chk_udp_rate.sh), 출력 **원문 없음 — SUMMARY 서술이 전부** |
| 10-20 §7.2 | 사용자 "실행 종료 방식이 문제인지, 통신 방식이 문제인지" → 09-09 기록 재독 | uid 호스트 `jetson` · 컨테이너 `admin` 둘 다 1000, `/dev/shm` 에 그날 10:48~10:57 생긴 FastDDS 파일 16 개 | 09-09 'SHM 자체' 는 과한 일반화(정정) — 본체는 [DDS 사고 카드 §5.4](dds-shm-incident.md) | [`chk_uid.sh`](../debug_log/2026-10-20/jobs/chk_uid.sh), 출력 **원문 없음** |
| 10-20 §7.3 · §7.3a | SHM 재기동 시험(합성, 도메인 88): 640×480 mono8 두 줄 15 Hz, 호스트 발행 → 컨테이너 구독, INT · TERM · KILL · '발행만 −9 재기동' 순환 | 팔 A(정리 없음) 15/15 · 팔 B(`fastdds shm clean`) 30/30 모두 컨테이너 구독 14.8~15.0 Hz, SHM 오류 0. (3) SHM 경로 판정 29/30(B24 +579/s) | 이 버전(2.6.12) · 규모에선 '종료 방식을 고쳐도 SHM 이 깨진다' 재현 안 됨 | [`run_shm_test.txt`](../debug_log/2026-10-20/outputs/run_shm_test.txt) · [`jobs/shm_test/`](../debug_log/2026-10-20/jobs/shm_test/run_shm_test.sh) |
| 10-20 §7.3b | 컨테이너 구독만 SHM 전용 프로파일로 같은 팔 B 30 주기 | **컨테이너 0.0 Hz 30/30**, 호스트 15.0, SHM 오류 0 | 처음 읽기 'SHM 이 안 통한다' ✘ → **시험 설계 결함**(§5.1) | [`run_shm_test_shmonly.txt`](../debug_log/2026-10-20/outputs/run_shm_test_shmonly.txt) |
| 10-20 §7.3c | V1 전부 SHM 전용 · V2 발행만 SHM+UDP | V1 호스트 163 · **컨테이너 150**(개, 6~10 s), V2 둘 다 0. 컨테이너 `/dev/shm` inode 1 = 호스트 | 호스트 ↔ 컨테이너 SHM 통함(측정). SHM 전용 참가자는 UDP 를 가진 참가자를 못 찾음 — 기전 미확인 | [`chk_shm_path.txt`](../debug_log/2026-10-20/outputs/chk_shm_path.txt) |
| 10-20 §7.4 | N-SHM 계획(카메라 · nvblox · cuVSLAM, 단계 S1~S5) | 기준값: nvblox 15.2 Hz · cuVSLAM 정지 13 / 주행 ≈ 10 Hz · 버림 39/s · CPU 54 / 75 % | 계획. '깊이 614 kB · ≈ 9 MB/s' 는 틀린 입력값(§7.5 정정) | [10-20 SUMMARY §7.4](../debug_log/2026-10-20/SUMMARY.md) |
| 10-20 §7.5 | 사용자 "해상도를 낮춰서 UDP 대역폭에 적절하기 때문인지 검증" — 크기만 바꿔 UDP 전송 | 38 kB **15.0 / 15.0** · 307 kB 14.8 / 14.8 · 307 kB × 2 14.8·14.2 / 14.2·12.8 · 614 kB 14.1 / 13.3 Hz | 맞다(측정) — 단 원인은 대역폭보다 '메시지 한 개 크기 > 소켓 버퍼'(기전은 **추정**). nvblox 는 N-SHM 범위에서 빼고 **카메라 ↔ cuVSLAM 만** | [`chk_udp_size.txt`](../debug_log/2026-10-20/outputs/chk_udp_size.txt) |
| 10-20 §9.1 | S1 코드(기본 끔) 배포 · 빌드 | — | `dds_shm:=false|true` · 프로파일 8 MB · prep `fastdds shm clean` | [`up_shm.sh`](../debug_log/2026-10-20/jobs/up_shm.sh) · 커밋 `8e31e2b1` |
| 10-20 §9.2 · §9.3 | S2 정지 A/B U1 → S → U2(각 prep → 20 s → 60 s 측정 → 25 s 기록) | cuVSLAM · `/vslam/odom` 13.2·13.1 → **15.0·15.0** → 13.0·12.8, 간격 경고 101 → **1** → 115, CPU 54.6 → 54.0 → 55.0 %, nvblox 15.1 그대로, 상자 칸 13 · 14 · 13. 버림 386 · **520** · 519 /s | 기준 1 · 3 · 4 통과, 기준 2 는 측정 결함으로 **판정 불가**(§5.2) | [`run_shm_static.txt`](../debug_log/2026-10-20/outputs/run_shm_static.txt) · [`anal_shm_static_box.txt`](../debug_log/2026-10-20/outputs/anal_shm_static_box.txt) |
| 10-20 §9.4 · §9.5 | S3 실제 스택 prep 10 회 + 카메라 −9 ×3 · nvblox −9 ×2 · cuVSLAM −9 ×1 | 10/10 PREP_OK · `vslam_twist` 10 s 출력 149~150 · 버림 0 · nvblox 15.1 Hz · SHM 오류 0 · clean 이 고아 1~2 개씩 | 합격(측정) | [`run_shm_restart.txt`](../debug_log/2026-10-20/outputs/run_shm_restart.txt) |
| 10-20 §9.6 · §9.7 | S4 그림자 주행 f2sm1 선언 → 게이트에서 세 번 멈춤(주행 안 함) | 게이트 B `topic hz` 첫 출력 4.5~5.6 s(한도 6), 게이트 P 정지 부하 62 %(> 60) | 그림자 + SHM 구성의 참가자 증가 · 부하(추정) — 게이트 처리는 [운용 카드](drive-ops-1019-1023.md) | [`run_f2sm1_attempt3.txt`](../debug_log/2026-10-20/outputs/run_f2sm1_attempt3.txt) |
| 10-20 §11 | 측정 실수 두 건을 칸 형식으로(사용자 요청) | — | README §2.3 칸 형식의 본보기가 됨 | [10-20 SUMMARY §11](../debug_log/2026-10-20/SUMMARY.md) |
| 10-21 §7 | f2sm1 주행(SHM 구성, 게이트 P 65 %) | `/vslam/odom` **15.0 Hz**(f2v1 9.5), 0.5 s 넘는 끊김 2(둘 다 bag 시작), `vslam_twist` 10 s 출력 142~154 · 버림 0, 간격 경고 4 분에 5 회 | 주행 중에도 입력 빠짐 해소(측정, 1 회) | `2026-10-21/outputs/run_f2sm1.txt` · `chk_f2sm1_logs.txt` · `gaps_f2sm1.txt` — 효과는 [cuVSLAM 카드](cuvslam-velocity-fusion.md) |
| 10-21 §18.2 | NVIDIA 구성 정지 시험 nv1 첫 실행(시험 컨테이너 `isaac_rs_test`) | 전 토픽 0 Hz, 출력에 **실제 SHM 오류 1 줄** `RTPS_TRANSPORT_SHM Error … Failed init_port fastrtps_port7413: open_and_lock_file failed`(17:00:45) | 0 Hz 원인은 토픽 이름(4.51.1 은 `/camera/depth/…`) — SHM 오류는 '처음 추론' 으로만 적히고 그 오류 자체는 설명 안 됨(§3 · §7) | `2026-10-21/outputs/run_nv_static_try1.txt` 31 행 |
| 10-21 §21.2 ~ 10-22 | 운용 구성 = 프로젝터 끔 · `vslam:=shadow` · `dds_shm:=true`(작업별 prep 스크립트 `SENSORS_ADD`) | prep 출력 'SHM 고아 정리: 2~3 zombie segments cleaned · 남은 fastrtps 2~4' | SHM 이 사실상 운용 구성 | `2026-10-21/outputs/prep_sm_1021_4.txt` · `2026-10-22/outputs/prep_op_1022_1.txt` · `prep_dr_1022_5.txt` |
| 10-23 §16 | 사용자 "vslam on 기본으로 채택" → `prep_patrol.sh` 기본 `emitter_off:=true vslam:=on dds_shm:=true` | — | prep 기본(launch 기본값은 그대로 false) | [`prep_patrol.sh`](../tools/prep_patrol.sh) 11 행 · 커밋 `dcfdb0b6` |
| (11-03 카드 작성 중) | 10-22 · 23 주행 13 회 보관 로그 재검 | 13/13 `cuvslam_up … DDS fastdds_shm_udp.xml`, sensors · nav2 · slam 로그 SHM 오류 **0**, `vslam_twist` 10 s 출력 중앙 **150**, 140 미만 창 1~4 개/주행, 버림 합 0~54 | 운용 중 재발 없음(측정 — 단 cuVSLAM · nvblox 로그는 보관 안 됨) | `2026-10-22/bags/logs_*/` · `2026-10-23/bags/logs_*/`(git 제외), 명령은 §9.14 |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| cuVSLAM 입력 빠짐 = CPU 경합(읽기 늦음)만 | 정지(CPU 54 %)에도 빠지나 · 소켓 버림 카운터 | 정지에도 13/15 Hz, 버림 39/s(§7.1) | **기각(단독으로는)** — 주행 중 더 빠지는 몫(≈ 10 Hz)은 CPU 경합으로 읽기가 늦어서(추정) |
| 빠짐 = UDP 소켓 수신 버퍼 넘침 | `rmem_max` vs 메시지 크기, cuVSLAM SIGSTOP 대조 | 212 992 B < IR 307 kB. SIGSTOP 20 s 동안 39 → 432/s(§7.1) | **지지(측정)**. ⚠ 432/s 를 'IR 데이터그램 수' 로 읽은 것은 계산 — SIGSTOP 은 cuVSLAM 프로세스의 모든 소켓(camera_info · /tf 등 포함)을 멈추므로 IR 몫만이 아니다(카드 작성 중 지적, 추정) |
| nvblox 가 안 빠지는 이유 = 깊이가 작아서 | 같은 경로 크기만 바꿔 전송(§7.5) | 38 kB 15.0 · 614 kB 13.3~14.1 · IR 두 줄 12.8~14.8 Hz | **지지(측정)** — 깊이 614 kB 가정(§7.4 · 10-12 §8.5)은 틀림, 실제 160×120 · 38 472 B |
| 원인은 '대역폭' | 15 Hz × 38 kB = 0.6 MB/s · 307 kB × 30 = 9 MB/s 는 루프백엔 작음 | 크기 · 동시 도착이 늘수록 버림이 늚 | **기각(측정과 안 맞음)** → '조각 수십 개가 한꺼번에 버퍼에 들어와 하나라도 잃으면 best effort 메시지 전체가 버려진다' 는 기전은 **추정**(조각 단위 측정 없음) |
| SHM 은 비정상 종료에 깨진다(09-09 판정) | 정리 없이 −9 를 섞은 재기동(팔 A), clean 뒤(팔 B), 실제 스택 −9(S3) | 15/15 · 30/30 · 10/10, SHM 오류 0, 팔 A 고아 41 개까지 쌓여도 정상 | **기각(이 버전 · 규모)** — 09-09 2 회차는 `rm -f` 로 살아 있는 참가자 파일을 지운 것이 더 유력(추정, [DDS 사고 카드](dds-shm-incident.md)) |
| 호스트 ↔ 컨테이너 SHM 이 안 통한다(§7.3b 0 Hz) | 모든 참가자를 SHM 전용으로(V1) | 컨테이너 150 개 수신 | **기각** — 0 Hz 는 transport 집합이 다른 참가자끼리의 발견 실패(V2 에서 호스트끼리도 0). 왜 못 찾는지는 **미확인** |
| SHM+UDP 혼합 구성에서 IR 이 실제로 SHM 으로 간다 | ① UDP 데이터그램 증가(§7.3a) ② 소켓 버림 감소(§9.2 기준 2) ③ cuVSLAM Hz · 간격 경고 | ① +30~80/s(영상 UDP 면 수백, 간접) ② 386 · 520 · 519 — 측정 노드 발견 폭주에 덮여 판정 불가, 조용한 창 S 10 s +0(다른 시각) ③ 13.1 → 15.0 Hz · 101 → 1 | **지지(간접 + 결과)** — 직접 근거(같은 창 소켓 버림)는 없다 |
| SHM 이 nvblox 에도 이득 | §7.5(깊이 38 kB 는 안 빠짐) · S2 nvblox 항목 | nvblox 15.1 Hz 세 조건 같음, 상자 칸 13 · 14 · 13 | **해당 없음(범위 제외)** — 깊이 해상도를 올리면(×2 = 154 kB 이상) 다시 검토 |
| 10-21 nv1 첫 실행 SHM 오류가 0 Hz 원인 | `ros2 topic list` | 드라이버 4.51.1 은 `/camera/depth/…` 로 발행, 분석기는 `/camera/camera/…` 구독 | **기각(0 Hz 원인으로는)**. 오류 줄 자체(시험 컨테이너 `-v /dev:/dev` · 앞 단계 exit −11 뒤 · port7413)는 **미확인** |

## 4. 조치와 효과
- **수신 버퍼 상향(§7.1 후보 1)은 안 함** — sudo · 사용자 결정 사항으로 남김. 대신 SHM(§7.1 후보와 별도, 사용자 "공유 메모리 재기동 시험을 하라. 통과하면 nvblox 도 공유메모리로 갈 계획"). IR 축소(후보 2, 320×240)도 안 함.
- **범위**: SHM+UDP 프로파일을 카메라 프로세스 · cuVSLAM 컨테이너 **둘만**(§7.4 → §7.5 에서 nvblox 제외). 나머지 EKF · SLAM · Nav2 · nvblox · 러너 · 기록기 · ros2 CLI 는 UDP 전용(09-09) 그대로 — 섞여도 UDP 로 만난다(§7.3c-3).
- **정리**: prep 이 프로세스 정리 뒤 `fastdds shm clean`(아무도 안 잡은 고아만). 09-09 식 `rm -f /dev/shm/fastrtps_*` 는 금지.
- **효과(측정)**:

  | | UDP | SHM | 출처 |
  |---|---|---|---|
  | cuVSLAM · `/vslam/odom` 정지 | 13.2 · 13.1 / 13.0 · 12.8 Hz | **15.0 · 15.0** | 10-20 §9.3 |
  | 프레임 간격 경고 / 60 s | 101 / 115 | **1** | 같음 |
  | 전체 CPU · 카메라 프로세스 | 54.6 · 23.5 / 55.0 · 23.4 % | 54.0 · 22.0 % | 같음 |
  | nvblox 깊이 · 상자 칸 · 북 · 서 면 | 15.1 · 13 · +6.6 · +1.9 / 15.1 · 13 · +6.8 · +2.5 | 15.1 · 14 · +6.4 · +2.4 | 같음 |
  | `/vslam/odom` 주행 · 0.5 s 끊김 | f2v1 9.5 Hz · 38 | f2sm1 **15.0 Hz** · 2(bag 시작) | 10-20 §6.4 · 10-21 §7 |
  | 재기동(−9 6 회 포함) | — | 10/10, SHM 오류 0 | 10-20 §9.5 |

- 한계:
  - 직접 근거(소켓 버림 절반 이하)는 판정 불가 — §5.2.
  - 메모리: 주석 계산 8 MB × 2 ≈ 16 MB. 컨테이너 안 `ros2 launch` 프로세스도 같은 환경변수를 받아 참가자가 하나 더일 수 있는데 세지 않음(**미확인**). 실행 중 `/dev/shm` fastrtps 10~12(§9.5) · 28(§9.3 끝) 개.
  - SHM 구간은 커널 UDP 통계 · 캡처로 볼 수 없다(10-12 §21 지적) — 이 경로의 건강은 cuVSLAM Hz · 간격 경고 · `vslam_twist` 출력 수로만 본다.
  - 그림자 + SHM 구성은 정지 부하 54~55 %(UDP 판과 같음)라 게이트 P(60 %)와 여유가 작다 — 10-21 §2 에서 그림자 구성만 65 %([운용 카드](drive-ops-1019-1023.md)). SHM 이 부하를 올린 것은 아님(§9.3 −0.6 ~ −1.0 %p).

### 4.1 지금 코드 영향 (11-03 저장소 기준)
- SHM 은 **prep 을 거칠 때만, 카메라 ↔ cuVSLAM 에만** 켜진다. launch 기본값은 모두 끔 — `ros2 launch` 를 직접 부르면 전부 UDP 전용.
  - [`fastdds_shm_udp.xml`](../../ros2_ws/src/rover_bringup/config/fastdds_shm_udp.xml) 23 행 `segment_size 8388608` · 30~36 행 SHM + UDPv4 · `useBuiltinTransports false`. 머리 주석 5~7 행 'rmem_max 상향(sudo) 대신 이 길을 택함', 10 행 'SHM 전용으로 만들면 UDP 참가자를 발견하지 못한다(§7.3c)'.
  - [`camera.launch.py`](../../ros2_ws/src/rover_bringup/launch/camera.launch.py) 30~32 행(`dds_shm` 이 참이면 `FASTRTPS_DEFAULT_PROFILES_FILE` = shm_udp 를 `env` 로) · 93 행(일반 Node) · 99 행(번갈이 합성 컨테이너) `additional_env=env` · 119 행 기본 `'false'`.
  - [`ekf.launch.py`](../../ros2_ws/src/rover_bringup/launch/ekf.launch.py) 70~74 행(`vslam != off` 일 때 `cuvslam_up.sh` 3 번째 인자로 shm_udp 또는 udp_only) · 108 행 기본 `'false'`.
  - [`cuvslam_up.sh`](../../ros2_ws/src/rover_bringup/scripts/cuvslam_up.sh) 10 행 기본 udp_only · 16 행 컨테이너용 사본 `/tmp/fastdds_cuvslam.xml`(nvblox 의 `/tmp/fastdds_udp_only.xml` 과 이름 분리) · 23 행 `export FASTRTPS_DEFAULT_PROFILES_FILE=/tmp/fastdds_cuvslam.xml`.
  - nvblox 는 UDP 고정: [`nvblox_up.sh`](../../ros2_ws/src/rover_navigation/scripts/nvblox_up.sh) 12 · 18 · 28 행.
  - 나머지 launch 는 UDP 전용: `base.launch.py` 17 · 29~30(agent 컨테이너) · 49 행, `sensors.launch.py` 15 · 24, `slam.launch.py` 15 · 92, `navigation.launch.py` 32 · 193, `localization.launch.py` 14 · 20.
  - [`prep_patrol.sh`](../tools/prep_patrol.sh) 11 행 `vslam) S="emitter_off:=true vslam:=on dds_shm:=true"`(기본 `ODOM=vslam`) · 12 행 `ODOM=rf2o` 는 `dds_shm` 없음(전부 UDP).
  - [`prep_fast.sh`](../tools/prep_fast.sh) 41~43 행 `fastdds shm clean` + 남은 수 · 70 행 SHM 오류 수 — ⚠ `/tmp/nav2.log · sensors.log · slam.log` 만 본다. `cuvslam.log` · nvblox 로그는 안 봄(S3 도구 `run_shm_restart.sh` 는 셋 다 봤음).
- 수신 버퍼: 저장소에 sysctl 설정 없음. [`chk_jetson_state.sh`](../tools/chk_jetson_state.sh) 8 행이 `rmem_max` 를 찍기만 한다 — 212 992 그대로(10-21 §16 NVIDIA 문서도 rmem 상향 권고, 사용자 결정으로 남음).
- ⚠ 낡은 주석: [`fastdds_udp_only.xml`](../../ros2_ws/src/rover_bringup/config/fastdds_udp_only.xml) 19~21 행 '1회차 뒤 정리 방식을 SIGKILL → SIGTERM 으로 바꿨으나 2회차가 재발했다 … → **원인 제거**: SHM 전송을 아예 쓰지 않는다' 가 10-20 §7.2 정정 뒤에도 그대로(이 카드 작성 중 확인). 세 launch(`base` 13~14 · `sensors` 11~12 · `slam` 11~12 · `navigation` 28) 머리 주석도 같은 설명을 가리킨다.

## 5. 내 실수
원본은 [10-20 §11](../debug_log/2026-10-20/SUMMARY.md)(README §2.3 칸 형식의 본보기). 여기엔 발췌와 데이터 위치만.

### 5.1 §7.3b — 'SHM 전용' 시험 설계 결함
| 칸 | 내용 |
|---|---|
| 하려 한 것 | §7.3a 의 'SHM 으로 갔다' 근거가 UDP 증가량(간접)뿐이고 B24 +579/s 이상치가 있어 직접 근거를 만들려 함. `fastdds_shm_only.xml`(SHM+UDP 에서 UDP 블록만 지움)을 **컨테이너 구독자에게만** |
| 본 것 | 30 주기 모두 `구독 컨테이너·호스트 Hz·UDP/s: 0.0 0.0 15.0 15.0`, SHM 오류 0 |
| 처음 추론 | 호스트 → 컨테이너 SHM 이 안 통한다 → §7.3a 통과는 전부 UDP 였다(틀림) |
| 의심한 이유 | 수신 0 인데 **오류도 0** — 경로 고장이면 세그먼트 열기 · 포트 오류가 남아야 함. '상대를 모름' 의 서명 |
| 판별 시험 | `chk_shm_path.sh`: V1 모두 SHM 전용 → 컨테이너 150 · 호스트 163 / V2 발행만 SHM+UDP → 둘 다 0 |
| 결론 | 시험 설계 결함(한쪽만 transport 를 바꾸면 발견이 안 됨). 발견 트래픽이 어느 transport 로 가는지는 **기전 미확인** |
| 다음에 알아보는 법 | ① 수신 0 + 오류 0 → 발견부터(`ros2 topic info -v`) ② 경로 판별은 모든 참가자를 같은 단일 transport 로(V1) ③ 프로파일을 한쪽만 바꾼 시험은 1 주기 연기 확인 뒤 30 주기 |
| 데이터 | [`run_shm_test_shmonly.txt`](../debug_log/2026-10-20/outputs/run_shm_test_shmonly.txt) · [`chk_shm_path.txt`](../debug_log/2026-10-20/outputs/chk_shm_path.txt) · 도구 [`run_shm_test_shmonly.sh`](../debug_log/2026-10-20/jobs/shm_test/run_shm_test_shmonly.sh) · [`chk_shm_path.sh`](../debug_log/2026-10-20/jobs/shm_test/chk_shm_path.sh) · [`fastdds_shm_only.xml`](../debug_log/2026-10-20/jobs/shm_test/fastdds_shm_only.xml) |

```bash
# jobs/shm_test/chk_shm_path.sh — run 이름 talker프로파일 호스트구독프로파일 컨테이너구독프로파일
O=/tmp/fastdds_shm_only.xml; U=/tmp/fastdds_shm_udp.xml
run "V1 전부 SHM 전용" $O $O $O
run "V2 발행 SHM+UDP · 호스트 구독 SHM 전용 · 컨테이너 SHM 전용" $U $O $O
```
```
컨테이너 /dev/shm 이 호스트와 같은가: 호스트 1 · 컨테이너 1 · 컨테이너에서 보이는 fastrtps 8 / 호스트 8
V1 전부 SHM 전용: 호스트 구독 [1792478394.844 163 163] · 컨테이너 구독 [1792478394.277 150 150] (시각 n1 n2, 약 6~10 s 분량)
V2 발행 SHM+UDP · 호스트 구독 SHM 전용 · 컨테이너 SHM 전용: 호스트 구독 [1792478410.426 0 0] · 컨테이너 구독 [1792478409.901 0 0] (시각 n1 n2, 약 6~10 s 분량)
```
- 덧붙임: 같은 절의 '실행 사고' — §7.3b 첫 시작 때 `CPROF` 를 환경변수가 아니라 인자로 넘겨 일반 프로파일로 돌기 시작 → 멈추고 러너 3 · 시험 노드 5 · 컨테이너 2 정리(10-20 §7.3a 끝). 감싸개 `run_shm_test_shmonly.sh` 는 `CPROF=/tmp/fastdds_shm_only.xml bash /tmp/run_shm_test.sh 0 30` 한 줄.

### 5.2 §9.3 — 측정 노드가 버림 카운터를 오염시킨 창
| 칸 | 내용 |
|---|---|
| 하려 한 것 | §9.2 기준 2 '버림/s 가 UDP 판의 절반 이하' 를 직접 근거로 |
| 본 것 | U1 386 · **S 520** · U2 519 /s. 같은 창 S 는 cuVSLAM 15.0 Hz · 경고 1 |
| 처음 추론 | (그대로면) SHM 에서 버림이 더 많다 |
| 의심한 이유 | 두 독립 측정과 모순 — §7.1 조용한 창 39/s · SIGSTOP 432/s 보다 큼, 그리고 영상이 520/s 씩 버려지면 15.0 Hz · 경고 1 일 수 없음 |
| 판별 시험 | `chk_udp_drops2.sh`: `/proc/net/udp` 소켓별 drops — 버림 많은 소켓은 포트 7410 · 7412 · 7468 · 7422 · 7458(DDS 발견 · 참가자 유니캐스트 대역), 새 참가자 없는 조용한 10 s: RcvbufErrors +0, drops 합 578 054 → 578 054 |
| 결론 | 측정 노드(+ 직전 `tf2_echo`)가 새 참가자로 붙는 순간 ≈ 26 프로세스가 발견 데이터를 한꺼번에 보내 발견 소켓이 넘침 → 시스템 전체 카운터에 섞임. 기준 2 판정 불가. §7.3a B16(+6 000) · B24(+579) 튐도 같은 기전으로 **추정**(미확인) |
| 다음에 알아보는 법 | ① 시스템 전체 카운터는 창 안에서 참가자를 만들지 않을 때만(측정 노드 먼저 띄우고 ≥ 10 s 뒤) ② 소비자 소켓 하나의 drops ③ 카운터가 독립 지표 둘과 모순이면 측정부터 의심 ④ §9.4 처럼 로그로만 건강 보기 |
| 데이터 | [`run_shm_static.txt`](../debug_log/2026-10-20/outputs/run_shm_static.txt) · 도구 [`run_shm_static.sh`](../debug_log/2026-10-20/jobs/run_shm_static.sh) · [`chk_udp_drops2.sh`](../debug_log/2026-10-20/jobs/chk_udp_drops2.sh). ⚠ 소켓별 포트 · 조용한 창 수치의 원문은 **원천 소실** — `outputs/chk_udp_drops.txt` 에는 앞 판 `chk_udp_drops.sh` 의 한 줄만 있다(§6-4) |

```bash
# jobs/run_shm_static.sh — 측정 창: 카운터 → 측정 노드 60 s(새 참가자) → 카운터
E0=$(rb)
python3 -u /tmp/chk_vslam_live.py 60 2>&1 | grep -av "^\[INFO\]"
E1=$(rb)
echo "  EKF 위반 +$((V1-V0)) · cuVSLAM 프레임 간격 경고 +$((G1-G0)) · 수신 버퍼 버림 $(( (E1-E0)/60 ))/s · …"
```
```
########## s (emitter_off:=true vslam:=shadow dds_shm:=true) ##########
  카메라 프로파일: fastdds_shm_udp.xml · cuVSLAM 프로파일: /tmp/sensors.log:DDS fastdds_shm_udp.xml
  /visual_slam/tracking/odometry    15.0 Hz · 처음→끝 이동 0.30 cm
  EKF 위반 +2 · cuVSLAM 프레임 간격 경고 +1 · 수신 버퍼 버림 520/s · SHM 오류 0
```

### 5.3 '깊이 614 kB · ≈ 9 MB/s'(§7.4 · 대화 답변, 10-12 §8.5 · §17 · §19 이어짐)
- 해상도를 확인하지 않은 계산값. 실제 발행 깊이는 데시메이션 ×4(09-08 N1.5 `decimation_filter.filter_magnitude: 4`)로 160×120 16UC1 · 직렬화 38 472 B(f2z1 bag 실측, 10-20 §7.5) — 칸 형식 기록은 [DDS 사고 카드 §5.6](dds-shm-incident.md). 이 정정이 '왜 nvblox 는 안 빠지나' 를 푼 열쇠였다.

## 6. 기록 어긋남 (원문 대조, 카드 작성 중)
1. **§7.3a 표 '−9 포함' 칸**: SUMMARY 는 팔 A '전체 −9 4 · 발행만 −9 재기동 4', 팔 B '7 · 8'. 원문 [`run_shm_test.txt`](../debug_log/2026-10-20/outputs/run_shm_test.txt) 는 주기마다 INT → TERM → KILL → 발행-9재기동 순환이라 A = KILL 4 · 발행-9 **3**, B = KILL 7 · 발행-9 **7**(B 의 INT · TERM 이 8 씩). 판정(오류 0)에는 영향 없음.
2. **세그먼트 크기**: §7.4 계획은 '카메라 8 MB · nvblox · cuVSLAM 4 MB; 합 16 MB', 실제 S1 코드는 파일 하나 8 MB 를 카메라 · cuVSLAM 이 같이 쓴다(`fastdds_shm_udp.xml` 23 행, `cuvslam_up.sh` 16 행이 같은 파일 복사). 시험용(`jobs/shm_test/fastdds_shm_udp.xml`)은 4 MB. [DDS 사고 카드 §4](dds-shm-incident.md) 의 'cuVSLAM 4 MB' 는 계획값을 옮긴 것이라 이번에 고침.
3. **잔재 16 개의 처리**: §7.2 는 `/dev/shm` 에 FastDDS 파일 16 개, §7.3 합격 (4) 는 '§7.2 의 기존 잔재 16 개는 첫 정리에서 처리 결과 기록' 이라 했으나, 시험 원문 첫 줄은 `시작 전 /dev/shm fastrtps 2 개`(팔 A 는 정리 없음) — 16 → 2 사이 무엇이 지웠는지 기록 없음.
4. **`outputs/chk_udp_drops.txt`**: §9.3 · §11.2 가 소켓별 포트 목록 · 조용한 창 '+0 · 578 054 → 578 054' 의 원문으로 이 파일을 적지만, 파일엔 `전체 RcvbufErrors 증가: 6973127` 한 줄뿐이다. 이 줄은 [`chk_udp_drops.sh`](../debug_log/2026-10-20/jobs/chk_udp_drops.sh) 마지막 줄이 '증가' 라는 이름표로 **누적값**을 찍은 것(소켓별 상위 8 줄 루프는 아무것도 안 찍음). `chk_udp_drops2.sh` 의 출력은 저장 안 됨 → **원천 소실**.
5. **`chk_shm_path.sh` 머리 주석**: 'V1 호스트 발행 → 호스트 구독, V2 호스트 발행 → 컨테이너 구독' — 코드 · 출력 · SUMMARY 는 'V1 모두 SHM 전용 · V2 발행만 SHM+UDP'. 주석이 고치기 전 설계로 남은 것(추정).
6. **§7.1 · §7.2 출력 원문 없음**: `rmem_max` 212 992 · 누적 3 716 712 · 39/s · 432/s · uid 1000 · 잔재 16 개는 SUMMARY 서술뿐(`chk_udp.sh` · `chk_udp_rate.sh` · `chk_uid.sh` 는 있음, `| tee` 없음).
7. **10-21 SHM 오류 줄**: 10-21 §18.2 표는 'DDS 공유메모리 오류로 전달이 막혔다' 를 '처음 추론' 칸에 두어 틀린 추론처럼 읽히지만, 오류 줄 자체는 실제 출력에 있다(`run_nv_static_try1.txt` 31 행). 0 Hz 의 원인이 아니었을 뿐, 오류가 왜 났는지는 다루지 않았다.
8. **10-21 그림자 + SHM prep 스크립트**: §1 · §4 가 쓰는 `prep_sm_1021.sh` 는 10-21 `jobs/` 에 없다(출력 `prep_sm_1021_*.txt` 만 있음) — **원문 없음**.
9. **[DDS 사고 카드](dds-shm-incident.md) 첫 판의 미리 쓴 요약**: '정리 없이 −9 를 섞은 재기동 시험이 15/15 · 30/30'(30/30 은 clean 뒤) · '10-23 부터 카메라 ↔ cuVSLAM 경로만 SHM'(SHM 운용은 10-21 주행부터, 10-23 은 `prep_patrol.sh` 기본) — 이번에 그 카드에서 고침.

## 7. 남은 것
- 'IR 이 SHM 으로 간다' 의 같은 창 직접 근거(cuVSLAM 소켓 하나의 drops, 측정 노드 없이) — 안 함.
- SHM 전용 참가자가 UDP 참가자를 못 찾는 기전(§7.3c) — 미확인. 실제 구성은 SHM+UDP 라 운용 영향은 없음.
- 메시지가 버퍼에서 버려지는 단위(조각 하나 손실 → 메시지 전체) — 추정, 조각 단위 측정 없음.
- 수신 버퍼 상향 — 사용자 결정 사항으로 남음. 큰 메시지가 UDP 로 가는 다른 쌍(예: 깊이를 올리면 카메라 → nvblox, §7.5 C3)에는 같은 한계.
- `prep_fast.sh` 70 행 SHM 오류 검사가 `cuvslam.log` · nvblox 로그를 안 본다 — SHM 을 쓰는 쪽 로그가 빠진 셈(고침 안 함, 이 카드 작성 중 발견).
- 10-21 nv1 시험 컨테이너의 SHM 오류(`port7413`) — 원인 미확인(`-v /dev:/dev` 로 `/dev/shm` 이 덮인 것과 관련 있는지 모름). 그 컨테이너는 운용에 안 씀.
- 낡은 주석 `fastdds_udp_only.xml` 19~21 행 '원인 제거' — 10-20 정정 반영 안 됨.
- 10-12 §17 사용자 결정 '프로세스 간 전달은 DDS SHM' 가운데 실제로 옮긴 것은 이 한 쌍뿐. 나머지 경로는 '이득 측정 없으면 UDP' (§7.4 원칙)로 남음 — 다시 정한 문장은 없음.
- 이후(10-26 ~): 10-27 §22 'SLAM stamp 정체는 통신 탓 아님 → 공유메모리로는 안 풀림'([SLAM stamp 정체](slam-stamp-freeze.md)). 다음 시기에서 채움.

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| f2v1 | 그림자 주행 UDP — 증상(9.5 Hz) | `2026-10-20/outputs/run_f2v1.txt` |
| §7.1 커널 · 카운터 | rmem · RcvbufErrors · SIGSTOP 대조 | `2026-10-20/jobs/chk_udp.sh` · `chk_udp_rate.sh`(출력 원문 없음) |
| SHM 재기동 팔 A · B | 15/15 · 30/30 | `jobs/shm_test/run_shm_test.sh` → `outputs/run_shm_test.txt` |
| SHM 전용 · 경로 판별 | 0 Hz 30/30 · V1 150 / V2 0 | `jobs/shm_test/run_shm_test_shmonly.sh` · `chk_shm_path.sh` → `outputs/run_shm_test_shmonly.txt` · `chk_shm_path.txt` |
| 크기별 UDP | 38 kB · 307 kB · 307 kB × 2 · 614 kB | `jobs/shm_test/chk_udp_size.sh` · `size_talker.py` → `outputs/chk_udp_size.txt` |
| S1 배포 | 3 파일 + 프로파일 · 빌드 | `jobs/up_shm.sh` · 커밋 `8e31e2b1` |
| S2 sh_u1 · sh_s · sh_u2 | 정지 A/B | `jobs/run_shm_static.sh` · `get_sh.sh` → `outputs/run_shm_static.txt` · `anal_shm_static_box.txt`, bag `~/bags/sh_*`(Jetson, 수십 MB) |
| 소켓별 버림 | 측정 오염 추적 | `jobs/chk_udp_drops.sh` · `chk_udp_drops2.sh` → `outputs/chk_udp_drops.txt`(한 줄, §6-4) |
| S3 | 재기동 10/10 | `jobs/run_shm_restart.sh` → `outputs/run_shm_restart.txt` |
| 그림 | (a) 크기별 · (b) 정지 A/B · (c) 재기동 | `jobs/fig_shm_day.py` → [`figures/shm_day_summary.png`](../debug_log/2026-10-20/figures/shm_day_summary.png) · 정리 페이지 `figures/day_summary_1020.html` |
| f2sm1 | SHM 그림자 주행 15.0 Hz | `2026-10-21/outputs/run_f2sm1.txt` · `chk_f2sm1_logs.txt` · `gaps_f2sm1.txt` |
| 운용 주행 13 회 로그 | SHM 프로파일 · 오류 0 · `vslam_twist` 통계 | `2026-10-22/bags/logs_*` · `2026-10-23/bags/logs_*`(git 제외) |

## 9. 도구 해설
공통: 10-20 의 Jetson 도구는 PC 스크래치패드 → Jetson `/tmp` 로 올려 `run_jn.sh` 로 실행(로버 안 움직임). 합성 시험은 도메인 88(실행 중 스택 도메인과 분리), 시험 노드 이름 `shmt_*`.

### 9.1 `chk_udp.sh` — 커널 UDP 설정 · 카운터 (Jetson, bash, 읽기만) · §7.1
- 왜: f2v1 입력 빠짐이 '전달' 문제인지 — 수신 버퍼 크기와 버림 카운터를 본다.
- 하는 일: `sysctl net.core.rmem_max rmem_default wmem_max net.ipv4.ipfrag_high_thresh ipfrag_time` · `docker inspect … net=… ipc=…` · `netstat -su` 에서 receive buffer · packet receive errors · reassembl 줄 · `/proc/net/snmp` Ip 줄 17 번째 값(ReasmFails).
- 출력: 화면 — **원문 없음**(SUMMARY 서술: `rmem_max = rmem_default = 212 992`, net=host · ipc=host, 누적 RcvbufErrors 3 716 712). 쓰인 곳 §7.1.
- 재사용: 가능. 계보: 10-13 `chk_jetson_state.sh` 8 행(rmem_max 만) → 이 판.

### 9.2 `chk_udp_rate.sh` — 버림 속도 · cuVSLAM 일시정지 대조 (Jetson, bash) · §7.1
- 하는 일: `e()` = `/proc/net/snmp` 두 번째 `Udp:` 줄 6 번째 열(RcvbufErrors). 20 s 차분 → 컨테이너 안 cuVSLAM pid 에 `kill -STOP` → 20 s 차분 → `kill -CONT`.
  ```bash
  e() { awk '/^Udp:/{n++} n==2 && /^Udp:/{print $6; exit}' /proc/net/snmp; }
  P=$(docker exec $CN bash -c "pgrep -f '__node:=cuvslam_[c]ontainer'" | head -1); docker exec $CN kill -STOP $P
  ```
- 출력: '그림자 구성(정지) 20 s: 수신 버퍼 오류 +N (초당 n)' · 'cuVSLAM 일시정지(SIGSTOP) 20 s: …' — **원문 없음**(SUMMARY 39/s · 432/s).
- 결함: 시스템 전체 카운터라 창 안의 모든 소켓 몫(§5.2 와 같은 함정 — 이 시험엔 새 참가자 없음). SIGSTOP 대조는 cuVSLAM 프로세스의 모든 소켓을 멈춰 IR 몫만 가르지 못한다(§3).
- 주의: 로버 안 움직임이지만 실행 중 cuVSLAM 을 20 s 멈춘다(그림자 구성이라 주 EKF 영향 없음).

### 9.3 `chk_uid.sh` — SHM 파일 권한 조건 (Jetson, bash) · §7.2
- 호스트 `id jetson` · 컨테이너 `id admin` · `/dev/shm` fastrtps 수 · `ls -la /dev/shm` 8 줄. 출력 원문 없음(SUMMARY: 둘 다 uid 1000 → 권한 충돌 없음, 파일 16 개).

### 9.4 `jobs/shm_test/` 합성 노드 세 개 (Jetson 호스트 · 컨테이너, Python rclpy) · §7.3 · §7.5
- `shm_talker.py 이름`: `/shmt/ir1` · `/shmt/ir2` 에 640×480 mono8(0 으로 채운 307 200 B) 15 Hz, 깊이 5(기본 reliable).
- `shm_listener.py 이름 상태파일`: 두 토픽을 `qos_profile_sensor_data`(best effort — cuVSLAM · nvblox 와 같음)로 구독, 매초 `'%.3f %d %d'`(시각 · 누적 수 두 개)를 상태파일에 원자 교체 · pid 파일.
- `shm_idle.py 이름`: 빈 노드(참가자 수 · 재기동 소란 역).
- `size_talker.py 이름 폭 높이 화소바이트 줄수`: 크기만 바꾼 talker(1 = mono8, 2 = 16UC1).

### 9.5 `jobs/shm_test/fastdds_shm_udp.xml` · `fastdds_shm_only.xml` — 시험 프로파일
- shm_udp: SHM(`segment_size 4194304`) + UDPv4, `useBuiltinTransports false`, 기본 참가자 프로파일. shm_only: 위에서 UDP transport 블록 · `userTransports` 의 udp 줄만 지운 것(diff 2 곳). 저장소 판(§9.9)은 8 MB.

### 9.6 `run_shm_test.sh` — SHM 재기동 시험 (Jetson, bash, 인자 `[NA=15] [NB=30]`, 환경 `CPROF`) · §7.3a · §7.3b
- 왜: 09-09 실패가 종료 · 정리 방식 문제인지 SHM 자체인지 측정으로 가른다(§7.2).
- 한 주기(`cycle`): (팔 B 만) `fastdds shm clean` → 6 s 기준 UDP 데이터그램/s(`/proc/net/snmp` Udp 2 열 InDatagrams) → `start_all`(호스트 talker · 호스트 listener · idle 2 + `docker exec -d -u admin` 컨테이너 listener, 프로파일 `${CPROF:-/tmp/fastdds_shm_udp.xml}`) → 6 s → `rate`(6 s 동안 컨테이너 · 호스트 수신 Hz 와 UDP 증가) → 종료. 종료 방식 = `(번호−1) % 4` → INT · TERM · KILL · '발행-9재기동'(talker 만 −9 → 2 s → 새 talker → 6 s rate → 전체 INT). `stop_all` 은 10 s 기다린 뒤 남으면 −9. SHM 오류 = 로그의 `open_and_lock_file|RTPS_TRANSPORT_SHM|init_port|Failed to create|SHM Error` 수.
  ```bash
  local mode=$(( ($2 - 1) % 4 )) MN=(INT TERM KILL "발행-9재기동")
  [ $1 = B ] && CL=$(fastdds shm clean 2>&1 | tail -1 | cut -c1-60) || CL="-"
  printf "%s%02d %-12s 정리[%s] 기준 UDP %d/s | 구독 컨테이너·호스트 Hz·UDP/s: %s%s | SHM오류 %d | 끝 /dev/shm %d\n" …
  ```
- 출력 [`run_shm_test.txt`](../debug_log/2026-10-20/outputs/run_shm_test.txt)(104 줄; −9 때 bash 'Killed' 줄 섞임):
  ```
  A15 KILL         정리[-] 기준 UDP 5132/s | 구독 컨테이너·호스트 Hz·UDP/s: 15.0 15.0 15.0 15.0 5121 | SHM오류 0 | 끝 /dev/shm 41
  B01 INT          정리[12 zombie segments cleaned] 기준 UDP 5130/s | 구독 컨테이너·호스트 Hz·UDP/s: 15.0 15.0 15.0 15.0 5149 | SHM오류 0 | 끝 /dev/shm 2
  B16 발행-9재기동 정리[5 zombie segments cleaned] 기준 UDP 11178/s | … 15.0 15.0 15.0 15.0 5129 | 발행 재기동 뒤 15.0 15.0 | SHM오류 0 | 끝 /dev/shm 10
  B24 발행-9재기동 정리[1 zombie segments cleaned] 기준 UDP 5104/s | … 15.0 15.0 15.0 15.0 5683 | 발행 재기동 뒤 15.0 15.0 | SHM오류 0 | 끝 /dev/shm 10
  마지막 정리: 0 zombie segments cleaned · /dev/shm fastrtps 10
  ```
  팔 B 컨테이너 두 줄 Hz: 15.0 · 15.0 이 28 주기, 14.8 이 한 줄씩 2 주기(카드 작성 중 셈).
- 판정 (3) 'UDP 증가 < 86/s' 는 같은 창 기준선 대비라 실행 중 스택 UDP(≈ 5 100/s)의 흔들림에 묻힌다(B16 · B24) — §5.2 기전으로 추정.
- `run_shm_test_shmonly.sh`(§7.3b): `CPROF=/tmp/fastdds_shm_only.xml bash /tmp/run_shm_test.sh 0 30` — 컨테이너 구독만 SHM 전용. 결과 0 Hz 는 설계 결함(§5.1).
- 재사용: 가능(도메인 88 · 합성, 로버 무관). 계보: 없음(이날 만) — 실제 스택판은 §9.12.

### 9.7 `chk_shm_path.sh` — 경로 판별 V1 · V2 (Jetson, bash) · §7.3c
- 하는 일: 호스트 · 컨테이너 `/dev/shm` inode 와 fastrtps 수 비교, hostname 비교 → `fastdds shm clean` → `run`(talker · 호스트 listener · 컨테이너 listener 를 각자 프로파일로, 12 s 뒤 상태파일 출력 → INT 3 s → −9 → clean). 결과는 §5.1 발췌.
- 결함: 머리 주석이 코드와 다름(§6-5). 상태파일 값은 Hz 가 아니라 누적 수(약 6~10 s 분량).

### 9.8 `chk_udp_size.sh` — 크기별 UDP 빠짐 (Jetson, bash) · §7.5
- 하는 일: 모두 `fastdds_udp_only.xml`(설치본 복사), 컨테이너 listener + `size_talker.py`. 조건마다 5 s 대기 → 20 s 동안 수신 수 · RcvbufErrors 차분. 조건 순서 '발행 없음 → C1 → C4 → C2 → C3' 를 두 번.
  ```bash
  one "C1 160×120×2B ×1 (38 kB, 지금 깊이)" 160 120 2 1
  one "C2 640×480×1B ×2 (307 kB ×2, IR 좌우)" 640 480 1 2
  ```
- 출력 [`chk_udp_size.txt`](../debug_log/2026-10-20/outputs/chk_udp_size.txt)(머리에 WSL 깨진 글자 한 줄):
  ```
  ##### 반복 2
    발행 없음(기준)              수신   0.0 /   0.0 Hz · 수신버퍼 버림   13/s
    C1 160×120×2B ×1 (38 kB, 지금 깊이) 수신  15.0 /   0.0 Hz · 수신버퍼 버림   11/s
    C4 640×480×1B ×1 (307 kB, IR 한 줄) 수신  14.8 /   0.0 Hz · 수신버퍼 버림   10/s
    C2 640×480×1B ×2 (307 kB ×2, IR 좌우) 수신  14.2 /  12.8 Hz · 수신버퍼 버림   16/s
    C3 640×480×2B ×1 (614 kB, 깊이 원본) 수신  13.3 /   0.0 Hz · 수신버퍼 버림   19/s
  ```
  (한 줄 조건의 두 번째 열 0.0 은 토픽이 없어서 — 정상.)
- 결함: 버림 카운터는 시스템 전체(실행 중 스택 몫 7~13/s 포함). 조건당 20 s · 2 회.

### 9.9 저장소 `fastdds_shm_udp.xml` · `camera.launch.py` · `ekf.launch.py` · `cuvslam_up.sh` — N-SHM 배선 (10-20 §9.1)
- 줄 번호는 §4.1. 흐름: `prep_patrol.sh`(ODOM=vslam) → `SENSORS_ADD`/`EXTRA_SENSORS` 에 `dds_shm:=true` → `sensors.launch.py` 가 `camera.launch.py` · (8 s 뒤) `ekf.launch.py` 를 포함 → 카메라 프로세스 `additional_env` · `cuvslam_up.sh` 3 번째 인자. 확인 방법: `/proc/<카메라 pid>/environ` 의 FASTRTPS · `/tmp/sensors.log` 의 `[cuvslam_up] … DDS fastdds_shm_udp.xml`(§9.10 이 씀).
- 배포 도구 [`up_shm.sh`](../debug_log/2026-10-20/jobs/up_shm.sh): `/tmp/vs_*` 를 rover_bringup src 에 덮고(원본 `.bak_<시각>`) `colcon build --symlink-install --packages-select rover_bringup`, 설치본 xml `ls -la`.

### 9.10 `run_shm_static.sh` — S2 정지 A/B (Jetson, bash) · §9.2 · §9.3
- 하는 일: bag 이름 충돌 검사(`~/bags/sh_u1 · sh_s · sh_u2`) → 조건 u1 · s · u2 · s_end 마다 `SENSORS_ADD="$SA" bash /tmp/prep_patrol.sh lite` → `tf2_echo map odom` 8 s(위치 추정) → 카메라 pid environ · 래퍼 로그로 프로파일 확인 → 20 s → 카운터 · 로그 줄 수(EKF 'Failed to meet update rate' · cuVSLAM 'Delta between') → `chk_vslam_live.py 60` → 차분 → nvblox 로그 'NVBlox Rates' 블록 → 25 s `ros2 bag record`(깊이 · camera_info · `static_map_slice` · /tf, QoS 덮어쓰기 best effort). 마지막 s_end 는 prep 만(다음 단계용).
- 출력 발췌 §5.2. 결함: 카운터 창 안에 새 참가자 둘(`tf2_echo` 는 창 전이지만 측정 노드는 창 안) — §5.2. 그 밖 판정은 같은 노드가 낸 Hz · 로그 줄이라 영향 없음.
- `chk_vslam_live.py`: 주 해설은 [cuVSLAM 카드](cuvslam-velocity-fusion.md)(10-20 §6.1 판). 여기선 토픽 4 개 Hz · 이동량과 `/proc` 프로세스 CPU 만 썼다.
- `get_sh.sh`(PC/WSL): bag 3 개를 스크래치패드로 scp(비밀번호는 스크래치패드 러너에서 읽음) → `anal_box_static.py`(§2 도구, 해설은 [유령 칸 카드](ghost-cells-depth-preset.md))로 [`anal_shm_static_box.txt`](../debug_log/2026-10-20/outputs/anal_shm_static_box.txt):
  ```
  == s: 깊이 330 장 · … | 조각(마지막 5 s, 48 개) 상자 칸 14 · 북 +6.4 · 서 +2.4 cm · 빈 바닥 유령 칸 0 · 빈 바닥 미지 21 %
  ```

### 9.11 `chk_udp_drops.sh` · `chk_udp_drops2.sh` — 소켓별 버림 (Jetson, bash, 읽기만) · §9.3 · §11.2
- `chk_udp_drops.sh`: `/proc/[0-9]*/fd/*` 의 `socket:[inode]` → pid · comm 표, `/proc/net/udp` 의 (inode, drops) 10 s 차분 상위 8 → 마지막 줄 '전체 RcvbufErrors 증가: <누적값>'(이름표와 달리 누적값). 출력 [`chk_udp_drops.txt`](../debug_log/2026-10-20/outputs/chk_udp_drops.txt) 은 그 마지막 줄 하나 — 상위 8 루프가 비었다(조용한 창이라 증가 소켓이 없었을 수 있음, 추정).
- `chk_udp_drops2.sh`: `/proc/net/udp` 머리 3 줄 · 소켓 수 · drops > 0 소켓 수 → 10 s 동안 RcvbufErrors 차분과 소켓 drops 합 → drops 상위 5(drops · 로컬 주소:포트(16 진) · inode). SUMMARY 의 포트 7410(0x1CF2) 등은 여기서 나왔다 — 출력 **원천 소실**.
- 재사용: 가능. 다음에 쓸 때 `| tee outputs/…`.

### 9.12 `run_shm_restart.sh` — S3 실제 스택 재기동 (Jetson, bash, 인자 `[N=10]`) · §9.4 · §9.5
- 하는 일: 회마다 `SENSORS_ADD="emitter_off:=true vslam:=shadow dds_shm:=true" bash /tmp/prep_patrol.sh lite` → PREP_OK 줄 수 · prep 의 'SHM 고아' 줄 → 25 s → **로그로만**: sensors.log 의 마지막 `vslam_twist]: 출력 N · 버림 M` · nvblox 로그 depth_image_callback Hz · `tf2_echo` yaw · SHM 오류(sensors · nvblox · cuvslam 로그). 3 · 6 · 9 회 카메라 −9, 4 · 8 회 nvblox −9, 7 회 cuVSLAM −9 → 10 s 뒤 `/dev/shm` 수 · 오류 · 남은 프로세스.
  ```bash
  err() { cat /tmp/sensors.log /tmp/nvblox_node.log /tmp/cuvslam.log 2>/dev/null | grep -acE 'open_and_lock_file|RTPS_TRANSPORT_SHM|init_port'; }
  3|6|9) pkill -9 -f 'realsense2_camera_[c]ontainer'; K="카메라 -9";;
  ```
- 출력 [`run_shm_restart.txt`](../debug_log/2026-10-20/outputs/run_shm_restart.txt):
  ```
  03 PREP_OK 2 · SHM 고아 정리: 2 zombie segments cleaned · 남은 fastrtps 12 · vslam_twist[출력 150 · 버림 0] · nvblox 깊이 15.1 Hz · map→odom yaw 0.655° · SHM 오류 0 | 카메라 -9 → 10 s 뒤: /dev/shm 26 · SHM 오류 0 · 남은 카메라 0 nvblox 1 cuVSLAM 1
  07 PREP_OK 2 · SHM 고아 정리: 1 zombie segments cleaned · 남은 fastrtps 12 · vslam_twist[출력 150 · 버림 0] · nvblox 깊이 15.1 Hz · map→odom yaw 0.067° · SHM 오류 0 | cuVSLAM -9 → 10 s 뒤: /dev/shm 21 · SHM 오류 0 · 남은 카메라 1 nvblox 1 cuVSLAM 0
  끝: /dev/shm fastrtps 28
  ```
  ('PREP_OK 2' 는 PREP_OK 가 든 줄 수 — `chk_prep.py` 136 행의 `PREP_OK` 와 `prep_fast.sh` 끝 줄 `prep 끝 — $(tail -1 /tmp/prepchk.txt)` 두 줄.) yaw −0.023 ~ 1.005°.
- 결함 · 범위: −9 뒤 '남은 쪽' 은 10 s 생존만 봄(데이터 흐름은 안 봄). `tf2_echo` 는 새 참가자지만 카운터를 안 재므로 §5.2 함정과 무관.

### 9.13 `fig_shm_day.py` — 하루 SHM 그림 (PC, matplotlib)
- §7.5 · §9.3 · §9.5 수치를 **출력 원문에서 손으로 옮겨** 세 칸 그림(독스트링 명시). (a) 307 kB × 2 막대는 두 줄 평균(14.5 · 13.5). 출력 [`shm_day_summary.png`](../debug_log/2026-10-20/figures/shm_day_summary.png). 재사용 불가(수치 하드코딩).

### 9.14 (11-03 카드 작성 중) 운용 주행 13 회 로그 재검
- PC Git Bash, 저장소 `Docs/debug_log/` 에서(입력 = 러너가 보관한 sensors · nav2 · slam 로그, git 제외 폴더):
  ```bash
  for d in 2026-10-2[2-3]/bags/logs_*; do echo "$d shm_prof=$(grep -ac 'fastdds_shm_udp' $d/sensors.log) shmerr=$(cat $d/*.log | grep -acE 'open_and_lock_file|RTPS_TRANSPORT_SHM|init_port')"; done
  grep -a 'vslam_twist\]: 출력' $d/sensors.log | grep -o '출력 [0-9]* · 버림 [0-9]*' | awk '{o=$2; b=$5; n++; bs+=b; if(b>bm)bm=b; if(o<140)lo++; a[n]=o} END{asort(a); printf "창 %d · 출력 중앙 %d · <140 창 %d · 버림 합 %d · 창 최대 %d", n, a[int((n+1)/2)], lo, bs, bm}'
  ```
  ```
  logs_f2lp1 창 56 · 출력 중앙 150 · <140 창 3 · 버림 합 54 · 창 최대 52
  logs_f2pi1 창 73 · 출력 중앙 150 · <140 창 2 · 버림 합 11 · 창 최대 6
  logs_f2rp1 창 68 · 출력 중앙 150 · <140 창 1 · 버림 합 0 · 창 최대 0
  logs_f2von2 창 44 · 출력 중앙 150 · <140 창 1 · 버림 합 0 · 창 최대 0
  (13 개 모두 shm_prof=1 · shmerr=0, 출력 중앙 150)
  ```
- 결과 파일은 남기지 않음 — **발췌가 전부**. 창은 prep 뒤부터 주행 끝까지(정지 구간 포함), `<140` 창은 기동 직후 · bag 시작과 겹치는지 따로 안 봄. f2lp1(두 바퀴)의 한 창 버림 52 는 원인 안 봄. cuVSLAM · nvblox 자체 로그는 보관 대상이 아니라 못 봄.

## 10. 용어
- **소켓 수신 버퍼(`SO_RCVBUF`, `net.core.rmem_default` · `rmem_max`)**: 커널이 UDP 소켓마다 받아 둔 데이터그램을 앱이 읽을 때까지 담는 크기. 넘치면 새 데이터그램을 버리고 `/proc/net/snmp` 의 Udp `RcvbufErrors` · `/proc/net/udp` 의 소켓별 `drops` 가 는다. 앱이 더 크게 요청해도 `rmem_max` 까지만(올리려면 sysctl · sudo).
- **RTPS 조각(fragment)**: Fast DDS 가 UDP 한 데이터그램(≈ 64 kB)보다 큰 메시지를 나눠 보내는 단위. best effort 에선 조각 하나만 잃어도 그 메시지 전체를 못 맞춘다(일반 동작 설명 — 이 장비에서 조각 단위로 잰 적은 없음).
- **SHM transport · segment**: Fast DDS 의 같은 호스트 전송. 참가자마다 `/dev/shm` 에 쓰는 쪽 세그먼트(`segment_size`)와 포트 · 잠금 파일을 만든다. 호스트 ↔ 컨테이너는 `ipc=host` 로 같은 `/dev/shm` 을 볼 때만(이 장비 inode 1 확인).
- **`fastdds shm clean`**: Fast DDS 공식 도구 — 아무 프로세스도 잡고 있지 않은 SHM 세그먼트 · 포트만 지운다('N zombie segments cleaned'). `rm -f /dev/shm/fastrtps_*` 와 달리 살아 있는 참가자 파일은 건드리지 않는다.
- **SHM+UDP 혼합 · 발견**: 참가자가 가진 transport 집합으로 서로를 찾는다. SHM+UDP 참가자와 UDP 전용 참가자는 UDP 로, SHM+UDP 끼리는 같은 호스트면 SHM 으로 데이터를 보낸다(10-20 §7.3c 측정과 맞는 범위). SHM 전용 참가자는 SHM+UDP 참가자를 못 찾았다(기전 미확인).
- **발견 폭주**: 새 DDS 참가자가 붙으면 기존 참가자 전부가 그 참가자에게 자기 정보 · 엔드포인트를 보낸다 — 참가자 ≈ 26 개면 한꺼번에 몰려 발견 포트(7400 대) 소켓이 넘친다(10-20 §11.2 추론). '주행 30 s 전 참가자 생성 금지' 규칙이 피하려는 것.
- **N-SHM**: 10-20 §7.4 계획 이름 — 카메라 ↔ 컨테이너(처음엔 nvblox · cuVSLAM, §7.5 뒤 cuVSLAM 만) 공유메모리 전송. 단계 S1 코드 · S2 정지 A/B · S3 재기동 · S4 주행(10-21 f2sm1) · S5 결정(10-23 prep 기본).
- **데시메이션 ×4**: RealSense `decimation_filter.filter_magnitude: 4` — 깊이를 가로 · 세로 1/4(640×480 → 160×120)로 줄임. IR 에는 안 걸린다.
