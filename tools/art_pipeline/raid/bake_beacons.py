"""Bake the raid's R3 class beacons (ART-6 3A; bible §4.8 "station beacons", round 21 `operators_r3`,
round 22 `class_colours_v2` / `operator_rigger`) from the approved concept.

The beacon is drawn by the concept's own `beacon()` on tag `art-concepts-r43`
(`docs/concepts/round22_raid_world/scripts/screens21.py`: the class-colour light cone opening from the
Safehouse pad, its cap ring, the holo emblem above it and each class's idle loop), called UNCHANGED at
the map scale its bonus frames use (`with_beacon`: scale 0.5) for FRAMES evenly spaced idle phases. The
emblems it reads are the round 6 class emblems exported exactly as the concept's `emblems20.py` does
(`slicelib.glyph_mask("EM_<CLASS>")`, alpha PNGs), and the class colours are `roof20.CLASS_RGB` (v2).
`beacon()` paints onto an opaque frame (light added, a dark plate behind the emblem), so it is run over
black and over white and the straight-alpha image is recovered from the two (difference matte):
nothing is redrawn.

    assets/raid/beacons/<class>.png   one strip of FRAMES frames (W x H each, left to right)
    assets/raid/beacons/manifest.json (frame size, the pad's pixel in a frame, frames, loop seconds)

screens21 imports the concept's whole screen kit for its other sheets (Blender finishes, fonts,
stickers); beacon() uses none of it, so those modules load as stand-ins carrying only the names
screens21 binds at import (screens20's `to_pil` is the concept's own one-line conversion, copied).

Usage (never from stdin): extract the tag's `docs/concepts/round22_raid_world/scripts/` and
`docs/concepts/round6_roster/scripts/` under `<root>` keeping their layout, then
    python tools/art_pipeline/raid/bake_beacons.py --src <root>
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import types
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "assets" / "raid" / "beacons"
TAG = "art-concepts-r43"
# with_beacon's map scale, the frame round the pad (px) and the pad's pixel in it.
SCALE = 0.5
W, H = 220, 260
PAD = (110, 210)
FRAMES = 16
# The concept's idle loop length (operator_gif: 16 frames at 100 ms).
LOOP_SECONDS = 1.6
CLASSES = ["breaker", "wrecker", "ghost", "phantom", "rigger", "overclocker", "botnet", "hivemind"]


def _to_pil(img):
    # screens20.to_pil (concept), unchanged
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8))


def _stand_ins() -> None:
    noop = lambda *a, **k: None  # noqa: E731
    sys.modules.setdefault("finish19", types.SimpleNamespace())
    sys.modules.setdefault("ui19", types.SimpleNamespace(SL=None))
    sys.modules.setdefault("icons21", types.SimpleNamespace())
    sys.modules.setdefault("screens20", types.SimpleNamespace(
        OUT="", BG=None, canvas=noop, paste=noop, crop=noop, label=noop, title=noop, wrap=noop, to_pil=_to_pil,
        to_f=noop, P=noop, scene_cam=noop, paste_rgba=noop, TXT=None, DIM=None, CLASSES=list(CLASSES)))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    args = ap.parse_args()
    src = Path(args.src)
    sys.path.insert(0, str(src / "round6_roster" / "scripts"))
    sys.path.insert(0, str(src / "round22_raid_world" / "scripts"))
    _stand_ins()
    import slicelib as SLB  # noqa: E402
    import roof20 as RF  # noqa: E402
    import screens21 as S21  # noqa: E402

    # emblems20.py, the class emblems only, into a scratch folder roof20 reads
    em_dir = Path(tempfile.mkdtemp(prefix="rebel_cell_emblems_"))
    for n in CLASSES:
        m = SLB.glyph_mask("EM_" + n.upper())
        im = Image.new("RGBA", m.size, (255, 255, 255, 0))
        im.putalpha(m)
        im.save(em_dir / (n + ".png"))
    RF.EMBLEMS = str(em_dir)

    OUT.mkdir(parents=True, exist_ok=True)
    files = []
    for cls in CLASSES:
        strip = Image.new("RGBA", (W * FRAMES, H), (0, 0, 0, 0))
        for f in range(FRAMES):
            t = f / FRAMES
            black = S21.beacon(np.zeros((H, W, 3), np.float32), PAD[0], PAD[1], cls, t, scale=SCALE)
            white = S21.beacon(np.ones((H, W, 3), np.float32), PAD[0], PAD[1], cls, t, scale=SCALE)
            cover = np.clip(1.0 - (white - black).mean(-1), 0.0, 1.0)
            alpha = np.clip(np.maximum(cover, black.max(-1)), 0.0, 1.0)
            rgb = np.clip(black / np.maximum(alpha[..., None], 1e-4), 0.0, 1.0)
            frame = np.concatenate([rgb, alpha[..., None]], -1)
            strip.paste(Image.fromarray((frame * 255).astype(np.uint8), "RGBA"), (f * W, 0))
        name = cls + ".png"
        strip.save(OUT / name)
        files.append(name)
    meta = {"schema": "rebel_cell.art_export/1", "asset": "raid_beacons",
            "about": "ART-6 3A R3 class beacons (one idle strip per class). Built by tools/art_pipeline/raid/bake_beacons.py; do not edit by hand.",
            "source": {"tag": TAG, "script": "docs/concepts/round22_raid_world/scripts/screens21.py (beacon)",
                       "emblems": "docs/concepts/round22_raid_world/scripts/emblems20.py (round6_roster slicelib EM_*)",
                       "colours": "docs/concepts/round22_raid_world/scripts/roof20.py (CLASS_RGB, v2)"},
            "scale": SCALE, "frame_px": [W, H], "pad_px": list(PAD), "frames": FRAMES, "loop_seconds": LOOP_SECONDS,
            "files": files}
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    shutil.rmtree(em_dir, ignore_errors=True)
    print("baked %d beacon strips into %s" % (len(files), OUT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
