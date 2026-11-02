# Isaac · cuVSLAM 평가 — rf2o 야외 적합성 · 사람 마스크 · JetPack 6.2 · 프로젝터 충돌 (5 시기: 09-29 §6~§11)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| 09-29 시점 **보류**(사용자 결정 §11 — 기능 완성 우선, Isaac 심화는 JetPack 7.2 이전 뒤). 측정으로 확인한 것: cuVSLAM 3.2.6 이 JetPack 6.2.2 에서 동작 · 정지 드리프트 0.44 cm · CPU 22.8 %(사람 있으면 88.1 %), 프로젝터 번갈이 60 Hz 실현 가능. 이후: 10-19 사용자가 '7.2 뒤로' 는 일정 결정이었다며 재개 → 10-21 프로젝터 **상시 끔**(09-29 에 기각한 O2)으로 결정 → **10-23 주 EKF 병진 = cuVSLAM**(아래 §7) | 09-29 | [09-29 §6](../debug_log/2026-09-29/SUMMARY.md) (rf2o 도입 계획 전 사용자 요청) | 09-29 에 스택 설정은 안 바꿈. 시험용만: [`vslam_standalone.launch.py`](../debug_log/2026-09-29/jobs/vslam_standalone.launch.py) · `job644`~`job654`(전부 [`2026-09-29/jobs/`](../debug_log/2026-09-29/jobs/)). 문서: `Docs/04_navigation/NAV2_EXPLORATION_PLAN.md §7.4`, CLAUDE.md §6 상태 줄(§11 반영) | [제자리 회전 옆 밀림 F0-a](f0-rotation-side-slip.md)(왜 병진 관측이 필요한가 — 방향 D) · [센서 컨디셔너](sensor-conditioner.md)(B2 · B3) · [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md)(rf2o 이후 칸) · [Phase N 후반 N6 · 유령 셀](nvblox-n6-global-ghosts.md)(nvblox 가 쓰는 깊이) · [깊이 점군 아티팩트 · depth_relay](depth-relay-artifacts.md) · [DDS 공유메모리 사고](dds-shm-incident.md)(호스트 → 컨테이너 영상 전달) |

**한 줄**: 09-23 에 정한 방향 D(라이다 · 영상 오도메트리의 속도를 odom EKF 에)를 실행하기 전에 사용자가 순서와 강건성을 물었다. rf2o 는 실내 구조에 맞고 야외 · 사람에는 약하다(원리 추정) → 사람 강건성을 rf2o 도입의 필수 조건으로 넣음(§6 · §6.1). cuVSLAM 의 사람 마스크는 Isaac ROS 5.0(JetPack 7.2 · Jazzy)에서만 쓸 수 있어 지금 플랫폼(JetPack 6.2.2 · Humble · Isaac 3.2)에선 불가(웹 확인, §7 · §8.1). 그래도 컨테이너에 이미 깔린 cuVSLAM 3.2.6 을 **단독으로 돌려 보니 동작했고**(정지 0.44 cm · 사람 걸어도 1.10 cm, §9), 남은 장애물은 같은 카메라를 nvblox(프로젝터 켬)와 cuVSLAM(프로젝터 끔)이 나눠 써야 하는 충돌이었다 → 측정으로 '상시 끔'(O2)을 기각하고 '번갈이'(O1)를 골랐다(§10.1). 사용자는 여기서 Isaac 심화를 미루고 기능 완성을 먼저 하기로 했다(§11).

