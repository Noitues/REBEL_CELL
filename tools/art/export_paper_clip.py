"""Export the paper clip (B5; review D24) from the round 44 concept kit, unchanged.

Designer ruling (2026-10-05): never redraw art the art pass already made. Review D24 asks for the concepts' paper clip
on work orders and dossiers. Round 44's map kit draws it inside `kit44.work_order` (the intercepted work order's
clip, `docs/concepts/round44_undesigned/A_map/scripts/kit44.py` on the art-pass branch). This runs `work_order` as
it is at 2x (`scale=2`), with the kit's paper stock swapped for a clear canvas for this one call (so only what is
drawn over the paper is left), and crops the clip's own box (the function's `clip` image: 26 x 64 x scale, placed
`10 x scale` from the right edge at the top) into `assets/ui/paper/paper_clip.png`.

Only paths change: the scripts' font paths point at the shipped faces (`assets/fonts`). No drawing code is edited.

Usage (never from stdin on this machine):
    python <scratch>/extract_dir.py origin/art-pass <dir> docs/concepts/round44_undesigned/A_map/scripts
    python tools/art/export_paper_clip.py --src <dir>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
FONTS = ROOT / "assets" / "fonts"
OUT = ROOT / "assets" / "ui" / "paper"
SCALE = 2
# kit44.work_order's clip: its image size and its inset from the paper's right edge (x scale).
CLIP_W, CLIP_H, CLIP_INSET = 26, 64, 10
PAPER_W = 330


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, help="the extracted art-pass tree (holds docs/concepts/...)")
    a = ap.parse_args()
    scripts = Path(a.src) / "docs" / "concepts" / "round44_undesigned" / "A_map" / "scripts"
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(scripts))
    from PIL import Image  # noqa: E402
    import kit44 as KIT  # noqa: E402
    U = KIT.K
    for k, f in (("ANTON", "Anton-Regular.ttf"), ("MONO", "ShareTechMono-Regular.ttf"), ("PLEX", "IBMPlexSansCondensed-Regular.ttf"),
                 ("PLEX_M", "IBMPlexSansCondensed-Medium.ttf"), ("MARKER", "PermanentMarker-Regular.ttf"),
                 ("COUR", "CourierPrime-Regular.ttf"), ("COUR_B", "CourierPrime-Bold.ttf")):
        if hasattr(U, k):
            setattr(U, k, str(FONTS / f))
    KIT.COUR, KIT.COUR_B = U.COUR, U.COUR_B
    if hasattr(U, "_fc"):
        U._fc.clear()
    orig = U.paper_tex
    U.paper_tex = lambda w, h, *args, **kw: Image.new("RGBA", (w, h), (0, 0, 0, 0))
    try:
        p = KIT.work_order([("SITE", "x")], w=PAPER_W, scale=SCALE)
    finally:
        U.paper_tex = orig
    cw, ch = CLIP_W * SCALE, CLIP_H * SCALE
    x0 = p.width - cw - CLIP_INSET * SCALE
    clip = p.crop((x0, 0, x0 + cw, ch))
    # The work order's letterhead band (kit44.MER, drawn on the paper before the clip) is the paper's, not the
    # clip's: its exact pixels are cleared (the clip, composited over it, keeps its own).
    band = tuple(KIT.MER) + (255,)
    px = clip.load()
    for y in range(clip.height):
        for x in range(clip.width):
            if px[x, y] == band:
                px[x, y] = (0, 0, 0, 0)
    OUT.mkdir(parents=True, exist_ok=True)
    clip.save(OUT / "paper_clip.png")
    print("wrote", OUT / "paper_clip.png", clip.size)
    return 0


if __name__ == "__main__":
    sys.exit(main())
