# Jetson Wi-Fi 간헐 무응답 (1 시기: 08-28 · 09-03)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 설정 | 관련 문제 |
|---|---|---|---|---|
| **우회**(실행을 네트워크와 분리 · 절전 끔) · 원인 미확정 · 이후 여러 번 재발(양상이 다름) | 08-28 ~ (이 카드는 09-03 까지 채움) | [08-28 '★ SLAM 첫 맵 완성'](../debug_log/2026-08-28/SUMMARY.md) "detach 실행 → WiFi 무관" | 저장소 파일 없음. Jetson 설정: `wlP1p1s0` power_save off(런타임) + NetworkManager 연결 `802-11-wireless.powersave 2`(영구, **그때 연결된 WEB_DEV_5G 프로파일에만**) — 09-03 | [첫 SLAM 지도](first-slam-map.md)(detach 실행이 생긴 곳) · 이후 DDS 분리 · IP 충돌(다음 시기) |

**한 줄**: PC 에서 Wi-Fi 너머 Jetson 으로 SSH 를 걸어 로버를 움직이는데, 그 연결이 가끔 몇 분씩 끊긴다. 08-28 에는 회전 스크립트가 SSH 와 함께 죽어 '재부팅이 아님' 을 확인(`job7g`)한 뒤 **스크립트를 Jetson 안에서 독립 실행(detach)** 하게 바꿔 우회했다. 09-03 저녁에는 플래시 직후 PC → Jetson ping 100 % 손실이 수 분씩 반복돼 Jetson 쪽을 진단(링크 유지 · 신호 −53 dBm · 끊김 로그 없음 · **절전 켜짐**)하고 절전을 껐다. 그 뒤 60 회 중 57 회 응답(5 % 손실) — 쓸 만하지만 완전하지 않았고, 절전이 원인인지는 확정하지 못했다(끈 직후에도 83 % 손실, 회복은 약 2 분 뒤).

> 읽는 법: 08~09 월 초 기록은 § 번호가 없어 '날짜 + 제목 글자' 로 인용. 09-03 Wi-Fi 진단 도구 3 개는 **출력 원문이 없다**(대화에만) — 수치는 SUMMARY 문장이 유일한 출처.

## 1. 증상
- 08-28 오전: 제자리 회전(`job7f`, SSH 전경 실행) 도중 연결이 끊겨 스크립트가 중간에 죽음. 이것은 SUMMARY 에 직접 문장으로는 없고, 다음 세 가지로 **재구성**한 것이다 — `job7g` 의 질문('재부팅 vs WiFi 단절 판별'), `job7h` 의 '잔존 회전 프로세스 정리', detach 실행기 `job7i_launch` 의 주석 'WiFi 끊겨도 Jetson 에서 독립 완주'. 끊긴 시각 · 길이 · 그때 회전량은 기록 없음.
- 09-03 18:30~18:45: 새 펌웨어 플래시 직후 PC(172.30.1.89) → Jetson(192.168.0.101) ping 100 % 손실이 수 분간 반복. 경로상 PC 쪽 공유기(172.30.1.254, WAN 192.168.0.6)가 'host unreachable' 회신 = .6 이 Jetson 의 ARP 응답을 못 받음([09-03 '플래시 + Jetson Wi-Fi 간헐 무응답 (18:30~18:45)'](../debug_log/2026-09-03/SUMMARY.md)).