## 1. 증상 · 질문
- §6 사용자: rf2o 를 넣기 전에 야외(농경지 등)에도 맞는가?
- §6.1 사용자: "야외가 아니더라도 사람이 돌아다니는 상황은 계속 일어난다. 그 정도 강건성은 필요하다."
- §7 사용자: "cuVSLAM 은 사람 특정이 가능하지 않나? 순서를 바꿀 생각 진행."
- §8 사용자: 지금 JetPack 6.2 가 맞는가, NITROS 는 쓸 만한가.

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-29 §6 | rf2o 야외 적합성 표(웹 출처 + 원리) | rf2o = range flow 조밀 정합, 단일 코어 0.9 ms(출처 수치). S2L 18 m · ±30 mm · 80 klx · IP65(사양) | 실내 도구, 야외는 **보조** 입력 — 퇴화 인지형 가변 공분산을 필수로 | 웹(MAPIRlab README · ICRA 2016 · 제조사 사양), 저장소 원문 없음 |
| 09-29 §6.1 | 사람 강건성 대책 설계 | — (설계만) | 자이로 일치 · 정지 검사 · Mahalanobis 거부 · 가변 σ, 시험 T1~T3 | — |
| 09-29 §7 | cuVSLAM 마스크 · 버전 조사 | 마스크 = Segformer 사람 분할(튜토리얼 플랫폼 Thor + D435). RealSense 마스크 경로는 Isaac 4.6.0 에서 깨졌고 5.0.0(2026-09-21)에서 수정. 4.x/5.x = Jazzy, Orin 은 4.6.0 부터 JetPack 7.2. Isaac 3.2 문서 VSLAM 튜토리얼엔 마스크 없음 | **지금 플랫폼에선 마스크 불가**. 순서 안 A/B/C 중 **C(현 순서 유지) 권함** | 웹, 원문 없음. 우리 L4T R36.5 · Ubuntu 22.04 · 컨테이너 humble 은 측정 |
| 09-29 §8 | `job644` 플랫폼 버전 · 영상 경로 | L4T 36.5.0 · CUDA 12.6 · nvblox 3.2.5 · **isaac_ros_visual_slam 3.2.6 설치됨**(실행한 적 없음) · nitros 3.2.5. 영상 경로 CPU: realsense 14.9 · nvblox 16.8 · depth_relay 4.2 → 합 ≈ 36 %, rplidar 18.6 · EKF 12.0 · controller 11.9 | 6.2.2 는 Isaac 3.2 지원 범위(6.1 · 6.2). **NITROS 는 5.0 부로 deprecated** + 지금 영상 경로에 끼어들 자리 없음 → 우리 코드엔 안 씀. cuVSLAM 을 붙일 땐 컨테이너 한 component container 합성 권함 | [`outputs/j644_platform.txt`](../debug_log/2026-09-29/outputs/j644_platform.txt) |
| 09-29 §9 | cuVSLAM 단독 실행 — **판정 전 선언**(V1-a ≥ 25 Hz · 끊김 0, V1-b 60 s 정지 ≤ 1 cm · ≤ 0.2°, V1-c 기록, V1-d 사람 ≤ 2 cm · 끊김 0) | 기동: IR 30.0 Hz · IMU 199.7 Hz · 프로젝터 0, tracker 생성 4.8 s. **V1-a** 29.7 Hz · 최대 간격 0.080 s · vo_state 1 = 1784/1784. **V1-b** xy 0.44(최대 0.51) cm · yaw +0.150° · z −0.98 cm. **V1-c** cuVSLAM 22.8 % · 카메라 13.1 % · GPU 5 % | V1-a · b 통과(yaw 여유 작음) | [`outputs/j646_649_vslam_v1.txt`](../debug_log/2026-09-29/outputs/j646_649_vslam_v1.txt) |
| 09-29 §8.1 | Orin Nano 에서 JetPack 7 가능? | JetPack 7.2 가 Orin 전체 지원, 최신 7.2.1(2026-08), SD 이미지 없음(ISO) | B 안(이전)이 Orin Nano 에도 공식 경로가 있음 — 판단은 그대로 | 웹, 원문 없음 |
| 09-29 §9.2 | V1-d 사람(사용자가 0.5~2 m 를 35 s 걸음) | xy 1.10(최대 1.22) cm · yaw +0.074° · vo_state 934/934 · 28.1 Hz · 최대 간격 0.340 s · **CPU 88.1 %**(정지 22.8 %의 약 4 배) | **V1-d 통과** — 정지 상태에서 1 차 방어. CPU 상승 원인 미확정 | 같은 파일 끝부분 |
| 09-29 §10 | 프로젝터 충돌 해결 후보 O1~O4 + **판정 전 선언**(O2 채택 조건: 끔 상자 점 ≥ 켬 80 % **그리고** 아래쪽 유효 ≥ 켬 90 %; O1 실현 조건: 깊이 · IR ≥ 55 Hz · 메타 번갈이 · 카메라 CPU 증가 ≤ 15 %p) | `realsense_splitter` 는 컨테이너 · apt 에 없음(소스 빌드 필요). 호스트 드라이버 4.58.3 에 `emitter_on_off` 있음 | — | [`outputs/j651_654_emitter.txt`](../debug_log/2026-09-29/outputs/j651_654_emitter.txt) 앞부분 |
| 09-29 §10.1 | M1 · M2 측정(로버 정지) | M1 켬 유효 61.6/61.1 % · 아래 42.9/41.9 % · 상자 점 2810/2820 vs 끔 24.7/24.9 % · **아래 19.2/19.1 %** · 상자 점 3086/3096. M2 깊이 59.5 · IR1 59.9 · IR2 59.7 Hz, `frame_emitter_mode` 0/1 매 프레임 교대, 카메라 CPU 9.8 % | **O2 불채택**(아래 유효 = 켬의 45 %, 기준 90 %), **O1 채택**(조건 모두 충족) | 같은 파일 |
| 09-29 §11 | **사용자 결정** | — | 기능 완성 우선 ①F0 나머지 → ②정지 수단 → ③F1 → ④F2 기준선 → ⑤JetPack 7.2 이전 Phase(cuVSLAM + 마스크 · O1 · rf2o · 사람) | CLAUDE.md §6 · `NAV2_EXPLORATION_PLAN.md §7.4` |

