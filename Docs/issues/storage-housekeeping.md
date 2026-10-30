# 로그 · 산출물 누적과 정리 보류 (3 시기: 09-18)

| 상태 | 기간 | 처음 본 곳 | 바꾼 파일 · 규칙 | 관련 문제 |
|---|---|---|---|---|
| **보류**(사용자 결정 '몇 GB 단위가 아니면 정리는 뒤로') · 공간 압박 없음 · 구조 문제 4 개는 남음 | 09-18 ~ (이 카드는 09-18 까지 채움 + 뒤 시기 포인터) | [09-18 §8](../debug_log/2026-09-18/SUMMARY.md) '로그 · 산출물 누적 조사(사용자 요청, 읽기 전용 — 삭제 없음)' | 바꾼 것 없음(조사만). 규칙: 보류 목록 순서(§4) · 작업 폴더 삭제 금지 조건 | [Jetson Wi-Fi](jetson-wifi-link.md)(같은 날, syslog 무회전 · wifi-mon 자체 회전) · 이후 큰 bag 수명 규칙(10-19) |

**한 줄**: 09-18 에 사용자 요청으로 Jetson 과 PC 에 쌓인 로그 · bag · 스크립트를 읽기만 하며 조사했다. Jetson 은 233 GB 중 28 GB 사용(193 GB 여유)이라 공간 문제는 없었지만, ① **logrotate 가 설치돼 있지 않아 `/var/log/syslog` 가 2 월부터 한 파일(144.6 MB)로 회전 없이 쌓임** ② PC 작업 폴더(세션 스크래치패드)에 저장소와 **겹치는 bag 160 MB 와 저장소에 없는 원본 bag 114 MB** 가 섞임 ③ **평문 비밀번호가 든 스크립트 사본 257 개** ④ 실제 운용 러너가 세션 임시 폴더에 있음 — 네 가지 구조 문제를 찾았다. 사용자는 '몇 GB 단위가 아니면 정리는 뒤로 미룬다' 고 정해 아무것도 지우지 않았고, 보류 목록을 순서대로 남겼다. 이후 ④ 는 09-28 에 그 작업 폴더가 통째로 사라지면서 현실이 됐고(원본 bag 114 MB 도 그때 함께 없어진 것으로 보임 — 추정), 10-12 에 상시 도구를 `Docs/tools/` 로 옮기는 규약이 생겼다. ① · ③ 은 이 카드 범위의 기록에서 처리되지 않았다.

> 읽는 법: 수치는 [`j430_disk.txt`](../debug_log/2026-09-18/outputs/j430_disk.txt) · [`j430b_logs.txt`](../debug_log/2026-09-18/outputs/j430b_logs.txt) · [`j430c_talkers.txt`](../debug_log/2026-09-18/outputs/j430c_talkers.txt)(Jetson)와 SUMMARY §8.2(PC — **출력 원문 없음**, Git Bash `du` · `git count-objects` 를 대화에서 실행). MB 는 도구마다 단위가 달라 같은 파일이 137.9(MiB, `du`/1048576)와 144.6(10⁶ B)로 적혀 있다 — 같은 값이다(144,564,126 B).

## 1. 증상
- 문제가 터진 게 아니라 **사용자 요청 조사**. 계기는 같은 날 Wi-Fi 분석에서 syslog 144 MB 를 통째로 훑어야 했던 것, 그리고 `job429_probe` 가 `logrotate.timer inactive` 를 보인 것([09-18 §7.1](../debug_log/2026-09-18/SUMMARY.md) '`/var/log/syslog` 는 … 회전되지 않는다 — 별도 과제').

