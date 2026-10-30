# 라이다 장착 방향(yaw) 확정 — π, 그리고 Foxglove 표시 혼선

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 | 관련 문제 |
|---|---|---|---|---|
| **해결**(yaw = π, 앞뒤 방향) · 카메라 y 부호(±0.0475)는 **보류**(이 시기 끝까지 미판정) · 미세 yaw(−2.68°)는 이후 시기 | 08-27 ~ 09-01 (이후 09-18 미세 보정) | [08-27 '미해결·다음'](../debug_log/2026-08-27/SUMMARY.md) "LiDAR yaw 정렬 … 현재 rpy 0, 케이블 방향 미검증" | `ros2_ws/src/rover_description/urdf/rover.urdf` · 기록 사본 `Docs/02_hardware/rover.urdf`(당시 `Docs/rover.urdf`) — `lidar_joint` rpy (0,0,0) → **(0,0,π)** | [회전 중 스캔 끌림](scan-drag-deskew.md) · [Foxglove 4초 스냅](foxglove-snap-cpu.md) · [센서 데크 yaw −2.68°](sensor-deck-yaw.md)(09-18) |

**한 줄**: 라이다(RPLidar S2L) 하드웨어 0° 가 로버의 어느 쪽을 보는지 정하는 데 08-28 하루 동안 도구 15 개를 썼고 결론이 π → 0 → π 로 오락가락했다. 수치(base_link 프레임 각도)는 처음부터 π 를 가리켰고, 혼선의 정체는 **Foxglove 의 fixed frame 이 `map` 인데 SLAM 이 안 떠 있어 `map` 프레임이 없었던 것**(사용자 발견)이었다. 확정 방법은 '거리로 구분되는 두 벽(좌 325 mm · 정면 800 mm)을 두고 원시 각도 차와 base_link 각도를 수치로 보는 것'(job6n · job6o). 09-01 에 사용자의 '180° 뒤집힘' 관찰도 손-정면 시험(job14e)으로 기각해 π 를 재확인했다. 카메라 y 부호는 이 시기에 판정하지 못했다.

## 1. 증상
- 08-27 URDF 의 `lidar_joint` rpy = 0(케이블 방향 미검증). 이전 프로젝트 기록(C8)은 π 였다(08-27 '판단·결정' 1). 어느 쪽이 맞는지 측정이 필요했다.
- 08-28 오후: yaw 를 π 로 바꾼 뒤에도 Foxglove 화면의 스캔이 로버 기준으로 뒤집혀/엉뚱하게 보임 → 'yaw 가 틀렸다' 로 읽고 0 으로 되돌렸다가(job6j) 다시 π 로(job6m). [08-28 'LiDAR yaw 최종 확정 (오후, 여러 차례 오락가락 후)'](../debug_log/2026-08-28/SUMMARY.md)
- 09-01: 사용자 "라이다가 180° 뒤집혀 보인다" 관찰. [08-31 SUMMARY '(2026-09-01 연속 세션)' → '결과 (수치)'](../debug_log/2026-08-31/SUMMARY.md)

## 2. 흐름 (시간순)
08-28 의 순서는 SUMMARY 에 job 단위로 다 적혀 있지 않다. 아래 순서는 출력 파일의 TF 값(yaw 0/180)과 배치 거리값이 이어지는 모양으로 맞춘 것(**추정**, job6h ~ 6j 사이 순서는 특히 불확실).