## 3. 가설과 판별
| 가설 · 질문 | 판별 | 결과 | 판정 |
|---|---|---|---|
| rf2o 는 야외 주 입력이 될 수 있다 | 원리 · 출처 비교(§6 표) | 개활지 · 작물 줄은 병진 관측 퇴화, 평면 · 정적 가정 위반 | 기각 — **원리 추정**(실측 없음) |
| 순서를 바꾸면(cuVSLAM 먼저) 사람 강건성이 생긴다 | 버전 · 플랫폼 조사(§7 · §8.1) | 마스크는 Isaac 5.0 = JetPack 7.2 · Jazzy 뿐 | 기각 — 순서와 무관하게 플랫폼 이전이 필요(웹 출처) |
| cuVSLAM 3.2.6 은 JetPack 6.2.2 에서 동작한다 | V1(§9 선언) | V1-a · b 통과 | **지지**(측정, 정지만) |
| 마스크 없이도 사람에 버틴다 | V1-d | 정지 로버 1.10 cm · 끊김 0 | 지지(정지 상태 한정). 움직이는 로버 + 사람(T2 · T3)은 미시험 |
| 프로젝터 상시 끔(O2)으로 충분하다 | M1 | 아래 절반 유효 비율 켬의 45 % | 기각(측정, 선언 기준) — **이후 10-21 에 사용자 결정으로 채택**(§7) |
| 번갈이(O1)는 이 카메라 · 드라이버로 실현된다 | M2 | 60 Hz · 메타 교대 · CPU 9.8 % | 지지(측정, 분리 노드는 아직 없음) |
| 사람이 있으면 cuVSLAM CPU 가 오르는 이유 | — | 후보 ① 이상치 제거 · 재검출 부담 ② 호스트 → 컨테이너 영상 누락이 CPU 경합으로 커짐 | 미확인 |

## 4. 조치와 효과
- 이 시기엔 스택을 바꾸지 않았다(평가만). 얻은 것: cuVSLAM 동작 · 부하 수치, 프로젝터 문제의 측정 근거(M1 · M2), 사람 강건성 시험 설계(T1~T3), 순서 결정(§11).
- 판단의 근거 구분: 버전 · 지원 범위 · deprecated · 마스크 경로는 **웹 출처**(이 저장소에 원문 없음 — 다시 쓸 땐 재확인), 플랫폼 버전 · 성능 수치는 **측정**, rf2o 야외 · 사람 영향은 **원리 추정**.

