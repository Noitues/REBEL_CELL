"""Bake the raid's BREACHED bit explosion (ART-6 3A; bible §4.8, round 21 `26_home_breached.gif`) from the
approved concept.

The burst is drawn by the concept's own `bit_burst()` on tag `art-concepts-r43`
(`docs/concepts/round22_raid_ui/scripts/ui21.py`: a white flash and shock ring, then 0 / 1 bits blasting
out, rising and falling as they fade), called UNCHANGED with the arguments its home-breached frame uses
(`screens22.py`: seed 26, red (255, 60, 50), 180 bits, radius 190) at FRAMES evenly spaced times. It
blends with the concept's `ui19._add_layer` (copied unchanged below: ui19 itself needs the concept's
whole Blender / sticker kit) over black and over white, and the straight-alpha frame is recovered from
the two (difference matte). The bits' font is the concept's Share Tech Mono (the game ships it).

    assets/raid/bits/bits.png      one strip of FRAMES frames (W x H each, left to right)
    assets/raid/bits/manifest.json (frame size, the burst's centre in a frame, frames)

Usage (never from stdin): extract the tag's `docs/concepts/round22_raid_ui/scripts/` under `<root>`
keeping its layout, then
    python tools/art_pipeline/raid/bake_bits.py --src <root>
"""

from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "assets" / "raid" / "bits"
FONT = ROOT / "assets" / "fonts" / "ShareTechMono-Regular.ttf"
TAG = "art-concepts-r43"
# screens22.py home breached: bit_burst(fr, cx, cy - 10, t, seed=26, col=(255, 60, 50), n=180, radius=190)
SEED, COL, N, RADIUS = 26, (255, 60, 50), 180, 190
W, H = 460, 380
CENTRE = (230, 200)
FRAMES = 24


def _add_layer(img_f, lay, glow=0.6):
    # ui19._add_layer (concept), unchanged
    a = np.asarray(lay, np.float32) / 255.0
    al = a[..., 3:4]
    out = img_f * (1 - al) + a[..., :3] * al
    bl = np.asarray(lay.split()[3].filter(ImageFilter.GaussianBlur(5)), np.float32)[..., None] / 255.0
    colm = np.asarray(lay.convert("RGB").filter(ImageFilter.GaussianBlur(5)), np.float32) / 255.0
    return np.clip(out + colm * glow * 1.4 * (bl > 0.01), 0, 1.2)


class Frame:
    """The minimum of the concept's frame bit_burst() reads."""

    def __init__(self, bg: float):
        self.img = np.full((H, W, 3), bg, np.float32)
        self.w, self.h, self.ox, self.oy = W, H, 0, 0


def _stand_ins() -> None:
    def add(fr, lay, glow=0.7):
        # ui20._add (concept), unchanged
        fr.img = _add_layer(fr.img, lay, glow)
        return fr

    names = dict(T=None, SL=types.SimpleNamespace(MONO=str(FONT)), F=lambda path, size: ImageFont.truetype(path, int(round(size))),
                 S=None, P=None, Frame=Frame, Pencil=object, _add=add)
    for c in ("PINK", "CYAN", "GREEN", "VIOLET", "AMBER", "LIME", "HARM", "HALCYON", "PAPER", "INKC", "ICE", "Y_PEN", "R_PEN"):
        names[c] = (0, 0, 0)
    sys.modules.setdefault("ui20", types.SimpleNamespace(**names))
    sys.modules.setdefault("ui19", types.SimpleNamespace(_add_layer=_add_layer))
    sys.modules.setdefault("layout", types.SimpleNamespace())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.src) / "round22_raid_ui" / "scripts"))
    _stand_ins()
    import ui21 as K  # noqa: E402

    OUT.mkdir(parents=True, exist_ok=True)
    strip = Image.new("RGBA", (W * FRAMES, H), (0, 0, 0, 0))
    for f in range(FRAMES):
        t = f / FRAMES
        black = K.bit_burst(Frame(0.0), CENTRE[0], CENTRE[1], t, seed=SEED, col=COL, n=N, radius=RADIUS).img
        white = K.bit_burst(Frame(1.0), CENTRE[0], CENTRE[1], t, seed=SEED, col=COL, n=N, radius=RADIUS).img
        cover = np.clip(1.0 - (white - black).mean(-1), 0.0, 1.0)
        alpha = np.clip(np.maximum(cover, np.clip(black, 0, 1).max(-1)), 0.0, 1.0)
        rgb = np.clip(black / np.maximum(alpha[..., None], 1e-4), 0.0, 1.0)
        frame = np.concatenate([rgb, alpha[..., None]], -1)
        strip.paste(Image.fromarray((frame * 255).astype(np.uint8), "RGBA"), (f * W, 0))
    strip.save(OUT / "bits.png")
    meta = {"schema": "rebel_cell.art_export/1", "asset": "raid_bits",
            "about": "ART-6 3A BREACHED bit explosion. Built by tools/art_pipeline/raid/bake_bits.py; do not edit by hand.",
            "source": {"tag": TAG, "script": "docs/concepts/round22_raid_ui/scripts/ui21.py (bit_burst)",
                       "call": "docs/concepts/round22_raid_ui/scripts/screens22.py (26_home_breached)"},
            "frame_px": [W, H], "centre_px": list(CENTRE), "radius_px": RADIUS, "frames": FRAMES, "files": ["bits.png"]}
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=1), encoding="utf-8", newline="\n")
    print("baked %d bit frames into %s" % (FRAMES, OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