| 날짜 · 곳 | 한 일 | 본 것(수치) | 그때 결론(틀렸으면 표시) | 데이터 |
|---|---|---|---|---|
| 08-27 '한 일' | 장착 후 쓸 `job4y`(손 0.3 m 5 초 → 최근접 섹터) 준비 | — | 손이 0° 에 안 나오면 yaw 보정 | [job4y.sh](../debug_log/2026-08-27/jobs/job4y.sh) |
| 08-28 아침 | `job6a` 기준선(손 없음) · `job4y` 실행, 당시 TF yaw 0 | 6a: 8 섹터 중 최근접 −90°(0.61 m). 4y: **6a 와 거의 같은 값**(−90° 0.61 m) | 4y 는 손을 못 잡음(**추정**: 손이 없었거나 스캔면 밖 — 기록 없음) | [job6a_prescan.txt](../debug_log/2026-08-28/outputs/job6a_prescan.txt) · [job4y_lidar_yaw.txt](../debug_log/2026-08-28/outputs/job4y_lidar_yaw.txt) |
| 08-28 | `job6c`(최근접 빔 + 10° 근거리 분포) | 출력 원문 없음 | — | [job6c.sh](../debug_log/2026-08-28/jobs/job6c.sh) |
| 08-28 | `job6d` 종이 흔들기(원시 각도, 15 s) | 점수 최대 bin 중심 **+165°**(±180° 양쪽 bin 의 std 0.085 · 0.089 가 가장 큼) | '종이 = 원시 ±180°' → yaw **π 후보** | [job6d_paper_wave.txt](../debug_log/2026-08-28/outputs/job6d_paper_wave.txt) |
| 08-28 | `job6e` URDF yaw π 배포 | TF `base_link→lidar_link` RPY (0,0,**180**) · (0.152, 0, 0.185) | π 적용 | [job6e_lidar_yaw_apply.txt](../debug_log/2026-08-28/outputs/job6e_lidar_yaw_apply.txt) |
| 08-28 | `job6f` 종이를 base_link 프레임에서 | 중심 **−165°** → 스크립트 판정 '후방(yaw 여전히 반대)'. base 0° 부근 bin 에는 근거리 빔 자체가 없음 | 혼란. **신뢰 낮음**(아래 §5) | [job6f_verify_front.txt](../debug_log/2026-08-28/outputs/job6f_verify_front.txt) |
| 08-28 | `job6g` 종이 v3(빔 후보 필터) | 후보 **4 빔**, 가중중심 −117° → '우' | 표본 4 빔 — 판정 불가 | [job6g_verify2.txt](../debug_log/2026-08-28/outputs/job6g_verify2.txt) |
| 08-28 '판단·결정' 1 | 종이 방식 포기 → 코너(정면+좌측 벽) 정지 `job6h` | base_link 30° bin: −30°~+150° 가 0.41~0.70 m(근거리 아크), 후방 ±180° 2.3~3.3 m 트임. 스크립트 판정은 최근접 bin +105° → '좌✗' | 사람 판독: **정면벽 0° · 좌측벽 +90° 일치 → π 확정**(오전 결론). 스크립트 '좌✗' 문구는 판정 논리 결함(§8 job6h) | [job6h_corner.txt](../debug_log/2026-08-28/outputs/job6h_corner.txt) · [lidar_yaw_CONFIRMED.txt](../debug_log/2026-08-28/outputs/lidar_yaw_CONFIRMED.txt) |
| 08-28 | `job6h` 다른 배치(파일명 wall_facing) | 최근접 +105°(0.61 m), 전방 0~30° 1.22 m | 배치 기록 없음 — **해석 미확인** | [job6h_wall_facing.txt](../debug_log/2026-08-28/outputs/job6h_wall_facing.txt) |
| 08-28 | `job6i` 같은 코너, 원시 각도(TF 무관) | 근거리 원시 −165°~−45° 와 +165°, 트임 원시 −15°·+15° | (π 면 base = 원시+180 → 근거리 +15°~+135°, 트임 ±165° = 후방) — 코너와 일치. 그때 결론 문구는 출력에 없음 | [job6i_raw_corner.txt](../debug_log/2026-08-28/outputs/job6i_raw_corner.txt) |
| 08-28 오후 | `job6j` URDF **yaw 0 으로 되돌림** | TF RPY (0,0,0). base 프레임: 벽이 −180°~0° · +135°~+180°(뒤 · 오른쪽), +0~+45° 트임 3.23 m | 되돌린 이유가 기록에 직접 없음 — **추정**: Foxglove 화면이 뒤집혀 보여서(SUMMARY "yaw π→0→π 변경 중"). **틀린 조치**(수치는 이미 π 를 지지) | [job6j_yaw0.txt](../debug_log/2026-08-28/outputs/job6j_yaw0.txt) |
| 08-28 | `job6k` 트인 공간 + 정면 단일 물체 | 최근접 원시 −77.4° @0.40 m, 그러나 근접 클러스터 −125°~+105° **449 빔** | 스크립트 '필요 yaw +90°' — **단일 물체가 아니었음**(클러터) → 버림 | [job6k_nearest.txt](../debug_log/2026-08-28/outputs/job6k_nearest.txt) |
| 08-28 | `job6l` 실제 상태 사실 확인 | RSP 1 개, TF yaw **0**(6j 반영 상태), URDF grep · /tf_static echo 는 빈 출력, foxglove pid 2911(일찍 기동) | 'stale 캐시' 의심 시작 | [job6l_state_check.txt](../debug_log/2026-08-28/outputs/job6l_state_check.txt) |
| 08-28 | `job6m` yaw π 재배포 + 전체 스택 재시작(foxglove 포함) | TF (0,0,180), scan 10.001 Hz · imu 200.131 Hz · filtered 29.996 Hz | stale TF 제거 목적 | [job6m_yaw_pi_fullrestart.txt](../debug_log/2026-08-28/outputs/job6m_yaw_pi_fullrestart.txt) |
| 08-28 오후 | 사용자 배치: 좌측 벽 ~325 mm · 정면 벽 ~800 mm. `job6n` 원시 각도 · 손잡이(handedness) 판정 | angle_increment **+0.1996°**(오른손 표기), 좌측벽 원시 **−86°**(0.40 m, 323 빔), 정면벽 원시 **−168°**(0.91 m, 219 빔), θ_L − θ_F = **+82°**(≈ +90) | 거울(반전) 아님 · 순수 회전. yaw = −θ_F 의 90° 스냅 = **π** | [job6n_handedness.txt](../debug_log/2026-08-28/outputs/job6n_handedness.txt) |
| 08-28 | `job6o` 배포 TF(π)로 base_link 각도 | 좌측벽 base **+94°**, 정면벽 base **+11°**, /tf_static 발행자 2 | π 검증 완료 | [job6o_baselink_walls.txt](../debug_log/2026-08-28/outputs/job6o_baselink_walls.txt) |
| 08-28 오후 | Foxglove 반전 설명 ① | — | 'stale tf_static: 클라이언트가 예전 yaw=0 캐시, 새로고침으로 해소'(**중간 결론, 아래로 대체**) | SUMMARY 같은 절 |
| 08-28 '★ ROOT CAUSE 확정(사용자 발견)' | Foxglove fixed frame 확인 | fixed frame = `map`, slam_toolbox 미가동 → `map` 프레임 없음. `base_link` 로 바꾸니 정면 · 좌측 벽 정상 | **혼선 원인 = fixed frame 오설정**. yaw=π 는 처음부터 맞았음 | SUMMARY 같은 절 |
| 08-28 '★ SLAM 첫 맵' | 360° 제자리 회전 매핑 | 복귀 자세 x +0.2 cm · y +0.1 cm · yaw +1° | SUMMARY: 'yaw(π) … 전 체인 정합 최종 증명'(**과한 주장 가능성** — §3 마지막 줄) | `ros2_ws/maps/rover_map.*` (job7j — [첫 SLAM 지도 카드](first-slam-map.md)) |
| 09-01 '결과 (수치)' | 사용자 '180° 뒤집힘' → `job14e_framecheck`(손을 물리 정면에) | 원시 180° 방향 최소거리 **150 → 28 cm** | yaw=π 면 원시 180° = base 0°(정면) → **π 재확정**. 뒤집힘은 사용자가 로버를 마주 보고 서서 생긴 좌우 관점 착시(사용자 오른쪽 = 로버 왼쪽) | [job14e_framecheck.sh](../debug_log/2026-08-31/jobs/job14e_framecheck.sh) · 출력 원문 없음(대화에만) |
| 08-27 · 08-28 · 08-31 '미해결·다음' | 카메라 `camera_link` y 부호(±0.0475) | 세 날 모두 '포인트클라우드 정합으로 판정 예정' | **미판정**으로 이 시기 종료 | URDF 주석 "y = +0.0475 … ⚠ 부호는 도면 337029-017 확정 대기" |
| 이후 09-18 §9 | 데크 yaw 발견 · 보정 | 정지 옆벽 +2.667/+2.686°(라이다) · +2.94°(카메라) | yaw = π 는 맞았고, 데크 −2.68° 가 그 위에 있었다 → lidar yaw π − 0.04677 | [센서 데크 yaw 카드](sensor-deck-yaw.md) |

