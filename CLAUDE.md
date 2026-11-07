# Project Instructions: true-pixel-auto

당신은 픽셀 아트 생성 및 정제 파이프라인(`true-pixel-auto`)이 활성화된 에이전트입니다.

## 핵심 작동 규칙 (자동 연계)
1. 사용자가 픽셀 아트, 도트 이미지, 게임 스프라이트 생성을 요청할 경우:
   - **Step 1**: 먼저 `imagegen` 도구를 호출하여 기본 이미지를 생성합니다. (프롬프트에 `pixel art sprite, flat solid background, crisp edges` 키워드를 자동 보강하십시오.)
   - **Step 2**: `imagegen`이 이미지 경로를 반환하면, **사용자에게 중간 결과를 보고하지 말고 즉시** `true_pixel_auto` MCP 도구(또는 아래 로컬 CLI)를 호출하여 이미지를 정제하십시오.
   - **Step 3**: 정제가 완료된 최종 진성 픽셀 이미지 경로와 적용된 규격(해상도, 색상 수)만 사용자에게 안내하십시오.
2. 사용자가 기존 이미지 파일의 정제를 요청하면 Step 2부터 수행합니다.

## 기본 파라미터 규격
사용자가 별도로 지정하지 않은 경우 아래 기본값을 적용합니다:
- `target_width`: 64
- `target_height`: 64
- `n_colors`: 16
- `upscale_factor`: 1 (미리보기 요청 시 8 → `_x8.png` 미리보기가 원본 도트 파일과 함께 생성됨)

## 로컬 CLI 실행 명령어 (MCP 미사용 시)
- `.venv/Scripts/python.exe true_pixel_auto.py <input_path> --width 64 --height 64 --colors 16 [--upscale 8]`
- 결과: `<입력파일명>_truepixel_<W>x<H>_<N>c.png` (입력 파일과 같은 폴더)

## 개발
- 의존성 설치: `python -m venv .venv` 후 `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- 테스트: `.venv/Scripts/python.exe test_true_pixel_auto.py`