## 2. 흐름 (시간순)
| 날짜 · 시각 | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 08-28 (11:23 전) | `job7f` 360° 회전을 SSH 로 실행 | 도중 끊김(위 재구성) | — | [`job7f.sh`](../debug_log/2026-08-28/jobs/job7f.sh)(출력 원문 없음) |
| 08-28 11:23 | 재부팅인지 단절인지 | uptime 2:32 · 부팅 08:51:45 · 노드 · agent 생존 · 신호 −44 dBm(Link Quality 66/70) | 재부팅 아님 → 네트워크 단절 | [`job7g.sh`](../debug_log/2026-08-28/jobs/job7g.sh) · [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt) |
| 08-28 | 잔존 회전 정리 · 정지 확인 | 잔존 없음 · ω ≈ 0 · `/cmd_vel` 무발행 | 로버는 서 있음 | [`job7h.sh`](../debug_log/2026-08-28/jobs/job7h.sh) · [`job7h_safety_cleanup.txt`](../debug_log/2026-08-28/outputs/job7h_safety_cleanup.txt) |
| 08-28 11:28 | detach v1 | 로그 빈 채 · 회전 안 함 | 실패(원인 미확인) | [`job7i_launch.sh`](../debug_log/2026-08-28/jobs/job7i_launch.sh) · [`job7j_spin_log.txt`](../debug_log/2026-08-28/outputs/job7j_spin_log.txt) |
| 08-28 11:42 | detach v2 | 59 s 완주 · 로그 실시간 | "WiFi 드롭 무관(제어경로 Jetson→USB→보드 로컬)" | [`job7k.sh`](../debug_log/2026-08-28/jobs/job7k.sh) · [`job7k_launch.sh`](../debug_log/2026-08-28/jobs/job7k_launch.sh) · [`job7j3_spin_final.txt`](../debug_log/2026-08-28/outputs/job7j3_spin_final.txt) |
| 09-03 18:30 무렵 | 펌웨어 플래시 · `-rst` 뒤 PC → Jetson ping | 100 % 손실 수 분 반복, .6 이 'host unreachable' | PC 쪽 공유기의 ARP 실패 | SUMMARY 문장만 |
| 09-03 | Jetson 쪽 진단(읽기 전용) | `wlP1p1s0` · WEB_DEV_5G ch36 · −53 dBm · AP 1 개 · NM 끊김 로그 없음 · 커널 로그 없음 · 트래픽 ≈ 0 · **Power save: on** | 링크 자체는 유지 | [`wifi_diag.sh`](../debug_log/2026-09-03/jobs/wifi_diag.sh) · [`wifi_diag2.sh`](../debug_log/2026-09-03/jobs/wifi_diag2.sh)(출력 원문 없음) |
| 09-03 | 절전 끄기(sudo, 사용자 고지) | 직후 30 s ping **83 % 손실** → 약 2 분 뒤 .6 · .1 · .101 각 15 회 0 % → 60 s 샘플 57/60 응답(5 % 손실, 최대 308 ms) | 사용 가능하나 완전하지 않음. 원인 **미확정**(해제와 회복이 시간상 겹치나 즉시 회복 아님) | [`wifi_fix.sh`](../debug_log/2026-09-03/jobs/wifi_fix.sh)(출력 원문 없음) |
| 09-03 '내일 할 일' 4 | 재발 관찰 | — | 재발 시 2.4 GHz SSID 또는 유선 검토 | [09-03 '마무리 (18:48)'](../debug_log/2026-09-03/SUMMARY.md) |