## 3. 가설과 판별
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| yaw = 0(하드웨어 0° = 로버 전방, 08-27 URDF 값) | 코너 · 두 벽 배치에서 base 각도 | yaw 0 이면 벽이 뒤 · 오른쪽에 나옴(job6j), 정면벽 원시 −168°(job6n) | **기각** |
| yaw = π(하드웨어 0° = 로버 후방, 이전 프로젝트 C8) | job6h · 6i · 6n · 6o · 14e | 정면벽 base +11° · 좌측벽 +94°, 손-정면 원시 180° 150→28 cm | **지지(확정)** |
| yaw = ±90°(job6k 스크립트 제안) | 같은 날 6n · 6o | 6k 는 449 빔 클러스터(단일 물체 아님) | **기각**(측정 무효) |
| 스캔이 거울상(왼손계) — inverted 필요 | 두 벽의 원시 각도 차 부호 | θ_L − θ_F = +82°(+90 이어야 오른손), angle_increment > 0 | **기각** — 드라이버가 오른손 메시지로 내보냄 |
| Foxglove 반전 = stale tf_static 캐시 | 6l(상태 확인) → 6m(전체 재시작) | 재시작 뒤에도 사용자 화면 문제는 fixed frame 을 바꾸고서야 풀림 | **대체됨**(원인 아님 또는 부분 원인 — 미확인). /tf_static 발행자 2(job6o)는 카메라 드라이버의 내부 정적 TF 와 RSP 일 가능성이 높아 '중복 = stale' 증거가 아님(**추정**, 발행자 이름은 안 봄) |
| Foxglove fixed frame = `map`(SLAM 없음) | 사용자가 `base_link` 로 바꿈 | 정상 표시 | **확인**(사용자) |
| 09-01 '라이다 프레임 180° 오류'(사용자) | job14e 손-정면 | 원시 180° 만 150→28 cm | **기각** — 관점 착시 |
| '360° SLAM 복귀 0.2 cm 가 yaw π 를 최종 증명'(08-28 SUMMARY) | 논리 점검(이 카드 작성 시) | 라이다 yaw 가 상수로 틀려도 **제자리 회전**에서는 모든 스캔이 같은 각만큼 돌아갈 뿐이라 지도는 자기 일관적이다. yaw 오류는 병진 때(로버가 스캔과 반대로 움직이는 것처럼) 드러난다 | **증명력 약함**(**추정**, 내 판단). 병진 주행 지도(08-31 저녁 `rover_map_drive`, 15.9×11 m)가 더 나은 간접 증거 |

## 4. 조치와 효과
- `lidar_joint` rpy (0,0,π), `inverted: False` 유지(`lidar.launch.py`). 08-28 에 확정, 09-01 job14e 로 재확인.
- 확정 뒤 이 값에 기대는 코드: 회전 시험 스크립트의 여유 계산 상수 `LX,LYAW = 0.152, π`(08-31 job8e · 8f, 09-01 job16h · 16k · 17c — [스캔 끌림 카드](scan-drag-deskew.md) · [Foxglove 카드](foxglove-snap-cpu.md)). 이후 `stuck_monitor.py LIDAR_YAW` 도 같은 값을 쥔다(CLAUDE.md, 09-18 동기화).
- 한계: 08-28 확정은 **앞뒤 방향(90° 격자 스냅)만**. job6o 정면벽 +11° 는 '정면' 으로 분류하고 넘어갔다 — 대역(0.65~0.95 m)에 다른 물체가 섞이면 중심이 끌리므로 +11° 가 장착 오차인지 측정법 오차인지 이 시기엔 가르지 않았다. 09-18 에 데크가 −2.68° 틀어진 것이 따로 발견된다(URDF 주석: "08-28 확정은 방향(π, 앞뒤)만이었고 미세 yaw 는 재지 않았다(당시 기록: 정면벽 +11° 로 보였음)").
- 기록 불일치: 현재 URDF `lidar_joint` 주석은 아직 "Foxglove 반전 관찰은 stale tf_static 캐시" 라고 적혀 있다. SUMMARY 의 최종 원인(fixed frame = map)으로 고쳐지지 않았다(파일 수정은 이 카드 범위 밖 — 남은 것 참조).

