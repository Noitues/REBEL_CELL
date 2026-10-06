"""M14 asset parity: the City Grid holo billboard panels (ART-5 5c) from round 26's own generator.

Runs `docs/concepts/round26_city_motion/scripts/cm.py` (tag art-concepts-r43) unchanged:
`_billboard_tex(seed, col)` draws an illegible hologram ad (a pictogram, glyph rows, frame, scanlines)
in a colour `col` and its lightened twin `c2 = col * 0.5 + 128`. The game tints each billboard per
instance, so this wrapper renders every panel twice with the concept's own function (col black and col
white) and packs the result: R = the c2 mask (255 where the concept used the lightened colour), A = the
panel's alpha. G and B are 0. The shader rebuilds `mix(col, col * 0.5 + 0.5, R)` with the instance colour.
The four panels are the four pictogram kinds (ring, wedge, chevrons, bars), one seed each, laid out as a
horizontal atlas, upscaled 2x nearest-neighbour (the concept panel is 72 x 44 px).

    python tools/art_pipeline/parity/export_billboards.py --concepts <extracted>/docs/concepts

Output: assets/city/billboards/panels.png + manifest.json.
"""
from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import parity_common as PC  # noqa: E402

ROUND = "round26_city_motion"
OUT = PC.ROOT / "assets" / "city" / "billboards"
KINDS = 4


def seed_for_kind(kind: int) -> int:
    """The smallest seed whose `random.Random(seed).randint(0, 3)` (the concept's pictogram pick) is `kind`."""
    s = 0
    while random.Random(s).randint(0, 3) != kind:
        s += 1
    return s


def main() -> int:
    a = PC.args(__doc__.splitlines()[0])
    scripts = PC.use_round(a.concepts, ROUND)
    import numpy as np
    from PIL import Image
    import cm

    man = PC.Manifest(OUT, "billboards", "M14 asset parity: holo billboard panel atlas (ART_BIBLE v2 4.2; round 26 city motion).",
                      ROUND, ["cm.py"], "tools/art_pipeline/parity/export_billboards.py")
    panels = []
    seeds = []
    for kind in range(KINDS):
        seed = seed_for_kind(kind)
        seeds.append(seed)
        dark = cm._billboard_tex(seed, (0, 0, 0))
        light = cm._billboard_tex(seed, (255, 255, 255))
        d = np.asarray(dark, np.uint8)
        lt = np.asarray(light, np.uint8)
        alpha = lt[:, :, 3]
        # col pixels are 0 in the black render, c2 pixels are 128: a pixel is lightened when it reads > 64.
        mask = np.where(d[:, :, 0] > 64, 255, 0).astype(np.uint8)
        mask = np.where(alpha > 0, mask, 0).astype(np.uint8)
        out = np.zeros(d.shape, np.uint8)
        out[:, :, 0] = mask
        out[:, :, 3] = alpha
        panels.append(Image.fromarray(out, "RGBA").resize((d.shape[1] * 2, d.shape[0] * 2), Image.NEAREST))
    w, h = panels[0].size
    atlas = Image.new("RGBA", (w * KINDS, h), (0, 0, 0, 0))
    for i, p in enumerate(panels):
        atlas.paste(p, (i * w, 0))
    man.add(atlas, "panels", "cm._billboard_tex(seed, col) x2 (black / white), seeds %s" % seeds,
            "%d panels of %d x %d side by side; R = c2 mask, A = alpha; 2x nearest" % (KINDS, w, h))
    man.write(scripts)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