## 2. 흐름 (시간순)
| 날짜 · § | 한 일 | 본 것(수치) | 그때 결론 | 데이터 |
|---|---|---|---|---|
| 09-18 §7.1 | Wi-Fi 계측 사전 점검 중 | 디스크 193 GB 여유 · syslog 144,399,555 B · `logrotate.timer` inactive · cron active · `/etc/logrotate.d/` 에 rsyslog 설정은 있음 | 회전 안 됨 → 별도 과제 | [`j429_probe.txt`](../debug_log/2026-09-18/outputs/j429_probe.txt) |
| 09-18 §8.1 | Jetson 큰 디렉터리 · 큰 파일 · logrotate · `/tmp` · `~/.ros/log` · docker (`job430`) | `/var/log` 156 MB · apt 캐시 193 MB · snapd 3,040 MB · `~/.ros` 49 MB · `/opt/ros` 734 MB · `/tmp` ≈0(아침 재부팅) · 100 MB 넘는 파일은 ollama 라이브러리 · snap 리비전 · 희소 파일 lastlog · antigravity IDE · bag/db3 0 개 | 공간 문제 없음 | [`j430_disk.txt`](../debug_log/2026-09-18/outputs/j430_disk.txt) |
| 09-18 §8.1 | logrotate 실체 · `~/.ros/log` 구성(`job430b`) | **`dpkg: un logrotate`**(미설치) · 바이너리 · cron.daily · timer · status 파일 모두 없음 · `/var/log` 파일 33 · 회전본 4 · syslog 144,564,126 B · kern.log 12,654,237 B · auth.log 3,482,255 B · lastlog 실제 16 KB(겉보기 173,097,544 B) · `~/.ros/log` 항목 9,746(launch 디렉터리 660 · python3 5,630 · nav2 노드별 224) · 47 MB · 30 일 넘은 파일 1,952 개 17.3 MB | 설정 파일만 있고 실행 주체가 없다 | [`j430b_logs.txt`](../debug_log/2026-09-18/outputs/j430b_logs.txt) |
| 09-18 §8.1 | syslog 를 채우는 것(`job430c`) | 날짜별 09-07~09-15 7.2~9.7 MB/일 → 09-16 2.2 · 09-17 1.2 · 09-18 0.2(오전) · 09-17 상위 반복: iio-sensor-proxy 'iio:device busy' 1,056 + 반복 묶음 640 · SSH 세션 시작 791 · 종료 787 · UVC 조회 실패 453 + 98 | 감소 = 09-16 mavlink-router 끔. 현재 주 발생원 = iio-sensor-proxy · SSH 폴링 · 카메라 UVC | [`j430c_talkers.txt`](../debug_log/2026-09-18/outputs/j430c_talkers.txt) |
| 09-18 §8.2 | PC 저장소 · 작업 폴더 · WSL | `.git` pack 7.8 MB · 작업 트리 309 MB 중 bag 186 MB(09-10 22 · 09-14 46 · 09-15 3 · 09-16 52 · 09-17 60) · 작업 폴더 `82ce61d4…/scratchpad` 283 MB · 810 파일(bag 37 개 275 MB 중 27 개 160 MB 는 저장소와 이름 · 크기 일치, **10 개 114 MB(09-11 v1~v4 · *_ret · cr1 · ret2)는 저장소에 없음**, 스크립트 job 329 · run 239) · 평문 비밀번호: 작업 폴더 러너 241 · WSL `/tmp` 16 · WSL `/tmp` 12 MB · 1,913 파일 · 빈 세션 폴더 5 | bag 은 이 PC 에만 있고 백업 없음 | SUMMARY 문장만(**출력 원문 없음**) |
| 09-18 §8.3 | 판단 | — | 공간은 급하지 않다. 문제는 구조 4 개(위 한 줄) | — |
| 09-18 §8.4 | **사용자 결정** | — | **몇 GB 단위가 아니면 정리는 뒤로**. 이번엔 아무것도 지우지 않음. GB 단위인 snap(3.0 GB) · ollama(≈3.7 GB)는 개인 도구라 대상 외 | — |

