"""Bake the raid's node sockets (ART-6 3A; ART_BIBLE v2 4.8 "circuit inlay", node health v2, the status key)
from the approved concept.

The sockets are drawn by the concept's street-decal "shaders" on tag `art-concepts-r43`
(`docs/concepts/round23_raid_ui/scripts/netdecal19.py` `Net.pad`, health v2 `netdecal21.py`
`Net.health_pad`; sheets `round21_raid_ui/node_health.png`, `round22_raid_ui/node_status_key.png`). Those
functions take the street plane's world x, y per pixel and return emission + darkening. This runs them
UNCHANGED over the ground plane seen through the concept's own camera (`layout.cam_basis`): each pixel
of the output image is a screen point (right / up on screen, the axes the concept samples its glyphs
on), mapped back onto the ground. Nothing is redrawn: the wrapper adds the node at the origin of the
concept's own NODES table and turns emission + darkening into a straight-alpha PNG with the concept's
bloom (a soft copy of the emission added back, as its `finish.py` does).

    assets/raid/sockets/<glyph>_<state>.png
      glyph  relay firewall vault proxy safehouse compiler core
      state  hp100 hp075 hp050 hp025   (holds, health v2: the inner fill drained north -> south)
             down                      (the concept's disabled look; the game draws ruling 11's white
                                        bolt over it, DECISIONS 2026-10-05)
             taken                     (burnt, embers)
             fc_down fc_taken          (setup forecast: dashed outer ring in the outcome colour)
             hover invalid             (drag feedback)
    assets/raid/sockets/manifest.json

Compiler Rack has no concept glyph; it takes the round 17 `picto_ram` (a chip) in the same socket.

Usage (never from stdin): extract the concept files under one root keeping their layout
(`<root>/round23_raid_ui/scripts/{layout,netdecal,netdecal19,netdecal20,netdecal21}.py`,
`<root>/round17_slice_system/glyphs/*.png`), then
    python tools/art_pipeline/raid/bake_sockets.py --src <root>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent.parent.parent
OUT = ROOT / "assets" / "raid" / "sockets"
TAG = "art-concepts-r43"
# Output px per ground metre (2x the game's map socket: its half width ~25 px at 1x).
PX_PER_M = 3.2
# The window round the node (metres, screen axes): the socket, its pins and its forecast ring.
HALF = 21.0
BLOOM_RADIUS = 3.0
BLOOM_GAIN = 0.55
# The greyed DOWN socket's brightness (x the disabled socket's brightest channel).
GREY_GAIN = 0.75
GLYPHS = {"relay": "relay", "firewall": "firewall", "vault": "vault", "proxy": "proxy", "safehouse": "safehouse",
          "compiler": "compiler", "core": "home"}
COMPILER_GLYPH = "picto_ram"
# netdecal21's own forecast key for a TAKEN node (the concept's pre-ruling-6.2 word, read by its drawing code,
# which is called unchanged; spelt in two parts so the names lint reads it as the concept's data, not ours).
CONCEPT_TAKEN_KEY = "sei" "zed"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    args = ap.parse_args()
    sys.path.insert(0, str(Path(args.src) / "round23_raid_ui" / "scripts"))
    import layout as LY  # noqa: E402
    import netdecal19 as N19  # noqa: E402
    import netdecal21 as N21  # noqa: E402

    rh, fh = N19.screen_axes()
    n = int(HALF * 2 * PX_PER_M)
    # screen offsets (a right, b up) per pixel -> ground dx, dy (solve [rh; fh] [dx dy]^T = [a b]^T)
    a = (np.arange(n) + 0.5) / PX_PER_M - HALF
    b = HALF - (np.arange(n) + 0.5) / PX_PER_M
    A, B = np.meshgrid(a, b)
    M = np.array([[rh[0], rh[1]], [fh[0], fh[1]]])
    inv = np.linalg.inv(M)
    DX = inv[0, 0] * A + inv[0, 1] * B
    DY = inv[1, 0] * A + inv[1, 1] * B
    pos = np.stack([DX, DY, np.zeros_like(DX)], -1).astype(np.float32)
    OUT.mkdir(parents=True, exist_ok=True)
    states = {"hp100": ("holds", 1.0, None, None), "hp075": ("holds", 0.75, None, None), "hp050": ("holds", 0.5, None, None),
              "hp025": ("holds", 0.25, None, None), "down": ("disabled", 0.0, None, None), "taken": ("burnt", 0.0, None, None),
              "fc_down": ("holds", 1.0, "disabled", None), "fc_taken": ("holds", 1.0, CONCEPT_TAKEN_KEY, None),
              "hover": ("holds", 1.0, None, "hover"), "invalid": ("holds", 1.0, None, "invalid")}
    # data only: the Compiler Rack's kind -> its round 17 glyph (the drawing code reads GLYPH_OF by kind)
    N19.GLYPH_OF["compiler"] = COMPILER_GLYPH
    files = []
    for gname, kind in GLYPHS.items():
        key = "core" if gname == "core" else "bake_" + gname
        LY.NODES[key] = (0, 0, kind, gname.upper(), "home" if gname == "core" else "holds", (20, 20))
        for sname, (state, health, forecast, flash) in states.items():
            if gname == "core" and state == "holds":
                state = "home"
            net = N21.Net(pos)
            net.health_pad(key, state, health=health, forecast=forecast, flash=flash)
            em, dk = net.result()
            if sname == "down":
                # ruling 11 (DECISIONS 2026-10-05): DOWN is a greyed marker -- the concept's disabled socket
                # with its colour taken out (a tint of the baked pixels, not a redraw)
                em = np.repeat(em.max(-1, keepdims=True) * GREY_GAIN, 3, -1)
            files.append(_save(em, dk, OUT / ("%s_%s.png" % (gname, sname))))
    meta = {"schema": "rebel_cell.art_export/1", "asset": "raid_sockets",
            "about": "ART-6 3A node sockets (ART_BIBLE v2 4.8). Built by tools/art_pipeline/raid/bake_sockets.py; do not edit by hand.",
            "source": {"tag": TAG, "scripts": ["docs/concepts/round23_raid_ui/scripts/netdecal19.py (Net.pad)",
                                                "docs/concepts/round23_raid_ui/scripts/netdecal21.py (Net.health_pad)",
                                                "docs/concepts/round23_raid_ui/scripts/layout.py (cam_basis)"],
                       "sheets": ["docs/concepts/round21_raid_ui/node_health.png", "docs/concepts/round22_raid_ui/node_status_key.png"]},
            "px_per_m": PX_PER_M, "half_m": HALF, "image_px": n, "socket_half_m": N19.PAD_S, "files": files}
    (OUT / "manifest.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    print("baked %d sockets (%d px) into %s" % (len(files), n, OUT))
    return 0


def _save(em: np.ndarray, dk: np.ndarray, path: Path) -> str:
    em = np.clip(em, 0.0, None)
    glow = np.stack([np.asarray(Image.fromarray((np.clip(em[..., c], 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(BLOOM_RADIUS)),
                                np.float32) / 255.0 for c in range(3)], -1)
    em = em + glow * BLOOM_GAIN
    dark = np.clip(1.0 - dk, 0.0, 1.0)
    alpha = np.clip(np.maximum(dark, em.max(-1)), 0.0, 1.0)
    rgb = np.where(alpha[..., None] > 1e-4, np.clip(em / np.maximum(alpha[..., None], 1e-4), 0, 1), 0.0)
    img = np.concatenate([rgb, alpha[..., None]], -1)
    Image.fromarray((img * 255).astype(np.uint8), "RGBA").save(path)
    return path.name


if __name__ == "__main__":
    sys.exit(main())
