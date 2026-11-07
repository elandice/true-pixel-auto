# true-pixel-auto

AI가 생성한 픽셀 아트 이미지(블러, 안티에일리어싱, 노이즈가 포함된 가짜 픽셀 아트)를 정교한 진짜 도트(True Pixel Art, 인덱스 PNG)로 변환해 주는 파이프라인 및 MCP(Model Context Protocol) 서버입니다.

---

## 주요 기능

1. **K-Means 클러스터링 기반 팔레트 추출**: 원본 이미지의 주요 색상을 추출하여 지정된 색상 수(`n_colors`)로 제한합니다.
2. **모드(Mode) 다운스케일링**: 격자 블록별 최빈 팔레트 인덱스를 추출하여 경계선 블러 및 안티에일리어싱을 깔끔하게 제거합니다.
3. **인덱스 PNG(Palette) 생성**: 실제 사용된 색상만 포함하는 최적화된 인덱스 색상 PNG를 생성합니다.
4. **미리보기 업스케일 지원**: 최근접 이웃(Nearest Neighbor) 보간법을 적용한 확대본(`_x8.png` 등)을 함께 출력할 수 있습니다.
5. **MCP 서버 및 CLI 듀얼 지원**: AI 에이전트(Claude Desktop 등) 연동용 MCP 서버와 독립 CLI 도구로 모두 활용 가능합니다.

---

## 설치 방법

```bash
# 가상환경 생성 및 활성화
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# 의존성 패키지 설치
pip install -r requirements.txt
```

---

## 사용법

### 1. CLI 실행

```bash
python true_pixel_auto.py <입력이미지경로> --width 64 --height 64 --colors 16 --upscale 8
```

#### 옵션
- `input`: 변환할 원본 이미지 파일 경로
- `--width`, `-W`: 목표 가로 해상도 (기본값: 64)
- `--height`, `-H`: 목표 세로 해상도 (기본값: 64)
- `--colors`, `-c`: 최대 팔레트 색상 수 (기본값: 16, 1~256)
- `--upscale`, `-u`: 결과 이미지 확대 배율 (기본값: 1, 예: 8 지정 시 원본 규격 파일과 함께 `_x8.png` 생성)

#### 결과 파일
입력 이미지와 동일한 디렉토리에 다음 파일들이 생성됩니다:
- `<파일명>_truepixel_<W>x<H>_<N>c.png`: 정제된 인덱스 PNG (도트 원본)
- `<파일명>_truepixel_<W>x<H>_<N>c_x<U>.png`: (옵션) 확대 미리보기 파일

---

### 2. MCP 서버 연동 (Claude Desktop 등)

`claude_desktop_config.json` 또는 프로젝트 루트의 `.mcp.json`에 등록하여 사용할 수 있습니다:

```json
{
  "mcpServers": {
    "true-pixel-auto": {
      "command": "C:/myproject/true-pixel-auto/.venv/Scripts/python.exe",
      "args": ["C:/myproject/true-pixel-auto/true_pixel_auto.py"]
    }
  }
}
```

---

## 테스트

```bash
python test_true_pixel_auto.py
```