이후(09-04 ~): 다음 시기에서 채움. 기록 위치만 적어 둔다.
- 09-15 14:03 · 09-16 15:57 · 09-17 13:38 — WEB_DEV_5G AP 가 먼저 끊고(deauth) 재인증 거부 → NetworkManager 가 예비 망 ALOPS(172.30.1.8)로 전환: [09-15 §3 · §3.1](../debug_log/2026-09-15/SUMMARY.md) · [09-17 §8.7 · §17](../debug_log/2026-09-17/SUMMARY.md). 09-17 §17 에 '09-03 에 끈 절전은 WEB_DEV_5G 프로파일뿐, ALOPS 는 절전 켜짐' 이 확인돼 있다.
- 09-18 공유기 로그 · 설정 조사, 끊김 계측 서비스(wifi-mon) 설치: [09-18 §3 · §4 · §7](../debug_log/2026-09-18/SUMMARY.md).
- 09-23 부팅 직후 DHCP 무응답(다른 양상) · 고정 IP(DHCP 예약) · ARP 중복 감시: [09-23 §0.1 · §5 · §11](../debug_log/2026-09-23/SUMMARY.md).
- 10-07 DHCP 무응답 재발 → ALOPS 로 작업: [10-07 §2.1](../debug_log/2026-10-07/SUMMARY.md).
- 10-14 사용자가 찾은 원인 — 다른 서버가 192.168.0.101 을 받아 IP 충돌: [10-14 §8.3~§8.6](../debug_log/2026-10-14/SUMMARY.md).
- 10-15 부터 192.168.0.110(DHCP 예약): [10-15 §1.1](../debug_log/2026-10-15/SUMMARY.md). 10-21 SSID 송출 중단: [10-21 §4](../debug_log/2026-10-21/SUMMARY.md).

## 3. 가설과 판별 (09-03 까지)
| 가설 | 판별 | 결과 | 판정 |
|---|---|---|---|
| 08-28 끊김 = Jetson 재부팅(전원 · 과부하) | `job7g` uptime · 부팅 이력 · 노드 생존 | 2:32 가동, 노드 · agent 생존 | **기각** |
| 08-28 끊김 = 약한 신호 | `job7g` iwconfig | −44 dBm, 66/70 | '지금은 좋음' 까지만 — 끊긴 순간 값이 아니라 **미확인** |
| 09-03 = Jetson 무선 링크 자체가 끊김 | `wifi_diag` · `wifi_diag2`(link · station dump · NM 로그 · 커널 로그) | 링크 유지 · NM · 커널 끊김 기록 없음 | **기각**(그 시각 기준) |
| 09-03 = Wi-Fi 절전(power save)으로 Jetson 이 ARP 에 늦게 답함 | 절전 끄고 ping | 직후 83 % 손실 → 약 2 분 뒤 회복 → 5 % 손실 | **미확인** — 끈 효과인지 저절로 회복인지 못 가름(끄기 전 같은 시간 동안의 기준선 없음) |
| 09-03 = PC 쪽 공유기(.6)의 WAN ARP | .6 이 'host unreachable' 을 회신 | 증상 위치는 .6 | 후보로 남김(공유기 쪽 로그 없음) — **미확인** |
| 09-03 = Jetson 무선 칩 드라이버(RTL8822CE 5 GHz) | — | 시험 없음 | 후보로 남김 — **미확인** |
| 플래시(ST-Link `-rst`)가 방아쇠 | 시간상 겹침만 | — | 플래시는 보드(MCU)이고 Jetson 무선과 연결고리 없음 — 우연으로 봄(**추정**, 판별 안 함) |

## 4. 조치와 효과
- **08-28 · detach 실행(가장 효과가 큰 조치)**: 로버를 움직이는 스크립트를 Jetson 안에서 SSH 와 무관하게 돌리고(`setsid … </dev/null &` + `disown`, 출력은 `/tmp/spin.log`), PC 는 나중에 로그만 읽는다(`job7k` · `job7k_launch` · `job7j`). 끊겨도 스크립트 자체의 가드 · 목표 · 시간 제한으로 끝난다. 효과: 같은 날 360° 회전 완주(59 s). 제어 경로(Jetson → USB → 보드)는 Wi-Fi 를 안 지나므로 '주행 중 끊김' 이 주행을 멈추지는 않는다 — 반대로 **PC 에서 멈출 수도 없다**(09-03 '벤치마크 중에는 … 사용자가 물리 정지 담당').
- **09-03 · 절전 끄기**: `iw dev wlP1p1s0 set power_save off`(재부팅 때 사라짐) + `nmcli con modify <당시 연결> 802-11-wireless.powersave 2`(그 프로파일에 영구). 효과: 5 % 손실 · 최대 308 ms 까지(위 표). 한계: 다른 프로파일(ALOPS)에는 적용 안 됨(09-17 §17 에서 확인).
- 남은 위험(09-03 판단): 주행 중 끊기면 Nav2 는 Jetson 에서 계속 돈다 → 사람이 물리적으로 정지. 온보드 정지 수단 · 목표 시간 제한은 다음 시기(09-29 '정지 수단', `nav_guard`).