## 5. 내 실수
**실수 1 — 측정 도구의 vo_state 정의 주석(§9.1)**
| 칸 | 내용 |
|---|---|
| 하려 한 것 | V1-a 판정 — `/visual_slam/status` 의 vo_state 분포(`job647_vslam_measure.py`) |
| 본 것 | 출력 줄 `vo_state 분포: {1: 1784} (3.2 정의: 0 미상, 1 성공, 2 실패, 3 성공+IMU 없음 …)` |
| 처음 추론 | 도구 작성 때 '3 = 성공 + IMU 없음' 값이 있다고 기억으로 적음(근거 없음) |
| 의심한 이유 | 같은 줄에 '원문 정의는 메시지 주석 확인' 이라고 스스로 남김 → `job650` 으로 메시지 파일을 읽음 |
| 판별 | `VisualSlamStatus.msg` 주석: `0 - Unknown state · 1 - Success · 2 - Failed` (3 없음) |
| 결론 | SUMMARY 는 메시지 파일 정의(0 · 1 · 2)로 적음 — 판정 영향 없음(분포가 전부 1). 도구 주석만 틀린 채 남음 |
| 다음에 알아보는 법 | 상태 코드 의미는 기억으로 쓰지 말고 메시지 정의 파일(`ros2 interface show` 또는 share/…/msg)을 먼저 읽어 도구에 넣는다 |
| 데이터 | `jobs/job647_vslam_measure.py` 마지막 print · `jobs/job650_vostate.sh` · `outputs/j646_649_vslam_v1.txt` 44~62 행 |

**기록과 원문이 다른 곳(정정 기록 없음 — 이 카드에서 확인)**
- §9.1 '프레임 간격 경고 25 회' · §9.2 '133(+108)' — `j646_649_vslam_v1.txt` 에는 기동 직후 5 줄만 있다(그 파일은 시작 로그 발췌). 25 · 133 을 센 원천(`/tmp/vslam_node.log`, Jetson)은 저장소에 없음 → **원천 소실**, 수치는 SUMMARY 기록으로만 남음.
- §9.2 표의 '사람 시험 odometry 934 개' 대 원문 `935 개`(vo_state 는 934) — SUMMARY 가 vo_state 개수를 odometry 칸에도 쓴 것으로 보임(1 개 차, 판정 영향 없음).

## 6. 남은 것 (09-29 시점)
- 움직이는 로버 + 사람(T2 · T3), 움직임 정확도(회전 시험 스캔 정합 대비) — 프로젝터 충돌 해결 뒤.
- O1 남은 일: 분리 노드(호스트 빠른 확인 a / 컨테이너 합성 b), 분리 뒤 30 Hz 깊이로 nvblox 품질 재확인, 스택 CPU 예산(≈ 320 % + cuVSLAM 23~88 %).
- 사람 있을 때 CPU 4 배 · 프레임 누락 원인 — 미확인.
- rf2o ROS 2 포트가 공분산을 채우는지 — 미확인(§6, 소스로 확인 예정).
- Isaac 5.0 의 기본 ROS 배포판(Jazzy/Lyrical) — 확정 못 함(§8.1).

