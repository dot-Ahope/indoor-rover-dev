# Rover 펌웨어 — 빌드 & 플래시 가이드

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-003 |
| 대상 H/W | STM32F405RGT6 / ALOPS Jupiter R1.4 |
| 대상 독자 | 저장소를 처음 받아서 빌드·플래시까지 진행하려는 개발자 |
| 검증 환경 | Windows 11 + PowerShell, STM32CubeCLT 1.21.0 |

> 이 문서는 git 저장소를 처음 clone 받은 상태에서 보드에 펌웨어를 굽고 동작 확인까지 하는 전체 절차를 정리합니다.
> Linux/Mac에서도 동일한 절차로 진행 가능하며, 차이점은 본문 중간중간 박스로 표시했습니다.

---

## 1. 사전 준비

### 1.1 하드웨어

- **ALOPS Jupiter R1.4** 보드 (STM32F405RGT6, VCAP 핸드리워크 적용본)
- **ST-Link V2 / V3** 프로그래머 (SWD)
- USB-Serial 연결:
  - **CH340N (보드 내장)** → USART1 (Jetson 통신, 921600 bps) — 윈도우에선 `USB-SERIAL CH340`로 잡힙니다
  - **ST-Link VCP** → UART5 디버그 콘솔 (115200 bps) — ST-Link V3SET 사용 시 보조 VCP가 UART5에 연결
- 5V/12V 전원 (모터 구동 시)

### 1.2 소프트웨어