## 5. 내 실수
- 이 시기에 '틀린 판정을 고친' 기록은 없다. 다만 두 가지는 판별이 비어 있다(다음 칸에 남김).
  - 08-28 끊김의 사실 자체가 SUMMARY 에 문장으로 없다 — 도구 주석으로만 재구성 가능. **다음에 알아보는 법**: 연결 끊김은 그 순간 PC 쪽 시각 · 증상(ssh 오류 문구) · 길이를 SUMMARY 에 한 줄로 남긴다.
  - 09-03 절전 OFF 의 효과를 '전후 같은 길이의 ping 기준선' 없이 판단했다. **다음에 알아보는 법**: 설정을 바꾸기 전에 같은 조건의 기준선(예: 60 s ping 손실률)을 먼저 남기고, 바꾼 뒤 같은 측정 — 그래야 '저절로 회복' 과 구별된다.

## 6. 남은 것 (09-03 시점)
- 원인 — 절전 · 공유기 ARP · 드라이버 중 무엇인지 미확정. 이후 양상이 다른 사건들이 이어짐(§2 이후 목록).
- 절전 설정이 프로파일별이라는 점(다른 SSID 로 붙으면 다시 켜짐).
- 주행 중 원격 정지 수단 없음.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job7g` | 재부팅 vs 단절 판별 | 08-28, 해설은 [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설) |
| `job7h` · `job7i_launch` · `job7j` · `job7k` · `job7k_launch` | 정지 확인 · detach 실행 · 로그 확인 | 08-28, 해설은 [첫 SLAM 지도 §8](first-slam-map.md#8-도구-해설) (아래에 요점만) |
| `wifi_diag.sh` · `wifi_diag2.sh` · `wifi_fix.sh` | 09-03 진단 · 절전 끄기 | `2026-09-03/jobs/` |

## 8. 도구 해설
공통: Jetson 에서 실행, PC → WSL → sshpass 러너(원본 소실, 후손 [`2026-10-08/jobs/run_jn.sh`](../debug_log/2026-10-08/jobs/run_jn.sh)). 09-03 도구는 이름이 번호(job)가 아닌 용도 이름인 첫 예(도구 이름 규약이 정식으로 생긴 것은 10-12).

### job7g · job7h — 단절 판별 · 정지 확인 (08-28) — 요점
- `job7g`: uptime · 부팅 시각 · `last -x` · ROS 프로세스 수 · agent Up 시간 · 보드 토픽 · HID 모듈 · `iwconfig` 신호. 재부팅이면 uptime 이 짧고 노드 · agent 가 사라진다는 논리. 출력 [`job7g_reboot_check.txt`](../debug_log/2026-08-28/outputs/job7g_reboot_check.txt). 한계: 신호는 '지금' 값.
- `job7h`: 회전 프로세스 패턴 `pkill` → 빈 `/cmd_vel` 8 회 → 실제 속도 → `/cmd_vel` 무발행 확인. 끊긴 뒤 '로버가 정말 서 있나' 를 원격으로 확인하는 첫 도구.

### job7i_launch → job7k_launch + job7k — detach 실행 (08-28) — 요점
- v1(`job7i_launch`): `setsid nohup bash /tmp/job7f.sh > /tmp/spin.log 2>&1 &`. 결과: 로그 빈 채 · 회전 안 함(원인 미확인). python 출력 버퍼링(`-u` 없음), stdin 미분리, `disown` 없음이 차이.
- v2(`job7k_launch` → `job7k`): 실행기는 `setsid bash /tmp/job7k.sh </dev/null >/dev/null 2>&1 &` + `disown` + 6 s 뒤 프로세스 수 · 로그 5 줄. 코어는 `exec >>/tmp/spin.log 2>&1` 로 자기 출력을 로그에, `python3 -u` · `flush=True`, 2 s 마다 진행 줄, 시작 · 끝 시각.
- 확인: `job7j`(로그 · 프로세스 · ω · 지도 · uptime · 세션)를 끊김과 무관하게 아무 때나 실행.
- 계보: 이 형태가 이후 모든 주행 러너의 뼈대(09 월 `run_detached` · 10 월 `run_jn.sh` · `/tmp/live/current.log` 실시간 로그 — 다음 시기).

### wifi_diag.sh — 무선 상태 진단 (09-03, 읽기 전용)
- 왜: ping 이 수 분씩 죽는데 Jetson 은 살아 있는지, 링크가 끊긴 건지.
- 하는 일: ① `iw dev` 에서 첫 인터페이스 이름(`wlP1p1s0`) · `uptime -p` ② `iw dev <IF> link` 의 SSID · signal · freq · rx/tx bitrate ③ `iw dev <IF> get power_save` ④ `nmcli -t -f DEVICE,STATE,CONNECTION dev status` 에서 그 장치 줄, 그 연결의 `802-11-wireless.powersave` · `connection.autoconnect-retries` ⑤ `journalctl -u NetworkManager --since "20 min ago"` 에서 disconnect · deactivat · activated · roam · auth · dhcp4 주소/임대 줄 마지막 12 ⑥ `dmesg` 에서 wlan · rtw · rtl88 · iwlwifi · brcm · wlP 마지막 8 ⑦ `ip -4 -br addr show <IF>`.
- 출력: 원문 없음(대화에만). SUMMARY 에 옮긴 것: WEB_DEV_5G · ch36 · −53 dBm · NM 끊김 로그 없음 · 커널 로그 없음 · **Power save: on**.
- 쓰인 곳: '링크는 유지 · 절전 켜짐' → `wifi_fix.sh`.
- 결함: NM 로그 20 분 창은 사건 시각을 정확히 덮는지 확인 안 함. `dmesg` 는 sudo 없이 실행 — 커널 설정에 따라 일반 사용자에게 막힐 수 있다(그 경우 '로그 없음' 과 '못 읽음' 이 같은 빈 출력, **추정**).
- 계보: → 09-17 `job427*_wifi.sh`(syslog 전체에서 deauth · reason 코드) → 09-18 `job428_wifi_dfs.sh` → 09-23 `job529_wifi_collect.sh`(다음 시기).
- 지금 다시: 그대로 쓸 수 있음. 지금은 `/var/log/wifi_mon/` 계측 기록이 더 낫다.

### wifi_diag2.sh — 연결 세부 · 트래픽 (09-03, 읽기 전용)
- 하는 일: ① `iw dev wlP1p1s0 station dump` 의 inactive · rx/tx packets · tx retries · tx failed · beacon loss · rx drop · signal · bitrate · connected time ② `nmcli dev wifi list --rescan no` 에서 같은 SSID(WEB_DEV) 의 AP 목록(로밍 후보 — BSSID · 채널 · 신호) ③ `journalctl -k --since "30 min ago"` 에서 무선 · deauth · disassoc · beacon 줄 ④ `ip neigh show dev wlP1p1s0`(게이트웨이 ARP 상태) ⑤ `/proc/net/dev` 를 5 s 간격 두 번 읽어 rx/tx kB/s ⑥ 실행 중 큰 노드(foxglove · controller_server · slam · ekf · rplidar · realsense) ⑦ `ss -tn state established` 외부 피어(예: Foxglove 8765 에 붙은 PC).
- 출력: 원문 없음. SUMMARY 에 옮긴 것: AP 1 개(로밍 아님) · 커널 로그 없음 · 트래픽 ≈ 0.
- 쓰인 곳: '로밍 · 트래픽 포화 · 커널 오류' 를 배제.
- 결함: tx retries/failed · beacon loss 수치는 SUMMARY 에 안 옮겨져 **원천 소실**.

### wifi_fix.sh — 절전 끄기 (09-03, sudo · 사용자 고지)
- 하는 일: 현재 연결 이름을 `nmcli -t -f DEVICE,CONNECTION dev status` 로 찾고 → `sudo iw dev wlP1p1s0 set power_save off`(런타임) → `sudo nmcli con modify "<연결>" 802-11-wireless.powersave 2`(영구; 2 = 끔) → 확인 줄 'power_save now: … NM(영구): …'. 비밀번호는 `<PW>` 로 가림.
- 출력: 원문 없음. 효과 수치는 §2 표(SUMMARY 문장).
- 알려진 결함: **그 순간 연결된 프로파일(WEB_DEV_5G)에만** 영구 적용 — 다른 SSID 로 자동 전환되면 절전이 다시 켜진다(09-17 §17 에서 실제로 확인). 적용 전 기준선 측정이 없다(§5).
- 되돌리기: `nmcli con modify <연결> 802-11-wireless.powersave 0`(기본값 = 전역 설정 따름) · `iw … power_save on`.
- 지금 다시: 쓸 수 있음. 쓸 때는 모든 무선 프로파일에 같이.

## 9. 용어
- **Wi-Fi power save(절전)**: 무선 카드가 쉬는 동안 AP 에게 '잠든다' 고 알리고 비콘 몇 번에 한 번만 깨어나 쌓인 패킷을 받는 방식. 전력은 줄지만 바깥에서 오는 패킷(ARP 질문 · ping)에 수백 ms 늦게 답하거나 놓칠 수 있다. `iw dev <IF> get power_save` 로 상태를 본다.
- **NetworkManager(NM)**: Ubuntu 의 네트워크 관리 데몬. 저장된 '연결 프로파일'(SSID · 비밀번호 · IP 방식 · 절전 · 자동연결 우선순위)을 들고 있다가 자동으로 붙는다. `nmcli` 가 명령줄 도구. `802-11-wireless.powersave` 값: 0 = 기본(전역 따름) · 2 = 끔 · 3 = 켬. 연결 중인 망이 끊기면 다음 우선순위 프로파일로 옮겨 가며, 이때 IP 가 바뀐다.
- **ARP**: 같은 망 안에서 'IP 주소 → 장치 MAC 주소' 를 묻는 방송 질문. 공유기가 Jetson 에게 패킷을 넘기려면 먼저 ARP 로 Jetson 의 MAC 을 알아야 한다. 답이 없으면 공유기는 'host unreachable' 을 돌려준다(09-03 의 .6). 같은 IP 를 두 장치가 쓰면(IP 충돌) ARP 답이 엇갈린다(10-14).
- **망 구조(이 시기)**: PC(172.30.1.89) → PC 쪽 공유기(LAN 172.30.1.254 / WAN 192.168.0.6) → 192.168.0.x 망 → Jetson(WEB_DEV_5G, 192.168.0.101). PC 와 Jetson 은 다른 서브넷이고 가운데 공유기가 NAT 로 이어 준다.
- **detach(setsid · nohup · disown)**: SSH 세션이 끊겨도 프로세스가 살아 있게 띄우는 방법 — [첫 SLAM 지도 §9](first-slam-map.md#9-용어).
- **deauth / 재인증 거부**(이후 시기 용어 미리): AP 가 클라이언트를 먼저 끊는 관리 프레임(reason 코드 포함), 그 뒤 같은 비밀번호로 다시 붙으려 할 때 AP 가 거절하는 것 — 09-15~17 사건의 양상.