## 7. 이후 (09-30 ~) — 포인터
- **10-02 ~ 10-07 rf2o**(§11 의 ⑤ 를 앞당긴 셈): 라이다 yaw π 로 병진 부호 반대 보정, 정지 사람 통과, 회전 중 큰 가림 실패(G3 기각), G4 휠 잔차 — 메모리 '회전 미끄러짐 · rf2o', [휠 오도 스케일 · 회전 슬립](wheel-odom-scale-slip.md) 이후 칸.
- **10-19 §15**: 사용자 — 09-29 §11 '7.2 뒤로' 는 일정 결정이지 기술 제약이 아니었다, "분리 노드부터" → 호스트 C++ `emitter_splitter_node`(지금 저장소 `ros2_ws/src/rover_bringup/src/emitter_splitter.cpp`, `camera.launch.py emitter_flash:=` 로만 쓰임). 10-19 §23.1: 번갈이 조건에선 cuVSLAM 이 이동을 못 따라감(끔 · IMU 끔 위치 오차 끝 204 cm). §24.1: 번갈이 중 노출 · 게인을 못 바꿈 — [10-19 SUMMARY](../debug_log/2026-10-19/SUMMARY.md).
- **10-20 §1**: 프로젝터 **상시 끔**이면 따라간다(f2z1, IMU 융합 끔 위치 끝 1.5 cm · yaw 0.8°) — [10-20 SUMMARY](../debug_log/2026-10-20/SUMMARY.md). §6~§9 그림자 융합 · 카메라 ↔ cuVSLAM 공유메모리(N-SHM — §8 '한 프로세스 합성' 의 다른 해법).
- **10-21 §20 사용자 결정: 프로젝터 상시 끔 유지**(= 09-29 에 기각한 O2). 09-29 M1 이 예고한 대가(바닥 깊이 구멍)는 맨바닥 **유령 칸**으로 나타남 → 10-22 깊이 프리셋 3 · nvblox 통합 거리 2.0 m — [10-21 SUMMARY](../debug_log/2026-10-21/SUMMARY.md) · [10-22 SUMMARY](../debug_log/2026-10-22/SUMMARY.md) · 메모리 '유령 칸 · 프로젝터 끔 유지'.
- **10-23 §16 사용자 결정: 주 EKF 병진 속도 = cuVSLAM**(`ekf.launch vslam:=on`, `Docs/tools/prep_patrol.sh` 기본 `ODOM=vslam` = `emitter_off:=true vslam:=on dds_shm:=true` — 지금 코드 확인). 근거 f2von1 · f2von2: W3 회전 창 13.2~16.8 cm(rf2o 21.5~30.7) · CPU 70 % — [10-23 SUMMARY](../debug_log/2026-10-23/SUMMARY.md).
- 사람 마스크 · JetPack 7.2 이전은 지금도 미실행(CLAUDE.md §6 상태 줄의 마지막 Phase).

## 8. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job644` | 플랫폼 · 패키지 버전 · 영상 경로 CPU | → `j644_platform.txt` |
| `job645` | cuVSLAM 노드 · 예제 launch · splitter 유무 · 드라이버 버전 | 출력 원문 없음(실시간 로그) |
| `job646` · `vslam_standalone.launch.py` · `job648` | cuVSLAM 단독 기동 · 정리 | → `j646_649_vslam_v1.txt` 앞부분 |
| `job647` · `job649` | V1 · V1-d 측정 + 부하 | → 같은 파일 |
| `job650` | vo_state 정의 | → 같은 파일 44~62 행 |
| `job651` · `job652` | 번갈이 준비물 · splitter apt · 예제 설정 | → `j651_654_emitter.txt` 1~118 행 |
| `job653` · `job654` | M1 켬/끔 깊이 · M2 번갈이 60 fps | → 같은 파일 120~ 행 |
| V1static · V1d_person | 정지 60 s · 사람 35 s | 로버 정지, bag 없음 |

## 9. 도구 해설
공통: 전부 Jetson 에서 `run_jn.sh`(실시간 로그 `/tmp/live/current.log`, 메모리 '실행 투명성')로 돌렸다 — 출력 파일 머리의 `===== … 시작 | jobNNN … 목적: …` 줄이 그 흔적. 컨테이너 이름 `isaac_ros_dev-aarch64-container`, 컨테이너 안 ROS 는 `/tmp/fastdds_udp_only.xml` 로 UDP 전용.
도구 계보: 09-29 단독 확인(`job646` · `vslam_standalone.launch.py`) → 10-19 분리 노드 · 오프라인 비교(`run_vslam_offline.sh` · `anal_vslam_cmp.py`) → 10-20 그림자 · `vslam_twist.py` · `cuvslam_up.sh`(지금 `rover_bringup/scripts/`) → 10-23 `ekf.launch vslam:=on`. 프로젝터 측정: `job653`(M1) → 10-19 S1 · 10-21 mx1 · mx2 · pr1(프리셋).