| 도구 | 용도 | 다운로드 |
|---|---|---|
| **STM32CubeCLT** ≥ 1.21 | ARM GCC 툴체인 + `STM32_Programmer_CLI` + ST-Link 드라이버 한 번에 설치 | https://www.st.com/en/development-tools/stm32cubeclt.html |
| **GNU Make** | Makefile 빌드 | Windows: [GnuWin32 make](https://gnuwin32.sourceforge.net/packages/make.htm) <br> Linux: `sudo apt install make` <br> macOS: 기본 설치됨 |
| **Git** | 저장소 clone | https://git-scm.com/ |
| (선택) **STM32CubeMX** | `.ioc` 파일 편집 (핀맵 변경 시) | https://www.st.com/en/development-tools/stm32cubemx.html |
| (선택) **시리얼 터미널** | UART5 콘솔 모니터링 | PuTTY / Tera Term / VS Code Serial Monitor |

> **STM32CubeCLT 한 방의 이점**: `arm-none-eabi-gcc`, `STM32_Programmer_CLI`, ST-Link USB 드라이버가 모두 포함됩니다. 별도 설치 불필요.

### 1.3 설치 확인

새 PowerShell 창을 열어 (PATH가 자동으로 잡혔다면) 다음 명령이 동작해야 합니다.

```powershell
arm-none-eabi-gcc --version    # 14.x 이상
make --version                  # GNU Make 3.81+
STM32_Programmer_CLI --version  # 2.22+
git --version
```

전부 안 잡혀도 정상입니다 — 아래 §3에서 PATH를 잡습니다.

---

## 2. 저장소 받기

```powershell
cd C:\Project\Rover
git clone <repo-url> Rover
cd Rover
```

> Linux/Mac 사용자: `cd ~/projects && git clone <repo-url> rover && cd rover`

### 디렉토리 구조 (빌드에 필요한 부분만)

```
Rover/
├── CLAUDE.md                          작업 지침
├── PROJECT_OVERVIEW.md                프로젝트 전반
├── Docs/                              모든 문서
│   ├── BUILD_AND_FLASH_GUIDE.md       (이 문서)
│   ├── FIRMWARE_DEV_PLAN.md           F0~F8 단계 정의
│   └── F0_CUBEMX_SETUP.md ~ F8_*.md   단계별 검증
└── firmware/
    └── rover_jupiter_fw/              ★ 빌드 대상
        ├── Makefile                   CubeMX 생성 Makefile
        ├── rover_jupiter_fw.ioc       CubeMX 프로젝트
        ├── STM32F405XX_FLASH.ld       링커 스크립트
        ├── startup_stm32f405xx.s
        ├── Core/                      애플리케이션 + CubeMX 생성 코드
        ├── App/                       우리 코드 (hal/drivers/app)
        ├── Drivers/                   STM32 HAL
        └── Middlewares/               FreeRTOS, micro-ROS (F5 이후)
```

---

## 3. 환경 설정 — PATH

### 3.1 Windows — 임시 (현재 PowerShell 창에서만)

```powershell
$env:Path = "C:\ST\STM32CubeCLT_1.21.0\GNU-tools-for-STM32\bin;" +
            "C:\ST\STM32CubeCLT_1.21.0\STM32CubeProgrammer\bin;" +
            "C:\Program Files (x86)\GnuWin32\bin;" + $env:Path
```

> STM32CubeCLT 설치 경로 (`C:\ST\STM32CubeCLT_*`) 는 설치 버전에 따라 다릅니다. `Get-ChildItem C:\ST\` 로 실제 경로를 먼저 확인하세요.

### 3.2 Windows — 영구 (PowerShell 프로필에 박기)

PowerShell 프로필은 셸 시작 시 자동 실행되는 스크립트 파일입니다.

#### (1) ExecutionPolicy 확인 — 한 번만

```powershell
Get-ExecutionPolicy -Scope CurrentUser
```

`Restricted` / `Undefined` 면 풀어줍니다 (본인이 만든 로컬 스크립트만 자유 실행, 인터넷 스크립트는 서명 요구 — 안전한 설정):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

#### (2) 프로필 파일 생성 후 열기

```powershell
if (!(Test-Path $PROFILE)) { New-Item -ItemType File -Path $PROFILE -Force }
notepad $PROFILE
```

#### (3) 아래 내용을 붙여넣고 저장

```powershell
# Rover 펌웨어 툴체인 PATH
$env:Path = "C:\ST\STM32CubeCLT_1.21.0\GNU-tools-for-STM32\bin;" +
            "C:\ST\STM32CubeCLT_1.21.0\STM32CubeProgrammer\bin;" +
            "C:\Program Files (x86)\GnuWin32\bin;" + $env:Path

# 한 줄 빌드/플래시 단축 함수
$FW_DIR = "C:\Project\Rover\Rover\firmware\rover_jupiter_fw"

function fw-build  { make -C $FW_DIR -j8 }
function fw-clean  { make -C $FW_DIR clean }
function fw-flash {
  fw-build
  if ($LASTEXITCODE -eq 0) {
    STM32_Programmer_CLI -c port=SWD reset=HWrst `
      -w "$FW_DIR\build\rover_jupiter_fw.elf" -rst
  }
}
```

#### (4) 적용

새 PowerShell 창을 열거나 현재 창에서 `. $PROFILE` 실행.

#### (5) 동작 확인

```powershell
arm-none-eabi-gcc --version
make --version
STM32_Programmer_CLI --list
```

### 3.3 Linux / macOS

`~/.bashrc` (또는 `~/.zshrc`) 끝에:

```bash
export PATH="/opt/st/stm32cubeclt_1.21.0/GNU-tools-for-STM32/bin:$PATH"
export PATH="/opt/st/stm32cubeclt_1.21.0/STM32CubeProgrammer/bin:$PATH"

FW_DIR="$HOME/projects/rover/firmware/rover_jupiter_fw"

fw-build() { make -C "$FW_DIR" -j$(nproc); }
fw-clean() { make -C "$FW_DIR" clean; }
fw-flash() {
  fw-build && \
  STM32_Programmer_CLI -c port=SWD reset=HWrst \
    -w "$FW_DIR/build/rover_jupiter_fw.elf" -rst
}
```

적용: `source ~/.bashrc`

---

## 4. 빌드

작업 디렉토리는 저장소 루트 (`Rover/`).

### 4.1 기본 빌드

```powershell
make -C firmware\rover_jupiter_fw -j8
```

- `-j8`: 병렬 컴파일 워커 수 (CPU 코어에 맞춰 4~16)
- 첫 빌드는 ~30초, 이후 증분 빌드는 1~2초

### 4.2 클린 / 재빌드

```powershell
make -C firmware\rover_jupiter_fw clean              # build/ 디렉토리 삭제
make -C firmware\rover_jupiter_fw clean ; make -C firmware\rover_jupiter_fw -j8   # 클린 빌드
```

### 4.3 산출물

```
firmware/rover_jupiter_fw/build/
├── rover_jupiter_fw.elf    ★ 플래시 권장 (디버그 정보 포함, 주소 자동 추출)
├── rover_jupiter_fw.hex    Intel HEX (옵션)
├── rover_jupiter_fw.bin    Raw 바이너리 (옵션)
└── rover_jupiter_fw.map    메모리 맵 (size 분석용)
```

### 4.4 빌드 성공 확인

마지막에 다음과 같은 size 요약이 나오면 OK:

```
arm-none-eabi-size build/rover_jupiter_fw.elf
   text    data     bss     dec     hex filename
  25916     108   71956   97980   17ebc build/rover_jupiter_fw.elf
```

| 항목 | 의미 | F405 한계 |
|---|---|---|
| `text` | 코드 + 상수 | Flash 1024 KB |
| `data` | 초기값 있는 변수 | RAM (Flash → RAM 복사) |
| `bss` | 0 초기화 변수 | RAM 128 KB (메인 SRAM) |

→ 위 예시는 Flash 2.5%, RAM 56% 사용. F5 micro-ROS 단계까지 진행해도 여유 충분.

> 단축 함수를 등록했다면: `fw-build`

---

## 5. ST-Link 플래시

### 5.1 보드 연결

1. ST-Link를 보드 SWD 헤더에 연결 (SWDIO=PA13, SWCLK=PA14, GND, 3V3)
2. 보드에 별도 전원 연결 (USB 또는 외부)
3. ST-Link를 PC USB에 연결
4. 인식 확인:

```powershell
STM32_Programmer_CLI --list
```

다음과 같이 ST-LINK가 나와야 합니다:

```
ST-Link Probe 0 :
   ST-LINK SN  : 00510025...
   ST-LINK FW  : V3J17M10B6S1
   Board Name  : STLINK-V3SET
```

### 5.2 플래시 명령

```powershell
STM32_Programmer_CLI -c port=SWD reset=HWrst -w firmware\rover_jupiter_fw\build\rover_jupiter_fw.elf -v -rst
```

#### 옵션 의미

| 플래그 | 뜻 |
|---|---|
| `-c port=SWD` | SWD 인터페이스로 접속 |
| `reset=HWrst` | NRST 핀으로 하드웨어 리셋 후 attach (안전) |
| `-w <파일>` | write (자동 erase + program). `.elf` 권장 — 주소 자동 |
| `-v` | 다운로드 후 verify (선택, 약간 시간 추가) |
| `-rst` | 프로그래밍 끝나면 software reset → 즉시 실행 |

#### 성공 출력 예시

```
Voltage     : 3.29V
Device ID   : 0x413
Device name : STM32F405xx/F407xx/F415xx/F417xx
Download in Progress: 100%
File download complete
Download verified successfully
MCU Reset
Software reset is performed
```

> 단축 함수를 등록했다면: `fw-flash` (빌드 → 플래시 한 방)

### 5.3 추가 명령 (필요 시)

```powershell
# 보드 완전 erase
STM32_Programmer_CLI -c port=SWD -e all

# Flash 영역 덤프 (디버깅용)
STM32_Programmer_CLI -c port=SWD -r 0x08000000 1024 dump.bin

# Read protection 설정 (양산 시)
STM32_Programmer_CLI -c port=SWD -ob RDP=0xBB
```

---

## 6. 동작 확인

### 6.1 LED · 부저 (육안 / 청각)

- **PC13 상태 LED**: 0.5초 주기 토글 (1Hz 깜박)
- **PB1 능동 부저**: 0.5초 주기 on/off (1Hz 삑-삑)

둘 다 안 되면 §8 트러블슈팅 참조.

### 6.2 UART5 디버그 콘솔

ST-Link V3SET의 보조 VCP가 UART5에 연결되어 있습니다. Windows에서 일반적으로 `COM8` 또는 `COM9` 로 잡힙니다.

#### COM 포트 확인

```powershell
STM32_Programmer_CLI --list
```

출력 중 ST-Link 두 VCP가 보입니다. **두 번째 포트**가 UART5입니다 (첫 번째는 ST-Link 메인 VCP):

```
Port: COM8 ... STLink Virtual COM Port 2     ← 이게 UART5
Port: COM9 ... STLink Virtual COM Port        ← ST-Link 메인 (사용 안 함)
```

> 환경에 따라 번호가 다를 수 있으니 직접 확인 필요. 보드 USB-CH340 (USART1, Jetson용)은 `USB-SERIAL CH340`로 별도 표시됩니다.

#### 시리얼 모니터링 (PuTTY / Tera Term / VS Code)

설정: `115200 8-N-1`, 흐름제어 없음.

#### PowerShell만으로 모니터링

```powershell
$p = [System.IO.Ports.SerialPort]::new('COM9',115200,'None',8,'One')
$p.Open()
try {
  while ($true) {
    $c = $p.ReadExisting()
    if ($c) { Write-Host -NoNewline $c } else { Start-Sleep -Milliseconds 50 }
  }
} finally { $p.Close() }
```

(Ctrl+C로 종료)

#### 기대 출력

리셋 직후:

```
=========================================
 Rover Jupiter F405 - F0 boot OK
 SYSCLK=168MHz  build=Jun 16 2026 11:23:45
=========================================
[hb 0] tick=0  freeHeap=63760  minEverHeap=63760
[hb 1] tick=1004  freeHeap=63760  minEverHeap=63760
[hb 2] tick=2009  freeHeap=63760  minEverHeap=63760
...
```

- 부팅 배너가 정확히 1회 출력 → **부팅 OK**
- `[hb N]` 1초 주기 출력 → **FreeRTOS 스케줄링 동작**
- `tick=` 증가량이 약 1005 → **1ms tick 정확**
- `freeHeap` 안정 → **메모리 누수 없음**

### 6.3 micro-ROS (F5 이후 단계)

F5 단계 이후 펌웨어가 올라가면 USART1 (`COM19` 기준 CH340) 으로 micro-ROS XRCE-DDS 통신이 시작됩니다. 검증 방법은 [`F5b_VERIFICATION.md`](F5b_VERIFICATION.md) 참조.

---

## 7. 일상 작업 흐름

```powershell
# 코드 수정 후
fw-flash

# 빌드만
fw-build

# 깨끗하게 다시
fw-clean ; fw-build

# 동작 확인
# (시리얼 모니터를 별도 창에 열어두고 fw-flash 하면 리셋 직후 부팅 배너가 보입니다)
```

---

## 8. 트러블슈팅

### `make: command not found` / `arm-none-eabi-gcc: command not found`

→ PATH 미설정. §3 다시 진행. 새 셸 창을 열어야 적용됩니다.

### `STM32_Programmer_CLI: command not found`

→ STM32CubeCLT 미설치 또는 PATH 미설정. 설치 경로 확인:

```powershell
Get-ChildItem 'C:\ST\STM32CubeCLT_*' -Directory
```

### `No STLink probe found` / `Error: Connection failed`

1. ST-Link USB 케이블 분리 후 재연결
2. 보드 전원 공급 확인 (`Voltage` 가 0V로 나오면 보드 전원 없음)
3. SWD 핀 연결 확인 (SWDIO / SWCLK / GND, 최소 3선)
4. 다른 IDE (STM32CubeIDE, STM32CubeProgrammer GUI) 가 같은 ST-Link를 점유 중이면 종료
5. 윈도우 장치관리자에서 ST-Link 드라이버 확인 (STM32CubeCLT 설치 시 자동 설치됨)

### `cannot enter debug mode` / `Cannot read register`

- 펌웨어가 SWD 핀을 GPIO로 재설정한 경우 발생할 수 있습니다 (F1 단계 핀 충돌)
- 해결: 보드 BOOT0 핀을 high로 당기고 리셋 → 시스템 부트로더 모드로 진입 후 재플래시
- 또는 `reset=HWrst` 옵션과 함께 NRST 핀을 ST-Link로 연결 (V3SET은 자동)

### PowerShell 프로필이 실행 안 됨

```
. : 이 시스템에서 스크립트를 실행할 수 없으므로 ...
```

→ §3.2 (1) ExecutionPolicy 설정.

### 빌드는 되는데 RAM/Flash 부족

```
region `RAM' overflowed by NN bytes
```

→ `STM32F405XX_FLASH.ld` 의 메모리 영역 확인. F405는 메인 SRAM 128KB + CCM 64KB. CCM은 DMA 불가하지만 일반 변수·스택용으로 활용 가능 (`__attribute__((section(".ccmram")))`).

### 시리얼 모니터에 한글 깨짐 / 출력 이상

- 보드레이트 확인 (UART5 = **115200**, USART1 = **921600** or **2000000**)
- 라인엔딩: `\r\n` 또는 `\n` (현재 펌웨어는 `\r\n` 출력)
- ST-Link FW 가 너무 오래된 경우 VCP 가 일부 baudrate 미지원 — STM32CubeProgrammer GUI 의 Firmware upgrade 기능으로 갱신

### `make` 가 PowerShell에서 동작하지 않음 / 경로 슬래시 문제

- GnuWin32 make 는 `-C` 옵션에서 `\` (백슬래시) 와 `/` (슬래시) 모두 인식
- 그래도 문제가 생기면 슬래시로 통일: `make -C firmware/rover_jupiter_fw -j8`

---

## 9. 다음 단계

빌드/플래시가 안정적으로 동작하면 단계별 검증으로 진입:

| 단계 | 문서 | 핵심 |
|---|---|---|
| **F0** | [F0_CUBEMX_SETUP.md](F0_CUBEMX_SETUP.md) | CubeMX `.ioc` + LED/UART/부저/태스크 골격 |
| **F1** | [F1_VERIFICATION.md](F1_VERIFICATION.md) | HAL/Driver 골격 + 페리페럴 sanity |
| **F2 ~ F8** | [INDEX.md](INDEX.md) 참조 | 모터·엔코더·PID·micro-ROS·IMU·통합 |

전체 개발 로드맵은 [`FIRMWARE_DEV_PLAN.md`](FIRMWARE_DEV_PLAN.md) §6.

---

*문서 끝.*
