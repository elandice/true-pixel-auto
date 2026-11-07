# Project Instructions: true-pixel-auto (Codex)

당신은 픽셀 아트 생성 및 정제 파이프라인(`true-pixel-auto`)이 활성화된 에이전트입니다.

## 핵심 작동 규칙 (자동 연계)
1. 사용자가 픽셀 아트, 도트 이미지, 게임 스프라이트 생성을 요청할 경우:
   - **Step 1**: `imagegen` 스킬의 내장 `image_gen` 도구로 기본 이미지를 생성합니다. 프롬프트에 `pixel art sprite, crisp edges` 키워드와, 배경은 사용자가 원하면 `transparent background` 아니면 `flat solid background`를 자동 보강하십시오. 투명 배경은 정제 후에도 유지됩니다.
   - **Step 2**: 이미지가 `$CODEX_HOME/generated_images/.../*.png`에 저장되면, **사용자에게 중간 결과를 보고하지 말고 즉시** 그 경로로 `true_pixel_auto` MCP 도구(또는 아래 로컬 CLI)를 호출하여 이미지를 정제하십시오.
   - **Step 3**: 정제 결과(`*_truepixel_<W>x<H>_<N>c.png`, 미리보기 요청 시 `*_xN.png`)는 원본과 같은 `generated_images` 폴더에 생성됩니다. 이를 현재 작업 폴더(사용자가 위치를 지정하면 그곳)로 복사한 뒤, 복사된 최종 경로와 적용된 규격(해상도, 색상 수)만 사용자에게 안내하십시오.
2. 사용자가 기존 이미지 파일의 정제를 요청하면 Step 2부터 수행합니다 (결과는 입력 파일 옆에 생성되므로 복사 불필요).

## 기본 파라미터 규격
사용자가 별도로 지정하지 않은 경우 아래 기본값을 적용합니다:
- `target_width`: 64
- `target_height`: 64
  - 원본이 정사각형이 아니면 긴 변을 64로 두고 짧은 변은 원본 비율에 맞추십시오 (예: 1825×862 → 64×30).
  - 여러 프레임을 나열한 스프라이트 시트라면 프레임 하나당 64를 기준으로 잡으십시오 (예: 가로 5프레임 1825×862 → 320×151).
- `n_colors`: 16
- `upscale_factor`: 1 (미리보기 요청 시 8 → `_x8.png` 미리보기가 원본 도트 파일과 함께 생성됨)

## 로컬 CLI 실행 명령어 (MCP 미사용 시)
- `.venv/Scripts/python.exe true_pixel_auto.py <input_path> --width 64 --height 64 --colors 16 [--upscale 8]`

## 개발
- 의존성 설치: `python -m venv .venv` 후 `.venv/Scripts/python.exe -m pip install -r requirements.txt`
- 테스트: `.venv/Scripts/python.exe test_true_pixel_auto.py`
- MCP 서버는 `~/.codex/config.toml`의 `[mcp_servers.true-pixel-auto]`에 절대 경로로 등록되어 있음. 폴더를 옮기면 다시 등록해야 함.
