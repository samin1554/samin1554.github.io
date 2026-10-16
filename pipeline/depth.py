"""Depth maps + web-sized cutouts for the living paintings.

Usage: .venv/bin/python -I codex/pipeline/depth.py
Reads assets/cutouts/{n}.png, writes assets/web/{n}.webp (cropped to the
figure, long side <= 1600) and assets/web/{n}-depth.png (8-bit, near = white,
same crop, half size). Depth outside the figure is extended from its edge so the
displaced mesh doesn't tear at the silhouette.
"""
from pathlib import Path

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import pipeline

ROOT = Path(__file__).resolve().parents[1] / "public"  # assets live under the site's public/
CUT, WEB, DEBUG = (ROOT / "assets" / d for d in ("cutouts", "web", "debug"))
LONG = 1600


def main():
    WEB.mkdir(parents=True, exist_ok=True)
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    est = pipeline("depth-estimation", model="depth-anything/Depth-Anything-V2-Small-hf", device=device)
    sheet = []
    for n in range(1, 7):
        im = Image.open(CUT / f"{n}.png")
        a = np.asarray(im.split()[-1])
        ys, xs = np.nonzero(a > 8)
        pad = int(.03 * max(im.size))
        box = (max(xs.min() - pad, 0), max(ys.min() - pad, 0),
               min(xs.max() + pad, im.width), min(ys.max() + pad, im.height))
        im = im.crop(box)
        s = min(1, LONG / max(im.size))
        im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
        im.save(WEB / f"{n}.webp", quality=84, method=6)

        rgb = im.convert("RGB")
        d = np.asarray(est(rgb)["predicted_depth"].squeeze().cpu().numpy(), np.float32)
        d = cv2.resize(d, im.size, interpolation=cv2.INTER_CUBIC)
        alpha = np.asarray(im.split()[-1]).astype(np.float32) / 255
        inside = alpha > .5
        lo, hi = np.percentile(d[inside], 2), np.percentile(d[inside], 98)
        d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)

        half = (im.width // 2, im.height // 2)
        dh = cv2.resize(d, half, interpolation=cv2.INTER_AREA)
        ah = cv2.resize(alpha, half, interpolation=cv2.INTER_AREA)
        hole = (ah < .5).astype(np.uint8) * 255
        d8 = cv2.inpaint((dh * 255).astype(np.uint8), hole, 12, cv2.INPAINT_TELEA)
        d8 = cv2.GaussianBlur(d8, (0, 0), 2.2)
        Image.fromarray(d8).save(WEB / f"{n}-depth.png", optimize=True)

        prev = Image.fromarray(d8).convert("RGB").resize((int(300 * half[0] / half[1]), 300))
        sheet.append(prev)
        print(n, im.size, f"{(WEB / f'{n}.webp').stat().st_size // 1024}KB")

    out = Image.new("RGB", (sum(p.width for p in sheet) + 40, 300), "white")
    x = 0
    for p in sheet:
        out.paste(p, (x, 0))
        x += p.width + 10
    out.save(DEBUG / "depth-sheet.jpg")


if __name__ == "__main__":
    main()