이후(09-21 ~): 다음 시기에서 채움. 기록 위치만 적어 둔다.
- 09-28: 작업 폴더 `82ce61d4…/scratchpad` 가 09:12 경 **폴더째 사라짐**(사용자 · Claude 가 지우지 않음, 도구의 오래된 세션 정리로 추정). 핵심 러너는 `Docs/debug_log/*/jobs/` 보관본(비밀번호 `<PW>`)으로 복원, 대체 러너 `run_jn.sh`: [09-28 SUMMARY](../debug_log/2026-09-28/SUMMARY.md) '스크래치패드' 줄(§ 번호 없는 머리 부분, 55 줄 무렵). ⚠ 보류 ② 의 '09-11 원본 bag 10 개를 저장소로 옮긴 뒤에만 …' 은 실행된 기록이 없고 저장소에 `2026-09-11/bags/` 가 없다 → **그 114 MB 는 이때 함께 소실된 것으로 보인다**(추정 — 다른 곳에 사본이 있는지 미확인).
- 10-12: 도구 이름 · 위치 규약(상시 도구는 `Docs/tools/`) — CLAUDE.md '도구 규약'. 보류 ③ 의 앞 절반(도구를 저장소로)은 이것으로 진행됨. 뒤 절반(비밀번호를 git 제외 파일에서 읽기)은 `run_jn.sh`(10-08)도 아직 `sshpass -p <PW>` 형태라 **미해결**.
- 10-19: GB 급 bag 은 '시각화 → 사용자가 짚는 부분 분석 → 기록 → 사용자 확인 뒤 삭제'(사용자 규칙, 메모리 '큰 bag 수명'). 작은 bag(수백 MB 이하)은 이 카드의 보류 규칙 그대로.
- (10-30 이 카드를 쓰며 읽기만 측정) PC 저장소 작업 트리의 `Docs/debug_log/*/bags` 합계 **약 4.4 GiB**(`du -sc` 4,628,940 KiB), `.git` 323 MB. 09-18 의 186 MB · 7.8 MB 와 비교하면 bag 은 이제 **GB 단위**다 — '몇 GB 단위면 다시 본다' 는 결정의 문턱을 넘었다(판단은 사용자 몫).

## 3. 판단의 근거와 한계
| 항목 | 측정 | 판단 | 한계 |
|---|---|---|---|
| 공간 | Jetson 193 GB 여유 · 로그 증가 1~2 MB/일(09-16 이후) | 급하지 않음 | 09-18 하루치 0.2 MB 는 오전만 |
| syslog 무회전 | logrotate 미설치(`dpkg un`) | 크기보다 **분석 비용** 문제(사건 하나 찾으려 144 MB 전체를 훑음) · 2 월부터 한 파일이라 오히려 Wi-Fi 전체 기간 집계가 가능했던 이점도 있음(09-17 §17.2) | 설치하면 첫 회전 때 현재 파일이 `.1` 로 밀리므로 '현 syslog 보관본 먼저'(보류 ①) |
| iio-sensor-proxy | 09-17 1,696 줄 | 카메라 IMU(HID 장치)를 데스크톱 화면 회전 서비스가 열려다 실패하는 것 — **추정**(서비스 이름 · 장치 busy 문구에서 추론, 장치 번호 대조 안 함) | 끄면 데스크톱 화면 회전이 안 됨(이 로버엔 무관, 추정) |
| `~/.ros/log` 9,746 항목 | 47 MB | 크기는 작고 개수가 많음 | ROS 2 는 자체 정리 없음 |
| 중복 bag | 이름 · 크기 일치 27 개 160 MB | 지워도 되는 쪽 | 해시 대조는 안 함(이름 · 크기만) |
| 평문 비밀번호 사본 | 257 개 | 크기가 아니라 **보안** 항목 — GB 규칙과 별개로 다뤄야 함 | 개수는 grep 결과(원문 없음) |
| 작업 폴더의 러너 | 러너 239 · job 329 | 지우면 도구가 사라짐 → ③ 전엔 지우지 말 것 | 세션 폴더 자체가 영구 보관소가 아니었다(09-28) |