## 5. 내 실수
### 5.1 yaw 오락가락(π → 0 → π) — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 라이다 0° 가 로버 어느 쪽인지 정하기. 처음엔 '움직이는 물체(종이)의 분산이 큰 방향 = 물체 방향' 으로(job6d → 6f → 6g), 다음엔 '가장 가까운 것 = 정면' 으로(job6h · 6k) |
| 본 것 | 6d: +165°(원시) · 6f: −165°(base, π 적용 뒤라면 0° 근처여야 함) · 6g: 4 빔 −117° · 6h: 최근접 +105° '좌✗' · 6k: −77° '+90° 필요'. 같은 질문에 다섯 가지 답 |
| 처음 추론 | 각 출력의 마지막 판정 줄을 그대로 받아 yaw 를 바꿈(π 적용 → 다시 의심 → 0 으로 되돌림, job6j) |
| 의심한 이유 | 출력끼리 서로 모순. 그리고 판정 줄 바로 위의 bin 표(근거리 아크 −30°~+150°)는 스크립트 판정('좌✗')과 다른 이야기를 했다 |
| 판별 | 거리로 갈리는 두 벽(325 mm · 800 mm) 배치 → 원시 각도 차(손잡이)와 base 각도를 각각 수치로(job6n · 6o) |
| 결론 | yaw = π. 앞선 도구들의 판정 줄이 틀린 이유: ① 종이 점수 = (근거리 빔 수 × std) 라 정지한 벽 수천~2 만 빔이 점수를 지배(6d 의 near_beams 7016 · 22650 · 18925), S2L 스캔면(지면 +18.5 cm)이 좁아 종이가 자주 빗나감 ② '최근접 = 정면' 은 코너에서 더 가까운 옆벽(0.41 m)이 이김 ③ '단일 물체' 가정이 클러터(449 빔)로 깨짐 |
| 다음에 알아보는 법 | 판정 줄보다 **bin 표 전체 모양**을 먼저 본다. 방향 판정은 '거리로 구분되는 두 기준물 + 원시 각도 차 부호 + base_link 각도' 3 가지가 맞아야 확정. 움직이는 물체 방식은 기준선(물체 없음) 차분 없이는 쓰지 않는다 |
| 데이터 | `2026-08-28/outputs/job6d_paper_wave.txt` · `job6f_verify_front.txt` · `job6g_verify2.txt` · `job6h_corner.txt` · `job6k_nearest.txt` · `job6n_handedness.txt` · `job6o_baselink_walls.txt` |

### 5.2 Foxglove 반전 = 'stale tf_static' 로 설명 — 칸 형식
| 칸 | 내용 |
|---|---|
| 하려 한 것 | 수치(π)와 Foxglove 화면(뒤집힘)의 모순 설명 |
| 본 것 | job6l: TF yaw 0(6j 되돌림 상태) · foxglove 는 일찍 기동된 pid · job6o: /tf_static 발행자 2 |
| 처음 추론 | yaw 를 바꾸는 동안 클라이언트가 예전 yaw=0 정적 TF 를 쥐고 있었다 → 정면벽 원시 −168° 가 base −168°(뒤)로 그려진 것과 일치. 브라우저 새로고침 · 전체 재시작(job6m)으로 해소 |
| 의심한 이유 | 사용자가 fixed frame 이 `map` 인 것을 발견 — `map` 은 SLAM 이 띄우는데 그때 SLAM 이 없었다 |
| 판별 | fixed frame `base_link` 로 바꿈(사용자) → 정상 |
| 결론 | 원인 = fixed frame 에 없는 프레임. stale 캐시는 실제로 있었는지조차 확인 안 됨(**미확인**). 발행자 2 는 정상 구성일 가능성(**추정**) |
| 다음에 알아보는 법 | 시각화가 수치와 다르면 먼저 **뷰어의 fixed frame 이 지금 TF 트리에 있는지**(`tf2_echo <fixed> base_link`) 확인. 화면만으로 센서 장착을 판정하지 않는다 |
| 데이터 | `2026-08-28/outputs/job6l_state_check.txt` · `job6m_yaw_pi_fullrestart.txt` · `job6o_baselink_walls.txt`, 사용자 관찰은 SUMMARY 문장만(화면 캡처 없음) |

## 6. 남은 것
- **카메라 y 부호(±0.0475)**: 08-27 · 08-28 · 08-31 세 번 '다음' 에 올랐으나 이 시기 안에 판정 없음. URDF 는 +0.0475(09-18 데크 회전 반영 뒤 0.04371). 도면(337029-017) 또는 스캔 vs 깊이 점군 정합으로 판정할 것 — 이후(09-04 ~): 다음 시기에서 채움.
- **미세 yaw → [센서 데크 yaw −2.68°](sensor-deck-yaw.md) 카드로 이어짐**: 08-28 의 yaw = π(앞뒤)는 맞았지만 그 위에 데크(라이다+카메라) 전체가 −2.68° 틀어져 있었다. 09-18 에 주행 bag 게걸음 각 +2.57°(수정판) · 옆면을 벽에 붙인 정지 측정 +2.667/+2.686° 로 찾아 `lidar_joint` yaw π → **3.09482**(π − 0.04677), 보정 뒤 정지 재측정 −0.031°(`2026-09-18/SUMMARY.md` §9 ~ §11). 이 카드 §4 의 '정면벽 +11°' 는 그 측정법(대역 원형 평균)으로는 2.7° 를 가를 수 없었다 — 재측정 도구는 `2026-09-18/jobs/job432c_wallyaw_tf.py`(절차는 데크 카드 §7).
- URDF `lidar_joint` 주석의 원인 문구(stale tf_static)를 fixed frame 원인으로 고칠지 — 사용자 결정 대기(이 카드는 파일을 고치지 않음).
- `job6h_wall_facing.txt` · `job4y_lidar_yaw.txt` 가 어떤 배치에서 나온 것인지 기록 없음.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| job4y | 손 0.3 m → 45° 섹터 최근접 | `2026-08-27/jobs/` · 출력 `2026-08-28/outputs/job4y_lidar_yaw.txt` |
| job6a · 6b | 기준선 스냅샷 · 재부팅 뒤 스택 재시작 | `2026-08-28/jobs/` · 출력은 **`2026-08-27/outputs/`** 에 잘못 놓임(`job6a_prescan.txt` = ssh 실패본, `job6b_restart.txt`) + `2026-08-28/outputs/job6a_prescan.txt`(정상본) |
| job6c · 6d · 6f · 6g | 최근접 빔 / 종이 흔들기 3 판 | `2026-08-28/jobs/` |
| job6e · 6j · 6m | URDF 배포(π · 0 · π + 전체 재시작) | 같은 곳 |
| job6h · 6i · 6k | 코너(base) · 코너(원시) · 단일 물체 | 같은 곳 |
| job6l | 실행 중 상태 사실 확인 | 같은 곳 |
| job6n · 6o | **확정**: 두 벽 손잡이 · base 각도 | 같은 곳 |
| job14e_framecheck | 09-01 손-정면 재확인 | `2026-08-31/jobs/` |
| `lidar_yaw_CONFIRMED.txt` | 오전(코너) 확정 메모 | `2026-08-28/outputs/` |

