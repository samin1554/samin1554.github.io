"""Cut the figures out of the reference posters.

Usage: .venv/bin/python -I codex/pipeline/cutout.py
Writes assets/cutouts/{n}.png (RGBA, 2x Lanczos), assets/stills/{n}.jpg and
assets/debug/sheet.jpg (cutouts over magenta, for checking fringes).

Each poster gets its own recipe: two segmentation models (isnet, birefnet) plus
colour keys for posters where the figure is tangled up with baked-in type.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

ROOT = Path(__file__).resolve().parents[1] / "public"  # assets live under the site's public/
REFS, OUT, STILLS, DEBUG = (ROOT / "assets" / d for d in ("refs", "cutouts", "stills", "debug"))
CACHE = DEBUG / "masks"


def model_mask(name, n, src):
    path = CACHE / f"{name}-{n}.png"
    if not path.exists():
        rgba = remove(src, session=new_session(name), post_process_mask=False)
        rgba.split()[-1].save(path)
    return np.asarray(Image.open(path)).astype(np.float32) / 255


def hsv(src):
    h, s, v = cv2.split(cv2.cvtColor(np.asarray(src), cv2.COLOR_RGB2HSV).astype(np.float32))
    return h * 2, s / 255, v / 255


def box(shape, x0, y0, x1, y1):
    h, w = shape
    m = np.zeros(shape, np.float32)
    m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
    return m


def fade(shape, y0, y1):
    """1 above y0, ramps to 0 at y1 (fractions of height)."""
    h = shape[0]
    y = np.linspace(0, 1, h)[:, None]
    return np.clip((y1 - y) / (y1 - y0), 0, 1) * np.ones(shape, np.float32)


def clean(m, min_frac=.03, close=5):
    m8 = (m > .5).astype(np.uint8)
    if close:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close, close))
        m8 = cv2.morphologyEx(m8, cv2.MORPH_CLOSE, k)
        m8 = cv2.morphologyEx(m8, cv2.MORPH_OPEN, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m8)
    if n <= 1:
        return m
    big = stats[1:, cv2.CC_STAT_AREA].max()
    keep = np.isin(lab, [i for i in range(1, n) if stats[i, cv2.CC_STAT_AREA] >= big * min_frac])
    # Fill small interior holes so dark armour or robes don't go transparent,
    # but leave big ones (the gap between an arm and the body) open.
    filled = keep.astype(np.uint8)
    cnts, _ = cv2.findContours(filled, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(filled, cnts, -1, 1, cv2.FILLED)
    hn, hlab, hstats, _ = cv2.connectedComponentsWithStats(((filled > 0) & ~keep).astype(np.uint8))
    small = np.isin(hlab, [i for i in range(1, hn) if hstats[i, cv2.CC_STAT_AREA] < keep.sum() * .01])
    return np.where(keep | small, np.maximum(m, small), 0).astype(np.float32)


def recipe(n, src):
    shape = src.size[::-1]
    isnet = lambda: model_mask("isnet-general-use", n, src)
    biref = lambda: model_mask("birefnet-general", n, src)
    H, S, V = hsv(src)

    if n == 1:  # Sacrifice: wings and head sit inside the black "SACRIFICE" letters
        paper = (V > .66) & (S < .32)
        ink = V < .2
        top = (~paper & ~ink).astype(np.float32) * box(shape, .02, .1, 1, .42)
        top = cv2.medianBlur((top * 255).astype(np.uint8), 5) / 255
        m = np.maximum(np.clip(isnet() * 1.8, 0, 1), top) * (1 - box(shape, 0, .9, 1, 1))
        m = clean(m, .05, 7)
        # The right wing is striped by the letters "ICE": close the gaps, then
        # inpaint the colour that was ink so the wing reads as one shape.
        wing = np.clip(box(shape, .55, .12, 1, .46) + box(shape, .38, .18, .6, .36), 0, 1)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45))
        closed = cv2.morphologyEx(((m > .5) * wing).astype(np.uint8), cv2.MORPH_CLOSE, k)
        gaps = ((closed > 0) & (m < .5)).astype(np.uint8)
        src = Image.fromarray(cv2.inpaint(np.asarray(src), gaps * 255, 9, cv2.INPAINT_TELEA))
        m = np.maximum(m, closed.astype(np.float32))
    elif n == 2:  # Judgement: clean model mask, drop footer type and barcode
        m = clean(biref() * fade(shape, .88, .92), .05)
    elif n == 3:  # Emperor: fade the cloak out above the paragraph of red type
        m = clean(biref() * fade(shape, .70, .76) * (1 - box(shape, 0, 0, 1, .045)), .05)
    elif n == 4:  # Midra: grey body + gold robe + flame head on a black map
        flame = (S > .5) & (V > .45)
        body = (V > .3) & (S < .35)
        figure = box(shape, .3, .3, .92, .78)
        text = box(shape, .64, .27, .97, .42) + box(shape, .0, .27, .26, .52) + box(shape, .93, .0, 1, 1)
        m = (flame | body).astype(np.float32) * figure * (1 - np.clip(text, 0, 1))
        m = np.maximum(m, np.clip(isnet() * 1.8, 0, 1) * figure) * (1 - np.clip(text, 0, 1))
        m = cv2.medianBlur((m * 255).astype(np.uint8), 7) / 255
        m = clean(m, .02, 9) * fade(shape, .72, .78)
    elif n == 6:  # Statues: paint out the red quote laid over the faces first
        red = (((H < 24) | (H > 336)) & (S > .43) & (V > .43)).astype(np.uint8) * 255
        red = cv2.dilate(red, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        src = Image.fromarray(cv2.inpaint(np.asarray(src), red, 7, cv2.INPAINT_TELEA))
        m = clean(model_mask("birefnet-general", n, src), .05)
    else:  # Eye-pyramid: model handles it
        m = clean(biref(), .05)
    return m, src


def main():
    for d in (OUT, STILLS, DEBUG, CACHE):
        d.mkdir(parents=True, exist_ok=True)
    previews = []
    for n in range(1, 7):
        src = Image.open(REFS / f"{n}.webp").convert("RGB")
        w, h = src.size
        m, src = recipe(n, src)
        alpha = cv2.GaussianBlur((m * 255).astype(np.uint8), (0, 0), .9)

        out = Image.merge("RGBA", (*src.split(), Image.fromarray(alpha)))
        out = out.resize((w * 2, h * 2), Image.LANCZOS)
        out.save(OUT / f"{n}.png", optimize=True)

        bg = Image.new("RGBA", out.size, (255, 0, 255, 255))
        bg.alpha_composite(out)
        previews.append(bg.convert("RGB").resize((int(460 * w / h), 460)))

        # Static fallback: darkened, slightly desaturated poster.
        arr = np.asarray(src).astype(np.float32) / 255
        arr = (arr * .7 + arr.mean(axis=2, keepdims=True) * .3) * .62
        Image.fromarray((arr.clip(0, 1) * 255).astype(np.uint8)).save(STILLS / f"{n}.jpg", quality=82)
        print(n, out.size, f"{(alpha > 128).mean():.0%} opaque")

    sheet = Image.new("RGB", (sum(p.width for p in previews) + 40, 460), "white")
    x = 0
    for p in previews:
        sheet.paste(p, (x, 0))
        x += p.width + 10
    sheet.save(DEBUG / "sheet.jpg")


if __name__ == "__main__":
    main()
