# F5a — micro-ROS 정적 라이브러리 빌드 + 펌웨어 링크

| 항목 | 값 |
|---|---|
| 문서 ID | ROVER-FW-007 |
| 단계 | F5a (펌웨어 개발 6단계 — F5 의 1/3) |
| 대상 | STM32F405 + Humble micro-ROS client |
| 목적 | libmicroros.a 빌드 + 펌웨어에 링크. 실제 micro-ROS 함수 호출은 F5b 에서 |
| 환경 | WSL2 Ubuntu-22.04 + ROS2 Humble (호스트: Windows 11) |

---

## 1. 추가/변경 사항

### 1.1 파일·디렉토리
- `firmware/rover_jupiter_fw/scripts/build_libmicroros_wsl.sh` — 라이브러리 빌드 자동화 (commit)
- `firmware/rover_jupiter_fw/Middlewares/Third_Party/micro_ros_stm32cubemx_utils/` — upstream clone (gitignored)
- `firmware/rover_jupiter_fw/Middlewares/Third_Party/micro_ros_stm32cubemx_utils/libmicroros/` — 빌드 산출물 (gitignored)
  - `libmicroros.a` — 7.4 MB 정적 라이브러리
  - `include/` — 1759 헤더 (rcl, rclc, rmw, std_msgs, geometry_msgs, sensor_msgs, nav_msgs, diagnostic_msgs, micro_ros_msgs 등)

### 1.2 Makefile 변경
```makefile
C_INCLUDES += -IMiddlewares/Third_Party/micro_ros_stm32cubemx_utils/libmicroros/include
LIBDIR     =  -LMiddlewares/Third_Party/micro_ros_stm32cubemx_utils/libmicroros
LIBS       += -lmicroros
```

### 1.3 .gitignore
- `firmware/**/micro_ros_stm32cubemx_utils/` — upstream 재현 가능
- `firmware/**/libmicroros/` — 빌드 재생성 가능

---

## 2. 빌드 환경 (1회 셋업)

### 2.1 WSL Ubuntu-22.04 distro
```powershell
wsl --install -d Ubuntu-22.04 --no-launch
```
> 기존 Ubuntu (24.04) 와 별도 — Humble 이 24.04 미지원이라 22.04 가 필수.

### 2.2 ROS2 Humble + 빌드 도구 (root 로 실행)
```powershell
wsl -d Ubuntu-22.04 -u root -- bash -c "
  apt-get update && apt-get install -y software-properties-common curl gnupg lsb-release &&
  add-apt-repository -y universe &&
  curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg &&
  echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu jammy main' > /etc/apt/sources.list.d/ros2.list &&
  apt-get update &&
  apt-get install -y ros-humble-ros-base ros-dev-tools python3-pip python3-colcon-common-extensions python3-rosdep gcc-arm-none-eabi build-essential git cmake
"
```
다운로드 약 1.5 GB. 5~10 분 소요.

### 2.3 upstream 유틸 clone (호스트 git)
```powershell
cd C:\Project\Rover\Rover\firmware\rover_jupiter_fw\Middlewares\Third_Party
git clone -b humble https://github.com/micro-ROS/micro_ros_stm32cubemx_utils.git
```

---

## 3. libmicroros.a 빌드 (반복 가능)

```powershell
wsl -d Ubuntu-22.04 -u root -- bash /mnt/c/Project/Rover/Rover/firmware/rover_jupiter_fw/scripts/build_libmicroros_wsl.sh
```

### 첫 실행 (~30 분, 약 1 GB 다운로드)
- rosdep init/update
- micro_ros_setup clone + colcon build
- create_firmware_ws (ROS2 패키지 80+ clone)
- tf2_msgs workaround clone
- 68 패키지 cross-compile (ARM Cortex-M4)
- 산출물 복사

### 재실행 (~3 분, 캐시 활용)
- 변경된 부분만 다시 빌드
- 라이브러리 재생성

### 산출물 위치
- `Middlewares/Third_Party/micro_ros_stm32cubemx_utils/libmicroros/libmicroros.a`
- `Middlewares/Third_Party/micro_ros_stm32cubemx_utils/libmicroros/include/`

### Cross-compile flags
스크립트가 `RET_CFLAGS` 로 다음을 전달:
```
-mcpu=cortex-m4 -mfloat-abi=hard -mthumb -mfpu=fpv4-sp-d16
-O2 -DSTM32F405xx -DUSE_HAL_DRIVER
-ffunction-sections -fdata-sections -DSTM32CUBEIDE
-DENOTSUP=1 -DECANCELED=1 -DEOWNERDEAD=1 -DENOTRECOVERABLE=1
```
펌웨어 Makefile 의 CFLAGS 와 일치 (Og→O2 만 차이, lib 는 사이즈 우선).

---

## 4. 펌웨어 빌드 검증

```powershell
cd C:\Project\Rover\Rover\firmware\rover_jupiter_fw
make
```

### 기대 결과
- 빌드 성공 (warning·error 없음)
- 크기 변동 없음 — F4 빌드 32700 byte = F5a 빌드 32700 byte
  - `--gc-sections` 가 unused micro-ROS 코드 모두 제거
- 보드에 플래시 시 F4 와 동일하게 동작 (실제 micro-ROS 호출 없음)

---

## 5. F5a 완료 기준 (DoD)

- [x] WSL Ubuntu-22.04 distro 셋업, ROS2 Humble 설치 완료
- [x] `build_libmicroros_wsl.sh` 로 `libmicroros.a` 생성 (7.4 MB)
- [x] 1759 헤더 추출
- [x] Makefile 에 include path + `-lmicroros` 추가
- [x] 펌웨어 결합 빌드 성공
- [x] 크기 변동 없음 (gc-sections OK)
- [ ] 플래시 후 F4 와 동일 동작 (사용자 실측 — 선택. 코드 무변경이므로 자동 통과)

→ F5b 진행: transport hook (UART1 + DMA) + executor task + agent 연결 확인.

---

## 6. 알려진 한계 / 주의사항

- **헤더 1759개 = 인클루드 검색 시간 증가**: 펌웨어 빌드 시간 +수 초. CCache 사용 검토 가능.
- **micro_ros_stm32cubemx_utils 디렉토리 = upstream**: 우리가 추가한 `extra_packages/` 같은 게 들어가면 그 파일은 commit 안 됨. 향후 custom msg 추가 시 별도 디렉토리(microros_component/) 사용.
- **빌드 캐시는 WSL 내부 `~/microros_build/`**: WSL distro 삭제 시 캐시 손실. 다시 30분 빌드.
- **메모리 제약 미반영**: F5b 에서 micro-ROS executor·publisher allocate 시 FreeRTOS heap 32KB → 48~64KB 상향 필요 가능. CubeMX `.ioc` 수정 또는 `FreeRTOSConfig.h` 수동 수정.
- **Tf2_msgs workaround**: micro_ros_setup 기본 패키지에 없어서 git clone 으로 추가. 빌드 스크립트에 포함됨.

---

*문서 끝.*