## 8. 도구 해설
공통: 모든 job 은 **Jetson** 에서 돈다. PC 에서 스크립트를 Jetson `/tmp` 로 보내 ssh 로 실행했고(비밀번호는 `<PW>`), 출력 원문을 PC 로 받아 `outputs/` 에 저장했다(일부 출력 첫 줄의 깨진 `wsl:` 경고 = PC 의 WSL 을 거친 흔적). 모두 `source /opt/ros/humble/setup.bash; source ~/ros2_ws/install/setup.bash` 뒤 bash 안에 python heredoc 을 넣은 1 회용 형태이고 인자는 없다. 스캔 구독은 전부 `qos_profile_sensor_data`(best effort). 공통 결함: `numpy` 의 'All-NaN slice' 경고가 출력에 섞인다(무해 — 빔이 하나도 없는 bin).

**도구 계보**
- 섹터 최근접: job4y(45° 섹터, lidar 프레임) → job6a(같은 표, 기준선) → job6c(개별 최근접 빔 + 10° 근거리 분포) → job6h(base_link 30° bin) → job6i(원시 30° bin, TF 무관) → job6k(단일 물체 최근접 + 클러스터 폭)
- 종이 흔들기: job6d(원시, 분산 × 빔 수) → job6f(base_link 변환) → job6g(빔 후보 필터 + 원형 가중 평균) — 셋 다 폐기
- 확정: job6n(거리 대역 두 벽 · 원시 각도 차) → job6o(같은 대역 · base_link 각도) → job14e(09-01, `/scan_raw` 한 장 · 원시 4 방위 최소거리)
- 배포: job6e(π) → job6j(0) → job6m(π + 전체 재시작). 상태 확인: job6l

### job4y.sh (08-27 작성, 08-28 실행)
- 왜: 08-27 '미해결' — "로버 정면 0.3 m 손 5 초 → job4y → lidar_joint rpy 확정".
- 하는 일: `/scan` 5 초 수집 → 빔별 중앙값(시간축 `nanmedian`) → 각도 = `angle_min + angle_increment·i`(도) → 45° 섹터 8 개(−180 섹터는 ±157.5° 바깥을 묶음)의 중앙거리 → 최솟값 섹터 = 'NEAREST' → 90° 스냅해 "lidar_yaw 를 (현재값 − snap) 으로 보정" 문구.
- 주의: 각도는 **lidar_link 프레임**(TF 적용 안 함). '현재 URDF yaw 가 적용된 프레임' 이라는 출력 문구는 틀렸다 — 코드는 TF 를 읽지 않는다.
- 출력: 섹터표 + `NEAREST sector: -90 deg (0.61 m)` → [job4y_lidar_yaw.txt](../debug_log/2026-08-28/outputs/job4y_lidar_yaw.txt). 값이 job6a 기준선과 거의 같아 손을 못 잡은 것으로 보인다(**추정**).
- 쓰인 곳: 결론에 안 쓰임. 계보 시작점.
- 결함: 섹터 45° 는 거칠고, 중앙값이라 섹터 일부를 가린 손은 사라진다. 다시 쓸 수 없음(대체: job6n 방식).

### job6a.sh — 기준선
- 왜: yaw 정렬 전 '손 없음' 기준 거리표 + 스택 상태.
- 하는 일: `ros2 node list` · 토픽 4 개(`/scan` · `/wheel_odom` · `/odometry/filtered` · `/camera/camera/imu`) `ros2 topic hz` 5 s · `tf2_echo base_link lidar_link` 의 RPY · job4y 와 같은 45° 섹터 중앙거리(4 s).
- 출력: [2026-08-28/outputs/job6a_prescan.txt](../debug_log/2026-08-28/outputs/job6a_prescan.txt) — scan 9.963 · wheel_odom 49.997 · filtered 29.999 · imu 199.642 Hz, TF RPY (0,0,0), 최근접 −90° 0.61 m. (같은 이름의 `2026-08-27/outputs/job6a_prescan.txt` 는 `No route to host` — 재부팅 중 실패본.)
- 계보: job4y 의 표를 그대로. 다시 쓸 일 없음.

### job6b.sh — 재부팅 뒤 스택 재시작(정렬 도구 아님, 맥락용)
- 하는 일: uptime · `/dev/rover` · `/dev/rplidar` · lsusb · HID 모듈 수(`lsmod | grep hid_sensor`) · iio 장치 → 남은 노드 pkill · agent 컨테이너 제거 → `base.launch.py`(10 s) → `sensors.launch.py`(35 s, 자이로 바이어스 로그) → 노드 · 토픽 hz · `/battery` 1 회.
- 출력: [2026-08-27/outputs/job6b_restart.txt](../debug_log/2026-08-27/outputs/job6b_restart.txt)(날짜 폴더 잘못 놓임) — 부팅 08:51:45, HID 6 개 · iio:device0/1 생존(재부팅 뒤 자동 로드 근거), wheel_odom 50.016 · scan 10.012 · imu 203.281 · filtered 30.001 Hz, 배터리 12.09 V.