### job644_platform.sh — 플랫폼 확인 (Jetson, bash)
- 부른 형태: 인자 없음.
- 하는 일: 호스트 `/etc/nv_tegra_release` 첫 줄 · `dpkg-query`(nvidia-jetpack · l4t-core · cuda · tensorrt) · `/usr/local/cuda-*` → 컨테이너 이미지 이름 · `isaac-ros-(nvblox|visual-slam|cuvslam|nitros|common|realsense|managed-nitros)` 패키지 버전 · CUDA → `ps --sort=-pcpu` 에서 영상 · 주요 노드 줄(누적 평균 %CPU).
- 출력: `j644_platform.txt`(맨 앞 줄은 WSL 경고 깨진 글자 — 무시). `nvidia-jetpack` 패키지 줄은 없음 → 'JetPack 6.2.2' 는 L4T 36.5 ↔ NVIDIA 공지 대응(웹)으로 적은 것.
- 결함: `ps` 의 %CPU 는 **프로세스 수명 누적 평균**이라 순간 부하가 아님(SUMMARY 에 '누적 평균' 으로 표시함).
- 지금 다시: 버전 확인용으로 그대로 가능.

### job646_vslam_up.sh · vslam_standalone.launch.py · job648_vslam_down.sh — cuVSLAM 단독 기동 (Jetson 호스트 + 컨테이너)
- 하는 일(`job646`): 주행 스택 프로세스 패턴 26 개를 TERM → 5 s → KILL(base 는 유지, `systemctl --user is-active rover-base` 출력) → 호스트 `realsense2_camera_node` 를 IR1 · IR2 640×360×30, 깊이 · 컬러 끔, `emitter_enabled 0`, gyro · accel 200, `unite_imu_method 2`, `initial_reset` 로 기동 → 12 s 뒤 열린 프로파일 · 토픽 hz · 프로젝터 값 확인 → 컨테이너에서 launch.
- `vslam_standalone.launch.py`: Isaac `isaac_ros_visual_slam_realsense.launch.py` 의 노드 파라미터를 그대로(IMU 융합 켬, 노이즈 0.000244 · 0.000019393 · 0.001862 · 0.003, calibration 200), 바꾼 것 = `image_jitter_threshold_ms 35`(30 fps), `publish_odom_to_base_tf` · `publish_map_to_odom_tf` **false**(기존 TF 충돌 방지), `base_frame camera_link`, `imu_frame camera_gyro_optical_frame`.
- `job648`: 컨테이너 cuVSLAM INT → KILL, 카메라 INT → KILL, 남은 수 출력. 원래 스택은 다음 prep 으로 복귀.
- 출력: `j646_649_vslam_v1.txt` 1~25 행(정리 뒤 남은 0 · base active · IR 30.002/29.995 · IMU 199.690 · emitter 0 · cuVSLAM 로그 발췌).
- 계보 · 지금: 10-20 부터 `rover_bringup/scripts/cuvslam_up.sh` 가 같은 역할(주행 스택과 함께). 이 판은 재사용 안 함.

### job647_vslam_measure.py · job649_vslam_v1.sh — V1 측정 (컨테이너 안 Python + 호스트 bash)
- 부른 형태: `bash job649_vslam_v1.sh DUR LABEL`(V1static 60, V1d_person 35) → 컨테이너에서 `python3 /tmp/job647_vslam_measure.py DUR LABEL`.
- 하는 일(`job647`): DUR 초 동안 `/visual_slam/tracking/odometry`(깊이 50) 수신 시각 · x · y · z · yaw 기록, `/visual_slam/status` vo_state 개수. 끝에 주기 = (n−1)/(끝−처음), 최대 간격, 처음 → 끝 xy · z · yaw 변화, **최대 이탈** = 처음 위치에서 가장 먼 xy. 메시지 정의가 컨테이너에만 있어 컨테이너에서 돌림.
- 하는 일(`job649`): 같은 시간 `tegrastats 1 s` · `top` 5 s 마다 → component_container · realsense2_camera · rplidar · python3 · ekf_node 의 평균 %CPU, 전체 CPU(idle 기준), GR3D 평균.
- 출력: `j646_649_vslam_v1.txt` 27~40 · 67~80 행.
- 결함: vo_state 정의 주석 오류(§5 실수 1). top 의 python3 14.1 % 는 측정 스크립트 자신(SUMMARY 에 '측정 부하' 로 표시). 정지 판정의 기준 '처음 위치' 는 첫 메시지 하나.
- 지금 다시: 정지 드리프트 확인용으로 가능(토픽 이름은 지금 `/visual_slam/tracking/odometry` 그대로인지 확인 필요).