## 4. 조치(보류 목록, 09-18 §8.4 순서 그대로)
1. Jetson logrotate 설치(현 syslog 보관본 먼저). — 이후 기록 없음, **미실행**.
2. 작업 폴더 bag: 09-11 원본 10 개 114 MB 를 저장소 bags 로 옮긴 **뒤에만** 중복 27 개 삭제. — 옮긴 기록 없음, 09-28 폴더 소실(§2 이후).
3. 운용 도구를 저장소 `tools/` 로 옮기고 비밀번호를 git 제외 파일에서 읽게 한 뒤 평문 사본 257 개 삭제. — 도구 이동은 10-12 규약으로 진행, 비밀번호 방식은 미해결.
4. `~/.ros/log` · apt 캐시 · iio-sensor-proxy. — 미실행.
- 함께 적은 것: `wifi-mon` 로그는 자체 회전(mon 50 MB · debug 300 MB, 각 `.1` 하나)이라 켜 둬도 된다.

## 5. 내 실수 · 기록 사이 모순
- 이 시기에 틀린 판정을 고친 기록은 없다. 원문 대조로 본 것:
  1. **'디렉터리 9746 개'**(`j430_disk.txt` §6)는 라벨 오류 — 실제는 항목 9,746(파일)이고 디렉터리는 660(`j430b_logs.txt`). SUMMARY 는 맞게 옮겼다.
  2. **단위**: syslog 137.9(MiB) vs 144.6(MB) — 위 '읽는 법'. lastlog 165.1 MB 도 MiB(173,097,544 B).
  3. **`job430` §9 'bag · db3 흩어진 것' 빈 출력**은 '없음' 이 맞다(아침 재부팅으로 `/tmp` 비움 + 홈엔 bag 안 둠). 다만 이 결과는 '재부팅 직후' 라는 조건부.
  4. **PC 쪽 수치는 원문이 없다** — 257 · 160 MB · 114 MB 는 SUMMARY 문장이 유일한 출처. **다음에 알아보는 법**: PC 쪽 조사도 Jetson 처럼 스크립트(`jobs/`)로 돌려 출력을 `outputs/` 에 남긴다(그랬다면 09-28 소실 뒤에도 무엇이 있었는지 목록이 남았을 것).
  5. **보류 ② 의 순서는 지켰지만 결과적으로 원본을 잃었다(추정)**: '옮긴 뒤에만 지운다' 는 우리가 지우는 경우만 막았고, 폴더가 **저절로** 사라지는 경우는 막지 못했다. **다음에 알아보는 법**: 저장소 밖에만 있는 원본(세션 스크래치패드 · Jetson `/tmp`)은 '정리' 가 아니라 '보존' 항목이다 — 크기 규칙과 상관없이 발견 즉시 저장소 `bags/` 로 옮긴다.