### job6c.sh — 최근접 빔 v2
- 왜: 45° 섹터가 거칠어서 '개별 최근접 빔 각도 + 0.8 m 이내 10° 분포'.
- 하는 일: 5 s 중앙값 → `range_min`(또는 0.05) 초과 유효 빔 중 최소 → `NEAREST BEAM: θ @ r`; 0.8 m 미만 빔을 10° bin 개수 · 최소거리로.
- 출력 원문 없음(대화에만). 결과가 쓰였다는 기록 없음. 다시 쓸 수 없음.

### job6d.sh — 종이 흔들기 v1(원시 각도)
- 왜: 물체 하나를 정면에 정확히 두기 어려워 '흔드는 물체 = 시간 변동이 큰 빔'.
- 하는 일: 15 s 동안 모든 스캔 행렬 M(스캔 × 빔) → 빔별 시간축 표준편차 `beam_std` · 0.7 m 미만 횟수 `near` → 30° bin 마다 `score = (bin 근거리 빔 합) × (bin 평균 std)`, `cnt > 5` 중 최대 → 중심 각, 90° 스냅으로 보정 후보.
- 출력: 151 스캔, 최대 점수 bin +165°, '보정 후보 −3.1416 rad' → [job6d_paper_wave.txt](../debug_log/2026-08-28/outputs/job6d_paper_wave.txt).
- 쓰인 곳: π 의 첫 근거(lidar_yaw_CONFIRMED 의 '근거 교차'). 다만 std 자체(0.085 · 0.089)는 ±180° bin 이 가장 컸으므로 이 경우엔 맞은 답을 냈을 가능성이 있다(**추정**).
- 결함: 점수에 빔 수를 곱해 정지한 근거리 벽(−120°~−60° bin 의 22650 · 18925 빔)이 점수를 키운다. 기준선 차분 없음. 폐기.

### job6e.sh — yaw π 배포
- 하는 일: PC 에서 올린 `/tmp/rover_src/rover_description/urdf/rover.urdf` 를 워크스페이스로 복사 → `colcon build --symlink-install --packages-select rover_description` → `robot_state_publisher` 만 재시작(`description.launch.py`) → `tf2_echo base_link lidar_link`.
- 출력: Translation (0.152, 0, 0.185), RPY (0, −0, 180) → [job6e_lidar_yaw_apply.txt](../debug_log/2026-08-28/outputs/job6e_lidar_yaw_apply.txt).
- 결함: RSP 만 재시작하므로 이미 접속해 있던 Foxglove 같은 클라이언트의 /tf_static 상태는 건드리지 않는다(job6l · 6m 로 이어진 의심의 출발점).

### job6f.sh — 종이 v2(base_link 프레임)
- 하는 일: TF 버퍼로 `base_link ← lidar_link` 회전을 받아 yaw = atan2(2(wz+xy), 1−2(y²+z²)) → 빔 각 + yaw 를 [−180,180) 로 → 30° bin 마다 std · 근거리 수, `cnt > 50` 중 `cnt × std` 최대 → '전방/후방/좌/우' 판정.
- 출력: yaw 180°, 중심 −165° → '후방(yaw 여전히 반대)' → [job6f_verify_front.txt](../debug_log/2026-08-28/outputs/job6f_verify_front.txt). base 0° 부근 bin 은 근거리 빔이 0 이라 표에 아예 없다 — 종이가 0.7 m 안 정면에 없었거나 스캔면을 빗나간 것(**추정**).
- 결함: 6d 와 같은 점수식. 폐기.

### job6g.sh — 종이 v3(후보 필터)
- 하는 일: 6f 와 같은 base 변환 뒤, 후보 빔 = `근거리(0.9 m 미만) 횟수 > 스캔 수 × 0.15` 그리고 `std > 0.03` → std 가중 원형 평균 → 판정(|c|<40 전방, >140 후방).
- 출력: 후보 4 빔, −117° '우' → [job6g_verify2.txt](../debug_log/2026-08-28/outputs/job6g_verify2.txt).
- 결함: 주석은 '정지 기준선 3 s → 흔들기' 라고 하지만 **코드에 기준선 단계가 없다**(TF 대기 2 s 뿐). 표본 4 빔으로는 판정 불가. 폐기.

### job6h.sh — 코너 정지(base_link)
- 왜: 08-28 '판단·결정' 1 — 벽은 전 높이를 덮어 스캔면에 확실히 걸리고 정답(정면 · 좌측)이 분명.
- 하는 일: 4 s 중앙값 → base 각 변환(6f 와 같음) → 30° bin 중앙거리(빔 3 개 이상) → 최솟값 bin 을 '벽 = 정면' 으로 판정.
- 출력: [job6h_corner.txt](../debug_log/2026-08-28/outputs/job6h_corner.txt) — 근거리 아크 −30°~+150°(0.41~0.70 m), 후방 3.26 · 2.32 m. 판정 줄 '+105° 좌✗'. 다른 배치 [job6h_wall_facing.txt](../debug_log/2026-08-28/outputs/job6h_wall_facing.txt) — 배치 미기록.
- 쓰인 곳: 오전 확정 메모 [lidar_yaw_CONFIRMED.txt](../debug_log/2026-08-28/outputs/lidar_yaw_CONFIRMED.txt)("전방벽 base 0°, 좌측벽 +90°").
- 결함: '최근접 bin = 정면' 판정 논리는 코너에서 틀린다(더 가까운 옆벽이 이김). 사람은 표 모양으로 맞게 읽었다. 다시 쓸 때는 판정 줄을 지우고 표만.

