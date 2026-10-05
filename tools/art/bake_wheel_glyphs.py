"""Interim corp crests for ART-2 2A (ART_BIBLE v2 2.4, 3.16): the crest glyphs 1C's atlas does not
carry yet (Meridian crane-A, Solace helix, Halcyon EYE, Orbital ringed planet, REBEL_CELL FIST), as 256 px
white-on-transparent PNGs in `assets/wheel/glyphs_interim/crest_<corp>.png` (`WheelGlyphs` reads them).
Every other wheel glyph comes from 1C's atlas. Drawn by the concept recipes, unchanged
(round 40 slicelib.glyph_mask, round 41 crests15).

Usage: python tools/art/bake_wheel_glyphs.py --src <extracted>/docs/concepts/round40_hub_inner_ring/scripts
    --crests <extracted>/docs/concepts/round41_wheel_stack/scripts
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "assets" / "wheel" / "glyphs_interim"
PX = 256

CRESTS = {"crest_meridian": "EM_MERIDIAN", "crest_solace": "EM_SOLACE", "crest_halcyon": "EYE",
          "crest_orbital": "EM_ORBITAL", "crest_rebel_cell": "FIST"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the round 40 concept scripts folder (from the tag)")
    ap.add_argument("--crests", required=True, help="the round 41 concept scripts folder (crests15.py)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, args.src)
    from PIL import Image

    import glyphs40 as G
    import slicelib as SL

    sys.path.append(args.crests)
    import crests15

    def to_png(m, name):
        if m is None:
            print("missing", name)
            return
        im = m if isinstance(m, Image.Image) else Image.fromarray(m)
        a = im.convert("L").resize((PX, PX), Image.LANCZOS)
        out = Image.new("RGBA", (PX, PX), (255, 255, 255, 0))
        out.putalpha(a)
        out.save(OUT / (name + ".png"), optimize=True)

    for name, gid in CRESTS.items():
        m = crests15.CUSTOM[gid]() if gid in crests15.CUSTOM else None
        try:
            m = m if m is not None else G.mask(gid)
        except Exception:  # noqa: BLE001 - the recipe chain raises on unknown names
            m = None
        if m is None:
            m = SL.glyph_mask(gid)
        to_png(m, name)
    print("wrote", len(list(OUT.glob("*.png"))), "glyphs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
