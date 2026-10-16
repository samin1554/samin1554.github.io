# Assets and rights

The site is the plain HTML/CSS/JS in `public/` (Astro copies it verbatim); the previous Astro homepage now lives at `/classic/` (`src/pages/classic.astro`).

**The five figure images are from Pinterest posters by other designers. They're for this local mockup only. Replace them before anything goes public.**

| # | Used in | Source (reference poster) | What to replace it with |
|---|---|---|---|
| 1 | I · hero | "SACRIFICE / Sacramento" poster (designer unknown). Built on Guido Reni, *St. Michael Archangel* (1636) | Reni's painting is public domain. Use a museum scan (Wikimedia Commons) and re-run the cutout |
| 2 | III · chapters | "FOR JUDGEMENT" poster (HDR.PSD, Episode 051) | A public-domain baroque portrait or Venetian mask painting, or a commissioned piece |
| 3 | II · works | "Emperor / Medieval Empire" poster | A public-domain armoured king (e.g. Rijksmuseum / Met Open Access), halftoned |
| 4 | IV · codex | Midra fan poster. Elden Ring and FromSoftware IP | Original art: commission it, or make a figure from public-domain etchings |
| 5 | V · letters | Surreal eye-diamond painting (artist unknown) | Commission or license it. The live Blender pyramid already covers the head |
| 6 | VI · curriculum (teaser + `curriculum.html`) | "Until death all defeat is psychological" statue poster (designer unknown) | The statues read like public-domain Renaissance sculpture (Giambologna / Florentine school). Photograph them or use a CC0 museum photo, then re-run with the red-text inpaint recipe |

Made in this project (free to use):
- `assets/models/pyramid.glb`: `pipeline/blender/pyramid.py`
- `assets/video/bg-*.mp4|jpg`: `pipeline/blender/bg_loops.py`
- `assets/scroll/*` (roller, parchment, burnt edge): `pipeline/blender/scroll.py`
- All typography, layout and code

## Rebuilding

```bash
python3 -m venv .venv && .venv/bin/pip install -r pipeline/requirements.txt
.venv/bin/python -I pipeline/cutout.py     # refs -> cutouts (rembg isnet + birefnet + colour keys)
.venv/bin/python -I pipeline/depth.py      # cutouts -> web/{n}.webp + web/{n}-depth.png
Blender --background --python pipeline/blender/bg_loops.py -- all
Blender --background --python pipeline/blender/pyramid.py
Blender --background --python pipeline/blender/scroll.py
```

To swap in a new image, drop it in `public/assets/refs/{n}.webp` and add or adjust its recipe in `cutout.py`. Then re-run both Python steps.