### job6i.sh — 코너 원시 각도
- 왜: TF 를 빼고 하드웨어 각도만으로 '회전인지 반전인지' 보려고.
- 하는 일: 4 s 중앙값 → 원시 각 30° bin 중앙거리, < 1.0 m '근거리(벽)', > 2.0 m '트임' 꼬리표 → 두 목록 출력. 판정은 사람 몫(출력에 정답 φ 안내 줄).
- 출력: 근거리 [−165, −135, −105, −75, −45, 165], 트임 [−15, 15] → [job6i_raw_corner.txt](../debug_log/2026-08-28/outputs/job6i_raw_corner.txt). π 면 base = 원시 + 180 이라 근거리 = +15°~+135° 와 −15°, 트임 = ±165°(후방) — 코너와 맞음.
- 계보: 이 '원시 + 사람 대조' 생각이 job6n 의 손잡이 판정으로 발전.

### job6j.sh — yaw 0 되돌림 + 참고 표
- 하는 일: 6e 와 같은 배포 절차(URDF 는 PC 에서 yaw 0 으로 고쳐 올린 판) → TF 확인(0 기대) → base 45° bin 중앙거리 + '벽/트임' 꼬리표 → `VERIFY_IN_FOXGLOVE`.
- 출력: RPY (0,0,0); 벽이 −180~0° · +135~180°, 트임 0~45° 3.23 m → [job6j_yaw0.txt](../debug_log/2026-08-28/outputs/job6j_yaw0.txt). 스크립트 안내문 자체가 "코너면 근거리가 0°~+90° 아크여야 정상" 이므로 **이 출력은 yaw 0 이 틀렸다는 증거**였다.
- 쓰인 곳: 되돌림은 job6m 에서 다시 π 로 덮임.

### job6k.sh — 단일 물체 최근접
- 하는 일: 4 s 중앙값 → 유효 빔(> max(range_min, 0.05)) 최근접 각 θ, 그 거리 + 0.15 m 안 빔들의 각 범위('클러스터') · 가까운 8 개 → 90° 스냅 → `필요한 lidar_yaw = −snap`.
- 출력: θ −77.4° @ 0.40 m, 클러스터 −125°~+105°(449 빔), '+90°' → [job6k_nearest.txt](../debug_log/2026-08-28/outputs/job6k_nearest.txt).
- 결함: 클러스터 폭이 230° 라는 것은 0.40~0.55 m 안에 물체가 여럿 = '트인 공간' 전제가 깨졌다는 뜻인데 스크립트는 판정을 그대로 낸다. 클러스터 폭 문턱으로 '판정 불가' 를 내게 해야 했다.

### job6l.sh — 실행 중 상태 사실 확인
- 하는 일: install · src URDF 의 `lidar_joint` origin grep, RSP 프로세스 수, `tf2_echo`, `ros2 param get /robot_state_publisher robot_description` 에서 lidar_joint 문자열, `/tf_static` 1 회 echo(transient_local)에서 lidar_link, foxglove 프로세스.
- 출력: RSP 1, TF RPY (0,0,0), foxglove pid 2911 — 나머지(URDF grep · /tf_static)는 **빈 출력** → [job6l_state_check.txt](../debug_log/2026-08-28/outputs/job6l_state_check.txt).
- 결함: `grep -A3 … | grep origin` 이 origin 줄을 못 잡음(주석 줄이 끼어 줄 수가 넘침 — **추정**), robot_description 은 40 자로 잘려 yaw 가 안 보임, /tf_static echo 는 6 s timeout 안에 못 받음. 'stale 캐시' 가설을 검증하지 못한 도구.

### job6m.sh — π 재배포 + 전체 재시작
- 하는 일: URDF 복사 · 빌드 → sensors/base/slam/description launch · 카메라 · 라이다 · EKF · conditioner · foxglove · RSP · slam 전부 pkill, agent 컨테이너 제거 → 남은 프로세스 수 → base.launch(10 s) → sensors.launch(35 s) → RSP · foxglove 개수, TF, 토픽 hz 4 개.
- 출력: 남은 0, RSP 1 · foxglove 1, RPY (0,0,180), scan 10.001 · imu 200.131 · filtered 29.996 Hz(wheel_odom 칸은 빈 값) → [job6m_yaw_pi_fullrestart.txt](../debug_log/2026-08-28/outputs/job6m_yaw_pi_fullrestart.txt).
- 마지막 안내 줄: "Foxglove 에서 RobotModel + TF 축 켜고 base_link +x(빨강) = 전방 기준으로 확인" — fixed frame 은 언급하지 않았다(그래서 원인을 못 잡음).

