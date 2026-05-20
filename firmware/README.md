# firmware/ — STM32F405 펌웨어

## 디렉토리 구조

```
firmware/
├── ROVER_F405.ioc        CubeMX 설정 (★커밋 대상)
├── Makefile              ┐
├── Core/                 │ CubeMX 자동 생성
├── Drivers/              │ (STM32 HAL, CMSIS)
├── Middlewares/          ┘ (FreeRTOS)
├── App/                  ← 우리가 작성하는 코드
│   ├── app/              App Layer (미션·안전·제어)
│   ├── hal/              HAL 추상화 인터페이스
│   ├── drivers/          저수준 드라이버
│   └── microros/         micro-ROS 통합
└── build/                빌드 산출물 (Git 제외)
```

## 규칙

- CubeMX 생성 파일(`Core/`, `Drivers/`)은 **`USER CODE BEGIN/END` 블록 안에만** 수정
- 우리 모듈은 전부 `App/` 에 작성하고, Makefile의 `C_SOURCES` / `C_INCLUDES`에 추가
- 이렇게 하면 CubeMX를 다시 생성해도 `App/` 코드는 안전
- `ROVER_F405.ioc` 는 반드시 커밋 (CubeMX 설정 원본)

## 시작

`docs/F0_CUBEMX_SETUP.md` 체크리스트대로 CubeMX 프로젝트를 이 폴더에 생성.
전체 계획은 `docs/FIRMWARE_DEV_PLAN.md`.
