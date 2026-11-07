"""가짜 픽셀 아트(16배 확대 + 블러 + 노이즈)를 만들어 원본 16x16 도트가 복원되는지 확인.

실행: .venv/Scripts/python.exe test_true_pixel_auto.py  (pytest로도 실행 가능)
"""
import os
import tempfile

import numpy as np
from PIL import Image, ImageFilter

from true_pixel_auto import process_pixel_art

COLORS = np.array([[0, 0, 0], [255, 255, 255], [220, 40, 40], [40, 200, 60], [40, 70, 230], [250, 220, 30]], np.uint8)


def test_restores_original_sprite():
    rng = np.random.default_rng(0)
    truth = COLORS[rng.integers(0, len(COLORS), (16, 16))]
    fake = Image.fromarray(truth).resize((256, 256), Image.Resampling.NEAREST).filter(ImageFilter.GaussianBlur(1.5))
    noisy = np.clip(np.asarray(fake, np.int16) + rng.integers(-8, 9, (256, 256, 3)), 0, 255).astype(np.uint8)

    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "fake.png")
        Image.fromarray(noisy).save(src)
        paths, used = process_pixel_art(src, 16, 16, 6, upscale_factor=8)
        out = Image.open(paths[0])
        assert out.mode == "P" and out.size == (16, 16)
        assert Image.open(paths[1]).size == (128, 128)
        assert used <= 6
        diff = np.abs(np.asarray(out.convert("RGB"), np.int16) - truth).max()
        assert diff <= 20, f"원본과 최대 색 차이 {diff}"


if __name__ == "__main__":
    test_restores_original_sprite()
    print("ok")