### job651_splitter_chk.sh · job652_splitter_apt.sh — 번갈이 준비물 (Jetson)
- 하는 일: 컨테이너 `ros2 pkg list` 에서 splitter · realsense, `nvblox_examples_bringup` 의 sensors 설정 · launch 목록과 `realsense.yaml` · `realsense.launch.py` 의 splitter 줄, 호스트 드라이버 파라미터 중 emitter · laser · infra_profile · hdr(`job651`); `ros2 pkg prefix realsense_splitter` · `apt-cache policy ros-humble-realsense-splitter`, `realsense_emitter_flashing.yaml` 원문과 `emitter_on.yaml` 과의 diff(`job652`).
- 출력: `j651_654_emitter.txt` 1~118 행. 결론 '컨테이너 · apt 에 없음' 의 근거.

### job653_depth_emit.py · job654_emit_m12.sh — M1 · M2 (Jetson 호스트)
- 부른 형태: `bash job654_emit_m12.sh` → M1 은 `python3 job653_depth_emit.py E 30` 을 E = 1 · 0 · 1 · 0 순서로.
- 하는 일(`job653`): `ros2 param set /camera/camera depth_module.emitter_enabled E` → 2 s 대기 → 깊이 `image_rect_raw`(16UC1 mm) N 프레임 + camera_info → 프레임마다 유효(>0) 화소 비율 전체 · 아래 절반, 내부 파라미터로 역투영 → TF 로 base_link 변환 → 상자 부피 x 1.10~1.30 · y −0.20~+0.03 · z 0.02~0.30 m 안 점 수 → 평균 · 최소 · 최대.
- 하는 일(`job654`): M1 카메라 = 깊이 640×480×15 만(IR · 컬러 · 점군 · IMU 끔); M2 카메라 = 깊이 · IR1 · IR2 640×480×60 + IMU 200 + `emitter_on_off true` → 열린 프로파일 · 적용값 · 토픽 hz · 메타데이터(`frame_laser_power` · `frame_emitter_mode`) · top 5 회 카메라 CPU.
- 출력: `j651_654_emitter.txt` 120~146 행.
- 결함 · 한계: 상자 부피 점 수에 바닥 가장자리 · 비산점이 섞였을 수 있음(SUMMARY 추정 — 끔이 110 % 로 나온 이유 후보). M2 CPU 9.8 % 는 top **순간값 5 회** 평균이라 §8 의 누적 평균 14.9 % 와 측정 방식이 다르다(SUMMARY 는 '점군 생성 끔 효과로 추정' 으로 비교함 — 방식 차이도 원인 후보).
- 계보: 같은 '켬/끔 유효 비율' 측정이 10-19 S1-b · 10-21 mx2 기준 3(켠 깊이 ≥ 90 %)으로 이어짐.

## 10. 용어
- **cuVSLAM**: NVIDIA 의 GPU 스테레오(+IMU) 시각 오도메트리 · SLAM. Isaac ROS 3.2 에선 `isaac_ros_visual_slam`, 5.0 부터 `isaac_ros_cuvslam`.
- **NITROS**: Isaac ROS 의 같은 프로세스 노드 간 무복사(GPU 버퍼) 전송 방식 — 5.0 부로 deprecated(웹 출처).
- **IR 프로젝터(emitter)**: D455f 가 점 무늬를 쏘아 무늬 없는 면에서도 스테레오 깊이를 얻게 하는 장치. 점이 카메라와 같이 움직여 시각 오도메트리엔 가짜 특징이 된다.
- **번갈이(emitter_on_off)**: 프로젝터를 프레임마다 켜고 끄기 — 켠 프레임은 깊이, 끈 프레임은 IR 추적에.
- **vo_state**: cuVSLAM 상태 메시지의 추적 결과 코드(0 미상 · 1 성공 · 2 실패).
- **range flow(rf2o)**: 연속 2D 스캔의 거리 변화율로 평면 운동을 직접 푸는 조밀 정합(대응점 탐색 없음).
