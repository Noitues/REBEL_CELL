"""Bake the raid's ICE crystals (ART-6 3A; round 22 "ICE as crystals (no fog)", the held threat of
`round21_raid_ui/interactions_gifs/15_threat_held_ice.gif`) from the approved concept.

The ice is drawn by the concept's own `ice()` on tag `art-concepts-r43`
(`docs/concepts/round22_raid_ui/scripts/ui22.py`), called UNCHANGED with the arguments its held-threat
frame uses (`screens22.py` g15: an ellipse mask 50 x 35 round the unit, seed 7, fill 0.45, density 9,
scale 1.5) over `grow` 0..1. `ice()` paints onto an opaque frame, so it is run twice per step, over black
and over white, and the straight-alpha image is recovered from the two (difference matte): nothing is
redrawn.

    assets/raid/ice/ice_<NN>.png    NN = 1..STEPS (grow = NN / STEPS)
    assets/raid/ice/manifest.json

Usage (never from stdin): extract `docs/concepts/round22_raid_ui/scripts/` of the tag under `<root>`
keeping its layout (`<root>/round22_raid_ui/scripts/ui22.py` and what it imports), then
    python tools/art_pipeline/raid/bake_ice.py --src <root>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "assets" / "raid" / "ice"
TAG = "art-concepts-r43"
# The concept frame's arguments (screens22.py g15).
RX, RY = 50, 35
SEED, FILL, DENSITY, SCALE = 7, 0.45, 9.0, 1.5
# The image round the mask (px; room for the crystals' glints) and the growth steps.
W, H = 150, 112
STEPS = 8


class Frame:
    """The minimum of the concept's frame `ice()` reads: an RGB float image and its size."""

    def __init__(self, bg: float):
        self.img = np.full((H, W, 3), bg, np.float32)
        self.w, self.h, self.ox, self.oy = W, H, 0, 0


def mask() -> np.ndarray:
    """The concept's ellipse_mask (ui21.py) round the image centre."""
    lay = Image.new("L", (W, H), 0)
    ImageDraw.Draw(lay).ellipse([W / 2 - RX, H / 2 - RY, W / 2 + RX, H / 2 + RY], fill=255)
    return np.asarray(lay.filter(ImageFilter.GaussianBlur(4)), np.float32) / 255


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.src) / "round22_raid_ui" / "scripts"))
    # ui22 imports the concept's whole screen kit (ui19 / ui20: Blender renders, fonts, the sticker
    # tray) for its other functions; ice() uses none of it, so those two load as empty stand-ins
    # (ui19's sticker tray empty for ui22's module-level slot table).
    import types
    sys.modules.setdefault("ui19", types.SimpleNamespace(TRAY=[]))
    sys.modules.setdefault("ui20", types.SimpleNamespace())
    import ui22 as K  # noqa: E402

    OUT.mkdir(parents=True, exist_ok=True)
    m = mask()
    files = []
    for k in range(1, STEPS + 1):
        grow = k / STEPS
        black = K.ice(Frame(0.0), m, grow=grow, seed=SEED, fill=FILL, density=DENSITY, scale=SCALE).img
        white = K.ice(Frame(1.0), m, grow=grow, seed=SEED, fill=FILL, density=DENSITY, scale=SCALE).img
        cover = np.clip(1.0 - (white - black).mean(-1), 0.0, 1.0)
        alpha = np.clip(np.maximum(cover, black.max(-1)), 0.0, 1.0)
        rgb = np.clip(black / np.maximum(alpha[..., None], 1e-4), 0.0, 1.0)
        img = np.concatenate([rgb, alpha[..., None]], -1)
        name = "ice_%02d.png" % k
        Image.fromarray((img * 255).astype(np.uint8), "RGBA").save(OUT / name)
        files.append(name)
    meta = {"schema": "rebel_cell.art_export/1", "asset": "raid_ice",
            "about": "ART-6 3A ICE crystals round a held threat. Built by tools/art_pipeline/raid/bake_ice.py; do not edit by hand.",
            "source": {"tag": TAG, "script": "docs/concepts/round22_raid_ui/scripts/ui22.py (ice)",
                       "call": "docs/concepts/round22_raid_ui/scripts/screens22.py g15 (15_threat_held_ice.gif)"},
            "image_px": [W, H], "mask_radii_px": [RX, RY], "steps": STEPS, "files": files}
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("baked %d ice steps into %s" % (len(files), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
