#!/usr/bin/env python3
"""
Prepare a portrait photo for clean ASCII conversion:
  1. Remove background (rembg) so the subject is isolated
  2. Bilateral-smooth away noise and texture while keeping sharp drawn edges
  3. Stretch tones so skin lands near bright/white and hair/lines stay dark
  4. Darken linework (difference-of-gaussians ridges) for better ASCII contrast
  5. Composite onto white and crop square around the subject

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.

Usage:
    python scripts/prep_photo.py [input.png] [output.png]
"""
import os
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INP = os.path.join(HERE, "..", "source-photo.png")
DEFAULT_OUT = os.path.join(HERE, "..", "source-prepped.png")


def prep_image(inp_path: str, out_path: str, line_weight: float = 0.6) -> str:
    # 1. Cut out the subject
    orig = Image.open(inp_path).convert("RGBA")
    cut = remove(orig)
    rgb = np.array(cut.convert("RGB"))
    alpha = np.array(cut.split()[-1])  # 0 = background
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    # 2. Smooth texture, keep edges
    smooth = gray
    for _ in range(3):
        smooth = cv2.bilateralFilter(smooth, 9, 40, 9)

    # 3. Tone stretch over subject only
    subj_mask = alpha > 128
    if np.any(subj_mask):
        lo, hi = np.percentile(smooth[subj_mask], [2, 92])
        if hi > lo:
            tone = np.clip((smooth.astype(np.float32) - lo) / (hi - lo), 0, 1)
        else:
            tone = smooth.astype(np.float32) / 255.0
    else:
        tone = smooth.astype(np.float32) / 255.0

    # 4. Difference-of-gaussians ridges -> darken
    fine = cv2.GaussianBlur(smooth, (0, 0), 1.5).astype(np.float32)
    coarse = cv2.GaussianBlur(smooth, (0, 0), 6).astype(np.float32)
    lines = np.clip((coarse - fine) / 40.0, 0, 1)
    out = np.clip(tone - line_weight * lines, 0, 1) * 255.0

    # 5. Paste onto white with slight feathering
    mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
    out = out * mask + 255.0 * (1.0 - mask)

    # Crop square around subject
    ys, xs = np.where(alpha > 20)
    if len(xs) > 0 and len(ys) > 0:
        side = max(xs.max() - xs.min(), ys.max() - ys.min()) + 60
        cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
    else:
        h, w = out.shape[:2]
        side = max(h, w)
        cx, cy = w // 2, h // 2

    canvas = np.full((side, side), 255, dtype=np.uint8)
    x0, y0 = cx - side // 2, cy - side // 2
    sx0, sy0 = max(x0, 0), max(y0, 0)
    sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
    canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    Image.fromarray(canvas, mode="L").save(out_path)
    print(f"wrote {out_path} ({canvas.shape[1]}x{canvas.shape[0]})")
    return out_path


if __name__ == "__main__":
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INP
    out = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_OUT
    prep_image(inp, out)