### job6n.sh — 손잡이(handedness) 판정 ★ 확정 도구
- 왜: '회전(yaw 로 해결)' 인지 '거울(inverted 필요)' 인지를 TF 없이 가르려고. 사용자가 좌측 벽 ~325 mm · 정면 벽 ~800 mm 로 배치 — 거리 대역만으로 두 벽이 갈린다.
- 하는 일: 4 s 중앙값 → `angle_increment` 부호 출력(+ 면 반시계 = 오른손 표기) → 대역 0.25~0.45 m 빔 = 좌측벽, 0.65~0.95 m = 정면벽 → 각 대역 빔 각도의 **원형 평균**(cos · sin 합의 atan2 — ±180° 경계를 넘는 정면벽에 필요) → d = θ_L − θ_F 를 [−180,180) 로 → |d − 90| < 45 면 오른손(회전), |d + 90| < 45 면 거울, 그 밖은 '애매' → 오른손이면 `round(−θ_F/90)·90` 을 yaw 로.
- 출력: inc +0.1996°, θ_L −86°(−118~+54, 323 빔, 0.40 m), θ_F −168°(−179~+180, 219 빔, 0.91 m), d +82° → 'lidar_yaw +3.1416' → [job6n_handedness.txt](../debug_log/2026-08-28/outputs/job6n_handedness.txt).
- 쓰인 곳: SUMMARY '판정 데이터', URDF 주석.
- 한계: 좌측벽 대역의 각 범위(−118°~+54°)가 172° 로 넓다 — 대역에 다른 물체가 섞였을 수 있어 중심이 수 ° 끌릴 수 있다. 90° 스냅 판정에는 충분하지만 미세 yaw 측정에는 못 쓴다. 지금도 다시 쓸 수 있다(배치만 맞으면). 미세 yaw 는 09-18 `job432c_wallyaw_tf.py`(벽에 옆면 붙이기) 쪽.

### job6o.sh — base_link 각도 검증
- 하는 일: 배포 TF RPY, `ros2 topic info /tf_static` 발행자 수, 6n 과 같은 두 대역을 base 각도(원시 + TF yaw)로 원형 평균 → 정면/좌/우/후 분류.
- 출력: RPY 180, 발행자 2, 좌측벽 +94° '좌측(+y)', 정면벽 +11° '정면(+x)' → [job6o_baselink_walls.txt](../debug_log/2026-08-28/outputs/job6o_baselink_walls.txt).
- 결함: 주석이 '발행자 수(중복 = stale 원인)' 라고 가정 — 실제로는 RSP 와 카메라 드라이버가 각각 /tf_static 을 내는 정상 구성일 수 있다(**추정**, `--verbose` 로 이름을 봤어야).

### job14e_framecheck.sh (09-01) — 손-정면 재확인
- 왜: 사용자 '180° 뒤집힘' 관찰.
- 하는 일: `tf2_echo base_link lidar_link`(Translation · Rotation 12 줄) → `/scan_raw`(디스큐 전 원시, 08-28 이후 rplidar 출력이 `/scan_raw` 로 바뀜) **첫 한 장** → 0.05~12 m 유효 빔 → 전체 최근접의 원시각과 'yaw=π 라면 base 몇 ° = 어느 쪽', 'yaw=0 이라면 …' 를 나란히 → 원시 0 · +90 · 180 · −90 방위 ±20° 창의 최소거리를 yaw 두 경우의 방위 이름과 함께.
- 출력 원문 없음(대화에만). SUMMARY 값: 손을 물리 정면에 대니 원시 180° 창 최소거리 150 → 28 cm(손 전 · 후 두 번 실행한 것으로 보임 — **추정**).
- 쓰인 곳: 09-01 '판단(근거 · 기각가설)' ①.
- 다시 쓸 수 있나: 그대로 쓸 수 있다(한 장만 보므로 손을 대고 있는 동안 실행). '앞에 손 대기 → 원시 180° 만 줄어드는가' 는 가장 싼 yaw 앞뒤 확인법.

## 9. 용어
- **yaw(장착 방향)**: 센서 좌표축이 로버 좌표축(base_link: +x 앞, +y 왼쪽, +z 위, REP-103)에 대해 z 축으로 돈 각. URDF `joint` 의 `origin rpy` 세 번째 값.
- **원시 각도(θ_lidar, θ_msg)**: LaserScan 메시지 안의 빔 각 `angle_min + i·angle_increment`. lidar_link 프레임 기준. base 각도 = 원시 + yaw(평면 스캔, 롤 · 피치 0 일 때).
- **angle_increment 부호**: + 면 빔 순서가 반시계(위에서 볼 때) = ROS 오른손 표기. S2L 은 물리적으로 시계 방향으로 돌지만 `rplidar_ros` 드라이버가 오른손 메시지로 바꿔 내보낸다(URDF 주석). 부호가 − 거나, 두 기준물의 원시 각 차가 −90° 로 나오면 거울상 → `inverted` 문제.
- **손잡이(handedness) 판정**: 왼쪽 기준물 각 − 정면 기준물 각이 +90° 면 회전만으로 맞출 수 있고(오른손), −90° 면 회전으로는 안 되고 뒤집기가 필요(거울).
- **90° 스냅**: 측정 각을 가장 가까운 90° 배수로 반올림. '앞뒤 · 좌우' 판정용. 수 ° 단위 장착 오차는 이걸로 못 본다.
- **원형 평균**: 각도들의 평균을 cos · sin 합의 atan2 로 구함. +179° 와 −179° 의 평균이 0° 가 되는 산술 평균 오류를 피한다.
- **tf_static / latched(transient_local)**: 변하지 않는 변환(센서 장착 등)은 `/tf_static` 에 한 번 발행하고, QoS 를 transient_local 로 둬 늦게 붙은 구독자도 마지막 값을 받는다('래치'). 클라이언트가 예전 값을 쥐고 있으면 'stale' 이 된다 — 이 카드에선 의심만 되고 확인되지 않음.
- **fixed frame(뷰어)**: Foxglove · RViz 가 모든 데이터를 그릴 기준 프레임. 이 프레임이 TF 트리에 없으면(예: SLAM 없이 `map`) 변환이 안 돼 화면이 엉뚱해진다. 센서 장착 확인은 `base_link` 로.
- **RSP(robot_state_publisher)**: URDF 를 읽어 고정 관절을 /tf_static 으로 발행하는 노드. URDF 를 바꾸면 빌드 + RSP 재시작이 필요.
- **스캔면 높이**: S2L 레이저가 도는 평면(지면 + 약 18.5 cm, 08-28 '판단·결정' 1). 이 높이를 벗어난 물체(손 · 종이)는 안 보인다.