## 6. 남은 것
- syslog 무회전(보류 ①) · `~/.ros/log` · apt 캐시 · iio-sensor-proxy 로그 잡음.
- 비밀번호를 스크립트에 쓰는 방식(러너 · `SPW=<PW>` 원격 명령줄 — Jetson 프로세스 목록에 평문, [Jetson Wi-Fi §8.1](jetson-wifi-link.md#81-3-시기-도구-09-15--09-18)).
- 저장소 bag 이 GB 단위가 됨(10-30 측정) — 사용자 결정 대상.

## 7. 실험 · 도구 색인
| 이름 | 무엇 | 위치 |
|---|---|---|
| `job430_disk.sh` (+ `run_j429.sh job430_disk.sh` 형태로 실행, 추정) | Jetson 디스크 · 큰 디렉터리 · 큰 파일 · logrotate · `/tmp` · `~/.ros/log` · docker · bag 흩어짐 | `2026-09-18/jobs/` → `outputs/j430_disk.txt` |
| `job430b_logs.sh` | logrotate 설치 여부 · `/var/log` 회전본 · `~/.ros/log` 구성 | `2026-09-18/jobs/` → `outputs/j430b_logs.txt` |
| `job430c_talkers.sh` | syslog 날짜별 크기 · 9/17 프로그램별 · 반복 메시지 | `2026-09-18/jobs/` → `outputs/j430c_talkers.txt` |
| PC `du` · `git count-objects` | 저장소 · 작업 폴더 · WSL `/tmp` | 대화에서 실행, 출력 원문 없음 |

## 8. 도구 해설
공통: Jetson 에서 실행, PC/WSL 러너가 올려 돌림(09-18 러너 `run_j429.sh` 는 첫 인자로 스크립트 이름을 받는 범용형 — `job430*` 전용 러너는 저장소에 없어 이 형태로 돌렸다고 **추정**). sudo 는 `SPW` 환경변수 → `S()` 함수(크기 읽기용, 삭제 명령 없음).

### job430_disk.sh — 누적 조사 본체 (09-18, 읽기 전용 · sudo 는 크기 읽기)
- 왜: 사용자 요청 '로그 · 산출물이 얼마나 쌓였나' — 지울 것을 정하기 전의 목록.
- 하는 일: ① `df -h / /tmp` ② 고정 목록 17 곳(`/var/log` · journal · crash · apt 캐시 · docker · snapd · `/tmp` · `~/.ros` · `~/.ros/log` · `ros2_ws` 와 build/install/log · `~/.cache` · Downloads · `~/bags` · `~/rosbag2` · `/opt/ros`)의 `du -sm`(있는 것만) ③ `/var/log` 의 5 MB 넘는 파일 상위 15 ④ logrotate timer enabled/active · `list-timers` · cron.daily · `/var/lib/logrotate/status` 의 syslog 줄 · `/etc/logrotate.d/rsyslog` 앞 20 줄 · `journalctl --disk-usage` ⑤ `/tmp` 상위 20 · 패턴별(bag_* · *.tgz · job* · run_* · *.log …) 개수 · 합계 ⑥ `~/.ros/log` 항목 수 · 가장 오래된/최신 · 월별 · 20 MB 넘는 파일 ⑦ `docker system df` · 컨테이너 · 이미지 ⑧ 홈 · `/var` · `/opt` · `/usr/local` 의 100 MB 넘는 파일 25 ⑨ 홈 · `/tmp` · `/var/tmp` 의 `*.db3` · `*.mcap` · `metadata.yaml` 을 디렉터리별 합계.
- 출력: [`j430_disk.txt`](../debug_log/2026-09-18/outputs/j430_disk.txt)(117 줄). 쓰인 곳: §8.1 표 대부분.
- 결함: ② 는 목록에 없는 곳(예: `/usr/local/lib/ollama`)을 못 봄 → ⑧ 의 큰 파일로만 드러남(ollama '≈3.7 GB' 는 ⑧ 의 파일 몇 개를 보고 잡은 값으로 보이며 디렉터리 합계 측정은 없음 — **추정**). ④ 는 `logrotate.timer` 유닛이 아예 없다는 오류 문구를 그대로 찍음 → 미설치 확인은 `job430b`. ⑥ 의 '디렉터리 9746 개' 라벨 오류(§5).
- 지금 다시: 쓸 수 있음(읽기 전용). 비교용으로 같은 목록을 다시 돌리면 증가량을 볼 수 있다.

### job430b_logs.sh — logrotate 실체 · ROS 로그 구성 (09-18, 읽기 전용)
- 하는 일: `dpkg -l logrotate` · 바이너리 · cron.daily · systemd timer/service · `/var/lib/logrotate/` 존재 확인 → `/var/log` 파일 수 · 회전본(`*.1` · `*.gz`) 수 → syslog · kern.log · auth.log 크기 → lastlog 실제 사용(`du -k`) vs 겉보기(`stat -c %s`) → `~/.ros/log` 항목 · 파일 · 디렉터리 수 · 합계, 파일 이름에서 PID · 시각을 떼어 프로그램별 개수, 최근 7 일 · 30 일 넘은 파일 수와 크기.
- 출력: [`j430b_logs.txt`](../debug_log/2026-09-18/outputs/j430b_logs.txt)(28 줄). 쓰인 곳: '**logrotate 패키지 미설치**' 판정 · lastlog 희소 파일 · `~/.ros/log` 표.
- 결함: 없음(확인형). 지금 다시: 쓸 수 있음.

### job430c_talkers.sh — syslog 를 채우는 것 (09-18, 읽기 전용, sudo 없음)
- 하는 일: syslog 의 `Sep 1~18` 줄을 날짜별 줄 수 · 바이트(줄 길이 + 1)로 합산 → 9/17 하루를 프로그램 이름(PID · 콜론 제거)별 줄 · MB 상위 12 → 9/17 메시지에서 PID · 숫자를 `N` 으로 바꿔 110 자로 자른 뒤 같은 문구 상위 8.
- 출력: [`j430c_talkers.txt`](../debug_log/2026-09-18/outputs/j430c_talkers.txt)(33 줄). 쓰인 곳: '7~10 MB/일 → 1~2 MB/일, 감소 = mavlink-router 끔' · 현재 주 발생원 3 개.
- 결함: NTP 전 시각 줄(재부팅 직후)은 엉뚱한 날짜에 합산될 수 있다(예: 09-18 부팅 줄이 `Sep 17 16:37` 로 찍힘 — [Jetson Wi-Fi §5.1 모순 3](jetson-wifi-link.md)). 하루 크기 비교엔 영향 작음(부팅 몇 분치).
- 지금 다시: 날짜 정규식만 바꿔 쓸 수 있음.

## 9. 용어
- **logrotate**: 로그 파일을 주기적으로 이름을 바꿔(`syslog` → `syslog.1` → `syslog.2.gz` …) 일정 개수만 남기는 도구. 설정(`/etc/logrotate.d/rsyslog`: 주 1 회 · 4 개 · 압축)이 있어도 **실행 주체(logrotate 패키지의 cron 작업 또는 systemd timer)** 가 없으면 아무 일도 안 일어난다 — 이 Jetson 이 그 상태였다.
- **rsyslog**: syslog 줄을 받아 규칙대로 파일에 쓰는 데몬. `/var/log/syslog` · kern.log · auth.log 를 쓴다. 파일을 옮긴 뒤에는 HUP 신호로 새 파일을 열게 해야 한다(wifi-mon 의 회전이 `pkill -HUP rsyslogd` 를 하는 이유).
- **희소 파일(sparse file)**: 겉보기 크기는 크지만 실제로 디스크 블록을 쓴 부분만 차지하는 파일. `/var/log/lastlog` 는 사용자 번호(UID)로 위치를 잡아 기록하므로 큰 UID 가 하나 있으면 겉보기 크기만 커진다 — `ls`/`stat` 은 173 MB, `du` 는 16 KB.
- **snap 리비전**: Ubuntu 의 snap 패키지는 갱신해도 옛 리비전을 몇 개 남겨 되돌릴 수 있게 한다(`/var/lib/snapd/snaps/*.snap` + 같은 크기의 cache). gnome · mesa · chromium 이 그래서 2 벌씩 보인다.
- **`~/.ros/log`**: ROS 2 노드 · launch 가 실행마다 남기는 로그(노드당 파일 · launch 당 디렉터리). 자동 삭제가 없다.
- **세션 스크래치패드**: Claude Code 세션마다 생기는 PC 의 임시 작업 폴더. 09-18 까지 러너 · bag 사본이 여기에 쌓였고, 09-28 에 오래된 세션 폴더가 통째로 사라졌다 — 영구 보관소가 아니다.
