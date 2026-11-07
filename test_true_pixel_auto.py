"""가짜 픽셀 아트(16배 확대 + 블러 + 노이즈)를 만들어 원본 16x16 도트가 복원되는지 확인.

실행: .venv/Scripts/python.exe test_true_pixel_auto.py  (pytest로도 실행 가능)
"""
import os
import tempfile

import numpy as np
from PIL import Image, ImageFilter

from true_pixel_auto import process_pixel_art

COLORS = np.array([[0, 0, 0], [255, 255, 255], [220, 40, 40], [40, 200, 60], [40, 70, 230], [250, 220, 30]], np.uint8)


def _convert_fake(sprite, n_colors, rng, d):
    """sprite(16x16 RGB/RGBA)를 AI풍으로 망가뜨려 저장한 뒤 변환. (출력 이미지, 미리보기, 색 수) 반환."""
    fake = Image.fromarray(sprite).resize((256, 256), Image.Resampling.NEAREST).filter(ImageFilter.GaussianBlur(1.5))
    noisy = np.asarray(fake, np.int16).copy()
    noisy[..., :3] += rng.integers(-8, 9, (256, 256, 3)).astype(np.int16)
    src = os.path.join(d, "fake.png")
    Image.fromarray(np.clip(noisy, 0, 255).astype(np.uint8)).save(src)
    paths, used = process_pixel_art(src, 16, 16, n_colors, upscale_factor=8)
    out, preview = (Image.open(p).copy() for p in paths)  # copy()로 즉시 읽어 파일 잠금 해제 (Windows 임시폴더 삭제용)
    return out, preview, used


def test_restores_original_sprite():
    rng = np.random.default_rng(0)
    truth = COLORS[rng.integers(0, len(COLORS), (16, 16))]
    with tempfile.TemporaryDirectory() as d:
        out, preview, used = _convert_fake(truth, 6, rng, d)
        assert out.mode == "P" and out.size == (16, 16) and "transparency" not in out.info
        assert preview.size == (128, 128)
        assert used <= 6
        diff = np.abs(np.asarray(out.convert("RGB"), np.int16) - truth).max()
        assert diff <= 20, f"원본과 최대 색 차이 {diff}"


def test_keeps_transparency():
    rng = np.random.default_rng(1)
    truth = COLORS[rng.integers(2, len(COLORS), (16, 16))]
    mask = np.zeros((16, 16), bool)
    mask[3:13, 4:12] = True
    sprite = np.dstack([truth, np.where(mask, 255, 0).astype(np.uint8)])
    sprite[~mask, :3] = [255, 0, 255]  # 투명 영역에 숨은 색: 팔레트에 섞이면 안 됨
    with tempfile.TemporaryDirectory() as d:
        out, preview, used = _convert_fake(sprite, 4, rng, d)
        rgba = np.asarray(out.convert("RGBA"), np.int16)
        assert ((rgba[..., 3] > 0) == mask).all(), "투명 영역이 원본과 다름"
        assert np.asarray(preview.convert("RGBA"))[0, 0, 3] == 0, "미리보기도 투명해야 함"
        assert used <= 4
        diff = np.abs(rgba[mask][:, :3] - truth[mask]).max()
        assert diff <= 20, f"원본과 최대 색 차이 {diff}"


if __name__ == "__main__":
    test_restores_original_sprite()
    test_keeps_transparency()
    print("ok")
