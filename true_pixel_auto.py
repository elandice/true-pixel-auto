"""true-pixel-auto: AI가 만든 가짜 픽셀 아트를 진짜 도트(인덱스 PNG)로 변환.

인자 없이 실행하면 MCP(stdio) 서버, 인자가 있으면 CLI:
    python true_pixel_auto.py input.png --width 64 --height 64 --colors 16 [--upscale 8]
"""
import argparse
import os
import sys

import numpy as np
from mcp.server.mcpserver import MCPServer  # mcp 2.x에서 FastMCP가 MCPServer로 이름 변경됨
from mcp.server.mcpserver.exceptions import ToolError
from PIL import Image
from sklearn.cluster import KMeans

mcp = MCPServer("true-pixel-auto")


def process_pixel_art(image_path, target_width=64, target_height=64, n_colors=16, upscale_factor=1):
    """변환 후 (저장된 경로 리스트, 실제 사용 색상 수)를 반환."""
    img = np.asarray(Image.open(image_path).convert("RGB"))
    orig_h, orig_w, _ = img.shape
    if not (1 <= target_width <= orig_w and 1 <= target_height <= orig_h):
        raise ValueError(f"목표 해상도 {target_width}x{target_height}는 1 이상, 원본 {orig_w}x{orig_h} 이하여야 합니다")
    if not 1 <= n_colors <= 256:
        raise ValueError("n_colors는 1~256 범위여야 합니다 (인덱스 PNG 한계)")
    if upscale_factor < 1:
        raise ValueError("upscale_factor는 1 이상이어야 합니다")

    # 1. K-Means 팔레트를 먼저 학습: 노이즈 낀 RGB 대신 팔레트 인덱스의 최빈값을 쓰면 블록에 없는 색이 섞여 나오지 않음
    pixels = img.reshape(-1, 3).astype(np.float32)
    sample = pixels[np.random.default_rng(42).choice(len(pixels), min(len(pixels), 20000), replace=False)]
    k = min(n_colors, len(np.unique(sample, axis=0)))
    kmeans = KMeans(n_clusters=k, random_state=42, n_init="auto").fit(sample)
    labels = kmeans.predict(pixels).reshape(orig_h, orig_w)

    # 2. 격자 블록마다 최빈 팔레트 인덱스(Mode)로 다운스케일 → 경계 안티에일리어싱 제거
    ys = np.linspace(0, orig_h, target_height + 1).astype(int)
    xs = np.linspace(0, orig_w, target_width + 1).astype(int)
    grid = np.empty((target_height, target_width), dtype=np.int64)
    for i in range(target_height):
        for j in range(target_width):
            grid[i, j] = np.bincount(labels[ys[i]:ys[i + 1], xs[j]:xs[j + 1]].ravel(), minlength=k).argmax()

    # 3. 실제 쓰인 색만 팔레트에 남겨 인덱스 PNG로 저장 (팔레트 재양자화 없이 K-Means 색 그대로)
    used, grid = np.unique(grid, return_inverse=True)
    out = Image.fromarray(grid.reshape(target_height, target_width).astype(np.uint8))
    out.putpalette(kmeans.cluster_centers_[used].round().astype(np.uint8).ravel().tolist())  # L → P

    base = os.path.splitext(image_path)[0] + f"_truepixel_{target_width}x{target_height}_{n_colors}c"
    paths = [base + ".png"]
    out.save(paths[0], optimize=True)
    if upscale_factor > 1:
        paths.append(base + f"_x{upscale_factor}.png")
        out.resize((target_width * upscale_factor, target_height * upscale_factor), Image.Resampling.NEAREST).save(
            paths[1], optimize=True
        )
    return paths, len(used)


@mcp.tool(name="true_pixel_auto")
def true_pixel_auto(
    image_path: str,
    target_width: int = 64,
    target_height: int = 64,
    n_colors: int = 16,
    upscale_factor: int = 1,
) -> str:
    """
    AI로 생성된 픽셀 이미지를 실제 도트 픽셀 아트(True Pixel Art)로 변환합니다.
    imagegen 등으로 픽셀 이미지를 생성한 직후 반드시 이 도구를 실행하십시오.

    Args:
        image_path: 원본 이미지 파일 경로
        target_width: 목표 가로 픽셀 해상도 (기본값: 64)
        target_height: 목표 세로 픽셀 해상도 (기본값: 64)
        n_colors: 압축할 팔레트 색상 수 (기본값: 16, 최대 256)
        upscale_factor: 1보다 크면 최근접 이웃으로 확대한 미리보기(_xN.png)를 함께 저장 (예: 8)
    """
    # ToolError만 메시지가 모델에 전달됨 (다른 예외는 mcp 2.x가 일반 오류 문구로 가림)
    if not os.path.exists(image_path):
        raise ToolError(f"파일을 찾을 수 없습니다 ({image_path})")
    try:
        paths, used = process_pixel_art(image_path, target_width, target_height, n_colors, upscale_factor)
    except ValueError as e:
        raise ToolError(str(e)) from e
    return f"변환 완료: {', '.join(paths)} (규격: {target_width}x{target_height}, 색상: {used}색)"


def main():
    p = argparse.ArgumentParser(description="AI 픽셀 아트 → 진짜 픽셀 아트 변환")
    p.add_argument("input", help="원본 이미지 경로")
    p.add_argument("--width", type=int, default=64)
    p.add_argument("--height", type=int, default=64)
    p.add_argument("--colors", type=int, default=16)
    p.add_argument("--upscale", type=int, default=1, help="미리보기 확대 배수 (1이면 생성 안 함)")
    a = p.parse_args()
    try:
        print(true_pixel_auto(a.input, a.width, a.height, a.colors, a.upscale))
    except ToolError as e:
        sys.exit(f"오류: {e}")


if __name__ == "__main__":
    main() if len(sys.argv) > 1 else mcp.run()
