# firmware/ — STM32F405 펌웨어

`firmware/` 는 펌웨어 프로젝트들의 컨테이너. 현재는 dev 보드용
`rover_jupiter_fw/` 하나. 다른 보드용 펌웨어가 생기면 이 아래에 나란히 추가한다.

## 디렉토리 구조

```
firmware/
└── rover_jupiter_fw/          STM32F405 CubeMX 프로젝트 (= 펌웨어 루트)
    ├── rover_jupiter_fw.ioc   CubeMX 설정 (★커밋 대상)
    ├── Makefile               빌드 (CubeMX 생성)
    ├── STM32F405XX_FLASH.ld   링커 스크립트
    ├── startup_stm32f405xx.s  스타트업 코드
    ├── App/                   ← 우리가 작성하는 코드
    │   ├── app/               App Layer (미션·안전·제어)
    │   ├── hal/               HAL 추상화 인터페이스
    │   ├── drivers/           저수준 드라이버
    │   └── microros/          micro-ROS 통합
    ├── Core/                  ┐ CubeMX 자동 생성
    ├── Drivers/               │ (STM32 HAL, CMSIS)
    └── Middlewares/           ┘ (FreeRTOS)
```

## 규칙

- CubeMX 생성 파일(`Core/`, `Drivers/`, `Middlewares/`)은
  **`USER CODE BEGIN/END` 블록 안에만** 수정
- 우리 모듈은 전부 `rover_jupiter_fw/App/` 에 작성하고,
  `Makefile`의 `C_SOURCES`/`C_INCLUDES`에 추가
- CubeMX를 다시 생성해도 `App/` 는 안전 (CubeMX가 모르는 폴더)
- `rover_jupiter_fw.ioc` 는 반드시 커밋
- `.mxproject`·빌드 산출물은 Git 제외 (루트 `.gitignore`)

## 시작

`docs/F0_CUBEMX_SETUP.md` 체크리스트 참조. 전체 계획은 `docs/FIRMWARE_DEV_PLAN.md`.
